<#
.SYNOPSIS
    A'Space OS V5 — Orchestrateur de Forks Souverains & Sous-Modules Mutants A0
    Forke automatiquement chaque dépôt de la matrice vers `https://github.com/Amdkn/<repo>`,
    l'attache au bon pôle dans `01_Forkable/`, configure `upstream` et crée la branche `aspace-v5-native`.
#>
param(
    [string]$GithubOwner = "Amdkn",
    [switch]$DryRun
)

$ErrorActionPreference = "Stop"

$SubmoduleMatrix = @(
    # --- PÔLE 00 : NOYAU SOUVERAIN A0 & MICRO-NOYAU CORDIS ---
    @{ Upstream = "agent0ai/agent-zero";          Target = "01_Forkable/FKB00_Runtime/00_A0_Core/agent-zero" },
    @{ Upstream = "agent0ai/a0-plugins";          Target = "01_Forkable/FKB00_Runtime/00_A0_Core/a0-plugins" },
    @{ Upstream = "agent0ai/spynel";              Target = "01_Forkable/FKB00_Runtime/00_A0_Core/spynel" },
    @{ Upstream = "agent0ai/tuxee";               Target = "01_Forkable/FKB00_Runtime/00_A0_Core/tuxee" },
    @{ Upstream = "cordiverse/cordis";            Target = "01_Forkable/FKB00_Runtime/00_A0_Core/cordis" },
    @{ Upstream = "deepseek-ai/deepseek-harness"; Target = "01_Forkable/FKB00_Runtime/00_A0_Core/deepseek-harness" },
    @{ Upstream = "earendil-works/pi";            Target = "01_Forkable/FKB00_Runtime/00_A0_Core/pi" },

    # --- PÔLE 03_3DWORLDS : PONT SPATIAL AGENT ZERO ---
    @{ Upstream = "agent0ai/space-agent";         Target = "01_Forkable/FKB03_3DWorlds/space-agent" },

    # --- PÔLE 04 : COCKPIT ADE (HERDR × ORCA × T3CODE) & HARNESSES UNIVERSELS ---
    @{ Upstream = "herdrdev/herdr";               Target = "01_Forkable/FKB00_Runtime/04_ADE_OpenRig/herdr" },
    @{ Upstream = "herdrdev/herdr-core";          Target = "01_Forkable/FKB00_Runtime/04_ADE_OpenRig/herdr-core" },
    @{ Upstream = "herdrdev/herdr-app";           Target = "01_Forkable/FKB00_Runtime/04_ADE_OpenRig/herdr-app" },
    @{ Upstream = "stablyai/orca";                Target = "01_Forkable/FKB00_Runtime/04_ADE_OpenRig/orca" },
    @{ Upstream = "pingdotgg/t3code";             Target = "01_Forkable/FKB00_Runtime/04_ADE_OpenRig/t3code" },
    @{ Upstream = "openclaw/openclaw";            Target = "01_Forkable/FKB00_Runtime/04_ADE_OpenRig/openclaw" },
    @{ Upstream = "anthropics/claude-code";       Target = "01_Forkable/FKB00_Runtime/04_ADE_OpenRig/claude-code" },
    @{ Upstream = "openai/codex";                 Target = "01_Forkable/FKB00_Runtime/04_ADE_OpenRig/codex" },
    @{ Upstream = "nousresearch/hermes-agent";    Target = "01_Forkable/FKB00_Runtime/04_ADE_OpenRig/hermes-agent" },

    # --- PÔLE 05 : MOTEURS DE RÉCURSIVITÉ & AUTO-AMÉLIORATION (3 HORIZONS) ---
    @{ Upstream = "PrimeIntellect-ai/prime-agent"; Target = "01_Forkable/FKB00_Runtime/05_Recursive_RSI/prime-agent" },
    @{ Upstream = "ashutoshsinghpr7/wikiskill";    Target = "01_Forkable/FKB00_Runtime/05_Recursive_RSI/wikiskill" },
    @{ Upstream = "google/adk-recipes";            Target = "01_Forkable/FKB00_Runtime/05_Recursive_RSI/adk-recipes" },
    @{ Upstream = "google-research/rrsi";          Target = "01_Forkable/FKB00_Runtime/05_Recursive_RSI/rrsi" },
    @{ Upstream = "google-research/dream-rsi";     Target = "01_Forkable/FKB00_Runtime/05_Recursive_RSI/dream-rsi" }
)

foreach ($item in $SubmoduleMatrix) {
    $upstream = $item.Upstream
    $repoName = ($upstream -split "/")[1]
    $forkUrl  = "https://github.com/$GithubOwner/$repoName.git"
    $target   = $item.Target

    Write-Host "[A0-FACTORY] Synchronisation de $upstream -> $forkUrl ($target)" -ForegroundColor Cyan
    if ($DryRun) { continue }

    gh api -X POST "repos/$upstream/forks" 2>$null | Out-Null

    if (-not (Test-Path $target)) {
        git submodule add --force $forkUrl $target
    }
}

Write-Host "[A0-FACTORY] Matrice de 22 sous-modules A0 synchronisée." -ForegroundColor Green
