# Skill Watch — Radar de Filtrage & Qualification d'Inférence YouTube

> **Doctrine Aspace OS V5** : *"Au-delà du matraquage des YouTubers et de la volatilité des plateformes post-vidéo, extraire le pur signal de calcul souverain."*

---

## 1. La Mission du Skill Watch

Les créateurs de contenu YouTube multiplient les vidéos racoleuses (*"Claude Opus 5.5 100% FREE"*, *"Nouvelle faille Stripe"*, *"Modèle secret 1M tokens gratuit"*). Ces annonces génèrent un afflux massif d'utilisateurs qui pousse les plateformes à :
1. Fermer les inscriptions gratuites ou durcir les conditions dans les 48 à 72 heures.
2. Dégrader les quotas ou bannir les cartes bancaires virtuelles / astuces de downgrade.
3. Remplacer subrepticement les modèles annoncés par des versions plus légères (downgrade silencieux).

Le **Skill Watch** a pour rôle d'agir comme un sas étanche et un filtre d'hygiène avant toute tentative d'injection dans **Aspace OS V5**.

---

## 2. Grille de Qualification en 5 Filtres

Pour chaque vidéo ou astuce détectée, le Skill Watch applique la grille suivante :

```
             [ Source Brute YouTube / Vidéo ]
                           │
                           ▼
 ┌──────────────────────────────────────────────────┐
 │ FILTRE 1 · Déduplication FLA / CCW               │
 │  Déjà présent dans FreeLLMAPI (:31415) ?         │ ── Oui ──► [ REJET : Déjà couvert ]
 │  Déjà accessible via Codex-ChatGPT-Web ?        │
 └─────────────────────────┬────────────────────────┘
                           │ Non (Nouvelle opportunité)
                           ▼
 ┌──────────────────────────────────────────────────┐
 │ FILTRE 2 · Authenticité du Modèle                │
 │  Véritable poids/modèle ou rebrand marketing ?    │ ── Faux ─► [ CLASSEMENT : Biais Clickbait ]
 │  Vérification par question miroir / tokenomics   │
 └─────────────────────────┬────────────────────────┘
                           │ Modèle authentique
                           ▼
 ┌──────────────────────────────────────────────────┐
 │ FILTRE 3 · Risque & Frictionalité                │
 │  Type A : Vraie clé API gratuite sans CB         │ ── Score A (Priorité Max)
 │  Type B : Crédit d'accueil limité (ex: $50 Exa)   │ ── Score B (Haute Valeur)
 │  Type C : Loop Stripe 0€ / Annulation immédiate  │ ── Score C (Fragile / Surveillance)
 └─────────────────────────┬────────────────────────┘
                           │
                           ▼
 ┌──────────────────────────────────────────────────┐
 │ FILTRE 4 · Durabilité & TTL Post-Acquisition     │
 │  Estimation du temps de survie de l'offre :      │
 │  - FLASH (< 7 jours)                             │
 │  - MOYEN TERME (1 mois / cycle)                  │
 │  - STABLE (modèle pérenne freemium)              │
 └─────────────────────────┬────────────────────────┘
                           │
                           ▼
 ┌──────────────────────────────────────────────────┐
 │ FILTRE 5 · Vecteur d'Injection Aspace OS         │
 │  - Voie A : Endpoint API direct -> FreeLLMAPI    │
 │  - Voie B : Interface Web -> Codex-Web + REA     │
 └──────────────────────────────────────────────────┘
```

---

## 3. Protocoles d'Injection

### Voie A : Passerelle Directe FreeLLMAPI
Applicable dès qu'une plateforme fournit :
- Une clé API (Bearer Token).
- Une URL de base compatible `OpenAI` (`/v1/chat/completions`) ou `Anthropic` (`/v1/messages`).
- Configuration automatique dans `01_Forkable/FKB01_Inference/03_Inference_FreeCloud/freellmapi`.

### Voie B : Automatisation Web Codex-ChatGPT-Web + API-Anything (FKB04)
Applicable lorsque la plateforme n'offre qu'un Playground Web ou une application Desktop :
- `API-Anything` reverse-engineere les requêtes réseau du client web.
- `Codex-ChatGPT-Web` embarque la session avec le bouclier anti-télémétrie `aspace-telemetry-shield.cjs`.
- Aucune fuite de données ni de blocage d'empreinte navigateur.
