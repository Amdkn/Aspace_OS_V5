# openai-plugins — TELEMETRY-AUDIT (H-M4, D12)

**Module :** `openai-plugins` (`openai/plugins` → `Amdkn/openai-plugins`).
**Gel :** `d420d13051bffe4543ed39e30fa46b87148e47dd`.
**Licence :** sans licence (aucun fichier LICENSE, API `license: null`).
**Méthode :** scan statique + dépendances + preuve réseau de l'adapter
(`unshare -n`). Le catalogue n'est pas un service en cours d'exécution :
aucun serveur, aucun daemon, aucun point d'entrée réseau à la racine.
**Verdict : télémétrie ZÉRO par construction pour l'adapter ; aucun SDK de
télémétrie dans l'amont.**

## §1. Périmètre

- Dépôt au gel : 62 plugins sous `plugins/<name>/`, 5 406 fichiers (clone
  partiel `--filter=blob:none --depth 1`), 94 Mo.
- 64 fichiers `plugin.json`, 31 `.mcp.json`, 36 `.app.json`, 1 `hooks.json`.
- 14 fichiers `package.json`, **aucun `node_modules`** dans le dépôt.
- Aucun workflow CI (`.github/workflows` absent), aucune suite racine.
- L'adapter : 4 fichiers sous `aspace-openai-plugins-adapter/`, stdlib
  Python seule.

## §2. Scan statique (SDK de télémétrie)

Recherche insensible à la casse sur tout le dépôt (hors `.git`) :
`posthog | sentry | segment.com | amplitude | mixpanel | google-analytics |
googletagmanager | hotjar | fullstory | intercom`.

- **0 SDK de télémétrie** dans le code et dans les dépendances.
- Les 71 occurrences du mot-clé large sont des **faux positifs** :
  - noms de plugins dans les marketplaces (`.agents/plugins/marketplace.json`
    et `api_marketplace.json` : `posthog`, `mixpanel-headless` — des
    intégrations que l'UTILISATEUR active avec ses propres identifiants,
    pas de la télémétrie du dépôt) ;
  - documentation de la skill `telemetry` de `build-macos-apps` (aide
    l'utilisateur à ajouter la télémétrie Apple `Logger` à SA propre app
    macOS — pas de la télémétrie du dépôt) ;
  - documentation d'observabilité Cloudflare (`cloudflare/skills/...`) ;
  - `remixPanel` dans `creative-production/.../app.js` (code DOM, le mot
    « remix » contient « mix », faux positif du motif `mixpanel`).
- Le mot `telemetry` seul apparaît dans : la skill macOS ci-dessus, des
  docs Cloudflare, et le bundle minifié `creative-production/mcp/
  server.bundle.mjs` (code de bibliothèque vendue/minifiée — aucun point de
  terminaison de télémétrie identifié dans le bundle).

## §3. Dépendances (14 `package.json`)

Aucune dépendance d'analytique dans les 14 fichiers. Contenu :

- `data-analytics` : `@lexical/*`, `lexical`, `@modelcontextprotocol/
  ext-apps`, `html-to-image`, `lucide-react`, `react`, `react-dom`,
  `recharts` (+ dev : `typescript`, `vite`, `playwright-core`, `pngjs`,
  `pixelmatch`, `concurrently`, `cross-env`).
- `plugin-eval` : **0 dépendance** (stdlib Node seule).
- `expo/.../scripts` : `ajv`, `ajv-formats`, `js-yaml`.
- `product-design` (+ templates) : `react`, `vite`, `@radix-ui/*`,
  `motion`, `@playwright/test` (dev).
- `shopify/*` (5 skills) : `typescript`, `@shopify/*`, `preact`,
  `graphql`, `type-fest`, `schema-dts`.
- `vercel/.../frontend` : `react`, `react-dom`, `vite` (dev).

**Aucun** `posthog-js`, `@sentry/*`, `@segment/*`, `amplitude-js`,
`mixpanel-browser`, `react-ga`, `@hotjar/*` — nulle part.

## §4. Appels réseau (code exécutable)

- **31 `.mcp.json`** : ~25 serveurs MCP distants en HTTP (points de
  terminaison des fournisseurs : `mcp.figma.com`, `mcp.notion.com`,
  `mcp.linear.app`, `mcp.slack.com`, `api.githubcopilot.com`,
  `gmailmcp.googleapis.com`, `calendarmcp.googleapis.com`,
  `drivemcp.googleapis.com`, `mcp.stripe.com`, `mcp.supabase.com`,
  `mcp.vercel.com`, `mcp.posthog.com`, `mcp.sentry.dev`,
  `mcp.datadoghq.com`, etc. — OAuth, `oauth_resource` déclaré) et 6
  locaux (`npx`, `node`, script de lancement). Ce sont les **fonctions**
  des plugins : ils parlent à l'API du fournisseur **quand l'utilisateur
  installe le plugin et s'authentifie**. Aucun n'est invoqué par défaut,
  aucun n'est invoqué par l'adapter.
- **42 fichiers exécutables** (`.mjs`/`.js`/`.cjs`/`.py`) contiennent
  `fetch(`/`axios`/`https.request` : appels aux API des fournisseurs
  (domaines des plugins) et URL de documentation/exemples. Premiers hôtes
  cités : `github.com` (51), `shopify.dev` (27), `example.com` (17),
  `cdn.shopify.com` (12), `ebi.ac.uk` / `rest.ensembl.org` (recherche
  sciences de la vie). Aucun hôte d'analytique.
- **Aucun envoi périodique, aucun heartbeat, aucun identifiant anonyme
  persistant** dans le code du dépôt (le catalogue ne tourne pas tout seul).

## §5. Preuve réseau (capture)

- **Adapter : preuve acquise.** Suite de fumée 8/8 re-courue sous
  `unshare -n` (namespace sans interface réseau) : identique (8/8 OK).
  L'adapter n'importe aucun module réseau (`socket`, `urllib`, `http`,
  `requests`, `httpx`, `aiohttp` — vérifié par test statique dans la suite
  elle-même). Télémétrie zéro par construction, pas par configuration.
- **Amont : pas de capture d'exécution** — il n'y a rien à capturer : le
  dépôt est un catalogue (manifestes + Markdown + serveurs MCP à la
  demande). Aucun processus du dépôt ne tourne par défaut. La preuve est
  donc statique + dépendances (§2–§4), et c'est la preuve correcte pour ce
  périmètre. Les serveurs MCP ne démarrent que sur installation explicite
  d'un plugin par l'utilisateur, avec ses identifiants.

## §6. Verdict

| Canal | Statut | Détail |
|---|---|---|
| SDK télémétrie (amont) | **ZÉRO** | 0 occurrence, 0 dépendance (§2–§3) |
| Envoi analytique (amont) | **ZÉRO** | aucun envoi périodique, aucun heartbeat (§4) |
| API fournisseurs (amont) | FONCTIONNEL, sous identifiants | 25 MCP distants OAuth + appels API des plugins ; jamais sans installation + authentification utilisateur (§4) |
| Adapter | **ZÉRO par construction** | stdlib seule, 0 appel réseau, preuve `unshare -n` (§5) |

**L'adapter neutralise tout par construction** : il ne démarre aucun
serveur MCP, ne lit aucun identifiant, ne fait aucun appel réseau. Il n'y
a rien à couper par contrat — il n'y a pas de canal à couper.

## §7. Déclencheurs tranchés

1. `posthog` / `mixpanel-headless` dans les marketplaces → **noms de
   plugins** (intégrations utilisateur, identifiants propres) — pas de la
   télémétrie du dépôt. Tranché : hors périmètre, jamais invoqué.
2. Skill `telemetry` de `build-macos-apps` → **aide l'utilisateur à
   ajouter Apple Logger à sa propre app** — pas de la télémétrie du dépôt.
   Tranché : documentation, pas du code exécuté.
3. Docs d'observabilité Cloudflare → **documentation de référence** pour
   l'utilisateur Cloudflare — pas du code du dépôt. Tranché : hors
   périmètre.
4. `server.bundle.mjs` (creative-production) → bundle minifié, le mot
   « telemetry » apparaît dans du code de bibliothèque vendue — **aucun
   point de terminaison de télémétrie identifié**. Tranché : pas d'envoi.
5. 25 MCP distants HTTP → **fonction des plugins, OAuth, sous
   identifiants utilisateur** — pas de la télémétrie. Tranché : jamais
   invoqués par l'adapter.

## §8. Reproduction

```bash
# SDK (attendu : 0 vrai positif)
grep -rniE "posthog|sentry\.io|@sentry|amplitude\.com|mixpanel|google-analytics" --exclude-dir=.git .
# Dépendances (attendu : aucun SDK analytique)
for f in $(find . -name "package.json" -not -path "./.git/*"); do python3 -c "import json;print('$f', list(json.load(open('$f')).get('dependencies',{})))"; done
# Preuve réseau adapter (attendu : 8/8 OK, identique sans réseau)
unshare -n python3 aspace-openai-plugins-adapter/smoke_test.py
# Zéro copie (attendu : 0 occurrence sur 7 775 blobs du gel)
gh api "repos/Amdkn/openai-plugins/git/trees/d420d13051bffe4543ed39e30fa46b87148e47dd?recursive=1" --jq '.tree[].sha' > /tmp/gel-blobs.txt
for b in 5b7188cf21c8defc056c94fbb56bc8b3b2d70b52 5243a9db2b6f26b9d9f3ffede6b772dcde694ddd d9d9607f2dee4dd553f803e7730a931c7bc89214 0b5775cb304ea4c6ba3a0c936007f38fa887f7b2; do grep -c "^$b$" /tmp/gel-blobs.txt; done
```
