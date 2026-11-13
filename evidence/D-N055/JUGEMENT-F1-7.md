# Jugement — D-N055 F1-7 : fonction Mémoriser (PR #50)

**Fonction :** le 1 — fonction Juger, exercée en sous-agent borné (pas une session 13e séparée), le mécanisme codé (module `judge` + CLI `judge-pr`) étant l'outil de validation du jugement.
**Date du jugement :** 2026-11-13 ~01:44 EST (`2026-11-13T06:44:27Z`).
**PR jugée :** #50 — « D-N055 F1-7: Mémoriser (retrouver un fait des 13 mémoires sans perte, par la fonction Mémoriser, sans Graham) », tête `913b8edd52fc0d04979404b22cc56d0f6dd3ec82`.
**Design jugé contre :** `plans/DESIGN-FONDATION-13-1-F1-7-PROJET.md`, SIGNÉ, journal 937 (D-F1-7-1..12, A-F1-7-1..6, P-F1-7-1..5).
**Méthode :** rejeu indépendant, rien pris sur parole. Clone frais, tête PR vérifiée à l'API avant bascule ; diff complet lu ; suite re-courue ; CLI re-courue sur les dossiers réels ; CI re-vérifiée à l'API au moment du jugement ; sources relues au fichier.

## Verdict : VALIDÉE

**Recommandation merge : OUI, tel quel, sur la tête `913b8ed`.**
Aucun amendement. Le merge est **autorisé tel quel** sur la tête autorisée.
**Tête autorisée : `913b8edd52fc0d04979404b22cc56d0f6dd3ec82`**
Merge en **true merge commit** (2 parents, DVG-01), jamais par le runner.

## État de la PR

- PR #50 **ouverte**, tête `913b8edd52fc0d04979404b22cc56d0f6dd3ec82` (1 commit, parent unique `474765f` = master au moment de la branche), base de la PR `474765f43ac2e51d229aef6b69f47c3a0e270ede` (master à l'ouverture, miroir pulse 01:15).
- `mergeable: true`, `mergeable_state: clean`, 30 fichiers, **+1925/−16**.
- Commit tête : committer « Aspace Factory » <factory@aspace.local>, date `2026-11-13T06:35:11Z` (01:35:11 EST), créée `2026-11-13T06:35:33Z`.

## CI re-vérifiée

Check-runs re-vérifiés à l'API à 01:44 EST, sur la tête jugée, un à un, avec leur conclusion — jamais repris du dossier d'exécution, jamais lus sur l'API legacy des statuts combinés. **8/8 success, 0 non-success** :

- Analyze (actions) : success
- CodeQL : success
- Deterministic Gate (5D Semantic AST + CAS Holons + 7R + OKF) : success
- S1-RICK & Reviewer-Security · OWASP Top 10 & Worktree Patch : success
- Verify Category 01_Kernel_Gates : success
- Verify Category 02_Holons_578_QualityControl : success
- Verify Category 03_Submodules_EGM_Harvester : success
- Verify Category 04_Security_OWASP_RigInfinity : success

## Diff lu

Diff complet lu (clone frais `~/workspace/v5-f1-7-juge`, jamais les fichiers de l'exécutant tels quels) ; table fichier par fichier, contenu vérifié : 30 fichiers, tous sous `00_Memoire/bundle/` ou `01_Forkable/FKB00_Runtime/00_A0_Core/fondation-13-1/` (code A'Space neuf).

| Fichier | Taille |
|---|---|
| `src/memory.rs` (nouveau, 653 lignes) | 24 210 o |
| `src/bin/recall-fact.rs` (nouveau, 402 lignes) | 14 262 o |
| `tests/memory.rs` (nouveau, 390 lignes) | 15 036 o |
| `tests/fixtures/citation-t1.md` (nouveau, 30 lignes) | dossier T1 |
| `tests/fixtures/citation-t3.md` (nouveau, 29 lignes) | dossier T3 |
| `tests/fixtures/citation-valide.md` (nouveau, 29 lignes) | dossier T2 |
| `tests/fixtures/citation-merge.md` (nouveau, 29 lignes) | dossier merge |
| `tests/fixtures/citation-fautif-1.md` (nouveau, 29 lignes) | dossier F-X1 |
| `tests/fixtures/citation-limite-*.md` (5 nouveaux, 29 lignes chacun) | dossiers limites (a)–(f) |
| `tests/fixtures/source-*.txt` (9 nouveaux, 1 ligne chacun) | lignes sources relues |
| `src/lib.rs` | 3 lignes modifiées (dont `pub mod memory;`) |
| `Cargo.toml` | 6 lignes modifiées (dont le binaire `recall-fact`, aucune dépendance) |
| `src/router.rs` | 8 lignes modifiées (`EVENT_TYPES` à 10 types, `fact_recalled` inclus) |
| `tests/router.rs` | 10 lignes modifiées (test des 10 types) |
| `fondation-13-1.manifest.json` | 1 ligne (surface + fonction Mémoriser, `validated_by` corrigé) |
| `fondation-13-1-TELEMETRY-AUDIT.md` | +45 lignes (§ Mémoriser) |
| `00_Memoire/bundle/concepts/fondation-13-1.md` | +114/−5 (§11 F1-7, §4/§6/§10 corrigés) |
| `00_Memoire/bundle/log.md` | +3 lignes (Note F1-7, append-only) |

## Rejeu indépendant

**`cargo test` 100/100 PASS, 0 échec** — re-couru dans un clone frais, sur la tête vérifiée, chiffres re-comptés aux logs, sans reprendre le récit du producteur. Suite re-comptée : 7 lib + 7 discover + 13 execute + 11 judge + 24 memory + 17 R10 + 21 router = 100, 0 échec (F1-2/F1-3/F1-4/F1-5/F1-6 en régression verte). Log : `~/workspace/v5-f1-7-scratch/suite-juge-f1-7.txt`.
CLI `recall-fact check` (binaire du clone frais) sur les dossiers réels : T1 ACCEPTÉ M1–M8, sortie 0 (4 lectures au fichier) ; T2 ACCEPTÉ M1–M8, sortie 0 (2 lectures) ; T3 ACCEPTÉ M1–M8, sortie 0 (1 lecture). CLI sur le fait F-X1 : REJET M3, sortie 2. CLI sur les faits F-X2/F-X3/F-X4 (dérivés chacun par une seule différence) : REJET M2, REJET M2, REJET M4, sortie 2. M6 (filet) prouvé par la suite (citation égale au fait planté rejetée M6).
Sources relues au fichier par moi : Bill:38 (10:50), MEMORY.md:98 (2027-10-09), daily 2026-10-09:146 (ID 11e complet), contradiction 10:46 (daily 10-17:657) et 10:55 (Rick:67). Fixtures `source-*.txt` byte-identiques aux lignes réelles (diff vérifié). Sorties CLI du producteur (`cli-t1.txt`, `cli-t2.txt`, `cli-t3.txt`, `cli-fautif-1.txt`) identiques à mes rejeux, à l'horodatage près.

## Lecture de la fonction jugée

Le module `memory` lu en entier (653 lignes, 24 210 o) — ordre M1 → M7 → M2 → M3 → M4 → M5 → M6 → M8 conforme au design ; M1 exige l'en-tête + les 4 champs + les quatre sections ; M7 insensible à la casse (leçon F1-5) ; M2 compare l'énoncé normalisé à la ligne relue ; M3 exige la date portée par la source ; M4 exige le statut parmi les six, justifié ; M5 exige le statut `contredit` et la version divergente listée ; M6 est le filet (citation égale au fait planté) ; M8 exige les limites nommées. La fonction ne contacte ni le fichier local ni l'API (ligne, date, corroborations et fait planté injectés par l'appelant) ; `JOURNAL_EVENT_TYPES` compte 10 types, `fact_recalled` inclus (A-F1-7-3), identique à `router::EVENT_TYPES` (test `dix_types_dont_fact_recalled`). Zéro dépendance externe, zéro appel sortant dans le code.
La CLI `recall-fact` lue en entier (402 lignes, 14 262 o) — découpage UTF-8 par fenêtres de 10 caractères (correctif du « — ») ; `--corroboration` découpé en 3 parties (le « : » de « 10:46 » ne casse pas le parsing) ; la date de la source est celle que porte la ligne, sinon toutes les dates de la ligne nommées (jamais la première choisie — M3 interdit l'inférence), sinon la date du fichier pour une note quotidienne. La CLI ne lit que des fichiers locaux et n'écrit que sur stdout/stderr ; 0 recherche sémantique (A-F1-7-5).

## Tableau des hold-outs

| Hold-out | Verdict | Preuve (rejeu indépendant) |
|---|---|---|
| H-F1-6 — Preuve du pas | VERT | 3/3 rappelés avec 4 champs exacts (T1 `contredit`, T2 `vérifié`, T3 `consigné`), fait F-X1 rejeté M3, cas limites §5.4 (a)–(f) traités (suite 24/24) ; citations rendues comme événements `fact_recalled` seq 33–35 ; merge de la PR du pas À VENIR (E7 par un tiers + reçu après merge) |
| H-M1 — Mesure zéro nommée | VERT | Registre 937 lignes (dernière ligne lue : journal 937, design F1-7 SIGNÉ, reçu 033) ; re-compilation re-mesurée : 42 notes quotidiennes, 4 fichiers bank, 23 pages people (pas 22 — correction portée en avant), MEMORY.md 160 lignes, AGENTS.md 45 lignes ; journal-router 35 lignes seq 1–35 lues au fichier |
| H-M2 — Aucun paquet amont modifié | VERT | Diff = 30 fichiers A'Space neufs, 0 dépendance |
| H-M3 — Suite verte | VERT | `cargo test` 100/100 re-couru, cas passants + 4 faits rejetés avec leur raison nommée + cas limites (a)–(f) + cas de forme |
| H-M4 — Télémétrie zéro | VERT | 0 appel sortant dans le code, audit joint (§ Mémoriser) ; CLI : lectures au fichier local nommées, comptées et tracées, 0 appel réseau, 0 recherche sémantique |
| H-M5 — Manifeste | VERT | Fonction Mémoriser nommée, adresse `fiber:a0:fondation-13-1` ; `validated_by` corrigé (F1-6, verdict avec réserves, PR #49 mergée `e2e9c146e3ed03ec0d5f3c7be05ca702251f960e`, jugement journal 936) |
| H-M6 — Frontière | VERT | Seul le code A'Space de la fonction Mémoriser ; section Divergence de la fiche remplie |
| H-M7 — Fiche versionnée | VERT | Fiche mise à jour, §11 F1-7 consigné, §4/§6/§10 corrigés |
| H-F8-9 — Plafonds | NON MESURÉ (voir R1) | Plafonds 1 % / 5 % / 20 % — mesure à la comptabilité du fournisseur, consignée dans le reçu du pas ; le juge ne mesure pas les tokens depuis ce poste |

## Écarts et observations

Aucun écart bloquant. Aucun amendement. Quatre observations (O1–O4) :

- **O1** — T3 : l'Énoncé du dossier est la ligne 146 entière (11e + 12e + 13e), pas le seul fragment du 11e nommé par le design. Fidèle à la source — la ligne est citée telle qu'elle est, les 4 champs correspondent (date 2026-10-09 = date du fichier, statut `consigné`). Non bloquant.
- **O2** — Journal-router seq 28–35 : tous horodatés 01:39:24 (heure de routage en lot), alors que les citations sont datées 01:32 et la PR ouverte 01:35:33. Le contenu des événements est exact (tête, CI, citations) ; les horodatages sont ceux du routage, pas ceux des faits. Non bloquant.
- **O3** — Un exec du coordinateur d'exécution a échoué (exit 1, commande inconnue, signalé par le principal). Ma re-vérification indépendante n'a trouvé aucun défaut attribuable : suite 100/100, CLI 4/4, fixtures byte-identiques, CI 8/8. Non bloquant.
- **O4** — Suivi F1-6 R1 partiellement ouvert : la fiche Divergence porte désormais la formulation opérateur (« L'appel de merge est effectué par l'opérateur, pas par la CLI »), mais le `note_code` du manifeste attribue encore l'appel de merge à la CLI (« CLI `execute-merge` : 1 appel en écriture d'état »). Suivi hors PR, pas un défaut de F1-7 (le `note_code` ajouté par F1-7, lui, est exact).

## Conformité au design

D-F1-7-1..12 adoptées (design §9) ; fait planté = F-X1, fichier distinct, une seule différence sur le champ Date, rejet M3 (A-F1-7-1) ; faits F-X2/F-X3/F-X4 = une seule différence chacun, rejets M2/M2/M4 (A-F1-7-2) ; `fact_recalled` légalisé 10e type, accepté par le routeur (A-F1-7-3) ; compte « 5 tiers » corrigé à 10 occurrences (A-F1-7-4) ; module pur + CLI lectrice, 0 recherche sémantique (A-F1-7-5) ; acte triple borné aux 3 faits d'essai, seconde citation par la session 13e exclue (A-F1-7-6) ; missions 013/014 et entry_id 034/035 proposés, assignation au dépôt (P-F1-7-1) ; domicile du code nommé (P-F1-7-2) ; ordre d'exécution tenu (P-F1-7-3) ; aucune exclusion ne couvre le fait F-X1 (P-F1-7-4) ; re-mesure à l'exécution (P-F1-7-5). Second jugement systématique par la session 13e exclu (D-F1-7-8) ; jugement rendu comme événement `judgment_rendered` seq 36 (D-F1-7-10) ; la mémoire ne juge pas (M7).

## Fautif planté (J6)

Fait F-X1 (date 2027-10-08 au lieu de 2027-10-09) : REJET M3 par la CLI recall-fact (sortie 2) — la date citée n'est pas celle que porte la source (la source porte 2026-11-06, 2027-10-09, 2027-05-21, 2027-02-02). Les faits F-X2/F-X3/F-X4 sont rejetés M2, M2 et M4.

## Ce que le juge n'a pas fait

Aucun reçu consigné par ce jugement, aucune PR mergée par ce jugement, rien écrit au registre par ce jugement, aucune modification de la PR. Le juge juge, il n'exécute pas.

## Ce que ce jugement ne prouve pas

Le merge reste à exécuter puis à vérifier 2 parents à l'API (E7, par un tiers) ; le reçu H-F1-6 vient après, par un exécutant dédié ; les plafonds H-F8-9 ne sont pas mesurés par ce jugement ; la montée en périmètre (retrouver n'importe quel fait) est hors de ce pas.

## Réserves

- **R1** — Mesure tokens du pas non mesurable depuis ce poste (H-F8-9, plafonds 1 % / 5 % / 20 %) : suivi hors PR, pour le reçu du merge.
- **R2** — Le reçu H-F1-6 du merge de la PR #50 (035 proposé, mission `LE1-FAB-D-N055-014`) vient après le merge, par un exécutant dédié. Le reçu de livraison 034 est proposé (mission `LE1-FAB-D-N055-013`) ; le design a pris 033 pour lui-même (journal 937, commit `d26b080`).
- **R3** — Suivi hors PR (O4) : aligner le `note_code` du manifeste sur la formulation Divergence F1-6 (l'appel de merge est effectué par l'opérateur, la CLI contrôle et gâte) ; la fiche Divergence le porte déjà, le manifeste non.

*Fin du jugement. Le juge ne merge rien, ne consigne pas de reçu R10, n'écrit pas au registre Nardole.*
