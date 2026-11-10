# Fiche d'adaptation — openclaw (D-N048 V3b)

**Adresse :** `fiber:a0:openclaw`
**Manifeste :** `openclaw.manifest.json` (même domicile)
**Audit télémétrie :** `openclaw-TELEMETRY-AUDIT.md` (même domicile)
**Statut :** état 0 Basique → 1 Adapté (fiche + adapter + manifeste ; suite partielle, voir § Tests — télémétrie 98/98 verte, reste qualifié, `unit` non couru)
**Licence :** MIT

## Commit gelé

- **Fork :** `Amdkn/openclaw` (parent `openclaw/openclaw`, MIT, branche `main`).
- **Gel : `ce7788f`** — version 2026.11.2.
- **Correction de création nommée :** le fork a d'abord été créé sur le HEAD courant de l'amont (`bd63497`) ; la référence `main` a été ramenée au gel par mise à jour forcée de la ref (SHA complet, corps JSON).
- **Gitlink V5 :** repointé vers le fork dans cette PR (chemin inchangé).
- **Tout commit amont ultérieur exige un amendement de design**, jamais un fast-forward silencieux (D5).
- **Clone partiel obligatoire (§1.6) :** repo amont ~13,3 Go (72 % du total des 21) — clone `--filter=blob:none --depth 1` + sparse checkout, étendu au fil des besoins des outils amont (prepare → `patches`, `src/gateway/methods`, `src/shared` ; build → `src`, `extensions` ; suite vitest → `ui`, `config`, `docs`, `crates`, `skills`, `tools`, `qa`, `security`, `custodian-skills`, `examples`, `deploy`, `apps`, `.agents`, `.claude`, `.openclaw`). Repo local final ~4,5 Go (dont `node_modules` 2,9 Go). Le checkout complet reste interdit.

## Adapter

- **Dossier :** `aspace-openclaw-adapter/` (contract.json + smoke test shell + README), commit `f6fd7aaf` sur le fork. **Seul code A'Space du fork** — le code amont est byte-identique au gel.
- **Surface (contrat seul, §1.5) :** sous-commandes qui parlent seulement — `--version` (`OpenClaw 2026.11.2 (<sha>)`, launcher seul sans build), `--help`, `telemetry show` (aperçu local de la requête quotidienne, sans envoi). Mode built préféré (`dist/entry.js`) ; sans build, mode sources via tsx (`node --import ./scripts/tsx.mjs src/entry.ts`, même mécanisme que les scripts amont) — le build complet est hors de portée de la VM de travail (tsdown : pic ~4,7 Go mesuré amont, heap résolu ici 3 502 Mo).
- **Jamais :** lancer la gateway (`openclaw gateway`, `onboard`), toute session agent, tout appel modèle, tout appel réseau hors npm/pnpm.
- **Couture JS (§1.5) :** contrat seul — aucune couture spécifique construite.
- **Smoke test :** `bash aspace-openclaw-adapter/smoke_test.sh` (maison scratch, `DO_NOT_TRACK=1` + `CI=1`, stdin fermé ; option `--netproof` : namespace sans interface réseau). **Vert** : mode sources, `OpenClaw 2026.11.2 (2ccb03b)`, `--help`, `telemetry show disabled` — normal 4 min 12 s, `--netproof` 2 min 22 s (2026-11-10). Piège consigné : sans stdin fermé, `telemetry show` attend indéfiniment une entrée interactive.

## Tests au gel et sur le fork adapté

- **Au gel `ce7788f`, bilan exact (2026-11-10, VM de travail partagée, 6 Go) :**
- **CI amont :** `pnpm test` (`node scripts/test-projects.mts`) ; unité `pnpm test:unit` (vitest, `test/vitest/vitest.unit.config.ts`, sharding par domaine). pnpm 12.15.0, Node v24.22.1.
- **Périmètre réellement couru (vitest direct, binaire stock — le wrapper amont est bloqué par un faux positif de son garde-fou, voir ci-dessous) :**
  - **Télémétrie ciblée — 98/98 VERTS, rc=0** : `telemetry-cli.test.ts` 9/9, `telemetry.test.ts` + `telemetry.async.test.ts` + `telemetry-installation-count.test.ts` 78/78, `telemetry-store.worker.test.ts` 8/8, `zod-schema.telemetry.test.ts` 3/3 (`logs-openclaw-suite-telemetry.log`).
  - **cli, partiel — 936 ✓ observés avant OOM** (run 22 min, tué par OOM, sans résumé) ; échecs qualifiés en isolation (`logs-openclaw-suite-updatecli.log`, `logs-openclaw-suite-complements.log`) : `update-command-executor.test.ts` 100 ✓ / 13 ✗, `capability-cli.test.ts` + `run-loop.test.ts` 285 ✓ / 8 ✗.
  - **runtime-config, complet — 373 ✓ / 319 ✗ / 53 ignorés (750, 23 fichiers), rc=1 — verdict INVALIDÉ** : 58× `ENOSPC: no space left on device` + 10× `database or disk is full` + cascade SQLite — le `/tmp` tmpfs (512 Mo) a saturé pendant le run (`logs-openclaw-suite-full.log`). Cause environnementale établie, pas un défaut produit.
  - **infra, partiel** : tests ✓ observés, run tué par OOM avant résumé (`logs-openclaw-suite-full.log`).
  - **unit : non couru** (OOM + temps sur VM partagée).
- **Qualification des échecs cli (tous reproduits en isolation, `--maxWorkers=1`) :**
  - **19× « dist requis »** (défaut d'environnement, pas du produit) : `Managed handoff requires its sealed runtime; use the repository test runner or the dist-backed pnpm openclaw CLI.` (`update-managed-service-handoff-runtime.ts:14`) + `ERR_MODULE_NOT_FOUND src/daemon/service-process-env.js` (enfant sans chargeur tsx) — 13 dans `update-command-executor`, 6 dans `run-loop`. Ces tests exigent le build `dist`, impossible ici (mémoire).
  - **4× timeouts sous charge** : 120 s (`capability-cli`, `run-loop` « upgrades an accepted restart »), 1× `fs-safe` timeout (`run-loop` preparing) ; `capability-cli` et `update-command-admit` **repassent verts en isolation** (flaky sous charge).
- **Limites franches (vérifiées, pas supposées) :**
  - **Build complet impossible** : tsdown pic ~4,7 Go (mesuré amont, `scripts/tsdown-build.mts:646-651`), heap résolu 3 502 Mo → garde-fou amont refuse avant tout output.
  - **Wrapper amont (`run-vitest.mjs`, `test-projects.mts`) inutilisable ici** : sa préparation appelle le garde-fou `live-gateway-dist-fence` en mode `requireVerified` ; la découverte y pousse le processus appelant comme binding (systemd présent sur la VM : `/run/systemd/system` existe) puis ne peut pas vérifier la séparation → refus systématique. La suite a donc couru par le binaire vitest stock, mêmes fichiers de tests, mêmes configs.
  - **Install** : `pnpm install --frozen-lockfile --ignore-scripts` rc=0 (ordre CI amont vérifié : install `--ignore-scripts` puis build ; le `prepare` exige des paquets construits).
  - **Suivi recommandé** : re-courir `runtime-config` avec `TMPDIR` sur grand disque (114 Go libres) et `unit` complet après build `dist`, sur VM moins chargée.

## Télémétrie

**Coupée par contrat (module réel dans l'amont).** Voir `openclaw-TELEMETRY-AUDIT.md` : module maison `src/infra/telemetry.ts` — statistiques anonymes **OFF par défaut** (opt-in explicite, `never-asked` sans consentement) + comptage d'installations sans payload + vérification de mise à jour quotidienne vers `https://telemetry.openclaw.ai/api/latest-version` ; OTel sans endpoint par défaut ; coupé par `DO_NOT_TRACK=1` / `CI=1` / vérification de mise à jour désactivée. L'adapter force `DO_NOT_TRACK=1` + `CI=1` et n'expose que des sous-commandes qui parlent seulement.

## Divergence (dette portée par le cœur Buzz, lane Clara / 12e)

- **Règles maison amont respectées (AGENTS.md) :** l'adapter ne touche pas au cœur de l'app (le cœur reste petit, tout le reste est en plugins — règle du mainteneur) ; aucune modification du comportement agent ; la racine `AGENTS.md` amont n'a PAS été éditée (H-M2).
- **Ré-audit télémétrie :** à chaque changement de commit gelé ou d'adapter, et au minimum à chaque transition d'état (D3).

## Références

- Design D-N048 (Clara, 2026-11-09) : `~/workspace/v4-factory/plans/FORKS-AMONT-21-plan-borne-vagues.md`.
- Évidences : `~/workspace/v4-factory/evidence/D-N048/PROGRESS-D-N048.md`.
- Fork : https://github.com/Amdkn/openclaw (gel `ce7788f`, adapter `f6fd7aaf`).
