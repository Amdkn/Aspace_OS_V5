"""AQuA factory reader — map V5 factory traces to AQuA evaluation cases.

Reads ``factory.sqlite`` (``02_Factory/factory.sqlite``) in READ-ONLY mode and
maps each durable workflow (``durable_workflows`` row, keyed by ``request_id``)
to ONE trace in the exact JSON shape AQuA ingests: a serialized ``EvalCase``
(``agentplatform._genai.types``), i.e. ``eval_case_id`` + ``agent_data``
(``agents`` + ``turns``), as produced by
``EvalCase.model_dump(mode="json", exclude_none=True)``.

Why this shape — the format AQuA expects, established from the code (see
``README.md`` for the full citation list):

* ``tools/trajectories/bundles.py:71`` — ``build_bundle(case, ...)`` takes an
  ``EvalCase`` whose ``agent_data`` holds the agent configurations and the
  conversation turns (docstring, lines 83-84); one turn becomes one
  ``TrajectoryStep`` indexed by its POSITION in ``agent_data.turns``
  (lines 109-118), not by the SDK's ``turn_index``.
* ``tools/trajectories/models.py:182`` (``TrajectoryManifest``) and ``:224``
  (``TrajectoryStep``) — the stored form: manifest (agents, step_count,
  status) + one row per turn, the turn being the serialized
  ``ConversationTurn`` dict.
* ``tools/ingestion/trace_converter.py:180`` — ``convert()`` builds
  ``AgentData(agents=..., turns=...)`` from OTEL traces: one trace becomes
  one ``ConversationTurn`` (lines 209-233); a span error becomes a
  ``function_response`` named ``"tool_error"`` (``_resolve_error_tool_name``,
  line 746).
* ``tests/test_trajectory_bundles.py`` (fixtures) and
  ``tests/conftest.py:1236`` — the constructor shapes: ``EvalCase``,
  ``AgentData(agents={agent_id: AgentConfig(agent_id, instruction)}, turns)``,
  ``ConversationTurn(turn_index, turn_id, events)``,
  ``AgentEvent(author, content=Content(role, parts=[Part(text=...)]))``.

Stdlib only (``sqlite3`` + ``json``). No Google dependency, no network call,
no write to the database — ever. The database is opened with
``mode=ro`` (URI) plus ``PRAGMA query_only = ON``.
"""

from __future__ import annotations

import argparse
import json
import sqlite3
import sys
from pathlib import Path

INGESTION_SOURCE = "factory_sqlite"
"""Value carried in provenance: this trace came from factory.sqlite."""

# --- Status vocabulary -----------------------------------------------------
# factory.ps1 writes, at intake time: workflows ``running``; steps ``running``
# or ``"waiting for writer lock: <holder>"``; resume moves ``paused`` /
# ``interrupted`` / ``asking`` back to ``running`` (factory.ps1 lines 291-294).
# Terminal values (``completed`` / ``failed``) are written by the execution
# loop, not by the intake — the classifier below is token-based on purpose so
# an unseen terminal spelling is classified, not silently dropped.

_FAILURE_TOKENS = ("fail", "error", "timeout", "abort", "crash")
_SUCCESS_VALUES = ("completed", "complete", "success", "succeeded", "done", "ok")
_IN_PROGRESS_VALUES = ("running", "paused", "interrupted", "asking")


def _is_failure(status: str | None) -> bool:
    s = (status or "").strip().lower()
    return any(tok in s for tok in _FAILURE_TOKENS)


def _is_success(status: str | None) -> bool:
    return (status or "").strip().lower() in _SUCCESS_VALUES


def _is_in_progress(status: str | None) -> bool:
    s = (status or "").strip().lower()
    return s in _IN_PROGRESS_VALUES or s.startswith("waiting for writer lock")


def classify_verdict(workflow_status: str | None, step_statuses: list[str | None]) -> str:
    """Workflow-level verdict, V5-side classification (not an AQuA field).

    ``failure`` if the workflow or any step failed; ``in_progress`` if the
    workflow or any step is still open; ``success`` only when the workflow
    and every step are terminal-success; ``unknown`` otherwise.
    """
    if _is_failure(workflow_status) or any(_is_failure(s) for s in step_statuses):
        return "failure"
    if _is_in_progress(workflow_status) or any(
        _is_in_progress(s) or not _is_success(s) for s in step_statuses
    ):
        return "in_progress"
    if _is_success(workflow_status) and all(_is_success(s) for s in step_statuses):
        return "success"
    return "unknown"


# --- Database ---------------------------------------------------------------


def open_readonly(db_path: str | Path) -> sqlite3.Connection:
    """Open a SQLite database strictly read-only (never creates, never writes)."""
    path = Path(db_path).expanduser().resolve()
    if not path.is_file():
        raise FileNotFoundError(f"factory.sqlite not found: {path}")
    conn = sqlite3.connect(f"{path.as_uri()}?mode=ro", uri=True)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA query_only = ON")
    return conn


def _fetch_workflows(conn: sqlite3.Connection) -> list[sqlite3.Row]:
    return conn.execute(
        "SELECT wid, request_id, owner_kind, owner_id, mode, status,"
        " model_pool, active_model, labels, created_at, updated_at"
        " FROM durable_workflows ORDER BY created_at, wid"
    ).fetchall()


def _fetch_steps(conn: sqlite3.Connection, wid: str) -> list[sqlite3.Row]:
    return conn.execute(
        "SELECT wid, step_key, seq, agent, harness, task, writer, worktree,"
        " hc_address, status, replay_policy, output, steers_json, attempts,"
        " updated_at FROM durable_steps WHERE wid = ? ORDER BY seq",
        (wid,),
    ).fetchall()


def _fetch_events(conn: sqlite3.Connection, wid: str) -> list[sqlite3.Row]:
    # The intake writes events with ticket_id = wid (factory.ps1 line 230),
    # so the workflow's journal is events.ticket_id = wid.
    return conn.execute(
        "SELECT id, ticket_id, phase, actor, verdict, detail, ts"
        " FROM events WHERE ticket_id = ? ORDER BY ts, id",
        (wid,),
    ).fetchall()


def _fetch_ticket(conn: sqlite3.Connection, wid: str) -> sqlite3.Row | None:
    # Opportunistic only: the intake does not create a ticket row for the
    # workflow, so a matching ticket is context when present, never required.
    return conn.execute(
        "SELECT id, source, thread_id, title, mandate, stage, risk, harness,"
        " worktree, branch, pr_url, created_at, updated_at"
        " FROM tickets WHERE id = ?",
        (wid,),
    ).fetchone()


# --- Mapping ----------------------------------------------------------------


def _text_part(text: str) -> dict:
    return {"text": text}


def _event(author: str, role: str, parts: list[dict], event_time: str | None) -> dict:
    ev: dict = {"author": author, "content": {"role": role, "parts": parts}}
    if event_time:
        ev["event_time"] = event_time
    return ev


def _map_step_to_turn(step: sqlite3.Row, turn_index: int) -> dict | None:
    """One durable step becomes one ConversationTurn.

    Returns None when the step carries neither a task nor an output and no
    failure signal — there is nothing conversational to emit; the step is
    still recorded in provenance with ``emitted_as_turn: false``.
    """
    task = (step["task"] or "").strip()
    output = (step["output"] or "").strip()
    status = step["status"] or ""
    agent = step["agent"] or "unknown"
    failed = _is_failure(status)

    events: list[dict] = []
    if task:
        # The assigned task is the instruction the worker received: a
        # user-role event, exactly as a user message opens a turn in AQuA.
        events.append(
            _event("user", "user", [_text_part(task)], step["updated_at"])
        )
    if output:
        events.append(
            _event(agent, "model", [_text_part(output)], step["updated_at"])
        )
    if failed:
        # AQuA's own OTEL converter promotes a runtime failure to a
        # function_response named "tool_error" (trace_converter.py:746).
        # The failure signal is the step's status — the only verdict the
        # factory records per step.
        failure_part = {
            "function_response": {
                "name": "tool_error",
                "response": {
                    "error": status,
                    "step_key": step["step_key"],
                    "agent": agent,
                    "attempts": step["attempts"],
                },
            }
        }
        if output:
            events[-1]["content"]["parts"].append(failure_part)
        else:
            events.append(
                _event(agent, "model", [failure_part], step["updated_at"])
            )
    if not events:
        return None
    return {
        "turn_index": turn_index,
        "turn_id": f"{step['wid']}:{step['step_key']}",
        "events": events,
    }


def _map_workflow(
    wf: sqlite3.Row,
    steps: list[sqlite3.Row],
    events: list[sqlite3.Row],
    ticket: sqlite3.Row | None,
) -> dict:
    """Map one workflow row (+ steps + events + optional ticket) to one case."""
    wid = wf["wid"]
    request_id = wf["request_id"] or wid

    turns: list[dict] = []
    agents: dict[str, dict] = {}
    step_summaries: list[dict] = []
    for step in steps:
        turn = _map_step_to_turn(step, len(turns))
        step_summaries.append(
            {
                "step_key": step["step_key"],
                "seq": step["seq"],
                "agent": step["agent"],
                "harness": step["harness"],
                "status": step["status"],
                "writer": step["writer"],
                "worktree": step["worktree"],
                "hc_address": step["hc_address"],
                "replay_policy": step["replay_policy"],
                "attempts": step["attempts"],
                "updated_at": step["updated_at"],
                "emitted_as_turn": turn is not None,
            }
        )
        if turn is not None:
            turns.append(turn)
        agent = step["agent"]
        if agent and agent not in agents:
            agents[agent] = {
                "agent_id": agent,
                "instruction": (
                    f"Worker V5 — Compagnon {agent} (harness {step['harness']})."
                ),
                "description": (
                    "Agent observé V5 — trace factory.sqlite, workflow "
                    f"{wid}, worktree {step['worktree']}."
                ),
            }

    verdict = classify_verdict(
        wf["status"], [s["status"] for s in steps]
    )

    case: dict = {
        "eval_case_id": request_id,
        "agent_data": {"agents": agents, "turns": turns},
        "aspace_provenance": {
            "wid": wid,
            "mode": wf["mode"],
            "status": wf["status"],
            "verdict": verdict,
            "model_pool": wf["model_pool"],
            "active_model": wf["active_model"],
            "labels": wf["labels"],
            "owner_kind": wf["owner_kind"],
            "owner_id": wf["owner_id"],
            "created_at": wf["created_at"],
            "updated_at": wf["updated_at"],
            "ingestion_source": INGESTION_SOURCE,
            "source": "factory.sqlite",
            "ticket": (
                {
                    "id": ticket["id"],
                    "source": ticket["source"],
                    "thread_id": ticket["thread_id"],
                    "title": ticket["title"],
                    "mandate": ticket["mandate"],
                    "stage": ticket["stage"],
                    "risk": ticket["risk"],
                    "harness": ticket["harness"],
                    "worktree": ticket["worktree"],
                    "branch": ticket["branch"],
                    "pr_url": ticket["pr_url"],
                    "created_at": ticket["created_at"],
                    "updated_at": ticket["updated_at"],
                }
                if ticket is not None
                else None
            ),
            # Journal milestones (events.ticket_id = wid). They are NOT
            # conversation turns — they are the workflow's journal, kept
            # as metadata so diagnosis can use them without pretending
            # they are agent utterances.
            "events": [
                {
                    "phase": e["phase"],
                    "actor": e["actor"],
                    "verdict": e["verdict"],
                    "detail": e["detail"],
                    "ts": e["ts"],
                }
                for e in events
            ],
            "steps": step_summaries,
        },
    }
    return case


def read_traces(db_path: str | Path) -> list[dict]:
    """Read every durable workflow from factory.sqlite and map it to a case.

    One workflow = one trace = one EvalCase-shaped dict (plus the
    ``aspace_provenance`` extension block, which R3 strips before
    constructing the SDK ``EvalCase``). The database is opened read-only;
    this function never writes.
    """
    conn = open_readonly(db_path)
    try:
        traces = []
        for wf in _fetch_workflows(conn):
            steps = _fetch_steps(conn, wf["wid"])
            events = _fetch_events(conn, wf["wid"])
            ticket = _fetch_ticket(conn, wf["wid"])
            traces.append(_map_workflow(wf, steps, events, ticket))
        return traces
    finally:
        conn.close()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Map factory.sqlite durable workflows to AQuA EvalCase JSONL."
    )
    parser.add_argument("--db", required=True, help="Path to factory.sqlite")
    parser.add_argument(
        "--out", required=True, help="Output JSONL file (one trace per line)"
    )
    args = parser.parse_args(argv)

    try:
        traces = read_traces(args.db)
    except (FileNotFoundError, sqlite3.Error) as exc:
        print(f"aqua_factory_reader: {exc}", file=sys.stderr)
        return 1

    out_path = Path(args.out)
    with out_path.open("w", encoding="utf-8") as fh:
        for trace in traces:
            fh.write(json.dumps(trace, ensure_ascii=False) + "\n")
    print(f"aqua_factory_reader: {len(traces)} trace(s) -> {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
