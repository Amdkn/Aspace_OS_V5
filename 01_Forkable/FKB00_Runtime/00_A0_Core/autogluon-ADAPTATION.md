# Fiche d'adaptation — autogluon (D-N053, pas A)

**Adresse :** `fiber:a0:autogluon`
**Manifeste :** `autogluon.manifest.json` (même domicile)
**Audit télémétrie :** `autogluon-TELEMETRY-AUDIT.md` (même domicile)
**Statut :** état 1 Adapté (fiche + adapter + manifeste, smoke vert, suite
amont bornée verte ; validation 13e en attente)

## Commit gelé

- **Fork :** `Amdkn/autogluon` (parent `autogluon/autogluon`, Apache-2.0,
  ~27 959 Ko, branche par défaut `master` — il n'y a **pas** de branche
  `main` dans ce fork).
- **Gel : `e3cb3b7`** — « [tabular] A model with a NaN validation score is
  not listed as trained (#6048) », commit amont 2026-11-03, version 1.6.4.
  HEAD de `master` et de `aspace-v5-native` au moment du pas.
- **Dérive amont : 13 commits** (mesure Discover, §2).
- **Tout commit amont ultérieur exige un amendement de design**, jamais un
  fast-forward silencieux.

## Bind (avant l'adapter, §D8)

Le pin V5 était brut (sans bind). Bind créé sur `aspace-v5-native` :
`aspace-plugin.json` (16L, format ML identique à mitra-2 / tabfm /
chronos-forecasting — diff contre le bind mitra-2 : seuls `name`,
`submodule_path`, `sovereign_fork_url` diffèrent), commit **`efadb39`**,
parent `e3cb3b7`, vérifié à l'API. Le fichier est ignoré par le
`.gitignore` amont (`*.json`, ligne 10) : ajout par `git add -f`.
**Re-application verbatim sur `master`** (F8 D2) : commit **`02e547a`**,
fichiers du bind seuls, blob identique (`5a576e94`).

## Adapter

- **Commit : `2de7c39`** sur `master` (vérifié à l'API), parent `e3cb3b7`.
  **Seul code A'Space du fork** — diff gel→adapter = 3 fichiers adapter
  seuls (+190/−0) : `aspace-autogluon-adapter/README.md`,
  `aspace-autogluon-adapter/autogluon_aspace_adapter/__init__.py`,
  `aspace-autogluon-adapter/tests/test_adapter_smoke.py`.
- **Surface :** `AutogluonAspaceAdapter.describe()` (épinglage, licence) ;
  `disable_telemetry()` (force `TABPFN_DISABLE_TELEMETRY=1`, idempotent) ;
  `create_predictor(*args, **kwargs)` → `TabularPredictor` (import
  paresseux, télémétrie coupée avant) ; `telemetry_guard()` (0 appel
  réseau par l'adapter).
- **Smoke adapter : 5/5 verts** (`tests/test_adapter_smoke.py`), y compris
  dans un namespace réseau sans aucune interface (`unshare -n`, EXIT 0).

## Tests au gel et sur le fork adapté

- **Suite amont bornée (périmètre nommé avant exécution) :
  `tabular/tests/unittests/test_model_class_settings.py` (2 tests :
  interrupteur télémétrie / réglages de classe) +
  `tabular/tests/unittests/test_global_settings.py` (3 tests) :
  5 passés, 0 rouge, 0 ignoré** (18,39 s, installation éditable
  `common` + `core` + `features` + `tabular` 1.6.4.dev0 depuis le gel ;
  log `logs-autogluon-suite-bornee.log`).
- **Suite complète du framework : hors périmètre** (milliers de tests,
  fits réels, GPU) sur cette VM (6 Go RAM, 1,5 CPU) — borne consignée
  honnêtement, comme l'exige la mission.
- **Smoke adapter : 5/5 verts**, au commit `02e547a`, avec et sans réseau.

## Télémétrie

**Zéro par l'adapter.** Voir `autogluon-TELEMETRY-AUDIT.md` : 0 SDK
télémétrie déclaré ; 5 sites réseau amont = téléchargements explicites
déclenchés par l'utilisateur (jamais d'émission de données d'usage) ;
seul émetteur connu = télémétrie TabPFN, défaut `False`, coupée par
l'adapter avant tout fit ; récupération des poids TabPFN gated en amont
par `ag.fetch_pretrained_weights`.

## Divergence (dette portée par le cœur Buzz)

- **Poids non montés :** TabPFN / Mitra — téléchargement explicite par
  l'opérateur, hors adapter ; miroirs HF = travail R1 (D-N052).
- **Dérive 13 commits** : gel tenu, revisite par signal (jamais de
  fast-forward silencieux).
- **`aspace-plugin.json` ignoré par l'amont** (`*.json` au `.gitignore`) :
  chaque dépôt du bind exige `git add -f`.
- **Ré-audit télémétrie :** à chaque changement de commit gelé ou d'adapter,
  et au minimum à chaque transition d'état.

## Preuves H-M1..H-M7

| # | Hold-out | Preuve |
|---|---|---|
| H-M1 | Gel nommé | `master` = `02e547a` (bind), parent adapter `2de7c39`, parent gel `e3cb3b7` ; `aspace-v5-native` = `efadb39` ; vérifié à l'API |
| H-M2 | Paquets amont intacts | Diff `e3cb3b7`→`2de7c39` = 3 fichiers adapter seuls, +190/−0 |
| H-M3 | Suite verte | Suite bornée 5/5 verte ; smoke adapter 5/5 vert |
| H-M4 | Télémétrie zéro | Audit versionné ; smoke 5/5 en namespace sans réseau |
| H-M5 | Manifeste | `autogluon.manifest.json`, `id: fiber:a0:autogluon`, `levels.current: 0` |
| H-M6 | Frontière adapter | `aspace-autogluon-adapter` seul code A'Space ; propriétaire : cœur Buzz |
| H-M7 | Fiche versionnée | Cette fiche (gel, bind, licence, audit, dette, contraintes §2) |

## Réserves

1. **Pin à trancher à l'intégration :** la mission dit « le pin = le commit
   adapter » (`2de7c39`) ; F8 D4 (précédent cordis) épingle le HEAD
   contenant adapter **et** bind (`02e547a`). Les deux SHA sont consignés
   ici ; le coordinateur / 13e tranche. Recommandation : `02e547a`
   (adapter + bind, comme cordis `6aab659`).
2. **Branche : `master`, pas `main`** (le fork n'a pas de `main`) — la
   mission disait `main` au sens générique ; D15 (le pin est la vérité).
3. **Suite bornée, pas complète** : le périmètre amont est les 2 fichiers
   nommés ci-dessus (5 tests) ; la suite complète du framework reste hors
   périmètre sur cette VM.
4. **Moteurs d'inférence V5 non touchés** (travail R1).

## Références

- Design D-N053 (Clara, 2026-11-10) :
  `~/workspace/v4-factory/plans/ADAPTATION-TOUS-MODULES-RUNTIME-plan-borne.md`
  (§D8, §2, H-M1..M7) ; design F8 (§D2, §D4).
- Fork : https://github.com/Amdkn/autogluon (gel `e3cb3b7`, bind `efadb39`,
  adapter `2de7c39`, bind re-appliqué `02e547a`).
