"""Smoke test for aspace-aqua-adapter (stdlib only).

Builds a temporary SQLite database with the factory schema copied verbatim
from ``02_Factory/factory.ps1`` (lines 42-95, the four tables the adapter
reads), inserts three known workflows — one success, one failure, one with
no steps — runs the adapter over it, and verifies:

* the two traces come out with the right fields and the right verdicts;
* the failure step carries a ``tool_error`` function_response part;
* the step-less workflow is emitted (turns == []), not dropped;
* the database file is NOT modified (sha256 before == after), proving
  read-only access.

Run:  python3 smoke_test.py
"""

from __future__ import annotations

import hashlib
import json
import sqlite3
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))

from aqua_factory_reader import read_traces  # noqa: E402

# Schema copied verbatim from ~/workspace/v5-repo/02_Factory/factory.ps1
# (lines 42-95) — the four tables the adapter reads.
SCHEMA = """
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
"""

T0 = "2026-11-10T15:00:00-05:00"
T1 = "2026-11-10T15:01:00-05:00"
T2 = "2026-11-10T15:02:00-05:00"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _seed(db_path: Path) -> None:
    conn = sqlite3.connect(str(db_path))
    conn.executescript(SCHEMA)
    # Workflow 1 — success, 2 steps, 1 event, 1 ticket (join test).
    conn.execute(
        "INSERT INTO durable_workflows VALUES (?,?,?,?,?,?,?,?,?,?,?)",
        ("wf-ok", "req-smoke-ok", "companion", "ryan", "chain", "completed",
         "freellmapi/auto,claude-sonnet-4-5", "freellmapi/auto", "smoke",
         T0, T1),
    )
    conn.execute(
        "INSERT INTO durable_steps VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
        ("wf-ok", "step-1", 1, "ryan", "python", "Adapter pi", 0,
         "/work/pi", None, "completed", "resume", "Adapter written, smoke 6/6",
         None, 1, T1),
    )
    conn.execute(
        "INSERT INTO durable_steps VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
        ("wf-ok", "step-2", 2, "clara", "python", "Review adapter", 0,
         "/work/pi", None, "completed", "resume", "Approved", None, 1, T1),
    )
    conn.execute(
        "INSERT INTO events (ticket_id, phase, actor, verdict, detail, ts)"
        " VALUES (?,?,?,?,?,?)",
        ("wf-ok", "durable_subagent", "python:ryan", "COMPLETED",
         "Adapter pi", T1),
    )
    conn.execute(
        "INSERT INTO tickets VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)",
        ("wf-ok", "smoke", "thread-1", "Smoke ticket", "Smoke the adapter",
         "open", "low", "python", "/work/pi", "smoke", None, T0, T1),
    )
    # Workflow 2 — failure on the second step (no output, 3 attempts).
    conn.execute(
        "INSERT INTO durable_workflows VALUES (?,?,?,?,?,?,?,?,?,?,?)",
        ("wf-fail", "req-smoke-fail", "companion", "bill", "chain", "failed",
         "freellmapi/auto", "freellmapi/auto", "smoke", T1, T2),
    )
    conn.execute(
        "INSERT INTO durable_steps VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
        ("wf-fail", "step-1", 1, "ryan", "python", "Prepare", 0,
         "/work/pi", None, "completed", "resume", "Prepared", None, 1, T1),
    )
    conn.execute(
        "INSERT INTO durable_steps VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
        ("wf-fail", "step-2", 2, "bill", "python", "Run suite", 0,
         "/work/pi", None, "failed", "resume", "", None, 3, T2),
    )
    conn.execute(
        "INSERT INTO events (ticket_id, phase, actor, verdict, detail, ts)"
        " VALUES (?,?,?,?,?,?)",
        ("wf-fail", "durable_subagent", "python:bill", "FAILED",
         "Run suite", T2),
    )
    # Workflow 3 — no steps at all (edge case: must be emitted, not dropped).
    conn.execute(
        "INSERT INTO durable_workflows VALUES (?,?,?,?,?,?,?,?,?,?,?)",
        ("wf-empty", "req-smoke-empty", "companion", "ryan", "chain",
         "running", "freellmapi/auto", "freellmapi/auto", "smoke", T2, T2),
    )
    conn.commit()
    conn.close()


class TestAquaFactoryReader(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.db = Path(self.tmp.name) / "factory.sqlite"
        _seed(self.db)
        self.hash_before = _sha256(self.db)

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def test_three_traces_in_created_order(self) -> None:
        traces = read_traces(self.db)
        self.assertEqual(len(traces), 3)
        self.assertEqual(
            [t["eval_case_id"] for t in traces],
            ["req-smoke-ok", "req-smoke-fail", "req-smoke-empty"],
        )

    def test_success_workflow_mapping(self) -> None:
        (ok,) = [t for t in read_traces(self.db)
                 if t["eval_case_id"] == "req-smoke-ok"]
        turns = ok["agent_data"]["turns"]
        self.assertEqual(len(turns), 2)
        self.assertEqual(turns[0]["turn_index"], 0)
        self.assertEqual(turns[0]["turn_id"], "wf-ok:step-1")
        self.assertEqual(turns[1]["turn_id"], "wf-ok:step-2")
        # Step 1: user event = task, model event = output, author = agent.
        user_ev, model_ev = turns[0]["events"]
        self.assertEqual(user_ev["author"], "user")
        self.assertEqual(user_ev["content"]["role"], "user")
        self.assertEqual(user_ev["content"]["parts"], [{"text": "Adapter pi"}])
        self.assertEqual(user_ev["event_time"], T1)
        self.assertEqual(model_ev["author"], "ryan")
        self.assertEqual(model_ev["content"]["role"], "model")
        self.assertEqual(model_ev["content"]["parts"],
                         [{"text": "Adapter written, smoke 6/6"}])
        # Agents: one config per distinct step agent.
        self.assertEqual(set(ok["agent_data"]["agents"]), {"ryan", "clara"})
        self.assertIn("python", ok["agent_data"]["agents"]["ryan"]["instruction"])
        # Provenance.
        prov = ok["aspace_provenance"]
        self.assertEqual(prov["wid"], "wf-ok")
        self.assertEqual(prov["verdict"], "success")
        self.assertEqual(prov["status"], "completed")
        self.assertEqual(prov["model_pool"], "freellmapi/auto,claude-sonnet-4-5")
        self.assertEqual(prov["active_model"], "freellmapi/auto")
        self.assertEqual(len(prov["events"]), 1)
        self.assertEqual(prov["events"][0]["verdict"], "COMPLETED")
        self.assertEqual(prov["ticket"]["title"], "Smoke ticket")
        self.assertTrue(all(s["emitted_as_turn"] for s in prov["steps"]))

    def test_failure_workflow_carries_tool_error(self) -> None:
        (fail,) = [t for t in read_traces(self.db)
                   if t["eval_case_id"] == "req-smoke-fail"]
        self.assertEqual(fail["aspace_provenance"]["verdict"], "failure")
        self.assertIsNone(fail["aspace_provenance"]["ticket"])
        turns = fail["agent_data"]["turns"]
        self.assertEqual(len(turns), 2)
        # Failing step: user event (task) + model event with ONLY the
        # function_response part (no output text to carry).
        user_ev, model_ev = turns[1]["events"]
        self.assertEqual(user_ev["content"]["parts"], [{"text": "Run suite"}])
        self.assertEqual(model_ev["author"], "bill")
        (part,) = model_ev["content"]["parts"]
        self.assertEqual(part["function_response"]["name"], "tool_error")
        resp = part["function_response"]["response"]
        self.assertEqual(resp["error"], "failed")
        self.assertEqual(resp["step_key"], "step-2")
        self.assertEqual(resp["agent"], "bill")
        self.assertEqual(resp["attempts"], 3)

    def test_empty_workflow_is_emitted_not_dropped(self) -> None:
        (empty,) = [t for t in read_traces(self.db)
                    if t["eval_case_id"] == "req-smoke-empty"]
        self.assertEqual(empty["agent_data"]["turns"], [])
        self.assertEqual(empty["agent_data"]["agents"], {})
        self.assertEqual(empty["aspace_provenance"]["verdict"], "in_progress")
        self.assertEqual(empty["aspace_provenance"]["events"], [])
        self.assertEqual(empty["aspace_provenance"]["steps"], [])

    def test_database_is_not_modified(self) -> None:
        read_traces(self.db)
        read_traces(self.db)  # twice: idempotent, still read-only
        self.assertEqual(_sha256(self.db), self.hash_before)

    def test_cli_writes_jsonl_and_does_not_touch_the_db(self) -> None:
        out = Path(self.tmp.name) / "traces.jsonl"
        proc = subprocess.run(
            [sys.executable, "src/aqua_factory_reader.py",
             "--db", str(self.db), "--out", str(out)],
            cwd=Path(__file__).resolve().parent,
            capture_output=True, text=True,
        )
        self.assertEqual(proc.returncode, 0, proc.stderr)
        lines = out.read_text(encoding="utf-8").splitlines()
        self.assertEqual(len(lines), 3)
        cases = [json.loads(line) for line in lines]
        self.assertEqual(
            [c["eval_case_id"] for c in cases],
            ["req-smoke-ok", "req-smoke-fail", "req-smoke-empty"],
        )
        self.assertEqual(_sha256(self.db), self.hash_before)


if __name__ == "__main__":
    unittest.main(verbosity=2)
