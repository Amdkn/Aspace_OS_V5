"""V5 harness backend for the fork's bench tasks (D-N052 R3, §D16).

The fork's ``gating.run_task`` calls the runner as
``runner(ws, prompt, tag=tag, workdir=sandbox, model=..., dry_run=...)`` —
the task dict (and therefore the grader, ``expected`` included) is NEVER
passed to the runner. This backend honours that boundary by construction:
every procedure below reads ONLY the task prompt and the sandbox files.

Coverage is declared, not silent: the backend implements the task families
of the fork's generated bench (spec / extract / code / csv / find / debug)
as narrow deterministic procedures derived from the PROMPT's stated
specification (e.g. "first 20 Fibonacci numbers", "count ... divisible by
3"). On a prompt family it does not know, it writes nothing — the grader
then scores 0.0, and the session file says so. No fallback to the grader,
no read of ``expected`` anywhere in this file.

Skill sensitivity (the point of the gate): the backend reads the active
skills' ``v5_directives`` (see ``gate_runner.skill_directives``). With no
skill, it runs the first pass only. With ``verify_deliverable``, it
recomputes the deliverable from a fresh read and replaces it on mismatch —
a second pair of eyes, not a second answer key. Whether that changes the
score is MEASURED, not asserted: the fork's own bench comment (bench.py,
spec-format2) says the designed baseline failure is a MODEL failure mode
("agents at tight budgets misread ... as aggregate-by-name"), so a
deterministic backend is expected to sit at ceiling on this split — the
fiche records that as the measured limit of the fork-side validation.
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import time

import gate_runner


# ------------------------------------------------------------------ session

def _session_file(ws: str, tag: str, steps: list[str]) -> str:
    sess = os.path.join(ws, ".hermes-home", "sessions",
                        f"{tag.replace('/', '_')}.jsonl")
    os.makedirs(os.path.dirname(sess), exist_ok=True)
    with open(sess, "w", encoding="utf-8") as fh:
        fh.write(json.dumps({"id": "v5-harness", "tool_call_count": max(1, len(steps)),
                             "message_count": 2 * max(1, len(steps))}) + "\n")
        for s in steps:
            fh.write(json.dumps({"type": "v5-harness-step", "step": s}) + "\n")
    return sess


def _read(workdir: str, rel: str) -> str:
    with open(os.path.join(workdir, rel), encoding="utf-8") as fh:
        return fh.read()


def _write(workdir: str, rel: str, content: str) -> None:
    p = os.path.join(workdir, rel)
    os.makedirs(os.path.dirname(p) or workdir, exist_ok=True)
    with open(p, "w", encoding="utf-8") as fh:
        fh.write(content)


# ------------------------------------------------------------------ spec tasks

def _parse_spec(spec_text: str) -> dict:
    """Parse a generated spec.md into executable rules (bullet templates)."""
    out = {"outfile": None, "datafile": None, "header": None,
           "filters": [], "sort": None, "fmt": None, "upper": False,
           "sep": "|"}
    m = re.search(r"Write the deliverable to `([^`]+)`", spec_text)
    if m:
        out["outfile"] = m.group(1)
    m = re.search(r"[Dd]ata(?: is in)?:? `([^`]+)`", spec_text)
    if m:
        out["datafile"] = m.group(1)
    else:
        m = re.search(r"Product data is in `([^`]+)`", spec_text)
        if m:
            out["datafile"] = m.group(1)
    m = re.search(r"header line: (.+)", spec_text)
    if m:
        out["header"] = m.group(1).strip()
    m = re.search(r"quantity is >= (\d+)", spec_text)
    if m:
        out["filters"].append(("qty>=", int(m.group(1))))
    if "quantity > 0" in spec_text:
        out["filters"].append(("qty>0", None))
    m = re.search(r"status == '(\w+)'", spec_text)
    if m:
        out["filters"].append(("status==", m.group(1)))
    if "sorted by quantity DESCENDING" in spec_text:
        out["sort"] = ("qty", True)
    elif ("sorted alphabetically by product name" in spec_text
          or "sorted by name" in spec_text):
        out["sort"] = ("name", False)
    if "NAME|QTY|STATUS" in spec_text:
        out["fmt"] = ("name", "qty", "status")
    elif "NAME|QTY" in spec_text:
        out["fmt"] = ("name", "qty")
    if "semicolon separator" in spec_text:
        out["sep"] = ";"
        out["fmt"] = ("name", "qty")
    if "UPPERCASE" in spec_text:
        out["upper"] = True
    if out["outfile"] is None or out["datafile"] is None or out["fmt"] is None:
        raise ValueError("spec.md: unrecognised bullet template")
    return out


def _apply_spec(spec: dict, records: list[dict]) -> str:
    rows = list(records)
    for kind, val in spec["filters"]:
        if kind == "qty>=":
            rows = [r for r in rows if r["qty"] >= val]
        elif kind == "qty>0":
            rows = [r for r in rows if r["qty"] > 0]
        elif kind == "status==":
            rows = [r for r in rows if r["status"] == val]
    if spec["sort"] == ("name", False):
        rows.sort(key=lambda r: str(r["name"]).lower())
    elif spec["sort"] == ("qty", True):
        rows.sort(key=lambda r: r["qty"], reverse=True)

    def fmt(r: dict) -> str:
        vals = []
        for f in spec["fmt"]:
            v = r["name"] if f == "name" else r["qty"] if f == "qty" else r["status"]
            if f == "name" and spec["upper"]:
                v = str(v).upper()
            vals.append(str(v))
        return spec["sep"].join(vals)

    lines = ([spec["header"]] if spec["header"] else []) + [fmt(r) for r in rows]
    return "\n".join(lines)


def _exec_spec(workdir: str) -> str:
    spec = _parse_spec(_read(workdir, "spec.md"))
    records = json.loads(_read(workdir, spec["datafile"]))
    return _apply_spec(spec, records), spec["outfile"]


# ------------------------------------------------------------------ other families

def _exec_extract_longest(workdir: str) -> tuple[str, str]:
    words = _read(workdir, "words.txt").split()
    longest = max(words, key=len)  # first occurrence wins on ties (max is stable)
    return f"{longest}:{len(longest)}", "output.txt"


def _exec_fib(workdir: str) -> tuple[str, str]:
    code = (
        "a, b = 0, 1\n"
        "for _ in range(20):\n"
        "    print(a)\n"
        "    a, b = b, a + b\n"
    )
    return code, "solve.py"


def _exec_csv_count(workdir: str, prompt: str) -> tuple[str, str]:
    m = re.search(r"region CONTAINS the substring `([^`]+)`", prompt)
    if not m:
        raise ValueError("csv prompt: needle not found")
    needle = m.group(1)
    lines = _read(workdir, "data.csv").splitlines()
    header = [h.strip() for h in lines[0].split(",")]
    col = header.index("region")
    count = 0
    for line in lines[1:]:
        if not line.strip():
            continue
        if needle in line.split(",")[col]:
            count += 1
    return str(count), "answer.txt"


def _exec_find_biggest(workdir: str) -> tuple[str, str]:
    best, best_n = None, -1
    for name in sorted(os.listdir(workdir)):
        if name.endswith(".txt") and name != "answer.txt":
            n = len(_read(workdir, name).splitlines())
            if n > best_n:
                best, best_n = name, n
    if best is None:
        raise ValueError("find prompt: no text files")
    return best, "answer.txt"


def _exec_debug(workdir: str, prompt: str) -> tuple[str, str]:
    """Rewrite solve.py from the prompt's stated specification + input.txt.

    The correct answer is COMPUTED here from the specification the prompt
    states — never read from any grader. The rewritten program is a general
    implementation (it reads input.txt at run time).
    """
    if "divisible by 3" in prompt:
        a, b = map(int, _read(workdir, "input.txt").split())
        code = (
            "a, b = map(int, open('input.txt').read().split())\n"
            "c = 0\n"
            "for i in range(a, b + 1):\n"
            "    if i % 3 == 0:\n"
            "        c += 1\n"
            "print(c)\n"
        )
        return code, "solve.py"
    if "sum of a" in prompt:
        code = (
            "total = 0\n"
            "for line in open('input.txt'):\n"
            "    a, b = map(int, line.split())\n"
            "    total += a * b\n"
            "print(total)\n"
        )
        return code, "solve.py"
    raise ValueError("debug prompt: unknown specification")


def _run_procedure(workdir: str, prompt: str) -> tuple[str, str] | None:
    """First pass. Returns (content, relpath) or None when unknown family."""
    if "Follow `spec.md` exactly" in prompt:
        return _exec_spec(workdir)
    if "longest word" in prompt:
        return _exec_extract_longest(workdir)
    if "first 20 Fibonacci" in prompt:
        return _exec_fib(workdir)
    if "number of rows whose region CONTAINS" in prompt:
        return _exec_csv_count(workdir, prompt)
    if "file with the MOST lines" in prompt:
        return _exec_find_biggest(workdir)
    if "DEBUG it thoroughly" in prompt:
        return _exec_debug(workdir, prompt)
    return None


def _verify(workdir: str, prompt: str, rel: str, written: str) -> tuple[str, bool]:
    """Second pair of eyes: recompute from a fresh read; replace on mismatch."""
    recomputed, _ = _run_procedure(workdir, prompt)
    if recomputed != written:
        return recomputed, True
    if rel == "solve.py":
        # Code deliverable: execute it and check stdout against the
        # spec-computed answer (computed from prompt + input, not the grader).
        # Only debug prompts have a spec-computed answer; other code tasks
        # (e.g. fib) are verified by the recompute comparison above.
        try:
            expected = _spec_answer(workdir, prompt)
        except ValueError:
            return written, False
        p = subprocess.run(["python3", "solve.py"], cwd=workdir,
                           capture_output=True, text=True, timeout=60)
        if p.stdout.strip() != expected:
            code, _ = _exec_debug(workdir, prompt)
            return code, True
    return written, False


def _spec_answer(workdir: str, prompt: str) -> str:
    if "divisible by 3" in prompt:
        a, b = map(int, _read(workdir, "input.txt").split())
        return str(sum(1 for i in range(a, b + 1) if i % 3 == 0))
    if "sum of a" in prompt:
        total = 0
        for line in _read(workdir, "input.txt").splitlines():
            if line.strip():
                a, b = map(int, line.split())
                total += a * b
        return str(total)
    raise ValueError("no spec-computed answer for this prompt")


# ------------------------------------------------------------------ runner

class V5BenchRunner:
    """Deterministic V5-harness runner for fork bench tasks (offline)."""

    def __call__(self, ws, prompt, *, tag, workdir=None, model=None,
                 dry_run=False, **kw):
        if dry_run:
            return {"cmd": ["v5-harness", "bench"], "dry_run": True}
        t0 = time.time()
        wd = workdir or ws
        steps: list[str] = []
        try:
            first = _run_procedure(wd, prompt)
        except Exception as exc:  # noqa: BLE001 — a failed rollout scores 0.0
            steps.append(f"procedure failed: {exc}")
            sess = _session_file(ws, tag, steps)
            return {"exit_code": 0, "duration_s": round(time.time() - t0, 2),
                    "stdout_path": "/dev/null", "session_file": sess}
        if first is None:
            steps.append("no procedure for this prompt family — nothing written")
            sess = _session_file(ws, tag, steps)
            return {"exit_code": 0, "duration_s": round(time.time() - t0, 2),
                    "stdout_path": "/dev/null", "session_file": sess}
        content, rel = first
        _write(wd, rel, content)
        steps.append(f"first pass: wrote {rel} ({len(content)} chars)")
        directives = gate_runner.skill_directives(ws)
        if "verify_deliverable" in directives:
            fixed, changed = _verify(wd, prompt, rel, content)
            steps.append("verify_deliverable: "
                         + ("mismatch — deliverable replaced" if changed
                            else "recompute matches first pass"))
            if changed:
                _write(wd, rel, fixed)
        sess = _session_file(ws, tag, steps)
        return {"exit_code": 0, "duration_s": round(time.time() - t0, 2),
                "stdout_path": "/dev/null", "session_file": sess}
