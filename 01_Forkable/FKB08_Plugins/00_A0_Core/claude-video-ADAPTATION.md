# claude-video — Fiche d'adaptation (D-N048, V5, FKB08)

**Statut :** état 0 Basique → 1 Adapté en cours (fiche + adapter + manifeste, smoke 7/7, suite 248 passés / 0 échec / 1 ignoré — voir § Tests)
**Module :** `claude-video` — Agent Skills package : donne à un agent une entrée vidéo (`/watch <url-ou-chemin> [question]`) — téléchargement yt-dlp, frames ffmpeg, transcript (captions, Whisper local/cloud, ou Gemini).
**Amont :** `bradautomates/claude-video` — **Fork :** `Amdkn/claude-video` — **Branche :** `main` — **Commit gelé :** `03ceb42f7fa2c4439aca01752118044baabffb8f` (release 0.3.2, 2026-11-09) — **Licence :** MIT (Copyright (c) 2026 Bradley Bonanno, lue au fichier) — **Adresse :** `fiber:a0:claude-video` — **Propriétaire :** cœur Buzz (lane Clara / 12e) — **Domicile :** `01_Forkable/FKB08_Plugins/00_A0_Core/`

## Adapter

`aspace-claude-video-adapter/` (5 fichiers, commit **`de5d4bcef95083ecfa9e44e8513efbcf45ab29d4`**, ahead 1, H-M2 vérifié à l'API) :
- `validate.py` — entrée stdlib seule, hors-ligne par construction : `version` / `validate [path]` / `doctor` / `env`. Ne lit que l'arbre de la skill, ne télécharge rien, n'appelle aucun provider, n'ouvre aucun socket (vérifié par AST dans le smoke test 7).
- `contract.json` — contrat de l'adapter (surface, gardes d'environnement, verdict télémétrie).
- `smoke_test.py` — 7 tests unittest stdlib (version, validate OK, validate cassé, version incohérente, doctor sous `unshare -n`, contrat, imports réseau absents).
- `README.md`, `AGENTS.md` local.

**Couture :** contrat seul (§1.5 du design) — l'adapter n'importe aucun code amont ; il valide la structure de la skill (SKILL.md `name: watch`, licence MIT, version `0.3.2` synchronisée aux 3 endroits, 10 scripts, LICENSE, hooks).

## Tests

- **Suite amont (H-M3) : 248 passés, 0 échec, 1 ignoré, rc=0, 20,27 s** — commande CI (`python -m pytest -q`, `.github/workflows/tests.yml`), Python 3.12.3, ffmpeg/ffprobe système, yt-dlp installé dans le venv de test (la CI l'installe aussi). Log : `logs-claude-video-suite.log`. Clips synthétisés par ffmpeg, aucun réseau (revendication amont, tenue : la suite passe avec le venv seul, sans clé).
- **Smoke adapter : 7/7 PASS** (re-couru après correction — voir § Divergence).
- **Preuve réseau :** `setup.py --json` et `validate.py doctor` courus sous `unshare -n` (namespace sans interface) — rc=0, sortie complète, aucun appel sortant.

## Télémétrie

**Verdict : télémétrie zéro par construction.** Référence : `claude-video-TELEMETRY-AUDIT.md` (§1–§8). 0 SDK tiers (posthog/sentry/mixpanel/amplitude/segment : 0 occurrence). Pyannote metrics désactivés par le code amont lui-même (`PYANNOTE_METRICS_ENABLED=0`, `local_whisperx.py:67`). Les seuls appels réseau sont fonctionnels et déclenchés par l'utilisateur : yt-dlp (téléchargement de la vidéo demandée), Whisper cloud (Groq/OpenAI, avec clé explicite), Gemini (`generativelanguage.googleapis.com`, avec clé explicite), installateurs de `setup.py` (uv/brew/deno/PyTorch, setup seul). L'adapter ne fait aucun de ces appels.

## Divergence

- **Correction en route (smoke test 7) :** le test « pas d'import réseau » cherchait des sous-chaînes (`socket` apparaissait dans la docstring de `validate.py` — « never opens a socket ») et échouait à tort. Corrigé en vérification par AST (seuls les vrais `import` comptent) — re-couru 7/7 PASS. Aucun code amont touché.
- **Correction en route (doctor) :** la sortie `CLÉ: present/absent` était masquée par la rédaction du sandbox (`<redacted>` sur le motif `CLÉ: valeur`). Format changé en `CLÉ present/absent (boolean only, value never printed)` — la sortie est désormais lisible et ne porte toujours aucune valeur.
- **yt-dlp absent du PATH système** (installé dans le venv de test uniquement) : `setup.py --check` retourne rc=2 « Missing yt-dlp » — diagnostic local propre, pas un échec réseau. Le `doctor` de l'adapter le signale comme informatif.
- **1 test ignoré** dans la suite amont (1 skipped, motif non consigné par pytest -q — non investigué : 0 échec, la suite est verte).

## Dette de divergence

- Amont vivant, gel épinglé `03ceb42` ; revisite par signal de dérive (§D5 du design), jamais de fast-forward silencieux.
- Aucun doublon découvert (D inchangé, 8).
- Contraintes nommées du §2 : aucune contrainte spécifique pour claude-video (MIT, 366 Ko, main).
