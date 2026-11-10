# Fiche d'adaptation — presenton (D-N048 V4, FKB07)

**Statut :** état 0 Basique → 1 Adapté en cours (fiche + adapter + manifeste,
smoke 8/8, suite 1 347 passés / 8 échecs prouvés environnementaux — voir § Tests)
**Fork :** https://github.com/Amdkn/presenton (gel `9af2b47`,
`9af2b47dda31060d3d5070e020a0825b15c94b32`, branche `main`)
**Amont :** https://github.com/presenton/presenton
**Licence :** **Apache-2.0** (vérifiée à l'API et au fichier `LICENSE`)
**Version amont :** 0.9.12-beta
**Adresse :** `fiber:a0:presenton`
**Dossier :** `aspace-presenton-adapter/` (contract.json + cli.mjs + smoke_test.mjs + README.md),
commit **`3e5d851`** sur le fork (premier commit adapter ; `3e5d85131ff08f9191a299d82a9640e94c342c7a`).
**Seul code A'Space du fork** — le code amont est byte-identique au gel
(diff gel→adapter = 4 fichiers, vérifié à l'API).
**Taille :** ~1,23 Go (clone partiel `--filter=blob:none --depth 1`, repo local 551 Mo).
**Touche :** Studio vidéo (fusion F4).

## Commit gelé

- **Gel :** `9af2b47` (Merge PR #1019, `fix/editor-context-budget`).
  Amont vérifié au moment du fork : HEAD main = gel, aucune dérive.
- **Structure :** racine Node (`scripts/`, `layouts.json`, `templates/`),
  `servers/fastapi/` (Python, `pyproject.toml`, `uv.lock`, 123 fichiers de tests),
  `servers/nextjs/` (app Next.js + Cypress), `electron/` (app Electron + Sentry).

## Tests

**Au gel `9af2b47` — TERMINÉ** (logs `logs-presenton-suite.log`,
`logs-presenton-fastapi-unit.log`, `logs-presenton-nextjs-font.log`,
`logs-presenton-smoke.log`).

- **Racine `npm test` (commande `test` déclarée) : 47 passés, 0 échec,
  rc=0** — 4 template-converter + 43 (package-metadata, desktop-export,
  sync-presentation-export, user-config-env, export-permissions,
  document-parser-security, sync-document-dependencies). Premier run :
  1 échec (`document-parser-security.test.mjs`, module
  `@llamaindex/liteparse` absent — pas de `npm install`) ; après
  `npm install --ignore-scripts` (74 paquets, 21 s) : vert complet.
- **Next.js `local-font-loading-validation.test.mjs` : 2 passés, 0 échec,
  rc=0** (stdlib seule).
- **FastAPI `tests/unit` (1 306 collectés, `uv sync --frozen` + pytest) :
  1 298 passés, 8 échecs, 135,72 s.** Les 8 échecs sont
  **prouvés environnementaux, aucun imputable à l'adapter
  (qui ne touche pas `servers/`)** :
  - 7 × `httpx.InvalidURL: Invalid port: ':1]'`
    (`test_chat_context_budget` ×1, `test_chat_llm_tools` ×1,
    `test_mcp_server_auth` ×5) : cause = le `NO_PROXY` ambiant de la
    VM contient `[::1]`, mal parsé par le `trust_env` de httpx.
    Preuve : `httpx.Client()` nu échoue dans ce shell avec la même
    erreur ; **re-run des 7 tests avec les variables proxy effacées :
    7 passed** (40,80 s).
  - 1 × `test_export_and_conversion_sidecars_have_group_only_read_access`
    (mode 0o770 vs 0o750 attendu) : cause = umask 0007 de cette VM
    (`mkdir` crée 0o770 ; le chemin `legacy` de `_permissions`
    conserve le mode existant — sous umask 022, `mkdir` crée 0o755
    et le test passe). Preuve : **re-run avec umask 0022 : 1 passed**.
- **Total couru : 1 347 passés, 8 échecs (tous environnementaux, prouvés),
  0 ignoré.**
- **Non courus (réserve nommée) :** FastAPI `tests/integration`,
  `edge_cases`, `regression` (serveurs live / providers LLM / réseau
  requis) ; Next.js Cypress (navigateur + app buildée requis).
- **Limites franches (environnement, pas le code) :** `uv sync`
  installe Python 3.11.18 via `uv` (le projet exige `>=3.11,<3.12`,
  la VM porte Python 3.12) ; la collecte pytest seule prend 137 s
  (imports lourds : spacy, mem0, qdrant) ; `/tmp` tmpfs 512 Mo
  évité (`TMPDIR=~/workspace/.tmp`) ; `package-lock.json` racine
  modifié par `npm install`, **reverti avant livraison**
  (`git status` propre hors adapter).
- **Commandes de référence :**
  `npm test` (racine) ; `node --test
  servers/nextjs/local-font-loading-validation.test.mjs` ;
  `TMPDIR=~/workspace/.tmp .venv/bin/python -m pytest tests/unit -q`
  (depuis `servers/fastapi`, après `uv sync --frozen`).

## Télémétrie

**RÉELLE, défaut ON, coupée par contrat** (audit complet :
`presenton-TELEMETRY-AUDIT.md`).

1. **Mixpanel** (Next.js) — token codé en dur, `api-eu.mixpanel.com`,
   session recording 100 %, canvas + fonts, ~91 sites d'appel (30 fichiers).
   Gate `DISABLE_ANONYMOUS_TRACKING` (env ou user-config) ; défaut **ON**,
   et un échec de `/api/telemetry-status` bascule aussi sur ON.
2. **Sentry** (Electron) — DSN codé en dur, `SENTRY_ENABLED` défaut
   **true**, `initMainSentry()` inconditionnel au démarrage.
   Traces 0.2 (packaged) / 1.0 (dev).
3. **mem0 / PostHog** (FastAPI) — `MEM0_TELEMETRY` défaut `True`
   (vérifié dans la roue mem0ai 2.0.18), `us.i.posthog.com`, cycle de
   vie à 100 %, hot-path échantillonné à 10 %. Presenton ne le
   désactive qu'en tests, jamais en production.

**Coupure par l'adapter :** l'adapter ne démarre aucun serveur et ne
fait aucun appel réseau — **télémétrie zéro par construction**.
Tout serveur presenton démarré par un appelant doit tourner avec
`DO_NOT_TRACK=1`, `DISABLE_ANONYMOUS_TRACKING=true`,
`SENTRY_ENABLED=false`, `MEM0_TELEMETRY=false` (`cli.mjs env`).

## Surface de l'adapter

- `version` — version presenton depuis `package.json` (0.9.12-beta).
- `validate [path]` — structure de `layouts.json`
  (`{"layouts": {"layouts": [{id, description, components: [{id,
  position, size, elements}]}]}}`, 14 layouts au gel, ids uniques).
- `check` — fichiers du layout figé présents.
- `env` — environnement télémétrie-off à forcer.
- **Smoke 8/8 VERT** (`logs-presenton-smoke.log`), dont la preuve
  zéro-réseau (`cli.mjs validate` dans `unshare -n`, exit 0) et le
  check statique (aucun `fetch`/`http`/`net` dans `cli.mjs`).

## Réserves nommées

1. Suite FastAPI integration/edge/regression non courue (serveurs
   live / LLM requis) ; Cypress non couru (navigateur requis).
2. Le volume exact émis par mem0 n'a pas été capturé sur un serveur
   en marche — établi par lecture du code mem0ai 2.0.18, pas par
   capture réseau.
3. `DO_NOT_TRACK` n'est pas honoré par presenton (non-interrupteur).
4. L'opt-out Mixpanel émet un dernier événement
   (`Usage_Analytics_Disabled`) au moment de la désactivation.
5. Clone partiel : le repo local est un clone `--filter=blob:none`
   (551 Mo) — certains blobs ne sont matérialisés qu'à la demande.

## Dette de divergence

Propriétaire : cœur Buzz. L'adapter est le seul code A'Space ; l'amont
reste byte-identique au gel. Toute dérive amont est signalée par
l'inventaire Auto Research (§D5), jamais fast-forwardée silencieusement.
Première revisite nommée par le design : aucune pour presenton
(l'amont n'a pas bougé depuis le gel au moment du fork).
