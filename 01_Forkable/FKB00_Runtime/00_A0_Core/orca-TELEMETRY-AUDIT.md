# Audit télémétrie zéro — orca (D-N053 pas F2)

**Module :** `Amdkn/orca`, gel `708aca6` (v1.4.214), adapter
`aspace-orca-adapter` (voir `orca-ADAPTATION.md`).
**Date :** 2026-11-13. **Verdict : 0 appel sortant par défaut.**

## Méthode

Scan statique du code au gel + lecture du `package.json` /
`pnpm-lock.yaml` + capture réseau bornée (strace du smoke :
`orca-ide --help`, `--version`, `worktree list --json`, preuve client
`orcad` contre stub local — voir `logs-strace-adapte.log`).
Chaque déclencheur du Discover §6 est tranché ci-dessous.

## Scan statique

- `grep -r "posthog" src/main/telemetry/*.ts package.json` : **27
  occurrences** — un SDK de télémétrie est présent, contrairement à
  herdr/herdr-core : **`posthog-node` ^5.52.5** en dépendance
  (`package.json` : 1, `pnpm-lock.yaml` : 3). Pas de Sentry.
- `src/main/telemetry/` : `client.ts`, `posthog-transport.ts`,
  `posthog-client-start.ts`, `consent.ts`, `opt-out-capture.ts`,
  `validator.ts`, `burst-cap.ts`, `event-sampling.ts`.
- `client.ts:21` : `const TELEMETRY_ENABLED = true` + `BUILD_IDENTITY`
  (`stable` / `rc` / null, via `ORCA_BUILD_IDENTITY`) — mais l'émission
  exige les DEUX : build officiel ET consentement explicite
  (`resolveConsent`, `consent.ts`) ; sans `settings.telemetry.optedIn`,
  état `pending_banner` (pas de transmission tant que la bannière n'est
  pas résolue). Builds contributeurs « fail closed ».
- `consent.ts:52-68` (`resolveEnvOverride`, vérifié au fichier) :
  `DO_NOT_TRACK` vrai → `disabled` (`do_not_track`) ;
  `ORCA_TELEMETRY_DISABLED` vrai → `disabled` (`orca_disabled`) ;
  toute variable CI non vide → `disabled` (`ci`). **L'override env bat
  tout choix stocké** (« Env/CI overrides beat any stored choice »).
- `posthog-transport.ts:91` : le transport PostHog émet par `fetch`
  (`getMainHttpClient().fetch`, `credentials: 'omit'`). Aucun client
  HTTP générique en dépendance directe (ni axios, ni undici, ni sentry)
  — le réseau passe par `fetch` natif / `ws` / `ssh2` /
  `electron-updater` / PostHog.
- `config/dev-app-update.yml` : `provider: github, owner: stablyai,
  repo: orca` (feed auto-update).
- Ce que la télémétrie ne transmet jamais (doc amont, vérifiée au
  fichier) : contenus de fichiers, prompts, sorties d'agents, sorties
  de terminal, noms de repos, branches, URLs, chemins, messages de
  commit, messages d'erreur bruts, stacks, comptes, emails, IP,
  hostname, username. ID anonyme local aléatoire (`installId`).
  Rétention : défaut du plan PostHog Cloud, pas de fenêtre
  personnalisée.

## Déclencheurs (Discover §6) — tous tranchés

| # | Émetteur | Déclencheur | Cible | Statut amont | Décision adapter |
|---|---|---|---|---|---|
| T1 | PostHog, usage anonyme | **Builds officiels seulement** (`TELEMETRY_ENABLED = true` + `BUILD_IDENTITY` stable/rc + write key injectée en CI) **ET consentement explicite** (`resolveConsent` — sans `optedIn`, `pending_banner`) | PostHog Cloud, région US | OFF jusqu'au choix explicite (fail-closed) | **Forcé OFF** par l'adapter (D-F2-5) : `ORCA_TELEMETRY_DISABLED=1` **et** `DO_NOT_TRACK=1` dans la config embarquée + lanceur, vérifiés au fichier ET par le smoke. |
| T2 | Auto-update (electron-updater) | **Automatique** : check de fond toutes les 24 h (`AUTO_UPDATE_CHECK_INTERVAL_MS = 24h`, retry 1 h, max 6 h, `updater-scheduling.ts` : `scheduleAutomaticUpdateCheck`) | GitHub releases `stablyai/orca` (feed `config/dev-app-update.yml`) | ON par défaut ; téléchargement + installation après nudge | **Coupée par le chemin de lancement** (D-F2-5) : config embarquée `autoDownload = false` + `autoInstallOnAppQuit = false` ; le lanceur CLI n'appelle jamais `scheduleAutomaticUpdateCheck` — le check n'est planifié que par le processus principal Electron (`updater-setup.ts:256/267/269`, `app.on` / `powerMonitor`), jamais démarré par l'adapter ; commande de mise à jour exclue du contrat. Vérifié par capture : 0 connexion vers les releases `stablyai/orca`. |
| T3 | Catalogue de plugins | Install / update explicite d'un plugin du catalogue officiel ou communautaire | Catalogue + PostHog (nom public `publisher.id` + version rapportés) | Manuel ; plugins Git URL / local / dossier dev **jamais rapportés** | **Hors contrat adapter** (commande non exposée comme voie de catalogue ; `plugin install/update` restent des commandes opérateur explicites, hors surface V5). |
| T4 | Agents pilotés (Claude Code / Codex) | Lancement d'agent explicite par l'utilisateur | Fournisseurs des agents (leurs propres appels, leurs propres clés) | Manuel | **Hors contrat adapter — l'adapter n'hérite pas d'une coupure réseau des agents** : orca ne coupe pas le réseau de ses agents, consigné dans la fiche. |
| T5 | Hôtes SSH / VMs cloud / serveur pairé (`orcad` serve) | Choix d'hôte explicite (`Choose a host`) : SSH (`ssh2`), VM cloud par worktree, serveur pairé | Hôte SSH / VM cloud / serveur pairé (HTTP+WS, loopback par défaut, Tailscale accepté) | Opt-in explicite | **Hors contrat adapter** (pas de lancement d'`orcad` par V5, D-F2-2) ; `--bind 0.0.0.0` / `allowPublic` exclus. |
| T6 | Pairing mobile | QR code explicite (`mobilePairing`, `orcad-start-contract.ts`) | App mobile pairée | Manuel | **Hors contrat adapter** (pairing non exposé). |
| T7 | Navigateur embarqué (`agent-browser`) + SDK Linear/Jira | Usage explicite (browser Computer Use, tickets Linear/Jira) | Sites visités / `linear.app` / Atlassian (tokens utilisateur) | Manuel | **Hors contrat adapter**. |
| T8 | `serve-sim`, `ws` | Serveur local `orcad` (loopback) | `127.0.0.1` uniquement par défaut | Local | **Vérifié à la capture (strace du smoke)** : 12 lignes `AF_INET`, toutes `sin_addr=inet_addr("127.0.0.1")` — **0 `AF_INET` sortant hors loopback** (`logs-strace-adapte.log`). |

## Capture réseau (bornée)

Chemins du smoke sous `strace -f -e trace=network` : `orca-ide
--help`, `--version`, `worktree list --json`, preuve client `orcad`
(stub local `127.0.0.1`, port éphémère) — **0 `AF_INET` hors
loopback** (12 `AF_INET`, 9 `sin_addr 127.0.0.1`, 3 `socket()` sans
adresse ; 10 `connect()`, tous loopback/unix). Aucune connexion vers
PostHog Cloud ni vers les releases `stablyai/orca`.

## Conclusion

**0 appel sortant par défaut.** Le seul émetteur automatique
potentiel (T1, PostHog) est fail-closed amont ET coupé par l'adapter
(`ORCA_TELEMETRY_DISABLED=1` + `DO_NOT_TRACK=1`, forcés et vérifiés) ;
le second (T2, auto-update) est coupé par le chemin de lancement
(jamais `scheduleAutomaticUpdateCheck`). Le reste est manuel et hors
contrat. Ré-audit à chaque changement de commit gelé ou d'adapter,
et au minimum à chaque transition d'état (D3).
