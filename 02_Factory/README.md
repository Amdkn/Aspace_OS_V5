# `02_Factory` — A'Space OS V5 Software, Security & Edge Deployment Factory (7 Catégories)

Ce répertoire contient l'usine logicielle autonome d'**A'Space OS V5**, organisée en **7 catégories spécialisées** tout en conservant à la racine les 4 points d'entrée constitutionnels (`factory.ps1`, `checks.ps1`, `semantic_gate.py`, `config.json`).

---

## Matrice des 5 Catégories Natives GitHub Actions (`.github/workflows/`)

| Catégorie GitHub Actions | Workflow Actif | Cible dans `02_Factory/` |
|---|---|---|
| **Deployment** | [`.github/workflows/aspace-v5-deploy-edge.yml`](../.github/workflows/aspace-v5-deploy-edge.yml) | [`07_Edge_CoolEmbrl_VPS/`](./07_Edge_CoolEmbrl_VPS) |
| **Continuous Integration** | [`.github/workflows/aspace-factory-ci-matrix.yml`](../.github/workflows/aspace-factory-ci-matrix.yml) | [`01_Kernel_Gates/`](./01_Kernel_Gates) & [`02_Holons_578_QualityControl/`](./02_Holons_578_QualityControl) |
| **Automation** | [`.github/workflows/aspace-egm-jules-dispatcher.yml`](../.github/workflows/aspace-egm-jules-dispatcher.yml) | [`03_Submodules_EGM_Harvester/`](./03_Submodules_EGM_Harvester) |
| **Security** | [`.github/workflows/aspace-security-owasp-codeql.yml`](../.github/workflows/aspace-security-owasp-codeql.yml) | [`04_Security_OWASP_RigInfinity/`](./04_Security_OWASP_RigInfinity) |
| **Pages / Telemetry** | [`.github/workflows/aspace-v5-pages-cockpit.yml`](../.github/workflows/aspace-v5-pages-cockpit.yml) | [`05_3DWorlds_Fractal_Deploy/`](./05_3DWorlds_Fractal_Deploy) |

---

## Architecture par Catégories (`01` à `07`)

### 1. [`01_Kernel_Gates/`](./01_Kernel_Gates) — Hyperviseur de Daemons (`Cordis × Automaton`) & Gates Noyau
* [`daemon_supervisor_cordis.py`](./01_Kernel_Gates/daemon_supervisor_cordis.py) — Hyperviseur unique résolvant le *Daemon Sprawl* : `Cordis` en Daemon Maître (`PID 1`), `Automaton` en Runtime de baux, et tous les sous-daemons (`RigInfinity`, `herdr-core`, `dsh`, `openclaw`, `agent-zero`) gérés comme Fibers paresseuses avec emprunt exclusif de style Rust (`borrow_fiber_rust_style`) et nettoyage réversible (`release_and_dispose_fiber`).

### 2. [`02_Holons_578_QualityControl/`](./02_Holons_578_QualityControl) — Standard Quality Control des 578 Holons (`OpenRig Demo × Rust`)
* [`openrig_demo_qc_578.py`](./02_Holons_578_QualityControl/openrig_demo_qc_578.py) — Applique la méthodologie Quality Control des agents Demo d'`OpenRig` et le déterminisme algorithmique de style Rust (`RigInfinityQualityContract`, `FencingToken`, `context_pack_sha256`, `leak_guard`) aux 578 Holons d'`Areas OS`.
* [`scaffold-578-holons.py`](./02_Holons_578_QualityControl/scaffold-578-holons.py) — Générateur déterministe des 8 fichiers canoniques et du plan `jules-burst-100-missions.md`.

### 3. [`03_Submodules_EGM_Harvester/`](./03_Submodules_EGM_Harvester) — Mutation `aspace-v5-native` & Synchronisation des Forks `Amdkn/*`
* [`mutate-and-push-forks.py`](./03_Submodules_EGM_Harvester/mutate-and-push-forks.py) — Sort les sous-modules du mode `detached HEAD`, injecte `aspace-plugin.json` sur la branche `aspace-v5-native` et pousse vers `Amdkn/*`.
* [`sync-a0-sovereign-factory.ps1`](./03_Submodules_EGM_Harvester/sync-a0-sovereign-factory.ps1) & [`sync-wargame-forks.ps1`](./03_Submodules_EGM_Harvester/sync-wargame-forks.ps1).

### 4. [`04_Security_OWASP_RigInfinity/`](./04_Security_OWASP_RigInfinity) — Triage Autonome `reviewer-security` & OWASP Top 10
* [`reviewer_security_harness.py`](./04_Security_OWASP_RigInfinity/reviewer_security_harness.py) — Agent autonome déclenché par Dependabot, CodeQL et Secret Scanning (Audit OWASP Top 10 + worktree isolé `sec-<id>` + PR `factory:security`).

### 5. [`05_3DWorlds_Fractal_Deploy/`](./05_3DWorlds_Fractal_Deploy) — Déploiement Spatial 3D & Montage Fractal
* [`deploy-city-orbit-and-fractal.ps1`](./05_3DWorlds_Fractal_Deploy/deploy-city-orbit-and-fractal.ps1), [`mount-fractal.ps1`](./05_3DWorlds_Fractal_Deploy/mount-fractal.ps1) & [`dashboard.html`](./05_3DWorlds_Fractal_Deploy/dashboard.html).

### 6. [`06_Jobs_Tickets/`](./06_Jobs_Tickets) — Historique des Tickets & Mandats d'Exécution
* Contient les traces et artefacts des tickets traités par l'usine (`tkt-*`).

### 7. [`07_Edge_CoolEmbrl_VPS/`](./07_Edge_CoolEmbrl_VPS) — Synchronisation CoolEmbrl (WSL2) & VPS via GitHub Actions
* [`sync_coolembrl_and_vps.py`](./07_Edge_CoolEmbrl_VPS/sync_coolembrl_and_vps.py) — Orchestrateur de synchronisation et d'audit des 5 catégories de workflows GitHub Actions vers CoolEmbrl WSL et le VPS distant.
