# Audit télémétrie — openrig (D-N051 F8, pas 4)

**Gel :** `bd39da9` (`bd39da9872afc39cbe0c8e839a322b4cb8955cbe`, 0.7.1),
fork `Amdkn/openrig`, branche `main`.
**Périmètre :** `packages/daemon/src/` (le daemon Hono + websocket) et
les `package.json` des 5 paquets. Méthode : lecture des sources au
fichier (pas de code search API — voir §1), inventaire des `fetch(`,
scan des dépendances.
**Verdict : zéro exporteur, zéro SDK ; une surface de lecture LOCALE
existe (correction §1) ; 4 sites sortants, tous fermés par défaut.**

## 1. Correction : le design affirmait « télémétrie 0 » — c'est faux

Le design (et Clara, via code search API) affirmait : `telemetry` 0,
`posthog` 0, `sentry` 0, `analytics` 0. La lecture des sources au gel
contredit la première affirmation :

- `packages/daemon/src/routes/telemetry.ts` (**95 lignes**) : 6 routes
  de lecture — `/api/telemetry/v1/events`,
  `/v1/queue-transitions`, `/v1/nodes/:nodeId/tenures`,
  `/usage/series`, `/usage/cost`, `/usage/top` (montées dans
  `server.ts:891` sous `/api/telemetry`).
- `packages/daemon/src/domain/finite-telemetry.ts`,
  `usage-series.ts`, `usage-samples-store.ts`,
  `telemetry-state-paths.ts`, `pi-usage-entries-store.ts`,
  `pi-usage-facts.ts`, `context-usage-store.ts` : le domaine de lecture
  (échantillons d'usage, coûts, tenures).
- L'en-tête de `routes/telemetry.ts` (51-08 A3) le dit : « the telemetry
  read surface over usage_samples — facts only; thresholds and
  judgments live at the edge. Option-A bar: **no account identity in
  any response** ».

**Ce que c'est :** une projection de lecture **locale** sur le SQLite
du daemon (`usage_samples`) — faits seulement, aucune identité de
compte, aucun envoi. **Ce que ce n'est pas :** un exporteur (aucun
`fetch` sortant dans ces fichiers, aucun SDK). La conclusion « zéro
par défaut » tient ; la prémisse « 0 signal » est corrigée et portée
en avant — le code search API ne fait pas foi ici, la lecture au
fichier fait foi.

## 2. Zéro SDK, zéro exporteur (vérifié)

Scan de `package.json`, `packages/daemon/package.json`,
`packages/cli/package.json`, `packages/tui/package.json`,
`packages/ui/package.json` : `posthog` 0, `sentry` 0, `segment` 0,
`mixpanel` 0, `amplitude` 0, `datadog` 0, `newrelic` 0,
`opentelemetry` / `@opentelemetry` 0. Le daemon dépend de `hono
^4.7.0`, `better-sqlite3 ^13.0.3`, `yaml`, `ulid` — aucune dépendance
télémétrie. **Aucun exporteur n'est câblé.**

## 3. Inventaire des `fetch(` du daemon (gel)

Tous les appels sortants du daemon, avec leur sort (8 sites) :

| Site | Destination | Sort |
|---|---|---|
| `adapters/pi-runner.ts:1319/1339/1375` | `endpoint.baseUrl` du daemon (`/api/activity/pi-usage-charges`, `/api/activity/hooks`, `/api/activity/pi-usage`) | **Loopback** — le daemon s'appelle lui-même |
| `adapters/stub-runner.ts:361` | `endpoint.baseUrl` (`/api/activity/hooks`) | **Loopback** |
| `daemon-db-path.ts:126` | `http://127.0.0.1:<port>/healthz` | **Loopback** (vérification de conflit de DB) |
| `domain/crash-cart-probes.ts:78` | URL injectée par l'appelant | **Loopback en pratique** (sonde de santé du daemon lui-même) |
| `domain/gateway/slack/slack-api.ts:105/119/126` | `https://slack.com/api/*` | **Fermé par défaut** — passerelle Slack, clé Bearer requise ; l'hôte est épinglé (`slack.com` exact, jamais un sous-domaine forgé) |
| `adapters/pi-openrouter-charge.ts:68` (`domain/openrouter-charge.js` : `OPENROUTER_GENERATION_URL`) | `https://openrouter.ai/api/v1/generation?id=…` | **Fermé par défaut** — `--openrouter-charge` seulement (`usage.pi_openrouter_charge`, opt-in) |
| `routes/hosts.ts:435/481` | URL d'un hôte distant fournie par l'opérateur (`/api/hosts/pair-request`) | **Fermé par défaut** — pairing initié par l'opérateur |
| `startup.ts:1045` (`domain/plugin-vendor-service.ts:61`, `REPO_BASE = https://github.com/mvschwarz/openrig-plugins`) | `github.com` | **Fermé par défaut** — fetch des assets du plugin `openrig-core` au démarrage ; tolère 404 / erreurs réseau |

**Bilan :** 4 sites loopback (le daemon vers lui-même), 4 sites
sortants — **aucun n'est actif par défaut sans une décision explicite
de l'opérateur** (clé Slack, flag `--openrouter-charge`, pairing,
fetch du plugin-vendor). Le port natif ne reprend **aucun** des 4
sites sortants : le daemon unique ne fetch pas le plugin-vendor au
démarrage, n'appelle pas Slack, ne fait pas de lookup OpenRouter, ne
paire pas d'hôte distant. La garde-fou de l'adapter
(`installOutboundGuard`, liste loopback seulement) les refuse tous
par défaut — prouvé par le smoke (fetch `github.com` bloqué avant
tout accès réseau ; `posthog` bloqué même quand autorisé).

## 4. Surface réseau du daemon (Hono + websocket)

- **Bind :** `packages/daemon/src/domain/bind-plan.ts` (OPR.0.5.5.20) —
  l'intention de bind ne passe QUE par `OPENRIG_BIND_HOST` ; le défaut
  est `["127.0.0.1"]` **plus l'IP tailscale quand une interface
  tailscale existe** ; un `OPENRIG_BIND_HOST` explicite surcharge.
  L'env de routage (`OPENRIG_HOST` / `RIGGED_HOST`) est observé, jamais
  consulté pour le bind. **Nuance portée en avant :** le défaut amont
  n'est pas loopback-only quand une IP tailscale existe — l'adaptateur
  A'Space le surcharge (`resolveAspaceBind()` → toujours
  `["127.0.0.1"]`, en consignant ce que l'amont aurait lié).
- **Serveur invité :** `packages/daemon/src/index.ts:346` — sert sur
  `OPENRIG_GUEST_ACTIVITY_HOST ?? "127.0.0.1"` (loopback par défaut).
- **URL d'activité des sièges :** dérivée de l'hôte + port liés du
  daemon (`startup.ts:654`, `domain/activity-endpoint.ts`) — les
  hôtes wildcard (`0.0.0.0` / `::`) sont rabattus sur `127.0.0.1`.
  Les sièges postent leurs hooks vers le daemon lui-même, en loopback.
- **Websocket :** la surface Hono sert aussi le canal websocket du
  daemon (même bind loopback, même plan). Aucun listener sur
  `0.0.0.0` n'a été trouvé dans `packages/daemon/src/` (seule mention :
  le rabattement wildcard → loopback et une note dans
  `domain/bundle-behaviour.ts:395` sur un listener dev Vault déclaré
  `0.0.0.0:8200` — une déclaration, pas le daemon).
- **Aucune exposition au-delà de localhost** dans la configuration
  A'Space (bind forcé 127.0.0.1, garde-fou sortant, zéro exporteur).

## 5. Ce que le port natif reprend — et ne reprend pas

- **Reprend :** la lecture télémétrie locale — `usage_series()` dans
  `openrig_state.rs` (même projection : échantillons par siège,
  fenêtre, limite ; faits seulement, aucune identité de compte).
- **Ne reprend pas :** le fetch plugin-vendor, la passerelle Slack,
  le lookup OpenRouter, le pairing d'hôtes. Aucun de ces 4 sites
  n'existe dans le code natif.
- **Ne reprend pas :** le serveur Hono lui-même (les routes sont
  ré-implémentées en Rust — la parité des routes `/api/telemetry/*`
  est un travail d'intégration).

## 6. Verdict

**Télémétrie zéro par défaut — PASS (H-P4-7, H-M4).** Zéro SDK, zéro
exporteur, surface de lecture locale seulement, 4 sites sortants tous
fermés par défaut, binding 127.0.0.1 seulement (avec la surcharge
tailscale documentée et refusée). La correction du §1 (la surface
locale existe) ne change pas le verdict — elle le précise.
