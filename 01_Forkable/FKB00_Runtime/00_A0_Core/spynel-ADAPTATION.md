# Fiche d'adaptation — spynel (état 1, D-N053 pas B)

**Adresse :** `fiber:a0:spynel` (design D-N053, Clara ; design signé pas B D-B0..D-B3)
**Manifeste :** `spynel.manifest.json` (même domicile, `00_A0_Core/`)
**Audit télémétrie :** `spynel-TELEMETRY-AUDIT.md` (même domicile)
**Statut :** état 1 Adapté (fiche + adapter + manifeste, tests verts) — validation 13e en attente (le coordinateur intègre, régime R10). `levels.current` = 0 dans le manifeste, monté à 1 à l'intégration par le parent.

## Commit gelé

- **Fork :** `Amdkn/spynel` (parent `agent0ai/spynel`, branche `main`, licence MIT).
- **Gel : `685ac65`** — « Support /models through the shared model selection path », 2026-11-04T05:59:01Z. HEAD amont au 2026-11-11 (dérive 0, vérifiée à l'API le jour même).
- **Bind Cordis Fiber (2L) : `3e076a1`** — `aspace-plugin.json` sur la branche `aspace-v5-native` (parent = gel).
- **Tout commit amont ultérieur exige un amendement de design**, jamais un fast-forward silencieux.

## Adapter

- **Paquet :** `aspace-spynel-adapter` (`aspace_spynel_adapter` 0.1.0), commit `fa9fe41` sur le fork. **Seul code A'Space du fork** (H-M6) — l'amont est byte-identique au gel, à une exception nommée ci-dessous (H-M2 QUALIFIÉ).
- **Surface :** `validate()` → dict (gel, licence, module Go, surface d'orchestration mesurée au fichier, zéro appel réseau) ; `doctor()` → liste de 7 contrôles ; `describe()` → manifeste machine ; constantes épinglées (`PINNED_UPSTREAM_COMMIT = 685ac65`, `BIND_COMMIT = 3e076a1`, `FIBER_ADDRESS`, cible `fiber:a0:agent-zero`).
- **Bind re-appliqué sur `main` :** commit `630ac6d` au-dessus de l'adapter (F8 D2) — `aspace-plugin.json` VERBATIM du bind `3e076a1` (diff vide, vérifié). **Le pin = le commit adapter `fa9fe41`.**
- **Smoke tests :** 5 passed in 0.12s (`aspace-spynel-adapter/tests/test_smoke.py`, 5 tests).

## Exception H-M2 (nommée, DOX — à juger par le 13e)

Le diff gel→adapter compte **7 fichiers** : 6 fichiers adapter + **1 ligne ajoutée à la racine `AGENTS.md`** (Child DOX Index : lien vers `aspace-spynel-adapter/AGENTS.md`). Le contrat DOX du repo est sans exception : chaque répertoire suivi possède son `AGENTS.md`, indexé par son parent — sans cette ligne, `scripts/dev.sh dox` échoue sur le fork adapté. L'alternative (laisser la porte DOX rouge) est pire qu'une ligne d'index. La ligne ne change aucune règle, aucun code, aucun contenu amont. Porte DOX vérifiée verte sur l'adapté : « DOX coverage valid for 50 tracked directories ». Les 3 `AGENTS.md` de l'adapter (racine + paquet + tests) font partie du périmètre adapter. **H-M2 est donc QUALIFIÉ, pas vert strict** — la décision appartient au 13e.

Note : un premier commit `5cefe40` avait inclus 2 `.pyc` par erreur (pytest) ; amendé avant push en `fa9fe41` (7 fichiers, 0 binaire).

## Tests au gel et sur le fork adapté

- **Au gel `685ac65` (baseline) : 25 ok, 3 FAIL** — `go test ./...` (Go 1.27.4 installé pour le pas ; `GOTMPDIR` sur /home car /tmp tmpfs 512 Mo saturé par les binaires de test — 450 Mo, échec de link constaté puis contourné par l'environnement, pas par la suite).
  - `internal/app` : `TestNotificationContextFailsClosedForRevokedMissingAndUnreadableOrigins` — « real history read error was suppressed » (0,69 s).
  - `internal/channel/tui` : `TestBlockedAndCPUHeavyMarkdownRenderKeepsContinuousInteractiveWorkResponsive/cpu-heavy` — 117,86 ms contre une cible < 100 ms (VM partagée 1,5 CPU).
  - `internal/harness` : `TestWorkerLaunchSurvivesActualControllerExit` (graceful + abrupt) — « could not catch up with retained worker progress ».
- **Sur le fork adapté (`fa9fe41`) : 25 ok, 3 FAIL — NON identiques :**
  - `internal/app` : **même test, même message** (stable, pré-existant au gel).
  - `internal/channel/telegram` : `TestWebhookModeVerifiesSecretAndRoutesUpdate` — « webhook bot did not stop » (nouveau).
  - `internal/harness` : `TestWorkerConcurrentLaunchAndConfirmedDeadReplacement` — « worker record changed while opening » (nouveau, autre test du même paquet).
  - `internal/channel/tui` : **vert sur l'adapté** (l'échec baseline a disparu).
- **Lecture :** les 3 échecs par run sont des tests de timing/coordination sensibles à la charge (VM partagée 1,5 CPU) — l'ensemble des échecs varie d'un run à l'autre, sauf le test `internal/app` (stable, pré-existant). L'adapter ne touche aucun code Go amont (fichiers Python + 1 ligne de doc) et ne peut pas causer ces échecs ; la porte DOX est verte. **H-B3 n'est pas vert strict — décision du coordinateur attendue (D-B2) : la liste exacte des tests proposés à l'exclusion est dans le rapport.**
- Commande suite : `go test ./...` (Go 1.27.4, `GOTMPDIR`/`TMPDIR` sur /home).
- Spynel is a classic, non-AI program that coordinates and oversees external AI/coding harnesses. "Simplicity at scale."

## Télémétrie

**Zéro par contrat.** Voir `spynel-TELEMETRY-AUDIT.md` : scan statique (0 SDK télémétrie, mot `telemetry` absent du code Go hors tests ; seuls sites réseau = canaux Telegram/WhatsApp activés par l'utilisateur, téléchargement du modèle de parole Parakeet, vérification de mise à jour interactive GitHub/npm, API locale socket Unix/loopback) + adapter stdlib Python seule + `validate()` et `doctor()` réussis dans un namespace réseau sans interface (0 appel sortant possible).

## Confinement

Aucun confinement commercial : code MIT. Usage B2B autorisé par la licence. Les canaux telegram/whatsapp exigent des secrets fournis par l'utilisateur (jamais lus ni stockés ici).

## Divergence (dette portée par le cœur Buzz)

Surface d'API épinglée : l'adapter ne dépend d'aucune API amont instable — il ne fait que constater (entrée, workers, orchestrateur, jobs, canaux, API locale). Toute dérive amont est un événement de design (revisite par signal, jamais de fast-forward silencieux). Le gel est le HEAD amont au 2026-11-11 (dérive 0 vérifiée à l'API le jour même). Correction de mesure : le Discover disait « 202 fichiers de test internal/ » — mesuré : 202 au total (188 `internal/`, 3 `scripts/`, 11 `third_party/bubbletea`).

## Références

- Design D-N053 (Clara, 2026-11-10) : `~/workspace/v4-factory/plans/ADAPTATION-TOUS-MODULES-RUNTIME-plan-borne.md` (D1–D16, H-M1..M7, H-A1..H-A8).
- Design signé pas B (2026-11-11) : `~/workspace/v4-factory/plans/DESIGN-D-N053-PAS-B-PROJET.md` (D-B0..D-B3).
- Discover pas B : `~/workspace/v4-factory/evidence/D-N053/b/DISCOVER-PAS-B.md`.
- Évidences : `~/workspace/v4-factory/evidence/D-N053/b/spynel/` (fiche + manifeste + audit, logs suite gel/adapté, smoke, netns, rapport).
- Fork : https://github.com/Amdkn/spynel (gel `685ac65`, adapter `fa9fe41`, bind re-appliqué `630ac6d`).
