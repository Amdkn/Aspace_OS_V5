# Jugement F1-10 — PR #53 (Rollback)

**Fonction :** le 1 — fonction Juger, pas une session
**Date :** 2026-11-13 ~05:38 EST
**PR jugée :** PR #53 « D-N055 F1-10 : Rollback (le 1 revient à la chaîne 13 si un hold-out échoue — un rollback prouvé) », tête 85301c3e9177fa9e290b86ace6482955a33e191c
**Design jugé contre :** `~/workspace/v4-factory/plans/DESIGN-FONDATION-13-1-F1-10-PROJET.md` (70 499 o, 218 lignes, sha256 `75c7703ab20b4ed471e5d98116ffb86d0c9ab0e21da257cd23adaf5444ae970e`, signé 2026-11-13T05:12:00-05:00, journal 943, reçu G-20261112-042)
**Méthode :** rejeu indépendant — PR vérifiée à l'API avant bascule, diff lu en entier, suite re-courue en clone frais, CLI re-courue sur des copies, routeur vérifié au fichier ; rien pris sur parole
**Verdict :** VALIDÉE AVEC RÉSERVES — merge OUI tel quel, 0 amendement
**Tête autorisée :** 85301c3e9177fa9e290b86ace6482955a33e191c

## Verdict

VALIDÉE AVEC RÉSERVES. La fonction Rollback est la preuve demandée : le 1 revient à la chaîne 13 si un hold-out échoue, et il le prouve par la fonction, pas par un récit. La tête vérifiée à l'API est la tête autorisée. Le merge est OUI tel quel, 0 amendement. Les réserves (R1–R4) sont des suivis hors PR, pas des conditions du merge.

## Lecture

- **Design lu en entier** (70 499 o, 218 lignes) : D-F1-10-1..12 ADOPTÉES, A-F1-10-1..7, P-F1-10-1..5, exécution autorisée. Checkpoint = dernier événement *avec preuve* du dispatch (seq + `event_id` + `at` + preuve) ; « sans perte » = histoire vérifiable, 3 cas à 0. F1-1 → Rick, F1-2 → Graham, F1-3 → Nardole (typage à la main), F1-4 → Bill avec décideur coordinateur (D-F1-10-3). Réveil = ré-instanciation par sous-agent borné étiqueté, désarchivage littéral EXCLU, arbitrage vision §8a (D-F1-10-5). 13e décideur de secours (D-F1-10-4). Re-preuve dans le même pas, R7 (D-F1-10-6). Deux nouveaux types `rollback_decided` / `rollback_executed`, 14 types (A-F1-10-3). Un seul réveil par session et par pas, T3 avant T8 (D-F1-10-8). Revert documenté exigé pour T2, sur base jetable, jamais master (D-F1-10-9). F-A3 NON utilisé comme échec simulé, T5 garde F-A1 accepté (D-F1-10-10). O3 conservée pendant la reprise (D-F1-10-11, A-F1-10-4). Module `rollback` + CLI `prove-rollback` codés (D-F1-10-12, A-F1-10-5).
- **Discover lu** (`DISCOVER-F1-10.md`, 88 065 o, 329 lignes, sha256 `0b91c80eb70c39a82a9c4ebd8a295ed484ccd6d846b0f8087b5eeeac92677ce9`) : mesure zéro §0, cas d'essai §5.2, faits §5.3, cas limites §5.4 (a)–(i), hold-outs §6, règles R1–R8 §6.
- **PR vérifiée à l'API avant bascule** (05:34 EST, re-vérifiée 05:37 EST) : ouverte, non mergée, tête = `85301c3e9177fa9e290b86ace6482955a33e191c`, base `c0b6dce16be922a6e0a0c7b084a605e2105702e2`, mergeable true, mergeable_state clean, 1 commit (1 parent `c0b6dce`), 21 fichiers +2772/−21. Message du commit : fonction Rollback — retour au checkpoint R1–R8 (prove-rollback, 14 types).
- **Diff complet lu** en clone frais `~/workspace/v5-f1-10-juge` (HEAD = tête vérifiée) : `src/rollback.rs` (842 lignes, 33 906 o — règles R1–R8, ordre R1→R4→R3→R2→R5→R6→R7→R8 ; structures Checkpoint, Decision, Loss, Revocation, RollbackCase ; parseur de dossier ; T0 rendu `NotApplicable`, pas un rejet) ; `src/bin/prove-rollback.rs` (561 lignes — lectures : dossier, journal réel, journal-scénario, design SIGNÉ, dossier du fait quand il est donné ; surcharges : le journal réel fait foi pour les checkpoints, le scénario pour les décisions simulées ; consigne commande exacte + sortie dans le dossier, section `## Rendus CLI`) ; `tests/rollback.rs` (617 lignes, 43 tests : 10 cas passants T0–T9, 5 faits F-R1..F-R5, 10 cas limites §5.4 (a)–(i), 11 règles une à une, 6 parseurs de fixtures) ; fixtures `rollback-fautif-1.md` à `rollback-fautif-5.md` relues au fichier (chacune UNE SEULE différence par rapport à un dossier valide) ; `rollback-valide-t1.md` relu ; `journal-f1-10-scenario.jsonl` (87 lignes : les 57 lignes du journal réel, byte-identiques au fichier, + 26 événements simulés seq 58–83 + 4 décisions simulées de faits seq 84–87) ; `revert-t2-temoin.txt` relu (base `9622c50`, merge simulé `5e73cc3`, revert `d02039f`, branche jetable locale jamais poussée, jamais master).
- **Fichiers de support vérifiés** : manifeste (Rollback ajoutée à la surface + `validate_rollback` / CLI `prove-rollback` ; `issued_by` + F1-10 journal 943 ; `validated_by` corrigé : F1-9 VALIDÉE AVEC RÉSERVES, PR #52 mergée `691b0a0`, jugement journal 942 — H-M5 fait à l'atterrissage ; `note_code` + § F1-10 O3 conservée, phrase F1-6 inchangée — R3) ; `Cargo.toml` (description + `[[bin]] prove-rollback`, 0 dépendance) ; `lib.rs` (`pub mod rollback`) ; `router.rs` (`EVENT_TYPES` 12→14, transitions R8 : l'exécution suit la décision, une seule décision par retour) ; `memory.rs` (`JOURNAL_EVENT_TYPES` 12→14, même ordre, mêmes contenus) ; audit télémétrie (§ Rollback : 0 appel sortant, CLI lectrice, 0 appel en écriture d'état, journal-scénario nommé fixture de test) ; `log.md` (+1 ligne append-only) ; fiche §14 F1-10 (suite 213/213, « Les 170 tests F1-2..F1-9 restent verts » = 213 − 43, exact) + §13 F1-9 corrigé CLOSE (PR #52 mergée `691b0a0`, journal 942, reçus 040/041) + Divergence (+4 entrées F1-10).
- **Dossier de rollback lu** (`ROLLBACK-F1-10.md`, 33 398 o, 504 lignes) : mesure zéro re-mesurée à l'exécution ~05:25 (registre 943, routeur 57 lignes, master `c0b6dce`, 0 PR, dernier EVT-20261113-032 seq 57) ; règle d'honnêteté SIMULÉ (aucun hold-out F1-1..F1-9 n'a jamais échoué, aucune fonction n'a jamais été reprise) ; rendus CLI consignés (T0 NON APPLICABLE, T1–T9 ACCEPTÉS, F-R1 REJET R3, F-R2 REJET R4, F-R3 REJET R4, F-R4 REJET R6, F-R5 REJET R4, horodatés 05:28:00 / 05:29:00). Rien n'est repris de ce dossier sans re-vérification — chaque rendu a été re-couru par le juge (section Rejeu).
- **Registre et reçus** : ligne 943 relue au fichier (design F1-10 SIGNÉ, reçu 042) ; reçu G-20261112-042 présent au ledger local ; registre 943 lignes ; reçu G-20261112-041 présent (checkpoint T8) ; ligne 787 relue au fichier (BYB F1-2 v2 ACCEPTÉ comme saisine, 2026-11-11 ~00:53 EST — checkpoint T7).
- **Jugement précédent lu comme forme** (`JUGEMENT-F1-9.md`, 16 154 o, 105 lignes, VALIDÉE AVEC RÉSERVES).

## Rejeu

cargo test 213/213, 0 échec — suite re-courue par le juge en clone frais `~/workspace/v5-f1-10-juge`, log re-compté au stdout (20 « test result: ok », 0 échec). Décomposition re-comptée : 16 lib + 7 discover + 13 execute + 11 judge + 24 memory + 17 R10 + 43 rollback + 24 router + 20 vision + 38 action = 213. Le log du producteur (`suite-f1-10.txt`, 343 lignes) porte les mêmes comptes, ligne par ligne.

CLI `prove-rollback` re-courue par le juge (binaire construit dans le clone frais, `--now 2026-11-13T05:45:00-05:00`) sur des COPIES — dossier copié + journal réel copié (88 lignes) + journal-scénario du clone + design copié + fixtures fautives copiées, dans `~/workspace/v5-f1-10-juge-scratch/` ; le dossier du producteur n'a pas été touché (33 398 o, mtime 05:25 EST, inchangé) :

| Cas | Attendu | Reçu | Sortie |
|---|---|---|---|
| T0 | NON APPLICABLE (hold-out vert) | NON APPLICABLE — hold-out H-F1-2 vert, 0 événement de rollback | 0 |
| T1 | ACCEPTÉ R1–R8 | ACCEPTÉ — 13e reprend F1-5 au checkpoint seq 20, re-preuve H-F1-2, perte 0 | 0 |
| T2 | ACCEPTÉ R1–R8 | ACCEPTÉ — Ryan reprend F1-6 au checkpoint seq 27, re-preuve H-F1-3, perte 0 | 0 |
| T3 | ACCEPTÉ R1–R8 | ACCEPTÉ — Graham reprend F1-7 au checkpoint seq 37, re-preuve H-F1-6, perte 0 | 0 |
| T4 | ACCEPTÉ R1–R8 | ACCEPTÉ — L00 + pulses + coordinateur reprend F1-8 au checkpoint seq 48, re-preuve H-F1-7, perte 0 | 0 |
| T5 | ACCEPTÉ R1–R8 | ACCEPTÉ — opérateur + sous-agents + coordinateur reprend F1-9 au checkpoint seq 57, re-preuve H-F1-8, perte 0 | 0 |
| T6 | ACCEPTÉ R1–R8 | ACCEPTÉ — Nardole reprend F1-3 au checkpoint seq 6, re-preuve H-F1-4, perte 0 | 0 |
| T7 | ACCEPTÉ R1–R8 | ACCEPTÉ — Rick reprend F1-1 au checkpoint registre journal 787, re-preuve H-F1-1, perte 0 | 0 |
| T8 | ACCEPTÉ R1–R8 | ACCEPTÉ — Graham reprend F1-2 au checkpoint reçu G-20261112-041, re-preuve H-F1-5, perte 0 | 0 |
| T9 | ACCEPTÉ R1–R8 | ACCEPTÉ — Bill reprend F1-4 au checkpoint seq 13, re-preuve H-F1-1, perte 0 | 0 |
| F-R1 | REJET R3 | REJET R3 — champ 'décideur', valeur reçue '' : le retour est décidé par le coordinateur, par événement du journal, jamais par la fonction elle-même | 2 |
| F-R2 | REJET R4 | REJET R4 — champ 'checkpoint — preuve', valeur reçue '(vide)' : un checkpoint sans preuve ne porte rien à re-vérifier | 2 |
| F-R3 | REJET R4 | REJET R4 — champ 'hold-out', valeur reçue 'vert' : reprise d'une fonction dont le hold-out est vert | 2 |
| F-R4 | REJET R6 | REJET R6 — champ 'révocation', valeur reçue 'effacement' : une révocation qui efface est une perte, pas une correction | 2 |
| F-R5 | REJET R4 | REJET R4 — champ 'repreneur', valeur reçue 'Ryan' : le repreneur est celui que le design nomme | 2 |

15/15 conformes aux attendus. Les sorties 2 des faits sont les rejets attendus, pas des échecs. Le contrôle F-R2 a été re-vérifié contre le journal réel : seq 49 (`dispatch_typed` F1-9, EVT-20261113-024, 2026-11-13T04:23:26-05:00) porte bien une preuve vide.

**Routeur vérifié au fichier** (`journal-router.jsonl`, 88 lignes, seq 1–88 contigus, event_ids uniques, `\n` final vérifié) : 14 types — dispatch_relayed 16, dispatch_typed 10, correction 9, rollback_decided 9, rollback_executed 9, dispatch_ack 8, judgment_requested 6, judgment_rendered 6, merge_executed 4, fact_recalled 3, vision_held 3, closure_pulse 2, action_taken 2, pulse 1 (total 88). Seq 58–60 = DELIVER, 61–62 = JUDGE (dispatch), 63–88 = 26 événements simulés T1–T9 (26 occurrences « SIMULÉ ») : `rollback_decided` + `correction` sauf T2 + `rollback_executed`, T3 avant T8. Les 9 checkpoints du design ont été relus au journal réel : seq 6 (EVT-20261111-006, `judgment_rendered` F1-3, 2026-11-11T02:02:33-05:00), seq 13 (EVT-20261112-006, F1-4, 2026-11-12T14:57:33-05:00), seq 20 (EVT-20261112-013, `closure_pulse` F1-5, 2026-11-12T22:26:13-05:00), seq 27 (EVT-20261113-002, `merge_executed` F1-6, 2026-11-13T00:35:31-05:00), seq 37 (EVT-20261113-012, F1-7, 2026-11-13T01:47:15-05:00), seq 48 (EVT-20261113-023, F1-8, 2026-11-13T03:25:55-05:00), seq 57 (EVT-20261113-032, F1-9, 2026-11-13T04:50:22-05:00) — tous avec preuve non vide, conformes au dossier.

## CI re-vérifiée à l'API

CI re-vérifiée à l'API par le juge sur la tête, check-run par check-run, à 05:34 EST puis de nouveau au moment du jugement (05:37 EST) — **8/8 success**, inchangée entre les deux lectures :

- CodeQL: success
- Verify Category 03_Submodules_EGM_Harvester: success
- Verify Category 01_Kernel_Gates: success
- Verify Category 04_Security_OWASP_RigInfinity: success
- Verify Category 02_Holons_578_QualityControl: success
- Deterministic Gate (5D Semantic AST + CAS Holons + 7R + OKF): success
- S1-RICK & Reviewer-Security · OWASP Top 10 & Worktree Patch: success
- Analyze (actions): success

## Hold-outs

- **H-F1-9 — VERT** (fenêtre observée du pas) : les 10 cas T0–T9 rendus par la fonction selon R1–R8, avec le rejet du fait F-R1 (section suivante) ; les retours rendus comme événements `rollback_decided` / `rollback_executed` (seq 63–88, marqués SIMULÉ) ; les re-preuves portées dans le même pas (R7, champ Re-preuve : oui dans chaque dossier — re-preuve simulée, comme l'échec : aucun échec réel n'a jamais eu lieu) ; les cas limites §5.4 (a)–(i) couverts par la suite (43 tests, 0 échec). Le reçu H-F1-9 est consigné après le merge (R2).
- **H-M1 — VERT** : mesure zéro du Discover re-mesurée par le juge à l'atterrissage — registre 943 lignes (ligne 943 = design signé, reçu 042), routeur 88 lignes seq 1–88, L00 Run #710 (05:27 EST, aucun seuil franchi), N2 Run #487 (W1 ANOMALIE persistante D-N021/D-N024/D-N026/D-N032, silence 12 j 10 h — hors périmètre de ce pas, dispatches clos ou en attente de décision), master `3458a2bd18dbc1cdd41229dad77df76c30c8b2d3` au jugement (miroir pulse ; l'ancre design `9622c50e7e703a4ec04b411cdc06325846c74a9b` est dépassée, comme prévu par P-F1-10-5), 0 PR ouverte autre que #53, mécanisme codé présent (module `rollback` + CLI `prove-rollback`, 9 modules, 9 CLI).
- **H-M2 — VERT** : aucun paquet amont modifié — code A'Space neuf, diff vide sur le code amont (21 fichiers, tous fondation / fiche / log / audit / manifeste).
- **H-M3 — VERT** : suite 213/213 re-courue par le juge (section Rejeu) ; 10 cas passants, 5 faits rejetés, cas limites §5.4 (a)–(i) — 0 rouge, aucune exclusion nécessaire.
- **H-M4 — VERT** : module `rollback` 0 appel sortant (données injectées) ; CLI `prove-rollback` lectures au fichier local nommées, 0 appel réseau, 0 appel en écriture d'état (O3 conservée) — vérifié au grep (aucun `http`, `reqwest`, socket ni processus dans `rollback.rs` et `prove-rollback.rs`) et relu dans l'audit télémétrie § Rollback.
- **H-M5 — VERT** : fonction Rollback nommée dans le manifeste ; ligne `validated_by` périmée corrigée à l'atterrissage (F1-9 VALIDÉE AVEC RÉSERVES, PR #52 mergée `691b0a0`, jugement journal 942).
- **H-M6 — VERT** : seul le code A'Space de la fonction Rollback ; section Divergence de la fiche remplie (4 entrées F1-10 : types légalisés, réveil = ré-instanciation, F-A3 non simulé, O3 portée comme limite nommée).
- **H-M7 — VERT** : fiche mise à jour (§14 F1-10 ajouté, §13 F1-9 corrigé — statut CLOSE et jugement VALIDÉE AVEC RÉSERVES, journal 942).
- **H-F8-9 — NON MESURÉ** (R1) : plafonds 1 % / 5 % / 20 % — mesure à la comptabilité du fournisseur, non mesurable depuis ce poste.

## Fautif planté (J6)

F-R1 — reprise auto-déclarée sans décision du coordinateur : REJET R3 (sortie 2) par la CLI `prove-rollback`, re-couru par le juge sur copies — « le retour est décidé par le coordinateur, par événement du journal, jamais par la fonction elle-même — une reprise auto-déclarée est une seconde vérité, pas un retour ». Le fait F-R1 est rejeté avec la règle attendue R3 : la fonction distingue le décidé de l'auto-déclaré. Le dossier du fait (`ROLLBACK-FAUTIF-1.md`) est byte-identique à la fixture `tests/fixtures/rollback-fautif-1.md`.

F-R2 → REJET R4 (« un checkpoint sans preuve ne porte rien à re-vérifier — un événement à preuve vide n'est jamais un checkpoint »). F-R3 → REJET R4 (« une fonction saine n'est pas reprise »). F-R4 → REJET R6 (« une révocation qui efface est une perte, pas une correction »). F-R5 → REJET R4 (« le repreneur est celui que le design nomme »). Dans tous les cas, la fonction ne laisse jamais passer le retour du fait : elle le rejette, avec la règle qui se déclenche en premier selon l'ordre du design (R1→R4→R3→R2→R5→R6→R7→R8).

## Ce que ce jugement ne prouve pas

- Le rollback d'un échec réel — les cas T1–T9 portent sur des échecs simulés, par design (D-F1-10-2, Discover §4.2). Ce jugement prouve la capacité, pas un événement.
- La semaine complète — portée par F1-11 (H-F1-10). Ce jugement prouve la fenêtre observée du pas.
- Le désarchivage littéral des sessions archivées — exclu de ce pas (D-F1-10-5, arbitrage vision §8a). Ce jugement prouve le réveil par ré-instanciation.
- La levée d'O3 — la CLI ne gagne pas le HTTPS dans ce pas (D-F1-10-11) ; l'appel en écriture reste celui de l'opérateur, gâté par l'ACCEPT pré-merge de la CLI (patron R1 de F1-6).
- Les tokens (H-F8-9) — non mesurables depuis ce poste (R1).
- Aucun reçu consigné par ce jugement. Rien n'est écrit au registre par ce jugement. Aucun merge exécuté par ce jugement. Aucune PR ouverte par ce jugement. Ce jugement est un verdict, pas une exécution.

## Réserves

- **R1 — Tokens (H-F8-9 NON MESURÉ).** Mesure à la comptabilité du fournisseur, non mesurable depuis ce poste. Suivi : consignée dans le reçu du pas, comme aux pas F1-5..F1-9.
- **R2 — Reçus après merge.** Reçus G-20261112-043 (livraison, mission `LE1-FAB-D-N055-022` PROPOSÉE) et G-20261112-044 (merge H-F1-9, mission `LE1-FAB-D-N055-023` PROPOSÉE) — numéros assignés au dépôt sur union fraîche des branches `work-*-ledger`, jamais anticipés (P-F1-10-1). Suivi : exécutant dédié de clôture, après le merge.
- **R3 — Alignement `note_code` du manifeste (suivi ouvert depuis F1-7, confirmé aux jugements F1-7, F1-8 et F1-9).** Le `note_code` répète « CLI `execute-merge` : 1 appel en écriture d'état nommé, compté et tracé (le merge) », alors que la Divergence (fiche) porte que l'appel est effectué par l'opérateur, la CLI contrôlant et gâtant. Le pas F1-10 a étendu le `note_code` sans corriger la phrase F1-6. Suivi : aligner le `note_code` sur la formulation Divergence — hors PR, dû pour un pas ultérieur.
- **R4 — F-A3 + ancres codées en dur (généralisation due pour F1-11).** F-A3 n'est pas l'échec simulé de T5, comme tranché (D-F1-10-10) ; il reste réserve ouverte et suivi F1-11. Sur les ancres : le code de `prove-rollback` ne porte aucune ancre codée en dur — vérifié au grep (un seul littéral « seq 20 » dans un test unitaire du parseur) ; les ancres des cas sont des données du dossier, lues aux arguments et aux fichiers. La généralisation reste due pour F1-11 (R4 F1-8).

## Observations

- **O1 — Décisions simulées lues dans la fixture, checkpoints lus au journal réel.** La CLI surcharge les faits de décision, d'arrêt et de checkpoint par les lectures au fichier — mais les décisions simulées (seq 58–83) ne sont jamais consignées au journal réel : elles sont lues dans la fixture, qui fait foi pour elles (nommé par le design, A-F1-10-5). Ce n'est pas un défaut : c'est la frontière nommée du simulé. Le juge l'a vérifiée : les 57 premières lignes de la fixture sont byte-identiques au journal réel.
- **O2 — Revert T2 attesté par le témoin seul.** Les commits du merge erroné simulé (`5e73cc3`) et de son revert (`d02039f`) n'existent pas sur le distant — vérifié par le juge (« not our ref ») : la branche jetable n'a jamais été poussée, jamais master, comme designé. Le revert n'est donc pas re-vérifiable dans l'historique Git ; il est attesté par le témoin `revert-t2-temoin.txt` (base, merge, revert, procédure). Limite honnête, pas un défaut.
- **O3 — Exec du producteur en échec (exit 129) sans défaut laissé.** Un exec de Ryan a échoué en cours d'exécution (subprocess non-zero) ; toutes les vérifications ci-dessus (PR, CI, suite, routeur) sont vertes et re-mesurées par le juge.
- **O4 — Le master bouge par miroirs pulse.** Ancre design `9622c50` → master `3458a2b` au jugement (miroirs pulse 05:15–05:31). Toute ancre est re-mesurée à l'API au moment de l'usage — le merge devra re-mesurer la base avant l'appel (patron F1-8, écart parent1).
- **O5 — Le dossier du producteur n'a pas été touché par le juge.** Les 15 re-runs CLI ont écrit leurs rendus dans la copie du juge (`~/workspace/v5-f1-10-juge-scratch/ROLLBACK-F1-10.md`), jamais dans `ROLLBACK-F1-10.md` (33 398 o, mtime 05:25 EST, inchangé).

## Auto-contrôle

Jugement auto-contrôlé par `judge-pr` (fonction Juger, clone frais, `--planted-rule R3`) : ACCEPTÉ — Jugement PR #53 : VALIDÉE AVEC RÉSERVES — J1–J8 passés (1 SHA complets vérifiés, tête 85301c3e9177fa9e290b86ace6482955a33e191c), sortie 0.
