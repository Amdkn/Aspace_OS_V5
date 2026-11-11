#!/usr/bin/env python3
"""
A'Space OS V5 — a0_egm_bridge.py
Pont d'Inférence & d'Orchestration Natif — moteur agent-zero natif (RigInfinity) sur :
  1. Le Routeur Unifié EGM (`http://127.0.0.1:31415/v1/chat/completions`)
  2. Le Ledger SQLite WAL (`00_Memoire/egm_missions.db`)
  3. Les Exécuteurs Poissons Rouges (Jules 100/j, Codex-ChatGPT-Web, Herdr/Orca ADE)
"""

from __future__ import annotations
import json
import sqlite3
import time
import urllib.request
from pathlib import Path
from typing import Any

WORKSPACE_ROOT = Path(__file__).resolve().parents[3]
DB_PATH = WORKSPACE_ROOT / "00_Memoire" / "egm_missions.db"
GATEWAY_URL = "http://127.0.0.1:31415/v1/chat/completions"


class AgentZeroEgmBridge:
    """
    Moteur natif agent-zero (boucle Agent + providers, RigInfinity).
    Sépare la planification macroscopique (Couche Éléphant) de l'exécution jetable (Couche Poisson Rouge).
    """

    def __init__(self, db_path: Path = DB_PATH, gateway_url: str = GATEWAY_URL):
        self.db_path = db_path
        self.gateway_url = gateway_url

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(str(self.db_path), timeout=15.0)
        conn.execute("PRAGMA journal_mode=WAL;")
        conn.row_factory = sqlite3.Row
        return conn

    def compile_goldfish_context(self, mission_row: dict[str, Any]) -> list[dict[str, str]]:
        """
        Construit la fenêtre stricte (< 4 Ko) envoyée à un worker Goldfish
        sans historique conversationnel polluant.
        """
        system_contract = (
            "You are an A'Space OS V5 Goldfish Worker operating under the Elephant-Goldfish Model (EGM). "
            "Execute ONLY the atomic submodule mission below, verify via deterministic gate, and terminate."
        )
        user_payload = (
            f"Mission ID: {mission_row['mission_id']}\n"
            f"Target Submodule: {mission_row['target_submodule']}\n"
            f"Holon Owner: {mission_row['holon_owner']} ({mission_row['area_code']})\n"
            f"Runner: {mission_row['runner_target']}\n\n"
            f"{mission_row['goldfish_prompt']}\n\n"
            f"Validation Command: {mission_row['validation_cmd']}"
        )
        return [
            {"role": "system", "content": system_contract},
            {"role": "user", "content": user_payload},
        ]

    def pop_batch_for_runner(self, runner_target: str, limit: int = 10) -> list[dict[str, Any]]:
        """
        Dépile un lot de missions QUEUED pour un exécuteur donné
        (`jules_cloud_100`, `codex_chatgpt_web`, `herdr_local_ade`).
        """
        if not self.db_path.exists():
            return []
        with self._connect() as conn:
            rows = conn.execute(
                """
                SELECT * FROM goldfish_missions
                WHERE status = 'QUEUED' AND runner_target = ?
                ORDER BY created_at ASC
                LIMIT ?
                """,
                (runner_target, limit),
            ).fetchall()
            batch = []
            for r in rows:
                d = dict(r)
                d["compiled_messages"] = self.compile_goldfish_context(d)
                batch.append(d)
            return batch

    def summary_stats(self) -> dict[str, Any]:
        if not self.db_path.exists():
            return {"error": "Database not initialized"}
        with self._connect() as conn:
            by_runner = {
                r["runner_target"]: r["c"]
                for r in conn.execute(
                    "SELECT runner_target, COUNT(*) AS c FROM goldfish_missions GROUP BY runner_target"
                ).fetchall()
            }
            by_area = {
                r["area_code"]: r["c"]
                for r in conn.execute(
                    "SELECT area_code, COUNT(*) AS c FROM goldfish_missions GROUP BY area_code ORDER BY area_code"
                ).fetchall()
            }
            total = sum(by_runner.values())
        return {
            "bridge": "AgentZeroEgmBridge",
            "gateway_url": self.gateway_url,
            "total_missions": total,
            "missions_by_runner": by_runner,
            "missions_by_area": by_area,
        }


if __name__ == "__main__":
    bridge = AgentZeroEgmBridge()
    print(json.dumps(bridge.summary_stats(), indent=2, ensure_ascii=False))
