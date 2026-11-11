# Audit télémétrie — presenton (D-N048 V4, FKB07)

**Module :** presenton — fork `Amdkn/presenton`, gel `9af2b47`
(`9af2b47dda31060d3d5070e020a0825b15c94b32`), branche `main`,
licence Apache-2.0, version 0.9.12-beta.
**Date :** 2026-11-10. **Périmètre :** l'intégralité du dépôt au gel
(scan mots-clés sur 11 577 fichiers, hors `.git` et `node_modules`),
plus lecture des trois implémentations trouvées et de la roue mem0ai 2.0.18.

## Verdict

**Télémétrie RÉELLE, défaut ON, coupée par contrat.**
Trois canaux indépendants, tous opt-out, aucun opt-in. L'adapter
(`aspace-presenton-adapter/`, surface hors-ligne, stdlib seule) ne
démarre aucun serveur et ne fait aucun appel réseau : **télémétrie
zéro par construction pour l'adapter**. Tout serveur presenton
démarré par un appelant DOIT tourner avec l'environnement forcé
(`cli.mjs env`) — sinon les trois canaux émettent.

## 1. Mixpanel — Next.js (le plus large)

**Fichier :** `servers/nextjs/utils/mixpanel.ts` (lu en entier).
**Token codé en dur** dans le source ; hôte `https://api-eu.mixpanel.com`.
Session recording : `record_sessions_percent: 100`,
`record_canvas: true`, `record_collect_fonts: true`,
`track_pageview: false`, `autocapture: false`.

**Défaut : ON.** La porte est `GET /api/telemetry-status`
(`servers/nextjs/app/api/telemetry-status/route.ts`, lu en entier) :
`telemetryEnabled = !isDisabled`, où `isDisabled` =
`DISABLE_ANONYMOUS_TRACKING === "true"` (env) OU la même clé dans le
fichier user-config. **Si l'appel à `/api/telemetry-status` échoue,
le code bascule sur ON** (`window.__mixpanel_telemetry_enabled = true`,
commentaire : « If the API call fails, default to enabling tracking »).

**Étendue :** ~91 sites d'appel distincts dans 30 fichiers
(`grep -rhoE 'trackEvent\(MixpanelEvent\.[A-Za-z_]+'`, 91 noms uniques) :
onboarding, providers, auth, upload, outline, community, éditeur,
templates, dashboard, settings, assistant IA. `MixpanelInitializer`
(`servers/nextjs/app/MixpanelInitializer.tsx`) appelle `initMixpanel()`
au montage et tracke un `PageView` à chaque navigation.
Opt-out : le toggle PrivacySettings écrit
`DISABLE_ANONYMOUS_TRACKING: "true"` dans le user-config — en émettant
d'abord un événement `Usage_Analytics_Disabled` (l'opt-out lui-même
est tracké une dernière fois).

**Interrupteur :** `DISABLE_ANONYMOUS_TRACKING=true` (env ou user-config).

## 2. Sentry — Electron (crash reporting)

**Fichiers :** `electron/app/sentry/main.ts` et
`electron/app/preloads/sentry.ts` (lus en entier) ;
dépendance `@sentry/electron ^7.20.2` (`electron/package.json`).
**DSN codé en dur** dans les deux fichiers
(`https://…@o4509882707410944.ingest.us.sentry.io/4511171070394368`).

**Défaut : ON.** `SENTRY_ENABLED` lu avec `parseBoolean(env, true)` —
opt-out. `initMainSentry()` est appelé **inconditionnellement** au
démarrage (`electron/app/main.ts:201`). Traces : 0.2 en packaged,
1.0 en dev. `sendDefaultPii` défaut false ; feedback et replay
défaut false (renderer). Breadcrumbs : `addMainBreadcrumb` appelé
depuis `electron/app/ipc/export_handlers.ts` et
`electron/app/utils/chromium-cache-recovery.ts`.

**Interrupteur :** `SENTRY_ENABLED=false`.

## 3. mem0 / PostHog — FastAPI (télémétrie serveur)

**Chaîne :** `servers/fastapi/services/mem0_oss_memory.py` construit
`mem0.Memory` (mem0ai 2.0.18, `uv.lock`) ; `posthog 7.81.1` est une
dépendance directe de `mem0ai` (vérifié dans `uv.lock`).
`MEM0_ENABLED` défaut true (`mem0_oss_memory.py`).

**Preuve lue dans la roue mem0ai 2.0.18** (`mem0/memory/telemetry.py`,
extraite de la roue téléchargée) : `MEM0_TELEMETRY` lu avec défaut
`"True"` ; client `Posthog(project_api_key=…, host=
"https://us.i.posthog.com")` ; événements de cycle de vie
(`mem0.init`, `mem0.reset`, `$identify`, …) à 100 %, événements
hot-path échantillonnés à 10 % par défaut
(`MEM0_TELEMETRY_SAMPLE_RATE`).

**Le code presenton ne désactive jamais cette télémétrie en
production** : `MEM0_TELEMETRY=false` n'apparaît que dans les tests
(`servers/fastapi/tests/unit/test_mem0_session_scope_security.py`,
`monkeypatch.setenv`, 2 occurrences). Le `telemetry_base` local
(`<mem0_dir>/telemetry/oss`) n'est que le répertoire de travail
local de mem0, pas une coupure réseau.

**Interrupteur :** `MEM0_TELEMETRY=false`.

## 4. Ce qui n'est PAS de la télémétrie

- `servers/fastapi/services/presenton_cloud.py` : synchronisation
  cloud **initiée par l'utilisateur** (identifiants stockés requis),
  pas une mesure d'usage.
- `scripts/sync-presentation-export.cjs` : `fetch` vers
  `api.github.com` (releases de `presenton-export`) — outil de
  synchronisation invoqué à la main (`npm run sync:presentation-export`),
  pas un envoi automatique.
- `docs/presenton-resource-usage.md` : le mot « telemetry » y désigne
  des mesures de performance locales (échantillons CPU/mémoire),
  pas un envoi.
- OpenTelemetry dans les lockfiles : transitif (Sentry / mem0),
  aucun exporteur configuré par presenton.
- Aucun PostHog / Segment / Amplitude / Mixpanel dans le code
  FastAPI lui-même ; aucun SDK tiers de télémétrie dans les
  `package.json` racine et Next.js (Mixpanel est une dépendance
  directe du frontend, voir §1).

## 5. Coupure par contrat (adapter)

L'adapter ne démarre aucun serveur et ne fait aucun appel réseau
(preuve : `smoke_test.mjs` — `cli.mjs validate` dans `unshare -n`,
exit 0 ; check statique : `cli.mjs` ne contient ni `fetch`, ni
`http`, ni `net`). Tout serveur presenton démarré par un appelant
doit tourner avec :

```
DO_NOT_TRACK=1
DISABLE_ANONYMOUS_TRACKING=true
SENTRY_ENABLED=false
MEM0_TELEMETRY=false
```

(`DO_NOT_TRACK` n'est pas honoré par presenton lui-même — ceinture
et bretelles pour l'outillage aval. Les trois interrupteurs
opératifs sont les trois autres.)

## 6. Preuve réseau

- Smoke test de l'adapter sous `unshare -n` : **VERT 8/8**
  (`logs-presenton-smoke.log`).
- Aucun serveur presenton n'a été démarré pendant cet audit
  (l'adapter ne le fait jamais) — la preuve réseau porte sur
  l'adapter, pas sur les serveurs. Les trois canaux ci-dessus sont
  établis par lecture du code et de la roue mem0ai, pas par capture
  réseau d'un serveur en marche.

## Réserves

1. Le volume exact émis par mem0 (événements, payload) n'a pas été
   capturé sur un serveur en marche — établi par lecture du code
   mem0ai 2.0.18, pas par capture.
2. `DO_NOT_TRACK` n'est pas un interrupteur presenton (non honoré).
3. L'opt-out Mixpanel émet un dernier événement
   (`Usage_Analytics_Disabled`) au moment de la désactivation.
