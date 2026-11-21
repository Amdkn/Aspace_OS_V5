"""Versioned, dependency-free metrics for evaluator-side comparisons."""
from __future__ import annotations


def pixel_metrics(predicted, actual) -> dict:
    if (predicted.width,predicted.height,predicted.channels)!=(actual.width,actual.height,actual.channels):
        raise ValueError("pixel observations must have identical dimensions and channels")
    if len(predicted.pixels)!=len(actual.pixels):
        raise ValueError("pixel buffers must have identical lengths")
    count=len(actual.pixels)
    absolute_error=sum(abs(a-b) for a,b in zip(predicted.pixels,actual.pixels))
    exact=sum(a==b for a,b in zip(predicted.pixels,actual.pixels))
    return {
        "byte_count":count,
        "mean_absolute_error":absolute_error/count if count else 0.0,
        "exact_byte_accuracy":exact/count if count else 1.0,
        "exact_image_match":predicted.pixels==actual.pixels
    }


def state_metrics(predicted: dict, actual: dict) -> dict:
    agent_exact=(predicted["agent"]["x"],predicted["agent"]["y"])==(actual["agent"]["x"],actual["agent"]["y"])
    crate_positions=lambda s: sorted((c["id"],c["x"],c["y"]) for c in s["crates"])
    gate_states=lambda s: sorted((g["id"],g["mode"],g["open"]) for g in s["gates"])
    plate_states=lambda s: sorted((p["id"],p["controls_gate_id"],p["active"]) for p in s["plates"])
    goal_exact=predicted["goal"]==actual["goal"]
    result={
        "agent_position_exact":agent_exact,
        "crate_positions_exact":crate_positions(predicted)==crate_positions(actual),
        "gate_states_exact":gate_states(predicted)==gate_states(actual),
        "plate_states_exact":plate_states(predicted)==plate_states(actual),
        "goal_exact":goal_exact,
        "terminal_exact":predicted["terminal"]==actual["terminal"]
    }
    result["full_dynamic_state_exact"]=all(result.values())
    return result
