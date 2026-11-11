# Audit télémétrie — D-N052 R2 (prime-agent) — A8

**Mission :** D-N052 R2 (= F8 pas 6). **Gel :** `74591cd` (fork `Amdkn/prime-agent`).
**Méthode :** code search + dépendances + surfaces de lecture locale + déclencheurs
par défaut ON (leçons pas 4 et pas 5 : un code search à 0 résultat n'est pas un
audit ; un déclencheur par défaut ON existe dans le fork ; une surface de
lecture locale existe). **Capture réseau live : NON réalisée** (aucun binaire
release construit sur cette VM — voir réserve R-A1) ; l'audit est statique +
dépendances, et chaque déclencheur est prouvé par le code + les tests du fork.

## T1 — Analytics produit (le déclencheur par défaut ON) — ABANDONNÉ

- **Preuve :** `crates/pa-telemetry/src/sinks/analytics.rs:20` :
  `ANALYTICS_ENDPOINT = "https://api.primeintellect.ai/api/v1/agent-analytics/events"`,
  client reqwest, timeout 1,5 s, format `{installation_id, events: [{id, name,
  timestamp, properties}]}` ; le backend plateforme relaie vers PostHog.
- **Défaut :** `crates/pa-core/src/session_engine/telemetry/status.rs:12` —
  `TelemetrySwitch::Default => true` (« Nothing set: on »). La télémétrie est
  **ON par défaut** quand rien n'est posé.
- **Gating build :** `telemetry_endpoint()` (status.rs:86) ne renvoie l'endpoint
  qu'en build release (`!cfg!(debug_assertions)`) — en debug (`cargo test`,
  dev), l'endpoint est `nowhere`, les tests et le dev n'atteignent jamais
  l'analytics produit. **En release, le POST part.**
- **Opt-outs :** `PI_OFFLINE` / `DO_NOT_TRACK` forcent OFF ;
  `PRIME_AGENT_TELEMETRY` force dans un sens ou l'autre ; puis settings
  `telemetry.enabled` ; puis le défaut (ON).
- **Preuve historique :** la régression #3288 (documentée dans
  `AGENTS.md` du fork, section « Performance and the critical path ») — le
  flush télémétrie au démarrage était attendu sur le chemin de lancement
  interactif : le POST analytics (un vrai aller-retour HTTPS, ~157 ms)
  tournait avant la première frame. Le correctif l'a déplacé vers le
  worker d'arrière-plan + le test `the_startup_flush_never_blocks_the_first_frame`.
  **Le POST existe donc en release, en arrière-plan, fire-and-forget.**
- **Verdict : ABANDONNÉ avec le fork.** 0 signal dans le portage natif :
  le seul sink câblé est le Noop (opt-out) ; aucun endpoint, aucune
  création d'install-id. Garde structurelle : le test
  `no_telemetry_endpoint_in_the_adapter` (adapter) et
  `no_telemetry_endpoint_in_the_native_modules` (RigInfinity) scannent
  les sources et échouent si l'URL apparaît.

## T2 — Endpoints de modèles (inférence, pas télémétrie) — REMPLACÉS PAR LA GATEWAY

- **Preuves :** `crates/pa-ai/src/` — `https://api.openai.com`,
  `https://api.anthropic.com`, `https://api.pinference.ai`,
  `https://api.individual.githubcopilot.com`, `https://bedrock-runtime.*.amazonaws.com`,
  `https://chatgpt.com` (et autres). Ce sont les endpoints d'inférence des
  fournisseurs (appels modèles, clé-gatés, initiés par l'utilisateur).
- **Verdict : PAS DE LA TÉLÉMÉTRIE.** Le portage natif ne les porte pas :
  le seul client modèle est le `GatewayProvider` (pas 5, D9) vers
  `http://127.0.0.1:31415/v1/chat/completions`, chaîne modelPool. Aucune
  clé fournisseur lue.

## T3 — Contrôle de mise à jour (update check) — MANUEL UNIQUEMENT, PAS UN DÉCLENCHEUR

- **Preuves :** `crates/pa-cli/src/command_registry.rs:208` —
  `update [--check] [--nightly|--stable]` ; `installer_update.rs` et
  `update_flow/plan.rs` appellent `latest_release` uniquement depuis le
  flux manuel. Aucun appel automatique / en arrière-plan trouvé dans
  `pa-agent`, `pa-core` (session_engine), `pa-daemon` (recherche
  `update_check|check_for_update|check_update` : 0 fichier). Les `https://`
  de `update/download.rs` sont des URLs d'exemple dans les tests.
- **Verdict : PAS UN DÉCLENCHEUR PAR DÉFAUT.** La mise à jour est une
  commande manuelle ; rien ne la déclenche au démarrage. Non portée
  (le portage natif n'a pas de mécanisme de mise à jour).

## T4 — `install.sh` distant du README (`curl ... | sh`) — JAMAIS EXÉCUTÉ

- **Preuve :** le README du fork documente une installation par
  `curl ... | sh` (script distant). **Jamais exécuté en R2** (A8) — ni
  dans l'adapter, ni dans le portage, ni dans les tests.
- **Verdict : NON EXÉCUTÉ, documenté.**

## T5 — Surfaces de lecture locale — LOCALES, SANS RÉSEAU

- **FileSink** (`pa-telemetry`, README) : miroir local JSONL de
  transparence à `<agentDir>/telemetry.jsonl` — lecture/écriture locale,
  aucun envoi réseau.
- **install_id** (`pa-telemetry/src/install_id.rs`) : `<agentDir>/telemetry.json`
  `{version, installationId}`, création exclusive 0600, validé au
  chargement (pseudonyme, pas d'identité utilisateur).
- **Verdict : LOCALES.** Le portage natif n'écrit ni miroir JSONL ni
  install-id (aucun fichier `telemetry.json*` créé par le code natif).

## T6 — Messagerie pair-à-pair du daemon — LOCALE UNIQUEMENT

- **Preuves :** `crates/pa-daemon/README.md` — transport direct-attach
  (tickets single-use, TTL 10 s), messagerie worker-to-worker par
  socket superviseur, store de sessions append-only JSONL. Tout est
  local (sockets Unix / 127.0.0.1), aucun endpoint externe.
- **Verdict : LOCAL.** Le portage natif ne reprend que la référence
  de l'interface (A1) ; aucune socket pair-à-pair n'est recréée.

## T7 — Dépendances réseau du workspace — INVENTAIRE

- `pa-telemetry` : `reqwest` (le sink analytics, T1).
- `pa-ai` / `pa-models` : clients HTTP fournisseurs (T2).
- `pa-core` : `reqwest` via `pa-telemetry` et les providers.
- **Adapter :** std only, aucune dépendance — aucun client HTTP possible.
- **Portage natif (RigInfinity) :** `reqwest` est une dépendance du
  workspace (utilisée par le `GatewayProvider` vers 127.0.0.1:31415
  uniquement) ; les modules `prime_agent_*` n'appellent aucun endpoint
  externe (garde structurelle T1).

## Verdict global (H-M4)

**Télémétrie zéro dans le natif.** Le seul signal sortant par défaut du
fork (T1, analytics PostHog en release) est abandonné avec le fork.
Les endpoints de modèles sont remplacés par la gateway locale. Le
contrôle de mise à jour est manuel. Aucune surface de lecture locale
n'envoie quoi que ce soit.

## Réserves

- **R-A1 — Pas de capture réseau live.** Aucun binaire release du fork
  n'a été construit sur cette VM (workspace 10 crates, coût prohibitif
  + risque OOM) ; la preuve est statique (code + tests du fork, dont
  `the_startup_flush_never_blocks_the_first_frame`). La capture live
  reste un acte machine (PC du Capitaine) si le 13e l'exige.
- **R-A2 — Suite du fork non re-courue en entier.** La suite
  `cargo test --workspace` du fork n'a pas été re-courue (même raison).
  Le crate `pa-telemetry` a été testé isolément (voir fiche).
