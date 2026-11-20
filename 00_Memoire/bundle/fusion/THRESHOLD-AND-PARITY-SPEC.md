---
okf_version: "0.2"
type: Specification
title: "Threshold & Behavioral Parity Spec — 8 Dimensions Obligatoires"
enonce_ref: "00_Memoire/bundle/fusion/FUSION-ENONCE.md"
enonce_sha256: "41889edb9c468ea62ee4641328c0e6f4bac2c618b81da751eebd2af4c05f648d"
---

# THRESHOLD-AND-PARITY-SPEC — Protocole des 8 Dimensions

## 1. Exigences Normatives sur 8 Dimensions

Tout organe candidat au statut `FUSIONNÉ` doit démontrer une parité comportementale exacte (`==` contre l'oracle amont) et une détection de sabotage sur chacune des 8 dimensions suivantes applicables à son contrat :

| # | Dimension | Cas obligatoires à couvrir | Sabotage de mutation exigé |
|---|---|---|---|
| **1** | **Bornes (`N-1, N, N+1`)** | Tester systématiquement `x = N - 1`, `x = N`, `x = N + 1` (et valeurs négatives/nulles `-1, 0, 1`) sur chaque comparaison `>`, `>=`, `<`, `<=`, `==` | Muter l'opérateur (`>` ↔ `>=`, `<` ↔ `<=`, `>` ↔ `!=`) ou décaler la constante (`N` ↔ `N-1`) via `_mutate_fn` ou surcharge dédiée |
| **2** | **Arrondis (`Floor, Ceil, Round, Banker, Epsilon`)** | Tester les moitiés exactes (`0.5` : JS `Math.round(x)` = `floor(x + 0.5)` vs Python `round()` banker's rounding sur entiers pairs), `math.ceil(60000/60000)` vs `60001/60000`, epsilons flottants (`±0.0001` autour de `0.002`, `0.5`, `0.25`) | Saboter en remplaçant `Math.round` par `math.floor` **et** par Python `round()`, ou décaler l'epsilon/floor de test |
| **3** | **Types & Encodages (`Null, Undefined, Empty, Missing, UTF-16`)** | Distinguer clé absente vs `null`/`None` vs `""` vs `[]`, chaînes UTF-8 avec astérisques/émojis hors BMP (`\U0001F600` = 2 code units UTF-16 JS vs 1 codepoint Python), tri canonique des clés | Remplacer `_js_slice` UTF-16 par slicing Python `[:end]`, injecter une clé parasite, confondre `{}` vs `None` |
| **4** | **Retries & Pacing (`0, 1, Max-1, Max, Max+1`)** | Vérifier succès immédiat (`0` retry), échec transitoire récupéré à la dernière tentative autorisée (`Max`), épuisement à `Max+1`, et exactitude du décompte `sleeps` / `elapsed == gap` vs `gap - 1` | Muter `attempt == 2` -> `attempt == 1`, `attempt < 3` -> `attempt < 2`, `>` -> `>=` sur le cooldown/gap |
| **5** | **Erreurs (`HTTP, Réseau, Exceptions`)** | Tester le code HTTP juste sous le seuil de retry (`499`), les seuils exacts de retry (`500`, `429`), les fallbacks `405`/`501` (`HEAD` -> `GET Range`), `404` toléré vs fatal, et `OSError` réseau | Muter `>= 500` -> `> 500` / `>= 499`, supprimer `or e.code == 429`, supprimer la gestion fallback `405`/`501` |
| **6** | **Fichiers & Payloads (`Vide, Limite, Limite+1, Corrompu`)** | Tester payload de `0` octet (`b""`), taille exacte (`N` octets ou `N` caractères), dépassement `N+1`, YAML/JSON invalide ou de mauvais type (liste au lieu de mapping), image rectangulaire vs carrée | Muter `size > 0` -> `size >= 0`, diminuer les bornes de 1 (`20479`, `1999`, `49`, `499`) ou inverser la garde géométrique |
| **7** | **Isolation (`Suppression physique Phase B`)** | Copier le sous-arbre dans `iso_root`, exécuter l'oracle en Phase A, détruire physiquement les sources par `_force_rmtree`, asserter `not exists()`, importer l'organe sans dépendance amont | Garde permanente d'existence avant Phase C (`assert not (iso / _gone).exists()`) |
| **8** | **Antifragilité (`Mutation & Clés parasites`)** | Exécuter `_assert_breaks` sur chaque fonction/méthode déclarée, chaque seuil/arrondi/retry muté via `_mutate_fn`, et chaque dictionnaire de sortie pollué par une clé parasite | Exiger `assert broke` pour 100 % des sabotages et re-exécuter `verify_all()` à la fin après restauration |

---

## 2. Validation Croisée Phase 3 — Référentiel des 129 Sabotages Cycle 7

L'audit du corpus Cycle 7 (`test_foundation_deletion_suite.py`, suite **7/7 PASS**, CI `#44733797882`) valide les 8 dimensions sur les **8 organes différentiels (`129` sabotages détectés à 100 %)** :

### 2.1 Référence `M001 a0-plugins` (`aspace_plugin_registry_organ.py` — 49 sabotages)

| Fonction / Constante | Ligne | Condition exacte | Cas `N-1 / N / N+1` vérifiés en parité `==` | Sabotage détectant la régression |
|---|---|---|---|---|
| `resolve_plugin_names` | L198 | `if start_idx > 0:` | `START_FROM = "-1", "0", "1", "2", "bad"` | `M001:resolve_start_from_ne_zero` (`> 0` -> `!= 0`) |
| `resolve_plugin_names` | L203 | `len(plugin_names) > max_plugins` | `MAX_PLUGINS=3` sur 3 plugins (OK) vs 4 plugins (Erreur) | `M001:resolve_max_plugins_ge` (`>` -> `>=`) |
| `read_plugin_yaml_text_strict` | L287 | `len(raw_text) > 2000` | `2000` chars (OK) vs `2001` chars (Erreur), YAML invalide/liste | `M001:INDEX_YAML_MAX_CHARS_1999` |
| `validate_fields` | L447-465 | `50`, `500`, `MAX_TAGS=5`, `MAX_SCREENSHOTS=5` | `50/51`, `500/501`, `5/6` tags, `5/6` screenshots | `M001:TITLE_MAX_LEN_49`, `DESCRIPTION_MAX_LEN_499`, `MAX_TAGS_4`, `MAX_SCREENSHOTS_4` |
| `validate_screenshot_url` | L380-408 | `> 2*1024*1024` + fallback `HEAD 405` -> `GET Range` | `2 Mo` exact (OK), `2 Mo + 1` (HEAD & GET 405), `.gif` rejeté | `M001:SCREENSHOT_MAX_BYTES_minus1`, `M001:validate_screenshot_url` |
| `validate_thumbnail` | L471-485 | `> 20*1024` + `width != height` + `len > 1` | PNG carré exact `20 480` o vs `20 481` o vs `16x12` vs 2 fichiers | `M001:THUMBNAIL_MAX_BYTES_20479`, `M001:validate_thumbnail` |
| `_pub_rename_asset` | L923, L935 | `range(3)` / `if attempt == 2: raise` | `rename_502` (1 échec) + `rename_502_twice` (2 échecs 502, succès à la 3e tentative) | `M001:_pub_rename_asset_max_2` (`attempt == 2` -> `1`) |
| `publish_index_release` | L1014 | `asset.get("size", 0) > 0` | `upload_failure_empty_next` (`index.json.next` `0` o ignoré, `.previous` promu) | `M001:publish_recover_size_ge_0` (`> 0` -> `>= 0`) |
| `download_index_release` | L1139-1147 | `e.code >= 500 or e.code == 429`, `attempt < 3` (HTTP & réseau) | `[499]` (1 essai), `[500,500,200]`, `[500,500,500]`, `[429,429,200]`, `["net_err","net_err",200]` | `M001:download_retry_gt_500`, `ge_499`, `no_429`, `attempt_lt_2`, `net_lt_2` |
| `compile_catalog_index` & adapter | L694, L1171 | Catalogue réel 235 dossiers / 230 indexés + schéma strict | Égalité JSON complète `compiled_index` & `audit` vs `fa8df85` | `M001:compile_catalog_index`, `audit_plugin_catalog`, clé parasite `extra_parasite_key` |

### 2.2 Référence `M074 tradingview-indicator-search-mcp-server` (`aspace_trading_copilot_foundation.py` — 28 sabotages)

| Fonction / Classe | Ligne | Condition exacte | Cas vérifiés contre Node v24 | Sabotage détectant la régression |
|---|---|---|---|---|
| `tv_snippet` / `_js_slice` | L301-312 | UTF-16-LE `len <= end*2`, `max_chars` | Longueur exacte `10` vs `11`, astral émoji `ab\U0001F600` (4 code units) vs `+c` | `M074:tv_snippet`, `M074:_js_slice_utf16` |
| `get_cached_search` / `get_cookie_jar` | L502, L614 | Strictly `ts - fetched_at > ttl_ms` | Égalité exacte à `5000 ms` (hit) vs `5001 ms` (miss) | `M074:Store.get_cached_search_ge`, `Store.get_cookie_jar_ge` |
| `query_corpus` | L659-660 | `min_likes > 0` / `s.likes >= ?` | `min_likes = 0, 10, 11, 120, 121` | `M074:Store.query_corpus_min_likes_gt` |
| `TradingViewThrottle._jitter` | L765-767 | `math.floor(min + r*(max-min) + 0.5)` (`Math.round`) | `random = 0.49, 0.5, 0.75` sur `[1000, 1001]` et `0.9` sur `[1000, 1000]` | `M074:Throttle._jitter_floor`, `Throttle._jitter_bankers_round` |
| `CircuitOpenError` / `is_open` / `note_blocked` / `run` | L694, L739, L744, L771 | `ceil(ms/60000)`, `now < open_until`, `count >= dailyBudget`, `blocks >= threshold` | `60001ms` vs `60000ms`, `899999ms` vs `900000ms`, `count = 4 vs 5`, `blocks = 3` | `M074:Throttle.is_open_le`, `note_blocked_gt`, `run_budget_gt` |
| `tv_to_listing` / `search_scripts` / `query_corpus` | L1096 | Clés exactes, `perPage` `0/1/24/25`, `total >= 1000`, `limit` `3/4` et `100/101` | Zéro clé parasite, notes `999` vs `1000` | `M074:tv_to_listing_extra_key`, `M074:create_tradingview_tools` |

### 2.3 Répartition complète sur les 8 organes différentiels (`129` sabotages)

| Module | Organe natif | Sabotages | Seuils / Arrondis critiques verrouillés |
|---|---|---|---|
| `M001` (`a0-plugins`) | `aspace_plugin_registry_organ.py` | **49** | `START_FROM=-1`, `MAX_PLUGINS`, `2000/50/500/5/20Ko/2Mo`, `rename_502_twice`, `size>0`, retries `499/500/429/net_err` |
| `M074` (`tradingview-indicator-search-mcp-server`) | `aspace_trading_copilot_foundation.py` | **28** | `>` TTL/cookie, `>=` `min_likes`, `Math.round` vs floor/banker, `Math.ceil`, `is_open`, `dailyBudget`, UTF-16 |
| `M044` (`context-language-models`) | `aspace_fkb02_memory_organ.py` | **15** | `> protect` (`_clm_normalize`), `<= limit` (`clm_may_grow`) |
| `M084` (`video-director`) | `aspace_video_studio_foundation.py` | **13** | `vd_read_time` plancher `1.6`, `fps=16` (`0.6/0.4/0.7`), `freeze=0.5`, `freeze_eps=0.25`, `std=6.0`, `seam=0.5`, `vd_compare_cuts <= 0.5`, `round()` |
| `M050` (`knowledge-catalog`) | `aspace_fkb02_memory_organ.py` | **10** | `okf_is_stale` `now == stale_after` vs `+1s`, single-child sans description |
| `M056` (`CLI-Anything`) | `aspace_fkb04_anything_organ.py` | **6** | Troncature `skill_intro` exactement `100` vs `101` caractères |
| `M118` (`04_Inference_Youtube_Discovery_Registry`) | `aspace_discovery_catalog.py` | **5** | Bornes `estimated_ttl_days` (`6/7/29/30`) + clé parasite |
| `M117` (`00_Marketplace_YoutubeSkills`) | `aspace_marketplace_engine.py` | **3** | Parité playbooks/requêtes + clé parasite |
| **Total** | **6 fichiers organes natifs** | **129** | **129 / 129 sabotages détectés en local et en CI `#44733797882`** |
