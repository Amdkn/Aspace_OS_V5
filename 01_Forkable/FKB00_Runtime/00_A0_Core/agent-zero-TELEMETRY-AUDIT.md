# Audit télémétrie — D-N051 F8 pas 5 (agent-zero)

This is by an automated agent, not a human.

- Gel : `ba9b67df0f54ac78106ae85c552ef5d2458f7c9a`
- Fork : `Amdkn/agent-zero` ← `agent0ai/agent-zero`
- Date d'audit : 2026-11-10 (observé à l'API et au fichier, au gel)
- Méthode : `git grep` sur les fichiers suivis au gel (`*.py`, `*.ts`, `*.js`),
  lecture des appelants, vérification des valeurs par défaut.

## Verdict

**H-P5-8 : QUALIFIÉ — 1 signal dans le fork, nommé ci-dessous ; 0 signal
dans le portage natif.**

La mention « télémétrie 0 signal » du design ne tient pas au gel :
le fork contient UN appel sortant de classe télémétrie (contrôle de
mise à jour avec identifiant anonymisé persistant, activé par défaut).
Il n'est PAS porté : ni l'adapter Python ni les modules Rust natifs
ne contiennent de contrôle de mise à jour, d'identifiant persistant,
ni d'appel sortant autre que le gateway `:31415`.

## Le signal (fork, 1)

| # | Fichier | Appel |
|---|---|---|
| 1 | `helpers/update_check.py:4-18` | `POST https://api.agent-zero.ai/a0-update-check` avec `{"current_version": <version>, "anonymized_id": sha256(persistent_id)[:20]}` |

- Appelant : `extensions/python/user_message_ui/_10_update_check.py:76`
  (`version = await update_check.check_version()`).
- Porte : le réglage `update_check_enabled`, dont la valeur par défaut
  est `True` (`helpers/settings.py:634`).
- Nature : contrôle de version avec identifiant anonymisé persistant
  (20 caractères hex du sha256 d'un id persistant). Ce n'est pas un
  SDK d'analytics tiers, mais c'est un signal sortant stable vers le
  domaine de l'amont, actif par défaut. Il est abandonné avec le fork :
  le portage natif ne le reprend pas.

## Ce qui n'existe PAS dans le fork (vérifié au gel)

- Aucun SDK d'analytics : `sentry`, `posthog`, `mixpanel`,
  `segment.io`, `amplitude` (analytics), `hotjar` — 0 occurrence dans
  les `*.py` suivis (les occurrences trouvées dans `webui/vendor/`
  et `plugins/_whisper_stt/` sont des faux positifs : liste de mots-clés
  du langage Raku, amplitude audio, `isEntryMissing`).
- `ANONYMIZED_TELEMETRY` n'apparaît que dans `tests/test_secrets.py`
  (le test vérifie que le nom n'entre pas dans les secrets exposés au
  prompt) — jamais dans le code d'exécution.
- Aucun `requests.post/get` vers un hôte externe dans les `*.py`
  (hors adapter).

## Appels sortants du fork qui ne sont PAS de la télémétrie

Fonctions utilisateur ou opérationnelles, déclenchées par l'usage,
sans identifiant persistant ni envoi d'usage :

| Fichier | Appel | Nature |
|---|---|---|
| `helpers/searxng.py` | `aiohttp` vers l'instance SearXNG configurée | recherche utilisateur |
| `helpers/rfc.py` | `aiohttp` (RFC) | lecture de RFC |
| `plugins/_context_window/helpers/currency.py` | `httpx` (taux de change, timeout 3 s) | fonction |
| `plugins/_browser/helpers/extension_manager.py` | `urllib` (téléchargement d'extension) | installation |
| `helpers/tailscale_tunnel.py:41` | `urllib` vers `TAILSCALE_STABLE_PACKAGES_URL` | téléchargement binaire |
| `helpers/tunnel_origins.py:100` | `urllib` (timeout 0,35 s) | vérification d'atteignabilité du tunnel |
| `helpers/cli_tunnel.py:54` | `urllib` (timeout 60 s) | vérification du tunnel |
| `helpers/server_startup.py:374` | `urllib` (timeout 2 s) | contrôle de santé local |
| `docker/run/fs/exe/self_update_manager.py:1016` | `urllib` (timeout 5 s) | auto-mise à jour |
| `plugins/_a2a_chat/helpers/fasta2a_client.py:43` | `httpx.AsyncClient` | protocole A2A (pair configuré) |
| `.github/scripts/docker_release_plan.py` | `urlopen` (CI seulement, pas le runtime) | script CI |

## Surface réseau conservée (fork, D3)

- Serveur UI : `run_ui.py` — `run_uvicorn_with_retries(host, port,
  ws="wsproto")`. Hôte par défaut `"localhost"`
  (`run_ui.py:32-35`, `WEB_UI_HOST` en surcharge), port par défaut
  `5000` (`helpers/runtime.py:171-175`, `WEB_UI_PORT` en surcharge).
- Tunnel : port API par défaut `55520`
  (`helpers/runtime.py:178-184`, `TUNNEL_API_PORT` en surcharge) ;
  `helpers/runtime.py:67-70` : `get_local_url()` retourne
  `"127.0.0.1"` (ou `host.docker.internal` en conteneur).
- Binding localhost seulement par défaut. Aucun `0.0.0.0` dans
  `run_ui.py` ni `helpers/runtime.py`.

## Portage natif : 0 signal

- Adapter Python (`aspace-agent-zero-adapter/`) : un seul appel
  sortant, `urllib.request.urlopen` vers le gateway
  `http://127.0.0.1:31415/v1/chat/completions`
  (`providers.py:108`). Aucune clé lue (`grep API_KEY|api_key` :
  seules les docstrings, la sentinelle `get_api_key` → `"None"`, et
  les assertions de test).
- Modules Rust (`crates/infinity-daemon/src/{agent,provider,memory,job}.rs`) :
  un seul appel sortant, le client reqwest du `provider.rs` vers le
  gateway `:31415`. Aucun contrôle de mise à jour, aucun identifiant
  persistant, aucun appel vers `api.agent-zero.ai`.
- Le daemon natif refuse tout bind non-loopback (`lib.rs:
  require_loopback`, D6) ; la surface UI reste locale.
