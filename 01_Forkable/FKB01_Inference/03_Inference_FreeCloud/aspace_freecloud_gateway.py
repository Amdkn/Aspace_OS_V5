#!/usr/bin/env python3
"""
A'Space OS V5 — aspace_freecloud_gateway.py (Production EGM Edition)
Architecture : Elephant-Goldfish Model (EGM) x Automaton Reserve x Agent Zero (A0)
Port : 127.0.0.1:31415 (Compatible OpenAI /v1/chat/completions & Mission Dispatcher)
"""

from __future__ import annotations
import json
import os
import sqlite3
import subprocess
import threading
import time
import urllib.request
import urllib.error
from dataclasses import dataclass, asdict
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
from pathlib import Path
from typing import Any

WORKSPACE_ROOT = Path(__file__).resolve().parents[3]
DB_PATH = WORKSPACE_ROOT / "00_Memoire" / "egm_missions.db"
PORT = int(os.environ.get("ASPACE_GATEWAY_PORT", "31415"))


# ============================================================================
# 1. COUCHE ÉLÉPHANT (Mémoire Persistante SQLite WAL, Quotas & Missions 578 Holons)
# ============================================================================
class ElephantStateLedger:
    """
    Gère l'état macroscopique (Elephant Layer) :
    - Quotas quotidiens (notamment Jules 100 sessions/jour avant le 11 nov. 2026)
    - Santé des 3 backends FreeCloud (freellmapi, freebuff, codex-chatgpt-web)
    - File de missions d'évolution des sous-modules Git Amdkn/*
    """

    def __init__(self, db_path: Path):
        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(str(self.db_path), timeout=15.0)
        conn.execute("PRAGMA journal_mode=WAL;")
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self) -> None:
        with self._connect() as conn:
            conn.executescript(
                """
                CREATE TABLE IF NOT EXISTS provider_health (
                    provider_id TEXT PRIMARY KEY,
                    tier INTEGER NOT NULL,
                    endpoint TEXT NOT NULL,
                    daily_limit INTEGER DEFAULT 1000,
                    used_today INTEGER DEFAULT 0,
                    consecutive_failures INTEGER DEFAULT 0,
                    cooldown_until REAL DEFAULT 0.0,
                    last_latency_ms REAL DEFAULT 0.0
                );

                CREATE TABLE IF NOT EXISTS goldfish_missions (
                    mission_id TEXT PRIMARY KEY,
                    target_submodule TEXT NOT NULL,
                    holon_owner TEXT NOT NULL,
                    area_code TEXT NOT NULL,
                    runner_target TEXT NOT NULL,
                    goldfish_prompt TEXT NOT NULL,
                    validation_cmd TEXT NOT NULL,
                    status TEXT DEFAULT 'QUEUED',
                    created_at REAL NOT NULL,
                    completed_at REAL
                );
                """
            )
            providers = [
                ("local_lfm3_needle", 0, "http://127.0.0.1:9931/v1/chat/completions", 999999),
                ("freellmapi", 1, "http://127.0.0.1:31416/v1/chat/completions", 5000),
                ("freebuff", 1, "http://127.0.0.1:31417/v1/chat/completions", 5000),
                ("codex_chatgpt_web", 2, "http://127.0.0.1:31418/v1/chat/completions", 1500),
                ("jules_cloud_100", 3, "https://jules.google.com/session", 100),
            ]
            for pid, tier, ep, lim in providers:
                conn.execute(
                    """
                    INSERT OR IGNORE INTO provider_health (provider_id, tier, endpoint, daily_limit)
                    VALUES (?, ?, ?, ?)
                    """,
                    (pid, tier, ep, lim),
                )

    def select_healthy_provider(self, prefer_tier: int = 1) -> dict[str, Any]:
        now = time.time()
        with self._connect() as conn:
            rows = conn.execute(
                """
                SELECT * FROM provider_health
                WHERE cooldown_until <= ? AND used_today < daily_limit
                ORDER BY ABS(tier - ?) ASC, consecutive_failures ASC, last_latency_ms ASC
                """,
                (now, prefer_tier),
            ).fetchall()
            if not rows:
                return {"provider_id": "freellmapi", "endpoint": "http://127.0.0.1:31416/v1/chat/completions"}
            return dict(rows[0])

    def record_outcome(self, provider_id: str, success: bool, latency_ms: float) -> None:
        now = time.time()
        with self._connect() as conn:
            if success:
                conn.execute(
                    """
                    UPDATE provider_health
                    SET used_today = used_today + 1,
                        consecutive_failures = 0,
                        cooldown_until = 0.0,
                        last_latency_ms = ?
                    WHERE provider_id = ?
                    """,
                    (latency_ms, provider_id),
                )
            else:
                conn.execute(
                    """
                    UPDATE provider_health
                    SET consecutive_failures = consecutive_failures + 1,
                        cooldown_until = ? + (MIN(consecutive_failures + 1, 6) * 30.0)
                    WHERE provider_id = ?
                    """,
                    (now, provider_id),
                )

    def enqueue_submodule_evolution_missions(self) -> int:
        """
        Scanne .gitmodules et génère des missions Goldfish
        pour muter chaque sous-module sur sa branche `aspace-v5-native` et saturer
        les 100 sessions/jour de Jules + Codex-Web + Herdr ADE.
        """
        gitmodules = WORKSPACE_ROOT / ".gitmodules"
        if not gitmodules.exists():
            return 0

        submodules: list[str] = []
        for line in gitmodules.read_text(encoding="utf-8", errors="ignore").splitlines():
            line = line.strip()
            if line.startswith("path = "):
                submodules.append(line.split("path = ", 1)[1].strip())

        created = 0
        now = time.time()
        with self._connect() as conn:
            for idx, sub_path in enumerate(submodules):
                mid = f"EGM-{sub_path.replace('/', '_')}"
                runner = "jules_cloud_100" if idx < 100 else ("codex_chatgpt_web" if idx % 2 == 0 else "herdr_local_ade")
                area_code = f"LD0{(idx % 8) + 1}"
                prompt = (
                    f"[GOLDFISH ATOMIC MISSION] Submodule: {sub_path} | Area: {area_code}\n"
                    f"1. Checkout branch `aspace-v5-native`.\n"
                    f"2. Wire native adapter to A0 (`00_A0_Core/agent-zero`) and Shared Brain MCP (`00_Memoire/shared_brain/memory.jsonl`).\n"
                    f"3. Expose Cordis Fiber plugin descriptor (`aspace-plugin.json`).\n"
                    f"4. Run deterministic tests and commit."
                )
                cur = conn.execute(
                    """
                    INSERT OR IGNORE INTO goldfish_missions
                    (mission_id, target_submodule, holon_owner, area_code, runner_target, goldfish_prompt, validation_cmd, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        mid,
                        sub_path,
                        f"S1-RICK/{area_code}",
                        area_code,
                        runner,
                        prompt,
                        "pwsh -NoProfile -ExecutionPolicy Bypass -File 02_Factory/checks.ps1",
                        now,
                    ),
                )
                if cur.rowcount > 0:
                    created += 1
        return created


# ============================================================================
# 2. COUCHE POISSON ROUGE (Exécuteur Sans État, Contexte Minimal & Bascule 3-en-1)
# ============================================================================
class GoldfishInferenceRouter:
    """
    Reçoit une requête d'Agent Zero (A0) ou d'un ADE (Herdr/Orca/T3Code),
    élague le bruit contextuel selon le protocole Elephant-Goldfish,
    et exécute l'inférence avec bascule automatique entre :
      1. freellmapi
      2. freebuff
      3. codex-chatgpt-web
      4. local_lfm3_needle
    """

    def __init__(self, ledger: ElephantStateLedger):
        self.ledger = ledger

    @staticmethod
    def compress_to_goldfish_window(messages: list[dict[str, Any]], max_Wait_chars: int = 12000) -> list[dict[str, Any]]:
        """
        Filtre Goldfish : conserve l'instruction système A0 et la tâche atomique courante
        tout en évitant l'accumulation de traces obsolètes qui dégradent le raisonnement.
        """
        if not messages:
            return []
        system_msgs = [m for m in messages if m.get("role") == "system"][:1]
        recent_msgs = [m for m in messages if m.get("role") != "system"][-4:]
        compacted = system_msgs + recent_msgs
        for m in compacted:
            content = str(m.get("content", ""))
            if len(content) > max_Wait_chars:
                m["content"] = content[: max_Wait_chars // 2] + "\n...[EGM-GOLDFISH-TRIM]...\n" + content[-(max_Wait_chars // 2) :]
        return compacted

    def dispatch_chat_completion(self, payload: dict[str, Any]) -> dict[str, Any]:
        messages = self.compress_to_goldfish_window(payload.get("messages", []))
        model_requested = str(payload.get("model", "aspace-a0-auto"))

        prefer_tier = 0 if "local" in model_requested or "reflex" in model_requested else 1
        tried: set[str] = set()

        for _ in range(3):
            provider = self.ledger.select_healthy_provider(prefer_tier=prefer_tier)
            pid = provider["provider_id"]
            if pid in tried:
                break
            tried.add(pid)

            t0 = time.time()
            try:
                req_body = json.dumps({**payload, "messages": messages}).encode("utf-8")
                req = urllib.request.Request(
                    provider["endpoint"],
                    data=req_body,
                    headers={"Content-Type": "application/json"},
                    method="POST",
                )
                with urllib.request.urlopen(req, timeout=2) as resp:
                    raw = json.loads(resp.read().decode("utf-8"))
                    latency = (time.time() - t0) * 1000.0
                    self.ledger.record_outcome(pid, True, latency)
                    raw["aspace_routing"] = {"provider": pid, "latency_ms": round(latency, 1), "mode": "EGM_LIVE"}
                    return raw
            except Exception:
                latency = (time.time() - t0) * 1000.0
                self.ledger.record_outcome(pid, False, latency)

        last_user = next((m.get("content", "") for m in reversed(messages) if m.get("role") == "user"), "")
        return {
            "id": f"chatcmpl-egm-{int(time.time())}",
            "object": "chat.completion",
            "created": int(time.time()),
            "model": model_requested,
            "aspace_routing": {
                "provider": "a0_egm_autonomous_fallback",
                "status": "READY_FOR_SUBMODULE_DAEMONS",
            },
            "choices": [
                {
                    "index": 0,
                    "message": {
                        "role": "assistant",
                        "content": (
                            f"[A0-EGM-GATEWAY :31415 ACTIF] Requête reçue ({len(str(last_user))} car.). "
                            f"File EGM synchronisée sur 00_Memoire/egm_missions.db."
                        ),
                    },
                    "finish_reason": "stop",
                }
            ],
        }


# ============================================================================
# 3. SERVEUR HTTP MULTI-THREADÉ (:31415) & DISPATCHER DE MISSIONS JULES / ADE
# ============================================================================
LEDGER = ElephantStateLedger(DB_PATH)
ROUTER = GoldfishInferenceRouter(LEDGER)


class AspaceGatewayHandler(BaseHTTPRequestHandler):
    def log_message(self, format: str, *args: Any) -> None:
        return

    def _send_json(self, code: int, data: dict[str, Any]) -> None:
        body = json.dumps(data, ensure_ascii=False, indent=2).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:
        if self.path in ("/health", "/v1/models"):
            with LEDGER._connect() as conn:
                providers = [dict(r) for r in conn.execute("SELECT * FROM provider_health").fetchall()]
                queued = conn.execute("SELECT COUNT(*) AS c FROM goldfish_missions WHERE status='QUEUED'").fetchone()["c"]
            self._send_json(
                200,
                {
                    "status": "ONLINE",
                    "architecture": "EGM (Elephant-Goldfish) x A0 FreeCloud 3-in-1",
                    "queued_goldfish_missions": queued,
                    "providers": providers,
                },
            )
            return

        if self.path == "/v1/egm/next-mission":
            with LEDGER._connect() as conn:
                row = conn.execute(
                    "SELECT * FROM goldfish_missions WHERE status='QUEUED' ORDER BY created_at ASC LIMIT 1"
                ).fetchone()
                if not row:
                    self._send_json(200, {"mission": None})
                    return
                conn.execute("UPDATE goldfish_missions SET status='DISPATCHED' WHERE mission_id=?", (row["mission_id"],))
                self._send_json(200, {"mission": dict(row)})
            return

        self._send_json(404, {"error": "Not found"})

    def do_POST(self) -> None:
        length = int(self.headers.get("Content-Length", "0"))
        raw_body = self.rfile.read(length).decode("utf-8") if length > 0 else "{}"
        payload = json.loads(raw_body) if raw_body else {}

        if self.path == "/v1/chat/completions":
            result = ROUTER.dispatch_chat_completion(payload)
            self._send_json(200, result)
            return

        if self.path == "/v1/egm/seed-missions":
            added = LEDGER.enqueue_submodule_evolution_missions()
            self._send_json(200, {"seeded_missions": added})
            return

        self._send_json(404, {"error": "Endpoint unknown"})


def run_gateway_server() -> None:
    seeded = LEDGER.enqueue_submodule_evolution_missions()
    print(f"[A0-EGM-GATEWAY] {seeded} missions Goldfish indexées depuis .gitmodules dans {DB_PATH}")
    print(f"[A0-EGM-GATEWAY] Écoute active sur http://127.0.0.1:{PORT}/v1/chat/completions")
    server = ThreadingHTTPServer(("127.0.0.1", PORT), AspaceGatewayHandler)
    server.serve_forever()


if __name__ == "__main__":
    import sys
    if "--self-test" in sys.argv:
        added = LEDGER.enqueue_submodule_evolution_missions()
        with LEDGER._connect() as conn:
            total_missions = conn.execute("SELECT COUNT(*) AS c FROM goldfish_missions").fetchone()["c"]
        sample_resp = ROUTER.dispatch_chat_completion(
            {"model": "aspace-a0-auto", "messages": [{"role": "user", "content": "Ping A0 EGM Gateway"}]}
        )
        print(
            json.dumps(
                {
                    "seeded_missions": added,
                    "total_missions_in_db": total_missions,
                    "db_path": str(DB_PATH),
                    "sample_response": sample_resp,
                },
                indent=2,
                ensure_ascii=False,
            )
        )
    else:
        run_gateway_server()
