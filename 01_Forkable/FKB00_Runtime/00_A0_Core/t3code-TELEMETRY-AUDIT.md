# Audit télémétrie — t3code (D-N048 V3b)

**Fork :** `Amdkn/t3code`, gel `dc72705`. **Télémétrie réelle dans l'amont (PostHog, défaut ON, clé codée en dur), forcée off par l'adapter.**

## 1. Scan statique

### 1a. Émetteur premier : `apps/server/src/telemetry/AnalyticsService.ts` (service Effect, ~330 lignes)

**Pas de SDK PostHog** — envoi HTTP maison (`effect/http/HttpClient`), aucune dépendance `posthog-js` / `@posthog/*` dans aucun `package.json` du monorepo (vérifié). Pas de Sentry, Segment, Mixpanel, Amplitude dans aucun manifeste (vérifié).

Configuration par défaut, lue dans `TelemetryEnvConfig` :

| Variable | Défaut codé en dur | Effet |
|---|---|---|
| `T3CODE_POSTHOG_KEY` | `phc_XOWci4oZP4VvLiEyrFqkFjP4CZn55mjYYBMREK5Wd6m` | clé API PostHog du projet amont, **dans le code source** |
| `T3CODE_POSTHOG_HOST` | `https://ingest.t3.codes` | hôte d'ingest first-party (reverse-proxy vers PostHog Cloud) |
| `T3CODE_TELEMETRY_ENABLED` | `true` | **télémétrie ON par défaut** |

Envoi : `POST {host}/batch/` avec `{ api_key, batch: [{ uuid, event, distinct_id, properties, timestamp }] }`. Propriétés envoyées : `installId`, `platform`, `arch`, `t3CodeVersion`, `telemetryChannel` (`dev` par défaut, `config.ts:26`), `clientType` (`desktop-app` / `cli-web-client`), `serverOs`, `serverArch`, `serverWslDistro`, `serverAppVersion`, `serverMode`. Flush de fond toutes les 10 s (`FLUSH_INTERVAL_MS`), lots de 20, retry jusqu'à 30 min (`MAX_BATCH_RETRY_MS`), flush de fermeture 1 s. Un lot rejeté (400/401/413) est abandonné.

Identité (`apps/server/src/telemetry/Identify.ts`) : `distinctId` par installation ; `recordOwners` envoie `install.owner_observed` une fois par propriétaire et par processus — propriétaires = compte T3 Connect, compte OpenAI (ChatGPT, `account_id`/`user_id` hachés via `hashTelemetryId`), compte Claude (`userID` / `accountUuid` hachés), appareil client. Les identifiants bruts ne sont jamais envoyés, leurs hachés le sont.

Câblage : le service est chargé par la couche serveur (`apps/server/src/server.ts`, `serverRuntimeStartup.ts`) — **tout démarrage du serveur `t3` embarque l'émetteur**.

### 1b. Contenu vendu (hors périmètre de l'adapter, consigné)

`.repos/` (24 120 fichiers suivis) contient des dépôts tiers vendus dans l'arbre : `alchemy-effect` (site docs, SDK navigateur PostHog `website/src/components/analytics/PostHog.astro`, proxy `analytics.alchemy.run` → PostHog Cloud US) et `effect` (types générés OpenRouter `ObservabilityPosthogDestination`). Ce ne sont **pas** du code t3code, jamais exécutés par la surface de l'adapter (CLI `t3` seule). Notés, non comptés comme télémétrie du module.

### 1c. Autres appels réseau du serveur (hors télémétrie, non exercés par l'adapter)

`apps/server/src/cli/` (connect, pair, update, cloud, auth provider) et `apps/server/src/cloud/` font des appels HTTP sortants (connexion T3 Connect, mises à jour, auth fournisseurs). L'adapter n'expose aucune de ces commandes : surface limitée aux commandes qui parlent seulement (`--help`, `--version`, `help`, `doctor --dry-run`).

## 2. Consentement et interrupteurs

- **`T3CODE_TELEMETRY_ENABLED=false`** : l'interrupteur. Il coupe `record` ET `sendBatch` entièrement (`if (!(yield* telemetryEnabled) ...) return`). C'est ce que l'adapter force.
- **Managed policy** (`apps/server/src/cli/policy.ts:113`, `ManagedPolicy`) : un refus de politique (`telemetry: false`) coupe la télémétrie — **off seulement, jamais on**.
- **Shell consent (desktop)** : `T3CODE_DESKTOP_SHELL_DISCOVERY_PENDING=1` retient l'envoi tant que le consentement du shell n'est pas établi — flux desktop seulement, pas le CLI.
- **`DO_NOT_TRACK` n'est PAS honoré** : zéro occurrence dans `apps/server/src` et `packages/*/src`.
- **Pas de prompt de consentement au démarrage du CLI** ; pas d'opt-out persistant côté CLI en dehors de la variable d'environnement.

## 3. Preuve d'exécution

- **Smoke test de l'adapter** (voir `aspace-t3code-adapter/smoke_test.mjs`) : n'exécute que des commandes qui parlent seulement (`--help`, `--version`, `help`, `doctor --dry-run`) sous `T3CODE_TELEMETRY_ENABLED=false` (et `T3CODE_POSTHOG_KEY` vidé, `T3CODE_POSTHOG_HOST` vidé, par défense en profondeur), maison T3 scratch, stdin fermé. Ces commandes ne démarrent pas le serveur : **le service `AnalyticsService` n'est jamais chargé**.
- **Preuve réseau** : le smoke test vérifie en plus, quand `unshare` est disponible, que `--help` s'exécute dans un namespace sans interface réseau (`unshare -n`) — zéro appel sortant possible par construction, pas seulement par absence observée.

## Conclusion

**PostHog réel, défaut ON, clé codée en dur, forcé off par l'adapter.** L'émetteur est un module maison (pas de SDK tiers), branché sur chaque démarrage de serveur, avec clé et hôte par défaut dans le code. L'adapter ne démarre jamais le serveur et force `T3CODE_TELEMETRY_ENABLED=false` (plus clé/hôte vidés) : **télémétrie zéro par contrat** pour la surface exposée. La seule voie d'envoi restante exigerait de lancer le serveur sans les interrupteurs — hors contrat de l'adapter.
