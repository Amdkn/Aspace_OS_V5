# openai-plugins — ADAPTATION (D12, clean-room)

**Statut :** état 0 Basique → 1 Adapté en cours (fiche + adapter + manifeste, smoke 8/8, suite amont qualifiée — voir § Tests)

**Module :** `openai-plugins` — catalogue de 62 plugins Codex (manifestes
`.codex-plugin/plugin.json`, skills Markdown, serveurs MCP distants).
**Amont :** `openai/plugins` (branche `main`).
**Fork :** `Amdkn/openai-plugins`.
**Commit gelé :** `d420d13051bffe4543ed39e30fa46b87148e47dd` (« Add AWS Core to
curated marketplace (#410) », 2026-11-06).
**Licence : SANS LICENCE** — aucun fichier LICENSE dans le dépôt, API GitHub
`license: null` (vérifié). Conséquence D12 : le fork est une référence
seule, l'adaptation est clean-room.
**Adapter :** `aspace-openai-plugins-adapter/` (4 fichiers), commit
**`060f2685f906be8778d7ead6d2cef6e9d8f82b32`** (main du fork, parent = gel).
**Propriétaire :** cœur Buzz (lane Clara / 12e).
**Domicile :** `01_Forkable/FKB08_Plugins/00_A0_Core/`.

## §1. Régime D12 (variante H-M2..H-M6)

Le design D-N048 D12 s'applique : fork = référence seule, adaptation =
clean-room, **aucune copie de fichier amont**. La variante remplace
H-M2..H-M6 (le gabarit standard suppose une licence libre et une adaptation
par greffe — ici ni l'une ni l'autre n'existe).

**Preuve zéro copie (vérifiée par l'exécutant, à re-vérifier par le 13e) :**
les 4 blobs de l'adapter — README.md `5b7188cf`, contract.json `5243a9db`,
mock_plugin.py `d9d9607f`, smoke_test.py `0b5775cb` — ont **0 occurrence
parmi les 7 775 blobs de l'arbre du gel** (comparaison par hash de blob,
arbre récursif lu à l'API). Le compare gel→HEAD du fork = ahead 1, behind 0,
exactement les 4 fichiers de l'adapter.

**Repli suppression nommé (D12) :** si la validation clean-room échoue, le
repli est la **suppression du fork** `Amdkn/openai-plugins` — aucune
publication d'une copie.

**Adresse :** le manifeste porte `"id": null` — aucune adresse tant qu'aucune
adaptation clean-room n'est validée. L'adresse `fiber:a0:openai-plugins`
n'est attribuée que par le jugement du 13e (même motif que claude-code en
V3b).

## §2. Adapter (écrit de zéro)

`aspace-openai-plugins-adapter/` — 4 fichiers, écrits de zéro depuis la
spécification publique du format de manifeste (un plugin vit sous
`plugins/<name>/` avec un manifeste `.codex-plugin/plugin.json` requis,
cf. README amont) :

- `contract.json` — contrat (surface, gel, régime D12).
- `mock_plugin.py` — générateur de manifeste minimal + validateur de
  structure (stdlib seule ; aucune importation réseau : ni `socket`, ni
  `urllib`, ni `http`, ni `requests`).
- `smoke_test.py` — 8 tests de fumée (contrat, manifeste, validation
  OK/KO, environnement, absence d'import réseau, absence de contenu amont).
- `README.md` — documentation de l'adapter.

**Couture :** contrat seule (§1.5) — validation JSON + contrôles de
fichiers, aucune réutilisation de code amont, aucun serveur MCP de plugin
démarré, aucun identifiant lu ni détenu.

## §3. Tests

**Smoke adapter : 8/8 PASS** (unittest stdlib), re-couru sous `unshare -n`
(preuve réseau : le namespace sans interface ne change rien — l'adapter ne
fait aucun appel). Le validateur accepte un vrai répertoire de plugin amont
(`plugins/adobe` → VALID, lecture seule, pas de copie).

**Suite amont (H-M3) — périmètre honnête : pas de suite racine, pas de CI.**
Log complet : `logs-openai-plugins-suite.log`.

- `plugin-eval` (`npm test`, commande du repo) : **28/28 PASS, rc=0**.
- Python (52 fichiers `test_*.py`) : **44 fichiers OK (217 tests)**.
- pytest : `test_package_utils.py` 19 passed, `test_app_dependencies.py`
  1 passed, `test_scrnaseq_post_count_qc_runner.py` 3 passed + 1 skipped.
- `.mjs` (`plugins/data-analytics/tests/`, node:test) : **184/191 pass**,
  1 skipped.

**Rouges RÉELS au gel (hors adapter, hors périmètre) :**

- `test_deliverable_framework.py` (public-equity-investing) : 64 tests,
  **30 failures** — assertions réelles : le document de politique au gel
  ne contient pas les phrases attendues (`'normal chat and wait'` absent,
  etc.) et des déclarations de skills ne correspondent pas. Dérive
  docs/tests amont au gel.
- `mcp-server.test.mjs` (data-analytics) : 78/79 — 1 réel : `rejects
  malformed widget resource aliases`, `TypeError: Cannot read properties
  of undefined (reading 'code')` (ligne 1987) — le serveur ne rejette pas
  l'alias mal formé comme attendu.
- `test_google_calendar_plugin_contract.py` (pytest) : 1 failed —
  `FileNotFoundError: pyproject.toml` à la racine du repo (absent) : le test
  suppose une disposition absente au gel.

**Rouges ENVIRONNEMENTAUX (cause établie, pas un défaut produit) :**

- 4 fichiers `.mjs` : `Cannot find package 'typescript'` (devDep absente,
  pas de `node_modules` dans le repo).
- `portable-artifact-verifier.test.mjs` : `Cannot find package
  'playwright-core'` (devDep absente).
- `test_portable_fallback.py` : `ModuleNotFoundError: bs4`.
- `test_sample.py` (fixture plugin-eval) : `ModuleNotFoundError: src`
  (PYTHONPATH non posé).
- `test_state_helpers.py` (public-equity-investing, 34 tests, 43 failures
  + 15 errors) : **tous** `FileNotFoundError: onboarding-state.json` — la
  fixture crée un codex-home isolé mais n'ensemence jamais le fichier ;
  défaut du harnais de test amont au gel.

**Non courus :** les suites nécessitant `npm install` (deps absentes) et
les tests d'intégration à identifiants (API fournisseurs).

## §4. Télémétrie

Zéro par construction pour l'adapter (voir
`openai-plugins-TELEMETRY-AUDIT.md`) : stdlib seule, aucun appel réseau.
Le catalogue lui-même ne contient **aucun SDK de télémétrie** (0 dans les
14 `package.json`, 0 dans le code). Les 31 `.mcp.json` pointent vers des
API de fournisseurs (OAuth, identifiants de l'utilisateur) — ce sont les
fonctions des plugins, jamais invoquées par l'adapter.

## §5. Divergence

**Divergence amont → adapter :** l'adapter ne reprend rien de l'amont. Il
implémente le format de manifeste (noms de champs publics : `name`,
`version`, `description`, `interface`, `skills`, `apps`, `author`) et un
validateur de structure. Aucun comportement de plugin, aucun serveur MCP,
aucune skill n'est reproduit. Les noms de champs sont la spécification
publique du format, pas du contenu amont.

**Dette de divergence :** le catalogue vit (62 plugins, ajouts réguliers —
dernier commit amont #410 le 2026-11-06). Le gel `d420d13` est épinglé ;
toute revisite = signal de dérive (inventaire hebdomadaire, §D5), jamais de
fast-forward silencieux. Le porteur de la dette est le cœur Buzz.

**Contraintes nommées du §2 :** sans licence (D12) ; couture JS (contrat
seul) ; repli suppression nommé.

## §6. Références

- Audit télémétrie : `openai-plugins-TELEMETRY-AUDIT.md` (§1–§8).
- Log de suite : `logs-openai-plugins-suite.log` (130 lignes).
- Manifeste : `openai-plugins.manifest.json` (`"id": null`, D12).
- Compare gel→adapter : ahead 1, behind 0, 4 fichiers adapter seuls.
