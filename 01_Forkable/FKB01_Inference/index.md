# FKB01_Inference — Pôle d'Inférence Souverain Unifié (4 Strates)

> **Architecture Déterministe** : FKB01 regroupe l'intégralité des capacités de génération de tokens d'Aspace OS V5, réparties en quatre strates étanches allant du calcul on-device ultra-léger jusqu'au registre de qualification des opportunités d'inférence.

---

## Les 4 Strates d'Inférence Souveraine

```
┌────────────────────────────────────────────────────────────────────────┐
│ STRATE 1 · INFERENCE LOCALE ON-DEVICE (01_Inference_Locale)            │
│  ├─ Cactus Needle : Tool-calling déterministe 2-bit & ASR Whistle     │
│  ├─ Fastino GLiNER 2.5 : Extraction d'entités & intention sans hallu. │
│  ├─ Kyutai Mimi & Moshi : Dialogue vocal & codec audio streaming       │
│  └─ Liquid AI LFM3-Omni-2B + LoRA : Modèle neuronal local (:9931)      │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │ Débordement si tâche trop lourde
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│ STRATE 2 · INFERENCE COOPERATIVE DISTRIBUEE (02_Inference_Cooperative) │
│  ├─ DeepInfer : Moteur C++/CUDA, micro-kernels FP8 & KV-Cache Paged   │
│  ├─ Mesh-LLM : Orchestration P2P, Pipeline Parallelism (PP) & mDNS     │
│  └─ Cross-Platform Client : Surface omnicanale Tauri/Flutter           │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │ Débordement si modèle colossal / externe
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│ STRATE 3 · INFERENCE FREECLOUD & SHIELD (03_Inference_FreeCloud)       │
│  ├─ FreeLLMAPI : Pool de 34 providers gratuits (port :31415)           │
│  ├─ Codex-ChatGPT-Web : Façade Web Pro étanche zéro-télémétrie        │
│  └─ Freebuff : Radar opportunités (Exa $50) branché Voie A/B          │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │ Alimentation continue & qualification anti-clickbait
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│ STRATE 4 · REGISTRE DE VEILLE YOUTUBE & SKILL WATCH (04_Inference...) │
│  ├─ Skill Watch : 5 filtres anti-clickbait & anti-durcissement CGU     │
│  ├─ Base Registry JSON : Suivi dynamique des opportunités indexées     │
│  └─ Qualification : APINex (20M/j), Refuseless, Croton, Kito, WorkBuddy│
└────────────────────────────────────────────────────────────────────────┘
```

---

## Tableau de Bord des Sous-Modules et Registres par Strate

| Strate | Sous-Module / Registre | Dépôt GitHub Amdkn / Source | Destination des Poids / Secrets |
|---|---|---|---|
| **01 Locale** | **Cactus Needle** | [Amdkn/needle](https://github.com/Amdkn/needle) | [HuggingFace Amdkn7/needle3](https://huggingface.co/Amdkn7/needle3) |
| **01 Locale** | **Kyutai Moshi** | [Amdkn/moshi](https://github.com/Amdkn/moshi) | Local weights / Hugging Face |
| **01 Locale** | **Kyutai Mimi** | [Amdkn/mimi](https://github.com/Amdkn/mimi) | [HuggingFace Amdkn7/mimi](https://huggingface.co/Amdkn7/mimi) |
| **01 Locale** | **Fastino GLiNER 2.5** | [Amdkn/GLiNER2.5-multi-Decide](https://github.com/Amdkn/GLiNER2.5-multi-Decide) | [HuggingFace Amdkn7/GLiNER2.5-multi-Decide](https://huggingface.co/Amdkn7/GLiNER2.5-multi-Decide) |
| **01 Locale** | **Liquid LFM3-Omni-2B** | [Amdkn/LFM3-Omni-2B](https://github.com/Amdkn/LFM3-Omni-2B) | [HuggingFace Amdkn7/LFM3-Omni-2B](https://huggingface.co/Amdkn7/LFM3-Omni-2B) |
| **01 Locale** | **Microsoft LoRA** | [Amdkn/LoRA](https://github.com/Amdkn/LoRA) | Adaptateurs locaux |
| **02 Coopérative** | **DeepInfer** | [Amdkn/DeepInfer](https://github.com/Amdkn/DeepInfer) | Compilateur CUDA / C++ local |
| **02 Coopérative** | **Mesh-LLM** | [Amdkn/mesh-llm](https://github.com/Amdkn/mesh-llm) | Libp2p / découverte mDNS |
| **02 Coopérative** | **Cross-Platform Client** | [Amdkn/cross-platform-llm-client](https://github.com/Amdkn/cross-platform-llm-client) | Application Desktop/Mobile |
| **03 FreeCloud** | **FreeLLMAPI** | [Amdkn/freellmapi](https://github.com/Amdkn/freellmapi) | Port local `:31415` |
| **03 FreeCloud** | **Codex-ChatGPT-Web** | [Amdkn/codex-chatgpt-web](https://github.com/Amdkn/codex-chatgpt-web) | Shield zéro-télémétrie |
| **03 FreeCloud** | **Freebuff** | [Amdkn/freebuff](https://github.com/Amdkn/freebuff) | Radar de découverte d'opportunités d'inférence (Exa $50) |
| **04 Veille YouTube** | **YouTube Discovery Registry** | `04_Inference_Youtube_Discovery_Registry` | Skill Watch anti-clickbait & Registre JSON des opportunités |
