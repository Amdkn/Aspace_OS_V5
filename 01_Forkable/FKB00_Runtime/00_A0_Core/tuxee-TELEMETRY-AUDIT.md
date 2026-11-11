# Audit télémétrie — tuxee (D-N053 pas B, H-M4)

**Module :** `tuxee` — fork `Amdkn/tuxee`, gel `a7e2061`, adapter (à consigner après push).
**Verdict : TÉLÉMÉTRIE ZÉRO par contrat.** Aucun SDK de télémétrie, aucun appel réseau en arrière-plan, aucun appel à l'import. Les seuls appels sortants sont le serveur lui-même (il écoute, il n'appelle pas), la vérification de mise à jour explicite (GitHub) et l'ACME (Let's Encrypt, certificats publics).

## 1. Scan statique du code amont (au gel)

Motifs cherchés dans `cmd/` + `internal/` + `experiments/` (hors `*_test.go`) : `posthog|amplitude|segment.io|sentry|datadog|newrelic|telemetry|analytics` → **0 hit**.
Motifs cherchés dans `web/` (hors `vendor/`) : `posthog|amplitude|sentry|google-analytics|googletagmanager` → **0 hit réel** (les seuls matchs sont des fragments de mots : `segments` dans `web/model.ts`, `usedAsEntry...` dans `web/app.ts`, `getAsFile` dans `web/file-drag.ts`).
Motifs réseau cherchés : `net/http|http.Get|http.Post` → sites ci-dessous uniquement.

### Sites réseau explicites (tous déclenchés par l'utilisateur ou la configuration, jamais en arrière-plan)

- `internal/server/` — le serveur HTTP/HTTPS lui-même (écoute sur 80/443, websockets pour les terminaux) : il sert, il n'appelle personne.
- `internal/update/release.go:46` — `api.github.com/repos/agent0ai/tuxee/releases/latest` (+ téléchargement de la release, checksum vérifié) : vérification de mise à jour explicite (`tuxee update`, action About, vérification au démarrage et quotidienne à 00:01) — jamais silencieuse au sens télémétrique (c'est la fonction de mise à jour du produit).
- `internal/tlsmanager/acme.go` — ACME (Let's Encrypt) : émission/renouvellement de certificats publics pour les domaines découverts par SNI ; certificats locaux sinon.
- `internal/server/download.go` — téléchargements initiés par l'utilisateur (fichiers, via le navigateur).
- `install.sh` — `github.com/agent0ai/tuxee/releases/download/...` (release + `checksums.txt`, sha256 vérifié) : installation explicite par l'opérateur, jamais automatique.

## 2. Dépendances

Dépendances Go (`go.mod`) : coder/websocket, creack/pty, dop251/goja, go-acme/lego, xgb, x/mod. Dépendances frontend (`package.json`) : dépendances locales embarquées. Aucun SDK de télémétrie déclaré (grep `posthog|amplitude|segment|sentry|datadog|newrelic|telemetry` dans `go.mod`/`go.sum`/`package.json` : 0 hit). L'adapter est **stdlib Python seule** (0 import réseau, vérifié par AST dans le smoke).

## 3. Preuve d'exécution — namespace sans interface

`unshare -n` (aucune interface réseau, DNS en échec) : `validate()` + `doctor()` réussissent (interface complète, 7/7 contrôles ok). Log : `logs-netns-validate.log`. **0 appel sortant possible dans ce namespace — la preuve est structurelle, pas déclarative.**

## 4. Poids dans le fork

Aucun poids monté : aucun fichier `.onnx` / `.safetensors` / `.pt` / `.pth` dans le repo (vérifié au fichier). Les modèles audio (PulseAudio) sont construits dans l'étape Docker, jamais dans le fork.

## 5. Déclencheurs tranchés

| Déclencheur | Décision |
|---|---|
| Vérification / téléchargement de mise à jour (GitHub) | Explicite (`tuxee update`, About, démarrage + quotidienne) — **conservé tel quel** (fonction du produit, pas une télémétrie) |
| ACME / Let's Encrypt | Certificats publics, domaines découverts par SNI — **conservé tel quel** |
| Serveur HTTP/HTTPS + websockets | Le serveur sert ; il n'appelle personne — **conservé tel quel** |
| Téléchargements utilisateur | Initiés par l'utilisateur via le navigateur — **conservés tels quels** |
| SDK de télémétrie | Aucun — **rien à retirer** |
| Appel réseau à l'import | Aucun (prouvé en netns pour l'adapter) — **rien à retirer** |
| Poids montés dans le fork | Aucun — **conforme** |

## 6. Ré-audit

À chaque changement de commit gelé ou d'adapter, et au minimum à chaque transition d'état.
