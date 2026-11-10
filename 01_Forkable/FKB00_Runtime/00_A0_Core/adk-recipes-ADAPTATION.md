# Fiche d'adaptation — adk-recipes (D-N048 V3b)

**Adresse :** `fiber:a0:adk-recipes`
**Manifeste :** `adk-recipes.manifest.json` (même domicile)
**Audit télémétrie :** `adk-recipes-TELEMETRY-AUDIT.md` (même domicile)
**Statut :** état 0 Basique → 1 Adapté en cours (fiche + adapter + manifeste, tests verts)
**Licence :** Apache-2.0

## Commit gelé

- **Fork :** `Amdkn/adk-recipes` (parent `google/adk-recipes`, Apache-2.0, branche `main`).
- **Gel : `a93b9cc`** — commit de tête « genmedia-for-commerce: usage tracking sends a one-segment gccl/ token (#2876) ».
- **Tout commit amont ultérieur exige un amendement de design**, jamais un fast-forward silencieux (D5).

## Adapter

- **Dossier :** `aspace-adk-recipes-adapter/` (contract.json + smoke test Python + README), commit `f14f79f` sur le fork. **Seul code A'Space du fork** — le code amont est byte-identique au gel.
- **Surface (contrat seul, §1.5) :** validateur local de recettes — `validate manifest|structure|readme|placement|all <scope>` (`tools/validate.py:main()`), lecture seule sur disque.
- **Jamais :** déployer ou exécuter une recette (uv run, ADK, Gemini), tout appel réseau, toute écriture hors du répertoire de sortie explicite, définir `AQA_TRACES_GCS_BUCKET` ou `LOGS_BUCKET_NAME`.
- **Couture Python↔Python (§2) :** contrat seul — aucune couture spécifique construite.
- **Smoke test :** `python3 -m pytest aspace-adk-recipes-adapter/smoke_test.py -q` — 6/6 (gel ancêtre, seul l'adapter a changé, contrat, variables télémétrie absentes, `validate manifest` + `validate structure` sur `core/python/rag-agent-search`, rejet d'un scope inexistant).

## Tests au gel et sur le fork adapté

- **Au gel `a93b9cc` : suite racine (outils + skills) 2718 passés, 0 échec, 2 skipped** (`uv run pytest`, 52 s, commande exacte de la CI `tools-tests.yml`) ; **recette `core/python/rag-agent-search` 1 passé, 0 échec** (`uv run pytest --ignore=tests/integration --ignore-glob="**/test_integration.py"`, commande exacte de la CI `python-tests.yml`, avec `MODEL_NAME=gemini-flash-latest` tiré de `.env.example`). Premier run recette sans la variable : 1 échec prouvé environnemental (`LLM=None`, `app/agent.py:34` lit `MODEL_NAME` ; la CI fournit la variable depuis `.env.example`, cf. AGENTS.md amont) — corrigé par la variable, aucun changement de code ni de test.
- **CI amont :** `python-tests.yml` = `uv run pytest --ignore=tests/integration --ignore-glob="**/test_integration.py"` par recette (matrice) ; `tools-tests.yml` = `uv sync --locked --dev` puis `uv run pytest` à la racine.
- **Limite franche :** `uv` absent de cette VM — installé manuellement (0.13.7, `~/.local/bin/uv`) ; `uv sync` télécharge depuis PyPI via le proxy de la VM.

## Télémétrie

**Zéro par construction (pas de SDK, mécanismes OTEL off par défaut).** Voir `adk-recipes-TELEMETRY-AUDIT.md` : aucun SDK tiers (posthog/sentry/segment) dans `pyproject.toml` / `uv.lock` ; OpenTelemetry confiné à deux recettes (`ambient-quality-agent` : export GCS seulement si `AQA_TRACES_GCS_BUCKET` défini ; `genmedia-for-commerce` : template `setup_telemetry()` seulement si `LOGS_BUCKET_NAME` défini, métadonnées seules) ; token `gccl/` = attribution dans un header d'appel Gemini, pas un envoi séparé. L'adapter n'exécute ni ne déploie aucune recette et ne définit aucune variable d'activation.

## Divergence (dette portée par le cœur Buzz, lane Clara / 12e)

- **Règles maison amont respectées (AGENTS.md) :** le dossier `AGENTS.md` amont n'a PAS été édité (H-M2) ; l'adapter ne touche pas aux recettes ni aux outils (validateurs locaux intacts) ; terminologie « recette » respectée ; `uv` utilisé, pas `pip` ; `ruff` ligne 80.
- **Ré-audit télémétrie :** à chaque changement de commit gelé ou d'adapter, et au minimum à chaque transition d'état (D3).

## Références

- Design D-N048 (Clara, 2026-11-09) : `~/workspace/v4-factory/plans/FORKS-AMONT-21-plan-borne-vagues.md`.
- Évidences : `~/workspace/v4-factory/evidence/D-N048/PROGRESS-D-N048.md`.
- Fork : https://github.com/Amdkn/adk-recipes (gel `a93b9cc`, adapter `f14f79f`).
