# Fiche d'adaptation — mattpocock-skills (D-N048 V5, FKB08)

**Statut :** état 0 Basique → 1 Adapté en cours (fiche + adapter + manifeste, smoke 12/12, suite statique : 39/39 frontmatter, 5/5 bash -n, 27/27 plugin, 1 écart de documentation nommé — voir § Tests)
**Fork :** https://github.com/Amdkn/mattpocock-skills (gel `4ae2317ddb22b046e26455e4f9c9b3aaaf62212d`, branche `main`, parent `mattpocock/skills`)
**Dossier :** `aspace-mattpocock-skills-adapter/` (contract.json + smoke_test.sh + README.md), commit `d6ebe3b` sur le fork. **Seul code A'Space du fork** — le code amont est byte-identique au gel (diff gel→adapter = 3 fichiers, vérifié à l'API, H-M2).

## Commit gelé

- **Amont :** `mattpocock/skills`, branche `main`, gel **`4ae2317`** (complet `4ae2317ddb22b046e26455e4f9c9b3aaaf62212d`, 2026-10-31).
- **Fork :** https://github.com/Amdkn/mattpocock-skills (HEAD `4ae2317` = gel dès la création, H-M1 tient ; aucune dérive amont constatée entre le gel du design et la création du fork).
- **Version :** 1.3.2. Taille ~2,2 Mo. Clone complet.

## Licence : MIT

`LICENSE` amont préservé byte-identique dans le fork (« MIT License, Copyright (c) 2026 Matt Pocock », vérifié au fichier). API GitHub : `license.spdx_id = MIT`.

## Renommage D2 (contrainte nommée du design)

Le fork est **`Amdkn/mattpocock-skills`**, pas `Amdkn/skills` : `Amdkn/skills`
est le fork d'`anthropics/skills`, **intouché** (collision de nom, §D2).
L'API de fork a d'abord créé `Amdkn/skills-1` (nom suffixé automatiquement),
renommé ensuite en `Amdkn/mattpocock-skills` par PATCH (nom vérifié à l'API,
parent `mattpocock/skills`, HEAD = gel). **Le chemin du sous-module est
inchangé** : `01_Forkable/FKB08_Plugins/mattpocock-skills`.

## Le module

Catalogue de skills d'agent pour l'ingénierie réelle (Matt Pocock) : **39
skills** en 5 seaux (engineering 20, productivity 7, misc 4, in-progress 8,
deprecated 0, un README seul). Chaque skill = un `SKILL.md` (frontmatter
`name` + `description`, invocation utilisateur ou modèle) + un
`agents/openai.yaml` (interface). Le plugin Claude Code
(`.claude-plugin/plugin.json`, version 1.3.2) embarque exactement le jeu
promu : **27 skills** (engineering + productivity). Les 8 skills
`in-progress` sont publiques par conception mais hors plugin. `ask-matt` est
le routeur qui cartographie les skills atteignables par l'utilisateur.
Règles maison du repo (AGENTS.md = CLAUDE.md) : aucun tiret cadratin dans la
prose ; chaque README de seau liste chaque skill du seau ; les skills
promues ont une page de documentation (`docs/<seau>/<skill>.md`).

## Surface de l'adapter (couture contrat seule, §1.5)

L'adapter **décrit** le module, il ne l'exécute pas. Surface :

- `contract.json` — inventaire contractuel : 39 skills (nom, seau, chemin,
  description), 5 scripts shell, versions 1.3.2, posture télémétrie. Généré
  depuis le disque (pas de transcription manuelle) : 39 descriptions
  non vides.
- `smoke_test.sh` — validation structurelle hors-ligne : fichiers de base,
  JSON valide, inventaire 39 = disque, frontmatter `name` + `description`
  sur 39/39, `bash -n` sur les 5 scripts, versions 1.3.2 cohérentes, aucun
  appel réseau dans l'adapter, HEAD du clone = gel.
- `README.md` — documentation de l'adapter, couture contrat seule,
  divergence.

Les 5 scripts shell du module sont des outils locaux ou des modèles à copier,
jamais exécutés par l'adapter : `scripts/link-skills.sh` (liens symboliques
vers `~/.claude/skills` et `~/.agents/skills`, dev-only), `scripts/list-skills.sh`
(liste les `SKILL.md`), `hitl-loop.template.sh` (boucle interactive,
stdin/stdout), `wizard/template.sh` (modèle d'assistant à réécrire),
`block-dangerous-git.sh` (garde-fou git, lit du JSON sur stdin). Aucun appel
réseau de l'adapter, aucun secret.

## § Tests

**Aucune suite de tests amont.** Pas de script `test` dans `package.json`,
aucun fichier de test, aucun job de test en CI (`.github/workflows` =
needs-info, release, triage-label ; `release.yml` ne fait que `npm ci`).
Le périmètre H-M3 est donc la **validation statique** des skills, consignée
dans `logs-mattpocock-skills-suite.log` :

- `bash -n` : **5/5 OK**.
- Frontmatter `name` + `description` (nom == dossier) : **39/39 OK**.
- `plugin.json` 27 == jeu promu 27 : 0 en trop, 0 manquant, 0 doublon
  (comparaison corrigée en route : la première version comparait des chemins
  `./skills/<seau>/<nom>` à des noms — normalisée sur le basename, re-courue
  verte).
- README racine : 27/27 promues référencées. README de seau : engineering,
  productivity, misc OK.
- `sync-plugin-version --check` : OK (1.3.2 en sync).
- Docs des skills promues (`docs/<seau>/<skill>.md`) : 27/27 présentes.
- **1 écart nommé (documentation amont, pré-existant au gel)** :
  `skills/in-progress/chief-of-staff/` existe (SKILL.md + agents/) mais n'est
  pas listé dans `skills/in-progress/README.md` (0 occurrence ; les 7 autres
  skills in-progress y sont). Cause racine : le skill et le README ont été
  touchés dans le même commit de gel `4ae2317` sans mise à jour du README —
  la règle maison (chaque README de seau liste chaque skill du seau) n'est
  pas tenue pour ce skill. Écart de documentation amont, pas un défaut de
  code, pas un blocage : l'adapter inventorie le disque, pas le README.

**Smoke test : 12/12 PASS** (`logs-mattpocock-skills-smoke.log`), re-couru
sous `unshare -n` (aucune interface réseau) : 12/12 PASS.

## Télémétrie (audit complet : `mattpocock-skills-TELEMETRY-AUDIT.md`)

**Télémétrie zéro par construction.** Aucun SDK tiers, aucun appel sortant
dans le code exécutable du module. Les URL dans les `SKILL.md` sont des
références de documentation, jamais des appels. Le seul `open_url` du code
(`wizard/template.sh`, exemple d'étape Stripe) est une ouverture de
navigateur déclenchée par l'utilisateur dans un modèle à réécrire, pas une
télémétrie. Preuve réseau : smoke 12/12 sous `unshare -n`.

## Réserves nommées

1. Aucune suite de tests amont : la validation est statique (voir § Tests).
   Une suite exécutable n'existe pas dans ce module — rien à re-courir en CI
   au-delà du périmètre statique.
2. Écart de documentation amont : `chief-of-staff` absent du README
   in-progress (pré-existant au gel, voir § Tests).
3. `shellcheck` absent de la VM : la validation shell est `bash -n`
   (syntaxe), pas une analyse statique approfondie.
4. Les 8 skills `in-progress` sont des bêtas publiques : leur contenu peut
   changer sans le cycle de version du plugin (hors plugin par conception).

## Dette de divergence

- **Dérive amont :** aucune constatée entre le gel du design (`4ae2317`,
  2026-10-31) et la création du fork. L'amont a bougé depuis ? Non vérifié
  après la création du fork — la revisite est par signal de dérive
  (inventaire hebdomadaire, §D5 du design), jamais un fast-forward
  silencieux. Le gel reste `4ae2317`.
- **Dette portée par le cœur Buzz** (lane Clara / 12e) : la fusion F8 (D-N051)
  n'a pas encore touché ce module (FKB08, pas une brique F8) ; la fiche et
  le manifeste vivent au domicile FKB08 en attendant.
- **Renommage D2** (voir ci-dessus) : le fork porte le nom
  `mattpocock-skills` ; toute référence à `Amdkn/skills` pour ce module est
  une erreur (c'est le fork d'`anthropics/skills`).
