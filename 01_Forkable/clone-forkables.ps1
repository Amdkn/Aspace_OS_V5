# Re-clone tous les 22 forks upstream non modifies de 01_Forkable (ignores par git). Idempotent.
# FKB00: infinity, openrig, needle, moshi, LoRA, GLiNER2.5-multi-Decide, mimi, LFM3-Omni-2B
# FKB02: huashu-motion, take-one, rossark-motion-skill, reanimate, argo, explainroo, video-director, earshot
# FKB03: agent-office
# FKB04: api-anything, CLI-Anything, rea
# Racine: elephant-goldfish-model, MiroFish
$ErrorActionPreference = "Stop"
$env:GIT_LFS_SKIP_SMUDGE = "1"
$here = Split-Path -Parent $MyInvocation.MyCommand.Path

$repos = @{
  "agent-office"            = "https://github.com/AgentSystemLabs/agent-office.git"
  "api-anything"            = "https://github.com/goodnight000/api-anything.git"
  "CLI-Anything"            = "https://github.com/HKUDS/CLI-Anything.git"
  "elephant-goldfish-model" = "https://github.com/google/elephant-goldfish-model.git"
  "infinity"                = "https://github.com/hydro-project/infinity.git"
  "MiroFish"                = "https://github.com/666ghj/MiroFish.git"
  "openrig"                 = "https://github.com/mvschwarz/openrig.git"
  "rea"                     = "https://github.com/morluto/rea.git"
  "needle"                  = "https://github.com/cactus-compute/needle.git"
  "moshi"                   = "https://github.com/kyutai-labs/moshi.git"
  "LoRA"                    = "https://github.com/microsoft/LoRA.git"
  "GLiNER2.5-multi-Decide"  = "https://huggingface.co/fastino/GLiNER2.5-multi-Decide"
  "mimi"                    = "https://huggingface.co/kyutai/mimi"
  "LFM3-Omni-2B"            = "https://huggingface.co/LiquidAI/LFM3-Omni-2B"
  "huashu-motion"           = "https://github.com/alchaincyf/huashu-motion.git"
  "take-one"                = "https://github.com/talsiach/take-one.git"
  "rossark-motion-skill"    = "https://github.com/rossark0/rossark-motion-skill.git"
  "reanimate"               = "https://github.com/NiazMorshed2007/reanimate.git"
  "argo"                    = "https://github.com/shreyaskarnik/argo.git"
  "explainroo"              = "https://github.com/vincentsch/explainroo.git"
  "video-director"          = "https://github.com/win4r/video-director.git"
  "earshot"                 = "https://github.com/Leonxlnx/earshot.git"
}

$paths = @{
  "agent-office"            = "FKB03_3DWorlds/agent-office"
  "api-anything"            = "FKB04_Tools_Anything/api-anything"
  "CLI-Anything"            = "FKB04_Tools_Anything/CLI-Anything"
  "infinity"                = "FKB00_Runtime/infinity"
  "openrig"                 = "FKB00_Runtime/openrig"
  "rea"                     = "FKB04_Tools_Anything/rea"
  "needle"                  = "FKB00_Runtime/inference-locale/needle"
  "moshi"                   = "FKB00_Runtime/inference-locale/moshi"
  "LoRA"                    = "FKB00_Runtime/inference-locale/LoRA"
  "GLiNER2.5-multi-Decide"  = "FKB00_Runtime/inference-locale/GLiNER2.5-multi-Decide"
  "mimi"                    = "FKB00_Runtime/inference-locale/mimi"
  "LFM3-Omni-2B"            = "FKB00_Runtime/inference-locale/LFM3-Omni-2B"
  "huashu-motion"           = "FKB02_Video_SaaS/huashu-motion"
  "take-one"                = "FKB02_Video_SaaS/take-one"
  "rossark-motion-skill"    = "FKB02_Video_SaaS/rossark-motion-skill"
  "reanimate"               = "FKB02_Video_SaaS/reanimate"
  "argo"                    = "FKB02_Video_SaaS/argo"
  "explainroo"              = "FKB02_Video_SaaS/explainroo"
  "video-director"          = "FKB02_Video_SaaS/video-director"
  "earshot"                 = "FKB02_Video_SaaS/earshot"
}

foreach ($name in $repos.Keys) {
  $rel = if ($paths.ContainsKey($name)) { $paths[$name] } else { $name }
  $dest = Join-Path $here $rel
  if (Test-Path (Join-Path $dest ".git")) { Write-Host "ok  $name"; continue }
  git clone --depth 1 $repos[$name] $dest
}
