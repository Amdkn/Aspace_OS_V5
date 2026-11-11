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
**Statut :** F1-0 livré (inventaire, PR V5 #23) ; F1-1 clos (BYB accepté, journal 787) ; F1-2 clos (PR #26 mergée `1f89b56`, reçu H-F1-5 G-20261111-006) ; F1-3 PR ouverte, non mergée (ce pas).

## 1. Mesure zéro (H-M1)

- **13 sessions** nommées par Clara (`chat.list`, ~22:53 EST) : Rick `2428b187`, 13e `a517ae1d`,
  11e `6f410ddd` (ID complet non établi), 12e `7489b6f0`, Yaz `e1ac3b2d`, Ryan `a152c901`,
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
- **ID 11e incomplet :** le design ne donne que `6f410ddd` (8 car.) — l'ID complet
  n'est pas établi, jamais inventé.
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

## 6. F1-2 — Recevoir (PR ouverte, non mergée)

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

## 7. F1-3 — Router (PR ouverte, non mergée)

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
