# Rapport — D-N053 pas F1 : herdr + herdr-core, état 0 → 1

**Exécutant :** Ryan (Factory). **Design :** signé Clara, 2026-11-12 ~14:10 EST
(`~/workspace/v4-factory/plans/DESIGN-D-N053-PAS-F1-PROJET.md`).
**Discover :** Bill (`~/workspace/v4-factory/evidence/D-N053/f1/DISCOVER-PAS-F1.md`).
**Branche :** `a0/dn053-pas-f1`, base master `861a01f` (re-vérifié à l'API avant usage).
**Commit d'intégration :** `7a821c7` (1 commit : 2 manifestes + 2 fiches + 2 audits +
gitlink herdr + registre). **PR V5 :** à ouvrir (voir fin de rapport).
**Harnais :** `harness-pas-f1.py` → `RESULTS-D-N053-F1.json`.

## Livrés

| Module | Gel | Adapter (pin) | Bind re-appliqué | Manifeste | État |
|---|---|---|---|---|---|
| herdr-core | `cd12ddd` (v0.1.18+10) | `d50ebd8` (12 fichiers) | `be144c8` (byte-identique) | `fiber:a0:herdr-core` | 0 → 1 |
| herdr | `ee5bfb5` (v0.9.5) | `2387c8a` (4 fichiers) | `637cc7b` (byte-identique) | `fiber:a0:herdr` | 0 → 1 |

- Commits vérifiés à l'API : adapter parent = gel, fichiers adapter seuls ;
  bind parent = adapter, `aspace-plugin.json` 24 lignes byte-identique.
  (Leçon d'atelier : les deux clones étaient en HEAD détachée — le premier
  push a dit « up-to-date » sans rien pousser ; les commits ont été remis
  sur `master` avant push. Vérifier la branche, pas seulement le SHA.)
- herdr-core : vraie crate (`lib.rs` 33/35 modules pub — le « 30 » du design
  est périmé, vérifié au fichier — + binaire `hc` client ; `server` et `cli`
  exclus). `notes = false` forcé. Preuve client H-F1-3 : round-trip trames +
  JSON-RPC canal 0 contre stub local (`protocol-proof` + 4 tests).
- herdr : contrat CLI seul (patron herdr-app, pas de `lib.rs`).
  `[update] version_check = false` + `manifest_check = false` forcés,
  vérifiés par `herdr config check` sur le binaire adapté.
- Gitlink herdr re-pointé sur l'adapter (`2387c8a`) ; gitlink herdr-core
  RESTE absent (acte F8 maintenu, H-F1-1). Registre : compteur **3 → 1**,
  table + paragraphe « Pas F1 », F9 Mesures : « 2 modules ADE en état 1 (pas F1) ».

## Suites — baseline au gel vs adapté

### herdr-core — VERT (consolidé 158/0/1)

| Suite | Baseline `cd12ddd` | Adapté `d50ebd8` |
|---|---|---|
| `cargo test --locked` | 157 passés / 1 échec / 1 ignoré | 158 passés / 0 échec / 1 ignoré |
| `fmt` | vert | vert |
| `clippy -- -D warnings` | vert | vert |
| smoke adapter + preuve protocole | — | vert (`SMOKE_EXIT:0`, `protocol-proof OK`) |
| strace smoke | — | 1 `connect()` Unix local, 0 `AF_INET` |

L'échec baseline est `a_machine_of_another_cpu_gets_the_released_build_for_it`
(« timed out waiting for added », fenêtre 10 s fixe) : avec la fenêtre portée
à 120 s (patch diagnostic temporaire, reverté), il passe en 22,89 s — flux
`machine add` fonctionnel, juste plus lent que 10 s sur cette VM. En série
(`--test-threads=1`), le binaire `distribution` passe 8/8. Diagnostic de
charge : en parallèle, les 8 tests téléchargent chacun ~110 Mo dans `/tmp`
(tmpfs 512 Mo, non redimensionnable — `mount` refusé, user namespace) et
`tar` échoue en ENOSPC ; `Session::program` fait `env_clear()`, donc
`TMPDIR` ne propage pas aux enfants. `--test-threads=1` = ordonnancement
seul, jamais une réduction de suite.

### herdr — NON VERT STRICT (2 rouges pré-existants au gel, 0 imputable à l'adapter)

| Suite | Baseline `ee5bfb5` | Adapté `2387c8a` |
|---|---|---|
| `cargo test --locked` (18 binaires avec résultat) | 384 passés / 4 échecs bruts / 2 ignorés | 384 passés / 4 échecs bruts / 2 ignorés |
| `cargo test --locked` (19e binaire main.rs) | incomplet (SIGPIPE) | incomplet (SIGPIPE) |
| maintenance-test Python | 150 tests OK | 150 tests OK |
| `bun test scripts/release-workflows.test.ts` | 5/5 (après install `just`) | 5/5 |
| docs-contract-test | 7/7 | 7/7 |
| smoke adapter | — | vert (`SMOKE_EXIT:0`) |
| strace smoke | — | 0 `connect()`, 0 `socket()` |

**Les 2 rouges, liste exacte (décision du coordinateur à demander — rien
exclu de ma propre initiative, H-F1-3) :**

1. **`ghostty-vt` — `pane_graphics_files::tests::snapshot_is_independent_and_preserves_borrowed_fd_offset_when_supported`** (1 échec, baseline ET adapté, identique).
   Cause prouvée au strace (`logs-strace-ghostty-vt-snapshot.log`) :
   `ioctl FICLONERANGE → EPERM` — le FileStore vit sous `/var/tmp` (tmpfs
   2 Go), le reflink y est refusé par l'environnement ; la liste de repli
   du test n'accepte pas EPERM (EOPNOTSUPP/ENOTTY/EXDEV/EINVAL/ENOSYS
   seulement). Code vendu (`vendor/libghostty-vt`), non touché.
2. **`herdr --bin herdr` (main.rs, 3755 tests) — INCOMPLET : meurt en SIGPIPE
   (signal 13) avant la fin, sans ligne « test result », baseline ET adapté
   (même binaire, même hash `2bc49dd626f7b03c`, même point de mort).**
   En série : 3141 tests ok avant la mort, 1 seul échec —
   `writable_directory_does_not_bypass_read_only_config` (artefact root :
   la VM tourne en root, le noyau ignore le bit read-only que le test veut
   faire respecter). Les 3 autres échecs main.rs vus en parallèle côté
   adapté (`config_publication_keeps_old_content_until_commit`,
   `config_metadata_preserves_ownership_and_acl_without_inheriting_extra_access`,
   `closed_agent_listener_does_not_block_a_live_replacement`) ne se
   reproduisent PAS en série — flakes de charge parallèle. Le SIGPIPE est
   une interaction inter-tests (le test où meurt le run passe seul ; le run
   meurt pendant le test suivant après un `--skip`) — diagnostic arrêté là.

**Résolus en série (flakiness de charge, pas des défauts) :** les 3
`live_handoff` (« empty response from …/herdr.sock » au 1er
`workspace.create`) — 24/24 en série des deux côtés. Le test bun
`release-workflows` échouait d'abord (4/5) parce que `just` est absent de
la VM (`spawnSync("just")` → status null) — `just` 1.59.0 installé
(`cargo install just --locked`), re-run 5/5, suite inchangée.

**0 régression :** les chiffres adaptés sont identiques aux chiffres
baseline, test pour test, sur les deux modules (binaires byte-identiques :
le test binaire herdr `2bc49dd626f7b03c` est le même au gel et sur l'adapté).

## Télémétrie — zéro appel sortant par défaut (les deux modules)

- Scans statiques propres (0 occurrence `telemetry|analytics|posthog|sentry|
  segment` dans le Rust ; 0 crate `reqwest`/`ureq`/`hyper`/`curl` dans les
  `Cargo.lock`) ; réseau = `curl` en sous-processus (chemin `update` manuel
  seulement) ou SSH. `product-announcement.json` = `null` (herdr).
- Audits versionnés au domicile V5, chaque déclencheur du Discover §6
  tranché (T1–T8). Captures strace : herdr-core 1 `connect()` Unix /
  0 `AF_INET` ; herdr 0 `connect()` / 0 `socket()`.

## Corrections de faits du design (signalées avec preuves)

- `lib.rs` herdr-core porte **35 modules `pub`**, pas 30 (le design est
  périmé sur ce point) — l'adapter en ré-exporte 33 (hors `server`, `cli`).
- L'identité git locale diffère entre les deux forks (herdr-core : `Ryan
  Factory (A'Space V4)` ; herdr : `Aspace Factory`) — cosmétique, commits
  conformes (lowercase conventional, pas de ligne AI co-author).

## Incidents d'environnement (et remèdes)

- **Quota disque plein (EDQUOT 122)** : ~50 Go de `target/` périmés
  supprimés (artefacts régénérables, dépôts intacts) ; volume 56 Go / 94 Go
  libres après ménage.
- **OOM (6–8 Go RAM, 1,5 CPU)** : ne jamais lancer 2 jobs cargo lourds en
  parallèle ; `CARGO_BUILD_JOBS=1` pour herdr.
- **`/tmp` tmpfs 512 Mo non redimensionnable** (`mount` refusé, user
  namespace) : les suites qui téléchargent ~110 Mo par test en parallèle y
  échouent en ENOSPC → `--test-threads=1` (ordonnancement seul).
- **`just` absent** → installé 1.59.0 (`cargo install just --locked`).
- **`zig` absent** → 0.16.0 manuel + `curl`/`zig fetch` local (400 via proxy VM).
- **Watchdog harnais herdr-core (30 s)** → `HC_TEST_WATCHDOG_S=600` (prévu
  par le harnais).

## Preuves (chemins)

- `~/workspace/v4-factory/evidence/D-N053/f1/herdr-core/` :
  `logs-suite-baseline-gel.log`, `logs-suite-adapte.log`,
  `logs-suite-adapte-distribution-rerun2.log`, `logs-adapter-build-test.log`,
  `logs-smoke-adapte.log`, `logs-strace-adapte.log`,
  `herdr-core-TELEMETRY-AUDIT.md`.
- `~/workspace/v4-factory/evidence/D-N053/f1/herdr/` :
  `logs-suite-baseline-gel.log` (run `--no-fail-fast` complet),
  `logs-suite-baseline-gel-live-handoff-rerun.log`,
  `logs-suite-adapte.log`, `logs-suite-adapte-live-handoff-rerun.log`,
  `logs-suite-adapte-main-rs-rerun.log`, `logs-suite-adapte-main-rs-skip1.log`,
  `logs-strace-ghostty-vt-snapshot.log`, `logs-maintenance-test-baseline.log`,
  `logs-maintenance-test-adapte.log`, `logs-docs-contract-test-baseline.log`,
  `logs-docs-contract-test-adapte.log`,
  `logs-release-workflows-test-baseline-rerun.log`,
  `logs-smoke-adapte.log`, `logs-strace-adapte.log`,
  `herdr-TELEMETRY-AUDIT.md`.
- `~/workspace/v4-factory/evidence/D-N053/f1/` : `harness-pas-f1.py`,
  `RESULTS-D-N053-F1.json`, `RAPPORT-PAS-F1.md` (ce fichier).
- Forks : https://github.com/Amdkn/herdr-core (master `be144c8`) ;
  https://github.com/Amdkn/herdr (master `637cc7b`).

## Décisions attendues du coordinateur

1. **H-F1-3 — exclusion des 2 rouges herdr** (liste exacte ci-dessus) ou
   acceptation du rouge : ghostty-vt EPERM + main.rs SIGPIPE incomplet.
   Sans décision, l'état 1 ne peut pas être revendiqué « suite verte ».
2. **H-F1-3 herdr-core** : vert consolidé, rien à décider.
