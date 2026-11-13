---
type: concept
id: ricks-verse
title: "Le Rick's Verse — Structuration V5 : Rick (S1), ses 3 Doctors intégrés, leurs Compagnons dans leurs Tardis"
created: "2026-11-10"
updated: "2026-11-10"
sources:
  - "ordre S0 du 2026-11-10 21:56 EST — GO Fondation 13 sessions → 1"
  - "demande S0 du 2026-11-10 22:04 EST — documentation mémoire V5 + LD08 Georgiou + G Sheets"
  - "../../../AGENTS.md (§8 — Tech OS, 13 holons S1/S2/S3)"
tags:
  - ricks-verse
  - s1-rick
  - doctors
  - compagnons
  - tardis
  - fondation-13-en-1
  - ld08-georgiou
---

# Le Rick's Verse — Structuration V5

## Décision (S0, 2026-11-10)

Le Rick's Verse est l'univers de Rick (S1) : il n'est plus un étage au-dessus de sessions séparées, il **intègre** ses trois Doctors dans son univers, et chaque Doctor est accompagné de ses Compagnons **dans son Tardis**. C'est la forme documentée de la Fondation ordonnée le 2026-11-10 : **fusionner les 13 sessions en 1** — Rick + 3 Doctors + 9 Compagnons — pour supprimer le point de défaillance unique du routeur (absent : rien ne bouge ; présent : il tourne en rond, et une contradiction locale tue le système global). La documentation vient après le lancement, pour correction et alignement par orientation.

## Structure — 1 univers, 3 Tardis, 13 rôles

| Tardis (noyau) | Doctor (S2) | Compagnons (S3) | Domaine du noyau |
|---|---|---|---|
| Kernel | 13e Doctor | Ryan, Yaz, Graham | Noyau technique — autorité pleine du 13e : valide ET exécute (merges, pushs) ; le Capitaine ne reçoit que l'arbitrage vision |
| Life | 11e Doctor | Amy, Rory, River | Vie et domaines Life OS |
| Buzz | 12e Doctor | Bill, Clara, Nardole | Découverte, design, coordination |

Rick (S1) tient l'univers entier : il structure en Before You Build (vision, non-négociables, critères mesurables, hors-scope) — aucune décision technique chez Rick, aucune décision technique chez S0.

## Canaux des Compagnons (décision S0, 2026-10-09)

- Yaz → Observatoire ; Ryan → Factory (l'Atelier) ; Bill → Frameworks ; Clara → Décisions ; Nardole → Agora ; Rory → Preuves.
- Amy, River, Graham et les Doctors : canaux inchangés.

## Continuité — pas de goulot (doctrine S0, 2026-11-09)

La continuité Clara → Nardole → Ryan est autonome et événementielle : la signature de Clara déclenche le typage de Nardole, le typage déclenche l'exécution de Ryan — sans relais humain ni relais A0. A0 garde la pulsation à chaque étape, jamais le gate. Dans le Rick's Verse, cette règle devient structurelle : les passages entre Tardis sont des événements, pas des attentes.

## Chaîne d'artefacts (templates V4 → templates V5)

`Mission.md` (Rick, S1) → `PRD.md` + `ADR-XXX` (Doctor, S2) → `TDD.md` (Compagnon, S3) → implémentation + reçu R10.

Les quatre templates vivent dans `v4-factory/templates/delegation/` (Mission, PRD, ADR, TDD) et sont repris comme templates de conception de V5 : chaque mission du Rick's Verse produit ces artefacts, tracés dans le registre Sheets (voir ci-dessous).

## Domiciles de la documentation

- **Mémoire V5** : cette page (`00_Memoire/bundle/concepts/ricks-verse.md`), référencée dans `bundle/index.md`, consignée dans `bundle/log.md` (append-only).
- **LD08 Georgiou (I1, Impact)** : conception déposée dans le dossier Drive « A3 GEORGIOU — LD08 Impact » et, côté repo, dans `00_Memoire/bundle/areas_os/I_LD08_Impact_MetaAspace/CONCEPTION-RICKS-VERSE.md`.
- **Google Sheets** : le Workgraph Muse existant (onglets Workgraph + Règles) reste le registre « qui travaille sur quoi » ; un second registre, « Rick's Verse — Structure, Artefacts & Manifestes (V5) », porte la structure des 3 Tardis, la chaîne d'artefacts et les manifestes.

## État (2026-11-10, 22:04 EST)

- Fondation 13 → 1 : **lancée** sur ordre S0 (21:56 EST) — plan de base écrit par Rick, Discover en cours. Non terminée.
- Réserves nommées, inchangées : jugement H-C2 toujours attendu ; failover modelPool (H-C2-4) non prouvable sur cette VM.
- Rien sans design signé Clara : la règle tient dans le Rick's Verse comme avant.
