---
title: "PRD LD01 — Product Requirements Document (A'Space MarketPlace)"
type: concept
status: active
updated: 2026-11-08
tags:
  - prd
  - ld01
  - requirements
  - apis
  - gws-primitive
---

# PRD LD01 : Product Requirements Document — A'Space MarketPlace

## 1. Problème Résolu
Les entreprises et créateurs sont pris au piège entre l'enfermement propriétaire (`x.ai/bot`), le bruit stérile sans livrable (`moltbook`) ou l'esclavage humain à la tâche (`rentahuman`). A'Space MarketPlace livre des résultats garantis produits par des escadrons souverains avec ordinateur virtuel dédié et reprise en main humaine instantanée.

---

## 2. Exigences Fonctionnelles (Functional Requirements)
- **FR-01 : Catalogue Dynamique 6 Catégories** : Exposition des 34 offres découpées en micro-services avec tarification transparente (Setup + Retainer).
- **FR-02 : Moteur de Garantie de Résultat (Outcome Escrow)** : Séquestre des fonds jusqu'à validation de la recette technique et des KPI métiers.
- **FR-03 : Passerelle de Commande n8n / GitHub Actions** : Chaque commande déclenche le workflow `.github/workflows/aspace-n8n-gws-orchestrator.yml`.
- **FR-04 : Console Take Control (OpenMuse)** : Interface web sécurisée pour prise de contrôle à distance sur le navigateur de l'agent.
- **FR-05 : Synchronisation Google Sheets Areas OS** : Enregistrement temps réel des transactions et marges dans l'onglet `B_LD01_BUSINESS_OS`.

---

## 3. Exigences Non-Fonctionnelles (Non-Functional Requirements)
- **NFR-01 : Performance** : Temps de réponse API $< 150\,\text{ms}$ sur Edge Cloudflare.
- **NFR-02 : Coût Marginal Zéro** : Inférence sur compute souverain gratuit (`FreeLLMAPI` + `FreeComputeAPI`).
- **NFR-03 : Disponibilité 99.9%** : Failover multi-modèles et nœuds jetables redondants (VPS, WSL, Cloud Shell).
