---
type: Architecture
title: "Fondation 13 → 1 : unifier les 13 sessions en 1 agent (D-N055)"
tags: [fondation, 13-1, unification, daemon, riginfinity, journal, juge-interne, rollback]
---
# Fondation 13 → 1 : unifier les 13 sessions en 1 agent (D-N055)

**Design signé Clara :** `FONDATION-13-1-plan-borne.md` (32 561 o, ~23:03 EST, 2026-11-10).
**Ordre S0 :** GO Fondation 13 → 1, « let's Fucking Go », 21:56 EST — documentation après,
pour correction et alignement par orientation. Pas de question de clarification avant
la première action concrète agentique.
**Dispatch :** D-N055, typé par Nardole (journal 774, ligne de table 119).
**Statut :** F1-0 livré (inventaire, PR V5 #23) ; F1-1 clos (BYB accepté, journal 787) ; F1-2 clos (PR #26 mergée `1f89b56`, reçu H-F1-5 G-20261111-006) ; F1-3 clos (PR #30 mergée `4668305`, reçu H-F1-4 G-20261111-016, journal 814) ; F1-4 clos (PR #44 mergée `573cad4`, reçu H-F1-1 G-20261112-021, journal 926) ; F1-5 clos (PR #47 mergée `4a68288`, reçu H-F1-2 G-20261112-029, journal 933) ; F1-6 clos (PR #49 mergée `e2e9c14`, reçu H-F1-3 G-20261112-032, journal 936) ; F1-7 clos (PR #50 mergée `055745b`, reçu H-F1-6 G-20261112-035, journal 938) ; F1-8 PR ouverte, non mergée (ce pas).

## 1. Mesure zéro (H-M1)

- **13 sessions** nommées par Clara (`chat.list`, ~22:53 EST) : Rick `2428b187`, 13e `a517ae1d`,
  11e `6f410ddd-4ef8-4834-805a-0b38ede9ba76` (ID complet établi F1-7 T3, source `~/memory/2026-10-09.md:146`), 12e `7489b6f0`, Yaz `e1ac3b2d`, Ryan `a152c901`,
  Bill `500abaec`, Clara `ef2544e6`, Nardole `ae7d36d1`, Rory `5dba06d6`, Amy `337fb65c`,
  River `dfd97c8e`, Graham `059b0c23`.
- **Registre Nardole : 776 lignes** à l'instantané F1-0 (2026-11-11T00:15:56-05:00).
  89 lignes sur 124 dans la fenêtre de la soirée contiennent « déjà traité » ou
  « pas de double-envoi » (72 %) — le coût de coordination est le travail.
- **Workgraph :** Sheet `1OFRYjujs81fPSS4HJWrB4M9yeduQAd35UVvaXBiHXrI` + miroir (26 lignes).
- **Ledger R10 :** 7 branches `work-dn*-ledger`, 247 fichiers, 212 reçus.
- **Inventaire F1-0 : 2 252 entrées typées** — `bundle/fondation-13-1/journal-inventaire.jsonl`
  (+ `INVENTAIRE-F1-0.md`, harnais 6/6 PASS, `RESULTS-F1-0.json`).
  7 mémoires présentes / 13 (6 absentes, consignées) ; mémoire partagée 88 entrées.

## 2. Les 13 fonctions (mapping D2)

Le « 1 » est **un lead avec un juge interne** (A siège = main A0 ; B corps = daemon
unique RigInfinity + harness Muse ; C mécanisme = sous-agents bornés à la demande,
refermés après usage). Une fonction reste distincte quand elle est une vérification
(juger, vérifier, décider, recevoir) ou une écriture concurrente (exécuter,
fabriquer) — jamais quand elle est une coordination (router, fluer) ou une capacité
du lead (structurer, découvrir, observer, interfacer, mémoriser).

| Fonction | Session d'origine | Dans le 1 |
|---|---|---|
| Structurer | Rick (S1) | capacité interne du lead |
| Juger | Doctors (S2) | **fonction de jugement séparée** (contexte propre, priors différents, artefact + objectif sans la conclusion du producteur, vérifications déterministes en outils) |
| Exécuter | Compagnons (S3) | sous-agents bornés, refermés après usage, écritures mono-threadées |
| Router | Nardole | **événement interne** (dispatch, accusé, pulsation = événements du journal) |
| Recevoir | Graham | ledger R10 comme donnée du changeset |
| Vérifier | Rory | vérifications déterministes appelées comme des outils (DVG-01, checks API) |
| Décider | Clara | **autorité de design unique, interne** (le design signé autorise l'exécution) |
| Découvrir | Bill | capacité interne du lead |
| Observer | Yaz | watchlist + heartbeat du daemon |
| Interfacer | Amy | surface du 1 (les canaux parlent à une seule session) |
| Fluer | River | flux des événements (le journal porte la continuité) |
| Mémoriser | Graham | **mémoire unique** (journal d'événements + fichiers de mémoire partagés) |
| Fabriquer | Ryan | sous-agent exécutant borné (merge, portage, dépôt — puis refermé) |

## 3. Réponse à §D5 — qui juge le juge

Le juge est une **fonction de jugement séparée à l'intérieur du 1** : contexte propre
(artefact + objectif, jamais la transcription du producteur), priors différents
(instruit pour chercher l'échec), artefact + objectif sans la conclusion du
producteur, vérifications déterministes en outils (DVG-01, checks CI re-vérifiés
au HEAD, suites par la commande du daemon, reçus lus au fichier). Le journal
d'événements rejouable est le dossier du jugement.

Trois filets, ordonnés : (a) **la faute plantée (H-F1-2)** — le design plante un
artefact fautif, le juge doit le rejeter, sinon la fonction revient à sa session
d'origine (le 13e) ; (b) **la vérification post-merge (H-02-A1)** — checks CI +
reçus ; (c) **le Capitaine comme arbitre de dernier ressort** (ses codes
d'exception). La session 13e est **gardée dormante** comme réserve, réveillée
seulement si le juge interne échoue. Ce que le champ ne prouve pas (porté
honnêtement) : aucune source ne démontre qu'un agent unique puisse être son
propre juge sans perdre la vérification — d'où trois filets, pas un seul.

## 4. Dette de divergence

- **Manifeste daemon (H-M5) — PARTIELLEMENT LEVÉ à F1-2 :** le manifeste du
  module est posé (`01_Forkable/FKB00_Runtime/00_A0_Core/fondation-13-1.manifest.json`,
  adresse `fiber:a0:fondation-13-1`, fonction Recevoir nommée, état 1).
  Réserve : le manifeste du daemon lui-même vit dans RigInfinity, pas dans
  V5 — son inscription là-bas reste due (hors de ce pas, le daemon n'est
  pas dans ce repo).
- **6 mémoires absentes :** 13e, 11e, Clara, Nardole, Rory, River — aucun fichier
  `MEMORY.md` dans leurs chats à l'instantané. Consignées comme absences ; si
  elles apparaissent, F1-7 les re-typifie.
- **ID 11e établi (correction portée en avant, D-F1-7-12a) :** l'ID complet est
  `6f410ddd-4ef8-4834-805a-0b38ede9ba76` — source `~/memory/2026-10-09.md:146`,
  vérifiée au `grep` ce tour, miroir `~/memory/bank/reflections.md`. La mention
  « ID complet non établi » est réfutée ; la fiche §4 et le plan §0 (qui ne
  donnent que `6f410ddd`) sont corrigés par cet amendement porté en avant.
- **Résiduels :** 38 têtes de journal « événement » + 226 puces « fait (défaut) »
  — comptés à part, textes et preuves conservés.
- **Registre vivant :** l'inventaire est un instantané (776 lignes, 00:15:56 EST) ;
  le registre continue de croître. La re-compilation liste les deltas par sha.

## 5. Contraintes (§2 du design)

- **Plafonds (§D9) :** 1 % la Fondation (55 M tokens), 5 % par pas (275 M),
  20 % mission-wide (1,1 Md) sur le pool de 5,5 Md restants. Arrêt dur à 20 %.
- **Calendrier :** 1 jour maximum par pas, 12 jours maximum (F1-0 → F1-11).
- **Séquence :** F1-0 inventaire → F1-1 structurer (première preuve partielle) →
  F1-2 recevoir → F1-3 router → F1-4 découvrir → F1-5 juger → F1-6 exécuter →
  F1-7 mémoire unifiée → F1-8 vision → F1-9 action → F1-10 rollback → F1-11 preuve finale.
  Un pas ne commence que quand le précédent est vert — sauf ordre S0.
- **Rollback (§D8) :** si un hold-out échoue, le 1 s'arrête sur la fonction concernée
  et la chaîne 13 reprend cette fonction — les sessions ne sont pas démantelées tant
  que le 1 n'est pas prouvé sur les 13 fonctions (H-F1-9).
- **Discipline préservée (§0.6) :** DVG-01, R10, hold-outs écrits avant exécution,
  saisine explicite au 13e à chaque livraison, true merge commit (2 parents),
  « documenté vs vérifié », `enforce_admins` reste false.
- **Codes d'exception (§D7) :** Code Rouge → fonction de jugement ; Code Noir
  Profond → fonctions d'exécution ; Code Jaune → fonction de structuration.
  Le Capitaine ne parle qu'à son Jumeau Numérique A0 (Main) — le 1 EST ce Main.
- **Ce qui ne change pas sans son mot explicite :** le démantèlement de la structure
  elle-même (correction du Capitaine, 2026-11-10 ~13:11 EST) ; la bascule plus rapide
  qu'une fonction à la fois (arbitrage vision, via Rick → A0).

## 6. F1-2 — Recevoir (PR #26 mergée `1f89b56`)

**Design signé :** `plans/DESIGN-FONDATION-13-1-F1-2-PROJET.md` (fonction de
design interne, journal 790, 2026-11-11 ~01:01 EST). Décisions D-F1-2-1..6,
amendements A-F1-2-1 / A-F1-2-2, précisions P-F1-2-1..3.

**Domicile du code :** `01_Forkable/FKB00_Runtime/00_A0_Core/fondation-13-1/`
(crate `fondation-13-1`, lib `r10_validator`, binaire `r10-receive`) ;
manifeste `00_A0_Core/fondation-13-1.manifest.json` (adresse
`fiber:a0:fondation-13-1`) ; audit télémétrie
`00_A0_Core/fondation-13-1-TELEMETRY-AUDIT.md`.

**Ce qui est livré :** le validateur R10 v1 (V1–V8, ordre V1 → V8 → V7 →
V2 → V3 → V4 → V5 → V6 ; rejet motivé, jamais de correction silencieuse)
+ le consignateur (`recorded_at` posé à la consignation depuis l'horloge
système, jamais repris du dépôt — D-F1-2-1) + la CLI `r10-receive`
(`validate` / `consign`).

**Suite H-M3 — VERTE :** `cargo test` — 20 tests, 0 échec (3 unitaires lib +
17 d'intégration) : cas passants = dépôts 001/002/026 rejoués (doivent
passer) ; cas rejetés = les 4 fautifs du Discover §6 (raisons nommées :
V3 SHA court, V4 observed_at non ISO, V5 proof[] vide, V7+V2 réécriture
de 002). Log : `v4-factory/evidence/D-N055/harness-F1-2.log`.

**Dépôt fautif planté (D-F1-2-6, amendement A-F1-2-1) :** fautif n° 1 (SHA
court `22f374d`, entry_id `G-20261111-901` + mission_id
`TEST-F1-2-FAUTIF-1` frais) — planté à
`v4-factory/evidence/D-N055/DEPOT-FAUTIF-1.json` et en fixture de la suite.
Rejet vérifié par la CLI : `REJET V3 — champ 'sha', valeur reçue '22f374d'
: SHA court ou mal formé — fournir le SHA complet (40 caractères
[0-9a-f])` (sortie 2). Le garde-fou V7+V2 est vérifié aussi par la CLI
(001 rejoué contre le ledger complet → V7, V2 nommé aussi).

**Mesure H-M1 re-mesurée à l'exécution** (base F1-0 : 37 reçus numérotés /
212 fichiers) : 8 branches `work-dn*-ledger`, 281 fichiers / 241 reçus
(sommes par branche), 66 reçus uniques, 41 numérotés (G-20261109-001..011
+ G-20261110-001..026 + G-20261111-001..004). L'état a bougé depuis F1-0
(003/004 consignés sur `work-dn052-ledger`) — la base F1-0 est inchangée,
c'est l'état courant qui est consigné ici.

**Hold-outs F1-2 :** H-M1 mesuré (ci-dessus) ; H-M2 diff vide sur l'amont
(code A'Space neuf) ; H-M3 suite verte (ci-dessus) ; H-M4 télémétrie zéro
(audit joint, 0 dépendance, 0 appel sortant) ; H-M5 partiellement levé
(manifeste du module posé — voir §4) ; H-M6 frontière (seul le code A'Space
du validateur ; voir Divergence) ; H-M7 cette fiche. H-F1-5 = le reçu du
merge qui clôt F1-2 (mission `LE1-FAB-D-N055-004`) — **après le merge,
par un exécutant dédié, pas dans ce pas**. Le reçu de livraison de la PR
(mission `LE1-FAB-D-N055-003`) est préparé dans
`v4-factory/evidence/D-N055/RESULTS-F1-2.json` — **non consigné au ledger
par ce pas** (le coordinateur consigne).

## 7. F1-3 — Router (PR #30 mergée `4668305`)

**Correction portée en avant :** l'en-tête de cette section disait « PR
ouverte, non mergée » — la PR #30 a été mergée `4668305` (2 parents,
DVG-01, reçu H-F1-4 G-20261111-016, journal 814). La fiche n'est pas
réécrite : la correction est portée ici.

**Design signé :** `plans/DESIGN-FONDATION-13-1-F1-3-PROJET.md` (fonction de
design interne, journal 806, 2026-11-11 ~01:53 EST). Décisions D-F1-3-1..6,
amendements A-F1-3-1 / A-F1-3-2, précisions P-F1-3-1..3.

**Domicile du code :** `01_Forkable/FKB00_Runtime/00_A0_Core/fondation-13-1/`
(crate `fondation-13-1` v0.2.0, lib `r10_validator`, module `router`,
binaire `route-dispatch`) ; manifeste
`00_A0_Core/fondation-13-1.manifest.json` (adresse `fiber:a0:fondation-13-1`,
fonctions Recevoir + Router nommées) ; audit télémétrie
`00_A0_Core/fondation-13-1-TELEMETRY-AUDIT.md` (§ Router ajouté).

**Ce qui est livré :** le routeur (R1–R8, ordre R1 → R2 → R3 → R4 → R5 →
R6 → R7 → R8 ; rejet motivé, jamais de correction silencieuse, jamais de
routage quand même) + l'inscripteur (`seq` = numéro de ligne, append-only)
+ le relais comme événement lu par la destinataire + la CLI
`route-dispatch` (`validate` / `type` / `relay` / `ack` / `pulse` /
`request-judgment` / `render-judgment`).

**Suite H-M3 — VERTE :** `cargo test` — 44 tests, 0 échec (7 unitaires lib +
17 d'intégration R10 + 20 d'intégration router) : cas passants = un dispatch
valide typé, relayé, accusé ; demande de jugement puis jugement rendu ;
relais après demande de jugement (correction R8) ; pulsation ; correction
référençant un événement existant ; cas rejetés =
les 5 fautifs du Discover §6 (raisons nommées : R2 sans design signé, R3
double-envoi, R4 destinataire = session, R5 `at` non ISO, R8 ack sans
typed) + relais sans acte préalable (R8). Log :
`v4-factory/evidence/D-N055/harness-F1-3.log`. Les 20 tests
F1-2 restent verts (régression : 0 échec).

**Dispatch fautif planté (D-F1-3-6, amendement A-F1-3-1) :** fautif n° 1
(sans design signé, `design_ref` vide, `dispatch_id`
`D-N055-F1-3-FAUTIF-1` + `event_id` `EVT-20261111-901` frais) — planté à
`v4-factory/evidence/D-N055/DISPATCH-FAUTIF-1.json` et en fixture de la
suite. Rejet vérifié par la CLI : `REJET R2 — champ 'design_ref' : aucun
design signé référencé — un dispatch sans design signé n'est jamais routé`
(sortie 2). Le garde-fou R4 est vérifié aussi (destinataire `Nardole` →
R4, `actor_to`).

**Mesure H-M1 re-mesurée à l'exécution** (base du Discover : registre 805
lignes) : registre 806 lignes (design F1-3 signé, journal 806) ; master
`29f52e9` (pulse Workgraph 01:53, parent `1947fab` — la base de la branche
`a0/f1-3-router` reste `1947fab`, mergeable) ; F1-2 clos (PR #26,
`1f89b56`, reçu 006).

**Correction portée en avant (R8) :** le Discover §4 et le design §3
disent « le relais suit le typage ». En usage réel, le routeur a rejeté
(R8, sortie 2) le relais de la demande de jugement — parce qu'une demande
de jugement (`judgment_requested`) est elle-même un acte de création de
dispatch, pas un `dispatch_typed`. La règle est corrigée : le relais suit
tout acte de création — `dispatch_typed` OU `judgment_requested` ; l'accusé
suit seulement le typage d'un dispatch de livraison. Le rejet R8 en direct
est conservé comme preuve que le routeur applique la règle (il a rejeté
avant la correction, pas après). Le design signé n'est pas réécrit : la
correction est portée en avant ici et dans le reçu de livraison 015.

**Correction portée en avant (R1) :** le Discover §4 et le design §3
disent « le dispatch porte exactement les 10 clés » — c'est l'ÉVÉNEMENT
inscrit qui porte 10 clés. Le dispatch soumis en porte 9 : `seq` est
assigné par le routeur à l'inscription (le numéro de séquence est le
numéro de ligne, il ne peut pas être dans la soumission). Le code
implémente R1 = 9 clés pour le dispatch ; une soumission portant `seq`
est rejetée R1 (clé inconnue — test `seq_soumis_rejete_r1`). Le design
signé n'est pas réécrit : la correction est portée en avant ici et dans
le reçu de livraison 015.

**Hold-outs F1-3 :** H-M1 mesuré (ci-dessus) ; H-M2 diff vide sur l'amont
(code A'Space neuf) ; H-M3 suite verte (ci-dessus) ; H-M4 télémétrie zéro
(audit joint, 0 dépendance, 0 appel sortant) ; H-M5 levé au niveau du
module (fonctions Recevoir + Router nommées dans le manifeste — le
manifeste du daemon RigInfinity reste dû, voir §4) ; H-M6 frontière (seul
le code A'Space du routeur ; voir Divergence) ; H-M7 cette fiche. H-F1-4
= le reçu du merge qui clôt F1-3 (mission `LE1-FAB-D-N055-006`) — **après
le merge, par un exécutant dédié, pas dans ce pas**. Le reçu de livraison
de la PR (mission `LE1-FAB-D-N055-005`) est préparé dans
`v4-factory/evidence/D-N055/RESULTS-F1-3.json` — **non consigné au ledger
par ce pas** (le coordinateur consigne).

## 8. F1-4 — Découvrir (PR #44 mergée `573cad4`)

**Correction portée en avant :** l'en-tête de cette section disait « PR
ouverte, non mergée » — la PR #44 a été mergée `573cad4` (2 parents,
DVG-01, reçu H-F1-1 G-20261112-021, journal 926). La fiche n'est pas
réécrite : la correction est portée ici.

**Design signé :** `plans/DESIGN-FONDATION-13-1-F1-4-PROJET.md` (fonction de
design interne, journal 923, 2026-11-12 ~14:10 EST). Décisions D-F1-4-1..6,
amendements A-F1-4-1 / A-F1-4-2 / A-F1-4-3, précisions P-F1-4-1..3.

**Domicile du code :** `01_Forkable/FKB00_Runtime/00_A0_Core/fondation-13-1/`
(crate `fondation-13-1` v0.2.0, lib `r10_validator`, module `discover`,
binaire `validate-discover`) ; manifeste
`00_A0_Core/fondation-13-1.manifest.json` (adresse `fiber:a0:fondation-13-1`,
fonctions Recevoir + Router + Découvrir nommées) ; audit télémétrie
`00_A0_Core/fondation-13-1-TELEMETRY-AUDIT.md` (§ Découvrir ajouté).

**Ce qui est livré :** la fonction Découvrir (D1–D8, ordre D1 → D4 → D5 →
D7 → D2 → D3 → D6 → D8 ; rejet motivé, jamais de correction silencieuse)
+ la CLI `validate-discover` (`check` : contrôle de recevabilité d'un
fichier Discover ; les contrôles D2/D3/D7 appellent les lectures au fichier
et à l'API par l'opérateur — les SHA qui résolvent sont injectés, même
frontière que le validateur R10).

**Suite H-M3 — VERTE :** `cargo test` — 51 tests, 0 échec (7 unitaires lib +
7 d'intégration discover + 17 d'intégration R10 + 20 d'intégration router) :
cas passant = ce Discover-ci (`discover-f1-4.md`, copie byte-identique de
`evidence/D-N055/DISCOVER-F1-4.md`, doit passer D1–D8) ; cas rejetés =
les 5 fautifs du Discover §6, dérivés chacun par UNE SEULE différence
(raisons nommées : D2 fait non vérifié, D4 décision tranchée, D7 source
citée non lue, D6 correction silencieuse, D5 exécution déguisée) — dont le
Discover fautif planté n° 1. Log :
`v4-factory/evidence/D-N055/harness-F1-4.log`. Les 44 tests F1-2/F1-3
restent verts (régression : 0 échec).

**Discover fautif planté (D-F1-4-4, amendement A-F1-4-1) :** fautif n° 1
(fait non vérifié — le merge de la PR #30 affirmé sans ancre, repris du
récit de l'exécutant F1-3) — planté à
`v4-factory/evidence/D-N055/DISCOVER-FAUTIF-1.md` (une seule différence,
ligne 45) et dérivé en suite. Rejet vérifié par la CLI : `REJET D2 —
champ 'ancre' : le merge de la PR #30 est affirmé sans ancre — ni SHA
complet du merge, ni vérification à l'API` (sortie 2). Les garde-fous D4,
D7, D6 et D5 sont vérifiés aussi par la CLI (fautifs n° 2, 3, 4, 5 →
rejets D4, D7, D6, D5, sortie 2).

**Re-validation de ce Discover-ci par la fonction (étape 4) :** la CLI
`validate-discover check` sur `DISCOVER-F1-4.md` — **ACCEPTÉ, D1–D8
passés (3 SHA complets vérifiés)**, en accord avec l'acceptation consignée
au design §9. Le hold-out H-F1-1 (variante) ne brise pas ici : la fonction
écrite après re-valide ce Discover avec le même verdict que l'acceptation
indépendante.

**Mesure H-M1 re-mesurée à l'exécution** (base du Discover : registre 922
lignes, 185 lignes « Bill », 198 « découvrir »/« discover », 3 occurrences
« F1-4 ») : registre 924 lignes (design F1-4 signé, journal 923) ; 186
lignes « Bill », 200 « découvrir »/« discover », 4 occurrences « F1-4 » ;
master `96d64ce` (tête vérifiée à l'API, base de la branche
`a0/f1-4-discover`) ; F1-3 clos (PR #30, `4668305`, reçu 016).

**Correction portée en avant (D7) :** la première version du contrôle D7
acceptait « non lu en entier » comme attestation, parce que la chaîne
contient « lu en entier » — le fautif n° 3 passait la suite. Le contrôle
exige désormais l'attestation positive : une ligne « non lu en entier »
n'atteste rien (leçon §0.4.5.1). La correction est portée ici et dans le
reçu de livraison 020 ; le design signé n'est pas réécrit.

**Hold-outs F1-4 :** H-M1 mesuré (ci-dessus) ; H-M2 diff vide sur l'amont
(code A'Space neuf) ; H-M3 suite verte (ci-dessus) ; H-M4 télémétrie zéro
(audit joint, 0 dépendance, 0 appel sortant) ; H-M5 levé au niveau du
module (fonctions Recevoir + Router + Découvrir nommées dans le manifeste
— le manifeste du daemon RigInfinity reste dû, voir §4) ; H-M6 frontière
(seul le code A'Space de la fonction Découvrir ; voir Divergence) ; H-M7
cette fiche. H-F1-1 (variante) = le reçu du merge qui clôt F1-4 (mission
`LE1-FAB-D-N055-008`) — **après le merge, par un exécutant dédié, pas dans
ce pas**. Le reçu de livraison de la PR (mission `LE1-FAB-D-N055-007`,
entry_id `G-20261112-020`) est consigné à l'ouverture de la PR — voir
`v4-factory/evidence/D-N055/RESULTS-F1-4.json`.

## 9. F1-5 — Juger (PR #47 mergée `4a68288`, journal 933)

**Design signé :** `plans/DESIGN-FONDATION-13-1-F1-5-PROJET.md` (fonction de
design interne, journal 931, 2026-11-12 ~21:24 EST). Décisions D-F1-5-1..9,
amendements A-F1-5-1 / A-F1-5-2 / A-F1-5-3 / A-F1-5-4, précisions P-F1-5-1..5.

**Domicile du code :** `01_Forkable/FKB00_Runtime/00_A0_Core/fondation-13-1/`
(crate `fondation-13-1` v0.2.0, lib `r10_validator`, module `judge`,
binaire `judge-pr`) ; manifeste
`00_A0_Core/fondation-13-1.manifest.json` (adresse `fiber:a0:fondation-13-1`,
fonctions Recevoir + Router + Découvrir + Juger nommées) ; audit télémétrie
`00_A0_Core/fondation-13-1-TELEMETRY-AUDIT.md` (§ Juger ajouté).

**Ce qui est livré :** la fonction Juger (J1–J8, ordre J1 → J7 → J2 → J5 →
J3 → J4 → J6 → J8 ; rejet motivé, jamais de correction silencieuse) + la
CLI `judge-pr` (`check` : jugement d'une PR — les contrôles J1/J7/J2/J5
sont structurels et locaux au dossier ; J3/J4/J6 appellent les lectures à
l'API et le rejeu par l'opérateur — SHA, CI et suite injectés, même
frontière que le validateur R10). La fonction EST le jugement (D-F1-5-5) :
pas de contrôle de recevabilité séparé avant le merge.

**Suite H-M3 — VERTE :** `cargo test` — 62 tests, 0 échec (7 unitaires lib +
11 d'intégration judge + 7 d'intégration discover + 17 d'intégration R10 +
20 d'intégration router) : cas passant = un jugement valide de la PR #44
(`jugement-valide.md`, faits vérifiés à l'API par le jugement F1-4) ;
cas rejetés = les 5 fautifs du Discover §6, dérivés chacun par UNE SEULE
différence (raisons nommées : J2 tête non autorisée, J3 CI non verte, J4
suite rouge sans exclusion, J5 vert repris du récit, J7 jugement qui
exécute) — dont la PR fautive plantée n° 1 ; cas limites = dossier sans
rejet du fautif (J6), document vide (J1), dossier sans limites nommées
(J8), rouge exclu par le coordinateur (J4, P-F1-5-4), type `closure_pulse`
légal (A-F1-5-3). Log : `v4-factory/evidence/D-N055/harness-F1-5.log`.
Les 51 tests F1-2/F1-3/F1-4 restent verts (régression : 0 échec).

**PR fautive plantée (D-F1-5-4, amendement A-F1-5-1) :** fautif n° 1
(tête non autorisée — le verdict autorise l'ancienne tête, la base
`96d64ce`, alors que la tête vérifiée est `2d38798`) — planté à
`v4-factory/evidence/D-N055/JUGEMENT-FAUTIF-1.md` (une seule différence,
ligne 13, `diff` vérifié) et dérivé en suite. Rejet vérifié par la CLI :
`REJET J2 — champ 'tête autorisée' : la tête autorisée n'est pas la tête
vérifiée à l'API — un jugement qui autorise une tête qu'il n'a pas
vérifiée est une signature en blanc` (sortie 2). Les garde-fous J3, J4,
J5 et J7 sont vérifiés aussi par la CLI (fautifs n° 2, 3, 4, 5 → rejets
J3, J4, J5, J7, sortie 2).

**Jugement de la PR du pas par la fonction (étape 4) :** à l'ouverture de
la PR — la CLI `judge-pr check` est courue sur le dossier de jugement de
la PR F1-5 (tête, CI et suite re-vérifiées à l'API), verdict attendu : le
même que l'acceptation du design §9. Le résultat est consigné dans le
reçu de livraison, pas anticipé ici : J3 exige une CI re-vérifiée à
l'API sur la tête, qui n'existe qu'une fois la PR ouverte (correction
portée en avant de l'ordre du design §4 — l'étape 4 suit l'ouverture,
elle ne la précède pas).

**Mesure H-M1 re-mesurée à l'exécution** (base du Discover : registre 930
lignes, 4 jugements mesurés 6 393 o / 16 597 o / 14 548 o / 18 291 o,
aucun mécanisme codé, journal-router 14 lignes seq 1–14) : registre 931
lignes (design F1-5 signé, journal 931) ; master `9b7f324` (tête vérifiée
à l'API, base de la branche `a0/f1-5-judge`) ; F1-4 clos (PR #44,
`573cad4`, reçu 021) ; D-N053 fermé (PR #46, `b6c61b2`, compteur état 0 :
1 → 0).

**Correction portée en avant (J7) :** la première version du contrôle J7
niait un marqueur d'exécution dès qu'un « ne » apparaissait dans les 48
caractères qui le précèdent — le « ne » de l'en-tête « Ce que ce jugement
ne prouve pas » niait à tort le marqueur de la ligne suivante, et le
fautif n° 5 passait la suite. La négation est désormais limitée à la
ligne du marqueur. La correction est portée ici et dans le reçu de
livraison ; le design signé n'est pas réécrit.

**Correction portée en avant (§8) :** l'en-tête « F1-4 PR ouverte, non
mergée » était périmé (PR #44 mergée `573cad4`, reçu 021, journal 926)
— correction portée en avant (fiche §8 et Statut ci-dessus).

**Hold-outs F1-5 :** H-M1 mesuré (ci-dessus) ; H-M2 diff vide sur l'amont
(code A'Space neuf) ; H-M3 suite verte (ci-dessus) ; H-M4 télémétrie zéro
(audit joint, 0 dépendance, 0 appel sortant) ; H-M5 levé au niveau du
module (fonctions Recevoir + Router + Découvrir + Juger nommées dans le
manifeste — le manifeste du daemon RigInfinity reste dû, voir §4) ; H-M6
frontière (seul le code A'Space de la fonction Juger ; voir Divergence) ;
H-M7 cette fiche. H-F1-2 = le reçu du merge qui clôt F1-5 (mission
`LE1-FAB-D-N055-010`) — **après le merge, par un exécutant dédié, pas dans
ce pas**. Le reçu de livraison de la PR (mission `LE1-FAB-D-N055-009`,
entry_id `G-20261112-028`) est consigné à l'ouverture de la PR — voir
`v4-factory/evidence/D-N055/RESULTS-F1-5.json`.

## 10. F1-6 — Exécuter (PR #49 mergée `e2e9c14`, journal 936)

**Design signé :** `plans/DESIGN-FONDATION-13-1-F1-6-PROJET.md` (fonction de
design interne, journal 934, 2026-11-12 ~22:49 EST). Décisions D-F1-6-1..12,
amendements A-F1-6-1 / A-F1-6-2 / A-F1-6-3 / A-F1-6-4 / A-F1-6-5, précisions P-F1-6-1..5.

**Domicile du code :** `01_Forkable/FKB00_Runtime/00_A0_Core/fondation-13-1/`
(crate `fondation-13-1` v0.2.0, lib `r10_validator`, module `execute`,
binaire `execute-merge`) ; manifeste
`00_A0_Core/fondation-13-1.manifest.json` (adresse `fiber:a0:fondation-13-1`,
fonctions Recevoir + Router + Découvrir + Juger + Exécuter nommées,
`validated_by` corrigé : F1-5 VALIDÉE, PR #47 mergée `4a68288`, jugement
journal 933) ; audit télémétrie
`00_A0_Core/fondation-13-1-TELEMETRY-AUDIT.md` (§ Exécuter ajouté, H-M4
reformulé : 0 appel sortant dans le code ; 1 appel en écriture d'état nommé,
compté et tracé, par la CLI).

**Ce qui est livré :** la fonction Exécuter (E1–E8, ordre E1 → E8 → E2 → E4 →
E3 → E5 → E6 → E7 ; rejet motivé, jamais de correction silencieuse) + la
CLI `execute-merge` (`check` : contrôle d'un dossier d'exécution — les
contrôles E1/E8/E2/E4 sont structurels et locaux au dossier ; E3/E5/E6
appellent les lectures à l'API et l'appel de merge par l'opérateur — SHA, CI,
mergeable et preuves post-merge injectés, même frontière que le validateur
R10). Le module `execute` est pur (0 appel sortant) ; la CLI est l'appelante
(lectures API nommées + le seul appel en écriture d'état, consigné E6).
La fonction EST l'exécution (D-F1-6-5) : pas de contrôle de recevabilité
séparé avant le merge.

**Suite H-M3 — VERTE :** `cargo test` — 76 tests, 0 échec (7 unitaires lib +
13 d'intégration execute + 11 d'intégration judge + 7 d'intégration discover +
17 d'intégration R10 + 21 d'intégration router) : cas passant = une exécution
valide du merge de la PR #44 (`execution-valide.md`, faits vérifiés à l'API
par le Discover F1-6) ; cas rejetés = les 5 fautifs du Discover §6, dérivés
chacun par UNE SEULE différence (raisons nommées : E2 tête non autorisée, E3
CI non verte, E1 merge sans jugement, E5 méthode squash, E8 exécutant qui
juge) — dont le merge fautif planté n° 1 ; cas limites = document vide (E1),
dossier sans limites nommées (E8), PR non mergeable (E4), appel non consigné
(E6), parent 2 non autorisé (E7), stade pré-merge (E1–E5), type
`merge_executed` légal comme 9e type (A-F1-6-4). Log :
`v4-factory/evidence/D-N055/suite-f1-6.txt`. Les 62 tests F1-2/F1-3/F1-4/F1-5
restent verts (régression : 0 échec).

**Merge fautif planté (D-F1-6-4, amendement A-F1-6-1) :** fautif n° 1
(tête non autorisée — le verdict autorise l'ancienne tête, la base
`96d64ce`, alors que la tête vérifiée est `2d38798`) — planté à
`v4-factory/evidence/D-N055/EXECUTION-FAUTIF-1.md` (une seule différence,
ligne 12, `diff` vérifié) et dérivé en suite. Rejet vérifié par la CLI :
`REJET E2 — champ 'tête autorisée' : la tête autorisée n'est pas la tête
vérifiée à l'API au moment du merge — un merge qui merge une tête qu'il n'a
pas vérifiée au moment de l'acte n'est pas une exécution, c'est un clic`
(sortie 2). Les garde-fous E3, E1, E5 et E8 sont vérifiés aussi par la CLI
(fautifs n° 2, 3, 4, 5 → rejets E3, E1, E5, E8, sortie 2).

**Merge témoin (A-F1-6-5) :** PR #48 (base jetable `a0/f1-6-witness-base` à
master HEAD `2cb56d0`, tête `a0/f1-6-witness` `7126b40`, changement trivial,
1 fichier +3/−0) — jugée VALIDÉE par la fonction Juger (contrôle CLI
`judge-pr` ACCEPTÉ J1–J8, sortie 0 — pas un verdict 13e ; CI 6/6 success,
les 2 jobs CodeQL et Analyze ne courant que sur PR vers master), mergée par
la fonction selon E1–E8 via la CLI `execute-merge` (pré-merge ACCEPTÉ, puis
`gh pr merge 48 --merge`, 1 seul appel en écriture d'état, consigné E6),
vérifiée E7 par un tiers : merge commit `5d86ff5` (2 parents `2cb56d0` +
`7126b40`, DVG-01, parent 2 = tête autorisée, merged true, merged_at
2026-11-13T04:31:19Z, base HEAD = merge commit, 0 PR ouverte). Branches
jetables supprimées après le merge (vérifié 404 à l'API). Le témoin précède
le merge de la PR du pas — jamais l'inverse. Le témoin ne touche pas à
master.

**Correction portée en avant (E2) :** la première version du contrôle E2
retenait la première ligne « tête autorisée » du dossier — l'en-tête cite
la tête autorisée en référence, et le fautif n° 1 passait la suite. E2 ne
retient désormais que la ligne « tête autorisée » de la section Instruction
(l'autorité), comme J2 ne retient que la ligne portant un SHA complet. La
correction est portée ici et dans le reçu de livraison ; le design signé
n'est pas réécrit.

**Correction portée en avant (routeur 7 → 9 types, A-F1-6-4) :** la F1-6
changeset porte la liste `EVENT_TYPES` du routeur à 9 types
(`closure_pulse` + `merge_executed`), réparant la réserve R2 du jugement
F1-5. Le design F1-3 n'est pas réécrit.

**Correction portée en avant (§9) :** l'en-tête « F1-5 PR ouverte, non
mergée » était périmé (PR #47 mergée `4a68288`, reçu 029, journal 933)
— correction portée en avant (fiche §9 et Statut ci-dessus).

**Hold-outs F1-6 :** H-M1 mesuré (registre 934 lignes, 6 merges mesurés,
aucun mécanisme codé, journal-router 20 lignes seq 1–20, master base
`2cb56d0` re-mesuré `f693e2b` à l'ouverture de la PR) ; H-M2 diff vide sur
l'amont (code A'Space neuf) ; H-M3 suite verte (ci-dessus) ; H-M4
télémétrie reformulée (audit joint, 0 dépendance, 0 appel sortant dans le
code, 1 appel en écriture d'état nommé, compté et tracé) ; H-M5 levé au
niveau du module (fonctions Recevoir + Router + Découvrir + Juger +
Exécuter nommées dans le manifeste — le manifeste du daemon RigInfinity
reste dû, voir §4) ; H-M6 frontière (seul le code A'Space de la fonction
Exécuter ; voir Divergence) ; H-M7 cette fiche. H-F1-3 = le reçu du merge
qui clôt F1-6 (mission `LE1-FAB-D-N055-012` PROPOSÉE) — **après le merge,
par un exécutant dédié, pas dans ce pas**. Le reçu de livraison de la PR
(mission `LE1-FAB-D-N055-011` PROPOSÉE, entry_id `G-20261112-031` PROPOSÉ)
est consigné à l'ouverture de la PR — voir
`v4-factory/evidence/D-N055/RESULTS-F1-6.json`.

## 11. F1-7 — Mémoriser (PR #50 mergée `055745b`, journal 938)

**Design signé :** `plans/DESIGN-FONDATION-13-1-F1-7-PROJET.md` (fonction de
design interne, journal 937, 2026-11-13 ~01:08 EST). Décisions D-F1-7-1..12,
amendements A-F1-7-1 / A-F1-7-2 / A-F1-7-3 / A-F1-7-4 / A-F1-7-5 / A-F1-7-6,
précisions P-F1-7-1..5.

**Domicile du code :** `01_Forkable/FKB00_Runtime/00_A0_Core/fondation-13-1/`
(crate `fondation-13-1` v0.2.0, lib `r10_validator`, module `memory`,
binaire `recall-fact`) ; manifeste
`00_A0_Core/fondation-13-1.manifest.json` (adresse `fiber:a0:fondation-13-1`,
fonctions Recevoir + Router + Découvrir + Juger + Exécuter + Mémoriser nommées,
`validated_by` corrigé : F1-6 VALIDÉE AVEC RÉSERVES, PR #49 mergée `e2e9c14`,
jugement journal 936) ; audit télémétrie
`00_A0_Core/fondation-13-1-TELEMETRY-AUDIT.md` (§ Mémoriser ajouté : 0 appel
sortant ; CLI lectrice, lectures au fichier local nommées, comptées et tracées,
0 appel réseau, 0 recherche sémantique).

**Ce qui est livré :** la fonction Mémoriser (M1–M8, ordre M1 → M7 → M2 → M3 →
M4 → M5 → M6 → M8 ; rejet motivé, jamais de correction silencieuse) + la CLI
`recall-fact` (`check` : citation d'un fait — les contrôles M1/M7/M2/M3/M4
sont structurels et locaux au dossier de citation ; M5/M6 appellent la
re-lecture au fichier et le rejet du fautif — la fonction est un mécanisme,
pas une session). Le module `memory` est pur (0 appel sortant, données
injectées) ; la CLI est la lectrice (re-compilation de l'index + re-lecture
des sources au fichier, lectures nommées, comptées, tracées ; 0 appel réseau,
0 recherche sémantique — A-F1-7-5). La fonction EST la citation (D-F1-7-7) :
pas de contrôle de recevabilité séparé avant un acte tiers.

**Suite H-M3 — VERTE :** `cargo test` — 100 tests, 0 échec (7 unitaires lib +
7 d'intégration discover + 13 d'intégration execute + 11 d'intégration judge +
24 d'intégration memory + 17 d'intégration R10 + 21 d'intégration router) :
cas passants = les 3 faits d'essai cités (T1 FreeLLMAPI, T2 aspaceos.tech,
T3 ID 11e — 4 champs exacts, vérifiés au fichier au moment de la citation) +
le fait de merge (base de F-X2) ; cas rejetés = les 4 fautifs du Discover §5.3,
dérivés chacun par UNE SEULE différence (raisons nommées : M3 date fausse,
M2 SHA altéré, M2 source absente, M4 statut faux) — dont le fait fautif planté
F-X1 ; cas limites = §5.4 (a) contradiction des trois heures portée (statut
`contredit`), (b) absence des 6 mémoires consignée (statut `absent`),
(c) source bougée signalée (statut `périmé` + re-résolution), (d) fait dupliqué
dédupliqué, (e) fait à date future (statut `à venir`), (f) fait sans date
(date « inconnue », jamais inférée) ; type `fact_recalled` légal comme 10e
type (A-F1-7-3). Log : `v4-factory/evidence/D-N055/suite-f1-7.txt` (copie
workspace `v5-f1-7-scratch/suite-f1-7.txt`). Les 76 tests F1-2/F1-3/F1-4/F1-5/
F1-6 restent verts (régression : 0 échec).

**Citations rendues par la CLI (H-F1-6, preuve du pas) :**
`v4-factory/evidence/D-N055/CITATIONS-F1-7.md` — T1 ACCEPTÉ M1–M8 (statut
`contredit`, 3 lectures), T2 ACCEPTÉ M1–M8 (statut `vérifié`, 1 lecture), T3
ACCEPTÉ M1–M8 (statut `consigné`, date du fichier, 1 lecture), F-X1 REJET M3
(sortie 2, date 2027-10-08 au lieu de 2027-10-09). Sorties CLI :
`cli-t1.txt`, `cli-t2.txt`, `cli-t3.txt`, `cli-fautif-1.txt`.

**Fait fautif planté (D-F1-7-6, amendement A-F1-7-1) :** fautif n° 1 (date
fausse — expiration 2027-10-08 au lieu de 2027-10-09) — planté à
`v4-factory/evidence/D-N055/CITATION-FAUTIF-1-F1-7.md` (une seule différence,
le champ Date) et dérivé en suite. Rejet vérifié par la CLI : `REJET M3 —
champ 'date', valeur reçue '2027-10-08' : la date citée n'est pas celle que
porte la source (la source porte 2026-11-06, 2027-10-09, 2027-05-21,
2027-02-02) — une mémoire qui cite une date qu'elle n'a pas vérifiée n'est
pas une mémoire, c'est une rumeur datée` (sortie 2). Les garde-fous M2, M4
et M6 sont vérifiés aussi par la suite (fautifs F-X2, F-X3, F-X4 → rejets M2,
M2, M4 ; citation égale au fautif → rejet M6).

**Correction portée en avant (re-compilation, D-F1-7-11a) :** `~/memory/people/`
compte **23 pages**, pas 22 comme l'annonçait le design — re-mesuré ce tour
(42 notes quotidiennes, 4 fichiers `bank/`, 160 lignes `~/MEMORY.md`, 45 lignes
`~/AGENTS.md` conformes).

**Correction portée en avant (M3, détail du rejet) :** la première version de
la CLI nommait la première date de la ligne comme « la date de la source »
(2026-11-06, date d'enregistrement) — choisir la première serait inférer.
La CLI nomme désormais toutes les dates que porte la ligne quand la date
citée n'y est pas, sans en choisir une.

**Correction portée en avant (UTF-8) :** la première version de la CLI
découpait les lignes par octets et paniquait sur « — » (T3) — corrigée par
fenêtres de 10 caractères.

**Correction portée en avant (§6, §10, Statut) :** les en-têtes « F1-2 PR
ouverte, non mergée » et « F1-6 PR ouverte, non mergée » étaient périmés
(PR #26 mergée `1f89b56`, PR #49 mergée `e2e9c14`, reçu 032, journal 936)
— correction portée en avant (fiche §6, §10 et Statut ci-dessus).

**Hold-outs F1-7 :** H-M1 mesuré (registre 937 lignes, journal-router 27 lignes
seq 1–27, master base `1f1f6e0` re-mesuré à l'ouverture de la PR) ; H-M2 diff
vide sur l'amont (code A'Space neuf) ; H-M3 suite verte (ci-dessus) ; H-M4
télémétrie (audit joint, 0 dépendance, 0 appel sortant, 0 recherche
sémantique) ; H-M5 levé au niveau du module (fonctions Recevoir + Router +
Découvrir + Juger + Exécuter + Mémoriser nommées dans le manifeste — le
manifeste du daemon RigInfinity reste dû, voir §4) ; H-M6 frontière (seul le
code A'Space de la fonction Mémoriser ; voir Divergence) ; H-M7 cette fiche.
H-F1-6 = le reçu du merge qui clôt F1-7 (mission `LE1-FAB-D-N055-014`
PROPOSÉE, entry_id `G-20261112-035` PROPOSÉ) — **après le merge, par un exécutant dédié, pas dans ce pas**. Le
reçu de livraison de la PR (mission `LE1-FAB-D-N055-013` PROPOSÉE, entry_id
`G-20261112-034` PROPOSÉ) est consigné à l'ouverture de la PR — voir
`v4-factory/evidence/D-N055/RESULTS-F1-7.json`.

## 12. F1-8 — Vision (PR ouverte, non mergée)

**Design signé :** `plans/DESIGN-FONDATION-13-1-F1-8-PROJET.md` (fonction de
design interne, journal 939, 2026-11-13 ~02:35 EST). Décisions D-F1-8-1..12,
amendements A-F1-8-1 / A-F1-8-2 / A-F1-8-3 / A-F1-8-4 / A-F1-8-5 / A-F1-8-6,
précisions P-F1-8-1..5.

**Domicile du code :** `01_Forkable/FKB00_Runtime/00_A0_Core/fondation-13-1/`
(crate `fondation-13-1` v0.2.0, lib `r10_validator`, module `vision`,
binaire `hold-vision`) ; manifeste
`00_A0_Core/fondation-13-1.manifest.json` (adresse `fiber:a0:fondation-13-1`,
fonctions Recevoir + Router + Découvrir + Juger + Exécuter + Mémoriser +
Vision nommées, `validated_by` corrigé : F1-7 VALIDÉE, PR #50 mergée
`055745b`, jugement journal 938) ; audit télémétrie
`00_A0_Core/fondation-13-1-TELEMETRY-AUDIT.md` (§ Vision ajouté : 0 appel
sortant ; CLI lectrice, lectures au fichier local nommées, comptées et tracées,
0 appel réseau, 0 recherche sémantique).

**Ce qui est livré :** la fonction Vision (V1–V8, ordre V1 → V6 → V2 → V3 →
V4 → V7 → V5 → V8 ; rejet motivé, jamais de correction silencieuse) + la CLI
`hold-vision` (`check` : rendu d'un état de vision — les contrôles V1/V6/V2/
V3/V4 sont structurels et locaux au dossier de vision ; V7/V5 appellent la
re-lecture au fichier et le rejet du fautif — la fonction est un mécanisme,
pas une session). Le module `vision` est pur (0 appel sortant, données
injectées) ; la CLI est la lectrice (lectures au fichier local nommées R1–R9
+ normalisation des fuseaux, lectures comptées, tracées ; 0 appel réseau,
0 recherche sémantique — A-F1-8-5). La fonction EST l'état de vision
(D-F1-8-5) : pas de contrôle de recevabilité séparé avant un acte tiers.

**Suite H-M3 — VERTE :** `cargo test` — 123 tests, 0 échec (10 unitaires lib +
7 d'intégration discover + 13 d'intégration execute + 11 d'intégration judge +
24 d'intégration memory + 17 d'intégration R10 + 21 d'intégration router +
20 d'intégration vision) : cas passants = les 3 cas d'essai rendus (T1
cohérence F1-7, T2 seuils D-N055/D-N053 non franchis, T3 divergence classée
N2 portée — lectures datées, comparaisons rejouables) ; cas rejetés = les 4
fautifs du Discover §5.3, dérivés chacun par UNE SEULE différence (raisons
nommées : V3 ancre fausse, V2 seq inexistant, V1 lecture non datée, V4
divergence lissée) — dont le fait fautif planté F-V1 ; cas limites = §5.4
(a) master qui bouge (dérive datée), (b) N2 ombre classée, (c) fenêtre L00
trouée (absence consignée), (d) fuseaux normalisés (EDT périmé → 02:13 EST),
(e) `pulse_2110` portée non re-vérifiée, (f) fiche/manifeste périmés portés ;
type `vision_held` légal comme 11e type (A-F1-8-3) ; premier événement
`correction` (seq 38+) corrigeant la liste des types elle-même. Log :
`v4-factory/evidence/D-N055/suite-f1-8.txt` (copie workspace
`v5-f1-8-scratch/suite-f1-8.txt`). Les 100 tests F1-2/F1-3/F1-4/F1-5/F1-6/F1-7
restent verts (régression : 0 échec).

**États de vision rendus par la CLI (H-F1-7, preuve du pas) :**
`v4-factory/evidence/D-N055/VISION-F1-8.md` — T1 ACCEPTÉ V1–V8 (cohérence
registre 938 = journal seq 37 = reçu G-20261112-035 = master `055745b` au
merge ; master lu `7feb8b0`, dérive datée ; 0 PR ouverte), T2 ACCEPTÉ V1–V8
(D-N055 seuil ~13:52, D-N053 seuil ~09:00, non franchis sur leurs ancres),
T3 ACCEPTÉ V1–V8 (divergence N2/L00 portée, statut `classée`), F-V1 REJET V3
par la CLI (sortie 2, ancre fausse : le journal 938 nomme D-N055, pas
D-N053). Sorties CLI : `cli-t1.txt`, `cli-t2.txt`, `cli-t3.txt`,
`cli-fautif-1.txt` (copies workspace `v5-f1-8-scratch/`).

**Fait fautif planté (D-F1-8-6, amendement A-F1-8-1) :** fautif F-V1 (seuil
D-N053 franchi sur l'ancre journal 938) — planté à
`v4-factory/evidence/D-N055/VISION-FAUTIF-1.md` (une seule différence,
l'ancre) et dérivé en suite. Rejet vérifié par la CLI : `REJET V3 — champ
'anchor_journal', valeur reçue 'journal 938 pour D-N053' : le journal 938
nomme D-N055, pas D-N053 — l'ancre est fausse ; le dernier événement
nommant D-N053 est le journal 930, ~21:00, seuil ~09:00, non franchi`
(sortie 2). Les garde-fous V1, V2, V4 et V5 sont vérifiés aussi par la suite
(fautifs F-V2, F-V3, F-V4 → rejets V2, V1, V4 ; fautif affirmé vrai → rejet V5).

**Correction portée en avant (liste miroir, A-F1-8-3) :** la liste
`JOURNAL_EVENT_TYPES` du module Mémoriser suit celle du routeur (même ordre,
mêmes contenus — une dérive entre les deux serait une seconde vérité, test
F1-7) : elle passe à 11 types (`vision_held`) avec ce pas. Les listes du
Juge (8 types, F1-5) et d'Exécuter (9 types, F1-6) restent figées à leur pas,
comme F1-7 les a laissées — ce sont des instantanés de leur pas, pas des
miroirs du routeur.

**Correction portée en avant (compte L00, D-F1-8-9) :** le Discover F1-8 §9
dit « 20 runs L00 absents » ; son §2.3 en compte 21 (#657–#666, #673,
#675–#684). Le compte qui fait foi est 21. Le Discover n'est pas réécrit ;
la correction est portée ici, en avant, et la vision porte 21 absences.

**Hold-outs F1-8 :** H-M1 mesuré (registre 939 lignes, journal-router 37 lignes
seq 1–37, master base `7feb8b0` re-mesuré à l'ouverture de la PR) ; H-M2 diff
vide sur l'amont (code A'Space neuf) ; H-M3 suite verte (ci-dessus) ; H-M4
télémétrie (audit joint, 0 dépendance, 0 appel sortant, 0 recherche
sémantique) ; H-M5 levé au niveau du module (fonctions Recevoir + Router +
Découvrir + Juger + Exécuter + Mémoriser + Vision nommées dans le manifeste —
le manifeste du daemon RigInfinity reste dû, voir §4) ; H-M6 frontière (seul
le code A'Space de la fonction Vision ; voir Divergence) ; H-M7 cette fiche.
H-F1-7 = le reçu du merge qui clôt F1-8 (mission `LE1-FAB-D-N055-017`
PROPOSÉE, entry_id `G-20261112-038` PROPOSÉ) — **après le merge, par un
exécutant dédié, pas dans ce pas**. Le reçu de livraison de la PR (mission
`LE1-FAB-D-N055-016` PROPOSÉE, entry_id `G-20261112-037` PROPOSÉ) est
consigné à l'ouverture de la PR par un exécutant dédié — pas dans ce pas.

## Divergence (H-M6)

- **`recorded_at` posé en UTC (`+00:00`), pas en `-05:00`.** La règle
  R10 exige ISO 8601 avec offset et `recorded_at` ≥ `observed_at` ; la
  bibliothèque standard Rust n'expose pas l'offset local sans dépendance
  externe, et le module est zéro-dépendance par design. L'offset UTC
  satisfait la règle (la comparaison se fait en secondes Unix,
  indépendante de l'offset). Les reçus Graham historiques restent en
  `-05:00` — la différence est une représentation, pas une vérité
  temporelle différente.
- **Le résolveur de SHA est injecté, pas intégré.** Le validateur ne
  contacte ni git ni l'API : l'appelant fournit les SHA qui résolvent
  (vérifiés par l'opérateur au git local ou à l'API). C'est un choix de
  frontière (zéro appel sortant dans le code), pas une lacune : la suite
  et la CLI reçoivent leurs SHA de l'opérateur.
- **La liste des designs signés est injectée, pas intégrée (F1-3).** Le
  routeur ne contacte ni le système de fichiers ni l'API pour prouver
  qu'un design est signé : l'appelant fournit la liste des designs signés
  (vérifiés par l'opérateur au fichier). Même choix de frontière que le
  résolveur de SHA (zéro appel sortant dans le code).
- **`seq` assigné à l'inscription, pas soumis (F1-3).** Le dispatch soumis
  porte 9 clés ; l'événement inscrit en porte 10 (`seq` = numéro de
  ligne). Une soumission portant `seq` est rejetée R1. Voir fiche §7 —
  correction portée en avant du Discover §4 / design §3.
- **Le manifeste du daemon (RigInfinity) n'est pas dans V5.** H-M5 est
  satisfait au niveau du module (manifeste posé ici) ; l'inscription dans
  le manifeste du daemon lui-même reste due côté RigInfinity.
- **Un SHA court est une référence, pas une citation (F1-4, D2).** Le
  Discover cite des SHA courts (`63b5816`, `12b7928`, `1f89b56`,
  `d972235`) comme abréviations ou en récit — le contrôle D2 ne les
  rejette pas : il exige la forme complète (40 hex, qui résout) là où le
  fait est affirmé comme preuve (merge PR #30 / PR #26, Master HEAD, §2).
  C'est le sens de l'acceptation du design §9, qui a accepté ce Discover
  avec ses SHA courts présents.
- **D4 et D6 sont portés par les sections, pas par le mot (F1-4).** D4 ne
  rejette « ADOPTÉE » que hors des §4 (la règle) et §6 (le rejet motivé,
  qui décrit les fautifs) — ces sections décrivent, elles ne tranchent
  pas. D6 vérifie la correction déclarée au §2 (compte BYB F1-2 v2 :
  14 214 o, écart de 146 o portés en avant) — une réécriture silencieuse
  l'efface du §2 et D6 la détecte ; les mentions du même compte aux §6/§7
  ne la remplacent pas.
- **D7 exige l'attestation positive (F1-4).** Une ligne « non lu en
  entier » au §10 n'atteste rien — le contrôle l'exclut (correction
  portée en avant, voir fiche §8).
- **J7 : la négation est limitée à la ligne du marqueur (F1-5).** Une
  mention niée (« Aucun reçu consigné par ce jugement ») n'est pas une
  exécution — mais la négation ne se lit que sur la ligne qui porte le
  marqueur : le « ne » de l'en-tête « Ce que ce jugement ne prouve pas »
  ne nie pas le marqueur de la ligne suivante (correction portée en
  avant, voir fiche §9).
- **J2 et J4 sont portés par les sections, pas par le mot (F1-5).** J2 ne
  retient que la ligne « tête autorisée » portant un SHA complet (une
  mention sans SHA n'autorise rien) ; J4 ne lit le compte « N/M » que
  dans la section Rejeu, après `cargo test` — un compte cité ailleurs
  (tableau des hold-outs, récit) ne prouve pas le rejeu.
- **`closure_pulse` accepté par la fonction Juger, pas par le routeur
  (F1-5, A-F1-5-3).** La fonction Juger accepte `closure_pulse` comme 8e
  type légal du journal (`JOURNAL_EVENT_TYPES`, 8 types) ; le routeur
  (F1-3) garde sa liste `EVENT_TYPES` à 7 types — le routeur est
  consommé, pas re-développé par ce pas, et sa mise à jour est un suivi
  hors pas, pas une réécriture du design F1-3.
- **Requalification de l'en-tête du jugement F1-3 (D-F1-5-2, portée en
  avant).** Le jugement F1-3 se présentait comme rendu par « la fonction
  de jugement interne (le 1) » — sans mécanisme codé, c'était un jugement
  en prose rendu par un sous-agent borné du 1, pas un jugement de la
  fonction. Son verdict (PR #30 VALIDÉE) tient, le merge est fait, rien
  n'est rouvert ; le design F1-3 n'est pas réécrit. À partir de F1-5,
  « fonction de jugement » ne désigne que le mécanisme codé (module
  `judge` + CLI + suite).
- **E2 ne retient que la ligne « tête autorisée » de la section Instruction
  (F1-6).** L'en-tête du dossier d'exécution cite la tête autorisée en
  référence ; seule la ligne de la section Instruction l'autorise — sinon
  le fautif n° 1 (tête autorisée = base) passerait E2 en gardant la tête
  vérifiée dans l'en-tête. Même patron que J2 (F1-5).
- **`merge_executed` légalisé 9e type (F1-6, A-F1-6-4).** La F1-6 changeset
  porte la liste `EVENT_TYPES` du routeur à 9 types (`closure_pulse` +
  `merge_executed`) ; le design F1-3 n'est pas réécrit. La réserve R2 du
  jugement F1-5 (routeur à 7 types) est réparée par ce pas.
- **`fact_recalled` légalisé 10e type (F1-7, A-F1-7-3).** La F1-7 changeset
  porte la liste `EVENT_TYPES` du routeur à 10 types ; la citation est
  rendue comme événement `fact_recalled` (preuve : les 4 champs + la
  re-lecture au fichier) ; le design F1-3 n'est pas réécrit.
- **M7 insensible à la casse (F1-7, leçon F1-5 portée).** La recherche des
  marqueurs de jugement se fait sur le texte en minuscules : un « Verdict »
  avec capitale est un verdict, comme un « Fautif planté » avec capitale
  devait être attrapé par J6.
- **L'appel de merge est effectué par l'opérateur, pas par la CLI (F1-6,
  A-F1-6-3).** La CLI `execute-merge`, std seul sans dépendance, ne fait
  pas d'HTTPS : elle contrôle le dossier d'exécution (E1–E8, `--pre-merge`
  avant l'appel, complet après), et l'opérateur effectue le seul appel en
  écriture d'état (`gh pr merge --merge`, ou `POST /pulls/{n}/merge`,
  méthode `merge`) sur instruction du dossier validé, puis le consigne
  (E6). C'est le même partage que les pas F1-2 à F1-5 (preuves injectées
  par l'opérateur, vérifiées à l'API) — la frontière est documentée, pas
  contournée.
- **`vision_held` légalisé 11e type + premier `correction` (F1-8,
  A-F1-8-3).** La F1-8 changeset porte la liste `EVENT_TYPES` du routeur
  à 11 types ; l'état de vision est rendu comme événement `vision_held`
  (preuve : lectures datées + comparaisons rejouables + divergences
  portées avec statut) ; le premier événement `correction` corrige la
  liste des types elle-même (les ajouts `closure_pulse`, `merge_executed`,
  `fact_recalled` et `vision_held` portés comme corrections, avec leurs
  événements de preuve) ; le design F1-3 n'est pas réécrit. La liste
  miroir du module Mémoriser suit (11 types) ; les listes du Juge (8) et
  d'Exécuter (9) restent figées à leur pas.
- **Fenêtre L00 trouée — 21 runs absents, cause non établie (F1-8,
  D-F1-8-9).** La vision porte les 21 absences comme une seule absence
  consignée (statut `ouverte`, deux blocs nommés) — elle ne conclut pas
  sur les runs absents (« absence consignée », pas « rien ne s'est
  passé »). Le Discover §9 dit « 20 » par erreur ; le compte qui fait
  foi est 21 (§2.3).
- **Ni la Sheet ni le miroir ne fait foi seul (F1-8, D-F1-8-10).** La
  vision compare les deux domiciles et porte la divergence (Bill présent
  au miroir, absent de la Sheet ; Coordinateur ×2 présent à la Sheet,
  absent du miroir) ; le domicile de référence est le registre (les
  événements), pas une des deux vues. La vision ne les réconcilie pas
  (V6) — la fusion est un pas ultérieur, ou un arbitrage vision.
- **Normalisation des fuseaux (F1-8, D-F1-8-11).** Tout horodatage
  comparé est converti en ISO 8601 avec offset avant comparaison ; un
  horodatage non normalisable est porté `périmé` (étiquette), pas rejeté
  comme instant. N2 « 03:13 EDT » en heure d'hiver = 02:13 EST, étiquette
  périmée — une comparaison qui mélangerait EST et EDT non normalisé se
  tromperait d'une heure.
- **Fiche/manifeste — dérive d'un pas (F1-8, D-F1-8-8).** La fiche et le
  manifeste disaient F1-7 « PR ouverte, non mergée » / « jugement à
  venir » alors que F1-7 est CLOSE (PR #50 mergée `055745b`, jugement
  VALIDÉE, journal 938). La changeset F1-8 corrige l'instance F1-7
  (statut `résolue`) ; la dérive structurelle — aucun chemin
  d'atterrissage ne met à jour la fiche — reste `ouverte`, hors de ce
  pas. La fonction Vision, elle, porte seulement : elle ne réécrit
  aucune source (V6).
