# Fiche d'adaptation — mitra-2 (D-N053, pas A)

**Adresse :** `fiber:a0:mitra-2`
**Manifeste :** `mitra-2.manifest.json` (même domicile)
**Audit télémétrie :** `mitra-2-TELEMETRY-AUDIT.md` (même domicile)
**Statut :** état 1 Adapté (fiche + adapter + manifeste, smoke vert, suite
amont 83/0/0 ; validation 13e en attente)

## Commit gelé

- **Repo :** `Amdkn/mitra-2` — **natif, pas un fork** (`fork: false`,
  `parent: null`, 96 Ko, Python — vérifié à l'API). Pas d'amont à
  souverainiser : l'adaptation porte sur le pipeline natif (§D14).
- **Gel : `3f277e5`** — « feat(aspace-v5): bind mitra-2 as Cordis Fiber
  (16L) to A0 EGM Core », HEAD de la branche `aspace-v5-native`, parent
  `b4701e8` (« Cheaper fine-tuning loop and prediction (v0.3.0) », HEAD de
  `main` au moment du bind). Le bind (24 lignes, format ML 16L identique à
  tabfm / chronos-forecasting) est donc l'enfant direct du HEAD `main`.
- **Branche de travail : `main`** (branche par défaut). L'adapter est
  commité sur `main` avec pour parent le gel `3f277e5` : `main` contient
  donc bind + adapter, comme l'exige F8 D2.
- **Tout commit natif ultérieur exige un amendement de design**, jamais un
  fast-forward silencieux.

## Adapter

- **Commit : `2676f75`** sur `main` (vérifié à l'API), parent `3f277e5`.
  **Seul code A'Space du repo** — diff gel→adapter = 3 fichiers adapter
  seuls (+182/−0) : `aspace-mitra-2-adapter/README.md`,
  `aspace-mitra-2-adapter/mitra2_aspace_adapter/__init__.py`,
  `aspace-mitra-2-adapter/tests/test_adapter_smoke.py`.
- **Surface :** `Mitra2AspaceAdapter.describe()` (épinglage, licence,
  contrat local-only) ; `create(checkpoint_dir, **kwargs)` → `MitraFinetune`
  sur checkpoint **local existant** (refus `FileNotFoundError` avant tout
  import lourd, y compris pour un identifiant de repo Hub) ;
  `recipe()` (résumé de la recette gelée `BASELINE`) ;
  `telemetry_guard()` (0 appel réseau par l'adapter).
- **Divergence documentée :** `device` par défaut `"cpu"` dans l'adapter
  (l'amont `MitraFinetune` défaut est `"cuda"`).
- **Smoke adapter : 4/4 verts** (`tests/test_adapter_smoke.py`), y compris
  dans un namespace réseau sans aucune interface (`unshare -n`, EXIT 0).

## Tests au gel et sur le repo adapté

- **Suite amont (`tests/` : `test_distribution`, `test_modes`,
  `test_speed`) : 83 passés, 0 rouge, 0 ignoré** (101,94 s, venv dédié
  `venv-dn053-a` : torch 2.15.0+cpu, sklearn 1.9.1, numpy 2.5.4, pandas
  2.3.3, pytest 9.2.0 + extra `autogluon.tabular[mitra]` installé en
  éditable depuis le gel autogluon ; log `logs-mitra-2-suite.log`).
  Historique honnête : sans l'extra, 80/2/1 — les 2 rouges
  (`test_protocol_patches_behaviour`,
  `test_fitted_context_memo_behaviour`) et l'ignoré venaient de
  `ModuleNotFoundError` sur l'extra optionnel `full`, **bilan identique
  au gel `3f277e5`** (worktree gel, log `logs-mitra-2-suite-gel.log`) —
  donc pré-existants et environnementaux, jamais imputables à l'adapter ;
  l'installation des dépendances manquantes (`pandas`, puis
  `omegaconf`/`loguru`/`einops`/`einx`/`transformers`/`huggingface_hub`)
  les a fait passer un à un jusqu'à 83/0/0.
- **Smoke adapter : 4/4 verts**, au commit `2676f75`, avec et sans réseau.

## Télémétrie

**Zéro par l'adapter.** Voir `mitra-2-TELEMETRY-AUDIT.md` : scan statique
(0 primitive réseau / télémétrie dans `src/` et `tests/`, 0 SDK déclaré) +
exécution en namespace sans réseau (smoke 4/4, EXIT 0). Nuance consignée :
le chargeur patché (`patches.install_use_hf_patch`) retombe sur le
`from_pretrained` d'origine pour un chemin non local — inatteignable via
l'adapter (`create()` refuse les chemins inexistants) et via
`resolve_checkpoint` (local-only, `FileNotFoundError` sinon).

## Divergence (dette portée par le cœur Buzz)

- **Poids non montés :** les poids Mitra-v2 viennent du Hub par un acte
  explicite de l'opérateur ; l'adapter ne les télécharge ni ne les monte
  (travail R1, D-N052 — pas D-N053).
- **`device` par défaut :** `"cpu"` (adapter) contre `"cuda"` (amont).
- **Recette gelée :** `BASELINE` (steps 50, lr 1e-5, warmup 10, tune full,
  snapshot_k 1, sans quantile-transform ni category-frequency, non stock).
- **Ré-audit télémétrie :** à chaque changement de commit gelé ou d'adapter,
  et au minimum à chaque transition d'état.

## Preuves H-M1..H-M7

| # | Hold-out | Preuve |
|---|---|---|
| H-M1 | Gel nommé | `main` = `2676f75`, parent `3f277e5` (bind, gel §2) ; parent du bind `b4701e8` ; vérifié à l'API |
| H-M2 | Paquets amont intacts | Diff `3f277e5`→`2676f75` = 3 fichiers adapter seuls, +182/−0 |
| H-M3 | Suite verte | Suite amont 83/0/0 (extra `mitra` complet) ; smoke adapter 4/4 vert |
| H-M4 | Télémétrie zéro | Audit versionné ; smoke 4/4 en namespace sans réseau |
| H-M5 | Manifeste | `mitra-2.manifest.json`, `id: fiber:a0:mitra-2`, `levels.current: 0` |
| H-M6 | Frontière adapter | `aspace-mitra-2-adapter` seul code A'Space ; propriétaire : cœur Buzz |
| H-M7 | Fiche versionnée | Cette fiche (gel, licence, audit, dette, contraintes §2) |

## Réserves

1. **Moteurs d'inférence V5 non touchés** (travail R1) — l'adapter ne couvre
   que le pipeline du repo natif.
2. **Poids non montés** (voir Divergence) — aucun poids Mitra-v2 n'a été
   téléchargé dans ce pas.

## Références

- Design D-N053 (Clara, 2026-11-10) :
  `~/workspace/v4-factory/plans/ADAPTATION-TOUS-MODULES-RUNTIME-plan-borne.md`
  (§D14, §2, H-M1..M7).
- Repo : https://github.com/Amdkn/mitra-2 (gel `3f277e5`, adapter `2676f75`).
