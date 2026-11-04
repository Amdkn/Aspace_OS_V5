---
name: aspace-factory
description: Operate the Aspace Software Factory (DeepSeek Superagent + ADW + Multi-Harness GitHub Factory). Use when running autonomous issue-to-merge pipelines, checking factory status, running deterministic gates, dispatching across dsh/hc/orca/gh, or configuring GitHub Security & Quality.
---
# Aspace Software Factory Skill (`aspace-factory`)

Ce skill permet à n'importe quel agent (**Claude Code**, **DeepSeek `dsh`**, **Codex**, **Pi**, **Herdr `hc`**, **Orca `orca`**, **Antigravity**) d'opérer l'**Aspace Software Factory V5**.

## 1. Commandes Principales (`factory/factory.ps1`)

```powershell
# Afficher le Mission Control (3 questions DeepSeek Superagent) + mettre à jour factory/state.json
pwsh -NoProfile -File factory/factory.ps1 status

# Exécuter les 5 Gates déterministes (OpenWiki purge, DOX/WikiLLM, OKF v0.2, Append-Only, Secrets)
pwsh -NoProfile -File factory/factory.ps1 gate

# Créer un Ticket avec Mandat dans la spine SQLite (.factory/factory.db)
pwsh -NoProfile -File factory/factory.ps1 intake -Title "Titre" -Mandate "Mandat" -Source "github:issue"

# Configurer les labels Factory, Dependabot alerts et Private Vulnerability Reporting sur GitHub
pwsh -NoProfile -File factory/factory.ps1 setup-github -Repo Amdkn/Aspace-OS-V5
```

## 2. Modèle de Domaine (DeepSeek Superagent `001-domain.md`)
`Source -> Trigger -> Thread -> Eval -> Ticket (Mandate) -> Assignment -> Executor -> Channel`

- **7 Stages ordonnés par priorité d'attention humaine** :
  1. `person/delivery` (Résultat prêt)
  2. `person/answer` (Une seule question concrète posée à l'humain)
  3. `person/review` (PR à haut risque demandant validation)
  4. `person/blocked, failed` (Bloqué par dépendance externe)
  5. `working/queued` (Follow-up en file d'attente via Subscription)
  6. `idle` (Terminé/En veille)
  7. `working` (Exécution autonome en cours)

## 3. Orchestration Multi-Harness (Qui fait quoi ?)
- **DeepSeek Harness (`dsh`)** : Prototype Superagent concret (`dsh -p "<mandate>" --allow-all`).
- **Herdr (`hc`)** : Cockpit multi-terminaux persistant (`hc spawn --template worker` / `hc spawn --template reviewer` / `hc wait`).
- **Orca (`orca`)** : Isolation en worktrees Git + DAG de tâches (`orca worktree create` / `orca task create`).
- **Claude Code (`.claude/agents/`)** : 8 sous-agents spécialisés (`intake-assessor`, `spec-writer`, `builder`, `reviewer-code`, `reviewer-security`, `reviewer-ux-ui`, `reviewer-drift`, `approver`).
- **GitHub (`gh` + `.github/workflows/`)** :
  - `factory-gate.yml` : Gate CI déterministe sur chaque PR/Push.
  - `factory-dispatch.yml` : Triage d'Issues/Commentaires (`/factory`, `factory:ready`) et Auto-Merge (`factory:ready-to-merge`).
  - `factory-wiki-insights.yml` : Insights WikiLLM & Graphify dans `$GITHUB_STEP_SUMMARY`.
