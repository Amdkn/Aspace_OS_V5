# UserPromptSubmit hook: injecte la mémoire V5 dans le contexte à chaque tour.
$ErrorActionPreference = 'SilentlyContinue'
$m = Split-Path $PSScriptRoot -Parent
$b = Join-Path $m 'bundle'
$o = New-Object System.Text.StringBuilder
[void]$o.AppendLine('<memoire-v5 source="00_Memoire/bundle" note="Rappel automatique. Lis-le avant de répondre ; consigne en append-only après ta réponse.">')
[void]$o.AppendLine('## index.md'); [void]$o.AppendLine((Get-Content (Join-Path $b 'index.md') -Raw))
foreach ($f in Get-ChildItem (Join-Path $b 'concepts') -Filter *.md) {
  $raw = Get-Content $f.FullName -Raw
  $body = ($raw -replace '(?s)^---.*?---\s*','')
  if ($body.Length -gt 1800) { $body = $body.Substring(0,1800) + "`n[...tronqué, voir $($f.FullName)]" }
  [void]$o.AppendLine("## concept: $($f.Name)"); [void]$o.AppendLine($body)
}
$log = Join-Path $b 'log.md'
[void]$o.AppendLine('## log.md (60 dernières lignes, append-only)')
[void]$o.AppendLine(((Get-Content $log -Tail 60) -join "`n"))
$g = Join-Path (Split-Path $m -Parent) 'graphify-out\GRAPH_REPORT.md'
if (Test-Path $g) { [void]$o.AppendLine('## graphify GRAPH_REPORT.md (début)'); [void]$o.AppendLine(((Get-Content $g -TotalCount 40) -join "`n")) }
[void]$o.AppendLine('</memoire-v5>')
[Console]::OutputEncoding = [Text.Encoding]::UTF8
Write-Output $o.ToString()
exit 0
