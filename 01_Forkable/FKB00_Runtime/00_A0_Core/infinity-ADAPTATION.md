# Fiche d'adaptation — infinity (D-N051 F8, pas 3)

**Adresse :** `fiber:a0:infinity` (cœur Buzz)
**Manifeste :** `infinity.manifest.json` (même domicile)
**Audit télémétrie :** `infinity-TELEMETRY-AUDIT.md` (même domicile)
**Statut :** état 0 Basique → 2 Adapté + Fusionné en un seul pas (§D11)
— adaptation + portage natif livrés ensemble ; le jugement du 13e
reste requis pour la montée d'état.

## Commit gelé

- **Fork :** `Amdkn/infinity` (parent `hydro-project/infinity`,
  Apache-2.0, branche `main`, 4 970 Ko).
- **Gel : `e1a3e4b`** (`e1a3e4b36e5f6143e03a59a7ad86e1abacfd22e8`) —
  « docs: explain Linux sandbox prerequisites (#188) »,
  2026-11-05T20:10:40Z. **Identique à l'amont, dérive 0** (vérifié
  à l'API : compare gel...amont `main` = identical, 0/0).
- **Pin V5 : `007409e`** (retiré au pas 8) — l'adapter
  (`007409e242f208545b003785cbe3aa24b45cd08e`, parent = gel).
- **Bind : `b0e6110`** — `main` HEAD du fork. Le bind est re-appliqué
  **verbatim sur `main` au gel par Ryan à l'intégration** (§D2), puis
  re-pin — pas par cet agent.
- Tout commit amont ultérieur exige un amendement de design, jamais
  un fast-forward silencieux (D1).

## Adapter

- **Paquet :** `aspace-infinity-adapter/` (`@aspace/infinity-adapter`
  0.1.0, Rust edition 2024, crate autonome `[workspace]` — elle ne
  rejoint pas le workspace amont), commit
  **`007409e242f208545b003785cbe3aa24b45cd08e`** sur le fork, parent
  = gel `e1a3e4b` (tête distante vérifiée à l'API). **Seul code
  A'Space du fork** (H-M2, vérifié à l'API : compare gel...HEAD =
  ahead 1, behind 0, 7 fichiers adapter uniquement).
- **Surface :** `AspaceSessionEntry` (miroir serde de `SessionEntry` :
  `cwd`, `shut_down`, `idle`, `archived`) + `SessionState` ;
  `RapOutbox` (résultat livré à un agent sans processus, collecté
  au réveil) ; `LocalhostPolicy` (loopback seul, `0.0.0.0` refusé) ;
  `GoldfishSchedule` (`fractal_layer='4L'` explicite, cap `75_000`) ;
  `verify_gel_lineage()` (H-M1/H-M2, en local) ;
  `check_upstream_surface()` (10 pins re-vérifiés sur les sources
  du gel).
- **Smoke :** voir `logs/adapter-smoke.log` — hibernation (2 étapes
  + réveil sur texte utilisateur seul), RAP sans processus,
  localhost-only, cap + 4L, lignée gel, surface épinglée.
- **Preuves MCP / RAP :** test `mcp_rap_proof.rs` — proxy MCP
  (`tools/list` via `start_proxy_server`, callback RAP reçue) +
  **vrais serveurs `rap-test-servers` inchangés**
  (`start_stub_image_server`, `start_stub_diff_server` : manifeste
  fetché, invocation POSTée, résultat reçu sur la callback URL).
  Test amont `mcp_proxy_callback.rs` : **1/1 vert** ;
  `rap_callback_flow.rs` : **2/2 verts** (dont
  `view_update_is_broadcast_without_waking_the_session`).

## Portage natif (RigInfinity, `aspace-v5-native`)

- **Repo :** `Amdkn/RigInfinity`, branche `aspace-v5-native`
  (HEAD `43c995f` avant le pas). Le stub `lib.rs` (19 lignes) est
  devenu le daemon natif : `crates/infinity-daemon/` avec
  `Cargo.toml` (workspace racine ajouté) + modules portés —
  `session_store.rs` (port quasi-verbatim), `memory_store.rs`
  (stores durables JSON + vues + migration), `session.rs`
  (SessionManager : create/resume/list/cleanup, admission du
  routeur, réveil sur texte utilisateur), `rap_callback.rs`
  (bridge loopback + `serve_callbacks`), `mcp_proxy.rs` (client
  MCP stdio JSON-RPC + HTTP, proxy RAP loopback), `rap.rs`
  (types RAP, mêmes tags serde que l'amont), `rap_servers.rs`
  (serveurs par session, `times_shut_down`), `client.rs`
  (protocole JSON-line sur socket Unix), `http.rs` (serveur
  HTTP/1.1 partagé). Binaire `riginfinity-daemon`.
- **Commits natifs :** `bd7c94658ddd2220d6203ef3433dd390feb2ae6c`
  (portage) + `aad4993f47db807e0f3b540703ff3f6f831e2a78` (tests),
  poussés directement sur `aspace-v5-native` (tête distante vérifiée
  à l'API), parents `43c995f` → `bd7c946` → `aad4993`. Pas de PR —
  le repo n'a ni CI ni processus PR.
- **Tests natifs :** voir `logs/native-port.log` — unitaires
  (hibernation, stores, RAP servers) + intégration
  `tests/daemon_proof.rs` (hibernation via le vrai protocole
  client Unix, RAP vers un agent sans processus, **vrai serveur
  MCP stdio Python inchangé** via le proxy).
- **Couture documentée (pas un renommage) :** le driver modèle /
  agent-core n'est pas porté (il vit dans `infinity-agent-core` et
  les providers, hors périmètre §D3) — le manager expose la file
  d'entrée (`take_input_receiver`) comme couture provider. Le
  WebSocket + les web assets (UI) ne sont pas portés (surface UI,
  hors pas) — les clients locaux utilisent le socket Unix, les
  outils distants RAP. `INFINITY_WS_BIND` non loopback est refusé
  au démarrage du daemon natif (R-2 de l'audit).

## Tests au gel et sur le fork adapté

- **Commandes CI (parité §D13) :** `cargo test --all-targets` +
  `cargo test --doc` + `cargo fmt --all --check` +
  `cargo clippy --all-targets -- -D warnings` + THIRD-PARTY
  (cargo-about). Logs : `logs/suite-parity.log` (passe fail-fast) +
  `logs/suite-parity-nff.log` (passe `--no-fail-fast` complète).
- **Bilan — `cargo test --all-targets --no-fail-fast` : 385 passés /
  42 échoués / 0 ignoré (59 binaires), EXIT 101.** Les 42 rouges
  sont TOUS environnementaux pré-existants au gel, 0 imputable à
  l'adapter (qui ne touche aucun fichier amont — compare API
  gel...HEAD = 7 fichiers adapter seuls) :
  - **36 échecs `sandbox-local`** (13 binaires : `bookmark_moved_…`,
    `clone_repo_switch`, `describe_changes`, `edit_file`,
    `execute_after_init`, `execute_command`, `jj_colocated`,
    `migrate`, `nested_repo_root`, `read_file_image`,
    `stale_workspace_cleanup`, `subagent_no_squash`,
    `tmpdir_stable`, `write_escape`) — tous paniquent à
    `tests/common.rs:143` : `run jj git init: No such file or
    directory` — **`jj` (jujutsu) absent de cette VM** (la CI
    l'installe ; `check.bash` l'exige aussi).
  - **6 échecs `infinity-slack-dataflow` (`dataflow_sim`)** — panique
    `hydro_lang …/trybuild/generate.rs:471`, `dep prebuild failed` :
    le pré-build hydro ne peut pas mettre à jour
    `target/hydro_trybuild/infinity-slack-dataflow/Cargo.lock`
    (`--locked` passé) — défaut de l'outillage hydro sur cette VM.
- **Bilan — daemon (le périmètre du pas), tout vert :**
  `infinity-daemon` lib 21/21, `keep_alive` 4/4,
  `mcp_proxy_callback` 1/1, `rap_callback_flow` 2/2,
  `e2e_daemon_tui` 6/6, snapshots TUI 66/66 au total,
  `web_e2e` 0 test (aucun cas exécuté — pas un échec),
  `live` 0 test (tests live provider, sans credentials — pas un échec).
- **`cargo test --doc` : 45 passés / 0 échoué, EXIT 0.**
- **`cargo fmt --all --check` : EXIT 0** (workspace amont ; l'adapter
  est formaté séparément, propre).
- **`cargo clippy --all-targets -- -D warnings` : EXIT 0** (propre).
- **THIRD-PARTY : PASS — `git diff --exit-code THIRD-PARTY` = 0**
  (cargo-about 0.9.3, `bash scripts/generate-third-party.sh`,
  log `logs/third-party.log`). L'adapter n'ajoute aucune dépendance
  amont ; le `Cargo.lock` du workspace est intact.
- **Réserves connues d'avance (confirmées) :** `web_e2e.rs` exige
  Playwright — présent sur cette VM (chromium-1248) mais 0 cas
  exécuté dans cette passe ; `check.bash` exige `jj` + `bwrap`
  (`bwrap` présent, `jj` absent — c'est la cause des 36 rouges
  sandbox-local).

## Télémétrie

**Zéro par contrat.** Voir `infinity-TELEMETRY-AUDIT.md` : 0 signal
(`telemetry`/`posthog`/`sentry`/`analytics` = 0 dans tout le fork),
0 appel sortant par défaut, surface daemon loopback seulement.
Réserves : R-1 `0.0.0.0` dans steering-server / poller /
sandbox-local (hors daemon, hors pas) ; R-2 `INFINITY_WS_BIND`
surchargeable (refusé côté natif) ; R-3 URLs de callback fournies
par l'appelant (validées loopback côté natif) ; R-4 remotes SSH
configurées (aucune par défaut).

## Divergence

- **4L / 8L (cosmétique, F8 D6) :** le plugin dit `4L`, le
  scheduler du bind défaut `8L`. L'adapter passe `'4L'`
  explicitement partout (`GoldfishSchedule::new`) ; le bind n'est
  pas réécrit (§D2).
- **Cap 75 000 (constante, §D8) :** repris tel quel du scheduler /
  README, **non mesuré, non garanti**. Aucun test de charge.
- **Précédence de statut (amont, vérifiée) :** `SessionEntry::status`
  lit `idle` avant `shut_down` — une session `idle` + `shut_down`
  s'affiche `Idle` alors qu'elle hiberne (`is_hibernating()` vrai).
  Repris tel quel dans l'adapter et le natif (fidélité au gel).
- **H-P3-7 reprise au checkpoint : CONDITIONNELLE (§D4).** La
  reprise utilise les checkpoints de pi (pas 2, non vert) : la
  preuve est consignée comme conditionnelle, pas comme verte.
  Re-preuve quand le pas 2 devient vert.
- **Dette :** le daemon sprawl ne se résorbe pas au pas 3 (§D12 —
  openrig et herdr-core tournent encore) ; le cron 30 min est
  retiré par Ryan dans la PR (§D5), pas ici.

## Hold-outs (état à la livraison)

| # | État |
|---|---|
| H-M1 gel | PASS — HEAD fork = gel `e1a3e4b`, dérive 0 |
| H-M2 amont intact | PASS — diff gel...HEAD = adapter seul (API) |
| H-M3 suite verte | **ROUGE QUALIFIÉ** — suite complète 385/42 (voir § Tests) : les 42 rouges sont environnementaux pré-existants (`jj` absent, pré-build hydro `--locked`) ; 0 imputable à l'adapter ; daemon 100 % vert ; doc 45/0 ; fmt + clippy propres. Jugement 13e requis. |
| H-M4 télémétrie zéro | PASS — audit versionné |
| H-M5 manifeste | PASS — `infinity.manifest.json`, `fiber:a0:infinity` |
| H-M6 frontière adapter | PASS — adapter seul code A'Space du fork |
| H-M7 fiche versionnée | PASS — cette fiche |
| H-P3-3 hibernation | PASS — daemon (amont + natif), 2 étapes + réveil texte seul |
| H-P3-4 RAP | PASS — résultat livré sans processus (amont + natif) |
| H-P3-5 daemon unique | PASS (portage) — le cron est retiré par Ryan en PR (§D5) |
| H-P3-6 MCP compat | PASS — test amont vert + vrais serveurs `rap-test-servers` + vrai MCP stdio natif |
| H-P3-7 checkpoints | **CONDITIONNELLE** — pas 2 non vert (§D4) |
| H-P3-8 télémétrie zéro | PASS — audit fork entier |
| H-P3-9 manifeste + fiche | PASS |
| H-P3-10 suite verte | **ROUGE QUALIFIÉ** — voir H-M3 (385/42, 42 environnementaux pré-existants ; daemon vert ; THIRD-PARTY en cours) |
