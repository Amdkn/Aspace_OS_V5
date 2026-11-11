# Fiche d'adaptation — dify (D-N048 V4, FKB07)

**Statut :** état 2 Vérifié (fiche + adapter + manifeste, tests verts — voir § Tests)
**Fork :** https://github.com/Amdkn/dify (gel `b29552aae0acb1801eeb2870a552cd939fe36a20`, branche `main`, parent `langgenius/dify`)
**Dossier :** `aspace-dify-adapter/` (contract.json + validate.py + smoke_test.py + README.md + AGENTS.md local), commit `0f860ba5` sur le fork. **Seul code A'Space du fork** — le code amont est byte-identique au gel (diff gel→adapter = 5 fichiers, vérifié à l'API, H-M2).
**Version amont :** 1.19.0 (`api/pyproject.toml` et `web/package.json` concordent).

## Licence — Apache-2.0 modifiée

Fichier `LICENSE` vérifié au fichier (l'API GitHub dit NOASSERTION car
le texte est modifié — pas une licence libre standard). Base Apache 2.0
+ deux conditions additionnelles, **les deux respectées par cet adapter** :

- **(a) Mono-tenant UNIQUEMENT** — « Unless explicitly authorized by
  Dify in writing, you may not use the Dify source code to operate a
  multi-tenant environment. » Un tenant = un workspace. L'adapter
  n'opère jamais en multi-tenant et ne le prépare pas.
- **(b) LOGO et copyright du frontend INTACTS** — « you may not remove
  or modify the LOGO or copyright information in the Dify console or
  applications » (définition : tout `web/` en source, image `web` en
  Docker). L'adapter ne touche jamais à `web/` ; 4 logos épinglés par
  sha256 dans `contract.json` (`web/public/logo/logo.svg`,
  `logo-site.png`, `logo-site-dark.png`, `web/public/favicon.ico`) —
  un logo qui change = l'adapter refuse.
- Note : « The interactive design of this product is protected by
  appearance patent. » © 2025 LangGenius, Inc. — le producteur peut
  durcir ou assouplir l'accord (clause contributeur) ; une évolution
  de licence = amendement (revisite par signal de dérive, D5).

## Surface de l'adapter (couture contrat seule, §1.5)

Validation hors-ligne du dépôt au gel, jamais de démarrage de serveur :

- `validate [--repo <chemin>]` — structure (`api/`, `web/`, `LICENSE`,
  `docker/`), LICENSE (deux conditions), logos intacts, version 1.19.0.
- `--version` — version + gel. `--doctor` — posture télémétrie
  (informative, aucun envoi).
- **Smoke 10/10** — dont `validate` sous `unshare -n` (sans interface
  réseau). Stdlib seule.

Règles maison : l'`AGENTS.md` racine de dify est un contrat liant —
**non édité** (H-M2) ; l'adapter porte son propre `AGENTS.md` local.
Les commandes backend passent par `uv run --project api` (règle amont) ;
les tests d'intégration sont CI-only (non attendus en local) ; contrôles
ciblés sur machine locale (règle amont).

## § Tests

**Périmètre :** tests unitaires ciblés, télémétrie d'abord (la surface
de l'audit H-M4) : `api/tests/unit_tests/services/test_telemetry_service.py`
(348 lignes), `api/tests/unit_tests/tasks/test_community_telemetry_task.py`
(50 lignes), `api/tests/unit_tests/tasks/test_enterprise_telemetry_task.py`
(71 lignes). Le monorepo complet est impraticable sur cette VM partagée
(6 Go RAM, 1,5 CPU ; 507 paquets résolus par `uv sync --group dev`) —
périmètre honnête, nommé, conforme à la règle amont « contrôles ciblés ».

**Bilan : 33 passés, 0 échec, 0 ignoré, 5 warnings (60,91 s, rc=0)** —
27 `test_telemetry_service.py` + 2 `test_community_telemetry_task.py` +
4 `test_enterprise_telemetry_task.py` (collecte : 33 tests). Log
`logs-dify-suite.log` (37 lignes, mode `-q`). Les 5 warnings sont des
`DeprecationWarning` amont (`JSONModelColumn` legacy, `models/agent.py`
et `models/skill.py`) + avertissements du plugin coverage (aucune
donnée collectée en mode `-q`) — aucun échec.

**Premier run : rc=4, échec de collecte — cause environnementale
prouvée à la racine, sans toucher au code ni aux tests.** La collecte
échouait dans `tests/conftest.py` → `services/billing_client/
transport.py:82` (client `httpx` au niveau module) : `httpx.Client()`
lit les variables proxy du sandbox et son `URLPattern` casse sur les
entrées IPv6 entre crochets de `no_proxy`/`NO_PROXY` (`[::1]`,
`[fd8b:…]` → `InvalidURL: Invalid port: ':1]'`). Preuve directe :
`httpx.Client()` lève avec l'env actuel, passe avec
`NO_PROXY=no_proxy=localhost,127.0.0.1`. Correctif d'environnement
uniquement (variables assainies pour le run), défaut produit : aucun.

**Commande de référence :** `uv run --project api pytest tests/unit_tests/services/test_telemetry_service.py tests/unit_tests/tasks/test_community_telemetry_task.py tests/unit_tests/tasks/test_enterprise_telemetry_task.py` (Python 3.13, `TMPDIR=~/workspace/.tmp`).

## Télémétrie (audit complet : `dify-TELEMETRY-AUDIT.md`)

- **Télémétrie communautaire api/ : DÉFAUT ON** — `DISABLE_TELEMETRY=false`,
  endpoints `https://otel.dify.ai/v1/events` (+ repli `.cn`), `install`
  (1×) + `heartbeat` (≤1/jour), charge anonyme, porte : édition COMMUNITY.
  Coupure par contrat : `DISABLE_TELEMETRY=true` + `DO_NOT_TRACK=true` +
  `CI=true` (à appliquer au déploiement, jamais par l'adapter qui ne
  démarre rien).
- Sentry api/web : OFF sans DSN. OpenTelemetry : OFF (`ENABLE_OTEL=false`).
  Amplitude web : OFF sans clé, opt-out par défaut. OTel entreprise : OFF.
- PostHog : dépendance transitive inutilisée de chromadb (jamais importé).
- Version-check (`updates.dify.ai`) : déclenché par la console seulement.

## Réserves nommées

1. **Suite :** périmètre ciblé uniquement (télémétrie) — la suite unitaire
   complète et les tests d'intégration ne sont pas courus ici (CI-only
   selon l'amont, VM partagée) ; à re-courir en CI hors sandbox.
2. **Télémétrie communautaire ON par défaut** — le seul mécanisme en
   défaut ON ; la coupure est contractuelle (3 interrupteurs), pas
   technique dans l'adapter (qui ne démarre pas le serveur).
3. **Licence modifiée** — les conditions (a) et (b) sont des obligations
   permanentes ; tout usage multi-tenant ou toute retouche de `web/`
   exige un arbitrage (licence commerciale ou autorisation écrite).
4. **Dérive amont constatée** — l'amont a bougé après le gel
   (`b63ed03`, poussé 2026-11-10) ; le gel `b29552a` reste épinglé,
   revisite = candidat de fusion (D5), jamais de fast-forward silencieux.

## Dette de divergence

Propriétaire : cœur Buzz (lane Clara / 12e). La divergence est portée
par le fork `Amdkn/dify` : l'adapter seul est du code A'Space ; tout le
reste est l'amont au gel. Dérive amont suivie par l'inventaire
hebdomadaire Auto Research (HEAD amont vs commit gelé).
