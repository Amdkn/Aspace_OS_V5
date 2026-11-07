---
entity_type: hf_model_pointer
model_family: "PathFM"
sovereign_repos:
  - "Amdkn/PathFM-125M"
  - "Amdkn/PathFM-300M"
  - "Amdkn/PathFM-Chaotic-75M"
  - "Amdkn/PathFM-Chaotic-125M"
upstream_repos:
  - "autogluon/PathFM-125M"
  - "autogluon/PathFM-300M"
  - "autogluon/PathFM-Chaotic-75M"
  - "autogluon/PathFM-Chaotic-125M"
code_submodule: "01_Forkable/FKB00_Runtime/02_PredictiveWargame_MachineLearning/PathFM"
fractal_layer: "16L"
license: "Apache-2.0"
---

# PathFM — Modèle de Fondation de Trajectoires & Systèmes Chaotiques

## 1. Matrice des Poids Souverains
| Modèle | Longueur de Contexte | Horizon Natif | Usage Cible dans A'Space OS V5 |
| :--- | :--- | :--- | :--- |
| `Amdkn/PathFM-125M` | Jusqu'à 8 192 pas | 480 pas | Simulation rapide de trajectoires continues multi-agents |
| `Amdkn/PathFM-300M` | Jusqu'à 8 192 pas | 480 pas | Prévision haute fidélité sur séries longues |
| `Amdkn/PathFM-Chaotic-75M` | 512 pas | 256 pas | Régimes de marché volatils et bifurcations chaotiques |
| `Amdkn/PathFM-Chaotic-125M` | 512 pas | 256 pas | Arbitrage haute précision sur systèmes dynamiques non linéaires |

## 2. Contrat d'Exécution Python
- `predict_samples` : Échantillonne les trajectoires jusqu'à 480 pas (ou 256 pas en mode chaotique).
- `rollout` : Prolonge chaque trajectoire de façon autonome sur un horizon étendu.
- `predict_quantiles` : Retourne les cônes d'incertitude quantiles et la prévision ponctuelle.
