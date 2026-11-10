# Fiche d'adaptation — nansen-cli (D-N048 V4)

**Adresse :** `fiber:a0:nansen-cli`
**Manifeste :** `nansen-cli.manifest.json` (même domicile)
**Audit télémétrie :** `nansen-cli-TELEMETRY-AUDIT.md` (même domicile)
**Statut :** état 2 Vérifié (fiche + adapter + manifeste, smoke 8/8, suite amont 5 943 passés / 7 échecs qualifiés environnementaux / 10 ignorés — voir § Tests)
**Licence :** MIT (Copyright (c) 2026 Nansen — `LICENSE` vérifié au fichier)

## Commit gelé

- **Fork :** `Amdkn/nansen-cli` (parent `nansen-ai/nansen-cli`, MIT, branche `main`).
- **Gel : `0b39ae5d84f986314e01393cda15bfdeea7fec70`** — v2.4.0, commit « docs: update agent prices to 100 (fast) and 400 (expert) credits (API-1238) (#819) ».
- **Correction de création nommée :** le fork a d'abord été créé sur le HEAD courant de l'amont (`97746e2`, après le gel — dérive constatée le 2026-11-10) ; la référence `main` a été ramenée au gel par mise à jour forcée de la ref (SHA complet, corps JSON — `gh api -f force=true` rejeté 422).
- **Gitlink V5 :** à avancer au gel dans la PR V4 (chemin inchangé).
- **Tout commit amont ultérieur exige un amendement de design**, jamais un fast-forward silencieux (D5).

## Adapter

- **Dossier :** `aspace-nansen-cli-adapter/` (contract.json + smoke_test.mjs + README.md), commit `70c93779be43b92d8e96f70e229b1c5fa80016bb` sur le fork. **Seul code A'Space du fork** — le code amont est byte-identique au gel (diff gel→adapter = 3 fichiers, vérifié à l'API : `ahead_by: 1, behind_by: 0`).
- **Surface (contrat seul, §1.5) :** commandes offline uniquement — `nansen --version`, `nansen doctor --offline`, `nansen auth status`, `nansen completion <bash|zsh|fish>`. Sous gardes `NANSEN_NO_TELEMETRY=1 DO_NOT_TRACK=1 NO_UPDATE_NOTIFIER=1 CI=1`, HOME scratch, `NANSEN_API_KEY` jamais présente.
- **Jamais :** toute commande de données (`research`, `smart-money`, `agent`, `web`, `alerts`, `feedback submit/get`, `account`), toute commande de trading (`trade`, `perp`, `wallet`, `bridge`, `limit-order`, `send`), `login` / `logout`, `nansen --help` (déclenche `refreshCostMapIfStale` : GET `https://api.nansen.ai/openapi.json` si le cache coûts est absent ou vieux de 24 h — exclu volontairement du smoke test).
- **Couture JS (§1.5) :** contrat seul — manifeste JSON + HTTP local, aucune intégration profonde.
- **Smoke test :** `node aspace-nansen-cli-adapter/smoke_test.mjs` (stdlib seule) — **8/8 VERT** : version exacte, doctor offline, auth status JSON (`logged_in: false`, `offline: true`, aucune clé), completion bash, preuve réseau `unshare -n` (`--version` et `doctor --offline` réussissent sans interface réseau), zéro fichier de télémétrie/session/cache sous le HOME scratch, absence de `NANSEN_API_KEY`.

## Contrainte API payante — sans identifiant, sans crédit

- **Faits :** l'API Nansen (`https://api.nansen.ai`, client `src/api.js`, clé `NANSEN_API_KEY` ou session navigateur) facture les appels en **crédits du compte** — les appels d'agent coûtent **100 (fast) à 400 (expert) crédits** (commit de tête du gel). Rails : crédits du compte, x402 (micropaiement signé, plafond 1 $ par défaut), MPP via tempo (CLI séparé, non signé par `nansen-cli`). Trading API séparée : `https://trading-api.nansen.ai`.
- **Adapter :** ne construit ni `NansenApi`, ni client trading, ni wallet ; n'exige ni n'invoque aucune clé ; n'appelle jamais un endpoint payant ; ne dépense aucun crédit. La surface autorisée ne touche que des commandes offline par contrat amont (`isOfflineCommand`, `cli.js:2739-2747`).
- **Arbitrage S0 en attente :** les identifiants et crédits Nansen sont un arbitrage vision S0, **non tranché par la chaîne**. Tant qu'il n'est pas tranché, l'adapter reste sur la surface offline. Toute extension de la surface au-delà de l'offline exige cet arbitrage.

## Tests au gel et sur le fork adapté

- **Au gel `0b39ae5` : suite amont `vitest run` (commande CI : `npm test` ; config `vitest.config.js` — 132 fichiers `src/**/*.test.js`, e2e exclus, `NANSEN_NO_TELEMETRY=1` forcé pour les tests, timeout 30 s). Node v24.22.1 (engines ≥ 22).**
- **Install des dépendances :** `npm install` **impossible sur cette VM** — l'extracteur npm échoue en `EPERM chown` (le sandbox bloque le `chown` sur les uids des tarballs ; `--user 0 --group 0` ne corrige pas). Contournement : **pnpm 10.33.0** (cache corepack) — `pnpm install --ignore-scripts` OK en 67 s. Dépendances résolues par pnpm (pas de `pnpm-lock.yaml` au gel ; `pnpm-lock.yaml` généré localement, **non committé**, supprimé du clone) — pas par `package-lock.json`. `postinstall.js` non exécuté (`--ignore-scripts` ; il ne s'exécute qu'en install globale de toute façon).
- **Bilan FINAL (run 3, umask 0022) : Test Files 3 failed | 126 passed (129) ; Tests 7 failed | 5 943 passed | 10 skipped (5 960).** Durée 753,45 s (début 17:00:24 UTC, log `logs-nansen-cli-suite.log`). **Périmètre : suite complète par défaut** (`vitest run`) — 129 fichiers (132 trouvés moins les 3 e2e exclus par la config, jamais courus : ils frappent le vrai réseau et exigent des wallets financés). La doc amont : « Unit tests mock all RPC/API calls — never hit real networks ». Réserve : les tests qui invoquent le CLI sans `NO_UPDATE_NOTIFIER` déclenchent le spawn update-check détaché vers le registre npm (observé pendant la suite) — registre uniquement, jamais l'API Nansen.
- **Run 2 (umask 0007, log `logs-nansen-cli-suite-run2.log`) : 91 échecs — CAUSE PROCÉDURALE PROUVÉE, pas le gel.** Les tests écrivent leurs fichiers d'identifiants en mode par défaut (`fs.writeFileSync` sans mode, ex. `auth-login.test.js:30,61,77,87`) ; sous umask 0007 ils sortent en 0660 ; la garde amont `safePath` (`auth-state.js:19-24`) et `checkStat` (`local-file.js:9-12`, `privateFile: true`) rejettent tout chemin inscriptible par le groupe (`stat.mode & 0o022`) avec `AUTH_STATE_INVALID` (« Saved authentication cannot be read safely ») — cascade sur auth-login (37), auth-final-repair (22), postinstall (9), auth-process (7), auth-refresh (2), auth-state (1), x402-audit (2), trading (2), cli (1). **Run 3 (umask 0022) : ces 91 échecs tombent à 0** — la cause est établie par la différence entre les deux runs, pas par affirmation.
- **Les 7 échecs restants (run 3), tous qualifiés à la racine, aucun défaut de code établi — l'adapter ne touche pas `src/` :**
  - `doctor.test.js` ×5 — **root (uid=0)** : les tests rendent un fichier/répertoire illisible (`chmod 000`) et attendent `'unreadable'` / `'error'` ; en root le fichier reste lisible (`expected null to be 'unreadable'`, `expected 'ok' to be 'error'`, `expected true to be false`, + 2 `Cannot read properties of undefined` en aval du même chemin). **Prouvé directement** : `cat` d'un fichier `chmod 000` réussit sous uid=0, ainsi que `ls` d'un répertoire `chmod 000`. Même famille que les 2 rouges Cordis (D-N047) et les 2 rouges t3code (V3b).
  - `execute-guard.test.js` ×1 — **timeout 30 s sous charge** (« treats NANSEN_YES=1 like --yes on a terminal ») : le même test **passait au run 2** et a expiré au run 3 (phase tests 1 977 s, VM partagée chargée) — flaky de contention, pas un défaut.
  - `package.test.js` ×1 — **réseau bloqué par la garde du test lui-même** : `npm install` du tarball `npm pack` échoue en `FETCH_ERROR … reason: Test blocked outbound connection` (registry.npmjs.org/@ethereumjs/rlp) — **échec identique aux runs 2 et 3**, déterministe, indépendant de l'umask ; le test exige l'accès au registre, que la garde du test bloque. Pas un défaut produit, pas lié à l'adapter (aucune touche au packaging).

## Télémétrie (résumé — détail dans l'audit)

- **Réelle, défaut ON :** module maison `src/telemetry.js` (437 lignes), endpoint `https://bi-data-sources.nansen.ai/.../v2/event`, événements `cli_command_succeeded/failed`, `trackAuthCommand` (login/logout), `trade_perps_*` (adresse wallet hachée SHA-256). Opt-out : `DO_NOT_TRACK=1` ou `NANSEN_NO_TELEMETRY=1` (seul le littéral `'1'` coupe). `anonymous_id` persistant + `session_id` 30 min sous `~/.nansen/`.
- **Zéro SDK tiers** (`package-lock.json` : 0 occurrence posthog/sentry/mixpanel/amplitude/segment).
- **Coupée par contrat :** gardes + surface offline seule (tracking no-op au wrapper CLI pour les commandes offline). Preuve : `unshare -n` 2/2 + zéro fichier de télémétrie sous le HOME scratch du smoke test.

## Dette de divergence

- **Dérive amont constatée :** amont `main` = `97746e2` au moment du fork (post-gel) ; le gel `0b39ae5` reste épinglé. Toute revisite = candidat de fusion (D5), jamais de fast-forward silencieux.
- **Dépendances :** résolues par pnpm ici, par npm en CI amont (`npm ci` dans `.github/workflows/ci.yml`). Le `package-lock.json` du gel reste la référence ; aucun changement de dépendance n'a été committé.
- **Propriétaire :** cœur Buzz (lane Clara / 12e).

## Réserves

1. **Télémétrie défaut ON** : hors adapter, toute commande non-offline sans gardes émet un événement vers `bi-data-sources.nansen.ai`.
2. **`--help` = réseau potentiel** (refresh du cost-map sur `api.nansen.ai`, sans clé, 0 crédit) — exclu de la surface.
3. **Update-check détaché** : sans `NO_UPDATE_NOTIFIER`/`CI`, chaque invocation non-offline spawn un enfant vers le registre npm (survit au parent).
4. **Arbitrage S0 en attente** (identifiants/crédits) — voir § Contrainte API payante.
5. **Suite amont : 5 943 passés / 7 échecs qualifiés environnementaux (5 root, 1 timeout flaky, 1 garde réseau du test) / 10 ignorés** — voir § Tests. À re-vérifier en CI (qui utilise `npm ci`, umask standard, non-root).
6. **Install npm impossible sur cette VM** (chown bloqué) — pnpm utilisé ; à re-vérifier en CI (qui utilise `npm ci`).
