"""Run transparent persistence/oracle smoke comparisons; not a JEPA result."""
from __future__ import annotations

import json
from ..env.toy_world import ToyWorldEnv, generate_layout
from ..env.renderer import render_rgb
from ..baselines.persistence import predict as persistence_predict
from ..baselines.symbolic_oracle import predict as symbolic_predict
from .metrics import pixel_metrics, state_metrics
from .replay import verify_replay

SEEDS=(0,1,42,99)
ACTIONS=("MOVE_N","MOVE_E","MOVE_S","MOVE_W","NOOP","INTERACT","MOVE_N","MOVE_E","MOVE_S","MOVE_W")
HORIZONS=(1,3,5,10)


def run_smoke() -> dict:
    rows=[]
    for seed in SEEDS:
        layout=generate_layout(seed)
        env=ToyWorldEnv(layout)
        initial_frame,_=env.reset(seed=seed)
        initial_state=env._evaluator_snapshot()
        actual_frames=[initial_frame]
        actual_states=[initial_state]
        for action in ACTIONS:
            frame,_,terminated,_,_=env.step(action)
            actual_frames.append(frame)
            actual_states.append(env._evaluator_snapshot())
            if terminated:
                break
        if len(actual_states)<=max(HORIZONS):
            raise AssertionError("smoke action sequence terminated before H10")
        if not verify_replay(layout,seed,list(ACTIONS)):
            raise AssertionError("independent replay mismatch")
        for horizon in HORIZONS:
            predicted_state=symbolic_predict(initial_state,layout,list(ACTIONS[:horizon]))
            predicted_frame=render_rgb(predicted_state,layout)
            oracle_state=state_metrics(predicted_state,actual_states[horizon])
            oracle_pixels=pixel_metrics(predicted_frame,actual_frames[horizon])
            persistence_pixels=pixel_metrics(persistence_predict(initial_frame,horizon),actual_frames[horizon])
            rows.append({
                "seed":seed,"layout_id":layout["layout_id"],"horizon":horizon,
                "oracle_state":oracle_state,"oracle_pixel":oracle_pixels,
                "persistence_pixel":persistence_pixels
            })
            if not oracle_state["full_dynamic_state_exact"] or not oracle_pixels["exact_image_match"]:
                raise AssertionError(f"symbolic oracle failed at seed={seed}, horizon={horizon}")
    return {
        "report_version":"toy-world.baseline-smoke.v1",
        "scope":"four seeded layouts; fixed ten-action trace; smoke test only, not benchmark leaderboard data",
        "episodes":len(SEEDS),
        "evaluations":len(rows),
        "oracle_state_exact_rate":sum(r["oracle_state"]["full_dynamic_state_exact"] for r in rows)/len(rows),
        "oracle_pixel_exact_rate":sum(r["oracle_pixel"]["exact_image_match"] for r in rows)/len(rows),
        "persistence_mean_pixel_mae":sum(r["persistence_pixel"]["mean_absolute_error"] for r in rows)/len(rows),
        "rows":rows
    }


if __name__=="__main__":
    print(json.dumps(run_smoke(),sort_keys=True,indent=2))
