# Re-clone les 9 forks upstream non modifies de 01_Forkable (ignores par git). Idempotent.
# Destinations FKB : agent-office -> FKB03, api-anything/CLI-Anything/rea -> FKB04,
# infinity/openrig/needle -> FKB00 Runtime & inference-locale ; elephant-goldfish-model et MiroFish inchanges.
$ErrorActionPreference = "Stop"
$here = Split-Path -Parent $MyInvocation.MyCommand.Path
$repos = @{
  "agent-office"            = "https://github.com/AgentSystemLabs/agent-office.git"
  "api-anything"            = "https://github.com/goodnight000/api-anything.git"
  "CLI-Anything"            = "https://github.com/HKUDS/CLI-Anything.git"
  "elephant-goldfish-model" = "https://github.com/google/elephant-goldfish-model.git"
  "infinity"                = "https://github.com/hydro-project/infinity.git"
  "MiroFish"                = "https://github.com/666ghj/MiroFish.git"
  "needle"                  = "https://github.com/cactus-compute/needle.git"
  "openrig"                 = "https://github.com/mvschwarz/openrig.git"
  "rea"                     = "https://github.com/morluto/rea.git"
}
$paths = @{
  "agent-office" = "FKB03_3DWorlds/agent-office"
  "api-anything" = "FKB04_Tools_Anything/api-anything"
  "CLI-Anything" = "FKB04_Tools_Anything/CLI-Anything"
  "infinity"     = "FKB00_Runtime/infinity"
  "needle"       = "FKB00_Runtime/inference-locale/needle"
  "openrig"      = "FKB00_Runtime/openrig"
  "rea"          = "FKB04_Tools_Anything/rea"
}
foreach ($name in $repos.Keys) {
  $rel = if ($paths.ContainsKey($name)) { $paths[$name] } else { $name }
  $dest = Join-Path $here $rel
  if (Test-Path (Join-Path $dest ".git")) { Write-Host "ok  $name"; continue }
  git clone --depth 1 $repos[$name] $dest
}
