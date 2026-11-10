# Audit télémétrie — mattpocock-skills (D-N048 V5, gel 4ae2317)

Module : catalogue de skills d'agent (Matt Pocock), 39 skills, 5 scripts
shell, version 1.3.2, MIT. Gel `4ae2317ddb22b046e26455e4f9c9b3aaaf62212d`
(2026-10-31). Méthode : scan statique (`grep -rniE` sur l'arbre complet hors
`.git`, `package-lock.json` exclu des comptages d'URL), lecture des 5 scripts
shell en entier, preuve réseau par smoke test sous `unshare -n`.

## §1 — Verdict

**Télémétrie zéro par construction.** Aucun SDK tiers de télémétrie, aucun
appel sortant dans le code exécutable du module, aucun mécanisme de collecte.
Les seuls éléments ressemblant à du réseau sont des références de
documentation dans la prose et un `open_url` d'exemple dans un modèle à
réécrire (voir §3 et §4). L'adapter ne fait aucun appel réseau et n'exécute
aucun script amont.

## §2 — Scan statique : aucun SDK tiers

Recherche : `posthog|sentry|mixpanel|amplitude|segment|telemetry|analytics|
track\(|axios|fetch\(` sur `*.sh`, `*.mjs`, `*.js`, `*.yaml`, `*.yml`,
`*.json` (hors `.git`, hors `package-lock.json`) : **0 occurrence**.

Dépendances (`package.json`) : uniquement des devDependencies
`@changesets/changelog-github` et `@changesets/cli` (gestion des versions et
du changelog, exécutées à la main au moment d'une release, jamais au
runtime). `package-lock.json` ne contient aucune dépendance de télémétrie.
Aucun `postinstall`, aucun hook d'installation.

## §3 — Les 5 scripts shell : appels sortants potentiels, un par un

| Script | Appels sortants | Verdict |
|---|---|---|
| `scripts/link-skills.sh` (62 lignes, dev-only) | Aucun. `ln -s` vers `~/.claude/skills` et `~/.agents/skills`, `git pull` manuel hors script | Local seul. Non invoqué par l'adapter |
| `scripts/list-skills.sh` (7 lignes) | Aucun. `find` + `sed` | Local seul |
| `skills/engineering/diagnosing-bugs/scripts/hitl-loop.template.sh` (44 lignes, modèle) | Aucun. `read`/`printf` sur stdin/stdout | Local seul, interactif |
| `skills/engineering/wizard/template.sh` (modèle à réécrire) | **1 `open_url`** (ligne 210) : `https://dashboard.stripe.com/test/apikeys` | Voir §3.1 |
| `skills/misc/git-guardrails-claude-code/scripts/block-dangerous-git.sh` (25 lignes, hook) | Aucun. Lit du JSON sur stdin, `jq` + `grep` | Local seul |

### §3.1 — `open_url` dans `wizard/template.sh`

Le `open_url "https://dashboard.stripe.com/test/apikeys"` est dans la
section **exemple** du modèle (« Replace the example below », étape
« Stripe: API keys ») : c'est une ouverture de navigateur déclenchée par
l'utilisateur qui suit l'assistant, pour copier ses propres clés Stripe de
test. Ce n'est pas une télémétrie (aucune donnée envoyée, aucune collecte),
pas un appel automatique (le modèle ne s'exécute que si un auteur de skill
le copie et le lance), et l'adapter ne l'invoque jamais. Tranché : hors
périmètre télémétrie, documenté ici pour traçabilité.

## §4 — URL dans la prose : références de documentation, jamais des appels

Les `SKILL.md` contiennent des URL (`https://…`) : toutes sont des liens de
documentation cités dans la prose (docs d'outils, références d'API, pages
d'aide : aihero.dev, gitlab.com, notion.com, vercel.com, etc.). Aucune
n'est invoquée par du code. Vérifié : aucune occurrence de `curl` ou `wget`
dans tout l'arbre (hors `.git`).

## §5 — `$schema` de `.changeset/config.json` : référence, pas un envoi

`.changeset/config.json` porte `"$schema":
"https://unpkg.com/@changesets/config@3.1.4/schema.json"`. C'est une
référence de schéma JSON, lue uniquement si un outil valide le fichier
(éditeur, CLI changesets) — le module ne la récupère pas lui-même et ne
l'envoie nulle part. Tranché : pas un appel sortant du module.

## §6 — Dépendances : dev-only, aucune télémétrie

`package.json` : `private: true`, deux devDependencies changesets
(versioning + changelog GitHub). Aucune dépendance de runtime, aucun SDK,
aucun appel au build ni à l'installation (`npm ci` en CI release uniquement,
voir `release.yml`).

## §7 — Preuve réseau

Smoke test de l'adapter (`smoke_test.sh`, 12 checks) re-couru sous
`unshare -n` (namespace sans interface réseau) : **12/12 PASS**. L'adapter
ne fait aucun appel réseau par construction (validation structurelle :
lecture de fichiers, `bash -n`, `python3 -c` sur du JSON local). Les 5
scripts amont ne sont jamais exécutés par l'adapter (seule leur syntaxe
est vérifiée par `bash -n`).

## §8 — Déclencheurs tranchés + conclusion

| Déclencheur potentiel | Tranché |
|---|---|
| `open_url` Stripe (template wizard) | Exemple à réécrire, ouverture navigateur par l'utilisateur, pas de télémétrie |
| `$schema` unpkg (changeset config) | Référence de schéma, pas un envoi du module |
| URL de documentation dans les `SKILL.md` | Prose, jamais invoquées par du code |
| `link-skills.sh` (symlinks + `git pull` manuel) | Outil dev-only, jamais invoqué par l'adapter |
| Envoi de données d'usage, identifiant, session | **Aucun mécanisme de ce type dans le module** |

**Conclusion : télémétrie zéro.** Aucun SDK, aucun appel sortant, aucun
mécanisme de collecte. Le module est un catalogue de textes (skills) et de
modèles shell : il ne peut pas télémétrer sans qu'un harness l'exécute, et
l'adapter ne l'exécute pas. L'audit tient sans réserve sur le périmètre
vérifié (arbre complet au gel, scripts lus en entier, preuve réseau
`unshare -n`).
