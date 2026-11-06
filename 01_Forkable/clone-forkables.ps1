# Re-clone tous les 50 forks souverains de 01_Forkable via Amdkn (GitHub). Idempotent.
# FKB00: automaton, infinity, openrig
# FKB01 01_Inference_Locale: needle, moshi, LoRA, GLiNER2.5-multi-Decide, mimi, LFM3-Omni-2B
# FKB01 02_Inference_Cooperative: DeepInfer, mesh-llm, cross-platform-llm-client
# FKB01 03_Inference_FreeCloud: freellmapi, codex-chatgpt-web, freebuff
# FKB02_Memory: 01_BillionContxtLanguage_AutoOnthology (billion-context, auto-ontology, context-language-models), servers (MCP memory), graphify, dox, knowledge-catalog, llm-wiki
# FKB03: cubefarm, agent-office
# FKB04: api-anything, CLI-Anything, rea
# FKB05: elephant-goldfish-model, MiroFish
# FKB06_Video_SaaS: huashu-motion, take-one, rossark-motion-skill, reanimate, argo, explainroo, video-director, earshot
# FKB07_Money_Maker: impeccable, OpenMontage, DeepTutor, OpenMausBot, text-to-cad, open-notebook, changedetection.io, uptime-kuma
# FKB07 01_Trading: tradingview-indicator-search-mcp-server, TradingView-Unified-MCP, nansen-cli, claude-trading-skills
$ErrorActionPreference = "Stop"
$env:GIT_LFS_SKIP_SMUDGE = "1"
$here = Split-Path -Parent $MyInvocation.MyCommand.Path

$repos = @{
  "automaton"                 = "https://github.com/Amdkn/automaton.git"
  "cubefarm"                  = "https://github.com/Amdkn/cubefarm.git"
  "codex-chatgpt-web"         = "https://github.com/Amdkn/codex-chatgpt-web.git"
  "freebuff"                  = "https://github.com/Amdkn/freebuff.git"
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
  "servers"                   = "https://github.com/Amdkn/servers.git"
  "billion-context"           = "https://github.com/Amdkn/billion-context.git"
  "auto-ontology"             = "https://github.com/Amdkn/auto-ontology.git"
  "context-language-models"   = "https://github.com/Amdkn/context-language-models.git"
  "graphify"                  = "https://github.com/Amdkn/graphify.git"
  "dox"                       = "https://github.com/Amdkn/dox.git"
  "knowledge-catalog"         = "https://github.com/Amdkn/knowledge-catalog.git"
  "llm-wiki"                  = "https://gist.github.com/34a4b4bf6d54b1828ba8c256615619e8.git"
  "huashu-motion"             = "https://github.com/Amdkn/huashu-motion.git"
  "take-one"                  = "https://github.com/Amdkn/take-one.git"
  "rossark-motion-skill"      = "https://github.com/Amdkn/rossark-motion-skill.git"
  "reanimate"                 = "https://github.com/Amdkn/reanimate.git"
  "argo"                      = "https://github.com/Amdkn/argo.git"
  "explainroo"                = "https://github.com/Amdkn/explainroo.git"
  "video-director"            = "https://github.com/Amdkn/video-director.git"
  "earshot"                   = "https://github.com/Amdkn/earshot.git"
  "impeccable"                = "https://github.com/Amdkn/impeccable.git"
  "OpenMontage"               = "https://github.com/Amdkn/OpenMontage.git"
  "DeepTutor"                 = "https://github.com/Amdkn/DeepTutor.git"
  "OpenMausBot"               = "https://github.com/Amdkn/OpenMausBot.git"
  "text-to-cad"               = "https://github.com/Amdkn/text-to-cad.git"
  "open-notebook"             = "https://github.com/Amdkn/open-notebook.git"
  "changedetection.io"        = "https://github.com/Amdkn/changedetection.io.git"
  "uptime-kuma"               = "https://github.com/Amdkn/uptime-kuma.git"
  "tradingview-indicator-search-mcp-server" = "https://github.com/Amdkn/tradingview-indicator-search-mcp-server.git"
  "TradingView-Unified-MCP"                 = "https://github.com/Amdkn/TradingView-Unified-MCP.git"
  "nansen-cli"                              = "https://github.com/nansen-ai/nansen-cli.git"
  "claude-trading-skills"                   = "https://github.com/tradermonty/claude-trading-skills.git"
}

$paths = @{
  "automaton"                 = "FKB00_Runtime/automaton"
  "cubefarm"                  = "FKB03_3DWorlds/cubefarm"
  "codex-chatgpt-web"         = "FKB01_Inference/03_Inference_FreeCloud/codex-chatgpt-web"
  "freebuff"                  = "FKB01_Inference/03_Inference_FreeCloud/freebuff"
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
  "servers"                   = "FKB02_Memory/servers"
  "billion-context"           = "FKB02_Memory/01_BillionContxtLanguage_AutoOnthology/billion-context"
  "auto-ontology"             = "FKB02_Memory/01_BillionContxtLanguage_AutoOnthology/auto-ontology"
  "context-language-models"   = "FKB02_Memory/01_BillionContxtLanguage_AutoOnthology/context-language-models"
  "graphify"                  = "FKB02_Memory/graphify"
  "dox"                       = "FKB02_Memory/dox"
  "knowledge-catalog"         = "FKB02_Memory/knowledge-catalog"
  "llm-wiki"                  = "FKB02_Memory/llm-wiki"
  "huashu-motion"             = "FKB06_Video_SaaS/huashu-motion"
  "take-one"                  = "FKB06_Video_SaaS/take-one"
  "rossark-motion-skill"      = "FKB06_Video_SaaS/rossark-motion-skill"
  "reanimate"                 = "FKB06_Video_SaaS/reanimate"
  "argo"                      = "FKB06_Video_SaaS/argo"
  "explainroo"                = "FKB06_Video_SaaS/explainroo"
  "video-director"            = "FKB06_Video_SaaS/video-director"
  "earshot"                   = "FKB06_Video_SaaS/earshot"
  "impeccable"                = "FKB07_Money_Maker/impeccable"
  "OpenMontage"               = "FKB07_Money_Maker/OpenMontage"
  "DeepTutor"                 = "FKB07_Money_Maker/DeepTutor"
  "OpenMausBot"               = "FKB07_Money_Maker/OpenMausBot"
  "text-to-cad"               = "FKB07_Money_Maker/text-to-cad"
  "open-notebook"             = "FKB07_Money_Maker/open-notebook"
  "changedetection.io"        = "FKB07_Money_Maker/changedetection.io"
  "uptime-kuma"               = "FKB07_Money_Maker/uptime-kuma"
  "tradingview-indicator-search-mcp-server" = "FKB07_Money_Maker/01_Trading/tradingview-indicator-search-mcp-server"
  "TradingView-Unified-MCP"                 = "FKB07_Money_Maker/01_Trading/TradingView-Unified-MCP"
  "nansen-cli"                              = "FKB07_Money_Maker/01_Trading/nansen-cli"
  "claude-trading-skills"                   = "FKB07_Money_Maker/01_Trading/claude-trading-skills"
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
