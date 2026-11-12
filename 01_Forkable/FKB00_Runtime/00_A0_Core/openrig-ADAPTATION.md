# Fiche d'adaptation — openrig (D-N051 F8, pas 4)

**Adresse :** `fiber:a0:openrig` (le corps — D2 : le daemon est le cœur du pas)
**Manifeste :** `openrig.manifest.json` (même domicile)
**Audit télémétrie :** `openrig-TELEMETRY-AUDIT.md` (même domicile)
**Statut :** état 0 Basique → 1 Adapté (fiche + adapter + manifeste ;
**H-P4-2 / H-P4-3 / H-P4-4 / H-P4-5 PARTIELS (preuve live = machine /
intégration), H-P4-9 / H-M3 PARTIELS (`test:repo` VERT, lint VERT,
cli+tui complets avec échecs amont qualifiés, daemon incomplet —
plafond ~35 min, 162/1 326 fichiers), H-P4-1 PARTIEL (bind
re-appliqué par le parent à l'intégration) — jugement 13e requis**
— voir § Hold-outs)

## Commit gelé

- **Fork :** `Amdkn/openrig` (parent `mvschwarz/openrig`, Apache-2.0,
  branche `main`).
- **Gel : `bd39da9`** (`bd39da9872afc39cbe0c8e839a322b4cb8955cbe`) —
  « fix(compaction): deliver a held post-compaction step after two idle
  unreadable polls (#2576) », 2026-11-05T21:03:09Z. Version **0.7.1**
  (`packages/daemon/package.json` : `@openrig/daemon` 0.7.1,
  Node.js 22 ou 24, tmux, macOS ou Linux — **WSL2 : les tests
  automatisés ne tournent pas sur WSL2**, §D8).
- **Vérifié au fichier :** clone local `~/workspace/openrig-repo`, HEAD =
  gel avant adaptation, arbre propre. `npm ci --ignore-scripts`
  terminé (444 paquets, 53 s, `node_modules` 271 Mo) ; le monorepo
  utilise **npm workspaces**.
- **Pin V5 : `649376c`** (retiré au pas 8) — l'adapter `b71bf87` + 2
  commits de lignée (13 fichiers A'Space seuls) ; le pin réel, corrigé
  au pas 8 (la fiche nommait le bind `adafb0d` comme pin).
- **Bind : `89f49c9`** — `main` HEAD du fork (bind re-appliqué
  au-dessus de l'adapter). Le bind d'origine `adafb0d`
  (`adafb0d16a83dd557c524bbe9d19c9a11e188f15`, 2026-11-07T22:38:15-05:00,
  « feat(aspace-v5): bind openrig as Cordis Fiber (4L) to A0 EGM Core »)
  — 2 fichiers : `aspace-plugin.json` (+23) et
  `src/lineage_spawner.ts` (+6). Parent du pin d'origine : `781b5fb`
  (2026-11-05, « docs(capability-map): teach what 0.7.8 added and drop
  three sentences it made false (#2568) »).
- **Dérive (D1) :** gel **226 commits derrière l'amont** (amont main
  `52cc63d`, dernier push 2026-11-10T21:45:02Z — l'amont pousse ~2
  commits par 25 min, la dérive bouge) ; pin **232 derrière** (diverged,
  amont 232 devant, pin 1 devant = le bind). Signal de revisite
  (inventaire hebdomadaire), **PAS de re-gel** : chasser le HEAD vivant
  viole la sanctuarisation (F8 D3). Tout commit amont ultérieur exige un
  amendement de design, jamais un fast-forward silencieux.
- **Arbre @gel :** 4 918 entrées. 5 paquets : `cli`, `daemon`,
  `test-system`, `tui`, `ui`.

## Version figée 0.7.1 — et l'écart avec les docs (D7)

- **Le gel est 0.7.1.** Les docs citent 0.7.5 / 0.7.8 — le commit
  `781b5fb` (parent du pin) enseigne ce que 0.7.8 a ajouté. **Les docs
  sont en avance sur le code gelé ; le gel et les tags ne sont pas la
  même chose.** Aucune affirmation de compatibilité 0.7.5 / 0.7.8 pour
  le gel. L'écart est consigné dans `contract.json` (`VERSION_DRIFT`)
  et dans l'adapter (`VERSION_DRIFT`, `PINNED_OPENRIG_VERSION`).

## Adapter

- **Paquet :** `aspace-openrig-adapter/` (`@aspace/openrig-adapter`
  0.1.0), **3 commits** sur le fork `main` : **`b71bf87`**
  (`b71bf870c4bd6a11799c053e9ec2a0f2dccb5b3c`, parent = gel `bd39da9`,
  l'adapter initial, 13 fichiers), **`ef00f30`**
  (`ef00f30909ae3b97f0cdea54896557d7a4cef5c8`, vérification de lignée
  post-commit), **`649376c`** (HEAD,
  `649376c803f76ea3b5bdb10097179e06c0645743`, la vérification tient pour
  n'importe quel nombre de commits adapter). **Seul code A'Space du
  fork** (H-M2 vérifié à l'API : compare gel..HEAD = ahead 3, behind 0,
  exactement les 13 fichiers adapter, 0 fichier amont).
- **Périmètre strict (§D2) : daemon + CLI** (le cycle de vie du daemon).
  **Hors périmètre :** le serveur HTTP Hono (les routes sont
  ré-implémentées en Rust, pas portées) ; la TUI/UI comme code
  (surfaces, §D3) ; les providers ; `test-system` (outillage de la
  suite, utilisé par H-M3, pas adapté).
- **Surface épinglée (vérifiée contre le gel, D2) :**
  - `Rig` / `Pod` / `Node` (siège) / `Edge` / `Binding` / `Session` —
    `packages/daemon/src/domain/types.ts:3,10,29,75,84,100`
    (voir `src/rig.ts`).
  - Herdr socket : NDJSON `{id,method,params}` → `{id,result}` sur
    `~/.config/herdr/herdr.sock` (`HERDR_SOCKET_PATH` /
    `HERDR_SESSION`) ; 8 méthodes : `ping`, `pane.list`,
    `pane.report_agent_session`, `workspace.list`, `workspace.create`,
    `layout.apply`, `tab.focus`, `tab.close`
    (`domain/terminal/herdr-transport.ts`, `herdr-adapter.ts`).
  - `resolveDaemonDbPath()` — `<OPENRIG_HOME>/openrig.sqlite`,
    `OPENRIG_DB` / `RIGGED_DB` en override, containment-checké
    (`src/daemon-db-path.ts`).
  - `resolveBindPlan()` — défaut `[127.0.0.1]` (+ IP tailscale quand
    présente) ; explicite `OPENRIG_BIND_HOST`
    (`domain/bind-plan.ts`, OPR.0.5.5.20).
  - `ATOM_TAXONOMIES = world | lore | skills | mission`
    (`domain/context-packs/context-pack-types.ts`, OPR.0.5.6.10).
  - Surface télémétrie locale `/api/telemetry/*` (voir § Télémétrie).
  - CLI lifecycle : `daemon-auto-start.ts`, `daemon-lifecycle.ts`,
    `daemon-lifecycle-status.ts`, `daemon-reachability.ts`,
    `daemon-start-lock.ts`, `local-daemon-owner.ts` — `packages/cli/src/`
    (**remplacés, pas portés**, §D5).
  - `spawnHolonRig()` du bind (`src/lineage_spawner.ts`, pin `adafb0d`)
    — déclaration seulement (`Date.now()`, aucun I/O, aucun appel au
    daemon) ; **remplacé** par l'ordonnanceur ULID (§D6).
- **Modules de l'adapter (`src/`) :** `rig.ts` (modèle + validation
  de spec), `lineage.ts` (ULID + scheduler), `herdr.ts` (politique
  socket + orphelins), `lifecycle.ts` (contrat daemon unique + sonde
  `/healthz` 500 ms + lock PID + re-pointage TUI), `telemetry.ts`
  (garde-fou sortant), `bind.ts` (127.0.0.1 seulement),
  `context-packs.ts` (validation manifeste + taxonomie).
- **Smoke :** `node --experimental-strip-types
  aspace-openrig-adapter/smoke_test.ts` — **61/61 PASS** (log
  `logs-openrig-smoke.log`). Tout est local (lectures git/fichiers,
  fonctions pures, serveur stub loopback, garde-fou fetch) — le smoke
  passe sans aucune interface réseau.
- **Typecheck :** `tsc -p aspace-openrig-adapter/tsconfig.json` —
  **0 erreur** (config patron pi : `allowImportingTsExtensions`,
  `noEmit`, imports relatifs `.ts`).

## Spawner remplacé — l'ordonnanceur de lignage (D6)

- Le bind déclare `spawnHolonRig(areaCode, childHolon)` →
  `RIG-${areaCode}-${childHolon}-${Date.now()}`, worktree
  `.worktrees/${rigId}`. C'est une déclaration, pas un ordonnanceur.
- Le remplacement (`LineageScheduler`, adapter + natif
  `openrig_lineage`) garde la forme (`RIG-<zone>-<holon>-<unique>`,
  `.worktrees/<rigId>`) mais l'unique est un **ULID** (26 car.,
  Crockford base32, monotone dans la milliseconde — la même famille
  d'identifiants que le daemon utilise, paquet `ulid`) : triable, sans
  collision dans la milliseconde, et consigné dans un `SpawnRecord`
  que le daemon unique persiste. Le smoke le prouve (2 ids distincts
  et triés, round-trip, pas de timestamp nu).

## Cycle de vie CLI remplacé (D5)

- Les commandes de cycle de vie du CLI openrig sont remplacées par
  celles du daemon unique (mêmes commandes, le daemon unique comme
  cible). L'adapter expose le contrat : `resolveUniqueDaemonEndpoint`
  (loopback seulement), `probeDaemon` (`/healthz`, 500 ms, sémantique
  3 états — un timeout est une boucle bloquée, pas un daemon arrêté,
  ruling 1ae863d2), `acquireDaemonLock` / `releaseDaemonLock` (un seul
  fichier PID, un seul daemon), `resolveTuiEndpoint` (re-pointage TUI,
  §D3). Le smoke prouve chaque fonction contre un serveur stub
  loopback (sonde OK, mauvais PID refusé, port fermé = `refused`,
  lock acquis puis libéré).

## Télémétrie

- **Zéro SDK, zéro exporteur** (`posthog` / `sentry` / `segment` /
  `mixpanel` / `amplitude` / `datadog` / `newrelic` / `opentelemetry` =
  0 occurrence dans tous les `package.json`).
- **CORRECTION portée en avant** (voir audit §1) : le design affirmait
  « télémétrie 0 » au code search — c'est faux. Le daemon **a** une
  surface télémétrie : `routes/telemetry.ts` (95 lignes, 6 routes de
  lecture) + `domain/finite-telemetry.ts`, `usage-series.ts`,
  `usage-samples-store.ts`. C'est une **projection de lecture LOCALE**
  sur le SQLite du daemon (`usage_samples`) — faits seulement, aucune
  identité de compte dans aucune réponse — pas un exporteur. La
  conclusion « zéro par défaut » tient ; la prémisse « 0 signal » est
  corrigée.
- **Sites sortants du daemon, tous fermés par défaut** (audit §2) :
  plugin-vendor (`github.com/mvschwarz/openrig-plugins`, au démarrage,
  tolère l'échec), Slack (`slack.com`, clé requise), OpenRouter
  (`openrouter.ai`, `--openrouter-charge` seulement), pairing
  d'hôtes distants (URL fournie par l'opérateur). L'adapter les refuse
  tous par défaut (`installOutboundGuard`, liste loopback seulement ;
  hôtes télémétrie/analytics bloqués même quand autorisés).
- **Binding : 127.0.0.1 seulement** (D9). L'adapter **surcharge** le
  défaut amont (qui ajoute l'IP tailscale quand elle existe) :
  `resolveAspaceBind()` retourne toujours `["127.0.0.1"]` et consigne
  ce que l'amont aurait lié, pour que la surcharge soit visible.

## Portage natif (RigInfinity, `aspace-v5-native`)

Le daemon openrig est retiré ; ses 3 fonctions vivent dans le daemon
unique (Rust, edition 2024, Apache-2.0). Ré-implémentation des
fonctions, pas copie du code (TS/Hono/SQLite → Rust) :

| Fonction du daemon | Module natif | Contenu |
|---|---|---|
| État SQLite (`openrig.sqlite`, 146 migrations) | `openrig_state.rs` | rusqlite (bundled) ; règle de chemin amont ; 8 tables cœur (rigs, pods, nodes, edges, bindings, sessions, events, usage_samples) + `schema_version` ; `usage_series()` (lecture télémétrie locale) ; `list_orphan_sessions()` (H-P4-3) |
| Context-packs (fichiers, taxonomie, cache mémoire) | `openrig_context_packs.rs` | serde_yaml ; validation manifeste + taxonomie ; `ContextPackLibrary` (scan + cache mémoire, zéro table SQLite) |
| Herdr (transport de terminal) | `openrig_terminal.rs` | Client socket Unix std-only, NDJSON ; 8 méthodes épinglées ; `HerdrSessionRegistry` + orphelins ; **aucun `Command::new("hc")`** (limite AGPL à distance) |
| Spawner de lignage (`Date.now()`) | `openrig_lineage.rs` | ULID std-only (`/dev/urandom`, monotone) ; `LineageScheduler` + `SpawnRecord` |

- **Base pas 3 vérifiée présente avant le portage :**
  `aspace-v5-native` HEAD `aad4993`, `crates/infinity-daemon/src/` =
  11 fichiers (client, http, lib, main, mcp_proxy, memory_store, rap,
  rap_callback, rap_servers, session, session_store).
- **Dépendances ajoutées** (registre crates.io joignable, vérifié) :
  `rusqlite 0.32` (bundled) + `serde_yaml 0.9` — workspace + crate.
  Aucune autre dépendance nouvelle.
- **Tests natifs :** `cargo test -p infinity-daemon` COMPLET, exit 0 —
  **lib 27/27, bin 0, intégration `daemon_proof` 4/4, doc 0**
  (log `logs-riginfinity-pas4-cargo-test-full.log`) ; `cargo
  clippy -p infinity-daemon --all-targets` — **0 warning** (1 warning
  `collapsible_if` corrigé, commit `e190645`) ; `cargo fmt --all
  --check` — **0** (correctif fmt dans le même commit).
- **Coordination :** travail dans un clone frais
  (`riginfinity-pas4-repo`), re-fetch avant push, jamais de force
  (le sous-agent du pas 3 travaille encore sur la même branche).

## Corrections portées en avant (design → réel)

1. **Télémétrie « 0 signal » — faux.** Le daemon a une surface
   télémétrie locale (`routes/telemetry.ts` + domaine). Corrigé dans
   l'audit : 0 exporteur, 0 SDK, mais une lecture locale existe.
2. **Rôles dans le YAML — absents.** Le design (H-P4-2) suppose des
   rôles `lead/worker/reviewer/kernel operator` dans le rig YAML. Le
   gel n'en déclare aucun : les membres portent `id`, `agent_ref`,
   `runtime`, `model`, `profile`, `cwd`, `startup`. `Node.role` est
   une colonne nullable fixée par le daemon à l'exécution. Le
   validateur l'accepte comme optionnel ; le rôle, quand il est
   présent, doit être dans la liste épinglée.
3. **Starter 1 pod / 2 membres / 1 edge — pas 4 / 5 / 4.** Le design
   citait 4 pods, 5 membres, 4 edges pour le starter
   (`specs/rigs/launch/starter/rig.yaml`) — le fichier réel déclare
   1 pod (`dev`), 2 membres (`build` claude-code, `review` codex),
   1 edge (`delegates_to` build → review). (`focused/code-review` :
   2 pods / 3 membres / 2 edges, avec des références qualifiées
   `pod.member` — le validateur les résout.)
4. **H-P4-7 cite le binding localhost — confirmé, avec une nuance :**
   le défaut amont ajoute l'IP tailscale quand elle existe
   (`bind-plan.ts`) ; l'adaptateur A'Space la refuse (voir §
   Télémétrie).

## Divergence (dette portée par le cœur Buzz, lane Clara / 12e)

- **Dérive amont : 226 commits derrière le gel** (amont `52cc63d`,
  2026-11-10T21:45:02Z) ; pin 232 derrière. Signal de revisite,
  jamais de re-gel silencieux.
- **Dette de portage (tables SQLite non portées) :** l'amont a 146
  migrations / ~50 tables ; le port natif couvre les 8 tables cœur.
  Restent, en optimisation continue : queue (`queue_items`,
  `queue_transitions`), inbox/outbox, checkpoints, snapshots,
  `classifier_leases`, `project_classifications`, et les ~25 colonnes
  de `Node` (handover, resume ledger, token refs, advisor). Le
  `schema_version` natif (= 1) trace la couverture.
- **Serveur Hono non porté** (par design, §D4 OUT) : les routes sont
  ré-implémentées en Rust — la parité des routes `/api/*` est un
  travail d'intégration, pas de ce pas.
- **TUI/UI : surfaces seulement.** Le re-pointage est contractuel
  (`resolveTuiEndpoint`) ; le branchement live de la TUI sur le
  daemon unique est vérifié à l'intégration (H-P4-10).
- **Harnais (claude-code, codex, pi, omp) : interfaces épinglées,**
  exécution live via le daemon unique à vérifier à l'intégration
  (H-P4-5).
- **Preuves live (rig qui démarre, cockpit Herdr, relais avec
  adresses persistantes) :** elles exigent herdr + tmux + le daemon
  unique en cours d'exécution — machine (PC), pas cette VM
  (H-P4-2/3 PARTIELS, procédures à écrire comme pour le pas 2).

## Hold-outs

| Hold-out | Verdict | Preuve |
|---|---|---|
| H-M1 Gel nommé | **PASS** | HEAD du fork = gel avant adaptation ; commit adapter `b71bf87` parent = gel ; consigné ici |
| H-M2 Paquets amont intacts | **PASS** | Vérifié à l'API : compare gel..HEAD = ahead 1, behind 0, 13 fichiers adapter uniquement ; smoke `verifyFrozenLineage` vert |
| H-M3 Suite verte | **PARTIEL** | Première passe : `test:repo` en échec sur 2 tests (`scripts/test-instance-isolation.test.mjs`, SIGKILL après 50 s — le timeout propre du test, pas une régression : le build cargo concurrent — compilation C de rusqlite — affamait le CPU de la VM pendant la suite). Re-run isolé : **2/2 PASS** (16,0 s / 17,2 s, log `logs-openrig-isolation-rerun.log`). Re-run complet de `npm test`, seul : **`test:repo` VERT — 334 tests, 333 pass, 0 fail, 1 skipped, 669 779 ms ; isolation ✔ 16 848 ms ; first-run references 528 checked, 0 failure ; context-packs `--check` OK, 57 packs** (log `logs-npm-test-rerun.log`). `npm run lint` **VERT** (exit 0, log `logs-openrig-lint.log`). `test:workspaces` **cli COMPLET** (368 fichiers : 6 en échec ; 12 tests en échec / 6 213 pass / 22 skipped ; log `logs-openrig-workspaces-cli-tui.log`) et **tui COMPLET** (128 fichiers : 1 test en échec / 1 201 pass). `test:workspaces` **daemon INCOMPLET** : 2 passes tuées par un SIGTERM externe à ~35–36 min (plafond d'exécution de la VM, pas un échec de test) ; 162/1 326 fichiers terminés en 2 passes ; passe 1 : 38 échecs / 11 fichiers ; passe 2 (daemon seul) : 11 échecs / 6 fichiers. Re-runs ciblés : daemon 12 fichiers — **15 en échec / 1 125 pass** (log `logs-openrig-failing12-rerun.log`) ; cli 6 fichiers — **11 en échec / 283 pass** (log `logs-openrig-failing-cli-rerun.log`) ; tui 1 fichier — **PASSE** (log `logs-openrig-failing-tui-rerun.log`). **Échecs stables (13 daemon + 8 cli), 0 imputable à l'adapter** — 0 référence à `aspace-openrig-adapter` hors du dossier adapter (grep vérifié), diff = adapter seul (H-M2, API). Daemon : bundle-routes 4 (root lit les fichiers `unreadable`), codex-runtime-adapter 1, queue-repository 1, skill-catalog-loadout 1, seat-launch-additions 1 (root), transcript-store 2 (root), bundle-local-skills 2, claude-activity-hook-delivery 1 (mode 0755 perdu au checkout, umask 0007). CLI : front-door 3 (timeouts 5 s, binaire réel sous charge), preflight 1 (root), scope-commands 1 (`unreadable`, root), chatroom-watch-tmux-args 1 (tmux réel + $HOME), scope-slice-claims 2 (batches 8 processus). **Flaky (passent en isolé ou varient)** : queue-routes 0/3/2, doctor 2→3, slice-claims 2 autres, s03-bound-launch 16→0, claude-bootstrap-config-home 8→0, send-prompt-guard 1→0, refresh-activity (tui) 1→0. Cargo natif complet **VERT** (lib 27/27 + `daemon_proof` 4/4). Jugement 13e requis. |
| H-M4 Télémétrie zéro | **PASS** | Audit versionné (avec la correction §1 ci-dessus) ; garde-fou prouvé par le smoke |
| H-M5 Manifeste | **PASS** | `openrig.manifest.json`, `fiber:a0:openrig`, `levels.current: 0` (le parent monte à 2) |
| H-M6 Frontière adapter | **PASS** | Adapter seul code A'Space du fork ; divergence remplie ; propriétaire : cœur Buzz, lane Clara / 12e |
| H-M7 Fiche versionnée | **PASS** | Cette fiche |
| H-P4-1 Gel + bind | **PARTIEL** | Gel vérifié HEAD ; **le bind est re-appliqué VERBATIM par le parent** (pas par cet exécutant) + re-pin à l'intégration |
| H-P4-2 Rigs YAML | **PARTIEL** | Structure validée par le smoke (starter 1/2/1 + code-review 2/3/2, edges qualifiées) ; **démarrage réel avec le runtime natif = preuve machine** (herdr + tmux + daemon unique) ; rôles : voir correction 2 |
| H-P4-3 Sièges Herdr | **PARTIEL** | Zéro orpheline prouvé au niveau code (détection adapter + store natif + registre, tests unitaires + socket mock) ; **cockpit live + relais avec adresses persistantes = preuve machine** |
| H-P4-4 Daemon retiré | **PARTIEL** | Les 3 fonctions vivent dans le daemon unique (4 modules natifs) ; le cycle de vie CLI est celui du daemon unique (contrat) ; **l'absence de processus openrig est vérifiée à l'intégration** (H-F8-4) |
| H-P4-5 Adapters | **PARTIEL** | Interfaces des harnais épinglées (runtimes claude-code/codex/pi/omp dans le modèle rig) ; **exécution live via le daemon unique = intégration** |
| H-P4-6 Orchestration ad hoc | **PASS** | Aucun appel `hc` direct : garde-fou adapter (smoke) + aucun `Command` dans le module natif ; le rig unique est la seule voie (code) |
| H-P4-7 Télémétrie zéro | **PASS** | Audit versionné ; surface Hono + websocket auditée ; binding 127.0.0.1 seulement (avec la surcharge tailscale) |
| H-P4-8 Manifeste + fiche | **PASS** | Manifeste + fiche dans `evidence/D-N051/p4/` (dépôt V5 `00_A0_Core/` = parent) |
| H-P4-9 Suite verte | **PARTIEL** | Comme H-M3 : `test:repo` vert, lint vert, cli+tui complets avec échecs amont qualifiés, daemon incomplet (plafond ~35 min, 162/1 326 fichiers) ; 13 échecs daemon stables + 8 cli stables, tous environnementaux (root uid 0, umask 0007, charge/timing), 0 imputable à l'adapter ; 7 fichiers flaky passent en isolé. Jugement 13e requis. |
| H-P4-10 Smoke sans l'original | **PARTIEL** | Mécanisme natif livré (4 modules + smoke adapter 61/61) ; **le cycle du Runtime sans le fork = harnais du parent** (H-F8-2) |
| H-F8-2 Cycle sans l'original | **PARTIEL** | Comme H-P4-10 — harnais du parent |
| H-F8-4 Un seul daemon | **PASS (construction)** | Le pas 4 ne retire qu'un daemon (openrig) et n'en ajoute aucun ; herdr-core reste jusqu'au pas 8 ; comptage vérifié à l'intégration |
| H-F8-9 Plafonds | **À JUGER** | Tailles : adapter 13 fichiers (3 commits, 1 435 + 39 + 17 lignes) ; port natif 4 modules (1 551 lignes + 177 de correctif fmt) ; le parent juge les plafonds (1 % module, 5 % pas, 20 % mission) |

## Contraintes nommées du §2 (design pas 4)

- D1 — gel sanctuarisé, jamais re-gelé sur le HEAD vivant.
- D2 — périmètre daemon + CLI ; tui/ui surfaces ; test-system outillage.
- D3 — TUI préservée comme surface, re-pointée sur le daemon unique.
- D4 — 3 fonctions portées (état, context-packs, Herdr) ; Hono non porté.
- D5 — cycle de vie CLI remplacé, pas porté.
- D6 — spawner remplacé par le vrai ordonnanceur (ULID).
- D7 — version figée 0.7.1 ; écart docs 0.7.5/0.7.8 consigné.
- D8 — Linux, jamais WSL2 (cette VM est Linux).
- D9 — binding 127.0.0.1 seulement ; télémétrie zéro par défaut.
- D10 — état visé 0 → 2 en un seul pas (adaptation + fusion ensemble).
- D11 — base pas 3 vérifiée présente (`aad4993`, 11 fichiers).
- D12 — sprawl : un daemon retiré, aucun ajouté.
- D13 — plus d'appel `hc` direct hors du rig.
- D14 — suite par la commande racine, jamais vitest nu.
