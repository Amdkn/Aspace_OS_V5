# factory/factory.ps1 — Aspace OS V5 Agnostic Software Factory & Durable Subagents Spine
# Fuses DeepSeek Superagent (dsh-superagent-prototype) + Pi Durable (earendil.com/posts/pi-durable) + pi-durable-subagents + ADW
param(
  [Parameter(Position=0)][string]$Command = "status",
  [Parameter(Position=1)][string]$Target = "",
  [string]$Action = "status",
  [string]$Title = "",
  [string]$Mandate = "",
  [string]$Source = "github/cli",
  [string]$Stage = "working/queued",
  [string]$Repo = "",
  [string]$Harness = "dsh",
  [string]$Agent = "worker",
  [string]$Task = "",
  [string]$TasksJson = "",
  [string]$ChainJson = "",
  [string]$Wid = "",
  [string]$To = "",
  [string]$Kind = "steer",
  [string]$Message = "",
  [string]$RequestId = "",
  [string]$Worktree = "",
  [bool]$Writer = $true,
  [int]$Tail = 0,
  [string]$Grep = "",
  [string]$Note = "",
  [string]$Query = ""
)
$ErrorActionPreference = 'Stop'
$root = Split-Path $PSScriptRoot -Parent
$cfg = Get-Content "$PSScriptRoot\config.json" -Raw | ConvertFrom-Json
if (-not $Repo) { $Repo = $cfg.github.default_repo }
if (-not $Worktree) { $Worktree = $root }
$dbPath = "$PSScriptRoot\factory.sqlite"
New-Item -ItemType Directory -Force "$PSScriptRoot\jobs" | Out-Null

# Initialiser le schéma SQLite complet (DeepSeek Superagent + Pi Durable + pi-durable-subagents)
$initSql = @'
import sqlite3, sys
con = sqlite3.connect(sys.argv[1])
con.executescript("""
CREATE TABLE IF NOT EXISTS tickets (
  id TEXT PRIMARY KEY,
  source TEXT,
  thread_id TEXT,
  title TEXT,
  mandate TEXT,
  stage TEXT,
  risk TEXT,
  harness TEXT,
  worktree TEXT,
  branch TEXT,
  pr_url TEXT,
  created_at TEXT,
  updated_at TEXT
);
CREATE TABLE IF NOT EXISTS events (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  ticket_id TEXT,
  phase TEXT,
  actor TEXT,
  verdict TEXT,
  detail TEXT,
  ts TEXT
);
CREATE TABLE IF NOT EXISTS durable_workflows (
  wid TEXT PRIMARY KEY,
  request_id TEXT UNIQUE,
  owner_kind TEXT,
  owner_id TEXT,
  mode TEXT,
  status TEXT,
  model_pool TEXT,
  active_model TEXT,
  labels TEXT,
  created_at TEXT,
  updated_at TEXT
);
CREATE TABLE IF NOT EXISTS durable_steps (
  wid TEXT,
  step_key TEXT,
  seq INTEGER,
  agent TEXT,
  harness TEXT,
  task TEXT,
  writer INTEGER,
  worktree TEXT,
  hc_address TEXT,
  status TEXT,
  replay_policy TEXT,
  output TEXT,
  steers_json TEXT,
  attempts INTEGER,
  updated_at TEXT,
  PRIMARY KEY (wid, step_key)
);
CREATE TABLE IF NOT EXISTS writer_locks (
  worktree TEXT PRIMARY KEY,
  holder_wid TEXT,
  holder_key TEXT,
  acquired_at TEXT
);
CREATE TABLE IF NOT EXISTS durable_docs (
  doc_kind TEXT,
  scope_id TEXT,
  version INTEGER,
  payload_json TEXT,
  updated_at TEXT,
  PRIMARY KEY (doc_kind, scope_id)
);
CREATE TABLE IF NOT EXISTS handoffs (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  conversation_id TEXT,
  note TEXT,
  history_snapshot TEXT,
  ts TEXT
);
""")
con.commit()
con.close()
'@
$initSql | python - $dbPath

switch ($Command) {
  "status" {
    Write-Host "=== ASPACE SOFTWARE FACTORY — MISSION CONTROL (DeepSeek 3-Question Panel + Pi Durable) ===" -ForegroundColor Cyan
    @'
import sqlite3, sys
con = sqlite3.connect(sys.argv[1])
cur = con.cursor()
rows = cur.execute("SELECT id, stage, risk, harness, title, pr_url FROM tickets ORDER BY updated_at DESC").fetchall()
need_human = [r for r in rows if r[1].startswith("person/")]
print(f"1. Does anything need you now?  -> {len(need_human)} ticket(s) in person/* stages")
for r in need_human:
    print(f"   [!] {r[0]} ({r[1]}) : {r[4]} {r[5] or ''}")
print(f"2. Is the factory healthy?      -> {len(rows)} total ticket(s) tracked in factory.sqlite")
for r in rows[:10]:
    print(f"   - {r[0]} | stage={r[1]} | risk={r[2]} | harness={r[3]} | {r[4]}")
wfs = cur.execute("SELECT wid, mode, status, active_model, labels FROM durable_workflows ORDER BY updated_at DESC LIMIT 8").fetchall()
locks = cur.execute("SELECT worktree, holder_wid, holder_key FROM writer_locks").fetchall()
print(f"   Durable Subagent Workflows: {len(wfs)} | Active Writer Locks: {len(locks)}")
for w in wfs:
    print(f"   * {w[0]} [{w[1]}] status={w[2]} model={w[3]} :: {w[4]}")
ev = cur.execute("SELECT ticket_id, phase, verdict, detail, ts FROM events ORDER BY id DESC LIMIT 8").fetchall()
print(f"3. Recent Spine Events ({len(ev)}):")
for e in ev:
    print(f"   [{e[4]}] {e[0]} :: {e[1]} -> {e[2]} ({e[3]})")
'@ | python - $dbPath
  }

  "gate" {
    pwsh -NoProfile -ExecutionPolicy Bypass -File "$PSScriptRoot\checks.ps1"
    exit $LASTEXITCODE
  }

  "setup-github" {
    Write-Host "=== CONFIGURING GITHUB REPOSITORY AS ASPACE SOFTWARE FACTORY: $Repo ===" -ForegroundColor Cyan
    foreach ($lbl in $cfg.github.labels) {
      gh label create $lbl.name --color $lbl.color --description $lbl.description --repo $Repo --force 2>&1 | Out-Null
      Write-Host "  [Label] $($lbl.name) (#$($lbl.color)) synced" -ForegroundColor Green
    }
    gh api -X PUT "repos/$Repo/private-vulnerability-reporting" 2>$null | Out-Null
    gh api -X PUT "repos/$Repo/vulnerability-alerts" 2>$null | Out-Null
    gh api -X PUT "repos/$Repo/automated-security-fixes" 2>$null | Out-Null
    Write-Host "  [Security & Quality] Private vulnerability reporting, Dependabot alerts & automated security fixes enabled on $Repo" -ForegroundColor Green
  }

  "intake" {
    if (-not $Target -and $Title) { $Target = $Title }
    if (-not $Target) { throw "Usage: factory.ps1 intake <issue-number-or-title> [-Mandate <mandate>]" }
    if (-not $Mandate) { $Mandate = $Target }
    $tid = if ($RequestId) { "tkt-" + $RequestId } else { "tkt-" + (Get-Date -Format "yyyyMMdd-HHmmss") }
    $jobDir = "$PSScriptRoot\jobs\$tid"
    New-Item -ItemType Directory -Force $jobDir | Out-Null
    $now = (Get-Date).ToString("o")
    @'
import sqlite3, sys
con = sqlite3.connect(sys.argv[1])
con.execute("INSERT OR IGNORE INTO tickets VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)",
  (sys.argv[2], sys.argv[6], sys.argv[3], sys.argv[3], sys.argv[7], sys.argv[8], "low", sys.argv[4], "", f"factory/{sys.argv[2]}", "", sys.argv[5], sys.argv[5]))
con.execute("INSERT INTO events (ticket_id, phase, actor, verdict, detail, ts) VALUES (?,?,?,?,?,?)",
  (sys.argv[2], "intake", "assessor", "ACCEPT", f"Ticket ensured in jobs/{sys.argv[2]}", sys.argv[5]))
con.commit()
'@ | python - $dbPath $tid $Target $Harness $now $Source $Mandate $Stage
    "# Mandate — $tid`n`n- **Target**: $Target`n- **Mandate**: $Mandate`n- **Harness**: $Harness`n- **Stage**: $Stage`n- **Created**: $now`n" | Set-Content "$jobDir\spec.md" -Encoding utf8
    Write-Host "Ticket $tid ready in factory/jobs/$tid (stage: $Stage, harness: $Harness)" -ForegroundColor Green
  }

  "subagents" {
    if ($Target -and $Action -eq "status") { $Action = $Target }
    $now = (Get-Date).ToString("o")
    switch ($Action) {
      "agents" {
        $agents = Get-ChildItem "$root\.claude\agents" -Filter "*.md" -EA SilentlyContinue | ForEach-Object { $_.BaseName }
        $hcTpls = ((hc templates --json 2>$null | ConvertFrom-Json).templates | ForEach-Object { $_.name })
        [pscustomobject]@{
          factoryAgents = $agents
          hcTemplates = $hcTpls
          harnesses = @("pi", "dsh", "dsh-superagent", "opencode", "claude-code", "codex", "agy")
          modelPool = @("freellmapi/auto", "freellmapi/claude-sonnet-4-5", "freellmapi/qwen3.8-max", "freellmapi/gemini-3.8-flash", "freellmapi/deepseek-v4-flash")
        } | ConvertTo-Json -Depth 5
      }
      "run" {
        if (-not $Task -and $Mandate) { $Task = $Mandate }
        if (-not $Task) { throw "Usage: factory.ps1 subagents -Action run -Agent <name> -Task <task>" }
        $w = if ($Wid) { $Wid } else { "wid-" + (Get-Date -Format "yyyyMMdd-HHmmss") }
        $reqId = if ($RequestId) { $RequestId } else { "req-$w" }
        $wrInt = if ($Writer) { 1 } else { 0 }
        @'
import sqlite3, sys, json
db, wid, req_id, agent, harness, task, writer, wt, now = sys.argv[1:10]
writer = int(writer)
con = sqlite3.connect(db)
cur = con.cursor()
existing = cur.execute("SELECT wid, status FROM durable_workflows WHERE request_id = ?", (req_id,)).fetchone()
if existing:
    print(json.dumps({"wid": existing[0], "status": existing[1], "idempotentReplay": True}))
    sys.exit(0)
lock_holder = cur.execute("SELECT holder_wid, holder_key FROM writer_locks WHERE worktree = ?", (wt,)).fetchone()
step_status = "running"
if writer and lock_holder and lock_holder[0] != wid:
    step_status = f"waiting for writer lock: {wt} held by {lock_holder[0]}/{lock_holder[1]}"
else:
    if writer:
        cur.execute("INSERT OR REPLACE INTO writer_locks VALUES (?,?,?,?)", (wt, wid, "step-1", now))
cur.execute("INSERT INTO durable_workflows VALUES (?,?,?,?,?,?,?,?,?,?,?)",
  (wid, req_id, "conversation", "main", "single", step_status, "freellmapi/auto,claude-sonnet-4-5,qwen3.8-max", "freellmapi/auto", task[:60], now, now))
cur.execute("INSERT INTO durable_steps VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
  (wid, "step-1", 1, agent, harness, task, writer, wt, "", step_status, "safe", "Checkpoint committed before execution.", "[]", 1, now))
cur.execute("INSERT INTO events (ticket_id, phase, actor, verdict, detail, ts) VALUES (?,?,?,?,?,?)",
  (wid, "durable_subagent", f"{harness}:{agent}", step_status.upper(), task[:80], now))
con.commit()
print(json.dumps({"wid": wid, "key": "step-1", "agent": agent, "harness": harness, "status": step_status, "writerLock": bool(writer)}))
'@ | python - $dbPath $w $reqId $Agent $Harness $Task $wrInt $Worktree $now
      }
      "chain" {
        if (-not $ChainJson) { throw "Usage: factory.ps1 subagents -Action chain -ChainJson '[...]'" }
        $w = if ($Wid) { $Wid } else { "wid-" + (Get-Date -Format "yyyyMMdd-HHmmss") }
        $reqId = if ($RequestId) { $RequestId } else { "req-$w" }
        @'
import sqlite3, sys, json
db, wid, req_id, chain_raw, harness, wt, now = sys.argv[1:8]
steps = json.loads(chain_raw)
con = sqlite3.connect(db)
cur = con.cursor()
cur.execute("INSERT OR IGNORE INTO durable_workflows VALUES (?,?,?,?,?,?,?,?,?,?,?)",
  (wid, req_id, "conversation", "main", "chain", "running", "freellmapi/auto,claude-sonnet-4-5,qwen3.8-max", "freellmapi/auto", f"chain({len(steps)} steps)", now, now))
prev_out = "Initial context"
for idx, s in enumerate(steps, 1):
    ag = s.get("agent", "worker")
    tk = s.get("task", "").replace("{previous}", prev_out)
    wr = 1 if s.get("writer", ag not in ["reviewer", "scout", "reviewer-code", "reviewer-security", "reviewer-ux-ui", "reviewer-drift"]) else 0
    key = s.get("key", f"step-{idx}")
    st = "running" if idx == 1 else "queued"
    cur.execute("INSERT OR REPLACE INTO durable_steps VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
      (wid, key, idx, ag, harness, tk, wr, wt, "", st, "safe", f"Checkpoint {key} ready", "[]", 1, now))
    prev_out = f"[Output of {key} ({ag})]"
con.commit()
print(json.dumps({"wid": wid, "mode": "chain", "steps": len(steps), "status": "running"}))
'@ | python - $dbPath $w $reqId $ChainJson $Harness $Worktree $now
      }
      "send" {
        if (-not $To -or -not $Message) { throw "Usage: factory.ps1 subagents -Action send -To <wid/key> -Kind steer|notify -Message <msg>" }
        @'
import sqlite3, sys, json
db, to_ref, kind, msg, now = sys.argv[1:6]
parts = to_ref.split("/", 1)
wid = parts[0]
key = parts[1] if len(parts) > 1 else "step-1"
con = sqlite3.connect(db)
cur = con.cursor()
row = cur.execute("SELECT steers_json FROM durable_steps WHERE wid=? AND step_key=?", (wid, key)).fetchone()
steers = json.loads(row[0]) if row and row[0] else []
if kind == "steer":
    # Latest steer replaces pending unapplied steers (pi-durable-subagents out-of-order steer rule)
    steers = [s for s in steers if s.get("kind") != "steer"]
steers.append({"kind": kind, "message": msg, "ts": now})
cur.execute("UPDATE durable_steps SET steers_json=?, updated_at=? WHERE wid=? AND step_key=?", (json.dumps(steers), now, wid, key))
cur.execute("UPDATE durable_workflows SET updated_at=? WHERE wid=?", (now, wid))
con.commit()
print(json.dumps({"to": f"{wid}/{key}", "kind": kind, "delivered": True, "activeQueueLength": len(steers)}))
'@ | python - $dbPath $To $Kind $Message $now
      }
      "resume" {
        @'
import sqlite3, sys, json
db, wid, now = sys.argv[1:4]
con = sqlite3.connect(db)
cur = con.cursor()
if wid:
    cur.execute("UPDATE durable_workflows SET status='running', updated_at=? WHERE wid=?", (now, wid))
    cur.execute("UPDATE durable_steps SET status='running', updated_at=? WHERE wid=? AND status IN ('paused','interrupted','asking')", (now, wid))
else:
    cur.execute("UPDATE durable_workflows SET status='running', updated_at=? WHERE status IN ('paused','interrupted')", (now,))
con.commit()
rows = cur.execute("SELECT wid, status, labels FROM durable_workflows WHERE status='running'").fetchall()
print(json.dumps({"resumed": [{"wid": r[0], "status": r[1], "labels": r[2]} for r in rows]}))
'@ | python - $dbPath $Wid $now
      }
      "handoff" {
        @'
import sqlite3, sys, json
db, note, now = sys.argv[1:4]
con = sqlite3.connect(db)
cur = con.cursor()
ev = cur.execute("SELECT ticket_id, phase, verdict, detail, ts FROM events ORDER BY id DESC LIMIT 50").fetchall()
cur.execute("INSERT INTO handoffs (conversation_id, note, history_snapshot, ts) VALUES (?,?,?,?)",
  ("root", note, json.dumps(ev), now))
con.commit()
print(json.dumps({"handoff": "committed", "note": note, "archivedEvents": len(ev), "ts": now}))
'@ | python - $dbPath $Note $now
      }
      "search-history" {
        @'
import sqlite3, sys, json
db, q = sys.argv[1:3]
con = sqlite3.connect(db)
cur = con.cursor()
ev = cur.execute("SELECT ticket_id, phase, actor, verdict, detail, ts FROM events WHERE detail LIKE ? OR ticket_id LIKE ? ORDER BY id DESC LIMIT 30", (f"%{q}%", f"%{q}%")).fetchall()
ho = cur.execute("SELECT id, note, ts FROM handoffs WHERE note LIKE ? OR history_snapshot LIKE ? ORDER BY id DESC LIMIT 10", (f"%{q}%", f"%{q}%")).fetchall()
print(json.dumps({"query": q, "events": ev, "handoffs": ho}, indent=2))
'@ | python - $dbPath $Query
      }
      default {
        @'
import sqlite3, sys, json, re
db, wid, tail_n, grep_pat = sys.argv[1], sys.argv[2], int(sys.argv[3]), sys.argv[4]
con = sqlite3.connect(db)
cur = con.cursor()
if wid:
    wf = cur.execute("SELECT wid, mode, status, active_model, labels, updated_at FROM durable_workflows WHERE wid=?", (wid,)).fetchone()
    steps = cur.execute("SELECT step_key, agent, harness, status, writer, worktree, output, steers_json FROM durable_steps WHERE wid=? ORDER BY seq", (wid,)).fetchall()
    out_steps = []
    for s in steps:
        lines = (s[6] or "").splitlines()[-5000:]
        if grep_pat:
            rx = re.compile(grep_pat)
            lines = [ln[:2000] for ln in lines if rx.search(ln[:2000])]
        if tail_n > 0:
            lines = lines[-tail_n:]
        out_steps.append({
            "key": s[0], "agent": s[1], "harness": s[2], "status": s[3],
            "writer": bool(s[4]), "worktree": s[5],
            "output": "\n".join(lines)[:4000],
            "steers": json.loads(s[7] or "[]")
        })
    print(json.dumps({"workflow": wf, "steps": out_steps}, indent=2))
else:
    wfs = cur.execute("SELECT wid, mode, status, active_model, labels, updated_at FROM durable_workflows ORDER BY updated_at DESC LIMIT 15").fetchall()
    locks = cur.execute("SELECT worktree, holder_wid, holder_key, acquired_at FROM writer_locks").fetchall()
    print(json.dumps({
        "workflows": [{"wid": w[0], "mode": w[1], "status": w[2], "model": w[3], "labels": w[4], "updatedAt": w[5]} for w in wfs],
        "writerLocks": [{"worktree": l[0], "holder": f"{l[1]}/{l[2]}", "acquiredAt": l[3]} for l in locks]
    }, indent=2))
'@ | python - $dbPath $Wid $Tail $Grep
      }
    }
  }
}
