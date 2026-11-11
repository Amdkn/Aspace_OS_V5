import { describe, expect, it, beforeEach, afterEach } from 'vitest'
import { createFiberHost } from '../src/index.ts'
import type { AspaceFiberHost } from '../src/index.ts'
import { localManifest, makeHost, sleep, tmpDir } from './helpers.ts'

describe('AspaceFiberHost — cycle de vie local', () => {
  let dir: string
  let host: AspaceFiberHost

  beforeEach(async () => {
    dir = tmpDir()
    host = await makeHost(dir)
  })

  afterEach(async () => {
    if (host) await host.disposeHost()
  })

  it('H-P1-10 : démarrage paresseux, santé alive, arrêt propre', async () => {
    let started = 0
    let disposed = 0
    host.register(localManifest(), {
      start: () => { started++ },
      dispose: () => { disposed++ },
    })
    expect(started).toBe(0) // paresseux : register ne démarre rien
    expect(host.get('fiber:a0:test-local').state).toBe('dormant')
    const lease = await host.activate('fiber:a0:test-local')
    expect(started).toBe(1)
    expect(lease.token).toMatch(/^lease-fiber:a0:test-local-\d+$/)
    expect((await host.health('fiber:a0:test-local')).ok).toBe(true)
    await host.dispose('fiber:a0:test-local')
    expect(disposed).toBe(1)
    expect(host.get('fiber:a0:test-local').state).toBe('disposed')
  })

  it('H-P1-1 : le bail expire réellement et le nettoyage s’exécute', async () => {
    let cleaned = 0
    host.register(localManifest({ lifecycle: { start: 'start', health: 'health', lease: { ttl_ms: 150 }, dispose: 'dispose' } }), {
      cleanupSteps: [() => { cleaned++ }],
    })
    await host.activate('fiber:a0:test-local')
    // Sweep explicite avec une horloge avancée : c'est le sweep (pas le
    // minuteur) qui expire le bail ici.
    const report = await host.sweepExpired(Date.now() + 1000)
    expect(report.expired).toContain('fiber:a0:test-local')
    expect(host.get('fiber:a0:test-local').state).toBe('disposed')
    expect(cleaned).toBe(1) // le nettoyage a été EXÉCUTÉ, pas nommé
  })

  it('H-P1-1 : le minuteur expire le bail sans sweep explicite', async () => {
    host.register(localManifest({ lifecycle: { start: 'start', health: 'health', lease: { ttl_ms: 120 }, dispose: 'dispose' } }), {})
    await host.activate('fiber:a0:test-local')
    await sleep(350)
    expect(host.get('fiber:a0:test-local').state).toBe('disposed')
  })

  it('H-P1-2 : request_id rejoué retourne le reçu sans ré-exécuter', async () => {
    let invokes = 0
    host.register(localManifest(), {
      invoke: () => { invokes++; return { n: invokes } },
    })
    const lease = await host.activate('fiber:a0:test-local')
    const env = { request_id: 'req-1', fiber_id: 'fiber:a0:test-local', operation: 'invoke', lease_token: lease.token, payload: { a: 1 } }
    const first = await host.invoke(env)
    expect(first.status).toBe('ok')
    expect(first.receipt_id).toBe('rcpt-req-1')
    const second = await host.invoke(env)
    expect(second.replayed).toBe(true)
    expect(second.receipt_id).toBe('rcpt-req-1')
    expect(invokes).toBe(1) // pas de ré-exécution
  })

  it('H-P1-2 : même request_id, payload différent → refus ; replay → nouveau id exigé', async () => {
    host.register(localManifest(), { invoke: () => 'ok' })
    const lease = await host.activate('fiber:a0:test-local')
    const base = { request_id: 'req-2', fiber_id: 'fiber:a0:test-local', operation: 'invoke', lease_token: lease.token, payload: { a: 1 } }
    await host.invoke(base)
    await expect(host.invoke({ ...base, payload: { a: 2 } })).rejects.toThrow(/payload-mismatch/)
    await expect(host.invoke({ ...base, replay_policy: 'replay' })).rejects.toThrow(/replay-requires-new-id/)
  })

  it('invoke sans bail valide est refusé', async () => {
    host.register(localManifest(), { invoke: () => 'ok' })
    const lease = await host.activate('fiber:a0:test-local')
    await expect(host.invoke({ request_id: 'r', fiber_id: 'fiber:a0:test-local', operation: 'invoke', payload: {} })).rejects.toThrow(/lease-required/)
    await expect(host.invoke({ request_id: 'r', fiber_id: 'fiber:a0:test-local', operation: 'invoke', lease_token: 'lease-faux', payload: {} })).rejects.toThrow(/lease-required/)
    // Bail expiré : refus même avec le bon token.
    host.register(localManifest({ id: 'fiber:a0:test-short', lifecycle: { start: 'start', health: 'health', lease: { ttl_ms: 80 }, dispose: 'dispose' } }), { invoke: () => 'ok' })
    const short = await host.activate('fiber:a0:test-short')
    await sleep(150)
    await expect(host.invoke({ request_id: 'r2', fiber_id: 'fiber:a0:test-short', operation: 'invoke', lease_token: short.token, payload: {} })).rejects.toThrow(/lease-expired/)
    expect(lease.token).toBeTruthy()
  })

  it('deadline dépassée → refus sans exécution', async () => {
    let invokes = 0
    host.register(localManifest(), { invoke: () => { invokes++ } })
    const lease = await host.activate('fiber:a0:test-local')
    await expect(host.invoke({
      request_id: 'r-dl', fiber_id: 'fiber:a0:test-local', operation: 'invoke',
      lease_token: lease.token, deadline: new Date(Date.now() - 1000).toISOString(), payload: {},
    })).rejects.toThrow(/deadline-exceeded/)
    expect(invokes).toBe(0)
  })

  it('renewLease prolonge, refuse l’expiré et le plafond', async () => {
    host.register(localManifest({ lifecycle: { start: 'start', health: 'health', lease: { ttl_ms: 200 }, dispose: 'dispose' } }), {})
    const first = await host.activate('fiber:a0:test-local')
    const renewed = await host.renewLease('fiber:a0:test-local')
    expect(renewed.renewals).toBe(1)
    expect(new Date(renewed.expires_at).getTime()).toBeGreaterThanOrEqual(new Date(first.expires_at).getTime())
    await expect(host.renewLease('fiber:a0:test-local', 200 * 10 + 1)).rejects.toThrow(/lease-cap/)
    await sleep(450)
    await expect(host.renewLease('fiber:a0:test-local')).rejects.toThrow(/lease-expired/)
  })

  it('H-P1-7 : rollback exécute dans l’ordre inverse, erreurs consignées sans blocage', async () => {
    const order: string[] = []
    const coeffects = {
      c1: { apply: () => { order.push('apply-c1') }, revert: () => { order.push('revert-c1') } },
      c2: { apply: () => { order.push('apply-c2') }, revert: () => { order.push('revert-c2'); throw new Error('c2-revert-boom') } },
    }
    // Une seule instance HMR par thread (règle amont) : disposer le host du
    // beforeEach avant d'en créer un second.
    await host.disposeHost()
    const host2 = await createFiberHost({ journalDir: tmpDir(), coeffectHandlers: coeffects })
    try {
      host2.register(localManifest({ coeffects: ['c1', 'c2'] }), {
        rollback: () => { order.push('rollback-impl') },
      })
      await host2.activate('fiber:a0:test-local')
      expect(order).toEqual(['apply-c1', 'apply-c2'])
      const report = await host2.rollback('fiber:a0:test-local', 'test')
      // rollback impl d'abord, puis co-effets en ordre inverse ; l'échec de c2
      // n'empêche pas c1 d'être révoqué.
      expect(order).toEqual(['apply-c1', 'apply-c2', 'rollback-impl', 'revert-c2', 'revert-c1'])
      expect(report.errors).toHaveLength(1)
      expect(report.errors[0]).toMatch(/c2-revert-boom/)
      expect(report.state).toBe('dormant')
      // Réactivable après rollback non terminal.
      await host2.activate('fiber:a0:test-local')
      expect(host2.get('fiber:a0:test-local').state).toBe('active')
    } finally {
      await host2.disposeHost()
    }
  })

  it('H-P1-8 : dépendances dans l’ordre topologique, cycle et manque refusés', async () => {
    const started: string[] = []
    const mk = (id: string, requires: string[]) => {
      host.register(localManifest({ id, requires }), { start: () => { started.push(id) } })
    }
    mk('fiber:a0:dep-b', [])
    mk('fiber:a0:dep-c', [])
    mk('fiber:a0:dep-a', ['fiber:a0:dep-b', 'fiber:a0:dep-c'])
    await host.activate('fiber:a0:dep-a')
    expect(started).toEqual(['fiber:a0:dep-b', 'fiber:a0:dep-c', 'fiber:a0:dep-a'])
  })

  it('H-P1-8 : cycle refusé avant tout démarrage', async () => {
    const started: string[] = []
    host.register(localManifest({ id: 'fiber:a0:cyc-x', requires: ['fiber:a0:cyc-y'] }), { start: () => { started.push('x') } })
    host.register(localManifest({ id: 'fiber:a0:cyc-y', requires: ['fiber:a0:cyc-x'] }), { start: () => { started.push('y') } })
    await expect(host.activate('fiber:a0:cyc-x')).rejects.toThrow(/cycle/)
    expect(started).toEqual([])
  })

  it('H-P1-8 : dépendance manquante refusée, rien ne démarre', async () => {
    const started: string[] = []
    host.register(localManifest({ id: 'fiber:a0:need-missing', requires: ['fiber:a0:absent'] }), { start: () => { started.push('x') } })
    await expect(host.activate('fiber:a0:need-missing')).rejects.toThrow(/dépendance manquante/)
    expect(started).toEqual([])
  })

  it('activation concurrente du même id : un seul démarrage, même bail', async () => {
    let started = 0
    host.register(localManifest(), { start: async () => { await sleep(50); started++ } })
    const [a, b] = await Promise.all([host.activate('fiber:a0:test-local'), host.activate('fiber:a0:test-local')])
    expect(started).toBe(1)
    expect(a.token).toBe(b.token)
  })

  it('activation partielle : la fiber démarrée est repliée', async () => {
    let rolledBack = 0
    let disposed = 0
    host.register(localManifest({ id: 'fiber:a0:good' }), {
      start: () => {},
      rollback: () => { rolledBack++ },
      dispose: () => { disposed++ },
    })
    host.register(localManifest({ id: 'fiber:a0:bad', requires: ['fiber:a0:good'] }), {
      start: () => { throw new Error('boom-start') },
    })
    await expect(host.activate('fiber:a0:bad')).rejects.toThrow(/boom-start/)
    expect(rolledBack).toBe(1)
    expect(disposed).toBe(1)
    expect(host.get('fiber:a0:good').state).toBe('disposed')
    expect(host.get('fiber:a0:bad').state).toBe('failed')
  })
})
