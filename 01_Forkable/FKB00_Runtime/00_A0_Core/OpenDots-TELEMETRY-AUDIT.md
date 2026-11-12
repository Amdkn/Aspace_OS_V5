# Audit télémétrie — OpenDots (D-N051 F8, pas 7)

**Gel :** `d4214af` (`d4214aff10f066911f3253cb3cb870764cd51a9f`), fork `Amdkn/OpenDots`.
**Méthode :** scan statique local sur le clone du gel + dépendances
(`package.json` / lockfiles) + capture réseau sur le portage natif.
**Le code search seul ne vaut pas preuve** (§0.4 : le code search API
a retourné 0 signal sur openbot/openmuse alors que le grep local
trouve une télémétrie réelle — deuxième occurrence de la leçon du pas 5).
Preuve grep : `logs/logs-telemetry-grep-all.log`.

## Déclencheurs (§D4) — tranchés un par un

- **1. Sink SDK → telemetry.copilotkit.ai → PostHog (défaut ON) : ABANDONNÉ.** docs/TELEMETRY.md : « SDK usage telemetry is enabled by default ». Événements intelligence_signup, oss.runtime.instance_created, oss.runtime.copilot_request_created, accessibility_title OpenDots. Preuve du sink : requêtes HogQL versionnées docs/telemetry/*.hogql.sql. Transport non porté ; 0 SDK PostHog/Sentry dans les package.json.
- **2. Product telemetry openbot : N/A.** Pas de product telemetry dans OpenDots.
- **3. Desktop telemetry : N/A.** Pas de desktop telemetry dans OpenDots.
- **4. Setup telemetry (src/server/setup-telemetry.ts + src/client/setup-telemetry.ts) : ABANDONNÉ.** Événements step_viewed, setup_abandoned, activated, setup_failed ; état persisté (installationId UUID, file max 256) ; le client poste sur /api/setup-telemetry avec keepalive. Non portée.
- **5. Export OTEL : N/A.** Pas d'export OTEL dans OpenDots.

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
