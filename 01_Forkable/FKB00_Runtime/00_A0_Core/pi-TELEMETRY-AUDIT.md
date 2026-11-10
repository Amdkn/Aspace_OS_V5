# Audit télémétrie — pi (D-N051 F8, pas 2)

**Module :** `Amdkn/pi` ← `earendil-works/pi` — gel `6e2222a` (1.5.0).
**Périmètre :** paquet `packages/durable` + interface de l'extension
(D6). Le reste du monorepo est audité ici à titre de réserve (R-1, R-3)
mais n'est pas dans le périmètre de l'adapter.
**Verdict : télémétrie zéro par contrat dans le périmètre.**
Méthode : scan statique au fichier (grep sur les sources, les
`package.json`, les réglages) + smoke sous `unshare -n` (zéro egress
physiquement possible). Aucune déclaration sans preuve de fichier.

## §1 — SDK de télémétrie

- **Zéro SDK dans tous les `package.json` du monorepo** : `posthog`,
  `sentry`, `segment`, `mixpanel`, `amplitude`, `datadog`, `newrelic`,
  `opentelemetry`, `@opentelemetry/*` — **0 occurrence** (scan
  `packages/*/package.json` + `package.json` racine).
- Aucune dépendance d'analytics dans `package-lock.json` pour les
  paquets du périmètre (`durable`, `telemetry`).

## §2 — Appels réseau sortants dans le périmètre

- **`packages/durable/src/` : 0 `fetch(`.**
- **`packages/telemetry/src/` : 0 `fetch(`.**
- Seul littéral `http(s)://` dans `packages/durable/src/` :
  `https://git-scm.com` — un lien de documentation, pas un appel.
- Le paquet `durable` n'émet **aucun** appel réseau : il ne fait que
  persister (SQLite / JSONL / mémoire) et ordonnancer.

## §3 — Contexte de télémétrie et défaut NOOP

- `TelemetryContext` : **71 fichiers** le référencent dans le repo
  (311 références, hors `node_modules` / `dist` / `.git`) — le chiffre
  du Discover (71 fichiers) est confirmé ; 31 fichiers mentionnent
  `NOOP_TELEMETRY_CONTEXT`.
- **Défaut NOOP vérifié au fichier** (le contrat D5) :
  - `packages/durable/src/harness/harness.ts:220` —
    `telemetry: NOOP_TELEMETRY_CONTEXT` par défaut.
  - `packages/durable/src/scheduler/scheduler.ts:410` — même défaut.
  - `packages/durable/src/submissions/submissions.ts:50` — même défaut.
- `DURABLE_TELEMETRY_SCHEMA` (`packages/durable/src/harness/telemetry.ts`)
  est **content-free** (aucune donnée de contenu n'y transite).
- 3 fichiers seulement de `packages/durable/src/` référencent
  `TelemetryContext` (harness, scheduler, submissions) — tous avec le
  défaut NOOP.
- **Zéro mention d'« exporter »** dans `packages/telemetry/src/` et
  `packages/durable/src/` — aucun exporteur branché, nulle part.

## §4 — Réglages (`settings.json`) et extension

- Aucun exporteur branché dans `settings.json` (fichier de réglages
  pi — vérifié : aucune clé de télémétrie / d'exporteur).
- Aucun exporteur branché dans `.pi/extensions/aspace-factory.ts`
  (l'extension n'appelle que `pwsh` en local et enregistre l'outil
  `subagents`).
- **Callbacks de l'adapter NOOP** : `ASPACE_TELEMETRY_CONTRACT =
  { context: "NOOP_TELEMETRY_CONTEXT", exporters: [] }` —
  vérifié par le smoke (45/45).

## §5 — Garde-fou de l'adapter (preuve d'exécution)

- `installOutboundGuard()` enveloppe le `fetch` global et refuse
  **avant tout accès réseau** tout hôte non loopback et non
  allow-listé.
- `TELEMETRY_BLOCKLIST` : 16 motifs (telemetry, analytics, posthog,
  sentry, segment, mixpanel, amplitude, datadog, newrelic, heap,
  fullstory, hotjar, pi.dev, openrouter.ai, api.openai.com,
  events.) — refusés même s'ils sont allow-listés.
- Smoke 45/45, dont 45/45 sous `unshare -n` (zéro interface) :
  `fetch` vers un hôte bloqué lève **avant** le réseau ; `fetch`
  vers un hôte inconnu lève **avant** le réseau ; seul le loopback
  passe le garde (et échoue ensuite au niveau OS, pas au garde).

## §6 — Réserves (hors périmètre, nommées)

- **R-1 — Télémétrie d'installation défaut ON (`coding-agent`,
  hors périmètre D6).** `packages/coding-agent/src/core/settings-defaults.ts:32`
  : `enableInstallTelemetry: true`. `reportInstallTelemetry`
  (`modes/interactive/interactive-mode.ts:1467-1484`) émet
  `GET https://pi.dev/api/report-install?version=<version>` (version
  + User-Agent, timeout 5 s, fire-and-forget, erreurs avalées) à
  chaque démarrage interactif, sauf si `PI_OFFLINE` est défini ou
  `PI_TELEMETRY` est falsy ou le réglage est désactivé.
  **Neutralisation :** le garde-fou de l'adapter refuse `pi.dev`
  (non loopback, non allow-listé) ; règle de déploiement :
  `PI_OFFLINE=1` ou `PI_TELEMETRY=0`. À porter en natif au pas 3
  (RigInfinity) comme réglage par défaut.
- **R-2 — Upload de rapport de bug (action explicite).**
  `packages/coding-agent/src/core/bug-report-upload.ts:20` : POST
  multipart vers `/v1/bug-reports` (gateway Radius), anonyme ou
  attribué. Déclenché uniquement par une action explicite de
  l'utilisateur — pas un envoi par défaut.
- **R-3 — Appels d'inférence (`packages/ai/src/`, 22 `fetch(`).**
  Destinations : openrouter.ai, ai-gateway.vercel.sh,
  bedrock-runtime.us-east-1.amazonaws.com, opencode.ai,
  router.huggingface.co, gateway.ai.cloudflare.com, api.openai.com,
  radius.pi.dev, api.mistral.ai, token-plan.*.aliyuncs.com,
  api.individual.githubcopilot.com, + flux OAuth (anthropic,
  github-copilot, kimi-coding, meta — échanges de jetons).
  Ce sont des **appels de modèle fonctionnels, clé-gatés** — pas de
  la télémétrie. Aucun ne part sans clé provisionnée.
- **R-4 — Autres `fetch(` du monorepo (hors périmètre).**
  `coding-agent` 8 (llama local, session-share, package-manager,
  wrapper management-http) ; `chord` 11 (dont le handler serveur
  `fetch(Request) → Response` — côté serveur, pas un appel sortant) ;
  `agent` 1 (proxy streaming, configuré par l'utilisateur) ;
  `mcp` 6 (OAuth discovery, transport streamable HTTP). Aucun
  n'est un exporteur de télémétrie.

## §7 — Ce qui n'a pas été vérifié ici

- Le comportement réseau réel du binaire `pi` en mode interactif
  sur le PC (H-P2-3/6/11, Phase D) — le garde-fou et le réglage
  `PI_OFFLINE` sont vérifiés au fichier, pas par capture réseau
  sur la machine.
- La suite complète du monorepo (seule la suite `durable` a tourné
  ici ; voir fiche § Tests).

## §8 — Conclusion

**Télémétrie zéro par contrat dans le périmètre `durable` +
extension.** Aucun SDK, aucun `fetch`, aucun exporteur, défaut NOOP
vérifié au fichier en 3 points, garde-fou exécuté (smoke 45/45 sous
`unshare -n`). Les deux réserves hors périmètre (R-1 install ping
défaut ON, R-3 appels d'inférence clé-gatés) sont nommées avec leur
neutralisation. Ré-audit à chaque changement de commit gelé ou
d'adapter, et au minimum à chaque transition d'état.
