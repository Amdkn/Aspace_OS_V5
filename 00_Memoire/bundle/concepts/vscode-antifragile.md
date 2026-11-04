---
type: Reference
title: Environnement VS Code & Orca Omnipotent & Antifragile
description: Configuration de .vscode/, Orca (profile-state.db + 8 skills), .mcp.json et doctor.ps1 donnant accès à 25 CLIs et 6 serveurs MCP sans friction.
tags: [vscode, orca, ide, antifragile, mcp, path, doctor]
generated: { by: agent/antigravity, at: 2026-11-03T15:19:00-05:00 }
status: active
---

# Architecture IDE Omnipotent & Antifragile (VS Code + Orca + Herdr + OpenCode + Pi)

| Couche | Fichier / Emplacement | Rôle |
|---|---|---|
| **VS Code** | `.vscode/settings.json`, `tasks.json`, `extensions.json`, `launch.json`, `mcp.json` | Interpréteur Python pointé sur `00_Memoire/.venv`, terminal PowerShell 7 par défaut avec `PATH` complet (27 outils), exclusions watcher/search sur les clones, auto-exécution de `doctor.ps1`. |
| **Orca IDE & CLI** | `%APPDATA%\orca\profiles\local-default\profile-state.db` + `~/bin/orca.cmd` | Shell par défaut forcé sur `pwsh.exe` (`PowerShell 7`), `agentPermissionDefault: "full-access"`, `nativeChatPermissionMode: "full-access"`, `agentDefaultArgs.claude = "--dangerously-skip-permissions"`, `agentDefaultArgs.pi = "--approve"`, `agentDefaultEnv` injecté avec le `PATH` des 27 outils pour tous les agents (`claude`, `codex`, `gemini`, `opencode`, `antigravity`, `pi`, `dsh`), confirmations de fermeture/suppression désactivées. |
| **OpenCode (`opencode` 1.19.5)** | `opencode.json` (workspace) & `~/.config/opencode/opencode.jsonc` (global) | Modèle par défaut `freellmapi/auto` (1M tokens, routeur local `127.0.0.1:31415`) + 12 modèles (`fusion`, `claude-opus-4-5`, `claude-sonnet-4-5`, `qwen3.8-max`, `gemini-3.8-flash`, `gpt-5.6-luna`, `deepseek-v4-flash`, etc.). Permissions `allow` totales (`edit`, `bash`, `webfetch`, `doom_loop`, `external_directory`), instructions DOX/WikiLLM auto-chargées, 3 serveurs MCP actifs, 8 agents Factory (`.claude/agents/*.md`) et 3 commandes `/factory-status`, `/factory-gate`, `/factory-intake`. |
| **Pi Coding Agent (`pi` 0.84.2)** | `.pi/settings.json`, `.pi/APPEND_SYSTEM.md`, `.pi/extensions/aspace-factory.ts`, `.pi/prompts/*.md` & `~/.pi/agent/settings.json`, `~/.pi/agent/models.json` | `defaultProjectTrust: "always"` (zéro blocage de trust), `defaultProvider: "freellmapi"`, `defaultModel: "auto"`, `defaultThinkingLevel: "high"`, `shellPath: "C:/Program Files/Git/bin/bash.exe"`. Charge automatiquement les 11 skills `.agents/skills/` + `.claude/skills/`, l'extension TypeScript `.pi/extensions/aspace-factory.ts` (outils `factory_status`, `factory_gate`, `factory_intake`, `durable_subagent_spawn` + commande `/factory`) et les templates `/factory-build` et `/factory-review`. |
| **Orca, Herdr & Factory Skills** | `.claude/skills/` & `.agents/skills/` | 11 skills natifs extraits et activés dans V5 : 8 skills Orca + 2 skills Herdr (`herdr-app`, `herdr-core`) + 1 skill `aspace-factory`. |
| **Auto-Réparation** | `.vscode/doctor.ps1` | Script antifragile vérifiant les 27 outils CLI, supprimant les certificats `NODE_EXTRA_CA_CERTS` morts (`.llmtrim\ca.pem`), restaurant `rg.exe`, `uv.exe`, `fd.exe`, `orca.cmd`, `herdr-app.cmd` dans `~/bin`, et maintenant `.claude/settings.json`, `opencode.json` et `.pi/settings.json` en mode sans friction. |
| **Serveurs MCP** | `.mcp.json` & `~/.claude.json` | 6 serveurs MCP locaux pré-approuvés (`memory`, `desktop-commander`, `playwright`, `chrome-devtools`, `context7`, `jules`) et `hasTrustDialogAccepted: true` + `hasClaudeMdExternalIncludesApproved: true`. |

# 27 Outils CLI garantis dans le `PATH` (VS Code + Orca + Herdr + OpenCode + Pi + DeepSeek `dsh` + Claude Code)
`pwsh`, `git`, `gh`, `node`, `npm`, `pnpm`, `python`, `uv`, `uvx`, `rg` (ripgrep), `fd`, `jq`, `sqlite3`, `ffmpeg`, `supabase`, `pm2`, `claude`, `codex`, `dsh`, `gemini`, `opencode`, `pi`, `hc`, `herdr-app`, `orca`, `agy`, `graphify`.

# Commandes clés Orca (`orca`)
```powershell
orca status --json                       # état de l'application, du runtime et du graphe Orca
orca worktree list --json                # lister les worktrees gérés par Orca
orca terminal list --json                # lister les terminaux actifs dans Orca
orca agent launch --agent claude --json  # lancer un agent dans Orca (démarre en bypass + PATH complet)
orca orchestration run-list --json       # superviser des runs multi-agents Orca
orca computer capabilities --json        # contrôle GUI natif (Computer Use)
orca tab list --json                     # navigateur embarqué Orca
```
