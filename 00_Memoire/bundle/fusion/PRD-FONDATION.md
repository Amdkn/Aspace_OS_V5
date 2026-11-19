---
okf_version: "0.2"
type: Specification
title: "PRD-FONDATION — Spécification Produit de la Fondation A'Space OS V5 (Matrice SPAD · 3 Noyaux)"
enonce_ref: "00_Memoire/bundle/fusion/FUSION-ENONCE.md"
enonce_sha256: "41889edb9c468ea62ee4641328c0e6f4bac2c618b81da751eebd2af4c05f648d"
---

# PRD-FONDATION — De 120 Pointeurs aux 3 Noyaux Souverains (`ÂME / SYSTÈME NERVEUX / CORPS`)

## 1. Problème & Finalité (L'objectif au-delà de l'objectif)
`01_Forkable` a crû de 26 à 120 modules hétérogènes (109 entrées `.gitmodules`, 101 gitlinks actifs, 12 modules F8 dé-pointés, 3 natifs, 4 registres/apps, 8 doublons fantômes). Une collection de pointeurs est une dette de maintenance, pas un système d'exploitation.

**Finalité de la Fondation A'Space (`ADR-13`)** : remplacer la collection de dépôts juxtaposés par **3 Noyaux Fondamentaux (`ÂME`, `SYSTÈME NERVEUX`, `CORPS`)** interconnectés sur un **Socle L0 unique**, rattachant les 5 organes spécialisés (`K1..K5`) et évoluant le long d'un seul cœur (`Python → Hybride → Rust`) où chaque module de $F$ est soit **FUSIONNÉ**, soit **RETENU**, soit **ÉCARTÉ**, avec `(RETENU + ÉCARTÉ) < 1/3` du corpus.

---

## 2. Architecture des 3 Noyaux & Organes Rattachés (`ADR-13`)

### Noyau 1 — `ÂME` (`Automaton` — Doctrine, Gouvernance 13→1, Mémoire Épistémique & Compétences — 29 modules)
- **Organe `K1` — Gouvernance, Vérification 13→1 & RSI** (11 modules) : `automaton`, `fondation-13-1`, `prime-agent`, `elephant-goldfish-model`, `gsd-core`, `gstack`, `superpowers`, `adk-recipes`, `dream-rsi`, `rrsi`, `wikiskill`.
  - Unification 13→1 (`fondation-13-1` Rust 100/100), baux TTL (`300s`), sanctuaire nocturne, isolation EGM (`egm_missions.db`) et boucle RSI bornée (`δ ≥ 1.7 %` + Juge externe).
- **Organe `K4` — Mémoire Neuro-Symbolique & Compétences** (18 modules) : `FKB02_Memory` (`auto-ontology`, `billion-context`, `context-language-models`, `dox`, `gbrain`, `graphify`, `infinite-brain-harness`, `infinite-brain-os`, `knowledge-catalog`, `llm-wiki`, `servers`) + `caveman`, `claude-mem`, `hermes-agent`, `anthropic-skills`, `claude-video`, `mattpocock-skills`, `openai-plugins`.
  - Mémoire vérifiée au fichier `M1–M8` (`aspace_fkb02_memory_organ.py` + `neuro_symbolic_bridge.py` + `memory.jsonl` sous verrou `O_EXCL` + bundle OKF v0.2), compression télégraphique `caveman` et apprentissage `/learn` borné.
- **Modules `RETENU` justifiés dans `ÂME` (2)** : `servers` (`@modelcontextprotocol/server-memory` référence Stdio) et `openai-plugins` (référence externe D12 Clean-Room sans licence).

### Noyau 2 — `SYSTÈME NERVEUX` (`Infinity` — Journal L0, Reçus R10, Hibernation Pure-Data, Fibres & Inférence — 22 modules)
- **Bus Nerveux L0, Hibernation & Fibres** (7 modules) : `RigInfinity` (Rust 105/105), `infinity`, `cordis`, `pi`, `aspace-fiber-host`, `deepseek-harness`, `spynel`.
  - État `Pure Data Between Turns` (hibernation coût zéro, réveil uniquement sur événement `RAP` / bail), checkpoints idempotents `requestId`, sonde sentinelle locale et pont Phase 2 Hybride Python ↔ binaires Rust (`r10-receive`, `route-dispatch`, `recall-fact`).
- **Organe `K3` — Inférence System-1/2 & Routage FreeCloud** (15 modules) : `GLiNER2.5-multi-Decide`, `LFM3-Omni-2B`, `LoRA`, `mimi`, `moshi`, `needle`, `DeepInfer`, `cross-platform-llm-client`, `mesh-llm`, `bifrost`, `codex-chatgpt-web`, `freebuff`, `freellmapi`, `04_Inference_Youtube_Discovery_Registry`, `FreeVPS` (`ÉCARTÉ`).
  - Classification < 10 ms (`GLiNER2.5` + `Needle`), passerelle FreeCloud unifiée (`:31415` sans télémétrie) et registre `aspace_discovery_catalog.py`.
- **Modules `RETENU` / `ÉCARTÉ` justifiés dans `SYSTÈME NERVEUX`** : 6 `RETENU` (actifs binaires/poids : `GLiNER2.5`, `LFM3-Omni-2B`, `mimi`, `moshi`, `needle`, `DeepInfer`) ; 1 `ÉCARTÉ` (`FreeVPS`).

### Noyau 3 — `CORPS` (`OpenRig` — Exécution Multi-Harness, Outils Anything, Surfaces 3D & Moteurs Prédictifs/B2B — 69 modules)
- **Organe `K2` — Action Multi-Harness, Outils Anything & Surfaces 3D** (26 modules) : `openrig`, `agent-zero`, `herdr`, `herdr-core`, `herdr-app`, `openbot`, `openmuse`, `OpenDots`, `OpenDuet`, `openclaw`, `orca`, `t3code`, `claude-code`, `codex`, `a0-plugins`, `tuxee`, `source-control-natif`, `agent-office`, `city-office`, `cubefarm`, `space-agent`, `CLI-Anything`, `agent-browser`, `agent-desktop`, `api-anything`, `rea`.
  - Multiplexage multi-harness sous un seul daemon maître `RigInfinity`, outillage universel `aspace_fkb04_anything_organ.py` (API HAR -> CLI JSON -> Accessibilité CDP `@ref` / UIA sans vol de focus -> rétro-ingénierie clean-room `rea`) et surfaces 3D des 578 Holons.
- **Organe `K5` — Moteurs Prédictifs, Wargame, Studio Vidéo & Valeur B2B** (43 modules) :
  - *Prédictif & Wargame (7)* : `autogluon`, `mitra-2`, `chronos-forecasting`, `timesfm`, `tabfm`, `PathFM`, `MiroFish`.
  - *Studio Vidéo Unifié (10 + 8 doublons FKB06 purgés)* : `OpenMontage`, `flute`, `argo`, `earshot`, `explainroo`, `huashu-motion`, `reanimate`, `rossark-motion-skill`, `take-one`, `video-director`.
  - *Trading Copilote Read-Only (11)* : 10 modules actifs/partiels sous veto `S0` + `LLM-Trading-Lab` (`ÉCARTÉ`).
  - *Services B2B & MarketPlace (15)* : 13 dépôts B2B + `00_Marketplace_YoutubeSkills` (absorbé dans `aspace_discovery_catalog.py`) + `LibertyRide2` (`RETENU`).
- **Modules `RETENU` / `ÉCARTÉ` justifiés dans `CORPS`** : 9 `RETENU` (`claude-code`, `codex`, `herdr-app`, `cubefarm`, `freqtrade`, `uptime-kuma`, `changedetection.io`, `dify`, `LibertyRide2`) ; 1 `ÉCARTÉ` (`LLM-Trading-Lab`).

---

## 3. Critères d'Acceptation & Mesures de Sortie (Cycle 4)
1. **Couverture 100 % de $F$ sous les 3 Noyaux** : 120 modules (`ÂME`: 29, `SYSTÈME NERVEUX`: 22, `CORPS`: 69) + 8 doublons FKB06 tracés dans `CARTE-DES-PRINCIPES.md` et `REGISTRE-DE-FUSION.md`.
2. **Garde §5.5** : `(RETENU + ÉCARTÉ) / 120 = 19 / 120 = 15.8 %` (< 33.3 %).
3. **Trajectoire Un Cœur (`ADR-13`)** : Phase 1 Python -> **Phase 2 Hybride (atteinte au Cycle 4 : `cargo test` vert sur `fondation-13-1` et `RigInfinity` + pont binaire Python↔Rust)** -> Phase 3 Rust destination.
4. **Tests de Suppression Réels (`29 / 120` `FUSIONNÉ`, +26 en Cycle 4)** : F8 (`9`), FKB04 (`8`), FKB02 (`9`), transverses (`M117`, `M118`, `M120`) vérifiés sur clone propre par le Juge externe lecture seule.
