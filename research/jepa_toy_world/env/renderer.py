"""Pure deterministic 192x192 RGB renderer for Toy World V1."""
from __future__ import annotations

from .toy_world import RGBFrame, WIDTH, HEIGHT

PALETTE = {
    "floor":(238,240,232),"wall":(52,61,66),"grid":(210,216,207),
    "agent":(35,105,190),"agent_marker":(245,245,245),
    "crate":(171,111,54),"crate_inset":(112,70,36),
    "manual_closed":(155,55,55),"manual_open":(205,220,205),
    "pressure_closed":(115,65,145),"pressure_open":(205,190,220),
    "plate_inactive":(125,130,125),"plate_active":(235,190,55),
    "goal":(55,155,95)
}
CELL=16
SIZE=WIDTH*CELL


def _rect(buf: bytearray, x: int, y: int, w: int, h: int, color: tuple[int,int,int]) -> None:
    r,g,b=color
    for py in range(y,y+h):
        start=(py*SIZE+x)*3
        for px in range(w):
            i=start+px*3
            buf[i]=r;buf[i+1]=g;buf[i+2]=b


def render_rgb(state: dict, layout: dict) -> RGBFrame:
    buf=bytearray(PALETTE["floor"]*(SIZE*SIZE))
    for wall in layout["walls"]:
        _rect(buf,wall["x"]*CELL,wall["y"]*CELL,CELL,CELL,PALETTE["wall"])
    _rect(buf,layout["goal"]["x"]*CELL+3,layout["goal"]["y"]*CELL+3,10,10,PALETTE["goal"])
    state_plates={p["id"]:p for p in state["plates"]}
    for plate in layout["plates"]:
        color=PALETTE["plate_active"] if state_plates[plate["id"]]["active"] else PALETTE["plate_inactive"]
        _rect(buf,plate["x"]*CELL+4,plate["y"]*CELL+4,8,8,color)
    state_gates={g["id"]:g for g in state["gates"]}
    for gate in layout["gates"]:
        current=state_gates[gate["id"]]
        if gate["mode"]=="manual":
            color=PALETTE["manual_open"] if current["open"] else PALETTE["manual_closed"]
        else:
            color=PALETTE["pressure_open"] if current["open"] else PALETTE["pressure_closed"]
        _rect(buf,gate["x"]*CELL+2,gate["y"]*CELL+6,12,4,color)
    for crate in state["crates"]:
        x,y=crate["x"]*CELL,crate["y"]*CELL
        _rect(buf,x+2,y+2,12,12,PALETTE["crate_inset"])
        _rect(buf,x+4,y+4,8,8,PALETTE["crate"])
    ax,ay=state["agent"]["x"]*CELL,state["agent"]["y"]*CELL
    _rect(buf,ax+3,ay+3,10,10,PALETTE["agent"])
    facing=state["agent"]["facing"]
    marker={"N":(ax+6,ay+3),"S":(ax+6,ay+9),"E":(ax+9,ay+6),"W":(ax+3,ay+6)}[facing]
    _rect(buf,marker[0],marker[1],4,4,PALETTE["agent_marker"])
    # Internal grid lines only; outer border remains unchanged.
    for cell in range(1,WIDTH):
        x=cell*CELL
        for y in range(SIZE):
            i=(y*SIZE+x)*3
            buf[i:i+3]=bytes(PALETTE["grid"])
        y=cell*CELL
        row=y*SIZE*3
        for x in range(SIZE):
            i=row+x*3
            buf[i:i+3]=bytes(PALETTE["grid"])
    return RGBFrame(SIZE,SIZE,3,bytes(buf))
