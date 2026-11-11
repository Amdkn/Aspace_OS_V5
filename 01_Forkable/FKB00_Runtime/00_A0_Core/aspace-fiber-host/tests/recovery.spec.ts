import { describe, expect, it } from 'vitest'
import { spawn } from 'node:child_process'
import { writeFileSync } from 'node:fs'
import { join } from 'node:path'
import { fileURLToPath } from 'node:url'
import { Journal } from '../src/journal.ts'
import { createFiberHost } from '../src/index.ts'
import { localManifest, makeHost, sleep, tmpDir } from './helpers.ts'

const journalTsPath = fileURLToPath(new URL('../src/journal.ts', import.meta.url))

describe('Reprise après crash', () => {
  it('H-P1-3 : terminé non rejoué, orphelin abandonné et compensé au redémarrage', async () => {
    const dir = tmpDir()
    const host = await makeHost(dir)
    let invokes = 0
    let rollbacks = 0
    host.register(localManifest(), {
      invoke: () => { invokes++; return 'done' },
      rollback: () => { rollbacks++ },
    })
    const lease = await host.activate('fiber:a0:test-local')
    const done = await host.invoke({ request_id: 'req-done', fiber_id: 'fiber:a0:test-local', operation: 'invoke', lease_token: lease.token, payload: { n: 1 } })
    expect(done.status).toBe('ok')
    expect(invokes).toBe(1)
    await host.disposeHost()
    // Crash simulé : un invoke-start sans invoke-complete, écrit dans le journal
    // exactement comme le host l'aurait écrit avant d'exécuter (append synchrone).
    const journal = new Journal(dir)
    journal.append('invoke-start', { operation: 'invoke', payload_hash: 'deadbeef' }, { request_id: 'req-orphan', fiber_id: 'fiber:a0:test-local' })
    journal.append('lease-grant', { token: 'lease-stale', holder: 'test', ttl_ms: 100, expires_at: new Date(Date.now() - 1000).toISOString() }, { fiber_id: 'fiber:a0:test-local' })

    // Redémarrage sur le même journal.
    const host2 = await makeHost(dir)
    try {
      host2.register(localManifest(), {
        invoke: () => { invokes++; return 'done' },
        rollback: () => { rollbacks++ },
      })
      const lease2 = await host2.activate('fiber:a0:test-local')
      // La compensation de l'orphelin a tourné à l'activation.
      expect(rollbacks).toBe(1)
      // Le terminé n'est pas rejoué.
      const replayed = await host2.invoke({ request_id: 'req-done', fiber_id: 'fiber:a0:test-local', operation: 'invoke', lease_token: lease2.token, payload: { n: 1 } })
      expect(replayed.replayed).toBe(true)
      expect(invokes).toBe(1)
      // Le journal porte la reprise.
      const events = new Journal(dir).readAll().map((e) => e.type)
      expect(events).toContain('crash-recovery')
      expect(events).toContain('lease-expire')
    } finally {
      await host2.disposeHost()
    }
  })

  it('H-P1-3 : SIGKILL réel — le journal survit et la reprise compense', async () => {
    const dir = tmpDir()
    // L'enfant n'importe que le Journal (zéro dépendance externe) : il écrit
    // les lignes qu'un host tué aurait laissées (invoke-start + bail, sans
    // invoke-complete), puis reste en vie jusqu'au SIGKILL. Le parent, lui,
    // fait tourner le vrai host sur le même journal et vérifie la reprise.
    const childScript = join(dir, 'killed-child.mjs')
    // Node 24 type-strippe le .ts à l'import : l'enfant n'a besoin d'aucun
    // chargeur (tsx) ni de node_modules — il n'importe que le Journal.
    writeFileSync(childScript, `
import { Journal } from ${JSON.stringify(journalTsPath)}
const j = new Journal(${JSON.stringify(dir)})
j.append('invoke-start', { operation: 'invoke', payload_hash: 'killhash' }, { request_id: 'req-killed', fiber_id: 'fiber:a0:test-local' })
j.append('lease-grant', { token: 'lease-killed', holder: 'killed-child', ttl_ms: 100, expires_at: new Date(Date.now() + 100).toISOString() }, { fiber_id: 'fiber:a0:test-local' })
console.log('ready')
setInterval(() => {}, 1000)
`)
    const child = spawn(process.execPath, [childScript], { stdio: ['ignore', 'pipe', 'pipe'] })
    let childOut = ''
    child.stdout!.on('data', (c) => { childOut += c.toString() })
    try {
      await new Promise<void>((resolve, reject) => {
        const timer = setTimeout(() => reject(new Error('enfant non prêt')), 15000)
        const check = setInterval(() => {
          if (childOut.includes('ready')) {
            clearTimeout(timer)
            clearInterval(check)
            resolve()
          }
        }, 50)
      })
      child.kill('SIGKILL')
      await new Promise<void>((r) => child.on('close', () => r()))
      expect(child.signalCode).toBe('SIGKILL')
      await sleep(250) // le bail de 100 ms est expiré à la reprise
      const host = await makeHost(dir)
      try {
        let rollbacks = 0
        host.register(localManifest(), { rollback: () => { rollbacks++ } })
        await host.activate('fiber:a0:test-local')
        expect(rollbacks).toBe(1) // orphelin compensé
        const events = new Journal(dir).readAll()
        expect(events.some((e) => e.type === 'crash-recovery' && e.request_id === 'req-killed')).toBe(true)
        expect(events.some((e) => e.type === 'lease-expire' && e.detail.token === 'lease-killed')).toBe(true)
      } finally {
        await host.disposeHost()
      }
    } finally {
      if (!child.killed) child.kill('SIGKILL')
    }
  })

  it('H-P1-3 : orphelin sans rollback déclaré → marqué non compensé, jamais effacé', async () => {
    const dir = tmpDir()
    const journal = new Journal(dir)
    journal.append('invoke-start', { operation: 'invoke', payload_hash: 'x' }, { request_id: 'req-nocomp', fiber_id: 'fiber:a0:test-local' })
    const host = await makeHost(dir)
    try {
      host.register(localManifest(), {}) // pas de rollback
      await host.activate('fiber:a0:test-local')
      const events = new Journal(dir).readAll()
      const rb = events.find((e) => e.type === 'rollback' && e.detail.compensated === false)
      expect(rb).toBeTruthy()
      expect(events.some((e) => e.type === 'crash-recovery')).toBe(true)
    } finally {
      await host.disposeHost()
    }
  })
})
