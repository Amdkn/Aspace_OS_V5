# Jugement 13e — D-N053 pas F2 : orca, état 0 → 1 (dernier module état 0 du Runtime)

**Juge :** 13e Doctor (fonction de jugement, indépendante — ni l'exécutant Ryan, ni le coordinateur).
**Date :** 2026-11-12 ~21:00 EST (2026-11-13T02:00Z).
**Objet :** PR #46 du repo `Amdkn/Aspace_OS_V5`.

## Verdict

**VALIDÉE AVEC RÉSERVES — merge OUI.**

- **Tête autorisée :** `e2d9ecb` (`e2d9ecb4e5747ca222bae4190b9da1f79f167c94`), seule tête sur laquelle le merge est autorisé.
- **Merge :** true merge (2 parents, DVG-01), jamais par le runner, jamais par le juge.
- **Amendements :** aucun (C1… : néant). Les réserves ci-dessous sont des suivis hors PR, pas des conditions de merge.
- **Décision du coordinateur sur H-F2-3 : ACCEPTÉE** (voir §5).

## 1. PR #46 re-vérifiée à l'API (2026-11-12 ~21:00 EST)

| Fait | Vérifié |
|---|---|
| État | OUVERTE |
| Tête | `e2d9ecb` = `e2d9ecb4e5747ca222bae4190b9da1f79f167c94` |
| Base | `master` ; parent unique du commit = `5629dac` = master actuel (vérifié à l'API ce tour) |
| Titre | « D-N053 pas F2 : orca adapté en Fibre Cordis (8L) — état 0 → 1 » |
| Commits | 1 ; message `feat(d-n053-f2): adapt orca as Cordis Fiber (8L) — state 0 to 1` |
| Mergeable | `true`, `mergeable_state: clean` |
| Fichiers | 5 (+312 / −4) : fiche + audit + manifeste ajoutés, gitlink `orca` modifié, `FUSIONS-REGISTRY.md` modifié |
| Autres PR ouvertes V5 | **0** — seule la #46 est ouverte |

## 2. CI re-vérifiée à l'API sur la tête `e2d9ecb`

**8/8 check-runs `completed` / `success`** : CodeQL ; Verify Category 01_Kernel_Gates ; Verify Category 02_Holons_578_QualityControl ; Verify Category 03_Submodules_EGM_Harvester ; Verify Category 04_Security_OWASP_RigInfinity ; S1-RICK & Reviewer-Security · OWASP Top 10 & Worktree Patch ; Deterministic Gate (5D Semantic AST + CAS Holons + 7R + OKF) ; Analyze (actions).

## 3. Pins, binds et forks re-vérifiés à l'API

| Fait | Vérifié |
|---|---|
| orca adapter `5d15464` (`5d154641332ae595a65b57ba5b7210b8056c5e2e`) | parent = gel `708aca6a46a09c3ad3503bd3abe0ae94b502e9a7` ✓ ; diff gel→adapter = **1 commit, 6 fichiers adapter seuls** (`aspace-orca-adapter/`, tous `added`, 0 suppression, aucun fichier amont touché) : README.md, config.json, contract.json, launch-orca-ide.sh, protocol-proof/proof.mjs, smoke_test.sh |
| orca bind `8beacf3` (`8beacf3169ea035394402e6434add900474b6cd7`) | parent = adapter `5d15464` ✓ ; 1 fichier (`aspace-plugin.json`, 24 lignes) ; blob `736c2e1b4ac786ea848abf6379adc936518755bc` **byte-identique** au bind `b659760` sur `aspace-v5-native` (même SHA, même taille 874 o) |
| orca fork `main` | = `8beacf3` ✓ ; fork non archivé, branche défaut `main` |
| Gel `708aca6` | commit amont `stablyai/orca`, 2026-11-08T01:59:32Z, v1.4.214 ✓ ; bind d'origine `b659760` parent = gel ✓ ; `aspace-v5-native` toujours à `b659760` (inchangée) |
| Pin = commit adapter | conforme au patron tranché journal 587 (§0 du design) |

## 4. Harnais rejoué indépendamment

Rejeu de `harness-pas-f2.py` par le juge sur une copie de l'évidence (`~/workspace/.scratch-f2-juge/evidence-f2-copy`, pour ne pas écraser `RESULTS-D-N053-F2.json`) contre le clone de la tête PR (`~/workspace/.scratch-f2-juge/v5-pr46`, HEAD `e2d9ecb` vérifié) : **25/27 PASS — les mêmes 2 FAIL que le rapport de l'exécutant** (`H-F2-3/baseline-verte`, `H-F2-3/adapte-verte`), aucune divergence de chiffres. L'évidence d'origine est intacte (md5 de `RESULTS-D-N053-F2.json` inchangé : `a103c2b918692ccf7bca374e30422e3b`, vérifié avant et après le rejeu).

Vérifications du harnais rejouées une à une (détail au §6) : H-F2-1 (gitlink orca = `5d15464` ; `.gitmodules` pointe toujours `Amdkn/orca` ; manifeste : adapter `5d15464`, gel `708aca6` ; bind `8beacf3` + blob `736c2e1` dans la fiche) ; H-F2-2 (fiche : amont byte-identique, adapter seul code A'Space) ; H-F2-3 (chiffres ci-dessous) ; H-F2-4 (audit 6 621 o, « 0 appel sortant par défaut » ; interrupteurs forcés ; strace 0 `AF_INET` hors loopback) ; H-F2-5 (`fiber:a0:orca`, `levels.current = 0`, unique parmi 41 manifestes) ; H-F2-6 (daemon exclu, couture actée absente, divergence + cœur Buzz) ; H-F2-7 (fiche complète : gel, MIT, audit, divergence, `orca-ide`, 31415, triage 142 ; liste jointe 145 lignes) ; H-F2-8 (compteur 25 → 0, paragraphe Pas F2, pin au registre, « 0 reste en état 0 »).

**Chiffres re-comptés par le juge aux logs** : baseline **2 094 passés / 1 échec / 29 ignorés ; 2 fichiers en échec / 263** ; adapté **2 094 / 1 / 29 ; 2 / 263 — chiffres identiques, test pour test**. Le test en échec diffère (baseline : `plugin-release-entry` ; adapté : `runtime-listener-probe`) ; le fichier en échec commun est `index-omitted-host-scope-selectors` (beforeAll timeout, 0 test en échec). **0 régression nette.**

## 5. Décision du coordinateur sur les 3 rouges — ACCEPTÉE

Le design (§4, H-F2-3) dispose : « Un test rouge bloque la montée d'état (sauf exclusion décidée par le coordinateur, liste exacte consignée, confirmée par le juge — le juge re-vérifie indépendamment chaque rouge exclu). » La décision du coordinateur (`DECISION-COORDINATEUR-H-F2-3.md`, 2026-11-12 ~20:45 EST) exclut exactement les 3 rouges du harnais. Le juge les a re-vérifiés indépendamment, à la source et aux logs, et **confirme l'exclusion des 3** :

### Rouge 1 — `src/cli/index-omitted-host-scope-selectors.test.ts` — hook `beforeAll` timeout 60 s

- **Identique baseline vs adapté** : les deux logs portent la même ligne — `Error: Hook timed out in 60000ms.` au `beforeAll` (l.66) — fichier en échec, 0 test en échec, 7 tests skipped des deux côtés.
- **Passe seul** : re-run des 3 fichiers (adapté) : 7/7 en 28,8 s (`logs-suite-adapte-rerun-3files.log`, vérifié au fichier). Le rapport et la décision disent « 41 s » — la durée citée ne correspond pas au log conservé (28,8 s) ; l'issue est identique (7/7), écart de chiffre sans conséquence, noté au §7.
- **Cause : charge parallèle** (263 fichiers, 1,5 CPU) — le hook dépasse 60 s quand la machine est saturée. Pré-existant au gel, 0 imputable à l'adapter. Exclusion acceptée.

### Rouge 2 — `src/cli/plugin-authoring/plugin-release-entry.test.ts` — « explains why there is no entry outside Git or before the first commit »

- **Échec baseline seulement** : baseline 1 échec (ce test) ; adapté 4/4 en full run ET 4/4 au re-run des 3 fichiers. L'adapté est vert sur ce test — 0 régression, l'adapté est meilleur.
- **Cause prouvée à la source** : le test construit son dossier « hors Git » sous `os.tmpdir()` (`tempRoot()`, `plugin-release-entry.test.ts` l.14–18, lu au gel). Le runner du full run pose `TMPDIR` dans le repo : `createRunTempDirectory()` (`config/scripts/test-runtime/execution-policy/vitest-run-temp-directory.mjs`, lu au gel) fixe `TMPDIR` au répertoire de run, lui-même créé sous le `tmpdir()` hérité — l'exécutant lançait avec `TMPDIR=<repo>/.tmp-test` (contournement du tmpfs `/tmp` 512 Mo, `.tmp-test` présent dans le clone). Le message d'échec le prouve : `git ls-tree failed: fatal: Not a valid object name 708aca6a46a09c3ad3503bd3abe0ae94b502e9a7:.tmp-test/ovbd1/orca-plugin-release-entry-yFD2Oi/loose` — le dossier « hors Git » est en fait DANS le clone orca, donc `releaseFor` trouve un repo Git (HEAD `708aca6`) et `git ls-tree` échoue autrement. Flake d'ordre/environnement, pré-existant au gel, 0 imputable à l'adapter. Exclusion acceptée.

### Rouge 3 — `src/cli/runtime/runtime-listener-probe.test.ts` — « refuses to call a profile free when the endpoint could not be reached at all »

- **Échec adapté seulement en full run** (passe en baseline full run 9/9) — et échoue aussi seul sur l'adapté (re-run des 3 fichiers : 8/9, même test, même assertion `expected 'not-listening' to be 'unproven'`).
- **Reproduit AU GEL par le juge, indépendamment** : worktree au gel `708aca6` (`~/workspace/.scratch-f2-juge/orca-gel-worktree`, `node_modules` lié depuis le clone de l'exécutant), un seul fichier, même runner : **1 échec / 8 passés, même test, même assertion** (log du juge : `~/workspace/.scratch-f2-juge/logs-rerun-gel-probe-juge.log`). Les fichiers test + probe sont byte-identiques gel vs adapté (vérifié par `diff` — le diff gel→adapter ne touche que `aspace-orca-adapter/`).
- **Cause prouvée à la source** : le test `chmod 0o000` un dossier et attend une erreur de permission → `unproven` (`runtime-listener-probe.test.ts`, l.85–96, lu au gel ; commentaire : « Permission errors cannot prove the profile is free »). La sonde (`runtime-listener-probe.ts`, l.10 et l.40, lue au gel) ne mappe que `ENOENT` et `ECONNREFUSED` vers `not-listening` ; toute autre erreur → `unproven`. **La VM tourne en root (uid 0, vérifié ce tour : `id -u` = 0)** : le noyau ignore le bit 0o000, la connexion atteint le chemin et répond `ECONNREFUSED` → `not-listening`. Artefact root, même classe que le `writable_directory` de F1 (R1 du jugement F1). Pré-existant au gel, 0 imputable à l'adapter. Exclusion acceptée.

**Ce qui n'est pas exclu** (vert des deux côtés, vérifié) : typecheck `tc:cli` + `tc:node` (`TC_CLI_EXIT:0`, `TC_NODE_EXIT:0`) ; `oxlint` borné 0 warning / 0 erreur (790 fichiers) ; smoke vert (`SMOKE_EXIT:0`) ; preuve client 4/4 (`PROOF_EXIT:0`).

## 6. Vérifications sensibles rejouées par le juge

**(a) Les 3 rouges, identité baseline vs adapté** — établi au §5 (mêmes chiffres 2 094/1/29 des deux côtés ; rouge 1 identique ; rouge 2 baseline seulement ; rouge 3 reproduit au gel par le juge). ✓

**(b) Preuve client H-F2-3 réelle** — lue au code source du fork (adapter `5d15464`) : `aspace-orca-adapter/protocol-proof/proof.mjs` (224 lignes, stdlib Node seule) — stub local `ServeReadiness` (`runtimeId`, `boundEndpoint`, `advertisedEndpoint`, `pairing`, `health`), serveur HTTP `/ready` + WS minimal RFC 6455 sur `127.0.0.1` port éphémère ; le client fait : readiness HTTP 200 + champs, connexion WS sur `boundEndpoint` loopback, round-trip JSON-RPC `server.status`, ping/pong. Log d'exécution vérifié : `logs-protocol-proof-adapte.log` — 4/4 (`PASS readiness HTTP 200 + champs ServeReadiness`, `PASS WS connect sur boundEndpoint loopback`, `PASS round-trip server.status`, `PASS ping/pong texte`, `PROOF: 4/4 checks — stub orcad local 127.0.0.1:36837`, `PROOF_EXIT:0`). Contre stub local, jamais contre un `orcad` V5 ni `onorca.dev`. Preuve réelle, pas déclarative. ✓

**(c) Télémétrie zéro** — interrupteurs vérifiés **au fichier source du fork**, pas seulement à la fiche : `aspace-orca-adapter/config.json` (lu à l'API au commit adapter `5d15464`) porte `telemetry: { ORCA_TELEMETRY_DISABLED: "1", DO_NOT_TRACK: "1" }`, `env_forced_by_launcher: ["ORCA_TELEMETRY_DISABLED=1", "DO_NOT_TRACK=1"]`, `auto_update: { autoDownload: false, autoInstallOnAppQuit: false }` avec le commentaire « n'appelle jamais scheduleAutomaticUpdateCheck », `orcad.bind: 127.0.0.1`, `command_linux: orca-ide`. `contract.json` (lu au même commit) : `form: [cli-contract, orcad-client]`, `excluded` complet (`orchestration task-create/dispatch/check`, toute commande de mise à jour, `orca serve` comme service V5, `orca open`, `--bind 0.0.0.0`, `allowPublic`, pairing mobile), `skills_reference` : les 11 skills du gel nommées + mécanisme version-matched. Audit lu en entier (6 621 o, T1–T8 tous tranchés ; T1 PostHog fail-closed + coupé, T2 auto-update coupée par le chemin de lancement, T3–T7 hors contrat, T8 capture). Capture strace **re-comptée par le juge** : 12 lignes `AF_INET`, **0 hors `127.0.0.1`** (9 `sin_addr 127.0.0.1`, 3 `socket()` sans adresse). ✓

**(d) Gitlink + `.gitmodules`** — vérifié au clone de la tête PR : `git ls-files -s` → `160000 5d154641332ae595a65b57ba5b7210b8056c5e2e 0 01_Forkable/FKB00_Runtime/04_ADE_OpenRig/orca` ; `.gitmodules` l.225–227 pointe toujours `https://github.com/Amdkn/orca.git` (inchangé). ✓

**(e) Compteur registre 1 → 0** — vérifié au clone de la tête : ligne 148 (compteur global **25 → 0**, « 0 reste en état 0 »), ligne 173 (table : orca état **1**, pin `5d15464`, `fiber:a0:orca`, MIT), ligne 188 (paragraphe « Pas F2 », adapter `5d15464`, bind `8beacf3`, blob `736c2e1b`, compteur 1 → 0), F9 Mesures (l.96) : « 3 modules ADE en état 1 (pas F1 + F2) ; orca en état 1 (pas F2) — compteur 0 ». Le diff PR #46 du registre (+5/−3) porte exactement : F9, compteur, table, paragraphe Pas F2. ✓

**(f) Dérive 1 178 / 1 205 re-mesurée indépendamment** — compare API gel → amont : `708aca6...91b3f12` → `ahead_by: 1178, behind_by: 0` ; `708aca6...41666c7` → `ahead_by: 1205, behind_by: 0` (commit `41666c7` daté 2026-11-13T01:17:39Z, conforme au rapport). Triage joint vérifié : `drift-perimeter-list.txt` 145 lignes (3 en-tête + 142 commits), `drift-perimeter-final.json` (`gel 708aca6`, `upstream_head_measured 91b3f12`, `drift_ahead_by 1178`, `measured_at 2026-11-12T23:15-05:00`, comptes `src/cli` 115 / `src/main/orcad` 39 / `src/main/telemetry` 10 / `src/shared` filtré 7 / distincts 142). ✓

**(g) Fiche complète, lue en entier** (225 lignes, au clone de la tête) : gel `708aca6` v1.4.214 2026-11-08T01:59:32Z ; licence MIT ; référence de l'audit ; tailles (arbre ~286 Mo / dépôt 2 233 158 Ko / amont 2 752 428 Ko) ; répertoires non-code exclus nommés ; formes A + B + C en référence ; serveur `orcad` opérateur-externe, jamais de service V5 ; collision Linux `orca` = lecteur d'écran GNOME, `orca-ide` ; interrupteurs + coupure auto-update ; couture orca ↔ herdr actée absente ; revendication 31415 qualifiée côté A'Space ; agents pilotés hors coupure (T4) ; `--version` amont documenté ; tests baseline/adapté 2 094/1/29 ; typecheck + lint ; smoke + preuve client ; strace ; les 3 rouges, liste exacte ; télémétrie zéro ; section Divergence (skills V5 vs gel, dette 1 178/1 205, revisite quotidienne, ré-audit à chaque transition) ; suivis S-F2-1..S-F2-6. ✓

**(h) Manifeste** — lu au clone de la tête : `id: fiber:a0:orca`, `adapter.commit: 5d15464`, `upstream.frozen_commit: 708aca6`, `levels.current: 0`, `telemetry_audit` référencé, surface listée (`orca-ide --help/--version/worktree list --json`, `orcad client: readiness + WS loopback + stop + idle-exit`). ✓

**(i) Bornes de suites respectées** — `test-perimeter-f2.txt` : 263 lignes, toutes dans le périmètre (`src/cli`, `src/main/orcad`, `src/main/telemetry`, `src/shared/*`) ; exclusions du design nommées dans la fiche (e2e Playwright/Electron, `mobile/`, Windows/macOS, `performance-contracts`, `preflight-*`, `release-*`) ; `tc:web` exclu, `tc:node` inclus. ✓

## 7. Réserves (suivis hors PR, non bloquantes)

- **R1 — Diagnostic SIGPIPE incomplet (F1, porté).** R1 du jugement F1 reste dû (S-F2-2) : re-courir main.rs herdr en utilisateur non-root et identifier le test fautif, au pas F2 ou sur une machine adéquate. Le pas F2 ne porte pas cette dette en silence : elle est consignée dans la fiche et ici.
- **R2 — Phrase du registre à compléter au reçu.** La ligne 188 du registre dit encore « décision attendue du coordinateur » pour H-F2-3 : la décision existe désormais (`DECISION-COORDINATEUR-H-F2-3.md`) et est confirmée par le présent jugement. Le coordinateur la consignera dans le reçu R10 du pas (références décision + jugement), sans rouvrir la PR — aucune modification de la tête `e2d9ecb` n'est exigée pour ce point. (Même réserve que R2 du jugement F1 pour la ligne 186, toujours en l'état au moment de ce jugement.)
- **R3 — Suivis hors F2 nommés au design (S-F2-1, S-F2-3, S-F2-5, S-F2-6) :** requalification H-P8-4 (pas 8) ; suivis pas 8 F8 ; alignement des skills orca V5 sur le gel (D-F2-7) ; revisite orca quotidienne tant que la dérive dépasse 20 (D-F2-4) — à dispatcher, non bloquants.
- **Note — durée du solo `index-omitted` :** le rapport et la décision disent « 7/7 en 41 s » ; le log conservé (`logs-suite-adapte-rerun-3files.log`) montre 7/7 en 28,8 s. L'issue est identique, le chiffre cité ne correspond pas au log conservé. Écart sans conséquence sur le verdict, consigné ici pour le registre.

## 8. Conformité au design signé Clara

- D-F2-1 (formes A + B, C en référence versionnée) ✓ ; D-F2-2 (client `orcad` seul, jamais de serveur V5, couture actée absente) ✓ ; D-F2-3 (CLI d'abord, `orcad` ensuite — ordre documentaire respecté : contrat CLI en tête de `contract.json`) ✓ ; D-F2-4 (gel tenu `708aca6`, triage des 1 161 → 1 178/1 205 versé en fiche et joint, revisite quotidienne) ✓ ; D-F2-5 (interrupteurs forcés, vérifiés au fichier source ; auto-update coupée par le chemin de lancement) ✓ ; D-F2-6 (31415 qualifiée côté A'Space dans la fiche, bind inchangé) ✓ ; D-F2-7 (stub du gel fait foi, divergence V5 consignée, non alignée) ✓ ; D-F2-8 (bornes §4 respectées : vitest borné 263 fichiers, `tc:cli` + `tc:node`, `oxlint` borné 790 fichiers, exclusions nommées) ✓ ; D-F2-9 (plafonds D12 — mesure au reçu du pas, hors périmètre du jugement, même posture que F1).
- Suivis hors F2 nommés au design (S-F2-1..S-F2-6) : non exécutés ici, à dispatcher — rappelés au §7, non bloquants.
- H-F2-3 : non vert strict, **vert sous l'exclusion décidée par le coordinateur et confirmée par le juge** (§5). Tous les autres hold-outs H-F2-1..H-F2-8 sont verts.

## 9. Ce que le juge n'a pas fait

Ni merge, ni modification de la PR, ni écriture sur les forks. Le harnais a été rejoué sur des copies (`~/workspace/.scratch-f2-juge/`, clone V5 `e2d9ecb` + copie d'évidence) ; l'évidence d'origine est intacte. La reproduction du rouge 3 au gel a été faite dans un worktree du clone de l'exécutant (`~/workspace/orca-f2`, HEAD `708aca6`, log du juge `~/workspace/.scratch-f2-juge/logs-rerun-gel-probe-juge.log`) — le worktree a été retiré après la preuve ; le clone de l'exécutant est inchangé (HEAD `8beacf3`).

---
*Jugement 13e — D-N053 pas F2 — 2026-11-12 ~21:00 EST. Verdict : VALIDÉE AVEC RÉSERVES, merge OUI, tête autorisée `e2d9ecb`, décision coordinateur H-F2-3 ACCEPTÉE.*
