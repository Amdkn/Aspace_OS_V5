# Audit télémétrie — herdr-app (D-N048 V3a)

**Fork :** `Amdkn/herdr-app`, gel `b1a2a67`. **Télémétrie présente dans l'amont, coupée par contrat.**

## 1. Scan statique

- Module dédié `src/telemetry.rs` (742 lignes) : **un petit rapport anonyme par installation et par jour UTC** — « Never what's in a terminal, never from the core, never free text: every field is a number, a bucket, a yes/no or a name from a list the app ships ».
- Hôte : `https://telemetry.herdr.dev/v1/report` (`telemetry.rs:34`) ; second hôte `https://telemetry.herdr.dev/v1/feedback` (`feedback.rs:9`, envoi de retour utilisateur — action explicite, jamais invoqué par l'adapter).
- Appels : `telemetry::start(settings::telemetry_setting(&person))` au démarrage (`main.rs:150`) ; `telemetry::clock()` (`main.rs:124`) ; `telemetry::quit()` (`main.rs:181`) ; fonction `telemetry` exposée aux mods (`mods.rs:940`, lecture du statut).
- **Aucun SDK télémétrie tiers** (pas de PostHog/Segment/Sentry) : module maison, `ureq`/`http` maison probable — le rapport est construit et envoyé par le module lui-même.

## 2. Consentement et interrupteurs

- **Défaut ON** : `settings::telemetry_setting` vaut `true` sans fichier person (`settings.rs:684`, `unwrap_or(true)`) ; `settings.json` `"telemetry": false` coupe et supprime l'id + la file non envoyée.
- **Interrupteurs d'exécution** (un seul suffit) : `DO_NOT_TRACK` (véridique), `HERDR_TELEMETRY=0`, CI. `env_off()` les lit au démarrage.
- **Seuls les builds release envoient** (`HERDR_APP_RELEASE`) — ou un build pointé vers un serveur de test (`HERDR_TELEMETRY_URL`) : « a build from source and the sandbox collect and show, but never send ».
- **L'adapter force `DO_NOT_TRACK=1` + `HERDR_TELEMETRY=0`** et ne construit que du debug (`cargo test --locked`, jamais release). Double barrière : interrupteurs + absence de `HERDR_APP_RELEASE`.

## 3. Preuve d'exécution

- **Smoke test adapter vert** (`bash aspace-herdr-app-adapter/smoke_test.sh`, 2026-11-09 18:26 EST) : `smoke herdr-app OK (version 0.1.14, --help, --skill)` — binaire debug, maison scratch (`HERDR_APP_HOME`), `DO_NOT_TRACK=1` + `HERDR_TELEMETRY=0` forcés.
- Le binaire debug ne peut pas envoyer (pas de `HERDR_APP_RELEASE`), et les interrupteurs coupent la collecte elle-même : **zéro appel sortant possible par construction**, pas seulement par absence observée.

## Conclusion

**Télémétrie zéro par contrat** : module amont réel mais coupé à deux niveaux (interrupteurs d'env + build non-release). L'adapter n'expose que des sous-commandes qui parlent seulement (`--help`, `--skill`, `--version`, `check`/`types`).
