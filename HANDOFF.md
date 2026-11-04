# HANDOFF — Reprise de continuité Aspace OS V5 (2026-11-04)

Lire d'abord : `AGENTS.md`, `00_Memoire/bundle/index.md`, fin de `00_Memoire/bundle/log.md`, `00_Memoire/bundle/concepts/sakana-fugu-inference.md`.

## État vérifié
- `pwsh -NoProfile -File factory/checks.ps1` → 6/6 PASS.
- Étage 3 de Cube Farm = `Areas OS` (522 Holons), total 3 OS = 578. Modules `holon-topology.ts` et `aspaceHolons.ts` importables sous Node 24 (578 ok).
- `codex-chatgpt-web` : bouclier télémétrie branché, MAJ GitHub off, `start-aspace-codex-web.ps1 -VerifyOnly` OK.
- Source brute : `00_Memoire/raw/sakana-fugu-10d-architecture-2026.md`.

## Reste à faire (ordre)
1. `cd 01_Forkable/automaton; npm i; npx vitest run src/__tests__/aspace-ceo-holon.test.ts` (vitest absent → ERR_MODULE_NOT_FOUND).
2. `cd 01_Forkable/cubefarm; npm i; npx vitest run server/aspaceHolons.test.ts`.
3. UI : touche `Tab` 2D en Tableaux-Portails dans `01_Forkable/cubefarm/client/src/ui/` (données prêtes : `PORTAL_BOARDS_2D`, `LOOP_HIERARCHY` dans `shared/aspaceHolons.ts`) + Mezzanine `agent-office`.
4. Pages concept encore obsolètes (193 Holons / Business OS) : `concepts/aspace-3os-holons.md`, `concepts/ceo-automaton-cubefarm.md`.
5. `00_Memoire\.venv\Scripts\graphify.exe update .`
6. Wire `ASPACE_DOM_TELEMETRY_SHIELD_SCRIPT` aussi dans `markTurnTabSurface` si absent des onglets manuels.
7. Brancher Sakana Fugu (`AspaceFuguRouter`) sur le routeur réel (`freellmapi` :31415, LFM3 :9931).

## Conventions
- `log.md` strictement append-only. Réponses en français télégraphique. Aucun process utilisateur tué sans ordre.
- `01_Forkable/{automaton,cubefarm,codex-chatgpt-web}` sont vendorisés (historique upstream local dans `.git.upstream/`, non versionné). Les 7 autres forks : `pwsh 01_Forkable/clone-forkables.ps1`.
- Locaux hors repo : serveur LFM3 `127.0.0.1:9931`, `Codex Web GPT.exe` installé (ne pas tuer).
- Quota modèle Antigravity épuisé par moments : basculer de modèle (pool failover).
