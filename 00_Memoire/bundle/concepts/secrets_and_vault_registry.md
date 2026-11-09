---
title: "Registre des Secrets, Vaults & Politique de Rotation (A'Space OS V5)"
type: concept
status: active
updated: 2026-11-09
tags:
  - secrets-management
  - security
  - vault
  - github-secrets
  - apps-script-properties
  - rotation-policy
  - zero-cleartext
---

# Registre des Secrets, Coffres-Forts (Vaults) & Politique de Rotation

> **Règle de Sécurité Fondamentale (Gate Déterministe 6/6)** :  
> **ZÉRO secret en clair dans le code source ou la documentation Git.**  
> Tout secret est stocké exclusivement dans les coffres-forts natifs dédiés (GitHub Secrets, Google Apps Script Script Properties, OS Keyring local).  
> Ce registre trace l'inventaire des clés, leur emplacement, leur finalité et leur calendrier de rotation.

---

## 1. Inventaire des Coffres-Forts (Vaults) & Variables Sécurisées

| Clé de Secret | Coffre de Stockage (Vault) | Portée & Service Associé | Mécanisme de Provisionnement | Fréquence de Rotation |
|---|---|---|---|---|
| `ASPACE_WORKFLOW_PAT` | **GitHub Secrets** (`Amdkn/Aspace_OS_V5`) | Repository Dispatch & Orchestration GitHub Actions (`aspace-n8n-gws-orchestrator.yml`) | Provisionné via `gh secret set` par Muse / A0 | 90 jours |
| `GITHUB_WORKFLOW_PAT` | **Google Apps Script Properties** (`1z3FfI39...`) | Relais d'événement depuis Apps Script vers GitHub Actions API (`/dispatches`) | Injecté par Muse dans *Propriétés du script* | 90 jours |
| `GCHAT_GROWTH_OS_WEBHOOK` | **Google Apps Script Properties** (`1z3FfI39...`) | Alertes interactives Card v2 vers Google Chat (`SOB Hub > 01 Growth OS`) | Créé dans Google Chat puis collé dans *Propriétés du script* par Muse | 180 jours |
| `ASPACE_GAS_HMAC_SALT` | **Google Apps Script Properties** + **GitHub Secrets** | Sel cryptographique HMAC-SHA256 pour valider l'intégrité des webhooks d'entrée | Généré aléatoirement (64 caractères hex) | 180 jours |
| `GWS_CREDENTIALS_JSON` | **GitHub Secrets** (`Amdkn/Aspace_OS_V5`) | Identifiants OAuth / Service Account pour `gws` CLI dans GitHub Actions | Provisionné lors de la configuration Google Cloud | 365 jours |
| `SUPABASE_SERVICE_ROLE_KEY` | **GitHub Secrets** (`Amdkn/Aspace_OS_V5`) | Accès administratif persistant base de données WorkGraph & State | Export Supabase Dashboard vers GitHub Secret | 180 jours |

---

## 2. Procédure Automatisée de Rotation par Muse (A0 24/7)

1. **GitHub PAT** :
   - Muse ouvre `https://github.com/settings/tokens` dans son navigateur actif.
   - Génère un Personal Access Token (classic ou fine-grained) avec les permissions : `repo`, `workflow`.
   - Met à jour le secret de dépôt GitHub : `gh secret set ASPACE_WORKFLOW_PAT`.
   - Met à jour la propriété dans Google Apps Script : `GITHUB_WORKFLOW_PAT`.

2. **Webhook Google Chat** :
   - Muse navigue dans `chat.google.com` $\rightarrow$ Espace `SOB Hub > 01 Growth OS` (ou `App, tech, collect...`).
   - *Paramètres de l'espace* $\rightarrow$ *Applications et intégrations* $\rightarrow$ *Gérer les webhooks*.
   - Génère l'URL du webhook entrant et met à jour `GCHAT_GROWTH_OS_WEBHOOK` dans Apps Script.

3. **Audit de Conformité Déterministe** :
   - Exécution de `02_Factory/checks.ps1` (Gate 6/6 `Secret Scanning Guard`) pour vérifier qu'aucune chaîne de secret n'a été committée dans le dépôt.

## 4. État vérifié au 2026-11-09 — déploiement Option 2 (GAS Gateway)

- `GITHUB_WORKFLOW_PAT` : POSÉ dans les Propriétés du script du projet `1z3FfI39...` le 2026-11-09. Token « Aspace-GAS-Gateway », scope `repo` uniquement, créé 2026-11-09, **expire le dimanche 7 février 2027** — rotation due avant cette date. Valeur jamais consignée ici.
- `ASPACE_GAS_HMAC_SALT` : POSÉ le 2026-11-09 (64 caractères hex, généré pour ce projet). Aucune expiration.
- `GCHAT_GROWTH_OS_WEBHOOK` : **NON CRÉÉ** — bouton « Ajouter des webhooks » désactivé dans l'espace « SOB Hub > 01 Growth OS » (AAQAnk6DxXM), mention « La gestion du webhook est limitée » (restriction côté Google, piste console Admin Workspace). Aucune URL inventée. La passerelle fonctionne sans lui (alerte simulée) ; le dispatch GitHub est réel (test 2026-11-09 09:37:40 : HTTP 204).
- `ASPACE_WORKFLOW_PAT` (GitHub Secrets) : PRÉSENT (vérifié 2026-11-09T14:25:58Z).
- `GWS_CREDENTIALS_JSON`, `SUPABASE_SERVICE_ROLE_KEY` : listés au §1 comme prévus, **non provisionnés** — absents des secrets du dépôt au 2026-11-09 (vérifié).
- Flux Studio « A'Space OS V5 — B_LD01 → GAS Gateway » : ACTIVÉ le 2026-11-09 à 09:38. Web App v1 : https://script.google.com/macros/s/AKfycbwJKpZADmqHuSYXg1pooZfILGe7PyyGgUTRoEhAcz9vg-2YsUvHS7BlWzqvOVJ5CV1LGA/exec
