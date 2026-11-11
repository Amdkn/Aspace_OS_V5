# Source control natif V5 — fiche (D-N054, H-M7)

**Mission :** D-N054 — Source control natif V5, au-delà du paradigme Scion.
**Design :** `SOURCE-CONTROL-NATIF-V5-SCION-plan-borne.md` (Clara, signé, 28 728 o, D1–D15).
**Adresse :** `fiber:a0:source-control-natif`. **Hôte :** daemon unique RigInfinity (`crates/infinity-daemon`, Rust).
**Propriétaire :** cœur Buzz (S2-D12 ; S3-BILL, S3-CLARA, S3-NARDOLE).

## Substrat (H-M1)

- V5 master `e68f130` (à la livraison SC-0 ; le master bouge par les pulses workgraph — re-vérifier avant chaque merge).
- `.gitmodules` : 118 entrées, 118 URL Amdkn, 0 dehors.
- Clone complet : 28,33 Go (openclaw 13,0 Go, 46 %) — l'argument du natif.
- Check `r10-receipt` : 0 occurrence dans V5 (décision signée H-02-A1-2, mécanisme à implémenter à SC-4).
- Branches : 21 (18 mergées, 3 en vie au design).

## Base daemon (SC-0)

- RigInfinity `aspace-v5-native`, pin **`e866578`** (re-pin SC-0 ; ancien pin `86f1139`, squelette).
- **34 fichiers suivis** au pin (`git ls-tree -r --name-only | wc -l`) — correction : le design citait 35.
- Commits déposés : `bd7c946` (pas 3 infinity) + `a372582` + `e190645` (pas 4 openrig) + `e866578` (pas 5 agent-zero).
- Preuve SC-0 : le pin pointe le daemon ; le Runtime démarre sur le pin (suite `cargo test -p infinity-daemon` re-vérifiée au pin).

## Référence clean-room

- **CarterT27/scion** (Rust, Apache-2.0, 3 972 Ko, 295 étoiles, 25 forks, push 2026-10-16, non affilié Anthropic, pas un fork) — **référence seule, jamais copiée** ; clean-room si transposition.
- Scion dans V5 avant D-N054 : nommé en 10 endroits, documenté en 1, implémenté en 0.
- Benchmark retenu : git gagne le commit ; le natif doit battre git à la *question* (pas de clone de 28 Go pour un diff) et à la *coordination* (le changeset porte son jugement).

## Dette de divergence

- **Dette SC-0 CLOSE (SC-1) :** le manifeste du daemon (`aspace-plugin.json` dans RigInfinity, pin `c6adc8d`) nomme désormais le module — capability `source_control_natif_read_api`. Le module a atterri : `crates/infinity-daemon/src/source_control.rs` + `tests/source_control_proof.rs`.
- Aucune divergence de code au SC-0 : le re-pin n'ajoute aucune ligne (changement de pointeur seul).

## SC-1 — API de lecture : diff, blame, ancêtre sans clone (D-N054)

- **Module :** `crates/infinity-daemon/src/source_control.rs` (1035 lignes) + `tests/source_control_proof.rs` (359 lignes), pin daemon **`c6adc8d`** (parent `ee5c838`, vérifié à l'API) ; **36 fichiers suivis** au pin (34 au SC-0 + module + test).
- **Contrat D4 — 6 requêtes exactement :** `diff`, `blame`, `ancêtre` vivent à SC-1, servies au-dessus de l'API GitHub (reqwest, déjà dépendance du daemon — 0 dépendance ajoutée) ; `reçu` (SC-3), `jugement` (SC-4), `hold-out` (SC-5) répondent `pending` structuré — jamais de fausse donnée.
- **Diff / ancêtre :** API compare (`/compare/{base}...{head}`) — fichiers + ajouts/suppressions + `merge_base_commit`.
- **Blame :** pas d'endpoint REST blame chez GitHub — calcul à la demande (différé, D3) par application avant des patches (*forward-application*) des commits touchant le chemin, vérifié contre le contenu au ref ; plafonds 100 commits / 2 000 lignes ; tout écart (historique tronqué, patch absent, contenu divergent) est une erreur, pas une attribution silencieuse. Cas renommage : contenu au commit de renommage pris comme base. Cas merge (correctif `ee5c838`, trouvé par la preuve live sur `AGENTS.md`) : un fichier introduit par un merge (la liste `commits?path=` nomme le merge, pas la création) est amorcé depuis le contenu au merge, attribué au merge — sinon le replay partirait à mi-fichier (hunk ligne 6, curseur ligne 1) et refuserait à tort. Cas racine + troncature (correctif `c6adc8d`, trouvé par la même preuve) : l'API plafonne la liste `files[]` d'un commit à 300 entrées — le commit racine de V5 (`877ebc8`, 1 631 fichiers) cache la création d'`AGENTS.md`, et `caf85c0` (300 fichiers) cache sa modification ; une racine sans entrée est amorcée depuis son propre contenu, tout autre gros commit sans entrée utilisable est un refus (`PatchUnavailable`), jamais un replay avec un trou — `AGENTS.md` lui-même n'est donc pas blâmable par cette API, et la preuve live choisit un fichier qualifié (chaque commit touchant porte une entrée, ou est un merge / une racine).
- **Preuve H-SC-3 (première preuve partielle, D10) :** une question servie sans clone de 28,33 Go — preuve live dans `RESULTS-D-N054-SC1.json` (diff + blame + ancêtre réels sur `Amdkn/Aspace_OS_V5`, recoupés à `gh api`).
- **Sans clone, par construction :** le module n'invoque jamais `git`, ne lance aucun sous-processus ; seul trafic sortant = HTTPS vers l'API GitHub, sur requête uniquement. Token par env (`GITHUB_TOKEN` / `GH_TOKEN`) — jamais en dur, jamais logué.
- **Suite (H-M3) :** `cargo test -p infinity-daemon` **64/64** au pin (lib 51/51 — dont 4 tests `source_control` — + `agent_zero_proof` 5/5 + `daemon_proof` 4/4 + `source_control_proof` 4/4, dont les cas merge et racine) ; clippy 0 warning ; rustfmt clean.
- **Clean-room :** écrit à partir de la surface REST GitHub et de l'algorithme standard d'attribution par lignes — aucun code copié de `CarterT27/scion`.

## SC-2 — Changeset WAL : entrée + pointeurs adressés par contenu (D-N054)

- **Module :** `crates/infinity-daemon/src/changeset.rs` (627 lignes) + `tests/changeset_proof.rs` (317 lignes), pin daemon **`655b2a4`** (parent `c83b281`, vérifié à l'API) ; **38 fichiers suivis** au pin (36 au SC-1 + module + test). Correctifs : `c83b281` (`tmp_path` sans appel processus) + `655b2a4` (commentaire sans le littéral greppé) — la preuve no-subprocess reste littérale.
- **Le changeset (H-SC-1, D2) :** une entrée append-only du WAL — id ULID maison, parent = tête de chaîne, auteur, message, instant ISO-8601 UTC, `entry_hash`, `prev_hash` ; tables `changeset_blobs` / `changesets` / `changeset_files` dans le même store SQLite que `factory.sqlite`, étendu (pas un second store) — `from_connection` applique le schéma à une connexion existante, preuve par test (`extends_existing_store` : table `rigs` pré-existante intacte). Mode WAL (`PRAGMA journal_mode=WAL`) sur fichier ; reprise prouvée par réouverture (`wal_mode_on_file_and_reopen`).
- **Sans copie :** chaque blob est stocké une fois (`INSERT OR IGNORE`, clé = SHA-256 hex) ; l'entrée ne stocke que le hash (64 car.) — un changeset se crée sans copie, preuve `changeset_created_without_copy` : blob 1 Mio, 1 seule ligne blob, 1 048 576 o stockés, entrée = hash seul ; même contenu dans 2 changesets → toujours 1 ligne blob.
- **Chaîne à l'épreuve des falsifications :** `entry_hash` = SHA-256 de la sérialisation canonique incluant `prev_hash` ; `verify_chain` + `replay` refusent toute rupture (preuve `tamper_detected` : `prev_hash` corrompu → erreur au verify et au replay). Caps : 1 000 fichiers / 64 Mio par blob, chemins repo-relatifs, refus avec motif — jamais d'écriture partielle (transaction unique).
- **Ce qui n'est PAS là :** ni jugement ni reçu dans le changeset — SC-3 (données dérivées), SC-4 (check `r10-receipt`), SC-5 (hold-outs comme gates). Un changeset sans verdict est une donnée, pas un gate.
- **Dépendance ajoutée :** `sha2 0.10` seule (SHA-256 — std n'en a pas, DefaultHasher instable inter-versions) ; ids ULID maison, horodatage `iso_now()` std-only. 0 appel réseau, 0 sous-processus, 0 invocation `git` (vérifié par grep). Note lock : la résolution offline a re-pinné les crates wasm-only `wasm-bindgen` 0.2.130 → 0.2.126 et `js-sys`/`web-sys` 0.3.107 → 0.3.103 — jamais compilées sur cette cible Linux, suite verte.
- **Suite (H-M3) :** `cargo test -p infinity-daemon` **75/75** au pin (lib 54/54 — dont 3 tests `changeset` — + `agent_zero_proof` 5/5 + `daemon_proof` 4/4 + `source_control_proof` 4/4 + `changeset_proof` 8/8) ; clippy `-D warnings` 0 ; rustfmt clean.
- **Plugin :** `aspace-plugin.json` nomme désormais `source_control_natif_changeset_wal` (capability, en plus de `source_control_natif_read_api`).
- **Clean-room :** écrit à partir du design et de la sémantique WAL de SQLite — aucun code copié de `CarterT27/scion`.

## Contraintes (§2 du design)

- Plafonds : 1 % le natif, 5 % par pas (SC-0..SC-10), 20 % mission-wide, alerte 80 %.
- Calendrier : 1 jour max par pas, 11 jours max. Un pas ne commence que quand le précédent est vert — sauf ordre S0.
- Le natif ne reconstruit pas git (BYB §3 OUT, garde-fou) ; local-first ; `enforce_admins` reste false ; pas de verrou global.
- Saisine explicite au 13e à chaque livraison ; merge true merge commit (2 parents, DVG-01), jamais par le runner ; reçu R10 par pas.
- Arbitrages vision possibles (via Rick → A0) : (a) store séparé de `factory.sqlite` ; (b) preuve finale avant les pas intermédiaires.
