<#
.SYNOPSIS
    Lance ou vérifie le serveur MCP officiel de mémoire partagée pour Aspace OS V5.
.DESCRIPTION
    Pointe de manière déterministe vers C:\Users\amado\Aspace OS V5\00_Memoire\shared_brain\memory.jsonl
    garantissant qu'aucun harness ne diverge vers un fichier local ou temporaire.
#>
[CmdletBinding()]
param(
    [ValidateSet('status', 'read', 'run', 'test')]
    [string]$Action = 'status',
    [string]$MemoryPath = "C:\Users\amado\Aspace OS V5\00_Memoire\shared_brain\memory.jsonl"
)

$ErrorActionPreference = 'Stop'
Write-Host "=== ASPACE OS V5 — MCP MEMORY GATEWAY (FKB02_Memory) ===" -ForegroundColor Cyan
Write-Host "Target Memory File: $MemoryPath" -ForegroundColor Gray

if (-not (Test-Path $MemoryPath)) {
    Write-Warning "Fichier mémoire introuvable à $MemoryPath. Initialisation..."
    $dir = Split-Path -Parent $MemoryPath
    if (-not (Test-Path $dir)) { New-Item -ItemType Directory -Path $dir -Force | Out-Null }
    Set-Content -Path $MemoryPath -Value '{"type":"entity","name":"Aspace_OS_V5","entityType":"OperatingSystem","observations":["Shared Brain Active"]}' -Encoding UTF8
    Write-Host "[OK] Fichier mémoire initialisé." -ForegroundColor Green
}

$env:MEMORY_FILE_PATH = $MemoryPath

switch ($Action) {
    'status' {
        $lines = (Get-Content $MemoryPath | Measure-Object -Line).Lines
        $size = (Get-Item $MemoryPath).Length
        Write-Host "Status: ACTIF" -ForegroundColor Green
        Write-Host "Taille: $size octets | Entrées: $lines lignes"
    }
    'read' {
        Write-Host "Contenu du Graphe de Connaissances :" -ForegroundColor Yellow
        Get-Content $MemoryPath | ForEach-Object {
            $obj = $_ | ConvertFrom-Json -ErrorAction SilentlyContinue
            if ($obj) {
                if ($obj.type -eq 'entity') {
                    Write-Host "  [ENTITÉ] $($obj.name) ($($obj.entityType)) : $($obj.observations -join '; ')" -ForegroundColor Cyan
                } elseif ($obj.type -eq 'relation') {
                    Write-Host "  [RELATION] $($obj.from) --[$($obj.relationType)]--> $($obj.to)" -ForegroundColor Magenta
                }
            }
        }
    }
    'test' {
        Write-Host "Test de l'exécutable MCP via npx..." -ForegroundColor Yellow
        $result = npx -y @modelcontextprotocol/server-memory --help 2>&1
        if ($LASTEXITCODE -eq 0 -or $result -match "Knowledge Graph") {
            Write-Host "[PASS] Serveur @modelcontextprotocol/server-memory opérationnel." -ForegroundColor Green
        } else {
            Write-Host "[WARN] Sortie: $result" -ForegroundColor Yellow
        }
    }
    'run' {
        Write-Host "Démarrage du serveur stdio..." -ForegroundColor Yellow
        npx -y @modelcontextprotocol/server-memory
    }
}
