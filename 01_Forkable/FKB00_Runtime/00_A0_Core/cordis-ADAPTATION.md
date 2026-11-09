# Fiche d'adaptation — Cordis (étape 0)

**Adresse :** `fiber:a0:cordis` (D2 — émetteur : exécution ; validateur : 13e)
**Manifeste :** `cordis.manifest.json` (même domicile)
**Audit télémétrie :** `cordis-TELEMETRY-AUDIT.md` (même domicile)
**Statut :** état 0 Basique → 1 Adapté en cours (fiche + adapter + manifeste, tests verts)

## Commit gelé

- **Fork :** `Amdkn/cordis` (parent `cordiverse/cordis`, MIT, branche `main`).
- **Gel : `b38ef58`** — « feat(hmr): invalidate resolution caches and package manifests (#298) », 2026-11-09.
- **Reprise #298 :** diff relu avant application (26 fichiers, +2741/−516, un seul commit). Réécriture HMR : runtime propre (`hmr/src/runtime/` — invalidation des caches de résolution et des manifests), README mécanisme transactionnel ; suppression du paquet `loader-utils` (absorbé par `loader/src/internal.ts` + `hmr/src/runtime/`) ; `loader` importe désormais depuis son propre `./internal.ts` ; tests HMR réécrits.
- **Correction de prémisse consignée :** le design porte « 11 paquets » (inventaire à #297). Au gel `b38ef58`, il reste **10 paquets** — `loader-utils` n'existe plus. Le manifeste liste les 10 paquets existants au gel. Porté au jugement du 13e.
- **Tout commit amont ultérieur exige un amendement de design**, jamais un fast-forward silencieux (D1).

## Adapter

- **Paquet :** `packages/aspace-cordis-adapter` (`@aspace/cordis-adapter` 0.1.0), commit `a40cc74` sur le fork. **Seul code A'Space du fork** (D6) — les 10 paquets amont sont byte-identiques au gel.
- **Surface :** `createAspaceApp()` → `{ ctx, hmr }` (HMR installé, watch off, reconcile explicite) ; `reconcile(ctx, roots)` → rapport `applied / partial / aborted / skipped / noop` ; `hasHmr(ctx)` ; constantes épinglées (`PINNED_CORDIS_COMMIT = b38ef58`, `PINNED_HMR_VERSION = 1.1.2`, `PINNED_HMR_SURFACE`).
- **Smoke tests :** 3/3 verts (`tests/smoke.spec.ts`).

## Tests au gel et sur le fork adapté

- **Au gel `b38ef58` : 691 passés, 2 rouges, 11 skipped (704).** Les 2 rouges sont prouvés pré-existants et environnementaux : identiques à #297, et ils passent en non-root (la VM tourne en root, un fichier chmod 444 reste inscriptible). #298 ajoute 56 tests verts, zéro nouvelle failure. Porté au jugement du 13e (H-C0-3).
- **Sur le fork adapté (`a40cc74`) : 694 passés, 2 rouges identiques, 11 skipped (707).** L'adapter ajoute 3 tests verts.
- **Limite franche :** le client Yarn est bloqué par le proxy de cette VM — les tests ont tourné avec des dépendances résolues par npm (`--legacy-peer-deps`), pas par `yarn.lock` (absent du dépôt amont). La CI du fork reste la voie de vérification yarn-native.

## Télémétrie

**Zéro.** Voir `cordis-TELEMETRY-AUDIT.md` : scan statique (2 `fetch()` seulement, package `create`, téléchargement de template initié par l'utilisateur ; zéro SDK télémétrie déclaré) + audit d'exécution (adapter + HMR : 118/118 verts dans un namespace réseau sans aucune interface — zéro appel sortant possible).

## Divergence (dette portée par le cœur Buzz, lane Clara / 12e)

- **Surface d'API instable épinglée :** l'amont avertit (core README ligne 7) que l'API est instable. L'adapter dépend de `ctx.plugin(Hmr)`, `ctx.hmr.reconcile`, `Hmr.Result { settled, aborted, skipped }`, `Hmr.SkipReason { host-module, native-addon, ambiguous-import, ambiguous-export }`. Toute dérive est un événement de design, pas une rupture silencieuse.
- **Comportements HMR dont l'adapter dépend :** la transaction `reconcile()` (sweep → caches de résolution → matching → graphe → découverte → import → remplacement) ; les remplacements de méthodes Node.js (lecture des manifests, `Module._load`) ne sont **pas restaurés** à la disposal — au plus une instance HMR active par thread ; la résolution ESM via lien retargeté n'observe la nouvelle cible que sur Node.js 24.16+ / 26.1+.
- **Dépendance introduite par #298 :** l'invalidation des caches de résolution et des manifests — la correction de justesse qui a motivé le gel après reprise.
- **Ré-audit télémétrie :** à chaque changement de commit gelé ou d'adapter, et au minimum à chaque transition d'état (D3).

## Références

- Design D-N047 (Clara, 2026-11-09) : `~/workspace/v4-factory/plans/CORDIS-AUTORESEARCH-plan-borne-etapes-0-1.md`.
- Évidences : `~/workspace/v4-factory/evidence/D-N047/PROGRESS-N047.md`.
- Fork : https://github.com/Amdkn/cordis (gel `b38ef58`, adapter `a40cc74`).
