# Fiche d'adaptation — agent-zero (D-N051 F8, pas 5)

**Adresse :** `fiber:a0:agent-zero` (le cœur — D2 : le moteur est le cœur du pas)
**Manifeste :** `agent-zero.manifest.json` (même domicile)
**Audit télémétrie :** `agent-zero-TELEMETRY-AUDIT.md` (même domicile)
**Statut :** état 0 Basique → 1 Adapté (fiche + adapter + manifeste ;
**H-P5-3 CONDITIONNELLE (durabilité, vert du pas 2), H-P5-8 QUALIFIÉ
(1 signal dans le fork, 0 dans le natif), H-M3 PARTIEL (suite adapter
36/36 ; suite propre au fork non exécutable sur cette VM),
H-P5-10 / H-F8-2 PARTIELS (cycle complet sans l'original = harnais du
parent), H-F8-9 À JUGER (plafonds, parent)** — voir § Hold-outs)

## Commit gelé

- **Fork :** `Amdkn/agent-zero` (parent `agent0ai/agent-zero`, MIT,
  branche `main`).
- **Gel : `ba9b67d`** (`ba9b67df0f54ac78106ae85c552ef5d2458f7c9a`) —
  « docs: refresh Launcher screenshot in README »,
  2026-11-01 22:10:32 +0100.
- **Vérifié à l'API par Ryan :** fork main HEAD = amont main HEAD,
  compare identical, dérive 0.
- **Vérifié au fichier :** clone local `~/workspace/agent-zero-repo`,
  HEAD = gel avant adaptation, arbre propre.
- **Pin (bind) : `176d23f`** — 1 fichier : `aspace-plugin.json`.
  Parent du pin : `ba9b67d` (le gel). Plugin
  `@aspace-v5/agent-zero`, famille `CORE_A0_KERNEL`, propriétaire
  `A0-AMADEUS / S1-RICK`, 2L. Licence MIT (fichier ; l'API dit
  NOASSERTION, le fichier fait foi).
- **Arbre @gel :** `plugins/` = **47 dossiers**, `_a0_connector`
  présent (compte vérifié au gel par Ryan, puis par le test
  `verify_triage`).

## Adapter

- **Paquet :** `aspace-agent-zero-adapter/` (Python, stdlib seule,
  version 0.1.0), **1 commit** sur le fork `main` : **`a042ddde`**
  (`a042ddde19e5938e13ee1896fdd91cf4551c6cff`, parent = gel
  `ba9b67d`, 17 fichiers, +1654 lignes). Vérifié à l'API après push
  (parent = gel, diff = adapter seul, H-M2).
- **Modules :**
  - `agent_loop.py` — la boucle Agent, miroir de `agent.py:364`
    (`Agent.monologue`) : message → modèle → outils → mémoire →
    réponse. Complétion seulement sur appel explicite de l'outil de
    réponse avec `break_loop`. Le texte libre reste des pensées de
    génération et continue silencieusement ; jamais d'appel d'outil
    synthétisé depuis la prose. L'intention malformée garde son chemin
    de réparation (avertissement dans l'historique, pas d'exception
    hors du tour). `hist_add_ai_response` possède l'avancement d'état
    Responses-API en interne (règle DOX amont).
  - `providers.py` — le client modèle, miroir de `models.py` :
    gateway EGM `:31415` seul, chaîne modelPool du pas 2
    (`freellmapi/auto` → `claude-sonnet-4-5` → `qwen3.8-max` →
    `gemini-3.8-flash` → `deepseek-v4-flash`), retest 15 min.
    **Pas de LiteLLM, pas de clé fournisseur** (D9) : aucun paramètre
    `api_key`, aucune lecture d'environnement, `get_api_key()` →
    `"None"` (sentinelle de refus).
  - `memory.py` — la mémoire unifiée (D6) : Shared Brain JSONL
    (append-only) fait foi ; `FaissIndex` = index dérivé, reconstruit
    depuis le JSONL, jamais l'inverse ; `check_no_divergence()`.
  - `job_loop.py` — le scheduler devenu job loop (D7) : tâches
    scheduled / adhoc / planned, preuve par reçu (ledger JSONL).
    **Aucun cron accepté** : `create_task` / `update_task` lèvent
    `ValueError` sur tout argument `cron`.
  - `plugins.py` — le tri D5 (35 portés / 9 surfaces / 3 abandonnés),
    vérifié contre le gel et mécaniquement contre le design (écart 0) ;
    `PluginRegistry`, le système de plugins natif (preuve des 3
    abandonnés).
  - `lineage.py` — H-M1/H-M2 + 10 épingles de surface (H-P5-1).
- **`contract.json`** — le contrat public de l'adapter (gel, pin,
  famille, propriétaire, gateway, chaîne, tri, dépendance nommée pas 4).
- **`AGENTS.md`** — le DOX enfant de l'adapter (frontière durable :
  stdlib seule, jamais d'import du fork, jamais de clé, jamais de cron).
- **Suite : 36/36 verte** (`pytest`, venv pas 5
  `~/workspace/.venvs-dn053/agent-zero`, pytest 9.2.0) :
  smoke 6, providers 8, memory 5, job_loop 7, plugins 7, lineage 3.
  Trois échecs initiaux corrigés dans le code (pas dans les tests) :
  intention malformée avalée par l'extraction, compteur d'historique
  avant ajout, fenêtre de retest non armée après basculement réussi.
- **Réserve R-A1 :** la suite propre au fork n'est PAS exécutable sur
  cette VM : `tests/test_litellm_sdk.py` ne collecte pas
  (`models.py:20` importe `litellm`, non installé ; Python système :
  pas de litellm/flask/langchain). L'adapter est la suite du module
  (périmètre H-M3 : adapter + tests natifs).

## La greffe n'était pas un import (§0.2)

Les 3 fichiers natifs (`a0_egm_bridge.py`, `a0_recursive_factory.py`,
`a0_holon_swarm_runtime.py`) n'importent jamais le fork — stdlib
seule. Ils ne font que référencer le sous-module par des chaînes,
des chemins et un contrat (gateway `:31415` + ledger SQLite WAL).
« Cesser de greffer » = écrire le moteur natif, pas couper des
imports. La coupure (retrait des références + du gitlink) est faite
par Ryan à l'intégration (§D13), pas par ce pas.

## Le tri des 47 plugins (D5)

Écrit dans le design avant l'exécution, appliqué ici, vérifié
mécaniquement contre le design (écart 0) et contre le gel
(`verify_triage` : 47 dossiers, correspondance exacte).

- **Portés (35)** — les capacités du moteur, dans le moteur natif :
  `_scheduler` (→ job loop), `_memory` (→ mémoire unifiée),
  `_code_execution`, `_browser`, `_desktop`, `_orchestrator`
  (borné : workers du moteur, pas un rig parallèle), `_a0_acp` /
  `_a2a_chat` (protocoles ACP/A2A), `_a0_connector` (pont EGM),
  `_context_window` / `_context_doctor`, `_error_retry`, `_commands`,
  `_goal`, `_search_engine`, `_document_query`, `_editor` /
  `_text_editor`, `_chat_compaction` / `_chat_branching` /
  `_chat_naming`, `_behavior_adjustment`, `_model_config`,
  `_notify_user`, `_wait`, `_skills`, `_migrate_agents`, `_discovery`,
  `_time_travel`, `_infection_check`, `_agent_editor`,
  `_promptinclude`, `_tool_access`, `_onboarding`, `_whats_new`.
- **Surfaces (9)** — préservées, re-pointées, pas portées comme code :
  `_telegram_integration`, `_whatsapp_integration`,
  `_email_integration` (les canaux — **aucun secret lu**),
  `_kokoro_tts`, `_whisper_stt`, `_office`, `_oauth`,
  `_pin_to_top`, `_sidebar_folders`.
- **Abandonnés (3)** — le méta-système du fork :
  `_plugin_installer`, `_plugin_scan`, `_plugin_validator`. Preuve :
  le système de plugins natif est celui de l'adapter
  (`PluginRegistry`), pas celui du fork.

## Télémétrie

Voir `agent-zero-TELEMETRY-AUDIT.md` (versionné, même domicile).

- **H-P5-8 : QUALIFIÉ.** La mention « 0 signal » du design ne tient
  pas au gel : le fork contient **1 signal** —
  `helpers/update_check.py` poste vers
  `https://api.agent-zero.ai/a0-update-check` avec
  `{current_version, anonymized_id}` (sha256 d'un id persistant,
  tronqué à 20 hex), appelé par
  `extensions/python/user_message_ui/_10_update_check.py:76`, porte
  `update_check_enabled` dont la **valeur par défaut est `True`**
  (`helpers/settings.py:634`). Ce n'est pas un SDK d'analytics
  tiers, mais c'est un signal sortant stable vers le domaine de
  l'amont, actif par défaut.
- **Le signal n'est PAS porté** : ni l'adapter ni les modules natifs
  ne contiennent de contrôle de mise à jour, d'identifiant persistant,
  ni d'appel sortant autre que le gateway `:31415`. **0 signal dans
  le natif.**
- Aucun SDK d'analytics dans le fork (sentry/posthog/mixpanel/
  segment/amplitude/hotjar : 0 occurrence dans les `*.py` suivis ;
  `ANONYMIZED_TELEMETRY` n'existe que dans `tests/test_secrets.py`).
- Surface conservée (D3) : serveur UI uvicorn, hôte par défaut
  `"localhost"` (`run_ui.py:32-35`), port 5000, port API tunnel
  55520 (`helpers/runtime.py:171-184`), `get_local_url()` →
  `127.0.0.1`. Binding localhost seulement par défaut.

## Portage natif (RigInfinity, `aspace-v5-native`)

- **Base :** tête `e190645` (pas 4 : 11 fichiers pas 3 +
  4 fichiers openrig). Vérifiée présente avant le portage.
- **4 modules** dans `crates/infinity-daemon/src/` (+ `lib.rs`) :
  - `agent.rs` — la boucle Agent (miroir de `agent.py:364`) :
    `AgentLoop`, `extract_tool_request`, `validate_tool_request`,
    garde 25 itérations, `break_loop` explicite, `hist_add_ai_response`
    possède l'avancement d'état en interne. Tests unitaires : 5.
  - `provider.rs` — le client gateway (miroir de `models.py`) :
    `GatewayProvider`, transport par trait (`ReqwestTransport` en
    production, stub en test), chaîne modelPool, failover + retest
    15 min, `get_api_key()` → `"None"`. Aucune clé. Tests : 4.
  - `memory.rs` — la mémoire unifiée (D6) : `SharedBrainMemory`
    (JSONL append-only), `FaissIndex` dérivé, `check_no_divergence`.
    Tests : 5.
  - `job.rs` — le job loop (D7) : `TaskSpec` (deny_unknown_fields —
    le refus du cron est structurel), `JobLoop`, `Receipt` par
    exécution. Tests : 6.
- **Preuve d'intégration :** `crates/infinity-daemon/tests/agent_zero_proof.rs`
  (5 tests) : boucle sans le fork ; failover contre un **stub HTTP
  local 127.0.0.1** (500 pour le premier lien, 200 pour le second,
  bascule enregistrée) ; mémoire persist + rebuild sans divergence ;
  tâche planifiée prouvée par reçu + cron refusé ; chaîne modelPool.
- **Commit natif : `e866578`**
  (`e866578032b6ded80b8573cec579413a37cd3a92`, parent = `e190645`,
  branche `aspace-v5-native`, 6 fichiers, +1691/−1). Poussé sans
  force, vérifié à l'API (parent = `e19064552714eec535e0ac7345fd5d13e9e081f5`).
  Re-fetch avant le push : aucun nouveau commit du pas 4 depuis
  `e190645` — son travail n'a pas été rebasé ni écrasé.
- **Tests natifs : lib 47/47** (20 nouveaux : agent 5, provider 4,
  memory 5, job 6), **`agent_zero_proof.rs` 5/5**,
  **`daemon_proof.rs` 4/4** (pas de régression du pas 3).
  **Clippy `-D warnings` propre, fmt propre.** Trois corrections
  avant le vert final : 41 `unwrap()` remplacés par `expect()` avec
  message (style maison : le code existant n'a aucun `unwrap()`),
  types complexes factorisés en alias (`ToolHandler`/`ToolTable`,
  `JobHandler`), formatage rustfmt.
- **Dépendance nommée (§D8) :** les fonctions pas 4 (état SQLite,
  context-packs, Herdr terminal) sont une dépendance nommée, pas
  attendue. Le portage est fait contre la base pas 3 ; les 4 fichiers
  pas 4 sont présents dans l'arbre (`openrig_state.rs`,
  `openrig_context_packs.rs`, `openrig_terminal.rs`,
  `openrig_lineage.rs`) depuis `a372582` + `e190645`. L'intégration
  des fonctions pas 4 est re-prouvée quand le merge du pas 4 atterrit
  (un reçu de suivi, pas un gate).
- **Non porté :** LiteLLM et les clés fournisseurs (D9) ; le cron
  (D7) ; le serveur UI comme module (D3 — surface re-pointée) ; le
  méta-système de plugins du fork (D5) ; les hooks WebUI, le serveur
  MCP, les templates de prompts (`prompts/`).

## Corrections portées en avant (design → réel)

1. **H-P5-8 : 1 signal, pas 0.** Le design dit « télémétrie 0
   signal » ; le gel contient le contrôle de mise à jour
   (`helpers/update_check.py`, défaut ON). Consigné dans l'audit,
   qualifié, non porté. La correction est portée en avant : le
   prochain design ne dira plus « 0 signal » sans la preuve par
   recherche de `update_check` et des identifiants persistants.
2. **Le compte des plugins au gel est 47, pas 46.** Le Discover
   listait 46 noms ; le 47e (`_a0_connector`) est déduit des 8 fichiers
   `test_a0_connector_*` et confirmé par le comptage au gel. Le tri
   couvre 47 (vérifié mécaniquement contre le design, écart 0).
3. **Ligne 364 d'`agent.py` :** `Agent` est bien à `agent.py:364`
   (épingle 1 des 10, vérifiée par le contenu).
4. **`Agent` est dans `agent.py`, pas `models.py`** (§0.2 du design
   confirmé au fichier) ; `models.py` = providers LiteLLM
   (`get_api_key_raw` lit `API_KEY_<SERVICE>` / `<SERVICE>_API_KEY` /
   `<SERVICE>_API_TOKEN` du .env ; `get_api_key` round-robin ;
   `_merge_provider_defaults` injecte la clé si absente).

## Divergence (dette portée par le cœur Kernel, lane A0 / S1-Rick)

- **R-A1** — la suite propre au fork n'est pas exécutable sur cette
  VM (litellm absent). La suite du module est l'adapter (36/36) +
  les tests natifs. La suite complète du fork est une preuve machine
  (environnement avec le stack complet).
- **R-A2** — H-P5-3 (durabilité) CONDITIONNELLE au vert du pas 2 (pi).
- **R-A3** — les fonctions pas 4 sont une dépendance nommée (§D8) ;
  l'intégration est re-prouvée au merge du pas 4.
- **R-A4** — H-P5-8 QUALIFIÉ : 1 signal dans le fork (update check,
  défaut ON), abandonné avec le fork, 0 dans le natif.
- **R-A5** — le failover modelPool complet (chaîne de 5) n'est prouvé
  que jusqu'au 2e lien contre le stub local ; les liens 3–5 sont
  prouvés par le transport stub en unitaire (chaîne épuisée → erreur).
  La preuve contre le vrai gateway `:31415` est une preuve machine
  (premier maillon injoignable sur cette VM, comme H-C2-4).

## Hold-outs

- **H-M1 PASS** — HEAD du fork = gel avant adaptation ; commit
  adapter parent = gel (vérifié à l'API).
- **H-M2 PASS** — diff gel..adapter = 17 fichiers adapter seuls
  (vérifié à l'API : push `ba9b67df..a042ddde`).
- **H-M3 PARTIEL** — suite adapter 36/36 verte ; suite propre au
  fork non exécutable sur cette VM (R-A1).
- **H-M4 QUALIFIÉ** — audit versionné ; 1 signal dans le fork, 0
  dans le natif (R-A4).
- **H-M5 PASS** — ce manifeste (`fiber:a0:agent-zero`).
- **H-M6 PASS** — adapter seul code A'Space du fork ; divergence
  remplie ; propriétaire `A0-AMADEUS / S1-RICK` ; précision §0.2.
- **H-M7 PASS** — cette fiche.
- **H-P5-1 PASS** — gel vérifié ; 10 épingles de surface vérifiées
  par le contenu au gel.
- **H-P5-2 PASS** — la boucle tourne sans le fork (smoke + preuve
  native).
- **H-P5-3 CONDITIONNELLE** — durabilité, au vert du pas 2 (R-A2).
- **H-P5-4 PASS** — gateway `:31415` seul, chaîne modelPool,
  failover prouvé (stub + HTTP local), aucune clé.
- **H-P5-5 PASS** — Shared Brain fait foi, FAISS dérivé, divergence
  vérifiée.
- **H-P5-6 PASS** — tâche planifiée prouvée par reçu ; cron refusé.
- **H-P5-7 PASS** — 47 triés, compte vérifié au gel et contre le
  design (écart 0).
- **H-P5-8 QUALIFIÉ** — 1 signal fork / 0 natif (R-A4).
- **H-P5-9 PASS** — manifeste + fiche dans `evidence/D-N051/p5/`.
- **H-P5-10 PARTIEL** — smoke sans l'original au niveau module
  (adapter + natif) ; le cycle complet du Runtime sans l'original =
  harnais du parent.
- **H-F8-2 PARTIEL** — mécanisme natif livré ; cycle complet =
  harnais du parent.
- **H-F8-4 PASS (construction)** — aucun daemon ajouté ni retiré par
  ce pas ; `run_ui.py` est une surface (D3).
- **H-F8-5 PASS** — aucun cron nulle part (adapter + natif) ; la
  présence est par heartbeat, pas par sondage.
- **H-F8-9 À JUGER** — adapter 17 fichiers / +1654 lignes ; natif
  4 modules ; plafonds jugés par le parent.

## Contraintes nommées du §2 (design pas 5)

- D1 gel confirmé, pas de re-gel. D2 adapter = moteur + plugins
  triés, serveur UI = surface. D3 serveur UI préservé, re-pointé,
  pas un daemon dans H-F8-4. D4 quatre fonctions en Rust dans le
  daemon unique. D5 tri des 47 écrit. D6 Shared Brain fait foi,
  FAISS = index. D7 scheduler dans le job loop, preuve par reçu,
  pas de cron. D8 base pas 3 présente, fonctions pas 4 = dépendance
  nommée, pas d'attente du merge du pas 4. D9 providers par le
  gateway `:31415` seul, LiteLLM et clés abandonnés. D10 plafonds
  D-N048, état visé 0 → 2. D11 bind re-appliqué verbatim sur `main`
  + re-pin (à Ryan). D12 famille/propriétaire portés tels quels.
  D13 greffe coupée (à Ryan, à l'intégration). D14 plus gros portage
  des 5 pas, 1 jour max, découpe moteur → plugins → scheduler.
  D15 coordination D-N053 pas B — le pas 5 développe agent-zero,
  D-N053 ne le re-développe pas.
