# FKB03_3DWorlds — Mondes 3D

## Sous-catégories

### Cubefarm (mappé)
- Emplacement : `01_Forkable/FKB03_3DWorlds/cubefarm` (non déplacé).
- Rôle : immeuble opérationnel, 3 étages OS, 578 holons, Lobby supervisé par A0.

### Agent-Office (mappé)
- Emplacement : `01_Forkable/FKB03_3DWorlds/agent-office` via clone-forkables.ps1.
- Upstream : https://github.com/Amdkn/agent-office.git
- Rôle : Mezzanine managers + Tab Portal Boards 2D (TODO HANDOFF).

### City Office (Fusion unifiée & Déploiement Vercel)
- Emplacement : `01_Forkable/FKB03_3DWorlds/city-office` (sous-module souverain [Amdkn/city-office](https://github.com/Amdkn/city-office)).
- Architecture spatiale concentrique :
  - **Cœur Central (0,0,0)** : Citadelle Voxel `CubeFarm` (Monolithe A0 Amadeus 7D + parcelles des 8 Domaines de Vie).
  - **Anneau Routier Périphérique** : Réseau routier circulaire `agent-office` matérialisant en temps réel les flux MCP et le pipeline agentique.
  - **Couronne Urbaine Périphérique** : 7 districts représentant les pôles `FKB00..FKB07`.
- Déploiement : Vercel Edge/Static via `vercel.json` (`city.aspaceos.tech`).
- Contrôle Fractal : Montable dynamiquement en couche `8L` via `02_Factory/mount-fractal.ps1`.
