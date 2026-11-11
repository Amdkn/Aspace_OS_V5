/**
 * Minimal type stubs for the upstream Cordis surface the host touches.
 *
 * These exist so `tsc --noEmit` checks OUR code without pulling the whole
 * upstream fork sources (which need the fork's own tsconfig and node_modules)
 * into the check. The REAL surface is verified at runtime by the vitest
 * suite, which imports the frozen submodule sources directly (vitest.config.ts
 * aliases). If a stub drifts from reality, the suite fails first.
 */
export class Fiber {
  dispose(): Promise<void> {
    throw new Error('stub — runtime only')
  }
}

export class Context {
  fiber!: Fiber
  plugin(..._args: unknown[]): Promise<Fiber> {
    throw new Error('stub — runtime only')
  }

  effect(_fn: () => (() => void) | void): void {
    throw new Error('stub — runtime only')
  }
}
