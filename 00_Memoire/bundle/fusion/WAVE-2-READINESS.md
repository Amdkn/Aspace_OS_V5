---
okf_version: "0.2"
type: Specification
title: "Wave 2 Readiness & Decision Gate — Mandat M071 financial-services"
enonce_ref: "00_Memoire/bundle/fusion/FUSION-ENONCE.md"
enonce_sha256: "41889edb9c468ea62ee4641328c0e6f4bac2c618b81da751eebd2af4c05f648d"
---

# WAVE-2-READINESS — Gate de Décision & Mandat d'Exécution (`M071`)

Ce document clôt la Phase 4 (Decision Gate) avant tout portage de code applicatif. Aucun module de Vague 3 (`M069`/`M077`/`M093`) n'est lancé prématurément.

---

## 1. Vérification des 5 Conditions Bloquantes (`ORGAN-CERTIFICATION-CONTRACT.md` §1)

### Condition 1 — Clôture de Cycle 7 (`M074` & `M001`) vérifiée
- Référence code figée à `47220ee350b3941acfc6b609d0c7d39e0a7a511d` sur `fusion/cycle-7`.
- **CI GitHub Actions verte** : `#44733797882` (`01_deletion_suite: rc=0`, `02_modules_lock: rc=0`, `03_factory_checks: rc=0`, **129 sabotages détectés**, `17 FUSIONNÉ / 84 PARTIEL / 17 RETENU / 2 ÉCARTÉ`).
- Limites offline de `M074` et `M001` consignées dans `FUSION-FACTORY-PROTOCOL-V1.md` §1.3 ; branches historiques `fusion/cycle-6` (`aae1566`) et `fusion/cycle-6-audit-fix` (`1768383`) intactes ; `FUSION-ENONCE.md` SHA-256 intact.

### Condition 2 — Contrat de fusion figé pour `M071 financial-services`
- **Module** : `M071 financial-services` (`F-CORPS-06` · `CORPS · Organe K5`, pin `4b7d7e5dbc9de0187eb21c49d7a0de7a2859eed1`, licence Apache-2.0).
- **Cible** : Nouvel organe natif `01_Forkable/FKB07_Money_Maker/01_Trading/aspace_financial_services_organ.py` (ou module K5 dédié raccordé au bus L0 via `consign_measured_l0_evidence`, avec veto `READ_ONLY_VETO_S0 = True` conforme ADR-07 / `DISCLAIMER` FSI interdisant tout conseil d'investissement ou exécution financière autonome).
- **Périmètre inclus (4 sous-systèmes déterministes)** :
  1. `DCFModelValidator` (`validate_dcf.py`) : validation DCF multi-feuilles `.xlsx` (`openpyxl`), 7 erreurs Excel, ratio `terminal_growth < wacc`, plage `WACC`, part `Terminal Value / EV`.
  2. `PitchDeckNumberExtractor` (`extract_numbers.py`) : normalisation d'unités (`T/B/M/K`), filtre d'années `1900..2099`, détection de 9 catégories financières, détection d'incohérences à tolérance `< 5 %`.
  3. `FSICatalogValidator` (`check.py`, `validate.py`, `orchestrate.py` filtrage anti-injection `extract_handoff`, `version_bump.py` règles semver, `quick_validate.py` frontmatter/longueur <= 64 chars & interdiction `< >`).
  4. `M365ManifestBuilder` (`build-manifest.mjs`) : construction URL query vs fragment sensible (`SENSITIVE_KEYS`), échappement XML `&amp;` et validation de motifs clés (`KEYS`) sans appel réseau vers les templates distants.
- **Périmètre explicitement hors exécution live** :
  - Les exemples d'authentification live Microsoft Entra (`examples/python-bootstrap/{app,config,get_tenant_id,mint_dev_token}.py`) et l'appel réseau `client.beta.agents.sessions.steer(...)` d'Anthropic CMA dans `orchestrate.py` ne sont pas présentés comme prouvés live en offline ; seule la logique déterministe d'extraction/validation (`extract_handoff`, configuration, validation schéma) est testée par oracle.

### Condition 3 — Stratégie d'oracle (Phase A) & Spécification des 8 Dimensions
- **Oracle dual** dans `_ORACLE_RUNNER_CODE` :
  - **Sous-oracle Python** exécutant directement les fichiers amont `validate_dcf.py`, `extract_numbers.py`, `quick_validate.py`, `validate.py`, `orchestrate.py`, `version_bump.py` et `check.py` depuis `01_Forkable/FKB07_Money_Maker/01_Trading/financial-services` avant suppression.
  - **Sous-oracle Node v24** exécutant les fonctions pures de `build-manifest.mjs` via module ESM temporaire (même patron éprouvé que `M074`).
- **Bornes & cas limites obligatoires (`THRESHOLD-AND-PARITY-SPEC.md`)** :
  - *DCF* : `adjacent = 0, 0.0001, 0.9999, 1.0` (`0 < adjacent < 1`), `terminal_growth == wacc` vs `wacc - 0.0001`, `wacc = 0.0499, 0.05, 0.20, 0.2001`, `proportion = 0.3999, 0.40, 0.70, 0.80, 0.8001`.
  - *Extract Numbers* : années `1899, 1900, 2099, 2100`, tolérance incohérence `4.99%` vs `5.0%` (`diff_pct < 0.05`), longueur chaîne courte `< 2` avec/sans unité, 11 multiplicateurs dont insensibilité à la casse.
  - *Skills & Governance* : nom skill `64` vs `65` caractères (`len(name) > 64`), chevron `<` / `>` dans description, détection de non-ASCII `.ps1` sans BOM UTF-8 (`b > 0x7F` avec et sans `\xef\xbb\xbf`), séquences JSON valides/injectées dans `extract_handoff` (longueurs `2000`/`2001` pour `event`, `256`/`257` pour `context_ref`, cibles autorisées vs non autorisées), comparaison semver (`(1, 2, 3)` vs `(1, 2, 4)`).
  - *M365 Manifest Builder* : clés sensibles (`azure_api_key`, `gateway_token`, etc.) routées après `#` vs publiques dans `?`, URL ayant déjà `?` vs sans `?`, présence de `#` bloquant par exception, échappement `&` -> `&amp;`.

### Condition 4 — Critères de suppression physique (Phase B)
- Copier le catalogue d'entrée (`plugins`, `managed-agent-cookbooks`, `.claude-plugin`) dans `iso_root / "test_input_m071_catalog"` (hors `01_Forkable/.../financial-services`) pour que `verify_m071()` rejoue l'audit du vrai catalogue réel de 364 fichiers après amputation.
- Ajouter `"01_Forkable/FKB07_Money_Maker/01_Trading/financial-services"` dans `SOURCE_DIRS_TO_DELETE_FOR_TEST`.
- En Phase B, `_force_rmtree` détruit physiquement `financial-services` dans `iso_root` et bloque sur `assert not target.exists()`.

### Condition 5 — Critères d'acceptation de promotion `FUSIONNÉ` (`18/120`)
- Dépendances CI `.github/workflows/foundation-proof.yml` : ajouter `openpyxl` et `jsonschema` à `pip install` et ajouter `01_Forkable/FKB07_Money_Maker/01_Trading/financial-services` au `git submodule update --init --recursive -- ...` avec garde de pin `4b7d7e5dbc9de0187eb21c49d7a0de7a2859eed1`.
- Minimum **`>= 30` nouveaux sabotages dédiés à `M071`** (total suite >= **159** sabotages) couvrant chaque fonction et chaque opérateur de seuil via `_mutate_fn`, plus le rejet de clé parasite.
- Succès 100 % des 3 commandes localement (`rc=0`) et sur GitHub Actions `foundation-proof.yml` (`success`), avec mise à jour cohérente de `REGISTRE-DE-FUSION.md` (`18 FUSIONNÉ / 83 PARTIEL / 17 RETENU / 2 ÉCARTÉ`), `CARTE-DES-PRINCIPES.md`, `DECISIONS.md` et `log.md`.

---

## 2. Mandat d'Exécution Prêt à Lancer — Prochaine Vague (`M071`)

```text
MANDAT D'EXÉCUTION — WAVE 2 CORPS · M071 (`financial-services`)
Branche : fusion/cycle-7 (sur la tête vérifiée du Cycle 8 Readiness)

1. Appliquer le Gate CI : ajouter `openpyxl` et `jsonschema` + initialisation/pin `4b7d7e5dbc9de0187eb21c49d7a0de7a2859eed1` de `01_Forkable/FKB07_Money_Maker/01_Trading/financial-services` dans `.github/workflows/foundation-proof.yml`.
2. Porter les 4 sous-systèmes déterministes de `M071` dans `01_Forkable/FKB07_Money_Maker/01_Trading/aspace_financial_services_organ.py`, raccordé au bus L0 (`consign_measured_l0_evidence`) avec `source_parity_verified == []` en auto-test et `READ_ONLY_VETO_S0 = True`.
3. Ajouter `verify_m071` dans `test_foundation_deletion_suite.py` selon `FUSION-FACTORY-PROTOCOL-V1.md` et `THRESHOLD-AND-PARITY-SPEC.md` (Phase A dual Python + Node v24 sur le vrai catalogue + workbooks `.xlsx` et decks aux bornes exactes `N-1/N/N+1`, Phase B suppression physique de `financial-services`, Phase C parité `==` stricte + >= 30 sabotages dédiés via `_assert_breaks`, `_mutate_fn` et clé parasite + reçu R10 `D-FSI-PARITY`).
4. Garder `M058`, `M066`, `M095` et `M120` en `PARTIEL`. Mettre à jour `REGISTRE-DE-FUSION.md` (`18 FUSIONNÉ`), `CORPS-CARTE.md`, `DECISIONS.md` et `log.md` (append-only LF).
5. Valider localement (3 suites `rc=0`), pousser uniquement sur `fusion/cycle-7`, attendre CI GitHub Actions verte, et préparer le terrain pour `#2 M093 powerbi-to-ai-visuals`.
```
