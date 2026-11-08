#!/usr/bin/env python3
"""
A'Space OS V5 — 02_Factory/07_Edge_CoolEmbrl_VPS/sync_coolembrl_and_vps.py
Orchestrateur de Déploiement Hybride entre :
  1. Le dépôt GitHub SSOT (`Amdkn/Aspace_OS_V5` & ses 5 catégories de GitHub Actions),
  2. L'instance locale **CoolEmbrl WSL** (Umbrel / Coolify / Docker sous WSL2),
  3. Le **VPS distant** (`VPS_HOST` / `VPS_USER` / `COOLIFY_WEBHOOK_URL`).

Capitalise sur les minutes illimitées des dépôts publics GitHub Actions à travers les 5 catégories natives :
  - Deployment             : `.github/workflows/aspace-v5-deploy-edge.yml`
  - Continuous Integration : `.github/workflows/aspace-factory-ci-matrix.yml`
  - Automation             : `.github/workflows/aspace-egm-jules-dispatcher.yml`
  - Security               : `.github/workflows/aspace-security-owasp-codeql.yml` + `.github/dependabot.yml`
  - Pages / Telemetry      : `.github/workflows/aspace-v5-pages-cockpit.yml`
"""

from __future__ import annotations
import json
import os
import platform
import shutil
import subprocess
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any

WORKSPACE_ROOT = Path(__file__).resolve().parents[2]
WORKFLOWS_DIR = WORKSPACE_ROOT / ".github" / "workflows"

EXPECTED_5_GITHUB_ACTION_CATEGORIES = {
    "Deployment": "aspace-v5-deploy-edge.yml",
    "Continuous_Integration": "aspace-factory-ci-matrix.yml",
    "Automation": "aspace-egm-jules-dispatcher.yml",
    "Security": "aspace-security-owasp-codeql.yml",
    "Pages_Telemetry": "aspace-v5-pages-cockpit.yml",
}


@dataclass
class EdgeTargetStatus:
    target_name: str
    kind: str  # wsl_coolembrl | remote_vps | github_actions_cloud
    reachable: bool
    details: dict[str, Any]


class CoolEmbrlVpsDeployer:
    def __init__(self, root: Path = WORKSPACE_ROOT) -> None:
        self.root = root

    def audit_github_workflows_5_categories(self) -> dict[str, Any]:
        statuses: dict[str, bool] = {}
        for category, wf_file in EXPECTED_5_GITHUB_ACTION_CATEGORIES.items():
            statuses[category] = (WORKFLOWS_DIR / wf_file).exists()
        return {
            "all_5_categories_present": all(statuses.values()),
            "categories": statuses,
            "dependabot_present": (self.root / ".github" / "dependabot.yml").exists(),
        }

    def probe_coolembrl_wsl(self) -> EdgeTargetStatus:
        is_windows = platform.system().lower().startswith("win")
        wsl_bin = shutil.which("wsl") or shutil.which("wsl.exe")
        if not is_windows or not wsl_bin:
            return EdgeTargetStatus(
                target_name="CoolEmbrl_WSL2",
                kind="wsl_coolembrl",
                reachable=False,
                details={"mode": "CI_CONTAINER_OR_NON_WINDOWS", "wsl_binary": bool(wsl_bin)},
            )
        return EdgeTargetStatus(
            target_name="CoolEmbrl_WSL2",
            kind="wsl_coolembrl",
            reachable=True,
            details={
                "wsl_binary": wsl_bin,
                "sync_command": "wsl.exe -e bash -lc 'cd /mnt/c/Users/amado/Aspace\\ OS\\ V5 && python3 02_Factory/01_Kernel_Gates/daemon_supervisor_cordis.py'",
                "design_standard": "CoolEmbrl 1.0 (S1-RICK Guarded)",
            },
        )

    def probe_vps_config(self) -> EdgeTargetStatus:
        vps_host = os.environ.get("VPS_HOST", "")
        vps_user = os.environ.get("VPS_USER", "root")
        coolify_hook = os.environ.get("COOLIFY_WEBHOOK_URL", "")
        return EdgeTargetStatus(
            target_name="Sovereign_VPS_Edge",
            kind="remote_vps",
            reachable=bool(vps_host or coolify_hook),
            details={
                "vps_host_configured": bool(vps_host),
                "vps_user": vps_user,
                "coolify_webhook_configured": bool(coolify_hook),
                "github_workflow": ".github/workflows/aspace-v5-deploy-edge.yml",
                "required_github_secrets": ["VPS_HOST", "VPS_USER", "VPS_SSH_KEY", "COOLIFY_WEBHOOK_URL", "COOLEMBRL_WEBHOOK_URL"],
            },
        )

    def full_edge_report(self) -> dict[str, Any]:
        return {
            "github_actions_5_categories": self.audit_github_workflows_5_categories(),
            "coolembrl_wsl": asdict(self.probe_coolembrl_wsl()),
            "remote_vps": asdict(self.probe_vps_config()),
        }


if __name__ == "__main__":
    deployer = CoolEmbrlVpsDeployer()
    report = deployer.full_edge_report()
    print(json.dumps(report, indent=2, ensure_ascii=False))
    if not report["github_actions_5_categories"]["all_5_categories_present"]:
        raise SystemExit(1)
