# Fiche d'adaptation — caveman (V1, FKB04)

**Adresse :** `fiber:a0:caveman` (D7 — émetteur : exécution ; validateur : 13e)
**Manifeste :** `caveman.manifest.json` (même domicile)
**Audit télémétrie :** `caveman-TELEMETRY-AUDIT.md` (même domicile)
**Statut :** état 0 Basique → 1 Adapté (fiche + adapter + manifeste, tests verts)

## Commit gelé

- **Fork :** `Amdkn/caveman` (parent `JuliusBrussee/caveman`, Apache-2.0, branche `main`).
- **Gel : `3dc497a`** (2026-11-09, HEAD de `main` au Discover).
- **Tout commit amont ultérieur exige un amendement de design**, jamais un fast-forward silencieux (D5).

## Adapter

- **Paquet :** `aspace-caveman-adapter` 0.1.0, commit `2f68929` sur le fork. **Seul code A'Space du fork** (H-M6) — le code amont est byte-identique au gel (diff gel→adapter = 3 fichiers, tous sous `aspace-caveman-adapter/`).
- **Couture : contrat seule (§1.5).** Caveman est en Go — hors des trois coutures Cordis. Aucune couture spécifique au Go n'est construite : l'adapter est le contrat CLI du binaire local `caveman-engine` (`contract.json`) + un smoke test Go.
- **Surface :** `version --json` (schéma `caveman.engine.version.v1`, capacités `compress, detect, retrieve, stats, registry, toon, pixel, evals`) ; `compress [--type <content-type>]` (stdin → stdout, rapport JSON sur stderr) ; `detect`, `stats`, `registry`, `toon encode|decode`. Sous-commande inconnue → exit 2.
- **Smoke tests :** 3/3 verts (`smoke_test.go` : version JSON, compress hors ligne sur échantillon verbeux — 126 → 119 tokens —, sous-commande inconnue → 2).

## Tests au gel et sur le fork adapté

- **Au gel `3dc497a` :** suite canonique `go test ./engine/... ./proxy/... ./shared/...` (CI `ci.yml:197`). **51 paquets ok, 2 paquets en échec, 2 tests nommés** (run complet, rc=1, 217 s) :
  - `TestFreshStoreSocketAnswersDecisionWellWithinBudget` (`proxy/internal/nativeruntime`) : 78 ms pour un budget de 250 ms — **passe isolément (0,288 s)** : échec de timing sous contention (suite Go + voie rapide claude-mem en parallèle sur 1,5 CPU partagé). Environnemental, pré-existant.
  - `TestNewHTTPClient_ProxyDirectFallbackKeepsGuardAndRefusesProxyAddress` (`shared/platform/ssrf`) : `http://direct.invalid/` retourne « malformed HTTP status code "Other" » — **prouvé environnemental** : le DNS du sandbox résout `.invalid` vers un middlebox (`198.18.112.27`, réponse vide au curl) ; le test attend l'échec DNS de CI. Échoue isolément, avec et sans variables proxy. Pré-existant.
  - Premier run : échecs massifs du store CCR (`sqlite parent ... is group/world writable`) + échecs de link (`no space left on device` sur `/tmp`, tmpfs 512 Mo). **Causes prouvées environnementales :** (1) le `umask 0007` du shell rend les répertoires temporaires inscriptibles par le groupe, et le store CCR refuse les parents inscriptibles par le groupe/le monde (mécanisme prouvé : `umask 0022` → répertoires 0755) ; (2) `/tmp` saturé à 94 % (410 Mo de `go-build*` + tarball Go 64 Mo).
  - **Correctifs d'environnement (aucun changement de code ni de test) :** `TMPDIR` sur le grand disque (`~/workspace/.tmp`, 150 Go), `umask 0022`, `/tmp` nettoyé. Les 2 échecs restants sont qualifiés ci-dessus, pas des correctifs.
  - Comptage par test (re-run verbeux, sans contention) : **2 366 pass, 1 fail, 13 skip** (52 paquets ok, 1 paquet en échec). **Le seul échec restant est le SSRF** (DNS sandbox, voir ci-dessus) ; le test de timing passe isolément et en re-run propre.
- **Sur le fork adapté (`2f68929`) :** l'adapter ajoute 3 tests verts (smoke test, `go test ./aspace-caveman-adapter/` : ok).
- **Limite franche :** Go 1.26.10 n'était pas installé sur la VM — installé dans `~/workspace/go` (téléchargement go.dev, 67 Mo) pour faire tourner la suite.

## Télémétrie

**Zéro par contrat.** Voir `caveman-TELEMETRY-AUDIT.md` : canal cloud (`proxy/internal/cloudlink`) inactif sans login ; interrupteurs `CAVEMAN_OFFLINE=1` + `DO_NOT_TRACK=1` + `CAVEMAN_TELEMETRY=0` ; preuve réseau en namespace sans interface (`version --json` + `compress` réussissent sans réseau).

## Dette de divergence

- **Aucune divergence :** le code amont est byte-identique au gel ; seul `aspace-caveman-adapter` diffère.
- **Propriétaire :** cœur Buzz (lane Clara / 12e).
- **Contrainte nommée (§2) :** Go — hors coutures Cordis (contrat seul, §1.5).
