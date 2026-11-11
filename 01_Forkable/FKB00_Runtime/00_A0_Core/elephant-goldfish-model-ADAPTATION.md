# Fiche d'adaptation — elephant-goldfish-model (état 1, D-N053 pas C, référence du canonique)

**Adresse :** `fiber:a0:elephant-goldfish-model` (design D-N053, Clara ; design signé pas C D-C0..D-C3)
**Manifeste :** `elephant-goldfish-model.manifest.json` (même domicile, `00_A0_Core/`)
**Audit télémétrie :** `elephant-goldfish-model-TELEMETRY-AUDIT.md` (même domicile)
**Statut :** état 1 Adapté (fiche + adapter + manifeste, tests verts) — validation 13e en attente (le coordinateur intègre, régime R10). `levels.current` = 0 dans le manifeste, monté à 1 à l'intégration par le parent.

## Commit gelé

- **Fork :** `Amdkn/elephant-goldfish-model` (parent `google/elephant-goldfish-model`, branche `main`, licence Apache-2.0).
- **Gel : `113a3afc`** — « fix(review): save GoldfishContext URLs as files (#289) », 2026-11-03. Dérive 39 vérifiée à l'API (design : 36 — la dérive bouge, +3), amont vivant — pas de re-gel, revisite par signal.
- **Bind Cordis Fiber (4L) : `3d643fe`** — `aspace-plugin.json` sur la branche `aspace-v5-native` (parent = gel).
- **Tout commit amont ultérieur exige un amendement de design**, jamais un fast-forward silencieux.
- **Point de vigilance consigné :** le fork `main` portait 3 commits amont au-delà du gel (`0dfb5bf`, `ccf79c5`, `6a8001e`) ; `main` ramené au gel avant adaptation (forced update, `--force-with-lease`), les 3 commits restant verbatim sur `upstream/main` (`google/elephant-goldfish-model`, vérifié par `merge-base --is-ancestor`) — le parent de l'adapter est le gel, per design §3.

## Adapter

- **Paquet :** `aspace-elephant-goldfish-model-adapter` (`aspace_elephant_goldfish_model_adapter` 0.1.0), commit `4f4a076` sur le fork. **Seul code A'Space du fork** (H-M6) — l'amont est byte-identique au gel (diff gel→adapter = 3 fichiers adapter seuls, +365 insertions, 0 modification amont — vérifié par `git diff` et à l'API).
- **Surface :** `validate()` → dict (gel, licence, comptage des 7 skills, frontmatter name + license + description — scalaires pliés `>-` gérés —, TEST.md + test_scenarios.yaml par skill, agents/assets/distributions/resources, 0 appel réseau) ; `doctor()` → liste de 8 contrôles ; `describe()` → manifeste machine ; constantes épinglées (`PINNED_UPSTREAM_COMMIT = 113a3afc`, `BIND_COMMIT = 3d643fe`, `FIBER_ADDRESS`).
- **Bind re-appliqué sur `main` :** commit `e9b3cef` au-dessus de l'adapter (F8 D4) — `aspace-plugin.json` VERBATIM du bind `3d643fe` (blob byte-identique, `cmp` vide, vérifié). **Le pin = le commit adapter `4f4a076`.**
- **Smoke tests :** 6 passed in 0.04s (`aspace-elephant-goldfish-model-adapter/tests/test_smoke.py`, 6 tests, pytest 8.3.5).

## Tests au gel et sur le fork adapté

- **Au gel `113a3afc` (baseline) : suite amont bornée VERTE** — `pytest tests/unit` (18 modules, offline, per TESTING.md ; Node 22.21.1, pytest 8.3.5 + pyyaml 6.0.2) : **336 passed, 2 skipped** (skips : `test_copilot_adapter.py:102` et `test_cursor.py:123`, sondes natives opt-in, attendus). Premier run : exit 1, erreurs de fixture `test_packaging.py` (`shutil.copytree` vers /tmp) — cause environnementale, pas du code : **/tmp tmpfs 512 Mo plein à 100 %** par les clones des autres pistes (`/tmp/f1-3-repo` 193 Mo, `/tmp/v5-p1` 139 Mo, non touchés) ; re-run avec `TMPDIR=$HOME/workspace/.tmp-pas-c` : exit 0, 336 passed, 2 skipped ; le run 1 est conservé (`logs-suite-baseline-run1-tmp-plein.log`).
- **Sur le fork adapté (`4f4a076`) : identique** — 336 passed, 2 skipped, mêmes 2 skips.
- Job site (Astro) **hors borne** et intégrations opt-in **exclues** par D-C2 (CLI authentifiés + quota). Aucune suite inventée.
- EGM est une **référence** du canonique `fiber:a0:superpowers` (§D5) : ses skills sont disponibles à travers le framework canonique, pas comme un framework parallèle.

## Index mesuré (au gel, au fichier)

- 7 dossiers dans `skills/`, 7 `SKILL.md`, 7/7 frontmatters `name` + `license: Apache-2.0` + `description` cohérents, 0 manquante, 0 inattendue.
- 7/7 `TEST.md`, 7/7 `test_scenarios.yaml`, 7/7 `agents/`, 7/7 `assets/` ; `references/` pour bootstrap et draft seulement.
- `distributions/` (claude), `resources/` (README.md, document_standards, execution_instructions.md).

## Télémétrie

**Zéro par contrat.** Voir `elephant-goldfish-model-TELEMETRY-AUDIT.md` : scan statique (0 SDK télémétrie ; le mot « telemetry » n'apparaît que comme critère de design dans une table de la skill brainstorm, pas comme du code) + adapter stdlib seule + `validate()` et `doctor()` réussis dans un namespace réseau sans interface (0 appel sortant possible).

## Confinement

Aucun confinement commercial : code et skills Apache-2.0. Usage B2B autorisé par la licence.

## Divergence (dette portée par le cœur Buzz)

Surface d'API épinglée : l'adapter ne dépend d'aucune API amont instable — il ne fait que constater (comptage, cohérence, intégrité). Toute dérive amont est un événement de design (revisite par signal, jamais de fast-forward silencieux). Dérive 39 au 2026-11-11 ; le gel reste `113a3afc`.

## Références

- Design D-N053 (Clara, 2026-11-10) : `~/workspace/v4-factory/plans/ADAPTATION-TOUS-MODULES-RUNTIME-plan-borne.md` (D1–D16, H-M1..M7, H-A1..H-A8).
- Design signé pas C (2026-11-11) : `~/workspace/v4-factory/plans/DESIGN-D-N053-PAS-C-PROJET.md` (D-C0..D-C3).
- Discover pas C : `~/workspace/v4-factory/evidence/D-N053/c/DISCOVER-PAS-C.md`.
- Évidences : `~/workspace/v4-factory/evidence/D-N053/c/elephant-goldfish-model/` (fiche + manifeste + audit, logs suite / smoke / netns, rapport).
- Fork : https://github.com/Amdkn/elephant-goldfish-model (gel `113a3afc`, adapter `4f4a076`, bind re-appliqué `e9b3cef`).
