import { describe, expect, it } from 'vitest'
import { readFileSync } from 'node:fs'
import { validateManifest } from '../src/manifest.ts'
import { localManifest } from './helpers.ts'

describe('AspaceFiberManifest v1', () => {
  it('valide le manifeste du host lui-même (non-régression)', () => {
    const m = validateManifest(JSON.parse(readFileSync(new URL('../../aspace-fiber-host.manifest.json', import.meta.url), 'utf-8')))
    expect(m.id).toBe('fiber:a0:aspace-fiber-host')
    expect(m.capabilities).toContain('cordis_fiber_host')
  })
  it('valide un manifeste complet', () => {
    const m = validateManifest(localManifest())
    expect(m.contract_version).toBe('1')
    expect(m.id).toBe('fiber:a0:test-local')
  })

  it('rejette contract_version ≠ 1', () => {
    expect(() => validateManifest(localManifest({ contract_version: '2' }))).toThrow(/contract_version/)
  })

  it('rejette un id hors motif', () => {
    expect(() => validateManifest(localManifest({ id: 'cordis' }))).toThrow(/id/)
    expect(() => validateManifest(localManifest({ id: 'fiber:a0:Bad_Name' }))).toThrow(/id/)
  })

  it('rejette un champ manquant en le nommant', () => {
    const bad = localManifest()
    delete bad.kind
    expect(() => validateManifest(bad)).toThrow(/kind/)
    const bad2 = localManifest()
    delete bad2.transport
    expect(() => validateManifest(bad2)).toThrow(/transport/)
  })

  it('rejette un transport inconnu et un ttl invalide', () => {
    expect(() => validateManifest(localManifest({ transport: { type: 'pigeon', ops: [] } }))).toThrow(/transport\.type/)
    const bad = localManifest()
    ;(bad.lifecycle as Record<string, unknown>).lease = { ttl_ms: 0 }
    expect(() => validateManifest(bad)).toThrow(/ttl_ms/)
  })

  it('exige socket_path pour unix-socket et url pour http-loopback', () => {
    expect(() => validateManifest(localManifest({ transport: { type: 'unix-socket', ops: [] } }))).toThrow(/socket_path/)
    expect(() => validateManifest(localManifest({ transport: { type: 'http-loopback', ops: [] } }))).toThrow(/url/)
  })

  it('rejette une racine non objet', () => {
    expect(() => validateManifest('non')).toThrow(/racine/)
    expect(() => validateManifest(null)).toThrow(/racine/)
  })
})
