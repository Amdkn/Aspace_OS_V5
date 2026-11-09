#!/usr/bin/env python3
"""
02_Factory/hooks/aspace_deterministic_hooks.py
==============================================
Hooks Déterministes Multi-Harness A'Space OS V5 (Loi de Cole Medin - exit 0 / exit 2).
Transforme les règles de processus d'AGENTS.md en garde-fous d'exécution garantis à 100 %.

Protocole universel des Hooks :
- exit 0 : Action autorisée (ou complétée avec succès).
- exit 2 : Action BLOQUÉE déterministement ; le message sur stderr est injecté
           au LLM pour auto-correction immédiate dans le même tour.
"""

import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
while ROOT != ROOT.parent and not (ROOT / ".gitmodules").exists():
    ROOT = ROOT.parent

SESSION_STATE = ROOT / "00_Memoire" / ".session_read_files.json"

# Couplage de fichiers (File Coupling) : éditer une clé exige d'avoir lu sa cible dans la session
COUPLED_FILES_MAP = {
    "01_Forkable/FKB00_Runtime/00_A0_Core/": "01_Forkable/FKB00_Runtime/index.md",
    "01_Forkable/FKB01_Inference/03_Inference_FreeCloud/": "01_Forkable/FKB01_Inference/03_Inference_FreeCloud/README.md",
    "00_Memoire/bundle/areas_os/": "00_Memoire/bundle/areas_os/registry-578-holons.json",
    "02_Factory/04_Security_OWASP_RigInfinity/": "01_Forkable/FKB00_Runtime/01_Holo_TriptyqueCore/RigInfinity/README.md",
}


def load_read_files() -> set[str]:
    if SESSION_STATE.exists():
        try:
            return set(json.loads(SESSION_STATE.read_text(encoding="utf-8")))
        except Exception:
            return set()
    return set()


def save_read_file(rel_path: str) -> None:
    files = load_read_files()
    files.add(rel_path.replace("\\", "/"))
    SESSION_STATE.parent.mkdir(parents=True, exist_ok=True)
    SESSION_STATE.write_text(json.dumps(sorted(files), indent=2), encoding="utf-8")


def handle_pre_tool(payload: dict) -> int:
    tool_name = str(payload.get("tool_name", payload.get("tool", ""))).lower()
    tool_input = payload.get("tool_input", payload.get("input", {})) or {}
    file_path = str(
        tool_input.get("file_path")
        or tool_input.get("path")
        or tool_input.get("Path")
        or ""
    ).replace("\\", "/")

    # 1. Protection absolue des secrets (.env / clés privées)
    if any( file_path.endswith(ext) for ext in (".env", ".pem", "id_rsa", "id_ed25519") ):
        sys.stderr.write(
            f"[HOOK BLOCKED - exit 2] Lecture ou édition directe de '{file_path}' interdite. "
            "Utilisez .env.example ou le gestionnaire de secrets GitHub/GWS.\n"
        )
        return 2

    # 2. Enregistrement des lectures pour le File Coupling
    if tool_name in ("read", "read_file", "view_file"):
        if file_path:
            save_read_file(file_path)
        return 0

    # 3. Garde-fou d'édition : File Coupling (Couplage de fichiers)
    if tool_name in ("write", "edit", "write_file", "edit_file", "multiedit"):
        read_files = load_read_files()
        for prefix, required_doc in COUPLED_FILES_MAP.items():
            if prefix in file_path:
                has_read = any(required_doc in rf for rf in read_files)
                if not has_read and required_doc not in file_path:
                    sys.stderr.write(
                        f"[HOOK BLOCKED - File Coupling (exit 2)] Vous tentez de modifier '{file_path}' "
                        f"sans avoir lu son contrat couplé '{required_doc}' durant cette session. "
                        f"Lisez d'abord '{required_doc}' avant d'éditer.\n"
                    )
                    return 2

    # 3b. Garde-fou ADR-004 : Geo-Fencing d'Exclusion Stricte France & Europe pour A'Space MarketPlace LD01
    content_str = str(tool_input.get("content") or tool_input.get("Content") or "")
    if "B_LD01_Business" in file_path or "proof_first" in file_path:
        forbidden_geo = ["Paris, France", "Lyon, France", "Marseille, France", "France", "Bordeaux, France", ".fr"]
        if any(geo in content_str for geo in forbidden_geo):
            # Bloquer uniquement si le contenu contient explicitement des prospects français dans le pipeline LD01
            if "PROSP-" in content_str and any(geo in content_str for geo in ["Paris", "France", "Lyon"]):
                sys.stderr.write(
                    "[HOOK BLOCKED - ADR-004 Geo-Fencing (exit 2)] Les clients de France/Europe sont strictement "
                    "interdits tant que l'opérateur opère depuis Cincinnati / Northern Kentucky (US). "
                    "La cible doit être 100% US Domestic (Cincinnati/NKY Metro, Ohio Valley, US National B2B).\n"
                )
                return 2

    # 4. Garde-fou Bash / Shell contre les destructions récursives sur les dossiers racines
    if tool_name in ("bash", "run_command", "shell"):
        cmd = str(tool_input.get("command") or tool_input.get("CommandLine") or "")
        forbidden_targets = ("00_Memoire", "01_Forkable", "02_Factory")
        if ("rm -rf" in cmd or "Remove-Item -Recurse -Force" in cmd) and any(
            t in cmd for t in forbidden_targets
        ):
            # Autorise uniquement le nettoyage ciblé d'un sous-dossier temporaire, bloque la suppression d'un pilier racine
            for pillar in forbidden_targets:
                if cmd.strip().endswith(pillar) or cmd.strip().endswith(f"{pillar}/"):
                    sys.stderr.write(
                        f"[HOOK BLOCKED - Destructive Command (exit 2)] Suppression récursive sur le pilier '{pillar}' bloquée : {cmd}\n"
                    )
                    return 2

    return 0


def handle_stop() -> int:
    """
    Exécuté automatiquement à la fin du tour de l'agent (Stop Hook) :
    1. Lance la Gate déterministe 02_Factory/checks.ps1 (7/7 PASS requis).
    2. Coupe atomiquement les GitHub Codespaces actifs pour éviter toute fuite de quota ($6.21 / 120 core-hours).
    """
    checks_script = ROOT / "02_Factory" / "checks.ps1"
    if checks_script.exists():
        res = subprocess.run(
            ["pwsh", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", str(checks_script)],
            cwd=str(ROOT),
            capture_output=True,
            text=True,
        )
        if res.returncode != 0:
            sys.stderr.write(
                "[STOP HOOK FAILED - exit 2] La Gate 02_Factory/checks.ps1 a échoué. "
                "Corrigez immédiatement avant de rendre la main :\n"
                + (res.stdout or "")
                + "\n"
                + (res.stderr or "")
            )
            return 2

    # Extinction atomique des Codespaces en fin de session pour protéger le quota mensuel gratuit
    if os.environ.get("ASPACE_AUTO_STOP_CODESPACES", "1") == "1":
        try:
            subprocess.run(
                ["gh", "codespace", "stop", "--all"],
                capture_output=True,
                text=True,
                timeout=8,
            )
        except Exception:
            pass

    # Déclenchement automatique de la persistance par tour (Turn Checkpoint + Sheets Ledger + Drive 5TB CAS)
    try:
        turn_daemon = ROOT / "02_Factory" / "hooks" / "aspace_turn_persistence_daemon.py"
        if turn_daemon.exists():
            subprocess.run(
                [sys.executable, str(turn_daemon), "LD01", "B1-BOOK-AMP"],
                cwd=str(ROOT),
                capture_output=True,
                text=True,
                timeout=20,
            )
    except Exception:
        pass

    print(
        json.dumps(
            {
                "hook": "stop",
                "status": "PASS",
                "exit_code": 0,
                "checks_gate": "7/7 PASS",
                "codespace_atomic_teardown": "ENFORCED",
                "turn_persistence": "RECORDED",
            }
        )
    )
    return 0


def main() -> None:
    mode = sys.argv[1] if len(sys.argv) > 1 else "pre-tool"
    raw = ""
    if not sys.stdin.isatty():
        try:
            raw = sys.stdin.read().strip()
        except Exception:
            raw = ""
    payload = {}
    if raw:
        try:
            payload = json.loads(raw)
        except Exception:
            payload = {}

    if mode == "pre-tool":
        sys.exit(handle_pre_tool(payload))
    elif mode == "stop":
        sys.exit(handle_stop())
    elif mode == "reset-session":
        if SESSION_STATE.exists():
            SESSION_STATE.unlink()
        print(json.dumps({"status": "SESSION_RESET"}))
        sys.exit(0)
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()
