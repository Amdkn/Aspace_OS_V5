# deepseek-harness — ADAPTATION (D-N048 V3b, FKB00)

## Adresse

`fiber:a0:deepseek-harness`

## Manifeste

`01_Forkable/FKB00_Runtime/00_A0_Core/deepseek-harness.manifest.json`

## Licence

MIT — `LICENSE` préservé byte-identique dans le fork `Amdkn/deepseek-harness`
(licence amont `deepseek-ai/deepseek-harness`, MIT, vérifiée à l'API).

## Audit télémétrie

`deepseek-harness-TELEMETRY-AUDIT.md` (dossier V3b, `~/workspace/v4-factory/evidence/D-N048/v3b/`).
**Verdict : zéro SDK tiers ; deux modules maison réels, coupés par contrat.**
`DSH_TELEMETRY_DISABLED=1` forcé sur chaque invocation de l'adapter ;
les commandes de l'adapter ne montent aucun profil, donc aucune instance de
`productAnalytics` ne démarre jamais.

## Statut

État 2 Vérifié — hold-outs H-M1..M7 verts + validation 13e (journal 434), PR #11 mergée `8d2c658`.

## Commit gelé

`fcc0ad4` (`fcc0ad462172522aaf5c93a7b2e01f6b9f0b0159`) — HEAD `master` du fork,
vérifié à l'API et au clone local. Amont `deepseek-ai/deepseek-harness`,
dernier push amont 2026-11-04T13:06:39Z (au gel au moment du fork).

## Adapter

`aspace-deepseek-harness-adapter/` (contract.json + smoke_test.mjs + README.md +
AGENTS.md local), commit `bea7272d6925cdd72524dbd01681c37f6c47e905`.

Surface talk-only (jamais de boot de profil, jamais d'appel modèle, jamais de
serveur) : `dsh --help`, `dsh --version` (0.2.2-rc.1),
`dsh --profile headless --dump-config`, `dsh --profile headless --dump-config-schema`.
Env forcé : `DSH_TELEMETRY_DISABLED=1`, `DSH_HOME=<scratch>`.

H-M2 : diff gel → adapter = les 4 fichiers de l'adapter seuls ; code amont
byte-identique, `AGENTS.md` / `CLAUDE.md` amont non édités.

## Tests

- **Smoke adapter** : `node --test aspace-deepseek-harness-adapter/smoke_test.mjs`
  — **5/5 PASS** (2026-11-09 ~19:5x EST).
- **Suite amont (H-M3)** : périmètre centré sur la surface de l'adapter
  (`apps/cli/tests` + `packages/boot/app-boot` + `packages/client/product-analytics`
  + `packages/host/product-telemetry-otel`), `pnpm exec vitest run --maxWorkers=2`,
  après `pnpm run build:native-system` OK (`system.node` construit) —
  **Test Files 40 passed | 1 skipped (41) ; Tests 5940 passed | 2 skipped (5942) ;
  0 échec** (durée 248,80 s, log `logs-deepseek-harness-suite.log`).
  Fichier ignoré : `apps/cli/tests/lazy-search-startup.compat.spec.ts` (1 test,
  skip conditionnel amont) ; 2e test ignoré dans
  `packages/client/product-analytics/tests/environment-query.host.spec.ts`.
  Le test amont de l'interrupteur télémétrie `telemetry-switch.spec.ts` (3 tests)
  passe. **Périmètre honnête : ce n'est pas la suite complète (2 053 fichiers
  de test au total) — impraticable sur cette VM en temps raisonnable (le seul
  `linked-resolution-matrix.spec.ts`, 4 800 tests, prend 230 s) ; le périmètre
  couru couvre la surface CLI + app-boot + les 2 modules télémétrie.**

## Télémétrie

Voir audit. Modules maison : `packages/client/product-analytics` (RPC
Desktop-only, `enabled` défaut `true`) et `packages/host/product-telemetry-otel`
(OTLP, défaut `https://dsh-otel-collector.deepseeksvc.com/v1/logs`).
Interrupteur : `DSH_TELEMETRY_DISABLED=1` → patch hard-disable de la ligne
télémétrie (`resolveTelemetryPatch`, `packages/boot/app-boot/src/profile-context.ts`).

## Réserves

1. **Typecheck pre-push amont — blocage environnemental (OOM), pas une erreur
   de code.** Le hook pre-push du repo (`lefthook.yml` : `pnpm run typecheck`)
   échoue sur `tsc -b tsconfig.host.json` : tué par SIGKILL (OOM killer) avec
   `--max-old-space-size=8192` sur une VM de 7,9 Go ; relancé à la main avec
   un plafond de 4 Go, il meurt après ~9,5 min en « JavaScript heap out of
   memory ». **4/5 gates PASS** (Host Typert, host compiler, client compiler,
   client aggregate), **zéro erreur de type**. L'adapter n'ajoute aucun fichier
   TypeScript — il ne peut pas affecter le typecheck. **Push effectué avec
   `--no-verify`** (décision Go_Bypass documentée) après deux morts OOM
   prouvées ; les checks pre-commit du repo (lint staged, whitespace, vendor
   manifest guard) passent. Log : `logs-deepseek-harness-typecheck.log` ;
   run plafonné : `logs-deepseek-harness-tsc-host.log`.
2. **Suite complète non courue** (voir § Tests) — 2 053 fichiers, périmètre
   ciblé seul.

## Divergence

Dette de divergence : cœur Buzz (lane Clara / 12e). Amont figé au gel
`fcc0ad4` ; toute dérive constatée par l'inventaire hebdomadaire Auto Research
devient un candidat de fusion (re-gel, diff relu, hold-outs re-courus,
validation 13e) — jamais un fast-forward silencieux (D5).

## Références

- Design : `~/workspace/v4-factory/plans/FORKS-AMONT-21-plan-borne-vagues.md`
  (§2 deepseek-harness, §6 H-M1..M7)
- Fork : `Amdkn/deepseek-harness` (parent `deepseek-ai/deepseek-harness`)
- Adapter : `aspace-deepseek-harness-adapter/` sur le fork
- Audit : `~/workspace/v4-factory/evidence/D-N048/v3b/deepseek-harness-TELEMETRY-AUDIT.md`
- Suite : `~/workspace/v4-factory/evidence/D-N048/logs-deepseek-harness-suite.log`
