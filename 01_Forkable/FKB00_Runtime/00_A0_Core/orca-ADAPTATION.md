# Fiche d'adaptation — orca (D-N053 pas F2)

**Adresse :** `fiber:a0:orca`
**Manifeste :** `orca.manifest.json` (même domicile)
**Audit télémétrie :** `orca-TELEMETRY-AUDIT.md` (même domicile)
**Statut :** état 1 Adapté (pas F2, PR V5 à juger par le 13e)
**Licence :** MIT

## Commit gelé

- **Fork :** `Amdkn/orca` (parent `stablyai/orca`, MIT, branche `main`).
- **Gel : `708aca6`** — version 1.4.214, 2026-11-08T01:59:32Z (« fix(terminal):
  never type a colour reply into the shell after the program that asked has
  exited (#37402) »).
- **Dérive au gel : 1 178** commits gel → amont HEAD `91b3f12`
  (2026-11-12T23:12:55Z), re-mesurée **1 205** en fin de pas (amont HEAD
  `41666c7`, 2026-11-13T01:17:39Z — l'amont pousse toutes les quelques
  minutes, +27 en ~2 h). **Tout commit amont ultérieur exige un amendement
  de design**, jamais un fast-forward silencieux (D-F2-4). Revisite par
  signal **quotidienne** tant que la dérive dépasse 20.
- **Triage versé (H-F2-7) :** liste exhaustive par chemin jointe à
  l'évidence (`drift-perimeter-list.txt` / `drift-perimeter-final.json`,
  145 lignes = 3 en-tête + **142 commits distincts** : `src/cli` 115,
  `src/main/orcad` 39, `src/main/telemetry` 10, `src/shared` filtré 7).
  Triage borné aux changements d'API/CLI/`orcad` (patron openbot 181 /
  herdr-core 53) : aucun des faits relevés ne touche le contrat CLI, le
  protocole `orcad` ni le consentement télémétrie — la surface adapter
  est stable au gel.
- **Tailles (E-F2-2) :** arbre au gel ~286 Mo (292 985 Ko, 39 200 fichiers) ;
  dépôt objet du fork 2 233 158 Ko (historique + ~100 branches
  `release-prep` héritées + tags) ; amont 2 752 428 Ko. Clone partiel
  obligatoire (`--filter=blob:none`).
- **Répertoires non-code exclus du clone partiel (E-F2-2, nommés) :**
  `docs/assets`, `docs/site/public`, `resources/onboarding`,
  `config/patches`, `src/renderer/src/i18n/locales`.

## Adapter

- **Dossier :** `aspace-orca-adapter/` (README + contrat JSON + config
  embarquée + lanceur + smoke test shell + preuve client `orcad`),
  commit **`5d15464`** sur le fork (parent = gel `708aca6`, vérifié à
  l'API). **Seul code A'Space du fork** — le code amont est byte-identique au gel (H-F2-2). Bind re-appliqué verbatim au-dessus (`8beacf3`,
  `aspace-plugin.json` 24 lignes, blob `736c2e1b4ac786ea848abf6379adc936518755bc`
  byte-identique au bind `b659760` sur `aspace-v5-native`) ; **pin = commit
  adapter `5d15464`**. Fork `main` = bind `8beacf3` (vérifié à l'API).
- **Forme (D-F2-1, D-F2-2, D-F2-3) — CLI-contrat (A) + client `orcad` (B),
  skills (C) en référence versionnée :** orca est une application
  Electron + CLI + daemon, pas une bibliothèque — ni la CLI seule ni le
  client `orcad` seul ne couvrent la surface. Forme A : contrat CLI
  (`out/cli/index.js`, `bin: orca`), exposé **`orca-ide` sur Linux**
  (collision GNOME, voir ci-dessous). Forme B : client du protocole
  `orcad` (readiness, WS loopback, stop, idle-exit) — preuve 4/4 contre
  stub local. Forme C : les 11 skills du gel nommées + mécanisme
  version-matched (guide chargé depuis l'exécutable) ; les guides
  complets de 289 lignes ne sont pas embarqués.
- **Le serveur `orcad` reste un serveur de l'opérateur, externe à V5
  (D-F2-2, MAJEURE) :** V5 ne lance jamais `orcad`, ne le supervise
  jamais, ne le réintroduit jamais comme service — `orcad` ne tourne que
  si l'opérateur le lance hors V5, comme le serveur herdr (TUI) au pas F1.
  **Exclus et vérifiés absents de la surface :** `--bind 0.0.0.0`,
  `allowPublic`, pairing mobile par défaut, toute exposition réseau non
  loopback, `orca serve` / `orca open` comme service V5, toute commande
  de mise à jour, `orchestration task-create/dispatch/check` pour les
  handoffs pleins.
- **Collision Linux (E-F2-6) :** sur Linux, `orca` nu = le lecteur
  d'écran GNOME (`/usr/bin/orca`) — hors terminaux Orca, le contrat
  expose **`orca-ide`, jamais `orca` nu** (sinon la synthèse vocale
  démarre sur la machine de l'utilisateur). Lanceur :
  `launch-orca-ide.sh`.
- **Interrupteurs forcés (D-F2-5, H-F2-4) :**
  `ORCA_TELEMETRY_DISABLED=1` **et** `DO_NOT_TRACK=1` — config embarquée
  `aspace-orca-adapter/config.json` + lanceur, vérifiés au fichier ET par
  le smoke. Ce sont les kill switches reconnus par `resolveEnvOverride`
  dans `src/main/telemetry/consent.ts` (priorité sur tout choix stocké ;
  sans consentement explicite l'état amont est déjà `pending_banner`).
  **Auto-update (T2) coupée par le chemin de lancement :** l'adapter
  force `autoDownload = false` et `autoInstallOnAppQuit = false` et son
  chemin de lancement n'appelle jamais `scheduleAutomaticUpdateCheck` —
  le check de fond 24 h (`AUTO_UPDATE_CHECK_INTERVAL_MS`,
  `updater-scheduling.ts`) n'est planifié que par le processus principal
  Electron (`updater-setup.ts`, `app.on` / `powerMonitor`), que le
  lanceur CLI ne démarre jamais. Vérifié par capture réseau : 0
  connexion vers les releases `stablyai/orca`.
- **Couture orca ↔ herdr actée absente (D-F2-2) :** 0 occurrence de
  `herdr` dans orca au gel ; protocoles distincts (HTTP+WS `orcad` contre
  NDJSON herdr et trames `hc`) ; PTY distincts (`node-pty`+xterm contre
  `portable-pty`). Aucun lien de code orca → herdr n'est inventé ; le
  cockpit « Herdr × Orca × T3Code » reste une juxtaposition déclarative,
  et le natif consomme les deux voies séparément.
- **Revendication 31415 (D-F2-6) :** le bind revendique
  `universal_harness_gateway_31415` +
  `http://127.0.0.1:31415/v1/chat/completions` — qualifiée côté A'Space
  (FreeCloud, `aspace_freecloud_gateway.py`), pas une capacité du gel :
  orca ne connaît pas 31415 (0 occurrence) et ne sert rien sur ce port.
  Bind re-appliqué verbatim, non modifié au pas F2.
- **Les agents pilotés (Claude Code / Codex) gardent leurs propres appels
  réseau (T4) :** orca ne coupe pas le réseau de ses agents — consigné,
  pas hérité.
- **Smoke test :** `bash aspace-orca-adapter/smoke_test.sh` (CLI construite
  `out/cli/index.js` : `--help` exit 0, `--version` message amont
  documenté, `worktree list --json` → JSON `runtime_unavailable` sans
  runtime, interrupteurs + coupure auto-update + interdits vérifiés,
  preuve client `orcad` 4/4). Ne lance jamais `orcad`, jamais l'app
  Electron, ne touche jamais la vraie config.
- **`--version` sur un build CLI seul :** répond « Could not determine
  the Orca version for this build. » (exit 1) — le lecteur de version
  (`src/cli/cli-version.ts`) lit `out/package.json`, que seul le packaging
  Electron complet y dépose. Comportement amont, assert tel quel par le
  smoke, pas un défaut de l'adapter.
- **Règles maison amont respectées (AGENTS.md) :** commits lowercase
  conventional, pas de ligne AI co-author ; `pnpm` retrouvé dans le cache
  corepack (12.18.0, le binaire 12.14.0 du `packageManager` n'est plus
  dans le PATH — shim `~/workspace/.bin/pnpm`) ; hook pre-commit
  `lint-staged` actif (oxlint 0 erreur après correction des accolades
  `proof.mjs`, oxfmt appliqué) ; aucune modification du code amont,
  aucun fichier de release touché. Le travail se fait dans le fork Amdkn,
  pas vers l'amont canonique.

## Tests au gel et sur le fork adapté

- **Au gel `708aca6` (baseline, `logs-suite-baseline-gel.log`) :**
  vitest borné au périmètre adapter (263 fichiers : `src/cli`,
  `src/main/orcad`, `src/main/telemetry`, `src/shared/*`
  consent/orcad-*/telemetry-*) : **2 094 passés / 1 échec / 29 ignorés ;
  2 fichiers en échec**. Exclus nommément (§4 du design) : e2e
  Playwright/Electron, `mobile/`, Windows/macOS, `performance-contracts`,
  `preflight-*`, `release-*`.
- **Sur l'adapté `5d15464` (`logs-suite-adapte.log`) :** même périmètre,
  **2 094 passés / 1 échec / 29 ignorés ; 2 fichiers en échec —
  chiffres identiques, test pour test.** 0 régression nette, mais le
  test en échec diffère d'un run à l'autre (les deux sont des flakes
  pré-existants, voir ci-dessous).
- **Typecheck borné :** `tc:cli` vert (exit 0) ; `tc:node` vert (exit 0)
  — premier run en échec sur 12 erreurs `Cannot find module
  .../renderer/src/i18n/locales/*.json` : le clone partiel exclut ce
  répertoire non-code par sparse-checkout (E-F2-2) ; après récupération
  des 11 blobs à la demande (`sparse-checkout add`, 16 Mo) puis
  restauration de l'exclusion, vert. **Lint borné :** `oxlint` sur le
  périmètre adapter, **0 warning / 0 erreur (790 fichiers)**.
- **Smoke adapter + preuve client :** verts (`SMOKE_EXIT:0`,
  `PROOF 4/4`, `PROOF_EXIT:0`). **Capture réseau (strace du smoke) :**
  12 lignes `AF_INET`, toutes `127.0.0.1` — **0 `AF_INET` sortant hors
  loopback** (T8).

## Les 3 rouges, liste exacte (décision du coordinateur à demander — rien exclu de ma propre initiative, H-F2-3)

1. **`src/cli/index-omitted-host-scope-selectors.test.ts` — hook
   `beforeAll` timeout 60 s (fichier en échec, 7 tests skipped, 0 test
   en échec), baseline ET adapté, identique.** Passe seul 7/7 en 41 s.
   Cause : charge parallèle (263 workers, 1,5 CPU) — le hook dépasse
   60 s quand la machine est saturée. Pré-existant au gel, 0 imputable
   à l'adapter.
2. **`src/cli/plugin-authoring/plugin-release-entry.test.ts` —
   « explains why there is no entry outside Git or before the first
   commit » : échec BASELINE seulement** (attendu 'not in a Git
   repository', reçu 'no catalog release entry: HEAD has no installable
   plugin here (git ls-tree failed: fatal: Not a valid object name
   708aca6...:.tmp-test/...)') ; **passe sur l'adapté 4/4** (et seul
   4/4). Cause prouvée à la source : le full run pose `TMPDIR` dans le
   repo (`.tmp-test/...`, `vitest-run-temp-directory.mjs`) — le dossier
   « hors Git » du test est en fait DANS le clone orca, donc
   `releaseFor` trouve un repo Git (HEAD `708aca6`) et `git ls-tree`
   échoue autrement. Flake d'ordre/environnement, pré-existant au gel,
   0 imputable à l'adapter.
3. **`src/cli/runtime/runtime-listener-probe.test.ts` — « refuses to
   call a profile free when the endpoint could not be reached at all » :
   échec ADAPTÉ seulement** (attendu 'unproven', reçu 'not-listening') ;
   **passe en baseline full run (9/9)**. Cause prouvée à la source et
   au gel : le test `chmod 0o000` un dossier et attend une erreur de
   permission → 'unproven' — mais **la VM tourne en root (uid 0)**,
   le noyau ignore le bit 0o000, la connexion atteint le chemin et
   répond ECONNREFUSED → 'not-listening'. **Reproduit sur un worktree
   au gel seul (1 échec / 8 passés)** — pré-existant au gel, artefact
   root (même classe que le `writable_directory` de F1, R1), 0
   imputable à l'adapter. Flake d'ordre/état : il passe en baseline
   full run, échoue en adapté full run et seul des deux côtés.

**H-F2-3 NON vert strict :** 1 test en échec par run (flake
pré-existant, identité variable) + 1 fichier en échec par hook timeout
(charge). Décision du coordinateur attendue : exclusion des 3 rouges
(liste exacte ci-dessus) ou acceptation du rouge. Sans décision,
l'état 1 ne peut pas être revendiqué « suite verte ».

## Télémétrie

**Zéro appel sortant par défaut.** Voir `orca-TELEMETRY-AUDIT.md` : SDK
PostHog présent dans le code amont (`posthog-node` ^5.52.5) mais
fail-closed (builds officiels + consentement explicite seulement) et
coupé par l'adapter (`ORCA_TELEMETRY_DISABLED=1` + `DO_NOT_TRACK=1`
forcés, vérifiés au fichier) ; auto-update coupée par le chemin de
lancement (jamais `scheduleAutomaticUpdateCheck`) ; capture réseau
(strace du smoke) : **0 `AF_INET` hors loopback**.

## Divergence (dette portée par le cœur Buzz, lane Clara / 12e)

- **Skills V5 vs gel (D-F2-7) :** le stub du gel fait foi (47 lignes,
  guide chargé depuis l'exécutable, version-matched). Les 6 skills V5
  (12 fichiers, guide complet de 289 lignes, blob différent du gel) sont
  consignées comme divergence, non alignées. Alignement V5 sur le gel =
  suivi hors F2 (S-F2-5).
- **Dette de divergence :** 1 178 commits au gel (re-mesurée 1 205 en
  fin de pas) — toute dérive future exige un amendement de design
  (D-F2-4). Revisite quotidienne tant que la dérive dépasse 20.
- **Ré-audit télémétrie :** à chaque changement de commit gelé ou
  d'adapter, et au minimum à chaque transition d'état (D3).
- **Hors périmètre (suivis séparés) :** S-F2-1 (requalification H-P8-4) ;
  S-F2-2 (diagnostic SIGPIPE main.rs herdr, R1 du jugement F1) ; S-F2-3
  (suivis pas 8 F8) ; S-F2-4 (registre l.186, reçu R10 F1) ; S-F2-5
  (alignement skills orca V5 sur le gel) ; S-F2-6 (revisite orca
  quotidienne).
- **Règles maison amont respectées (AGENTS.md) :** la racine `AGENTS.md`
  amont n'a PAS été éditée (H-M2) ; l'adapter ne touche pas au cœur.

## Références

- Design pas F2 signé Clara (2026-11-12T17:46:09-05:00) :
  `~/workspace/v4-factory/plans/DESIGN-D-N053-PAS-F2-PROJET.md`.
- Discover pas F2 de Bill :
  `~/workspace/v4-factory/evidence/D-N053/f2/DISCOVER-PAS-F2.md`.
- Évidences : `~/workspace/v4-factory/evidence/D-N053/f2/` (logs
  baseline/adapté, typecheck, lint, smoke, strace, audit, harnais,
  rapport ; liste de triage `drift-perimeter-list.txt` /
  `drift-perimeter-final.json`).
- Fork : https://github.com/Amdkn/orca (gel `708aca6`, adapter
  `5d15464`, bind `8beacf3`).
