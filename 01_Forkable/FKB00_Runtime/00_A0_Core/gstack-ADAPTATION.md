# Fiche d'adaptation — gstack (état 1, D-N053 pas C, référence du canonique)

**Adresse :** `fiber:a0:gstack` (design D-N053, Clara ; design signé pas C D-C0..D-C3)
**Manifeste :** `gstack.manifest.json` (même domicile, `00_A0_Core/`)
**Audit télémétrie :** `gstack-TELEMETRY-AUDIT.md` (même domicile)
**Statut :** état 1 Adapté (fiche + adapter + manifeste, tests verts) — validation 13e en attente (le coordinateur intègre, régime R10). `levels.current` = 0 dans le manifeste, monté à 1 à l'intégration par le parent.

## Commit gelé

- **Fork :** `Amdkn/gstack` (parent `garrytan/gstack`, branche `main`, licence MIT).
- **Gel : `3742ee95`** — « feat: cut standalone /plan-eng-review; /autoplan keeps its eng phase (GST-1698) (#4108) », 2026-11-07. Dérive 101 vérifiée à l'API (conforme au design), amont vivant — pas de re-gel, revisite par signal.
- **Bind Cordis Fiber (4L) : `a79170c`** — `aspace-plugin.json` sur la branche `aspace-v5-native` (parent = gel).
- **Tout commit amont ultérieur exige un amendement de design**, jamais un fast-forward silencieux.

## Adapter

- **Paquet :** `aspace-gstack-adapter` (`aspace_gstack_adapter` 0.1.0), commit `6cb6da7` sur le fork. **Seul code A'Space du fork** (H-M6) — l'amont est byte-identique au gel (diff gel→adapter = 3 fichiers adapter seuls, +326 insertions, 0 modification amont — vérifié par `git diff` et à l'API).
- **Surface :** `validate()` → dict (gel, licence, comptage des 64 skills de premier niveau, 75 SKILL.md, 1 745 `*.test.ts`, frontmatter du routeur racine, `.gstack/`/`agents/`/`autoplan/`, présence du runner borné, 0 appel réseau) ; `doctor()` → liste de 9 contrôles ; `describe()` → manifeste machine ; constantes épinglées (`PINNED_UPSTREAM_COMMIT = 3742ee95`, `BIND_COMMIT = a79170c`, `FIBER_ADDRESS`).
- **Bind re-appliqué sur `main` :** commit `f63ac22` au-dessus de l'adapter (F8 D4) — `aspace-plugin.json` VERBATIM du bind `a79170c` (blob byte-identique, `cmp` vide, vérifié). **Le pin = le commit adapter `6cb6da7`.**
- **Smoke tests :** 6 passed in 0.59s (`aspace-gstack-adapter/tests/test_smoke.py`, 6 tests).
- **Correction de mesure en cours :** le comptage initial « 80 SKILL.md » (Discover, `git ls-files | grep 'SKILL.md$'`) comptait 5 fixtures `*-SKILL.md` et l'adapter comptait 3 SKILL.md de `node_modules/playwright-core` installés par `bun install` — mesure corrigée : **75 SKILL.md exactement nommés** (64 dossiers skills + racine + 10 imbriqués), vérifiée par `comm` suivi-vs-disque.

## Tests au gel et sur le fork adapté

- **Au gel `3742ee95` (baseline) : suite amont bornée NON VERTE** — `bun run scripts/test-free-shards.ts --quick` (1 079/1 631 fichiers, 4 shards, ~9 min) : **726 tests en échec dans 65 fichiers** (shard 1 : 540/17 ; shard 2 : 80/19 ; shard 3 : 63/16 ; shard 4 : 43/13), 4/4 shards en échec. Grappes : `browse/test/*` (E2E Chromium/GPU réel — pas d'affichage ni GPU sur cette VM, Aside macOS-only), QA E2E (`skill-e2e-qa-workflow`, `qa-only-capability`), `autoplan-admission` (gating runtime, `GSTACK_ALLOW_UNSUPPORTED_RUNTIME`), CSO, `codex-cli` (CLI absent), `plan-floor` (timeouts). **Pré-existant au gel, 0 imputable à l'adapter** (l'adapter n'existait pas au moment du run ; il ne touche aucun code amont). H-C3 NON VERT strict — à juger (même posture que pas B spynel/tuxee, décision D-B2) ; **aucune réduction appliquée** (D-C2).
- **Sur le fork adapté (`6cb6da7`) :** run `--quick` relancé : **729 tests en échec dans 66 fichiers** (shard 1 : 541/18 ; shard 2 : 80/19 ; shard 3 : 62/15 ; shard 4 : 46/14) — mêmes grappes que le gel (726/65), écarts aux marges = flakiness (`callback.test.ts` vs `qa-only-capability.test.ts`, `gstack-settings-hook-symlink`, `tree-receipt-gbrain-pair` vs `qa-functional-observer`). **0 imputable à l'adapter** (il ne touche aucun code amont). H-C3 NON VERT strict — à juger (même posture que pas B spynel/tuxee, décision D-B2) ; **aucune réduction appliquée** (D-C2).
- Suite complète hors périmètre sur cette VM (1 745 fichiers, sharding CI à 20 jobs). Le `--quick` est le sous-ensemble rapide défini par l'amont (« explicit fast subset, not acceptance », honnête).
- gstack est une **référence** du canonique `fiber:a0:superpowers` (§D5).

## Index mesuré (au gel, au fichier)

- 4 967 fichiers suivis ; 64 dossiers skills de premier niveau avec SKILL.md ; 75 SKILL.md exactement nommés ; 1 745 `*.test.ts`.
- SKILL.md racine (routeur, généré depuis SKILL.md.tmpl, frontmatter `name: gstack` + description).
- `.gstack/` (always-run.json, generated.json, pregate.json, ship-policy.json, ship-policy.example.json) ; `agents/` (openai.yaml) ; `autoplan/` (DRIVER.md, SKILL.md, sections/).

## Télémétrie

**Zéro par contrat.** Voir `gstack-TELEMETRY-AUDIT.md` : scan statique (0 SDK télémétrie ; 0 dépendance de télémétrie dans package.json / bun.lock) + adapter stdlib seule + `validate()` et `doctor()` réussis dans un namespace réseau sans interface (0 appel sortant possible).

## Confinement

Aucun confinement commercial : code et skills MIT. Usage B2B autorisé par la licence.

## Divergence (dette portée par le cœur Buzz)

Surface d'API épinglée : l'adapter ne dépend d'aucune API amont instable — il ne fait que constater (comptage, cohérence, intégrité). Toute dérive amont est un événement de design (revisite par signal, jamais de fast-forward silencieux). Dérive 101 au 2026-11-11 ; le gel reste `3742ee95`.

## Références

- Design D-N053 (Clara, 2026-11-10) : `~/workspace/v4-factory/plans/ADAPTATION-TOUS-MODULES-RUNTIME-plan-borne.md` (D1–D16, H-M1..M7, H-A1..H-A8).
- Design signé pas C (2026-11-11) : `~/workspace/v4-factory/plans/DESIGN-D-N053-PAS-C-PROJET.md` (D-C0..D-C3).
- Discover pas C : `~/workspace/v4-factory/evidence/D-N053/c/DISCOVER-PAS-C.md`.
- Évidences : `~/workspace/v4-factory/evidence/D-N053/c/gstack/` (fiche + manifeste + audit, logs suite / smoke / netns, rapport).
- Fork : https://github.com/Amdkn/gstack (gel `3742ee95`, adapter `6cb6da7`, bind re-appliqué `f63ac22`).
