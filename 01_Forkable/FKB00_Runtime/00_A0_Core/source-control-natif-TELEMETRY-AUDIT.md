# Audit télémétrie — source control natif V5, SC-0 (D-N054, H-M4)

**Portée :** le pas SC-0 (re-pin RigInfinity `86f1139` → `e866578`). Le re-pin est un changement de pointeur seul : **0 ligne de code ajoutée, 0 dépendance ajoutée, 0 appel réseau ajouté par ce pas.**

## Le daemon au pin `e866578`

- **Code natif :** Rust, std-only + `rusqlite` 0.32 (bundled) + `serde_yaml` 0.9 (portages pas 3/4/5). Aucun SDK d'analytics, aucun client HTTP sortant dans le code natif.
- **Lecture locale seule :** la surface de lecture `/api/telemetry/*` du daemon openrig (6 routes sur le SQLite du daemon, faits seulement, aucune identité de compte) est reprise en lecture locale (`usage_series()`) — aucun site sortant.
- **Sites sortants fermés par défaut (audit pas 4) :** Slack clé-gaté, OpenRouter opt-in, pairing opérateur, plugin-vendor tolérant — tous fermés par défaut.
- **Agent-zero (pas 5) :** le fork contient 1 signal (`helpers/update_check.py` → `https://api.agent-zero.ai/a0-update-check`, défaut `True`) — **non porté dans le natif : 0 signal dans le daemon.**

## Verdict SC-0

**0 exporteur, 0 SDK, 0 appel sortant par défaut au pin `e866578`.** Le re-pin n'ajoute rien : la télémétrie du daemon est inchangée par ce pas. Tout déclencheur futur (SC-1+) sera tranché et consigné dans cet audit.

## SC-1 — le module `source_control` (pin `c6adc8d`)

**Portée :** le pas SC-1 ajoute le module de lecture (`crates/infinity-daemon/src/source_control.rs`, 922 lignes) + son test (`tests/source_control_proof.rs`, 251 lignes). **0 dépendance ajoutée** (reqwest, serde_json, tokio déjà dépendances du daemon).

**Déclencheur tranché — appels sortants sur requête uniquement :**
- **Destination unique : l'API GitHub (`https://api.github.com`).** Le module émet des GET HTTPS uniquement quand une des 3 requêtes vivantes est posée (`diff`, `blame`, `ancêtre`) ; aucune émission au démarrage, aucun heartbeat, aucun polling.
- **Authentification :** token lu dans l'environnement (`GITHUB_TOKEN`, sinon `GH_TOKEN`) à la construction du transport ; absent, les requêtes partent sans token (quota anonyme GitHub). Le token n'est jamais écrit dans un fichier, jamais logué (les erreurs nomment l'URL et le statut, pas le header), jamais stocké.
- **Ce qui n'est PAS émis :** aucun SDK d'analytics, aucun exporteur de télémétrie, aucun appel vers un tiers autre que l'API GitHub, aucun sous-processus `git` (vérifié par grep : 0 occurrence de `Command` / `git clone` dans le module et son test), aucun clone (le module ne connaît pas le concept de checkout).
- **Données sortantes :** seuls les paramètres de la question (repo, refs, chemin) partent vers l'API GitHub ; aucune donnée locale (état du daemon, sessions, mémoire) n'est transmise.

## Verdict SC-1

**0 exporteur, 0 SDK, 0 appel sortant par défaut au pin `c6adc8d`.** Le seul trafic sortant nouveau est celui des 3 requêtes de lecture, vers l'API GitHub uniquement, sur demande explicite — c'est la fonction du module, pas de la télémétrie.

## SC-2 — le module `changeset` (pin `655b2a4`)

**Portée :** le pas SC-2 ajoute le module WAL (`crates/infinity-daemon/src/changeset.rs`, 627 lignes) + son test (`tests/changeset_proof.rs`, 317 lignes). Correctifs `c83b281` (parent `814b83c`) + `655b2a4` : `tmp_path` sans appel processus, commentaire sans le littéral greppé — la preuve no-subprocess reste littérale. **1 dépendance ajoutée** (`sha2` 0.10 — hachage seul, aucune émission réseau ; son arbre : `digest`, `crypto-common`, `block-buffer`, `typenum`, `generic-array`, `cpufeatures`).

**Déclencheur tranché — aucun :** le module n'émet rien. SQLite local seul (`changeset_blobs` / `changesets` / `changeset_files` dans le store de la factory, mode WAL) ; 0 invocation `git`, 0 sous-processus, 0 socket (vérifié par grep : 0 occurrence de `Command` / `reqwest` / `TcpStream` / `git clone` dans le module et son test) ; aucun token, aucun secret, aucune donnée sortante — le changeset ne quitte jamais la machine.

**Correction :** les comptes de lignes SC-1 de cet audit (922 / 251) étaient périmés — les fichiers font 1 035 / 359 lignes (fiche). Les comptes SC-2 ci-dessus sont vérifiés au fichier.

## Verdict SC-2

**0 exporteur, 0 SDK, 0 appel sortant par défaut au pin `655b2a4`.** Le WAL est purement local ; le seul trafic sortant du natif reste celui des 3 requêtes de lecture SC-1, vers l'API GitHub uniquement, sur demande explicite.
