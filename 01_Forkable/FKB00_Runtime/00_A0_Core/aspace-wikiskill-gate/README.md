# aspace-wikiskill-gate — WikiSkill branché sur les traces AQuA (D-N052 R3, H2)

Adapter A'Space pour `wikiskill` (WikiSkill, arXiv:2608.27454) — design signé
Clara, D-N052 §D5/§D16. Le vrai `gating.py` (Algorithm 1) branché sur les
traces AQuA ; le backend est le harness V5.

## Ce qui est réel ici

- **Le gate** : `wikiskill/gating.py` du fork (`Amdkn/wikiskill` @ `59a6a04`,
  gitlink `01_Forkable/FKB00_Runtime/05_Recursive_RSI/wikiskill`) — état
  `runs/state.json`, skill set comme repo git (`skills/active`, commits
  base/accept, `reset --hard` + `clean` au rejet), wiki conservée.
  `src/gate_runner.py` orchestre les primitives réelles (`load_state`,
  `save_state`, `commit_base`, `apply_proposal`, `rollback`,
  `accept_commit`) ; la décision est Algorithm 1 verbatim
  (`R_val > R_best` → accept, sinon reject + rollback).
- **Les traces** : `factory.sqlite` (snapshot live du PC, voir la fiche)
  lues par le lecteur AQuA R0 (EvalCase) ; 7 traces réelles, 3 DEFECT /
  4 PENDING au diagnostic mécanique.
- **La règle** : compilée depuis la trace réelle `h-p2-3-20261111-1245`
  (workflow en attente d'un writer lock détenu par un step sans mise à jour
  depuis 8 jours) — `stale_writer_lock`.
- **Le delta** : recalculé `2·sqrt(0.8·0.2/900)` = **0.0267** (le 0.017 du
  docstring de la démo est retiré comme nombre ; voir la fiche pour la
  provenance corrigée : N=900, p=0.80 viennent du code de la démo, PAS du
  fork — vérifié : 0 occurrence dans le fork).
- **Le backend bench** : `src/bench_backend.py` — exécuteur déterministe des
  tâches du bench du fork (prompt + sandbox seulement, JAMAIS le grader).
  Mesuré : le split de validation du fork est au plafond (9/9 sans skill
  comme avec) — la skill diagnostique ne s'y discrimine pas (voir fiche §5).

## Layout

- `src/aqua_gate.py` — diagnostic attendu (mécanique), moteur de règles,
  compilation de règle, delta, fixture structurelle (sans texte libre).
- `src/gate_runner.py` — orchestration Algorithm 1 sur les traces.
- `src/bench_backend.py` — runner déterministe pour `gating.run_gate`
  sur les tâches du bench du fork.
- `smoke_test.py` — 5 tests offline (delta, diagnostics, gate
  accept/reject/rollback, backend sans accès grader, prompt inconnu).
- `fixtures/traces-v5-structural.jsonl` — les 7 traces réduites aux champs
  structurels (statuts, agents, tentatives, horodatages) — aucun texte
  libre, rejouable hors ligne.

## Preuve

`~/workspace/v4-factory/evidence/D-N052/r3/` — `run_holdouts_r3.py`,
`RESULTS-R3.json`, `H-R4-PROOF.md`. Le hold-out H-R4 y est rejoué en
entier sur le snapshot réel (accept 0.6667 → 1.0, rejet 0.3333, rollback
vérifié, wiki conservée, holdout V5 0.6667 → 1.0).
