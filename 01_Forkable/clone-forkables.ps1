# Re-clone tous les 29 forks souverains de 01_Forkable via Amdkn (GitHub). Idempotent.
# FKB00: automaton, infinity, openrig
# FKB01 01_Inference_Locale: needle, moshi, LoRA, GLiNER2.5-multi-Decide, mimi, LFM3-Omni-2B
# FKB01 02_Inference_Cooperative: DeepInfer, mesh-llm, cross-platform-llm-client
# FKB01 03_Inference_FreeCloud: freellmapi, codex-chatgpt-web
# FKB02: huashu-motion, take-one, rossark-motion-skill, reanimate, argo, explainroo, video-director, earshot
# FKB03: cubefarm, agent-office
# FKB04: api-anything, CLI-Anything, rea
# Racine: elephant-goldfish-model, MiroFish
$ErrorActionPreference = "Stop"
$env:GIT_LFS_SKIP_SMUDGE = "1"
$here = Split-Path -Parent $MyInvocation.MyCommand.Path

$repos = @{
  "automaton"                 = "https://github.com/Amdkn/automaton.git"
  "cubefarm"                  = "https://github.com/Amdkn/cubefarm.git"
  "codex-chatgpt-web"         = "https://github.com/Amdkn/codex-chatgpt-web.git"
  "agent-office"              = "https://github.com/Amdkn/agent-office.git"
  "api-anything"              = "https://github.com/Amdkn/api-anything.git"
  "CLI-Anything"              = "https://github.com/Amdkn/CLI-Anything.git"
  "elephant-goldfish-model"   = "https://github.com/Amdkn/elephant-goldfish-model.git"
  "infinity"                  = "https://github.com/Amdkn/infinity.git"
  "MiroFish"                  = "https://github.com/Amdkn/MiroFish.git"
  "openrig"                   = "https://github.com/Amdkn/openrig.git"
  "rea"                       = "https://github.com/Amdkn/rea.git"
  "freellmapi"                = "https://github.com/Amdkn/freellmapi.git"
  "needle"                    = "https://github.com/Amdkn/needle.git"
  "moshi"                     = "https://github.com/Amdkn/moshi.git"
  "LoRA"                      = "https://github.com/Amdkn/LoRA.git"
  "GLiNER2.5-multi-Decide"    = "https://github.com/Amdkn/GLiNER2.5-multi-Decide.git"
  "mimi"                      = "https://github.com/Amdkn/mimi.git"
  "LFM3-Omni-2B"              = "https://github.com/Amdkn/LFM3-Omni-2B.git"
  "DeepInfer"                 = "https://github.com/Amdkn/DeepInfer.git"
  "mesh-llm"                  = "https://github.com/Amdkn/mesh-llm.git"
  "cross-platform-llm-client" = "https://github.com/Amdkn/cross-platform-llm-client.git"
  "huashu-motion"             = "https://github.com/Amdkn/huashu-motion.git"
  "take-one"                  = "https://github.com/Amdkn/take-one.git"
  "rossark-motion-skill"      = "https://github.com/Amdkn/rossark-motion-skill.git"
  "reanimate"                 = "https://github.com/Amdkn/reanimate.git"
  "argo"                      = "https://github.com/Amdkn/argo.git"
  "explainroo"                = "https://github.com/Amdkn/explainroo.git"
  "video-director"            = "https://github.com/Amdkn/video-director.git"
  "earshot"                   = "https://github.com/Amdkn/earshot.git"
}

$paths = @{
  "automaton"                 = "FKB00_Runtime/automaton"
  "cubefarm"                  = "FKB03_3DWorlds/cubefarm"
  "codex-chatgpt-web"         = "FKB01_Inference/03_Inference_FreeCloud/codex-chatgpt-web"
  "freellmapi"                = "FKB01_Inference/03_Inference_FreeCloud/freellmapi"
  "agent-office"              = "FKB03_3DWorlds/agent-office"
  "api-anything"              = "FKB04_Tools_Anything/api-anything"
  "CLI-Anything"              = "FKB04_Tools_Anything/CLI-Anything"
  "infinity"                  = "FKB00_Runtime/infinity"
  "openrig"                   = "FKB00_Runtime/openrig"
  "rea"                       = "FKB04_Tools_Anything/rea"
  "needle"                    = "FKB01_Inference/01_Inference_Locale/needle"
  "moshi"                     = "FKB01_Inference/01_Inference_Locale/moshi"
  "LoRA"                      = "FKB01_Inference/01_Inference_Locale/LoRA"
  "GLiNER2.5-multi-Decide"    = "FKB01_Inference/01_Inference_Locale/GLiNER2.5-multi-Decide"
  "mimi"                      = "FKB01_Inference/01_Inference_Locale/mimi"
  "LFM3-Omni-2B"              = "FKB01_Inference/01_Inference_Locale/LFM3-Omni-2B"
  "DeepInfer"                 = "FKB01_Inference/02_Inference_Cooperative/DeepInfer"
  "mesh-llm"                  = "FKB01_Inference/02_Inference_Cooperative/mesh-llm"
  "cross-platform-llm-client" = "FKB01_Inference/02_Inference_Cooperative/cross-platform-llm-client"
  "huashu-motion"             = "FKB02_Video_SaaS/huashu-motion"
  "take-one"                  = "FKB02_Video_SaaS/take-one"
  "rossark-motion-skill"      = "FKB02_Video_SaaS/rossark-motion-skill"
  "reanimate"                 = "FKB02_Video_SaaS/reanimate"
  "argo"                      = "FKB02_Video_SaaS/argo"
  "explainroo"                = "FKB02_Video_SaaS/explainroo"
  "video-director"            = "FKB02_Video_SaaS/video-director"
  "earshot"                   = "FKB02_Video_SaaS/earshot"
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
