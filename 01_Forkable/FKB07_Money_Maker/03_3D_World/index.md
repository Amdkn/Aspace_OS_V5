# 03_3D_World — Moteur B2B de Génération de Mondes 3D (QwenLM / BlenderWorld)

Sous-pôle de **FKB07_Money_Maker** dédié à la monétisation et à la production procédurale d'environnements, de scènes et d'actifs 3D pilotés par agents IA.

## 1. Vue d'Ensemble & Composants

| Composant | Source Upstream | Rôle & Architecture |
|---|---|---|
| **BlenderWorld** | [QwenLM/BlenderWorld](https://github.com/QwenLM/BlenderWorld) (Fork souverain [Amdkn/BlenderWorld](https://github.com/Amdkn/BlenderWorld)) | Framework multi-agents Vision-Language couplé à l'API Python native de Blender (`bpy`) pour la génération déterministe de mondes 3D. |

## 2. Boucle Opérationnelle (*Render-Critique-Refine*)

1. **Traduction Prompt $\rightarrow$ Code Procédural `bpy`** : L'agent architecte traduit les spécifications clients (bâtiments, voiries, meubles, accessoires, usines) en scripts Python Blender exécutables.
2. **Critique Visuelle Multimodale** : Rendu multi-angles automatique inspecté par le modèle Vision pour éliminer les collisions, objets flottants et anomalies d'échelle.
3. **Export Direct `.glb` / `.gltf`** : Conversion des scènes en maillages légers optimisés pour le WebGL, compatibles immédiatement avec Three.js, **`cubefarm`**, **`agent-office`** et **`city-office`**.

## 3. Offre Commerciale Productized B2B (The OMK Office)

- **Pack Décor & Monde Virtuel Clé en Main** : 1 200 $ setup + 350 $/mois pour la maintenance d'espaces virtuels WebGL (marques, studios, métavers, jeux, e-commerce immersif).
- **Synergie FKB03 & FKB07** : Fournit le pipeline d'actifs 3D procéduraux pour la métropole `City Office` déployée sur Vercel (`city.aspaceos.tech`).
