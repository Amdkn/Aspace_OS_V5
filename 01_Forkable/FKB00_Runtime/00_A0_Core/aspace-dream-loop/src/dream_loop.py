"""Dream loop — Dream-RSI + RRSI over the V5 harness backend (D-N052 R4, H3).

One cycle (``dream_rsi/orchestrate.py``: explore -> learning -> promote):

1. DREAM (explore): :func:`dream_variants.generate_variants` produces the
   candidate policy versions from the compile trace (deterministic variant
   generator — V5 mirror; the fork's proposer is a model agent).
2. LEARNING (replay): every version is replayed on the replay world — the
   frozen trace pool — once per budget preference beta in the measured grid
   (``DRSI_REPLAY_BETA_GRID`` default ``0, 0.25, 0.5, 0.75, 1``). The replay
   objective is Eq. 1 of the paper as implemented in
   ``dream_rsi/learning/heuristic_search/eval.py``: fitness = mean
   per-trace normalised budget<->attainment hypervolume (AUC) minus the
   parallelism penalty (``DRSI_REPLAY_PARALLELISM_PENALTY`` lambda = 0.05).
   The V5 mirror of that objective is implemented below, verbatim where it
   is pure math (:func:`trace_auc` is a line-for-line reimplementation of
   the fork's ``_trace_auc`` — the harness verifies equality against the
   real fork function on the same points).
3. RRSI (evaluate in worktrees): every candidate is drafted in its own
   real git worktree on a branch off ``evolve/v5-traces`` (the fork's
   pattern: "Candidates in git worktrees ... accepting one fast-forwards
   the branch"), screened by the critic, evaluated on the validation split
   by the V5 harness backend, and judged by the REAL ``rrsi/selection.py``
   Algorithm 2 (``select_round``) with the coding-instance parameters
   (``domains/coding/rrsi.json``: delta 0.017, beta0 0.10, beta1 44.5,
   w_s 0.0, w_c 15.0, w_n 0.5).
4. PROMOTE (gate): the R3 gate (``gate_runner`` — real ``gating.py``
   Algorithm 1) decides. Promotion is committed ONLY if the gate accepts;
   a refusal rolls back and nothing is promoted. The evolve branch is
   fast-forwarded to the accepted candidate only (RRSI pattern).

What is V5's here (design §D16, J-4 analogue — documented, never hidden):

* The replay world is the trace pool, not a fork discovery tree: one replay
  world = the whole pool as a single trace with ``n_evaluated`` = 7
  probeable nodes (the 7 traces, in reader order). The fork's per-trace
  AUC would skip 5 of the 7 traces as replay worlds: ``_pareto_summary``
  skips traces with ``n_evaluated < 2`` ("only one probeable node, so
  budget==exhaustive always and the AUC is mathematically forced to 0"),
  and 5 of our traces have a single step. The pool-level replay is the
  faithful single-trace reading of the same code (``evaluate_on_trace``).
* The budget mapping: at budget preference beta the replay evaluates the
  variant on the first ``N(beta) = max(1, ceil(beta * n_pool))`` traces of
  the pool (deterministic order). beta = 0 is the minimal probe (1 trace),
  beta = 1 is exhaustive (all 7). beta is a preference, not a hard cap —
  as in the fork, where beta = 0 still runs the policy.
* The parallel penalty is 1.0: the V5 mirror is serial (one worker), so
  ``effective_sequential_rounds / total_budget`` = 1 at every beta.
* The rollout/grading is the V5 harness backend (``aqua_gate.score_split``),
  not the fork's ``run_gate`` — the fork's runner is built for bench tasks
  (sandbox + model runner). The gate DECISION is the fork's Algorithm 1.

Stdlib only, plus the fork modules passed in by the caller (``sys.path``):
``aqua_gate`` / ``gate_runner`` (R3, in the V5 tree) and ``rrsi.selection``
/ ``rrsi.evaluate`` (fork, read-only). No network, no model call, no write
to the snapshot — the loop only reads traces and writes its own work dirs.
"""

from __future__ import annotations

import json
import math
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from types import SimpleNamespace

import aqua_gate as ag
import gate_runner as gr

# --- Beta, measured on the fork (design §D6) --------------------------------
# DRSI_REPLAY_BETA_GRID default "0.0,0.25,0.5,0.75,1.0":
#   dream_rsi/learning/heuristic_search/eval.py:397 (_parse_beta_grid)
#   README.md, env table: DRSI_REPLAY_BETA_GRID = 0,0.25,0.5,0.75,1
# 0.35 has ZERO occurrences in the whole dream-rsi repo (measured) — it is
# the demo's number, not the module's; it is never used as a value here.
BETA_GRID: tuple[float, ...] = (0.0, 0.25, 0.5, 0.75, 1.0)
PARALLELISM_PENALTY_WEIGHT = 0.05
"""DRSI_REPLAY_PARALLELISM_PENALTY default — eval.py:79."""

# RRSI selection parameters, coding instance (domains/coding/rrsi.json):
# delta 0.017 (3 passes of 178), beta0 0.10, beta1 44.5, w_s 0.0, w_c 15.0,
# w_n 0.5. (Other instances: eng delta 0.020, workspace delta 0.004.)
RRSI_DELTA = 0.017
RRSI_CFG = SimpleNamespace(beta0=0.10, beta1=44.5, w_s=0.0, w_c=15.0, w_n=0.5)


def budget_for_beta(beta: float, n_pool: int) -> int:
    """Probe budget at budget preference beta (V5 mirror mapping)."""
    return max(1, math.ceil(beta * n_pool))


def trace_auc(pts: list[tuple[float, float, float]], ref_budget: float):
    """Normalised budget<->attainment hypervolume for one trace across betas.

    VERBATIM reimplementation of the fork's ``_trace_auc`` —
    ``dream_rsi/learning/heuristic_search/eval.py:469-498`` (same docstring
    sense, same math, same return shape). The harness checks this function
    against the real fork function on identical points; any drift is a
    harness failure, not a silent difference.

    ``pts`` are ``(budget, attainment, beta)`` with attainment in [0, 1].
    We keep the non-dominated frontier (cheapest budget for each attainment
    level) and integrate the area it dominates versus the exhaustive
    reference ``(ref_budget, attain=0)``, normalised to [0, 1]. Reaching
    the ceiling with few probes -> ~1; needing the full exhaustive budget
    (parallel-refine) -> ~0; never scoring -> 0.
    """
    if ref_budget <= 0 or not pts:
        return 0.0, []
    best_by_budget: dict[float, tuple[float, float]] = {}
    for b, a, beta in sorted(pts, key=lambda p: (p[0], -p[1])):
        if b not in best_by_budget or a > best_by_budget[b][0]:
            best_by_budget[b] = (a, beta)
    front: list[tuple[float, float, float]] = []
    amax = -1.0
    for b in sorted(best_by_budget):
        a, beta = best_by_budget[b]
        if a > amax:  # strictly better attainment than anything cheaper
            front.append((b, a, beta))
            amax = a
    hv = 0.0
    prev_a = 0.0
    for b, a, _ in front:
        hv += (a - prev_a) * max(0.0, ref_budget - b)
        prev_a = a
    return hv / ref_budget, [
        {"beta": beta, "total_budget": b, "attain": a} for b, a, beta in front
    ]


def replay_variant(rule: dict, pool: list[dict], trace_by_wid: dict, ref,
                   betas: tuple[float, ...] = BETA_GRID) -> dict:
    """Learning (replay): beta sweep of one variant over the trace pool.

    One replay world = the whole pool (single-trace reading of the fork's
    ``evaluate_on_trace``). At each beta the variant is replayed on the
    first ``N(beta)`` traces; attainment = R over those traces, normalised
    by ``run_best`` = 1.0. Reward = AUC - lambda * parallel_penalty, with
    the serial penalty 1.0 and lambda = 0.05 (the fork's
    ``_pareto_summary`` shape: ``reward = mean_auc - weight *
    mean_penalty``).
    """
    n_pool = len(pool)
    pts: list[tuple[float, float, float]] = []
    grid_rows = []
    for beta in betas:
        n = budget_for_beta(beta, n_pool)
        scored = ag.score_split(pool[:n], trace_by_wid, ref, [rule])
        attain = scored["mean"]  # run_best = 1.0, so attainment = R
        pts.append((float(n), attain, beta))
        grid_rows.append({"beta": beta, "budget": n, "attainment": attain,
                          "n_evaluated": n})
    auc, front = trace_auc(pts, float(n_pool))
    full = ag.score_split(pool, trace_by_wid, ref, [rule])
    reward = round(auc - PARALLELISM_PENALTY_WEIGHT * 1.0, 4)
    return {
        "betas": list(betas),
        "grid": grid_rows,
        "auc": round(auc, 4),
        "front": front,
        "parallel_penalty": 1.0,
        "parallelism_weight": PARALLELISM_PENALTY_WEIGHT,
        "reward": reward,
        "full_pool_R": full["mean"],
    }


def rank_variants(replays: dict[str, dict]) -> list[str]:
    """Dream selection: best version by reward, then full-pool R, then cost.

    Ties keep the incumbent (the fork's discover semantics: "The best
    version, which may be the current policy, explores the next round" —
    README; ``evaluate_incumbent=True`` in ``orchestrate.py``).
    """
    def key(name: str):
        r = replays[name]
        return (-r["reward"], -r["full_pool_R"], r.get("cost", 0),
                0 if name == "incumbent" else 1, name)

    return sorted(replays, key=key)


# --- RRSI worktree evaluation (real selection.py) ----------------------------


def _git(*args: str, cwd: str) -> subprocess.CompletedProcess:
    return subprocess.run(["git", *args], cwd=cwd, capture_output=True,
                          text=True, check=True)


def init_evolve_repo(repo_dir: str) -> str:
    """Scratch evolve repo (RRSI pattern): branch ``evolve/v5-traces``.

    This is NOT the V5 repo — it is the RRSI-side record of the search
    (frontier + edit history), kept in the evidence work dir. The incumbent
    (R3 rule) is the base commit; each candidate gets its own worktree.
    """
    os.makedirs(repo_dir, exist_ok=True)
    if not os.path.isdir(os.path.join(repo_dir, ".git")):
        _git("init", "-b", "main", cwd=repo_dir)
        _git("config", "user.name", "aspace-dream-loop", cwd=repo_dir)
        _git("config", "user.email", "dream-loop@aspace.local", cwd=repo_dir)
        Path(repo_dir, "FRONTIER.md").write_text(
            "# Frontier — RRSI evolve/v5-traces (D-N052 R4)\n\n"
            "Incumbent H0: stale_writer_lock (R3, R=1.0 on T_val).\n",
            encoding="utf-8")
        _git("add", "FRONTIER.md", cwd=repo_dir)
        _git("commit", "-m", "RRSI evolve base: incumbent H0 stale_writer_lock",
             cwd=repo_dir)
        _git("branch", "evolve/v5-traces", cwd=repo_dir)
    return repo_dir


def draft_candidate(repo_dir: str, worktrees_dir: str, name: str,
                    rule: dict) -> dict:
    """Draft one candidate in its own real git worktree (RRSI pattern).

    Branch ``candidate/<name>`` off ``evolve/v5-traces``; the variant file
    is committed there. Returns the worktree path + commit.
    """
    os.makedirs(worktrees_dir, exist_ok=True)
    wt = os.path.join(worktrees_dir, name)
    branch = f"candidate/{name}"
    existing = subprocess.run(
        ["git", "branch", "--list", branch], cwd=repo_dir,
        capture_output=True, text=True).stdout.strip()
    if existing:
        _git("worktree", "remove", "--force", wt, cwd=repo_dir)
        _git("branch", "-D", branch, cwd=repo_dir)
    _git("worktree", "add", "-b", branch, wt, "evolve/v5-traces", cwd=repo_dir)
    Path(wt, f"{name}.json").write_text(
        json.dumps(rule, ensure_ascii=False, indent=2), encoding="utf-8")
    _git("add", f"{name}.json", cwd=wt)
    _git("commit", "-m", f"RRSI candidate {name}", cwd=wt)
    head = _git("rev-parse", "HEAD", cwd=wt).stdout.strip()
    return {"name": name, "worktree": wt, "branch": branch, "commit": head}


def evaluate_in_worktree(candidate: dict, val_traces: list[dict],
                         trace_by_wid: dict, ref) -> dict:
    """Evaluate the candidate AS CHECKED OUT in its worktree.

    The variant is loaded FROM the worktree path (not from memory): the
    worktree is the evaluation input, as in RRSI. S' = R on T_val via the
    V5 harness backend; C' = clause-evaluations (see ``variant_cost``).
    """
    from dream_variants import critic_screen, variant_cost

    path = os.path.join(candidate["worktree"], f"{candidate['name']}.json")
    rule = json.loads(Path(path).read_text(encoding="utf-8"))
    critic_ok, critic_note = critic_screen(rule)
    if not critic_ok:
        return {"name": candidate["name"], "critic_ok": False,
                "critic_note": critic_note, "S": None, "C": None,
                "gate_failure": "critic_reject"}
    scored = ag.score_split(val_traces, trace_by_wid, ref, [rule])
    return {"name": candidate["name"], "critic_ok": True,
            "critic_note": critic_note, "S": scored["mean"],
            "C": variant_cost(rule, len(val_traces)),
            "per_trace": scored["results"]}


def rrsi_select(evaluations: list[dict], incumbent_S: float,
                incumbent_C: int, incumbent_counts: dict) -> dict:
    """Judge every candidate with the REAL ``rrsi/selection.py`` Algorithm 2.

    ``select_round`` is imported from the fork (read-only); the V5 side
    only supplies the measured (S', C') and the coding-instance config.
    Novelty: every candidate is a ``skill`` edit and the incumbent already
    holds an accepted ``skill`` edit, so nu = 0 for all — the within-band
    shaped rule then admits a candidate only for a token saving
    (``w_s = 0`` in the coding instance: never for a within-band score
    gain), exactly as the instance documents.
    """
    from rrsi import selection as sel
    from rrsi.evaluate import EvalResult, TaskResult

    incumbent = EvalResult(job="incumbent", k=1, per_task={}, S=incumbent_S,
                           C=float(incumbent_C), n_expected=0, missing=0)
    cands = []
    for ev in evaluations:
        if ev["S"] is None:
            cand = sel.Candidate(variant=ev["name"], edits=[],
                                 gate_failure=ev.get("gate_failure"))
            cands.append(cand)
            continue
        per_task = {t["task_id"]: TaskResult(rewards=[t["score"]])
                    for t in ev["per_trace"]}
        cand = sel.Candidate(
            variant=ev["name"],
            edits=[{"component": "skill",
                    "hypothesis": f"{ev['name']} diagnoses stale traces"}],
            ev=EvalResult(job=ev["name"], k=1, per_task=per_task,
                          S=ev["S"], C=float(ev["C"]),
                          n_expected=len(per_task), missing=0))
        cands.append(cand)
    winner, decisions = sel.select_round(
        cands, incumbent, incumbent_S, RRSI_DELTA, RRSI_CFG,
        incumbent_counts)
    return {
        "winner": winner.variant if winner is not None else None,
        "decisions": [d.to_json() for d in decisions],
        "delta": RRSI_DELTA,
        "cfg": {"beta0": RRSI_CFG.beta0, "beta1": RRSI_CFG.beta1,
                "w_s": RRSI_CFG.w_s, "w_c": RRSI_CFG.w_c,
                "w_n": RRSI_CFG.w_n},
        "incumbent": {"S": incumbent_S, "C": incumbent_C},
    }


# --- One full cycle ----------------------------------------------------------


def run_dream_cycle(*, snapshot: str, ref: datetime, v5_gate_src: str,
                    evolve_repo: str, worktrees_dir: str, gate_ws: str,
                    gate_order: tuple[str, ...] = (
                        "v-regress", "v-single-clause", "v-tight-1h",
                        "v-loose-7d"),
                    outdir: str) -> dict:
    """One Dream-RSI + RRSI cycle: dream -> replay -> worktrees -> gate.

    ``ref`` is the snapshot instant (temporal truth: observed_at of the
    snapshot, not "now"). ``gate_order`` is the order the gate tries the
    challengers in (regressing first, so the reject + rollback is
    demonstrated before the accept — as in R3). Returns the cycle report.
    """
    sys.path.insert(0, os.path.dirname(__file__))
    from dream_variants import generate_variants

    import aqua_factory_reader  # R0 reader (real)

    traces = aqua_factory_reader.read_traces(snapshot)
    by_wid = {t["aspace_provenance"]["wid"]: t for t in traces}
    by_id = {t["eval_case_id"]: t for t in traces}
    compile_id = "h-p2-3-20261111-1245"
    val_ids = ("smoke-durable-01", "h-p2-6-20261111-1250",
               "h-p2-7-20261111-1255")
    hold_ids = ("smoke-chain-01", "h-p2-11-20261111-1255",
                "h-p2-3-20261111-1255")
    val = [by_id[i] for i in val_ids]
    hold = [by_id[i] for i in hold_ids]

    # 1. DREAM — variants from the compile trace.
    variants = generate_variants(by_id[compile_id], by_wid, ref)

    # 2. LEARNING — beta sweep replay over the pool.
    replays = {}
    for name, rule in variants.items():
        rep = replay_variant(rule, traces, by_wid, ref)
        rep["cost"] = len(rule["clauses"]) * len(traces)
        replays[name] = rep
    ranking = rank_variants(replays)
    dream_selected = ranking[0]

    # 3. RRSI — worktrees + real Algorithm 2 selection.
    init_evolve_repo(evolve_repo)
    candidates = {}
    evaluations = []
    for name in ("v-tight-1h", "v-loose-7d", "v-single-clause", "v-regress"):
        cand = draft_candidate(evolve_repo, worktrees_dir, name,
                               variants[name])
        candidates[name] = cand
        evaluations.append(
            evaluate_in_worktree(cand, val, by_wid, ref))
    incumbent_rep = replays["incumbent"]
    incumbent_eval = ag.score_split(val, by_wid, ref, [variants["incumbent"]])
    from dream_variants import variant_cost
    selection = rrsi_select(
        evaluations, incumbent_eval["mean"],
        variant_cost(variants["incumbent"], len(val)),
        {"skill": 1})

    # 4. GATE — Algorithm 1 on the fresh workspace, in gate_order.
    state = gr.init_workspace(gate_ws)
    baseline = gr.measure_baseline(gate_ws, state, val, by_wid, ref)
    known = variants
    gate_iters = []
    promoted = None
    for k, name in enumerate(gate_order, start=1):
        wiki_before = gr.wiki_pattern_hash(gate_ws)
        it = gr.gate_iteration(gate_ws, state, k, variants[name], val,
                               by_wid, ref, known)
        it["variant"] = name
        it["wiki_conserved"] = gr.wiki_pattern_hash(gate_ws) == wiki_before
        it["active_rules"] = gr.active_rule_names(gate_ws)
        gate_iters.append(it)
        if it["accepted"] and promoted is None:
            promoted = name
            # RRSI pattern: accepting fast-forwards the evolve branch.
            _git("checkout", "evolve/v5-traces", cwd=evolve_repo)
            _git("merge", "--ff-only", candidates[name]["branch"],
                 cwd=evolve_repo)
    hold_base = ag.score_split(hold, by_wid, ref, [])
    hold_promoted = ag.score_split(
        hold, by_wid, ref,
        [variants[promoted]] if promoted else [])

    report = {
        "cycle": "H3-dry-run",
        "snapshot": snapshot,
        "reference_time": ref.isoformat(),
        "n_traces": len(traces),
        "splits": {"compile": compile_id, "validation": list(val_ids),
                   "holdout_v5": list(hold_ids)},
        "variants": sorted(variants),
        "replays": replays,
        "ranking": ranking,
        "dream_selected": dream_selected,
        "candidates": candidates,
        "evaluations": evaluations,
        "rrsi_selection": selection,
        "gate": {
            "baseline_R": baseline["mean"],
            "r_best": state["r_best"],
            "iterations": gate_iters,
            "promoted": promoted,
        },
        "holdout_v5": {"baseline_R": hold_base["mean"],
                       "promoted_R": hold_promoted["mean"]},
    }
    os.makedirs(outdir, exist_ok=True)
    with open(os.path.join(outdir, "cycle-report.json"), "w",
              encoding="utf-8") as fh:
        json.dump(report, fh, indent=2, ensure_ascii=False)
    return report
