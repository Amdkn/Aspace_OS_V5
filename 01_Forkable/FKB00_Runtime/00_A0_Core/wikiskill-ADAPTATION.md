# Fiche d'adaptation — wikiskill (D-N048 V3a)

**Adresse :** `fiber:a0:wikiskill`
**Manifeste :** `wikiskill.manifest.json` (même domicile)
**Audit télémétrie :** `wikiskill-TELEMETRY-AUDIT.md` (même domicile)
**Statut :** état 2 Vérifié (hold-outs verts + validation 13e, PR #9 mergée `d0631f1`)
**Licence :** MIT

## Commit gelé

- **Fork :** `Amdkn/wikiskill` (parent `ashutoshsinghpr7/wikiskill`, MIT, branche `main`).
- **Gel : `cdc291c`** — version 0.1.5, zéro dépendance.
- **Tout commit amont ultérieur exige un amendement de design**, jamais un fast-forward silencieux (D5).

## Adapter

- **Dossier :** `aspace-wikiskill-adapter/` (contrat JSON + smoke test pytest + README), commit `59a6a04` sur le fork. **Seul code A'Space du fork** — le paquet amont est byte-identique au gel.
- **Surface (contrat seul, §1.5) :** `wikiskill.cli:main(argv)` ; `wikiskill init <domain> --ws <dir>` (génère le bench démo depuis une graine, matérialise le workspace en local) ; `wikiskill status <domain> --ws <dir>` (lecture de l'état local).
- **Jamais :** `wikiskill evolve` (backend agent / modèle), tout appel réseau, toute écriture hors du workspace passé en `--ws`.
- **Smoke tests :** 4/4 verts (init + status hors-ligne dans un répertoire scratch).

## Tests au gel et sur le fork adapté

- **Au gel `cdc291c` : 73 passés, 1 skipped (74).** Suite `pytest tests/ -q` (CI amont : `pip install -e .`, pyflakes, `pytest tests/ -q`).
- **Sur le fork adapté (`59a6a04`) : 73 passés, 1 skipped + smoke 4/4.** L'adapter ajoute 4 tests verts.
- **Limite franche :** pytest absent du Python système (PEP 668) — suite courue dans un venv dédié (`~/workspace/.tmp/venv-pytest`, pytest 9.2.0).

## Télémétrie

**Zéro.** Voir `wikiskill-TELEMETRY-AUDIT.md` : scan statique (zéro occurrence de SDK télémétrie, zéro appel réseau dans le paquet) + preuve d'exécution (init + status hors-ligne, répertoire scratch, aucun appel sortant).

## Divergence (dette portée par le cœur Buzz, lane Clara / 12e)

- **Dépendance introduite par le design :** aucune — l'adapter ne fait que piloter la CLI amont hors-ligne.
- **Ré-audit télémétrie :** à chaque changement de commit gelé ou d'adapter, et au minimum à chaque transition d'état (D3).

## Références

- Design D-N048 (Clara, 2026-11-09) : `~/workspace/v4-factory/plans/FORKS-AMONT-21-plan-borne-vagues.md`.
- Évidences : `~/workspace/v4-factory/evidence/D-N048/PROGRESS-D-N048.md`.
- Fork : https://github.com/Amdkn/wikiskill (gel `cdc291c`, adapter `59a6a04`).
