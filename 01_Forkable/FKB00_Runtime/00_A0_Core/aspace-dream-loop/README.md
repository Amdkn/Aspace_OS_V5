# aspace-dream-loop — Dream-RSI + RRSI sur le backend harness V5 (D-N052 R4, H3)

Adapter A'Space pour `dream-rsi` (DREAM-RSI, Google Research) et `rrsi`
(RRSI, Google Research) — design signé Clara, D-N052 §4 R4, §D6, §D7, §D16,
§6 H-R5. La boucle rêve → worktree → évaluation → promotion par le gate R3.

## Ce qui est réel ici

- **Le gate** : le gate R3 (`aspace-wikiskill-gate`, `gate_runner.py` —
  vrai `gating.py` du fork wikiskill, Algorithm 1), consommé tel quel,
  non modifié. La promotion n'a lieu que si le gate accepte.
- **La sélection RRSI** : le vrai `rrsi/selection.py` du fork
  (`select_round`, `judge`, `cost_rule` — Algorithm 2), importé du fork
  en lecture seule, avec les paramètres de l'instance coding
  (`domains/coding/rrsi.json` : delta 0.017, beta0 0.10, beta1 44.5,
  w_s 0.0, w_c 15.0, w_n 0.5).
- **Le replay Dream-RSI** : l'objectif de replay (Éq. 1) tel qu'implémenté
  dans `dream_rsi/learning/heuristic_search/eval.py` — hypervolume
  budget↔attainment (AUC) moins la pénalité de parallélisme (λ = 0.05).
  `dream_loop.trace_auc` est une ré-implémentation verbatim du `_trace_auc`
  du fork ; le harnais vérifie l'égalité contre la vraie fonction du fork
  sur les mêmes points.
- **Les worktrees** : vrais git worktrees (un par candidat, branche
  `candidate/<nom>` depuis `evolve/v5-traces`, dans un dépôt scratch
  d'évolution — pas le dépôt V5). La variante est chargée DEPUIS le
  worktree pour l'évaluation. Accepter = fast-forward de la branche
  d'évolution vers le candidat (patron RRSI).
- **Les traces** : `factory.sqlite` (snapshot live du PC) lues par le
  lecteur AQuA R0 ; 7 traces réelles, mêmes splits que R3.

## Ce qui est miroir V5 (documenté, jamais caché — analogue J-4 de R3)

- **Le proposant Dream** est un générateur déterministe de variantes
  (TTL × sous-ensemble de clauses autour de la règle R3), pas un agent
  modèle comme dans le fork (`dream_rsi/agents/` : Gemini CLI, Claude
  Agent SDK, Codex CLI). Aucun appel modèle, aucun appel réseau.
- **Le monde de replay** est le pool de traces (7 traces, un seul monde,
  `n_evaluated` = 7 nœuds), pas un « discovery tree » du fork. Le
  `_pareto_summary` du fork sauterait 5 des 7 traces comme mondes
  (une seule step → `n_evaluated < 2` → AUC forcée à 0) — voir fiche §5.
- **Le budget** : à la préférence β, le replay évalue la variante sur les
  `max(1, ceil(β·7))` premières traces du pool (β = 0 : sonde minimale,
  β = 1 : exhaustif). La pénalité parallèle vaut 1.0 (miroir sériel).
- **Le coût RRSI** `C` : pas de tokens (aucun appel modèle) — le coût
  mesuré est le nombre d'évaluations de clauses (`n_clauses × n_traces`).
  Le ΔC relatif est ce que l'Algorithme 2 consomme.
- **Le rollout / grading** est le backend harness V5
  (`aqua_gate.score_split`), pas le `run_gate` du fork (bâti pour des
  tâches de bench, sandbox + runner modèle).

## Beta — mesuré sur le code (§D6)

- Grille β : `0, 0.25, 0.5, 0.75, 1` — `dream_rsi/learning/
  heuristic_search/eval.py:397` (`_parse_beta_grid`, défaut
  `DRSI_REPLAY_BETA_GRID`) et README (table des variables d'environnement).
- λ (pénalité de parallélisme) : `0.05` — `eval.py:79`
  (`DEFAULT_PARALLELISM_PENALTY`).
- **0.35 : 0 occurrence dans tout le dépôt dream-rsi** (mesuré par grep,
  `third_party/` inclus). C'est le nombre de la démo, pas du module — il
  n'est jamais utilisé comme valeur.
- RRSI (à ne pas confondre) : beta0 / beta1 sont les coefficients de la
  règle de coût de l'Algorithme 2 (coding : 0.10 / 44.5), pas une
  préférence de budget.

## Layout

- `src/dream_variants.py` — génération déterministe des variantes
  (Dream / explore) + écran du critique (pas de logique spécifique à une
  trace dans les clauses).
- `src/dream_loop.py` — replay β (learning), évaluation RRSI en worktree,
  sélection Algorithm 2, gate Algorithm 1, promotion.
- `smoke_test.py` — 7 checks offline sur la fixture structurelle R3
  (aucun snapshot live requis).
