# Stop hook: consigne en APPEND-ONLY l'échange (entrée **Auto**) dans log.md et ledger.jsonl.
$ErrorActionPreference = 'SilentlyContinue'
$m = Split-Path $PSScriptRoot -Parent
$log = Join-Path $m 'bundle\log.md'
$ledger = Join-Path $m 'ledger.jsonl'
$in = [Console]::In.ReadToEnd()
try { $h = $in | ConvertFrom-Json } catch { exit 0 }
if ($h.stop_hook_active) { exit 0 }
$tp = $h.transcript_path
if (-not $tp -or -not (Test-Path $tp)) { exit 0 }

$lastUser = $null; $lastAsst = $null
foreach ($line in Get-Content $tp -Tail 400) {
  try { $o = $line | ConvertFrom-Json } catch { continue }
  if ($o.type -eq 'user' -and $o.message.content -is [string]) {
    $t = $o.message.content.Trim()
    if ($t -and -not $t.StartsWith('<')) { $lastUser = $t; $lastAsst = $null }
  } elseif ($o.type -eq 'assistant') {
    $txt = ($o.message.content | Where-Object { $_.type -eq 'text' } | ForEach-Object { $_.text }) -join ' '
    if ($txt.Trim()) { $lastAsst = $txt.Trim() }
  }
}
if (-not $lastUser) { exit 0 }
function Short($s,$n){ $s = ($s -replace '\s+',' ').Trim(); if ($s.Length -gt $n) { $s.Substring(0,$n) + '…' } else { $s } }

$now = Get-Date
$day = $now.ToString('yyyy-MM-dd')
$heading = "## $day"
$existing = Get-Content $log -Raw
$prefix = ''
if ($existing -notmatch [regex]::Escape($heading + "`n") -and $existing -notmatch [regex]::Escape($heading + "`r`n")) { $prefix = "`n$heading`n" }
$entry = "$prefix* **Auto** [$($now.ToString('HH:mm')) session $(Short $h.session_id 8)]: demande = $(Short $lastUser 220) | réponse = $(Short $lastAsst 400)`n"
[IO.File]::AppendAllText($log, $entry, (New-Object Text.UTF8Encoding($false)))

$rec = [ordered]@{ ts = $now.ToString('o'); session = $h.session_id; cwd = $h.cwd; user = (Short $lastUser 1000); assistant = (Short $lastAsst 2000) } | ConvertTo-Json -Compress
[IO.File]::AppendAllText($ledger, $rec + "`n", (New-Object Text.UTF8Encoding($false)))
exit 0
