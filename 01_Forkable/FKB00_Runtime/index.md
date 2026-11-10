# `01_Forkable/FKB00_Runtime` — Architecture Souveraine A0 en 6 Pôles

Ce répertoire regroupe les moteurs d'exécution, le micro-noyau spatio-temporel, les modèles prédictifs Wargame, les spécifications maîtres, le cockpit ADE et les moteurs d'auto-amélioration récursive d'**A'Space OS V5** (`Amdkn/Aspace_OS_V5`).

---

## Sanctuarisation

**FKB00 est sanctuarisé : aucune écriture dans FKB00 sans design signé de Clara ; la fusion se fait sur des gels nommés, jamais sur des HEAD vivants ; la revisite est par signal de dérive (inventaire hebdomadaire).**

---

## 00. [`00_A0_Core`](./00_A0_Core) — Noyau Souverain A0 (`Agent-Zero × Cordis × DSH × Pi`)
Réécriture souveraine d'Agent Zero greffée sur le micro-noyau spatio-temporel Cordis (`Everything-is-a-Plugin`, Fibers à effets réversibles et co-effets réactifs) :
- `agent-zero` (`Amdkn/agent-zero` ← `agent0ai/agent-zero`) — Cœur d'agent autonome réécrit pour A0 Amadeus.
- `a0-plugins` (`Amdkn/a0-plugins` ← `agent0ai/a0-plugins`) — Catalogue d'extensions natives A0.
- `spynel` (`Amdkn/spynel` ← `agent0ai/spynel`) — Télémétrie et sentinelle temps réel Agent0.
- `tuxee` (`Amdkn/tuxee` ← `agent0ai/tuxee`) — Exécution système et environnement Linux/conteneur Agent0.
- `cordis` (`Amdkn/cordis` ← `cordiverse/cordis`) — Micro-noyau TypeScript de composabilité spatio-temporelle (< 50 Ko).
- `deepseek-harness` (`Amdkn/deepseek-harness` ← `deepseek-ai/deepseek-harness`) — Harness modulaire construit sur Cordis.
- `pi` (`Amdkn/pi` ← `earendil-works/pi`) — Moteur minimaliste à 4 outils atomiques (`Read`, `Write`, `Edit`, `Bash`) et arbre de sessions durable.
- [`a0_recursive_factory.py`](./00_A0_Core/a0_recursive_factory.py) — Implémentation exécutable du moteur récursif A0 à 3 Horizons (Cordis Fiber + Prime-Agent RLM `/refine` + AQuA/WikiSkill + Dream-RSI/RRSI).

---

## 01. [`01_Holo_TriptyqueCore`](./01_Holo_TriptyqueCore) — Triptyque Métabolique, Lignage & Population
- `automaton` (`Amdkn/automaton` ← `Conway-Research/automaton`) — Réserve d'inférence structurée, baux de survie et budget souverain.
- `openrig` (`Amdkn/openrig`) — Arbre généalogique, mandats et descendance vérifiable des sous-agents.
- `infinity` (`Amdkn/infinity`) — Gestionnaire de population distribuée jusqu'à 75 000 micro-agents frugaux.

---

## 02. [`02_PredictiveWargame_MachineLearning`](./02_PredictiveWargame_MachineLearning) — Wargame & Modèles Tabulaires/Séries Temporelles
- `autogluon` (`Amdkn/autogluon`) — Orchestrateur Tabular & TimeSeries.
- `mitra-2` (`Amdkn/mitra-2`) — Fondation tabulaire in-context learning (AutoGluon Mitra v2).
- `chronos-forecasting` (`Amdkn/chronos-forecasting`) — Fondation de prévision temporelle Chronos-2.
- `PathFM` (`Amdkn/PathFM`) — Fondation pathologique/séquentielle.
- `timesfm` (`Amdkn/timesfm`) — Google Research TimesFM.
- `tabfm` (`Amdkn/tabfm`) — Google Research TabFM.
- `MiroFish` (`Amdkn/MiroFish`) — Moteur de simulation Wargame multi-agents (`S3-RORY` 4P).
- [`models/`](./02_PredictiveWargame_MachineLearning/models) — Fiches d'architecture liées aux dépôts Hugging Face & GitHub.

---

## 03. [`03_MasterSpec_CleanPlan`](./03_MasterSpec_CleanPlan) — Gouvernance, Spécifications Maîtres & Plans Propres
- `elephant-goldfish-model` (`Amdkn/elephant-goldfish-model`) — Architecture EGM (Mémoire Éléphant de spécification × Exécution Poisson Rouge sans pollution de contexte).
- `get-shit-done` (`Amdkn/get-shit-done`) — Protocole d'exécution déterministe GSD.
- `gstack` (`Amdkn/gstack`) — Pile de gouvernance et revues structurées.
- `superpowers` (`Amdkn/superpowers`) — Compétences d'ingénierie chirurgicale et TDD.

---

## 04. [`04_ADE_OpenRig`](./04_ADE_OpenRig) — Cockpit ADE (`Herdr × Orca × T3Code`) & Harnesses Universels
- `herdr`, `herdr-core`, `herdr-app` (`Amdkn/herdr*` ← `herdrdev/*`) — Multiplexeur de terminaux Rust et UI GPUI accélérée GPU.
- `orca` (`Amdkn/orca` ← `stablyai/orca`) — Isolation de worktrees Git, DAG multi-agents et Computer Use.
- `t3code` (`Amdkn/t3code` ← `pingdotgg/t3code`) — Interface web/desktop légère de revue de diffs et pilotage multi-modèles.
- `openclaw` (`Amdkn/openclaw` ← `openclaw/openclaw`) — Démon d'agent autonome 24/7 multi-canaux.
- `claude-code` (`Amdkn/claude-code` ← `anthropics/claude-code`) — Harness CLI agnostique cablé sur la passerelle FreeCloud `:31415`.
- `codex` (`Amdkn/codex` ← `openai/codex`) — Harness CLI agnostique cablé sur la passerelle FreeCloud `:31415`.
- `hermes-agent` (`Amdkn/hermes-agent` ← `nousresearch/hermes-agent`) — Agent auto-améliorant avec boucle d'apprentissage `/learn`.

---

## 05. [`05_Recursive_RSI`](./05_Recursive_RSI) — Récursivité & Auto-Amélioration sur 3 Horizons
- `prime-agent` (`Amdkn/prime-agent` ← `PrimeIntellect-ai/prime-agent`) — Horizon 1 (Court terme) : paradigme RLM (`rlm.spawn`, `/refine`, REPL Python persistant, snapshots avec rollback).
- `wikiskill` (`Amdkn/wikiskill` ← `ashutoshsinghpr7/wikiskill`) — Horizon 2 (Moyen terme, `arXiv:2608.27454`) : compilation de Playbooks par 4 rôles séparés (*Worker, Note-Taker, Playbook Writer, Strict Manager*) et Holdout Set ($\delta \ge 1.7\%$).
- `adk-recipes` (`Amdkn/adk-recipes` ← `google/adk-recipes`) — Horizon 2 : Google **AQuA** (*Ambient Quality Agent*, `core/python/ambient-quality-agent`).
- `rrsi` (`Amdkn/rrsi` ← `google-research/rrsi`) — Horizon 3 (Long terme) : *Recursive Self-Improvement* par évolution de worktrees Git.
- `dream-rsi` (`Amdkn/dream-rsi` ← `google-research/dream-rsi`) — Horizon 3 : auto-amélioration hors-ligne à 0 $ par recherche d'arbre et replay de trajectoires.

---

## 06. [`06_Sovereign_Bot_Coworkers`](./06_Sovereign_Bot_Coworkers) — Coéquipiers Souverains (Bots)
Les 4 bots sont 1 fonction × 4 (coéquipier incarné : workspace + navigateur + terminal). Fusion F8 (§D7) : la surface unique est native (RigInfinity), spécifiée depuis les quatre — **OpenBot comme référence de base**, avec les fonctions distinctives portées comme traits (OpenDots : coworkers always-on ; OpenDuet : humain dans la boucle, proactif ; OpenMuse : agent personnel). Au pas 7, les 3 pointeurs (OpenMuse, OpenDots, OpenDuet) quittent `.gitmodules` ; le pointeur OpenBot quitte au pas 8, quand la surface native est vérifiée.
- `openbot` (`Amdkn/openbot` ← `CopilotKit/OpenBot`) — Référence de la surface unique ; gel `2b5b14f`.
- `openmuse` (`Amdkn/openmuse` ← `CopilotKit/openmuse`) — Agent personnel ; gel `a4944f4`.
- `OpenDots` (`Amdkn/OpenDots` ← `CopilotKit/OpenDots`) — Coworkers always-on ; gel `d4214af`.
- `OpenDuet` (`Amdkn/OpenDuet` ← `CopilotKit/OpenDuet`) — Humain dans la boucle, proactif ; gel `f52288f`.
