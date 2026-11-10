# Audit télémétrie — nansen-cli (D-N048 V4)

**Module :** `nansen-cli` — fork `Amdkn/nansen-cli`, gel `0b39ae5d84f986314e01393cda15bfdeea7fec70`
(amont `nansen-ai/nansen-cli`, v2.4.0, MIT, branche `main`).
**Méthode :** lecture du code source au gel (pas de copie), scan mots-clés,
preuves d'exécution (CLI réel sur HOME scratch + `unshare -n`).
**Verdict : télémétrie maison RÉELLE, défaut ON — coupée par contrat par
l'adapter. Zéro SDK tiers. API payante jamais appelée par l'adapter.**

## 1. Télémétrie maison — `src/telemetry.js` (437 lignes)

Un module maison, **sans aucun SDK tiers** (grep `package-lock.json` :
0 occurrence de posthog / sentry / mixpanel / amplitude / segment /
rudderstack — vérifié ; les 4 dépendances runtime sont
`@ethereumjs/rlp`, `@noble/curves`, `@noble/hashes`, `@scure/base`).

- **Endpoint unique :** `POST https://bi-data-sources.nansen.ai/events-service-68ifmnpsx2uq7cgab8dw/v2/event`
  (`TELEMETRY_URL`, `telemetry.js:28`). Timeout 1 s, fire-and-forget,
  erreurs avalées (`sendEvent` ne rejette jamais).
- **Défaut ON (opt-out).** Prédicat unique `isTelemetryDisabled(env)` :
  seul le littéral `'1'` coupe — `DO_NOT_TRACK=1` **ou**
  `NANSEN_NO_TELEMETRY=1`. `'0'` / `'true'` / `'false'` ne coupent pas
  (test amont `doctor.test.js:461` l'assert).
- **Événements émis :**
  - `cli_command_succeeded` / `cli_command_failed` — chemin de commande
    (`/smart-money/netflow`…), latence, noms de flags seuls (jamais les
    valeurs), chaîne, code d'erreur, statut HTTP.
  - `trackAuthCommand` — `login` / `logout` seulement (flags fermés
    `--human --api-key --api-key-stdin --no-browser --json`, codes
    `AUTH_*` fermés).
  - `trade_perps_order/close_succeeded|failed` — une par jambe de réponse
    Hyperliquid : side, outcome, `oid`, `submission_id`, adresse wallet
    **hachée SHA-256 base64** (jamais brute), jamais prix / taille /
    texte d'erreur brut.
- **Identité persistante :** `anonymous_id` (UUID aléatoire) dans
  `~/.nansen/telemetry-id` (0600), `session_id` dans `~/.nansen/session`
  (rotation 30 min d'inactivité). `user_id: null`. **Aucune clé API,
  aucun identifiant de compte, aucun prix, aucune adresse brute** n'est
  envoyé (le `anonymous_id` « laisse BI résoudre un utilisateur Nansen
  quand il est disponible » — commentaire amont).
- **Déclenchement :** wrapper CLI (`src/cli.js:2746-2747`). Les commandes
  dites *offline* ont un tracking no-op par construction :
  `auth`, `doctor --offline`, `mcp` (usage), `completion`, `cache`,
  `feedback forget`, `trade limit-order create|cancel --dry-run`.
  Tests amont : `auth-telemetry.test.js` assert « auth status and doctor
  offline never send telemetry or other network even when telemetry is
  enabled ».

## 2. Autres appels réseau de l'amont (hors télémétrie)

| Appel | Déclencheur | Cible | Payant ? |
|---|---|---|---|
| Update-check | Toute commande non-offline, non-auth-mutation (`cli.js:2752`) — **y compris `--version`** | `GET https://registry.npmjs.org/nansen-cli/latest` (processus détaché, cache 24 h) | Non (registre npm public) |
| Cost-map refresh | `--help` / `help` (`cli.js:2785`) et avant exécution, si cache absent ou vieux de 24 h | `GET https://api.nansen.ai/openapi.json` (spec publique, **sans clé**) | Non (0 crédit, pas d'auth) — mais appel vers l'hôte de l'API payante |
| Client API | Toute commande de données (`research`, `agent`, `web`, `alerts`, `feedback`, `account`…) | `https://api.nansen.ai` (`src/api.js`, `NANSEN_API_KEY` ou session navigateur, x402 pay-per-call) | **Oui — crédits du compte** |
| Trading API | Commandes `trade limit-order` | `https://trading-api.nansen.ai` (`src/limit-order.js`, `X-API-Key` si présente) | **Oui** |
| x402 | Paiements micropaiement (7 fichiers `src/x402*.js`, politique `src/x402-policy.js`, journal `~/.nansen/x402/payments.jsonl`) | API Nansen + chaînes (USDC Base/Solana, USDT0 X Layer) | **Oui — signature de paiement** |
| Feedback | `feedback submit/get` | Backend Nansen avec credentials (`src/commands/feedback.js`) | **Oui (compte)** |
| Postinstall | `npm install -g` **seulement** (retour anticipé en install locale) | `npx skills add nansen-ai/nansen-cli` + `nansen account` (appel API annoncé « 0 crédit ») | Appel API en install globale |
| Hyperliquid / RPC | `perp`, `trade`, `wallet`… (`src/hl-client.js`, `src/trading.js`, `src/swap-simulation.js`…) | Hyperliquid, RPC chaînes | Non-Nansen, hors périmètre adapter |

- **31 sites `fetch(`** dans 16 fichiers de `src/` (hors tests) :
  `api.js`, `auto-paginate.js`, `commands/agent.js`,
  `commands/feedback.js`, `cost-cache.js`, `limit-order.js`, `privy.js`,
  `solana-simulation.js`, `swap-simulation.js`, `telemetry.js`,
  `trade-validation.js`, `trading.js`, `transfer.js`,
  `x402-payment-balance.js`, `x402-svm.js`, `x402.js`.
- **Règles d'accès payantes (AGENTS.md amont) :** 3 rails — crédits du
  compte (clé API ou session navigateur `nansen login`), x402
  (micropaiement signé, plafond 1 $ par paiement par défaut,
  `NANSEN_X402_MAX_AMOUNT`, plafond de session
  `NANSEN_X402_SESSION_MAX_AMOUNT`), MPP via tempo (CLI séparé,
  `nansen-cli` ne signe pas de credentials MPP).

## 3. Où vivent les appels API payants (pour prouver que l'adapter ne les touche jamais)

- **Point d'entrée unique des données :** `src/api.js` — classe client
  Nansen (`baseUrl` défaut `https://api.nansen.ai`,
  `src/auth-credentials.js:7`), clé lue via `NANSEN_API_KEY` ou session
  sauvegardée ; `webFetch` (`api.js:1720`) ; retry x402 (`_x402Retry`,
  `api.js:1013`).
- **Coûts en crédits :** `src/cost-cache.js` lit les coûts par endpoint
  depuis la spec OpenAPI (`x-credit-cost`) ; le commit de tête du gel
  est littéralement « update agent prices to 100 (fast) and 400 (expert)
  credits » — les appels d'agent coûtent **100 à 400 crédits**.
- **Authentification :** `src/auth-*.js` (7 fichiers) — clé API,
  session navigateur (OAuth `nansen:api`), keychain OS ; stockage
  `~/.nansen/` (0700 / 0600).
- **L'adapter n'importe aucun de ces modules** : il n'exécute que
  `node src/index.js` avec la surface offline et les 4 gardes ; il ne
  construit ni `NansenApi`, ni client trading, ni wallet.

## 4. Preuves d'exécution (CLI réel, HOME scratch)

1. `--version` **sans gardes** : crée uniquement
   `.nansen/last-version.json` (comptabilité de la notice de mise à
   jour) — pas de `telemetry-id`, pas de `session`. Le spawn
   update-check détaché est prouvé au code (`cli.js:2752` +
   `update-check.js: scheduleUpdateCheck`, coupé par
   `NO_UPDATE_NOTIFIER` / `CI`) ; le fichier `update-check.json`
   n'était pas encore présent à +8 s (proxy lent, fetch 5 s timeout —
   non concluant sur l'issue du fetch, concluant sur le chemin de code).
2. `--version` **avec gardes** (`NANSEN_NO_TELEMETRY=1 DO_NOT_TRACK=1
   NO_UPDATE_NOTIFIER=1 CI=1`, HOME scratch) : `2.4.0`, rc 0, **zéro
   fichier créé** sous le HOME scratch.
3. `doctor --offline` **avec gardes** : rc 0, « offline diagnostics »,
   « Telemetry disabled », « no update-check cache yet », « Credit cost
   map not cached yet (refreshes on next nansen help) » — confirme que
   `--help` déclencherait le refresh du cost-map.
4. `auth status` **avec gardes** : JSON, `logged_in: false`,
   `offline: true`, `api_key.present: false`, rc 0.
5. **Preuve réseau** (smoke test, `unshare -n`) : `--version` et
   `doctor --offline` réussissent sans interface réseau — 2/2.
6. **Suite amont elle-même :** `vitest.config.js` force
   `NANSEN_NO_TELEMETRY=1` pour les tests ; la doc amont dit « Unit
   tests mock all RPC/API calls — never hit real networks ». Réserve :
   les tests qui invoquent le CLI sans `NO_UPDATE_NOTIFIER` déclenchent
   le spawn update-check détaché (observé dans les processus enfants
   pendant la suite : `node -e` vers `registry.npmjs.org`) — registre
   npm uniquement, jamais l'API Nansen.

## 5. Ce que l'adapter coupe, par construction

- **Télémétrie :** gardes `NANSEN_NO_TELEMETRY=1` + `DO_NOT_TRACK=1`
  (double interrupteur du même prédicat) **et** surface limitée aux
  commandes offline (tracking no-op au wrapper).
- **Update-check :** `NO_UPDATE_NOTIFIER=1` + `CI=1` (coupe le spawn
  détaché, y compris sur `--version`).
- **Cost-map :** `--help` exclu de la surface (seule voie de
  `refreshCostMapIfStale` sur le chemin d'aide).
- **API payante / x402 / trading :** surface interdite par contrat
  (`contract.json`, section `forbidden_surface`) ; aucune clé dans
  l'environnement enfant (assert du smoke test) ; HOME scratch (aucun
  credential à lire).
- **Postinstall :** l'install des dépendances a été faite en local
  (`pnpm install --ignore-scripts`) — le postinstall ne s'exécute
  qu'en install globale et n'est jamais invoqué par l'adapter.

## 6. Réserves

1. **Télémétrie défaut ON** : sans les gardes, toute commande
   non-offline émet un événement vers `bi-data-sources.nansen.ai`
   (fire-and-forget, 1 s). L'adapter ne protège que sa propre surface ;
   un usage du CLI hors adapter sans les gardes télémètre.
2. **`--help` = réseau potentiel** : sur HOME vierge ou cache vieux de
   24 h, `--help` GET la spec OpenAPI sur `api.nansen.ai` (sans clé,
   0 crédit). L'adapter l'exclut ; la documentation utilisateur du
   fork doit en tenir compte.
3. **Update-check détaché** : sans `NO_UPDATE_NOTIFIER`/`CI`, chaque
   invocation non-offline spawn un enfant qui GET le registre npm.
   L'enfant survit au processus parent (detached + unref) — observé
   pendant la suite amont.
4. **Arbitrage S0 en attente** : identifiants/crédits Nansen non
   tranchés — toute extension de la surface au-delà de l'offline
   exige cet arbitrage.
