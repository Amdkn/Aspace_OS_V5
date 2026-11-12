# Preuve H-R5 — D-N052 R4 (Dream-RSI + RRSI, H3)

**Verdict : PASS — 18/18 checks** (`RESULTS-R4.json`, rejouable :
`python3 run_holdouts_r4.py --snapshot /tmp/factory-r4-snapshot.sqlite --v5 <clone> --outdir .`).
Branche `a0/dn052-r4-dream` @ `9f5a5bb5a62d63cde380ba716fa0ebe0603ca4c0`,
base master `df115f9`, parent R3 `5bfa2db`.

## Ce qui est prouvé

Dream-RSI produit une variante, RRSI l'évalue en worktree, promotion
seulement si le gate l'accepte (beta mesuré sur le code, pas 0.35).

## Traces (réelles)

Snapshot live de `factory.sqlite` du PC
(`/mnt/c/Users/amado/Aspace OS V5/02_Factory/factory.sqlite`), copie par
API backup SQLite, sha256
`305c5a28ec0b1076bcd636efe6d158119d404cae093dcb6c5f663ac06cba3595`,
61 440 o, instantané 2026-11-11T14:08:28-05:00. **Byte-identique au
snapshot R3** : la base n'a pas bougé depuis 13:21. Live sha avant ==
après (`ea9043cf…`). 7 workflows / 9 steps / 6 events, lus par le
lecteur AQuA R0 (7 traces, base non modifiée). Diagnostic mécanique :
3 DEFECT / 4 PENDING. Détenteur du lock : âge 680 736 s (≈ 7,9 j).

| Rôle | Traces |
|---|---|
| Compilation | `h-p2-3-20261111-1245` (attente writer lock) |
| Validation T_val | `smoke-durable-01`, `h-p2-6-20261111-1250`, `h-p2-7-20261111-1255` |
| Holdout V5 | `smoke-chain-01`, `h-p2-11-20261111-1255`, `h-p2-3-20261111-1255` |

## Beta mesuré (pas 0.35)

- Grille β : `0, 0.25, 0.5, 0.75, 1` — `dream_rsi/learning/
  heuristic_search/eval.py:397`, README (table des variables).
- λ = 0.05 — `eval.py:79` (`DEFAULT_PARALLELISM_PENALTY`).
- **0.35 : 0 occurrence dans tout le dépôt dream-rsi** (grep mesuré,
  `third_party/` inclus).
- RRSI coding : delta 0.017, beta0 0.10, beta1 44.5, w_s 0.0, w_c 15.0,
  w_n 0.5 (`domains/coding/rrsi.json`).

## Replay (Dream)

Cinq variantes depuis la trace de compilation. Reward = AUC − 0.05
(miroir `_trace_auc` vérifié égal à la vraie fonction du fork :
0.2381 == 0.2381). Quatre variantes à égalité au reward 0.8071 (plafond
AUC — atteindre 1.0 sur la première sonde maximise la frontière) ;
la séparation vient du R pool : incumbent 1.0, `v-loose-7d` 1.0,
`v-tight-1h` 0.4286, `v-regress` 0.2857, `v-single-clause` 0.7143
(reward 0.1881). Dream garde l'incumbent sur l'égalité.

**Découverte mesurée : le TTL 1 h a expiré entre R3 et R4.** À 13:21 les
traces fraîches avaient ~30 min ; à 14:08 elles ont 4 390–5 004 s, donc
`v-tight-1h` diagnostique DEFECT les quatre traces PENDING. L'intervalle
invariant mesuré à R4 est [2 h, 7 j], pas [1 h, 7 j].

## Évaluation RRSI (vrais worktrees, vrai Algorithm 2)

Quatre candidats en vrais worktrees (`candidate/<nom>`, commits vérifiés,
variante chargée depuis le worktree). Critique : 4/4 pass (aucune
logique spécifique à une trace dans les clauses). `select_round` réel :
**gagnant = aucun** — incumbent S* = 1.0 (plafond) : `v-single`,
`v-regress`, `v-tight` bloquées par le plancher ajusté au bruit
(S 0.6667 / 0.3333 / 0.3333 < 0.983) ; `v-loose` rejetée par la règle de
coût dans la bande (façonnée 0, w_s = 0). Ce n'est pas un échec : la
sélection juge contre l'incumbent, le gate juge contre le jeu vide.

## Gate (vrai `gating.py`, Algorithm 1)

- Baseline T_val (S0 vide) : **R = 0.6667**, R_best = 0.6667.
- Itération 1 — `v-regress` : **R = 0.3333 → REJETÉE** ; rollback vérifié,
  wiki conservée.
- Itération 2 — `v-single-clause` : **R = 0.6667 → REJETÉE**
  (0.6667 n'est pas > 0.6667).
- Itération 3 — `v-tight-1h` : **R = 0.3333 → REJETÉE** (TTL 1 h expiré).
- Itération 4 — `v-loose-7d` : **R = 1.0 → ACCEPTÉE** ; marge 0.3333 ≥
  delta 0.0267 ; R_best 0.6667 → 1.0 ; skill committée.
- Holdout V5 (disjoint) : baseline 0.6667 → avec règle **1.0** (3/3).
- Promotion : `v-loose-7d` seulement (règle active unique ; seule sa
  branche candidate est fast-forwardée sur `evolve/v5-traces`).

## Daemon (substitution, test de jour)

`aspace-dream-daemon` — **SUBSTITUTION du daemon RigInfinity** (F8 D8,
pas livré), condition de retrait consignée dans son README. Test
`--run-now` : cycle DONE en < 1 s, checkpoint écrit, promu `v-loose-7d`,
R_best 1.0, exit 0. Non démarré en détaché : le coordinateur l'installe
et le démarre (supervisé) avant 00h. La course de nuit n'a pas eu lieu
pendant cette session.

## Découverte incidente

Lock orphelin vivant : `wid-20261103-170251/step-1` tient le writer lock
depuis le 2026-11-03 (8 jours) et bloque `h-p2-3-20261111-1245`. Fait
opérationnel réel, à router (hors R4) — décision Doctor requise, aucune
purge unilatérale.
