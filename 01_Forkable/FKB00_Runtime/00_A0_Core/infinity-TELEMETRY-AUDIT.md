# Audit télémétrie — infinity (D-N051 F8 pas 3)

**Fork :** `Amdkn/infinity` ← `hydro-project/infinity`, gel `e1a3e4b`
(dérive 0) · **Date :** 2026-11-10 · **Périmètre :** fork entier
(daemon + providers + slack-bot, §D9) · **Verdict : télémétrie
zéro par défaut ; 0 appel sortant sans configuration.**

## 1. Recherche de signaux (code search, vérifié)

| Motif | `.rs` | `.toml` |
|---|---|---|
| `telemetry` | 0 | 0 |
| `posthog` | 0 | 0 |
| `sentry` | 0 | 0 |
| `analytics` | 0 | 0 |
| `segment.io` / `amplitude` / `mixpanel` | 0 | 0 |

Aucun SDK de télémétrie, aucun envoi d'événement, aucun beacon.
L'endpoint EGM du bind (`http://127.0.0.1:31415/v1/chat/completions`)
n'existe pas dans le fork — il vit côté V5 uniquement.

## 2. Surface réseau du daemon (portée du pas)

| Appel | Fichier | Cible | Statut |
|---|---|---|---|
| Socket Unix du daemon | `lib.rs:62` | `~/.infinity/daemon.sock` (local) | OK, local |
| WebSocket | `lib.rs:86` | `INFINITY_WS_BIND` défaut `127.0.0.1:8080` | OK par défaut — voir R-2 |
| Proxy MCP | `mcp_proxy.rs:130` | `TcpListener::bind("127.0.0.1:0")` | OK, loopback |
| Callback RAP (bridge) | `rap-client/src/callback_server.rs:18` | `TcpListener::bind("127.0.0.1:0")` | OK, loopback |
| POST résultat MCP | `mcp_proxy.rs:80` | `invocation.callback_url` (fournie par l'appelant) | OK si loopback — voir R-3 |
| POST choix utilisateur | `client_handler.rs:610` | `pending.response_url` (fournie par l'appelant) | Voir R-3 |
| Connexions distantes | `remote.rs:147,433` | socket Unix local + SSH vers remotes **configurées** | Voir R-4 |
| Serveurs RAP de test | `rap-test-servers/src/lib.rs:48,177` | `127.0.0.1:0` + POST vers callback URL | OK, loopback |
| Client HTTP RAP | `rap-client/src/http.rs:58` | `server_url` de la config RAP | Configuré, pas de défaut externe |
| Client callback | `rap-protocol/src/lib.rs:265` | callback URL fournie | Voir R-3 |

**Aucune écoute `0.0.0.0` dans le daemon.** Le daemon démarre sans
provider configuré : **0 appel sortant par défaut**.

## 3. Providers et slack-bot (hors périmètre, §D9 — nommés, non portés)

| Composant | Appels externes | Gating |
|---|---|---|
| `infinity-provider-bedrock` | API AWS Bedrock (`aws-sdk-bedrockruntime`) | Clés AWS — externe par conception |
| `infinity-provider-rig` | Backends `rig-core` (Anthropic / OpenAI / … selon config) | Clés provider — externe par conception |
| `infinity-slack-bot` | API Slack (`slack_client.rs`, `slack_io.rs:749`) | Bot token — externe par conception |
| `infinity-agent-lambda` | `rap_http.rs:31` POST vers URL RAP configurée | Config |
| `sandbox-remote` | AWS SigV4 (`sigv4_client.rs`) | Clés AWS |

Ces appels n'existent que si l'opérateur les configure (clés +
endpoints) : ils ne sont jamais déclenchés par l'adapter ni par le
daemon natif, qui ne portent ni provider ni slack-bot.

## 4. Réserves

- **R-1 — `0.0.0.0` hors daemon (3 sites, non démarrés par le pas) :**
  `rap-steering-server/src/main.rs:161`,
  `rap-github-event-poller/src/main.rs:171`,
  `sandbox-local/src/server.rs:25` lient `0.0.0.0:{port}`. Ce sont
  des rôles serveur (webhook GitHub, pilotage, sandbox) — ils ne
  sont ni démarrés par le daemon, ni par l'adapter, ni par le
  daemon natif. À trancher si un jour ils entrent dans le Runtime
  (liaison loopback ou exposition explicite par arbitrage vision).
- **R-2 — `INFINITY_WS_BIND` surchargeable :** le défaut est
  `127.0.0.1`, mais la variable d'environnement peut le changer.
  Le daemon natif **refuse** toute valeur non loopback
  (`require_loopback`, erreur au démarrage) ; l'amont ne le refuse
  pas. L'adapter exige loopback (`LocalhostPolicy`).
- **R-3 — URLs de callback fournies par l'appelant :** `callback_url`
  (RAP) et `response_url` (choix utilisateur) sont des cibles POST
  dont l'hôte vient de l'appelant. Le proxy MCP **natif** refuse
  toute callback URL non loopback ; l'amont ne la valide pas. Un
  toolset malveillant ne peut donc pas exfiltrer via le daemon
  natif — mais l'amont, lui, posterait.
- **R-4 — Remotes configurées :** `remote.rs` ouvre du SSH vers les
  daemons distants listés dans la config utilisateur. Aucune remote
  par défaut ; chaque remote est un choix explicite de l'opérateur.

## 5. Conclusion (H-M4 / H-P3-8)

**Télémétrie zéro, vérifié :** 0 signal, 0 SDK, 0 appel sortant par
défaut, surface daemon loopback seulement. Les seuls appels
externes possibles sont (a) les providers / Slack, clé-gatés et non
portés, (b) les URLs de callback fournies par l'appelant, validées
loopback côté natif, (c) les remotes SSH configurées. Les 3 écoutes
`0.0.0.0` du fork sont hors daemon et hors pas — consignées en R-1.
