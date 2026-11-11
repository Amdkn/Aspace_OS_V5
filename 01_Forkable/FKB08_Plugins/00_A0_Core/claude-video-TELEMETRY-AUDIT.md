# claude-video — Audit télémétrie (D-N048, V5, H-M4)

**Module :** `claude-video` (fork `Amdkn/claude-video`, gel `03ceb42f7fa2c4439aca01752118044baabffb8f`, MIT, skill 0.3.2, Python stdlib + yt-dlp + ffmpeg)
**Verdict : télémétrie zéro par construction — 0 SDK tiers, 0 appel sortant par défaut.**
**Méthode :** scan statique (grep exhaustif du code, des dépendances et des docs) + lecture des chemins de code + preuves réseau `unshare -n`. Aucun appel réseau n'a été exécuté par l'audit (aucune clé, aucun téléchargement, aucun provider contacté).

## §1 — Scan statique (SDK télémétrie)

| Motif cherché | Occurrences |
|---|---|
| posthog / sentry / mixpanel / amplitude / segment | **0** (code, scripts, docs, JSON) |
| analytics / tracking / beacon (code) | **0** (les seules occurrences sont des mots du langage naturel : CHANGELOG « segment timestamps », README « Segment timestamps are retained » — des horodatages de transcription, pas de télémétrie) |
| `requests` / `httpx` / `aiohttp` | **0** — réseau stdlib `urllib` uniquement (`gemini.py`, `whisper.py`) |

## §2 — Appels réseau (fonctionnels, tous déclenchés par l'utilisateur)

| Hôte / appel | Déclencheur | Défaut | Fichier |
|---|---|---|---|
| Source vidéo + CDN (via yt-dlp, subprocess) | `/watch <url>` explicite de l'utilisateur | N/A (c'est la fonction) | `download.py` (yt-dlp `--no-playlist --no-simulate`) |
| `https://api.groq.com/openai/v1/audio/transcriptions` | Transcription, backend `groq` | OFF — exige `GROQ_API_KEY` explicite | `whisper.py` |
| `https://api.openai.com/v1/audio/transcriptions` | Transcription, backend `openai` | OFF — exige `OPENAI_API_KEY` explicite | `whisper.py` |
| `https://generativelanguage.googleapis.com` | Moteur `gemini` | OFF — exige `GEMINI_API_KEY` explicite | `gemini.py` |
| `https://aistudio.google.com/apikey` | Lien de documentation uniquement (jamais appelé) | — | `gemini.py`, `setup.py` |
| Installateurs `setup.py` : `astral.sh/uv`, `brew.sh`, `deno.com`, `download.pytorch.org/whl/cpu`, `docs.astral.sh` | `setup.py` (installation WhisperX) explicite | N/A (setup seul) | `setup.py` |

Aucun de ces appels n'est de la télémétrie : ce sont les fonctions du produit (télécharger la vidéo demandée, transcrire avec le provider choisi par l'utilisateur, installer les dépendances choisies).

## §3 — Pyannote (télémétrie désactivée par le code amont)

`skills/watch/scripts/local_whisperx.py:67`, fonction `child_env()` : l'environnement enfant du processus WhisperX force `PYANNOTE_METRICS_ENABLED='0'` (avec `PYTHONIOENCODING='utf-8'`, `PYTHONWARNINGS='ignore'`). La documentation amont le confirme (README : « Pyannote telemetry is disabled » ; SKILL.md §163 : « Pyannote telemetry is disabled »). Warm-cache : l'inférence locale fonctionne hors-ligne ; les bibliothèques de modèles peuvent encore tenter des vérifications de cache/mise à jour réseau (déclaration amont, non vérifiée ici — l'adapter ne lance jamais WhisperX).

## §4 — Clés et configuration

Clés lues depuis l'environnement ou `~/.config/watch/.env` (mode `0600`, `config.py`) : `GROQ_API_KEY`, `OPENAI_API_KEY`, `GEMINI_API_KEY`. Aucune clé n'est committée (règle AGENTS.md amont, tenue au gel). L'adapter ne lit jamais le fichier `.env` et ne rapporte la présence des clés qu'en booléens (jamais de valeur). Aucune clé n'a été fournie pendant cet audit (les trois absentes dans l'environnement de test).

## §5 — Preuves réseau (`unshare -n`, namespace sans interface)

- `setup.py --json` sous `unshare -n` : **rc=0**, JSON complet (`engine: local`, `gemini_key_present: false`, `has_api_key: false`, `missing_binaries: [yt-dlp]`) — le preflight ne fait aucun appel réseau.
- `setup.py --check` sous `unshare -n` : rc=2, diagnostic local propre (« Missing yt-dlp ») — aucune tentative réseau, aucun blocage.
- `validate.py doctor` sous `unshare -n` : **rc=0** — l'adapter est prouvé hors-ligne.
- La suite amont passe sans clé et sans réseau sortant (248 passés, 1 ignoré).

## §6 — Dépendances

Stdlib Python uniquement pour le code de la skill (`urllib`, `subprocess`, `argparse`, `json`, `re`, `tempfile`, `pathlib`). Binaires externes : `ffmpeg`/`ffprobe` (locaux, aucun réseau), `yt-dlp` (subprocess, téléchargement à la demande). Aucun `requirements.txt` / `pyproject.toml` / `package.json` — aucune dépendance Python tierce à auditer. La CI installe `pytest` + `yt-dlp[default]` (outils de test, pas du produit).

## §7 — Ce que l'adapter coupe (par contrat)

L'adapter (`aspace-claude-video-adapter/validate.py`) ne télécharge rien, n'appelle aucun provider, n'ouvre aucun socket — vérifié par AST dans le smoke test 7 (aucun import `urllib`/`requests`/`httpx`/`aiohttp`/`socket`). Gardes d'environnement : `DO_NOT_TRACK=1`, `WATCH_WHISPER_BACKEND=none`, `HF_HUB_OFFLINE=1`, HOME scratch. La surface est lecture seule sur l'arbre de la skill.

## §8 — Réserves

1. Les vérifications de cache/mise à jour des bibliothèques de modèles WhisperX (déclaration amont) n'ont pas été prouvées par capture — l'adapter ne lance jamais WhisperX, donc hors périmètre de l'adapter ; à re-vérifier si WhisperX est un jour invoqué.
2. `yt-dlp` contacte la source vidéo et ses CDN (fonction du produit) ; un cookie explicite (`--cookies`) est un jar en lecture/écriture — opt-in uniquement, jamais inspecté automatiquement (règle SKILL.md).
3. Le test ignoré de la suite (1 skipped) n'a pas été investigué (0 échec).
