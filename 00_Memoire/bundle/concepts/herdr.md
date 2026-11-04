---
type: Reference
title: Environnement Herdr (herdr-app + hc)
description: Configuration antifragile de Herdr, herdr-app.cmd, programs.json, config.toml, templates hc et protocole d'orchestration.
resource: file:///C:/Users/amado/.config/herdr-app/AGENTS.md
tags: [herdr, hc, orchestration, antifragile, templates]
generated: { by: agent/antigravity, at: 2026-11-03T15:24:00-05:00 }
status: active
---

# Architecture Antifragile Herdr (`herdr-app` + `hc`)

| Composant | Fichier | Rôle |
|---|---|---|
| **Fix `herdr-app.cmd`** | `C:\Users\amado\bin\herdr-app.cmd` | Le wrapper d'origine utilisait `start "" herdr-app.exe %*`, ce qui détachait le processus et avalait tout `stdout` (`herdr-app status`, `commands`, `--skill` renvoyaient vide). Corrigé pour exécuter directement `herdr-app.exe %*` dès qu'un argument est fourni. |
| **Boutons Agents Herdr** | `~/.config/herdr-app/programs.json` | Surcharge en direct (`live`) le lancement des agents depuis l'UI Herdr : `claude` → `["claude", "--dangerously-skip-permissions"]`, `codex` → `["codex", "--no-daemon", "--dangerously-bypass-approvals-and-sandbox"]` (`--no-daemon` requis par `hc`), `antigravity` → `["agy", "--dangerously-skip-permissions"]`. |
| **Core & Recovery Shell** | `~/.config/herdr-core/config.toml` & `%APPDATA%\herdr-core\config.toml` | `shell = ["pwsh.exe", "-NoLogo"]` pour que tous les nouveaux terminaux et les terminaux récupérés (`hc keep`) démarrent en PowerShell 7. |
| **Profil PowerShell 7** | `Documents\PowerShell\profile.ps1` & `Microsoft.PowerShell_profile.ps1` | Injecte automatiquement les 25 outils CLI dans `PATH` + les variables `ANTHROPIC_BASE_URL` (`http://127.0.0.1:31415`), `PYTHONUTF8=1`, `DO_NOT_TRACK=1` dans chaque terminal ouvert par Herdr. |
| **Templates `hc`** | `~/.config/herdr-core/templates/` (`worker.md`, `reviewer.md`) | Rôles prêts à l'emploi pour `hc run --bg --name <nom> worker "<tâche>"` et `reviewer "<tâche>"` (lancent Claude en bypass avec consigne de retour `hc send`). |
| **Skills Herdr** | `.claude/skills/herdr-app` & `.claude/skills/herdr-core` (et `.agents/skills/`) | Manuels complets `herdr-app --skill` et `hc --skill` embarqués comme skills natifs dans V5. |

# Commandes d'orchestration Herdr
```powershell
herdr-app status                                              # JSON : layout, space, tab, focused_pane, errors
hc ls                                                         # terminaux : address, agent, where = "Space / Tab"
hc templates                                                  # rôles disponibles : worker, reviewer
hc run --bg --name w1 worker "Tâche... Réponds avec hc send $env:HC_TERMINAL_ID"
hc send <t> "Tâche. Réponds avec: hc send $env:HC_TERMINAL_ID '<résultat>'"
hc wait <t>; hc read <t> --lines 50
herdr-app shot                                                # capture PNG instantanée de la fenêtre Herdr
```
