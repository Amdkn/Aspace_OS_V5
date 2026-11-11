# Audit télémétrie — Automaton (D-N051 F8, pas 1)

**Module :** `automaton` — `fiber:a0:automaton` — fork `Amdkn/automaton`
(parent `Conway-Research/automaton`, MIT, branche `main`)
**Gel :** `e025526` (`e0255269f2fd6b3940a8398424fdff3aec940ba0`,
« feat(aspace): integrer doctrine souveraine A0 Amadeus CEO Holon et outils
holoniques », 2026-11-06 03:32:10 -05:00)
**Auditeur :** adaptation pas 1 (D-N051) — vérifié au fichier et à l'exécution
le 2026-11-10. **Verdict : télémétrie zéro par contrat** (aucun SDK
télémétrie, aucun appel sortant par défaut) — avec 3 réserves nommées (§7),
dont une neutralisée par l'adapter.

## §1 — Méthode

1. Scan statique du code (`src/`, `packages/`, `scripts/`) : occurrences de
   `telemetry|analytics|posthog|sentry|segment|mixpanel|amplitude|datadog|
   newrelic|track(|reportUsage|usageStats`, de `fetch(|axios|WebSocket|
   XMLHttpRequest`, et de chaque URL `http(s)://` littérale.
2. Audit des dépendances : `package.json`, `pnpm-lock.yaml`,
   `package-lock.json`, `packages/cli/package.json` — recherche des SDK
   télémétrie/analytics dans les dépendances directes et transitives.
3. Audit des défauts ON/OFF : chaque appel sortant est classé par
   déclencheur (défaut / clé configurée / action explicite de l'utilisateur
   ou de l'agent) avec sa référence de fichier:ligne.
4. Capture réseau : le smoke test de l'adapter est re-couru sous
   `unshare -n` (namespace réseau sans aucune interface) — 21/21 verts,
   ce qui prouve qu'aucun appel sortant n'est nécessaire à l'adapter, et
   le garde-fou `installOutboundGuard()` est testé en direct (§8).

## §2 — SDK télémétrie : zéro

| Recherche | Résultat |
|---|---|
| `posthog\|sentry\|segment\|mixpanel\|amplitude\|datadog\|newrelic` dans `package.json`, `pnpm-lock.yaml`, `package-lock.json`, `packages/cli/package.json` | **0 occurrence** |
| `telemetry\|analytics` dans les dépendances (directes + transitives, via `package-lock.json`) | **0 paquet** |
| Dépendances directes runtime (16) | `better-sqlite3`, `chalk`, `cron-parser`, `gray-matter`, `js-tiktoken`, `openai`, `ora`, `simple-git`, `@solana/web3.js`, `bs58`, `siwe`, `tweetnacl`, `ulid`, `viem`, `yaml` — aucune n'est un SDK télémétrie |
| Dépendances dev (4) | `@types/node`, `tsx`, `typescript`, `vitest` |

Aucun paquet du graphe n'émet de télémétrie d'usage. (`openai` est le SDK
d'inférence, pas de la télémétrie : il n'appelle que l'endpoint configuré,
avec la clé fournie — §4.)

## §3 — Scan statique du code

- Occurrences de `telemetry` hors tests et hors doctrine A'Space : **0**.
  Les seules mentions sont dans les fichiers de doctrine A'Space du gel
  (`constitution.md`, `src/aspace/holon-topology.ts`,
  `src/agent/aspace-holon-tools.ts`, `src/agent/system-prompt.ts`) qui
  **exigent** le zéro-télémétrie (« Zero Telemetry », « zero-telemetry
  enforcement », « aspace-telemetry-shield.cjs ») — ce sont des exigences,
  pas des émissions.
- `src/observability/` (`logger.ts` 117 L, `metrics.ts` 162 L,
  `alerts.ts` 174 L, `pretty-sink.ts` 87 L) : **0 occurrence de `fetch` ou
  `http`** dans les 4 fichiers. Les métriques sont des compteurs/jauges
  en mémoire, les alertes évaluent des instantanés locaux, le logger écrit
  sur stdout/fichier. L'observabilité est strictement locale.
- `track(` dans `src/memory/ingestion.ts:628` : un compteur de répétition
  en commentaire (« Check for existing entry to track repetition count ») —
  pas un envoi.
- Point de choke unique des appels HTTP Conway : **un seul `fetch(`**
  applicatif, `src/conway/http-client.ts:83`, avec timeout, retries et
  disjoncteur. Tous les appels Conway (`client.ts`, `inference.ts`,
  `x402.ts`, `identity/provision.ts`, `social/client.ts`) passent par lui.

## §4 — Chaque appel sortant, tranché

| # | Destination | Déclencheur | Défaut | Fichier | Verdict |
|---|---|---|---|---|---|
| 1 | `https://api.conway.tech` (API + `inference.conway.tech`, `social.conway.tech`) | Clé Conway provisionnée (`CONWAY_API_KEY` / `config.conwayApiKey`) + action (inférence, crédits, provisionnement SIWE, inbox social) | OFF sans clé ; **fallback ON** si clé présente et pas de clé OpenAI (§7 R-1) | `src/conway/client.ts:56,330,545`, `src/conway/http-client.ts:83`, `src/agent/loop.ts:149-169`, `src/config.ts:142` | Fonctionnel, clé-gaté |
| 2 | `https://api.openai.com` (SDK `openai`) | Clé `OPENAI_API_KEY` configurée | OFF sans clé | `src/inference/provider-registry.ts:75,543`, `src/inference/inference-client.ts` | Fonctionnel, clé-gaté |
| 3 | `https://api.anthropic.com` | Clé `ANTHROPIC_API_KEY` configurée | OFF sans clé | `src/conway/inference.ts:305`, `src/agent/loop.ts:143` | Fonctionnel, clé-gaté |
| 4 | `https://api.groq.com`, `https://api.together.xyz` | Clés `GROQ_API_KEY` / `TOGETHER_API_KEY` configurées (registre de providers) | OFF sans clé | `src/inference/provider-registry.ts:120,165` | Fonctionnel, clé-gaté |
| 5 | `https://api.mainnet-beta.solana.com` (défaut, surchargeable par `SOLANA_RPC_URL`) ; `https://mainnet.base.org` | Opérations x402 / top-up USDC, avec clé et wallet provisionnés | OFF sans wallet provisionné | `src/conway/x402.ts:212,261`, `src/setup/configure.ts:306` | Fonctionnel, clé-gaté, payant potentiel |
| 6 | `https://ipfs.io` | Publication/résolution IPFS explicite (réplication) | OFF — action explicite | `src/types.ts:1370,1378` | Fonctionnel, action explicite |
| 7 | `https://github.com` | Spawn de réplique (`git clone`) et `git fetch origin main` | Voir R-2 (§7) | `src/replication/spawn.ts:132,272`, `src/self-mod/upstream.ts` (`checkUpstream`) | Fonctionnel, action explicite / heartbeat |
| 8 | `http://localhost` / `http://127.0.0.1` (Ollama `:11434`, FreeLLMAPI `:31415`, LFM3 `:9931`, santé `:9931`…) | Inférence locale configurée | Loopback uniquement | `src/ollama/discover.ts:46`, `src/index.ts:72`, `src/aspace/holon-topology.ts:151-264`, `src/inference/provider-registry.ts:210` | Local, zéro egress |
| 9 | `https://app.conway.tech` | Wizard de setup (lien affiché, pas un appel automatique) | OFF | `src/setup/wizard.ts:233` | Lien, pas un appel |
| 10 | `https://eips.ethereum.org` | Référence dans un commentaire / doc | — | `src/registry/agent-card.ts:23` | Commentaire, pas un appel |

**Bilan : 0 appel sortant par défaut sans clé ni action.** Le seul appel
sortant par défaut est le `git fetch origin main` du heartbeat (§7 R-2) —
un fetch git vers l'origin, sans payload, pas de la télémétrie.

## §5 — Défauts ON/OFF (heartbeat)

`src/heartbeat/config.ts` (`DEFAULT_HEARTBEAT_CONFIG`), toutes les entrées
`enabled: true` par défaut :

| Tâche | Fréquence | Sortant ? |
|---|---|---|
| `heartbeat_ping` | `*/15 * * * *` | Non (local) |
| `check_credits` | `0 */6 * * *` | Oui, API Conway — seulement avec clé provisionnée |
| `check_usdc_balance` | `*/5 * * * *` | Oui, RPC chaîne — seulement avec wallet provisionné |
| `check_for_updates` | `0 */4 * * *` | **Oui — `git fetch origin main`, sans clé (R-2)** |
| `health_check` | `*/30 * * * *` | Non (local) |
| `check_social_inbox` | `*/2 * * * *` | Oui, API sociale Conway — seulement avec clé |

## §6 — Neutralisation par l'adapter

`aspace-automaton-adapter/` (seul code A'Space du fork) neutralise les
risques ci-dessus sans toucher à l'amont :

1. **`installOutboundGuard()`** enveloppe le `fetch` global : tout hôte
   non-loopback et non explicitement allow-listé lève
   `AspaceOutboundBlockedError` **avant** tout accès réseau ; les hôtes de
   la `TELEMETRY_BLOCKLIST` (16 motifs : posthog, sentry, segment,
   mixpanel, amplitude, datadog, newrelic, google-analytics, etc.) sont
   refusés même s'ils sont allow-listés. Allow-list par défaut : loopback
   uniquement — le fallback Conway par défaut (R-1) est donc **bloqué**
   sauf opt-in explicite `allowHosts: ['api.conway.tech']`.
2. **`ASPACE_HEARTBEAT_OVERRIDES`** : contrat de déploiement —
   `check_for_updates: { enabled: false }`. Le fetch git périodique (R-2)
   est désactivé par configuration ; l'adapter ne peut pas intercepter les
   appels `child_process` git, c'est donc une règle de déploiement, pas un
   intercepteur — portée en réserve R-2.
3. **Surface épinglée** (`PINNED_SURFACE`) : `getRepoInfo()` (lectures git
   locales uniquement) est le seul helper amont enveloppé ;
   `checkUpstream()` est nommé et explicitement NON enveloppé — toute
   utilisation future est un événement de design.

## §7 — Réserves nommées

- **R-1 — Fallback Conway silencieux (neutralisé par l'adapter).**
  `src/agent/loop.ts:155-169` : sans clé OpenAI mais avec une clé Conway,
  le runtime route l'inférence vers Conway Compute en réécrivant
  `OPENAI_BASE_URL`. L'utilisateur qui provisionne une clé Conway sans
  clé OpenAI émet donc vers `api.conway.tech` sans l'avoir demandé
  explicitement. Neutralisé par défaut par le garde-fou de l'adapter
  (allow-list loopback uniquement) ; opt-in explicite requis.
- **R-2 — `check_for_updates` par défaut ON (contrat de déploiement,
  pas d'intercepteur).** `src/heartbeat/tasks.ts:276-306` (tâche amont,
  pré-existante au gel — vérifié : présente dans `d8f8168`) + `git fetch
  origin main` (`src/self-mod/upstream.ts`) toutes les 4 h. Ce n'est pas
  de la télémétrie (aucune donnée envoyée, fetch git vers l'origin
  GitHub), mais c'est le seul appel sortant par défaut du runtime.
  Désactivé par `ASPACE_HEARTBEAT_OVERRIDES` au déploiement. Un déploiement
  qui le laisse ON téléphone à GitHub toutes les 4 h.
- **R-3 — Tâches de crédits/USDC périodiques (clé-gatées).**
  `check_credits` (6 h) et `check_usdc_balance` (5 min) émettent vers
  l'API Conway et le RPC chaîne dès qu'une clé Conway / un wallet est
  provisionné. Fonctionnel, pas de la télémétrie — mais un déploiement
  provisionné émet périodiquement vers l'extérieur.
- **R-4 — Self-mod amont.** Les outils `pull_upstream` /
  `review_upstream_changes` (`src/agent/tools.ts:597`) peuvent fetcher et
  appliquer du code amont sur initiative de l'agent. Jamais de
  fast-forward silencieux : tout commit amont appliqué exige un amendement
  de design (D1).

## §8 — Capture réseau (exécution)

- **Smoke test de l'adapter, 21/21 verts**, re-couru sous `unshare -n`
  (namespace réseau sans aucune interface — aucun egress physiquement
  possible) : **21/21 verts également**. Chaque check du smoke est local
  (lectures git + garde-fou qui lève avant tout accès réseau).
  Commande : `unshare -n npx tsx aspace-automaton-adapter/smoke_test.ts`
  (2026-11-10, VM A'Space).
- **Preuve directe du garde-fou** (dans le smoke, checks 18–19) :
  `fetch('https://api.conway.tech/v1/chat')` sous garde lève
  `AspaceOutboundBlockedError` ; `fetch('http://127.0.0.1:9/nope')` passe
  le garde (échec = refus de connexion OS, pas le garde).
- **Scan des dépendances installé** (`pnpm install --frozen-lockfile`,
  208 paquets résolus) : aucun paquet de télémétrie dans l'arbre installé.
- Le `git fetch origin main` de R-2 n'a pas été exécuté pendant l'audit
  (aucun appel réseau émis par l'auditeur vers l'amont hors `gh api` /
  registre npm pour l'installation des dépendances — trafic d'audit,
  pas du runtime).
