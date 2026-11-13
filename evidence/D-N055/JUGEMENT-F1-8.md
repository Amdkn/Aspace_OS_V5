# Jugement — D-N055 F1-8 : fonction Vision (PR #51)

**Fonction :** le 1 — fonction Juger, exercée en sous-agent borné (pas une session 13e séparée), le mécanisme codé (module `judge` + CLI `judge-pr`) étant l'outil de validation du jugement.
**Date du jugement :** 2026-11-13 ~03:18 EST (`2026-11-13T08:18:43Z`).
**PR jugée :** #51 — « D-N055 F1-8: Vision (le 1 tient registres et calendriers sans contradiction locale, par la fonction Vision) », tête `3328071c3467708bef078583bec6098b977ba66b`.
**Design jugé contre :** `plans/DESIGN-FONDATION-13-1-F1-8-PROJET.md`, SIGNÉ, journal 939 (D-F1-8-1..12, A-F1-8-1..6, P-F1-8-1..5).
**Méthode :** rejeu indépendant, rien pris sur parole. Clone frais, tête PR vérifiée à l'API avant bascule ; diff complet lu ; suite re-courue ; CLI re-courue sur les dossiers réels ; CI re-vérifiée à l'API au moment du jugement ; sources relues au fichier.

## Verdict : VALIDÉE AVEC RÉSERVES

**Recommandation merge : OUI, tel quel, sur la tête `3328071`.**
Aucun amendement. Le merge est **autorisé tel quel** sur la tête autorisée.
**Tête autorisée : `3328071c3467708bef078583bec6098b977ba66b`**
Merge en **true merge commit** (2 parents, DVG-01), jamais par le runner.

## État de la PR

- PR #51 **ouverte**, tête `3328071c3467708bef078583bec6098b977ba66b` (1 commit, parent unique `7feb8b0fc916750ee00eadc5c5801200dc8462cb` = master à l'ancre du design), base de la PR `78190d4d4c2a5389dd94266caaa57a670820d8a7` (master à l'ouverture, pulse 02:55 — 3 commits miroir après le parent ; le diff de la PR est la comparaison à trois points depuis la base de fusion `7feb8b0`, 14 fichiers +2972/−23).
- `mergeable: true`, `mergeable_state: clean`, 14 fichiers, **+2972/−23**.
- Commit tête : auteur « Aspace Factory », date `2026-11-13T08:01:54Z` (03:01:54 EST), PR créée `2026-11-13T08:02:11Z`.

## CI re-vérifiée

Check-runs re-vérifiés à l'API à 03:18 EST, sur la tête jugée, un à un, avec leur conclusion — jamais repris du dossier de livraison, jamais lus sur l'API legacy des statuts combinés. **8/8 success, 0 non-success** :

- Analyze (actions) : success
- CodeQL : success
- Deterministic Gate (5D Semantic AST + CAS Holons + 7R + OKF) : success
- S1-RICK & Reviewer-Security · OWASP Top 10 & Worktree Patch : success
- Verify Category 01_Kernel_Gates : success
- Verify Category 02_Holons_578_QualityControl : success
- Verify Category 03_Submodules_EGM_Harvester : success
- Verify Category 04_Security_OWASP_RigInfinity : success

## Diff lu

Diff complet lu (clone frais `~/workspace/v5-f1-8-juge`, jamais les fichiers de l'exécutant tels quels) ; table fichier par fichier, contenu vérifié : 14 fichiers, tous sous `00_Memoire/bundle/` ou `01_Forkable/FKB00_Runtime/00_A0_Core/fondation-13-1/` (code A'Space neuf). La comparaison est à trois points depuis la base de fusion `7feb8b0` — le diff à deux points depuis la base enregistrée `78190d4` compterait en plus les 3 commits miroir du pulse (10 insertions / 10 suppressions sur `00_Memoire/WORKGRAPH-MUSE.md`), qui ne font pas partie de la PR (O5).

| Fichier | Taille |
|---|---|
| `src/vision.rs` (nouveau, 826 lignes) | 32 929 o |
| `src/bin/hold-vision.rs` (nouveau, 1 145 lignes) | 47 304 o |
| `tests/vision.rs` (nouveau, 767 lignes) | 27 380 o |
| `tests/fixtures/vision-fautif-1.md` (nouveau, 12 lignes) | 574 o |
| `src/lib.rs` | +11 lignes (dont `pub mod vision;`) |
| `Cargo.toml` | +6 lignes (dont le binaire `hold-vision`, aucune dépendance) |
| `src/router.rs` | +9 lignes (`EVENT_TYPES` à 11 types, `vision_held` inclus) |
| `src/memory.rs` | +14 lignes (`JOURNAL_EVENT_TYPES` à 11 types) |
| `tests/router.rs` | +9 lignes (test des 11 types) |
| `tests/memory.rs` | +7 lignes (test des 11 types) |
| `fondation-13-1.manifest.json` | 1 ligne (surface + fonction Vision, `validated_by` corrigé) |
| `fondation-13-1-TELEMETRY-AUDIT.md` | +50 lignes (§ Vision) |
| `00_Memoire/bundle/concepts/fondation-13-1.md` | +136 lignes (§12 F1-8, §11/§1 corrigés, Divergence complétée) |
| `00_Memoire/bundle/log.md` | +1 ligne (Note F1-8, append-only) |

## Rejeu indépendant

**`cargo test` 123/123 PASS, 0 échec** — re-couru dans un clone frais, sur la tête vérifiée, chiffres re-comptés aux logs, sans reprendre les chiffres du producteur. Suite re-comptée : 10 lib + 7 discover + 13 execute + 11 judge + 24 memory + 17 R10 + 21 router + 20 vision = 123, 0 échec (F1-2/F1-3/F1-4/F1-5/F1-6/F1-7 en régression verte). Log : `~/workspace/v5-f1-8-scratch/suite-juge-f1-8.txt` (le log du producteur `suite-f1-8.txt` porte les mêmes comptes, 123/123).
CLI `hold-vision check` (binaire du clone frais) sur les dossiers réels, avec le master courant (`64dcd2940e69887ba2127ca653e29d73d1939051`, lu à l'API au moment du rejeu) et 1 PR ouverte injectés : T1 ACCEPTÉ V1–V8, sortie 0 (4 comparaisons) ; T2 ACCEPTÉ V1–V8, sortie 0 (2 seuils non franchis) ; T3 ACCEPTÉ V1–V8, sortie 0 (1 comparaison divergente-portée). CLI sur le fait F-V1 : REJET V3, sortie 2. Garde-fous F-V2/F-V3/F-V4 : rejets V2, V1, V4 par la suite (tests unitaires `f_v2`, `f_v3`, `f_v4`). Ancres relues au fichier par moi : registre lignes 938/930 (F1-7 CLOSE / F2 CLOSE), journal seq 37 (merge F1-7, `055745b`, 01:47:15-05:00), reçu G-20261112-035 (sha `055745b853495c38f0aaa0ae6c3d2adad9e89177`), L00 Run #702, N2 Run #484, miroir Bill présent. Sorties CLI du producteur (`cli-t1.txt`, `cli-t2.txt`, `cli-t3.txt`, `cli-fautif-1.txt`) identiques à mes rejeux, à la dérive près : master `78190d4` → `64dcd29`, 0 → 1 PR ouverte, journal 37 → 46 lignes, mtimes, chemins `v5-f1-8` vs `v5-f1-8-juge` (O1 : deux libellés périmés dans mon rejeu, voir Écarts).

## Lecture de la fonction jugée

Le module `vision` lu en entier (826 lignes, 32 929 o) — ordre V1 → V6 → V2 → V3 → V4 → V7 → V5 → V8 conforme au design ; V1 exige source exacte + horodatage ISO avec offset, jamais dans le futur ; V6 refuse toute résolution, toute modification de source et toute consignation de reçu ; V2 exige les deux valeurs et l'existence du seq cité (dernier seq connu) ; V3 exige l'ancre nommant le dispatch, le seuil = ancre + 12 h, et la cohérence du franchissement avec l'instant ; V4 exige chaque divergence connue portée avec statut valide et source, et rejette le lissage (comparaison cohérente qui recouvre une divergence portée) ; V7 exige chaque absence connue consignée ; V5 est le filet (un seuil porté égal au fait fautif planté) ; V8 exige des limites nommées et refuse la complétude affirmée. Normalisation des fuseaux (D-F1-8-11) : ISO avec offset, mural EST/EDT, étiquette « EDT » après 2026-11-01 périmée (instant vrai une heure plus tôt, EST). La fonction ne contacte ni le fichier local ni l'API (lectures, comparaisons, divergences et fait fautif injectés par l'appelant) ; `JOURNAL_EVENT_TYPES` compte 11 types, `vision_held` inclus (A-F1-8-3), identique à `router::EVENT_TYPES` (tests `onze_types_dont_vision_held`). Zéro dépendance externe, zéro appel sortant dans le code.
La CLI `hold-vision` lue en entier (1 145 lignes, 47 304 o) — 9 lectures au fichier local nommées (R1–R9) + 1 reçu + 1 dossier fautif quand il est donné, comptées et tracées ; re-lecture des ancres au fichier (registre lignes 938/930, journal seq 37, reçu 035, L00 #702, N2 #484) avec échec nommé si l'ancre ne correspond plus ; normalisation des fuseaux ; master et PR ouvertes injectés par l'opérateur (vérifiés à l'API) ; Sheet citée du Discover (02:13:32 EST), limite nommée V8. La CLI ne lit que des fichiers locaux et n'écrit que sur stdout/stderr ; 0 recherche sémantique (A-F1-8-5). Limite lue : les ancres de livraison sont codées en dur (lignes 938/930, seq 37, reçu 035, Run #702/#484) et deux libellés le sont aussi — voir O1/R4.

## Tableau des hold-outs

| Hold-out | Verdict | Preuve (rejeu indépendant) |
|---|---|---|
| H-F1-7 — Preuve du pas | VERT | 3/3 rendus par la CLI avec lectures datées et comparaisons rejouables (T1 cohérence F1-7, T2 seuils non franchis, T3 divergence classée), fait F-V1 rejeté V3, cas limites §5.4 (a)–(f) traités (suite 20/20) ; états rendus comme événements `vision_held` seq 43–45 ; premier `correction` seq 46 ; merge de la PR du pas À VENIR (E7 par un tiers + reçu après merge) ; second état à l'instant du merge (R4 : libellés codés en dur à noter) |
| H-M1 — Mesure zéro nommée | VERT | Registre 939 lignes (dernière ligne lue : journal 939, design F1-8 SIGNÉ, reçu 036) ; journal-router 46 lignes seq 1–46 contigus (37 au rendu, 9 événements F1-8 ajoutés) ; L00 85 lignes, Run #702 lu ; N2 495 lignes, Run #484 lu ; master base `7feb8b0`, PR base `78190d4`, master lu `64dcd29` au rejeu ; design 55 874 o / 194 lignes, sha256 `d2fe2130…` ; Discover 56 972 o / 287 lignes, sha256 `b4584760…` |
| H-M2 — Aucun paquet amont modifié | VERT | Diff = 14 fichiers A'Space neufs, 0 dépendance |
| H-M3 — Suite verte | VERT | Suite 123/123 re-courue, cas passants + 4 faits rejetés avec leur raison nommée + cas limites (a)–(f) + cas de forme |
| H-M4 — Télémétrie zéro | VERT | 0 appel sortant dans le code, audit joint (§ Vision) ; CLI : lectures au fichier local nommées, comptées et tracées, 0 appel réseau, 0 recherche sémantique |
| H-M5 — Manifeste | VERT | Fonction Vision nommée, adresse `fiber:a0:fondation-13-1` ; `validated_by` corrigé (F1-7 VALIDÉE, PR #50 mergée `055745b`, jugement journal 938) |
| H-M6 — Frontière | VERT | Seul le code A'Space de la fonction Vision ; section Divergence de la fiche remplie |
| H-M7 — Fiche versionnée | VERT | Fiche mise à jour, §12 F1-8 consigné, §11/§1 corrigés |
| H-F8-9 — Plafonds | NON MESURÉ (voir R1) | Plafonds 1 % / 5 % / 20 % — mesure à la comptabilité du fournisseur, consignée dans le reçu du pas ; le juge ne mesure pas les tokens depuis ce poste |

## Écarts et observations

Aucun écart bloquant. Aucun amendement. Sept observations (O1–O7) :

- **O1** — Ancres de livraison codées en dur dans la CLI (lignes 938/930, seq 37, reçu 035, Run #702/#484) — et deux libellés avec elles : la lecture journal porte la source « (seq 37) » alors que sa valeur suit le dernier événement (seq 46, `correction`, à mon rejeu), et la comparaison T1 « PR ouvertes » porte à droite « 0 PR ouverte » en dur alors que la gauche dit « 1 PR ouverte(s) » à mon rejeu. Au rendu (03:00) les deux étaient exacts (37 lignes, 0 PR ouverte) ; à mon rejeu ils sont périmés, et la fonction ne les détecte pas (V2 vérifie la présence des deux valeurs, pas leur accord). Non bloquant pour ce merge — le dossier de preuve du rendu est exact — mais le second état, à l'instant du merge, portera les mêmes libellés périmés : à noter dans son dossier (R4).
- **O2** — Commentaire `memory.rs` : « les 10 du routeur » — le routeur en compte 11 depuis ce pas (`vision_held`). Le code (tableau à 11 entrées) est exact ; le commentaire est périmé d'un. Non bloquant.
- **O3** — Fiche §12 : le résumé T1 cite le master `7feb8b0` (valeur du cas de test, 02:40) alors que l'état rendu à 03:00 lisait `78190d4`. Le dossier de preuve (`VISION-F1-8.md`) est exact ; la fiche confond la valeur du test et celle du rendu. Non bloquant.
- **O4** — Suivi F1-7 R3 toujours ouvert : le `note_code` du manifeste attribue encore l'appel de merge à la CLI (« CLI `execute-merge` : 1 appel en écriture d'état ») alors que la Divergence F1-6 dit que l'appel est effectué par l'opérateur. Suivi hors PR (R3).
- **O5** — Parent de la tête (`7feb8b0`) antérieur à la base enregistrée (`78190d4`) de 3 commits miroir du pulse : le diff de la PR est la comparaison à trois points depuis la base de fusion `7feb8b0` (14 fichiers, +2972/−23, identique à l'API) ; le diff à deux points depuis `78190d4` compterait en plus le miroir, qui n'est pas la PR. Non bloquant ; le merge sera un vrai merge sur la tête courante.
- **O6** — Un exec du coordinateur d'exécution a échoué (exit 1, commande inconnue, signalé par le principal). Ma re-vérification indépendante n'a trouvé aucun défaut attribuable : suite 123/123, CLI 4/4, ancres relues, CI 8/8. Non bloquant.
- **O7** — L00/N2 ont avancé depuis le rendu (L00 85 lignes, N2 495 lignes) : la CLI relit au fichier à chaque rendu ; les ancres du pas (938/930, seq 37, reçu 035) sont inchangées. Non bloquant.

## Conformité au design

D-F1-8-1..12 adoptées (design §9) ; fait fautif planté = F-V1, fichier distinct, une seule différence sur l'ancre, rejet V3 (A-F1-8-1) ; faits F-V2/F-V3/F-V4 = une seule différence chacun, rejets V2/V1/V4 (A-F1-8-2) ; `vision_held` légalisé 11e type, premier `correction` émis à la livraison (A-F1-8-3) ; fenêtre observée du pas, deux états datés, semaine par F1-11 (A-F1-8-4) ; module pur + CLI lectrice, 0 recherche sémantique (A-F1-8-5) ; acte triple borné aux 3 cas d'essai, seconde vision systématique par la session 13e exclue (A-F1-8-6) ; missions 016/017 et entry_id 037/038 proposés, assignation au dépôt (P-F1-8-1) ; domicile du code nommé (P-F1-8-2) ; ordre d'exécution tenu (P-F1-8-3) ; aucune exclusion ne couvre le fait F-V1 (P-F1-8-4) ; re-mesure à l'exécution (P-F1-8-5). Second jugement systématique par la session 13e exclu (D-F1-8-6) ; jugement rendu comme événement `judgment_rendered` (prochain seq 47, par le routeur) ; la vision ne tranche pas (V6).

## Fautif planté (J6)

Fait F-V1 (ancre journal 938 pour D-N053) : REJET V3 par la CLI hold-vision (sortie 2) — le journal 938 nomme D-N055, pas D-N053 — l'ancre est fausse ; le dernier événement nommant D-N053 est le journal 930, ~21:00, seuil ~09:00, non franchi. Les garde-fous F-V2/F-V3/F-V4 sont rejetés V2, V1 et V4.

## Ce que le juge n'a pas fait

Aucun reçu consigné par ce jugement, aucune PR mergée par ce jugement, rien écrit au registre par ce jugement, aucune modification de la PR. Le juge juge, il n'exécute pas.

## Ce que ce jugement ne prouve pas

Le merge reste à exécuter puis à vérifier 2 parents à l'API (E7, par un tiers) ; le second état de vision, à l'instant du merge, reste à rendre (R4) ; le reçu H-F1-7 vient après, par un exécutant dédié ; les plafonds H-F8-9 ne sont pas mesurés par ce jugement ; la montée en périmètre (tenir n'importe quel registre) est hors de ce pas.

## Réserves

- **R1** — Mesure tokens du pas non mesurable depuis ce poste (H-F8-9, plafonds 1 % / 5 % / 20 %) : suivi hors PR, pour le reçu du merge.
- **R2** — Le reçu H-F1-7 du merge de la PR #51 (038 proposé, mission `LE1-FAB-D-N055-017`) vient après le merge, par un exécutant dédié. Le reçu de livraison 037 est proposé (mission `LE1-FAB-D-N055-016`) ; le design a pris 036 pour lui-même (journal 939, commit `501d95b`).
- **R3** — Suivi hors PR (O4) : aligner le `note_code` du manifeste sur la formulation Divergence F1-6 (l'appel de merge est effectué par l'opérateur, la CLI contrôle et gâte) ; la fiche Divergence le porte déjà, le manifeste non.
- **R4** — Ancres de livraison codées en dur dans la CLI (O1) : le second état de vision, à l'instant du merge, portera les libellés « (seq 37) » et « 0 PR ouverte » périmés — l'exécutant les note comme tels dans le dossier du second état, ou la CLI est paramétrée avant ce rendu ; la généralisation (ancres paramétrées, pas codées) est due au plus tard pour F1-11, qui répète la vision sur 7 jours.

*Fin du jugement. Le juge ne merge rien, ne consigne pas de reçu R10, n'écrit pas au registre Nardole.*
