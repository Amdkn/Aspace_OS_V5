---
entity_type: wargame_swarm_engine
name: "MiroFish"
sovereign_fork: "https://github.com/Amdkn/MiroFish"
pinned_commit: "7657031ac01184afe2cb220f5ee3545573b5e843"
submodule_path: "01_Forkable/FKB00_Runtime/02_PredictiveWargame_MachineLearning/MiroFish"
upstream: "https://github.com/666ghj/MiroFish"
fractal_layer: "20L"
license: "MIT"
coupled_models:
  - "Mitra-v2 (autogluon/mitra-classifier-2 & autogluon/mitra-regressor-2) -> Amdkn/mitra-2"
  - "Chronos-2 (autogluon/chronos-2 & chronos-2-small) -> Amdkn/chronos-forecasting"
  - "PathFM (autogluon/PathFM-125M/300M & Chaotic) -> Amdkn/PathFM"
  - "TabFM & TimesFM (google/tabfm-1.1.0-pytorch & timesfm-3.0-pytorch) -> Amdkn/tabfm & Amdkn/timesfm"
---

# MiroFish - Moteur de Simulation Multi-Agents & Wargame Prédictif (Couche 20L)

## 1. Rôle et Architecture dans Aspace OS V5
MiroFish est le moteur de wargame et de simulation de dynamique sociale/marché/agents incarné par **S3-RORY** (Persistance, Continuité 4P et Wargames MiroFish).
Il génère des environnements de simulation multi-agents (OASIS + MindGraph) dont les états émergents sont injectés directement dans le quatuor de modèles prédictifs situés dans `01_Forkable/FKB00_Runtime/02_PredictiveWargame_MachineLearning/models/`.

## 2. Structuration avec le Dossier models/
- **models/chronos2-mitra2.md** : Mitra-v2 classe en temps réel les décisions d actions des agents MiroFish. Chronos-2 prévoit les séries d indicateurs agrégés.
- **models/pathfm.md** : PathFM calcule le rollout et la trajectoire spatio-temporelle continue des dynamiques chaotiques dans la simulation.
- **models/google-tabfm-timesfm.md** : Google TabFM et TimesFM agissent comme arbitres et jury de double vérification externe pour valider la robustesse des simulations MiroFish.
