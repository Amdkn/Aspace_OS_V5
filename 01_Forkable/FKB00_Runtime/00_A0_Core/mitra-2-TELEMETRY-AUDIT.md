# Audit télémétrie — mitra-2 (D-N053, pas A)

**Repo :** `Amdkn/mitra-2` (natif) — **gel : `3f277e5`** — **adapter : `2676f75`**
**Date :** 2026-11-10 ~22:30 EST · **Exécutant :** Ryan (Factory)
**Résultat : 0 appel sortant de télémétrie par l'adapter. Zéro SDK télémétrie.**

## 1. Scan statique — code source (`src/`, `tests/`, adapter)

Commande : `grep -rn -E "requests\.|urllib|http\.client|socket|huggingface_hub|snapshot_download|posthog|sentry|mixpanel|segment|telemetry|sendBeacon|WebSocket|aiohttp|httpx" --include="*.py" src tests aspace-mitra-2-adapter`

- **0 occurrence** dans `src/` et `tests/` (aucune primitive réseau, aucun
  SDK télémétrie, aucun appel Hub dans le code du pipeline).
- **4 occurrences, adapter seul** : le mot « telemetry » dans
  `telemetry_guard()` et son test — des constantes déclaratives, pas des
  appels.
- **Chargeur patché (`patches.py`, `install_use_hf_patch`) :** le
  `from_pretrained` patché sert d'abord les répertoires locaux
  (`config.json` + `model.safetensors` lus sur disque) et ne retombe sur
  le `from_pretrained` d'origine que pour un chemin non local. Cette
  retombée est **inatteignable via l'adapter** : `create()` refuse tout
  chemin inexistant avant tout import lourd, et `resolve_checkpoint`
  (point d'entrée de `MitraFinetune`) est local-only (`FileNotFoundError`
  sinon). Aucun téléchargement implicite.
- **Résolution de checkpoint (`checkpoint.py`) :** locale seule —
  répertoire `save_pretrained` retourné tel quel, `.pt` unique converti
  une fois en cache `<checkpoint>.ag16[.reg]` voisin, sinon
  `FileNotFoundError` / `ValueError`. Aucun accès réseau.

## 2. Audit des dépendances

Déclarées dans `pyproject.toml` : `numpy>=1.24`, `scikit-learn>=1.4`,
`torch>=2.1` ; optionnelles : `autogluon.tabular[mitra]>=1.6`,
`tabarena>=0.1.0` ; dev : `pytest>=7`.

**Zéro SDK télémétrie déclaré** : aucun de `sentry`, `posthog`, `mixpanel`,
`amplitude`, `segment`, `analytics`, `bugsnag`, `datadog`, `newrelic`,
`trackjs`, `hotjar`, `fullstory`, `logrocket`.

## 3. Audit d'exécution — capture réseau

Méthode : namespace réseau `unshare -n` (vérifié d'abord : `connect`
vers 8.8.8.8:53 échoue `Network is unreachable` — **aucun réseau externe
possible**).

- **Smoke adapter : 4/4 verts, EXIT 0** (`tests/test_adapter_smoke.py`,
  0,02 s) dans le namespace sans réseau. **Zéro appel sortant possible
  pendant ce run — et le run passe.**
- L'adapter n'importe que la stdlib au niveau module (`pathlib`) ; `torch`,
  `mitra_finetune`, `autogluon` ne sont importés que dans les méthodes
  qui en ont besoin (vérifié par le test
  `test_import_does_not_pull_heavy_deps`).

## 4. Conclusion

**0 appel sortant de télémétrie, en statique comme en exécution.** Le seul
trafic réseau possible du pipeline est le téléchargement explicite d'un
poids depuis le Hub par l'opérateur (hors adapter, travail R1) — jamais
déclenché par l'adapter, jamais en arrière-plan.

**Re-audit :** à chaque changement de commit gelé ou d'adapter, et au minimum
à chaque transition d'état.
