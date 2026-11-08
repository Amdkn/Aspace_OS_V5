# `02_Factory` — A'Space OS V5 Software & Security Factory (Structurée en 6 Catégories)

Ce répertoire contient l'usine logicielle autonome d'**A'Space OS V5**, organisée en **6 catégories spécialisées** tout en conservant à la racine les 4 points d'entrée constitutionnels (`factory.ps1`, `checks.ps1`, `semantic_gate.py`, `config.json`).

---

## Architecture par Catégories

### 1. [`01_Kernel_Gates/`](./01_Kernel_Gates) — Hyperviseur de Daemons (`Cordis × Automaton`) & Gates Noyau
* [`daemon_supervisor_cordis.py`](./01_Kernel_Gates/daemon_supervisor_cordis.py) — Hyperviseur unique résolvant le *Daemon Sprawl* : `Cordis` en Daemon Maître (`PID 1`), `Automaton` en Runtime de baux, et tous les sous-daemons (`RigInfinity`, `herdr-core`, `dsh`, `openclaw`, `agent-zero`) gérés comme Fibers paresseuses avec emprunt exclusif de style Rust (`borrow_fiber_rust_style`) et nettoyage réversible (`release_and_dispose_fiber`).

### 2. [`02_Holons_578_QualityControl/`](./02_Holons_578_QualityControl) — Standard Quality Control des 578 Holons (`OpenRig Demo × Rust`)
* [`openrig_demo_qc_578.py`](./02_Holons_578_QualityControl/openrig_demo_qc_578.py) — Applique la méthodologie Quality Control des agents Demo d'`OpenRig` et le déterminisme algorithmique de style Rust (`RigInfinityQualityContract`, `FencingToken`, `context_pack_sha256`, `leak_guard`) aux 578 Holons d'`Areas OS`.
* [`scaffold-578-holons.py`](./02_Holons_578_QualityControl/scaffold-578-holons.py) — Générateur déterministe des 8 fichiers canoniques (`README.md`, `SOUL.md`, `AGENTS.md`, `CONTRACTS.md`, `CAPABILITIES.md`, `RUNBOOK.md`, `STATE.md`, `MEMORY.md`) et du plan `jules-burst-100-missions.md`.

### 3. [`03_Submodules_EGM_Harvester/`](./03_Submodules_EGM_Harvester) — Mutation `aspace-v5-native` & Synchronisation des Forks `Amdkn/*`
* [`mutate-and-push-forks.py`](./03_Submodules_EGM_Harvester/mutate-and-push-forks.py) — Sort les sous-modules du mode `detached HEAD`, injecte `aspace-plugin.json` sur la branche `aspace-v5-native` et pousse vers `Amdkn/*`.
* [`sync-a0-sovereign-factory.ps1`](./03_Submodules_EGM_Harvester/sync-a0-sovereign-factory.ps1) — Orchestrateur de forks pour le noyau `A0`.
* [`sync-wargame-forks.ps1`](./03_Submodules_EGM_Harvester/sync-wargame-forks.ps1) — Synchronisation des forks Wargame & ML.

### 4. [`04_Security_OWASP_RigInfinity/`](./04_Security_OWASP_RigInfinity) — Triage Autonome `reviewer-security` & OWASP Top 10
* [`reviewer_security_harness.py`](./04_Security_OWASP_RigInfinity/reviewer_security_harness.py) — Agent autonome déclenché par Dependabot (`.github/dependabot.yml`), CodeQL et Secret Scanning (`.github/workflows/aspace-security-owasp-codeql.yml`) :
  1. Déclenchement automatique (*Triggers*),
  2. Audit **OWASP Top 10** (`A01`..`A10`),
  3. Isolation dans un worktree dédié sous `04_Security_OWASP_RigInfinity/sec-worktrees/sec-<id>`,
  4. Validation automatisée (`checks.ps1` / `semantic_gate.py`),
  5. Création de PR prioritaire marquée `factory:security`.

### 5. [`05_3DWorlds_Fractal_Deploy/`](./05_3DWorlds_Fractal_Deploy) — Déploiement Spatial 3D & Montage Fractal
* [`deploy-city-orbit-and-fractal.ps1`](./05_3DWorlds_Fractal_Deploy/deploy-city-orbit-and-fractal.ps1) — Déploiement `City Office` (`CubeFarm × Agent-Office`).
* [`mount-fractal.ps1`](./05_3DWorlds_Fractal_Deploy/mount-fractal.ps1) — Montage des couches fractales `0L..20L`.
* [`dashboard.html`](./05_3DWorlds_Fractal_Deploy/dashboard.html) — Cockpit visuel de la Software Factory.

### 6. [`06_Jobs_Tickets/`](./06_Jobs_Tickets) — Historique des Tickets & Mandats d'Exécution
* Contient les traces et artefacts des tickets traités par l'usine (`tkt-*`).
