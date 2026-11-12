# Fiche d'adaptation — herdr (D-N053 pas F1)

**Adresse :** `fiber:a0:herdr`
**Manifeste :** `herdr.manifest.json` (même domicile)
**Audit télémétrie :** `herdr-TELEMETRY-AUDIT.md` (même domicile)
**Statut :** état 1 Adapté (pas F1, PR V5 à juger par le 13e)
**Licence :** Apache-2.0

## Commit gelé

- **Fork :** `Amdkn/herdr` (parent `herdrdev/herdr`, Apache-2.0, branche `master`).
- **Gel : `ee5bfb5`** — version 0.9.5, 2026-10-29.
- **Dérive au gel : 0** (gel = amont HEAD au moment du fork).
- **Tout commit amont ultérieur exige un amendement de design**, jamais un fast-forward silencieux (D-F1-4).

## Adapter

- **Dossier :** `aspace-herdr-adapter/` (README + contrat JSON + config embarquée + smoke test shell), commit **`2387c8a`** sur le fork (parent = gel `ee5bfb5`, vérifié à l'API). **Seul code A'Space du fork** — le code amont est byte-identique au gel (H-F1-2). Bind re-appliqué verbatim au-dessus (`637cc7b`, `aspace-plugin.json` 24 lignes, byte-identique au bind `df9b626`) ; **pin = commit adapter `2387c8a`**.
- **Forme (D-F1-1) — CONTRAT CLI SEUL, patron herdr-app :** herdr est un binaire seul, pas de `lib.rs` (E-F1-9) — l'adapter est un contrat, pas une bibliothèque. Surface : `herdr --help` / `--version`, `herdr server stop|reload-config|reload-agent-manifests`, commandes panes/workspaces/tabs, sessions, terminal, agent, machine, `herdr config check`. API machine via `herdr.sock` NDJSON (schéma `docs/next/api/herdr-api.schema.json`, 10 759 lignes, enveloppe `{id, method, params}` → `{id, result}`, PAS JSON-RPC 2.0).
- **Le serveur herdr reste un serveur de l'opérateur, externe à V5 (D-F1-2) :** V5 ne lance ni ne supervise aucun serveur herdr ; l'adapter ne fait que parler au serveur déjà en cours, côté opérateur. Aucun lancement de serveur par V5 dans la surface.
- **Interrupteurs forcés (D-F1-5, H-F1-4) :** `[update] version_check = false` + `[update] manifest_check = false` — config embarquée `aspace-herdr-adapter/config.toml`, vérifiées au fichier ET par le binaire lui-même (`herdr config check` → `config: ok` avec `HERDR_CONFIG_PATH` sur la config embarquée). Défauts amont : `true` (`src/config/model.rs:43-44`). Endpoints neutralisés par ces interrupteurs : `herdr.dev/latest.json`, `herdr.dev/preview.json`, `formulae.brew.sh/api/formula/herdr.json`, `herdr.dev/agent-detection/index.toml` (intervalle 30 min).
- **Couture herdr ↔ herdr-core (E-F1-3) :** 0 lien de code inventé — les deux repos sont deux produits séparés à ces pins. La couture nommée est (a) la bibliothèque adapter herdr-core comme client du protocole encadré `hc`, (b) l'adapter CLI-contrat herdr comme client du socket herdr NDJSON. Le natif consomme les deux voies séparément (D-F1-2).
- **Revendication 31415 (D-F1-6) :** le bind revendique `universal_harness_gateway_31415` + `http://127.0.0.1:31415/v1/chat/completions` — qualifiée côté A'Space (FreeCloud, `aspace_freecloud_gateway.py`), pas une capacité du gel. Bind re-appliqué verbatim, non modifié au pas F1.
- **Smoke test :** `bash aspace-herdr-adapter/smoke_test.sh` (build debug du binaire, `--version` 0.9.5, `--help`, `server --help` sans contacter de serveur, `herdr config check` sur la config embarquée, exclusion contractuelle de `update` / `plugin update` de la surface). Ne lance jamais de serveur herdr, ne touche jamais la vraie config (`HERDR_CONFIG_PATH` sur copie scratch).
- **Règles maison amont respectées (AGENTS.md) :** commits lowercase conventional, pas de ligne AI co-author ; `just` absent de la VM (python/bun/cargo directs, repli acté) ; aucune modification du code amont, aucun `docs/next/CHANGELOG.md`, aucun fichier de release touché. Le travail se fait dans le fork Amdkn, pas vers l'amont canonique — la guardrail « external contributor » ne s'applique pas ici (pas de PR ni d'issue vers `herdrdev/herdr`).

## Tests au gel et sur le fork adapté

- **Au gel `ee5bfb5` :** `cargo test --locked` (repli acté, `cargo-nextest` absent) + `maintenance-test` (Python, `python3 -m unittest`, 13 modules) + `docs-contract-test` (`bun test ./scripts/docs`) + `bun test scripts/release-workflows.test.ts`. Résultat consolidé (voir `logs-suite-baseline-gel.log` — run `--no-fail-fast`, tous les binaires — + `logs-suite-baseline-gel-live-handoff-rerun.log`, `logs-suite-adapte-main-rs-rerun.log`, `logs-suite-adapte-main-rs-skip1.log`) :
  - **18 binaires sur 19 : 384 passés, 4 échecs bruts, 2 ignorés.** Les 3 `live_handoff` (« empty response from …/herdr.sock » au 1er `workspace.create`) sont une course au démarrage du serveur sous 1,5 CPU en parallèle — **24/24 en série** (`--test-threads=1`, ordonnancement seul). Reste **1 échec : `ghostty-vt` (`snapshot_is_independent_and_preserves_borrowed_fd_offset_when_supported`)** : `ioctl FICLONERANGE → EPERM` prouvé au strace (`logs-strace-ghostty-vt-snapshot.log`) — le FileStore vit sous `/var/tmp` (tmpfs 2 Go), le reflink y est refusé par l'environnement, et la liste de repli du test n'accepte pas EPERM (EOPNOTSUPP/ENOTTY/EXDEV/EINVAL/ENOSYS seulement). Échec pré-existant au gel, dans du code vendu (`vendor/libghostty-vt`), cause environnementale prouvée. **Non corrigé** (règle adapter-seul + code vendu) et **non exclu de ma propre initiative** — décision du coordinateur à demander (H-F1-3, liste exacte consignée ici).
  - **19e binaire, `herdr --bin herdr` (main.rs, 3755 tests) : INCOMPLET des deux côtés — il meurt en SIGPIPE (signal 13) avant la fin, sans ligne « test result », en baseline comme en adapté (même binaire, même hash `2bc49dd626f7b03c`, même point de mort).** En série : **3141 tests ok avant la mort, 1 seul échec** — `writable_directory_does_not_bypass_read_only_config` (artefact root : la VM tourne en root, le noyau ignore le bit read-only que le test veut faire respecter ; pré-existant au gel). Les 3 autres échecs main.rs vus en parallèle côté adapté (`config_publication_keeps_old_content_until_commit`, `config_metadata_preserves_ownership_and_acl_without_inheriting_extra_access`, `closed_agent_listener_does_not_block_a_live_replacement`) ne se reproduisent PAS en série — flakes de charge parallèle, pas une régression (le binaire est byte-identique entre baseline et adapté). Le SIGPIPE est une interaction inter-tests (le test où meurt le run passe seul ; le run meurt pendant le test suivant après un `--skip`) — diagnostic arrêté là : cause amont pré-existante, hors périmètre adapter, à trancher par le coordinateur (exclusion ou acceptation du rouge, liste exacte ici).
  - **maintenance Python 150 tests OK** ; **release-workflows 5/5** ; **docs-contract 7/7** (voir `logs-maintenance-test-baseline.log`, `logs-release-workflows-test-baseline-rerun.log`, `logs-docs-contract-test-baseline.log`). Profils `render_scale_profile`, tests Windows, `ui-hot-path-architecture-test`, `integration-assets-test` exclus (design §4).
  - Le run 1 s'était arrêté au 1er binaire en échec (fail-fast par défaut de `cargo test`) — le run complet est en `--no-fail-fast` (mêmes tests, tous les binaires). Le test bun `release-workflows` échouait d'abord (4/5) parce que `just` est absent de la VM (`spawnSync("just")` → status null) — `just` 1.59.0 installé (`cargo install just --locked`), re-run 5/5, suite inchangée.
- **Sur l'adapté `2387c8a` :** même suite + smoke adapter vert (voir `logs-suite-adapte.log`, `logs-suite-adapte-live-handoff-rerun.log`, `logs-smoke-adapte.log`, `logs-strace-adapte.log`). Résultat : **18 binaires 384 passés / 4 échecs bruts** (identiques à la baseline : 1 ghostty-vt EPERM + 3 live_handoff, 24/24 en série) ; **main.rs toujours incomplet en SIGPIPE** (même binaire byte-identique, même point de mort) avec 3141 ok / 1 échec artefact root en série ; **maintenance Python 150 OK, release-workflows 5/5, docs-contract 7/7** (voir `logs-maintenance-test-adapte.log`, `logs-docs-contract-test-adapte.log`). **0 régression : les chiffres adaptés sont identiques aux chiffres baseline, test pour test.**
- **Limite franche (environnement) :** Zig 0.16.0 installé manuellement (`~/workspace/.tmp/zig-x86_64-linux-0.16.0`, build.rs de `ghostty-vt` l'exige) ; le client HTTP de zig ne passe pas le proxy de la VM (400) — `uucode` et `iterm2-themes` téléchargés avec `curl` puis mis en cache par `zig fetch` local. La VM n'a que 6 Go de RAM et 1,5 CPU : les builds lourds se font SEULS, `CARGO_BUILD_JOBS=1` (un run à `JOBS=2` a été tué SIGKILL OOM pendant la compilation de la crate `herdr`). Quota disque saturé une fois pendant le pas (EDQUOT 122, ~50 Go de `target/` périmés supprimés, dépôts intacts). `/tmp` est un tmpfs de 512 Mo non redimensionnable (`mount` refusé, user namespace) — les suites qui téléchargent ~110 Mo par test en parallèle y échouent en ENOSPC ; voir la fiche herdr-core pour le diagnostic complet (`--test-threads=1` = ordonnancement seul, jamais une réduction de suite).

## Télémétrie

**Zéro appel sortant par défaut.** Voir `herdr-TELEMETRY-AUDIT.md` : aucun SDK de télémétrie, aucune crate HTTP ; tout le réseau passe par `curl` en sous-processus (chemin `update` uniquement, hors contrat) ou par SSH. `product-announcement.json` = `null`. `zbus`/logind = D-Bus local. Capture réseau (strace des chemins du smoke) : **0 `connect()`, 0 `socket()`** (`logs-strace-adapte.log`).

## Divergence (dette portée par le cœur Buzz, lane Clara / 12e)

- **Règles maison amont respectées (AGENTS.md) :** la racine `AGENTS.md` amont n'a PAS été éditée (H-M2) ; l'adapter ne touche pas au cœur.
- **Ré-audit télémétrie :** à chaque changement de commit gelé ou d'adapter, et au minimum à chaque transition d'état (D3).
- **Dette de divergence :** 0 au gel — toute dérive future exige un amendement de design (D-F1-4).
- **Hors périmètre (suivis séparés) :** S-F1-1 (requalification PTY H-P8-4), S-F1-2 (en-tête AGPL de `openrig_terminal.rs`).

## Références

- Design pas F1 signé Clara (2026-11-12) : `~/workspace/v4-factory/plans/DESIGN-D-N053-PAS-F1-PROJET.md`.
- Discover pas F1 de Bill : `~/workspace/v4-factory/evidence/D-N053/f1/DISCOVER-PAS-F1.md`.
- Évidences : `~/workspace/v4-factory/evidence/D-N053/f1/herdr/`.
- Fork : https://github.com/Amdkn/herdr (gel `ee5bfb5`, adapter `2387c8a`, bind `637cc7b`).
