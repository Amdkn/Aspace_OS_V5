---
entity_type: hf_model_pointer
model_family: "Google-TabFM-TimesFM"
sovereign_repos:
  - "Amdkn/tabfm-1.1.0-pytorch"
  - "Amdkn/timesfm-3.0-pytorch"
upstream_repos:
  - "google/tabfm-1.1.0-pytorch"
  - "google/timesfm-3.0-pytorch"
fractal_layer: "20L"
license: "tabfm-non-commercial-v1.0 & timesfm-non-commercial-license-v1.0"
---

# Google TabFM 1.1.0 & TimesFM 3.0 — Jury de Calibration Interne A0

## 1. Google TabFM 1.1.0 (PyTorch, 1.65 Go)
- **Architecture** : 24 blocs Transformer ICL couvrant `/classification` et `/regression`.
- **Rôle V5** : Arbitre lourd et second avis indépendant pour vérifier la convergence des prédictions de Mitra-v2 sur les matrices d'états complexes.

## 2. Google TimesFM 3.0 (PyTorch, 1.32 Go, ~300M params)
- **Architecture** : Stacked Mixing Transformer à 20 couches, 16 têtes d'attention (`dim=1280`), mécanisme *Variate Attention* et *CPM Iterative RevIN*.
- **Patch Contexte $\rightarrow$ Horizon** : Patch d'entrée de 32 pas vers horizon de 64 pas ($t+64$).
- **Quantiles Multi-Niveaux** : Sortie directe de la distribution avec cône d'incertitude `q10`..`q90` (médiane à l'index 4), calculant automatiquement le risque de chute (*downside drawdown*).
