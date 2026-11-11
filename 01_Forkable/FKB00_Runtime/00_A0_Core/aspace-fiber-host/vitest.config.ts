import { resolve, dirname } from 'node:path'
import { fileURLToPath } from 'node:url'
import { defineConfig } from 'vitest/config'

const here = dirname(fileURLToPath(import.meta.url))
const cordisDir = resolve(here, '..', 'cordis', 'packages')
const nm = resolve(here, 'node_modules')

// Tests resolve the REAL upstream sources from the frozen submodule (exact gel
// content), never a registry copy: cordis, hmr, loader, include, adapter.
// The upstream sources' own registry deps (cosmokit, schemastery, ...) live in
// this package's node_modules (declared explicitly: npm does not install the
// dependencies of file: linked packages), so they are aliased too — the
// submodule tree stays pristine (no node_modules inside it).
export default defineConfig({
  test: {
    environment: 'node',
    testTimeout: 30000,
    sequence: { shuffle: false },
    // HMR needs Node internals: the flag must reach the vitest WORKER
    // processes (config key: test.execArgv — poolOptions.forks.execArgv is
    // ignored by vitest 4; verified by debug spec printing process.execArgv).
    pool: 'forks',
    execArgv: ['--expose-internals'],
  },
  resolve: {
    alias: [
      { find: /^cordis$/, replacement: resolve(cordisDir, 'core', 'src', 'index.ts') },
      { find: /^@cordisjs\/plugin-hmr$/, replacement: resolve(cordisDir, 'hmr', 'src', 'index.ts') },
      { find: /^@cordisjs\/plugin-loader$/, replacement: resolve(cordisDir, 'loader', 'src', 'index.ts') },
      { find: /^@cordisjs\/plugin-include$/, replacement: resolve(cordisDir, 'include', 'src', 'index.ts') },
      { find: /^@aspace\/cordis-adapter$/, replacement: resolve(cordisDir, 'aspace-cordis-adapter', 'src', 'index.ts') },
      { find: /^cosmokit$/, replacement: resolve(nm, 'cosmokit') },
      { find: /^schemastery$/, replacement: resolve(nm, 'schemastery') },
      { find: /^@babel\/code-frame$/, replacement: resolve(nm, '@babel', 'code-frame') },
      { find: /^@standard-schema\/spec$/, replacement: resolve(nm, '@standard-schema', 'spec') },
      { find: /^node-addon-require-builtin$/, replacement: resolve(nm, 'node-addon-require-builtin') },
    ],
  },
})
