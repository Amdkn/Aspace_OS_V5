# 02_Factory/checks.ps1 — Gate déterministe Aspace Software Factory ("Agent proposes, code disposes")
$ErrorActionPreference = 'Stop'
$root = Split-Path $PSScriptRoot -Parent
Set-Location $root

$failures = @()
Write-Host "=== ASPACE FACTORY — DETERMINISTIC GATE ===" -ForegroundColor Cyan

# 1. Vérifier que l'environnement et les 26 outils sont intacts
Write-Host "[1/6] Doctor & Tools Check..." -NoNewline
pwsh -NoProfile -ExecutionPolicy Bypass -File "$root\.vscode\doctor.ps1" | Out-Null
if ($LASTEXITCODE -ne 0) { $failures += "doctor.ps1 failed" } else { Write-Host " PASS" -ForegroundColor Green }

# 2. Vérifier l'absence de résidus OpenWiki
Write-Host "[2/6] OpenWiki Purge Check..." -NoNewline
if ((Test-Path "$root\.github\workflows\openwiki-update.yml") -or (Test-Path "$root\00_Memoire\openwiki")) {
  $failures += "OpenWiki residue found"
  Write-Host " FAIL" -ForegroundColor Red
} else { Write-Host " PASS" -ForegroundColor Green }

# 3. Vérifier la validité de tous les fichiers JSON critiques
Write-Host "[3/6] JSON Schema & Config Check..." -NoNewline
foreach ($jf in @(".claude\settings.json", ".claude\settings.local.json", ".mcp.json", ".vscode\settings.json", ".vscode\tasks.json", ".vscode\mcp.json", "02_Factory\config.json")) {
  $p = Join-Path $root $jf
  if (-not (Test-Path $p)) { $failures += "Missing JSON: $jf"; continue }
  try { Get-Content $p -Raw | ConvertFrom-Json | Out-Null } catch { $failures += "Invalid JSON: $jf" }
}
if ($failures.Count -eq 0) { Write-Host " PASS" -ForegroundColor Green } else { Write-Host " FAIL" -ForegroundColor Red }

# 4. Vérifier le contrat DOX + WikiLLM + OKF v0.2
Write-Host "[4/6] DOX & OKF v0.2 Bundle Check..." -NoNewline
foreach ($cf in Get-ChildItem "$root\00_Memoire\bundle\concepts" -Filter *.md) {
  $raw = Get-Content $cf.FullName -Raw
  if ($raw -notmatch '(?s)^---\r?\n.*?\btype:\s*\S+.*?\r?\n---') {
    $failures += "Invalid OKF frontmatter in $($cf.Name)"
  }
}
if ($failures.Count -eq 0) { Write-Host " PASS" -ForegroundColor Green } else { Write-Host " FAIL" -ForegroundColor Red }

# 5. Vérifier l'intégrité Append-Only de 00_Memoire/bundle/log.md via Git
Write-Host "[5/6] Append-Only Log Guard..." -NoNewline
$diff = git diff HEAD -- "00_Memoire/bundle/log.md" 2>$null
$deletedLines = ($diff | Where-Object { $_ -match '^-[^-]' }).Count
if ($deletedLines -gt 0) {
  $failures += "00_Memoire/bundle/log.md had $deletedLines deleted/modified lines (APPEND-ONLY violation)"
  Write-Host " FAIL ($deletedLines modified lines)" -ForegroundColor Red
} else { Write-Host " PASS" -ForegroundColor Green }

# 6. Scan anti-fuite de secrets dans les fichiers suivis par Git
Write-Host "[6/6] Secret Scanning Guard..." -NoNewline
$tracked = git ls-files 2>$null | Where-Object { $_ -notmatch '(\.test\.(ts|js)|_test\.(ts|js)|test-fixtures)' }
if ($tracked) {
  $leaks = Select-String -Path $tracked -Pattern '(ghp_[A-Za-z0-9]{30,}|sk-ant-[A-Za-z0-9\-_]{20,}|AIza[0-9A-Za-z\-_]{35}|BEGIN (RSA|OPENSSH|EC) PRIVATE KEY)' -EA SilentlyContinue
  if ($leaks) {
    $failures += "Secret leak detected in: $($leaks.Filename -join ', ')"
    Write-Host " FAIL" -ForegroundColor Red
  } else { Write-Host " PASS" -ForegroundColor Green }
} else { Write-Host " PASS (no tracked files yet)" -ForegroundColor Green }

# 7. Level 5 Semantic Gate (deterministic, fail-closed — D-N044 A2)
Write-Host "[7/7] Level 5 Semantic Gate..." -NoNewline
if (-not (Get-Command python3 -ErrorAction SilentlyContinue)) {
  $failures += "python3 absent — Level 5 Semantic Gate not executed"
  Write-Host " FAIL (python3 absent)" -ForegroundColor Red
} else {
  python3 02_Factory/semantic_gate.py
  if ($LASTEXITCODE -ne 0) { $failures += "Level 5 Semantic Gate failed" } else { Write-Host " PASS" -ForegroundColor Green }
}

if ($failures.Count -gt 0) {
  Write-Host "=== GATE RESULT: FAIL ===" -ForegroundColor Red
  $failures | ForEach-Object { Write-Host " - $_" -ForegroundColor Red }
  exit 1
}
Write-Host "=== GATE RESULT: PASS (Ready for Independent Reviewers) ===" -ForegroundColor Green
exit 0
