# Re-clone les 7 forks upstream non modifies de 01_Forkable (ignores par git). Idempotent.
# Destinations FKB (2026-11-04) : agent-office -> FKB03, api-anything/CLI-Anything/rea -> FKB04,
# needle -> FKB00 inference-locale ; elephant-goldfish-model et MiroFish inchanges.
$ErrorActionPreference = "Stop"
$here = Split-Path -Parent $MyInvocation.MyCommand.Path
$repos = @{
  "agent-office"            = "https://github.com/AgentSystemLabs/agent-office.git"
  "api-anything"            = "https://github.com/goodnight000/api-anything.git"
  "CLI-Anything"            = "https://github.com/HKUDS/CLI-Anything.git"
  "elephant-goldfish-model" = "https://github.com/google/elephant-goldfish-model.git"
  "MiroFish"                = "https://github.com/666ghj/MiroFish.git"
  "needle"                  = "https://github.com/cactus-compute/needle.git"
  "rea"                     = "https://github.com/morluto/rea.git"
}
$paths = @{
  "agent-office" = "FKB03_3DWorlds/agent-office"
  "api-anything" = "FKB04_Tools_Anything/api-anything"
  "CLI-Anything" = "FKB04_Tools_Anything/CLI-Anything"
  "needle"       = "FKB00_Runtime/inference-locale/needle"
  "rea"          = "FKB04_Tools_Anything/rea"
}
foreach ($name in $repos.Keys) {
  $rel = if ($paths.ContainsKey($name)) { $paths[$name] } else { $name }
  $dest = Join-Path $here $rel
  if (Test-Path (Join-Path $dest ".git")) { Write-Host "ok  $name"; continue }
  git clone --depth 1 $repos[$name] $dest
}
