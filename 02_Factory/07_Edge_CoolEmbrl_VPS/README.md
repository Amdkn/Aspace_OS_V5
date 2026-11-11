# `07_Edge_CoolEmbrl_VPS` — Pont de Déploiement Actif vers CoolEmbrl (WSL) & VPS via GitHub Actions

Ce module relie les **5 catégories natives de GitHub Actions** du dépôt public `Amdkn/Aspace_OS_V5` à ton infrastructure locale (**CoolEmbrl WSL2**) et distante (**VPS / Coolify**) :

| Catégorie Native GitHub Actions | Fichier Workflow (`.github/workflows/`) | Rôle Opérationnel |
|---|---|---|
| **1. Deployment** | [`aspace-v5-deploy-edge.yml`](../../.github/workflows/aspace-v5-deploy-edge.yml) | Exécute les gates déterministes puis synchronise via `rsync`/SSH et webhooks vers le **VPS** et **CoolEmbrl Edge**. |
| **2. Continuous Integration** | [`aspace-factory-ci-matrix.yml`](../../.github/workflows/aspace-factory-ci-matrix.yml) | Matrice CI parallèle testant `01_Kernel_Gates`, `02_Holons_578_QualityControl`, `03_Submodules_EGM_Harvester` et `04_Security_OWASP_RigInfinity`. |
| **3. Automation** | [`aspace-egm-jules-dispatcher.yml`](../../.github/workflows/aspace-egm-jules-dispatcher.yml) | Cron toutes les 6h alimentant la file SQLite `00_Memoire/egm_missions.db` et l'orchestrateur `RigInfinity`. |
| **4. Security** | [`aspace-security-owasp-codeql.yml`](../../.github/workflows/aspace-security-owasp-codeql.yml) + [`dependabot.yml`](../../.github/dependabot.yml) | Triage autonome `reviewer-security` (OWASP Top 10, isolation en worktree `sec-<id>`, PR `factory:security`). |
| **5. Pages / Telemetry** | [`aspace-v5-pages-cockpit.yml`](../../.github/workflows/aspace-v5-pages-cockpit.yml) | Génère et publie le snapshot télémétrique du Cockpit (578 Holons + état du démon Cordis). |

## Configuration des Secrets GitHub (`Settings > Secrets and variables > Actions`)
- `VPS_HOST` : IP ou domaine de ton VPS
- `VPS_USER` : Utilisateur SSH (ex. `root` ou `ubuntu`)
- `VPS_SSH_KEY` : Clé privée SSH Ed25519/RSA pour `rsync` et le redémarrage de `:31415`
- `COOLIFY_WEBHOOK_URL` *(optionnel)* : Webhook de déploiement Coolify sur le VPS
- `COOLEMBRL_WEBHOOK_URL` *(optionnel)* : Webhook Tailscale/Cloudflare Tunnel vers ton instance CoolEmbrl WSL
