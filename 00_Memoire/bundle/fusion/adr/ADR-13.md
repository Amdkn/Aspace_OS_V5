---
okf_version: "0.2"
type: Decision
title: "ADR-13 — Amendement ADR-12 : Trois Noyaux (ÂME / SYSTÈME NERVEUX / CORPS) & Trajectoire d'Un Cœur (Python → Hybride → Rust)"
enonce_ref: "00_Memoire/bundle/fusion/FUSION-ENONCE.md"
enonce_sha256: "41889edb9c468ea62ee4641328c0e6f4bac2c618b81da751eebd2af4c05f648d"
amends: "ADR-12"
---

# ADR-13 — Trois Noyaux Fondamentaux (`ÂME / SYSTÈME NERVEUX / CORPS`) & Trajectoire du Cœur (`Python → Hybride → Rust`)

- **Statut** : `ACCEPTÉE` (Décision non négociable de l'architecte ; amende `ADR-12`)
- **Portée** : Topologie racine de la Fondation A'Space OS V5 et feuille de route d'évolution d'un seul cœur exécutable.

---

## 1. Clarification et Amendement de l'`ADR-12` (La Base des Trois Noyaux)

L'`ADR-12` a réfuté par les faits une variante précise : *« trois noyaux dans `FKB00` avec `FKB01` à `FKB08` laissés sans fusion »*. Elle en a conclu à tort qu'il fallait ériger `K1..K5` en cinq racines séparées.

En application de la doctrine fondatrice (`tryptyque-runtime-core-fusion.md`), **tous les modules de $F$ (`FKB00` à `FKB08`, 120 modules sans exception)** fusionnent ou se rattachent sous exactement **Trois Noyaux Fondamentaux** interconnectés sur le socle L0 (`fondation-13-1` / `RigInfinity`) :

1. **`ÂME` (`Automaton` — doctrine, gouvernance constitutionnelle, vérification 13→1, mémoire épistémique & compétences)** :
   - **Organes rattachés** :
     - **Organe `K1` — Gouvernance, Vérification 13→1 & RSI** (`fondation-13-1`, `automaton`, `prime-agent`, `elephant-goldfish-model`, `gsd-core`, `gstack`, `superpowers`, `adk-recipes`, `dream-rsi`, `rrsi`, `wikiskill` — 11 modules).
     - **Organe `K4` — Mémoire Neuro-Symbolique & Compétences** (`auto-ontology`, `billion-context`, `context-language-models`, `dox`, `gbrain`, `graphify`, `infinite-brain-harness`, `infinite-brain-os`, `knowledge-catalog`, `llm-wiki`, `servers`, `caveman`, `claude-mem`, `hermes-agent`, `anthropic-skills`, `claude-video`, `mattpocock-skills`, `openai-plugins` — 18 modules).
   - **Responsabilité** : porter la loi, la mémoire vérifiée (`M1–M8`), l'ontologie DAG, l'isolation EGM, les baux TTL et la porte hold-out (`δ ≥ 1.7 %`) du RSI.

2. **`SYSTÈME NERVEUX` (`Infinity` — journal d'événements L0, reçus R10, hibernation pure-data, fibres réactives & inférence calibrée)** :
   - **Organes rattachés** :
     - **Bus Nerveux L0, Hibernation & Fibres** (`RigInfinity`, `infinity`, `cordis`, `pi`, `aspace-fiber-host`, `deepseek-harness`, `spynel` — 7 modules).
     - **Organe `K3` — Inférence System-1/2 & Routage FreeCloud** (`GLiNER2.5-multi-Decide`, `LFM3-Omni-2B`, `LoRA`, `mimi`, `moshi`, `needle`, `DeepInfer`, `cross-platform-llm-client`, `mesh-llm`, `bifrost`, `codex-chatgpt-web`, `freebuff`, `freellmapi`, `04_Inference_Youtube_Discovery_Registry`, `FreeVPS` — 15 modules).
   - **Responsabilité** : assurer le réveil strictement événementiel (coût zéro entre tours), la commutation réactive (`RAP`, `Cordis`), l'inscription append-only du journal L0 + reçus `R10`, et l'irrigation inférentielle souveraine System-1 (< 10 ms) / FreeCloud (`:31415`).

3. **`CORPS` (`OpenRig` — exécution multi-harness, source-control WAL, outils Anything, surfaces 3D & moteurs prédictifs/B2B)** :
   - **Organes rattachés** :
     - **Organe `K2` — Action Multi-Harness, Outils Anything & Surfaces 3D** (`openrig`, `agent-zero`, `herdr`, `herdr-core`, `herdr-app`, `openbot`, `openmuse`, `OpenDots`, `OpenDuet`, `openclaw`, `orca`, `t3code`, `claude-code`, `codex`, `a0-plugins`, `tuxee`, `source-control-natif`, `agent-office`, `city-office`, `cubefarm`, `space-agent`, `CLI-Anything`, `agent-browser`, `agent-desktop`, `api-anything`, `rea` — 26 modules).
     - **Organe `K5` — Moteurs Prédictifs, Wargame, Studio Vidéo & Valeur B2B** (`autogluon`, `chronos-forecasting`, `mitra-2`, `tabfm`, `timesfm`, `MiroFish`, `PathFM`, les 10 moteurs vidéo canoniques + 8 doublons purgés FKB06, les 11 actifs trading read-only sous veto `S0`, les 13 services B2B + `00_Marketplace_YoutubeSkills` + `LibertyRide2` — 43 modules).
   - **Responsabilité** : exécuter les actions sur le monde matériel/logiciel sans fragmentation de daemons, incarner les 578 Holons en 3D et produire la valeur B2B sous confinement de licences et veto `S0`.

- **Distribution des 120 modules sans exception** : `ÂME` (29) · `SYSTÈME NERVEUX` (22) · `CORPS` (69) = **120 modules**.

---

## 2. Trajectoire d'Un Seul Cœur Qui Évolue (`Python → Hybride → Rust`)

Il n'existe **pas deux cœurs concurrents** : un seul cœur formel évolue en 3 phases séquentielles. **À chaque phase, les fixtures Rust canoniques de `fondation-13-1` (`anchor-001.json`, `anchor-002.json`, `anchor-026.json`, `dispatch-*.json`, `citation-*.md`) font foi.**

| Phase | Implémentation du Cœur | Invariant de Vérité | Critère de Passage Exécutable vers la Phase Suivante |
|---|---|---|---|
| **Phase 1 — Python** | `aspace_foundation_kernel.py` + organes Python (`K1..K5`) | 100 % des fixtures Rust validées octet pour octet (`R1–R8`, `V1–V8`, `M1–M8`) ; `0` correction silencieuse | 1. Toolchain `rustup`/`cargo` active localement.<br>2. `cargo test` **100 % vert** sur `fondation-13-1` (100/100) et `RigInfinity` (105/105).<br>3. Binaires Rust compilés (`r10-receive`, `route-dispatch`, `recall-fact`) invocables depuis Python sur les fixtures. |
| **Phase 2 — Hybride** *(atteinte au Cycle 4)* | Python orchestre les organes fonctionnels absorbeurs (`FKB04`, `FKB02`, etc.) tandis que le noyau L0 invoque et contre-valide via les binaires Rust (`fondation-13-1` + `RigInfinity`) | Concordance 1:1 (differential verification) entre la validation Python et la sortie des binaires Rust ; tests de suppression réussis par le Juge externe | 1. Tous les modules cibles `FUSIONNÉ` de `FKB01..FKB08` ont passé le test de suppression du Juge externe sur clone propre.<br>2. Chaque organe Python (`K1..K5`) a son équivalent porté en crate Rust dans le workspace unifié `RigInfinity × fondation-13-1`.<br>3. L'exécution des fixtures canoniques + suite hold-out est identique à 100 % en Rust pur sans interpréteur Python L0/L1. |
| **Phase 3 — Rust (Destination)** | Workspace Rust souverain unique (`RigInfinity × fondation-13-1`) portant les Trois Noyaux (`ÂME`, `SYSTÈME NERVEUX`, `CORPS`) et leurs organes `K1..K5` | Zéro dépendance runtime Python dans le socle L0/L1 ; 1 seul processus daemon maître loopback (`127.0.0.1`) ; `0 connect()` externe non autorisé | `cargo test --workspace` 100 % vert (dont 100 % des fixtures `anchor-*` et hold-out), validé par le Juge externe lecture seule. |

---

## 3. Modules Résolus & Invariants
- **Invariant Topologique** : Tout module du `REGISTRE-DE-FUSION.md` (`M001..M120`) déclare explicitement son noyau racine parmi `{ÂME, SYSTÈME NERVEUX, CORPS}` et son organe rattaché (`K1..K5` / Bus L0).
- **Invariant de Régression** : Aucun code Python de Phase 1 ou Phase 2 ne peut introduire de règle sémantique divergente des fixtures Rust de `fondation-13-1/tests/fixtures/`.
