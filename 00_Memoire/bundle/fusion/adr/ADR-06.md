---
okf_version: "0.2"
type: Decision
title: "ADR-06 — Auto-Amélioration Bornée par Hold-Out & Juge Externe vs Mutation Autonome"
enonce_ref: "00_Memoire/bundle/fusion/FUSION-ENONCE.md"
enonce_sha256: "41889edb9c468ea62ee4641328c0e6f4bac2c618b81da751eebd2af4c05f648d"
---

# ADR-06 — Auto-Amélioration Bornée par Hold-Out & Juge Externe vs Mutation Autonome
- **Statut** : `ACCEPTÉE`
- **Conflit** : `hermes-agent` (`/learn`), `prime-agent` (`/refine`), `rrsi` et `dream-rsi` proposent l'auto-modification continue des skills, prompts et worktrees, ce qui menace la stabilité de `FKB00` et des contrats L0.
- **Décision** : La boucle RSI à 3 Horizons est **strictement subordonnée au hold-out et au Juge externe** :
  - Horizon 1 (`prime-agent` / `RigInfinity`) : snapshots réversibles avant chaque `/refine`, rollback automatique si métrique baisse.
  - Horizon 2 (`wikiskill` + `adk-recipes` AQuA + `hermes-agent` `/learn`) : séparation des 4 rôles (Worker, Note-Taker, Playbook Writer, Strict Manager) ; promotion interdite si gain sur hold-out `< δ = 1.7 %`.
  - Horizon 3 (`dream-rsi` / `rrsi`) : replay hors-ligne à coût nul et mutations uniquement sur branches/worktrees jetables ; jamais d'écriture directe sur `master` ou `FKB00` sans validation indépendante (`judge-pr` + Juge externe).
- **Invariant** : Un créateur de mutation ne peut jamais valider sa propre promotion.
- **Modules résolus** : `prime-agent`, `wikiskill`, `adk-recipes`, `dream-rsi`, `rrsi`, `hermes-agent`, `gstack`, `superpowers`.
