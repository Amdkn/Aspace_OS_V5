"""Evaluator-only exact transition oracle; never pass this module to candidates."""
from __future__ import annotations
from copy import deepcopy
from ..env.toy_world import transition_state


def predict(state: dict, layout: dict, actions: list[str]) -> dict:
    result=deepcopy(state)
    for action in actions:
        result=transition_state(result,layout,action)
    return result
