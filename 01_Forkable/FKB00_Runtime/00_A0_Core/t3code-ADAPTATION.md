# Fiche d'adaptation — t3code (D-N048 V3b)

**Adresse :** `fiber:a0:t3code`
**Manifeste :** `t3code.manifest.json` (même domicile)
**Audit télémétrie :** `t3code-TELEMETRY-AUDIT.md` (même domicile)
**Statut :** état 2 Vérifié (hold-outs H-M1..M7 verts + validation 13e, PR #11 mergée `8d2c658` ; fiche + adapter + manifeste, tests verts)
**Licence :** MIT

## Commit gelé

- **Fork :** `Amdkn/t3code` (parent `pingdotgg/t3code`, MIT, branche `main`).
- **Gel : `dc72705`** — version 0.1.7.
- **Correction de création nommée :** le fork a d'abord été créé sur le HEAD courant de l'amont (`9110dc2`, après le gel) ; la référence `main` a été ramenée au gel par mise à jour forcée de la ref (SHA complet, corps JSON).
- **Gitlink V5 :** à avancer dans la PR V3b (chemin inchangé).
- **Tout commit amont ultérieur exige un amendement de design**, jamais un fast-forward silencieux (D5).

## Adapter

- **Dossier :** `aspace-t3code-adapter/` (contract.json + smoke test + README + AGENTS.md), commit `4eedddf` sur le fork. **Seul code A'Space du fork** — le code amont est byte-identique au gel.
- **Surface (contrat seul, §1.5) :** sous-commandes qui parlent seulement — `t3 --version` (0.1.7), `t3 --help`, `t3 help`, `t3 doctor --dry-run` (maison T3 scratch, stdin fermé).
- **Jamais :** lancer le serveur (`t3` nu, `up`, `start`, `serve`, `connect`, `update`, `install`, `service`, `__service-launcher`) ; aucun appel réseau.
- **Couture TS↔Python↔Rust (§1.5) :** contrat seul — aucune couture spécifique construite.
- **Smoke test :** `node --test aspace-t3code-adapter/smoke_test.mjs` (6 checks, binaire construit `apps/server/dist/bin.mjs`).

## Tests au gel et sur le fork adapté

- **Au gel `dc72705` : suite serveur partielle récoltée + périmètre ciblé clos** — la suite complète du paquet serveur (`pnpm --filter t3 test` = `vp test run`, 478 fichiers) a tourné de 00:46 à 02:17 UTC puis **le processus s'est terminé sans résumé ni ligne `rc=`** (log figé à 02:17 UTC, cause de la mort non établie — pas de trace OOM lue). Bilan récolté du log par Ryan (`logs-t3code-suite.log`, comptage Python après strip ANSI) : **212 fichiers verts (5 385 tests verts) + 1 fichier en échec (`src/preview/ServerBrowserStream.test.ts`, 11 tests, 6 échecs) = 5 396 tests comptés sur ~265 fichiers non atteints**. Les 6 échecs = timeouts de 120 s sur des tests de flux navigateur (`InterruptError: All fibers interrupted without error`) ; les 5 autres tests du même fichier sont verts — classés environnementaux (VM partagée, charge 3–15, pas de navigateur réel), cause non prouvée à la racine, réserve nommée pour le 13e. **Périmètre ciblé clos** (la surface de l'adapter : `src/telemetry/` + `src/cli/` + `serverRuntimeStartup.test.ts`, 27 fichiers) : **220 passés, 2 échecs, 1 skipped (223), 372 s, rc=1** (log : `logs-t3code-suite-perimeter.log`).
- **Les 2 échecs sont environnementaux, qualifiés à la racine** : `src/cli/theme.test.ts` — « restores the previous theme when a re-publish fails to set » (dossier passé en `chmod 0o555`, écriture attendue en échec) et « refuses to write when the settings file cannot be read » (fichier passé en `chmod 0o000`, lecture attendue en échec). **La VM tourne en root (uid=0)** : root lit un fichier 000 et écrit dans un dossier 555 — prouvé directement sur cette VM. Les chmod n'ont aucun effet sur root, les échecs attendus ne se produisent pas. Pré-existants au gel (le code testé est amont, l'adapter ne touche ni au thème ni au CLI), même famille que les 2 rouges Cordis de D-N047. Hors adapter.
- **CI amont :** `.github/workflows/ci.yml` (jobs sharded : test_server, test_web, test_packages…) ; `vp run check:changed` pour les vérifications rapides.

## Télémétrie

**PostHog réel, défaut ON, forcé off par l'adapter.** Voir `t3code-TELEMETRY-AUDIT.md` : `apps/server/src/telemetry/AnalyticsService.ts` — envoi HTTP maison vers `https://ingest.t3.codes`, clé par défaut codée en dur, `T3CODE_TELEMETRY_ENABLED` défaut `true`, `DO_NOT_TRACK` non honoré. L'adapter force `T3CODE_TELEMETRY_ENABLED=false` (plus clé/hôte vidés) et ne démarre jamais le serveur : le service n'est jamais chargé.

## Divergence (dette portée par le cœur Buzz, lane Clara / 12e)

- **Règles maison amont respectées (AGENTS.md) :** la racine `AGENTS.md` amont n'a PAS été éditée (H-M2) ; l'adapter ne touche pas au cœur de l'app ; aucune PR amont créée (règle amont : jamais de PR sans demande du développeur).
- **Ré-audit télémétrie :** à chaque changement de commit gelé ou d'adapter, et au minimum à chaque transition d'état (D3).
- **Contrainte nommée du design (§2) : PostHog à forcer off** — fait (voir audit).

## Références

- Design D-N048 (Clara, 2026-11-09) : `~/workspace/v4-factory/plans/FORKS-AMONT-21-plan-borne-vagues.md`.
- Évidences : `~/workspace/v4-factory/evidence/D-N048/PROGRESS-D-N048.md`.
- Fork : https://github.com/Amdkn/t3code (gel `dc72705`, adapter `4eedddf`).
