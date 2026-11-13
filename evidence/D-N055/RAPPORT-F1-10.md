# Rapport — D-N055 F1-10 : fonction Rollback (PR #53)

**Pas :** D-N055 F1-10 (Fusion 13 → 1) — fonction Rollback : le 1 revient à la chaîne 13 si un hold-out échoue, par la fonction, au checkpoint du journal, sans perte.
**Design :** signé Clara 2026-11-13T05:12:00-05:00 (`DESIGN-FONDATION-13-1-F1-10-PROJET.md`, 70 499 o, 218 lignes), journal 943, reçu G-20261112-042. Discover Bill 88 065 o, 329 lignes.
**Exécution :** Ryan (Factory), PR #53 ouverte 05:29:04 EST ; coordinateur terminé après la livraison, rapport complet, avec les preuves.
**Jugement :** fonction Juger en sous-agent borné (pas une session 13e), `JUGEMENT-F1-10.md` (19 826 o, 111 lignes) — VALIDÉE AVEC RÉSERVES, merge OUI tel quel, 0 amendement.
**Merge :** PR #53 mergée 2026-11-13T10:40:32Z (05:40:32 EST), commit `28d32f7`, 2 parents (DVG-01). **F1-10 CLOSE.**

## Livré

| Élément | Fichier | Taille |
|---|---|---|
| Module Rollback (nouveau) | `src/rollback.rs` | 35 744 o, 842 lignes, R1–R8 (ordre R1 → R4 → R3 → R2 → R5 → R6 → R7 → R8), pur, 0 appel sortant |
| CLI (nouveau) | `src/bin/prove-rollback.rs` | 20 682 o, 561 lignes, commande `check`, lectures : dossier, journal, design |
| Suite (nouveau) | `tests/rollback.rs` + 8 fixtures | 17 913 o, 617 lignes, 43 tests |
| Fixtures | `tests/fixtures/journal-f1-10-scenario.jsonl` | 52 401 o, 87 lignes (les 57 premières byte-identiques au journal réel) |
| Fixtures fautif | `tests/fixtures/rollback-fautif-1..5.md` | 2 697 / 2 231 / 2 284 / 2 293 / 2 256 o, 56 / 50 / 50 / 50 / 50 lignes |
| Fixture valide + témoin | `tests/fixtures/rollback-valide-t1.md` + `revert-t2-temoin.txt` | 2 254 o (49 lignes) + 1 017 o (20 lignes) |
| Routeur 14 types | `src/router.rs` (`EVENT_TYPES` 12 → 14) | `rollback_decided` + `rollback_executed` inclus (A-F1-10-3), +34/−4 |
| Test routeur 14 types | `tests/router.rs` | +56/−4 |
| Mémoire (types journal) | `src/memory.rs` (`JOURNAL_EVENT_TYPES` 12 → 14) | +12/−5 |
| Test mémoire | `tests/memory.rs` | +5/−3 |
| Branchements | `src/lib.rs`, `Cargo.toml` | `pub mod rollback;`, binaire `prove-rollback`, 0 dépendance |
| Fiche | `00_Memoire/bundle/concepts/fondation-13-1.md` (§14 F1-10, §13 F1-9 CLOSE, Divergence remplie) | +155/−2 |
| Manifeste | `fondation-13-1.manifest.json` | Rollback nommée, `validated_by` corrigé (F1-8 VALIDÉE AVEC RÉSERVES, journal 940 ET F1-9 VALIDÉE AVEC RÉSERVES, PR #52 mergée `691b0a0`, jugement journal 942) |
| Audit télémétrie | `fondation-13-1-TELEMETRY-AUDIT.md` (§ Rollback) | 0 appel sortant, 0 appel en écriture d'état (O3 conservée), +65/−0 |
| Log mémoire | `00_Memoire/bundle/log.md` (Note, append-only) | +1 ligne |

Suite totale après F1-10 : `cargo test` **213/213 PASS** (16 lib + 7 discover + 13 execute + 11 judge + 24 memory + 17 R10 + 43 rollback + 24 router + 20 vision + 38 action), re-courue par le juge en clone frais.

## Séquence

1. **Design signé** 05:12:00 (journal 943, reçu 042, validé `r10-receive`).
2. **Exécution** lancée ~05:15. Fonction écrite, fautif planté F-R1 (reprise auto-déclarée) → REJET R3, sortie 2 ; F-R2 → REJET R4, F-R3 → REJET R4, F-R4 → REJET R6, F-R5 → REJET R4, sortie 2 ; dossiers valides T1–T9 → ACCEPTÉS R1–R8, sortie 0 ; T0 → NON APPLICABLE, sortie 0.
3. **Incident mineur** : un exec du Ryan a échoué en cours de route (exit 129, subprocess non-zero) — sans impact établi, toutes les vérifications re-mesurées vertes par le coordinateur (O3).
4. **PR #53 ouverte** 05:29:04 EST, tête `85301c3`, base `c0b6dce`, 21 fichiers +2772/−21, mergeable true/clean, CI 8/8.
5. **Jugement** ~05:38 EST : VALIDÉE AVEC RÉSERVES (R1 tokens, R2 reçus 043/044, R3 alignement `note_code`, R4 F-A3 + ancres). Rejeu indépendant : CI 8/8 re-vérifiée deux fois, suite 213/213 re-courue, CLI re-courue 15/15 conformes sur des copies (dossier du producteur intact, 33 398 o, mtime 05:25 EST), checkpoints relus au journal réel, module lu en entier, auto-contrôle par `judge-pr` ACCEPTÉ J1–J8 (`--planted-rule R3`). Événement `judgment_rendered` seq 89.
6. **Merge** 05:40:32 EST selon la procédure R1 : pré-merge ACCEPTÉ E1–E5 (sortie 0, après 1 rejet de forme du dossier : E1 « tête autorisée » exige le libellé en minuscules, `line_containing` sensible à la casse), 1 seul appel opérateur `gh pr merge 53 --merge --repo Amdkn/Aspace_OS_V5` (premier essai sans `--repo` : « not a git repository », aucun merge effectué), contrôle complet ACCEPTÉ E1–E8 (sortie 0), E6 consignée, E7 re-vérifiée par un tiers. Merge commit `28d32f7`, 2 parents (`3458a2b` + `85301c3`, DVG-01), master = merge commit au merge, 0 PR ouverte. Événement `merge_executed` seq 90.
7. **Clôture** : E7 re-vérifiée par un tiers, reçus 043 (livraison) + 044 (H-F1-9), journal 944, preuves du jour sur master. **F1-10 CLOSE.**

## Réserves (portées au reçu 044)

- **R1** — mesure tokens du pas non mesurable depuis ce poste (H-F8-9, plafonds 1 % / 5 % / 20 %) : suivi hors PR.
- **R2** — ce reçu-ci (H-F1-9, 044) ; livraison 043 (mission LE1-FAB-D-N055-022).
- **R3** — alignement `note_code` du manifeste sur la Divergence (suivi F1-7 toujours ouvert, confirmé aux jugements F1-7, F1-8, F1-9 et F1-10) : le `note_code` répète « CLI `execute-merge` : 1 appel en écriture d'état nommé, compté et tracé (le merge) », alors que la Divergence porte que l'appel est effectué par l'opérateur, la CLI contrôlant et gâtant. Le pas F1-10 n'a pas corrigé la phrase F1-6. Suivi hors PR.
- **R4** — F-A3 + ancres codées en dur (généralisation due pour F1-11). Le code de `prove-rollback` ne porte aucune ancre codée en dur — un seul littéral « seq 20 » dans un test unitaire du parseur. Suivi : généralisation des ancres codées en dur, due pour F1-11.

## Observations

- O1 — décisions simulées lues dans la fixture (nommé par le design), checkpoints lus au journal réel.
- O2 — revert T2 attesté par le témoin seul — commits `5e73cc3`/`d02039f` absents du distant (« not our ref »), jamais master comme designé.
- O3 — exec Ryan exit 129 sans défaut laissé.
- O4 — master `9622c50` → `3458a2b` au jugement — base re-mesurée avant l'appel de merge ; aucun écart parent1 sur ce pas : le parent réel `3458a2b` est celui attendu aux pré-vérifications.
- O5 — le dossier du producteur n'a pas été touché par le juge (33 398 o, mtime 05:25 EST, inchangé) ; les 15 re-runs CLI ont écrit dans les copies du juge.
- O6 — le pulse 05:10 a classé F1-10 « pas encore lancée » (12 min sans avancement au registre) alors que le coordinateur design lancé 04:59 travaillait — le silence du registre pendant un travail en cours n'est pas un blocage ; le design a été signé 05:12, journal 943.
- O7 — L00 vivant : Run #709 à 05:17 EST (pulse 05:26) ; les notes dead-man des pulses 04:45–05:15 lisaient une vieille ligne du corps (Run #696/#697 à 23:17–23:27 EST) alors que le fichier prépend ses runs en tête — leçon confirmée 04:46 et 05:26.

## Hold-outs

| Hold-out | Verdict | Preuve |
|---|---|---|
| H-F1-9 — Preuve du pas | VERT | 10 cas T0–T9 rendus par la CLI (T0 NON APPLICABLE, T1–T9 ACCEPTÉS R1–R8), fait F-R1 rejeté R3, cas limites ; re-preuve simulée comme l'échec, par design ; événements `rollback_decided` / `rollback_executed` seq 63–88 (SIMULÉ) ; `merge_executed` seq 90 ; 0 reprise réelle exécutée — la preuve est simulée, le mécanisme est codé et rejoué par le juge (15/15) |
| H-M1 — Mesure zéro nommée | VERT | Registre 943 lignes (dernière ligne lue : journal 943, design F1-10 SIGNÉ, reçu 042) ; journal-router 89 lignes seq 1–89 contigus au jugement (90 après le merge : seq 89 `judgment_rendered`, seq 90 `merge_executed`) ; L00 Run #709 (05:17 EST, aucun seuil franchi) ; N2 Run #486 ; design 70 499 o / 218 lignes, sha256 `75c7703a…` ; Discover 88 065 o / 329 lignes, sha256 `0b91c80e…` |
| H-M2 — Aucun paquet amont modifié | VERT | Diff = 21 fichiers A'Space, 0 dépendance |
| H-M3 — Suite verte | VERT | Suite 213/213 re-courue, cas passants + 5 faits rejetés avec leur raison nommée + cas de forme |
| H-M4 — Télémétrie zéro | VERT | 0 appel sortant dans le code, audit joint (§ Rollback) ; CLI : lectures au fichier local nommées, comptées et tracées, 0 appel réseau, 0 appel en écriture d'état (O3 conservée) |
| H-M5 — Manifeste | VERT | Fonction Rollback nommée, adresse `fiber:a0:fondation-13-1` ; `validated_by` corrigé (F1-8 VALIDÉE AVEC RÉSERVES, journal 940 ET F1-9 VALIDÉE AVEC RÉSERVES, PR #52 mergée `691b0a0`, jugement journal 942) |
| H-M6 — Frontière | VERT | Seul le code A'Space de la fonction Rollback ; section Divergence de la fiche remplie |
| H-M7 — Fiche versionnée | VERT | Fiche mise à jour, §14 F1-10 consigné, §13 F1-9 CLOSE |
| H-F8-9 — Plafonds | NON MESURÉ (voir R1) | Plafonds 1 % / 5 % / 20 % — mesure à la comptabilité du fournisseur, consignée dans le reçu du pas ; le juge ne mesure pas les tokens depuis ce poste |

## Preuves

- Jugement : `evidence/D-N055/JUGEMENT-F1-10.md` (19 826 o).
- Dossier de rollback : `evidence/D-N055/ROLLBACK-F1-10.md` (33 398 o, 504 lignes).
- Dossier d'exécution du merge : `evidence/D-N055/EXECUTION-MERGE-F1-10.md` (E6 + E7 tiers).
- Reçus : G-20261112-042 (design, `3763669`), G-20261112-043 (livraison, `23caae8`), G-20261112-044 (merge H-F1-9, `97c74ab`), branche `work-dn055-ledger`.
- Journal-router : seq 1–90 contigus (`judgment_rendered` seq 89, `merge_executed` seq 90).
- Merge : PR #53, commit `28d32f712ca0d2840959917fa848c07b0b03feb2`, 2 parents (DVG-01), master = merge commit au merge, 0 PR ouverte.

## Suivis hors pas

- S-F2-1 (= S-F1-1 requalification H-P8-4 amendement F8, S-F1-2 en-tête AGPL `openrig_terminal.rs`, S-F1-3 revisite herdr-core signal 3 jours) · S-F2-2 (R1 SIGPIPE main.rs) · S-F2-3 (suivis pas 8 F8) · S-F2-4 (E-F2-8 registre l.186 → reçu R10 F1) · S-F2-5 (alignement skills V5 sur le gel orca) · S-F2-6 (revisite quotidienne orca, dérive 1 205) · R3 F1-7/F1-8/F1-9/F1-10 (alignement `note_code` du manifeste) · R1 F1-10 (tokens non mesurables, H-F8-9) · R4 F1-8/F1-9/F1-10 (généralisation des ancres CLI + cas F-A3, due pour F1-11).
- Reste de D-N055 après F1-10 : **F1-11**.

*Fin du rapport. F1-10 CLOSE.*
