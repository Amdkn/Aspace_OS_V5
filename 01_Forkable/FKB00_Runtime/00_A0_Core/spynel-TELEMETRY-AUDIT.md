# Audit télémétrie — spynel (D-N053 pas B, H-M4)

**Module :** `spynel` — fork `Amdkn/spynel`, gel `685ac65`, adapter (à consigner après push).
**Verdict : TÉLÉMÉTRIE ZÉRO par contrat.** Aucun SDK de télémétrie, aucun appel réseau en arrière-plan, aucun appel à l'import. Le seul signal sortant par défaut est la vérification de mise à jour, autorisée par le lancement interactif uniquement (DOX : lancements headless / non interactifs = aucune vérification proactive).

## 1. Scan statique du code amont (au gel)

Motifs cherchés dans `cmd/` + `internal/` (hors `*_test.go`) : `posthog|amplitude|segment.io|sentry|datadog|newrelic|telemetry` → **0 hit**. Le mot `telemetry` n'apparaît nulle part dans le code Go hors tests.
Motifs réseau cherchés : `http.Get|http.Post|http.NewRequest|websocket.Dial|DialContext|net.Dial` → sites ci-dessous uniquement.

### Sites réseau explicites (tous déclenchés par l'utilisateur ou la configuration, jamais en arrière-plan)

- `internal/channel/telegram/telegram.go:782,885,953` — API Bot Telegram (`getUpdates`, envois) : canal activé par l'utilisateur, token fourni par lui, allow-list vérifiée à chaque événement (fail closed).
- `internal/channel/whatsapp/` — bibliothèque `whatsmeow` (connexion aux serveurs WhatsApp) : canal activé par l'utilisateur, session persistée dans le workspace.
- `internal/media/parakeet_model.go:264` — téléchargement du modèle de parole depuis `github.com/k2-fsa/sherpa-onnx/releases/download/asr-models/` : explicite, parole activée par l'utilisateur, modèle mis en cache per-user (licence NVIDIA Open Model / CC BY 4.0 selon le modèle).
- `internal/updater/github.go:56` — `api.github.com/repos/agent0ai/spynel/releases/latest` ; `internal/updater/updater.go:245` — `registry.npmjs.org/spynel/latest` : vérification de mise à jour, **10 s / horaire, lancements TUI interactifs seulement**, autorisée par le lancement (`PeriodicChecksEnabled`) ; les lancements headless / non interactifs ne font aucune vérification proactive.
- `internal/localapi/` + `internal/harness/worker_client.go` — API locale : socket Unix privé authentifié (token) et loopback authentifié entre le TUI et le service élu ; pas de TCP exposé par défaut.
- `internal/updater/worker_update.go:145-158` — HTTP sur socket Unix local (`http://worker/update`, dial `unix`) : IPC local, pas du réseau.

## 2. Dépendances

Dépendances (`go.mod`, 55 modules) : charmbracelet (TUI), sherpa-onnx-go (parole), whatsmeow (WhatsApp), go-sqlite3, protobuf, yaml. Aucun SDK de télémétrie déclaré (grep `posthog|amplitude|segment|sentry|datadog|newrelic|telemetry` dans `go.mod`/`go.sum` : 0 hit). L'adapter est **stdlib Python seule** (0 import réseau, vérifié par AST dans le smoke).

## 3. Preuve d'exécution — namespace sans interface

`unshare -n` (aucune interface réseau, DNS en échec) : `validate()` + `doctor()` réussissent (surface complète, 7/7 contrôles ok). Log : `logs-netns-validate.log`. **0 appel sortant possible dans ce namespace — la preuve est structurelle, pas déclarative.**

## 4. Poids dans le fork

Aucun poids monté : les modèles de parole (Parakeet) sont téléchargés explicitement par l'utilisateur dans le cache per-user du système, jamais dans le fork. Aucun fichier `.safetensors` / `.bin` / `.pt` / `.pth` / `.onnx` dans le repo (vérifié au fichier).

## 5. Déclencheurs tranchés

| Déclencheur | Décision |
|---|---|
| Vérification de mise à jour (GitHub / npm) | Interactive seulement, autorisée par le lancement — **conservée telle quelle** (comportement amont documenté, pas une télémétrie) |
| Téléchargement du modèle de parole (Parakeet) | Explicite, parole activée par l'utilisateur — **conservé tel quel** |
| Canaux Telegram / WhatsApp | Activés et authentifiés par l'utilisateur — **conservés tels quels** |
| API locale (socket Unix / loopback) | IPC local authentifié — **conservé tel quel** |
| SDK de télémétrie | Aucun — **rien à retirer** |
| Appel réseau à l'import | Aucun (prouvé en netns pour l'adapter ; l'amont n'appelle rien à l'import) — **rien à retirer** |
| Poids montés dans le fork | Aucun — **conforme** |

## 6. Ré-audit

À chaque changement de commit gelé ou d'adapter, et au minimum à chaque transition d'état.
