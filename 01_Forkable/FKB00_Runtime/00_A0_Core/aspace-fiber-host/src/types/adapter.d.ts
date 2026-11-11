/**
 * Minimal type stub for @aspace/cordis-adapter (see cordis.d.ts — the vitest
 * suite verifies the real surface against the frozen submodule sources).
 */
import type { Context, Fiber } from './cordis.d.ts'

export const ADAPTER_VERSION: string
export const PINNED_CORDIS_COMMIT: string
export const PINNED_HMR_VERSION: string
export const PINNED_HMR_SURFACE: readonly string[]

export type ReconcileVerdict = 'applied' | 'partial' | 'aborted' | 'skipped' | 'noop'

export interface ReconcileReport {
  verdict: ReconcileVerdict
  settled: number
  aborted: number
  skipped: number
  reasons: string[]
}

export function createAspaceApp(options?: { base?: string }): Promise<{ ctx: Context, hmr: Fiber }>
export function reconcile(ctx: Context, roots: Iterable<string>): Promise<ReconcileReport>
export function hasHmr(ctx: Context): boolean

declare const Hmr: unknown
export { Hmr }

declare const _default: { createAspaceApp: typeof createAspaceApp, reconcile: typeof reconcile, hasHmr: typeof hasHmr }
export default _default
