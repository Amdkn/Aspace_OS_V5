"""Independent evaluator-only reference transition implementation.

This module deliberately does not import the simulator transition function.
It is a second implementation of the frozen V1 rules, used to detect engine
bugs rather than merely repeat the engine's output.
"""
from __future__ import annotations

from copy import deepcopy

_ACTIONS={"NOOP","MOVE_N","MOVE_S","MOVE_E","MOVE_W","INTERACT"}
_DELTAS={"MOVE_N":(0,-1,"N"),"MOVE_S":(0,1,"S"),"MOVE_E":(1,0,"E"),"MOVE_W":(-1,0,"W")}


def _blocked(x: int, y: int, layout: dict, state: dict, ignored_crate: str | None = None) -> bool:
    if x<0 or y<0 or x>=layout["width"] or y>=layout["height"]:
        return True
    if any((wall["x"],wall["y"])==(x,y) for wall in layout["walls"]):
        return True
    gate_states={gate["id"]:gate for gate in state["gates"]}
    for gate in layout["gates"]:
        if (gate["x"],gate["y"])==(x,y) and not gate_states[gate["id"]]["open"]:
            return True
    for crate in state["crates"]:
        if crate["id"]!=ignored_crate and (crate["x"],crate["y"])==(x,y):
            return True
    return False


def _reconcile_mechanisms(state: dict, layout: dict) -> None:
    occupied={(state["agent"]["x"],state["agent"]["y"])}
    occupied.update((crate["x"],crate["y"]) for crate in state["crates"])
    plate_states={plate["id"]:plate for plate in state["plates"]}
    for plate_layout in layout["plates"]:
        plate_states[plate_layout["id"]]["active"]=(plate_layout["x"],plate_layout["y"]) in occupied
    for gate in state["gates"]:
        if gate["mode"]=="pressure":
            controller=next(p for p in state["plates"] if p["controls_gate_id"]==gate["id"])
            gate["open"]=controller["active"]


def predict(state: dict, layout: dict, actions: list[str]) -> dict:
    """Apply actions using a separate implementation of the V1 transition rules."""
    current=deepcopy(state)
    for action in actions:
        if action not in _ACTIONS:
            raise ValueError("unknown action: "+str(action))
        if current["terminal"]:
            raise ValueError("terminal episode must be reset before another action")
        nxt=deepcopy(current)
        if action in _DELTAS:
            dx,dy,facing=_DELTAS[action]
            nxt["agent"]["facing"]=facing
            target=(nxt["agent"]["x"]+dx,nxt["agent"]["y"]+dy)
            crate=next((item for item in nxt["crates"] if (item["x"],item["y"])==target),None)
            if crate is None:
                if not _blocked(target[0],target[1],layout,nxt):
                    nxt["agent"]["x"],nxt["agent"]["y"]=target
            else:
                destination=(target[0]+dx,target[1]+dy)
                if not _blocked(destination[0],destination[1],layout,nxt,crate["id"]):
                    crate["x"],crate["y"]=destination
                    nxt["agent"]["x"],nxt["agent"]["y"]=target
        elif action=="INTERACT":
            vectors={"N":(0,-1),"S":(0,1),"E":(1,0),"W":(-1,0)}
            dx,dy=vectors[nxt["agent"]["facing"]]
            target=(nxt["agent"]["x"]+dx,nxt["agent"]["y"]+dy)
            gate=next((item for item in layout["gates"] if (item["x"],item["y"])==target and item["mode"]=="manual"),None)
            if gate is not None:
                state_gate=next(item for item in nxt["gates"] if item["id"]==gate["id"])
                state_gate["open"]=not state_gate["open"]
        _reconcile_mechanisms(nxt,layout)
        nxt["goal"]["reached"]=(nxt["agent"]["x"],nxt["agent"]["y"])==(layout["goal"]["x"],layout["goal"]["y"])
        nxt["terminal"]=nxt["goal"]["reached"]
        nxt["tick"]=current["tick"]+1
        nxt["crates"].sort(key=lambda item:item["id"])
        nxt["gates"].sort(key=lambda item:item["id"])
        nxt["plates"].sort(key=lambda item:item["id"])
        current=nxt
    return current
