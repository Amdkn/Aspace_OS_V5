# Audit télémétrie — agent-browser (FKB04)

**Module :** `Amdkn/agent-browser` (fork de `vercel-labs/agent-browser`), commit `f88c40b7`, v0.42.0, Apache-2.0.
**Date :** 2026-11-12. **Auditeur :** Antigravity (Aspace OS V5).

## 1. Scan statique (`package.json`, `bin/*.js`, `cli/Cargo.toml`, `cli/src/*.rs`)
- **SDKs télémétrie** : Aucun (`sentry`, `posthog`, `segment`, `analytics`, `amplitude` absents).
- **Appels réseau** : Uniquement CDP local (`ws://127.0.0.1:...`) ou URLs explicitement demandées par l'agent.
- **Variables d'isolation** : `DO_NOT_TRACK=1`, `ASPACE_ZERO_TELEMETRY=1`.

## 2. Statut Souverain
- **Verdict** : PROPRE (zéro télémétrie embarquée). Prêt pour le Palier 1 de `codex-chatgpt-web` (snapshot d'accessibilité `@e1`, `@e2` + daemon CDP).
