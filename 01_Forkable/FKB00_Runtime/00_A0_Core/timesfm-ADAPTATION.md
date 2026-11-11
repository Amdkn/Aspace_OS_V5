# Fiche d'adaptation — timesfm (état 1, D-N053 pas A)

**Adresse :** `fiber:a0:timesfm` (design D-N053, Clara)
**Manifeste :** `timesfm.manifest.json` (même domicile, `00_A0_Core/`)
**Audit télémétrie :** `timesfm-TELEMETRY-AUDIT.md` (même domicile)
**Statut :** état 1 Adapté (fiche + adapter + manifeste, tests verts) — validation 13e en attente (le coordinateur intègre, Ryan ouvre la PR V5, régime R10). `levels.current` = 0 dans le manifeste, monté à 1 à l'intégration par le parent.

## Commit gelé

- **Fork :** `Amdkn/timesfm` (parent `google-research/timesfm`, branche `master`, licence Apache-2.0).
- **Gel : `e51928e`** — « Update README.md », 2026-09-29T19:36:24Z. HEAD amont au 2026-11-10 (dérive 0, vérifiée à l'API le jour même).
- **Bind Cordis Fiber (16L) : `1050570`** — `aspace-plugin.json` sur la branche `aspace-v5-native` (parent = gel).
- **Tout commit amont ultérieur exige un amendement de design**, jamais un fast-forward silencieux.

## Adapter

- **Paquet :** `aspace-timesfm-adapter` (`aspace_timesfm_adapter` 0.1.0), commit `7cb4f64` sur le fork. **Seul code A'Space du fork** (H-M6) — l'amont est byte-identique au gel (diff gel→adapter = 3 fichiers adapter seuls, +212 insertions, 0 modification amont — vérifié par `git diff`).
- **Surface :** `validate()` → dict (gel, licence, import amont, poids dans le fork, 0 appel réseau) ; `doctor()` → liste de contrôles ; `describe()` → manifeste machine ; constantes épinglées (`PINNED_UPSTREAM_COMMIT = e51928e`, `BIND_COMMIT = 1050570`, `FIBER_ADDRESS`).
- **Bind re-appliqué sur `master` :** commit `e88dc6d` au-dessus de l'adapter (F8 D2) — `aspace-plugin.json` VERBATIM du bind `1050570` (diff vide, vérifié). **Le pin = le commit adapter `7cb4f64`.**
- **Smoke tests :** 6 passed in 14.97s (`aspace-timesfm-adapter/tests/test_smoke.py`, 6 tests).

## Tests au gel et sur le fork adapté

- **Au gel `e51928e` (baseline) : 63 passed in 148.47s (0:02:28)** (148.47s (0:02:28)).
- **Sur le fork adapté (`7cb4f64`) : 63 passed in 250.32s (0:04:10)** (250.32s (0:04:10)).
- Suite `tests/` (torch + flax ; la suite legacy `v1/tests/` jax est hors perimetre, cf. AGENTS.md du repo). `test_model_loading` travaille sur un checkpoint local (pas de telechargement).
- Commande suite : `PYTHONPATH=src python -m pytest tests/ -q` (venv dédié, `PYTHONPATH` sur le paquet amont — aucune installation dans le clone).
- TimesFM : Time Series Foundation Model (Google Research), backends torch / flax / mlx. Poids non-commerciaux, confines au profil interne.

## Télémétrie

**Zéro par contrat.** Voir `timesfm-TELEMETRY-AUDIT.md` : scan statique (0 SDK télémétrie, seuls téléchargements de poids explicites par `from_pretrained`) + dépendances auditées + import et `validate()` réussis dans un namespace réseau sans interface (0 appel sortant possible).

## Confinement

CONFINEMENT PROFIL INTERNE (D-N052 D3, design D-N053 D3) : les POIDS TimesFM sont non-commerciaux (licence Google non-commerciale des checkpoints) ; jamais en B2B, jamais montes dans le fork (les miroirs HF sont le travail R1). Le code du repo est Apache-2.0.

## Divergence (dette portée par le cœur Buzz)

Surface d'API epinglee : l'adapter ne depend d'aucune API amont — il constate. Dérive amont 0 au 2026-11-10 (gel = HEAD amont). Toute derive ulterieure est un signal de revisite, jamais un fast-forward.

## Références

- Design D-N053 (Clara, 2026-11-10) : `~/workspace/v4-factory/plans/ADAPTATION-TOUS-MODULES-RUNTIME-plan-borne.md` (D1–D16, H-M1..M7, H-A1..H-A8).
- Discover de Bill (corrigé) : `~/workspace/architecture-compagnons/discover-adaptation-tous-modules-runtime.md`.
- Évidences : `~/workspace/v4-factory/evidence/D-N053/a/timesfm/` (fiche + manifeste + audit, logs baseline / adapté / smoke / netns, rapport).
- Fork : https://github.com/Amdkn/timesfm (gel `e51928e`, adapter `7cb4f64`, bind re-appliqué `e88dc6d`).
