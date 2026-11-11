# Fiche d'adaptation — WikiSkill, H2 (D-N052 R3)

**Module :** wikiskill — fork `Amdkn/wikiskill` ← `ashutoshsinghpr7/wikiskill`,
licence MIT, gel `cdc291c`, adapter `59a6a04` (tête du fork, re-pin R0),
adresse `fiber:a0:wikiskill`, état 2 (manifeste corrigé R0).
**Pas :** R3 (WikiSkill, H2) — dépend de R0 seulement (satisfaite).
**Design :** plan borné D-N052 signé Clara (§D5, §D16, §4, §6).
**Exécutant :** Ryan. **Branche :** `a0/dn052-r3-wikiskill` (base master
`df115f9` — voir §7 pour le choix de la base).

## 1. Actes

1. **Gitlink wikiskill restauré** (`05_Recursive_RSI/wikiskill` @ `59a6a04`)
   — le seul pointeur remis dans la branche (master vidé par `feb338e`,
   §7) ; le code du gate est importé du fork, jamais copié.
2. **Adapter `aspace-wikiskill-gate`** (`00_A0_Core/`) : branchement du vrai
   `gating.py` (Algorithm 1) sur les traces AQuA ; backend = harness V5
   (§D16) ; delta recalculé (§D5) ; holdout V5 (§D5).
3. **Preuve H-R4** : `~/workspace/v4-factory/evidence/D-N052/r3/`
   (`run_holdouts_r3.py`, `RESULTS-R3.json`, `H-R4-PROOF.md`).

## 2. Le gate — ce qui est réel, ce qui est V5

**Réel (fork, importé, jamais ré-implémenté)** : `gating.py` — état
`runs/state.json`, skill set comme repo git (`skills/active`, commits
base/accept, `reset --hard` + `clean` au rejet), wiki (`wiki/` + son repo
git). La décision est Algorithm 1 verbatim : `R_val > R_best` → accept,
sinon reject + rollback des skills seulement, wiki conservée. Le `run_gate`
du fork est utilisé tel quel pour les tâches du bench (avec le runner V5) ;
pour les traces, `run_gate_v5` en miroite la forme (mêmes primitives
d'état/git, même décision) parce que `run_gate`/`run_task` du fork sont
bâtis pour des tâches de bench (sandbox + runner modèle + `scoring.grade`).

**V5 (l'adapter définit le backend, §D16)** : rollout = moteur de règles
sur les traces AQuA ; grading = 1.0 si le diagnostic produit égale le
diagnostic attendu (mécanique, §3) ; trace = `factory.sqlite` via le
lecteur R0. Le backend bench est un exécuteur déterministe (prompt +
sandbox seulement, JAMAIS le grader — prouvé comportementalement par le
test d'altération du smoke test).

**Écart de boucle documenté** : pas d'early stop à `R_best == 1.0`
(contrairement à `harness.evolve`) — H-R4 exige de démontrer l'accept
PUIS le rejet (ou l'inverse) en séquence sur le même workspace ; le
contrôle de boucle est celui du runner, pas Algorithm 1, qui est intact.

## 3. Diagnostic attendu (mécanique, seuils nommés)

Vocabulaire : HEALTHY / DEFECT_DETECTED (démo `AquaDiagnostic`) + PENDING
(trace non terminale sans signal de défaut — une trace en cours n'est pas
une preuve de santé).

- DEFECT si (a) token d'échec (`fail/error/timeout/abort/crash`) dans le
  statut du workflow ou d'un step ; (b) attente d'un writer lock dont le
  détenteur n'a pas eu de mise à jour depuis plus de TTL_STALE ; (c)
  workflow ou step `running` sans mise à jour depuis plus de TTL_STALE.
- HEALTHY si workflow terminal-succès et tous steps succès.
- PENDING sinon.

**TTL_STALE = 24 h (86 400 s).** Robustesse mesurée sur le snapshot R3 :
la classification est INVARIANTE pour tout seuil dans [1 h, 7 j] — les
traces périmées ont ~8 jours, les fraîches quelques dizaines de minutes.
La valeur exacte dans cet intervalle ne peut pas changer le résultat.

## 4. Delta — recalculé 0.0267, provenance corrigée

`delta_min = 2·sqrt(p·(1−p)/N)`, N = 900, p = 0.80 →
`2·sqrt(0.8·0.2/900)` = 0.026666… → **0.0267**. Le 0.017 du docstring de
la démo est retiré comme nombre (conservé ici comme l'erreur qu'il était).

**Correction de provenance (vérifiée)** : N=900 et p=0.80 viennent du
code de la démo (`a0_recursive_factory.py`,
`WikiSkillPlaybookCompiler.__init__` : `holdout_size=900`,
`baseline_p=0.80`) — ils ne sont PAS dans le fork (vérifié : 0 occurrence
de `900`, `delta`, `0.017` dans `gating.py`, `scoring.py`, README du fork ;
Discover §69). La formule du design « avec le N et le p du fork » est
inexacte sur ce point ; la valeur 0.0267, elle, est celle que le design
épingle et que le code recalcule. Le gate décide par Algorithm 1 strict
(`R_val > R_best`) ; le delta est le plancher de bruit rapporté avec la
décision (marge vs `delta_min`), pas un second gate.

## 5. Splits — mesurés à l'exécution (design §D5)

**Source** : snapshot live de `factory.sqlite` du PC
(`/mnt/c/Users/amado/Aspace OS V5/02_Factory/factory.sqlite`), copie par
API backup SQLite (jamais de copie brute d'une base vivante), sha256
`305c5a28ec0b1076bcd636efe6d158119d404cae093dcb6c5f663ac06cba3595`,
61 440 o, 7 workflows / 9 steps / 6 events, instantané
2026-11-11T13:21:26-05:00. Statuts : 6 `running`, 1 attente de writer
lock ; aucun workflow terminal (ni succès ni échec) — les 2 workflows du
2026-11-03 tournent depuis 8 jours (défaut réel : lock périmé, voir §8).

| Rôle | Traces | Contenu |
|---|---|---|
| Compilation | `h-p2-3-20261111-1245` | attente writer lock, détenteur `wid-20261103-170251/step-1` (8 j) |
| Validation T_val | `smoke-durable-01`, `h-p2-6-20261111-1250`, `h-p2-7-20261111-1255` | 1 DEFECT + 2 PENDING |
| Holdout V5 | `smoke-chain-01`, `h-p2-11-20261111-1255`, `h-p2-3-20261111-1255` | 1 DEFECT + 2 PENDING |

Splits stratifiés (1 défaut + 2 en cours chacun), déclarés avant les runs.
N du holdout V5 = 3 (mesuré, pas inventé).

**Résultats mesurés (harness)** : baseline T_val R = 0.6667 ; règle
acceptée R = 1.0 (marge 0.3333 ≥ delta 0.0267, R_best 0.6667 → 1.0) ;
variante régressive R = 0.3333 → rejetée, rollback vérifié (skills
vides, wiki motifs inchangée) ; holdout V5 : 0.6667 → 1.0 avec la règle
acceptée.

**Split du fork (bench, graine 7 : 13 train / 9 val)** : exécuté pour de
vrai (`gating.run_gate` + `scoring.grade`, runner V5). Mesuré :
baseline 1.0 (9/9), avec skill 1.0 (9/9) — **plafond**. La skill
diagnostique ne s'y discrimine pas : le défaut de référence du bench
(`spec-format2-2`, commentaire bench.py) est un mode d'échec de MODÈLE
(« agents at tight budgets misread … as aggregate-by-name »), pas un
mode d'échec d'un backend déterministe. Le split du fork ne valide donc
pas la skill en R3 — limite mesurée, pas cachée : un backend modèle
serait nécessaire pour que ce split discrimine (amendement possible,
pas inventé ici). La validation substantive est le gate traces + holdout
V5 ci-dessus.

## 6. Règle compilée — `stale_writer_lock`

Depuis `h-p2-3-20261111-1245` (Note-Taker → Playbook Writer) :
- Clause 1 `lock_holder_stale` : attente de writer lock + détenteur sans
  mise à jour depuis plus de TTL_STALE → DEFECT.
- Clause 2 `running_stale` : workflow/step `running` sans mise à jour
  depuis plus de TTL_STALE → DEFECT.
Les deux clauses sont le même invariant (un step sans mise à jour depuis
plus de TTL_STALE est périmé), lu sur cette seule trace : la trace nomme
son détenteur, et le détenteur EST un des steps périmés du 3 nov.
(âge du détenteur au snapshot : 677 914 s ≈ 7,8 j).

**Contrôle négatif** : variante surgénéralisée `running_means_defect`
(« running → DEFECT », lecture fautive de la même trace) : R = 0.3333
sur T_val → rejetée, rollback vérifié.

## 7. Base de branche — master vidé (`feb338e`)

Vérifié à l'API : `feb338e` (2026-11-11T10:06:54Z, « Pulse workgraph
05:05 ») a réduit l'arbre master à `00_Memoire` seule (parent `0065bc5` :
21 entrées). Dernier master sain : `0065bc5`. La branche R3 part du HEAD
master courant `df115f9` (et NON de `0065bc5`) : une branche depuis le
dernier master sain ferait de la PR une restauration intégrale du repo —
ce qui préempterait la décision S0 en attente sur la restauration. La PR
R3 ne contient donc que le gitlink wikiskill + l'adapter (diff petit,
jugeable) ; aucun merge, aucun commit vers master.

## 8. Découverte incidente (hors R3, à router)

Le snapshot réel montre un **writer lock périmé vivant** : le step
`wid-20261103-170251/step-1` tient le lock depuis le 2026-11-03 17:02
(8 jours, statut `running` sans mise à jour) et bloque
`h-p2-3-20261111-1245` (en attente depuis 12:45 aujourd'hui). C'est le
défaut que la règle détecte — et un fait opérationnel réel, pas un
artefact de preuve : la factory a un lock orphelin depuis 8 jours.
À router au coordinateur (pas un acte R3).

## 9. Limites et réserves

- R-1 : le split du fork est au plafond avec le backend déterministe
  (§5) — la validation fork ne discrimine pas la skill en R3.
- R-2 : `factory.sqlite` n'a jamais été commité dans V5 (vérifié :
  `git log --all` vide sur ce chemin) ; la source de traces est le
  snapshot live du PC (§5), pas le repo. Les 7 traces sont toutes non
  terminales ; aucun succès terminal dans le jeu (HEALTHY non exercé sur
  données réelles — exercé dans le smoke test sur données synthétiques).
- R-3 : la règle `stale_writer_lock` ne couvre que les défauts de
  péremption/blocage ; un défaut à token d'échec (`failed`) n'apparaît
  dans aucune trace réelle du snapshot.
- Aucune dépense ; aucun secret en clair (les traces consignées en
  evidence sont scannées ; la fixture du repo est structurelle, sans
  texte libre) ; aucun appel modèle ; aucune activation client.
