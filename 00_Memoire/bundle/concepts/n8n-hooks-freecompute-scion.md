---
title: "GitHub as n8n Primitive, Deterministic Hooks (exit 2), FreeComputeAPI & Anthropic Scion"
type: concept
status: active
updated: 2026-11-08
tags:
  - hooks
  - n8n
  - freecomputeapi
  - gws-cli
  - scion
  - life-os
---

# GitHub as n8n Primitive × Deterministic Hooks × FreeComputeAPI × Scion

## 1. Loi de Cole Medin : Hooks Déterministes (`exit 0` / `exit 2`)

Plutôt que de diluer l'attention du LLM dans des fichiers de règles géants, [`02_Factory/hooks/aspace_deterministic_hooks.py`](file:///c:/Users/amado/Aspace%20OS%20V5/02_Factory/hooks/aspace_deterministic_hooks.py) applique un contrôle d'exécution déterministe :
- **`pre-tool` (`PreToolUse`)** :
  - Bloque (`exit 2`) toute lecture directe de `.env`, `.pem`, `id_rsa`.
  - Bloque (`exit 2`) toute suppression récursive sur les piliers racines (`00_Memoire`, `01_Forkable`, `02_Factory`).
  - Applique le **File Coupling** (`COUPLED_FILES_MAP`) : toute édition dans `01_Forkable/FKB00_Runtime/00_A0_Core/`, `01_Forkable/FKB01_Inference/03_Inference_FreeCloud/`, `00_Memoire/bundle/areas_os/` ou `02_Factory/04_Security_OWASP_RigInfinity/` exige d'avoir lu son contrat couplé durant la session (`00_Memoire/.session_read_files.json`).
- **`stop` (`Stop`)** :
  - Exécute `02_Factory/checks.ps1` (`7/7 PASS` obligatoire, sinon `exit 2`).
  - Exécute `gh codespace stop --all` pour couper tout GitHub Codespace oublié en fin de session.

## 2. Les 5 Familles de Nœuds n8n dans GitHub + Google Workspace CLI (`gws`)

[`02_Factory/gws_lifeos_n8n_dispatcher.py`](file:///c:/Users/amado/Aspace%20OS%20V5/02_Factory/gws_lifeos_n8n_dispatcher.py) et [`.github/workflows/aspace-n8n-gws-orchestrator.yml`](file:///c:/Users/amado/Aspace%20OS%20V5/.github/workflows/aspace-n8n-gws-orchestrator.yml) transforment GitHub en moteur n8n complet structuré selon les 5 familles canoniques :
1. **Trigger Nodes** : `workflow_dispatch`, `repository_dispatch` (`gws_webhook_trigger`, `supabase_event`, `make_activepieces_bridge`), et `schedule` (`0 6,21 * * *` hors sanctuaire nocturne `A1-BETH` `00h00-05h00`).
2. **Core Nodes** : Routage `Switch` par vaisseau `Life OS` et génération du reçu cryptographique `R10` (`CANARY_RECEIPT`).
3. **App Nodes (`gws` CLI)** :
   - `21_Ikigai_Orville` $\rightarrow$ Google Slides (`gws slides presentations`)
   - `22_Wheel_Discovery` $\rightarrow$ Google Sheets (`gws sheets spreadsheets.values`)
   - `23_12WY_SNW` $\rightarrow$ Google Calendar (`gws calendar events`)
   - `24_PARA_Enterprise` $\rightarrow$ Google Drive & Docs (`gws drive files`)
   - `25_GTD_Cerritos` $\rightarrow$ Google Tasks (`gws tasks tasklists`)
   - `26_DEAL_Protostar` $\rightarrow$ Google Chat (`gws chat spaces`)
4. **AI Cluster Nodes** : `A0 Amadeus` connecté à `FreeLLMAPI` (`127.0.0.1:31415`) et au bus mémoire `00_Memoire/shared_brain/memory.jsonl` + `00_Memoire/egm_missions.db`.
5. **Community Nodes & Scion** : [`02_Factory/github-app-manifest.json`](file:///c:/Users/amado/Aspace%20OS%20V5/02_Factory/github-app-manifest.json) (`Aspace-Factory-App`) appliquant les principes **Scion** d'Anthropic (*Sparse Checkouts* pour éviter de cloner les 66 sous-modules en CI et commits GraphQL `createCommitOnBranch`).

## 3. `FreeComputeAPI` : Routeur Atomique des Quotas Mensuels Gratuits

[`01_Forkable/FKB00_Runtime/00_A0_Core/aspace_freecompute_router.py`](file:///c:/Users/amado/Aspace%20OS%20V5/01_Forkable/FKB00_Runtime/00_A0_Core/aspace_freecompute_router.py) fédère les 8 fournisseurs de compute et d'automatisation gratuits :
- **Cloudflare Workers (`aspaceos.tech`)** : 100 000 req/jour.
- **Upstash Box** : 10 boxes concurrentes, 5h CPU/mois, auto-pause.
- **Cloudroom** : 2 992 Cloud Credits.
- **Google Cloud Shell (`antigravity-a0`)** : 50h/semaine.
- **GitHub Actions & `Amdkn/FreeVPS`** (`01_Forkable/FKB01_Inference/03_Inference_FreeCloud/FreeVPS`) : runners publics + `timeout-minutes: 15`.
- **GitHub Codespaces** : 120 core-hours/mois protégés par `purge_stale_codespaces()`.
- **Activepieces (1 000 tasks/mois MCP) & Make.com (1 000 ops/mois)**.
- **Ngrok (`https://local-other.internal`), Cloudflare Zero Trust & Tailscale**.
