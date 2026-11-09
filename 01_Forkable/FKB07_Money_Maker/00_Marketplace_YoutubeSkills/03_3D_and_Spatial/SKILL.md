---
name: 3d-and-spatial
description: Skill de conception d'univers 3D Web interactifs (Three.js, Spline, Gaussian Splatting, Blender to WebGL) pour A'Space MarketPlace (LD01).
---

# Skill : 3D & Spatial Computing (A'Space MarketPlace · Catégorie 03)

Transforme les techniques de modélisation 3D Web, d'optimisation GLTF et de Gaussian Splatting en pavillons immersifs pour City Office et vitrines 3D client.

## 1. Offres Productisées Associées
1. **Vitrines E-Commerce 3D Interactives** : Configurateurs de produits 3D Three.js légers (< 5 Mo, 60 FPS mobile) ($2 000 setup + $150/m).
2. **Pavillons Virtuels & Showrooms WebGL** : Mondes immersifs pour marques, galeries d'art et événements virtuels ($3 500 setup).
3. **Pipeline Gaussian Splatting / Photogrammétrie** : Numérisation d'espaces réels et restitution temps réel dans le navigateur ($1 800/scan).

## 2. Vidéos Fondatrices Ingestées
- `https://youtu.be/g3p40vPW_DU` : Interactive 3D Web Apps with Three.js & Spline
- `https://youtu.be/-Q4SvlX9KyU` : Blender to WebGL Optimization Pipeline
- `https://youtu.be/6_MrVEXM06E` : 3D Gaussian Splatting & Spatial Computing

## 3. Protocole d'Exécution RigInfinity
1. **Export & Compression** : Pipeline Draco / KTX2 pour compresser les maillages et textures GLB.
2. **Garde-Fou Anti-Boucle** : Script de surveillance tuant tout worker de rendu 3D bloqué dans une boucle de réflexion.
3. **Stockage CAS** : Scènes `.glb` hébergées sur le **Bucket Drive 5 To** et chargées via CDN.
