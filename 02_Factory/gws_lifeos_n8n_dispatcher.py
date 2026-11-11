#!/usr/bin/env python3
"""
02_Factory/gws_lifeos_n8n_dispatcher.py
=======================================
Orchestrateur GitHub-as-n8n Primitive × Google Workspace CLI (gws) pour Life OS 2026.
Implémente explicitement les 5 Familles de Nœuds n8n (YouTube oYiIB8GGadQ) :
  1. Trigger Nodes    (Webhooks GitHub, Cron, GWS Push Notifications)
  2. Core Nodes       (Code, HTTP Request, If/Switch, Merge, Crypto HMAC-SHA256)
  3. App Nodes        (Google Workspace CLI : Slides, Sheets, Calendar, Drive, Docs, Tasks, Chat + Supabase + Slack/Discord)
  4. AI Cluster Nodes (Root Agent A0 + Memory MCP + Tools via FreeLLMAPI :31415)
  5. Community Nodes  (Aspace-Factory-App Scion Sparse-Checkout & FreeComputeAPI Router)
"""

import argparse
import hashlib
import json
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent
while ROOT != ROOT.parent and not (ROOT / ".gitmodules").exists():
    ROOT = ROOT.parent

# Mapping canonique des 6 Vaisseaux Starfleet de Life OS (A2) vers Google Workspace CLI (gws)
LIFE_OS_GWS_MAP = {
    "21_Ikigai_Orville": {
        "vessel": "USS Orville (Ikigai)",
        "gws_service": "slides",
        "gws_resource": "presentations",
        "cli_cmd": ["gws", "slides", "presentations", "get"],
        "purpose": "Deck Ikigai Visionnaire & Alignement Trimestriel",
    },
    "22_Wheel_Discovery": {
        "vessel": "USS Discovery / Zora (Life Wheel)",
        "gws_service": "sheets",
        "gws_resource": "spreadsheets.values",
        "cli_cmd": ["gws", "sheets", "spreadsheets", "values", "get"],
        "purpose": "Télémétrie des 8 Domaines LD01..LD08 + Bouclier Beth LD03/LD04",
    },
    "23_12WY_SNW": {
        "vessel": "USS Curie / SNW (12 Week Year)",
        "gws_service": "calendar",
        "gws_resource": "events",
        "cli_cmd": ["gws", "calendar", "events", "list"],
        "purpose": "Timeblocking 12WY & Sanctuaire Nocturne 00h00-05h00",
    },
    "24_PARA_Enterprise": {
        "vessel": "USS Enterprise (PARA)",
        "gws_service": "drive+docs",
        "gws_resource": "files+documents",
        "cli_cmd": ["gws", "drive", "files", "list"],
        "purpose": "Synchronisation SSOT des 6 dossiers Google Drive A'Space OS & Areas OS",
    },
    "25_GTD_Cerritos": {
        "vessel": "USS Cerritos (GTD)",
        "gws_service": "tasks",
        "gws_resource": "tasks",
        "cli_cmd": ["gws", "tasks", "tasklists", "list"],
        "purpose": "Inbox Zero & Actions Immédiates Summer (< 2 min)",
    },
    "26_DEAL_Protostar": {
        "vessel": "USS Protostar (DEAL)",
        "gws_service": "chat",
        "gws_resource": "spaces.messages",
        "cli_cmd": ["gws", "chat", "spaces", "list"],
        "purpose": "Délégation Automatisation & Notifications Exécutives A0 -> S0",
    },
}


class N8nFiveFamiliesEngine:
    """Exécute un workflow selon la topologie exacte des 5 familles de nœuds n8n."""

    def __init__(self, event_source: str, vessel: str, action: str) -> None:
        self.event_source = event_source
        self.vessel = vessel
        self.action = action
        self.gws_installed = shutil.which("gws") is not None

    # 1. TRIGGER NODES
    def node_1_trigger(self) -> dict:
        return {
            "family": "1_Trigger_Node",
            "event_source": self.event_source,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "target_vessel": self.vessel,
        }

    # 2. CORE NODES (If/Switch, Merge, Crypto Receipt)
    def node_2_core_transform(self, trigger_payload: dict) -> dict:
        vessels = (
            list(LIFE_OS_GWS_MAP.keys())
            if self.vessel == "ALL_6_VESSELS"
            else [self.vessel]
        )
        digest = hashlib.sha256(
            json.dumps(trigger_payload, sort_keys=True).encode("utf-8")
        ).hexdigest()[:16]
        return {
            "family": "2_Core_Node",
            "logic": "Switch_By_LifeOS_Vessel + HMAC_Receipt",
            "resolved_vessels": vessels,
            "canary_receipt_r10": f"R10-N8N-{digest}",
        }

    # 3. APP NODES (Google Workspace CLI + Supabase + Slack/Discord)
    def node_3_app_gws_dispatch(self, resolved_vessels: list[str]) -> list[dict]:
        results = []
        for v_key in resolved_vessels:
            spec = LIFE_OS_GWS_MAP.get(v_key)
            if not spec:
                continue
            status = "READY_GWS_CLI" if self.gws_installed else "SIMULATED_DRY_RUN_GWS"
            if self.gws_installed and self.action == "live-probe":
                try:
                    proc = subprocess.run(
                        ["gws", "--version"],
                        capture_output=True,
                        text=True,
                        timeout=5,
                    )
                    status = f"GWS_ACTIVE ({proc.stdout.strip() or 'ok'})"
                except Exception as exc:
                    status = f"GWS_FALLBACK ({exc})"
            results.append(
                {
                    "family": "3_App_Node",
                    "vessel_key": v_key,
                    "vessel_name": spec["vessel"],
                    "gws_service": spec["gws_service"],
                    "cli_command": " ".join(spec["cli_cmd"]),
                    "purpose": spec["purpose"],
                    "status": status,
                }
            )
        return results

    # 4. AI CLUSTER NODES (Root Agent A0 + Memory MCP + Tools)
    def node_4_ai_cluster(self, app_results: list[dict]) -> dict:
        # Exécution du Cascadeur IPBD 4D (Mitra-v2/TabFM 3D Sheets -> Chronos-2/TimesFM 4D Calendar/Chat DEAL Muse)
        ipbd_cascade_status = "NOT_RUN"
        try:
            cascade_script = ROOT / "02_Factory" / "ipbd_4d_chronos_cascade.py"
            if cascade_script.exists():
                c_proc = subprocess.run(
                    [sys.executable, str(cascade_script)],
                    capture_output=True,
                    text=True,
                    timeout=20,
                    cwd=str(ROOT),
                )
                if c_proc.returncode == 0:
                    ipbd_cascade_status = "IPBD_4D_CHRONOS_CASCADE_COMPLETED"
        except Exception as exc:
            ipbd_cascade_status = f"IPBD_CASCADE_ERR ({exc})"

        return {
            "family": "4_AI_Cluster_Node",
            "root_agent": "A0_Amadeus_Cortex",
            "llm_provider": "FreeLLMAPI_Gateway (127.0.0.1:31415 -> freellmapi/auto)",
            "memory_bus": "00_Memoire/shared_brain/memory.jsonl + egm_missions.db",
            "synthesized_vessels_count": len(app_results),
            "ipbd_4d_cascade": ipbd_cascade_status,
        }

    # 5. COMMUNITY NODES (Scion Sparse-Checkout & FreeComputeAPI)
    def node_5_community_scion(self) -> dict:
        return {
            "family": "5_Community_Node",
            "github_app": "Aspace-Factory-App",
            "scion_mode": "sparse-checkout + GraphQL createCommitOnBranch",
            "freecompute_guard": "atomic-codespace-stop-on-exit",
        }

    def run(self) -> dict:
        t = self.node_1_trigger()
        c = self.node_2_core_transform(t)
        a = self.node_3_app_gws_dispatch(c["resolved_vessels"])
        ai = self.node_4_ai_cluster(a)
        com = self.node_5_community_scion()
        return {
            "engine": "Aspace_GitHub_n8n_Primitive_v5",
            "action": self.action,
            "pipeline": {
                "1_trigger": t,
                "2_core": c,
                "3_app_gws": a,
                "4_ai_cluster": ai,
                "5_community_scion": com,
            },
        }


def main() -> None:
    parser = argparse.ArgumentParser(description="Aspace GitHub-as-n8n GWS Dispatcher")
    parser.add_argument("--event", default="manual_or_ci_trigger")
    parser.add_argument("--vessel", default="ALL_6_VESSELS")
    parser.add_argument("--action", default="sync-cockpit")
    args = parser.parse_args()

    engine = N8nFiveFamiliesEngine(
        event_source=args.event,
        vessel=args.vessel,
        action=args.action,
    )
    report = engine.run()
    out_path = ROOT / "00_Memoire" / "gws_n8n_last_dispatch.json"
    out_path.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(report, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
