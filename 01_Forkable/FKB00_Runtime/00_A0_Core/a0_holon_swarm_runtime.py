#!/usr/bin/env python3
"""
A'Space OS V5 — 01_Forkable/FKB00_Runtime/00_A0_Core/a0_holon_swarm_runtime.py
Unifie en un seul cycle d'exécution :
  1. Quatuor Fondamental : Agent Zero (A0) x Automaton (Réserve/Baux) x OpenRig (Descendance/Worktree) x Infinity (Population 578->75k)
  2. Périphériques Core  : Cordis (Fibers réversibles) x Pi (4 outils atomiques) x DSH
  3. Cockpit ADE & Harnesses : Herdr-Core / Orca / T3Code + OpenClaw / Hermes / Claude Code / Codex / Prime-Agent
  4. Boucle Wargame & RSI : Mitra-v2/Chronos-2/PathFM (Pré-check) + AQuA/WikiSkill/Dream-RSI/RRSI (Post-check)
"""

from __future__ import annotations
import json
import os
import sqlite3
import time
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any, Literal

WORKSPACE_ROOT = Path(__file__).resolve().parents[3]
REGISTRY_578_PATH = WORKSPACE_ROOT / "00_Memoire" / "bundle" / "areas_os" / "J1_Jerry_Macro_CrossOS" / "registry-578-holons.json"
EGM_DB_PATH = WORKSPACE_ROOT / "00_Memoire" / "egm_missions.db"

BethState = Literal["GREEN", "ORANGE", "RED", "HALT_LD03", "HALT_LD04"]


@dataclass
class AutomatonEnergyLease:
    lease_id: str
    holon_id: str
    area_code: str
    tier_allocated: int  # 0=Local LFM3/Needle, 1=FreeCloud 3-in-1, 2=Frontier Pro, 3=Jules 100/j
    max_tokens: int
    beth_guard_state: BethState
    wargame_win_prob: float
    approved: bool


@dataclass
class OpenRigDescendant:
    rig_id: str
    parent_holon: str
    assigned_holon: str
    area_code: str
    worktree_path: str
    ade_mux: str        # herdr-core | orca | t3code
    harness_engine: str # agent-zero | prime-agent | claude-code | codex | openclaw | hermes-agent
    fractal_layer: str  # 2L..20L


class A0SovereignRuntime:
    def __init__(self, beth_state: BethState = "GREEN", max_active_population: int = 64):
        self.beth_state = beth_state
        self.max_active_population = max_active_population
        self.active_rigs: dict[str, OpenRigDescendant] = {}

    def request_automaton_lease(
        self,
        holon_id: str,
        area_code: str,
        wargame_win_prob: float,
        requested_tier: int = 1,
    ) -> AutomatonEnergyLease:
        """
        Implémente la réserve structurée d'Automaton + Disjoncteur A1-Beth + Gate Prédictive (02_PredictiveWargame).
        """
        if self.beth_state in ("HALT_LD03", "HALT_LD04"):
            return AutomatonEnergyLease(
                lease_id=f"LEASE-HALT-{int(time.time())}",
                holon_id=holon_id,
                area_code=area_code,
                tier_allocated=0,
                max_tokens=0,
                beth_guard_state=self.beth_state,
                wargame_win_prob=wargame_win_prob,
                approved=False,
            )

        effective_tier = requested_tier if wargame_win_prob >= 0.60 else min(requested_tier, 1)
        token_budget = 4096 if effective_tier <= 1 else 16384

        return AutomatonEnergyLease(
            lease_id=f"LEASE-{holon_id}-{int(time.time())}",
            holon_id=holon_id,
            area_code=area_code,
            tier_allocated=effective_tier,
            max_tokens=token_budget,
            beth_guard_state=self.beth_state,
            wargame_win_prob=round(wargame_win_prob, 4),
            approved=True,
        )

    def spawn_openrig_descendant(
        self,
        parent_holon: str,
        assigned_holon: str,
        area_code: str,
        submodule_target: str,
        harness_engine: str = "prime-agent",
        fractal_layer: str = "8L",
    ) -> OpenRigDescendant | None:
        """
        Crée un descendant OpenRig géré par Infinity (contrôle de population) et isolé dans Herdr-Core / Orca.
        """
        if len(self.active_rigs) >= self.max_active_population:
            oldest_key = next(iter(self.active_rigs))
            del self.active_rigs[oldest_key]

        rig_id = f"RIG-{area_code}-{assigned_holon}-{len(self.active_rigs) + 1:03d}"
        worktree = f".worktrees/{rig_id}/{submodule_target.split('/')[-1]}"

        descendant = OpenRigDescendant(
            rig_id=rig_id,
            parent_holon=parent_holon,
            assigned_holon=assigned_holon,
            area_code=area_code,
            worktree_path=worktree,
            ade_mux="herdr-core+orca+t3code",
            harness_engine=harness_engine,
            fractal_layer=fractal_layer,
        )
        self.active_rigs[rig_id] = descendant
        return descendant


if __name__ == "__main__":
    import argparse
    import signal
    import sys

    # D-N052 R5 : la démo sans argument sort aussitôt (exit 0) — elle ne
    # suffit pas à prouver un spawn tenu par un bail. `--serve` rejoue la
    # même démo (lease + spawn, mêmes valeurs), l'imprime en JSON, puis
    # TIENT le bail jusqu'à son TTL ou jusqu'à SIGTERM/SIGINT (sortie 0
    # propre). Sans argument, le comportement historique est inchangé.
    parser = argparse.ArgumentParser(description="A0 sovereign runtime")
    parser.add_argument("--serve", action="store_true",
                        help="tenir le bail TTL secondes après la démo")
    parser.add_argument("--ttl", type=int, default=300,
                        help="bail TTL en secondes (défaut 300, §D8)")
    parser.add_argument("--max-population", type=int, default=64,
                        help="cap de population active (défaut 64)")
    args = parser.parse_args()

    runtime = A0SovereignRuntime(beth_state="GREEN",
                                 max_active_population=args.max_population)
    lease = runtime.request_automaton_lease("B2.4-RD-DC", "LD01", wargame_win_prob=0.82, requested_tier=1)
    rig = runtime.spawn_openrig_descendant(
        parent_holon="A0-AMADEUS",
        assigned_holon="B3.4-MARVEL-SQUAD",
        area_code="LD01",
        submodule_target="Amdkn/RigInfinity",
        harness_engine="prime-agent",
        fractal_layer="8L",
    )
    print(json.dumps({"lease": asdict(lease), "spawned_rig": asdict(rig) if rig else None}, indent=2), flush=True)
    if not args.serve:
        raise SystemExit(0)

    stop = {"flag": False}

    def _on_signal(signum, frame):  # noqa: ARG001
        stop["flag"] = True

    signal.signal(signal.SIGTERM, _on_signal)
    signal.signal(signal.SIGINT, _on_signal)
    deadline = time.monotonic() + max(0, args.ttl)
    print(json.dumps({"serving": True, "pid": os.getpid(),
                      "ttl_sec": args.ttl,
                      "max_active_population": args.max_population,
                      "worktree_path": rig.worktree_path if rig else None}),
          flush=True)
    while not stop["flag"] and time.monotonic() < deadline:
        time.sleep(0.2)
    print(json.dumps({"serving": False,
                      "reason": "signal" if stop["flag"] else "ttl_expired",
                      "exit": 0}), flush=True)
    raise SystemExit(0)
