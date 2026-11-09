# Fiche d'adaptation — rrsi (D-N048 V3a)

**Adresse :** `fiber:a0:rrsi`
**Manifeste :** `rrsi.manifest.json` (même domicile)
**Audit télémétrie :** `rrsi-TELEMETRY-AUDIT.md` (même domicile)
**Statut :** état 0 Basique → 1 Adapté en cours (fiche + adapter + manifeste, tests verts)
**Licence :** Apache-2.0

## Commit gelé

- **Fork :** `Amdkn/rrsi` (parent `google-research/rrsi`, Apache-2.0, branche `main`).
- **Gel : `be50316`** — version 0.1.0.
- **Tout commit amont ultérieur exige un amendement de design**, jamais un fast-forward silencieux (D5).

## Adapter

- **Dossier :** `aspace-rrsi-adapter/` (contrat JSON + smoke test pytest + README), commit `cc424cc` sur le fork. **Seul code A'Space du fork** — le paquet amont est byte-identique au gel.
- **Surface (contrat seul, §1.5) :** cœur pur de la méthode, hors-ligne — `rrsi.schedule.budget_table(T, b_min, b_max)`, `rrsi.config.RRSIConfig` (T=20, b_min=1, b_max=4), `rrsi.selection.select_round`, `rrsi.history.History` ; CLI `python3 rrsi.py --help` / `status` (lecture seule).
- **Jamais :** tout appel modèle (Claude sur Vertex AI, `llm.py`), les domaines `eng` / `workspace` (runners, passerelle MCP, socket locale), `third_party/archipelago` (runners de benchmark, httpx), tout appel réseau.
- **Smoke tests :** 5/5 verts (cœur pur + `--help` de la CLI, hors-ligne).

## Tests au gel et sur le fork adapté

- **Au gel `be50316` : 8 passés (8).** Suite `pytest tests/ -q` — « Unit tests for the method core: no API, no benchmark » (en-tête de `test_core.py`).
- **Sur le fork adapté (`cc424cc`) : 8 passés + smoke 5/5.** L'adapter ajoute 5 tests verts.
- **Limite franche :** pytest absent du Python système (PEP 668) — suite courue dans un venv dédié (`~/workspace/.tmp/venv-pytest`, pytest 9.2.0). La dépendance déclarée `anthropic[vertex]` n'est jamais importée par le cœur testé.

## Télémétrie

**Zéro SDK.** Voir `rrsi-TELEMETRY-AUDIT.md` : les occurrences du mot-clé sont des faux positifs (segments de trajectoire / ELF) ; réseau confiné aux domaines de benchmark (socket locale 127.0.0.1 pour la passerelle, httpx dans `third_party/archipelago`), jamais invoqués par l'adapter.

## Divergence (dette portée par le cœur Buzz, lane Clara / 12e)

- **Dépendance introduite par le design :** aucune — l'adapter n'expose que le cœur pur.
- **Ré-audit télémétrie :** à chaque changement de commit gelé ou d'adapter, et au minimum à chaque transition d'état (D3).

## Références

- Design D-N048 (Clara, 2026-11-09) : `~/workspace/v4-factory/plans/FORKS-AMONT-21-plan-borne-vagues.md`.
- Évidences : `~/workspace/v4-factory/evidence/D-N048/PROGRESS-D-N048.md`.
- Fork : https://github.com/Amdkn/rrsi (gel `be50316`, adapter `cc424cc`).
