---
okf_version: "0.2"
type: Decision
title: "ADR-05 — Isolation Poisson Rouge (`EGM`) & Sparse (`Scion`) vs Contexte Monolithique"
enonce_ref: "00_Memoire/bundle/fusion/FUSION-ENONCE.md"
enonce_sha256: "41889edb9c468ea62ee4641328c0e6f4bac2c618b81da751eebd2af4c05f648d"
---

# ADR-05 — Isolation Poisson Rouge (`EGM`) & Sparse (`Scion`) vs Contexte Monolithique
- **Statut** : `ACCEPTÉE`
- **Conflit** : `billion-context` et `claude-mem` tendent à accumuler d'immenses fenêtres historiques, tandis que `elephant-goldfish-model` (EGM), `caveman` et `source-control-natif` (Scion sparse + changeset CAS sans copie) prouvent que l'accumulation dégrade la précision et explose les coûts.
- **Décision** : Couplage obligatoire **Éléphant (`K4`/SQLite WAL) × Poisson Rouge (`K2` exécution bornée)** :
  - L'état macro et les blobs CAS SHA-256 (`billion-context`, `changeset WAL`) restent sur disque/NVMe.
  - Chaque worker ne reçoit qu'un sous-graphe élagué, une vue sparse de ses fichiers cibles (`Scion`), et communique en mode télégraphique (`caveman`) sans perte d'identifiants.
  - Les surfaces `BusinessOS` inutilisées (« trous » non consommés par aucun lecteur) sont supprimées selon la règle sparse.
- **Invariant** : Aucun worker d'exécution ne charge l'intégralité du graphe `memory.jsonl` (`read_graph` interdit en routine).
- **Modules résolus** : `elephant-goldfish-model`, `billion-context`, `caveman`, `source-control-natif`, `orca`, `tuxee`, `BusinessOS`.
