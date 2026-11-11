/**
 * Helpers partagés par les tests du host. Aucun test ici (helpers.ts n'est
 * pas collecté par vitest).
 */
import { mkdtempSync } from 'node:fs'
import { tmpdir } from 'node:os'
import { join } from 'node:path'
import { createFiberHost } from '../src/index.ts'
import type { AspaceFiberHost, CoeffectHandler } from '../src/index.ts'

export function tmpDir(): string {
  return mkdtempSync(join(tmpdir(), 'fiber-host-'))
}

export function localManifest(overrides: Record<string, unknown> = {}): Record<string, unknown> {
  return {
    contract_version: '1',
    id: 'fiber:a0:test-local',
    kind: 'service',
    version: '0.1.0',
    source: { repo: 'Amdkn/Aspace_OS_V5', frozen_commit: '1947fab40869adecba38b1500cec9f77e74fd4b7', license: 'MIT', provenance: 'test P1' },
    entry: { language: 'ts', path: 'tests/helpers.ts' },
    adapter: { version: '0.1.0', commit: '1947fab40869adecba38b1500cec9f77e74fd4b7' },
    capabilities: ['test_local'],
    requires: [],
    coeffects: [],
    permissions: { network: 'none', shell: false, files: [], secrets: [] },
    transport: { type: 'in-process', ops: ['invoke', 'health'] },
    lifecycle: { start: 'start', health: 'health', lease: { ttl_ms: 300_000 }, dispose: 'dispose', rollback: 'rollback' },
    state_owner: 'test P1',
    holdouts: ['H-P1-10'],
    ...overrides,
  }
}

export function socketManifest(socketPath: string, overrides: Record<string, unknown> = {}): Record<string, unknown> {
  return {
    ...localManifest({ id: 'fiber:a0:test-rust', kind: 'agent', transport: { type: 'unix-socket', socket_path: socketPath, ops: ['create_session', 'resume_session', 'list_sessions', 'send_input', 'cleanup_session'] } }),
    entry: { language: 'rust', path: 'crates/infinity-daemon/src/main.rs' },
    ...overrides,
  }
}

export function httpManifest(url: string, overrides: Record<string, unknown> = {}): Record<string, unknown> {
  return {
    ...localManifest({ id: 'fiber:a0:test-python', kind: 'agent', transport: { type: 'http-loopback', url, ops: ['chat'] } }),
    entry: { language: 'python', path: '01_Forkable/FKB00_Runtime/00_A0_Core/a0_egm_bridge.py' },
    ...overrides,
  }
}

export async function makeHost(journalDir: string, coeffects: Record<string, CoeffectHandler> = {}): Promise<AspaceFiberHost> {
  return createFiberHost({ journalDir, coeffectHandlers: coeffects })
}

export const sleep = (ms: number): Promise<void> => new Promise((r) => setTimeout(r, ms))
