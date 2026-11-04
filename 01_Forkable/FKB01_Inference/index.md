# FKB01_Inference — Inférence souveraine multi-plateformes

## Sous-catégories

### Codex-GPT-Web (mappé)
- Emplacement : `01_Forkable/codex-chatgpt-web` (non déplacé).
- Rôle : hub web et CLI multi-plateformes zéro télémétrie (shield `aspace-telemetry-shield.cjs`).
- Constitution (ligne 21) : combiné à api-anything, CLI-Anything et rea, rotation intelligente sur quota.

### FreeLLMAPI (mappé, service)
- Routeur unifié. Compte du Capitaine sur son PC (port :31415 docs V5 ; sandbox :3001 distinct).
- Faits dashboard 2026-11-04 (capture du Capitaine) : 4,1B restants, 96% de 4,2B, 176,7M utilisés.
- 71 modèles + 120 sans quota publié. Routage Balanced : fiabilité 50%, vitesse 25%, intelligence 25%.
- Modèles visibles : Qwen3.8 Max/Omni (xKiro), Gemini Flash 3.5/3.6/3.7, Qwen3.7 Max 120/120, Qwen3.6, SenseNova, Aion 3.0.
- Failover V5 existant : freellmapi/auto → claude-sonnet-4-5 → qwen3.8-max → gemini-3.8-flash → deepseek-v4-flash.

### Fusion (question ouverte, analyse d'abord)
- Peut-on fusionner routeur + hub en un seul point d'inférence souveraine ?
- Piste : codex-web en façade (zéro télémétrie), FreeLLMAPI en pool (rotation quota),
  LFM3 local en repli. Plateformes : Muse, Gemini, Claude, DeepSeek, Z, Qwen.
- Optimisation via FKB04 (API Anything) avant tout code de fusion.
