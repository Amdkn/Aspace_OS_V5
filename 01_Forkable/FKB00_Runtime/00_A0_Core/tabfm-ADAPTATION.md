# Fiche d'adaptation — tabfm (état 1, D-N053 pas A)

**Adresse :** `fiber:a0:tabfm` (design D-N053, Clara)
**Manifeste :** `tabfm.manifest.json` (même domicile, `00_A0_Core/`)
**Audit télémétrie :** `tabfm-TELEMETRY-AUDIT.md` (même domicile)
**Statut :** état 1 Adapté (fiche + adapter + manifeste, tests verts) — validation 13e en attente (le coordinateur intègre, Ryan ouvre la PR V5, régime R10). `levels.current` = 0 dans le manifeste, monté à 1 à l'intégration par le parent.

## Commit gelé

- **Fork :** `Amdkn/tabfm` (parent `google-research/tabfm`, branche `main`, licence Apache-2.0).
- **Gel : `fbb6655`** — « Merge pull request #97 from asdespot/fix/pytorch-jaxtyping-array-import », 2026-08-18T17:12:51Z. HEAD amont au 2026-11-10 (dérive 0, vérifiée à l'API le jour même).
- **Bind Cordis Fiber (16L) : `a8d6be9`** — `aspace-plugin.json` sur la branche `aspace-v5-native` (parent = gel).
- **Tout commit amont ultérieur exige un amendement de design**, jamais un fast-forward silencieux.

## Adapter

- **Paquet :** `aspace-tabfm-adapter` (`aspace_tabfm_adapter` 0.1.0), commit `0a56dff` sur le fork. **Seul code A'Space du fork** (H-M6) — l'amont est byte-identique au gel (diff gel→adapter = 3 fichiers adapter seuls, +212 insertions, 0 modification amont — vérifié par `git diff`).
- **Surface :** `validate()` → dict (gel, licence, import amont, poids dans le fork, 0 appel réseau) ; `doctor()` → liste de contrôles ; `describe()` → manifeste machine ; constantes épinglées (`PINNED_UPSTREAM_COMMIT = fbb6655`, `BIND_COMMIT = a8d6be9`, `FIBER_ADDRESS`).
- **Bind re-appliqué sur `main` :** commit `a6e899e` au-dessus de l'adapter (F8 D2) — `aspace-plugin.json` VERBATIM du bind `a8d6be9` (diff vide, vérifié). **Le pin = le commit adapter `0a56dff`.**
- **Smoke tests :** 6 passed in 14.54s (`aspace-tabfm-adapter/tests/test_smoke.py`, 6 tests).

## Tests au gel et sur le fork adapté

- **Au gel `fbb6655` (baseline) : 56 passed, 22 warnings in 228.79s (0:03:48) (avec jax+chex ; sans jax : 24 passed, 32 skipped, 1 warning in 57.21s)** (228.79s (0:03:48)).
- **Sur le fork adapté (`0a56dff`) : 56 passed, 22 warnings in 266.51s (0:04:26)** (266.51s (0:04:26)).
- Suite bornee torch + jax (voir SUITES-BORNEES-GROUPE-2.md). Baseline sans jax : 24 passed, 32 skipped (tests jax `skipUnless(HAS_JAX)` — `chex` manquait alors) ; baseline avec jax+chex : 56 passed, 0 skipped. Hors perimetre : `tabfm/src/jax/*`, `tabfm/src/pytorch/model_test.py` (parite torch↔jax), `classifier_and_regressor_multidevice_test.py` (multi-device).
- Commande suite : `PYTHONPATH=. python -m pytest tabfm/src/classifier_and_regressor_test.py tabfm/src/classifier_and_regressor_pytorch_test.py -q` (venv dédié, `PYTHONPATH` sur le paquet amont — aucune installation dans le clone).
- TabFM : Tabular Foundation Model, classification/regression zero-shot par in-context learning (backends jax / pytorch). Poids non-commerciaux, confines au profil interne.

## Télémétrie

**Zéro par contrat.** Voir `tabfm-TELEMETRY-AUDIT.md` : scan statique (0 SDK télémétrie, seuls téléchargements de poids explicites par `from_pretrained`) + dépendances auditées + import et `validate()` réussis dans un namespace réseau sans interface (0 appel sortant possible).

## Confinement

CONFINEMENT PROFIL INTERNE (D-N052 D3, design D-N053 D3) : les POIDS TabFM sont non-commerciaux ; jamais en B2B, jamais montes dans le fork (les miroirs HF sont le travail R1). Le code du repo est Apache-2.0.

## Divergence (dette portée par le cœur Buzz)

Surface d'API epinglee : l'adapter ne depend d'aucune API amont — il constate. Dérive amont 0 au 2026-11-10 (gel = HEAD amont). Revisite par signal uniquement.

## Références

- Design D-N053 (Clara, 2026-11-10) : `~/workspace/v4-factory/plans/ADAPTATION-TOUS-MODULES-RUNTIME-plan-borne.md` (D1–D16, H-M1..M7, H-A1..H-A8).
- Discover de Bill (corrigé) : `~/workspace/architecture-compagnons/discover-adaptation-tous-modules-runtime.md`.
- Évidences : `~/workspace/v4-factory/evidence/D-N053/a/tabfm/` (fiche + manifeste + audit, logs baseline / adapté / smoke / netns, rapport).
- Fork : https://github.com/Amdkn/tabfm (gel `fbb6655`, adapter `0a56dff`, bind re-appliqué `a6e899e`).
