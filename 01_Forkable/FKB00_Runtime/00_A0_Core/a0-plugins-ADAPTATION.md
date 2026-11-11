# Fiche d'adaptation — a0-plugins (état 1, D-N053 pas B)

**Adresse :** `fiber:a0:a0-plugins` (design D-N053, Clara ; design signé pas B D-B0..D-B3)
**Manifeste :** `a0-plugins.manifest.json` (même domicile, `00_A0_Core/`)
**Audit télémétrie :** `a0-plugins-TELEMETRY-AUDIT.md` (même domicile)
**Statut :** état 1 Adapté (fiche + adapter + manifeste, tests verts) — validation 13e en attente (le coordinateur intègre, régime R10). `levels.current` = 0 dans le manifeste, monté à 1 à l'intégration par le parent.

## Commit gelé

- **Fork :** `Amdkn/a0-plugins` (parent `agent0ai/a0-plugins`, branche `main`, licence MIT).
- **Gel : `d040c3f`** — « Merge pull request #682 from TerminallyLazy/add/code-intelligence », 2026-11-04T16:31:48Z. HEAD amont au 2026-11-11 (dérive 0, vérifiée à l'API le jour même).
- **Bind Cordis Fiber (2L) : `f73f767`** — `aspace-plugin.json` sur la branche `aspace-v5-native` (parent = gel).
- **Tout commit amont ultérieur exige un amendement de design**, jamais un fast-forward silencieux.

## Adapter

- **Paquet :** `aspace-a0-plugins-adapter` (`aspace_a0_plugins_adapter` 0.1.0), commit `fa8df85` sur le fork. **Seul code A'Space du fork** (H-M6) — l'amont est byte-identique au gel (diff gel→adapter = 3 fichiers adapter seuls, +368 insertions, 0 modification amont — vérifié par `git diff` et à l'API).
- **Surface :** `validate()` → dict (gel, licence, comptage de l'index, cohérence `generated/` vs `plugins/`, intégrité des `index.yaml`, cohérence avec le tri agent-zero, 0 appel réseau) ; `doctor()` → liste de 8 contrôles ; `describe()` → manifeste machine ; constantes épinglées (`PINNED_UPSTREAM_COMMIT = d040c3f`, `BIND_COMMIT = f73f767`, `FIBER_ADDRESS`).
- **Bind re-appliqué sur `main` :** commit `f436cdf` au-dessus de l'adapter (F8 D2) — `aspace-plugin.json` VERBATIM du bind `f73f767` (diff vide, vérifié). **Le pin = le commit adapter `fa8df85`.**
- **Smoke tests :** 7 passed in 0.17s (`aspace-a0-plugins-adapter/tests/test_smoke.py`, 7 tests).

## Tests au gel et sur le fork adapté

- **Au gel `d040c3f` (baseline) : suite amont verte** — `python scripts/test_index_release.py` : « Verified complete index: 230 plugins / Index publication and recovery checks passed. » (venv du pas, qui fournit le `python` attendu par la CI ; avec le `python3` système seul, le test échoue sur `python: command not found` dans le pas `check_rebuild` — écart d'environnement, pas du code : la CI amont fournit `python`).
- **Sur le fork adapté (`fa8df85`) : identique** — même sortie, 230 plugins.
- Aucune suite inventée. Commande suite : `python scripts/test_index_release.py` (venv `~/workspace/.venvs-dn053/pas-b`, pyyaml + pytest).
- a0-plugins est l'index communautaire des plugins Agent Zero : `index.yaml` pointe vers le dépôt du plugin ; aucun code de plugin monté dans le fork.

## Index mesuré (au gel, au fichier)

- 235 dossiers dans `plugins/`, 232 noms résolus (`^[a-z0-9_]+$`, hors réserve), 230 indexés (moins `codex_provider` et `discord`, bloqués par `blocked.md`) — le chiffre 230 est celui de la suite amont elle-même.
- 233 `index.yaml` présents, tous des mappings YAML valides, tous avec title + description + github ; max 5 screenshots (règle amont respectée).
- 2 dossiers en `plugin.yaml` seul (`a0-llmfallback`, `agent0-terminal`) : format historique amont, constatés, non modifiés.
- 87 thumbnails générées, dont 2 orphelines constatées (`chat_organizer`, `d2_audio` : plugins retirés, thumbnails restées) ; 155 thumbnails locales ; 0 plugin sans thumbnail.
- **H-B6 :** 0 des 3 abandonnés (`_plugin_installer`, `_plugin_scan`, `_plugin_validator`) et 0 des 9 surfaces agent-zero dans l'index — cohérent avec le tri des 47 plugins (H-P5-7).

## Télémétrie

**Zéro par contrat.** Voir `a0-plugins-TELEMETRY-AUDIT.md` : scan statique (0 SDK télémétrie ; seuls appels réseau = scripts CI explicites vers `api.github.com` et un vers OpenRouter pour les thumbnails, jamais à l'import) + adapter stdlib seule + `validate()` et `doctor()` réussis dans un namespace réseau sans interface (0 appel sortant possible).

## Confinement

Aucun confinement commercial : code et index MIT. Usage B2B autorisé par la licence.

## Divergence (dette portée par le cœur Buzz)

Surface d'API épinglée : l'adapter ne dépend d'aucune API amont instable — il ne fait que constater (comptage, cohérence, intégrité). Toute dérive amont est un événement de design (revisite par signal, jamais de fast-forward silencieux). Le gel est le HEAD amont au 2026-11-11 (dérive 0 vérifiée à l'API le jour même). Faits amont constatés, non corrigés par l'adapter : 2 thumbnails orphelines, 2 dossiers en `plugin.yaml` historique.

## Références

- Design D-N053 (Clara, 2026-11-10) : `~/workspace/v4-factory/plans/ADAPTATION-TOUS-MODULES-RUNTIME-plan-borne.md` (D1–D16, H-M1..M7, H-A1..H-A8).
- Design signé pas B (2026-11-11) : `~/workspace/v4-factory/plans/DESIGN-D-N053-PAS-B-PROJET.md` (D-B0..D-B3).
- Discover pas B : `~/workspace/v4-factory/evidence/D-N053/b/DISCOVER-PAS-B.md`.
- Évidences : `~/workspace/v4-factory/evidence/D-N053/b/a0-plugins/` (fiche + manifeste + audit, logs suite / smoke / netns, rapport).
- Fork : https://github.com/Amdkn/a0-plugins (gel `d040c3f`, adapter `fa8df85`, bind re-appliqué `f436cdf`).
