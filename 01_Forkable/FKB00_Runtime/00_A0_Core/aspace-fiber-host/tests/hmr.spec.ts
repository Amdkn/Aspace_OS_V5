import { describe, expect, it, beforeEach, afterEach } from 'vitest'
import { writeFileSync } from 'node:fs'
import { join } from 'node:path'
import { pathToFileURL } from 'node:url'
import Loader from '@cordisjs/plugin-loader'
import { createFiberHost } from '../src/index.ts'
import type { AspaceFiberHost } from '../src/index.ts'
import { tmpDir } from './helpers.ts'

/**
 * HMR — un seul fichier (une seule instance HMR par thread, règle amont).
 * Patron repris des tests amont (packages/hmr/tests/reconcile.spec.ts) :
 * Loader avec baseUrl, entry chargée par ctx.loader.create, valeur lue par
 * ctx.bail, modification du fichier puis reconcile explicite.
 */
describe('HMR — réconciliation explicite', () => {
  let dir: string
  let host: AspaceFiberHost
  let entryPath: string

  beforeEach(async () => {
    dir = tmpDir()
    host = await createFiberHost({ journalDir: dir })
    entryPath = join(dir, 'entry.ts')
    writeFileSync(entryPath, `export let value = 'v1'\nexport function apply(ctx) {\n  ctx.on('hmr-test/value', () => value)\n}\n`)
    await host.ctx.plugin(Loader, { baseUrl: pathToFileURL(join(dir, 'base.ts')).href })
    const id = await (host.ctx as any).loader.create({ name: './entry.ts' })
    await (host.ctx as any).loader.store[id].innerFiber.await()
  })

  afterEach(async () => {
    if (host) await host.disposeHost()
  })

  it('H-P1-4 : reconcile applique le module modifié, racines vides = noop', async () => {
    expect((host.ctx as any).bail('hmr-test/value')).toBe('v1')
    writeFileSync(entryPath, `export let value = 'v2'\nexport function apply(ctx) {\n  ctx.on('hmr-test/value', () => value)\n}\n`)
    const report = await host.reconcile([entryPath])
    expect(report.verdict).toBe('applied')
    expect(report.settled).toBeGreaterThanOrEqual(1)
    expect((host.ctx as any).bail('hmr-test/value')).toBe('v2')
    const noop = await host.reconcile([])
    expect(noop.verdict).toBe('noop')
    expect(noop.settled).toBe(0)
  })
})
