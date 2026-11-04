# 01_Forkable/FKB-INDEX.md — Carte des catégories FKB

Créé 2026-11-04 sur ordre du Capitaine. Les catégories rangent les forks.
Les dossiers vendorisés existants NE SONT PAS déplacés (voir Règle de placement).

## Catégories

| Catégorie | Sous-catégories | Contenu | Statut |
|---|---|---|---|
| FKB00_Runtime | Automaton, Harnesses, Agents-Durables, Inference-Locale, Noyau-Perpétuel-A0 | Runtime du jumeau + inférence locale | Index créé, automaton mappé |
| FKB01_Inference | Codex-GPT-Web, FreeLLMAPI, Fusion | Inférence souveraine multi-plateformes | Index créé, codex-web mappé |
| FKB02_Video_SaaS | Repos-8, Fusion-8 | 8 repos vidéo + fusion vers 03_Videaste | Index créé, repos indexés seulement |
| FKB03_3DWorlds | Cubefarm, Agent-Office, Fusion | Mondes 3D | Index créé, cubefarm mappé, agent-office à cloner |
| FKB04_Tools_Anything | API-Anything, CLI-Anything, REA, Optimisation | Couche d'optimisation universelle | Index créé, 3 repos à cloner |

## Règle de placement (décision consignée 2026-11-04)

- `automaton`, `cubefarm`, `codex-chatgpt-web` restent à `01_Forkable/` racine.
- Raison : 90+ références chemin dans le repo (AGENTS.md, concepts, HANDOFF, holon-topology.ts).
  Un déplacement silencieux les rendrait toutes obsolètes sans gain.
- Les index FKB les mappent (lien logique, pas déplacement physique).
- Un déplacement physique = refactor séparé, avec mise à jour des références, pas ici.

## Clonage sur PC

- `pwsh 01_Forkable/clone-forkables.ps1` clone les 7 forks vers leurs destinations FKB :
  agent-office → FKB03, api-anything / CLI-Anything / rea → FKB04,
  needle → FKB00 inference-locale, elephant-goldfish-model et MiroFish inchangés
  (non assignés par cet ordre).
- `.gitignore` mis à jour avec les nouvelles destinations.

## Règle d'intégration

- FKB améliore chaque fork (outils, inférence, monde, vidéo).
- La Factory (02_Factory) réplique ensuite toute fonctionnalité voulue, utile,
  ou en manque — vers de nouveaux paradigmes de sérendipité par agnostique fractal.
- La fusion vidéo aboutit dans `03_Videaste/` à la racine de V5.
- La fusion inférence aboutit à un seul point d'inférence souveraine (hub + routeur + local).
