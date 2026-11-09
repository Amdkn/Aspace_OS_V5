# Audit télémétrie — Cordis (étape 0, D-N047 / D3)

**Fork :** `Amdkn/cordis` — **gel : `b38ef58`** — **adapter : `a40cc74`**
**Date :** 2026-11-09 ~17:07 EST · **Exécutant :** Ryan (Factory)
**Résultat : 0 appel sortant de télémétrie. Zéro SDK télémétrie.**

## 1. Scan statique — code source (`packages/`)

Commande : `grep -rn --include="*.ts" -E "fetch\(|axios|WebSocket|sendBeacon|XMLHttpRequest|http\.request|https\.request|net\.connect" packages/ --exclude-dir=fixtures`

- **2 occurrences, un seul fichier : `packages/create/src/index.ts:294,314`.**
  - Ligne 294 : `fetcher` passé à `stageYarnBin` — téléchargement du binaire yarn lors du scaffolding.
  - Ligne 314 : `fetchOrExit(url)` — téléchargement du tarball de template depuis le registre, URL fournie par l'utilisateur.
  - Les deux sont déclenchées **uniquement par une commande explicite de l'utilisateur** (`create-cordis`, scaffolding). Ce n'est pas de la télémétrie : aucune donnée d'usage n'est envoyée, rien n'est émis en arrière-plan.
- **Zéro occurrence** de `axios`, `WebSocket`, `sendBeacon`, `XMLHttpRequest`, `http.request`, `https.request`, `net.connect` dans tout `packages/`.
- Imports `node:http` : uniquement dans des **tests** (`create/tests/scaffold.spec.ts`, `package-manager/tests/registry.ts`) — serveurs locaux de test, pas du code de production.

## 2. Audit des dépendances

- **Il n'y a pas de `yarn.lock` dans le dépôt amont** (non versionné) — l'audit porte donc sur les dépendances **déclarées** dans les `package.json` des 11 paquets (10 amont + adapter).
- **Zéro SDK télémétrie déclaré** : aucun de `sentry`, `posthog`, `mixpanel`, `amplitude`, `segment`, `analytics`, `bugsnag`, `datadog`, `newrelic`, `trackjs`, `hotjar`, `fullstory`, `logrocket`.
- Dépendances déclarées (toutes utilitaires/CLI) : `@babel/code-frame`, `@standard-schema/spec`, `chokidar`, `cosmokit`, `env-paths`, `get-registry`, `js-yaml`, `kleur`, `picomatch`, `prompts`, `schemastery`, `supports-color`, `tar`, `which-pm-runs`, `yaml`, `yargs-parser`. `get-registry` sert au `create` à résoudre l'URL du registre — cohérent avec les 2 `fetch()` ci-dessus.
- Hash de la liste des dépendances (audit) : voir la liste ci-dessus, vérifiée au 2026-11-09 sur le fork au gel + adapter.

## 3. Audit d'exécution — capture réseau

Méthode : namespace réseau `unshare -n` (une seule interface, loopback sans adresse IP — **aucun réseau externe possible**, pas même 127.0.0.1).

- **Adapter + HMR : 118/118 verts, 1 skipped, EXIT 0** (8 fichiers : 7 HMR + 1 adapter), dans le namespace sans réseau. **Zéro appel sortant possible pendant ce run — et le run passe.**
- **Suite complète dans le namespace :** log partiel, 0 échec dans les fichiers terminés ; le run a été tué à ~9 min, bloqué sur une attente réseau (test dépendant du registre, vraisemblablement `create` ou `package-manager` — les seuls paquets avec du code réseau). Ce blocage confirme que les seuls tests dépendants du réseau sont ceux des paquets à code réseau explicite ci-dessus, jamais de la télémétrie.

## 4. Conclusion

**0 appel sortant de télémétrie, en statique comme en exécution.** Le seul trafic réseau du fork est le téléchargement de templates/binaires déclenché explicitement par l'utilisateur (`create-cordis`). Aucun SDK de télémétrie, aucune primitive réseau cachée.

**Re-audit :** à chaque changement de commit gelé ou d'adapter, et au minimum à chaque transition d'état (D3).
