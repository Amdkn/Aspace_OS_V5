---
title: "Spec LD01 — Spécifications Techniques, Financières et Recette RigInfinity"
type: concept
status: active
updated: 2026-11-08
tags:
  - spec
  - ld01
  - architecture
  - cel
  - riginfinity
---

# SPEC LD01 : Spécifications Techniques & Modèle Financier de la MarketPlace

## 1. Modèle Financier & Unités Économiques (Unit Economics)

- **Panier Moyen d'Entrée (Setup Initial)** : $499 à $2 500 selon la catégorie.
- **Abonnement Récurrent (Retainer Mensuel)** : $199 à $400/mois.
- **Coût Marginal de Production (Tokens & Compute)** : **<$0.50 par livraison**, grâce au routage `FreeLLMAPI` (4.2B tokens gratuits) et `FreeComputeAPI` (GitHub Actions n8n, GAS, Cloudflare Workers).
- **Marge Brute Estimée** : **94 % à 98 %**.

---

## 2. Spécification d'Isolation & Sécurité CEL
Chaque bot ou service commandé est exécuté dans une bulle étanche :
- **Conteneur Dédié** : Image Docker `OpenBot` avec session Chromium propre.
- **Politique CEL (Common Expression Language)** :
  ```protobuf
  request.auth != null && 
  !request.tool.startsWith("env.read") && 
  !request.tool.startsWith("fs.root_delete") && 
  audit.passed_7_of_7 == true
  ```
- **Console Take Control** : `OpenMuse` permet à l'acheteur ou au FDE d'interagir en direct sur le navigateur virtuel en cas de CAPTCHA ou d'approbation humaine.

---

## 3. Critères de Recette & Outcome Escrow
- **Livrable vérifié** avant déblocage de fonds :
  - Audit Lighthouse $\ge 95$ pour les sites.
  - Résolution $\ge 92\,\%$ des cas limites (*unhappy paths*) pour les agents.
  - Enregistrement immédiat dans Google Sheets `B_LD01_BUSINESS_OS` et archivage binaire dans le Bucket Drive 5 To.
