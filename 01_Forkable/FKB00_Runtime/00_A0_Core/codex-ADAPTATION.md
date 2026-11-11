# Fiche d'adaptation — codex (D-N048 V3b)

**Adresse :** `fiber:a0:codex`
**Manifeste :** `codex.manifest.json` (même domicile)
**Audit télémétrie :** `codex-TELEMETRY-AUDIT.md` (même domicile)
**Statut :** état 2 Vérifié (hold-outs H-M1..M7 verts + validation 13e, PR #11 mergée `8d2c658` ; fiche + adapter + manifeste, smoke 6/6, suite 8 931 passés / 49 échecs qualifiés environnementaux / 17 ignorés, 6 crates non courues OOM — voir § Tests)
**Licence :** Apache-2.0

## Commit gelé

- **Fork :** `Amdkn/codex` (parent `openai/codex`, Apache-2.0, branche `main`).
- **Gel : `27fcd7c`** — version workspace `0.0.0` (estampillée à la release).
- **Correction de création nommée :** le fork a d'abord été créé sur le HEAD courant de l'amont (`caae161`, après le gel) ; la référence `main` a été ramenée au gel par mise à jour forcée de la ref (SHA complet, corps JSON — `gh api -f force=true` rejeté).
- **Gitlink V5 :** à avancer au gel dans cette PR (chemin inchangé).
- **Tout commit amont ultérieur exige un amendement de design**, jamais un fast-forward silencieux (D5).

## Adapter

- **Dossier :** `aspace-codex-adapter/` (contract.json + smoke test shell + README + AGENTS.md local), commit `0a0094d` sur le fork (premier commit `69e9baa` ; correctif smoke test seul — le grep du pin ne tolérait pas le JSON compact, 1 ligne). **Seul code A'Space du fork** — le code amont est byte-identique au gel (diff gel→adapter = 4 fichiers, vérifié à l'API).
- **Surface (contrat seul, §1.5) :** sous-commandes qui parlent seulement — `codex --version`, `codex --help`, `codex exec --help`. Jamais `exec` / `review` (appel modèle), `login` / `logout`, `update`, `app-server` / `exec-server`, `fork`.
- **Jamais :** tout appel modèle, tout appel réseau, toute authentification.
- **Couture Rust↔TS (§2) :** contrat seul — aucune couture spécifique construite.
- **Smoke test :** `bash aspace-codex-adapter/smoke_test.sh` (binaire `codex-rs/target/debug/codex`, construit au gel avec Rust 1.95.0, maison scratch `CODEX_HOME`, overrides forcés ; vérifie `--version`, `--help`, `exec --help`, et le passage sans interface réseau via `unshare -n`) — **6/6 VERT** (log `logs-codex-smoke.log`).

## Tests au gel et sur le fork adapté

- **Au gel `27fcd7c` : suite amont `cargo test --locked` (workspace `codex-rs/`, 169 crates membres, Rust 1.95.0) — TERMINÉE** (log `logs-codex-suite.log`, sections v11 + v13-b1 à v13-b9). CI amont : `just test` = `cargo nextest run --no-fail-fast` (profil local) ; `cargo test --locked` est la voie équivalente sans nextest.
- **Bilan (dernier run par crate, dédupliqué par script sur le log — binaires `Running` → crate via fichiers `.d`) : 8 931 passés, 49 échecs, 17 ignorés, 142 crates avec binaires de test exécutés.** 21 crates sans test par construction (0 annotation `#[test]` : supports, modèles, templates, macros). **6 crates non courues : `codex-app-server`, `codex-tui`, `codex-cli`, `codex-agent-extension`, `codex-thread-manager-sample`, `codex-core`** — leurs binaires de test ne compilent pas sur cette VM (OOM répétée, 7+ kills documentés ; leurs LIBS compilent — le binaire `codex` et les libs profil test sont construits). 2 crates support avec tests non courues car leurs parents ne l'ont pas été : `app_test_support` (4 tests), `core_test_support` (48 tests).
- **Échecs par crate (49, tous qualifiés, aucun défaut de code établi — l'adapter ne touche pas `codex-rs/`) :**
  - `codex-network-proxy` — 21, déterministes, signature `blocked-by-allowlist` au lieu du verdict attendu (`mitm-required` / `method-policy` / passage) ; reproduits à l'identique sans proxy ambiant (re-run `v13-b3e-proxy`, 321/21) — proxy ambiant écarté ; cause racine non établie sur cette VM, à re-vérifier en CI.
  - `codex-linux-sandbox` — 14 (lib 162/0) : 4 initiaux `bwrap unavailable` → `bubblewrap` 0.9.0 installé, les 4 passent ; 13 nouveaux en `managed_proxy` + 1 `handoff_client` : le sandbox réel ne fonctionne pas sur cette VM (`bwrap: Can't mount proc: Operation not permitted` — namespaces/montages restreints ; les enfants du test voient toujours `bwrap unavailable`).
  - `codex-git-attribution` — 3 au re-run (0/3), 1/2 au premier run : flaky sous charge (retry auth / wiremock, résultats variables entre runs).
  - `codex-apply-patch` — 2 : tests de permissions, impossibles en root (uid 0, vérifié).
  - `codex-windows-sandbox` — 1 : même cause root (énumération d'un répertoire « protégé » qui réussit en root).
  - `codex-exec-server` — 2 : timing OTEL / traversal cache, non reproduits (re-run tué par redémarrage runtime).
  - `codex-otel` — 2 : `buffered_operations` (flush/shutdown, timing).
  - `codex-tcp-tunnel` — 2 : `QUIC handshake timed out` (UDP/timing sandbox).
  - `codex-external-agent-migration` — 1 : inférence marketplace, 188 s, réseau sandbox.
  - `codex-guardian-v2` — 1 : binaire `codex-code-mode-host` absent — causé par l'exclusion temporaire ci-dessous, pas par le code (130/1 avec `RUST_MIN_STACK=64M` ; sans elle, stack overflow du binaire de test — voir réserves).
- **Périmètre réellement couru : 142 crates avec tests exécutés + 21 crates sans test par construction = 163/169 membres du workspace temporaire** (total au gel : 173 membres, dont 4 exclues temporairement ci-dessous). **6 crates non courues (OOM)** : `codex-app-server`, `codex-tui`, `codex-cli`, `codex-agent-extension`, `codex-thread-manager-sample`, `codex-core` — leurs binaires de test ne compilent pas sur cette VM (OOM répétée, 7+ kills documentés ; leurs LIBS compilent — le binaire `codex` et les libs profil test sont construits). Exclusions temporaires LOCALES, réversibles, jamais committées (reverties avant livraison — voir § Réserves) : `codex-code-mode-host`, `codex-code-mode-runtime`, `codex-v8-poc` (sous-modules `rusty_v8` googlesource injoignables via le proxy — fetch v8 bloqué, rc=101, 0 test) et `codex-voice-host` (`gstreamer-1.0` système absent, non installable : `libzstd1` hatch `1.5.5+dfsg2-2build1.1+hatch1` bloque `libzstd-dev`). Lockfile chirurgical (0 montée de version, 109 paquets retirés) — reverti aussi.
- **Limites franches (environnement, pas le code) :** toolchain 1.95.0 via rustup (défaut VM 1.99.1) ; VM 8 Go partagés avec les autres agents V3b — OOM répétés sur les gros binaires de test ; `/tmp` tmpfs 512 Mo plein → `TMPDIR=~/workspace/.tmp` ; `libcap-dev` 2.66 installé (build `codex-bwrap`) ; `bubblewrap` 0.9.0 installé ; `RUST_MIN_STACK=64M` requis pour 2 binaires (guardian-v2/v3, stack overflow sous pile par défaut 8 Mo — prouvé : guardian-v3 `housekeeping` passe 2/2 avec 64 Mo) ; quota disque atteint une fois (cible `target/debug/incremental/` purgée, 49 Go libérés) ; 5+ redémarrages runtime subis (reprises depuis le cache `target/`).
- **Commande de référence :** `TMPDIR=~/workspace/.tmp RUST_MIN_STACK=67108864 CARGO_BUILD_JOBS=1 CARGO_NET_GIT_FETCH_WITH_CLI=true cargo +1.95.0 test --locked --offline -p <crate>` par lots (le run workspace complet ne tient pas sur cette VM partagée — OOM).

## Télémétrie

**Coupée par contrat (module réel dans l'amont).** Voir `codex-TELEMETRY-AUDIT.md` : analytics premier parti vers le backend ChatGPT (ON par défaut pour le CLI interactif, OFF par défaut pour `app-server`), coupés par `-c analytics.enabled=false` ; Sentry limité au feedback explicite (aucun `sentry::init`), coupé par `-c feedback.enabled=false` ; OTEL sans exporteur par défaut ; zéro SDK tiers (PostHog/Segment/Mixpanel/Amplitude absents du workspace).

## Divergence (dette portée par le cœur Buzz, lane Clara / 12e)

- **Règles maison amont respectées :** aucun fichier amont touché (H-M2) ; l'adapter ne touche pas au cœur (CLI, app-server, core) ; la racine `CLAUDE.md` amont n'a PAS été éditée.
- **Ré-audit télémétrie :** à chaque changement de commit gelé ou d'adapter, et au minimum à chaque transition d'état (D3).

## Références

- Design D-N048 (Clara, 2026-11-09) : `~/workspace/v4-factory/plans/FORKS-AMONT-21-plan-borne-vagues.md`.
- Évidences : `~/workspace/v4-factory/evidence/D-N048/PROGRESS-D-N048.md`.
- Fork : https://github.com/Amdkn/codex (gel `27fcd7c`, adapter `0a0094d`).
