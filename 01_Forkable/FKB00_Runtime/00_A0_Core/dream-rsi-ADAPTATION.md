# Fiche d'adaptation — dream-rsi (D-N048 V3a)

**Adresse :** `fiber:a0:dream-rsi`
**Manifeste :** `dream-rsi.manifest.json` (même domicile)
**Audit télémétrie :** `dream-rsi-TELEMETRY-AUDIT.md` (même domicile)
**Statut :** état 2 Vérifié (hold-outs verts + validation 13e, PR #9 mergée `d0631f1`)
**Licence :** Apache-2.0

## Commit gelé

- **Fork :** `Amdkn/dream-rsi` (parent `google-research/dream-rsi`, Apache-2.0, branche `main`).
- **Gel : `8ec35bd`** — version 0.1.0.
- **Tout commit amont ultérieur exige un amendement de design**, jamais un fast-forward silencieux (D5).

## Adapter

- **Dossier :** `aspace-dream-rsi-adapter/` (contrat JSON + smoke test pytest + README), commit `fa0c8f0` sur le fork. **Seul code A'Space du fork** — le paquet amont est byte-identique au gel.
- **Surface (contrat seul, §1.5) :** `dream_rsi.cli.main:main(argv)` ; `dream-rsi --help` ; section `learning` (replay, export, allocate, discover, directions — hors-ligne).
- **Jamais :** `dream-rsi explore` / `evolve` (agent de codage réel, appels API), les évaluateurs KernelBench (requêtes POST vers un serveur GPU), tout appel réseau.
- **Smoke tests :** 5/5 verts (`--help` + import du paquet, hors-ligne).

## Tests au gel et sur le fork adapté

- **Au gel `8ec35bd` : 96 passés, 10 skipped, 1 deselected (107).** Suite `pytest tests/ -q` (pytest `-m 'not integration'` par défaut — les tests d'intégration appellent un agent réel).
- **Écart d'environnement corrigé, nommé :** premier run 95 passés / 1 échec — `test_kernel_client_defaults_follow_the_paper_protocol` échouait sur `ModuleNotFoundError: requests` (extra optionnel `kernel` non installé). Après installation des extras optionnels (`requests`, `pyyaml`, `numpy`, `scipy`, `psutil`) dans le venv : **96 passés, 10 skipped, 1 deselected**. Aucun changement de code ni de test.
- **Sur le fork adapté (`fa0c8f0`) : 96 passés, 10 skipped, 1 deselected + smoke 5/5.** L'adapter ajoute 5 tests verts.
- **Limite franche :** pytest absent du Python système (PEP 668) — suite courue dans un venv dédié (`~/workspace/.tmp/venv-pytest`, pytest 9.2.0).

## Télémétrie

**Zéro.** Voir `dream-rsi-TELEMETRY-AUDIT.md` : scan statique (zéro occurrence de SDK télémétrie, zéro appel réseau dans le paquet) ; réseau confiné aux évaluateurs KernelBench (`requests.post` vers un serveur GPU explicite), jamais invoqués par l'adapter.

## Divergence (dette portée par le cœur Buzz, lane Clara / 12e)

- **Dépendance introduite par le design :** aucune — l'adapter n'expose que la section hors-ligne.
- **Ré-audit télémétrie :** à chaque changement de commit gelé ou d'adapter, et au minimum à chaque transition d'état (D3).

## Références

- Design D-N048 (Clara, 2026-11-09) : `~/workspace/v4-factory/plans/FORKS-AMONT-21-plan-borne-vagues.md`.
- Évidences : `~/workspace/v4-factory/evidence/D-N048/PROGRESS-D-N048.md`.
- Fork : https://github.com/Amdkn/dream-rsi (gel `8ec35bd`, adapter `fa0c8f0`).
