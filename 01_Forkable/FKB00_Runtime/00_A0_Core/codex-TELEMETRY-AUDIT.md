# Audit télémétrie — codex (D-N048 V3b)

**Fork :** `Amdkn/codex`, gel `27fcd7c`. **Télémétrie présente dans l'amont, coupée par contrat.**

## 1. Scan statique

### 1.1 Aucun SDK tiers de télémétrie produit

- **Zéro PostHog / Segment / Mixpanel / Amplitude** dans tout le workspace (168 crates, `codex-rs/Cargo.toml` + tous les `Cargo.toml` membres, grep complet).
- Deux SDK présents, tous deux **maison / premier parti** :
  - `sentry = "0.46.0"` (workspace) — utilisé **uniquement** par `codex-rs/feedback/` (voir §1.3).
  - `opentelemetry 0.31.0` + `opentelemetry-otlp` + `opentelemetry-appender-tracing` + `tracing-opentelemetry` — exporteurs **configurés explicitement ou absents** (voir §1.4).

### 1.2 Analytics maison, premier parti (`codex-rs/analytics/`, 10 660 lignes)

- `AnalyticsEventsClient` (`client.rs:118`) émet vers `{chatgpt_backend_url}/codex/analytics-events/events` :
  - défaut `https://chatgpt.com/backend-api/` ; variante gov `https://gov.chatgpt.com/backend-api/` ; un proxy explicite est possible (`client_tests.rs:357`).
  - **Hôte unique, premier parti (OpenAI)** — aucun hôte tiers.
- Contenu : **faits d'usage structurés** (reducer `reducer.rs`, faits `facts.rs`) — usage de tokens (`TurnTokenUsageFact`), statuts d'appels d'outils (`CodeModeToolCallFact`, `ControlToolCallFact`), compaction (`CodexCompactionEvent`), mesures plugins/skills (`PluginMeasurementsInput`, `SkillInvocation`), revue Guardian (`GuardianReviewEventParams`). **Aucun contenu de fichier, aucun texte libre.**
- Transport : file d'événements (256 messages, timeout 10 s, flush 25 s), déduplication (4 096 clés). Les secrets fournisseurs et en-têtes gateway sont **retirés** des requêtes analytics (`client.rs:140`).
- `AnalyticsEventsClient::disabled()` est utilisé dans de nombreux chemins (handlers bespoke `bespoke_event_handling.rs`, `command_exec.rs`) — ces chemins n'émettent jamais.

### 1.3 Sentry = feedback explicite seulement (`codex-rs/feedback/`)

- DSN codé en dur (`lib.rs:62`) : `https://ae32ed50620d7a7792c1ce5df38b3e3e@o33249.ingest.us.sentry.io/4510195390611458`.
- **Aucun `sentry::init` dans tout le workspace** — pas de crash reporting automatique. Le SDK ne sert qu'à `upload_feedback` (envoi explicite, initié par l'utilisateur : `codex feedback` / rapport) et à `save_feedback` (export local, sans envoi).
- `feedback.enabled = false` coupe les envois de feedback et la rétention de revue Guardian en arrière-plan (`FeedbackConfigToml`, `config/src/types.rs`).

### 1.4 OpenTelemetry = opt-in par configuration

- Exporteurs `otel.exporter` / `otel.trace_exporter` / `otel.metrics_exporter` (`OtelExporterKind`) — tous `Option`, **défaut : aucun exporteur** (`otel_init.rs: build_provider` retourne `None` sans export configuré).
- L'exporteur de métriques intégré (`Statsig`) est **soumis au consentement analytics** (coupé si analytics désactivé). Les collecteurs OTLP explicites ne le sont **pas** (doc `AnalyticsConfigToml` : les couper exige `otel.metrics_exporter = "none"`).
- `code-mode-host` : flags CLI `--otel-trace-listen` / `--otel-trace-exporter`, opt-in explicite.
- Télémétrie du daemon de mise à jour (`cli/src/daemon_telemetry.rs`) : **une seule métrique** `codex.daemon.update` (résultat de mise à jour), émise uniquement si un fournisseur OTEL a été construit (exporteur configuré), avec chargement de la configuration sous consentement et timeout 2 s.

## 2. Consentement et interrupteurs

- **Défaut analytics : ON pour le CLI interactif** (`client.rs:403` — file créée sauf `analytics_enabled == Some(false)` ; `config.analytics_enabled` vient de `analytics.enabled` dans `config.toml`, `None` par défaut). **OFF par défaut pour `app-server`** (opt-in explicite `--analytics-default-enabled`, `cli/src/main.rs:618,631`).
- **Interrupteurs** (un seul suffit) :
  - `config.toml` : `[analytics] enabled = false` (par profil, `AnalyticsConfigToml.enabled`) — coupe les événements analytics sur toutes les surfaces du produit.
  - `[feedback] enabled = false` — coupe les envois Sentry de feedback.
  - `otel.metrics_exporter = "none"` — coupe les exporteurs OTLP de métriques (les collecteurs explicites ne suivent pas le consentement analytics).
  - Builds debug uniquement : `CODEX_ANALYTICS_EVENTS_CAPTURE_FILE=<chemin>` redirige les événements vers un JSONL local (mode 0600) et **désactive l'envoi réseau** (`analytics_capture.rs`, `client.rs:159-167`).
- **L'adapter force `analytics.enabled=false` + `feedback.enabled=false` via overrides CLI `-c`** (même mécanisme que les tests amont, `app-server/tests/suite/v2/feedback.rs:402`), avec `CODEX_HOME` scratch et variables `OTEL_*` démontées. Double barrière : overrides + absence de configuration d'exporteur.

## 3. Preuve d'exécution

Preuve acquise par le smoke test (binaire debug `codex-rs/target/debug/codex`, construit au gel `27fcd7c` avec Rust 1.95.0, maison scratch `CODEX_HOME`, overrides forcés `-c analytics.enabled=false -c feedback.enabled=false`, `OTEL_SDK_DISABLED=1`) : `--version` passe **sans interface réseau** (`unshare -n`, 6/6 checks, log `logs-codex-smoke.log`). Le binaire ne peut émettre que vers le backend ChatGPT (premier parti) et ne le fait que si `analytics.enabled` n'est pas `false` ; avec les overrides, la file d'événements n'est pas créée (`client.rs:403`).

## Conclusion

**Télémétrie zéro par contrat** : analytics premier parti réel mais coupée à la source (overrides `-c analytics.enabled=false -c feedback.enabled=false`, maison scratch, pas d'exporteur OTLP configuré) ; Sentry limité au feedback explicite (jamais invoqué par l'adapter) ; aucun SDK tiers. L'adapter n'expose que des sous-commandes qui parlent seulement (`--help`, `--version`).
