---
title: "ADR-004 : Sanctuarisation Juridictionnelle US (Cincinnati / NKY) & Geo-Fencing d'Exclusion Stricte France / Europe"
type: concept
status: active
updated: 2026-11-09
tags:
  - adr
  - geo-fencing
  - us-jurisdiction
  - cincinnati-nky
  - ld01
  - aspace-marketplace
---

# ADR-004 : Sanctuarisation Juridictionnelle US (Cincinnati / Northern Kentucky) & Geo-Fencing d'Exclusion Stricte France / Europe

## 1. Statut
**ACCEPTÉ & DÉTERMINISTE** (En vigueur immédiatement sur tous les pipelines A'Space OS V5).

---

## 2. Contexte & Déclencheur
L'opérateur souverain **Amadou Kone (`human:amdkn`)** opère et réside dans la région métropolitaine de **Cincinnati, Ohio / Northern Kentucky (NKY)**, États-Unis.

Tenter d'acquérir ou de facturer des clients en France ou dans l'Union Européenne depuis les États-Unis introduit des frictions asymétriques toxiques :
1. **Fardeau Réglementaire Extraterritorial** : RGPD européen, directives sur les services numériques, cookies banners et surcoûts juridiques de mise en conformité transfrontalière.
2. **Complexité Fiscale et Bancaire** : TVA intracommunautaire (MOSS), doubles retenues à la source, conversions de devises EUR/USD avec commissions bancaires destructrices de marge.
3. **Friction Temporelle (Fuseau Horaire)** : Décalage horaire de 6 heures (EST vs CET) nuisant à la réactivité opérationnelle et brisant le sanctuaire homéostatique `LD03/LD04` d'Amadou Kone.
4. **Pouvoir d'Achat Inférieur** : Le marché B2B américain (Midwest & US National) dispose de budgets de services informatiques et d'automatisation 2,5 à 4 fois plus élevés que le marché français, en dollars USD natifs.
5. **Véhicule Maître LD01** : Le pôle économique LD01 est désormais exclusivement incarné par **`A'Space MarketPlace`** (Projet Picard de Book). Le label historique « OMK Office » est rétrogradé au rang d'archive/composant et banni des communications sortantes.

---

## 3. Décision d'Architecture
1. **Sanctuarisation Territoriale US Domestic & Regional (Cincinnati / NKY / US B2B)** :
   - 100 % des campagnes d'acquisition, prospections et contrats de service d'**A'Space MarketPlace** ciblent exclusivement des entités enregistrées aux États-Unis (prioritairement dans l'écosystème régional de Cincinnati / Northern Kentucky, Ohio Valley, et les marques nationales US).
2. **Geo-Fencing d'Exclusion Déterministe France & Europe (CEL Rule)** :
   - Toute tentative d'onboarder, de prospecter ou d'inscrire dans le registre `B_LD01_BUSINESS_OS` un compte situé en France ou dans l'Union Européenne est **rejetée déterministement avec `exit 2`** par les hooks pré-exécution.
   - Les domaines `.fr`, `.eu` et adresses IP européennes sont filtrés en amont des pipelines de prospection GTME.
3. **Unité Monétaire Exclusive : USD ($)** :
   - Tous les contrats, abonnements et garanties d'A'Space MarketPlace sont stipulés et encaissés en dollars américains ($ USD).

---

## 4. Conséquences
- **Positives** :
  - Zéro exposition au RGPD européen.
  - Facturation directe US sous droit de l'Ohio / Kentucky / Delaware.
  - Synergie immédiate avec l'écosystème local de Cincinnati / NKY (Hub logistique mondial Amazon CVG / DHL, grands sièges Kroger, P&G alumni, TQL, cabinets juridiques KMK / Taft / Frost Brown Todd).
  - Suppression complète du décalage horaire.
- **Négatives / Trade-offs** :
  - Abandon total des opportunités commerciales en France et en Europe tant que l'opérateur réside à Cincinnati / NKY.

---

## 5. Règle CEL d'Application Déterministe
```protobuf
// Politique CEL intégrée dans les hooks A'Space MarketPlace LD01
prospect.country == "US" && 
!prospect.location.containsAny(["France", "Paris", "Europe", "EU", ".fr", ".eu"]) && 
marketplace.brand == "Aspace_MarketPlace"
```
