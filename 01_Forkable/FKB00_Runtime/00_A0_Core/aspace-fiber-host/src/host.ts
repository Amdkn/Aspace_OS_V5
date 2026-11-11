/**
 * @aspace/fiber-host — AspaceFiberHost.
 *
 * A real Fiber host on the real Cordis Context (built by @aspace/cordis-adapter):
 * dynamic registry, dependency-ordered lazy activation, real leases with
 * expiry and renewal, receipts, idempotence, crash recovery, executed
 * cleanup and rollback, explicit HMR reconciliation.
 *
 * Isolation rule (D-1): Cordis and HMR are reached ONLY through
 * @aspace/cordis-adapter (createAspaceApp / reconcile / hasHmr), except for
 * the type-only import of Context/Fiber below (erased at compile time).
 */
import type { Context, Fiber } from 'cordis'
import { createAspaceApp, reconcile as adapterReconcile } from '@aspace/cordis-adapter'
import { validateManifest } from './manifest.ts'
import type { FiberManifest } from './manifest.ts'
import { Journal, isoNow, payloadHash } from './journal.ts'
import type { JournalEvent } from './journal.ts'
import { HttpLoopbackTransport, InProcessTransport, UnixSocketTransport } from './transports.ts'
import type { InProcessImpl, Transport } from './transports.ts'
import {
  DependencyError,
  LeaseExpiredError,
  LeaseRequiredError,
  StateError,
  TransportError,
  UnknownFiberError,
  FiberHostError,
} from './errors.ts'

/** Upstream surface the host depends on, as names — a drift is a design event. */
export const PINNED_HOST_SURFACE = [
  'ctx.plugin(apply, config)',
  'fiber.dispose()',
  'ctx.effect(() => disposer)',
  'ctx.hmr.reconcile(() => roots)',
  'Hmr.Result { settled, aborted, skipped }',
] as const

export interface Envelope {
  request_id: string
  trace_id?: string
  parent_id?: string
  session_id?: string
  holon_id?: string
  fiber_id: string
  operation: string
  deadline?: string
  lease_token?: string
  replay_policy?: 'safe' | 'replay'
  payload?: Record<string, unknown>
  callback_url?: string
}

export interface InvokeResult {
  status: string
  result: unknown
  artefacts: unknown[]
  errors: string[]
  receipt_id: string
  replayed?: boolean
}

export interface Lease {
  token: string
  fiber_id: string
  holder: string
  ttl_ms: number
  granted_at: string
  expires_at: string
  renewals: number
}

export interface CoeffectHandler {
  apply: () => void | Promise<void>
  revert: () => void | Promise<void>
}

export type FiberState = 'registered' | 'dormant' | 'starting' | 'active' | 'draining' | 'disposed' | 'failed'

export interface FiberRecord {
  manifest: FiberManifest
  state: FiberState
}

export interface HealthReport {
  ok: boolean
  detail: string
}

const LEASE_RENEW_CAP = 10

function addMs(iso: string, ms: number): string {
  return new Date(new Date(iso).getTime() + ms).toISOString()
}

export class AspaceFiberHost {
  readonly ctx: Context
  private readonly hmrFiber: Fiber
  private readonly journal: Journal
  private readonly records = new Map<string, {
    manifest: FiberManifest
    state: FiberState
    impl?: InProcessImpl
    transport?: Transport
    fiber?: Fiber
    lease?: Lease
    timer?: ReturnType<typeof setTimeout>
    activationOrder: number
    activationPromise?: Promise<Lease>
    appliedCoeffects: string[]
    lastExpiredToken?: string
  }>()
  private readonly coeffects: Record<string, CoeffectHandler>
  private readonly defaultTtlMs: number
  private orderSeq = 0
  private disposed = false
  private activationQueue: Promise<unknown> = Promise.resolve()

  private constructor(ctx: Context, hmrFiber: Fiber, journal: Journal, coeffects: Record<string, CoeffectHandler>, defaultTtlMs: number) {
    this.ctx = ctx
    this.hmrFiber = hmrFiber
    this.journal = journal
    this.coeffects = coeffects
    this.defaultTtlMs = defaultTtlMs
  }

  static async create(options: {
    base?: string
    journalDir: string
    coeffectHandlers?: Record<string, CoeffectHandler>
    defaultLeaseTtlMs?: number
  }): Promise<AspaceFiberHost> {
    const { ctx, hmr } = await createAspaceApp({ base: options.base })
    const journal = new Journal(options.journalDir)
    const host = new AspaceFiberHost(ctx, hmr, journal, options.coeffectHandlers ?? {}, options.defaultLeaseTtlMs ?? 300_000)
    host.recoverFromJournal()
    return host
  }

  // --- crash recovery (boot) -------------------------------------------------
  private recoverFromJournal(): void {
    const now = Date.now()
    for (const orphan of this.journal.orphanedStarts()) {
      this.journal.append('crash-recovery', {
        request_id: orphan.request_id,
        fiber_id: orphan.fiber_id,
        abandoned: true,
        compensated: false,
        reason: 'invoke-start sans invoke-complete — compensation à l’activation de la fiber (rollback déclaré) ou marquée non compensée',
      }, { request_id: orphan.request_id, fiber_id: orphan.fiber_id })
    }
    const granted = new Map<string, { expires_at: string }>()
    const expired = new Set<string>()
    for (const ev of this.journal.readAll()) {
      if (ev.type === 'lease-grant' && ev.detail.token) granted.set(String(ev.detail.token), { expires_at: String(ev.detail.expires_at) })
      if (ev.type === 'lease-expire' && ev.detail.token) expired.add(String(ev.detail.token))
    }
    for (const [token, l] of granted) {
      if (!expired.has(token) && new Date(l.expires_at).getTime() <= now) {
        this.journal.append('lease-expire', { token, recovered: true, reason: 'bail expiré pendant l’arrêt — disposé à la reprise' })
      }
    }
  }

  /** Orphaned request_ids (started, never completed) still awaiting compensation. */
  pendingOrphans(fiberId: string): JournalEvent[] {
    return this.journal.orphanedStarts().filter((ev) => ev.fiber_id === fiberId)
  }

  // --- registry ---------------------------------------------------------------
  register(manifestValue: unknown, impl?: InProcessImpl): FiberManifest {
    const manifest = validateManifest(manifestValue)
    if (this.records.has(manifest.id)) throw new StateError(`fiber déjà enregistrée : ${manifest.id}`)
    if (manifest.transport.type === 'in-process' && !impl) {
      throw new StateError(`fiber ${manifest.id} : transport in-process exige une implémentation à l’enregistrement`)
    }
    this.records.set(manifest.id, { manifest, state: 'dormant', impl, activationOrder: 0, appliedCoeffects: [] })
    return manifest
  }

  list(): FiberRecord[] {
    return [...this.records.values()].map((r) => ({ manifest: r.manifest, state: r.state }))
  }

  get(id: string): FiberRecord {
    const rec = this.records.get(id)
    if (!rec) throw new UnknownFiberError(id)
    return { manifest: rec.manifest, state: rec.state }
  }

  // --- activation ---------------------------------------------------------------
  private activationPlan(id: string): string[] {
    const order: string[] = []
    const visiting = new Set<string>()
    const visit = (fid: string): void => {
      const rec = this.records.get(fid)
      if (!rec) throw new DependencyError(`dépendance manquante : ${fid} (exigée par ${id})`)
      if (order.includes(fid)) return
      if (visiting.has(fid)) throw new DependencyError(`cycle de dépendances détecté impliquant ${fid}`)
      visiting.add(fid)
      for (const dep of rec.manifest.requires) visit(dep)
      visiting.delete(fid)
      order.push(fid)
    }
    visit(id)
    return order
  }

  async activate(id: string, opts: { ttlMs?: number, holder?: string } = {}): Promise<Lease> {
    if (this.disposed) throw new StateError('host disposé')
    const rec = this.records.get(id)
    if (!rec) throw new UnknownFiberError(id)
    if (rec.state === 'active' && rec.lease) return rec.lease
    if (rec.activationPromise) return rec.activationPromise
    const plan = this.activationPlan(id)
    // Serialised: two concurrent activations never interleave a shared dependency.
    const promise = this.activationQueue.then(() => this.runActivation(plan, id, opts))
    this.activationQueue = promise.catch(() => {})
    rec.activationPromise = promise
    try {
      return await promise
    } finally {
      rec.activationPromise = undefined
    }
  }

  private async runActivation(plan: string[], targetId: string, opts: { ttlMs?: number, holder?: string }): Promise<Lease> {
    const started: string[] = []
    try {
      for (const fid of plan) {
        const r = this.records.get(fid)!
        if (r.state === 'active' && r.lease) continue
        await this.startOne(fid, opts)
        started.push(fid)
      }
    } catch (err) {
      for (const fid of [...started].reverse()) {
        try {
          await this.rollbackOne(fid, 'activation-rollback')
        } catch {
          // Rollback errors are journaled inside rollbackOne; never mask the cause.
        }
        try {
          await this.disposeOne(fid, 'activation-rollback')
        } catch {
          // Dispose errors are journaled inside disposeOne; never mask the cause.
        }
      }
      const target = this.records.get(targetId)!
      target.state = 'failed'
      this.journal.append('activation-rollback', { target: targetId, started, error: err instanceof Error ? err.message : String(err) }, { fiber_id: targetId })
      throw err
    }
    return this.records.get(targetId)!.lease!
  }

  /** Revert the fiber's applied co-effects, in reverse order, exactly once. */
  private async revertCoeffects(fid: string): Promise<{ reverted: number, errors: string[] }> {
    const rec = this.records.get(fid)!
    const errors: string[] = []
    let reverted = 0
    for (const name of [...rec.appliedCoeffects].reverse()) {
      try {
        await this.coeffects[name]?.revert()
        reverted++
      } catch (err) {
        errors.push(err instanceof Error ? err.message : String(err))
      }
    }
    rec.appliedCoeffects = []
    return { reverted, errors }
  }

  private async startOne(fid: string, opts: { ttlMs?: number, holder?: string }): Promise<void> {
    const rec = this.records.get(fid)!
    const m = rec.manifest
    rec.state = 'starting'
    // Pending crash compensations first: the fiber's declared rollback runs
    // before any new start (D-6).
    const orphans = this.pendingOrphans(fid)
    if (orphans.length > 0 && rec.impl?.rollback) {
      for (const orphan of orphans) {
        await rec.impl.rollback()
        this.journal.append('rollback', { request_id: orphan.request_id, compensated: true, reason: 'crash-recovery' }, { request_id: orphan.request_id, fiber_id: fid })
      }
    } else if (orphans.length > 0) {
      this.journal.append('rollback', { compensated: false, reason: 'crash-recovery sans rollback déclaré — marqué non compensé, jamais effacé', orphans: orphans.map((o) => o.request_id) }, { fiber_id: fid })
    }
    // Co-effects first (reversible effects, in manifest order).
    for (const name of m.coeffects) {
      const handler = this.coeffects[name]
      if (!handler) throw new DependencyError(`co-effet sans handler : ${name} (fiber ${fid})`)
      await handler.apply()
      rec.appliedCoeffects.push(name)
    }
    try {
      rec.transport = this.buildTransport(m, rec.impl)
      if (m.transport.type === 'in-process') {
        await rec.impl!.start?.()
        // Lifecycle anchor: a real Cordis fiber. Its disposal is driven by
        // Cordis (fiber.dispose() runs the registered effect); impl.dispose()
        // itself is awaited and journaled by disposeOne, exactly once.
        rec.fiber = await this.ctx.plugin((ctx: Context) => {
          ctx.effect(() => () => {})
        })
      }
      const health = await rec.transport.health()
      if (!health.ok) throw new TransportError(`fiber ${fid} : santé en échec à l’activation — ${health.detail}`)
    } catch (err) {
      await this.revertCoeffects(fid)
      // Partial start: unwind what startOne already created (anchor fiber or
      // started impl), so a failed fiber never leaks a live implementation.
      if (rec.fiber) {
        try {
          await rec.fiber.dispose()
        } catch {
          // Best effort; the activation failure below carries the cause.
        }
        rec.fiber = undefined
      } else if (rec.impl?.dispose) {
        try {
          await rec.impl.dispose()
          this.journal.append('cleanup', { step: 'impl-dispose-after-failed-start', ok: true }, { fiber_id: fid })
        } catch (e) {
          this.journal.append('cleanup', { step: 'impl-dispose-after-failed-start', ok: false, error: e instanceof Error ? e.message : String(e) }, { fiber_id: fid })
        }
      }
      rec.transport = undefined
      rec.state = 'failed'
      throw err
    }
    rec.state = 'active'
    rec.activationOrder = ++this.orderSeq
    const ttl = opts.ttlMs ?? m.lifecycle.lease.ttl_ms ?? this.defaultTtlMs
    const grantedAt = isoNow()
    const lease: Lease = {
      token: `lease-${fid}-${this.journal.lastSeq + 1}`,
      fiber_id: fid,
      holder: opts.holder ?? 'aspace-fiber-host',
      ttl_ms: ttl,
      granted_at: grantedAt,
      expires_at: addMs(grantedAt, ttl),
      renewals: 0,
    }
    rec.lease = lease
    this.armLeaseTimer(fid)
    this.journal.append('lease-grant', { token: lease.token, holder: lease.holder, ttl_ms: ttl, expires_at: lease.expires_at }, { fiber_id: fid })
  }

  private buildTransport(m: FiberManifest, impl?: InProcessImpl): Transport {
    switch (m.transport.type) {
      case 'in-process':
        return new InProcessTransport(impl!)
      case 'unix-socket':
        return new UnixSocketTransport(m.transport.socket_path)
      case 'http-loopback':
        return new HttpLoopbackTransport(m.transport.url!)
    }
  }

  // --- leases -------------------------------------------------------------------
  private armLeaseTimer(fid: string): void {
    const rec = this.records.get(fid)!
    if (rec.timer) clearTimeout(rec.timer)
    if (!rec.lease) return
    const delay = Math.max(0, new Date(rec.lease.expires_at).getTime() - Date.now())
    rec.timer = setTimeout(() => {
      void this.expireLease(fid, 'ttl')
    }, delay)
    rec.timer.unref?.()
  }

  async renewLease(id: string, ttlMs?: number): Promise<Lease> {
    const rec = this.records.get(id)
    if (!rec) throw new UnknownFiberError(id)
    if (!rec.lease) throw new LeaseExpiredError(id)
    if (new Date(rec.lease.expires_at).getTime() <= Date.now()) throw new LeaseExpiredError(id)
    const ttl = ttlMs ?? rec.lease.ttl_ms
    if (ttl > rec.lease.ttl_ms * LEASE_RENEW_CAP) {
      throw new FiberHostError('lease-cap', `renouvellement refusé : ttl ${ttl} > plafond ${rec.lease.ttl_ms * LEASE_RENEW_CAP}`)
    }
    rec.lease = {
      ...rec.lease,
      ttl_ms: ttl,
      expires_at: addMs(isoNow(), ttl),
      renewals: rec.lease.renewals + 1,
    }
    this.armLeaseTimer(id)
    this.journal.append('lease-grant', { token: rec.lease.token, renewed: true, renewals: rec.lease.renewals, expires_at: rec.lease.expires_at }, { fiber_id: id })
    return rec.lease
  }

  async sweepExpired(nowMs: number = Date.now()): Promise<{ expired: string[] }> {
    const expired: string[] = []
    for (const [fid, rec] of this.records) {
      if (rec.state === 'active' && rec.lease && new Date(rec.lease.expires_at).getTime() <= nowMs) {
        await this.expireLease(fid, 'sweep')
        expired.push(fid)
      }
    }
    return { expired }
  }

  private async expireLease(fid: string, cause: 'ttl' | 'sweep'): Promise<void> {
    const rec = this.records.get(fid)
    if (!rec || rec.state !== 'active' || !rec.lease) return
    const token = rec.lease.token
    rec.lastExpiredToken = token
    await this.disposeOne(fid, 'lease-expired')
    this.journal.append('lease-expire', { token, cause }, { fiber_id: fid })
  }

  // --- invoke (idempotent) -------------------------------------------------------
  async invoke(envelope: Envelope): Promise<InvokeResult> {
    if (!envelope.request_id) throw new FiberHostError('request-id-required', 'invoke sans request_id — refusé')
    const rec = this.records.get(envelope.fiber_id)
    if (!rec) throw new UnknownFiberError(envelope.fiber_id)
    // A token whose lease already expired names the cause even after disposal.
    if (envelope.lease_token && envelope.lease_token === rec.lastExpiredToken) throw new LeaseExpiredError(envelope.fiber_id)
    if (rec.state !== 'active' || !rec.lease) throw new StateError(`fiber ${envelope.fiber_id} non active (état ${rec.state})`)
    if (new Date(rec.lease.expires_at).getTime() <= Date.now()) throw new LeaseExpiredError(envelope.fiber_id)
    if (!envelope.lease_token || envelope.lease_token !== rec.lease.token) {
      throw new LeaseRequiredError(envelope.fiber_id)
    }
    if (envelope.deadline && new Date(envelope.deadline).getTime() <= Date.now()) {
      throw new FiberHostError('deadline-exceeded', `deadline dépassée pour ${envelope.request_id}`)
    }
    const hash = payloadHash(envelope.payload ?? {})
    const stored = this.journal.completedReceipt(envelope.request_id)
    if (stored) {
      const storedHash = stored.payload_hash as string | undefined
      if (storedHash && storedHash !== hash) {
        throw new FiberHostError('payload-mismatch', `request_id ${envelope.request_id} rejoué avec un payload différent — refusé`)
      }
      if (envelope.replay_policy === 'replay') {
        throw new FiberHostError('replay-requires-new-id', `request_id ${envelope.request_id} déjà terminé — replay exige un nouveau request_id`)
      }
      return { ...(stored as unknown as InvokeResult), replayed: true }
    }
    if (envelope.callback_url) {
      this.journal.append('receipt', { request_id: envelope.request_id, note: 'rap-deferred', callback_url: envelope.callback_url }, { request_id: envelope.request_id, fiber_id: envelope.fiber_id })
    }
    this.journal.append('invoke-start', { operation: envelope.operation, payload_hash: hash }, { request_id: envelope.request_id, fiber_id: envelope.fiber_id })
    let outcome: { status: string, result: unknown, artefacts: unknown[], errors: string[] }
    try {
      outcome = await rec.transport!.invoke(envelope)
    } catch (err) {
      outcome = { status: 'error', result: null, artefacts: [], errors: [err instanceof Error ? err.message : String(err)] }
    }
    const receipt: InvokeResult = {
      status: outcome.status,
      result: outcome.result,
      artefacts: outcome.artefacts,
      errors: outcome.errors,
      receipt_id: `rcpt-${envelope.request_id}`,
    }
    this.journal.append('invoke-complete', { receipt, payload_hash: hash, operation: envelope.operation }, { request_id: envelope.request_id, fiber_id: envelope.fiber_id })
    return receipt
  }

  // --- health ---------------------------------------------------------------------
  async health(id: string): Promise<HealthReport> {
    const rec = this.records.get(id)
    if (!rec) throw new UnknownFiberError(id)
    if (rec.state !== 'active' || !rec.transport) return { ok: false, detail: `état ${rec.state}` }
    return rec.transport.health()
  }

  // --- rollback & dispose ------------------------------------------------------------
  private async runCleanupSteps(fid: string, steps: Array<() => void | Promise<void>>): Promise<Array<{ step: number, ok: boolean, error?: string }>> {
    const results: Array<{ step: number, ok: boolean, error?: string }> = []
    for (let i = 0; i < steps.length; i++) {
      try {
        await steps[i]()
        results.push({ step: i, ok: true })
        this.journal.append('cleanup', { step: i, ok: true }, { fiber_id: fid })
      } catch (err) {
        const message = err instanceof Error ? err.message : String(err)
        results.push({ step: i, ok: false, error: message })
        this.journal.append('cleanup', { step: i, ok: false, error: message }, { fiber_id: fid })
      }
    }
    return results
  }

  private async rollbackOne(fid: string, reason: string): Promise<{ steps: number, errors: string[] }> {
    const rec = this.records.get(fid)!
    const errors: string[] = []
    let steps = 0
    if (rec.impl?.rollback) {
      try {
        await rec.impl.rollback()
        steps++
      } catch (err) {
        errors.push(err instanceof Error ? err.message : String(err))
      }
    }
    const { reverted, errors: revertErrors } = await this.revertCoeffects(fid)
    errors.push(...revertErrors)
    steps += reverted
    this.journal.append('rollback', { reason, steps, errors }, { fiber_id: fid })
    return { steps, errors }
  }

  async rollback(id: string, reason: string, opts: { terminal?: boolean } = {}): Promise<{ steps: number, errors: string[], state: FiberState }> {
    const rec = this.records.get(id)
    if (!rec) throw new UnknownFiberError(id)
    const { steps, errors } = await this.rollbackOne(id, reason)
    if (opts.terminal) {
      await this.disposeOne(id, 'rollback-terminal')
    } else if (rec.state === 'active') {
      await this.disposeOne(id, 'rollback')
      rec.state = 'dormant'
      rec.lease = undefined
    } else {
      rec.state = 'dormant'
    }
    return { steps, errors, state: rec.state }
  }

  private async disposeOne(fid: string, reason: string): Promise<void> {
    const rec = this.records.get(fid)!
    if (rec.state === 'disposed') return
    rec.state = 'draining'
    if (rec.timer) {
      clearTimeout(rec.timer)
      rec.timer = undefined
    }
    // 1. Cordis fiber disposal (driven by Cordis), then impl.dispose() awaited
    // and journaled here, exactly once.
    if (rec.fiber) {
      try {
        await rec.fiber.dispose()
        this.journal.append('cleanup', { step: 'cordis-fiber-dispose', ok: true }, { fiber_id: fid })
      } catch (err) {
        this.journal.append('cleanup', { step: 'cordis-fiber-dispose', ok: false, error: err instanceof Error ? err.message : String(err) }, { fiber_id: fid })
      }
      rec.fiber = undefined
      if (rec.impl?.dispose) {
        try {
          await rec.impl.dispose()
          this.journal.append('cleanup', { step: 'impl-dispose', ok: true }, { fiber_id: fid })
        } catch (err) {
          this.journal.append('cleanup', { step: 'impl-dispose', ok: false, error: err instanceof Error ? err.message : String(err) }, { fiber_id: fid })
        }
      }
    } else if (rec.transport) {
      try {
        await rec.transport.dispose()
      } catch (err) {
        this.journal.append('cleanup', { step: 'transport-dispose', ok: false, error: err instanceof Error ? err.message : String(err) }, { fiber_id: fid })
      }
    }
    // 2. Declared cleanup steps, in order (they were declared as the fiber's own order).
    if (rec.impl?.cleanupSteps) {
      await this.runCleanupSteps(fid, rec.impl.cleanupSteps)
    }
    // 3. Co-effects reverted in reverse order (exactly once — consumed here).
    const { errors: revertErrors } = await this.revertCoeffects(fid)
    for (const e of revertErrors) {
      this.journal.append('cleanup', { step: 'coeffect-revert', ok: false, error: e }, { fiber_id: fid })
    }
    rec.lease = undefined
    rec.transport = undefined
    rec.state = 'disposed'
  }

  async dispose(id: string): Promise<void> {
    const rec = this.records.get(id)
    if (!rec) throw new UnknownFiberError(id)
    await this.disposeOne(id, 'dispose')
  }

  // --- HMR ---------------------------------------------------------------------------
  async reconcile(roots: Iterable<string>): Promise<{ verdict: string, settled: number, aborted: number, skipped: number, reasons: string[] }> {
    const report = await adapterReconcile(this.ctx, roots)
    this.journal.append('reconcile', { ...report }, {})
    return report
  }

  // --- host shutdown ---------------------------------------------------------------------
  async disposeHost(): Promise<void> {
    if (this.disposed) return
    this.disposed = true
    const actives = [...this.records.entries()]
      .filter(([, r]) => r.state === 'active' || r.state === 'starting' || r.state === 'draining')
      .sort((a, b) => b[1].activationOrder - a[1].activationOrder)
    for (const [fid] of actives) {
      try {
        await this.disposeOne(fid, 'host-shutdown')
      } catch {
        // Shutdown continues through failures; each is journaled in disposeOne.
      }
    }
    try {
      await this.hmrFiber.dispose()
    } catch {
      // HMR already disposed or never started — shutdown continues.
    }
    try {
      await this.ctx.fiber.dispose()
    } catch {
      // Root fiber disposal is best-effort at shutdown.
    }
  }
}

/** Build a host on the real Cordis Context. Crash recovery runs at boot. */
export async function createFiberHost(options: {
  base?: string
  journalDir: string
  coeffectHandlers?: Record<string, CoeffectHandler>
  defaultLeaseTtlMs?: number
}): Promise<AspaceFiberHost> {
  return AspaceFiberHost.create(options)
}
