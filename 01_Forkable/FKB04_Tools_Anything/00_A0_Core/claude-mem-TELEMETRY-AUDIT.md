# Audit télémétrie — claude-mem (D-N048, V1, FKB04)

**Module :** `Amdkn/claude-mem` (fork de `TheDotMack/claude-mem`), gel `a926f57`, Apache-2.0.
**Date :** 2026-11-09. **Auditeur :** Ryan (Factory). **Régime :** R10.

## 1. Scan statique (TypeScript, `src/`)

- **Service télémétrie** : `src/services/telemetry/` (`telemetry.ts`,
  `cli-telemetry.ts`, `consent.ts`, `common.ts`, `backfill.ts`, ...).
  SDK **`posthog-node`** (dépendance dev), hôte par défaut
  `https://us.i.posthog.com` (`common.ts:21`). Batching en arrière-plan.
- **Consentement** (`consent.ts`, fonction pure, ordre de précédence) :
  1. `DO_NOT_TRACK` posé (toute valeur non vide sauf `0`/`false`) → **toujours off** ;
  2. `CLAUDE_MEM_TELEMETRY` : `0`/`false`/`off` → off ;
  3. config `telemetry.json` : `enabled` ;
  4. **Défaut : ON** (opt-out, événements anonymes seulement).
  → L'adapter force `DO_NOT_TRACK=1` (+ `CLAUDE_MEM_TELEMETRY=0`) :
  la couche 1 tranche avant toute autre.
- **Événements** : `captureCliEvent` (hooks), `hook_failed` (à seuil),
  `work_state_telemetry`. Tous passent par le client PostHog — muet
  quand le consentement est off.
- **Autres appels réseau déclarés** : `express` (serveur local),
  `ioredis`/`bullmq` (file locale), `pg` (Postgres), `better-auth` —
  tous des services locaux, jamais appelés par l'adapter (qui ne touche
  que le SQLite local via `bun:sqlite`).

## 2. Dépendances déclarées

Un seul SDK télémétrie : `posthog-node` (devDependency). Aucun autre
SDK analytics. L'adapter n'importe rien de `src/services/telemetry/`.

## 3. Preuve réseau (capture en namespace sans interface)

**Exécutée 2026-11-09, `unshare -n` (aucune interface réseau) :**
`bun test packages/aspace-claude-mem-adapter/tests/smoke.spec.ts` avec
`DO_NOT_TRACK=1` → **5 pass, 0 fail** (480 ms). **Zéro appel sortant
possible** (aucune interface dans le namespace) — le test ne touche
que le SQLite local.

## 4. Verdict

**Télémétrie zéro par contrat** : l'adapter ne fait aucun appel réseau
(SQLite local seul) et force le consentement off pour le module.
Aucun identifiant, aucun crédit dépensé.
