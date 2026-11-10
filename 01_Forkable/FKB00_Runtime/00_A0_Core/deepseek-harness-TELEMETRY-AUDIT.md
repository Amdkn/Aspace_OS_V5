# Audit télémétrie — deepseek-harness (D-N048 V3b)

**Fork :** `Amdkn/deepseek-harness`, gel `fcc0ad4` (branche `master`). **Télémétrie présente dans l'amont, maison, coupée par interrupteur.**

## 1. Scan statique

- **Aucun SDK télémétrie tiers** : zéro occurrence de `posthog`, `@sentry`, `mixpanel`, `amplitude`, `segment` dans aucun `package.json` du monorepo ni dans `pnpm-lock.yaml` (vérifié par grep sur tous les `package.json` + le lock).
- **Module maison n° 1 — `packages/client/product-analytics`** (`@deepseek-ai/dsh-client-product-analytics` 0.2.2-rc.1) : « Desktop-only analytics RPC and live compaction collection ». Service Cordis `ProductAnalytics` (TypertRemoteService), `enabled` **défaut `true`** (`z.boolean().default(true).volatile()`, `index.ts`), intake authentifié (« Authenticated event intake; disabled instances do not inspect identity or accept new events »). Événements déclarés (`src/events.ts`) : `desktop_app_launch`, `auth_page_view/click`, `api_key_save_click`, `onboarding_*`, `send_button_click` (avec `session_id`, `model_name`, `thinking_effort`, `run_mode`), `model_switch`, `thinking_level_switch`, `context_compression` (avec `session_id`, déclencheur auto/manuel), `branch_session_click`, `sidebar_menu_click`, `plugin_toggle/install/uninstall`, `agent_preset_switch`, `code_work_view_toggle`. Le service rapporte `context_compression` à chaque compaction de session (`session/event`).
- **Module maison n° 2 — `packages/host/product-telemetry-otel`** (`@deepseek-ai/dsh-host-product-telemetry-otel`) : adaptateur OTel. Exporteur OTLP/HTTP, **endpoint par défaut `https://dsh-otel-collector.deepseeksvc.com/v1/logs`**, canal `dsh_otel_report` (`src/index.ts:47-48`). Honore `OTEL_EXPORTER_OTLP_LOGS_COMPRESSION` / `OTEL_EXPORTER_OTLP_COMPRESSION`.
- **Montage** : `productAnalytics` est monté par l'app **Desktop** (`apps/desktop/src/main.ts`, `welcome-backend.ts`) et le bundle web (`packages/bundle/web-app`) — pas par le CLI lui-même. Le CLI (`apps/cli`) démarre des profils ; la ligne télémétrie fait partie de la composition du profil (voir §2).
- Le mot-clé `telemetry` apparaît dans ~474 fichiers du repo, quasi tous de la documentation/notes (`.agents/notes/`) ou des tests ; les deux seuls modules d'émission sont ceux ci-dessus.

## 2. Consentement et interrupteurs

- **Interrupteur d'exécution (CLI) — `DSH_TELEMETRY_DISABLED`** : toute valeur non vide désactive durement la télémétrie. `resolveTelemetryPatch(disabledEnv, hasRow)` (`packages/boot/app-boot/src/profile-context.ts:52-55`) retourne `{ id: TELEMETRY_ROW_ID, disabled: true }` quand la variable est posée ; le patch est ajouté à la composition du profil (`readProfilePatches`, `profile-context.ts:81-83`) et branché dans le lanceur CLI (`apps/cli/src/profile-boot.ts:321`, `telemetryDisabledEnv: process.env.DSH_TELEMETRY_DISABLED`).
- **Pas de surface de réglage utilisateur** pour ce collecteur (« Application-owned collection policy; no user settings surface », `packages/client/product-analytics/src/index.ts`) : l'interrupteur est l'env var, pas un réglage d'interface.
- **L'adapter force `DSH_TELEMETRY_DISABLED=1`** sur chaque invocation et ne démarre jamais un profil (jamais `dsh --profile …`, jamais de serveur, jamais d'appel modèle) : les sous-commandes exposées (`--help`, `--version`, `dump-config`) n'amorcent pas le service `productAnalytics`.
- Double barrière : interrupteur d'env + absence de montage (les commandes de l'adapter ne montent aucun profil Desktop/web).

## 3. Preuve d'exécution

Smoke test de l'adapter : `node --test aspace-deepseek-harness-adapter/smoke_test.mjs`,
**5/5 PASS** (2026-11-09 ~19:5x EST, après `pnpm install --frozen-lockfile` OK,
2,1 Go, pnpm v11.28.5). Les 5 checks invoquent le lanceur source
(`node --import tsx/esm apps/cli/src/bin.ts`) avec `DSH_TELEMETRY_DISABLED=1` et
`DSH_HOME=<scratch>` : `--help` (exit 0), `--version` (`0.2.2-rc.1`),
`--profile headless --dump-config` (arbre composé, sans boot),
`--profile headless --dump-config-schema` (JSON Schema, sans montage).

Aucune de ces commandes ne monte un profil : `--dump-config` compose et imprime
puis sort ; `--dump-config-schema` n'évalue pas `!!js`. La ligne télémétrie
(`productAnalytics`) n'est donc jamais instanciée, et aucun appel vers
`dsh-otel-collector.deepseeksvc.com` n'est possible depuis ces commandes.
Aucun trafic réseau sortant n'a été observé pendant le smoke test (les
invocations sont locales ; la seule activité réseau de la session est le
`pnpm install` des dépendances, antérieur).

## Conclusion

**Télémétrie maison réelle, coupée par contrat** : pas de SDK tiers ; deux modules maison (collecteur d'événements Desktop, défaut ON ; exporteur OTLP vers `dsh-otel-collector.deepseeksvc.com`) ; interrupteur unique et vérifiable `DSH_TELEMETRY_DISABLED=1`, forcé par l'adapter sur chaque invocation, et surface limitée aux commandes qui parlent seulement (`--help`, `--version`, `--dump-config`, `--dump-config-schema`).
