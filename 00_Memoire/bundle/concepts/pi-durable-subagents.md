---
type: Architecture
title: "Pi 1.5.0, Pi Durable & pi-durable-subagents (Architecture Agnostique V5)"
tags: [pi, pi-durable, subagents, sqlite, idempotency, writer-lock, deepseek-superagent, multi-harness]
---
# Pi 1.5.0, Pi Durable & `pi-durable-subagents` dans Aspace OS V5

## 1. Mise à jour Pi 1.5.0 (`@earendil-works/pi-coding-agent@1.5.0`)
- **Nouveautés clés de Pi 1.5.0 intégrées dans V5** :
  - Validation unifiée des schémas d'outils via `@earendil-works/pi-schema` avec coercition automatique (y compris pour les outils MCP et les extensions important `Type` depuis `@earendil-works/pi-ai`).
  - Streaming incrémental ultra-rapide (réutilisation de la coloration syntaxique et des blocs Markdown sans re-parsing à chaque delta).
  - Gestion native des changelogs d'extensions condensée via `"collapseChangelog": true` dans `.pi/settings.json` et `~/.pi/agent/settings.json`.
  - Résolution de la collision de skills entre `.agents/skills` et `.claude/skills` : Pi découvre automatiquement `.agents/skills/` (12 skills actifs sans aucun warning de collision).

## 2. Synthèse Architecturale : `earendil.com/posts/pi-durable/` + `pi-durable-subagents`

| Innovation | Source | Implémentation Agnostique dans Aspace OS V5 |
|---|---|---|
| **1. Découplage Compute / Storage & Checkpoints avant exécution** | `earendil.com/posts/pi-durable/` | Chaque workflow, étape (`durable_steps`), ticket et événement est commité dans `02_Factory/factory.sqlite` **avant** son exécution. Si un processus meurt ou redémarre, `02_Factory/factory.ps1 subagents -Action resume` reprend exactement au dernier checkpoint. |
| **2. Idempotence stricte par `requestId` & `replay: "safe"`** | `pi-durable` & `pi-durable-subagents` | Chaque soumission porte un `request_id` unique dans `durable_workflows`. Un retry après crash retourne l'exécution existante (`idempotentReplay: true`) au lieu de dupliquer le travail. |
| **3. Worktree Writer Lock (`writerLock`)** | `pi-durable-subagents` | Table `writer_locks` dans `02_Factory/factory.sqlite` : un seul agent avec `writer: true` (`edit`/`write`) peut modifier un worktree donné à la fois. Les autres écrivains passent en `waiting for writer lock: <root> held by <wid>/<key>`, tandis que les reviewers (`writer: false`) s'exécutent immédiatement en parallèle. |
| **4. Pool de Modèles & Failover (`modelPool` & `exhaustedPatterns`)** | `pi-durable-subagents` | En cas d'épuisement d'un modèle/provider, bascule dans la même session sur la chaîne `freellmapi/auto` → `claude-sonnet-4-5` → `qwen3.8-max` → `gemini-3.8-flash` → `deepseek-v4-flash`. |
| **5. Steer Ordonné & Remplacement Out-of-Order** | `pi-durable-subagents` | `subagents -Action send -To <wid>/<key> -Kind steer -Message "..."` : si deux steers arrivent avant application, le plus récent remplace le précédent ; `notify` s'empile sans écraser. |
| **6. Arbre de Propriété (`ownership`) & `background: true`** | `earendil.com/posts/pi-durable/` | Les tâches `foreground` sont liées à la tâche parente et s'annulent de bas en haut (`abort`) ; les tâches `background: true` (`hc run --bg --outlive-parent`) survivent à la fin du tour. |
| **7. Documents Atomiques (`defineDoc`) & `handoff` + `search_history`** | `earendil.com/posts/pi-durable/` | Tables `durable_docs` et `handoffs` dans `02_Factory/factory.sqlite` : un agent peut faire un `handoff` vers une fenêtre de contexte neuve tout en interrogeant tout l'historique antérieur avec `search_history`. |

## 3. Exploitation par Tous les Harnesses (Zéro Cloisonnement)
Bien que le package npm original `pi-durable-subagents` se désactive sur Windows natif hors WSL, l'implémentation d'Aspace OS V5 dans `.pi/extensions/aspace-factory.ts` et `02_Factory/factory.ps1` fonctionne **nativement sur Windows** et est partagée entre :
- **Pi 1.5.0** : outils natifs `subagents`, `handoff`, `search_history`, `factory_status`, `factory_gate`, `factory_intake` + commandes `/subagents` et `/factory`.
- **DeepSeek Harness (`dsh`) & DeepSeek Superagent** : via `02_Factory/factory.ps1 subagents` et les presets `dsh-superagent-worker` / `dsh-superagent-router` (timeout foreground 5s → background job).
- **OpenCode 1.19.5** : via `opencode.json` (commandes `/subagents-status`, `/subagents-run`, `/subagents-resume` et les 8 agents Factory).
- **Claude Code, Codex, Antigravity, Herdr (`hc`) & Orca (`orca`)** : via le skill universel `pi-durable-subagents` (`.agents/skills/pi-durable-subagents/SKILL.md` et `.claude/skills/pi-durable-subagents/SKILL.md`) et `02_Factory/factory.ps1`.
