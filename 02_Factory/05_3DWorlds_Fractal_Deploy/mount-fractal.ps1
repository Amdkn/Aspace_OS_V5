# 02_Factory/mount-fractal.ps1
# Serendipity Fractal V5 - Orchestrateur de Montage Progressif & Mise en Orbite
[CmdletBinding()]
param(
  [ValidateSet("0L", "2L", "4L", "8L", "16L", "20L")]
  [string]$TargetLayer = "8L",
  [switch]$SpinOutCityOffice = $false
)

$ErrorActionPreference = 'Stop'
$root = Resolve-Path (Join-Path $PSScriptRoot "..")
Set-Location $root

Write-Host "=== [SERENDIPITY FRACTAL V5] ACTIVATION COUCHE $TargetLayer ===" -ForegroundColor Cyan

# 1. Purge des dossiers résiduels racine (si présents)
$residuals = @("03_Videaste", "graphify-out", "test-projet")
foreach ($r in $residuals) {
  if (Test-Path $r) {
    Write-Host "[CLEAN] Suppression du dossier résiduel racine : $r" -ForegroundColor Yellow
    git rm -rf --ignore-unmatch $r 2>$null | Out-Null
    if (Test-Path $r) { Remove-Item -Recurse -Force $r }
  }
}

# 2. Option : Création & Préparation Orbite de City-Office (CubeFarm au centre + Agent-Office autour)
if ($SpinOutCityOffice) {
  $cityDir = Join-Path $root "01_Forkable\FKB03_3DWorlds\city-office"
  if (-not (Test-Path $cityDir)) { New-Item -ItemType Directory -Force $cityDir | Out-Null }

  # Configuration Vercel native
  $vercelConfig = @{
    version = 2
    framework = "vite"
    buildCommand = "npm run build"
    outputDirectory = "dist"
  } | ConvertTo-Json -Depth 4
  Set-Content -Path "$cityDir\vercel.json" -Value $vercelConfig -Encoding UTF8

  Write-Host "[ORBIT] Création / vérification du dépôt satellite Amdkn/city-office sur GitHub..." -ForegroundColor Magenta
  gh repo create Amdkn/city-office --public --description "A'Space OS V5 City Office — Fusion of CubeFarm (Central Sanctuary) surrounded by Agent-Office (Ring Road & Autonomous Traffic)" 2>$null
  Write-Host "[OK] Prêt à être déployé sur Vercel et relié en sous-module dans 01_Forkable/FKB03_3DWorlds/city-office." -ForegroundColor Green
}

# 3. Montage progressif des couches fractales (0L -> 2L -> 4L -> 8L -> 16L -> 20L)
$layerOrder = @("0L", "2L", "4L", "8L", "16L", "20L")
$maxIdx = $layerOrder.IndexOf($TargetLayer)

$layerPaths = @{
  "2L"  = @("01_Forkable/FKB02_Memory/servers")
  "4L"  = @("01_Forkable/FKB01_Inference/01_Inference_Locale/GLiNER2.5-multi-Decide", "01_Forkable/FKB01_Inference/01_Inference_Locale/needle")
  "8L"  = @("01_Forkable/FKB03_3DWorlds/cubefarm", "01_Forkable/FKB03_3DWorlds/agent-office", "01_Forkable/FKB03_3DWorlds/city-office", "01_Forkable/FKB07_Money_Maker/03_3D_World/BlenderWorld")
  "16L" = @("01_Forkable/FKB04_Tools_Anything/api-anything", "01_Forkable/FKB06_Video_SaaS/huashu-motion", "01_Forkable/FKB07_Money_Maker/impeccable")
  "20L" = @("01_Forkable/FKB02_Memory/01_BillionContxtLanguage_AutoOnthology/billion-context", "01_Forkable/FKB02_Memory/01_BillionContxtLanguage_AutoOnthology/auto-ontology", "01_Forkable/FKB02_Memory/01_BillionContxtLanguage_AutoOnthology/context-language-models")
}

for ($i = 1; $i -le $maxIdx; $i++) {
  $l = $layerOrder[$i]
  if ($layerPaths.ContainsKey($l)) {
    foreach ($p in $layerPaths[$l]) {
      if (Test-Path $p) {
        Write-Host "[MOUNT $l] Hydratation shallow (--depth 1) de $p..." -ForegroundColor Green
        git submodule update --init --depth 1 -- $p 2>$null
      }
    }
  }
}

Write-Host "[SUCCÈS] Couche $TargetLayer active et opérationnelle." -ForegroundColor Green
