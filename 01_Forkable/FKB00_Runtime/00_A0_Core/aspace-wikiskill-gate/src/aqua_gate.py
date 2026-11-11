"""AQuA gate — WikiSkill gate over V5 factory traces (D-N052 R3, H2).

Branching of the REAL wikiskill ``gating.py`` (Algorithm 1) onto AQuA traces
(design §D5, §D16):

* Trace source: ``factory.sqlite`` read through the R0 reader
  (``aqua_factory_reader.read_traces`` — EvalCase-shaped dicts).
* Task: given one trace, produce the AQuA diagnosis. The diagnosis vocabulary
  is the demo's (``AquaDiagnostic``: HEALTHY / DEFECT_DETECTED) extended with
  PENDING for a non-terminal trace with no defect signal yet — a trace still
  running is not healthy *evidence*, it is unfinished.
* Expected diagnosis (mechanical, declared here — the adapter defines the
  backend, §D16; every threshold is named so the 13e can judge it):

  - DEFECT_DETECTED when (a) a failure token (fail/error/timeout/abort/crash)
    appears in the workflow or any step status, or (b) the workflow waits for
    a writer lock whose holder step has had no update for more than TTL_STALE,
    or (c) the workflow (or any step) has been ``running`` with no update for
    more than TTL_STALE.
  - HEALTHY when the workflow is terminal-success and every step is success.
  - PENDING otherwise.

  TTL_STALE = 24 h (86 400 s). Robustness, measured on the R3 snapshot: the
  classification is INVARIANT for any threshold in [1 h, 7 d] — the stale
  traces are ~8 days old, the fresh ones minutes old. The exact value inside
  that interval cannot change the result.
* Rule engine: a compiled rule is a list of clauses. With no rule the engine
  returns the default diagnosis (HEALTHY for terminal success, else PENDING):
  no knowledge means no defect detected — the S0 baseline.
* Delta (design §D5): ``delta_min = 2*sqrt(p*(1-p)/N)`` with N = 900,
  p = 0.80 — RECOMPUTED here (0.0267). Provenance, verified: these numbers
  come from the V5 demo code (``a0_recursive_factory.py``,
  ``WikiSkillPlaybookCompiler.__init__``: ``holdout_size=900``,
  ``baseline_p=0.80``). They are NOT in the fork — verified: 0 occurrence of
  ``900``, ``delta`` or ``0.017`` in the fork's ``gating.py``, ``scoring.py``
  and README (Discover §69). The design's phrase "avec le N et le p du fork"
  is inaccurate on this point; the fiche records the correction. The gate
  decision itself is the fork's Algorithm 1 verbatim (``R_val > R_best``);
  the delta is the significance yardstick reported alongside the decision
  (margin vs ``delta_min``), not a second gate.

Stdlib only. No network, no model, no write to the database — the reader is
read-only and the gate only reads the traces it is given.
"""

from __future__ import annotations

import json
import math
import re
from datetime import datetime, timezone

# --- Constants (design §D5, §D17) -------------------------------------------

DELTA_N = 900
"""Holdout size N of the delta formula — from the demo code, not the fork."""

DELTA_P = 0.80
"""Baseline success rate p of the delta formula — from the demo code."""

TTL_STALE_S = 86_400
"""A workflow/step with no update for longer than this is stale (24 h)."""

TTL_ROBUST_LO_S = 3_600
TTL_ROBUST_HI_S = 7 * 86_400
"""Classification is invariant for any TTL inside [1 h, 7 d] on the R3 data."""

FAILURE_TOKENS = ("fail", "error", "timeout", "abort", "crash")
SUCCESS_VALUES = ("completed", "complete", "success", "succeeded", "done", "ok")

LOCK_RE = re.compile(
    r"waiting for writer lock: .* held by (?P<wid>\S+)/step-(?P<step>\S+)",
    re.IGNORECASE,
)


def delta_min(n: int = DELTA_N, p: float = DELTA_P) -> float:
    """Noise floor ``2*sqrt(p*(1-p)/N)`` — 0.0267 for N=900, p=0.80."""
    return round(2.0 * math.sqrt(p * (1.0 - p) / float(n)), 4)


# --- Time --------------------------------------------------------------------


def parse_ts(ts: str | None) -> datetime | None:
    if not ts:
        return None
    try:
        dt = datetime.fromisoformat(ts)
    except ValueError:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt


def age_s(updated_at: str | None, ref: datetime) -> float | None:
    dt = parse_ts(updated_at)
    if dt is None:
        return None
    return (ref - dt).total_seconds()


# --- Expected diagnosis (mechanical) -----------------------------------------


def _has_failure_token(status: str | None) -> bool:
    s = (status or "").strip().lower()
    return any(tok in s for tok in FAILURE_TOKENS)


def _is_success(status: str | None) -> bool:
    return (status or "").strip().lower() in SUCCESS_VALUES


def _lock_holder(trace_by_wid: dict, status: str) -> dict | None:
    """Resolve the writer-lock holder step from the trace set (may be None)."""
    m = LOCK_RE.search(status or "")
    if not m:
        return None
    holder_trace = trace_by_wid.get(m.group("wid"))
    if holder_trace is None:
        return None
    step_key = "step-" + m.group("step")
    for st in holder_trace["aspace_provenance"]["steps"]:
        if st["step_key"] == step_key:
            return st
    return None


def expected_diagnosis(trace: dict, trace_by_wid: dict, ref: datetime,
                       ttl_s: int = TTL_STALE_S) -> str:
    """Mechanical expected diagnosis for one trace (see module docstring)."""
    prov = trace["aspace_provenance"]
    status = prov["status"] or ""
    steps = prov["steps"]

    if _has_failure_token(status) or any(
        _has_failure_token(s["status"]) for s in steps
    ):
        return "DEFECT_DETECTED"

    holder = _lock_holder(trace_by_wid, status)
    if holder is not None:
        holder_age = age_s(holder["updated_at"], ref)
        if holder_age is not None and holder_age > ttl_s:
            return "DEFECT_DETECTED"
        return "PENDING"  # blocked, but the holder is alive: contention, not defect

    for s in steps:
        st_age = age_s(s["updated_at"], ref)
        if (s["status"] or "").strip().lower() == "running" and st_age is not None and st_age > ttl_s:
            return "DEFECT_DETECTED"
    wf_age = age_s(prov["updated_at"], ref)
    if (status.strip().lower() == "running" and wf_age is not None
            and wf_age > ttl_s):
        return "DEFECT_DETECTED"

    if _is_success(status) and steps and all(_is_success(s["status"]) for s in steps):
        return "HEALTHY"
    if _is_success(status) and not steps:
        return "HEALTHY"
    return "PENDING"


# --- Rule engine (the V5 harness backend's rollout+grading) ------------------

# A clause is a dict: {"kind": "lock_holder_stale"|"running_stale", "ttl_s": int}
# A rule is a dict: {"name", "source_trace", "clauses": [...], "skill_md",
#                    "purpose_md", "task_directives": [...]}


def _clause_matches(clause: dict, trace: dict, trace_by_wid: dict,
                    ref: datetime) -> bool:
    prov = trace["aspace_provenance"]
    status = prov["status"] or ""
    ttl = clause.get("ttl_s", TTL_STALE_S)
    if clause["kind"] == "lock_holder_stale":
        holder = _lock_holder(trace_by_wid, status)
        if holder is None:
            return False
        holder_age = age_s(holder["updated_at"], ref)
        return holder_age is not None and holder_age > ttl
    if clause["kind"] == "running_stale":
        for s in prov["steps"]:
            st_age = age_s(s["updated_at"], ref)
            if ((s["status"] or "").strip().lower() == "running"
                    and st_age is not None and st_age > ttl):
                return True
        wf_age = age_s(prov["updated_at"], ref)
        return (status.strip().lower() == "running" and wf_age is not None
                and wf_age > ttl)
    if clause["kind"] == "running_any":
        # Negative control only (regressing variant): any running
        # workflow/step matches, regardless of age.
        if status.strip().lower() == "running":
            return True
        return any((s["status"] or "").strip().lower() == "running"
                   for s in prov["steps"])
    raise ValueError(f"unknown clause kind {clause['kind']!r}")


def diagnose_with_rules(trace: dict, trace_by_wid: dict, ref: datetime,
                        rules: list[dict]) -> str:
    """Rollout: apply the active rules; default when none matches."""
    for rule in rules:
        if any(_clause_matches(c, trace, trace_by_wid, ref)
               for c in rule["clauses"]):
            return "DEFECT_DETECTED"
    prov = trace["aspace_provenance"]
    if _is_success(prov["status"]) and all(
        _is_success(s["status"]) for s in prov["steps"]
    ):
        return "HEALTHY"
    return "PENDING"


def grade_trace(trace: dict, trace_by_wid: dict, ref: datetime,
                rules: list[dict], ttl_s: int = TTL_STALE_S) -> float:
    """Grading: 1.0 when the produced diagnosis equals the expected one."""
    expected = expected_diagnosis(trace, trace_by_wid, ref, ttl_s=ttl_s)
    got = diagnose_with_rules(trace, trace_by_wid, ref, rules)
    return 1.0 if got == expected else 0.0


def score_split(traces: list[dict], trace_by_wid: dict, ref: datetime,
                rules: list[dict]) -> dict:
    """R over a split: mean grade + per-trace detail (fork's mean_score shape)."""
    results = []
    for t in traces:
        expected = expected_diagnosis(t, trace_by_wid, ref)
        got = diagnose_with_rules(t, trace_by_wid, ref, rules)
        results.append({
            "task_id": t["eval_case_id"],
            "expected": expected,
            "got": got,
            "score": 1.0 if got == expected else 0.0,
        })
    scores = [r["score"] for r in results]
    mean = round(sum(scores) / len(scores), 4) if scores else 0.0
    return {"results": results, "mean": mean}


# --- Rule compilation (Note-Taker -> Playbook Writer) -------------------------

def compile_rule_from_trace(trace: dict, trace_by_wid: dict,
                            ref: datetime) -> dict:
    """Compile a rule from a DEFECT trace (the AQuA TRIGGER_WIKISKILL step).

    Note-Taker: extract the failure signature from the trace (status, lock
    holder identity + staleness). Playbook Writer: generalise into clauses —
    the holder-staleness check and the running-staleness check are the same
    invariant (a step with no update for more than TTL_STALE is stale), both
    read off this one trace: the trace names its holder, and the holder IS
    one of the stale Nov-3 steps.
    """
    prov = trace["aspace_provenance"]
    status = prov["status"] or ""
    holder = _lock_holder(trace_by_wid, status)
    holder_age = age_s(holder["updated_at"], ref) if holder else None
    if holder is None:
        raise ValueError(
            f"cannot compile a lock rule from {trace['eval_case_id']}: "
            "no writer-lock holder in the trace status"
        )
    note = {
        "domain": "factory.sqlite / durable workflows",
        "source_task": trace["eval_case_id"],
        "invariant": (
            "A workflow waiting for a writer lock held by a step with no "
            "update for more than TTL_STALE is DEFECT (stale lock holder); "
            "a workflow/step running with no update for more than TTL_STALE "
            "is DEFECT (stale execution)."
        ),
        "aqua_diagnosis": {
            "status": "DEFECT_DETECTED",
            "root_cause": "STALE_WRITER_LOCK",
            "action": "TRIGGER_WIKISKILL_COMPILATION",
        },
        "evidence": {
            "status": status,
            "holder_wid": (LOCK_RE.search(status).group("wid")
                           if LOCK_RE.search(status) else None),
            "holder_step_key": holder["step_key"],
            "holder_status": holder["status"],
            "holder_updated_at": holder["updated_at"],
            "holder_age_s": round(holder_age) if holder_age is not None else None,
            "ttl_stale_s": TTL_STALE_S,
        },
    }
    skill_md = (
        "---\n"
        "name: stale_writer_lock\n"
        "description: Diagnose a factory trace as DEFECT when it waits on a stale writer lock or runs stale.\n"
        "---\n"
        "# Stale writer lock\n"
        "\n"
        "## Rule\n"
        "\n"
        "- A workflow waiting for a writer lock is DEFECT_DETECTED when the "
        "holder step has had no update for more than TTL_STALE (24 h).\n"
        "- A workflow or step `running` with no update for more than "
        "TTL_STALE (24 h) is DEFECT_DETECTED (stale execution).\n"
        "- Otherwise the diagnosis is unchanged (HEALTHY for terminal success,\n"
        "  PENDING for a trace still in progress with no defect signal).\n"
        "\n"
        "## Origin\n"
        "\n"
        f"Compiled from AQuA trace `{trace['eval_case_id']}` — "
        "workflow waiting for a writer lock held by a step last updated "
        f"{holder['updated_at']} (age {round(holder_age)} s at the snapshot).\n"
        "\n"
        "<!-- v5_directives: verify_preconditions, verify_deliverable -->\n"
    )
    purpose_md = (
        "Origin: AQuA trace h-p2-3-20261111-1245 (writer-lock defect).\n"
        "Patterns: stale-writer-lock, stale-running-step.\n"
        f"Evidence: holder {holder['step_key']} age "
        f"{round(holder_age)} s > TTL_STALE {TTL_STALE_S} s.\n"
    )
    return {
        "name": "stale_writer_lock",
        "source_trace": trace["eval_case_id"],
        "clauses": [
            {"kind": "lock_holder_stale", "ttl_s": TTL_STALE_S},
            {"kind": "running_stale", "ttl_s": TTL_STALE_S},
        ],
        "task_directives": ["verify_preconditions", "verify_deliverable"],
        "note": note,
        "skill_md": skill_md,
        "purpose_md": purpose_md,
    }


def regressing_rule_variant() -> dict:
    """Negative control: an over-generalised variant of the same lesson.

    'Running means defect' — compiled by misreading the source trace (the
    trace was running AND defective, so running alone is taken as the defect
    signal). It flags the healthy/in-progress traces too, so R must fall.
    This is the rule the gate must refuse.
    """
    return {
        "name": "running_means_defect",
        "source_trace": "h-p2-3-20261111-1245 (misread)",
        "clauses": [{"kind": "running_any", "ttl_s": 0}],
        "task_directives": [],
        "note": {
            "domain": "factory.sqlite / durable workflows",
            "source_task": "h-p2-3-20261111-1245 (misread)",
            "invariant": "Any running workflow is DEFECT (over-generalised).",
            "aqua_diagnosis": {
                "status": "DEFECT_DETECTED",
                "root_cause": "RUNNING",
                "action": "TRIGGER_WIKISKILL_COMPILATION",
            },
        },
        "skill_md": (
            "---\nname: running_means_defect\ndescription: Diagnose any running workflow as DEFECT.\n---\n"
            "# Running means defect\n\n- Any workflow with status `running` is DEFECT_DETECTED.\n"
        ),
        "purpose_md": "Origin: misread of h-p2-3-20261111-1245.\n",
    }


# --- Structural fixture (no free text) ---------------------------------------


def structural_trace(trace: dict) -> dict:
    """The trace reduced to structural fields (no task/output text).

    What the gate needs (statuses, agents, attempts, timestamps) is kept;
    free text (task, output, labels, event detail) is dropped so the fixture
    can live in the repo without leaking work content.
    """
    prov = trace["aspace_provenance"]
    return {
        "eval_case_id": trace["eval_case_id"],
        "aspace_provenance": {
            "wid": prov["wid"],
            "mode": prov["mode"],
            "status": prov["status"],
            "verdict": prov["verdict"],
            "created_at": prov["created_at"],
            "updated_at": prov["updated_at"],
            "steps": [
                {
                    "step_key": s["step_key"],
                    "seq": s["seq"],
                    "agent": s["agent"],
                    "harness": s["harness"],
                    "status": s["status"],
                    "attempts": s["attempts"],
                    "updated_at": s["updated_at"],
                }
                for s in prov["steps"]
            ],
        },
    }


def load_structural_fixture(path: str) -> list[dict]:
    traces = []
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line:
                traces.append(json.loads(line))
    return traces
