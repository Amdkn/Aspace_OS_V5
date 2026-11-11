# Audit télémétrie — space-agent (D-N048, V2, FKB03)

**Module :** `Amdkn/space-agent` (fork de `agent0ai/space-agent`), gel `10f4ffd`, MIT.
**Date :** 2026-11-09. **Auditeur :** Ryan (Factory). **Régime :** R10.

## 1. Scan statique (code JS, hors tests)

- **Aucun SDK télémétrie** : `grep -i posthog|segment|sentry|amplitude|mixpanel|telemetry`
  sur `package.json` et `package-lock.json` → **0 occurrence**. Aucun
  `DO_NOT_TRACK` à honorer : il n'y a rien à désactiver.
- **Canal de mise à jour identifié** : `commands/update.js` — commande CLI
  **explicite** (`space update`) qui résout l'URL distante
  (`commands/lib/update_remote.js` : `GIT_URL` > origine locale > dépôt
  canonique) puis fait un fetch git (git natif, repli isomorphic-git).
  Pour les remotes GitHub, `SPACE_GITHUB_TOKEN` n'est envoyé que s'il est
  posé. **L'adapter n'invoque jamais `space update`.** Rien ne se met à
  jour au démarrage du serveur.
- **electron-updater** : présent uniquement dans `packaging/desktop/main.js`
  (hôte desktop Electron) — jamais importé par le serveur fin
  (`server/`, `app/`, `space.js`, `commands/`). La surface A'Space
  (serveur fin + CLI) ne l'atteint pas.
- **Proxy** (`server/router/proxy.js`) : proxy de requêtes **initiées par
  l'utilisateur** (fetch vers un amont explicite) — pas un appel de fond.
- **Dépendances réseau** (`package.json`) : `archiver` (zip local),
  `electron-updater` (desktop, voir ci-dessus), `isomorphic-git`
  (opérations git locales ; fetch distant uniquement via les commandes
  explicites `update` / `supervise`).

## 2. Dépendances déclarées

Aucun SDK télémétrie (PostHog, Segment, Sentry, analytics) dans
`package.json` ni `package-lock.json`. Le seul canal sortant potentiel
est `space update` (explicite) et le proxy utilisateur — tous deux
hors du chemin de l'adapter.

## 3. Preuve réseau (boot en namespace sans interface)

**Exécutée 2026-11-09, `unshare -n` (aucune interface réseau) :**
- `node space serve HOST=127.0.0.1 PORT=0 CUSTOMWARE_PATH=<scratch>` atteint
  l'état `space server listening at http://127.0.0.1:<port>` sans erreur et
  sans tentative sortante journalisée. Le boot n'a besoin d'aucun réseau.
- **Limite honnête :** le check de santé en boucle locale est impossible
  dans ce namespace (`lo` down, pas de `CAP_NET_ADMIN` pour la lever —
  `ip link set lo up` → Operation not permitted). La preuve boucle locale
  est le smoke test de l'adapter dans le namespace normal (4/4,
  `GET /api/health` → `{ok: true, name: "space-agent-server"}`).
