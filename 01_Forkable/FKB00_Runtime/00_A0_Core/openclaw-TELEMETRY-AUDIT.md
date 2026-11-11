# Audit télémétrie — openclaw (D-N048 V3b)

**Fork :** `Amdkn/openclaw`, gel `ce7788f`. **Télémétrie présente dans l'amont, coupée par contrat (défaut + interrupteurs).**

## 1. Scan statique

- **Aucun SDK télémétrie tiers** : ni PostHog, ni Segment, ni Sentry, ni Mixpanel, ni Amplitude — dans `package.json` (134 dépendances), ni dans `pnpm-lock.yaml` (grep vide). Le seul SDK d'observabilité est `@opentelemetry/sdk-node` 0.223.0 (OTel, export vers un collecteur **configuré par l'opérateur**, jamais un endpoint vendeur).
- **Module maison dédié** `src/infra/telemetry.ts` (460 lignes) : statistiques d'usage anonymes + vérification de mise à jour quotidienne. Endpoint par défaut : `https://telemetry.openclaw.ai/api/latest-version` (`telemetry.ts:36`).
- **Contenu du payload** (`TelemetryPayload`, `telemetry.ts:57-69`) : `schema: 1`, version, plateforme, Node, surface (`gateway` | `cli`), fonctionnalités (canaux publics, familles de fournisseurs, plugins publics, nombre de plugins activés, sessions dernières 24 h). Aucun texte libre, aucun secret, aucun contenu de conversation.
- **Comptage d'installations** (`telemetry-installation-count.ts`) : requête POST **sans payload**, un seul en-tête de comptage, une fois par jour au plus.
- **Second canal** : `src/cli/daemon-cli/update-run.ts` → `sendUpdateResultTelemetry` (résultat de mise à jour) ; `src/cli/plugins-cli.runtime.ts` → `emitMarketplaceFeedTelemetry` (émission interne d'événements de flux marketplace, pas d'envoi réseau direct dans la fonction — le transport passe par le module télémétrie).
- **OTel** (`diagnostics.otel`, `src/config/zod-schema.logging.ts:18-22`) : endpoint/traces/metrics/logs tous optionnels, sans défaut — aide en ligne : « Keep disabled unless your collector endpoint and auth are fully configured » (`src/config/schema.help.runtime.ts:419`).

## 2. Consentement et interrupteurs

- **Statistiques de fonctionnalités : OFF par défaut.** `telemetry.enabled` est un booléen optionnel, sans défaut (`src/config/zod-schema.telemetry.ts`) ; aide : « Disabled by default and always disabled when DO_NOT_TRACK=1 ». Raison `never-asked` tant que l'opérateur n'a pas consenti (`telemetry.ts:236-252`).
- **DO_NOT_TRACK** : `DO_NOT_TRACK=1` ou `true` coupe les statistiques **et** le comptage d'installations (`isDoNotTrackEnabled`, `telemetry.ts:175-178`).
- **CI** : `CI` véridique coupe tout envoi vers l'endpoint de production (`isAutomatedEnvironment`, `telemetry.ts:104-117`) — « someone else's pipeline should not report to us on every job ».
- **Vérification de mise à jour désactivable** : `config.update.checkOnStart === false`, `OPENCLAW_NO_AUTO_UPDATE`, mode Nix — coupe aussi la télémétrie (`isUpdateCheckDisabled`).
- **Endpoint surchargeable** : `OPENCLAW_TELEMETRY_ENDPOINT` (défaut `https://telemetry.openclaw.ai/api/latest-version`).
- **Sous-commande dédiée** : `openclaw telemetry show` (aperçu local de la requête, sans envoi), `openclaw telemetry on/off` (consentement écrit dans la config, horodaté).
- **L'adapter force `DO_NOT_TRACK=1` + `CI=1`** et n'expose que des sous-commandes qui parlent seulement (`--version`, `--help`, `telemetry show`). Double barrière : interrupteurs + surface sans démarrage de gateway.

## 3. Preuve d'exécution (2026-11-10, VM de travail)

- `node openclaw.mjs --version` (launcher seul, sans build) : `OpenClaw 2026.11.2 (ce7788f)` — aucun réseau.
- **Build complet impossible sur cette VM** : `pnpm build` (tsdown) exige un pic ~4,7 Go (mesuré amont, `scripts/tsdown-build.mts:646-651` : une tranche 5 Gio passe, une tranche 4 Gio est tuée) ; heap résolu ici 3 502 Mo. `--help` et `telemetry show` ont donc été prouvés **depuis les sources via tsx** (`node --import ./scripts/tsx.mjs src/entry.ts` — même mécanisme que les scripts amont), jamais de gateway, jamais d'appel modèle.
- **`telemetry show` réel, `DO_NOT_TRACK=1` + `CI=1`, HOME scratch, stdin fermé** :
  ```
  Feature stats: disabled
  Installation counting: disabled
  Reason: disabled in an automated environment (CI is set)
  Endpoint: https://telemetry.openclaw.ai/api/latest-version
  Last ping: never
  Request: none (disabled in an automated environment (CI is set))
  ```
  Aucune requête construite, aucun envoi — `Request: none`.
- **Preuve réseau** : smoke test en namespace sans interface (`unshare -n`, mode `--netproof`) : `--version`, `--help`, `telemetry show` verts sans interface réseau (2 min 22 s) — le CLI de contrat n'a besoin d'aucun réseau.
- **Piège d'exécution consigné** : sans stdin fermé (`< /dev/null`), `telemetry show` (comme `telemetry --help`) attend indéfiniment une entrée interactive et ne termine jamais ; le smoke test ferme stdin. Cause exacte non établie (chargement de config / invite de premier lancement), mais le comportement est reproductible et contourné par contrat.

## Conclusion

**Télémétrie zéro par contrat** : module maison réel (statistiques anonymes + comptage d'installations + vérification de mise à jour quotidienne vers `telemetry.openclaw.ai`), mais **désactivée par défaut** (opt-in explicite), **coupée par `DO_NOT_TRACK=1` et `CI=1`**, OTel sans endpoint par défaut. L'adapter n'expose que des sous-commandes qui parlent seulement et force les deux interrupteurs.
