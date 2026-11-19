---
okf_version: "0.2"
type: Specification
title: "DDD-CONTRATS-COMMUNS — Contrats L0 d'Interconnexion Alignés sur fondation-13-1"
enonce_ref: "00_Memoire/bundle/fusion/FUSION-ENONCE.md"
enonce_sha256: "41889edb9c468ea62ee4641328c0e6f4bac2c618b81da751eebd2af4c05f648d"
---

# DDD-CONTRATS-COMMUNS — Couche Fondamentale L0

Conformément à l'ÉNONCÉ §1 (4) et à l'**`ADR-13`**, la Fondation A'Space interconnecte ses **3 Noyaux Fondamentaux (`ÂME` / `SYSTÈME NERVEUX` / `CORPS`)** — rattachant les organes `K1..K5` et le Bus L0 — au niveau le plus fondamental par des contrats uniques strictement alignés **octet pour octet** sur les validateurs Rust zéro-dépendance de `01_Forkable/FKB00_Runtime/00_A0_Core/fondation-13-1/` (`src/lib.rs`, `src/router.rs`, `src/memory.rs`) et invoqués/doublés en **Phase 2 Hybride (`Python → Hybride → Rust`)** par `01_Forkable/FKB00_Runtime/00_A0_Core/aspace_foundation_kernel.py`.

---

## 1. Contrat C1 — Journal d'Événements Unifié (`EventJournal`)

- **Autorité source** : `fondation-13-1/src/router.rs` (binaire `route-dispatch`, constantes `DISPATCH_KEYS`, `EVENT_TYPES`, `FUNCTIONS_13`).
- **Format physique** : fichier JSON Lines (`*.jsonl`), encodage UTF-8, **strictement append-only**.
- **Schéma d'une soumission (`DISPATCH_KEYS`, 9 clés exactes — `R1`)** :
  ```json
  {
    "actor_from": "structurer | judge | executor | router | receiver | verifier | decider | discoverer | observer | interfacer | fluer | memorizer | fabricator",
    "actor_to": "structurer | judge | executor | router | receiver | verifier | decider | discoverer | observer | interfacer | fluer | memorizer | fabricator",
    "at": "ISO-8601 avec offset (R5, jamais futur)",
    "design_ref": "chemin ou id de design signé (R2)",
    "dispatch_id": "identifiant du dispatch",
    "event_id": "EVT-AAAAMMJJ-NNN (R3, date valide et unique)",
    "payload": "verbe + objet (>= 2 mots nommant l'acte, R6)",
    "proof": ["obligatoire et non vide pour dispatch_ack / judgment_rendered (R7)"],
    "type": "closure_pulse | correction | dispatch_ack | dispatch_relayed | dispatch_typed | fact_recalled | judgment_rendered | judgment_requested | merge_executed | pulse"
  }
  ```
- **Schéma inscrit (10 clés)** : l'inscripteur assigne `seq = numéro_de_ligne` (1-indexed). Toute soumission portant déjà `seq` est rejetée (**R1**).
- **Règles ordonnées `R1 → R2 → R3 → R4 → R5 → R6 → R7 → R8`** :
  - **R4** : `actor_from` et `actor_to` doivent appartenir aux 13 fonctions canoniques `FUNCTIONS_13`, jamais un nom de session isolée.
  - **R8** : `dispatch_relayed` suit `dispatch_typed` ou `judgment_requested` ; `dispatch_ack` suit `dispatch_typed` ; `judgment_rendered` suit `judgment_requested`.

---

## 2. Contrat C2 — Reçus Cryptographiques `R10` (`R10Receipt`)

- **Autorité source** : `fondation-13-1/src/lib.rs` (binaire `r10-receive`, constantes `R10_KEYS`, `R10_SCHEMA`, règles `V1 → V8 → V7 → V2 → V3 → V4 → V5 → V6`).
- **Schéma JSON exact (`R10_KEYS`, 9 clés exactes — `V1`)** :
  ```json
  {
    "entry_id": "G-AAAAMMJJ-NNN (date valide et unique, V7)",
    "issuer": "émetteur du reçu (ex: Kernel K5 / Ryan)",
    "mission_id": "identifiant unique de mission non vide (V2)",
    "observed_at": "ISO-8601 avec offset, non futur (V4)",
    "proof": ["au moins 1 preuve vérifiable non vide (V5)"],
    "recorded_at": "ISO-8601 UTC +00:00 posé à la consignation (jamais repris du dépôt)",
    "schema": "aspace.r10-receipt.v1 (V8)",
    "sha": "<40 caractères hex [0-9a-f] résolvant dans Git> (V3)",
    "summary": "résumé non vide nommant le livrable (#PR ou SHA >= 7 hex) (V6)"
  }
  ```
- **Invariants** :
  - **V7 + V2** : un `entry_id` ou un `mission_id` déjà consigné ne peut jamais être réécrit.
  - **V3** : le SHA court est rejeté ; seuls les 40 caractères hexadécimaux résolvant sont acceptés.
  - **V6** : tout reçu sans mention de livrable (`#<num>` ou SHA ≥ 7 hex) est rejeté.

---

## 3. Contrat C3 — Statut Épistémique de la Mémoire (`EpistemicCitation`)

- **Autorité source** : `fondation-13-1/src/memory.rs` (binaire `recall-fact`, règles `M1 → M7 → M2 → M3 → M4 → M5 → M6 → M8`).
- **Format de citation vérifiable (`M1`)** :
  - En-tête portant `**Fonction :**`, `**Date de la citation :**`, `**Fait demandé :**`, `**Mécanisme :**`.
  - Section `## Citation` portant les 4 champs obligatoires : `**Énoncé :**`, `**Source :**`, `**Date :**`, `**Statut :**`.
  - Quatre sections obligatoires : `## Vérification au fichier`, `## Corroborations et contradictions`, `## Ce que cette citation ne prouve pas`, `## Ce que la fonction n'a pas fait`.
- **Les 6 statuts exclusifs (`STATUSES`)** : `vérifié`, `consigné`, `périmé`, `contredit`, `absent`, `à venir`.
- **Invariants (`M2–M8`)** :
  - **M7** : la mémoire ne juge pas (`JUDGMENT_MARKERS` interdits sauf négation sur la même ligne ; section « Ce que la fonction n'a pas fait » non vide).
  - **M2 / M3** : la source existe au fichier et la ligne relue contient l'énoncé normalisé ; la date citée figure sur la ligne source (sinon `"inconnue"`).
  - **M4 / M5** : `à venir` exige `cited > today`, `périmé` exige `cited < today` + marqueur de déplacement ; toute corroboration divergente impose le statut `contredit` et le listage explicite des versions divergentes.
  - **M6 / M8** : rejet du fait fautif planté ; limites nommées dans section dédiée non vide.
- **Pont Shared Brain (`K4`)** : `neuro_symbolic_bridge.py` extrait dynamiquement entités et relations acycliques vers `00_Memoire/shared_brain/memory.jsonl` (verrou `O_EXCL`) sans jamais court-circuiter `validate_citation`.

---

## 4. Contrat C4 — Fibre, Capacité & Cycle d'Hibernation (`FiberContract`)

- **Autorité source** : `aspace-fiber-host` (`src/host.ts`) + `RigInfinity` (`session_store.rs`, `rap.rs`) + `MODULES-LOCK.json`.
- **État actuel de l'intégration** : `PARTIEL` sur le câblage Unix socket `cordis_socket` (`RigInfinity`) et la dépendance locale `file:../cordis/*` dans `aspace-fiber-host/package.json`.
- **Invariants** : unicité globale `capabilities_owned`, hibernation Pure-Data entre tours (`session_store.rs`), nettoyage LIFO réversible.

---

## 5. Contrat C5 — Protocole de Test de Suppression (`DeletionProof`)

- **Autorité source** : ÉNONCÉ §1 (3) — *« la source d'un module FUSIONNÉ peut quitter l'arbre actif sans perte de capacité (test de suppression, jugé par un juge externe) »*.
- **Conditions vérifiées** :
  1. Absence réelle ou suppression physique vérifiée du répertoire source du module dans un clone de test **et** preuve d'exécution de sa capacité portée dans la Fondation (`test_foundation_deletion_suite.py`, `cargo test` sur `fondation-13-1` & `RigInfinity`, organes natifs `FKB04`/`FKB02`/`M117`/`M118`).
  2. Retrait des gitlinks `.gitmodules` effectué par famille **après** verdict favorable du Juge externe (règle Cycle 4).
  3. Validation par le Juge-comparateur externe en lecture seule sur clone neuf.
