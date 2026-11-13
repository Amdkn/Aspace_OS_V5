# Fiche d'Adaptation — agent-desktop (FKB04 -> CCW Palier 2 Plus)

**Dépôt :** `Amdkn/agent-desktop` (`01_Forkable/FKB04_Tools_Anything/agent-desktop`), commit `54855b62`.

## Rôle dans `codex-chatgpt-web` (CCW Plus)
1. **Pilotage des apps desktop téléchargées** : complète `CLI-Anything` pour les applications IA Windows installées localement (ChatGPT Desktop, Claude Desktop, clients locaux) qui n'exposent ni API HTTP ni CLI.
2. **Exécution sans vol de focus** : utilise l'arbre d'accessibilité Windows UIA avec refs (`@ref`) et *skeleton drilling* via `agent-desktop mcp`.
