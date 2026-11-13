# Fiche d'Adaptation — agent-browser (FKB04 -> CCW Palier 1)

**Dépôt :** `Amdkn/agent-browser` (`01_Forkable/FKB04_Tools_Anything/agent-browser`), commit `f88c40b7`.

## Rôle dans `codex-chatgpt-web` (CCW)
1. **Couche de stabilité navigateur (Palier 1)** : remplace ou complète les sélecteurs CSS fragiles par des snapshots d'arbre d'accessibilité (`@e1`, `@e2`) via CDP sur le port de débogage Electron ou Chromium dédié.
2. **Couplage API-Anything + REA** : capture les sessions authentifiées et gère les checkpoints humains (login/Passkey/CAPTCHA) pendant que `API-Anything` exécute les appels HTTP JSON appris.
