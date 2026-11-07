---
entity_type: hf_model_pointer
model_family: "AutoGluon-Chronos2-Mitra2"
sovereign_repos:
  - "Amdkn/chronos-2"
  - "Amdkn/chronos-2-small"
  - "Amdkn/mitra-classifier-2"
  - "Amdkn/mitra-regressor-2"
upstream_repos:
  - "autogluon/chronos-2"
  - "autogluon/chronos-2-small"
  - "autogluon/mitra-classifier-2"
  - "autogluon/mitra-regressor-2"
code_submodules:
  - "01_Forkable/FKB00_Runtime/02_PredictiveWargame_MachineLearning/mitra-2"
  - "01_Forkable/FKB00_Runtime/02_PredictiveWargame_MachineLearning/chronos-forecasting"
  - "01_Forkable/FKB00_Runtime/02_PredictiveWargame_MachineLearning/autogluon"
github_sovereign_forks:
  - "https://github.com/Amdkn/mitra-2"
  - "https://github.com/Amdkn/chronos-forecasting"
  - "https://github.com/Amdkn/autogluon"
fractal_layer: "16L"
license: "Apache-2.0"
---

# Chronos-2 & Mitra-v2 — Socle Prédictif Commercial (Apache-2.0)

## 1. Mitra-v2 (75.7M Classifier & 76.7M Regressor)
- **Architecture** : Transformer 2D à 12 couches avec attention croisée lignes $\times$ colonnes en apprentissage en contexte (In-Context Learning zero-shot).
- **Consensus à 8 Copies** : Vote d'ensemble à 8 copies indépendantes (*8 copies vote*) pour stabiliser la prédiction tabulaire sans réentraînement.
- **Rôle V5** : Classification et régression sur les états d'agents MiroFish, conversion de prospects B2B, scoring de solvabilité.

## 2. Chronos-2 (120M & 28M Small)
- **Architecture** : Modèle de fondation temporel universel prédisant à plus de 300 séries par seconde.
- **Covariables** : Support natif des covariables passées et futures connues (promotions, jours fériés, annonces macroéconomiques).
- **Rôle V5** : Prévision de trésorerie, charge système des holons et métriques d'activité.


## Couplage Wargame MiroFish
Mitra-v2 et Chronos-2 sont interfacés directement avec le moteur de simulation MiroFish (`MiroFish/`) pour classifier les états décisionnels du swarm et prédire les séries temporelles multivariées.
