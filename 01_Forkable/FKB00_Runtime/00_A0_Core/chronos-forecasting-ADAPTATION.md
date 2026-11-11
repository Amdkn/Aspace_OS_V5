# Fiche d'adaptation — chronos-forecasting (état 1, D-N053 pas A)

**Adresse :** `fiber:a0:chronos-forecasting` (design D-N053, Clara)
**Manifeste :** `chronos-forecasting.manifest.json` (même domicile, `00_A0_Core/`)
**Audit télémétrie :** `chronos-forecasting-TELEMETRY-AUDIT.md` (même domicile)
**Statut :** état 1 Adapté (fiche + adapter + manifeste, tests verts) — validation 13e en attente (le coordinateur intègre, Ryan ouvre la PR V5, régime R10). `levels.current` = 0 dans le manifeste, monté à 1 à l'intégration par le parent.

## Commit gelé

- **Fork :** `Amdkn/chronos-forecasting` (parent `amazon-science/chronos-forecasting`, branche `main`, licence Apache-2.0).
- **Gel : `1224faf`** — « Compute series lengths in row order so predict_df handles categorical item ids (#537) », 2026-10-05T14:25:02Z. HEAD amont au 2026-11-10 (dérive 0, vérifiée à l'API le jour même).
- **Bind Cordis Fiber (16L) : `e049fe2`** — `aspace-plugin.json` sur la branche `aspace-v5-native` (parent = gel).
- **Tout commit amont ultérieur exige un amendement de design**, jamais un fast-forward silencieux.

## Adapter

- **Paquet :** `aspace-chronos-forecasting-adapter` (`aspace_chronos_forecasting_adapter` 0.1.0), commit `c749362` sur le fork. **Seul code A'Space du fork** (H-M6) — l'amont est byte-identique au gel (diff gel→adapter = 3 fichiers adapter seuls, +212 insertions, 0 modification amont — vérifié par `git diff`).
- **Surface :** `validate()` → dict (gel, licence, import amont, poids dans le fork, 0 appel réseau) ; `doctor()` → liste de contrôles ; `describe()` → manifeste machine ; constantes épinglées (`PINNED_UPSTREAM_COMMIT = 1224faf`, `BIND_COMMIT = e049fe2`, `FIBER_ADDRESS`).
- **Bind re-appliqué sur `main` :** commit `8cb6d00` au-dessus de l'adapter (F8 D2) — `aspace-plugin.json` VERBATIM du bind `e049fe2` (diff vide, vérifié). **Le pin = le commit adapter `c749362`.**
- **Smoke tests :** 6 passed in 19.38s (`aspace-chronos-forecasting-adapter/tests/test_smoke.py`, 6 tests).

## Tests au gel et sur le fork adapté

- **Au gel `1224faf` (baseline) : 566 passed, 2 deselected, 20 xfailed, 51 warnings in 926.68s (0:15:26)** (926.68s (0:15:26)).
- **Sur le fork adapté (`c749362`) : 566 passed, 2 deselected, 20 xfailed, 48 warnings in 804.09s (0:13:24)** (804.09s (0:13:24)).
- Exclusion unique : les 2 tests `test_base_chronos_pipeline_loads_from_huggingface` (test_chronos.py, test_chronos_bolt.py) qui telechargent `amazon/chronos-t5-tiny` depuis le Hub — pas de telechargement de poids dans ce pas. Les 20 xfailed sont des xfail declares par l'amont (tests de quantification / precision mixte), identiques au gel et sur l'adapte.
- Commande suite : `PYTHONPATH=src python -m pytest test/ -k "not test_base_chronos_pipeline_loads_from_huggingface" -q` (venv dédié, `PYTHONPATH` sur le paquet amont — aucune installation dans le clone).
- Chronos : prevision de series temporelles pre-entrainee (Chronos, Chronos-2, Chronos-Bolt). Poids : telechargement explicite par l'utilisateur via from_pretrained, jamais monte dans le fork.

## Télémétrie

**Zéro par contrat.** Voir `chronos-forecasting-TELEMETRY-AUDIT.md` : scan statique (0 SDK télémétrie, seuls téléchargements de poids explicites par `from_pretrained`) + dépendances auditées + import et `validate()` réussis dans un namespace réseau sans interface (0 appel sortant possible).

## Confinement

Aucun confinement commercial : code Apache-2.0, poids Chronos distribues sous Apache-2.0 par l'amont. Usage B2B autorise par la licence.

## Divergence (dette portée par le cœur Buzz)

Surface d'API epinglee : l'adapter ne depend d'aucune API amont instable — il ne fait que constater (import du paquet, constantes). Toute derive amont est un evenement de design (revisite par signal, jamais de fast-forward silencieux). Le gel est le HEAD amont au 2026-11-10 (derive 0 verifiee a l'API le jour meme).

## Références

- Design D-N053 (Clara, 2026-11-10) : `~/workspace/v4-factory/plans/ADAPTATION-TOUS-MODULES-RUNTIME-plan-borne.md` (D1–D16, H-M1..M7, H-A1..H-A8).
- Discover de Bill (corrigé) : `~/workspace/architecture-compagnons/discover-adaptation-tous-modules-runtime.md`.
- Évidences : `~/workspace/v4-factory/evidence/D-N053/a/chronos-forecasting/` (fiche + manifeste + audit, logs baseline / adapté / smoke / netns, rapport).
- Fork : https://github.com/Amdkn/chronos-forecasting (gel `1224faf`, adapter `c749362`, bind re-appliqué `8cb6d00`).
