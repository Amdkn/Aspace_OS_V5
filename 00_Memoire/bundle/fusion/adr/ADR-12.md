---
okf_version: "0.2"
type: Decision
title: "ADR-12 — Topologie de la Fondation : Réfutation de « 3 Noyaux FKB00 + FKB01..08 non fusionnés » → 5 Noyaux Interconnectés (`K1..K5`)"
enonce_ref: "00_Memoire/bundle/fusion/FUSION-ENONCE.md"
enonce_sha256: "41889edb9c468ea62ee4641328c0e6f4bac2c618b81da751eebd2af4c05f648d"
---

# ADR-12 — Topologie de la Fondation : Réfutation de « 3 Noyaux FKB00 + FKB01..08 non fusionnés » → 5 Noyaux Interconnectés (`K1..K5`)
- **Statut** : `ACCEPTÉE`
- **Conflit & Test de l'Hypothèse (§2)** : Le §2 demande explicitement de **tester l'hypothèse** : *« ces trois noyaux pour FKB00 (Automaton/Infinity/OpenRig), et FKB01 à FKB08 sans fusion »*.
- **Réfutation par les faits bruts** :
  1. Dans `FKB00` lui-même, les trois noyaux `Automaton / Infinity / OpenRig` ne couvrent pas la **vérité formelle et vérification déterministe** (`fondation-13-1` + `EGM/GSD/Superpowers` + `RSI hold-out`) ni l'isolation des **modèles ML prédictifs** (`MiroFish`, `PathFM`, `TabFM`, `TimesFM`, `Mitra-v2`, `Chronos-2`) qui obéissent à des contraintes de licences et de hold-outs totalement distinctes du daemon d'exécution.
  2. Laisser `FKB01..FKB08` sans fusion violerait directement les points (1), (2) et (4) de l'ÉNONCÉ :
     - `FKB06_Video_SaaS` est un **doublon mort** de `FKB07/02_Video` (0 gitlink actif, 8 entrées fantômes).
     - `FKB04` (`api-anything`, `CLI-Anything`, `agent-browser`, `agent-desktop`) et `FKB03` (`cubefarm`, `agent-office`, `city-office`) sont directement les interfaces d'action et de surface du système d'exécution (`K2`), pas des silos autonomes.
     - `FKB01` alimente directement le System-1 (`GLiNER/Needle`) et la passerelle (`:31415`) sans lesquels `Automaton`/`Agent-Zero`/`RigInfinity` sont muets (`K3`).
     - `FKB02` et `FKB08` fusionnent la mémoire épistémique vérifiée (`M1–M8`), l'ontologie (`auto-ontology`) et les compétences validées (`wikiskill` / `hermes` / `anthropic-skills`) dans un même noyau de savoir (`K4`).
     - `FKB00/02_PredictiveWargame_MachineLearning` + `FKB07_Money_Maker` forment la couche de prévision probabiliste et de génération de valeur B2B soumise aux mêmes garde-fous financiers et de licence (`K5`).
- **Décision déduite des principes** : La Fondation A'Space tient exactement en **5 Noyaux Interconnectés (`K1..K5`)** posés sur un **Socle L0 Commun** (3 contrats transversaux + fibre + test de suppression) :
  - **K1 — Gouvernance, Âme & Vérification** (11 modules)
  - **K2 — Exécution, Concurrence & Surface Vivante** (33 modules)
  - **K3 — Inférence & Décision Calibrée** (15 modules)
  - **K4 — Mémoire Neuro-Symbolique & Compétences** (18 modules)
  - **K5 — Prédictif, Wargame & Moteurs de Valeur B2B** (43 modules)
- **Invariant** : Chaque noyau `K1..K5` lit et émet via les 3 contrats L0 obligatoires (`EventJournal`, `R10Receipt`, `EpistemicFact`).
