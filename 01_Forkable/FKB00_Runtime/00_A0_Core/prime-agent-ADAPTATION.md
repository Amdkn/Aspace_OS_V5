# prime-agent — ADAPTATION (D-N052 R2 = F8 pas 6, la récursion)

**Dispatch :** D-N052 R2, typé à Ryan, journal 775 (2026-11-11 ~00:11 EST),
submission `9f874506-d80c-4cf9-a884-16a6c468aa55`. Typage direct Nardole sur
instruction directe A0 (parallèle au D-N055, journal 774).
**Design :** D-N052 signé Clara (D4/D13 confirmés, non amendés) + **amendement A1
SIGNÉ Clara** (`DEVELOPPEMENT-MODULES-RECURSIVITE-amendement-a1-r2-prime-agent.md`,
16 275 o, ~22:56 EST). Discover Bill :
`discover-d-n052-r2-prime-agent.md` (23 814 o, §0–§8). Séquence R2-1..R2-7.
**Un seul développement, deux usages — la PR R2 est la PR du pas 6.**
F8 pas 6 consomme R2, ne le refait pas. Dépôts R10 : 005 (livraison) / 006 (merge).

## §0 — Ancres (vérifiées à l'API, 2026-11-11 ~00:2x EST)

- Fork `Amdkn/prime-agent` ← `PrimeIntellect-ai/prime-agent`, 111 506 Ko, main, MIT
  (fichier ; API NOASSERTION).
- **Gel `74591cd`** (full `74591cddef28d11249c3171112114fc4755375d7`, 2026-11-04T22:27:39Z,
  « feat(kernel): rlm.end_turn() — the sanctioned terminal call (#3830) »).
- **Fork main HEAD = le gel.** Bind `3ba6791` (full
  `3ba6791f723635ce89dcf79f69bdfa101e340576`, parent = gel, 1 fichier
  `aspace-plugin.json`) = HEAD de la branche **`aspace-v5-native`** du fork
  (compare gel...bind : ahead 1, behind 0). À re-appliquer sur main en R2-6 (F8 D2)
  — par Ryan, PAS par ce développement.
- **Dérive amont : 21** (tête `6aaa3a2`, full
  `6aaa3a25518b1d01389540eabb4e3a89bca666bb`, compare gel...tête : ahead 21,
  behind 0) — candidat de revisite, pas un gate, pas de re-gel (A4).
- Version 0.10.2, Rust edition 2021, workspace 10 crates (pa-agent, pa-ai, pa-cli,
  pa-core, **pa-daemon**, pa-models, pa-perf, **pa-telemetry**, pa-tui, pa-types).
- **Pin V5 : `3bac96a`** (retiré au pas 8) — l'adapter
  (`3bac96af34511fde1f0d3bbf4e7bc94ad605e69a`, parent = gel), dans
  `05_Recursive_RSI` ; bind re-appliqué sur `main` du fork :
  `2054f538b` (parent = adapter, 1 fichier `aspace-plugin.json`,
  blob byte-identique au bind `3ba6791`, vérifié à l'API).
- **Bind : `2054f53`** — `main` HEAD du fork (bind re-appliqué au-dessus de l'adapter).
- Aucun manifeste V5 avant R2 — créé ici, état 2 dès le départ (A3,
  `fiber:a0:prime-agent`).
- Master V5 au moment de l'intégration : `107006b` (vérifié à l'API, base de la
  PR R2, branche `d-n052-r2-prime-agent`).
- RigInfinity : repo `Amdkn/RigInfinity`, branche par défaut `aspace-v5-native`,
  HEAD `e866578` (full `e866578032b6ded80b8573cec579413a37cd3a92`, vérifié à l'API).

## §0.1 — Décisions A1–A11 (amendement Clara, résumé d'exécution)

- **A1** `pa-daemon` déposé comme référence, jamais lancé (RigInfinity = seul daemon).
- **A2** runtime Python re-pointé comme surface (REPL), pas porté, jamais un second daemon.
- **A3** manifeste `fiber:a0:prime-agent`, état 2 dès le départ.
- **A4** dérive 7→21 = revisite, pas de re-gel, pas de revue API avant R2.
- **A5** plafonds 1 % / 5 % / 20 % sur pool 5,5 Md.
- **A6** réserve R-1 (test TabFM PARTIEL) non-gate, test non touché.
- **A7** smoke : `rlm.spawn` + `/refine` + rollback sur le vrai harness ; points
  d'entrée confirmés à l'exécution.
- **A8** audit télémétrie : code search + dépendances + capture réseau (déclencheurs
  par défaut ON) + surfaces de lecture locale ; chaque déclencheur tranché ;
  `curl|sh` jamais exécuté.
- **A9** composition par l'adapter (`aspace-prime-agent-adapter`).
- **A10** pin → adapter, vérifié à l'API après merge ; bind = ancre de lignée.
- **A11** un seul développement, deux usages.

## §1 — Points d'entrée confirmés à l'exécution (dans le code du gel)

- `rlm.spawn` = `prime-agent-runtime/src/rlm/__init__.py:212`
  `async def spawn(prompt, *, name, model=None, thinking=None, cwd=None)` (wire
  `rlm.run` ; `_spawn` avec `factory` `{runId, specId, stateId}`) ; Rust :
  `RlmSpawnRequest` dans `crates/pa-core/src/session_engine/rlm_host.rs:138`
  (prompt, name, model, thinking, cwd, spawned_by_request_id, factory).
- `rlm.collect` = `__init__.py:463` (wire `rlm.collect` ; `timeout_ms=0` = snapshot
  non bloquant ; timeout = snapshots courants, jamais d'erreur) ;
  `RLMChildResult` (:105), `RLMSpawnHandle` (:29), `RLMSubagent` (:60, status
  running/completed/error/cancelled).
- `rlm.end_turn` = `__init__.py:196` (wire `rlm.end_turn`, appel terminal sanctionné ;
  lève si l'hôte ne le supporte pas, jamais de no-op silencieux).
  `RLM_PROGRESS_NOTE_MAX_LENGTH = 512`.
- `/refine` : `plan_refinement` (executor.rs:194 ; rollback via `options.rollback_id`,
  erreur `Refinement {id} not found` sur id inconnu), `apply_refinement_plan` (:304),
  `rollback_proposal` (planner.rs:505, édits inverses en ordre inverse, saute les
  non-appliqués), `review_auto_refine` (:363, gate automatique),
  `generate_refinement_id` (canonique `refine_<17 chiffres>`), skill
  `skills/refine/SKILL.md` (`refine.run(instructions, global_=False)`, `refine.status()`).
- `pa-daemon` : ACP stdio (`initialize`, `session/new`, `session/prompt`,
  `session/close`, `session/cancel`, `session/update` avec `_meta` corrélé) ;
  superviseur (1 worker/session, restart/backoff, registre) ; store JSONL ; tickets
  single-use TTL 10 s.
- Surface contract du fork (`AGENTS.md`) : API RLM du REPL
  `rlm.spawn/find_models/collect/list_subagents/delete_subagent/create_session/progress_note`,
  `rlm.harness` CRUD, `agent_message.send`, `agent_observe`, `compact`, `goal`,
  `refine`, `attach_image`, skills.

## §2 — Volet A : adapter (FAIT, commité + poussé)

Clone fork `~/workspace/prime-agent-repo`, branche **`ryan/d-n052-r2-adapter`**
depuis le gel. **Commit `3bac96af34511fde1f0d3bbf4e7bc94ad605e69a`**
(parent = gel `74591cddef28d11249c3171112114fc4755375d7`, vérifié), 13 fichiers,
+1787, poussé sur `ryan/d-n052-r2-adapter`.

Identité : `Prime-Agent Adapter (A'Space V5) <prime-agent-adapter@aspace.local>`
(précédent pas 5 `a042ddde` ; la config git ambiante n'a AUCUNE identité et sans
identité le commit échoue — le précédent a été suivi).

Contenu `aspace-prime-agent-adapter/` (crate Rust std-only, son propre
`[workspace]`) : `Cargo.toml` + `Cargo.lock`, `README.md`, `AGENTS.md`,
`contract.json`, `src/lib.rs`, `src/rlm.rs` (RlmEngine : spawn/collect/end_turn,
bornes profondeur 5 / 16 enfants / bail 300 s, erreurs typées),
`src/refine.rs` (plan/apply/rollback, Local par défaut, baseline, gate
`review_auto_refine` à seuil passé par l'appelant), `src/runtime_surface.rs` (A2,
`RuntimeSurface::repointed()`, check), `src/daemon_ref.rs` (A1,
`DaemonRef::launch_attempt` refuse par construction, 6 méthodes ACP),
`src/lineage.rs` (mesure zéro + 10 surface pins + tests structurels H-M2/H-M4),
`tests/smoke.rs` (5 preuves), `tests/telemetry_guard.rs` (garde H-M4 — le garde
habite dans `tests/`, pas dans `src/`, sinon le scan se matchait lui-même).

**Suite adapter : 18/18 verte** (lib 12, smoke 5, guard 1) ; `cargo fmt --check`
propre ; `cargo clippy --all-targets -- -D warnings` propre.

Corrections en cours de route : erreur de type `Some(answer.as_str())` →
`Some(answer)` (2×, adapter + preuve native) ; garde télémétrie déplacée de
`src/lineage.rs` vers `tests/telemetry_guard.rs` (auto-match). `target/` du
adapter NON commité (non ignoré par le .gitignore du fork — ajout sélectif par
fichiers).

## §3 — Volet B : portage natif RigInfinity (FAIT, commité + poussé)

Clone frais `~/workspace/riginfinity-r2-repo` (HEAD API `e866578` vérifié),
branche **`ryan/d-n052-r2-native`**. **Commit
`9050a1fbb7f8da25c4cae11326016dbd200b36de`** (parent
`e866578032b6ded80b8573cec579413a37cd3a92`, vérifié), 6 fichiers, +1506, poussé
sur `ryan/d-n052-r2-native`.

4 modules `crates/infinity-daemon/src/` :

- `prime_agent_rlm.rs` — moteur RLM natif : spawn/collect/end_turn, bornes,
  ledger spawn edge avec factory tag, `run_cycle`, serde camelCase.
- `prime_agent_refine.rs` — Continual Harness natif + store JSON durable
  `HarnessStore` `<dir>/harness.json`, load/save atomique write+rename,
  re-lecture avant apply.
- `prime_agent_runtime.rs` — surface A2.
- `prime_agent_daemon.rs` — référence A1 + garde `SingleDaemon` : seul
  RigInfinity admis.
- Branché dans `lib.rs` (4 `pub mod` + paragraphe doc D-N052 R2).

Test de preuve `crates/infinity-daemon/tests/prime_agent_proof.rs` (6 tests) :
spawn returns ; refine applique Local sur disque ; rollback restaure sur disque ;
cycle H1 contre un **vrai stub HTTP gateway loopback** (TcpListener 127.0.0.1:0,
POST sync par TcpStream std, réponse chat completion parsée) ; single daemon +
surface ; garde télémétrie (scan des `prime_agent_*.rs`).

**Suite complète `cargo test` du daemon : 70/70 verte, 0 échec**
(log : `suite-native.log`, `CARGO_TEST_EXIT=0`) :

| binaire | passés | échecs |
|---|---|---|
| lib (`infinity_daemon`) | **55** (dont 8 nouveaux prime-agent : daemon 2, rlm 2, refine 2, runtime 2) | 0 |
| `agent_zero_proof` | **5** | 0 |
| `daemon_proof` | **4** (pas de régression) | 0 |
| `prime_agent_proof` | **6** | 0 |
| doc-tests | 0 | 0 |

`cargo fmt --check` propre ; `cargo clippy --all-targets -- -D warnings` propre.

## §4 — Audit télémétrie (A8)

Artefact : `prime-agent-TELEMETRY-AUDIT.md` (6 902 o). Chaque déclencheur tranché :

- **T1 — Analytics produit, défaut ON en release : ABANDONNÉ avec le fork.**
  `crates/pa-telemetry/src/sinks/analytics.rs:20` :
  `ANALYTICS_ENDPOINT = "https://api.primeintellect.ai/api/v1/agent-analytics/events"`
  (reqwest, timeout 1,5 s, format `{installation_id, events: [...]}`, relais
  PostHog). Défaut : `TelemetrySwitch::Default => true` (« Nothing set: on »,
  `status.rs:12`). `telemetry_endpoint()` ne renvoie l'endpoint qu'en build
  release (`!cfg!(debug_assertions)`) — en debug, nowhere. Opt-outs :
  `PI_OFFLINE` / `DO_NOT_TRACK` forcent OFF ; `PRIME_AGENT_TELEMETRY` force dans
  un sens ou l'autre ; puis settings `telemetry.enabled`. Preuve historique :
  régression #3288 (fork AGENTS.md, « Performance and the critical path ») — le
  flush télémétrie au démarrage attendu sur le chemin de lancement (~157 ms avant
  la première frame) ; correctif = worker arrière-plan + test
  `the_startup_flush_never_blocks_the_first_frame`. **Verdict : 0 signal dans
  le natif** (garde structurelle H-M4 dans l'adapter et dans la preuve native).
- **T2 — Endpoints de modèles** (api.openai.com, api.anthropic.com,
  api.pinference.ai, api.individual.githubcopilot.com, bedrock-runtime,
  chatgpt.com) : inférence, clé-gatés, initiés par l'utilisateur — **PAS de la
  télémétrie** ; remplacés par la gateway locale (`GatewayProvider`,
  `http://127.0.0.1:31415/v1/chat/completions`, chaîne modelPool).
- **T3 — Update check : manuel uniquement** (`prime-agent update [--check]`,
  `installer_update.rs` / `update_flow/plan.rs`) ; aucun appel automatique trouvé
  (recherche `update_check|check_for_update|check_update` : 0 fichier). Les
  `https://` de `update/download.rs` sont des URLs d'exemple dans les tests.
  **Pas un déclencheur par défaut.**
- **T4 — `install.sh` distant du README (`curl | sh`) : jamais exécuté en R2.**
- **T5 — Surfaces de lecture locale** : `FileSink` (miroir JSONL local
  `<agentDir>/telemetry.jsonl`) et `install_id` (`<agentDir>/telemetry.json`,
  0600, pseudonyme) — locales, sans réseau ; le natif n'en crée aucune.
- **T6 — Messagerie pair-à-pair du daemon** : sockets locales uniquement.
- **T7 — Dépendances** : `pa-telemetry` reqwest (T1) ; `pa-ai`/`pa-models` clients
  fournisseurs (T2) ; **adapter : std only, aucune dépendance** ; natif : reqwest
  du workspace utilisé par le `GatewayProvider` vers 127.0.0.1:31415 uniquement.

## §5 — Hold-outs (verdicts, détail dans `prime-agent.manifest.json`)

H-R3 **PASS** (spawn + /refine + rollback sur le vrai harness, sans appel modèle).
H-M1 **PASS**, H-M2 **PASS**, H-M3 **PARTIEL** (adapter 18/18 ; suite du fork non
re-courue en entier — R-A2), H-M4 **QUALIFIÉ** (1 signal fork, 0 natif),
H-M5 **PASS** (ce manifeste), H-M6 **PASS**, H-M7 **PASS** (cette fiche).
H-F8-1 **PARTIEL** (doublon pa-daemon déposé comme référence ; retrait du pointeur
à l'intégration), H-F8-2 **PARTIEL** (mécanisme natif livré ; cycle complet du
Runtime sans l'original = harnais du parent), H-F8-3 **À JUGER** (4 conditions,
retrait du pointeur + validation 13e à l'intégration), H-F8-4 **PASS**
(construction), H-F8-5 **PASS** (aucun cron), H-F8-9 **À JUGER** (plafonds, parent).

## §6 — Réserves nommées

- **R-A1** — pas de capture réseau live (aucun binaire release construit sur cette
  VM — coût + OOM ; acte machine si le 13e l'exige).
- **R-A2** — suite du fork non re-courue en entier.
- **R-1 (A6)** — test TabFM PARTIEL, non-gate, non touché.
- **Réserve de preuve** — première passe de la suite native : lib 55/55 et
  agent_zero_proof 5/5 vus, daemon_proof non visible (buffer `grep` de 4096 o),
  prime_agent_proof bloqué (voir §7). La seconde passe, sortie vers fichier,
  donne les comptes définitifs (§3) et lève cette réserve.
- **Dérive amont 21 commits** (tête `6aaa3a2`) : candidat de revisite, pas un gate,
  pas de re-gel (A4).

## §7 — Corrections en cours de route (leçons)

1. **Deadlock tokio du test H1 (vrai bug de test, trouvé live).** Le test
   `runtime_cycle_with_h1_over_a_real_gateway_stub` tournait sous
   `#[tokio::test]` (runtime current-thread, un seul fil) ; le fournisseur
   synchrone (std TcpStream, `read_to_string` bloquant) bloque le fil de
   l'exécuteur pendant que la tâche stub (spawnée sur le même runtime) ne peut
   jamais être polluée → deadlock, 0 CPU, 8 min, tué par SIGTERM (preuve `ps` :
   `prime_agent_proof` à 0:00 CPU après 8:05). Correctif :
   `#[tokio::test(flavor = "multi_thread")]` + commentaire dans le test
   (tokio `rt-multi-thread` présent dans le workspace). Le test passe en 0,02 s.
2. **Le pipe `grep` masque la progression.** `cargo test | grep …` bufferise par
   blocs de 4096 o : la sortie est restée figée à exactement 4096 o pendant
   8 minutes alors que la suite progressait (daemon_proof terminé, prime_agent
   en cours). Pour les suites longues : sortie vers un fichier, jamais un pipe
   `grep` seul.
3. **Piège `pkill -f`.** Un `pkill -f <motif>` dont le motif figure dans la ligne
   de commande du shell lui-même tue le shell (SIGTERM 15). Vérifier avec
   `ps … | grep "[c]argo test"` (crochet qui casse l'auto-match).

## §8 — Intégration V5 (FAITE, dans cette PR R2 = pas 6)

Intégration V5 par Ryan : manifeste + fiche + audit en `00_A0_Core/`, gitlink
prime-agent → adapter `3bac96af`, registres F8 + D-N053, bind re-appliqué sur
`main` du fork (`2054f538b`, parent = adapter, blob byte-identique, vérifié à
l'API) → PR R2 (= pas 6) → jugement 13e → merge → dépôts R10 005/006.
**Pointeur conservé (décision d'intégration, H-F8-3 À JUGER) :** le portage natif
`9050a1f` vit sur la branche `ryan/d-n052-r2-native` de RigInfinity, non mergé
dans `aspace-v5-native` (HEAD `e866578`, pin V5 inchangé) — la condition (a) de
l'incorporation native n'est pas remplie dans l'arbre épinglé par V5, donc le
pointeur `.gitmodules` reste et le pin pointe sur l'adapter vérifié. Le retrait
du pointeur est un acte ultérieur, après merge du portage natif dans RigInfinity
et re-pin. **Aucune modification des 3 fichiers natifs Python** : aucune
`target_fork` / `submodule_target` ne pointe vers prime-agent (les deux pointent
déjà vers `Amdkn/RigInfinity` depuis le pas 5) ; les mentions de Prime-Agent y
sont des docstrings du paradigme RLM (désormais implémenté en natif) et
`harness_engine="prime-agent"` un défaut comportemental, laissé tel quel par le
pas 5 lui-même. Ne PAS merger — le 13e juge d'abord.
