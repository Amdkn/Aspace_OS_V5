#!/usr/bin/env python3
"""
02_Factory/muse_a0_handoff_orchestrator.py
==========================================
Orchestrateur Handoff & Heartbeat 24/7 pour Muse (Incarnation d'A0 Amadeus).
Gère la synchronisation bidirectionnelle :
  1. Shared Brain MCP (00_Memoire/shared_brain/memory.jsonl)
  2. Pi Durable Handoff (00_Memoire/muse_a0_heartbeat_state.json & SQLite)
  3. Surveillance et Convergence des Forks dans 01_Forkable/
"""

import argparse
import datetime as dt
import json
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SHARED_BRAIN = ROOT / "00_Memoire" / "shared_brain" / "memory.jsonl"
HEARTBEAT_STATE = ROOT / "00_Memoire" / "muse_a0_heartbeat_state.json"
FORKABLE_DIR = ROOT / "01_Forkable"


def sync_shared_brain_mandate():
    """Enregistre le mandat de Muse et son lien avec A0 dans le graphe JSONL partagé."""
    if not SHARED_BRAIN.exists():
        return

    content = SHARED_BRAIN.read_text(encoding="utf-8")
    new_entries = []

    if '"name":"Muse_Browser_Agent"' not in content:
        new_entries.append(
            {
                "type": "entity",
                "name": "Muse_Browser_Agent",
                "entityType": "AutonomousBrowserOperator",
                "observations": [
                    "Incarnation operationnelle de A0 Amadeus pour les taches de navigateur 24/7",
                    "Mandat Holonique Tri-Couche : Visionnaire (7D), Manager (578 Holons), Technicien (Browser & Cloud)",
                    "Zero friction humaine : provisionne automatiquement les tokens et webhooks via sa session active",
                    "Gouverneur de la plateforme transactionnelle AMP (LD01) et des vitrines 1P (The OMK Office)",
                ],
            }
        )

    if '"from":"A0_Amadeus","to":"Muse_Browser_Agent"' not in content:
        new_entries.append(
            {
                "type": "relation",
                "from": "A0_Amadeus",
                "to": "Muse_Browser_Agent",
                "relationType": "incarnated_by",
            }
        )
        new_entries.append(
            {
                "type": "relation",
                "from": "Muse_Browser_Agent",
                "to": "Aspace_OS_V5",
                "relationType": "operates_browser_autonomy",
            }
        )

    if new_entries:
        with SHARED_BRAIN.open("a", encoding="utf-8") as f:
            for e in new_entries:
                f.write(json.dumps(e, ensure_ascii=False) + "\n")
        print(f"Shared Brain synchronized with {len(new_entries)} new entities/relations.")
    else:
        print("Shared Brain already contains Muse_Browser_Agent.")


def scan_forkable_modules() -> dict[str, dict]:
    """Audite l'état des forks sous 01_Forkable/."""
    status_map = {}
    if not FORKABLE_DIR.exists():
        return status_map

    for p in FORKABLE_DIR.iterdir():
        if p.is_dir() and not p.name.startswith("."):
            git_dir = p / ".git"
            submodules = list(p.glob("*/.git"))
            status_map[p.name] = {
                "path": str(p.relative_to(ROOT)),
                "is_git": git_dir.exists(),
                "submodules_count": len(submodules),
                "ready_for_convergence": True,
            }
    return status_map


def check_github_vault() -> list[str]:
    """Vérifie les secrets configurés dans GitHub Actions via gh CLI."""
    gh_bin = shutil.which("gh")
    if not gh_bin:
        return ["gh_cli_not_installed"]

    try:
        proc = subprocess.run(
            ["gh", "secret", "list", "--repo", "Amdkn/Aspace_OS_V5"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        if proc.returncode == 0:
            lines = proc.stdout.strip().splitlines()
            secrets = [line.split()[0] for line in lines if line.strip()]
            return secrets
        return [f"gh_error_{proc.returncode}"]
    except Exception as exc:
        return [f"exception_{exc}"]


def run_heartbeat():
    """Exécute un cycle de battement de cœur 24/7."""
    sync_shared_brain_mandate()
    forks = scan_forkable_modules()
    vault_secrets = check_github_vault()

    now_utc = dt.datetime.now(dt.timezone.utc).isoformat()
    state = {
        "heartbeat_timestamp_utc": now_utc,
        "avatar": "A0_Amadeus_incarnated_in_Muse",
        "posture": "Visionnaire / Manager / Technicien",
        "human_sovereign_status": "Amadou_Kone_S0_OutOfTheLoop_Sanctuary",
        "github_vault_secrets_configured": vault_secrets,
        "active_integrations": {
            "google_apps_script": "Aspace_Gateway_GAS.js (Project 1z3Ffl39...)",
            "workspace_studio": "Trigger onWorkspaceStudioSheetEdit on B_LD01_BUSINESS_OS",
            "google_chat": "Target space: SOB Hub > 01 Growth OS",
            "github_actions": "Workflow aspace-n8n-gws-orchestrator.yml (dispatch: gws_webhook_trigger)",
        },
        "forkable_modules_convergence": forks,
        "next_autonomous_actions": [
            "Surveillance automatique du déploiement de la Web App Apps Script",
            "Création du Webhook Google Chat dans SOB Hub > 01 Growth OS par Muse dans le navigateur",
            "Raccordement du déclencheur Workspace Studio par Muse",
            "Surveillance des tests de la Cohorte 25 B2B dans Google Sheets",
        ],
    }

    HEARTBEAT_STATE.write_text(json.dumps(state, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Heartbeat state updated: {HEARTBEAT_STATE}")
    return state


def run_handoff(mandate_text: str):
    """Génère un paquet de passation formel pour Muse."""
    sync_shared_brain_mandate()
    hb = run_heartbeat()

    handoff_package = {
        "handoff_id": f"HANDOFF-MUSE-{dt.datetime.now(dt.timezone.utc).strftime('%Y%m%d-%H%M%S')}",
        "timestamp_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
        "sender": "Antigravity_Pair_Agent",
        "receiver": "Muse_Browser_Agent_A0",
        "mandate": mandate_text,
        "system_status": hb,
        "protocol": "Zero-Human-Attention (DeepSeek Superagent Law 1: Take as little human attention as possible)",
    }

    handoff_file = ROOT / "00_Memoire" / "muse_handoff_package.json"
    handoff_file.write_text(json.dumps(handoff_package, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Handoff package generated: {handoff_file}")
    return handoff_package


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Muse A0 Handoff & Heartbeat Orchestrator")
    parser.add_argument("action", choices=["heartbeat", "handoff", "sync-brain", "vault-check"], default="heartbeat", nargs="?")
    parser.add_argument("--mandate", type=str, default="Exécuter en totale autonomie sans bloquer l'humain")
    args = parser.parse_args()

    if args.action == "heartbeat":
        run_heartbeat()
    elif args.action == "handoff":
        run_handoff(args.mandate)
    elif args.action == "sync-brain":
        sync_shared_brain_mandate()
    elif args.action == "vault-check":
        print("Vault secrets:", check_github_vault())
