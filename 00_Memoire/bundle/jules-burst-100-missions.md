---
type: runbook
id: jules-burst-100-missions
title: "Plan d'Urgence Jules.google.com (100 Sessions/Jour avant le 11 Novembre 2026) & Essaim EGM"
status: active
updated: 2026-11-08
---

# Plan d'Urgence `Jules.google.com` (100 Sessions/Jour) × `Codex-ChatGPT-Web` × `04_ADE_OpenRig`

> **Fenêtre Critique (7 → 11 Novembre 2026)** : `jules.google.com/session` offre **100 sessions d'agents de code cloud gratuites par jour** avant la fermeture des nouvelles sessions d'écriture le 11 novembre 2026.
> Toutes les missions ci-dessous sont indexées dans `00_Memoire/egm_missions.db` par le routeur EGM (`aspace_freecloud_gateway.py` sur `:31415`).

## 1. Commandes d'Activation Immédiate
```powershell
# 1. Peupler et vérifier le Ledger Éléphant-Poisson Rouge (EGM) + tester le routeur :31415
python 01_Forkable/FKB01_Inference/03_Inference_FreeCloud/aspace_freecloud_gateway.py --self-test

# 2. Démarrer le démon HTTP EGM (:31415) pour Agent Zero (A0), Claude Code, Codex, Herdr & OpenClaw
python 01_Forkable/FKB01_Inference/03_Inference_FreeCloud/aspace_freecloud_gateway.py

# 3. Inspecter les lots par Area (LD01..LD08) depuis le pont Agent Zero
python 01_Forkable/FKB00_Runtime/00_A0_Core/a0_egm_bridge.py
```

## 2. File Active des 99 Missions Atomiques Poissons Rouges (`Goldfish Missions`)

| # | Mission ID | Sous-Module Cible (`Amdkn/*`) | Area (`LD`) | Holon Owner | Runner Prioritaire | Branche Cible |
|---|---|---|---|---|---|---|
| 1 | `EGM-01_Forkable_FKB00_Runtime_00_A0_Core_a0-plugins` | `01_Forkable/FKB00_Runtime/00_A0_Core/a0-plugins` | `LD07` | `S1-RICK/LD07` | `jules_cloud_100` | `aspace-v5-native` |
| 2 | `EGM-01_Forkable_FKB00_Runtime_00_A0_Core_agent-zero` | `01_Forkable/FKB00_Runtime/00_A0_Core/agent-zero` | `LD06` | `S1-RICK/LD06` | `jules_cloud_100` | `aspace-v5-native` |
| 3 | `EGM-01_Forkable_FKB00_Runtime_00_A0_Core_cordis` | `01_Forkable/FKB00_Runtime/00_A0_Core/cordis` | `LD02` | `S1-RICK/LD02` | `jules_cloud_100` | `aspace-v5-native` |
| 4 | `EGM-01_Forkable_FKB00_Runtime_00_A0_Core_deepseek-harness` | `01_Forkable/FKB00_Runtime/00_A0_Core/deepseek-harness` | `LD03` | `S1-RICK/LD03` | `jules_cloud_100` | `aspace-v5-native` |
| 5 | `EGM-01_Forkable_FKB00_Runtime_00_A0_Core_pi` | `01_Forkable/FKB00_Runtime/00_A0_Core/pi` | `LD04` | `S1-RICK/LD04` | `jules_cloud_100` | `aspace-v5-native` |
| 6 | `EGM-01_Forkable_FKB00_Runtime_00_A0_Core_spynel` | `01_Forkable/FKB00_Runtime/00_A0_Core/spynel` | `LD08` | `S1-RICK/LD08` | `jules_cloud_100` | `aspace-v5-native` |
| 7 | `EGM-01_Forkable_FKB00_Runtime_00_A0_Core_tuxee` | `01_Forkable/FKB00_Runtime/00_A0_Core/tuxee` | `LD01` | `S1-RICK/LD01` | `jules_cloud_100` | `aspace-v5-native` |
| 8 | `EGM-01_Forkable_FKB00_Runtime_01_Holo_TriptyqueCore_automaton` | `01_Forkable/FKB00_Runtime/01_Holo_TriptyqueCore/automaton` | `LD03` | `S1-RICK/LD03` | `jules_cloud_100` | `aspace-v5-native` |
| 9 | `EGM-01_Forkable_FKB00_Runtime_01_Holo_TriptyqueCore_infinity` | `01_Forkable/FKB00_Runtime/01_Holo_TriptyqueCore/infinity` | `LD01` | `S1-RICK/LD01` | `jules_cloud_100` | `aspace-v5-native` |
| 10 | `EGM-01_Forkable_FKB00_Runtime_01_Holo_TriptyqueCore_openrig` | `01_Forkable/FKB00_Runtime/01_Holo_TriptyqueCore/openrig` | `LD02` | `S1-RICK/LD02` | `jules_cloud_100` | `aspace-v5-native` |
| 11 | `EGM-01_Forkable_FKB00_Runtime_02_PredictiveWargame_MachineLearning_MiroFish` | `01_Forkable/FKB00_Runtime/02_PredictiveWargame_MachineLearning/MiroFish` | `LD06` | `S1-RICK/LD06` | `jules_cloud_100` | `aspace-v5-native` |
| 12 | `EGM-01_Forkable_FKB00_Runtime_02_PredictiveWargame_MachineLearning_PathFM` | `01_Forkable/FKB00_Runtime/02_PredictiveWargame_MachineLearning/PathFM` | `LD01` | `S1-RICK/LD01` | `jules_cloud_100` | `aspace-v5-native` |
| 13 | `EGM-01_Forkable_FKB00_Runtime_02_PredictiveWargame_MachineLearning_autogluon` | `01_Forkable/FKB00_Runtime/02_PredictiveWargame_MachineLearning/autogluon` | `LD02` | `S1-RICK/LD02` | `jules_cloud_100` | `aspace-v5-native` |
| 14 | `EGM-01_Forkable_FKB00_Runtime_02_PredictiveWargame_MachineLearning_chronos-forecasting` | `01_Forkable/FKB00_Runtime/02_PredictiveWargame_MachineLearning/chronos-forecasting` | `LD03` | `S1-RICK/LD03` | `jules_cloud_100` | `aspace-v5-native` |
| 15 | `EGM-01_Forkable_FKB00_Runtime_02_PredictiveWargame_MachineLearning_mitra-2` | `01_Forkable/FKB00_Runtime/02_PredictiveWargame_MachineLearning/mitra-2` | `LD05` | `S1-RICK/LD05` | `jules_cloud_100` | `aspace-v5-native` |
| 16 | `EGM-01_Forkable_FKB00_Runtime_02_PredictiveWargame_MachineLearning_tabfm` | `01_Forkable/FKB00_Runtime/02_PredictiveWargame_MachineLearning/tabfm` | `LD04` | `S1-RICK/LD04` | `jules_cloud_100` | `aspace-v5-native` |
| 17 | `EGM-01_Forkable_FKB00_Runtime_02_PredictiveWargame_MachineLearning_timesfm` | `01_Forkable/FKB00_Runtime/02_PredictiveWargame_MachineLearning/timesfm` | `LD02` | `S1-RICK/LD02` | `jules_cloud_100` | `aspace-v5-native` |
| 18 | `EGM-01_Forkable_FKB00_Runtime_03_MasterSpec_CleanPlan_elephant-goldfish-model` | `01_Forkable/FKB00_Runtime/03_MasterSpec_CleanPlan/elephant-goldfish-model` | `LD05` | `S1-RICK/LD05` | `jules_cloud_100` | `aspace-v5-native` |
| 19 | `EGM-01_Forkable_FKB00_Runtime_03_MasterSpec_CleanPlan_get-shit-done` | `01_Forkable/FKB00_Runtime/03_MasterSpec_CleanPlan/get-shit-done` | `LD01` | `S1-RICK/LD01` | `jules_cloud_100` | `aspace-v5-native` |
| 20 | `EGM-01_Forkable_FKB00_Runtime_03_MasterSpec_CleanPlan_gstack` | `01_Forkable/FKB00_Runtime/03_MasterSpec_CleanPlan/gstack` | `LD07` | `S1-RICK/LD07` | `jules_cloud_100` | `aspace-v5-native` |
| 21 | `EGM-01_Forkable_FKB00_Runtime_03_MasterSpec_CleanPlan_superpowers` | `01_Forkable/FKB00_Runtime/03_MasterSpec_CleanPlan/superpowers` | `LD08` | `S1-RICK/LD08` | `jules_cloud_100` | `aspace-v5-native` |
| 22 | `EGM-01_Forkable_FKB00_Runtime_04_ADE_OpenRig_claude-code` | `01_Forkable/FKB00_Runtime/04_ADE_OpenRig/claude-code` | `LD03` | `S1-RICK/LD03` | `jules_cloud_100` | `aspace-v5-native` |
| 23 | `EGM-01_Forkable_FKB00_Runtime_04_ADE_OpenRig_codex` | `01_Forkable/FKB00_Runtime/04_ADE_OpenRig/codex` | `LD04` | `S1-RICK/LD04` | `jules_cloud_100` | `aspace-v5-native` |
| 24 | `EGM-01_Forkable_FKB00_Runtime_04_ADE_OpenRig_herdr` | `01_Forkable/FKB00_Runtime/04_ADE_OpenRig/herdr` | `LD05` | `S1-RICK/LD05` | `jules_cloud_100` | `aspace-v5-native` |
| 25 | `EGM-01_Forkable_FKB00_Runtime_04_ADE_OpenRig_herdr-app` | `01_Forkable/FKB00_Runtime/04_ADE_OpenRig/herdr-app` | `LD07` | `S1-RICK/LD07` | `jules_cloud_100` | `aspace-v5-native` |
| 26 | `EGM-01_Forkable_FKB00_Runtime_04_ADE_OpenRig_herdr-core` | `01_Forkable/FKB00_Runtime/04_ADE_OpenRig/herdr-core` | `LD06` | `S1-RICK/LD06` | `jules_cloud_100` | `aspace-v5-native` |
| 27 | `EGM-01_Forkable_FKB00_Runtime_04_ADE_OpenRig_hermes-agent` | `01_Forkable/FKB00_Runtime/04_ADE_OpenRig/hermes-agent` | `LD05` | `S1-RICK/LD05` | `jules_cloud_100` | `aspace-v5-native` |
| 28 | `EGM-01_Forkable_FKB00_Runtime_04_ADE_OpenRig_openclaw` | `01_Forkable/FKB00_Runtime/04_ADE_OpenRig/openclaw` | `LD02` | `S1-RICK/LD02` | `jules_cloud_100` | `aspace-v5-native` |
| 29 | `EGM-01_Forkable_FKB00_Runtime_04_ADE_OpenRig_orca` | `01_Forkable/FKB00_Runtime/04_ADE_OpenRig/orca` | `LD08` | `S1-RICK/LD08` | `jules_cloud_100` | `aspace-v5-native` |
| 30 | `EGM-01_Forkable_FKB00_Runtime_04_ADE_OpenRig_t3code` | `01_Forkable/FKB00_Runtime/04_ADE_OpenRig/t3code` | `LD01` | `S1-RICK/LD01` | `jules_cloud_100` | `aspace-v5-native` |
| 31 | `EGM-01_Forkable_FKB00_Runtime_05_Recursive_RSI_adk-recipes` | `01_Forkable/FKB00_Runtime/05_Recursive_RSI/adk-recipes` | `LD08` | `S1-RICK/LD08` | `jules_cloud_100` | `aspace-v5-native` |
| 32 | `EGM-01_Forkable_FKB00_Runtime_05_Recursive_RSI_dream-rsi` | `01_Forkable/FKB00_Runtime/05_Recursive_RSI/dream-rsi` | `LD02` | `S1-RICK/LD02` | `jules_cloud_100` | `aspace-v5-native` |
| 33 | `EGM-01_Forkable_FKB00_Runtime_05_Recursive_RSI_prime-agent` | `01_Forkable/FKB00_Runtime/05_Recursive_RSI/prime-agent` | `LD06` | `S1-RICK/LD06` | `jules_cloud_100` | `aspace-v5-native` |
| 34 | `EGM-01_Forkable_FKB00_Runtime_05_Recursive_RSI_rrsi` | `01_Forkable/FKB00_Runtime/05_Recursive_RSI/rrsi` | `LD01` | `S1-RICK/LD01` | `jules_cloud_100` | `aspace-v5-native` |
| 35 | `EGM-01_Forkable_FKB00_Runtime_05_Recursive_RSI_wikiskill` | `01_Forkable/FKB00_Runtime/05_Recursive_RSI/wikiskill` | `LD07` | `S1-RICK/LD07` | `jules_cloud_100` | `aspace-v5-native` |
| 36 | `EGM-01_Forkable_FKB01_Inference_01_Inference_Locale_GLiNER2.5-multi-Decide` | `01_Forkable/FKB01_Inference/01_Inference_Locale/GLiNER2.5-multi-Decide` | `LD07` | `S1-RICK/LD07` | `jules_cloud_100` | `aspace-v5-native` |
| 37 | `EGM-01_Forkable_FKB01_Inference_01_Inference_Locale_LFM3-Omni-2B` | `01_Forkable/FKB01_Inference/01_Inference_Locale/LFM3-Omni-2B` | `LD01` | `S1-RICK/LD01` | `jules_cloud_100` | `aspace-v5-native` |
| 38 | `EGM-01_Forkable_FKB01_Inference_01_Inference_Locale_LoRA` | `01_Forkable/FKB01_Inference/01_Inference_Locale/LoRA` | `LD06` | `S1-RICK/LD06` | `jules_cloud_100` | `aspace-v5-native` |
| 39 | `EGM-01_Forkable_FKB01_Inference_01_Inference_Locale_mimi` | `01_Forkable/FKB01_Inference/01_Inference_Locale/mimi` | `LD08` | `S1-RICK/LD08` | `jules_cloud_100` | `aspace-v5-native` |
| 40 | `EGM-01_Forkable_FKB01_Inference_01_Inference_Locale_moshi` | `01_Forkable/FKB01_Inference/01_Inference_Locale/moshi` | `LD05` | `S1-RICK/LD05` | `jules_cloud_100` | `aspace-v5-native` |
| 41 | `EGM-01_Forkable_FKB01_Inference_01_Inference_Locale_needle` | `01_Forkable/FKB01_Inference/01_Inference_Locale/needle` | `LD04` | `S1-RICK/LD04` | `jules_cloud_100` | `aspace-v5-native` |
| 42 | `EGM-01_Forkable_FKB01_Inference_02_Inference_Cooperative_DeepInfer` | `01_Forkable/FKB01_Inference/02_Inference_Cooperative/DeepInfer` | `LD02` | `S1-RICK/LD02` | `jules_cloud_100` | `aspace-v5-native` |
| 43 | `EGM-01_Forkable_FKB01_Inference_02_Inference_Cooperative_cross-platform-llm-client` | `01_Forkable/FKB01_Inference/02_Inference_Cooperative/cross-platform-llm-client` | `LD04` | `S1-RICK/LD04` | `jules_cloud_100` | `aspace-v5-native` |
| 44 | `EGM-01_Forkable_FKB01_Inference_02_Inference_Cooperative_mesh-llm` | `01_Forkable/FKB01_Inference/02_Inference_Cooperative/mesh-llm` | `LD03` | `S1-RICK/LD03` | `jules_cloud_100` | `aspace-v5-native` |
| 45 | `EGM-01_Forkable_FKB01_Inference_03_Inference_FreeCloud_codex-chatgpt-web` | `01_Forkable/FKB01_Inference/03_Inference_FreeCloud/codex-chatgpt-web` | `LD06` | `S1-RICK/LD06` | `jules_cloud_100` | `aspace-v5-native` |
| 46 | `EGM-01_Forkable_FKB01_Inference_03_Inference_FreeCloud_freebuff` | `01_Forkable/FKB01_Inference/03_Inference_FreeCloud/freebuff` | `LD07` | `S1-RICK/LD07` | `jules_cloud_100` | `aspace-v5-native` |
| 47 | `EGM-01_Forkable_FKB01_Inference_03_Inference_FreeCloud_freellmapi` | `01_Forkable/FKB01_Inference/03_Inference_FreeCloud/freellmapi` | `LD05` | `S1-RICK/LD05` | `jules_cloud_100` | `aspace-v5-native` |
| 48 | `EGM-01_Forkable_FKB02_Memory_01_BillionContxtLanguage_AutoOnthology_auto-ontology` | `01_Forkable/FKB02_Memory/01_BillionContxtLanguage_AutoOnthology/auto-ontology` | `LD05` | `S1-RICK/LD05` | `jules_cloud_100` | `aspace-v5-native` |
| 49 | `EGM-01_Forkable_FKB02_Memory_01_BillionContxtLanguage_AutoOnthology_billion-context` | `01_Forkable/FKB02_Memory/01_BillionContxtLanguage_AutoOnthology/billion-context` | `LD04` | `S1-RICK/LD04` | `jules_cloud_100` | `aspace-v5-native` |
| 50 | `EGM-01_Forkable_FKB02_Memory_01_BillionContxtLanguage_AutoOnthology_context-language-models` | `01_Forkable/FKB02_Memory/01_BillionContxtLanguage_AutoOnthology/context-language-models` | `LD06` | `S1-RICK/LD06` | `jules_cloud_100` | `aspace-v5-native` |
| 51 | `EGM-01_Forkable_FKB02_Memory_dox` | `01_Forkable/FKB02_Memory/dox` | `LD08` | `S1-RICK/LD08` | `jules_cloud_100` | `aspace-v5-native` |
| 52 | `EGM-01_Forkable_FKB02_Memory_gbrain` | `01_Forkable/FKB02_Memory/gbrain` | `LD03` | `S1-RICK/LD03` | `jules_cloud_100` | `aspace-v5-native` |
| 53 | `EGM-01_Forkable_FKB02_Memory_graphify` | `01_Forkable/FKB02_Memory/graphify` | `LD07` | `S1-RICK/LD07` | `jules_cloud_100` | `aspace-v5-native` |
| 54 | `EGM-01_Forkable_FKB02_Memory_infinite-brain-harness` | `01_Forkable/FKB02_Memory/infinite-brain-harness` | `LD05` | `S1-RICK/LD05` | `jules_cloud_100` | `aspace-v5-native` |
| 55 | `EGM-01_Forkable_FKB02_Memory_infinite-brain-os` | `01_Forkable/FKB02_Memory/infinite-brain-os` | `LD04` | `S1-RICK/LD04` | `jules_cloud_100` | `aspace-v5-native` |
| 56 | `EGM-01_Forkable_FKB02_Memory_knowledge-catalog` | `01_Forkable/FKB02_Memory/knowledge-catalog` | `LD01` | `S1-RICK/LD01` | `jules_cloud_100` | `aspace-v5-native` |
| 57 | `EGM-01_Forkable_FKB02_Memory_llm-wiki` | `01_Forkable/FKB02_Memory/llm-wiki` | `LD03` | `S1-RICK/LD03` | `jules_cloud_100` | `aspace-v5-native` |
| 58 | `EGM-01_Forkable_FKB02_Memory_servers` | `01_Forkable/FKB02_Memory/servers` | `LD02` | `S1-RICK/LD02` | `jules_cloud_100` | `aspace-v5-native` |
| 59 | `EGM-01_Forkable_FKB03_3DWorlds_agent-office` | `01_Forkable/FKB03_3DWorlds/agent-office` | `LD01` | `S1-RICK/LD01` | `jules_cloud_100` | `aspace-v5-native` |
| 60 | `EGM-01_Forkable_FKB03_3DWorlds_city-office` | `01_Forkable/FKB03_3DWorlds/city-office` | `LD03` | `S1-RICK/LD03` | `jules_cloud_100` | `aspace-v5-native` |
| 61 | `EGM-01_Forkable_FKB03_3DWorlds_cubefarm` | `01_Forkable/FKB03_3DWorlds/cubefarm` | `LD08` | `S1-RICK/LD08` | `jules_cloud_100` | `aspace-v5-native` |
| 62 | `EGM-01_Forkable_FKB03_3DWorlds_space-agent` | `01_Forkable/FKB03_3DWorlds/space-agent` | `LD03` | `S1-RICK/LD03` | `jules_cloud_100` | `aspace-v5-native` |
| 63 | `EGM-01_Forkable_FKB04_Tools_Anything_CLI-Anything` | `01_Forkable/FKB04_Tools_Anything/CLI-Anything` | `LD03` | `S1-RICK/LD03` | `jules_cloud_100` | `aspace-v5-native` |
| 64 | `EGM-01_Forkable_FKB04_Tools_Anything_api-anything` | `01_Forkable/FKB04_Tools_Anything/api-anything` | `LD02` | `S1-RICK/LD02` | `jules_cloud_100` | `aspace-v5-native` |
| 65 | `EGM-01_Forkable_FKB04_Tools_Anything_hermes-agent` | `01_Forkable/FKB04_Tools_Anything/hermes-agent` | `LD04` | `S1-RICK/LD04` | `jules_cloud_100` | `aspace-v5-native` |
| 66 | `EGM-01_Forkable_FKB04_Tools_Anything_rea` | `01_Forkable/FKB04_Tools_Anything/rea` | `LD04` | `S1-RICK/LD04` | `jules_cloud_100` | `aspace-v5-native` |
| 67 | `EGM-01_Forkable_FKB06_Video_SaaS_argo` | `01_Forkable/FKB06_Video_SaaS/argo` | `LD08` | `S1-RICK/LD08` | `jules_cloud_100` | `aspace-v5-native` |
| 68 | `EGM-01_Forkable_FKB06_Video_SaaS_earshot` | `01_Forkable/FKB06_Video_SaaS/earshot` | `LD01` | `S1-RICK/LD01` | `jules_cloud_100` | `aspace-v5-native` |
| 69 | `EGM-01_Forkable_FKB06_Video_SaaS_explainroo` | `01_Forkable/FKB06_Video_SaaS/explainroo` | `LD02` | `S1-RICK/LD02` | `jules_cloud_100` | `aspace-v5-native` |
| 70 | `EGM-01_Forkable_FKB06_Video_SaaS_huashu-motion` | `01_Forkable/FKB06_Video_SaaS/huashu-motion` | `LD03` | `S1-RICK/LD03` | `jules_cloud_100` | `aspace-v5-native` |
| 71 | `EGM-01_Forkable_FKB06_Video_SaaS_reanimate` | `01_Forkable/FKB06_Video_SaaS/reanimate` | `LD04` | `S1-RICK/LD04` | `jules_cloud_100` | `aspace-v5-native` |
| 72 | `EGM-01_Forkable_FKB06_Video_SaaS_rossark-motion-skill` | `01_Forkable/FKB06_Video_SaaS/rossark-motion-skill` | `LD05` | `S1-RICK/LD05` | `jules_cloud_100` | `aspace-v5-native` |
| 73 | `EGM-01_Forkable_FKB06_Video_SaaS_take-one` | `01_Forkable/FKB06_Video_SaaS/take-one` | `LD06` | `S1-RICK/LD06` | `jules_cloud_100` | `aspace-v5-native` |
| 74 | `EGM-01_Forkable_FKB06_Video_SaaS_video-director` | `01_Forkable/FKB06_Video_SaaS/video-director` | `LD07` | `S1-RICK/LD07` | `jules_cloud_100` | `aspace-v5-native` |
| 75 | `EGM-01_Forkable_FKB07_Money_Maker_01_Trading_LLM-Trading-Lab` | `01_Forkable/FKB07_Money_Maker/01_Trading/LLM-Trading-Lab` | `LD05` | `S1-RICK/LD05` | `jules_cloud_100` | `aspace-v5-native` |
| 76 | `EGM-01_Forkable_FKB07_Money_Maker_01_Trading_TradingAgents` | `01_Forkable/FKB07_Money_Maker/01_Trading/TradingAgents` | `LD03` | `S1-RICK/LD03` | `jules_cloud_100` | `aspace-v5-native` |
| 77 | `EGM-01_Forkable_FKB07_Money_Maker_01_Trading_TradingView-Unified-MCP` | `01_Forkable/FKB07_Money_Maker/01_Trading/TradingView-Unified-MCP` | `LD08` | `S1-RICK/LD08` | `jules_cloud_100` | `aspace-v5-native` |
| 78 | `EGM-01_Forkable_FKB07_Money_Maker_01_Trading_Vibe-Trading` | `01_Forkable/FKB07_Money_Maker/01_Trading/Vibe-Trading` | `LD01` | `S1-RICK/LD01` | `jules_cloud_100` | `aspace-v5-native` |
| 79 | `EGM-01_Forkable_FKB07_Money_Maker_01_Trading_ai-hedge-fund` | `01_Forkable/FKB07_Money_Maker/01_Trading/ai-hedge-fund` | `LD08` | `S1-RICK/LD08` | `jules_cloud_100` | `aspace-v5-native` |
| 80 | `EGM-01_Forkable_FKB07_Money_Maker_01_Trading_claude-trading-skills` | `01_Forkable/FKB07_Money_Maker/01_Trading/claude-trading-skills` | `LD02` | `S1-RICK/LD02` | `jules_cloud_100` | `aspace-v5-native` |
| 81 | `EGM-01_Forkable_FKB07_Money_Maker_01_Trading_daily_stock_analysis` | `01_Forkable/FKB07_Money_Maker/01_Trading/daily_stock_analysis` | `LD07` | `S1-RICK/LD07` | `jules_cloud_100` | `aspace-v5-native` |
| 82 | `EGM-01_Forkable_FKB07_Money_Maker_01_Trading_financial-services` | `01_Forkable/FKB07_Money_Maker/01_Trading/financial-services` | `LD02` | `S1-RICK/LD02` | `jules_cloud_100` | `aspace-v5-native` |
| 83 | `EGM-01_Forkable_FKB07_Money_Maker_01_Trading_freqtrade` | `01_Forkable/FKB07_Money_Maker/01_Trading/freqtrade` | `LD06` | `S1-RICK/LD06` | `jules_cloud_100` | `aspace-v5-native` |
| 84 | `EGM-01_Forkable_FKB07_Money_Maker_01_Trading_nansen-cli` | `01_Forkable/FKB07_Money_Maker/01_Trading/nansen-cli` | `LD01` | `S1-RICK/LD01` | `jules_cloud_100` | `aspace-v5-native` |
| 85 | `EGM-01_Forkable_FKB07_Money_Maker_01_Trading_tradingview-indicator-search-mcp-server` | `01_Forkable/FKB07_Money_Maker/01_Trading/tradingview-indicator-search-mcp-server` | `LD07` | `S1-RICK/LD07` | `jules_cloud_100` | `aspace-v5-native` |
| 86 | `EGM-01_Forkable_FKB07_Money_Maker_03_3D_World_BlenderWorld` | `01_Forkable/FKB07_Money_Maker/03_3D_World/BlenderWorld` | `LD04` | `S1-RICK/LD04` | `jules_cloud_100` | `aspace-v5-native` |
| 87 | `EGM-01_Forkable_FKB07_Money_Maker_DeepTutor` | `01_Forkable/FKB07_Money_Maker/DeepTutor` | `LD01` | `S1-RICK/LD01` | `jules_cloud_100` | `aspace-v5-native` |
| 88 | `EGM-01_Forkable_FKB07_Money_Maker_OpenMausBot` | `01_Forkable/FKB07_Money_Maker/OpenMausBot` | `LD02` | `S1-RICK/LD02` | `jules_cloud_100` | `aspace-v5-native` |
| 89 | `EGM-01_Forkable_FKB07_Money_Maker_OpenMontage` | `01_Forkable/FKB07_Money_Maker/OpenMontage` | `LD08` | `S1-RICK/LD08` | `jules_cloud_100` | `aspace-v5-native` |
| 90 | `EGM-01_Forkable_FKB07_Money_Maker_changedetection.io` | `01_Forkable/FKB07_Money_Maker/changedetection.io` | `LD05` | `S1-RICK/LD05` | `jules_cloud_100` | `aspace-v5-native` |
| 91 | `EGM-01_Forkable_FKB07_Money_Maker_impeccable` | `01_Forkable/FKB07_Money_Maker/impeccable` | `LD07` | `S1-RICK/LD07` | `jules_cloud_100` | `aspace-v5-native` |
| 92 | `EGM-01_Forkable_FKB07_Money_Maker_open-notebook` | `01_Forkable/FKB07_Money_Maker/open-notebook` | `LD04` | `S1-RICK/LD04` | `jules_cloud_100` | `aspace-v5-native` |
| 93 | `EGM-01_Forkable_FKB07_Money_Maker_powerbi-to-ai-visuals` | `01_Forkable/FKB07_Money_Maker/powerbi-to-ai-visuals` | `LD06` | `S1-RICK/LD06` | `jules_cloud_100` | `aspace-v5-native` |
| 94 | `EGM-01_Forkable_FKB07_Money_Maker_text-to-cad` | `01_Forkable/FKB07_Money_Maker/text-to-cad` | `LD03` | `S1-RICK/LD03` | `jules_cloud_100` | `aspace-v5-native` |
| 95 | `EGM-01_Forkable_FKB07_Money_Maker_uptime-kuma` | `01_Forkable/FKB07_Money_Maker/uptime-kuma` | `LD06` | `S1-RICK/LD06` | `jules_cloud_100` | `aspace-v5-native` |
| 96 | `EGM-01_Forkable_FKB08_Plugins_anthropic-skills` | `01_Forkable/FKB08_Plugins/anthropic-skills` | `LD05` | `S1-RICK/LD05` | `jules_cloud_100` | `aspace-v5-native` |
| 97 | `EGM-01_Forkable_FKB08_Plugins_claude-video` | `01_Forkable/FKB08_Plugins/claude-video` | `LD08` | `S1-RICK/LD08` | `jules_cloud_100` | `aspace-v5-native` |
| 98 | `EGM-01_Forkable_FKB08_Plugins_mattpocock-skills` | `01_Forkable/FKB08_Plugins/mattpocock-skills` | `LD06` | `S1-RICK/LD06` | `jules_cloud_100` | `aspace-v5-native` |
| 99 | `EGM-01_Forkable_FKB08_Plugins_openai-plugins` | `01_Forkable/FKB08_Plugins/openai-plugins` | `LD07` | `S1-RICK/LD07` | `jules_cloud_100` | `aspace-v5-native` |

## 3. Template de Prompt Poisson Rouge (`Goldfish Prompt` < 4 Ko) à Soumettre à Jules / Codex-Web / Herdr
```text
[GOLDFISH ATOMIC MISSION] Repository: Amdkn/<submodule> | Branch: aspace-v5-native
1. Create or checkout branch `aspace-v5-native`.
2. Add `aspace-plugin.json` exposing this repository as a reversible Cordis Fiber for A0 (`00_A0_Core/agent-zero`).
3. Connect state/telemetry hooks to `http://127.0.0.1:31415/v1/chat/completions` and `00_Memoire/shared_brain/memory.jsonl`.
4. Run existing unit tests / linter and open PR or commit directly on `aspace-v5-native`.
```
