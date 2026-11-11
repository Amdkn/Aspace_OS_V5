# Fiche d'adaptation — space-agent (V2, FKB03)

**Adresse :** `fiber:a0:space-agent` (D7 — émetteur : exécution ; validateur : 13e)
**Manifeste :** `space-agent.manifest.json` (même domicile)
**Licence :** MIT — LICENSE préservé byte-identique dans le fork (voir manifeste + table de gel)
**Audit télémétrie :** `space-agent-TELEMETRY-AUDIT.md` (même domicile)
**Statut :** état 0 Basique → 1 Adapté (fiche + adapter + manifeste, tests verts)

## Commit gelé

- **Fork :** `Amdkn/space-agent` (parent `agent0ai/space-agent`, MIT, branche `main`).
- **Gel : `10f4ffd`** (2026-06-08, HEAD de `main` au Discover).
- **Tout commit amont ultérieur exige un amendement de design**, jamais un fast-forward silencieux (D5).
- **Première revisite du gel nommée (D5) : AUCUNE DÉRIVE.** Amont re-vérifié à
  l'API le 2026-11-09 : HEAD de `main` toujours `10f4ffdaf50a8136cf8450d17c11286178fd58e6`,
  dernier push 2026-06-08T10:37:28Z. Le gel tient ; aucune revisite proposée.

## Adapter

- **Paquet :** `aspace-space-agent-adapter` 0.1.0, commit `4c7bcd2` sur le fork. **Seul code A'Space du fork** (H-M6) — le code amont est byte-identique au gel (diff gel→adapter = 4 fichiers, tous sous `aspace-space-agent-adapter/`).
- **Couture : contrat seule (§1.5).** Space-agent est en JS — hors des trois coutures Cordis. Aucune couture spécifique au JS n'est construite : l'adapter est le contrat du serveur local (`contract.json`) + un smoke test `node:test`.
- **Surface :** `node space --version` → `v0.0+<commits>` (git-dérivé ; le pin de version est package.json 0.36.0) ; `node space serve HOST=127.0.0.1 PORT=0 CUSTOMWARE_PATH=<scratch>` (port éphémère, URL loggée) ; `GET /api/health` (anonyme) → `{ok: true, name: "space-agent-server"}`. Jamais `space update` ni `space supervise`.
- **Smoke tests :** 4/4 verts (`smoke_test.mjs` : pin gel + version, `--version`, commande inconnue → non-zéro, boot serveur 127.0.0.1 + `/api/health`).
- **DOX :** la racine `AGENTS.md` amont est intentionnellement inchangée (H-M2 l'exige) ; l'adapter porte son propre `AGENTS.md` local (étape 6 du closeout DOX).

## Tests au gel et sur le fork adapté

- **Au gel `10f4ffd` :** suite canonique = les `*_test.mjs` sous `tests/` (39 fichiers, `node:test`, pas de script `test` au package.json). **123 pass, 10 fail, 0 skip** (133 tests, run par fichier avec timeout 120 s par fichier — le run global `node --test tests/` est inutilisable : timeout 0, les harnesses navigateur pendent).
  - **Correctifs d'environnement (aucun changement de code ni de test) :** `npm install` racine (deps `archiver`, `electron-updater`, `isomorphic-git`) ; `npm install --prefix packaging` + script d'install Electron manuel (`node node_modules/electron/install.js` — le `--ignore-scripts` initial avait sauté le téléchargement du binaire Electron 35.7.5). Après correctifs : `browser_address_bar` 1/1, `browser_content_format` 5/5.
  - **10 échecs restants, tous qualifiés à la racine, aucun imputable à l'adapter :**
    1. `browser_desktop_harness` (1) : « Timed out waiting for Novinky listing content » — le test navigue vers le site réel Novinky (réseau externe, indisponible dans le sandbox).
    2. `onscreen_agent_prompt_shape`, `prompt_budget_trim`, `prompt_items`, `promptinclude` (4) : `ERR_MODULE_NOT_FOUND` pour les imports absolus `/mod/...` — ces chemins ne se résolvent que dans l'app servie (le serveur mappe `/mod/` vers l'arbre des modules) ; aucun loader, aucun `/mod` à la racine du FS, aucune CI amont (un seul workflow : release-desktop). **Prouvé par diagnostic :** avec un symlink temporaire `/mod → app/L0/_all/mod/`, les 4 fichiers passent (14 tests) ; symlink retiré après. Défaut pré-existant au gel.
    3. `router_cache_headers` (2) : `res.once is not a function` (`responses.js:103`) — le mock `res` du test n'implémente pas `.once` (dérive test/implémentation au gel).
    4. `server_cluster_write_stress` (1) : `EMFILE: too many open files` — limite descripteurs 4096, non relevable ici (`ulimit` → Operation not permitted).
    5. `set_command` (2) : `ENOENT '/workspace/agent-one/commands/params.yaml'` — chemin de checkout de l'auteur codé en dur.
- **Sur le fork adapté (`4c7bcd2`) :** l'adapter ajoute 4 tests verts (smoke test, `node --test aspace-space-agent-adapter/smoke_test.mjs`).
- **Limite franche :** la version git-dérivée (`v0.0+<commits>`) dépend des tags ; le fork créé avec `default_branch_only=true` n'a copié **aucun tag** (amont : 30 tags, latest v0.66) — le pin de version est package.json 0.36.0, pas la chaîne git-dérivée.

## Télémétrie

**Zéro par contrat.** Voir `space-agent-TELEMETRY-AUDIT.md` : aucun SDK télémétrie dans le lock ; `space update` explicite uniquement (jamais invoqué) ; `electron-updater` cantonné au packaging desktop ; preuve réseau : boot en `unshare -n` sans interface (limite honnête : `lo` non relevable sans privilèges, la preuve boucle locale est le smoke test 4/4).

## Dette de divergence

- **Aucune divergence :** le code amont est byte-identique au gel ; seul `aspace-space-agent-adapter` diffère.
- **Propriétaire :** cœur Buzz (lane Clara / 12e).
- **Contrainte nommée (§2) :** JS — hors coutures Cordis (contrat seul, §1.5) ; HEAD de 5 mois (première revisite nommée : aucune dérive).
