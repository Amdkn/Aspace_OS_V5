#!/usr/bin/env python3
"""
01_Forkable/FKB00_Runtime/00_A0_Core/aspace_freecompute_router.py
=================================================================
FreeComputeAPI v5.2 — Agrégateur, Routeur et Comptabilité Prévisible des Quotas Gratuits.
Couvre l'ensemble de la constellation Compute & Automatisation gratuite :

1. Google Apps Script (GAS) : 90 min CPU/jour, 6 min max/run, 20 000 UrlFetch/jour ($0/m)
2. Google Workspace Studio : 13 déclencheurs natifs (Gmail, Chat, Sheets, Drive, Forms, Meet)
3. Retool Workflows : 5 000 runs/mois gratuits, requêtes API REST/GraphQL illimitées ($0/m)
4. Zenphi & GKit : Automatisation no-code GWS & REST CRUD Sheets illimité ($0/m)
5. Cloudflare Workers (aspaceos.tech) : 100 000 req/jour, 10ms CPU/run ($0/m)
6. Upstash Box : 10 boxes concurrentes, 5h CPU/mois, auto-pause natif ($0/m)
7. Cloudroom : 2 992 crédits cloud sandbox ($0/m)
8. Google Cloud Shell (antigravity-a0) : 50h/semaine VM Linux persistante ($0/m)
9. GitHub Actions Public & FreeVPS (Amdkn/FreeVPS) : 2 000 min/mois ($0/m)
10. GitHub Codespaces : 120 core-hours/mois + purge atomique ($0/m)
11. Trio Workflow Cloud : Activepieces (1 000 tasks/m) + Make.com (1 000 ops/m) + Zapier (100 tasks/m)
12. Tunnels Mesh : Ngrok 1GB/m + Cloudflare Zero Trust + Tailscale ($0/m)
"""

from __future__ import annotations

import json
import subprocess
import sys
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]


@dataclass
class ComputeProvider:
    id: str
    category: str  # serverless_gas | studio_trigger | enterprise_workflow | edge_worker | container_box | cloud_shell | ephemeral_vm | workflow_ops | tunnel
    free_quota_desc: str
    monthly_free_units: str
    max_duration_sec: int
    auto_stop_cmd: str
    priority: int
    endpoint_or_target: str
    cost_usd_per_unit: float = 0.0


PROVIDERS: list[ComputeProvider] = [
    # --- 1. GOOGLE APPS SCRIPT & WORKSPACE STUDIO ---
    ComputeProvider(
        id="google-apps-script-serverless",
        category="serverless_gas",
        free_quota_desc="90 min CPU/jour (2 700 min/mois), 6 min max/run, 20 000 UrlFetch/jour",
        monthly_free_units="2,700 CPU-minutes/month",
        max_duration_sec=360,
        auto_stop_cmd="gas-execution-auto-kill-6m",
        priority=1,
        endpoint_or_target="https://script.google.com/macros/s/Aspace_Gateway_GAS/exec",
    ),
    ComputeProvider(
        id="google-workspace-studio-triggers",
        category="studio_trigger",
        free_quota_desc="13 déclencheurs natifs illimités (Gmail, Chat, Sheets, Drive, Forms, Meet)",
        monthly_free_units="Illimité (inclus dans compte Google)",
        max_duration_sec=30,
        auto_stop_cmd="studio-event-dispatch",
        priority=1,
        endpoint_or_target="https://studio.workspace.google.com",
    ),
    # --- 2. RETOOL, ZENPHI & GKIT ---
    ComputeProvider(
        id="retool-workflows-free",
        category="enterprise_workflow",
        free_quota_desc="5 000 runs de workflows/mois gratuits, 5 utilisateurs, requêtes API illimitées",
        monthly_free_units="5,000 runs/month",
        max_duration_sec=120,
        auto_stop_cmd="retool-webhook-ack",
        priority=2,
        endpoint_or_target="https://retool.com/products/workflows",
    ),
    ComputeProvider(
        id="gkit-sheets-rest-crud",
        category="enterprise_workflow",
        free_quota_desc="Beta $0/mois : SheetsAPI full REST CRUD, JSON/CSV, GDriveKit scanner",
        monthly_free_units="Illimité Beta $0/month",
        max_duration_sec=60,
        auto_stop_cmd="gkit-stateless-crud",
        priority=2,
        endpoint_or_target="https://gkit.mreshank.com",
    ),
    ComputeProvider(
        id="zenphi-gws-automation",
        category="enterprise_workflow",
        free_quota_desc="Free Tier GWS Native : process builder sans limite 6 min de GAS, step-level audit",
        monthly_free_units="500 steps/month (Free)",
        max_duration_sec=600,
        auto_stop_cmd="zenphi-process-complete",
        priority=3,
        endpoint_or_target="https://app.zenphi.com",
    ),
    # --- 3. EDGE WORKERS & SANDBOXES ---
    ComputeProvider(
        id="cloudflare-workers-aspaceos",
        category="edge_worker",
        free_quota_desc="100,000 req/jour, 10ms CPU/req (aspaceos.tech)",
        monthly_free_units="3,000,000 req/month",
        max_duration_sec=10,
        auto_stop_cmd="stateless-auto-terminate",
        priority=1,
        endpoint_or_target="https://aspaceos.tech",
    ),
    ComputeProvider(
        id="upstash-box-ephemeral",
        category="container_box",
        free_quota_desc="10 concurrent boxes, 5h CPU/mois, 5GB storage",
        monthly_free_units="5 CPU-hours/month",
        max_duration_sec=300,
        auto_stop_cmd="upstash-box-auto-pause",
        priority=4,
        endpoint_or_target="https://console.upstash.com/box",
    ),
    ComputeProvider(
        id="cloudroom-sandbox",
        category="container_box",
        free_quota_desc="2,992 Cloud Credits restants (Starter Free Tier)",
        monthly_free_units="2,992 credits",
        max_duration_sec=600,
        auto_stop_cmd="cloudroom-session-close",
        priority=4,
        endpoint_or_target="https://app.cloudroom.dev",
    ),
    # --- 4. CLOUD SHELL & EPHEMERAL VMS ---
    ComputeProvider(
        id="google-cloud-shell-antigravity-a0",
        category="cloud_shell",
        free_quota_desc="50h/semaine VM Linux gcloud persistante $HOME (5GB), projet antigravity-a0",
        monthly_free_units="200 hours/month",
        max_duration_sec=1800,
        auto_stop_cmd="exit",
        priority=5,
        endpoint_or_target="cloudshell:antigravity-a0",
    ),
    ComputeProvider(
        id="github-actions-freevps",
        category="ephemeral_vm",
        free_quota_desc="Runners publics gratuits + 2 000 min/mois privé (Amdkn/FreeVPS)",
        monthly_free_units="2,000 minutes/month",
        max_duration_sec=900,
        auto_stop_cmd="cancel-workflow-after-15m",
        priority=5,
        endpoint_or_target="01_Forkable/FKB01_Inference/03_Inference_FreeCloud/FreeVPS",
    ),
    ComputeProvider(
        id="github-codespaces-guarded",
        category="ephemeral_vm",
        free_quota_desc="120 core-hours/mois + purge atomique Stop Hook ($6.21 guarded)",
        monthly_free_units="120 core-hours/month",
        max_duration_sec=900,
        auto_stop_cmd="gh codespace stop --all",
        priority=6,
        endpoint_or_target="github:codespaces",
    ),
    # --- 5. WORKFLOW OPS CLOUD (ACTIVEPIECES, MAKE, ZAPIER) ---
    ComputeProvider(
        id="workflow-ops-triad",
        category="workflow_ops",
        free_quota_desc="Activepieces (1 000 tasks/m) + Make.com (1 000 ops/m) + Zapier (100 tasks/m)",
        monthly_free_units="2,100 operations/month",
        max_duration_sec=60,
        auto_stop_cmd="stateless-webhook-roundrobin",
        priority=3,
        endpoint_or_target="mcp+webhook://workflow-ops-triad",
    ),
    # --- 6. MESH TUNNELS ---
    ComputeProvider(
        id="ngrok-cloudflare-tailscale-mesh",
        category="tunnel",
        free_quota_desc="Ngrok 1 GB/mois (local-other.internal) + Cloudflare Zero Trust + Tailscale",
        monthly_free_units="1 GB bandwidth/month",
        max_duration_sec=86400,
        auto_stop_cmd="tunnel-healthcheck",
        priority=1,
        endpoint_or_target="https://local-other.internal",
    ),
]


def purge_stale_codespaces(dry_run: bool = False) -> list[dict]:
    """Inspecte et stoppe immédiatement les GitHub Codespaces inactifs pour protéger le quota."""
    actions: list[dict] = []
    try:
        res = subprocess.run(
            ["gh", "codespace", "list", "--json", "name,repository,state,createdAt"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        if res.returncode != 0 or not res.stdout.strip():
            return actions

        codespaces = json.loads(res.stdout)
        for cs in codespaces:
            name = cs.get("name", "")
            repo = cs.get("repository", "")
            state = cs.get("state", "")
            is_legacy = any(tag in repo for tag in ("Aspace_OS_V3", "Aspace_OS_V4"))

            if state.lower() in ("available", "running") and not dry_run:
                subprocess.run(
                    ["gh", "codespace", "stop", "-c", name],
                    capture_output=True,
                    text=True,
                    timeout=10,
                )
                actions.append({"codespace": name, "repo": repo, "action": "STOPPED_ACTIVE"})
            else:
                actions.append(
                    {
                        "codespace": name,
                        "repo": repo,
                        "state": state,
                        "legacy_alert": is_legacy,
                    }
                )
    except Exception as exc:
        actions.append({"warning": str(exc)})
    return actions


def select_compute(task_type: str, estimated_seconds: int = 30) -> dict:
    """
    Algorithme de routage à coût nul ($0.00) avec comptabilité prévisible :
    Sélectionne le meilleur fournisseur gratuit selon la nature de la tâche et sa durée.
    """
    candidates = [p for p in PROVIDERS if p.max_duration_sec >= estimated_seconds]

    if task_type in ("gws_trigger", "sheet_mutation", "form_submit", "email_event"):
        # Priorité absolue : Déclencheurs Workspace Studio & Google Apps Script
        candidates = [
            p for p in candidates if p.category in ("studio_trigger", "serverless_gas")
        ] or candidates
    elif task_type in ("b2b_workflow", "crm_sync", "retool_ui"):
        # Priorité : Retool Workflows, GKit, Zenphi
        candidates = [
            p for p in candidates if p.category in ("enterprise_workflow", "workflow_ops")
        ] or candidates
    elif task_type in ("heavy_build", "docker_sandbox", "git_mutation"):
        # Priorité : Cloud Shell, Ephemeral VMs, Container Boxes
        candidates = [
            p
            for p in candidates
            if p.category in ("container_box", "cloud_shell", "ephemeral_vm")
        ] or candidates

    candidates.sort(key=lambda x: x.priority)
    chosen = candidates[0] if candidates else PROVIDERS[0]

    return {
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "task_type": task_type,
        "estimated_seconds": estimated_seconds,
        "selected_provider": asdict(chosen),
        "total_cost_usd": 0.00,
        "atomic_teardown_contract": chosen.auto_stop_cmd,
    }


def compute_monthly_quota_accounting() -> dict:
    """Retourne la synthèse consolidée de la capacité de calcul mensuelle gratuite."""
    return {
        "total_providers": len(PROVIDERS),
        "zero_cost_guarantee": "100% Free Tiers / Open Quotas",
        "monthly_capacities": {
            "google_apps_script": "2,700 CPU-min/month (90 min/day)",
            "google_workspace_studio": "13 Native Event Triggers (Unlimited)",
            "retool_workflows": "5,000 Runs/month",
            "cloudflare_workers": "3,000,000 Requests/month",
            "workflow_ops_triad": "2,100 Ops/month (Activepieces + Make + Zapier)",
            "github_actions_public_private": "Unlimited Public + 2,000 Private min/month",
            "google_cloud_shell": "200 Hours Linux VM/month (50h/week)",
            "github_codespaces": "120 Core-hours/month",
            "upstash_boxes": "5 CPU-hours/month (10 boxes)",
            "cloudroom_credits": "2,992 Credits",
        },
    }


def main() -> None:
    task_type = sys.argv[1] if len(sys.argv) > 1 else "sheet_mutation"
    duration = int(sys.argv[2]) if len(sys.argv) > 2 else 15
    selection = select_compute(task_type=task_type, estimated_seconds=duration)
    accounting = compute_monthly_quota_accounting()
    codespace_audit = purge_stale_codespaces()

    report = {
        "router": "Aspace_FreeComputeAPI_v5.2",
        "quota_accounting": accounting,
        "dispatch_decision": selection,
        "codespace_quota_guard": codespace_audit,
    }
    print(json.dumps(report, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
