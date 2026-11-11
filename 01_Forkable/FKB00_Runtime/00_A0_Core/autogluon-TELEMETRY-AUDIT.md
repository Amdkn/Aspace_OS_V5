# Audit télémétrie — autogluon (D-N053, pas A)

**Fork :** `Amdkn/autogluon` — **gel : `e3cb3b7`** — **adapter : `2de7c39`** —
**bind : `efadb39`** (re-appliqué `02e547a`)
**Date :** 2026-11-10 ~22:30 EST · **Exécutant :** Ryan (Factory)
**Résultat : 0 appel sortant de télémétrie par l'adapter. Zéro SDK télémétrie
déclaré. Un seul émetteur amont connu : la télémétrie TabPFN, défaut OFF,
coupée par l'adapter.**

## 1. Scan statique — code source (hors tests)

Commandes : `grep -rn -i "posthog|sentry|mixpanel|amplitude|segment|datadog|newrelic|bugsnag|hotjar|fullstory|logrocket|trackjs"` sur `core/setup.py`,
`tabular/setup.py`, `common/setup.py`, `pyproject.toml`, `setup.cfg` ;
`grep -rn -E "requests\.(get|post)|urllib\.request|http\.client|socket\.socket|aiohttp|httpx\.(get|post)"` sur `autogluon/`, `common/`, `core/src/`,
`tabular/src/` ; `grep -rn -i telemetry` sur les mêmes.

- **Zéro SDK télémétrie déclaré** (aucun des 12 noms cherchés dans les
  dépendances).
- **5 sites réseau, tous des téléchargements explicites déclenchés par
  l'utilisateur, jamais de la télémétrie :**
  - `common/src/autogluon/common/loaders/_utils.py:197` — `download()` :
    `requests.get(url)` pour télécharger un fichier (S3 ou URL) demandé.
  - `common/src/autogluon/common/loaders/load_pkl.py:135` —
    `_load_pickle_from_url(url)` : `requests.get(url)`, URL fournie par
    l'utilisateur.
  - `common/src/autogluon/common/utils/presets_io.py:29` —
    `load_preset_dict_from_location(location)` : `urllib` pour charger un
    preset depuis une location donnée.
  - `core/src/autogluon/core/utils/files.py:69` — `download(url, ...)` :
    `requests.get(url)`, journalisé (« Downloading … from … »).
  - `tabular/src/autogluon/tabular/models/tabpfnv2/_weight_fetch.py` —
    récupération des poids TabPFN depuis Hugging Face (avec repli
    `urllib.request.urlopen` vers huggingface.co) ; **gated en amont** par
    `ag.fetch_pretrained_weights` (`weight_fetch_policy` : si la
    récupération est interdite, le checkpoint manquant lève
    `PretrainedWeightsUnavailableError` au lieu de télécharger).
  - Aucune donnée d'usage n'est envoyée par ces 5 sites : ce sont des
    lectures (GET / téléchargement), pas des émissions.
- **Télémétrie TabPFN (seul émetteur connu) :**
  - `model_telemetry: False` par défaut dans les modèles TabPFN v2
    (`tabpfnv2_5_model.py:141`), v2.5/v3 (`tabpfn3_model.py:253`,
    `tabpfn3_5_model.py:69`, `tabpfnv2_6_model.py:36`).
  - Quand `model_telemetry` est faux, le modèle appelle lui-même
    `disable_tabpfn_telemetry()` qui force
    `TABPFN_DISABLE_TELEMETRY=1` (`tabpfnv2_5_model.py:223-224,370-371,492-493`).
  - L'adapter force la même variable **avant** tout import d'`autogluon`
    et avant tout fit (`disable_telemetry()`), en défense en profondeur.

## 2. Audit des dépendances

- Dépendances déclarées par `core/setup.py` et `tabular/setup.py`
  (versions dynamiques, `setup.py`) : pas de SDK télémétrie (voir §1).
- L'adapter lui-même n'a **aucune dépendance** (stdlib seule).

## 3. Audit d'exécution — capture réseau

Méthode : namespace réseau `unshare -n` (vérifié : `connect` vers
8.8.8.8:53 échoue `Network is unreachable` — **aucun réseau externe
possible**).

- **Smoke adapter : 5/5 verts, EXIT 0** (`tests/test_adapter_smoke.py`)
  dans le namespace sans réseau. **Zéro appel sortant possible pendant ce
  run — et le run passe.**
- L'adapter n'importe que la stdlib au niveau module ; `autogluon` n'est
  importé que dans `create_predictor()` (vérifié par le test
  `test_import_does_not_pull_autogluon`).

## 4. Conclusion

**0 appel sortant de télémétrie, en statique comme en exécution.** Le seul
trafic réseau du fork est le téléchargement explicite (modèle, preset,
poids) demandé par l'utilisateur ; la seule télémétrie connue (TabPFN)
est OFF par défaut et coupée par l'adapter avant tout fit.

**Re-audit :** à chaque changement de commit gelé ou d'adapter, et au minimum
à chaque transition d'état.
