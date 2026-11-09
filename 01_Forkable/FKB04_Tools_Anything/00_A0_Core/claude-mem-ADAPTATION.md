# Fiche d'adaptation — claude-mem (V1, FKB04)

**Adresse :** `fiber:a0:claude-mem` (D7 — émetteur : exécution ; validateur : 13e)
**Manifeste :** `claude-mem.manifest.json` (même domicile)
**Audit télémétrie :** `claude-mem-TELEMETRY-AUDIT.md` (même domicile)
**Statut :** état 0 Basique → 1 Adapté (fiche + adapter + manifeste, tests verts)

## Commit gelé

- **Fork :** `Amdkn/claude-mem` (parent `TheDotMack/claude-mem`, Apache-2.0, branche `main`).
- **Gel : `a926f57`** (2026-11-09, HEAD de `main` au Discover).
- **Tout commit amont ultérieur exige un amendement de design**, jamais un fast-forward silencieux (D5).
- **Touche à la mémoire F3** : l'adapter ne fait que lire le store SQLite ; l'observer du module reste le seul écrivain (règles `AGENTS.md` du module : pas de file, pas de rejeu d'inférence).

## Adapter

- **Paquet :** `packages/aspace-claude-mem-adapter` (`@aspace/claude-mem-adapter` 0.1.0), commit `3fdbd73` sur le fork. **Seul code A'Space du fork** (H-M6) — le code amont est byte-identique au gel (diff gel→adapter = 5 fichiers, tous sous `packages/aspace-claude-mem-adapter/`).
- **Couture : patron Cordis.** `createAspaceMem({dbPath})` → `{ search, listByProject, close, dbPath }` — recherche plein-texte (FTS5 + sous-chaînes) et listage par projet sur `MemoryItemsRepository`, **en lecture seule** (aucune méthode d'écriture exposée, aucune inférence déclenchée).
- **Smoke tests :** 5/5 verts (`tests/smoke.spec.ts`, `bun test`) : surface épinglée, télémétrie forcée à zéro, search (hit / miss / requête vide), listByProject (2 mémoires), base en mémoire éphémère. Typecheck `tsc --noEmit` propre.
- **Preuve réseau :** smoke test 5/5 en namespace sans interface (`unshare -n`).

## Tests au gel et sur le fork adapté

- **Au gel `a926f57` :** voie rapide `bun scripts/test-lanes.ts fast` (commande `test` du `package.json`). **Premier run brut : 13 484 pass, 33 fail, 4 erreurs** (lot 1 : 7 700 tests, 25 fail ; lot 2 : 5 914 tests, 8 fail + 4 erreurs). **Tous les échecs qualifiés à la racine, aucun imputable à l'adapter :**
  - **21 échecs launcher / bundles (lot 1)** : le bundle checké `plugin/scripts/claude-mem-launcher.cjs` imprime le protocole `2` alors que la source dit `3` (`src/launcher/launcher-protocol.ts:19`). **Prouvé : bundles périmés au gel** — un rebuild complet (`node scripts/build-hooks.js`, procédure CI amont) les régénère et le bundle imprime `3` ; après rebuild, `tests/launcher/claude-mem-launcher.test.ts` 33/33 et `tests/launcher/install-launcher.test.ts` 0 fail. **Aucune modification du fork** : les bundles rebuildés sont restaurés (`git checkout`) après vérification — H-M2 tient (seul l'adapter diffère du gel). Le rebuild est une étape de procédure, pas un changement de code.
  - **1 échec `plugin-distribution` (#3424, npm tarball)** : `npm pack --dry-run --json` seul prend **5,378 s** (rc=0, JSON valide) — juste au-dessus du timeout de test bun (5 s). Environnemental (disque VM lent). Vérifié par re-run avec `--timeout 15000`.
  - **1 échec `memory PreToolUse` (codex)** : `claude-mem: plugin scripts not found` — le script shell du hook codex exige `plugin/node_modules`, absent après un install racine seul (`plugin/package.json` existe, deps propres). **Corrigé par l'environnement** : `bun install` dans `plugin/` → test 14/14.
  - **1 échec `processesStillUsingArm` (pgrep/emoji)** : **cause prouvée** — le répertoire de test contient un emoji 🧠 ; bisection : tous les morceaux échappés matchent sauf l'emoji seul ; pgrep (procps-ng 4.0.4) ne décode pas le multibyte UTF-8 sous `LC_CTYPE=POSIX` (locale VM). **Corrigé par l'environnement** : `LC_ALL=C.UTF-8` → test 32/32.
  - **4 échecs langue/presse-papiers + 4 erreurs de build (lot 2, UI `my-work`)** : esbuild `Could not resolve "lucide-react" / "cn" / "motion/react"` — le workspace `src/ui/my-work` a son propre `package.json`, jamais installé par l'install racine. **Corrigé par l'environnement** : `bun install` dans `src/ui/my-work/` → `hosted-setup` 19/19.
  - **2 échecs OpenCode worker endpoint (`file-host`, `env-over-file`)** : **prouvé environnemental, non réparable ici** — le worker se connecte à `http://0.0.0.0:<port>` (le test vérifie la précédence env-sur-fichier) ; le sandbox intercepte `0.0.0.0` (réponse vide du middlebox, `ECONNRESET`), alors que `127.0.0.1` répond 200 (vérifié avec serveurs Python et Bun). Le scénario `default` (127.0.0.1) passe. **Réserve nommée, portée au jugement du 13e.**
  - **Re-run complet avec la procédure corrigée** (build + installs racine/plugin/my-work + `LC_ALL=C.UTF-8` + `--timeout 15000`, log `logs-claude-mem-suite-fast2.log`, 711 s) : **13 571 pass, 97 skip, 2 fail, 0 erreur** (lot 1 : 7 656 pass / 0 fail, 7 723 tests ; lot 2 : 5 915 pass / 2 fail / 30 skip, 5 947 tests ; total 13 670 tests, 1 202 fichiers). **Les 2 seuls échecs sont les OpenCode nommés en réserve.**
- **Sur le fork adapté (`3fdbd73`) :** l'adapter ajoute 5 tests verts (smoke test) + typecheck propre.
- **Limite franche :** `bun install` a été nécessaire (289 modules, `node_modules` absent du clone partiel) ; dépendances résolues par Bun via le proxy.

## Télémétrie

**Zéro par contrat.** Voir `claude-mem-TELEMETRY-AUDIT.md` : SDK `posthog-node` (devDependency), hôte `https://us.i.posthog.com`, **défaut ON** (opt-out) — l'adapter force `DO_NOT_TRACK=1` (+ `CLAUDE_MEM_TELEMETRY=0`), couche 1 de la précédence de consentement ; l'adapter n'importe rien de `src/services/telemetry/` ; preuve réseau en namespace sans interface (5/5).

## Dette de divergence

- **Aucune divergence :** le code amont est byte-identique au gel ; seul `packages/aspace-claude-mem-adapter` diffère.
- **Propriétaire :** cœur Buzz (lane Clara / 12e).
- **Contrainte nommée (§2) :** touche à la mémoire F3 (couture mémoire TS, établie tôt par V1).
