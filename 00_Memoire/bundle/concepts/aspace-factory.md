---
type: Architecture
title: "Aspace Software Factory V5 (DeepSeek Superagent + Multi-Harness GitHub Factory)"
tags: [software-factory, deepseek-dsh, github-actions, adw, multi-agent, herdr, orca, wikillm]
---
# Aspace Software Factory V5

## 1. Purge finale d'OpenWiki & Remplacement CI
- Le workflow `.github/workflows/openwiki-update.yml` (qui appelait `openwiki` et le modèle inexistant `gpt-5.6-terra`) a été **définitivement supprimé**.
- La gate déterministe `factory/checks.ps1` (exécutée localement et dans `.github/workflows/factory-gate.yml`) échoue immédiatement si `.github/workflows/openwiki-update.yml` ou toute référence active à `openwiki` / `gpt-5.6-terra` réapparaît dans `.github/workflows/`.

## 2. Fusion des 12 Sources d'Inspiration

| Source | Concept Clé Intégré dans Aspace Factory V5 | Fichiers d'Implémentation |
|---|---|---|
| **1. `deepseek-ai/dsh-superagent-prototype`** *(Cœur prioritaire)* | Philosophie *"Minimum human attention, maximum value"*, chaîne `Source -> Trigger -> Thread -> Eval -> Ticket (Mandate) -> Assignment -> Executor -> Channel`, Subscriptions sans re-Eval, 7 stages ordonnés par priorité d'attention humaine, règle d'1 seule question concrète, préfixe `This is by an automated agent, not a human`, et Panel à 3 questions (`005-panel.md`). CLI `dsh` intégré. | `factory/config.json`, `factory/factory.ps1`, `factory/dashboard.html`, `.claude/agents/intake-assessor.md` |
| **2. `coleam00/ai-software-factory`** | Pipeline d'agents spécialisés (`Intake Assessor -> Spec Writer -> Builder -> 4 Reviewers -> Approver`) + auto-merge par label `factory:ready-to-merge` et escalation `factory:needs-human`. | `.claude/agents/*.md`, `.github/workflows/factory-dispatch.yml` |
| **3. `coleam00/factory-mission-control`** | Tableau de bord visuel en temps réel découplé des repos cibles. | `factory/dashboard.html`, `factory/state.json` |
| **4. `coleam00/Archon`** | Boucles de workflows déterministes (ADW) séparant la planification (`spec-writer`) de l'exécution (`builder`). | `factory/factory.ps1`, `.claude/agents/spec-writer.md` |
| **5. `EricTechPro/super-board`** | Matrice de routage multi-modèles et multi-rôles avec quorum d'approbation avant merge. | `factory/config.json` (`reviewSwarm`, `harnesses`) |
| **6. `PromtEngineer/software-factory`** | Portes de qualité multi-étapes (Security, Code, UX/UI, Drift) avant intégration. | `.github/workflows/factory-gate.yml`, `factory/checks.ps1` |
| **7. `leonvanzyl/skills`** | Architecture modulaire par `SKILL.md` partagée entre tous les agents (`.claude/skills/` et `.agents/skills/`). | `.claude/skills/aspace-factory/SKILL.md`, `.agents/skills/aspace-factory/SKILL.md` |
| **8. `zazencodes/software-factory-claude-code`** | Agents atomiques invocables en ligne de commande ou sous-agents Claude Code avec TDD strict. | `.claude/agents/builder.md`, `.claude/agents/reviewer-code.md` |
| **9. `mvschwarz/openrig`** | Rig d'ingénierie auto-réparateur (`doctor.ps1` + gates locales). | `.vscode/doctor.ps1`, `factory/checks.ps1` |
| **10. `google-research/harness2`** | Protocole d'évaluation déterministe inter-harness (Claude, DeepSeek `dsh`, Codex, Pi, Gemini/Antigravity). | `factory/checks.ps1`, `factory/config.json` |
| **11. `disler/super-simple-software-factory`** | Colonne vertébrale ADW minimaliste et ultra-lisible (`Trigger -> Isolate -> Build -> Validate -> Ship`). | `factory/factory.ps1` |
| **12. `pi.dev/packages/pi-durable-subagents`** | Persistance SQLite (`.factory/factory.db`) des tickets, mandats, événements et abonnements pour survivre aux redémarrages de sessions. | `.factory/factory.db`, `factory/factory.ps1` |

## 3. Couverture Complète des Surfaces GitHub
1. **Issues** : Formulaires structurés `.github/ISSUE_TEMPLATE/factory-task.yml`, `factory-bug.yml`, `factory-epic.yml` (avec champ `Mandate` et sélection du Harness `dsh`, `claude`, `codex`, `pi`, `hc`, `orca`).
2. **Pull Requests** : `.github/PULL_REQUEST_TEMPLATE.md` avec contrat de vérification des 4 Reviewers et `CODEOWNERS` (`@Amdkn`).
3. **Discussions** : Routées dans `.github/ISSUE_TEMPLATE/config.yml` comme source d'idéation amont avant transformation en Ticket (`Source: github:discussion`).
4. **Actions** :
   - `factory-gate.yml` : Gate déterministe (OpenWiki purge, DOX/WikiLLM, OKF v0.2, Append-Only `log.md`, Secret scan).
   - `factory-dispatch.yml` : Triage autonome (`Eval -> Ticket`), attribution du label `factory:claimed` et Auto-Merge (`factory:ready-to-merge`).
   - `factory-wiki-insights.yml` : Compilation des métriques WikiLLM & Graphify dans `$GITHUB_STEP_SUMMARY`.
5. **Projects** : Synchronisation des 7 stages DeepSeek Superagent avec les labels GitHub (`factory:claimed`, `factory:needs-human`, `factory:ready-to-merge`, `factory:blocked`).
6. **Wiki** : Remplacé par **WikiLLM + OKF v0.2** (`00_Memoire/bundle/`) maintenu directement par les agents et vérifié à chaque PR par `factory-gate.yml`.
7. **Security and Quality** :
   - `.github/SECURITY.md` (active la Security Policy sur GitHub).
   - `.github/dependabot.yml` (active Dependabot sur GitHub Actions, pip et npm).
   - `factory/factory.ps1 setup-github -Repo <owner/repo>` active par API REST GitHub (`gh api`) les **Dependabot Alerts** (`vulnerability-alerts`) et le **Private Vulnerability Reporting** (`private-vulnerability-reporting`).
8. **Insights** : Tableau de bord local `factory/dashboard.html` + résumés d'exécution GitHub Actions (`factory-wiki-insights.yml`).
