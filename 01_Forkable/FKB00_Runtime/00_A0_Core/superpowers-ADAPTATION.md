# Fiche d'adaptation — superpowers (état 1, D-N053 pas C, canonique MasterSpec)

**Adresse :** `fiber:a0:superpowers` (design D-N053, Clara ; design signé pas C D-C0..D-C3)
**Manifeste :** `superpowers.manifest.json` (même domicile, `00_A0_Core/`)
**Audit télémétrie :** `superpowers-TELEMETRY-AUDIT.md` (même domicile)
**Statut :** état 1 Adapté (fiche + adapter + manifeste, tests verts) — validation 13e en attente (le coordinateur intègre, régime R10). `levels.current` = 0 dans le manifeste, monté à 1 à l'intégration par le parent.

## Commit gelé

- **Fork :** `Amdkn/superpowers` (parent `obra/superpowers`, branche `main`, licence MIT).
- **Gel : `22f0b463`** — « Release v7.0.2: brainstorming tuning, harness bootstrap fixes, SDD helper fixes (#2657) », 2026-11-03. Dérive 0 vérifiée à l'API (fork main = gel avant adaptation).
- **Bind Cordis Fiber (4L) : `4ca2922`** — `aspace-plugin.json` sur la branche `aspace-v5-native` (parent = gel).
- **Tout commit amont ultérieur exige un amendement de design**, jamais un fast-forward silencieux.

## Adapter

- **Paquet :** `aspace-superpowers-adapter` (`aspace_superpowers_adapter` 0.1.0), commit `5813de0` sur le fork. **Seul code A'Space du fork** (H-M6) — l'amont est byte-identique au gel (diff gel→adapter = 3 fichiers adapter seuls, +378 insertions, 0 modification amont — vérifié par `git diff` et à l'API).
- **Surface :** `validate()` → dict (gel, licence, comptage des 15 skills, frontmatter name + description, cohérence index, hooks/scripts/index.js/plugins multi-hôtes, 0 appel réseau) ; `doctor()` → liste de 8 contrôles ; `describe()` → manifeste machine ; constantes épinglées (`PINNED_UPSTREAM_COMMIT = 22f0b463`, `BIND_COMMIT = 4ca2922`, `FIBER_ADDRESS`).
- **Bind re-appliqué sur `main` :** commit `a73b34d` au-dessus de l'adapter (F8 D4) — `aspace-plugin.json` VERBATIM du bind `4ca2922` (blob byte-identique, sha256 `f8b61f7d…`, vérifié). **Le pin = le commit adapter `5813de0`.**
- **Smoke tests :** 6 passed in 0.08s (`aspace-superpowers-adapter/tests/test_smoke.py`, 6 tests).

## Tests au gel et sur le fork adapté

- **Au gel `22f0b463` (baseline) : suite amont bornée VERTE** — `npm test` dans `tests/brainstorm-server/` (7 fichiers `*.test.js` node + 2 scripts shell) : 139 PASS (32 + 15 + 3 + 20 + 7 + 34 + 13 + 8 + 7). Premier run : exit 1 sans aucune assertion en échec (log tronqué en pleine section lifecycle, aucun `FAIL`) — flakiness de timing/port de la VM, re-run exit 0, 139/139 ; le run 1 est conservé (`logs-suite-baseline-run1-flaky.log`).
- **Sur le fork adapté (`5813de0`) : identique** — `npm test` exit 0, 139 PASS, mêmes 9 sections.
- `run-skill-tests.sh` **exclu** par D-C2 (CLI Claude absent + quota modèle). Aucune suite inventée. Commande suite : `cd tests/brainstorm-server && npm install && npm test` (Node v24.22.1).
- superpowers est le framework de skills **canonique** MasterSpec (§D5) : les 3 autres modules du pas C sont des références du canonique, pas des frameworks parallèles.

## Index mesuré (au gel, au fichier)

- 15 dossiers dans `skills/`, 15 `SKILL.md`, 15/15 frontmatters `name` + `description` cohérents (name = nom du dossier), 0 manquante, 0 inattendue.
- `hooks/` (`hooks.json`, `hooks-cursor.json`, `session-start`), `scripts/` (5 scripts shell), `index.js` racine, plugins multi-hôtes (`.claude-plugin`, `.codex-plugin`, `.opencode`, `.pi`).
- **H-C6 :** superpowers nommé canonique AVANT l'adaptation des 3 autres (premier adapter du pas, ordre D-C0) ; l'adapter nomme les 3 références sans les adapter.

## Télémétrie

**Zéro par contrat.** Voir `superpowers-TELEMETRY-AUDIT.md` : scan statique (0 SDK télémétrie ; 1 image de marque distante primeradiant.com, omise par opt-out explicite, jamais déclenchée par l'adapter) + adapter stdlib seule + `validate()` et `doctor()` réussis dans un namespace réseau sans interface (0 appel sortant possible).

## Confinement

Aucun confinement commercial : code et skills MIT. Usage B2B autorisé par la licence.

## Divergence (dette portée par le cœur Buzz)

Surface d'API épinglée : l'adapter ne dépend d'aucune API amont instable — il ne fait que constater (comptage, cohérence, intégrité). Toute dérive amont est un événement de design (revisite par signal, jamais de fast-forward silencieux). Le gel est le HEAD amont au 2026-11-11 (dérive 0 vérifiée à l'API le jour même).

## Références

- Design D-N053 (Clara, 2026-11-10) : `~/workspace/v4-factory/plans/ADAPTATION-TOUS-MODULES-RUNTIME-plan-borne.md` (D1–D16, H-M1..M7, H-A1..H-A8).
- Design signé pas C (2026-11-11) : `~/workspace/v4-factory/plans/DESIGN-D-N053-PAS-C-PROJET.md` (D-C0..D-C3).
- Discover pas C : `~/workspace/v4-factory/evidence/D-N053/c/DISCOVER-PAS-C.md`.
- Évidences : `~/workspace/v4-factory/evidence/D-N053/c/superpowers/` (fiche + manifeste + audit, logs suite / smoke / netns, rapport).
- Fork : https://github.com/Amdkn/superpowers (gel `22f0b463`, adapter `5813de0`, bind re-appliqué `a73b34d`).
