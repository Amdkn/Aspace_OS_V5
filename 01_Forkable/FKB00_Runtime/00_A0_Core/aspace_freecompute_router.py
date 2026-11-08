#!/usr/bin/env python3
"""
01_Forkable/FKB00_Runtime/00_A0_Core/aspace_freecompute_router.py
=================================================================
FreeComputeAPI — Agrégateur et Routeur Atomique des Compute & Quotas Mensuels Gratuits.
Pendant « Compute & Automatisation » de FreeLLMAPI (4.2B tokens/mois).

Gère de façon déterministe :
1. Cloudflare Workers (aspaceos.tech : 100 000 req/jour, 10 ms CPU/invocation)
2. Upstash Box (10 boxes concurrentes, 5h CPU/mois, auto-pause natif)
3. Cloudroom (2 992 Cloud Credits disponibles)
4. Google Cloud Shell (antigravity-a0 : 50h/semaine d'exécution éphémère)
5. GitHub Codespaces (120 core-hours/mois — inclut purge_stale_codespaces() contre les fuites de quota)
6. GitHub Actions Public & FreeVPS (Amdkn/FreeVPS : 2 000 min/mois + runners publics)
7. Activepieces (1 000 crédits/mois + MCP) & Make.com (1 000 ops/mois)
8. Tunnels Souverains (Ngrok local-other.internal, Cloudflare Zero Trust, Tailscale)
"""

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
    category: str  # edge_worker | container_box | cloud_shell | ephemeral_vm | workflow_ops | tunnel
    free_quota_desc: str
    max_duration_sec: int
    auto_stop_cmd: str
    priority: int
    endpoint_or_target: str


PROVIDERS: list[ComputeProvider] = [
    ComputeProvider(
        id="cloudflare-workers-aspaceos",
        category="edge_worker",
        free_quota_desc="100,000 req/day, 10ms CPU/req (aspaceos.tech)",
        max_duration_sec=10,
        auto_stop_cmd="stateless-auto-terminate",
        priority=1,
        endpoint_or_target="https://aspaceos.tech",
    ),
    ComputeProvider(
        id="upstash-box-ephemeral",
        category="container_box",
        free_quota_desc="10 concurrent boxes, 5h CPU/month, 5GB storage",
        max_duration_sec=300,
        auto_stop_cmd="upstash-box-auto-pause",
        priority=2,
        endpoint_or_target="https://console.upstash.com/box",
    ),
    ComputeProvider(
        id="cloudroom-sandbox",
        category="container_box",
        free_quota_desc="2,992 Cloud Credits remaining (Starter Free Tier)",
        max_duration_sec=600,
        auto_stop_cmd="cloudroom-session-close",
        priority=3,
        endpoint_or_target="https://app.cloudroom.dev",
    ),
    ComputeProvider(
        id="google-cloud-shell-antigravity-a0",
        category="cloud_shell",
        free_quota_desc="50 hours/week persistent $HOME (5GB), project antigravity-a0",
        max_duration_sec=1800,
        auto_stop_cmd="exit",
        priority=4,
        endpoint_or_target="cloudshell:antigravity-a0",
    ),
    ComputeProvider(
        id="github-actions-freevps",
        category="ephemeral_vm",
        free_quota_desc="Public repo runners + 2,000 min/month private (timeout-minutes: 15)",
        max_duration_sec=900,
        auto_stop_cmd="cancel-workflow-after-15m",
        priority=5,
        endpoint_or_target="01_Forkable/FKB01_Inference/03_Inference_FreeCloud/FreeVPS",
    ),
    ComputeProvider(
        id="github-codespaces-guarded",
        category="ephemeral_vm",
        free_quota_desc="120 core-hours/month + 15GB storage ($6.21 guarded by Stop Hook)",
        max_duration_sec=900,
        auto_stop_cmd="gh codespace stop --all",
        priority=6,
        endpoint_or_target="github:codespaces",
    ),
    ComputeProvider(
        id="activepieces-make-bus",
        category="workflow_ops",
        free_quota_desc="Activepieces 1,000 tasks/month (MCP) + Make.com 1,000 ops/month",
        max_duration_sec=60,
        auto_stop_cmd="stateless-webhook",
        priority=1,
        endpoint_or_target="mcp+webhook://activepieces-make-bus",
    ),
    ComputeProvider(
        id="ngrok-cloudflare-tailscale-mesh",
        category="tunnel",
        free_quota_desc="Ngrok 1 GB/month (https://local-other.internal) + Cloudflare Zero Trust + Tailscale",
        max_duration_sec=86400,
        auto_stop_cmd="tunnel-healthcheck",
        priority=1,
        endpoint_or_target="https://local-other.internal",
    ),
]


def purge_stale_codespaces(dry_run: bool = False) -> list[dict]:
    """
    Inspecte les GitHub Codespaces (ex. anciens codespaces Aspace_OS_V3 / V4)
    et stoppe immédiatement toute instance active pour stopper l'hémorragie de quota ($6.21).
    """
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
                        "legacy_v3_v4_storage_alert": is_legacy,
                        "recommendation": "Delete dormant V3/V4 codespace to free 15GB storage quota"
                        if is_legacy
                        else "OK",
                    }
                )
    except Exception as exc:
        actions.append({"warning": str(exc)})
    return actions


def select_compute(task_type: str, estimated_seconds: int = 30) -> dict:
    """
    Sélectionne le fournisseur de compute gratuit optimal selon la durée et la nature de la tâche,
    et retourne son contrat d'extinction atomique (Auto-Teardown).
    """
    candidates = [p for p in PROVIDERS if p.max_duration_sec >= estimated_seconds]
    if task_type in ("webhook", "n8n_trigger", "edge_routing"):
        candidates = [p for p in candidates if p.category in ("edge_worker", "workflow_ops")] or candidates
    elif task_type in ("heavy_build", "docker_sandbox", "git_mutation"):
        candidates = [
            p for p in candidates if p.category in ("container_box", "cloud_shell", "ephemeral_vm")
        ] or candidates

    candidates.sort(key=lambda x: x.priority)
    chosen = candidates[0] if candidates else PROVIDERS[0]
    return {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "task_type": task_type,
        "estimated_seconds": estimated_seconds,
        "selected_provider": asdict(chosen),
        "atomic_teardown_contract": chosen.auto_stop_cmd,
    }


def main() -> None:
    task_type = sys.argv[1] if len(sys.argv) > 1 else "heavy_build"
    duration = int(sys.argv[2]) if len(sys.argv) > 2 else 120
    selection = select_compute(task_type=task_type, estimated_seconds=duration)
    codespace_audit = purge_stale_codespaces()
    report = {
        "router": "Aspace_FreeComputeAPI_v5",
        "total_providers_registered": len(PROVIDERS),
        "dispatch_decision": selection,
        "codespace_quota_guard": codespace_audit,
    }
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
