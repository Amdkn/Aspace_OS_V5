# Re-clone tous les 23 forks souverains de 01_Forkable via Amdkn (GitHub) et Amdkn7 (Hugging Face). Idempotent.
# FKB00: infinity, openrig, needle, moshi, LoRA, GLiNER2.5-multi-Decide, mimi, LFM3-Omni-2B
# FKB01: freellmapi
# FKB02: huashu-motion, take-one, rossark-motion-skill, reanimate, argo, explainroo, video-director, earshot
# FKB03: agent-office
# FKB04: api-anything, CLI-Anything, rea
# Racine: elephant-goldfish-model, MiroFish
$ErrorActionPreference = "Stop"
$env:GIT_LFS_SKIP_SMUDGE = "1"
$here = Split-Path -Parent $MyInvocation.MyCommand.Path

$repos = @{
  "agent-office"            = "https://github.com/Amdkn/agent-office.git"
  "api-anything"            = "https://github.com/Amdkn/api-anything.git"
  "CLI-Anything"            = "https://github.com/Amdkn/CLI-Anything.git"
  "elephant-goldfish-model" = "https://github.com/Amdkn/elephant-goldfish-model.git"
  "infinity"                = "https://github.com/Amdkn/infinity.git"
  "MiroFish"                = "https://github.com/Amdkn/MiroFish.git"
  "openrig"                 = "https://github.com/Amdkn/openrig.git"
  "rea"                     = "https://github.com/Amdkn/rea.git"
  "needle"                  = "https://github.com/Amdkn/needle.git"
  "moshi"                   = "https://github.com/Amdkn/moshi.git"
  "LoRA"                    = "https://github.com/Amdkn/LoRA.git"
  "freellmapi"              = "https://github.com/Amdkn/freellmapi.git"
  "GLiNER2.5-multi-Decide"  = "https://huggingface.co/Amdkn7/GLiNER2.5-multi-Decide"
  "mimi"                    = "https://huggingface.co/Amdkn7/mimi"
  "LFM3-Omni-2B"            = "https://huggingface.co/Amdkn7/LFM3-Omni-2B"
  "huashu-motion"           = "https://github.com/Amdkn/huashu-motion.git"
  "take-one"                = "https://github.com/Amdkn/take-one.git"
  "rossark-motion-skill"    = "https://github.com/Amdkn/rossark-motion-skill.git"
  "reanimate"               = "https://github.com/Amdkn/reanimate.git"
  "argo"                    = "https://github.com/Amdkn/argo.git"
  "explainroo"              = "https://github.com/Amdkn/explainroo.git"
  "video-director"          = "https://github.com/Amdkn/video-director.git"
  "earshot"                 = "https://github.com/Amdkn/earshot.git"
}

$paths = @{
  "agent-office"            = "FKB03_3DWorlds/agent-office"
  "api-anything"            = "FKB04_Tools_Anything/api-anything"
  "CLI-Anything"            = "FKB04_Tools_Anything/CLI-Anything"
  "infinity"                = "FKB00_Runtime/infinity"
  "openrig"                 = "FKB00_Runtime/openrig"
  "freellmapi"              = "FKB01_Inference/freellmapi"
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
  if (-not (Test-Path (Join-Path $dest ".git"))) {
    Write-Host "Clonage souverain de $name ($($repos[$name])) vers $rel..."
    New-Item -ItemType Directory -Force -Path $dest | Out-Null
    git clone $repos[$name] $dest
  } else {
    Write-Host "OK (deja clone): $rel"
  }
}
