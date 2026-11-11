---
type: Concept
title: "Neuro-Tabular Wargame & Quatuor Prédictif (AutoGluon x Google x CEO-Bench)"
tags: [predictive-wargame, autogluon, mitra-v2, tabfm, timesfm, chronos, pathfm, ceo-bench, gbrain, gstack, superpowers, gsd]
---

# Neuro-Tabular Wargame & Quatuor Prédictif (AutoGluon x Google x CEO-Bench)

## 1. Synthèse des 3 Brainstormings

Le pôle `01_Forkable/FKB00_Runtime/02_PredictiveWargame_MachineLearning` ancre l'intelligence collective narrative et émergente des essaims (MiroFish / OASIS) dans des modèles de fondation quantitatifs rigoureux :

1. **Axe Transversal Tabulaire (L'État $X$)** :
   - **Mitra-v2** (`autogluon/mitra-classifier-2` & `mitra-regressor-2`, Apache-2.0, 75.7M) : Transformer 2D à 12 couches avec vote par consensus à 8 copies (*8 copies vote*).
   - **Google TabFM 1.1.0** (`google/tabfm-1.1.0-pytorch`, non-commercial) : Transformer ICL à 24 blocs pour l'arbitrage R&D interne et la détection d'incertitude.
2. **Axe Longitudinal Temporel (Le Temps $t$)** :
   - **Chronos-2** (`autogluon/chronos-2`, Apache-2.0, 120M) : Prévision zero-shot haute vitesse avec covariables futures connues.
   - **Google TimesFM 3.0** (`google/timesfm-3.0-pytorch`, non-commercial) : Stacked Mixing Transformer à 20 couches (miroir de la couche `20L`), 16 têtes, *Variate Attention* multivariée et cônes de quantiles `q10`..`q90`.
3. **Axe Chaotique & Trajectoires** :
   - **PathFM** (`autogluon/PathFM`, Apache-2.0) : Modèles 75M à 300M avec versions dédiées aux dynamiques chaotiques (`PathFM-Chaotic`) générant des faisceaux de trajectoires via `rollout` et `predict_quantiles`.
4. **Méta-Orchestrateur Déterministe** :
   - **AutoGluon Core** (`autogluon/autogluon`, Apache-2.0) : Stacking et ensembling unifiés liant `TabularPredictor` et `TimeSeriesPredictor`.

---

## 2. La Règle du 90% Déterministe / 10% Jugement IA (CEO-Bench & StarMynd)

Inspiré de **CEO-Bench** (`ceobench.com`) et de **Infinite-Brain-OS** (StarMynd / Garry Tan `GBrain`) :
- Les décisions économiques et d'entreprise ne doivent jamais reposer sur le vote subjectif ou l'hallucination d'un LLM seul.
- Le socle de calcul (90%) est strictement déterministe (équations microéconomiques, modèles tabulaires ICL, séries temporelles quantiles).
- Le LLM n'intervient que sur les 10% restants de **jugement contextuel, formulation stratégique et arbitrage narratif**.

---

## 3. Triade de Gouvernance & Discipline

1. **Gouvernance des Rôles (`gstack` + `gbrain`)** : Définit qui décide (CEO, Architect, Designer, Eng Manager, QA) avec cycle de consolidation 24/7.
2. **Isolation du Contexte (`get-shit-done` / GSD + `infinite-brain-os`)** : Charge orchestrateur maintenue à 30-40%, délégations atomiques propres.
3. **Discipline d'Exécution (`superpowers` en mode headless)** : Pipeline TDD rigoureux où aucun code de production n'est écrit sans test préalable.

---

## 4. Doctrine Asset-Reference Hugging Face

- **0 binaire lourd dans Git** : Poids `.safetensors` maintenus hors Git dans le cache `~/.cache/huggingface/hub/`.
- Duplication serveur à serveur instantanée sur `huggingface.co/Amdkn/*`.
- Fiches miroirs `.md` et index central dans `01_Forkable/HF-SOVEREIGN-INDEX.md`.
