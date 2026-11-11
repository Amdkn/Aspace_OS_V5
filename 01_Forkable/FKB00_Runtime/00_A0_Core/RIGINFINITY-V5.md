# RigInfinity V5 — fiche technique (piste F, audit §3 / plan P2)

**Mission :** piste F — Manifeste AspaceFiberManifest v1 + fiche RigInfinity (audit GPT 2026-11-11, plan P2 : convergence du moteur).
**Adresse :** `fiber:a0:riginfinity`. **Hôte :** daemon unique RigInfinity (`crates/infinity-daemon`, Rust).
**Propriétaire :** 13e Doctor (Kernel) — moteur d'exécution natif ; holon_owner déclaré par `aspace-plugin.json` : S1-RICK / A1-BETH / A1-MORTY.
**Manifeste :** `01_Forkable/FKB00_Runtime/00_A0_Core/riginfinity.manifest.json` (AspaceFiberManifest v1).

## Substrat

- RigInfinity `aspace-v5-native`, pin **`c6adc8d`** (gitlink V5 vérifié à l'API, type submodule, master `5ff0578` ; compare e866578...c6adc8d = 3 commits : `62331c8`, `ee5c838`, `c6adc8d`).
- Module NATIF Amdkn : pas de fork, pas de gel amont, pas d'adapter — le pin EST la référence. Branche `main` distincte `86f1139`.
- **36 fichiers suivis** au pin ; 0 fichier `.ts` ; pas de daemon TypeScript OpenRig, pas de CLI/TUI, pas de `security-harness`.
- Rust : 20 fichiers src (6 688 lignes) + 3 fichiers de tests (978 lignes) = 7 666 lignes `.rs` au total.

## Base daemon (pin c6adc8d)

- Binaire `riginfinity-daemon` (`src/main.rs`, 16 lignes : `run_daemon(true)`, Unix socket + RAP callbacks, loopback only) ; cœur `src/lib.rs` (209 lignes).
- Règle D6 (lib.rs) : chaque listener bind `127.0.0.1` seulement, jamais `0.0.0.0`.
- **Suite re-courue sur cette VM au pin : `cargo test -p infinity-daemon` 64/64** (lib 51/51 + `agent_zero_proof` 5/5 + `daemon_proof` 4/4 + `source_control_proof` 4/4) ; clippy 0 warning ; rustfmt clean.

## Fonctions portées (prouvé — code + tests au pin)

| Source | Fichiers natifs | Preuve |
|---|---|---|
| Agent Zero (boucle agentique) | `agent.rs` (430 l.), `provider.rs` (336 l.), `memory.rs` (327 l.), `job.rs` (364 l.) | Portage `e866578` (F8 pas 5) ; `agent_zero_proof` 5/5 |
| Infinity (concurrence, hibernation, RAP, MCP) | `session_store.rs` (248 l.), `session.rs` (475 l.), `rap_callback.rs` (178 l.), `rap.rs` (159 l.), `rap_servers.rs` (111 l.), `mcp_proxy.rs` (584 l.) | Portage `bd7c946` + `aad4993` (F8 pas 3) ; `daemon_proof` 4/4 |
| OpenRig (rigs, rôles, lignage, worktrees, context packs) | `openrig_state.rs` (687 l.), `openrig_context_packs.rs` (303 l.), `openrig_lineage.rs` (249 l.), `openrig_terminal.rs` (439 l.) | Portage `a372582` + `e190645` (F8 pas 4) |
| Source control natif (D-N054) | `source_control.rs` (1 035 l.) | SC-1 `c6adc8d` ; `source_control_proof` 4/4 ; contrat D4, 6 requêtes |
| Appui | `memory_store.rs` (372 l.), `client.rs` (123 l.), `http.rs` (43 l.) | — |

## Interfaces conservées

- Protocole RAP (`SessionRapManager`, `rap_servers.rs`) ; proxy MCP (un port par toolset, `mcp_proxy.rs`).
- Transport socket Herdr (`openrig_terminal.rs`) ; scheduler de lignage ULID (`openrig_lineage.rs`, remplace le spawner `Date.now()` du bind).
- Forme serde `SessionEntry` (`cwd`, `shut_down`, `idle`, `archived`) et hibernation en deux temps (`session_store.rs`).
- Cycle de vie session : démarrage paresseux des serveurs RAP à la première étape, arrêt à l'idle, arrêt global à la sortie du daemon (`shutdown_all`).
- Contrat D4 source-control : 6 requêtes exactement, reçu/jugement/hold-out en `pending` structuré (SC-1).

## Non porté — par design (lib.rs, D3/D7/D9)

- Providers bedrock/rig, slack-bot ; WebSocket + web-asset UI ; serveur WebUI (surfaces, re-pointées vers le daemon unique).
- Serveur Hono OpenRig (routes ré-implémentées en Rust, non copiées) ; LiteLLM et clés providers ; cron.

## Restant à intégrer (P2 → P7)

- **Prime Agent :** portage `9050a1f` NON mergé dans `aspace-v5-native` (branche `ryan/d-n052-r2-native` seule, vérifié à l'API ; 0 fichier `prime*` dans l'arbre) — suite 70/70 au portage (lib 55/55 + `prime_agent_proof` 6/6 + `agent_zero_proof` 5/5 + `daemon_proof` 4/4). La condition (a) de l'incorporation native n'est pas remplie dans l'arbre épinglé par V5.
- **Daemon TypeScript OpenRig + CLI/TUI :** non portés — hors périmètre P2 sauf valeur réelle démontrée (audit §6 : compléter uniquement les fonctions à valeur réelle).
- **security-harness :** absent de l'arbre — voir dette ci-dessous.
- **Hôte Cordis (P1) :** brancher le daemon au `AspaceFiberHost` (socket Unix, baux réels) — aucun bind Cordis → RigInfinity à ce jour.
- **Baux et budgets (P3 Automaton) ; preuve daemon unique (P7).**

## Dette de divergence

- **Dette F-RIG-1 (OUVERTE) :** `aspace-plugin.json` dans RigInfinity déclare 5 capacités dont 2 sans preuve — `openrig_demo_qc_578_holons` (le nombre 578 n'apparaît qu'en prose : README, constitution, `docs/heartbeat.md`, commentaire `lib.rs` ; 0 module, 0 test, 0 donnée) et `reviewer_security_owasp_top10` (déclarée nulle part ailleurs ; 0 module, 0 test). Le manifeste V5 ne déclare que les 3 capacités prouvées (`rust_deterministic_ownership`, `infinity_daemon_rap_protocol`, `source_control_natif_read_api`). Correction = commit RigInfinity (retirer les 2 capacités de `aspace-plugin.json` ou les implémenter), hors de cette PR V5.
- **Dette SC-0 CLOSE (SC-1) :** `aspace-plugin.json` nomme désormais `source_control_natif_read_api` — vérifiée au fichier au pin `c6adc8d`.

## Contraintes

- Une capacité déclarée sans preuve = rejet du jugement (discipline piste F).
- Aucun fast-forward silencieux : tout re-pin exige PR dédiée + compare API + suite verte + jugement 13e.
- `enforce_admins` reste false ; local-first ; le daemon n'invoque jamais `git` (module source-control : seul trafic sortant = HTTPS vers l'API GitHub, sur requête, token par env).
