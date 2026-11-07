# A'Space OS V5 — Registre Souverain des Modèles Hugging Face (`HF-SOVEREIGN-INDEX`)

> **Doctrine Asset-Reference** : Aucun poids binaire (`.safetensors`, `.gguf`, `.bin`) n'est stocké dans Git. Les agents utilisent ce registre pour résoudre le chemin du dépôt souverain sur Hugging Face (`hf.co/Amdkn/*`), connaître la couche fractale d'activation (`4L`..`20L`) et charger la fiche technique `.md` associée.

---

## 1. Pôle `FKB01_Inference` — Perception, Triage & Appel d'Outils (Couche `4L`)

| Identifiant Souverain HF | Dépôt Amont (Upstream) | Fiche Locale V5 (`.md`) | Spécifications & Rôle | Licence | Couche |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **`Amdkn/LFM3-Omni-2B`** | `LiquidAI/LFM2-2.6B` / `LFM3-Omni-2B` | [`FKB01_Inference/models/lfm3-omni-2b.md`](FKB01_Inference/models/lfm3-omni-2b.md) | 2B params, 13 têtes d'attention, multimodal (texte/audio/vidéo), port `:9931` | Open Weights | `4L` |
| **`Amdkn/GLiNER2.5-multi-Decide`** | `fastino/GLiNER2.5-multi-Decide` | [`FKB01_Inference/models/gliner2.5-multi-decide.md`](FKB01_Inference/models/gliner2.5-multi-decide.md) | Extracteur d'entités & classifieur zero-shot 16 langues, CPU `< 10 ms` | Apache-2.0 | `4L` |
| **`Amdkn/mimi`** | `kyutai/mimi` | [`FKB01_Inference/models/kyutai-mimi.md`](FKB01_Inference/models/kyutai-mimi.md) | Codec audio neuronal temps réel 24 kHz streaming (tokens acoustiques & sémantiques) | CC-BY-4.0 / MIT | `4L` |

---

## 2. Pôle `FKB00_Runtime/02_PredictiveWargame_MachineLearning` — Quatuor Prédictif (Couches `16L` & `20L`)

| Identifiant Souverain HF | Dépôt Amont (Upstream) | Fiche Locale V5 (`.md`) | Spécifications & Rôle | Licence | Couche |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **`Amdkn/mitra-classifier-2`** | `autogluon/mitra-classifier-2` | [`models/chronos2-mitra2.md`](FKB00_Runtime/02_PredictiveWargame_MachineLearning/models/chronos2-mitra2.md) | 75,7M params, 12L 2D Transformer, vote par consensus à 8 copies | **Apache-2.0** | `16L` |
| **`Amdkn/mitra-regressor-2`** | `autogluon/mitra-regressor-2` | [`models/chronos2-mitra2.md`](FKB00_Runtime/02_PredictiveWargame_MachineLearning/models/chronos2-mitra2.md) | 76,7M params, régression tabulaire In-Context Learning zero-shot | **Apache-2.0** | `16L` |
| **`Amdkn/chronos-2`** | `autogluon/chronos-2` | [`models/chronos2-mitra2.md`](FKB00_Runtime/02_PredictiveWargame_MachineLearning/models/chronos2-mitra2.md) | 120M params (et variante `chronos-2-small` 28M), séries temporelles avec covariables futures | **Apache-2.0** | `16L` |
| **`Amdkn/PathFM-125M`** | `autogluon/PathFM-125M` | [`models/pathfm.md`](FKB00_Runtime/02_PredictiveWargame_MachineLearning/models/pathfm.md) | Contexte 8 192 pas $\rightarrow$ horizon 480 pas (`predict_samples`, `rollout`) | **Apache-2.0** | `16L` |
| **`Amdkn/PathFM-300M`** | `autogluon/PathFM-300M` | [`models/pathfm.md`](FKB00_Runtime/02_PredictiveWargame_MachineLearning/models/pathfm.md) | 300M params, contexte 8 192 pas $\rightarrow$ horizon 480 pas | **Apache-2.0** | `20L` |
| **`Amdkn/PathFM-Chaotic-75M`** | `autogluon/PathFM-Chaotic-75M` | [`models/pathfm.md`](FKB00_Runtime/02_PredictiveWargame_MachineLearning/models/pathfm.md) | Systèmes dynamiques chaotiques, contexte 512 pas $\rightarrow$ horizon 256 pas | **Apache-2.0** | `16L` |
| **`Amdkn/PathFM-Chaotic-125M`** | `autogluon/PathFM-Chaotic-125M` | [`models/pathfm.md`](FKB00_Runtime/02_PredictiveWargame_MachineLearning/models/pathfm.md) | Systèmes chaotiques haute précision, contexte 512 pas $\rightarrow$ horizon 256 pas | **Apache-2.0** | `20L` |
| **`Amdkn/tabfm-1.1.0-pytorch`** | `google/tabfm-1.1.0-pytorch` | [`models/google-tabfm-timesfm.md`](FKB00_Runtime/02_PredictiveWargame_MachineLearning/models/google-tabfm-timesfm.md) | 24 blocs ICL (`/classification` & `/regression`), 1,65 Go — Jury R&D interne | Non-Commercial | `20L` |
| **`Amdkn/timesfm-3.0-pytorch`** | `google/timesfm-3.0-pytorch` | [`models/google-tabfm-timesfm.md`](FKB00_Runtime/02_PredictiveWargame_MachineLearning/models/google-tabfm-timesfm.md) | 20 couches, 16 têtes, Variate Attention, patch 32 $\rightarrow$ 64, 1,32 Go — Oracle temporel | Non-Commercial | `20L` |
