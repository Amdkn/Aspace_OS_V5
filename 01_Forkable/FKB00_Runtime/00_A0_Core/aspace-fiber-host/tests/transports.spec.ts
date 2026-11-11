import { describe, expect, it, beforeEach, afterEach } from 'vitest'
import { createServer } from 'node:net'
import { createServer as createHttpServer } from 'node:http'
import { unlinkSync } from 'node:fs'
import { join } from 'node:path'
import { RIG_OPS, defaultRigSocketPath } from '../src/transports.ts'
import { createFiberHost } from '../src/index.ts'
import type { AspaceFiberHost } from '../src/index.ts'
import { httpManifest, makeHost, socketManifest, tmpDir } from './helpers.ts'

describe('Transports — unix-socket (Rust) et http-loopback (Python)', () => {
  let dir: string
  let host: AspaceFiberHost

  beforeEach(async () => {
    dir = tmpDir()
    host = await makeHost(dir)
  })

  afterEach(async () => {
    if (host) await host.disposeHost()
  })

  it('H-P1-5 : le client socket parle le protocole JSON-lines de RigInfinity', async () => {
    const sock = join(dir, 'daemon.sock')
    const received: string[] = []
    const server = createServer((conn) => {
      let buf = ''
      conn.on('data', (chunk) => {
        buf += chunk.toString('utf-8')
        let nl: number
        while ((nl = buf.indexOf('\n')) >= 0) {
          const line = buf.slice(0, nl)
          buf = buf.slice(nl + 1)
          received.push(line)
          const req = JSON.parse(line) as Record<string, unknown>
          if (req.op === 'list_sessions') conn.write(JSON.stringify({ ok: true, sessions: [] }) + '\n')
          else if (req.op === 'create_session') conn.write(JSON.stringify({ ok: true, session_id: 's-1' }) + '\n')
          else conn.write(JSON.stringify({ ok: false, error: `unknown op: ${req.op}` }) + '\n')
        }
      })
    })
    await new Promise<void>((r) => server.listen(sock, r))
    try {
      host.register(socketManifest(sock))
      const lease = await host.activate('fiber:a0:test-rust')
      // Santé = list_sessions (il n'y a pas d'op health en amont).
      expect((await host.health('fiber:a0:test-rust')).ok).toBe(true)
      expect(JSON.parse(received[0]!).op).toBe('list_sessions')
      const res = await host.invoke({
        request_id: 'req-sock-1', fiber_id: 'fiber:a0:test-rust', operation: 'create_session',
        lease_token: lease.token, payload: { cwd: '/tmp', model: 'default' },
      })
      expect(res.status).toBe('ok')
      expect((res.result as Record<string, unknown>).session_id).toBe('s-1')
      const createLine = JSON.parse(received[2]!) as Record<string, unknown>
      expect(createLine.op).toBe('create_session')
      expect(createLine.cwd).toBe('/tmp')
      // Op hors table : refusée AVANT tout envoi (le serveur ne reçoit rien de plus),
      // et consignée comme reçu d'erreur (jamais d'exception silencieuse).
      const before = received.length
      const refused = await host.invoke({
        request_id: 'req-sock-2', fiber_id: 'fiber:a0:test-rust', operation: 'explode',
        lease_token: lease.token, payload: {},
      })
      expect(refused.status).toBe('error')
      expect(refused.errors[0]).toMatch(/op inconnue/)
      expect(received.length).toBe(before)
    } finally {
      server.close()
      try {
        unlinkSync(sock)
      } catch {
        // Déjà nettoyé.
      }
    }
  })

  it('H-P1-5 : la table des ops est celle de client.rs (détecteur de dérive)', () => {
    // Verbatim de crates/infinity-daemon/src/client.rs (docblock + dispatch).
    expect([...RIG_OPS]).toEqual(['create_session', 'resume_session', 'list_sessions', 'send_input', 'cleanup_session'])
  })

  it('le chemin de socket par défaut respecte INFINITY_STATE_DIR', () => {
    const saved = process.env.INFINITY_STATE_DIR
    process.env.INFINITY_STATE_DIR = '/tmp/inf-test'
    expect(defaultRigSocketPath()).toBe('/tmp/inf-test/daemon.sock')
    delete process.env.INFINITY_STATE_DIR
    expect(defaultRigSocketPath()).toMatch(/\.infinity\/daemon\.sock$/)
    if (saved !== undefined) process.env.INFINITY_STATE_DIR = saved
  })

  it('H-P1-6 : http-loopback — santé TCP, invoke POST, HTTP 500 consignée en erreur', async () => {
    const posts: Array<Record<string, unknown>> = []
    let failNext = false
    const server = createHttpServer((req, res) => {
      let body = ''
      req.on('data', (c) => { body += c })
      req.on('end', () => {
        posts.push(JSON.parse(body) as Record<string, unknown>)
        if (failNext) {
          res.writeHead(500, { 'content-type': 'application/json' })
          res.end(JSON.stringify({ error: 'boom' }))
          return
        }
        res.writeHead(200, { 'content-type': 'application/json' })
        res.end(JSON.stringify({ id: 'chatcmpl-1', choices: [] }))
      })
    })
    await new Promise<void>((r) => server.listen(0, '127.0.0.1', r))
    const port = (server.address() as { port: number }).port
    try {
      host.register(httpManifest(`http://127.0.0.1:${port}/v1/chat/completions`))
      const lease = await host.activate('fiber:a0:test-python')
      expect((await host.health('fiber:a0:test-python')).ok).toBe(true)
      const ok = await host.invoke({
        request_id: 'req-http-1', fiber_id: 'fiber:a0:test-python', operation: 'chat',
        lease_token: lease.token, payload: { model: 'test', messages: [] },
      })
      expect(ok.status).toBe('ok')
      expect(posts).toHaveLength(1)
      expect(posts[0]!.request_id).toBe('req-http-1')
      failNext = true
      const bad = await host.invoke({
        request_id: 'req-http-2', fiber_id: 'fiber:a0:test-python', operation: 'chat',
        lease_token: lease.token, payload: { model: 'test', messages: [] },
      })
      expect(bad.status).toBe('error')
      expect(bad.errors[0]).toMatch(/HTTP 500/)
    } finally {
      server.close()
    }
  })

  it('H-P1-6 : garde loopback — hôte non loopback rejeté à l’activation', async () => {
    host.register(httpManifest('http://192.168.1.1:31415/v1/chat/completions', { id: 'fiber:a0:test-remote' }))
    await expect(host.activate('fiber:a0:test-remote')).rejects.toThrow(/non loopback/)
    expect(host.get('fiber:a0:test-remote').state).toBe('failed')
  })

  it('H-P1-6 : santé TCP en échec quand rien n’écoute', async () => {
    // Port éphémère fermé : on réserve un port puis on le libère.
    const probe = createHttpServer()
    await new Promise<void>((r) => probe.listen(0, '127.0.0.1', r))
    const port = (probe.address() as { port: number }).port
    await new Promise<void>((r) => probe.close(() => r()))
    // Une seule instance HMR par thread (règle amont) : disposer le host du
    // beforeEach avant d'en créer un second.
    await host.disposeHost()
    const host2 = await createFiberHost({ journalDir: tmpDir() })
    try {
      host2.register(httpManifest(`http://127.0.0.1:${port}/v1/chat/completions`, { id: 'fiber:a0:test-dead' }))
      await expect(host2.activate('fiber:a0:test-dead')).rejects.toThrow(/santé en échec/)
    } finally {
      await host2.disposeHost()
    }
  })
})
