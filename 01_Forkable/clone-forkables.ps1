# Re-clone les 7 forks upstream non modifies de 01_Forkable (ignores par git). Idempotent.
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
foreach ($name in $repos.Keys) {
  $dest = Join-Path $here $name
  if (Test-Path (Join-Path $dest ".git")) { Write-Host "ok  $name"; continue }
  git clone --depth 1 $repos[$name] $dest
}
