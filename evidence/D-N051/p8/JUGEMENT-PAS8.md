# Jugement 13e — D-N051 F8 pas 8 : RigInfinity natif, l'incorporation (PR #43)

**Juge :** 13e (fonction indépendante — ni exécutant, ni coordinateur).
**Objet :** PR [#43](https://github.com/Amdkn/Aspace_OS_V5/pull/43) — « D-N051 F8 pas 8 : RigInfinity natif, l'incorporation (état 2 → 3) »,
branche `ryan/d-n051-f8-pas8`, base master `0b16b3a`, tête `c8ed937` (1 commit, 1 parent : `0b16b3a`).
**Norme :** plan borné signé Clara `FUSION-F8-PAS8-RIGINFINITY-NATIF-plan-borne.md` (D1–D18, H-M1..M7 ×11, H-P8-1..11, H-F8-1/2/3/4/5/8/9).
**Pièces lues en entier :** plan, Discover Bill, `RAPPORT-PAS8.md`, `RESULTS-F8-P8.json`, jugement 13e pas 7 (`JUGEMENT-PAS7.md`).
**Méthode :** rien pris sur parole — chaque fait re-vérifié à la source (API GitHub, clones frais `~/juge-p8/`,
re-cours complet de la suite cargo + clippy + fmt + daemon live + strace + les 7 suites adapter + tsc extension pi).
`TMPDIR` sur `$HOME/juge-p8` pour tous les runs (`/tmp` 512 Mo, leçon des pas 7/8).
**Incident de méthode (nommé, sans effet sur les mesures) :** la machine d'exécution a été remplacée en cours
de jugement (~17:2x) — `/home/juge-p8` a disparu avec elle. Le travail a repris dans `~/juge-p8`
(home persistant) : **tous les re-cours ont été refaits** (cargo, clippy, fmt, daemon, strace, 7 suites adapter,
2 tsc) et les valeurs citées ci-dessous sont celles des runs post-reprise, avec leurs logs survivants ;
les runs pré-remplacement avaient donné les mêmes chiffres, observés en sortie d'outil.

## Verdict : VALIDÉE AVEC RÉSERVES

## Recommandation merge : OUI après amendements — INTERDIT sur la tête `c8ed937`

Le fond est validé : le merge `9050a1f` est un vrai merge, `/refine` est re-prouvé **par comportement**,
les 7 pointeurs + le gitlink herdr-core sont retirés de l'arbre (pas seulement de `.gitmodules`),
le daemon unique est compté live (1 processus, 0 `hc`), la LICENSE est déposée, le manifeste est à jour,
les 7 suites adapter sont vertes en re-cours indépendant, le pin est prouvé 7/7 à l'API avant retrait.
**Aucun défaut de substance ne bloque le merge.** Ce qui bloque, ce sont **trois lignes de documents**
— dont une qui touche au compteur de clôture de F8 lui-même (§1) : le registre déposé dit
« 11 en état 2, 0 en état 3 » alors que la condition de succès du plan exige « les 11 en état 3 ».
Le merge est autorisé dès les amendements ci-dessous livrés, vérifiés par le coordinateur à l'API + CI verte —
sans nouveau jugement complet.

### Conditions exactes de merge (toutes à remplir, dans l'ordre)

- **C1 — Fiche pi (H-M7, F10) :** ajouter dans `01_Forkable/FKB00_Runtime/00_A0_Core/pi-ADAPTATION.md`
  la ligne « pi en état 3 **sous condition H-P8-pi** (vert de la Phase D du pas 2, plan pas 8 §D5) ».
  Vérifiable au fichier : 1 occurrence de « H-P8-pi » dans la fiche.
- **C2 — Rapport + harnais (F7, F9) :** (a) `evidence/D-N051/p8/RAPPORT-PAS8.md` §8 : « 28 chemins » → **« 30 chemins »**,
  Modifiés 17 → **19** (ajouter `.gitmodules` et `agent-zero-ADAPTATION.md` à la liste) ;
  (b) `RAPPORT-PAS8.md` §4 et `RESULTS-F8-P8.json` (détail H-P8-7) : remplacer
  « cycle Intake → Éveil → Rig → Résolution → Validation prouvé en suite » par
  « cycle H1 + refinement prouvés en suite (`runtime_cycle_with_h1_over_a_real_gateway_stub` vert) ;
  cycle complet 5 étapes en suivi machine réelle ».
- **C3 — Registre, compteurs (F11) :** `01_Forkable/FUSIONS-REGISTRY.md` ligne 90 : les compteurs deviennent
  **« 0 en état 0, 0 en état 1, 0 en état 2, 11 en état 3 — pi en état 3 sous condition H-P8-pi (§D5) »**,
  en lieu et place de « 0, 0, 11 en état 2, 0 en état 3 ». Vérifiable au fichier : la ligne 90 porte
  « 11 en état 3 » et « 0 en état 2 ».
- **C4 — CI :** re-courir la CI sur la tête amendée ; **8/8 `completed/success`** exigés, `mergeable: true`
  + `mergeable_state: clean` conservés. Le merge est ensuite un **true merge (2 parents, DVG-01)** :
  parents `0b16b3a` + tête amendée.

---

## 1. La question principale — les compteurs du registre (F11) : « 0/0/11/0 » ne dit pas « les 11 en état 3 »

**Fait vérifié au fichier (clone frais, branche PR, tête `c8ed937`) :**

```
- **Mesures :** compteur états 0–3 — **0 en état 0, 0 en état 1, 11 en état 2** (cordis, automaton, pi,
  infinity, agent-zero, openrig, prime-agent, openbot, openmuse, OpenDots, OpenDuet), **0 en état 3**
  — pi en état 3 sous condition H-P8-pi (§D5 du plan pas 8)
```

Le format est celui du registre lui-même, établi aux pas précédents (Discover §0.1, jugement pas 7 §2 :
avant le pas 8 : 0/1/10/0 = 0 en état 0, 1 en état 1 — pi —, 10 en état 2, 0 en état 3).
Après le pas 8, pi passe 1 → 3 et les dix passent 2 → 3 : le compte honnête est **0/0/0/11**.
Or la ligne déposée dit 11 en état 2, 0 en état 3.

**Le plan se contredit lui-même, et l'exécution a suivi la lettre contre le fond :**
- §D13 : « ligne 90 compteurs → 0/0/11/0 » ; §5 : « les compteurs F8 sont à 0/0/11/0 ».
- §5 (condition de succès) et H-F8-8 : « **les 11 en état 3** (pi sous condition H-P8-pi) » ; §5 : « F8 est CLOSE ».
- Les deux ne peuvent pas être vrais ensemble sous le format (état 0, état 1, état 2, état 3) du registre.
  « 0/0/11/0 » place les 11 dans la case état 2 ; « les 11 en état 3 » les place dans la case état 3.
- Le détail `COMPTEUR-F8` de RESULTS (« 0/0/11/0 visés … état 3 effectif au jugement ») ne résout rien :
  il rationalise l'écart (« effectif au jugement ») au lieu de le corriger — le registre déposé dit 0 en état 3.

**Décision :** la condition de succès (§5, H-F8-8) est l'exigence de fond ; le chiffre §D13 est la coquille.
Le registre est le document de référence de F8 : il ne peut pas clore F8 en affichant 0 en état 3.
Corrigé par **C3**. Si Clara entend maintenir « 0/0/11/0 », c'est un amendement du plan qui doit aussi
réécrire §5 et H-F8-8 (redéfinir ce que compte le compteur) — pas une lecture que le juge puisse trancher seul.

---

## 2. Hold-outs — verdicts du juge (preuves re-courues)

### H-M1..M7 ×11 — tous PASS sauf H-M3 ×4 (voir §3)

| Hold-out | 7 restants | 4 déjà retirés | Preuve du juge |
|---|---|---|---|
| H-M1 pin contient l'adapter | PASS ×7 | PASS (pin « retiré au pas 5/7 ») | H-P7-1-PIN 7/7 re-prouvé à l'API (§5) ; agent-zero : gitlink pré-retrait `176d23f` vérifié dans l'historique V5 (commit `1cf831a`) |
| H-M2 adapter seul code A'Space | PASS ×11 | — | Diffs gel…pin cités des pas d'adaptation ; fiches corrigées C2 (§7) ; 0 import du fork hors adapter (vérifié aux pas d'adaptation, repris) |
| H-M3 suite adapter | PASS ×7 | **QUALIFIÉ** ×4 | §3, re-cours complets ci-dessous (7/7) ; les 4 déjà retirés cités de leur pas, pas re-courus (§D18) |
| H-M4 télémétrie zéro | PASS ×11 | — | Audits lus aux pas d'adaptation ; strace natif re-couru §4 (0 `connect()`) |
| H-M5 manifeste | PASS ×11 | — | `fiber:a0:<module>` lus dans le clone frais PR ; `levels.current` = 2 (×10), pi = 1 |
| H-M6 frontière adapter | PASS ×11 | — | Adapter seul code A'Space ; sections divergence remplies ; propriétaire cœur Buzz |
| H-M7 fiche | PASS ×10, **voir F10** | — | 11 fiches présentes ; 0 occurrence « Pin (bind) » (grep, 37 fiches) ; **fiche pi sans la ligne H-P8-pi (C1)** |

### H-P8-1..H-P8-11

| # | Verdict juge | Preuve |
|---|---|---|
| H-P8-1 merge `9050a1f` + `/refine` | **PASS** | Vrai merge `95e95f9` (2 parents `11a82ba` + `9050a1f`, API + clone frais) ; cargo 105/105 re-couru ; `refine_available()` = preuve par comportement (§4, R-J10 levée) ; gitlink re-piné `95e95f9` |
| H-P8-2 LICENSE V5 | **PASS** | `LICENSE` à la racine, 11 338 o ; diff vs LICENSE RigInfinity = 1 seule ligne (l. 189, `Copyright 2026 A'Space`) |
| H-P8-3 harnais voit le pin | **PASS** | H-P7-1-PIN 7/7 re-prouvé à l'API avant tout retrait (§5) |
| H-P8-4 daemon herdr-core + PTY | **PASS** | Fibre retirée du superviseur (0 occurrence `fiber:ade:herdr-core-pty`) ; gitlink `14a3772` retiré ; socket absent ; 0 `hc` ; `pty_proof` 1/1 vert dans la suite 105/105 (`daemon_opens_pty_session_and_executes_command_with_receipt ... ok`) |
| H-P8-5 liste fermée §D14 | **PASS** | Coupes vérifiées au diff (§6) ; extension pi compilée sans le gitlink (tsc --strict EXIT 0, §3) ; chaînes `Amdkn/openbot` légitimes (§6) |
| H-P8-6 un seul daemon, compté live | **PASS** | `fn main` unique, 1 `[[bin]]` ; daemon lancé + compté live : **1 processus `riginfinity-dae`, 0 `hc`** (§4) |
| H-P8-7 cycle sans les originaux | **PARTIEL** | Smoke du harnais vert (cycle H1 + refinement, §4) ; **formulation sur-vendue (F9)** ; cycle complet 5 étapes sur machine réelle = SUIVI (§D9–D10) |
| H-P8-8 manifeste à jour | **PASS** | Pin `95e95f9`, 46 fichiers (26 src / 9 203 l. + 7 tests / 2 082 l., re-comptés), suite 105/105, ports SC-2 + pas 7 + pas 8, `single_daemon` PROUVÉ, `prime_agent_non_merge` RÉSOLU, prime-agent rayé (4 dettes restantes), `state: 2` (§D1) — **R-J5 levée** |
| H-P8-9 registre + fiches | **PASS sauf C3** | Ligne 89 corrigée (pas 6 CLOSE 789, pas 7 CLOSE 914, pas 8 en cours) ; ligne 90 cordis corrigée `a40cc74` ; 0 occurrence « Pin (bind) » ; **compteurs faux en substance (F11, C3)** |
| H-P8-10 pi conditionnelle | **PASS sauf C1** | H-P8-pi nommée au registre (l. 90) et dans RESULTS ; **absente de la fiche pi (F10, C1)** ; retrait du pointeur, coupure des références, smoke et compilation inconditionnels |
| H-P8-11 plafonds | **QUALIFIÉ** | Patron p5, comme à tous les pas (R-J7 reportée) |

### H-F8

| # | Verdict juge | Preuve |
|---|---|---|
| H-F8-1 7 pointeurs retirés | **PASS** | `.gitmodules` 114 → 106 ; gitlinks 106 → 98 ; les 8 chemins nommés absents de l'arbre ; RigInfinity présent, re-piné `95e95f9` |
| H-F8-2 cycle sans originaux | **PARTIEL** | Voir H-P8-7 (F9) |
| H-F8-3 incorporation native | **PARTIEL** | (a) fonction native 105/105 ; (b) pointeurs retirés ; (c) smoke PARTIEL ; (d) **validation 13e rendue par le présent jugement** |
| H-F8-4 un seul daemon | **PASS** | Construction + comptage live (§4) — **R-J8 levée** |
| H-F8-5 heartbeat, pas de cron | **PASS** | 0 « cron » dans `Cargo.lock` ; mentions en src = commentaires d'abandon/refus ; tests de refus verts dans la suite 105/105 |
| H-F8-8 final | **PARTIEL** | `.gitmodules` : 0 des 11 ; LICENSE à la racine ; manifeste à jour ; **les 11 en état 3 = le présent jugement (pi sous condition H-P8-pi) ; compteurs à corriger (C3)** |
| H-F8-9 plafonds | **QUALIFIÉ** | Voir H-P8-11 (R-J7 reportée) |

Compteurs vérifiés au fichier (branche PR) : **F8 0/0/11/0 déposé, 0/0/0/11 exigé (C3)** ;
**D-N053 25 → 3 inchangé** (herdr `df9b626`, herdr-core, orca `b659760` toujours pointés ; seul le gitlink
herdr-core est retiré, comme acte daemon F8, pas comme développement D-N053).
Recompte de `RESULTS-F8-P8.json` par le juge : **97 checks — 87 PASS, 6 QUALIFIÉ, 4 PARTIEL, 0 FAIL — exact**
(statut écrit « QUALIFIE » sans accent dans le JSON ; PARTIEL : H-P8-7, H-F8-2, H-F8-3, H-F8-8 ;
QUALIFIÉ : H-P8-11, H-F8-9, H-M3-agent-zero, H-M3-openmuse, H-M3-OpenDots, H-M3-OpenDuet).

---

## 3. Suites adapter re-courues par le juge (clones frais, aux pins)

| Module | Commande du juge | Résultat juge | Exécutant |
|---|---|---|---|
| cordis `a40cc74` | `npm install --legacy-peer-deps` + build + `vitest run …/smoke.spec.ts` | **3/3, EXIT 0** | 3/3 |
| automaton `7cdaa00` | `bun smoke_test.ts` | **21/21, EXIT 0** | 21/21 |
| pi `13be830` | `node --experimental-strip-types smoke_test.ts` (`V5_CONFIG` sur le clone PR) | **45/45, EXIT 0** | 45/45 |
| infinity `007409e` | `cargo test` (adapter) | **13/13, EXIT 0** (lib 4 + smoke 3 + mcp_rap_proof 6) | 13/13 |
| openrig `649376c` | `npm ci` + `node --experimental-strip-types smoke_test.ts` (branche `main`) + `tsc -p` adapter (strict) | **61/61, EXIT 0 ; tsc EXIT 0** | 61/61, tsc EXIT 0 |
| prime-agent `3bac96a` | `cargo test` (adapter) | **18/18, EXIT 0** (lib 12 + smoke 5 + guard 1) | 18/18 |
| openbot `6e62238` | `bun test ./tests/adapter.checks.ts` | **9/9, EXIT 0** | 9/9 |

**Extension pi (§D5, H-P8-5) :** imports par nom npm uniquement
(`@earendil-works/pi-coding-agent`, `typebox`, `node:child_process`), 0 import du sous-module, 0 import relatif.
`tsc --noEmit --strict` **EXIT 0** avec la configuration du projet pi (target ES2024, `skipLibCheck: true`,
strict) — 0 erreur dans `aspace-factory.ts` sur 3 runs (voir F8 : 2 runs à nu échouent sur des `.d.ts`
de dépendances uniquement, jamais sur le fichier lui-même).

**Incidents de re-cours (artefacts de méthode du juge, prouvés comme tels, pas des défauts du code) :**
- **openrig, 1er run de l'exécutant 60/61** (« branch is main ») : artefact du checkout détaché, confirmé par
  le re-cours du juge — sur une branche `main` au même pin : **61/61**. La substance passait déjà au 1er run.
- **automaton, runner `bun` vs `npx tsx`** : `node --experimental-strip-types` ne résout pas les imports
  `…/src/index.js` → `.ts` ; bun exécute les mêmes 21 checks. Écart de runner uniquement.
- **cordis, build préalable requis** : le smoke exige les `lib/` construites. Enquête du juge : `yakumo esbuild`
  ne démarre pas sur un clone frais — il faut d'abord bootstraper `packages/core/lib` (`dumble` direct,
  EXIT 0), et le loader `tsx` résout `cordis` vers la source rc.12 (sans `Context.use`) : c'est **sans tsx**
  que yakumo passe après le bootstrap. Le build préalable est une étape d'environnement, pas une modification
  du fork (les `lib/` sont gitignorées) ; le 3/3 est confirmé.
- **infinity, 1er run du juge 12/13** : `smoke_gel_lineage_adapter_only` échoue sur mon clone superficiel
  (`--depth 1` : le gel `e1a3e4b` n'est pas ancêtre de HEAD dans un historique greffé). Après `fetch --unshallow`
  (gel ancêtre vérifié) : **13/13, EXIT 0**. Artefact de méthode, prouvé par le correctif.
- **pi extension, tsc à nu** : voir F8.

**H-M3 QUALIFIÉ ×4 (agent-zero, openmuse, OpenDots, OpenDuet) :** petits checks cités de leur pas, pas re-courus —
c'est la règle §D18 du plan, acceptée (R-J15). Les suites complètes des forks sont citées de leur pas, pas
re-courues (§D18) : cordis 9/9 ; automaton 1 646/0/1 (réserve js-tiktoken) ; pi 4 431/9 qualifiés ;
infinity 385/42 ROUGE QUALIFIÉ ; openrig test:repo 334 (333/0/1) ; prime-agent suite propre non re-courue (R-A2) ;
openbot bun 10 891/345/285 ROUGE QUALIFIÉ. 0 échec imputable à un adapter dans tous les cas.

---

## 4. Natif — suite, `/refine`, daemon, télémétrie (re-cours du juge @`95e95f9`)

`cargo test -p infinity-daemon` en clone frais @`95e95f9` : **EXIT 0, 105/105**
(lib 70 + agent_zero_proof 5 + bots_proof 7 + changeset_proof 8 + daemon_proof 4 + prime_agent_proof 6 +
pty_proof 1 + source_control_proof 4). `clippy --all-targets -- -D warnings` EXIT 0 ;
`cargo fmt --check` EXIT 0. Arbre natif **46 fichiers** dont 5 prime\* (re-compté) ;
src 26 fichiers / 9 203 lignes, tests 7 fichiers / 2 082 lignes (re-comptés).

**`/refine` — R-J10 LEVÉE, preuve par comportement, pas par bascule de constante.**
`bots.rs` lu : `refine_available()` (l. 342) planifie une vraie refinement via `plan_refinement`,
l'applique via `apply_refinement_plan` sur un `HarnessState` en mémoire, et ne retourne vrai que si
une édition est appliquée et l'état non vide — si le module `prime_agent_refine` était absent ou cassé,
le code ne compilerait pas ou la sonde échouerait. Le test `refine_is_available_after_pas6_merge`
(lib + preuve, 2 occurrences) re-prouve indépendamment le même round-trip (plan + apply + relecture
de l'entrée « pas8-proof »). Dans mon run 105/105 : `refine_is_available_after_pas6_merge ... ok` (×2),
`runtime_cycle_with_h1_over_a_real_gateway_stub ... ok`,
`daemon_opens_pty_session_and_executes_command_with_receipt ... ok`.
Le motif d'indisponibilité survit comme chaîne morte dans `refine_unavailable_reason()` (branche else,
jamais prise puisque `refine_available()` est vrai) — résidu documentaire, pas un défaut.

**Daemon unique — R-J8 LEVÉE, comptage live.** `fn main` unique (`main.rs`), un seul `[[bin]]`
(`riginfinity-daemon`). Daemon lancé depuis le binaire construit sur le SHA exact, compté live :
**1 processus `riginfinity-dae`, 0 `hc`**, log « infinity-daemon ready », arrêt propre après timeout.
`strace -f -e trace=connect` : **0 `connect()`**, 0 non-loopback. Socket `/tmp/herdr-core.sock` absent (= muet).
Observation reprise de l'exécutant (pas un écart) : aucun socket créé au démarrage — serveurs RAP paresseux.

---

## 5. H-P7-1-PIN 7/7 — re-prouvé par le juge à l'API (R-J2 levée)

Gitlinks V5 @`0b16b3a` vérifiés un par un (arbre API récursif) ; compares `pin...main` et `adapter...pin`
à l'API, un par un — chiffres **identiques** à l'exécutant :

| Module | Gitlink V5 @`0b16b3a` = pin | pin…`main` HEAD | adapter…pin | pin ≠ gel |
|---|---|---|---|---|
| cordis | `a40cc74` | ahead 2/0 | identical 0/0 | oui |
| automaton | `7cdaa00` | ahead 1/0 | identical 0/0 | oui |
| pi | `13be830` | ahead 1/0 | identical 0/0 | oui |
| infinity | `007409e` | ahead 1/0 | identical 0/0 | oui |
| openrig | `649376c` | ahead 1/0 | ahead 2/0 | oui |
| prime-agent | `3bac96a` | ahead 1/0 | identical 0/0 | oui |
| openbot | `6e62238` | identical 0/0 | ahead 1/0 | oui |

Le harnais du pas 8 contient le check (script `run_holdouts_f8_p8.py`, l. 41, 64) et l'a couru **avant** tout
retrait — le trou du pas 7 est fermé. La lettre C1 du jugement pas 7 (re-pin sur le `main` avec bind) ne
s'applique qu'aux pointeurs survivants ; pour les 6 retirés, le pin-adapter suffit et le retrait rend le
re-pin sans objet (plan §D7) — la substance (« le pin contient l'adaptation ») est prouvée ci-dessus pour les 7.

---

## 6. Décisions sur les questions centrales (Q2–Q8)

- **Q2 PARTIEL / QUALIFIÉ : acceptables avec réserves (R-J6, R-J7, R-J15).** H-P8-7/H-F8-2 PARTIEL :
  le mécanisme est livré et vérifié ; le cycle complet 5 étapes sur machine réelle reste dû (suivi S1) —
  c'est la position explicite du plan (§D9), pas une tolérance du juge. H-F8-3/H-F8-8 PARTIEL : ils ne sont
  PARTIEL que parce que la validation 13e est le présent jugement — ils deviennent effectifs par lui (+ C3).
  H-F8-9/H-P8-11 QUALIFIÉ : dépense non mesurable, patron p5 accepté à tous les pas.
- **Q3 Chaînes `Amdkn/openbot` dans `aspace_marketplace_engine.py` : légitimes.** Lues aux lignes 96 et 163 :
  ce sont des chaînes `open_source_engines=[...]` de deux offres du catalogue (`MPLACE-C1-FDE-SPRINT`,
  `MPLACE-C3-SOVEREIGN-COWORKER`) — elles nomment le fork, qui existe toujours sur GitHub, et un contexte
  de conteneur, pas le chemin du sous-module V5. Classement chaîne (§D14 c) confirmé. Aucune référence
  d'exécution ne survit : les coupes du §D14 sont vérifiées au diff (clone-forkables 3 entrées, matrice sync
  3 entrées, mutate-and-push-forks 3 branches — `py_compile` OK —, mount-fractal 1 chemin, README 1 phrase) ;
  survivants vérifiés : `MODULES-LOCK.json` (registre), `.pi` (imports npm, §3), workflows (aucun chemin
  de sous-module retiré), superviseur (fibre retirée, `py_compile`/parse OK).
- **Q4 Condition pi (§D5 / H-P8-pi) : le merge peut partir sans le vert de la Phase D.**
  Le design tranche (patron H-P3-7, accepté deux fois) ; le juge ne rouvre pas un arbitrage de design.
  Ce qui est conditionnel : la durabilité native de pi. Ce qui est inconditionnel et vérifié : retrait du
  pointeur, coupure des références, smoke 45/45 sans l'original, compilation de l'extension (tsc EXIT 0).
  Le reçu de suivi S2 reste dû quand la Phase D devient verte. **Réserve : la condition doit être nommée
  dans la fiche pi (C1, F10).**
- **Q5 R-J5 levée.** Manifeste mis à jour **dans** le pas 8 (§D11), pas par commit de suivi : pin, fichiers,
  suite, ports, `single_daemon` PROUVÉ, `prime_agent_non_merge` RÉSOLU — tous vérifiés au fichier (§2).
- **Q6 R-J10 levée.** Voir §4 — `/refine` prouvé par comportement.
- **Q7 Dérive 774 commits : consignée, jamais suivie (§D15).** Aucun re-gel, aucun fast-forward.
  Le triage 181 d'openbot reste valable (jugement pas 7 §5).
- **Q8 Aucune nouvelle adaptation, aucun secret lu, aucun re-gel.** Diff PR vérifié : 30 fichiers
  (896 insertions, 127 deletions) — retraits, re-pin, LICENSE, registre, manifeste, fiches, preuves.
  Aucun code adapter neuf, aucun dépôt dans RigInfinity au-delà du merge `9050a1f`.

---

## 7. Faits faux ou inexacts — nommés précisément (suite du jugement pas 7, F1–F6)

- **F7 — « PR — contenu (28 chemins) » du RAPPORT §8 est faux.** La PR compte **30 fichiers**
  (API : `changed_files: 30` ; `git diff --name-only 0b16b3a HEAD` = 30 ; 896 insertions, 127 deletions).
  Le rapport compte 3 ajoutés + 17 modifiés + 8 supprimés = 28 ; le réel est 3 + **19** + 8.
  Les deux oubliés de la liste « Modifiés » : **`.gitmodules`** et **`agent-zero-ADAPTATION.md`**
  (diffs vérifiés : `.gitmodules` −8 entrées ; agent-zero fiche : « Pin (bind) » → « Pin V5 » + ligne « Bind »).
  Le contenu de la PR est complet ; c'est l'inventaire du rapport qui est faux. Corrigé par C2(a).
- **F8 — Les logs tsc sont vides, pas des preuves.** `logs-adapter-openrig-tsc.log` : **0 octet** ;
  `logs-pi-ext-tsc.log` : **0 octet**. Le « tsc EXIT 0 » affirmé dans le rapport et dans RESULTS repose sur
  des fichiers vides ; de plus le harnais H-P8-5 ne vérifie que l'existence du log pi-ext et l'absence du mot
  « error » dans son contenu (`run_holdouts_f8_p8.py`, l. 143). **Substance confirmée par le juge :**
  openrig `tsc -p aspace-openrig-adapter/tsconfig.json --noEmit` (strict) **EXIT 0** (re-cours du juge) ;
  pi extension `tsc --noEmit --strict` **EXIT 0** sous la configuration du projet (target ES2024,
  `skipLibCheck: true`) ; 0 erreur dans `aspace-factory.ts` sur 3 runs — les 2 runs à nu échouent
  uniquement sur des `.d.ts` de dépendances (TS 7.0.2 : `path.PlatformPath` ; TS 5.9.3 sans tsconfig :
  cible ES5 par défaut). Les reçus de l'exécutant sont faibles ; les faits sont vrais. Pas de C distinct :
  le juge a produit les preuves ; le harnais des pas suivants doit exiger un log non vide.
- **F9 — H-P8-7 « cycle … prouvé en suite » est une sur-vente.** Le détail RESULTS affirme :
  « cycle Intake → Éveil → Rig → Résolution → Validation prouvé en suite
  (`runtime_cycle_with_h1_over_a_real_gateway_stub` vert, oui) ». Le test, **lu** par le juge
  (`prime_agent_proof.rs`, l. 230) : un cycle H1 — `run_cycle(spawn_request("scout"))` contre un stub
  gateway réel, puis `plan_refinement` + `apply_refinement_plan` + `turn_ended()` — **les cinq noms
  d'étapes n'y figurent pas**. Ce qui est prouvé : un cycle H1 + un round-trip de refinement.
  Le PARTIEL reste le statut correct (même famille que le constat Q4 du jugement pas 7 : « cycle complet =
  ce harnais » est circulaire comme preuve) ; c'est la formulation qui est fausse. Corrigé par C2(b).
- **F10 — H-M7-pi non conforme : la fiche pi ne consigne pas la condition.** `grep` dans
  `pi-ADAPTATION.md` (clone frais PR) : **0 occurrence** de « H-P8-pi », 0 de « condition », 0 de « état 3 ».
  Le plan §D18/H-M7 exige que la fiche consigne « la condition pi (§D5) le cas échéant ». La condition est
  consignée au registre (l. 90) et dans RESULTS (H-P8-10, H-M5-pi, COMPTEUR-F8), et la fiche documente le
  fond (Phase D : H-P2-3/6 PARTIEL, H-P2-11 NON VÉRIFIABLE, l. 409) — mais le libellé de la condition manque
  dans la fiche du module. Corrigé par **C1**.
- **F11 — Compteurs du registre (voir §1).** La ligne 90 déposée (« 11 en état 2, 0 en état 3 ») contredit
  la condition de succès du plan (« les 11 en état 3 », §5 et H-F8-8). Le plan se contredit lui-même
  (§D13/§5 vs §5/H-F8-8) ; l'exécution a suivi la lettre. Corrigé par **C3**.
- **Exactitudes confirmées (à porter au crédit de l'exécution) :** recomptage RESULTS 87/6/4/0 exact ;
  PR #43 (ouverte, non mergée, `mergeable: true`, `clean`, tête `c8ed937`, base `0b16b3a`, 1 parent) ;
  CI 8/8 `completed/success` (CodeQL, S1-RICK & Reviewer-Security, Cat 01, Cat 02, Deterministic Gate,
  Cat 04, Cat 03, Analyze — plus de Cat 04 bloquée, R-J9 levée) ; merge RigInfinity `95e95f9`
  (2 parents, 46 fichiers, 5 prime\*) ; `.gitmodules` 114 → 106, gitlinks 106 → 98 ;
  LICENSE 11 338 o, diff 1 ligne ; registre l. 89 corrigée, l. 148 D-N053 25 → 3 inchangé ;
  manifeste (pin, fichiers, lignes, ports, `single_daemon`, `prime_agent_non_merge`) exact au fichier ;
  MODULES-LOCK (5 gitlink null, pins conservés, RigInfinity pin = gitlink = `95e95f9`) ;
  `check-modules-lock.py` sur la tête PR : vérifications 1–4 VERTES, v5 12/12, v6 11/12 (trou pré-existant, R-J14) ;
  H-P7-1-PIN 7/7 chiffres identiques ; suites adapter 3/3, 21/21, 45/45, 13/13, 61/61, 18/18, 9/9 toutes
  reproduites ; incidents nommés par l'exécutant (openrig 60/61, automaton `bun`, cordis build préalable)
  tous confirmés et expliqués ; fiches C2 : 8 fiches corrigées dans la PR, 0 occurrence « Pin (bind) »
  (dont infinity, qui nommait le bind `be616bf` comme pin, et openrig `adafb0d` — corrigés) ;
  agent-zero « Pin V5 : `176d23f` » vérifié comme le vrai gitlink pré-retrait (historique V5, commit `1cf831a`).

---

## 8. Rejeu indépendant du harnais — résultats

Clones frais `~/juge-p8/` (V5 PR `c8ed937`, RigInfinity `95e95f9`, 7 forks aux pins, extension pi),
logs `juge-*` :
**cargo 105/105, clippy 0, fmt 0, daemon live 1/0, strace 0 `connect()`, 7 suites adapter vertes
(3/3, 21/21, 45/45, 13/13, 61/61, 18/18, 9/9), tsc openrig EXIT 0, tsc extension pi EXIT 0.**
Recomptage RESULTS-F8-P8.json : **87 PASS, 6 QUALIFIÉ, 4 PARTIEL, 0 FAIL — exact.**
Le harnais d'origine (`run_holdouts_f8_p8.py`) a été lu : il vérifie le pin (H-P7-1-PIN), les retraits,
le superviseur, le registre et le manifeste au fichier — et ses deux faiblesses sont nommées en F8
(logs tsc vides acceptés) et F9 (wording du cycle non vérifié contre le test lu).

---

## 9. Réserves numérotées

**Levées au pas 8 :** R-J1 (pin openbot — gitlink `6e62238` vérifié avant retrait, pointeur retiré au pas 8) ;
R-J2 (harnais aveugle au pin — H-P7-1-PIN dans le harnais, 7/7 re-prouvé) ; R-J3 (étiquette « Pin (bind) » —
0 occurrence, 8 fiches corrigées + 3 bots) ; R-J5 (manifeste en retard — à jour dans le pas) ;
R-J8 (1 daemon par construction — comptage live 1/0) ; R-J9 (Cat 04 bloquée — CI 8/8 `completed/success`) ;
R-J10 (`/refine` conditionnel — prouvé par comportement, §4).

- **R-J4 (reportée du pas 7) — États déclarés avant jugement.** Les 11 manifestes portent déjà
  `levels.current = 2` (pi = 1) alors que l'état 2 exige la validation 13e — et l'état 3, le présent
  jugement + le merge. Patron pré-existant, accepté ; l'état 3 devient effectif au présent jugement + merge (C3).
- **R-J6 (reportée du pas 7) — H-P8-7 / H-F8-2 PARTIEL : pas de cycle Runtime complet exécuté.**
  Accepté (non exécutable sur cette VM) ; le cycle complet sur machine réelle reste dû (suivi S1, §D9–D10).
- **R-J7 (reportée du pas 7) — H-F8-9 QUALIFIÉ : plafonds non mesurés.** 1 %/5 %/20 % affirmés non
  mesurables depuis la factory (patron p5). Accepté ; la mesure à la comptabilité fournisseur (D12) reste
  due en principe (suivi S3).
- **R-J11 (bloquante, levée par C1) — Fiche pi sans la ligne H-P8-pi (F10).** Voir §7.
- **R-J12 (bloquante, levée par C2a) — Comptage §8 faux : 28 au lieu de 30 (F7).** Voir §7.
- **R-J13 (bloquante, levée par C2b) — Wording H-P8-7 sur-vendu (F9).** Voir §7.
- **R-J14 — MODULES-LOCK : `v5_head` périmé (`7fe71a3`) + trou `riginfinity-ADAPTATION.md` (pré-existants).**
  Vérifiés au fichier et par `check-modules-lock.py` (v6 : 11/12). `v5_head` ne peut être la tête de PR
  qu'après la création du commit de merge — suivi post-merge S4 : le mettre à jour sur le SHA du merge ;
  trancher la fiche du natif (la créer, ou consigner dans le script que le natif n'a pas de fiche).
  Ni l'un ni l'autre ne bloque le merge : le lock est aligné sur le fond (5 gitlink null, RigInfinity `95e95f9`).
- **R-J15 — H-M3 QUALIFIÉ ×4 (agent-zero, openmuse, OpenDots, OpenDuet).** Petits checks cités de leur pas,
  pas re-courus — règle §D18 du plan, acceptée. Leurs suites complètes restent citées, pas re-courues.

## 10. Arbitrages vision — non tranchés (remontent via Rick → A0)

Comme l'exigent le plan et la mission, le juge ne tranche pas : (a) le titulaire de la LICENSE — A'Space
ou l'entité juridique (§D2) ; (b) l'inlining de l'arbre natif dans V5, amendement du design maître (§D1) ;
(c) pi en gate dur sur la Phase D plutôt que conditionnel (§D5) ; (d) le cycle complet sur Alpha/PC comme
gate de merge plutôt que suivi (§D9) ; (e) la mesure du pool à la comptabilité fournisseur avant de clore
F8 (§D12). Le design tranche ; les faits vérifiés ici sont ceux sur lesquels ces arbitrages s'appuieront.

## 11. Suivis dus après le merge

- **S1 (Ryan)** : cycle complet Intake → Éveil → Rig → Résolution → Validation + comptage live du daemon
  unique sur machine réelle (Alpha / PC). Un seul reçu couvre cycle + comptage (§D9–D10, R-J6).
- **S2 (pi, H-P8-pi)** : quand la Phase D du pas 2 devient verte, re-preuve de la durabilité native de pi
  et levée de la condition sur son état 3 (§D5, R-J11).
- **S3 (D12)** : mesure du pool à la comptabilité fournisseur — due en principe, jamais mesurée (R-J7).
- **S4 (coordinateur)** : `MODULES-LOCK.json` `v5_head` = SHA du merge ; fiche `riginfinity-ADAPTATION.md`
  à trancher (R-J14).
- **Registre Nardole** : non touché par le juge (append-only, coordinateur seul).

## 12. Conclusion

**VALIDÉE AVEC RÉSERVES — merge OUI après amendements (C1–C4), INTERDIT sur `c8ed937`.**
Le travail est réel et vérifié indépendamment : vrai merge `9050a1f`, `/refine` prouvé par comportement,
7 pointeurs + 1 gitlink daemon retirés de l'arbre, daemon unique compté live, LICENSE déposée, manifeste
à jour (R-J5 levée), pin prouvé 7/7, 7 suites adapter vertes en re-cours, CI 8/8 verte. Les réserves
bloquantes sont trois lignes de documents (fiche pi, inventaire du rapport, compteurs du registre) —
pas un travail à refaire. Le coordinateur vérifie les amendements à l'API (fiche pi : 1 occurrence « H-P8-pi » ;
rapport : « 30 chemins » + 2 fichiers ; registre l. 90 : « 11 en état 3 » ; CI 8/8 sur la tête amendée)
et merge ensuite en true merge (2 parents, DVG-01), puis reçu R10. **F8 est CLOSE à ce merge.**

*Juge 13e — jugement rendu sur preuves re-courues, 2026-11-12. Fichiers de travail :
`~/juge-p8/` (clones frais, logs `juge-*` : cargo, clippy, fmt, daemon, strace, 7 suites adapter, 2 tsc).*
