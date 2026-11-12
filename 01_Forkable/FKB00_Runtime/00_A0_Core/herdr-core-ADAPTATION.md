# Fiche d'adaptation — herdr-core (D-N053 pas F1)

**Adresse :** `fiber:a0:herdr-core`
**Manifeste :** `herdr-core.manifest.json` (même domicile)
**Audit télémétrie :** `herdr-core-TELEMETRY-AUDIT.md` (même domicile)
**Statut :** état 1 Adapté (pas F1, PR V5 à juger par le 13e)
**Licence :** Apache-2.0

## Commit gelé

- **Fork :** `Amdkn/herdr-core` (parent `herdrdev/herdr-core`, Apache-2.0, branche `master`).
- **Gel : `cd12ddd`** — version 0.1.18 + 10 commits (`v0.1.18-10-gcd12ddd`), 2026-11-07.
- **Dérive au gel : 53 commits** vers l'amont HEAD `13da068` (v0.1.19 `06793ed` + v0.1.20 `de97ea5`) — triage versé au design §2.1 : protocole gelé (0 commit sur `wire.rs` + `rpc.rs`), schéma additif seul (32 méthodes = 32 méthodes, `server.restart` gagne un paramètre optionnel `environment`), `server.rs` +90 lignes, `client.rs` +26, `lib.rs` +7, 84 fichiers touchés. Revisite par signal raccourcie à 3 jours tant que la dérive dépasse 20 (D-F1-4, suivi S-F1-3).
- **Tout commit amont ultérieur exige un amendement de design**, jamais un fast-forward silencieux (D-F1-4).

## Adapter

- **Dossier :** `aspace-herdr-core-adapter/` (crate adapter + contrat JSON + config embarquée + preuve de protocole + smoke test shell), commit **`d50ebd8`** sur le fork (parent = gel `cd12ddd`, vérifié à l'API). **Seul code A'Space du fork** — le code amont est byte-identique au gel (H-F1-2). Bind re-appliqué verbatim au-dessus (`be144c8`, `aspace-plugin.json` 24 lignes, byte-identique au bind `14a3772`) ; **pin = commit adapter `d50ebd8`**.
- **Forme (D-F1-1, les deux) — une vraie crate, pas un contrat seul :**
  - **Bibliothèque** (`src/lib.rs`, crate `aspace-herdr-core-adapter`) : ré-exporte **33 des 35 modules `pub`** de `lib.rs` amont — tous sauf `server` (le daemon `server::serve()`) et `cli` (`cli::main()` dispatche `server start`, `update`, `serve`, `hold` et auto-démarre un daemon). Précision : le décompte « 30 modules » du design est périmé — `lib.rs` porte 35 modules `pub` au gel.
  - **CLI cliente** (`src/bin/hc.rs`, binaire `hc`) : chaque verbe parle à un core **déjà en cours, côté opérateur**, via `client::require_existing` — jamais `connect_or_start`. `hc server start`, `hc update`, `serve`, `hold` n'existent pas dans ce binaire (clap les rejette). Verbes : `run ls get kill rm label keep send wait keys interrupt attach read put exec`, `terminal <verbe>`, `file read|write|edit`, `machine add|ls|login|update|rename|rm`, `events`, `templates`, `server status|stop|restart`, `schema`, `doctor`, `call <méthode>`.
  - **Protocole** : la connexion démarre en mode plain (une ligne JSON-RPC par ligne) ; un `hello` réussi avec `framed: true` bascule en trames (`[channel u32 LE][kind u8][len u32 LE][payload]`, `MAX_PAYLOAD` 16 Mo, fenêtre 256 Ko) ; canal 0 = JSON-RPC ; schéma `schema/hc.openrpc.json` (32 méthodes, versionné comme contrat). Les appels unitaires de `client::call` restent en mode plain — c'est le mode encadré qui porte les flux attachés.
- **Jamais (le serveur `hc` n'est PAS réintroduit) :** `server::serve()` (verrou `core.lock`, écoute, `Core::start`, `recover_kept`, `run_jobs`, `watch_foreground`, `save_when_due`, enregistrements launchd/systemd) ; `hc server start` ; l'état `~/.local/state/herdr-core/` tenu par un serveur V5 ; l'auto-démarrage (`demand-start`, `hc-launchd-*`) ; `hc update` (jamais contre `releases.herdr.dev` — les tests amont utilisent le faux serveur local `releases_server.py`).
- **Socket par défaut réel (E-F1-4) :** `$XDG_RUNTIME_DIR/herdr-core/default.sock` (session `default`, env `HC_SESSION` ; override `HC_SOCKET` > config > défaut). `/tmp/herdr-core.sock` n'est PAS le défaut `hc` — c'était l'override du superviseur V5, fibre retirée par F8 pas 8.
- **Acte de build (E-F1-8) :** le sous-module `vendor/ghostty` est non initialisé en clone frais (shallow `-1e5cdb8`) — `git submodule update --init --depth 1` comme acte de build, pas de code.
- **Interrupteur forcé (D-F1-5, H-F1-4) :** `notes = false` — config embarquée `aspace-herdr-core-adapter/config.toml`, vérifiée au fichier ET par la preuve de protocole (la lib lit la config et `notes == Some(false)`). Défaut amont : ON.
- **Couture herdr ↔ herdr-core (E-F1-3) :** 0 lien de code inventé — les deux repos sont deux produits séparés à ces pins. La couture nommée est (a) la bibliothèque adapter herdr-core comme client du protocole encadré `hc`, (b) l'adapter CLI-contrat herdr comme client du socket herdr NDJSON. Le natif consomme les deux voies séparément (D-F1-2).
- **Revendication 31415 (D-F1-6) :** le bind revendique `universal_harness_gateway_31415` + `http://127.0.0.1:31415/v1/chat/completions` — qualifiée côté A'Space (FreeCloud, `aspace_freecloud_gateway.py`), pas une capacité du gel. Bind re-appliqué verbatim, non modifié au pas F1.
- **Preuve client du protocole encadré (H-F1-3) :** `tests/protocol_roundtrip.rs` (4 tests : round-trip trames `hello` canal 0, round-trip plain-mode `client::call` `server.status`, constantes, socket par défaut) et `protocol-proof/` (binaire autonome : config `notes=false` lue par la lib, `require_existing` échoue proprement sans serveur, `hello` plain `framed:true` puis round-trip trames + JSON-RPC `server.status` canal 0 contre un stub local). Jamais contre un serveur `hc` V5, jamais contre `releases.herdr.dev`.
- **Smoke test :** `bash aspace-herdr-core-adapter/smoke_test.sh` (crate adapter debug, session scratch, XDG scratch ; construit la crate, lance ses tests, vérifie le binaire adapter `hc`, la config `notes = false`, l'absence de `server`/`update` de la surface, et la preuve de protocole).
- **Corrections d'atelier (hors design, mécaniques) :** la crate telle que livrée par le premier jet ne compilait pas (`fn main() -> i32` invalide, `stdin.is_terminal()` sans trait en portée, `mut` inutile) — 3 corrections minimales appliquées avant le commit, sans changement de comportement. Voir le reçu du pas.

## Tests au gel et sur le fork adapté

- **Au gel `cd12ddd` :** `cargo test --locked` workspace Linux : **157 passés, 1 échec, 1 ignoré** (voir `logs-suite-baseline-gel.log`). L'échec unique est `distribution::a_machine_of_another_cpu_gets_the_released_build_for_it` — « timed out waiting for added » (fenêtre fixe de 10 s du harnais) ; diagnostic : avec la fenêtre portée à 120 s (patch temporaire, reverté, clone vérifié propre), le test passe en 22,89 s — le flux `machine add` aboutit, plus lentement que les 10 s fixes sur cette VM (1,5 CPU). Échec de timing pré-existant au gel, 0 imputable à l'adapter (qui ne touche ni `machines.rs`, ni `releases.rs`, ni le flux d'installation). Les deux premiers runs en SIGABRT venaient du watchdog du harnais (30 s par défaut, `tests/common/mod.rs`) — levé à 600 s pour les runs (`HC_TEST_WATCHDOG_S`, prévu par le harnais : « CI's slower runners set HC_TEST_WATCHDOG_S »), pas une réduction de suite. `fmt` vert, `clippy -- -D warnings` vert. Tests `windows`/`macos` exclus (cibles CI par matrice). `cargo-deny` exclu nommément (absent de la VM).
- **Sur l'adapté `d50ebd8` :** même suite + tests de la crate adapter **4/4** + smoke adapter vert + preuve de protocole verte (voir `logs-suite-adapte.log`, `logs-suite-adapte-distribution-rerun2.log`, `logs-smoke-adapte.log`). Résultat consolidé : **158 passés, 0 échec, 1 ignoré** (11 + 135 + 0 + 2 + 2 + distribution 8/8) ; `fmt` vert, `clippy -- -D warnings` vert. Le binaire `distribution` a été re-couru en série (`--test-threads=1`, ordonnancement seul, mêmes 8 tests) après diagnostic : en parallèle, les 8 tests téléchargent chacun ~110 Mo dans `/tmp` (tmpfs 512 Mo, non redimensionnable — `mount` refusé, user namespace) et `tar` échoue en ENOSPC (« Wrote only X of 10240 bytes ») ; `Session::program` fait `env_clear()`, donc `TMPDIR` ne propage pas aux enfants. En série : 8/8, y compris le test de timing (10 s suffisent quand le CPU n'est pas disputé). La baseline parallèle reste la référence gel (157/1) ; l'écart vient de l'environnement, pas de l'adapter (qui ne touche aucun fichier amont).
- **Limite franche :** Zig absent de cette VM — installé manuellement (0.16.0, `~/workspace/.tmp/zig-x86_64-linux-0.16.0`) pour `ghostty-vt`. Le client HTTP de zig ne passe pas le proxy de la VM (400) — les paquets manquants sont téléchargés avec curl puis mis en cache par `zig fetch` local. Le quota disque de la VM a été saturé pendant le pas (~50 Go de `target/` périmés supprimés, dépôts intacts) — deux runs tués par EDQUOT 122 avant le ménage.

## Télémétrie

**Zéro appel sortant par défaut.** Voir `herdr-core-TELEMETRY-AUDIT.md` : aucun SDK de télémétrie, aucune crate HTTP ; tout le réseau passe par `curl` en sous-processus (chemin `hc update` uniquement) ou par SSH. Capture réseau (strace des chemins du smoke) : 1 seul `connect()` — socket Unix local, `ENOENT` sans serveur — 0 `AF_INET`. `hc update` manuel, hors contrat (n'existe pas dans le binaire adapter) ; `notes` défaut ON, forcé OFF par l'adapter.

## Divergence (dette portée par le cœur Buzz, lane Clara / 12e)

- **Règles maison amont respectées (AGENTS.md) :** la racine `AGENTS.md` amont n'a PAS été éditée (H-M2) ; l'adapter ne touche pas au cœur.
- **Ré-audit télémétrie :** à chaque changement de commit gelé ou d'adapter, et au minimum à chaque transition d'état (D3).
- **Dette de divergence :** 53 commits amont non repris (triage versé au design §2.1) ; revisite par signal à 3 jours tant que la dérive dépasse 20.

## Références

- Design pas F1 signé Clara (2026-11-12) : `~/workspace/v4-factory/plans/DESIGN-D-N053-PAS-F1-PROJET.md`.
- Discover pas F1 de Bill : `~/workspace/v4-factory/evidence/D-N053/f1/DISCOVER-PAS-F1.md`.
- Évidences : `~/workspace/v4-factory/evidence/D-N053/f1/herdr-core/`.
- Fork : https://github.com/Amdkn/herdr-core (gel `cd12ddd`, adapter `d50ebd8`, bind `be144c8`).
