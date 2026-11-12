# Jugement 13e — D-N053 pas F1 : herdr + herdr-core, état 0 → 1

**Juge :** 13e Doctor (fonction de jugement, indépendante — ni l'exécutant Ryan, ni le coordinateur).
**Date :** 2026-11-12 ~16:30 EST.
**Objet :** PR #45 du repo `Amdkn/Aspace_OS_V5`.

## Verdict

**VALIDÉE AVEC RÉSERVES — merge OUI.**

- **Tête autorisée :** `7a821c7` (`7a821c775e4ae836764f7aad947f42560a533eb0`), seule tête sur laquelle le merge est autorisé.
- **Merge :** true merge (2 parents, DVG-01), jamais par le runner, jamais par le juge.
- **Amendements :** aucun (C1… : néant). Les deux réserves ci-dessous sont des suivis hors PR, pas des conditions de merge.
- **Décision du coordinateur sur H-F1-3 : ACCEPTÉE** (voir §5).

## 1. PR #45 re-vérifiée à l'API (2026-11-12 ~16:30 EST)

| Fait | Vérifié |
|---|---|
| État | OUVERTE |
| Tête | `7a821c7` = `7a821c775e4ae836764f7aad947f42560a533eb0` |
| Base | `master` ; parent unique du commit = `861a01f` = master actuel (vérifié à l'API ce tour) |
| Titre | « D-N053 pas F1 : herdr + herdr-core adaptés en Fibres Cordis (8L) — état 0 → 1 » |
| Commits | 1 ; message `feat(d-n053-f1): adapt herdr + herdr-core as Cordis Fibers (8L) — state 0 to 1` |
| Mergeable | `true`, `mergeable_state: clean` |
| Fichiers | 8 (+216 / −5) : 2 fiches + 2 audits + 2 manifestes ajoutés, gitlink `herdr` modifié, `FUSIONS-REGISTRY.md` modifié |
| Autres PR ouvertes V5 | **0** — seule la #45 est ouverte |

## 2. CI re-vérifiée à l'API sur la tête `7a821c7`

**8/8 check-runs `completed` / `success`** : CodeQL ; Verify Category 01_Kernel_Gates ; Verify Category 02_Holons_578_QualityControl ; Verify Category 03_Submodules_EGM_Harvester ; Verify Category 04_Security_OWASP_RigInfinity ; S1-RICK & Reviewer-Security · OWASP Top 10 & Worktree Patch ; Deterministic Gate (5D Semantic AST + CAS Holons + 7R + OKF) ; Analyze (actions).

## 3. Pins, binds et forks re-vérifiés à l'API

| Fait | Vérifié |
|---|---|
| herdr-core adapter `d50ebd8` (`d50ebd80858f65a819614cfbf336e48df82acef1`) | parent = gel `cd12ddd88bc11490228343291dc1096c9ed3bf77` ✓ ; diff gel→adapter = **1 commit, 12 fichiers adapter seuls** (`aspace-herdr-core-adapter/`, ajouts uniquement, aucun fichier amont touché) |
| herdr-core bind `be144c8` (`be144c877dbaf1d71c307550445b35129e48827d`) | parent = adapter `d50ebd8` ✓ ; 1 fichier (`aspace-plugin.json`, 24 lignes) ; blob `d63a37095734c9a6848ae2e05154102474281ba0` **byte-identique** au bind `14a3772` sur `aspace-v5-native` (même SHA, même taille 892 o) |
| herdr-core fork master | = `be144c8` ✓ ; fork non archivé, branche défaut `master` |
| herdr adapter `2387c8a` (`2387c8abbd2239079ee42f6163360f08585a7dcb`) | parent = gel `ee5bfb5041bb3e4a49d591c72308aae3c81ecdde` ✓ ; diff gel→adapter = **1 commit, 4 fichiers adapter seuls** (`aspace-herdr-adapter/`, ajouts uniquement) |
| herdr bind `637cc7b` (`637cc7b44066ad937a34c2356ab2b4f55ff8f8b1`) | parent = adapter `2387c8a` ✓ ; 1 fichier (`aspace-plugin.json`, 24 lignes) ; blob `50477df4ad8c8a475290ae25a58022e54e44243f` **byte-identique** au bind `df9b626` sur `aspace-v5-native` (même SHA, même taille 877 o) |
| herdr fork master | = `637cc7b` ✓ ; fork non archivé, branche défaut `master` |
| Pin = commit adapter | conforme au patron tranché journal 587 (§0 du design) |

## 4. Harnais rejoué indépendamment

Rejeu de `harness-pas-f1.py` par le juge sur une copie de l'évidence (`/tmp/f1-juge`, pour ne pas écraser `RESULTS-D-N053-F1.json`) contre le clone de la tête PR (`/tmp/v5-pr45`, HEAD `7a821c7` vérifié) : **32/34 PASS — les mêmes 2 FAIL que le rapport de l'exécutant** (`H-F1-3/herdr-baseline-verte`, `H-F1-3/herdr-adapte-verte`), aucune divergence de chiffres.

Vérifications du harnais rejouées une à une (détail au §6) : H-F1-1 (gitlink herdr = `2387c8a` ; herdr-core absent de `.gitmodules` — 0 occurrence, vérifié au clone de la tête ; manifestes : adapters `d50ebd8`/`2387c8a`, gels `cd12ddd`/`ee5bfb5`) ; H-F1-2 (diffs adapter-seuls, §3) ; H-F1-3 (chiffres ci-dessous) ; H-F1-4 (audits 2 970 o / 3 567 o, « 0 appel sortant par défaut ») ; H-F1-5 (`fiber:a0:herdr-core`, `fiber:a0:herdr`, `levels.current = 0`, sans doublon, herdr-app distincte) ; H-F1-6 (daemon exclu, couture nommée, divergence + cœur Buzz) ; H-F1-7 (fiches complètes : gel, licence, audit, divergence, socket réel, 31415, triage 53, ghostty) ; H-F1-8 (compteur 3 → 1, paragraphe Pas F1, pins au registre, orca état 0).

## 5. Décision du coordinateur sur les 2 rouges — ACCEPTÉE

Le design (§4, H-F1-3) dispose : « Un test rouge bloque la montée d'état (sauf exclusion décidée par le coordinateur, liste exacte consignée). » La décision du coordinateur (`DECISION-COORDINATEUR-H-F1-3.md`, 2026-11-12 ~16:20 EST) exclut exactement les 2 rouges du harnais. Le juge les a re-vérifiés indépendamment, à la source et aux logs, et **confirme l'exclusion** :

### Rouge 1 — ghostty-vt `snapshot_is_independent_and_preserves_borrowed_fd_offset_when_supported`

- **Identique baseline vs adapté** : 1 échec dans les deux runs, mêmes chiffres globaux 384/4/2 (18 binaires), même nom de test (4 occurrences dans chaque log).
- **Cause prouvée au strace** (`logs-strace-ghostty-vt-snapshot.log`) : `ioctl(4, BTRFS_IOC_CLONE_RANGE or FICLONERANGE, …) = -1 EPERM (Operation not permitted)` — FileStore sous `/var/tmp` (tmpfs), reflink refusé par l'environnement.
- **Vérifié au code vendu au gel** (juge, lecture directe de `crates/ghostty-vt/src/pane_graphics_files.rs` au gel `ee5bfb5`, lignes ~728–738) : la liste de repli du test n'accepte que `EOPNOTSUPP | ENOTTY | EXDEV | EINVAL | ENOSYS` — **EPERM n'y figure pas**. L'échec est donc mécanique dès que l'environnement répond EPERM, et le code est vendu (`vendor/libghostty-vt`), non touché par l'adapter (diff adapter-seul, §3).
- **Conclusion :** défaut pré-existant au gel, cause environnementale, 0 imputable à l'adapter. Exclusion acceptée.

### Rouge 2 — `herdr --bin herdr` (main.rs, 3755 tests) incomplet, SIGPIPE

- **Identique baseline vs adapté** : les deux logs portent la même ligne — `process didn't exit successfully: …/herdr-2bc49dd626f7b03c (signal: 13, SIGPIPE)` — **même binaire, même hash `2bc49dd626f7b03c`, même point de mort**, sans ligne « test result » des deux côtés.
- **Re-run série vérifié au fichier** (`logs-suite-adapte-main-rs-rerun.log`) : comptage exact par le juge — **3 141 tests `ok`, 1 seul `FAILED`** : `writable_directory_does_not_bypass_read_only_config`. Cet échec unique est un artefact root (la VM tourne en root ; le noyau ignore le bit read-only que le test veut faire respecter) — pré-existant au gel.
- Les 3 autres échecs main.rs vus en parallèle côté adapté ne se reproduisent pas en série (flakes de charge) ; les 3 `live_handoff` sont 24/24 en série des deux côtés (vérifié : `test result: ok. 24 passed; 0 failed` dans les deux logs de re-run).
- **Conclusion :** run incomplet pré-existant au gel, 0 régression (binaire byte-identique). Exclusion acceptée.

**Ce qui n'est pas exclu** (vert des deux côtés, vérifié) : herdr-core consolidé 158/0/1 (voir §6) ; herdr maintenance Python 150 OK ; bun release-workflows 5/5 ; docs-contract 7/7 ; smokes verts (`SMOKE_EXIT:0` ×2) ; preuve client H-F1-3 verte.

## 6. Vérifications sensibles rejouées par le juge

**(a) Les 2 rouges identiques baseline vs adapté** — établi au §5 (mêmes chiffres, même binaire hash `2bc49dd626f7b03c`, strace EPERM). ✓

**(b) Preuve client H-F1-3 réelle** — lue au code source du fork (adapter `d50ebd8`) : `tests/protocol_roundtrip.rs` (4 tests : round-trip trames `hello` canal 0, round-trip plain-mode `client::call` `server.status`, constantes, socket par défaut) et `protocol-proof/` (binaire autonome). Log d'exécution vérifié : `logs-adapter-build-test.log` — 4/4 `ok` (`framed_jsonrpc_roundtrip_on_channel_zero`, `plain_mode_client_call_roundtrip`, `adapter_constants_are_the_f1_pins`, `default_socket_is_under_xdg_runtime_dir`), `TEST_EXIT:0`. Smoke log : « protocol-proof OK: hello plain (framed:true) -> framed server.status round-trip on channel 0 » + « wire HEADER=9 MAX_PAYLOAD=16MiB WINDOW=256KiB, notes=false read by the library, require_existing fails cleanly with no server ». Contre stub local UnixStream, jamais contre un serveur `hc` V5 ni `releases.herdr.dev`. Preuve réelle, pas déclarative. ✓

**(c) Télémétrie zéro** — interrupteurs vérifiés **au fichier source du fork**, pas seulement à la fiche : `aspace-herdr-core-adapter/config.toml` porte `notes = false` ; `aspace-herdr-adapter/config.toml` porte `[update] version_check = false` + `manifest_check = false`. Audits lus en entier (T1–T8 tous tranchés ; herdr : seul faux positif `segment_index`, 0 SDK). Captures strace vérifiées : herdr-core 1 `connect()` AF_UNIX local (ENOENT, sans serveur), 0 `AF_INET` ; herdr 0 `connect()`, 0 `socket()` (log `logs-strace-adapte.log` : 3 lignes de sortie uniquement, aucune syscall réseau). ✓

**(d) Gitlink herdr-core absent de `.gitmodules`** — vérifié au clone de la tête PR : `grep -c herdr-core .gitmodules` = 0 ; `git ls-files -s` ne liste aucun gitlink herdr-core (seul `herdr` = `2387c8a`). Acte F8 maintenu. ✓

**(e) Compteur registre 3 → 1** — vérifié au clone de la tête : ligne 148 (compteur global 25 → 1), ligne 186 (paragraphe « Pas F1 », « compteur 3 → 1 »), table lignes 171–173 : herdr état 1 pin `2387c8a`, herdr-core état 1 pin `d50ebd8`, **orca état 0 pin `b659760` (F2)**. ✓

**(f) Correction de fait « lib.rs 35 modules pub, pas 30 »** — vérifiée au fichier amont au gel : `crates/herdr-core/src/lib.rs` @ `cd12ddd` porte **35** `pub mod` (liste complète relevée : addr, api, attach, cli, client, config, events, exec, files, foreground, holder, holder_proto, input, keys, locale, machines, notes, paths, picker, platform, put, relay, releases, remote, rpc, runtime, server, status, stitch, sweep, templates, terminals, viewers, wait, wire). L'adapter en ré-exporte 33 (liste relevée au fichier : les 35 moins `server` et `cli`) — `contract.json` confirme `lib_rs_pub_modules_upstream: 35`, `reexported_modules: 33`, `excluded_modules: [server, cli]`, `never_used: [client::connect_or_start, client::connect_or_start_explicit, client::spawn_core]`. Le design est périmé sur ce point ; la fiche corrige à raison. ✓

**(g) Formes des adapters, daemon jamais revenu** — vérifié au code source du fork : `src/lib.rs` adapter (doc : client seul, `server` et `cli` exclus) ; `src/bin/hc.rs` utilise `client::require_existing` (jamais `connect_or_start`), `ServerCmd` = Status/Stop/Restart seulement, pas de `server start`, pas de `update`, pas de `serve`, pas de `hold` (clap les rejette) ; `contract.json` herdr-core : `excluded: [hc server start, hc update, hc serve, hc hold]`, `form: [library, client-cli]` ; `contract.json` herdr : `form: [cli-contract]`, `library: null`, `excluded: [herdr update, herdr plugin update, any launch of a herdr server by V5]`. herdr = CLI-contrat seul (pas de `lib.rs`, E-F1-9) ; herdr-core = bibliothèque + CLI cliente `hc` sans serveur. Le daemon `hc` n'est réintroduit nulle part. ✓

**Chiffres herdr-core re-comptés par le juge aux logs** : baseline 157/1/1 (échec unique `a_machine_of_another_cpu_gets_the_released_build_for_it`, « timed out waiting for added », fenêtre 10 s fixe — timing pré-existant) ; adapté brut 152/6/1 (dont distribution 2/6 en parallèle, ENOSPC `/tmp` tmpfs 512 Mo) + distribution série 8/8 → consolidé **158/0/1** (arithmétique : 152 − 2 + 8 = 158 ; détail 11 + 135 + 0 + 2 + 2 + 8). `fmt` EXIT:0 et `clippy -- -D warnings` EXIT:0 en baseline et sur l'adapté (vérifiés aux logs). ✓

**Chiffres herdr re-comptés par le juge aux logs** : baseline 384/4/2 = adapté 384/4/2, test pour test ; 0 régression. ✓

## 7. Réserves (suivis hors PR, non bloquantes)

- **R1 — Diagnostic SIGPIPE incomplet.** La cause racine de la mort en SIGPIPE du binaire main.rs reste indiagnostiquée (« interaction inter-tests », diagnostic arrêté par l'exécutant). Elle est pré-existante au gel et identique des deux côtés, donc elle ne bloque pas l'état 1, mais elle doit être fermée en suivi : re-courir main.rs en utilisateur non-root (pour purger aussi l'artefact `writable_directory`) et identifier le test fautif, au pas F2 ou sur une machine adéquate. Le pas F1 ne porte pas cette dette en silence : elle est consignée ici.
- **R2 — Phrase du registre à compléter au reçu.** La ligne 186 du registre dit encore « décision attendue du coordinateur » : la décision existe désormais (`DECISION-COORDINATEUR-H-F1-3.md`) et est confirmée par le présent jugement. Le coordinateur la consignera dans le reçu R10 du pas (références décision + jugement), sans rouvrir la PR — aucune modification de la tête `7a821c7` n'est exigée pour ce point.

## 8. Conformité au design signé Clara

- D-F1-1 (formes séparées) ✓ ; D-F1-2 (voie `hc` = bibliothèque cliente, serveur herdr opérateur-externe, aucun nouveau client natif) ✓ ; D-F1-3 (herdr-core d'abord, herdr ensuite — ordre documentaire respecté) ✓ ; D-F1-4 (gel tenu `cd12ddd`, triage des 53 versé en fiche, revisite 3 jours) ✓ ; D-F1-5 (interrupteurs forcés, vérifiés au fichier) ✓ ; D-F1-6 (31415 qualifiée côté A'Space dans les deux fiches + `contract.json`, binds inchangés) ✓ ; D-F1-7 (bornes §4 respectées : deny exclu nommément, nextest repli acté, ui-hot-path / integration-assets / profils render_scale / Windows exclus) ✓ ; D-F1-8 (plafonds D12 — mesure au reçu du pas, hors périmètre du jugement).
- Suivis hors F1 nommés au design (S-F1-1 requalification H-P8-4, S-F1-2 en-tête AGPL `openrig_terminal.rs`, S-F1-3 revisite 3 jours) : non exécutés ici, à dispatcher — rappelés, non bloquants.
- H-F1-3 : non vert strict, **vert sous l'exclusion décidée par le coordinateur et confirmée par le juge** (§5). Tous les autres hold-outs H-F1-1..H-F1-8 sont verts.

## 9. Ce que le juge n'a pas fait

Ni merge, ni modification de la PR, ni écriture sur les forks. Le harnais a été rejoué sur des copies (`/tmp/f1-juge`, `/tmp/v5-pr45`, `/tmp/hc-check`) ; l'évidence d'origine est intacte.

---
*Jugement 13e — D-N053 pas F1 — 2026-11-12 ~16:30 EST. Verdict : VALIDÉE AVEC RÉSERVES, merge OUI, tête autorisée `7a821c7`.*
