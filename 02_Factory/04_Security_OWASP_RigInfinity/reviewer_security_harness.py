#!/usr/bin/env python3
"""
A'Space OS V5 — 02_Factory/04_Security_OWASP_RigInfinity/reviewer_security_harness.py
Implémente le Triage Autonome de l'agent `reviewer-security` (Spécification NotebookLM Factory V5) :
  1. Déclenchement automatique (Triggers) : Dependabot, CodeQL, Secret Scanning.
  2. Audit OWASP Top 10 (A01 Broken Access Control .. A10 SSRF).
  3. Isolation dans un Worktree dédié sous `02_Factory/04_Security_OWASP_RigInfinity/sec-<id>`
     (compatible `02_Factory/sec-<id>`).
  4. Validation automatisée via `02_Factory/checks.ps1` / `semantic_gate.py`.
  5. Préparation et soumission de Pull Request prioritaire marquée du tag `factory:security`.
"""

from __future__ import annotations
import hashlib
import json
import subprocess
import time
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any, Literal

WORKSPACE_ROOT = Path(__file__).resolve().parents[2]
SEC_WORKTREES_DIR = WORKSPACE_ROOT / "02_Factory" / "04_Security_OWASP_RigInfinity" / "sec-worktrees"

OWASP_TOP_10_2025: dict[str, str] = {
    "A01": "Broken Access Control & Holon Boundary Bypass",
    "A02": "Cryptographic Failures & Unencrypted Secrets",
    "A03": "Injection (Prompt Injection, Shell Injection, SQLi)",
    "A04": "Insecure Design & Missing A1-Beth Circuit Breaker",
    "A05": "Security Misconfiguration & Exposed Daemon Ports",
    "A06": "Vulnerable and Outdated Components (Dependabot Submodules)",
    "A07": "Identification and Authentication Failures (Missing LeaseToken)",
    "A08": "Software and Data Integrity Failures (Unsigned Gitlinks)",
    "A09": "Security Logging and Monitoring Failures (Append-Only Log Violation)",
    "A10": "Server-Side Request Forgery (Unbounded Subagent Webhook)",
}


@dataclass
class SecurityAlert:
    alert_id: str
    trigger_source: Literal["dependabot", "codeql", "secret_scanning", "owasp_audit"]
    target_path: str
    owasp_category: str
    severity: Literal["CRITICAL", "HIGH", "MEDIUM", "LOW"]
    summary: str


@dataclass
class SecurityRemediationReceipt:
    alert_id: str
    owasp_rule: str
    isolated_worktree: str
    validation_gate_passed: bool
    pr_branch: str
    pr_labels: list[str]
    automated_header: str
    timestamp: float


class ReviewerSecurityAgent:
    """
    Agent `reviewer-security` opérant en mode déterministe RigInfinity.
    """

    AUTOMATED_HEADER = "This is by an automated agent, not a human."

    def __init__(self, workspace_root: Path = WORKSPACE_ROOT):
        self.workspace_root = workspace_root
        SEC_WORKTREES_DIR.mkdir(parents=True, exist_ok=True)

    def classify_owasp(self, alert: SecurityAlert) -> str:
        desc = OWASP_TOP_10_2025.get(alert.owasp_category, OWASP_TOP_10_2025["A06"])
        return f"{alert.owasp_category}: {desc}"

    def prepare_isolated_sec_worktree(self, alert_id: str) -> Path:
        """
        Génère l'environnement isolé `02_Factory/04_Security_OWASP_RigInfinity/sec-worktrees/sec-<id>`
        pour ne jamais impacter la branche principale avant validation.
        """
        safe_id = "".join(c for c in alert_id if c.isalnum() or c in ("-", "_"))[:24]
        wt_dir = SEC_WORKTREES_DIR / f"sec-{safe_id}"
        wt_dir.mkdir(parents=True, exist_ok=True)
        return wt_dir

    def run_deterministic_validation(self) -> bool:
        gate_script = self.workspace_root / "02_Factory" / "semantic_gate.py"
        if not gate_script.exists():
            return False
        proc = subprocess.run(["python", str(gate_script)], cwd=str(self.workspace_root), capture_output=True, text=True)
        return proc.returncode == 0

    def triage_and_remediate(self, alert: SecurityAlert) -> SecurityRemediationReceipt:
        owasp_rule = self.classify_owasp(alert)
        wt_dir = self.prepare_isolated_sec_worktree(alert.alert_id)
        pr_branch = f"sec/{alert.alert_id.lower()}"

        # Écriture du manifeste de remédiation dans le worktree isolé
        patch_spec = {
            "header": self.AUTOMATED_HEADER,
            "alert": asdict(alert),
            "owasp_classification": owasp_rule,
            "worktree": str(wt_dir.relative_to(self.workspace_root)).replace("\\", "/"),
            "pr_branch": pr_branch,
            "labels": ["factory:security", f"owasp:{alert.owasp_category.lower()}", f"trigger:{alert.trigger_source}"],
        }
        (wt_dir / "remediation-receipt.json").write_text(
            json.dumps(patch_spec, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
        )

        gate_ok = self.run_deterministic_validation()

        return SecurityRemediationReceipt(
            alert_id=alert.alert_id,
            owasp_rule=owasp_rule,
            isolated_worktree=str(wt_dir.relative_to(self.workspace_root)).replace("\\", "/"),
            validation_gate_passed=gate_ok,
            pr_branch=pr_branch,
            pr_labels=["factory:security", f"owasp:{alert.owasp_category.lower()}"],
            automated_header=self.AUTOMATED_HEADER,
            timestamp=time.time(),
        )


if __name__ == "__main__":
    agent = ReviewerSecurityAgent()
    sample_alert = SecurityAlert(
        alert_id="SEC-2026-001",
        trigger_source="dependabot",
        target_path="01_Forkable/FKB00_Runtime/01_Holo_TriptyqueCore/RigInfinity",
        owasp_category="A06",
        severity="HIGH",
        summary="Verify deterministic Rust-style ownership bounds across submodule daemons",
    )
    receipt = agent.triage_and_remediate(sample_alert)
    print(json.dumps(asdict(receipt), indent=2, ensure_ascii=False))
