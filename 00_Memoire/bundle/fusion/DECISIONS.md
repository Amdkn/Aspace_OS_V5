---
okf_version: "0.2"
type: DecisionLog
title: "Journal des Décisions Réversibles — Fusion Fondation (Cycle 7)"
enonce_ref: "00_Memoire/bundle/fusion/FUSION-ENONCE.md"
enonce_sha256: "41889edb9c468ea62ee4641328c0e6f4bac2c618b81da751eebd2af4c05f648d"
---

# DECISIONS — A'Space OS V5 (Cycle 7)

| Date | Décision | Raison | Alternative écartée |
|---|---|---|---|
| 2026-11-19 | Utiliser `ubuntu-latest` dans `.github/workflows/foundation-proof.yml` | Compile et exécute `RigInfinity` nativement en sockets Unix sans WSL tout en exécutant `pwsh` sur `02_Factory/checks.ps1` via chemins `/` portables | `windows-latest` dépourvu de WSL UmbrelOS préinstallé pour `RigInfinity` |
| 2026-11-19 | Initialiser récursivement en CI uniquement les sous-modules exercés par les preuves (dont `RigInfinity == 95e95f9`) | Évite plusieurs Go d'historiques non utilisés dans les 3 suites tout en garantissant 100 % des oracles et tests Rust fail-closed | `git submodule update --init --recursive` global sur l'ensemble des 101 gitlinks |
