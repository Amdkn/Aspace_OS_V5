# 04_Inference_Youtube_Discovery_Registry — Radar Anti-Bruit & Veille Inférence

> **Rôle** : Filtrer le battage médiatique des créateurs YouTube pour capter les véritables opportunités d'inférence gratuite (crédits de bienvenue, quotas quotidiens, modèles furtifs), neutraliser le risque de dérive des plateformes post-acquisition, et router les tokens qualifiés vers **FreeLLMAPI** (Voie A) ou **Codex-ChatGPT-Web** (Voie B).

---

## 1. Tableau de Bord des Opportunités Analysées

| ID | Opportunité / Modèle | Plateforme | Volume / Quota | Risque & Frictionalité | Durabilité (TTL) | Décision Watch Skill & Vecteur |
|---|---|---|---|---|---|---|
| **OPP-001** | **Claude Opus 5.5 / Sonnet 5.5** | `kito.dev` | 50 $ à 200 $ (plan Pro Plus) | Élevé (Stripe Loop / CB requise) | Fragile (patch Stripe imminent) | **Surveillance** : Voie B (Web / session jetable) |
| **OPP-002** | **DeepSeek V4.1 Flash Obliterated** | `refuseless.com` | 100 crédits dédiés (512K context) | Faible (Google Auth sans CB) | Moyen | **Qualifié** : Voie A (Clé API directe dans FreeLLMAPI) |
| **OPP-003** | **Tencent Hunyuan 4 (HY4)** | `apinex.com` | **20 Millions tokens / jour** (1M context) | Faible (Zero CB, renouvellement 24h) | Élevé / Stable | **PÉPITE OR (Score A+)** : Voie A (Injecté dans FreeLLMAPI) |
| **OPP-004** | **Croton Alpha (Stealth 1M)** | `openrouter.ai` / Killo | Gratuit 7 jours (1M context) | Faible (Compte OpenRouter) | Flash (7 jours) | **Actif Flash** : Voie A (Déjà routable via FreeLLMAPI) |
| **OPP-005** | **Tencent Hunyuan 4 (HY4)** | `workbuddy.ai` | 200-300 crédits / jour | Moyen (App Desktop requise) | Flash (4 au 15 nov.) | **Rejeté** : Remplacé par OPP-003 (APINex offre 20M/j en API pure) |

---

## 2. Les 3 Enseignements Stratégiques du Watch Skill

1. **La supériorité de l'API Pure sur les Apps Desktop Propriétaires** :
   - L'opportunité WorkBuddy (OPP-005) pousse à installer une application desktop fermée pour obtenir quelques centaines de crédits de Hunyuan 4 jusqu'au 15 novembre.
   - L'analyse croisée du Watch Skill a permis de débusquer **APINex (OPP-003)** qui offre **20 millions de tokens par jour du même modèle** directement en API sans installer aucun logiciel tiers !

2. **L'hygiène stricte des "Loops" de facturation Stripe (Kito)** :
   - Le downgrade immédiat sur Kito permet d'obtenir un cycle gratuit d'Opus 5.5, mais expose une carte bancaire.
   - Règle de sécurité Aspace OS : ne jamais engager de moyen de paiement principal. Isoler sur des sessions de test via `Codex-ChatGPT-Web` ou des cartes virtuelles à plafond 0 €.

3. **L'enrichissement permanent de FreeLLMAPI (Port :31415)** :
   - Les clés API gratuites (Refuseless 100 crédits, APINex 20M/j, Exa AI 50$) alimentent directement la chaîne de secours de FreeLLMAPI, garantissant qu'Aspace OS V5 ne tombe jamais à 0 token.

---

## 3. Documents & Références

- [`SKILL_WATCH.md`](SKILL_WATCH.md) : Spécification complète de la grille de qualification à 5 filtres.
- [`registry.json`](registry.json) : Base JSON machine-readable pour l'orchestrateur.
- Dossier [`opportunities/`](opportunities/) : Fiches d'analyse détaillées par vidéo.
