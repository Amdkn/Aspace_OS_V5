# .vscode/doctor.ps1 — Auto-vérification et Auto-réparation (Antifragile) de l'environnement Aspace OS V5 (VS Code + Orca + Herdr)
$ErrorActionPreference = 'SilentlyContinue'
$root = Split-Path $PSScriptRoot -Parent

# 1. Injecter tous les chemins d'outils dans la session courante
$paths = @(
  "$root\00_Memoire\.venv\Scripts",
  "$HOME\bin",
  "$HOME\.local\bin",
  "$HOME\AppData\Roaming\npm",
  "$HOME\AppData\Local\Microsoft\WinGet\Links",
  "$HOME\AppData\Local\Programs\supabase",
  "$HOME\AppData\Local\Programs\orca\resources\bin",
  "$HOME\AppData\Local\agy\bin",
  "C:\Program Files\PowerShell\7",
  "C:\Program Files\Git\cmd",
  "C:\Program Files\GitHub CLI",
  "C:\Program Files\nodejs",
  "C:\Python314",
  "C:\Python314\Scripts"
)
foreach ($p in $paths) {
  if ((Test-Path $p) -and ($env:PATH -notlike "*$p*")) {
    $env:PATH = "$p;$env:PATH"
  }
}

# 2. Self-healing : restaurer rg.exe, uv.exe, fd.exe, orca.cmd et herdr-app.cmd dans ~/bin
if (-not (Test-Path "$HOME\bin\rg.exe") -and (Test-Path "$HOME\.cache\opencode\bin\rg.exe")) {
  Copy-Item "$HOME\.cache\opencode\bin\rg.exe" "$HOME\bin\rg.exe" -Force
}
if (-not (Test-Path "$HOME\bin\uv.exe") -and (Test-Path "$root\00_Memoire\.venv\Scripts\uv.exe")) {
  Copy-Item "$root\00_Memoire\.venv\Scripts\uv.exe" "$HOME\bin\uv.exe" -Force
}
if (-not (Test-Path "$HOME\bin\fd.exe") -and (Test-Path "$HOME\.pi\agent\bin\fd.exe")) {
  Copy-Item "$HOME\.pi\agent\bin\fd.exe" "$HOME\bin\fd.exe" -Force
}
$orcaBin = "$HOME\AppData\Local\Programs\orca\resources\bin\orca.exe"
if ((Test-Path $orcaBin) -and -not (Test-Path "$HOME\bin\orca.cmd")) {
  "@echo off`r`n`"$orcaBin`" %*`r`n" | Set-Content "$HOME\bin\orca.cmd" -Encoding ascii
}
$herdrCmd = "$HOME\bin\herdr-app.cmd"
if ((Test-Path $herdrCmd) -and ((Get-Content $herdrCmd -Raw) -match '^\s*@echo off\s+start ""')) {
  '@echo off
if "%~1"=="" (
  start "" "C:\Users\amado\AppData\Local\Programs\herdr-app\herdr-app.exe"
) else (
  "C:\Users\amado\AppData\Local\Programs\herdr-app\herdr-app.exe" %*
)
' | Set-Content $herdrCmd -Encoding ascii
  Write-Host "[SELF-HEAL] herdr-app.cmd réparé (stdout synchrone restauré)" -ForegroundColor Yellow
}

# 3. Self-healing : nettoyer NODE_EXTRA_CA_CERTS s'il pointe vers un fichier inexistant (ex: .llmtrim\ca.pem)
if ($env:NODE_EXTRA_CA_CERTS -and -not (Test-Path $env:NODE_EXTRA_CA_CERTS)) {
  Remove-Item Env:\NODE_EXTRA_CA_CERTS -EA SilentlyContinue
  [Environment]::SetEnvironmentVariable("NODE_EXTRA_CA_CERTS", $null, "User")
}

# 4. Self-healing : vérifier ~/.config/herdr-app/programs.json (incluant claude, codex, opencode, pi, dsh-harness, dsh-superagent, antigravity)
$herdrProg = "$HOME\.config\herdr-app\programs.json"
if (-not (Test-Path $herdrProg)) {
  @'
{
  "programs": {
    "claude": { "name": "Claude Code", "icon": "icons/claude.svg", "tint": false, "tile": "#1c1d21", "color": "#ffffff", "run": ["claude", "--dangerously-skip-permissions"] },
    "codex": { "name": "Codex", "icon": "icons/codex.svg", "tint": false, "tile": "#1c1d21", "color": "#ffffff", "run": ["codex", "--no-daemon", "--dangerously-bypass-approvals-and-sandbox"] },
    "opencode": { "name": "OpenCode", "icon": "icons/opencode.svg", "tint": false, "tile": "#1c1d21", "color": "#ffffff", "run": ["opencode"] },
    "pi": { "name": "Pi Agent", "icon": "icons/pi.svg", "tint": false, "tile": "#1c1d21", "color": "#ffffff", "run": ["pi", "--approve"] },
    "dsh-harness": { "name": "DeepSeek Harness", "icon": "icons/terminal.svg", "tint": false, "tile": "#1c1d21", "color": "#ffffff", "run": ["dsh", "web"] },
    "dsh-superagent": { "name": "DeepSeek Superagent", "icon": "icons/terminal.svg", "tint": false, "tile": "#1c1d21", "color": "#ffffff", "run": ["dsh", "--profile", "superagent"] },
    "antigravity": { "name": "Antigravity", "icon": "icons/antigravity.svg", "tint": false, "tile": "#1c1d21", "color": "#ffffff", "run": ["agy", "--dangerously-skip-permissions"] }
  }
}
'@ | Set-Content $herdrProg -Encoding utf8
  Write-Host "[SELF-HEAL] Herdr programs.json restauré" -ForegroundColor Yellow
}

# 5. Self-healing : vérifier OpenCode (opencode.json) et Pi (.pi/settings.json + ~/.pi/agent/settings.json)
$piGlobal = "$HOME\.pi\agent\settings.json"
if (Test-Path $piGlobal) {
  try {
    $pj = Get-Content $piGlobal -Raw | ConvertFrom-Json
    if ($pj.defaultProjectTrust -ne "always") {
      $pj | Add-Member defaultProjectTrust "always" -Force
      $pj | ConvertTo-Json -Depth 10 | Set-Content $piGlobal -Encoding utf8
      Write-Host "[SELF-HEAL] Pi defaultProjectTrust remis sur always" -ForegroundColor Yellow
    }
  } catch {}
}

# 6. Self-healing : vérifier que .claude/settings.json est un JSON valide en mode bypassPermissions
$cs = Join-Path $root ".claude\settings.json"
if (Test-Path $cs) {
  try {
    $j = Get-Content $cs -Raw | ConvertFrom-Json
    if ($j.permissions.defaultMode -ne "bypassPermissions" -or -not $j.skipDangerousModePermissionPrompt) {
      if (-not $j.permissions) { $j | Add-Member permissions ([pscustomobject]@{}) -Force }
      $j.permissions | Add-Member defaultMode "bypassPermissions" -Force
      $j | Add-Member skipDangerousModePermissionPrompt $true -Force
      $j | ConvertTo-Json -Depth 20 | Set-Content $cs -Encoding utf8
      Write-Host "[SELF-HEAL] .claude/settings.json remis en bypassPermissions" -ForegroundColor Yellow
    }
  } catch {
    if (Test-Path "$cs.bak2") { Copy-Item "$cs.bak2" $cs -Force; Write-Host "[SELF-HEAL] .claude/settings.json restauré depuis backup" -ForegroundColor Yellow }
  }
}

# 5. Vérification des 27 outils critiques (incluant dsh DeepSeek Harness et fd)
$tools = @("pwsh","git","gh","node","npm","pnpm","python","uv","uvx","rg","fd","jq","sqlite3","ffmpeg","supabase","pm2","claude","codex","dsh","gemini","opencode","pi","hc","herdr-app","orca","agy","graphify")
$ok = @(); $missing = @()
foreach ($t in $tools) {
  if (Get-Command $t -EA SilentlyContinue) { $ok += $t } else { $missing += $t }
}

$skillsCount = (Get-ChildItem "$root\.claude\skills" -Directory -EA SilentlyContinue).Count
$agentsCount = (Get-ChildItem "$root\.claude\agents" -Filter "*.md" -EA SilentlyContinue).Count
$hcTemplates = ((hc templates --json 2>$null | ConvertFrom-Json).templates | ForEach-Object { $_.name }) -join ", "
$herdrErrors = Get-ChildItem "$HOME\.config\herdr-app" -Filter "*.error" -EA SilentlyContinue

Write-Host "=== ASPACE OS V5 — DOCTOR ANTIFRAGILE (VS CODE + ORCA + HERDR + OPENCODE + PI + FACTORY) ===" -ForegroundColor Cyan
Write-Host ("Outils actifs ({0}/{1}) : {2}" -f $ok.Count, $tools.Count, ($ok -join ", ")) -ForegroundColor Green
if ($missing.Count -gt 0) {
  Write-Host ("Outils manquants : {0}" -f ($missing -join ", ")) -ForegroundColor Red
}
Write-Host ("Mémoire WikiLLM : {0} concepts | Skills : {1} | Agents Factory : {2} | OpenCode : {3} | Pi : {4} | Templates hc : [{5}] | Graphe : {6}" -f (Get-ChildItem "$root\00_Memoire\bundle\concepts" -Filter *.md).Count, $skillsCount, $agentsCount, (Test-Path "$root\opencode.json"), (Test-Path "$root\.pi\settings.json"), $hcTemplates, (Test-Path "$root\graphify-out\graph.json")) -ForegroundColor Cyan
exit 0
