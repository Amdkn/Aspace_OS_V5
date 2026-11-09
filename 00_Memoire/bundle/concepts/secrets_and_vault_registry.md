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
| `GITHUB_WORKFLOW_PAT` | **Google Apps Script Properties** (`1z3Ffl39...`) | Relais d'événement depuis Apps Script vers GitHub Actions API (`/dispatches`) | Injecté par Muse dans *Propriétés du script* | 90 jours |
| `GCHAT_GROWTH_OS_WEBHOOK` | **Google Apps Script Properties** (`1z3Ffl39...`) | Alertes interactives Card v2 vers Google Chat (`SOB Hub > 01 Growth OS`) | Créé dans Google Chat puis collé dans *Propriétés du script* par Muse | 180 jours |
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
