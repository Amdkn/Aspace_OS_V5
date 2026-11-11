---
type: concept
id: a0-cordis-recursive-factory
title: "Noyau Souverain A0 : Micro-Noyau Cordis × Agent-Zero × Tri-Horizon RSI"
status: active
updated: 2026-11-08
owners:
  - "human:amdkn"
  - "aspace:a0:amadeus"
related:
  - "01_Forkable/FKB00_Runtime/00_A0_Core/a0_recursive_factory.py"
  - "01_Forkable/FKB01_Inference/03_Inference_FreeCloud/aspace_freecloud_gateway.py"
  - "02_Factory/sync-a0-sovereign-factory.ps1"
---

# Noyau Souverain A0 (`Agent-Zero × Cordis × Automaton × OpenRig × Infinity`)

## 1. Loi Fondamentale : Paradigme « Fork-Mutant + Micro-Noyau Cordis »
Dans `Amdkn/Aspace_OS_V5`, chaque dépôt externe est forké sous `https://github.com/Amdkn/<repo>` et relié en sous-module Git souverain. Le cœur d'`agent0ai/agent-zero` (`00_A0_Core/agent-zero`) est transmuté par :
1. **Bus Spatio-Temporel Cordis (`cordiverse/cordis` + `deepseek-ai/deepseek-harness`)** : chaque capacité (inférence, mémoire, monde 3D, harness) est encapsulée dans une `CordisFiber` dotée d'effets réversibles (`cleanup_stack`) et de co-effets réactifs (`PENDING` sans crash lors d'un hot-swap).
2. **Triptyque Métabolique (`01_Holo_TriptyqueCore`)** :
   - `automaton` : Réserve d'inférence structurée à 3 paliers, baux de survie et budget.
   - `openrig` : Lignage généalogique typé de chaque sous-agent enfant.
   - `infinity` : Passage à l'échelle jusqu'à 75 000 micro-agents frugaux.
3. **Moteur minimaliste Pi (`earendil-works/pi`)** : 4 primitives atomiques (`Read`, `Write`, `Edit`, `Bash`) et arbre de sessions durable.

## 2. Architecture de Récursivité à 3 Horizons (`a0_recursive_factory.py`)
| Horizon | Cadence | Moteurs & Dépôts | Garantie Formelle |
|---|---|---|---|
| **Horizon 1 (Court Terme — Intra-Tâche)** | Seconde / Tour | `PrimeIntellect-ai/prime-agent` (`rlm.spawn`, `/refine`, REPL persistant) | Prompt système immuable ; rollback instantané sur snapshot si le score régresse. |
| **Horizon 2 (Moyen Terme — Inter-Sessions)** | Heure / Fin de Ticket | `google/adk-recipes` (AQuA) + `ashutoshsinghpr7/wikiskill` (arXiv:2608.27454) | Séparation en 4 rôles (*Worker, Note-Taker, Playbook Writer, Strict Manager*) + Holdout Set ($\delta \ge 1.7\%$). |
| **Horizon 3 (Long Terme — Nocturne 00h–05h)** | Nuit / Cycle 12WY | `google-research/dream-rsi` + `google-research/rrsi` | Exploration arborescente hors-ligne à 0 $ ($\beta$) et mutation dans un worktree Git isolé validé par `02_Factory/checks.ps1`. |

## 3. Mono-Gateway FreeCloud 3-en-1 (`aspace_freecloud_gateway.py`)
Unifie `freellmapi`, `freebuff` et `codex-chatgpt-web` derrière `http://127.0.0.1:31415/v1/chat/completions` :
- **Palier 0 (Réflexe Local 0 $)** : `GLiNER2.5-multi-Decide` + `Needle-3` + `Kyutai-Mimi` + `LFM3-Omni-2B` (`:9931`).
- **Palier 1 (FreeCloud 3-en-1)** : Rotation automatique avec circuit-breaker (<5 ms).
- **Palier 2 (Frontière sous Quota Automaton)** : Débloqué uniquement si le ROI calculé par `02_PredictiveWargame_MachineLearning` est $\ge 3\times$ le coût en tokens.
