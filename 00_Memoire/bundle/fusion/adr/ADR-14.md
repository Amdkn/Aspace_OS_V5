---
okf_version: "0.2"
type: Decision
title: "ADR-14 — Amendement ADR-13 : Règle du Tiers Maximal (≤ 40 modules) & Quatre Noyaux Équilibrés (ÂME / SYSTÈME NERVEUX / CORPS / MÉTABOLISME)"
enonce_ref: "00_Memoire/bundle/fusion/FUSION-ENONCE.md"
enonce_sha256: "41889edb9c468ea62ee4641328c0e6f4bac2c618b81da751eebd2af4c05f648d"
amends: "ADR-13"
---

# ADR-14 — Règle d'Équilibre Topologique (≤ 1/3 par Noyau) & Scission de `CORPS` → Quatre Noyaux (`ÂME / SYSTÈME NERVEUX / CORPS / MÉTABOLISME`)

- **Statut** : `ACCEPTÉE` (Décision non négociable de l'architecte au Cycle 5 ; amende `ADR-13`)
- **Portée** : Prévention de tout noyau fourre-tout dépassant $1/3$ du corpus ($40$ modules sur $120$).

---

## 1. Conflit Identifié au Cycle 4

Sous l'`ADR-13`, le noyau `CORPS` regroupait `69` modules sur `120` (`57,5 %` du corpus : `K2` = `26` + `K5` = `43`), dépassant largement le seuil de cohérence architecturale d'un tiers (`40` modules). Ce regroupement mélangeait l'appareil d'action immédiate (`OpenRig`, harnesses, bots, outils Anything, surfaces 3D) avec la détection prédictive ML/Wargame et l'usine économique B2B (`K5`).

## 2. Décision — Plafond Strict $\le 1/3$ (`40` modules) & Quatre Noyaux Équilibrés

1. **Invariant de Partition Équilibrée** : Aucun noyau fondamental de la Fondation A'Space OS V5 ne peut dépasser un tiers du corpus ($120 / 3 = 40$ modules maximum par noyau).
2. **Scission de `CORPS (69)` et Distribution sur 4 Noyaux Interconnectés (120/120 modules sans exception)** :
   - **`ÂME` (`Automaton`) — `29` modules (`24,2 % ≤ 33,3 %`)** :
     - **Organe `K1`** — Gouvernance Constitutionnelle, Vérification 13→1 & RSI (`11` modules : `fondation-13-1`, `automaton`, `prime-agent`, `elephant-goldfish-model`, `gsd-core`, `gstack`, `superpowers`, `adk-recipes`, `dream-rsi`, `rrsi`, `wikiskill`).
     - **Organe `K4`** — Mémoire Épistémique & Compétences (`18` modules : `auto-ontology`, `billion-context`, `context-language-models`, `dox`, `gbrain`, `graphify`, `infinite-brain-harness`, `infinite-brain-os`, `knowledge-catalog`, `llm-wiki`, `servers`, `caveman`, `claude-mem`, `hermes-agent`, `anthropic-skills`, `claude-video`, `mattpocock-skills`, `openai-plugins`).
   - **`SYSTÈME NERVEUX` (`Infinity`) — `29` modules (`24,2 % ≤ 33,3 %`)** :
     - **Bus Nerveux L0, Hibernation & Fibres** (`7` modules : `RigInfinity`, `infinity`, `cordis`, `pi`, `aspace-fiber-host`, `deepseek-harness`, `spynel`).
     - **Organe `K3`** — Inférence System-1/2 & Routage FreeCloud (`15` modules : `GLiNER2.5-multi-Decide`, `LFM3-Omni-2B`, `LoRA`, `mimi`, `moshi`, `needle`, `DeepInfer`, `cross-platform-llm-client`, `mesh-llm`, `bifrost`, `codex-chatgpt-web`, `freebuff`, `freellmapi`, `04_Inference_Youtube_Discovery_Registry`, `FreeVPS`).
     - **Organe `K3-ML`** — Cortex Prédictif & Wargame (`7` modules transférés de `K5` : `MiroFish`, `PathFM`, `autogluon`, `chronos-forecasting`, `mitra-2`, `tabfm`, `timesfm` — capteurs statistiques et simulation prédictive alimentant la prise de décision du système nerveux).
   - **`CORPS` (`OpenRig`) — `26` modules (`21,7 % ≤ 33,3 %`)** :
     - **Organe `K2`** — Exécution Multi-Harness, Bots Incarnés, Source-Control WAL, Outils Anything & Surfaces 3D (`26` modules : `openrig`, `agent-zero`, `herdr`, `herdr-core`, `herdr-app`, `openbot`, `openmuse`, `OpenDots`, `OpenDuet`, `openclaw`, `orca`, `t3code`, `claude-code`, `codex`, `a0-plugins`, `tuxee`, `source-control-natif`, `agent-office`, `city-office`, `cubefarm`, `space-agent`, `CLI-Anything`, `agent-browser`, `agent-desktop`, `api-anything`, `rea`).
   - **`MÉTABOLISME` (`BusinessOS`) — `36` modules (`30,0 % ≤ 33,3 %`)** :
     - **Organe `K5`** — Production Créative Vidéo/CAO, Finance Read-Only sous veto S0 & Valeur B2B (`36` modules : les `10` moteurs vidéo canoniques, les `11` actifs finance/trading read-only sous veto S0, les `13` services B2B/Apprentissage/BI + `00_Marketplace_YoutubeSkills` + `LibertyRide2`).

| Noyau Fondamental | Incarnation | Organes Rattachés | Nombre de Modules | Part du Corpus (Seuil $\le 33{,}3\,\%$) |
|---|---|---|---|---|
| **`ÂME`** | `Automaton` | `K1` (11) + `K4` (18) | **29** | `24,2 %` ($\le 40$) ✅ |
| **`SYSTÈME NERVEUX`** | `Infinity` | Bus L0 (7) + `K3` (15) + `K3-ML` (7) | **29** | `24,2 %` ($\le 40$) ✅ |
| **`CORPS`** | `OpenRig` | `K2` (26) | **26** | `21,7 %` ($\le 40$) ✅ |
| **`MÉTABOLISME`** | `BusinessOS` | `K5` (36) | **36** | `30,0 %` ($\le 40$) ✅ |
| **Total** | — | **Tous les organes** | **120** | **Max = 36 $\le$ 40** ✅ |

## 3. Contrats Communs d'Interconnexion L0 & Vérification Cycle 5

- Les 4 noyaux restent strictement interconnectés sur les mêmes contrats L0 (`EventJournal`, `R10Receipt`, `EpistemicFact M1-M8`, `FileLock O_EXCL`).
- **Preuve obligatoire de fusion (Cycle 5)** : aucun module `FKB04`, `FKB02`, `M117`, `M118` ne conserve le statut `FUSIONNÉ` sans comparaison différentielle automatisée comparant directement la sortie de l'organe natif à la sortie de la source d'origine sur des entrées identiques avant/après suppression physique réelle de la source. Tout module sans comparaison différentielle amont exécutable (ou sans fenêtre Win32 interactive réelle pour `M058`) passe ou demeure `PARTIEL`.
