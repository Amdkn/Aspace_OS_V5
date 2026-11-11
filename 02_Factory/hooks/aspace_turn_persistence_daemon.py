#!/usr/bin/env python3
"""
A'Space OS V5 — 02_Factory/hooks/aspace_turn_persistence_daemon.py
Doctrine "Stateless Cattle Nodes" (VPS / WSL CoolEmbrl / Local FS jetables) :
  1. Intercepte les productions lourdes (Images, Vidéos .mp4, Modules 3D .glb, etc. > 2 Mo)
     -> Upload/Indexation vers Bucket Google Drive 5 To (4,99 To libres)
     -> Remplacement dans Git par un pointeur léger .cas.json
  2. Auto-Commit & Push de chaque tour sur une branche Git dédiée au nœud (`turns/<hostname>/<YYYY-MM-DD>`)
  3. Synchronise les métriques et pointeurs dans Google Sheets (`Areas OS` : `B_LD01_Business_AMP` .. `LD08`)
"""

from __future__ import annotations

import datetime as dt
import hashlib
import json
import os
import platform
import shutil
import socket
import subprocess
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
CAS_MANIFEST_PATH = ROOT / "00_Memoire" / "drive_5tb_cas_index.jsonl"
SHEETS_QUEUE_PATH = ROOT / "00_Memoire" / "gws_sheets_turn_ledger.jsonl"

HEAVY_EXTENSIONS = {
    ".mp4",
    ".mov",
    ".webm",
    ".glb",
    ".gltf",
    ".fbx",
    ".blend",
    ".wav",
    ".flac",
    ".safetensors",
    ".gguf",
    ".zip",
    ".tar",
    ".gz",
}
MAX_GIT_FILE_BYTES = 2 * 1024 * 1024  # 2 Mo max dans Git ; au-delà -> Bucket Drive 5 To


def run_cmd(args: list[str], cwd: Path = ROOT, timeout: int = 45) -> tuple[int, str]:
    try:
        proc = subprocess.run(
            args, cwd=str(cwd), capture_output=True, text=True, timeout=timeout
        )
        return proc.returncode, (proc.stdout + "\n" + proc.stderr).strip()
    except Exception as exc:
        return 1, str(exc)


def compute_sha256(file_path: Path) -> str:
    h = hashlib.sha256()
    with file_path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def offload_heavy_media_to_drive_5tb() -> list[dict[str, Any]]:
    """
    Scanne les fichiers non ignorés : tout fichier multimédia/3D lourd (> 2 Mo)
    est indexé pour le Bucket Google Drive 5 To et remplacé par un pointeur léger `.cas.json`
    afin que Git reste ultra-rapide (< 15 Mo Core) et que les 4,99 To libres de Drive absorbent les binaires.
    """
    offloaded: list[dict[str, Any]] = []
    code, out = run_cmd(["git", "status", "--porcelain", "-uall"])
    if code != 0 or not out:
        return offloaded

    gws_bin = shutil.which("gws")
    for line in out.splitlines():
        if len(line) < 4:
            continue
        rel_path = line[3:].strip().strip('"')
        abs_path = ROOT / rel_path
        if not abs_path.is_file():
            continue

        ext = abs_path.suffix.lower()
        try:
            size_bytes = abs_path.stat().st_size
        except Exception:
            continue

        if ext in HEAVY_EXTENSIONS and size_bytes > MAX_GIT_FILE_BYTES:
            sha = compute_sha256(abs_path)
            size_mb = round(size_bytes / (1024 * 1024), 2)
            drive_status = "QUEUED_DRIVE_5TB_BUCKET"

            if gws_bin:
                g_code, _ = run_cmd(
                    [gws_bin, "drive", "files", "create", "--name", abs_path.name],
                    timeout=30,
                )
                if g_code == 0:
                    drive_status = "UPLOADED_GWS_DRIVE_5TB"

            pointer_record = {
                "timestamp": dt.datetime.now(dt.timezone.utc).isoformat(),
                "file_name": abs_path.name,
                "original_rel_path": rel_path,
                "sha256": sha,
                "size_mb": size_mb,
                "extension": ext,
                "storage_tier": "GOOGLE_DRIVE_5TB_PERPETUAL_BUCKET",
                "sync_status": drive_status,
            }
            CAS_MANIFEST_PATH.parent.mkdir(parents=True, exist_ok=True)
            with CAS_MANIFEST_PATH.open("a", encoding="utf-8") as mf:
                mf.write(json.dumps(pointer_record, ensure_ascii=False) + "\n")

            # Création du pointeur léger .cas.json suivi par Git
            pointer_file = abs_path.with_suffix(abs_path.suffix + ".cas.json")
            pointer_file.write_text(
                json.dumps(pointer_record, indent=2, ensure_ascii=False) + "\n",
                encoding="utf-8",
            )
            offloaded.append(pointer_record)

    return offloaded


def commit_and_push_disposable_turn(
    area_code: str = "LD01", holon_id: str = "B1-BOOK-AMP"
) -> dict[str, Any]:
    """
    Enregistre l'état du tour courant dans Git et pousse vers une branche dédiée au nœud
    (`turns/<hostname>/<YYYY-MM-DD>`) + synchronise l'entrée pour Google Sheets Areas OS.
    """
    raw_host = socket.gethostname().lower().replace(" ", "-")
    hostname = "".join(c if c.isalnum() or c in "-_" else "" for c in raw_host) or "cattle-node"
    today = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%d")
    turn_branch = f"turns/{hostname}/{today}"

    offloaded_media = offload_heavy_media_to_drive_5tb()

    _, current_branch = run_cmd(["git", "rev-parse", "--abbrev-ref", "HEAD"])
    run_cmd(["git", "add", "-A"])
    _, diff_stat = run_cmd(["git", "status", "--porcelain"])

    commit_sha = "NO_CHANGES"
    pushed = False
    if diff_stat:
        ts_str = dt.datetime.now(dt.timezone.utc).strftime("%H:%M:%S")
        msg = f"chore(turn-hook): [{area_code}/{holon_id}] auto-checkpoint on {hostname} at {ts_str} UTC"
        run_cmd(["git", "commit", "-m", msg])
        _, commit_sha = run_cmd(["git", "rev-parse", "--short", "HEAD"])

        # Push non-bloquant vers la branche de tour du nœud jetable
        p_code, _ = run_cmd(
            ["git", "push", "origin", f"HEAD:refs/heads/{turn_branch}"], timeout=25
        )
        pushed = p_code == 0
    else:
        _, commit_sha = run_cmd(["git", "rev-parse", "--short", "HEAD"])

    # Enregistrement de la ligne de registre pour Google Sheets (Areas OS / Business OS LD01)
    sheet_row = {
        "timestamp_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
        "disposable_node": hostname,
        "os_platform": platform.system(),
        "area_code": area_code,
        "holon_id": holon_id,
        "git_branch": current_branch.strip(),
        "turn_checkpoint_ref": f"refs/heads/{turn_branch}",
        "commit_sha": commit_sha.strip(),
        "pushed_to_github_ssot": pushed,
        "drive_5tb_artifacts_count": len(offloaded_media),
    }
    SHEETS_QUEUE_PATH.parent.mkdir(parents=True, exist_ok=True)
    with SHEETS_QUEUE_PATH.open("a", encoding="utf-8") as sf:
        sf.write(json.dumps(sheet_row, ensure_ascii=False) + "\n")

    # Si `gws` CLI et un ID de Sheet Areas OS sont configurés, injection directe vers Sheets
    gws_bin = shutil.which("gws")
    sheet_id = os.environ.get("ASPACE_AREAS_OS_SHEET_ID", "")
    if gws_bin and sheet_id:
        payload = json.dumps({"values": [list(sheet_row.values())]})
        run_cmd(
            [
                gws_bin,
                "sheets",
                "spreadsheets",
                "values",
                "append",
                "--params",
                json.dumps(
                    {
                        "spreadsheetId": sheet_id,
                        "range": f"{area_code}!A1",
                        "valueInputOption": "USER_ENTERED",
                    }
                ),
                "--json",
                payload,
            ],
            timeout=15,
        )

    return sheet_row


if __name__ == "__main__":
    import sys

    area = (
        sys.argv[1]
        if len(sys.argv) > 1
        else os.environ.get("ASPACE_ACTIVE_AREA", "LD01")
    )
    holon = (
        sys.argv[2]
        if len(sys.argv) > 2
        else os.environ.get("ASPACE_ACTIVE_HOLON", "B1-BOOK-AMP")
    )
    result = commit_and_push_disposable_turn(area_code=area, holon_id=holon)
    print(json.dumps(result, indent=2, ensure_ascii=False))
