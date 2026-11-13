# Rapport — D-N053 pas F2 : orca, état 0 → 1 (dernier module état 0 du Runtime)

**Exécutant :** Ryan (Factory). **Design :** signé Clara, 2026-11-12T17:46:09-05:00
(`~/workspace/v4-factory/plans/DESIGN-D-N053-PAS-F2-PROJET.md`).
**Discover :** Bill (`~/workspace/v4-factory/evidence/D-N053/f2/DISCOVER-PAS-F2.md`).
**Branche :** `a0/dn053-pas-f2`, base master `5629dac` (re-vérifié à l'API avant usage).
**Commit d'intégration :** `e2d9ecb` (`e2d9ecb4e5747ca222bae4190b9da1f79f167c94`,
1 commit : fiche + audit + manifeste + gitlink orca + registre, parent =
master `5629dac`). **PR V5 :** #46 (voir fin de rapport).
**Harnais :** `harness-pas-f2.py` → `RESULTS-D-N053-F2.json`.

## Livré

| Module | Gel | Adapter (pin) | Bind re-appliqué | Manifeste | État |
|---|---|---|---|---|---|
| orca | `708aca6` (v1.4.214) | `5d15464` (6 fichiers) | `8beacf3` (byte-identique) | `fiber:a0:orca` | 0 → 1 |

- Commits vérifiés à l'API : adapter parent = gel, fichiers adapter seuls ;
  bind parent = adapter, `aspace-plugin.json` 24 lignes, blob
  `736c2e1b4ac786ea848abf6379adc936518755bc` byte-identique au bind
  `b659760` sur `aspace-v5-native`.
  (Leçon d'atelier F1 appliquée : travail sur `main`, pas en HEAD détachée —
  vérifié avant le push ; push `708aca6..8beacf3` propre.)
- orca : CLI-contrat (Forme A, `orca-ide` sur Linux) + client `orcad`
  (Forme B, jamais de serveur V5) + skills en référence versionnée
  (Forme C, 11 skills du gel nommées). `ORCA_TELEMETRY_DISABLED=1` +
  `DO_NOT_TRACK=1` forcés, vérifiés par le smoke. Auto-update coupée
  par le chemin de lancement (jamais `scheduleAutomaticUpdateCheck`).
  Preuve client H-F2-3 : round-trip readiness + WS `server.status`
  contre stub local `127.0.0.1` (4/4).
- Gitlink orca re-pointé sur l'adapter (`5d15464`) ; `.gitmodules`
  inchangé. Registre : compteur **1 → 0**, table + paragraphe « Pas F2 »,
  F9 Mesures : « orca en état 1 (pas F2) — compteur 0 ».

## Suites — baseline au gel vs adapté

### orca — NON VERT STRICT (chiffres identiques, 3 rouges pré-existants, 0 imputable à l'adapter)

| Suite | Baseline `708aca6` | Adapté `5d15464` |
|---|---|---|
| vitest borné (263 fichiers) | 2 094 passés / 1 échec / 29 ignorés ; 2 fichiers en échec | 2 094 passés / 1 échec / 29 ignorés ; 2 fichiers en échec |
| `tc:cli` | — | vert (exit 0) |
| `tc:node` | — | vert (exit 0, après récupération des locales à la demande — voir ci-dessous) |
| `oxlint` borné (790 fichiers) | — | vert (0 warning / 0 erreur) |
| smoke adapter + preuve client | — | vert (`SMOKE_EXIT:0`, `PROOF 4/4`) |
| strace smoke | — | 12 `AF_INET`, toutes `127.0.0.1`, 0 hors loopback |

**Les 3 rouges, liste exacte (décision du coordinateur à demander — rien
exclu de ma propre initiative, H-F2-3) :**

1. **`src/cli/index-omitted-host-scope-selectors.test.ts` — hook
   `beforeAll` timeout 60 s** (fichier en échec, 7 tests skipped, 0 test
   en échec), baseline ET adapté, identique. Passe seul 7/7 en 41 s.
   Cause : charge parallèle (263 workers, 1,5 CPU).
2. **`src/cli/plugin-authoring/plugin-release-entry.test.ts` — « explains
   why there is no entry outside Git or before the first commit » :
   échec BASELINE seulement** (attendu 'not in a Git repository', reçu
   'no catalog release entry: HEAD has no installable plugin here (git
   ls-tree failed: fatal: Not a valid object name 708aca6...:.tmp-test/...)').
   Passe sur l'adapté 4/4 et seul 4/4. Cause prouvée à la source : le
   full run pose `TMPDIR` dans le repo (`.tmp-test/...`,
   `vitest-run-temp-directory.mjs`) — le dossier « hors Git » du test est
   en fait DANS le clone orca, donc `releaseFor` trouve un repo Git
   (HEAD `708aca6`) et `git ls-tree` échoue autrement. Flake
   d'ordre/environnement, pré-existant au gel.
3. **`src/cli/runtime/runtime-listener-probe.test.ts` — « refuses to call
   a profile free when the endpoint could not be reached at all » :
   échec ADAPTÉ seulement** (attendu 'unproven', reçu 'not-listening') ;
   passe en baseline full run (9/9). Cause prouvée à la source et au
   gel : le test `chmod 0o000` un dossier et attend une erreur de
   permission → 'unproven' — mais **la VM tourne en root (uid 0)**, le
   noyau ignore le bit 0o000, la connexion atteint le chemin et répond
   ECONNREFUSED → 'not-listening'. **Reproduit sur un worktree au gel
   seul (1 échec / 8 passés)** — pré-existant au gel, artefact root
   (même classe que le `writable_directory` de F1, R1 du jugement F1).
   Flake d'ordre/état : il passe en baseline full run, échoue en adapté
   full run et seul des deux côtés.

**0 régression nette :** les totaux sont identiques des deux côtés
(2 094/1/29, 2 fichiers en échec) ; le test en échec diffère parce que
les rouges n° 2 et n° 3 sont des flakes d'ordre/état pré-existants.

## Télémétrie — zéro appel sortant par défaut

- SDK PostHog présent au gel (`posthog-node` ^5.52.5, 27 occurrences)
  mais fail-closed (builds officiels + consentement explicite seulement)
  et coupé par l'adapter (`ORCA_TELEMETRY_DISABLED=1` +
  `DO_NOT_TRACK=1`, kill switches reconnus par `resolveEnvOverride`,
  vérifiés au fichier).
- Auto-update coupée par le chemin de lancement (config `autoDownload =
  false` + `autoInstallOnAppQuit = false` ; jamais
  `scheduleAutomaticUpdateCheck` — le check 24 h n'est planifié que par
  le processus principal Electron, jamais démarré par l'adapter).
- Audit versionné au domicile V5, chaque déclencheur du Discover §6
  tranché (T1–T8). Capture strace : 12 `AF_INET`, toutes `127.0.0.1`,
  0 hors loopback.

## Dérive

- Gel tenu `708aca6`. Dérive totale **1 178** au moment de l'exécution
  (amont HEAD `91b3f12`, 2026-11-12T23:12:55Z), **re-mesurée 1 205** en
  fin de pas (amont HEAD `41666c7`, 2026-11-13T01:17:39Z).
- Triage exhaustif par chemin joint : **142 commits distincts**
  (`drift-perimeter-list.txt`, 145 lignes = 3 en-tête + 142 commits ;
  `drift-perimeter-final.json`).

## Corrections de faits du design (signalées avec preuves)

- Dérive 1 161 (design) → **1 178** à l'exécution (puis 1 205 en fin de
  pas) : l'amont pousse toutes les quelques minutes.
- `tc:node` exige les locales i18n (`src/renderer/src/i18n/locales`,
  11 fichiers, 16 Mo) : le clone partiel les exclut par sparse-checkout
  (E-F2-2) — premier run en échec sur 12 erreurs `Cannot find module`,
  vert après récupération des blobs à la demande et restauration de
  l'exclusion.
- `--version` sur un build CLI seul répond « Could not determine the
  Orca version for this build. » (exit 1) : `out/package.json` absent —
  comportement amont, assert tel quel par le smoke.

## Incidents d'environnement (et remèdes)

- **`pnpm` absent du PATH** (binaire 12.14.0 disparu, seul le store
  subsiste) : retrouvé dans le cache corepack (12.18.0),
  shim `~/workspace/.bin/pnpm`. Le hook pre-commit `lint-staged` tourne
  avec ce shim (oxlint 0 erreur après correction des accolades de
  `proof.mjs`, oxfmt appliqué par le hook).
- **`/tmp` tmpfs 512 Mo** : scratch sous `~/workspace/` uniquement, jamais
  `/tmp` ; les suites y écrivent via `TMPDIR` du runner (`.tmp-test`
  dans le repo) — c'est aussi la cause du rouge n° 2.
- **VM en root (uid 0)** : cause du rouge n° 3 (chmod 0o000 ignoré).
- **Quota disque :** 93 Go libres, aucun ménage nécessaire.

## Preuves (chemins)

- `~/workspace/v4-factory/evidence/D-N053/f2/` :
  `logs-suite-baseline-gel.log`, `logs-suite-adapte.log`,
  `logs-suite-adapte-rerun-3files.log`,
  `logs-typecheck-cli-adapte.log`, `logs-typecheck-node-adapte.log`,
  `logs-lint-adapte.log`, `logs-smoke-adapte.log`,
  `logs-protocol-proof-adapte.log`, `logs-strace-adapte.log`,
  `logs-smoke-strace-run.log`, `orca-TELEMETRY-AUDIT.md`,
  `drift-perimeter-final.json`, `drift-perimeter-list.txt`,
  `test-perimeter-f2.txt`, `harness-pas-f2.py`,
  `RESULTS-D-N053-F2.json`, `RAPPORT-PAS-F2.md` (ce fichier).
- Fork : https://github.com/Amdkn/orca (main `8beacf3`).

## Décisions attendues du coordinateur

1. **H-F2-3 — exclusion des 3 rouges** (liste exacte ci-dessus) ou
   acceptation du rouge : index-omitted (beforeAll timeout, charge) +
   plugin-release-entry (échec baseline seulement, TMPDIR) +
   runtime-listener-probe (échec adapté seulement, artefact root,
   reproduit au gel). Sans décision, l'état 1 ne peut pas être
   revendiqué « suite verte ».
2. **H-F2-3 herdr-core / herdr** : inchangé (F1).

## PR

**PR V5 #46 :** https://github.com/Amdkn/Aspace_OS_V5/pull/46 — tête
`e2d9ecb`, base `master`, titre « D-N053 pas F2 : orca adapté en Fibre
Cordis (8L) — état 0 → 1 ». STOP à la PR ouverte — pas de jugement,
pas de merge (à la charge du 13e puis du coordinateur).
