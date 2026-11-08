---
type: concept
id: wargame-riginfinity-cordis-daemon
title: "Wargame Au-Delà d'Argon : Hyperviseur Cordis × Automaton Runtime × Fusion RigInfinity (Rust) × Reviewer-Security OWASP"
status: active
updated: 2026-11-08
owners:
  - "human:amdkn"
  - "aspace:a0:amadeus"
related:
  - "02_Factory/01_Kernel_Gates/daemon_supervisor_cordis.py"
  - "02_Factory/02_Holons_578_QualityControl/openrig_demo_qc_578.py"
  - "02_Factory/04_Security_OWASP_RigInfinity/reviewer_security_harness.py"
  - "01_Forkable/FKB00_Runtime/01_Holo_TriptyqueCore/RigInfinity"
---

# Wargame Au-Delà des Traces d'Argon : Cordis Daemon, Automaton Runtime & Fusion `RigInfinity`

## 1. Verdict Architectural sur « Agent Zero + Cordis en Daemon + Automaton en Runtime »

### Le Piège Mortel du *Daemon Sprawl* (Ce qu'il ne faut surtout pas faire)
Presque tous les modules forkés d'A'Space OS V5 possèdent leur propre daemon natif :
- `hydro-project/infinity` possède `crates/infinity-daemon/src/main.rs` (Rust, RAP protocol, `mcp_proxy.rs`),
- `mvschwarz/openrig` possède `packages/daemon/src/` (TypeScript/Hono, SQLite migrations, `context-packs-src`),
- `herdr-core` possède son daemon PTY Rust,
- `deepseek-harness` (`dsh`) possède son serveur Cordis `:3081`,
- `openclaw` possède son daemon 24/7,
- `agent-zero` possède son serveur Web/Docker.

**Verdict Wargame** :
- **NON** si chaque sous-module lance son daemon en parallèle au démarrage : 15+ daemons concurrents créent des conflits de ports, saturent la RAM/WSL et violent l'unicité d'écriture SQLite (`writerLock`).
- **OUI (Architecture Optimale Retenue)** si et seulement si on applique la **Hiérarchie d'Hypervision à 3 Couches (`daemon_supervisor_cordis.py`)** :
  1. **`Cordis` = Hyperviseur & Daemon Maître Unique (`PID 1` d'Aspace)** : Seul bus permanent en mémoire. Tous les daemons des sous-modules (`RigInfinity`, `herdr-core`, `dsh`, `openclaw`, `agent-zero`) sont déclarés comme des **`ManagedDaemonFiber` à démarrage paresseux (*Lazy Spawn*)**.
  2. **`Automaton` = Gouverneur Métabolique en Runtime (Tick Engine & Baux)** : Tourne à l'intérieur du bus maître pour délivrer les baux (`LeaseToken` TTL 300s), vérifier l'état homéostatique `A1-Beth` (`GREEN | ORANGE | RED | HALT_LD03 | HALT_LD04`) et gérer la réserve d'inférence à 3 paliers.
  3. **`Agent Zero (A0)` = Cortex Cognitif Éphémère (Mode EGM)** : N'est jamais laissé en boucle infinie ; il est instancié à la demande pour une mission Poisson Rouge bornée, puis libéré via la pile de nettoyage réversible (`dispose()`).

---

## 2. Fusion d'`OpenRig` et d'`Infinity` en `Amdkn/RigInfinity` (Paradigme « De Go vers Rust »)

Le sous-module souverain **`01_Forkable/FKB00_Runtime/01_Holo_TriptyqueCore/RigInfinity`** (`https://github.com/Amdkn/RigInfinity`) fusionne :
1. **La Rigueur de Contrôle Qualité d'`OpenRig` (`packages/daemon` + `demo/`)** :
   - `context-packs-src`, `policies` (*leak-guard*), `specs` et `demo` appliqués comme **Standard Quality Control** des **578 Holons** (`02_Factory/02_Holons_578_QualityControl/openrig_demo_qc_578.py`).
2. **Le Déterminisme Prédictible en Rust d'`Infinity` (`crates/infinity-daemon/src/`)** :
   - Passage métaphorique et structurel **« de Go (goroutines implicites à mémoire partagée) vers Rust (Ownership & Borrowing exclusif, `TypedThreadId`, Pattern Matching exhaustif sans course critique) »**.
   - Chaque worktree ou ressource GWS ne peut avoir qu'**un seul emprunteur actif** (`active_holon_borrower`) muni d'un `FencingToken` monotone.
3. **Le Harness `reviewer-security` Intégré (`02_Factory/04_Security_OWASP_RigInfinity/reviewer_security_harness.py`)** :
   - **Triggers automatiques** : Dependabot (`.github/dependabot.yml`), CodeQL & Secret Scanning (`.github/workflows/aspace-security-owasp-codeql.yml`).
   - **Audit OWASP Top 10** (`A01` à `A10`).
   - **Isolation en Worktree dédié** : `02_Factory/04_Security_OWASP_RigInfinity/sec-worktrees/sec-<id>`.
   - **Validation déterministe** : `02_Factory/checks.ps1` + création de PR prioritaire marquée `factory:security`.

---

## 3. Taxonomie Structurée de `02_Factory/` en 6 Catégories

Au lieu de déverser les scripts en vrac à la racine de `02_Factory/`, l'usine logicielle est organisée en 6 catégories :
1. `01_Kernel_Gates/` — Superviseur de daemons Cordis/Automaton et gates sémantiques.
2. `02_Holons_578_QualityControl/` — Générateur des 578 Holons et Standard Quality Control OpenRig Demo × Rust.
3. `03_Submodules_EGM_Harvester/` — Mutation `aspace-v5-native` et synchronisation des forks `Amdkn/*`.
4. `04_Security_OWASP_RigInfinity/` — Harness `reviewer-security`, audit OWASP Top 10 et worktrees isolés `sec-<id>`.
5. `05_3DWorlds_Fractal_Deploy/` — Déploiement spatial `City Office` (`CubeFarm × Agent-Office`), montage fractal et dashboard.
6. `06_Jobs_Tickets/` — Historique des tickets et exécutions d'agents.
