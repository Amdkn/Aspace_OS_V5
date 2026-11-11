---
type: concept
id: ambition-modo-de-volar
title: "Protocole d'Ambition « Modo de Volar » (Felix Rieseberg — 4 Vecteurs & Outside Judge)"
created: "2026-11-03"
updated: "2026-11-11"
sources:
  - "../../raw/felix-rieseberg-ambition-2026.md"
  - "../../../AGENTS.md"
  - "../../../01_Forkable/FKB00_Runtime/automaton/src/aspace/holon-topology.ts"
  - "../../../01_Forkable/FKB03_3DWorlds/cubefarm/shared/aspaceHolons.ts"
tags:
  - ambition
  - modo-de-volar
  - felix-rieseberg
  - outside-judge
  - speed-altitude-depth-range
---

# Protocole d'Ambition « Modo de Volar » (Felix Rieseberg)

Intégration structurelle dans **Aspace OS V5** de l'essai de **Felix Rieseberg** (*"How to Be More Ambitious: A Tutorial for Humans with Models"*, `https://felixrieseberg.com/how-to-be-more-ambitious-a-tutorial-for-humans-with-models/`), inspiré de la gravure de Goya *Modo de Volar* (*Une façon de voler*) et des travaux d'Albert Bandura sur l'**auto-efficacité** (*self-efficacy*).

## 1. Principe Fondateur : L'Ambition comme Compétence Systémique
- Le goulot d'étranglement avec les modèles modernes n'est plus la faisabilité technique, mais **la taille de ce que l'humain et l'agent osent demander et vérifier**.
- La confiance ne précède pas l'action : ce sont les **preuves d'exécution réussies** (*mastery experiences*) qui élargissent l'ambition suivante.

## 2. Les 4 Vecteurs Orthogonaux d'Ambition

### Vecteur 1 — Speed (Vitesse d'Exécution)
- Cadence **Fable 5** (ratio $>80\\%$ `tool_use`, 1–2 phrases télégraphiques entre outils, commande $>5\text{s}$ en arrière-plan).
- Parallélisation systématique via **Pi Durable Subagents** (`02_Factory/factory.ps1 subagents`) et worktrees **Orca** (`writerLock` par worktree).

### Vecteur 2 — Altitude (Hauteur Stratégique)
- Toujours répondre à : ***« What's the goal beyond the goal? »*** (*Quel est l'objectif au-delà de l'objectif demandé ?*).
- Identifier les **3 décisions les plus urgentes** que le CEO (`A0 Amadeus` / `Amadou Kone`) doit trancher, avec les meilleurs arguments **pour** et **contre**.
- Concevoir le **mécanisme systémique** qui détecte ou prévient automatiquement cette classe de problème à partir des données historiques (`02_Factory/checks.ps1`, SQLite, Graphify).

### Vecteur 3 — Depth (Profondeur Industrielle & Outside Judge)
Application obligatoire du protocole de profondeur en **4 étapes** :
1. **Standard d'expert mondial** : inclure sans qu'on le demande ce qu'un spécialiste mondial du domaine ferait (idempotence `requestId`, gestion des cas limites, sécurité, tests unitaires).
2. **Matière première brute** : repartir des sources brutes (`00_Memoire/raw/`, SQLite `factory.sqlite`, code source, télémétrie réelle) et jamais de résumés dégradés.
3. **Instruments industriels** : produire du code exécutable, des bases SQLite/JSON validées et des cibles exigeantes (ex. latence locale $<200\text{ms}$ au lieu de $5\text{s}$).
4. **Outside Judge (Juge Externe Indépendant)** : ne jamais laisser l'agent créateur noter seul son propre livrable. Soumettre chaque résultat à un évaluateur séparé en lecture seule (`S1-RICK`, `S3-YAZ`, `reviewer-code` / `reviewer-security` en `writer: false`, et `pwsh -NoProfile -File 02_Factory/checks.ps1`).

### Vecteur 4 — Range (Envergure Multi-Disciplinaire & Verbes d'Impact)
- **Remplacer les noms par des verbes d'effet réel** : ne pas livrer « un mémo » ou « un tableau », mais *architecturer, automatiser, tester, déployer et prouver de bout en bout*.
- **Équipage Holonique Multi-Domaines** : mobiliser les méthodes réelles de chaque discipline à travers `Tech OS`, `Life OS 2026` et `Areas OS`, en incluant systématiquement un critique Red Team (`S1-RICK` / `A1-MORTY`).

## 3. De la demande au prompt expert : le compilateur de mission

Le levier est de ne plus demander à l’humain d’écrire lui-même un prompt d’expert à chaque mission. L’agent utilise le contexte, les fichiers, les données et les outils disponibles pour compiler l’intention en Mission Contract complet, puis il l’exécute. Le template réutilisable est [`templates/ambition-mission-template.md`](../templates/ambition-mission-template.md).

Le prompt expert devient un artefact de gouvernance réutilisable, appliqué par DOX et les harnesses, et relié au Workgraph.

## 4. Exécution continue et mémoire de mission

- L’agent maintient le graphe des travaux actif jusqu’aux critères finaux, sans arrêt artificiel à la fin d’une phase, d’un ticket, d’un commit ou d’une réponse.
- Chaque mission possède un état durable, des dépendances, des checkpoints, des preuves et une prochaine action exécutable.
- Les workers de calcul sont remplaçables ; Git distant porte le code et les artefacts de reprise. Les bases et index locaux sont des caches reconstructibles, sauf contrat de stockage durable explicite.
- Une capacité 24/7 n’est revendiquée qu’après validation d’un scheduler ou d’un runner persistant et d’une reprise après remplacement de worker.

## 5. Profil OKF V5

Le template utilise OKF v0.2 et ajoute des champs producteur Aspace compatibles avec son extensibilité : `ambition`, `execution_contract` et les métadonnées de mission. Ces extensions ne modifient pas la spécification OKF upstream.
