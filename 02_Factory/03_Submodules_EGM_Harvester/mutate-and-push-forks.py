#!/usr/bin/env python3
"""
A'Space OS V5 — 02_Factory/mutate-and-push-forks.py
Sort les sous-modules de l'état 'Mort par Conception' (detached HEAD) :
1. Bascule chaque sous-module sur la branche souveraine `aspace-v5-native`
2. Injecte le descripteur Cordis Fiber (`aspace-plugin.json`) et les adaptateurs des 6 Familles
3. Commit & Push dans le dépôt GitHub respectif (`Amdkn/<repo>`) via Git local ou GitHub API
4. Met à jour `00_Memoire/egm_missions.db` (status='COMPLETED') et les pointeurs Git (`160000`) de `Aspace_OS_V5`
"""

from __future__ import annotations
import base64
import concurrent.futures
import json
import sqlite3
import subprocess
import time
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
DB_PATH = ROOT / "00_Memoire" / "egm_missions.db"
BRANCH_NAME = "aspace-v5-native"

FAMILY_SPECS: dict[str, dict[str, Any]] = {
    "00_A0_Core": {
        "family": "CORE_A0_KERNEL",
        "fractal_layer": "2L",
        "holon_owner": "A0-AMADEUS / S1-RICK",
        "capabilities": ["egm_bridge_31415", "holon_578_dispatch", "cordis_fiber_host"],
        "integration_target": "01_Forkable/FKB00_Runtime/00_A0_Core/a0_egm_bridge.py",
    },
    "01_Holo_TriptyqueCore": {
        "family": "METABOLIC_LINEAGE_POPULATION",
        "fractal_layer": "4L",
        "holon_owner": "A1-BETH / A1-MORTY",
        "capabilities": ["automaton_reserve_lease", "openrig_worktree_lineage", "infinity_75k_scheduler"],
        "integration_target": "01_Forkable/FKB00_Runtime/00_A0_Core/a0_holon_swarm_runtime.py",
    },
    "02_PredictiveWargame_MachineLearning": {
        "family": "NEURO_TABULAR_TEMPORAL_CHAOTIC_WARGAME",
        "fractal_layer": "16L",
        "holon_owner": "S2-SOL / B1..I1",
        "capabilities": ["mitra_8vote_icl", "chronos_timesfm_quantiles", "pathfm_chaotic_rollout", "mirofish_swarm"],
        "integration_target": "01_Forkable/FKB00_Runtime/02_PredictiveWargame_MachineLearning/triptych_autogluon_engine.py",
    },
    "03_MasterSpec_CleanPlan": {
        "family": "DETERMINISTIC_GOVERNANCE_TDD",
        "fractal_layer": "4L",
        "holon_owner": "S1-RICK",
        "capabilities": ["egm_context_isolation", "gstack_role_perspectives", "superpowers_headless_tdd", "gsd_40pct_cap"],
        "integration_target": "02_Factory/checks.ps1",
    },
    "04_ADE_OpenRig": {
        "family": "ADE_MULTIPLEXER_AND_HARNESSES",
        "fractal_layer": "8L",
        "holon_owner": "A1-MORTY / J1-JERRY",
        "capabilities": ["herdr_rust_pty", "orca_fleet_router", "t3code_cockpit", "universal_harness_gateway_31415"],
        "integration_target": "01_Forkable/FKB01_Inference/03_Inference_FreeCloud/aspace_freecloud_gateway.py",
    },
    "05_Recursive_RSI": {
        "family": "THREE_HORIZON_RECURSIVE_RSI",
        "fractal_layer": "20L",
        "holon_owner": "S3-GRAHAM / A1-BETH",
        "capabilities": ["prime_rlm_refine", "wikiskill_4role_compiler", "aqua_ambient_auditor", "dream_rsi_0usd_replay", "rrsi_worktree_evolver"],
        "integration_target": "01_Forkable/FKB00_Runtime/00_A0_Core/a0_recursive_factory.py",
    },
}


def classify_submodule(sub_path: str) -> dict[str, Any]:
    for key, spec in FAMILY_SPECS.items():
        if key in sub_path:
            return spec
    if "FKB01_Inference" in sub_path:
        return {
            "family": "SOVEREIGN_INFERENCE_TRIAD_AND_FREECLOUD",
            "fractal_layer": "4L",
            "holon_owner": "S1-RICK",
            "capabilities": ["lfm3_mimi_gliner_needle", "freecloud_3in1_failover"],
            "integration_target": "01_Forkable/FKB01_Inference/03_Inference_FreeCloud/aspace_freecloud_gateway.py",
        }
    if "FKB02_Memory" in sub_path:
        return {
            "family": "NEURO_SYMBOLIC_SHARED_BRAIN",
            "fractal_layer": "2L",
            "holon_owner": "S3-GRAHAM",
            "capabilities": ["mcp_shared_brain_jsonl", "gbrain_infinite_bi", "billion_context_ontology"],
            "integration_target": "00_Memoire/shared_brain/memory.jsonl",
        }
    if "FKB03_3DWorlds" in sub_path:
        return {
            "family": "SPATIAL_CITY_OFFICE_3D",
            "fractal_layer": "8L",
            "holon_owner": "A0-AMADEUS / A2-DISCOVERY",
            "capabilities": ["cubefarm_sanctuary_core", "agent_office_ring_road", "space_agent_reshaper"],
            "integration_target": "https://cubefarm-delta.vercel.app",
        }
    return {
        "family": "AREAS_OS_EXECUTION_PLUGIN",
        "fractal_layer": "16L",
        "holon_owner": "J1-JERRY / B1..I1",
        "capabilities": ["cordis_revertible_fiber", "areas_os_ld01_ld08"],
        "integration_target": "00_Memoire/bundle/areas_os/J1_Jerry_Macro_CrossOS/registry-578-holons.json",
    }


def run_git(cwd: Path, args: list[str], timeout: int = 25) -> tuple[int, str]:
    try:
        proc = subprocess.run(
            ["git", "-c", "user.name=Amdkn", "-c", "user.email=amdkn@aspace.os"] + args,
            cwd=str(cwd),
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        return proc.returncode, (proc.stdout + "\n" + proc.stderr).strip()
    except Exception as exc:
        return 1, str(exc)


def parse_gitmodules() -> list[dict[str, str]]:
    gm = ROOT / ".gitmodules"
    if not gm.exists():
        return []
    modules: list[dict[str, str]] = []
    current: dict[str, str] = {}
    for line in gm.read_text(encoding="utf-8", errors="ignore").splitlines():
        s = line.strip()
        if s.startswith("[submodule "):
            if current.get("path"):
                modules.append(current)
            current = {}
        elif "=" in s:
            k, v = [x.strip() for x in s.split("=", 1)]
            current[k] = v
    if current.get("path"):
        modules.append(current)
    return modules


def inject_family_specific_adapters(abs_dir: Path, sub_path: str) -> list[str]:
    extra_files: list[str] = []
    # F8 pas 8 : les 3 branches d'injection (automaton, openrig, infinity) sont
    # retirees — leurs fonctions vivent dans le natif RigInfinity. La fonction
    # reste un no-op pour les modules restants (aucune branche par famille).
    return extra_files


def mutate_remote_via_gh_api(repo_name: str, manifest_json: str, layer: str) -> str:
    """
    Pour un fork Amdkn/<repo> non cloné sur disque, crée la branche `aspace-v5-native`
    et y commite `aspace-plugin.json` directement via l'API GitHub, puis retourne le nouveau SHA.
    """
    try:
        p1 = subprocess.run(
            ["gh", "api", f"repos/Amdkn/{repo_name}/commits/HEAD", "--jq", ".sha"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        base_sha = p1.stdout.strip()
        if len(base_sha) != 40:
            return ""
        subprocess.run(
            [
                "gh",
                "api",
                "-X",
                "POST",
                f"repos/Amdkn/{repo_name}/git/refs",
                "-f",
                f"ref=refs/heads/{BRANCH_NAME}",
                "-f",
                f"sha={base_sha}",
            ],
            capture_output=True,
            text=True,
            timeout=10,
        )
        b64 = base64.b64encode(manifest_json.encode("utf-8")).decode("ascii")
        p2 = subprocess.run(
            [
                "gh",
                "api",
                "-X",
                "PUT",
                f"repos/Amdkn/{repo_name}/contents/aspace-plugin.json",
                "-f",
                f"message=feat(aspace-v5): bind {repo_name} as Cordis Fiber ({layer}) to A0 EGM Core",
                "-f",
                f"content={b64}",
                "-f",
                f"branch={BRANCH_NAME}",
                "--jq",
                ".commit.sha",
            ],
            capture_output=True,
            text=True,
            timeout=12,
        )
        new_sha = p2.stdout.strip()
        return new_sha if len(new_sha) == 40 else base_sha
    except Exception:
        return ""


def mutate_submodule(mod: dict[str, str], push_remote: bool = True) -> dict[str, Any]:
    sub_path = mod["path"]
    sub_url = mod.get("url", "")
    abs_dir = ROOT / sub_path
    spec = classify_submodule(sub_path)
    repo_name = sub_path.split("/")[-1]

    plugin_manifest = {
        "$schema": "https://aspaceos.tech/schemas/cordis-fiber-v5.json",
        "name": f"@aspace-v5/{repo_name.lower()}",
        "submodule_path": sub_path,
        "sovereign_fork_url": sub_url,
        "branch": BRANCH_NAME,
        "family": spec["family"],
        "fractal_layer": spec["fractal_layer"],
        "holon_owner": spec["holon_owner"],
        "capabilities": spec["capabilities"],
        "a0_integration_target": spec["integration_target"],
        "egm_gateway_endpoint": "http://127.0.0.1:31415/v1/chat/completions",
        "shared_brain_path": "00_Memoire/shared_brain/memory.jsonl",
        "cordis_contract": {
            "everything_is_a_plugin": True,
            "revertible_effects": True,
            "reactive_coeffects": True,
        },
    }
    manifest_json = json.dumps(plugin_manifest, indent=2, ensure_ascii=False) + "\n"

    # Case 1: Initialized local git submodule (.git exists)
    if abs_dir.exists() and (abs_dir / ".git").exists():
        run_git(abs_dir, ["checkout", "-B", BRANCH_NAME])
        (abs_dir / "aspace-plugin.json").write_text(manifest_json, encoding="utf-8")
        extra = inject_family_specific_adapters(abs_dir, sub_path)
        run_git(abs_dir, ["add", "aspace-plugin.json"] + extra)
        run_git(
            abs_dir,
            ["commit", "-m", f"feat(aspace-v5): bind {repo_name} as Cordis Fiber ({spec['fractal_layer']}) to A0 EGM Core"],
        )
        _, head_sha = run_git(abs_dir, ["rev-parse", "HEAD"])
        head_sha = head_sha.strip()

        pushed = False
        if push_remote and "github.com/Amdkn/" in sub_url:
            p_code, _ = run_git(abs_dir, ["push", "-u", "origin", BRANCH_NAME, "--force"], timeout=25)
            pushed = (p_code == 0)

        return {
            "path": sub_path,
            "repo": repo_name,
            "branch": BRANCH_NAME,
            "sha": head_sha if len(head_sha) == 40 else "",
            "family": spec["family"],
            "layer": spec["fractal_layer"],
            "pushed_to_amdkn": pushed,
            "status": "MUTATED_ACTIVE_LOCAL_GIT",
        }

    # Case 2: Uncloned gitlink submodule -> mutate remote via GitHub API on `aspace-v5-native`
    abs_dir.mkdir(parents=True, exist_ok=True)
    remote_sha = ""
    if push_remote and "github.com/Amdkn/" in sub_url:
        remote_sha = mutate_remote_via_gh_api(repo_name, manifest_json, spec["fractal_layer"])

    return {
        "path": sub_path,
        "repo": repo_name,
        "branch": BRANCH_NAME,
        "sha": remote_sha,
        "family": spec["family"],
        "layer": spec["fractal_layer"],
        "pushed_to_amdkn": bool(remote_sha),
        "status": "MUTATED_ACTIVE",
    }


def main(push_remote: bool = False) -> None:
    modules = parse_gitmodules()
    results: list[dict[str, Any]] = []

    with concurrent.futures.ThreadPoolExecutor(max_workers=12) as pool:
        futs = [pool.submit(mutate_submodule, mod, push_remote) for mod in modules]
        for f in concurrent.futures.as_completed(futs):
            results.append(f.result())

    # Update parent gitlink SHAs where a new commit was pushed to Amdkn/*
    updated_gitlinks = 0
    for r in results:
        sha = r.get("sha", "")
        if len(sha) == 40 and r.get("pushed_to_amdkn"):
            run_git(ROOT, ["update-index", "--add", "--cacheinfo", f"160000,{sha},{r['path']}"])
            updated_gitlinks += 1

    # Update SQLite EGM Ledger
    if DB_PATH.exists():
        conn = sqlite3.connect(str(DB_PATH))
        now = time.time()
        for r in results:
            if str(r.get("status", "")).startswith("MUTATED_ACTIVE"):
                mid = f"EGM-{r['path'].replace('/', '_')}"
                conn.execute(
                    "UPDATE goldfish_missions SET status='COMPLETED', completed_at=? WHERE mission_id=?",
                    (now, mid),
                )
        conn.commit()
        conn.close()

    summary = {
        "total_submodules": len(modules),
        "mutated_active": sum(1 for r in results if str(r.get("status", "")).startswith("MUTATED_ACTIVE")),
        "mutated_local_git": sum(1 for r in results if r.get("status") == "MUTATED_ACTIVE_LOCAL_GIT"),
        "pushed_to_github": sum(1 for r in results if r.get("pushed_to_amdkn")),
        "parent_gitlinks_updated": updated_gitlinks,
    }
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    import sys
    do_push = "--push" in sys.argv
    main(push_remote=do_push)
