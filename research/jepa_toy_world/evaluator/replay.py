"""Deterministic action-trace recording and independent replay checks."""
from __future__ import annotations

import hashlib
from ..env.toy_world import ToyWorldEnv, canonical_json, sha256_id


def run_trace(layout: dict, seed: int, actions: list[str]) -> list[dict]:
    env=ToyWorldEnv(layout)
    observation,_=env.reset(seed=seed)
    trace=[]
    for action in actions:
        before=env._evaluator_snapshot()
        before_hash=sha256_id(before)
        observation,_,terminated,_,_=env.step(action)
        after=env._evaluator_snapshot()
        trace.append({
            "tick":after["tick"],
            "action":action,
            "prior_state_hash":before_hash,
            "result_state_hash":sha256_id(after),
            "observation_sha256":hashlib.sha256(observation.pixels).hexdigest(),
            "terminal":terminated
        })
        if terminated and action != actions[-1]:
            raise ValueError("trace contains actions after terminal state")
    return trace


def verify_replay(layout: dict, seed: int, actions: list[str]) -> bool:
    return run_trace(layout,seed,actions)==run_trace(layout,seed,actions)
