# Audit télémétrie — adk-recipes (D-N048 V3b)

**Fork :** `Amdkn/adk-recipes`, gel `a93b9cc`. **Aucun SDK télémétrie tiers ; OpenTelemetry confiné à deux recettes, off par défaut.**

## 1. Scan statique

- **Aucun SDK télémétrie tiers au projet racine** : `pyproject.toml` et `uv.lock` ne contiennent ni PostHog, ni Sentry, ni Segment, ni Mixpanel, ni Amplitude (grep vérifié). Le seul « telemetry » de `pyproject.toml` est un commentaire sur la profondeur des racines de recettes.
- **OpenTelemetry confiné à deux recettes Python** (dépendances au niveau recette, pas au niveau racine) :
  - `core/python/ambient-quality-agent/` — deps `opentelemetry-api>=1.42.1`, `opentelemetry-sdk>=1.42.1` (son `pyproject.toml`) ; module `src/ambient_quality_agent/telemetry/` (`setup.py`, `gcs_span_exporter.py`) ; appelé à l'import de `fast_api_app.py:207` (`telemetry_setup.attach_gcs_exporter(trace.get_tracer_provider())`).
  - `core/python/genmedia-for-commerce/` — deps `opentelemetry-instrumentation-google-genai`, `opentelemetry-exporter-otlp-proto-http`, `opentelemetry-resourcedetector-gcp` (son `pyproject.toml`) ; template `app/app_utils/telemetry.py` (skill `scaffold-python-recipe`) : `setup_telemetry()` configure l'upload OTEL vers GCS.
- **Signal du commit de tête `a93b9cc` élucidé** (« usage tracking sends a one-segment gccl/ token », #2876, diff relu) : la recette `genmedia-for-commerce` ajoute un header `x-goog-api-client` avec un token `gccl/<version>-genmedia-for-commerce` sur **chaque appel Gemini déjà effectué** (`core/python/genmedia-for-commerce/.../clients.py`, `tracking_headers()` ; test `test_clients.py`). C'est une attribution d'usage dans un header d'appel API, pas un envoi télémétrique séparé.
- **Réseau dans le cœur, sans rapport avec la télémétrie** : `core/python/adk-voice-agent/` utilise `httpx` (passerelle MCP, auth GitHub) — appels initiés par l'utilisateur, pas de collecte. `tools/` (validateurs `validate.py`, `validate_manifest.py`, `validate_structure.py`, `validate_readme.py`, `validate_placement.py`) : **zéro télémétrie, zéro appel réseau** — validation locale de fichiers.
- **Faux positifs écartés** : le mot-clé « telemetry » apparaît dans des SKILL.md et templates de skills (`make-python-recipe-deployable`, `scaffold-python-recipe`) — ce sont des modèles de code pour recettes scaffoldées, pas du code exécuté par le cœur. Le mot « telemetry » dans `ambient-quality-agent/tools/` désigne des outils qui *lisent* la télémétrie déjà exportée par l'utilisateur (ingestion `gs://`, Cloud Logging), ils n'en émettent pas.

## 2. Consentement et interrupteurs

- **`ambient-quality-agent`** : `attach_gcs_exporter()` retourne `False` sans `config.traces_gcs_bucket` (variable `AQA_TRACES_GCS_BUCKET`) — **défaut : pas d'export**, une ligne de log (« No AQA_TRACES_GCS_BUCKET; spans are not exported to GCS. »). L'export GCS n'a lieu que si le déployeur configure explicitement un bucket.
- **`telemetry.py` (template de recette)** : `setup_telemetry()` ne fait rien sans `LOGS_BUCKET_NAME` **et** `OTEL_INSTRUMENTATION_GENAI_CAPTURE_MESSAGE_CONTENT != "false"` — **défaut : désactivé**. Quand activé : métadonnées seules (`NO_CONTENT`, jamais de prompts/réponses), upload GCS `gs://<bucket>/completions`.
- **`gccl/`** : pas d'interrupteur — c'est un header d'identification de la recette sur l'appel Gemini lui-même ; il ne part que quand l'utilisateur appelle Gemini via cette recette.
- **L'adapter n'active rien** : il n'exécute ni ne déploie aucune recette, ne définit aucune des variables d'activation (`AQA_TRACES_GCS_BUCKET`, `LOGS_BUCKET_NAME`), et ne fait aucun appel réseau.

## 3. Preuve d'exécution

- Smoke test de l'adapter (voir `aspace-adk-recipes-adapter/smoke_test.py`) : validation locale d'une recette dans un répertoire scratch, variables d'activation explicitement absentes. **Zéro appel sortant possible par construction** : le code exécuté (`tools/validate*.py`) ne contient aucun appel réseau (scan §1) et n'importe aucune des deux recettes télémétrées.
- Preuve réseau `unshare -n` : à compléter au smoke test si l'espace de noms est disponible sur la VM ; le smoke test lui-même ne requiert aucun réseau.

## Conclusion

**Télémétrie zéro par construction pour l'adapter** : aucun SDK tiers ; les deux mécanismes OpenTelemetry du repo sont confinés à deux recettes et **off par défaut** (bucket GCS requis, jamais configuré par l'adapter) ; le token `gccl/` est une attribution dans un header d'appel API, pas une télémétrie. L'adapter n'exécute que le validateur local `tools/validate.py`, sans réseau ni modèle.
