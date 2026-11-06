# 03_Inference_FreeCloud — Pôle Cloud Zéro-Coût & Bouclier Télémétrie

> **Rôle** : Fournir une capacité de calcul massive et redondante sans carte bancaire, protégée par des boucliers anti-télémétrie stricts, servant de repli de grande envergure pour les agents autonomes d'Aspace OS V5.

---

## Composants Hébergés

### 1. [`freellmapi`](https://github.com/Amdkn/freellmapi) (Port `:31415`)
- **Routeur Unifié Multi-Providers** : Accès à 34 fournisseurs gratuits d'inférence (plus de 635 endpoints de modèles).
- **Failover Dynamique** : Bascule automatique en cas d'épuisement de quota (`freellmapi/auto` $\rightarrow$ `claude-sonnet-4-5` $\rightarrow$ `qwen3.8-max` $\rightarrow$ `gemini-3.8-flash` $\rightarrow$ `deepseek-v4-flash`).
- **Gouvernance Pi Durable** : Détection des erreurs de quota et ré-essai automatique après 15 minutes.

### 2. [`codex-chatgpt-web`](https://github.com/Amdkn/codex-chatgpt-web) (Bouclier Zéro-Télémétrie)
- **Façade Étanche** : Utilise les sessions Web de ChatGPT (y compris Pro) comme modèle natif dans Codex avec contexte, outils, streaming et vision sans consommer le quota API Codex.
- **Bouclier Anti-Télémétrie (`aspace-telemetry-shield.cjs`)** : 24 patterns de télémétrie bloqués localement, neutralisation des mises à jour non sollicitées via `start-aspace-codex-web.ps1`.
