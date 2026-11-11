# Audit télémétrie — caveman (D-N048, V1, FKB04)

**Module :** `Amdkn/caveman` (fork de `JuliusBrussee/caveman`), gel `3dc497a`, Apache-2.0.
**Date :** 2026-11-09. **Auditeur :** Ryan (Factory). **Régime :** R10.

## 1. Scan statique (code Go, hors tests)

- **Canal cloud identifié** : `proxy/internal/cloudlink/link.go` — `settings`
  (`cloud` = URL de base de l'API de contrôle, `gateway` = où vit
  `/v1/route`, `key`/`access` = identifiants de login appareil).
  Le canal n'est actif qu'après login (`signedIn()` exige `cloud != ""`
  ET (`key != ""` OU `access != ""`)). **L'adapter ne se logue jamais.**
- **Interrupteurs d'envoi** (`link.go:359, 437`) :
  - `CAVEMAN_OFFLINE=1` : « benchmark and air-gapped runs send nothing ».
  - `telemetry.enabled=false` (config), `DO_NOT_TRACK` (toute valeur
    non vide sauf `0`/`false`), `CAVEMAN_TELEMETRY=0` : « no runtime events ».
  - `events.go:27` : les événements ne sont jamais [émis] une fois
    l'opt-out posé.
- **WebSocket local** : `browse/cmd/caveman-browse/main.go` — `ws://` vers
  le débogueur Chrome **local** (pas un appel sortant).
- **Dépendances réseau** (`go.mod`) : `chromedp` (automatisation navigateur
  local), `pgx/v5` (client Postgres — jamais instancié par l'engine),
  `gobwas/httphead` (indirect). Aucun SDK télémétrie déclaré.
- **Binaire engine** (`engine/cmd/caveman-engine`) : opérations locales
  (compress/detect/stats/registry/toon/pixel/evals), estimations de tokens
  locales, store de reprise CCR sous `~/.caveman/`. Aucun appel réseau
  dans le chemin `compress`.

## 2. Dépendances déclarées

Aucun SDK télémétrie (PostHog, Segment, Sentry, analytics) dans `go.mod`.
Le seul canal sortant potentiel est le `cloudlink` du proxy, désactivé
par contrat (voir §1).

## 3. Preuve réseau (capture en namespace sans interface)

**Exécutée 2026-11-09, `unshare -n` (aucune interface réseau) :**
- `caveman-engine version --json` → `{"schema": "caveman.engine.version.v1",
  "capabilities": ["compress", "detect", "retrieve", "stats", "registry",
  "toon", "pixel", "evals"]}`, exit 0.
- `caveman-engine compress` sur échantillon verbeux (668 o) → exit 0,
  sortie 627 o, rapport JSON `tokens_before: 126, tokens_after: 119`.
- Env : `CAVEMAN_OFFLINE=1`, `DO_NOT_TRACK=1`, `CAVEMAN_TELEMETRY=0`,
  `HOME` scratch. **Zéro appel sortant possible** (aucune interface
  dans le namespace) — les deux commandes réussissent sans réseau.

## 4. Verdict

**Télémétrie zéro par contrat** : l'adapter (`aspace-caveman-adapter`)
n'exécute que le binaire engine local, avec les trois interrupteurs
posés et sans login. Aucun identifiant, aucun crédit dépensé.
