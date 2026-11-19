---
okf_version: "0.2"
type: Decision
title: "ADR-11 — Source Canonique Unique & Purge des Doublons Inter-Pôles"
enonce_ref: "00_Memoire/bundle/fusion/FUSION-ENONCE.md"
enonce_sha256: "41889edb9c468ea62ee4641328c0e6f4bac2c618b81da751eebd2af4c05f648d"
---

# ADR-11 — Source Canonique Unique & Purge des Doublons Inter-Pôles
- **Statut** : `ACCEPTÉE`
- **Conflit** : 8 dépôts vidéo existent en double dans `.gitmodules` (`FKB02_Video_SaaS/*` pointant vers `FKB06_Video_SaaS/*` sans gitlink `160000` et déjà présents sous `FKB07_Money_Maker/02_Video/*`), `hermes-agent` existait en doublon FKB00/FKB04, `get-shit-done` a été remplacé par `gsd-core`, `OpenDuet` dupliquait `OpenBot`, et `infinite-brain-os` recouvre partiellement `OKF v0.2`.
- **Décision** :
  - **Cycle 1 exécuté** : suppression immédiate des 8 entrées doublons fantômes `FKB02_Video_SaaS/*` (`FKB06_Video_SaaS/*`) de `.gitmodules` (109 → 101 entrées alignées 1:1 avec les 101 gitlinks `160000`). Tous les moteurs vidéo fusionnent sous l'unique contrat `aspace_video_studio_foundation.py` en `FKB07_Money_Maker/02_Video/`.
  - `hermes-agent` conserve son unique emplacement canonique `FKB04` (avant absorption totale en `K4`) ; `gsd-core` remplace `get-shit-done`.
- **Invariant** : Zéro URL Git dupliquée dans `.gitmodules` (`len(.gitmodules) == len(distinct_urls) == len(gitlinks_160000)`).
- **Modules résolus** : les 10 moteurs vidéo (`OpenMontage`, `argo`, `earshot`, `explainroo`, `flute`, `huashu-motion`, `reanimate`, `rossark-motion-skill`, `take-one`, `video-director`) + 8 entrées doublons `FKB06`, `hermes-agent`, `gsd-core`, `OpenDuet`, `infinite-brain-os`, `anthropic-skills`, `mattpocock-skills`.
