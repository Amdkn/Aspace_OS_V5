---
okf_version: "0.2"
type: Specification
title: "Fusion Factory Protocol V1 — Consolidation Cycle 7 et Standard Transversal"
enonce_ref: "00_Memoire/bundle/fusion/FUSION-ENONCE.md"
enonce_sha256: "41889edb9c468ea62ee4641328c0e6f4bac2c618b81da751eebd2af4c05f648d"
---

# FUSION-FACTORY-PROTOCOL-V1 — A'Space OS V5

## 1. Consolidation & Gel de Référence Cycle 7 (`fusion/cycle-7` @ `47220ee`)

Le Cycle 7 sur `fusion/cycle-7` constitue la **référence de certification code** avant ouverture de la Vague 2 suivante. Aucun comportement des organes déjà certifiés n'est modifié durant la mise en place du protocole Cycle 8.

### 1.1 Chaîne des 6 commits Cycle 7 et preuves CI associées

| Ordre | Commit SHA-40 | Contribution | Run GitHub Actions (`ubuntu-latest`) |
|---|---|---|---|
| 1 | `525bdfd5c3ed722cef7befb948c18a46420c41fa` | Porte B CI (`.github/workflows/foundation-proof.yml`), portabilité `/` de `02_Factory/checks.ps1`, création `DECISIONS.md` | `#44676005699` (`success`) |
| 2 | `3d2d9411ecf3dabb2fdcafbe6b29fe78b7b4b239` | Cartographie complète des 62 modules `CORPS` (`CORPS-CARTE.md`, 11 familles `F-CORPS-01..11`) | `#44676580933` (`success`) |
| 3 | `85ea439652e56bdf7981c9bda1bcdf57d6eee9a2` | Vague 1 `CORPS` · `M074 tradingview-indicator-search-mcp-server` (`aspace_trading_copilot_foundation.py` + oracle Node v24 + 20 sabotages) | `#44677865893` (`success`) |
| 4 | `fd8f53fd176ebc191bc295437c63b981c53603ac` | Fermeture des 3 trous de bornes `M074` + bornes/arrondis exacts et 16 sabotages ciblés sur les 7 organes différentiels | Validé cumulativement dans `#44721386435` et `#44733797882` |
| 5 | `2f09268c99464159f3cdce74fcf3a7e7fe3828b9` | Vague 2 `CORPS` · `M001 a0-plugins` (`aspace_plugin_registry_organ.py`, 1 316 lignes, oracle `fa8df85` + 41 sabotages + garde pin CI) | `#44721386435` (`success`, artefact `3 399` o) |
| 6 | `47220ee350b3941acfc6b609d0c7d39e0a7a511d` | Audit indépendant `M001` : fermeture de 4 trous (`START_FROM=-1`, `rename_502_twice`, récupération `size > 0`, retries `dl_retries`) + 8 sabotages `_mutate_fn` (**129 sabotages total**) | `#44733797882` (`success`, `1m59s`, artefact `14627118414`) |

### 1.2 État des branches et invariants gelés (`git ls-remote origin`)

- **`00_Memoire/bundle/fusion/FUSION-ENONCE.md`** : SHA-256 intact `41889edb9c468ea62ee4641328c0e6f4bac2c618b81da751eebd2af4c05f648d`.
- **Branches historiques gelées** : `refs/heads/fusion/cycle-6` (`aae156631212f9759b7d8dff1798e7df015c0933`), `refs/heads/fusion/cycle-6-audit-fix` (`176838374c318f9745598252006fa18fe4651911`), et `refs/heads/master` (`b85cc8ea0974e95837601383c41203409b91a660` au moment du push `47220ee`).
- **Compteurs vérifiés dans `REGISTRE-DE-FUSION.md`** : **17 `FUSIONNÉ`** (9 F8 via `RigInfinity` + 8 différentiels `==`), **84 `PARTIEL`**, **17 `RETENU`**, **2 `ÉCARTÉ`** (`19/120 = 15,8 % < 1/3`), répartis strictement sous **3 Noyaux `ADR-15`** (`ÂME` 29 · `SYSTÈME NERVEUX` 29 · `CORPS` 62).

### 1.3 Audit de clôture `M074` & `M001` et limites offline assumées

Il est interdit de confondre trois niveaux distincts :
1. **Parité fonctionnelle offline** : l'organe natif reproduit à égalité stricte (`==`) les sorties, erreurs, bornes, arrondis et machines à états de la source amont sur fixtures déterministes.
2. **Autonomie opérationnelle (post-suppression)** : l'organe s'exécute et passe 100 % des vérifications après suppression physique (`_force_rmtree`) des répertoires sources dans l'arbre isolé `iso_root`.
3. **Certification opérationnelle live** : l'organe opère contre des endpoints externes réels, authentifications réelles, systèmes de fichiers/OS réels.

| Organe | Preuve acquise au Cycle 7 | Limite offline documentée (honneteté §5.8) |
|---|---|---|
| `M074 tradingview-indicator-search-mcp-server` (`aspace_trading_copilot_foundation.py`) | Oracle Node v24 sur 6 fixtures JSON réelles + SQLite FTS5 + `TradingViewThrottle` (`Math.round`, `Math.ceil`, `is_open`, `dailyBudget`) + UTF-16 `_js_slice` + 28 sabotages + reçu R10 `D-TRADING-PARITY` + veto `READ_ONLY_VETO_S0` | Appels HTTP live vers `tradingview.com` (protection Cloudflare, cookies de session, changements de DOM/API distants) non exercés en ligne en CI ni en sandbox |
| `M001 a0-plugins` (`aspace_plugin_registry_organ.py`) | Oracle amont Python `fa8df85` sur catalogue réel (235 dossiers / 230 indexés), validation YAML/PNG (`20 Ko`/`2 Mo`), `MAX_PLUGINS`, `START_FROM=-1`, 13 scénarios Release, 5 séquences `dl_retries` + 49 sabotages + reçu R10 `D-PLUGINS-PARITY` | Appels REST/GraphQL/Releases GitHub (`api.github.com`, `uploads.github.com`, validation d'URL de captures externes) simulés via `opener` / `request_json_fn` déterministes sans jeton ni mutation réseau live |
| Modules maintenus `PARTIEL` (`M058`, `M066`, `M095`, `M120`) | Gardes explicites dans `test_foundation_deletion_suite.py` | `M058` (`desktop_live=False`), `M066` (~3 200 LOC CDP live), `M095` (pas de runtime `bpy`), `M120` (provenance `D-N048 V0` sans preuve exécutable `K4`/sabotage) |

---

## 2. Pipeline Standard en 5 Étapes — A'Space Fusion Factory

Tout portage futur de `CORPS`, `SYSTÈME NERVEUX` ou `ÂME` suit obligatoirement ce pipeline séquentiel :

1. **`01 — DISCOVERY` (Inventaire & Qualification)** :
   - Inspecter le sous-module au fichier : comptage réel des fichiers/LOC par extension, SHA-40 du gitlink, licence (`MIT` / `Apache-2.0` vs `AGPL-3.0` / `CC BY-NC`), dépendances runtime réelles, graphe d'imports, faisabilité sous `ubuntu-latest` CI.
   - Rattacher sans exception à l'un des 3 Noyaux `ADR-15` (`ÂME`, `SYSTÈME NERVEUX`, `CORPS`) et nommer explicitement toute part hors périmètre ou nécessitant un découpage en lots.
2. **`02 — EXTRACTION` (Contrat & Organe Natif)** :
   - Concevoir le contrat typé et porter le cœur exécutable dans l'organe Python/Rust cible sous `01_Forkable/`, raccordé au bus L0 (`aspace_foundation_kernel.py` via `consign_measured_l0_evidence`).
   - Zéro import runtime vers les répertoires sources supprimables ; zéro auto-test déclarant `source_parity_verified` non vide.
3. **`03 — PARITY` (Oracle Amont & Comparaison Stricte)** :
   - En `Phase A`, exécuter la **vraie source amont** (Node, Python ou binaire compilé) sur des données réelles du dépôt + jeux de bornes `N-1 / N / N+1` (spécifiés dans `THRESHOLD-AND-PARITY-SPEC.md`) -> `oracle_outputs.json`.
   - En `Phase C`, comparer les sorties par **égalité stricte (`==`)** sur dictionnaires/listes désérialisés, sans tolérance aux clés parasites ni normalisation masqueuse (`undefined` vs `null`, ordre des clés triées, unité UTF-16 vs UTF-8, arrondis JS vs Python).
4. **`04 — ANTIFRAGILITY` (Suppression Physique & Sabotages)** :
   - En `Phase B`, supprimer physiquement (`_force_rmtree`) tous les répertoires sources dans `iso_root` et vérifier leur absence avant tout import en `Phase C`.
   - Exécuter la boucle complète de sabotages (`_assert_breaks`) : remplacement de chaque fonction publique/aide déclarée, injection de clé parasite, et mutation chirurgicale `_mutate_fn` des seuils, opérateurs de comparaison (`>`, `>=`, `<`, `<=`, `!=`), constantes d'arrondi et bornes de retry.
   - Rejouer `verify_all()` après restauration complète de tous les sabotages pour garantir l'absence d'effet de bord.
5. **`05 — CERTIFICATION` (R10, Registre Dynamique & Double Preuve)** :
   - Consigner le reçu R10 mesuré via `consign_*_parity_receipt(...)` sur le journal L0.
   - Mettre à jour `REGISTRE-DE-FUSION.md`, `CARTE-DES-PRINCIPES.md`, `DECISIONS.md` et `log.md` (append-only LF).
   - Valider localement **et** sur GitHub Actions (`foundation-proof.yml`) les 3 commandes fail-closed (`test_foundation_deletion_suite.py`, `check-modules-lock.py`, `02_Factory/checks.ps1`) avant toute promotion `FUSIONNÉ`.

---

## 3. Trois Dimensions Transversales

| Dimension | Mécanismes obligatoires | Preuves vérifiables |
|---|---|---|
| **Security** | Provenance signée (`MODULES-LOCK.json` + pins CI dans `foundation-proof.yml`), ségrégation des licences, zéro secret en clair (`checks.ps1 [6/6]`), garde anti-injection (`validate_remote_plugin_name`, `READ_ONLY_VETO_S0`) | `check-modules-lock.py` 12/12 VERT, `checks.ps1` `[6/6]` PASS, tests d'injection/rejet |
| **Observability** | Journal L0 JSONL (`02_Factory/jobs/l0_foundation_journal.jsonl`), `EventJournal` + `R10Ledger`, journal append-only `00_Memoire/bundle/log.md`, artefacts CI (`01_deletion_suite.log`, `02_modules_lock.log`, `03_factory_checks.log`, `return_codes.json`) | Inscription vérifiée `after_lines >= before_lines + N`, artefact CI horodaté par SHA-40 |
| **Lifecycle** | Règle de conservation du gitlink tant que la Phase A exécute la source amont ; évolution `Python -> Hybride Phase 2 -> Rust` ; interdiction de réécriture d'historique ; maintien strict du statut `PARTIEL` si la parité est incomplète ou offline-seulement pour la couche UI/live | Alignement 1:1 `.gitmodules == 101 gitlinks`, trajectoire `fondation-13-1` + `RigInfinity` |

---

## 4. Audit d'Industrialisation & Frontière de Factorisation

Le Cycle 7 démontre qu'il est contre-productif d'imposer une super-classe métier universelle à des organes aux contrats disjoints (un compilateur d'index GitHub `M001`, un client SQLite/FTS5 Node `M074`, un analyseur d'images vidéo `M084` et un moteur FSI/DCF `M071`).

| Catégorie | Ce qui doit être standardisé / factorisable | Ce qui doit rester spécifique par organe |
|---|---|---|
| **Outillage de test (`Phase A/B/C`)** | Helpers `_safe_call`, `_assert_breaks`, `_mutate_fn`, isolement `iso_root`, suppression `_force_rmtree`, contrôle des clés en trop, assertions d'auto-test (`source_parity_verified == []`) | Scripts d'oracles spécifiques au runtime amont (ESM Node v24 `.mjs`, scripts Python CLI, fixtures binaires PNG/XLSX/DuckDB) |
| **Bus L0 & Reçus R10** | `consign_measured_l0_evidence(...)`, format strict `EventJournal` & `R10Ledger` dans `aspace_foundation_kernel.py` | Sémantique métier de l'organe (`READ_ONLY_VETO_S0` pour K5 Trading, hygiène Agent Zero pour K2 Plugins, etc.) |
| **Vérification du Registre & CI** | Calcul dynamique `registry_fusionne == proven_fusionne`, bijection `CARTE <-> REGISTRE`, règle 3 Noyaux `ADR-15`, workflow Porte B fail-closed | Dépendances CI propres à chaque vague (ajout explicite et minimal dans `foundation-proof.yml` + pin SHA du sous-module requis) |
