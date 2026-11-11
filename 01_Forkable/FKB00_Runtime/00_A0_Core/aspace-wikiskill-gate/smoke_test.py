"""Smoke tests — aspace-wikiskill-gate (D-N052 R3).

Offline, stdlib only (unittest). Two families:

1. Trace gate on SYNTHETIC trace dicts (same shape as the R0 reader emits):
   baseline / reject + rollback / accept + R_best, delta, wiki conserved.
   The synthetic base mirrors the R0 smoke's 3 known workflows (ok / fail /
   empty) plus a lock-blocked one — the mechanics, not the real snapshot,
   are what the smoke proves. The real snapshot is the evidence harness's
   job (run_holdouts_r3.py).
2. Bench backend: procedures from prompt+sandbox only. The tamper test
   proves the no-grader boundary behaviourally: a task whose grader
   ``expected`` is deliberately WRONG still yields the spec-computed
   deliverable (the backend never sees ``expected`` — the fork's
   ``run_task`` never passes the task dict to the runner).

Run: ``python3 smoke_test.py`` from this directory.
"""

from __future__ import annotations

import json
import os
import shutil
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..",
                                "05_Recursive_RSI", "wikiskill"))

from datetime import datetime  # noqa: E402

import aqua_gate as ag  # noqa: E402
import bench_backend as bb  # noqa: E402
import gate_runner as gr  # noqa: E402
from wikiskill import bench, gating, tasks as tm  # noqa: E402

REF = datetime.fromisoformat("2026-11-11T13:21:26-05:00")


def _trace(eval_case_id, status, steps, updated_at):
    return {
        "eval_case_id": eval_case_id,
        "agent_data": {"agents": {}, "turns": []},
        "aspace_provenance": {
            "wid": "wid-" + eval_case_id,
            "mode": "single",
            "status": status,
            "verdict": "in_progress",
            "created_at": updated_at,
            "updated_at": updated_at,
            "steps": steps,
        },
    }


def _step(step_key, status, updated_at, agent="worker"):
    return {"step_key": step_key, "seq": 1, "agent": agent, "harness": "pi",
            "status": status, "writer": 0, "worktree": "/work",
            "hc_address": "", "replay_policy": "safe", "attempts": 1,
            "updated_at": updated_at}


class TestDelta(unittest.TestCase):
    def test_delta_recomputed(self):
        self.assertEqual(ag.delta_min(), 0.0267)
        self.assertEqual(ag.delta_min(900, 0.80), 0.0267)
        # 0.017 (docstring) is NOT the formula's value.
        self.assertNotEqual(ag.delta_min(), 0.017)


class TestTraceGate(unittest.TestCase):
    def setUp(self):
        self.old = datetime.fromisoformat("2026-11-03T17:02:51-05:00")
        self.traces = [
            _trace("ok-1", "running",
                   [_step("step-1", "running", "2026-11-11T13:00:00-05:00")],
                   "2026-11-11T13:00:00-05:00"),
            _trace("stale-1", "running",
                   [_step("step-1", "running", "2026-11-03T17:02:51-05:00")],
                   "2026-11-03T17:02:51-05:00"),
            _trace("locked-1",
                   "waiting for writer lock: C:\\work held by "
                   "wid-stale-1/step-1",
                   [_step("step-1", "waiting for writer lock: C:\\work held by "
                           "wid-stale-1/step-1", "2026-11-11T13:00:00-05:00")],
                   "2026-11-11T13:00:00-05:00"),
        ]
        self.by_wid = {t["aspace_provenance"]["wid"]: t for t in self.traces}
        self.tmp = tempfile.mkdtemp(prefix="wikiskill-gate-smoke-")

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_expected_diagnoses(self):
        got = [ag.expected_diagnosis(t, self.by_wid, REF) for t in self.traces]
        self.assertEqual(got, ["PENDING", "DEFECT_DETECTED", "DEFECT_DETECTED"])

    def test_gate_accept_reject_rollback(self):
        ws = os.path.join(self.tmp, "ws")
        rule = ag.compile_rule_from_trace(self.traces[2], self.by_wid, REF)
        reg = ag.regressing_rule_variant()
        known = {rule["name"]: rule, reg["name"]: reg}
        state = gr.init_workspace(ws)
        val = self.traces
        base = gr.measure_baseline(ws, state, val, self.by_wid, REF)
        self.assertEqual(base["mean"], 0.3333)
        h0 = gr.wiki_pattern_hash(ws)
        r1 = gr.gate_iteration(ws, state, 1, reg, val, self.by_wid, REF, known)
        self.assertFalse(r1["accepted"])
        self.assertEqual(gr.active_rule_names(ws), [])
        self.assertEqual(gr.wiki_pattern_hash(ws), h0)
        r2 = gr.gate_iteration(ws, state, 2, rule, val, self.by_wid, REF, known)
        self.assertTrue(r2["accepted"])
        self.assertEqual(state["r_best"], 1.0)
        self.assertEqual(gr.active_rule_names(ws), ["stale_writer_lock"])


class TestBenchBackend(unittest.TestCase):
    def test_no_grader_access_tampered_expected(self):
        """The executor never sees the grader: tamper expected, output stays spec-computed."""
        ws = tempfile.mkdtemp(prefix="wikiskill-bench-smoke-")
        try:
            from wikiskill import harness
            harness.init_workspace(ws)
            tasks = bench.generate(7)
            tampered = [dict(t) for t in tasks]
            for t in tampered:
                if t["id"] == "csv-north-count":
                    t["grader"] = dict(t["grader"], expected="WRONG")
            tm.save(ws, tampered)
            tm.materialize_all(ws, tampered)
            val = [t for t in tampered if t["split"] == "val"]
            runner = bb.V5BenchRunner()
            g0 = gating.run_gate(ws, val, 0, runner=runner, overwrite=True)
            got = {r["id"]: r["score"] for r in g0["results"]}
            # csv-north-count scores 0.0 against the TAMPERED expected (4 != WRONG)
            # — proving the deliverable was the spec-computed "4", not the grader's.
            self.assertEqual(got["csv-north-count"], 0.0)
            sandbox = tm.sandbox_dir(ws, "csv-north-count")
            with open(os.path.join(sandbox, "answer.txt")) as fh:
                self.assertEqual(fh.read().strip(), "4")
            # Every other val task scores 1.0 against its true expected.
            self.assertEqual(sum(v for k, v in got.items()
                                 if k != "csv-north-count"), 8)
        finally:
            shutil.rmtree(ws, ignore_errors=True)

    def test_unknown_prompt_writes_nothing(self):
        ws = tempfile.mkdtemp(prefix="wikiskill-bench-smoke-")
        try:
            runner = bb.V5BenchRunner()
            res = runner(ws, "Do something unknowable.", tag="iter-00/val/x",
                         workdir=ws)
            self.assertEqual(res["exit_code"], 0)
            self.assertEqual(os.listdir(ws), [".hermes-home"])
        finally:
            shutil.rmtree(ws, ignore_errors=True)


if __name__ == "__main__":
    unittest.main(verbosity=2)
