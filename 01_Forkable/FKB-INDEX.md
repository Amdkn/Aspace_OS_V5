# 01_Forkable/FKB-INDEX.md — Carte des catégories FKB

Créé 2026-11-04 sur ordre du Capitaine. Les catégories rangent les forks.
Les dossiers vendorisés existants NE SONT PAS déplacés (voir Règle de placement).

## Catégories

| Catégorie | Sous-catégories | Contenu | Statut |
|---|---|---|---|
| FKB00_Runtime | Triptyque Core (Automaton, Infinity, OpenRig), Harnesses, Agents-Durables, Inference-Locale | Runtime vivant du jumeau + moteur d'hibernation + rigs de dév | Index créé, Automaton mappé, Infinity et OpenRig clonés |
| FKB01_Inference | Codex-GPT-Web, FreeLLMAPI, Fusion | Inférence souveraine multi-plateformes | Index créé, codex-web mappé |
| FKB02_Video_SaaS | Repos-8, Fusion-8 | 8 repos vidéo + fusion vers 03_Videaste | Index créé, repos indexés seulement |
| FKB03_3DWorlds | Cubefarm, Agent-Office, Fusion | Mondes 3D | Index créé, cubefarm mappé, agent-office à cloner |
| FKB04_Tools_Anything | API-Anything, CLI-Anything, REA, Optimisation | Couche d'optimisation universelle | Index créé, 3 repos à cloner |

## Règle de placement (décision alignée 2026-11-05)

- `automaton` est physiquement placé dans `01_Forkable/FKB00_Runtime/automaton/` (aux côtés d'Infinity, OpenRig et Needle).
- `cubefarm` est physiquement placé dans `01_Forkable/FKB03_3DWorlds/cubefarm/` (aux côtés d'Agent-Office).
- `codex-chatgpt-web` est physiquement placé dans `01_Forkable/FKB01_Inference/codex-chatgpt-web/` (façade zéro-télémétrie).
- Toutes les références de chemins (AGENTS.md, concepts WikiLLM, HANDOFF, tests et topologie) ont été mises à jour de façon cohérente.









## Clonage sur PC

- `pwsh 01_Forkable/clone-forkables.ps1` clone les 9 forks vers leurs destinations FKB :
  infinity et openrig → FKB00, agent-office → FKB03, api-anything / CLI-Anything / rea → FKB04,
  needle → FKB00 inference-locale, elephant-goldfish-model et MiroFish inchangés
  (non assignés par cet ordre).
- `.gitignore` mis à jour avec les nouvelles destinations.

## Règle d'intégration

- FKB améliore chaque fork (outils, inférence, monde, vidéo).
- La Factory (02_Factory) réplique ensuite toute fonctionnalité voulue, utile,
  ou en manque — vers de nouveaux paradigmes de sérendipité par agnostique fractal.
- La fusion vidéo aboutit dans `03_Videaste/` à la racine de V5.
- La fusion inférence aboutit à un seul point d'inférence souveraine (hub + routeur + local).
