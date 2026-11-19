---
okf_version: "0.2"
type: Specification
title: "PRD-FONDATION — Spécification Produit de la Fondation A'Space OS V5 (Matrice SPAD · 4 Noyaux ADR-14)"
enonce_ref: "00_Memoire/bundle/fusion/FUSION-ENONCE.md"
enonce_sha256: "41889edb9c468ea62ee4641328c0e6f4bac2c618b81da751eebd2af4c05f648d"
---

# PRD-FONDATION — De 120 Pointeurs aux 4 Noyaux Équilibrés (`ÂME / SYSTÈME NERVEUX / CORPS / MÉTABOLISME`)

## 1. Problème & Finalité (L'objectif au-delà de l'objectif)
`01_Forkable` a crû de 26 à 120 modules hétérogènes (109 entrées `.gitmodules`, 101 gitlinks actifs, 12 modules F8 dé-pointés, 3 natifs, 4 registres/apps, 8 doublons fantômes). Une collection de pointeurs est une dette de maintenance, pas un système d'exploitation.

**Finalité de la Fondation A'Space (`ADR-14` amendant `ADR-13`)** : remplacer la collection de dépôts juxtaposés par **4 Noyaux Fondamentaux équilibrés (`ÂME`, `SYSTÈME NERVEUX`, `CORPS`, `MÉTABOLISME`)** — chacun plafonné à `≤ 1/3` du corpus (`40` modules max) et interconnectés sur un **Socle L0 unique** — rattachant les organes spécialisés (`K1..K5`, `K3-ML`) et évoluant le long d'un seul cœur (`Python → Hybride → Rust`) où chaque module de $F$ est soit **FUSIONNÉ**, soit **RETENU**, soit **ÉCARTÉ**, avec `(RETENU + ÉCARTÉ) < 1/3` du corpus.

---

## 2. Architecture des 4 Noyaux Équilibrés & Organes Rattachés (`ADR-14`)

### Noyau 1 — `ÂME` (`Automaton` — Doctrine, Gouvernance 13→1, Mémoire Épistémique & Compétences — 29 modules · 24.2 %)
- **Organe `K1` — Gouvernance, Vérification 13→1 & RSI** (11 modules) : `automaton`, `fondation-13-1`, `prime-agent`, `elephant-goldfish-model`, `gsd-core`, `gstack`, `superpowers`, `adk-recipes`, `dream-rsi`, `rrsi`, `wikiskill`.
  - Unification 13→1 (`fondation-13-1` Rust 100/100), baux TTL (`300s`), sanctuaire nocturne, isolation EGM (`egm_missions.db`) et boucle RSI bornée (`δ ≥ 1.7 %` + Juge externe).
- **Organe `K4` — Mémoire Neuro-Symbolique & Compétences** (18 modules) : `FKB02_Memory` (`auto-ontology`, `billion-context`, `context-language-models`, `dox`, `gbrain`, `graphify`, `infinite-brain-harness`, `infinite-brain-os`, `knowledge-catalog`, `llm-wiki`, `servers`) + `caveman`, `claude-mem`, `hermes-agent`, `anthropic-skills`, `claude-video`, `mattpocock-skills`, `openai-plugins`.
  - Mémoire vérifiée au fichier `M1–M8` (`aspace_fkb02_memory_organ.py` + `neuro_symbolic_bridge.py` + `memory.jsonl` sous verrou `O_EXCL` + bundle OKF v0.2), compression télégraphique `caveman` et apprentissage `/learn` borné. Preuves différentielles source-vs-organe Cycle 5 pour `M044 context-language-models` et `M050 knowledge-catalog`.
- **Modules `RETENU` justifiés dans `ÂME` (2)** : `servers` (`@modelcontextprotocol/server-memory` référence Stdio) et `openai-plugins` (référence externe D12 Clean-Room sans licence).

### Noyau 2 — `SYSTÈME NERVEUX` (`Infinity` — Journal L0, Hibernation Pure-Data, Inférence & Cortex Prédictif — 29 modules · 24.2 %)
- **Bus Nerveux L0, Hibernation & Fibres** (7 modules) : `RigInfinity` (Rust 105/105), `infinity`, `cordis`, `pi`, `aspace-fiber-host`, `deepseek-harness`, `spynel`.
  - État `Pure Data Between Turns` (hibernation coût zéro, réveil uniquement sur événement `RAP` / bail), checkpoints idempotents `requestId`, sonde sentinelle locale et pont Phase 2 Hybride Python ↔ binaires Rust (`r10-receive`, `route-dispatch`, `recall-fact`).
- **Organe `K3` — Inférence System-1/2 & Routage FreeCloud** (15 modules) : `GLiNER2.5-multi-Decide`, `LFM3-Omni-2B`, `LoRA`, `mimi`, `moshi`, `needle`, `DeepInfer`, `cross-platform-llm-client`, `mesh-llm`, `bifrost`, `codex-chatgpt-web`, `freebuff`, `freellmapi`, `04_Inference_Youtube_Discovery_Registry` (`M118`), `FreeVPS` (`ÉCARTÉ`).
  - Classification < 10 ms (`GLiNER2.5` + `Needle`), passerelle FreeCloud unifiée (`:31415` sans télémétrie) et registre `aspace_discovery_catalog.py`.
- **Organe `K3-ML` — Cortex Prédictif & Wargame** (7 modules transférés de `K5` par `ADR-14`) : `autogluon`, `mitra-2`, `chronos-forecasting`, `timesfm`, `tabfm`, `PathFM`, `MiroFish`.
- **Modules `RETENU` / `ÉCARTÉ` justifiés dans `SYSTÈME NERVEUX`** : 6 `RETENU` (actifs binaires/poids : `GLiNER2.5`, `LFM3-Omni-2B`, `mimi`, `moshi`, `needle`, `DeepInfer`) ; 1 `ÉCARTÉ` (`FreeVPS`).

### Noyau 3 — `CORPS` (`OpenRig` — Exécution Multi-Harness, Outils Anything & Surfaces 3D — 26 modules · 21.7 %)
- **Organe `K2` — Action Multi-Harness, Outils Anything & Surfaces 3D** (26 modules) : `openrig`, `agent-zero`, `herdr`, `herdr-core`, `herdr-app`, `openbot`, `openmuse`, `OpenDots`, `OpenDuet`, `openclaw`, `orca`, `t3code`, `claude-code`, `codex`, `a0-plugins`, `tuxee`, `source-control-natif`, `agent-office`, `city-office`, `cubefarm`, `space-agent`, `CLI-Anything`, `agent-browser`, `agent-desktop`, `api-anything`, `rea`.
  - Multiplexage multi-harness sous un seul daemon maître `RigInfinity`, outillage universel `aspace_fkb04_anything_organ.py` (preuve différentielle `M056 CLI-Anything` sur `zotero`/`audacity` ; `M058 agent-desktop` maintenu `PARTIEL` sans repli `headless-fallback`) et surfaces 3D des 578 Holons.
- **Modules `RETENU` justifiés dans `CORPS` (4)** : `claude-code`, `codex`, `herdr-app`, `cubefarm`.

### Noyau 4 — `MÉTABOLISME` (`BusinessOS` — Production Vidéo, Finance S0 & Marché B2B — 36 modules · 30.0 %)
- **Organe `K5` — Studio Vidéo, Trading Copilote Read-Only & Services B2B** (36 modules) :
  - *Studio Vidéo Unifié (10 + 8 doublons FKB06 purgés)* : `OpenMontage`, `flute`, `argo`, `earshot`, `explainroo`, `huashu-motion`, `reanimate`, `rossark-motion-skill`, `take-one`, `video-director`.
  - *Trading Copilote Read-Only (11)* : 10 modules actifs/partiels sous veto `S0` + `LLM-Trading-Lab` (`ÉCARTÉ`).
  - *Services B2B & MarketPlace (15)* : 13 dépôts B2B + `00_Marketplace_YoutubeSkills` (`M117`, absorbé dans `aspace_discovery_catalog.py` avec preuve différentielle) + `LibertyRide2` (`RETENU`).
- **Modules `RETENU` / `ÉCARTÉ` justifiés dans `MÉTABOLISME`** : 5 `RETENU` (`freqtrade`, `uptime-kuma`, `changedetection.io`, `dify`, `LibertyRide2`) ; 1 `ÉCARTÉ` (`LLM-Trading-Lab`).

---

## 3. Critères d'Acceptation & Mesures de Sortie (Cycle 5)
1. **Couverture 100 % de $F$ sous les 4 Noyaux (`ADR-14`, chacun ≤ 40 modules)** : 120 modules (`ÂME`: 29, `SYSTÈME NERVEUX`: 29, `CORPS`: 26, `MÉTABOLISME`: 36) + 8 doublons FKB06 tracés dans `CARTE-DES-PRINCIPES.md` et `REGISTRE-DE-FUSION.md`.
2. **Garde §5.5** : `(RETENU + ÉCARTÉ) / 120 = 19 / 120 = 15.8 %` (< 33.3 %).
3. **Trajectoire Un Cœur (`ADR-13` / `ADR-14`)** : Phase 1 Python -> **Phase 2 Hybride (`cargo test` vert sur `fondation-13-1` et `RigInfinity` + pont binaire Python↔Rust)** -> Phase 3 Rust destination.
4. **Preuves de Suppression Réelles & Différentielles (`15 / 120` `FUSIONNÉ`, `86` `PARTIEL`)** : 9 F8 via `RigInfinity` Rust + `M120 llm-wiki` + **5 modules validés par comparaison différentielle source-vs-organe sur entrées identiques avant/après suppression physique** (`M044`, `M050`, `M056`, `M117`, `M118`). Les `14` autres modules FKB02/FKB04 (dont `M058 agent-desktop`, sans fenêtre Win32 interactive réelle ni `headless-fallback`) sont honnêtement classés `PARTIEL`.
