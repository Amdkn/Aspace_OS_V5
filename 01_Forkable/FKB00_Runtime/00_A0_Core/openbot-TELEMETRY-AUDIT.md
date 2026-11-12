# Audit télémétrie — openbot (D-N051 F8, pas 7)

**Gel :** `2b5b14f` (`2b5b14fc163fd12734ca871dddc68d8ffa31a1b7`), fork `Amdkn/openbot`.
**Méthode :** scan statique local sur le clone du gel + dépendances
(`package.json` / lockfiles) + capture réseau sur le portage natif.
**Le code search seul ne vaut pas preuve** (§0.4 : le code search API
a retourné 0 signal sur openbot/openmuse alors que le grep local
trouve une télémétrie réelle — deuxième occurrence de la leçon du pas 5).
Preuve grep : `logs/logs-telemetry-grep-all.log`.

## Déclencheurs (§D4) — tranchés un par un

- **1. Sink SDK → telemetry.copilotkit.ai → PostHog (défaut ON sur le desktop + le runtime, app_id=openbot toujours porté) : ABANDONNÉ.** Le transport télémétrie du SDK n'est pas porté ; le natif n'émet vers aucun sink. L'opt-out (COPILOTKIT_TELEMETRY_DISABLED / DO_NOT_TRACK) n'est pas repris — il n'y a rien à désactiver, il n'y a pas d'émetteur. Preuve grep : `telemetry.copilotkit.ai` cité dans desktop/src-tauri/src/desktop_telemetry.rs (1 occurrence) et dans des fixtures d'extension (tests) ; 0 SDK PostHog/Sentry dans les package.json.
- **2. Product telemetry openbot (opt-in serveur, app_id=openbot toujours porté) : ABANDONNÉ.** Module server/src/telemetry/product.ts (+ product-routes.ts, product-boundaries.ts) non porté ; le natif n'émet pas app_id=openbot. Diff gel...amont HEAD sur product.ts + otel.ts : 0 ligne (vérifié au triage 181).
- **3. Desktop telemetry (ON par défaut, événements oss.desktop.*) : ABANDONNÉ.** desktop/src/telemetry.ts + server/src/desktop-telemetry.ts non portés ; les événements de setup ne sont pas portés. La dérive 181 ajoute des événements setup_failed (f065d4a, 8aca2f4) — le déclencheur est abandonné, pas suivi.
- **4. Setup telemetry OpenDots : N/A.** Pas de setup telemetry dans openbot.
- **5. Export OTEL (otel.ts, OFF par défaut) : ABSENT, CONFIRMÉ.** server/src/telemetry/otel.ts présent au gel, OFF par défaut (« Nothing set means nothing is exported ») ; confirmé absent du natif, pas porté.
- **Extension navigateur (extension/src/background/network/telemetry.ts) : ABANDONNÉ.** Surface — son module télémétrie n'est pas porté (§D4).

## Dépendances

- **Aucun SDK PostHog / Sentry / analytics dans les `package.json`**
  (grep vérifié sur les 4 bots : 0 occurrence `posthog|@sentry` dans
  les `package.json`). La destination PostHog est prouvée par les
  docs et les requêtes HogQL, pas par un SDK direct — le transport
  est celui du SDK CopilotKit, non porté.
- **Variables d'opt-out non reprises** (`COPILOTKIT_TELEMETRY_DISABLED`,
  `DO_NOT_TRACK`, `CPK_TELEMETRY_ID`) : il n'y a rien à désactiver,
  il n'y a pas d'émetteur dans le natif.

## Capture réseau (preuve H-M4 / H-P7-7)

Le portage natif (`bots.rs` + `bots_proof.rs`) tourne sous `strace`
(`-e trace=connect`) : strace -f -e trace=connect sur bots_proof 7/7 : 2 connect(), tous 127.0.0.1 (stub gateway loopback), 0 non-loopback (logs-riginfinity-pas7-strace-run.log / -raw.txt).. Voir
`logs/logs-riginfinity-pas7-strace.log`. Les preuves natives
n'appellent que le stub gateway loopback (`127.0.0.1`, port éphémère)
et des fichiers temporaires — 0 appel sortant par défaut.

## Verdict

**PASS — télémétrie zéro** — les 5 déclencheurs sont tranchés, 0
émetteur dans le natif, 0 appel sortant par défaut. Les déclencheurs
abandonnés restent dans les forks (hors du chemin d'exécution natif) ;
ils ne sont pas portés, pas désactivés par une variable — ils sont
absents.
