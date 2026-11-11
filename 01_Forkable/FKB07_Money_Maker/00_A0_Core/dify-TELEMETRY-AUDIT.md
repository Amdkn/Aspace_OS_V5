# Audit télémétrie — dify (D-N048 V4, gel b29552a)

Périmètre : les chemins que l'adapter touche (validation hors-ligne du
dépôt) + les modules de télémétrie connus de l'amont : `api/services/
telemetry_service.py`, `api/tasks/community_telemetry_task.py`,
`api/configs/feature/__init__.py` (`CommunityTelemetryConfig`,
`CHECK_UPDATE_URL`), `api/configs/extra/sentry_config.py`,
`api/configs/observability/otel/otel_config.py`,
`api/extensions/ext_sentry.py`, `api/extensions/ext_otel.py`,
`api/enterprise/telemetry/exporter.py`, `api/core/telemetry/` (gateway),
`web/app/components/base/amplitude/`, `web/instrumentation-client.ts`,
`web/env.ts`, `api/uv.lock` (dépendances). Scan mots-clés
(telemetry, analytics, posthog, sentry, track) : 207 fichiers sous
`api/`, `web/`, `sdks/`, `packages/` — triés ci-dessous, la plupart
étant de la télémétrie applicative interne (traces de workflow) ou des
tests, pas des envois externes.

## §1 — Télémétrie communautaire api/ : RÉELLE, DÉFAUT ON

Mécanisme : `api/services/telemetry_service.py`
(`CommunityTelemetryService`) + `api/tasks/community_telemetry_task.py`
(tâche Celery `community_telemetry.send_heartbeat`, beat toutes les
30 min) + `api/configs/feature/__init__.py:952` (`CommunityTelemetryConfig`).

- **Défaut ON** : `DISABLE_TELEMETRY=false`, `DO_NOT_TRACK=false`,
  `CI=false` (défauts lus au code).
- **Porte** : n'émet que si édition `COMMUNITY` + `DISABLE_TELEMETRY`
  faux + `DO_NOT_TRACK` faux + `CI` faux + endpoint non vide
  (`_is_enabled`, `telemetry_service.py:78`).
- **Endpoints** : `https://otel.dify.ai/v1/events`, repli
  `https://otel.dify.cn/v1/events` (POST httpx, timeout 3 s).
- **Événements** : `install` (1×) et `heartbeat` (tâche toutes les
  30 min, mais `_is_heartbeat_due` limite à 1/jour — même date calendaire
  = pas de renvoi).
- **Charge anonyme** : event, `instance_id` (UUID aléatoire local),
  version, édition, `deployment_type: "unknown"`, schema_version 1, os,
  arch, sent_at, installed_at (install seulement). Aucune donnée
  utilisateur, aucun tenant, aucun contenu.

## §2 — Sentry : OFF par défaut (deux côtés)

- api : `api/extensions/ext_sentry.py` — `sentry_sdk.init` uniquement
  `if dify_config.SENTRY_DSN` ; `SENTRY_DSN` défaut `None`
  (`sentry_config.py`), `.env.example` vide. Sample rates 1.0 par défaut
  mais inertes sans DSN.
- web : `web/instrumentation-client.ts:49-61` — init uniquement si
  `!IS_DEV && SENTRY_DSN` (`NEXT_PUBLIC_SENTRY_DSN` optionnel) ;
  traces 0.1, replay session 0.1, replay erreur 1.0.

## §3 — OpenTelemetry : OFF par défaut

`api/configs/observability/otel/otel_config.py` : `ENABLE_OTEL=false`
par défaut ; endpoint de base `http://localhost:4318` (local) ; pas de
clé par défaut. `api/extensions/ext_otel.py` + instrumentation OTel
(`extensions/otel/`) inertes sans `ENABLE_OTEL`. OTel entreprise :
`ENTERPRISE_TELEMETRY_ENABLED=false` par défaut, et la porte exige
l'édition `ENTERPRISE` (`enterprise/telemetry/exporter.py:50`).

## §4 — Amplitude web : OFF par défaut (double porte)

SDK `@amplitude/analytics-browser` dans `web/package.json`. Init dans
`web/app/components/base/amplitude/init.ts` : `shouldOptOut` vaut `true`
par défaut (opt-out jusqu'à consentement) ET `AMPLITUDE_API_KEY` vaut
`''` par défaut (`web/config/index.ts`, `NEXT_PUBLIC_AMPLITUDE_API_KEY`
optionnel). `ensureAmplitudeInitialized` retourne sans rien faire si
pas de clé ou opt-out. Aucun envoi sans clé posée par l'opérateur.

## §5 — Autres envois externes (déclenchés par l'usage, pas en fond)

- **Version-check** : `GET /console/version`
  (`api/controllers/console/system.py:43`) → `httpx.get` vers
  `https://updates.dify.ai?current_version=…` — déclenché uniquement
  quand la console appelle l'endpoint ; rien si `CHECK_UPDATE_URL`
  vide. Pas un battement de fond.
- **Marketplace / templates** : `https://marketplace.dify.ai`,
  `https://creators.dify.ai`, `https://tmpl.dify.ai` — défauts de
  configuration, appelés lors d'un usage explicite (parcours du
  marketplace / modèles), pas en fond.
- **Icônes** : `https://assets.dify.ai/images/…` — URL codée en dur
  (référence d'asset, pas un envoi).
- **Scarf** : `SCARF_NO_ANALYTICS` déclaré en config
  (`feature/__init__.py:1382`), lu par la librairie Unstructured
  elle-même ; aucune émission dans le code dify.

## §6 — PostHog : dépendance transitive inutilisée

`posthog 7.0.1` présent dans `api/uv.lock` (dépendance de `chromadb`,
`uv.lock:916-937`) ; **zéro import** `posthog` dans `api/` (source) et
absent de `pyproject.toml`. Jamais importé, jamais appelé.

## §7 — Télémétrie applicative interne (pas d'envoi externe)

`api/core/telemetry/` (gateway : routage vers la pipeline de traces ou
la file Celery entreprise, no-op en CE derrière des imports paresseux)
et `api/enterprise/telemetry/` (traces/métriques internes) ne sortent
pas du déploiement sans exporteur configuré (OTel off, entreprise off).
Les 207 fichiers du scan sont majoritairement ces traces internes,
des filtres de log et des tests.

## §8 — Preuve réseau

L'adapter lui-même est prouvé sans réseau : `smoke_test.py` exécute
`validate` sous `unshare -n` (namespace sans interface) — 10/10, dont
le cas sans réseau. La télémétrie communautaire (§1) n'est pas
exercée par l'adapter : l'adapter ne démarre jamais `api/`, donc
aucun battement Celery n'est déclenché par lui. La coupure par contrat
est documentée dans `contract.json` (`telemetry_cut_switches`) :
`DISABLE_TELEMETRY=true` + `DO_NOT_TRACK=true` + `CI=true`,
`ENABLE_OTEL=false`, `SENTRY_DSN` unset — à appliquer au déploiement,
pas à l'adapter.

## Conclusion

**Télémétrie zéro par contrat pour l'adapter** (il n'émet rien et ne
démarre rien). **Télémétrie réelle dans l'amont, défaut ON pour un seul
mécanisme** : la télémétrie communautaire anonyme (§1), coupée par les
trois interrupteurs nommés. Tout le reste (Sentry, OTel, Amplitude,
OTel entreprise) est OFF par défaut et exige une configuration
explicite de l'opérateur. Aucun SDK tiers de télémétrie n'est appelé
par l'adapter ; PostHog n'est qu'une dépendance transitive morte.
