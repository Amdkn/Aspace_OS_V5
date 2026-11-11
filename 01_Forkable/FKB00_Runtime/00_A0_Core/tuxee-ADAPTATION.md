# Fiche d'adaptation — tuxee (état 1, D-N053 pas B)

**Adresse :** `fiber:a0:tuxee` (design D-N053, Clara ; design signé pas B D-B0..D-B3)
**Manifeste :** `tuxee.manifest.json` (même domicile, `00_A0_Core/`)
**Audit télémétrie :** `tuxee-TELEMETRY-AUDIT.md` (même domicile)
**Statut :** état 1 Adapté (fiche + adapter + manifeste, tests verts) — validation 13e en attente (le coordinateur intègre, régime R10). `levels.current` = 0 dans le manifeste, monté à 1 à l'intégration par le parent.

## Commit gelé

- **Fork :** `Amdkn/tuxee` (parent `agent0ai/tuxee`, branche `main`, licence MIT — fichier ; l'API dit `NOASSERTION`, le fichier fait foi).
- **Gel : `a7e2061`** — « Keep shortcut terminals open after commands finish », 2026-11-05. Amont vivant, dérive 2 (HEAD amont `590ec97`, 2026-11-09) — gel tenu, revisite par signal, jamais de fast-forward silencieux.
- **Bind Cordis Fiber (2L) : `5c51b78`** — `aspace-plugin.json` sur la branche `aspace-v5-native` (parent = gel).
- **Tout commit amont ultérieur exige un amendement de design**, jamais un fast-forward silencieux.

## Adapter

- **Paquet :** `aspace-tuxee-adapter` (`aspace_tuxee_adapter` 0.1.0), commit `5cad42a` sur le fork. **Seul code A'Space du fork** (H-M6) — l'amont est byte-identique au gel, à une exception nommée ci-dessous (H-M2 QUALIFIÉ).
- **Surface :** `validate()` → dict (gel, licence, module Go, interface mesurée au fichier, zéro appel réseau) ; `doctor()` → liste de 7 contrôles ; `describe()` → manifeste machine ; constantes épinglées (`PINNED_UPSTREAM_COMMIT = a7e2061`, `BIND_COMMIT = 5c51b78`, `FIBER_ADDRESS`, pile provisionnée `fiber:a0:agent-zero` + `fiber:a0:spynel` + `fiber:a0:a0-plugins`).
- **Bind re-appliqué sur `main` :** commit `0b3e473` au-dessus de l'adapter (F8 D2) — `aspace-plugin.json` VERBATIM du bind `5c51b78` (diff vide, vérifié). **Le pin = le commit adapter `5cad42a`.**
- **Smoke tests :** 6 passed in 0.11s (`aspace-tuxee-adapter/tests/test_smoke.py`, 6 tests).

## Exception H-M2 (nommée, DOX — à juger par le 13e)

Le diff gel→adapter compte **7 fichiers** : 6 fichiers adapter + **1 ligne ajoutée à la racine `AGENTS.md`** (Child DOX Index : lien vers `aspace-tuxee-adapter/AGENTS.md`). Le contrat DOX du repo exige un `AGENTS.md` par répertoire et son indexation par le parent — sans cette ligne, la porte DOX échoue sur le fork adapté. La ligne ne change aucune règle, aucun code, aucun contenu amont. Les 3 `AGENTS.md` de l'adapter (racine + paquet + tests) font partie du périmètre adapter. **H-M2 est donc QUALIFIÉ, pas vert strict** — la décision appartient au 13e. (Même patron que spynel, même justification.)

## Tests au gel et sur le fork adapté

- **Prérequis de suite (environnement, pas de réduction) :** `web/dist`, `internal/terminal/engine.js`, `internal/keeper/keeper.bin` sont générés et ignorés par Git — construits avant la suite per DOX (`npm run build`, `make -C internal/keeper/native` avec `musl-gcc` installé pour le pas, `libpam0g-dev` installé pour les en-têtes PAM, Go 1.27.4). Environnement de suite : `USER=root`, `TMPDIR=/tmp` (le chown échoue sur /home dans ce bac à sable, il passe sur /tmp), `LANG=C.UTF-8` (le test de prompts échoue en locale POSIX), `umask 022`.
- **Au gel `a7e2061` (baseline, environnement corrigé) : 14 ok, 2 FAIL** — `go test ./...` :
  - `internal/processes` : `TestMemorySharing` — « shared memory duplicated or omitted: 75029504 » (comptabilité PSS du conteneur).
  - `internal/server` : `TestAnonymousReleaseIndependence` — « anonymous release contract changed » (testdata `login-surface.json` générée à `cf89daf`, `web/` modifiée par 10+ commits ensuite dont `a0015aa` et `de10445` — baseline non régénérée par l'amont ; vérifié : le build Node 22 = CI donne le même échec que Node 24, l'hypothèse Node est réfutée).
- **Sur le fork adapté (`5cad42a`) : 14 ok, 2 FAIL — IDENTIQUES** (mêmes tests, mêmes messages : `TestMemorySharing` 75061248, `TestAnonymousReleaseIndependence`).
- **Lecture :** les 2 échecs sont pré-existants au gel et identiques sur l'adapté — l'adapter (fichiers Python + 1 ligne de doc) ne touche aucun code Go amont et ne peut pas les causer. **H-B3 n'est pas vert strict — décision du coordinateur attendue (D-B2) : la liste exacte des tests proposés à l'exclusion est dans le rapport.**
- Commande suite : `go test ./...` (Go 1.27.4, `GOTMPDIR`/`TMPDIR=/tmp`, `USER=root`, `LANG=C.UTF-8`).
- Tuxee — the most convenient Linux for servers and agents.

## Télémétrie

**Zéro par contrat.** Voir `tuxee-TELEMETRY-AUDIT.md` : scan statique (0 SDK télémétrie ; 0 hit `telemetry`/`analytics` en Go et en JS hors vendor — les seuls matchs JS sont des fragments de mots ; seuls sites réseau = serveur lui-même, mise à jour GitHub explicite, ACME Let's Encrypt, téléchargements initiés par l'utilisateur, install.sh) + adapter stdlib Python seule + `validate()` et `doctor()` réussis dans un namespace réseau sans interface (0 appel sortant possible).

## Confinement

Aucun confinement commercial : code MIT. Usage B2B autorisé par la licence. L'installation télécharge la release GitHub officielle (checksum sha256 vérifié) ; les secrets (`ROOT_PASSWORD`) sont fournis par l'opérateur, jamais lus ni stockés ici.

## Divergence (dette portée par le cœur Buzz)

Surface d'API épinglée : l'adapter ne dépend d'aucune API amont instable — il ne fait que constater (install, compose, Dockerfile, cmd/tuxee, docker/). Toute dérive amont est un événement de design (revisite par signal, jamais de fast-forward silencieux). Dérive au gel : 2 commits (amont vivant).

## Références

- Design D-N053 (Clara, 2026-11-10) : `~/workspace/v4-factory/plans/ADAPTATION-TOUS-MODULES-RUNTIME-plan-borne.md` (D1–D16, H-M1..M7, H-A1..H-A8).
- Design signé pas B (2026-11-11) : `~/workspace/v4-factory/plans/DESIGN-D-N053-PAS-B-PROJET.md` (D-B0..D-B3).
- Discover pas B : `~/workspace/v4-factory/evidence/D-N053/b/DISCOVER-PAS-B.md`.
- Évidences : `~/workspace/v4-factory/evidence/D-N053/b/tuxee/` (fiche + manifeste + audit, logs suite gel/adapté, smoke, netns, rapport).
- Fork : https://github.com/Amdkn/tuxee (gel `a7e2061`, adapter `5cad42a`, bind re-appliqué `0b3e473`).
