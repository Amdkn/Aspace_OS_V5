# 02_Factory/sync-wargame-forks.ps1
$ErrorActionPreference = 'Continue'
Set-Location "C:\Users\amado\Aspace OS V5"

$repos = @(
  @{ Upstream = "autogluon/PathFM";                   Target = "01_Forkable/FKB00_Runtime/02_PredictiveWargame_MachineLearning/PathFM" },
  @{ Upstream = "autogluon/autogluon";                Target = "01_Forkable/FKB00_Runtime/02_PredictiveWargame_MachineLearning/autogluon" },
  @{ Upstream = "garrytan/gbrain";                    Target = "01_Forkable/FKB02_Memory/gbrain" },
  @{ Upstream = "starmynd-org/infinite-brain-os";     Target = "01_Forkable/FKB02_Memory/infinite-brain-os" },
  @{ Upstream = "starmynd-org/infinite-brain-harness"; Target = "01_Forkable/FKB02_Memory/infinite-brain-harness" },
  @{ Upstream = "starmynd-org/powerbi-to-ai-visuals"; Target = "01_Forkable/FKB07_Money_Maker/powerbi-to-ai-visuals" },
  @{ Upstream = "garrytan/gstack";                    Target = "01_Forkable/FKB00_Runtime/03_Governance_Harnesses/gstack" },
  @{ Upstream = "obra/superpowers";                   Target = "01_Forkable/FKB00_Runtime/03_Governance_Harnesses/superpowers" },
  @{ Upstream = "gsd-build/get-shit-done";            Target = "01_Forkable/FKB00_Runtime/03_Governance_Harnesses/get-shit-done" }
)

foreach ($r in $repos) {
  $parts = $r.Upstream.Split('/')
  $org = $parts[0]
  $name = $parts[1]

  Write-Host "[GH FORK] $($r.Upstream) -> Amdkn/$name..." -ForegroundColor Cyan
  gh repo fork $r.Upstream --clone=false 2>$null

  if (-not (Test-Path $r.Target)) {
    # Test if Amdkn fork is reachable
    $remoteUrl = "https://github.com/Amdkn/$name.git"
    $remoteCheck = gh repo view "Amdkn/$name" 2>$null
    if (-not $remoteCheck) {
      $remoteUrl = "https://github.com/$($r.Upstream).git"
    }

    Write-Host "[SUBMODULE] Adding $remoteUrl -> $($r.Target)..." -ForegroundColor Green
    git submodule add --depth 1 $remoteUrl $r.Target
  } else {
    Write-Host "[EXISTS] Target $($r.Target) already exists." -ForegroundColor Yellow
  }
}
Write-Host "Sync complete." -ForegroundColor Green
