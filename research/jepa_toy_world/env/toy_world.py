"""Deterministic JEPA Toy World simulator; standard-library only.

Candidate-facing API: reset/step return RGB observations and empty info.
Ground truth remains private to the evaluator process.
"""
from __future__ import annotations

import copy
import hashlib
import json
from dataclasses import dataclass
from typing import Any

WIDTH = 12
HEIGHT = 12
ACTIONS = {"NOOP", "MOVE_N", "MOVE_S", "MOVE_E", "MOVE_W", "INTERACT"}
DIRECTIONS = {
    "MOVE_N": (0, -1, "N"),
    "MOVE_S": (0, 1, "S"),
    "MOVE_E": (1, 0, "E"),
    "MOVE_W": (-1, 0, "W"),
}


def canonical_json(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def sha256_id(value: Any) -> str:
    return "sha256:" + hashlib.sha256(canonical_json(value)).hexdigest()


class PCG32:
    """PCG-XSH-RR 64/32 with the V1 fixed stream selector."""
    MULTIPLIER = 6364136223846793005
    INCREMENT = 1442695040888963407
    MASK64 = (1 << 64) - 1
    MASK32 = (1 << 32) - 1

    def __init__(self, seed: int):
        if isinstance(seed, bool) or not isinstance(seed, int) or not 0 <= seed <= self.MASK64:
            raise ValueError("seed must be an unsigned 64-bit integer")
        self.state = 0
        self._advance()
        self.state = (self.state + seed) & self.MASK64
        self._advance()

    def _advance(self) -> int:
        oldstate = self.state
        self.state = (oldstate * self.MULTIPLIER + self.INCREMENT) & self.MASK64
        xorshifted = (((oldstate >> 18) ^ oldstate) >> 27) & self.MASK32
        rot = (oldstate >> 59) & 31
        return ((xorshifted >> rot) | (xorshifted << ((-rot) & 31))) & self.MASK32

    def next_u32(self) -> int:
        return self._advance()

    def randbelow(self, bound: int) -> int:
        if isinstance(bound, bool) or not isinstance(bound, int) or not 1 <= bound <= (1 << 32):
            raise ValueError("bound must be an integer in [1, 2^32]")
        threshold = ((1 << 32) - bound) % bound
        while True:
            value = self.next_u32()
            if value >= threshold:
                return value % bound


def _layout_variant(index: int) -> dict[str, Any]:
    variants = [
        {"agent_spawn":{"x":1,"y":1,"facing":"E"},"crates":[{"id":"crate-01","x":4,"y":1}],"gates":[{"id":"gate-manual","x":7,"y":1,"mode":"manual","initial_open":False},{"id":"gate-pressure","x":9,"y":8,"mode":"pressure","initial_open":False}],"plates":[{"id":"plate-01","x":8,"y":8,"controls_gate_id":"gate-pressure"}],"goal":{"x":10,"y":10}},
        {"agent_spawn":{"x":1,"y":10,"facing":"E"},"crates":[{"id":"crate-01","x":4,"y":10}],"gates":[{"id":"gate-manual","x":7,"y":10,"mode":"manual","initial_open":False},{"id":"gate-pressure","x":9,"y":2,"mode":"pressure","initial_open":False}],"plates":[{"id":"plate-01","x":8,"y":2,"controls_gate_id":"gate-pressure"}],"goal":{"x":10,"y":1}},
        {"agent_spawn":{"x":10,"y":1,"facing":"W"},"crates":[{"id":"crate-01","x":7,"y":1}],"gates":[{"id":"gate-manual","x":4,"y":1,"mode":"manual","initial_open":False},{"id":"gate-pressure","x":2,"y":8,"mode":"pressure","initial_open":False}],"plates":[{"id":"plate-01","x":3,"y":8,"controls_gate_id":"gate-pressure"}],"goal":{"x":1,"y":10}},
        {"agent_spawn":{"x":10,"y":10,"facing":"W"},"crates":[{"id":"crate-01","x":7,"y":10}],"gates":[{"id":"gate-manual","x":4,"y":10,"mode":"manual","initial_open":False},{"id":"gate-pressure","x":2,"y":2,"mode":"pressure","initial_open":False}],"plates":[{"id":"plate-01","x":3,"y":2,"controls_gate_id":"gate-pressure"}],"goal":{"x":1,"y":1}}
    ]
    chosen = copy.deepcopy(variants[index])
    return {
        "schema_version":"toy-world.layout.v1",
        "layout_id":f"layout-{index + 1:02d}",
        "width":WIDTH,"height":HEIGHT,"walls":[],
        **chosen
    }


def generate_layout(seed: int) -> dict[str, Any]:
    """V1 generator consumes exactly one PCG32 bounded draw: template index [0, 4)."""
    return _layout_variant(PCG32(seed).randbelow(4))


def validate_layout(layout: dict[str, Any]) -> None:
    if layout.get("schema_version") != "toy-world.layout.v1":
        raise ValueError("unsupported layout schema")
    if layout.get("width") != WIDTH or layout.get("height") != HEIGHT:
        raise ValueError("layout must be 12x12")
    def pos(item: dict[str, Any]) -> tuple[int, int]:
        x, y = item.get("x"), item.get("y")
        if isinstance(x, bool) or isinstance(y, bool) or not isinstance(x, int) or not isinstance(y, int) or not (0 <= x < WIDTH and 0 <= y < HEIGHT):
            raise ValueError("coordinate outside 12x12 grid")
        return x, y
    walls = {pos(w) for w in layout["walls"]}
    if len(walls) != len(layout["walls"]):
        raise ValueError("duplicate wall coordinate")
    ids: set[str] = set()
    occupied: set[tuple[int, int]] = set(walls)
    for collection in ("crates", "gates", "plates"):
        for entity in layout[collection]:
            entity_id = entity["id"]
            if entity_id in ids:
                raise ValueError("entity IDs must be globally unique")
            ids.add(entity_id)
            cell = pos(entity)
            if cell in occupied:
                raise ValueError("layout entities may not overlap walls or each other")
            occupied.add(cell)
    spawn = pos(layout["agent_spawn"])
    goal = pos(layout["goal"])
    if spawn in occupied or goal in occupied or spawn == goal:
        raise ValueError("spawn and goal must be distinct free cells")
    gate_by_id = {g["id"]: g for g in layout["gates"]}
    controllers: set[str] = set()
    for plate in layout["plates"]:
        gate_id = plate["controls_gate_id"]
        gate = gate_by_id.get(gate_id)
        if gate is None or gate["mode"] != "pressure":
            raise ValueError("plate must reference an existing pressure gate")
        if gate_id in controllers:
            raise ValueError("pressure gate may have only one controller")
        controllers.add(gate_id)
    for gate in layout["gates"]:
        if gate["mode"] == "pressure" and gate["id"] not in controllers:
            raise ValueError("every pressure gate requires exactly one plate")
        if gate["mode"] == "manual" and gate["id"] in controllers:
            raise ValueError("manual gate cannot have a plate controller")


def initial_state(layout: dict[str, Any], seed: int) -> dict[str, Any]:
    validate_layout(layout)
    layout_copy = copy.deepcopy(layout)
    gates = [{"id":g["id"],"mode":g["mode"],"open":bool(g["initial_open"])} for g in sorted(layout["gates"],key=lambda x:x["id"])]
    plates = [{"id":p["id"],"controls_gate_id":p["controls_gate_id"],"active":False} for p in sorted(layout["plates"],key=lambda x:x["id"])]
    state = {
        "schema_version":"toy-world.state.v1",
        "episode_id":f"seed-{seed:016x}-{layout['layout_id']}",
        "layout_id":layout["layout_id"],
        "layout_hash":sha256_id(layout_copy),
        "tick":0,
        "agent":copy.deepcopy(layout["agent_spawn"]),
        "crates":sorted(copy.deepcopy(layout["crates"]),key=lambda x:x["id"]),
        "gates":gates,"plates":plates,
        "goal":{"x":layout["goal"]["x"],"y":layout["goal"]["y"],"reached":False},
        "terminal":False
    }
    _refresh_plates_and_gates(state, layout)
    return state


def _cell_blocked(x: int, y: int, layout: dict[str, Any], state: dict[str, Any], ignore_crate: str | None = None) -> bool:
    if not (0 <= x < WIDTH and 0 <= y < HEIGHT):
        return True
    if any(w["x"] == x and w["y"] == y for w in layout["walls"]):
        return True
    if any(g["x"] == x and g["y"] == y and not next(sg for sg in state["gates"] if sg["id"] == g["id"])["open"] for g in layout["gates"]):
        return True
    if any(c["id"] != ignore_crate and c["x"] == x and c["y"] == y for c in state["crates"]):
        return True
    return False


def _refresh_plates_and_gates(state: dict[str, Any], layout: dict[str, Any]) -> None:
    occupants = {(state["agent"]["x"],state["agent"]["y"])}
    occupants.update((c["x"],c["y"]) for c in state["crates"])
    layout_plates = {p["id"]:p for p in layout["plates"]}
    for plate in state["plates"]:
        lp = layout_plates[plate["id"]]
        plate["active"] = (lp["x"],lp["y"]) in occupants
    active_by_gate = {p["controls_gate_id"]:p["active"] for p in state["plates"]}
    for gate in state["gates"]:
        if gate["mode"] == "pressure":
            gate["open"] = bool(active_by_gate[gate["id"]])


def transition_state(state: dict[str, Any], layout: dict[str, Any], action: str) -> dict[str, Any]:
    if action not in ACTIONS:
        raise ValueError(f"unknown action: {action}")
    if state["terminal"]:
        raise ValueError("terminal episode must be reset before another action")
    nxt = copy.deepcopy(state)
    dx = dy = 0
    if action in DIRECTIONS:
        dx, dy, facing = DIRECTIONS[action]
        nxt["agent"]["facing"] = facing
        tx, ty = nxt["agent"]["x"] + dx, nxt["agent"]["y"] + dy
        crate = next((c for c in nxt["crates"] if (c["x"],c["y"]) == (tx,ty)), None)
        if crate is None:
            if not _cell_blocked(tx,ty,layout,nxt):
                nxt["agent"]["x"],nxt["agent"]["y"] = tx,ty
        else:
            cx, cy = tx + dx, ty + dy
            if not _cell_blocked(cx,cy,layout,nxt,ignore_crate=crate["id"]):
                crate["x"],crate["y"] = cx,cy
                nxt["agent"]["x"],nxt["agent"]["y"] = tx,ty
    elif action == "INTERACT":
        facing = nxt["agent"]["facing"]
        fdx,fdy = {"N":(0,-1),"S":(0,1),"E":(1,0),"W":(-1,0)}[facing]
        target=(nxt["agent"]["x"]+fdx,nxt["agent"]["y"]+fdy)
        gate_layout=next((g for g in layout["gates"] if (g["x"],g["y"])==target and g["mode"]=="manual"),None)
        if gate_layout is not None:
            gate_state=next(g for g in nxt["gates"] if g["id"]==gate_layout["id"])
            gate_state["open"]=not gate_state["open"]
    _refresh_plates_and_gates(nxt,layout)
    nxt["goal"]["reached"]=(nxt["agent"]["x"],nxt["agent"]["y"])==(layout["goal"]["x"],layout["goal"]["y"])
    nxt["terminal"]=nxt["goal"]["reached"]
    nxt["tick"]+=1
    nxt["crates"].sort(key=lambda x:x["id"])
    nxt["gates"].sort(key=lambda x:x["id"])
    nxt["plates"].sort(key=lambda x:x["id"])
    return nxt


@dataclass(frozen=True)
class RGBFrame:
    width: int
    height: int
    channels: int
    pixels: bytes


class ToyWorldEnv:
    """Gymnasium-shaped, read-only-observation environment (no Gymnasium dependency)."""
    metadata = {"render_modes":["rgb_array"],"render_fps":1}

    def __init__(self, layout: dict[str, Any] | None = None):
        self._provided_layout = copy.deepcopy(layout)
        self._layout: dict[str, Any] | None = None
        self._state: dict[str, Any] | None = None
        self._seed = 0
        self._observation_count = 0

    def reset(self, *, seed: int | None = None, options: dict[str, Any] | None = None):
        from .renderer import render_rgb
        if seed is not None:
            if isinstance(seed,bool) or not isinstance(seed,int) or not 0 <= seed <= PCG32.MASK64:
                raise ValueError("seed must be an unsigned 64-bit integer")
            self._seed=seed
        layout=(options or {}).get("layout",self._provided_layout)
        self._layout=copy.deepcopy(layout) if layout is not None else generate_layout(self._seed)
        self._state=initial_state(self._layout,self._seed)
        self._observation_count=0
        return render_rgb(self._state,self._layout), {}

    def step(self, action: str):
        from .renderer import render_rgb
        if self._state is None or self._layout is None:
            raise RuntimeError("reset must be called before step")
        self._state=transition_state(self._state,self._layout,action)
        self._observation_count+=1
        reward=1.0 if self._state["terminal"] else 0.0
        return render_rgb(self._state,self._layout), reward, self._state["terminal"], False, {}

    def render(self):
        from .renderer import render_rgb
        if self._state is None or self._layout is None:
            raise RuntimeError("reset must be called before render")
        return render_rgb(self._state,self._layout)

    def _evaluator_snapshot(self) -> dict[str, Any]:
        if self._state is None:
            raise RuntimeError("reset must be called before evaluator snapshot")
        return copy.deepcopy(self._state)

    def _evaluator_layout(self) -> dict[str, Any]:
        if self._layout is None:
            raise RuntimeError("reset must be called before evaluator layout")
        return copy.deepcopy(self._layout)
