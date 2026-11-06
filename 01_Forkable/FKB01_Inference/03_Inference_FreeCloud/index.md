# 03_Inference_FreeCloud — Pôle Cloud Zéro-Coût, Radar d'Opportunités & Bouclier Télémétrie

> **Rôle** : Fournir une capacité de calcul massive et redondante sans carte bancaire, protégée par des boucliers anti-télémétrie stricts, et alimentée en continu par un radar de veille d'opportunités d'inférence gratuite (sponsors, affiliations, promotions d'IA).

---

## Les Trois Piliers de l'Inférence FreeCloud

```
┌────────────────────────────────────────────────────────────────────────┐
│ 1. FreeLLMAPI (Port :31415)                                            │
│  └─ Routeur unifié 34 providers gratuits (635 endpoints)               │
│  └─ Bascule dynamique automatique en cas de quota épuisé               │
│  └─ Réception des clés et endpoints découverts (ex: Exa Search/Embed)  │
└───────────────────────────────────▲────────────────────────────────────┘
                                    │
               Voie A : Enregistrement API / Endpoints
                                    │
┌───────────────────────────────────┴────────────────────────────────────┐
│ 3. Freebuff (Radar d'Inférence & Découverte d'Opportunités)            │
│  └─ Agent de codage gratuit (Desktop, CLI, Web, Cloud, Chat)           │
│  └─ Modèle économique basé sur les annonces & affiliations sponsors    │
│  └─ Détection continue de nouvelles opportunités de calcul gratuit :   │
│     • Exa AI : 50 $ de crédits offerts à l'inscription (+20 $ Buff)   │
│     • Nouveaux providers / tokens gratuits injectables                 │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
          Voie B : Automatisation Web & Scraping via API-Anything
                                    │
┌───────────────────────────────────▼────────────────────────────────────┐
│ 2. Codex-ChatGPT-Web (Façade Étanche & Bouclier CJS)                   │
│  └─ Façade Web Pro (session locale sans quota API Codex)               │
│  └─ Bouclier anti-télémétrie `aspace-telemetry-shield.cjs`             │
│  └─ Interface optimisée par FKB04 (API-Anything) pour capter et        │
│     exploiter les nouvelles interfaces web d'inférence en direct       │
└────────────────────────────────────────────────────────────────────────┘
```

---

## Composants Hébergés

### 1. [`freellmapi`](https://github.com/Amdkn/freellmapi) (Port `:31415`)
- **Routeur Unifié Multi-Providers** : Accès à 34 fournisseurs gratuits d'inférence (plus de 635 endpoints de modèles).
- **Failover Dynamique** : Bascule automatique en cas d'épuisement de quota (`freellmapi/auto` $\rightarrow$ `claude-sonnet-4-5` $\rightarrow$ `qwen3.8-max` $\rightarrow$ `gemini-3.8-flash` $\rightarrow$ `deepseek-v4-flash`).
- **Gouvernance Pi Durable** : Détection des erreurs de quota et ré-essai automatique après 15 minutes.
- **Extension Dynamique (Voie A)** : Intégration de clés tierces gratuites obtenues (ex. API Exa Search & Embeddings financée par les 50 $ de crédits d'accueil).

### 2. [`codex-chatgpt-web`](https://github.com/Amdkn/codex-chatgpt-web) (Bouclier Zéro-Télémétrie & Façade Web)
- **Façade Étanche** : Utilise les sessions Web de ChatGPT (y compris Pro) comme modèle natif dans Codex avec contexte, outils, streaming et vision sans consommer le quota API Codex.
- **Bouclier Anti-Télémétrie (`aspace-telemetry-shield.cjs`)** : 24 patterns de télémétrie bloqués localement, neutralisation des mises à jour non sollicitées via `start-aspace-codex-web.ps1`.
- **Couplage FKB04 API-Anything (Voie B)** : Automatisation des flux web pour transformer n'importe quelle nouvelle interface web découverte par Freebuff en API exploitable par nos agents.

### 3. [`freebuff`](https://github.com/Amdkn/freebuff) (Radar d'Opportunités & Agent Gratuit)
- **Cinq Produits Gratuits** : Desktop app, CLI terminal, Web app, Cloud repo agents et Chat de recherche, sans abonnement ni clé API requise.
- **Radar de Découverte Sémantique** : Freebuff s'appuie sur des annonces textuelles de partenaires pour financer ses modèles. Ces annonces constituent pour Aspace OS une source active de veille pour capter de nouvelles offres de crédits gratuits (ex. Exa AI à 50 $).
- **Boucle Vertueuse d'Inférence** :
  - **Sens Entrant** : Les offres sponsorisées détectées par Freebuff procurent des crédits et clés API.
  - **Sens Exploitation** : Ces clés sont injectées dans FreeLLMAPI (Voie A) ou automatisées dans Codex-ChatGPT-Web via API-Anything (Voie B).
  - **Sens Réciproque** : Freebuff bénéficie en retour des optimisations de routage et des boucliers d'Aspace OS V5.
