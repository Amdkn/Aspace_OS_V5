# Audit télémétrie — superpowers (D-N053 pas C, H-M4)

**Module :** `superpowers` — fork `Amdkn/superpowers`, gel `22f0b463`, adapter `5813de0`.
**Verdict : TÉLÉMÉTRIE ZÉRO par contrat.** Aucun SDK de télémétrie, aucun appel réseau en arrière-plan, aucun appel à l'import. Le seul appel réseau du repo est une image de marque distante, chargée par le navigateur de l'utilisateur et omise par opt-out explicite, jamais déclenchée par l'adapter.

## 1. Scan statique du code amont (au gel)

Motifs cherchés dans tout le repo (hors `.git`, hors `node_modules`) : `posthog|sentry|amplitude|mixpanel` → **0 hit** dans le code (`*.js`, `*.cjs`, `*.json`, `*.md` — les 2 hits `segment` sont le mot anglais « segment » dans un chemin et dans RELEASE-NOTES.md, pas un SDK).
Motifs réseau cherchés : `requests.|httpx.|urllib|urlopen|socket.|http.client|aiohttp` → **0 hit** (repo Node, pas de Python applicatif).
URLs distantes cherchées dans `index.js` + `skills/brainstorming/scripts/server.cjs` : **1 seule** — voir §2.

### Sites réseau explicites (tous déclenchés par l'utilisateur, jamais en arrière-plan)

- `skills/brainstorming/scripts/server.cjs:106` — `https://primeradiant.com/brand/superpowers-visual-brainstorming-logo.png` (logo de marque des écrans brainstorm du serveur local). Chargée par le navigateur de l'utilisateur quand il ouvre la page ; **omise** si `SUPERPOWERS_DISABLE_TELEMETRY=true` / `DISABLE_TELEMETRY=true` / `CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC=1`, ou sur bind non-loopback (server.cjs:527). Testée par la suite amont (`branding.test.js`, 7/7 : les 3 variables d'opt-out vérifiées).
- `skills/brainstorming/scripts/server.cjs:251` — lien `https://github.com/obra/superpowers` (ancre HTML, pas un appel serveur).
- Le serveur lui-même est loopback par défaut (`http://127.0.0.1:PORT/?key=…`, server.cjs:287) ; aucune donnée sortante (les événements WebSocket sont relayés vers stdout local, pas vers un tiers).

## 2. Dépendances

`tests/brainstorm-server/package.json` : seule dépendance `ws ^8.21.0` (WebSocket, pour les tests) ; `package.json` racine : **aucun script, aucune dépendance**. Aucun SDK de télémétrie déclaré (grep `posthog|sentry|amplitude|mixpanel|telemetry` dans `package.json` / `package-lock.json` : 0 hit hors le nom de la variable d'opt-out). L'adapter est **stdlib seule** (0 import réseau dans `aspace_superpowers_adapter/__init__.py`, vérifié : 0 hit).

## 3. Preuve d'exécution — namespace sans interface

`unshare -n` (aucune interface réseau, DNS en échec) : `validate()` + `doctor()` réussissent (inventaire cohérent, 15 skills, 8/8 contrôles ok). Log : `logs-netns-validate.log`. **0 appel sortant possible dans ce namespace — la preuve est structurelle, pas déclarative.**

## 4. Poids dans le fork

Aucun poids : le repo est des skills Markdown + scripts JS. Aucun fichier `.safetensors` / `.bin` / `.pt` / `.pth` dans le repo (vérifié au fichier).

## 5. Déclencheurs tranchés

| Déclencheur | Décision |
|---|---|
| Image de marque primeradiant.com (logo écrans brainstorm) | Explicite, navigateur de l'utilisateur, opt-out documenté et testé (3 variables) — **conservée telle quelle** (comportement amont, pas une télémétrie ; jamais déclenchée par l'adapter) |
| Lien github.com/obra/superpowers (ancre HTML) | Pas un appel serveur — **conservé tel quel** |
| SDK de télémétrie | Aucun — **rien à retirer** |
| Appel réseau à l'import | Aucun (prouvé en netns) — **rien à retirer** |
| Poids montés dans le fork | Aucun — **conforme** |

## 6. Ré-audit

À chaque changement de commit gelé ou d'adapter, et au minimum à chaque transition d'état.
