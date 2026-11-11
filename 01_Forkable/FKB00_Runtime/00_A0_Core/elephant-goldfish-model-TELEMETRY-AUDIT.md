# Audit télémétrie — elephant-goldfish-model (D-N053 pas C, H-M4)

**Module :** `elephant-goldfish-model` — fork `Amdkn/elephant-goldfish-model`, gel `113a3afc`, adapter `4f4a076`.
**Verdict : TÉLÉMÉTRIE ZÉRO par contrat.** Aucun SDK de télémétrie, aucun appel réseau en arrière-plan, aucun appel à l'import. Les seuls appels réseau du repo sont des scripts CI / de packaging explicites et des tests offline contre des API simulées, jamais déclenchés par l'adapter.

## 1. Scan statique du code amont (au gel)

Motifs cherchés dans tout le repo (hors `.git`) : `posthog|sentry|amplitude|mixpanel` → **0 hit** dans le code Python/JS (`*.py`, `*.js`, `*.mjs`).
Motif `telemetry` (mot seul) : **1 hit** — `skills/egm-brainstorm/SKILL.md:98`, une cellule de table (« Observability & SRE Debuggability | Telemetry & operational visibility | … ») : critère de design pour l'utilisateur, pas du code, pas un appel.
Motifs réseau cherchés : `requests.|httpx.|urllib|urlopen|socket.|http.client|aiohttp` → hits limités aux tests et aux scripts explicites ci-dessous, **0 à l'import** de l'adapter (stdlib seule, vérifié : 0 hit dans `aspace_elephant_goldfish_model_adapter/__init__.py`).

### Sites réseau explicites (tous déclenchés par l'utilisateur / la CI, jamais en arrière-plan)

- `tests/unit/test_scope_advisory.py` et voisins — workflow JS offline contre une **fausse API GitHub** (fake, locale, per TESTING.md) ; aucune donnée sortante.
- `tests/integration/test_claude.py`, `test_codex.py` — intégrations opt-in, **exclues** de la borne D-C2 (CLI authentifiés + quota) ; jamais exécutées ici.
- Job site CI (`site/`) — builds Astro, **hors borne** ; jamais exécuté ici.
- Scripts de packaging / release — appels API GitHub explicites, déclenchés par les workflows, jamais à l'import d'une skill.

## 2. Dépendances

`pyproject.toml` `[dependency-groups] test` : `pytest==8.3.5`, `pyyaml==6.0.2` — aucune dépendance réseau applicative, aucun SDK de télémétrie déclaré. L'adapter est **stdlib seule** (0 import réseau, vérifié : 0 hit).

## 3. Preuve d'exécution — namespace sans interface

`unshare -n` (aucune interface réseau, DNS en échec) : `validate()` + `doctor()` réussissent (inventaire cohérent, 7 skills, 8/8 contrôles ok). Log : `logs-netns-validate.log`. **0 appel sortant possible dans ce namespace — la preuve est structurelle, pas déclarative.**

## 4. Poids dans le fork

Aucun poids : le repo est des skills Markdown + scripts Python/JS + ressources documentaires. Aucun fichier `.safetensors` / `.bin` / `.pt` / `.pth` dans le repo (vérifié au fichier).

## 5. Déclencheurs tranchés

| Déclencheur | Décision |
|---|---|
| Tests offline contre fausse API GitHub | Locaux, simulés, 0 donnée sortante — **conservés tels quels** |
| Intégrations opt-in Claude/Codex | Exclues de la borne D-C2, jamais exécutées ici — **conservées telles quelles** (comportement amont) |
| Job site CI (Astro) | Hors borne, jamais exécuté ici — **conservé tel quel** |
| SDK de télémétrie | Aucun — **rien à retirer** |
| Appel réseau à l'import | Aucun (prouvé en netns) — **rien à retirer** |
| Poids montés dans le fork | Aucun — **conforme** |

## 6. Ré-audit

À chaque changement de commit gelé ou d'adapter, et au minimum à chaque transition d'état.
