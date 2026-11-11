# Audit télémétrie — a0-plugins (D-N053 pas B, H-M4)

**Module :** `a0-plugins` — fork `Amdkn/a0-plugins`, gel `d040c3f`, adapter (à consigner après push).
**Verdict : TÉLÉMÉTRIE ZÉRO par contrat.** Aucun SDK de télémétrie, aucun appel réseau en arrière-plan, aucun appel à l'import. Les seuls appels réseau du repo sont des scripts CI explicites vers l'API GitHub (et un vers OpenRouter pour les thumbnails), jamais déclenchés par l'adapter.

## 1. Scan statique du code amont (au gel)

Motifs cherchés dans `scripts/*.py` : `wandb|sentry|posthog|mixpanel|amplitude|segment.com|telemetry` → **0 hit**.
Motifs réseau cherchés : `requests.|httpx.|urllib|urlopen|socket.|http.client|aiohttp` → **76 lignes**, toutes dans les scripts CI ci-dessous, **0 à l'import** (que des `import urllib.*` et des appels dans des fonctions `main()` / helpers appelés par les workflows).

### Sites réseau explicites (tous déclenchés par l'utilisateur / la CI, jamais en arrière-plan)

- `scripts/download_index_release.py` — `api.github.com/repos/.../releases/tags/...` (téléchargement de la release d'index, déclenché par le test / la CI).
- `scripts/publish_index_release.py` — `api.github.com/.../releases` (GET/POST/DELETE d'assets, publication de l'index, déclenchée par le workflow).
- `scripts/sync_plugin_state.py` — API GitHub (synchronisation de l'état des plugins, workflow `generate-plugin-state.yml`).
- `scripts/validate_plugin_submission.py` — `api.github.com/.../contents/plugin.yaml` + `raw.githubusercontent.com` (validation d'une PR, workflow `validate-plugin-pr.yml`).
- `scripts/close_inactive_failing_prs.py`, `scripts/find_orphan_plugin_names.py` — `api.github.com/graphql` + REST (maintenance, workflows).
- `scripts/update_index_stars.py`, `scripts/wait_for_index_serialization.py` — API GitHub (statistiques, attente de sérialisation).
- `scripts/openrouter_image_gen.py:45` — `openrouter.ai/api/v1/chat/completions` (génération d'une thumbnail, workflow `generate-missing-thumbnails.yml`, clé `OPENROUTER_API_KEY` fournie par la CI — **aucune clé lue ni stockée ici**).
- `scripts/test_index_release.py` — n'appelle le réseau que via les fonctions mockées du test (aucun appel réel : `urllib` importé, requêtes simulées en mémoire).

## 2. Dépendances

Aucun manifeste de dépendances applicatives (pas de `pyproject.toml` / `requirements.txt` à la racine) ; les workflows installent `pyyaml`, `pillow`, `requests` (CI seulement). Aucun SDK de télémétrie déclaré (grep `wandb|sentry|posthog|mixpanel|amplitude|telemetry` dans `.github/` : 0 hit). L'adapter est **stdlib seule** (0 import réseau dans `aspace_a0_plugins_adapter/__init__.py`, vérifié : 0 hit).

## 3. Preuve d'exécution — namespace sans interface

`unshare -n` (aucune interface réseau, DNS en échec) : `validate()` + `doctor()` réussissent (indexed : 230, 8/8 contrôles ok). Log : `logs-netns-validate.log`. **0 appel sortant possible dans ce namespace — la preuve est structurelle, pas déclarative.**

## 4. Poids dans le fork

Aucun poids : l'index ne contient que des pointeurs (`index.yaml`) et des images (thumbnails ≤ 20 Ko par règle amont). Aucun fichier `.safetensors` / `.bin` / `.pt` / `.pth` dans le repo (vérifié par `validate()` : pas de scan de poids applicable, l'adapter ne liste que l'index).

## 5. Déclencheurs tranchés

| Déclencheur | Décision |
|---|---|
| Appels API GitHub (releases, GraphQL, contenus) | Explicites, CI / opérateur, jamais automatiques à l'import — **conservés tels quels** (comportement amont, pas une télémétrie) |
| Génération de thumbnail via OpenRouter | Explicite, workflow CI, clé fournie par la CI — **conservé tel quel**, aucune clé dans le fork |
| SDK de télémétrie | Aucun — **rien à retirer** |
| Appel réseau à l'import | Aucun (prouvé en netns) — **rien à retirer** |
| Poids montés dans le fork | Aucun — **conforme** |

## 6. Ré-audit

À chaque changement de commit gelé ou d'adapter, et au minimum à chaque transition d'état.
