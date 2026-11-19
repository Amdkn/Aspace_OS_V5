---
okf_version: "0.2"
type: Specification
title: "PRD-FONDATION — Spécification Produit de la Fondation A'Space OS V5 (Matrice SPAD)"
enonce_ref: "00_Memoire/bundle/fusion/FUSION-ENONCE.md"
enonce_sha256: "41889edb9c468ea62ee4641328c0e6f4bac2c618b81da751eebd2af4c05f648d"
---

# PRD-FONDATION — De 120 Pointeurs à 5 Noyaux Souverains Interconnectés

## 1. Problème & Finalité (L'objectif au-delà de l'objectif)
`01_Forkable` a crû de 26 à 120 modules hétérogènes (109 entrées `.gitmodules`, 101 gitlinks actifs, 12 modules F8 dé-pointés, 3 natifs, 4 registres/apps, 8 doublons fantômes). Une collection de pointeurs est une dette de maintenance, pas un système d'exploitation.

**Finalité de la Fondation A'Space** : remplacer la collection de dépôts juxtaposés par **5 Noyaux Fondamentaux interconnectés (`K1..K5`)** sur un **Socle L0 unique**, où chaque module de $F$ est soit **FUSIONNÉ** (son principe, ses invariants et ses interfaces vivent dans la Fondation et sa source peut quitter l'arbre sans perte), soit **RETENU** (binaire/poids/app physique indispensable justifié), soit **ÉCARTÉ** (doublon/hors-périmètre vérifié), avec `(RETENU + ÉCARTÉ) < 1/3` du corpus.

---

## 2. Architecture des 5 Noyaux (Exigences Fonctionnelles)

### Noyau K1 — Gouvernance, Âme & Vérification (11 modules)
- **Modules sources** : `Automaton`, `Fondation-13-1`, `Prime-Agent`, `Elephant-Goldfish-Model`, `GSD-Core`, `GStack`, `Superpowers`, `ADK-Recipes (AQuA)`, `WikiSkill`, `Dream-RSI`, `RRSI`.
- **Exigences fonctionnelles** :
  - **F-K1.1 (Unification 13→1)** : exécuter Recevoir (`R10`), Router (`seq`), Découvrir (`D1–D8`), Juger (`J1–J8`), Exécuter (`E1–E8`) et Mémoriser (`M1–M8`) en binaire déterministe zéro-dépendance (`fondation-13-1`).
  - **F-K1.2 (Constitution & Homéostasie)** : appliquer les baux TTL (`300s`), le sanctuaire nocturne (`00h–05h`), la protection E-Myth (`Beth/Morty/Rick`) et l'allocation budgétaire `Automaton`.
  - **F-K1.3 (Isolation EGM & RSI Borné)** : isoler la mémoire macro SQLite (`egm_missions.db`) des contextes éphémères d'exécution ; borner toute auto-amélioration (`/refine`, `/learn`, `WikiSkill`, `Dream-RSI`, `RRSI`) par hold-out (`δ ≥ 1.7%`) et Juge externe.

### Noyau K2 — Exécution, Concurrence & Surface Vivante (33 modules)
- **Modules sources** : `RigInfinity`, `Cordis`, `aspace-fiber-host`, `Infinity`, `OpenRig`, `Pi`, `Agent-Zero`, `a0-plugins`, `Spynel`, `Tuxee`, `DeepSeek-Harness`, `source-control-natif`, `OpenBot/Muse/Dots/Duet`, `Herdr/Herdr-Core/Herdr-App`, `Orca`, `T3Code`, `OpenClaw`, `Claude-Code`, `Codex`, `API-Anything`, `CLI-Anything`, `REA`, `Agent-Browser`, `Agent-Desktop`, `CubeFarm`, `Agent-Office`, `City-Office`, `Space-Agent`.
- **Exigences fonctionnelles** :
  - **F-K2.1 (Daemon Maître Unique)** : héberger les 578 Holons en état `Pure Data Between Turns` (hibernation coût zéro, réveil sur événement RAP, `requestId` idempotent, `writerLock` par worktree).
  - **F-K2.2 (Multiplexage Multi-Harnesses)** : piloter `Claude Code`, `Codex`, `OpenCode`, `Pi`, `dsh` via `OpenRig` YAML + terminaux PTY `Herdr` + isolation `Orca` / `source_control` WAL sans copie.
  - **F-K2.3 (Surface Universelle & Incarnation 3D)** : exposer toute API/CLI/Desktop (`api-anything` -> `CLI-Anything` -> `agent-browser` `@ref` / `agent-desktop` sans vol de focus) et projeter l'état vivant dans l'interface unifiée (`City-Office` / `CubeFarm` + `herdr-app`).
- **Modules `RETENU` justifiés en K2 (4)** : `claude-code` (binaire externe D12 Clean-Room), `codex` (binaire worker externe), `herdr-app` (GUI GPU compilée), `cubefarm` (surface WebGL 3D active). -> Total 4 `RETENU` en K2.

### Noyau K3 — Inférence & Décision Calibrée (15 modules)
- **Modules sources** : `GLiNER2.5-multi-Decide`, `Cactus Needle`, `Mimi`, `Moshi`, `LFM3-Omni-2B`, `LoRA`, `DeepInfer`, `Mesh-LLM`, `Cross-Platform-Client`, `FreeLLMAPI`, `Bifrost`, `Codex-ChatGPT-Web`, `Freebuff`, `FreeVPS` (`ÉCARTÉ`), `YouTube-Discovery-Registry`.
- **Exigences fonctionnelles** :
  - **F-K3.1 (Pipeline System-1 Local)** : classifier/extraire l'intention en < 10 ms (`GLiNER2.5`), mapper vers JSON `function_calls` par grammaire contrainte (`Needle`), tokeniser/synthétiser la voix localement (`Mimi`/`Moshi`/`LFM3 + LoRA`).
  - **F-K3.2 (Gateway FreeCloud & Mesh Unifiée)** : router de façon transparente sur `:31415` (`Tier 0 local -> Tier 1 FreeLLMAPI/Bifrost/Freebuff -> Tier 2 Codex-ChatGPT-Web bouclier 24 patterns -> Mesh P2P`) avec failover automatique sur `exhaustedPatterns` et `YouTube-Discovery-Registry`.
- **Modules `RETENU` / `ÉCARTÉ` justifiés en K3** : 6 `RETENU` (actifs binaires/poids neuronaux : `GLiNER2.5`, `LFM3-Omni-2B`, `mimi`, `moshi`, `needle`, `DeepInfer`) ; 1 `ÉCARTÉ` (`FreeVPS` pour risque CGU GitHub Actions et instabilité).

### Noyau K4 — Mémoire Neuro-Symbolique & Compétences (18 modules)
- **Modules sources** : `Auto-Ontology`, `Billion-Context`, `Context-Language-Models`, `MCP Servers (Memory)`, `Graphify`, `GBrain`, `Infinite-Brain-OS`, `Infinite-Brain-Harness`, `DOX`, `Knowledge-Catalog`, `LLM-Wiki`, `Claude-Mem`, `Caveman`, `Hermes-Agent`, `Anthropic-Skills`, `MattPocock-Skills`, `OpenAI-Plugins`, `Claude-Video`.
- **Exigences fonctionnelles** :
  - **F-K4.1 (Mémoire Épistémique Triple-Couche)** : combiner substrat CAS `billion-context`, compilateur DAG `auto-ontology`, graphe AST `graphify`, recherche hybride `gbrain`, wiki OKF v0.2 (`00_Memoire/bundle/`), graphe MCP `memory.jsonl` (`FileLock O_EXCL`) et validation stricte `M1–M8`.
  - **F-K4.2 (Catalogue Unique de Compétences)** : unifier `SKILL.md` (divulgation progressive + `/learn` + `/watch` Dual-Engine + compression télégraphique `caveman` + conventions TDD `mattpocock`).
- **Modules `RETENU` justifiés en K4 (2)** : `servers` (`@modelcontextprotocol/server-memory` référence MCP Stdio officielle) et `openai-plugins` (référence externe D12 Clean-Room sans licence).

### Noyau K5 — Prédictif, Wargame & Moteurs de Valeur B2B (43 modules)
- **Modules sources** :
  - *Axe Prédictif & Wargame (7)* : `AutoGluon`, `Mitra-2`, `Chronos-Forecasting`, `TimesFM`, `TabFM`, `PathFM`, `MiroFish`.
  - *Axe Studio Vidéo Unifié (10 + 8 doublons FKB06 purgés)* : `OpenMontage`, `flute`, `argo`, `earshot`, `explainroo`, `huashu-motion`, `reanimate`, `rossark-motion-skill`, `take-one`, `video-director`.
  - *Axe Trading Copilote Read-Only (11)* : `TradingAgents`, `TradingView-Unified-MCP`, `Vibe-Trading`, `ai-hedge-fund`, `claude-trading-skills`, `daily_stock_analysis`, `financial-services`, `freqtrade`, `nansen-cli`, `tradingview-indicator-search-mcp-server`, `LLM-Trading-Lab` (`ÉCARTÉ`).
  - *Axe Services B2B & MarketPlace (15)* : `BusinessOS`, `Impeccable`, `Uptime-Kuma`, `ChangeDetection`, `DeepTutor`, `Open-Notebook`, `OpenMausBot`, `PowerBI-to-AI`, `Text-to-CAD`, `BlenderWorld`, `Scrapling`, `Dify`, `Presenton`, `00_Marketplace_YoutubeSkills`, `LibertyRide2`.
- **Exigences fonctionnelles** :
  - **F-K5.1 (Prédiction & Confinement Licence)** : exécuter le dual-jury réel (`Mitra-v2` + `Chronos-2` en `b2b_commercial` Apache-2.0 ; ajout `TabFM` + `TimesFM` + `PathFM` uniquement en `a0_internal_wargame` ; `MiroFish` AGPL-3.0 isolé en service séparé).
  - **F-K5.2 (Studio Vidéo Unifié)** : orchestrer les 10 moteurs vidéo sous contrat unique `aspace_video_studio_foundation.py` (zéro doublon FKB06 dans `.gitmodules`).
  - **F-K5.3 (Garde-Fou Trading & Productized B2B)** : forcer `READ_ONLY` + `dry_run` + veto `S0` sur tout actif trading ; opérer `The OMK Office` et `LibertyRide2` via `aspace_marketplace_engine.py` et reçus `R10`.
- **Modules `RETENU` / `ÉCARTÉ` justifiés en K5** : 5 `RETENU` (`freqtrade`, `uptime-kuma`, `changedetection.io`, `dify`, `LibertyRide2`) ; 1 `ÉCARTÉ` (`LLM-Trading-Lab`, benchmark historique redondant).

---

## 3. Critères d'Acceptation & Mesures de Sortie
1. **Couverture 100 % de $F$** : 120 modules + 8 doublons FKB06 tracés dans `CARTE-DES-PRINCIPES.md` et `REGISTRE-DE-FUSION.md`.
2. **Garde §5.5** : `(RETENU + ÉCARTÉ) / 120 = 19 / 120 = 15.83 %` (< 33.3 %).
3. **Intégrité des Contrats L0** : `test_foundation_deletion_suite.py` passe à 100 % sur `EventJournal`, `R10Receipt`, `EpistemicFact` et les preuves de suppression F8 + FKB06.
4. **Gates déterministes** : `checks.ps1`, `check-modules-lock.py` et `cargo test` (`fondation-13-1`) verts ; verdict indépendant du Juge-comparateur.
