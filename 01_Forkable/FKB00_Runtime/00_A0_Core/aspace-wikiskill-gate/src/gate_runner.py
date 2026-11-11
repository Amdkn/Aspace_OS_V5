"""Gate runner — drive the REAL wikiskill gating.py over V5 trace-tasks.

Algorithm 1, verbatim from the fork (``gating.py`` docstring + ``harness.evolve``):

    if R(T_val,k) > R_best: accept (S_k <- S'_k, R_best <- R)
    else: reject, roll back skills only; wiki retained.

What is real here (imported from the fork submodule, never re-implemented):
``load_state`` / ``save_state`` (``runs/state.json``), ``ensure_active_repo``,
``commit_base``, ``apply_proposal``, ``rollback``, ``skill_diff``,
``accept_commit``; the wiki helpers (``wiki.ensure`` / ``commit`` /
``append_skill_impact`` / ``append_log``).

What is V5's (design §D16 — the adapter defines the backend): the rollout and
the grading. The fork's ``run_gate``/``run_task`` are built for fork bench
tasks (sandbox materialisation + model runner + ``scoring.grade``); the V5
rollout over AQuA traces is ``run_gate_v5`` below, which mirrors
``run_gate``'s return shape (``{"iter", "results", "mean"}``) but scores each
trace with the V5 harness backend (``aqua_gate.score_split``). The gate
DECISION is the same code path as ``harness.evolve``'s (``accepted =
r_val > prev_best``; ``accept_commit`` else ``rollback``).

One deliberate difference from ``evolve``: no early stop at ``R_best == 1.0``.
H-R4 requires demonstrating BOTH the accept and the reject in sequence on
the same workspace; the early stop would end the loop after the accept. The
loop control is the runner's, not Algorithm 1's — Algorithm 1 itself is
untouched.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import sys
from pathlib import Path

# The fork package lives in the V5 submodule (gitlink 59a6a04). It is added to
# sys.path by the caller (the evidence harness) or resolved relative to this
# file: <v5>/01_Forkable/FKB00_Runtime/05_Recursive_RSI/wikiskill.
_HERE = Path(__file__).resolve()
WIKISKILL_DIR = str(
    _HERE.parents[3] / "05_Recursive_RSI" / "wikiskill"
)
if WIKISKILL_DIR not in sys.path and os.path.isdir(WIKISKILL_DIR):
    sys.path.insert(0, WIKISKILL_DIR)

from wikiskill import gating, wiki  # noqa: E402  (fork, real)
from wikiskill import prompts  # noqa: E402  (fork, real: gate outcome entries)

import aqua_gate  # noqa: E402


# --- V5 validation loop (mirrors gating.run_gate) ----------------------------

def run_gate_v5(trace_tasks, trace_by_wid, ref, rules, it: int) -> dict:
    """Validation rollout over a trace split with the *current* active rules."""
    scored = aqua_gate.score_split(trace_tasks, trace_by_wid, ref, rules)
    return {"iter": it, "results": scored["results"], "mean": scored["mean"]}


def proposal_of(rule: dict) -> dict:
    """A compiled rule as a gating.apply_proposal proposal (action create)."""
    return {
        "action": "create",
        "name": rule["name"],
        "skill_md": rule["skill_md"],
        "purpose_md": rule["purpose_md"],
    }


def active_rule_names(ws: str) -> list[str]:
    d = gating.active_dir(ws)
    if not os.path.isdir(d):
        return []
    return sorted(
        n for n in os.listdir(d)
        if os.path.isdir(os.path.join(d, n)) and not n.startswith(".")
    )


def active_rules(ws: str, known_rules: dict[str, dict]) -> list[dict]:
    """Machine clauses of the currently active skills (by name)."""
    return [known_rules[n] for n in active_rule_names(ws) if n in known_rules]


def skill_directives(ws: str) -> list[str]:
    """v5_directives declared in the active SKILL.md files (bench backend)."""
    found: list[str] = []
    d = gating.active_dir(ws)
    if not os.path.isdir(d):
        return found
    for name in active_rule_names(ws):
        p = os.path.join(d, name, "SKILL.md")
        try:
            text = open(p, encoding="utf-8").read()
        except OSError:
            continue
        m = re.search(r"<!--\s*v5_directives:\s*([^>]*)-->", text)
        if m:
            found.extend(x.strip() for x in m.group(1).split(",") if x.strip())
    return sorted(set(found))


# --- Wiki integrity ----------------------------------------------------------

def wiki_pattern_hash(ws: str) -> str:
    """Hash of the wiki knowledge pages (patterns + index), NOT the audit log.

    The gate outcome entries (log.md / skill-impact.md) legitimately grow on
    every iteration — they are the audit trail. What rollback must conserve
    is the KNOWLEDGE: the pattern pages. That is the fork's "wiki retained".
    """
    h = hashlib.sha256()
    wdir = wiki.wiki_dir(ws)
    for rel in sorted(["index.md"] + [
        os.path.join("patterns", f)
        for f in sorted(os.listdir(os.path.join(wdir, "patterns")))
        if os.path.isfile(os.path.join(wdir, "patterns", f))
    ]):
        p = os.path.join(wdir, rel)
        if os.path.isfile(p):
            h.update(rel.encode())
            h.update(open(p, "rb").read())
    return h.hexdigest()


# --- Gate iteration (Algorithm 1) --------------------------------------------

def gate_iteration(ws: str, state: dict, k: int, rule: dict,
                   trace_tasks, trace_by_wid, ref,
                   known_rules: dict[str, dict]) -> dict:
    """One Algorithm 1 iteration: apply the proposal, gate it, accept or roll back."""
    prev_best = state["r_best"]
    gating.commit_base(ws, k)
    desc = gating.apply_proposal(ws, proposal_of(rule))
    diff = gating.skill_diff(ws)
    rules = active_rules(ws, known_rules)
    gate = run_gate_v5(trace_tasks, trace_by_wid, ref, rules, k)
    r_val = gate["mean"]
    accepted = r_val > prev_best
    if accepted:
        gating.accept_commit(ws, k, r_val)
        state["r_best"] = r_val
    else:
        gating.rollback(ws)
    delta = aqua_gate.delta_min()
    state["history"].append({
        "iter": k,
        "r_val": r_val,
        "prev_best": prev_best,
        "accepted": accepted,
        "proposal": desc,
        "delta_min": delta,
        "margin": round(r_val - prev_best, 4),
        "margin_ge_delta": round(r_val - prev_best, 4) >= delta,
    })
    state["next_iter"] = k + 1
    gating.save_state(ws, state)
    wiki.append_skill_impact(
        ws, prompts.gate_outcome_entry(ws, k, proposal_of(rule), r_val,
                                       accepted, diff, prev_best))
    wiki.append_log(
        ws, f"iter-{k:02d}: R_val={r_val} "
            f"{'ACCEPT' if accepted else 'reject'} (R_best={state['r_best']})")
    wiki.commit(ws, f"iter-{k:02d}: gate outcome "
                    f"({'accept' if accepted else 'reject'}, R_val={r_val})")
    return {"iter": k, "r_val": r_val, "prev_best": prev_best,
            "accepted": accepted, "gate": gate, "delta_min": delta,
            "margin": round(r_val - prev_best, 4)}


def init_workspace(ws: str) -> dict:
    """Fresh gate workspace: wiki skeleton + empty skill git repo + state."""
    os.makedirs(ws, exist_ok=True)
    wiki.ensure(ws)
    gating.ensure_active_repo(ws)
    state = gating.load_state(ws)
    gating.save_state(ws, state)
    return state


def measure_baseline(ws: str, state: dict, trace_tasks, trace_by_wid,
                     ref) -> dict:
    """Baseline validation with S0 = empty skill set (state r_best = baseline)."""
    gate0 = run_gate_v5(trace_tasks, trace_by_wid, ref, [], 0)
    state["baseline"] = gate0["mean"]
    state["r_best"] = gate0["mean"]
    wiki.append_log(
        ws, f"iter-00 baseline: R={gate0['mean']} "
             f"(S0=empty, {len(trace_tasks)} val traces)")
    gating.save_state(ws, state)
    return gate0
