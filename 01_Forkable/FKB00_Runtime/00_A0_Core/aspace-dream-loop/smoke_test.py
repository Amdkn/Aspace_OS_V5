"""Smoke tests — aspace-dream-loop (D-N052 R4). Offline, stdlib only.

Uses the R3 structural fixture (no live snapshot, no text) to check the
loop's mechanics: variant generation, beta-sweep replay math, Dream
ranking, critic screen, RRSI Algorithm 2 (real selection.py) and the gate
accept/reject/rollback on the fixture traces.

Usage: python3 smoke_test.py [--v5 <clone>] [--rrsi <rrsi-repo>]
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import tempfile
from datetime import datetime

_HERE = os.path.dirname(os.path.abspath(__file__))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--v5", default=os.path.join(
        os.environ.get("HOME", "~"), "workspace", "v5-r4"))
    ap.add_argument("--rrsi", default=os.path.join(
        os.environ.get("HOME", "~"), "workspace", "rrsi-repo"))
    ap.add_argument("--dream-rsi", default=os.path.join(
        os.environ.get("HOME", "~"), "workspace", "dream-rsi-repo"))
    args = ap.parse_args()

    gate_src = os.path.join(args.v5, "01_Forkable", "FKB00_Runtime",
                            "00_A0_Core", "aspace-wikiskill-gate", "src")
    wikiskill_dir = os.path.join(
        args.v5, "01_Forkable", "FKB00_Runtime", "05_Recursive_RSI",
        "wikiskill")
    sys.path.insert(0, gate_src)
    sys.path.insert(0, wikiskill_dir)
    sys.path.insert(0, os.path.join(_HERE, "src"))
    sys.path.insert(0, args.rrsi)

    import aqua_gate as ag
    import gate_runner as gr
    from dream_loop import BETA_GRID, replay_variant, rank_variants, trace_auc
    from dream_variants import critic_screen, generate_variants, variant_cost

    ref = datetime.fromisoformat("2026-11-11T14:08:28-05:00")
    fixture_path = os.path.join(os.path.dirname(gate_src), "fixtures",
                                "traces-v5-structural.jsonl")
    traces = ag.load_structural_fixture(fixture_path)
    by_wid = {t["aspace_provenance"]["wid"]: t for t in traces}
    by_id = {t["eval_case_id"]: t for t in traces}
    val_ids = ("smoke-durable-01", "h-p2-6-20261111-1250",
               "h-p2-7-20261111-1255")
    val = [by_id[i] for i in val_ids]

    ok = 0
    total = 0

    def check(name, cond, detail=""):
        nonlocal ok, total
        total += 1
        ok += bool(cond)
        print(f"[{'PASS' if cond else 'FAIL'}] {name}: {detail}")

    # 1. Variants.
    variants = generate_variants(by_id["h-p2-3-20261111-1245"], by_wid, ref)
    check("variants", set(variants) == {"incumbent", "v-tight-1h", "v-loose-7d",
                                         "v-single-clause", "v-regress"},
          f"{len(variants)} variants from the compile trace")

    # 2. Beta grid is the measured one.
    check("beta-grid", BETA_GRID == (0.0, 0.25, 0.5, 0.75, 1.0),
          f"grid {list(BETA_GRID)} (0.35 absent by construction)")

    # 3. Replay math equals the fork's real _trace_auc on the same points.
    sys.path.insert(0, args.dream_rsi)
    from dream_rsi.learning.heuristic_search import eval as fork_eval
    pts = [(1.0, 1.0, 0.0), (2.0, 0.5, 0.25), (4.0, 0.75, 0.5),
           (6.0, 0.6667, 0.75), (7.0, 0.7143, 1.0)]
    mine = trace_auc(pts, 7.0)
    real = fork_eval._trace_auc(pts, 7.0)
    check("replay-math-equals-fork", mine == real,
          f"mirror AUC {mine[0]:.4f} == fork AUC {real[0]:.4f}")

    # 4. Replay + ranking: incumbent kept on the tie (TTL-invariant regime).
    replays = {}
    for name, rule in variants.items():
        rep = replay_variant(rule, traces, by_wid, ref)
        rep["cost"] = len(rule["clauses"]) * len(traces)
        replays[name] = rep
    ranking = rank_variants(replays)
    check("dream-keeps-incumbent-on-tie", ranking[0] == "incumbent",
          f"ranking {ranking}; top reward "
          f"{replays[ranking[0]]['reward']}")
    check("regress-auc-ties-incumbent",
          replays["v-regress"]["reward"] == replays["incumbent"]["reward"]
          and replays["v-regress"]["full_pool_R"] <
          replays["incumbent"]["full_pool_R"],
          f"regress reward {replays['v-regress']['reward']} == incumbent "
          f"{replays['incumbent']['reward']} (AUC ceiling: reaching 1.0 on "
          f"the first probe maxes the frontier) but full-pool R "
          f"{replays['v-regress']['full_pool_R']} < "
          f"{replays['incumbent']['full_pool_R']} — the AUC does not "
          f"separate them, R does (measured limit, fiche §5)")

    # 5. Critic screen passes the generic variants.
    check("critic", all(critic_screen(r)[0] for r in variants.values()),
          "no trace literal in any clause set")

    # 6. RRSI selection (real): no winner at the ceiling (S* = 1.0).
    from dream_loop import rrsi_select
    from dream_variants import variant_cost as vc
    evals = []
    for name in ("v-tight-1h", "v-loose-7d", "v-single-clause", "v-regress"):
        s = ag.score_split(val, by_wid, ref, [variants[name]])
        evals.append({"name": name, "S": s["mean"],
                      "C": vc(variants[name], len(val)),
                      "per_trace": s["results"]})
    inc = ag.score_split(val, by_wid, ref, [variants["incumbent"]])
    sel = rrsi_select(evals, inc["mean"], vc(variants["incumbent"], len(val)),
                      {"skill": 1})
    check("rrsi-selection-ran", sel["winner"] is None and
          len(sel["decisions"]) == 4,
          f"winner={sel['winner']} (ceiling: incumbent S*=1.0); "
          f"decisions={[d['reason'][:40] for d in sel['decisions']]}")

    # 7. Gate on the fixture: reject regress, single, tight; accept loose.
    with tempfile.TemporaryDirectory() as td:
        ws = os.path.join(td, "ws")
        state = gr.init_workspace(ws)
        base = gr.measure_baseline(ws, state, val, by_wid, ref)
        r1 = gr.gate_iteration(ws, state, 1, variants["v-regress"], val,
                               by_wid, ref, variants)
        r2 = gr.gate_iteration(ws, state, 2, variants["v-single-clause"],
                               val, by_wid, ref, variants)
        r3 = gr.gate_iteration(ws, state, 3, variants["v-tight-1h"], val,
                               by_wid, ref, variants)
        r4 = gr.gate_iteration(ws, state, 4, variants["v-loose-7d"], val,
                               by_wid, ref, variants)
        check("gate-reject-then-accept",
              base["mean"] == 0.6667 and not r1["accepted"]
              and r1["r_val"] == 0.3333 and not r2["accepted"]
              and r2["r_val"] == 0.6667 and not r3["accepted"]
              and r3["r_val"] == 0.3333 and r4["accepted"]
              and r4["r_val"] == 1.0 and state["r_best"] == 1.0
              and gr.active_rule_names(ws) == ["v-loose-7d"],
              f"baseline {base['mean']}, regress {r1['r_val']} rejected, "
              f"single {r2['r_val']} rejected, tight {r3['r_val']} "
              f"rejected (TTL 1h expired at this ref), loose "
              f"{r4['r_val']} accepted, R_best {state['r_best']}")

    print(f"smoke: {ok}/{total} checks PASS")
    return 0 if ok == total else 1


if __name__ == "__main__":
    raise SystemExit(main())
