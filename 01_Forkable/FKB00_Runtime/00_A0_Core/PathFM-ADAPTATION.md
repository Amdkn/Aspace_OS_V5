# Fiche d'adaptation — PathFM (état 1, D-N053 pas A)

**Adresse :** `fiber:a0:PathFM` (design D-N053, Clara)
**Manifeste :** `PathFM.manifest.json` (même domicile, `00_A0_Core/`)
**Audit télémétrie :** `PathFM-TELEMETRY-AUDIT.md` (même domicile)
**Statut :** état 1 Adapté (fiche + adapter + manifeste, tests verts) — validation 13e en attente (le coordinateur intègre, Ryan ouvre la PR V5, régime R10). `levels.current` = 0 dans le manifeste, monté à 1 à l'intégration par le parent.

## Commit gelé

- **Fork :** `Amdkn/PathFM` (parent `autogluon/PathFM`, branche `main`, licence CC BY-NC 4.0).
- **Gel : `8a3a42c`** — « Prepare PathFM release », 2026-11-01T06:57:08Z. HEAD amont au 2026-11-10 (dérive 0, vérifiée à l'API le jour même).
- **Bind Cordis Fiber (16L) : `d94942e`** — `aspace-plugin.json` sur la branche `aspace-v5-native` (parent = gel).
- **Tout commit amont ultérieur exige un amendement de design**, jamais un fast-forward silencieux.

## Adapter

- **Paquet :** `aspace-PathFM-adapter` (`aspace_pathfm_adapter` 0.1.0), commit `8bcdd5b` sur le fork. **Seul code A'Space du fork** (H-M6) — l'amont est byte-identique au gel (diff gel→adapter = 3 fichiers adapter seuls, +212 insertions, 0 modification amont — vérifié par `git diff`).
- **Surface :** `validate()` → dict (gel, licence, import amont, poids dans le fork, 0 appel réseau) ; `doctor()` → liste de contrôles ; `describe()` → manifeste machine ; constantes épinglées (`PINNED_UPSTREAM_COMMIT = 8a3a42c`, `BIND_COMMIT = d94942e`, `FIBER_ADDRESS`).
- **Bind re-appliqué sur `main` :** commit `e4a9009` au-dessus de l'adapter (F8 D2) — `aspace-plugin.json` VERBATIM du bind `d94942e` (diff vide, vérifié). **Le pin = le commit adapter `8bcdd5b`.**
- **Smoke tests :** 6 passed in 77.34s (0:01:17) (`aspace-PathFM-adapter/tests/test_smoke.py`, 6 tests).

## Tests au gel et sur le fork adapté

- **Au gel `8a3a42c` (baseline) : N/A — pas de suite amont** (?).
- **Sur le fork adapté (`8bcdd5b`) : N/A — pas de suite amont (smoke + import)** (?).
- PAS DE SUITE AMONT (verifie : aucun repertoire tests, aucune config pytest dans le repo). Suite de substitution : smoke adapter 6/6 + import `from pathfm import PathFM, PathFMPipeline` avec les dependances epinglees amont (torch 2.9.1, transformers 5.13.0, numpy 1.26.4, chronos-forecasting 2.3.1 PyPI). Aucun `from_pretrained` (exigerait des poids — travail R1).
- Commande suite : `(pas de suite amont — voir ci-dessous)` (venv dédié, `PYTHONPATH` sur le paquet amont — aucune installation dans le clone).
- PathFM : generative forecasting de trajectoires multivariees (modeles chaotiques). Code CC BY-NC 4.0, modeles non-commerciaux, confines au profil interne.

## Télémétrie

**Zéro par contrat.** Voir `PathFM-TELEMETRY-AUDIT.md` : scan statique (0 SDK télémétrie, seuls téléchargements de poids explicites par `from_pretrained`) + dépendances auditées + import et `validate()` réussis dans un namespace réseau sans interface (0 appel sortant possible).

## Confinement

CONFINEMENT PROFIL INTERNE (design D-N053 D3) : le CODE du repo PathFM est CC BY-NC 4.0 (LICENSE lue par Clara) et les MODELES PathFM sont non-commerciaux ; jamais en B2B (verifie a la configuration du profil commercial, H-A5 : `aspace_precheck_weights.py` NON_COMMERCIAL + `assert_commercial_safe()`). Manifeste ML corrige a CC BY-NC 4.0 (acte nomme du pas A, evidence D-N053/a/PathFM/).

## Divergence (dette portée par le cœur Buzz)

Surface d'API epinglee : l'adapter ne depend d'aucune API amont — il constate. Dérive amont 0 au 2026-11-10 (gel = HEAD amont). Le bind a ete cree par ce pas (D8) : `aspace-plugin.json` copie verbatim du format ML 16L (seuls name, submodule_path, sovereign_fork_url changent) ; ajout force car le `.gitignore` amont ignore `*.json`. Revisite par signal uniquement.

## Références

- Design D-N053 (Clara, 2026-11-10) : `~/workspace/v4-factory/plans/ADAPTATION-TOUS-MODULES-RUNTIME-plan-borne.md` (D1–D16, H-M1..M7, H-A1..H-A8).
- Discover de Bill (corrigé) : `~/workspace/architecture-compagnons/discover-adaptation-tous-modules-runtime.md`.
- Évidences : `~/workspace/v4-factory/evidence/D-N053/a/PathFM/` (fiche + manifeste + audit, logs baseline / adapté / smoke / netns, rapport).
- Fork : https://github.com/Amdkn/PathFM (gel `8a3a42c`, adapter `8bcdd5b`, bind re-appliqué `e4a9009`).
