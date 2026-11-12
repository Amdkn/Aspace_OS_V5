# Rapport consolidé — D-N053 pas C : MasterSpec, les skills (4 modules)

**Coordinateur :** pas C (D-N053). **Design signé :** fonction de design interne, 2026-11-11 ~02:06 EST (`DESIGN-D-N053-PAS-C-PROJET.md` : D-C0 4 modules, D-C1 option (a) renommage get-shit-done → gsd-core, D-C2 bornes §4 nommées, D-C3 plafonds). **État visé :** 1 (Adapté) par module. **Régime :** R10.

## Table des 4 modules (commits poussés, têtes vérifiées à l'API)

| Module | Gel (parent de l'adapter) | Bind `aspace-v5-native` | Adapter | Bind re-appliqué | Branche |
|---|---|---|---|---|---|
| superpowers (canonique) | `22f0b463` | `4ca2922` | `5813de0` (3 fichiers, +378/−0) | `a73b34d` | `main` |
| elephant-goldfish-model | `113a3afc` | `3d643fe` | `4f4a076` (3 fichiers, +365/−0) | `e9b3cef` | `main` |
| gstack | `3742ee95` | `a79170c` | `6cb6da7` (3 fichiers, +326/−0) | `f63ac22` | `main` |
| gsd-core (nouveau fork) | `cb15dcf1` | `d8c51c5` (créé pendant le pas) | `adc42da` (3 fichiers, +356/−0) | `1214039` | `next` |

Pin = commit adapter (tranché journal 587, reçu G-20261110-016 ; jamais « pin = adapter+bind HEAD »). Re-applications du bind vérifiées byte-identiques (diff vide / `cmp` vide / sha256 identique pour superpowers). Forks souverains vérifiés à l'API ; licences lues au fichier (MIT ×3, Apache-2.0 ×1).

## Bilans (smoke + suite, baseline au gel vs adapté)

| Module | Smoke adapter | Suite |
|---|---|---|
| superpowers | 6/6 + netns 8/8 | **suite amont bornée VERTE au gel et sur l'adapté** (`npm test` dans `tests/brainstorm-server/` : 139 PASS, 9 sections, 0 failed). Run 1 au gel : exit 1 sans assertion en échec (log tronqué en pleine section lifecycle) — flakiness de timing, re-run exit 0, 139/139. |
| elephant-goldfish-model | 6/6 + netns 8/8 | **suite amont bornée VERTE au gel et sur l'adapté** (`pytest tests/unit` : 336 passed, 2 skipped). Run 1 : exit 1, erreurs fixture `test_packaging.py` — cause environnementale, /tmp tmpfs 512 Mo plein à 100 % par les clones des autres pistes (non touchés) ; re-run avec TMPDIR hors /tmp : exit 0. |
| gstack | 6/6 + netns 9/9 | **suite amont bornée NON VERTE au gel et sur l'adapté** (`bun run scripts/test-free-shards.ts --quick`) : gel 726 tests en échec / 65 fichiers (540/17 + 80/19 + 63/16 + 43/13), adapté 729 / 66 fichiers (541/18 + 80/19 + 62/15 + 46/14) — mêmes grappes (browse E2E, QA E2E, autoplan-admission, CSO, codex-cli), 0 imputable à l'adapter, écarts aux marges = flakiness. H-C3 NON VERT strict — à juger. |
| gsd-core | 6/6 + netns 9/9 | **suite amont bornée NON VERTE strict au gel comme sur l'adapté** (`node scripts/run-tests.cjs --suite unit`, 1 169 fichiers, 3 shards `--shard i/3`, sig `cfacde7f`) : gel **50 086 pass / 3 fail** (16 379/1 + 17 913/2 + 15 794/0), adapté **50 087 pass / 2 fail** (16 379/1 + 17 914/1 + 15 794/0) — delta +1/−1 = test flaky pi-package (`pi-package.test.cjs:152`, timeout 30 s sous contention), passé au run adapté. Échecs restants environnementaux et identiques dans les deux runs : #1634 (umask 0007, mode 640 vs 644) et npm-audit 403 (proxy de sortie de la VM, vérifié manuellement). **Zéro échec imputable à l'adapter.** H-C3 NON VERT strict — à juger. Voir `gsd-core/NOTE-CORRECTION-BASELINE.md` (runs 1–8, orage EPERM sandbox, carte des filesystems, TMPDIR=/var/tmp + GIT_TEMPLATE_DIR). |

## Hold-outs H-C1..H-C8 (harnais `harness-pas-c.py` → `RESULTS-D-N053-C.json`)

Run harnais 1 : 27/35 PASS, 1 QUALIFIÉ, 7 FAIL — 6 FAILs = défauts de mesure du harnais (H-C2 : troncature des chemins par `git diff --stat` ; H-C8 : `split("---")` tronqué par le séparateur de tableau Markdown ; H-C3/gsd-core : logs agrégés absents, le harnais lisait `logs-suite-baseline-gel.log` / `logs-suite-adapte.log`) + 1 FAIL réel (H-C1/gsd-core : gitlink gsd-core absent du commit — `git add -A` l'avait retiré de l'index, le répertoire du sous-module n'existant pas sur disque ; corrigé par `git update-index --add --cacheinfo` + amend, commit `b61b890` → `1f75556`).
Corrections appliquées et documentées dans le harnais (commentaires datés) : `--stat-width=200` (H-C2), `split("\n---\n")` (H-C8) ; logs agrégés créés par concaténation verbatim des 3 shards (`logs-suite-baseline-gel.log` 50 086/3, `logs-suite-adapte.log` 50 087/2 — sommes exactes préservées, fichiers sources intacts).
Run harnais 2 (commit `1f75556`) : **33/35 PASS, 1 QUALIFIÉ, 1 FAIL** :
- H-C1 (4/4), H-C2 (4/4), H-C4 (4/4), H-C5 (4/4 + sans-doublon), H-C6 (5/5), H-C7 (4/4), H-C8 : PASS.
- H-C3 superpowers / EGM / smokes (4/4) : PASS.
- H-C3/gstack : **QUALIFIÉ** — `--quick` NON VERT strict (726 gel / 729 adapté), à juger.
- H-C3/gsd-core : **FAIL** — NON VERT : gel (50 086, 3), adapté (50 087, 2), à juger.

## Actes nommés

1. **EGM — fork main ramené au gel avant adaptation.** Le fork `main` portait 3 commits amont au-delà du gel (`0dfb5bf`, `ccf79c5`, `6a8001e`) ; `main` ramené au gel par `reset --hard` + `push --force-with-lease` (parent de l'adapter = gel, per design §3). Les 3 commits restent verbatim sur `upstream/main` (`google/elephant-goldfish-model`, vérifié par `merge-base --is-ancestor`).
2. **gsd-core — bind 4L créé pendant le pas** (`d8c51c5`, parent = gel `cb15dcf1`, patron D8 / pas A autogluon, même gabarit que les 3 autres binds 4L) sur la nouvelle branche `aspace-v5-native` du fork `Amdkn/gsd-core` ; re-appliqué verbatim sur `next` (`1214039`).
3. **Corrections de mesure en cours :**
   - gstack « 80 SKILL.md » → **75** (le comptage initial comptait 5 fixtures `*-SKILL.md` ; l'adapter comptait 3 SKILL.md de `node_modules/playwright-core` installés par `bun install` — exclusion node_modules ajoutée).
   - gsd-core « 109 workflows » → **91 fichiers à la racine + 18 sous-dossiers (187 fichiers)**.
   - gsd-core `bin/lib/` : la mesure brute (265 .cjs) est polluée par `npm run build:lib` (ADR-457 : artefacts .cjs gitignored compilés dans ce dossier) — la mesure porte sur les **9 sources suivies**.
4. **/tmp tmpfs 512 Mo saturé** (100 % au run EGM) par les clones des autres pistes (`/tmp/f1-3-repo` 193 Mo, `/tmp/v5-p1` 139 Mo, non touchés) ; `TMPDIR=$HOME/workspace/.tmp-pas-c` pour EGM, gstack et gsd-core ; seul `/tmp/pytest-of-root` (20 Mo, mes propres résidus) supprimé.

## Points à trancher (pour le coordinateur / 13e)

1. **H-C3 gstack NON VERT strict** — suite bornée `--quick` rouge au gel (726) comme sur l'adapté (729), grappes environnementales pré-existantes (navigateur/GPU absents, CLI codex absent, timeouts). Aucune réduction appliquée. Décision attendue : accepter le pas avec réserve (même posture que pas B D-B2), ou autre.
2. **H-C3 gsd-core NON VERT strict** — suite bornée rouge au gel (50 086/3) comme sur l'adapté (50 087/2), 2 échecs environnementaux identiques (#1634 umask, npm-audit 403 proxy VM) ; delta = flaky pi-package passé au run adapté. Aucune réduction appliquée. Décision attendue : accepter le pas avec réserve (même posture que pas B D-B2), ou autre.

## Réserves

1. superpowers : run 1 de la baseline flaky (exit 1, aucune assertion en échec) — log conservé (`logs-suite-baseline-run1-flaky.log`).
2. EGM : run 1 de la baseline en échec environnemental (/tmp plein) — log conservé (`logs-suite-baseline-run1-tmp-plein.log`).
3. gstack : dérive 101, gel tenu ; correction de mesure SKILL.md 80 → 75.
4. gsd-core : build:lib génère 256 .cjs gitignored dans `bin/lib/` (ADR-457) ; ancien fork `Amdkn/get-shit-done` non touché (H-A7). Suite : 2 runs invalides conservés comme évidence (shard 1 adapté tentative 1 : orage EPERM sandbox 16 285/79, log `logs-suite-adapte-shard1-eperm-orage.log` ; shard 3 adapté tentative 1 tué par reboot VM à 6/9, log `logs-suite-adapte-shard3-tue-reboot-6sur9.log`). VM rebootée 2× pendant le run adapté (~15:24, ~17:25 UTC) ; charge First Light (llama-server) présente pendant les runs.
5. Aucun secret, aucune dépense, aucune activation client, aucun test sur numéro réel ; `~/workspace/v5-repo/` jamais utilisé pour pousser.

## Intégration (§6) — commit prêt, PR EN ATTENTE (bloquant master)

- Clone `~/workspace/v5-repo-dn053-pc/`, branche `a0/dn053-pas-c`, commit **`1f75556`** (amend de `b61b890` — gitlink gsd-core restauré, voir § Hold-outs). 19 fichiers : 12 fiches/manifestes/audits (levels 0 → 1), 4 gitlinks (dont renommage get-shit-done → gsd-core), `.gitmodules` renommé, registre 11 → 7. Base : **`0065bc5`** (dernier master à arbre complet, 2026-11-11 05:00 UTC).
- **BLOQUANT — arbre master effacé depuis 05:05 UTC :** le commit `feb338e` (« Pulse workgraph 05:05 ») a pour parent `0065bc5` mais son arbre ne contient QUE `00_Memoire` ; tous les commits master suivants (jusqu'à `df115f9`, 12:03 UTC, vérifié à l'API) ont le même arbre réduit. `01_Forkable`, `02_Factory`, `.gitmodules`, `AGENTS.md`, etc. ont disparu de l'arbre master pendant ~13 h — les pulses Workgraph committent depuis un checkout ne contenant que `00_Memoire`. Conséquence : la PR ne peut pas être ouverte contre le master actuel (le merge laisserait master partiel : 00_Memoire + 01_Forkable sans le reste de l'arbre). **Décision attendue du coordinateur :** restaurer l'arbre master depuis `0065bc5` + corriger le processus pulse (commit depuis un checkout complet), puis ouvrir la PR depuis cette branche ; jugement indépendant et merge ensuite, reçus `G-20261111-017` (livraison) / `G-20261111-018` (merge).
- Branche poussée sur origin (`a0/dn053-pas-c`, commit `1f75556`) — le commit est disponible pour le jugement dès que la base est réglée.

## Évidence et environnements

- `evidence/D-N053/c/superpowers/` : fiche, manifeste (levels 0), audit, rapport, logs suite gel/adapté, smoke, netns.
- `evidence/D-N053/c/elephant-goldfish-model/` : idem.
- `evidence/D-N053/c/gstack/` : idem + listes des fichiers en échec gel/adapté.
- `evidence/D-N053/c/gsd-core/` : idem + `NOTE-CORRECTION-BASELINE.md` (runs 1–8, causes racines, carte des filesystems, environnement final), logs suite gel/adapté par shard, logs des runs invalides conservés.
- `evidence/D-N053/c/harness-pas-c.py`, `evidence/D-N053/c/RESULTS-D-N053-C.json`, `evidence/D-N053/c/log.md`, `evidence/D-N053/c/RAPPORT-PAS-C.md` (ce fichier).
- Venvs : `~/workspace/.venvs-dn053/pas-c` (pytest 9.2.0 + pyyaml), `~/workspace/.venvs-dn053/pas-c-egm` (pytest 8.3.5 + pyyaml 6.0.2). Node 22.21.1 (`~/workspace/.tools/node-v22.21.1-linux-x64`), bun 1.4.4, Node v24.22.1. Clones de travail : `~/workspace/{superpowers,elephant-goldfish-model,gstack,gsd-core}-repo`.
