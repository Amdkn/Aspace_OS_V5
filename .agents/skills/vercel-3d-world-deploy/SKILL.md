---
name: vercel-3d-world-deploy
description: Deploy 3D agent worlds (Three.js, Cubefarm, Agent-Office, City-Office) on Vercel Edge with zero-backend autonomous fallbacks, safe chunking and error boundaries.
version: 1.0.0
platforms: [macos, linux, windows]
metadata:
  hermes:
    tags: [vercel, 3d, threejs, webgl, agentic, cubefarm, agent-office]
    category: deployment
---

# Vercel 3D World Deployment Skill

Deploy, harden and run 3D multiplayer or single-player agent offices and spatial worlds on Vercel Edge/Serverless static hosting without requiring an active local backend daemon or WebSocket swarm.

Inspired by the **Hermes Agent Skills Learning Model** (`NousResearch/hermes-agent`), this skill captures verified operational lessons and deterministic failure modes encountered during the deployments of `cubefarm` and `agent-office`.

---

## When to Use

Use this skill when:
- Deploying Three.js / Canvas / React-Three-Fiber applications (`cubefarm`, `agent-office`, `city-office`, `BlenderWorld`) to Vercel.
- Solving the **"Connecting to swarm server..."** or **"Knocking on the door"** infinite loading locks.
- Diagnosing and fixing the **"Blue/Blank Screen of Death"** (silent React crashes on `#root`).
- Isolating browser client builds from Node-only PTY/WebSocket server backends.
- Packaging standalone preview demonstrations for clients or investors.

---

## Architecture & Progressive Disclosure

```
Level 0: skills_list()          → [vercel-3d-world-deploy]
Level 1: SKILL.md (this file)    → Core mental models, deployment checklist, decision tree & pitfalls
Level 2: Autonomous Fallback    → Injecting compliant WorldSnapshot / WelcomeMsg on WebSocket timeout
```

```
┌──────────────────────────────────────────────────────────────┐
│                    VERCEL STATIC EDGE CDN                    │
│                                                              │
│  [index.html] ──> [Vite Client Bundle (dist)]                │
│                         │                                    │
│       ┌─────────────────┴─────────────────┐                  │
│       ▼                                   ▼                  │
│  [WebSocket Probe]                   [Timeout 1.2s]          │
│       │                                   │                  │
│       ├─► Server Present: Live sync       └─► Server Absent  │
│       └─► Server Offline ─────────────────────┐              │
│                                               ▼              │
│                                   [Inject Autonomous Orbit]  │
│                                               │              │
│       ┌───────────────────────────────────────┴──────────┐   │
│       ▼                                                  ▼   │
│  [Compliant Snapshot State]                      [ErrorBoundary]
│  - Repos + Issues + Previews                     - Catch WebGL/3D
│  - CEO + Agents (Role/Look/Skin)                 - 2D Pocket Fallback
│  - Settings.setupDone: true                                  │
│                                                              │
│  ===> INSTANT 3D RENDERING WITHOUT SERVER DEPENDENCY <===    │
└──────────────────────────────────────────────────────────────┘
```

---

## The 4 Golden Lessons (Cubefarm & Agent-Office Post-Mortem)

### 1. The Autonomous Orbit Fallback Pattern
* **Problem**: Vercel serves static assets and serverless functions; it does not host long-lived persistent WebSocket daemons. If the client unconditionally waits for `/ws`, the UI stays frozen on loading screens (`Connecting to the swarm server...`, `Knocking on the door`).
* **Rule**: Always race the WebSocket connection with a **1.2s – 1.5s timer**. If the socket does not reach `WebSocket.OPEN` within that window, automatically synthesize and dispatch a compliant state snapshot (`snapshot` for Cubefarm, `welcome` for Agent-Office).

### 2. Eliminating the "Blue Screen of Death" (Strict Schema Completeness)
* **Problem**: In Three.js and React 19, reading a property on `undefined` (e.g. `repo.issues.filter`, `repo.preview.status`, `agent.look.skin`) during the render loop causes an unhandled exception. React tears down the entire DOM tree, leaving only the bare CSS background (`#bfe3ff` sky blue).
* **Rule**:
  1. The fallback mock snapshot must satisfy **100% of the TypeScript interface**. Arrays (`issues: []`, `pulls: []`, `held: []`) must never be omitted.
  2. The CEO agent must be explicitly provided under `CEO_ID = 'ceo'` with `role: 'ceo'`.
  3. Set `settings.setupDone = true` so first-run wizards do not hijack the screen when models are pre-instantiated.

### 3. Client/Server Build Isolation
* **Problem**: Running `pnpm run build` or `npm run build` on Vercel often attempts to bundle server-side binaries (`node-pty`, `@xterm/headless`, `selfsigned`), which fail in standard frontend build containers.
* **Rule**:
  1. Create a `vercel.json` pointing specifically to the client build command:
     ```json
     {
       "buildCommand": "pnpm run build:client",
       "outputDirectory": "dist"
     }
     ```
  2. In `vite.config.ts`, verify that `chunkSizeWarningLimit` is elevated (e.g., `2000`) and Three.js / Excalidraw fonts are emitted cleanly.

### 4. React & WebGL Error Boundaries
* **Problem**: Missing WebGL extensions or driver hiccups on mobile/low-end devices result in a frozen canvas.
* **Rule**: Wrap `<Office />` in an `<ErrorBoundary>`. On error, render a clear fallback card offering:
  - `🔄 Reload Office`
  - `📱 Switch to 2D Pocket/Lite Mode`

---

## Standard Fallback Implementation Templates

### A. Cubefarm Template (`client/src/net.ts`)
```typescript
const fallbackTimer = setTimeout(() => {
  if (!settled && !useStore.getState().loaded) {
    settled = true;
    try { socket?.close(); } catch {}
    injectAutonomousOrbit();
  }
}, 1200);
```

### B. Agent-Office Template (`src/client/net.ts`)
```typescript
const fallbackTimer = setTimeout(() => {
  if (!this.up) {
    this.up = true;
    this.statusHandlers.forEach(h => h(true));
    const autonomousWelcome: ServerMsg = {
      t: 'welcome',
      you: 'user-s0',
      peers: [],
      floors: [{ id: 'aspace-lobby', name: 'Aspace Skyline Lobby', floor: 1 }],
      projectsDir: { dir: '', custom: false },
      ice: [],
      chat: [{ from: 'system', name: 'A0-Amadeus', color: '#ff8a5b', text: 'Autonomous Orbit Activated', at: Date.now() }],
      invites: false,
      version: '0.1.0-aspace-v5',
      upgrade: { available: false, latest: '' },
      usage: { promptTokens: 0, completionTokens: 0, costUsd: 0 },
      limits: { maxWorkers: 4 },
      me: { admin: true },
      notify: { sound: false, desktop: false },
      machine: { name: 'Aspace Sovereign Cloud', online: true },
      sky: { time: 12, weather: 'clear' },
      theme: { holiday: 'none' },
      map: { layout: 'standard' },
      prompts: { default: 'aspace' },
      leaveOnMerge: false,
      floor: 'aspace-lobby',
      project: { id: 'aspace-os', name: 'Aspace OS V5' },
      workers: [],
      issues: { items: [], fetchedAt: Date.now(), loading: false },
      pulls: { items: [], fetchedAt: Date.now(), loading: false },
      queue: { tasks: [], maxWorkers: 4 }
    };
    for (const h of this.handlers) h(autonomousWelcome);
  }
}, 1200);
```

---

## Verification & Deterministic Gates
1. **Local Test**: `tsc --noEmit` returns exit code 0.
2. **Preview Test**: Run `vite preview --port 5317` without the server backend running.
3. **Behavioral Acceptance**:
   - The office renders within < 2 seconds.
   - The player avatar can walk (`WASD`).
   - The CEO desk and mission control are visible.
   - The phone (`P`) and Overview (`Tab`) open immediately.
4. **Deterministic Gate**: `pwsh -NoProfile -File 02_Factory/checks.ps1` returns **PASS**.
