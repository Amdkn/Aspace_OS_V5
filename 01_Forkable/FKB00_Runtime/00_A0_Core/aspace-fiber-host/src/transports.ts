/**
 * @aspace/fiber-host — transports.
 *
 * Three transports, one envelope. The wire formats are pinned to the sources
 * read at Discover time:
 * - unix-socket: RigInfinity client protocol — JSON-lines, one request per
 *   line, one JSON reply per line (crates/infinity-daemon/src/client.rs).
 *   Ops: create_session, resume_session, list_sessions, send_input,
 *   cleanup_session. No `health` op exists upstream: health is `list_sessions`
 *   expecting {"ok": true}. Default socket: $INFINITY_STATE_DIR/daemon.sock,
 *   else ~/.infinity/daemon.sock (lib.rs socket_path()).
 * - http-loopback: POST the envelope as JSON to the EGM gateway
 *   (http://127.0.0.1:31415/v1/chat/completions, a0_egm_bridge.py).
 *   Health is a bare TCP connect (proves the gateway listens, sends nothing).
 *   Loopback guard: any host other than 127.0.0.1 / ::1 is rejected.
 * - in-process: direct call of the implementation handed at registration.
 * RAP is out of P1: callback_url is carried through and ignored with a
 * recorded warning (rap-deferred); async delivery arrives in P2.
 */
import { connect, createConnection } from 'node:net'
import { homedir } from 'node:os'
import { join } from 'node:path'
import { TransportError } from './errors.ts'
import type { Envelope } from './host.ts'

/** RigInfinity client ops, verbatim from client.rs (drift detector: tests compare). */
export const RIG_OPS = ['create_session', 'resume_session', 'list_sessions', 'send_input', 'cleanup_session'] as const
export type RigOp = (typeof RIG_OPS)[number]

export function defaultRigSocketPath(): string {
  const dir = process.env.INFINITY_STATE_DIR
  if (dir && dir.length > 0) return join(dir, 'daemon.sock')
  return join(homedir(), '.infinity', 'daemon.sock')
}

export interface Transport {
  health(): Promise<{ ok: boolean, detail: string }>
  invoke(envelope: Envelope): Promise<{ status: string, result: unknown, artefacts: unknown[], errors: string[] }>
  dispose(): Promise<void>
}

function isLoopbackHost(host: string): boolean {
  return host === '127.0.0.1' || host === '::1' || host === 'localhost'
}

/** One JSON-lines request/response round-trip over a Unix socket. */
export function jsonLinesRoundTrip(socketPath: string, request: Record<string, unknown>, timeoutMs = 5000): Promise<Record<string, unknown>> {
  return new Promise((resolve, reject) => {
    const socket = connect(socketPath)
    let buf = ''
    let done = false
    const timer = setTimeout(() => {
      if (done) return
      done = true
      socket.destroy()
      reject(new TransportError(`unix-socket: délai dépassé (${timeoutMs} ms) sur ${socketPath}`))
    }, timeoutMs)
    socket.on('error', (err) => {
      if (done) return
      done = true
      clearTimeout(timer)
      reject(new TransportError(`unix-socket: ${socketPath} — ${err.message}`))
    })
    socket.on('data', (chunk) => {
      buf += chunk.toString('utf-8')
      const nl = buf.indexOf('\n')
      if (nl < 0) return
      if (done) return
      done = true
      clearTimeout(timer)
      const line = buf.slice(0, nl)
      socket.end()
      try {
        resolve(JSON.parse(line) as Record<string, unknown>)
      } catch {
        reject(new TransportError(`unix-socket: réponse non JSON sur ${socketPath} : ${line.slice(0, 120)}`))
      }
    })
    socket.on('connect', () => {
      socket.write(JSON.stringify(request) + '\n')
    })
  })
}

export class UnixSocketTransport implements Transport {
  readonly socketPath: string
  constructor(socketPath?: string) {
    const p = socketPath ?? defaultRigSocketPath()
    if (!p.startsWith('/') || p.includes('\0')) {
      throw new TransportError(`unix-socket: chemin absolu exigé, reçu ${JSON.stringify(socketPath)}`)
    }
    this.socketPath = p
  }

  async health(): Promise<{ ok: boolean, detail: string }> {
    try {
      const reply = await jsonLinesRoundTrip(this.socketPath, { op: 'list_sessions' })
      return reply.ok === true
        ? { ok: true, detail: 'list_sessions ok' }
        : { ok: false, detail: `list_sessions non ok : ${JSON.stringify(reply).slice(0, 200)}` }
    } catch (err) {
      return { ok: false, detail: err instanceof Error ? err.message : String(err) }
    }
  }

  async invoke(envelope: Envelope): Promise<{ status: string, result: unknown, artefacts: unknown[], errors: string[] }> {
    if (!RIG_OPS.includes(envelope.operation as RigOp)) {
      throw new TransportError(`unix-socket: op inconnue "${envelope.operation}" — refusée avant envoi (ops : ${RIG_OPS.join(', ')})`)
    }
    const reply = await jsonLinesRoundTrip(this.socketPath, { op: envelope.operation, ...(envelope.payload as Record<string, unknown>) })
    if (reply.ok === true) return { status: 'ok', result: reply, artefacts: [], errors: [] }
    return { status: 'error', result: reply, artefacts: [], errors: [String(reply.error ?? 'unknown error')] }
  }

  async dispose(): Promise<void> {
    // No persistent connection: nothing to close.
  }
}

export class HttpLoopbackTransport implements Transport {
  readonly url: string
  private readonly host: string
  private readonly port: number
  constructor(url: string) {
    let parsed: URL
    try {
      parsed = new URL(url)
    } catch {
      throw new TransportError(`http-loopback: URL invalide ${JSON.stringify(url)}`)
    }
    if (parsed.protocol !== 'http:') throw new TransportError(`http-loopback: http: exigé, reçu ${parsed.protocol}`)
    if (!isLoopbackHost(parsed.hostname)) {
      throw new TransportError(`http-loopback: hôte non loopback rejeté : ${parsed.hostname}`)
    }
    this.url = url
    this.host = parsed.hostname === 'localhost' ? '127.0.0.1' : parsed.hostname
    this.port = Number(parsed.port)
    if (!this.port) throw new TransportError(`http-loopback: port exigé dans ${url}`)
  }

  /** Bare TCP connect: proves the gateway listens without sending anything. */
  async health(): Promise<{ ok: boolean, detail: string }> {
    return new Promise((resolve) => {
      const socket = createConnection({ host: this.host, port: this.port })
      const timer = setTimeout(() => {
        socket.destroy()
        resolve({ ok: false, detail: `tcp connect délai dépassé (${this.host}:${this.port})` })
      }, 5000)
      socket.on('connect', () => {
        clearTimeout(timer)
        socket.end()
        resolve({ ok: true, detail: `tcp ${this.host}:${this.port} joignable` })
      })
      socket.on('error', (err) => {
        clearTimeout(timer)
        resolve({ ok: false, detail: err.message })
      })
    })
  }

  async invoke(envelope: Envelope): Promise<{ status: string, result: unknown, artefacts: unknown[], errors: string[] }> {
    const res = await fetch(this.url, {
      method: 'POST',
      headers: { 'content-type': 'application/json' },
      body: JSON.stringify(envelope),
      signal: AbortSignal.timeout(5000),
    })
    const text = await res.text()
    let body: unknown = text
    try {
      body = JSON.parse(text)
    } catch {
      // Non-JSON body: keep the raw text.
    }
    if (!res.ok) return { status: 'error', result: body, artefacts: [], errors: [`HTTP ${res.status}`] }
    return { status: 'ok', result: body, artefacts: [], errors: [] }
  }

  async dispose(): Promise<void> {
    // Stateless: nothing to close.
  }
}

export interface InProcessImpl {
  start?: () => void | Promise<void>
  health?: () => { ok: boolean, detail: string } | Promise<{ ok: boolean, detail: string }>
  invoke?: (envelope: Envelope) => unknown | Promise<unknown>
  dispose?: () => void | Promise<void>
  rollback?: () => void | Promise<void>
  cleanupSteps?: Array<() => void | Promise<void>>
}

/** A local fiber: the implementation is handed at registration, called directly. */
export class InProcessTransport implements Transport {
  constructor(private readonly impl: InProcessImpl) {}

  async health(): Promise<{ ok: boolean, detail: string }> {
    if (this.impl.health) return this.impl.health()
    return { ok: true, detail: 'alive' }
  }

  async invoke(envelope: Envelope): Promise<{ status: string, result: unknown, artefacts: unknown[], errors: string[] }> {
    if (!this.impl.invoke) return { status: 'ok', result: null, artefacts: [], errors: [] }
    const result = await this.impl.invoke(envelope)
    return { status: 'ok', result, artefacts: [], errors: [] }
  }

  async dispose(): Promise<void> {
    if (this.impl.dispose) await this.impl.dispose()
  }
}
