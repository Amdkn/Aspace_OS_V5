# Audit télémétrie — agent-desktop (FKB04)

**Module :** `Amdkn/agent-desktop` (fork de `vercel-labs/agent-desktop`), commit `54855b62`, v1.2.0, Apache-2.0.
**Date :** 2026-11-12. **Auditeur :** Antigravity (Aspace OS V5).

## 1. Scan statique (`Cargo.toml`, `npm/package.json`, `src/*.rs`)
- **SDKs télémétrie** : Aucun (`sentry`, `posthog`, `segment`, `analytics` absents).
- **Surface locale** : Lecture de l'arbre d'accessibilité natif OS (Windows UIA / macOS AX / Linux AT-SPI) + serveur MCP local (`agent-desktop mcp`).
- **Variables d'isolation** : `DO_NOT_TRACK=1`, `ASPACE_ZERO_TELEMETRY=1`.

## 2. Statut Souverain
- **Verdict** : PROPRE (zéro télémétrie embarquée). Prêt pour le Palier 2 de `codex-chatgpt-web` (pilotage des plateformes desktop téléchargées).
