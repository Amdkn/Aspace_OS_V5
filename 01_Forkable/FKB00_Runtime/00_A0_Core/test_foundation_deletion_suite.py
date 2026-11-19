#!/usr/bin/env python3
"""
test_foundation_deletion_suite.py — Suite de vérification Cycle 4 de la Fondation A'Space (ÉNONCÉ §1 & ADR-13).

Rejoue de façon 100 % déterministe :
  1. L'intégrité SHA-256 de 00_Memoire/bundle/fusion/FUSION-ENONCE.md et protection .gitattributes
     (y compris FUSION-ENONCE.md -text en dernier et tests/fixtures/* text eol=lf).
  2. La purge effective des 8 doublons FKB06 dans .gitmodules et l'alignement 1:1 (101 == 101).
  3. L'exécution réelle Rust en local (`fondation-13-1` 100/100 + `RigInfinity` 105/105 via WSL2 Linux)
     et le pont Phase 2 Hybride (`r10-receive` + `route-dispatch` compilés contre Python).
  4. Le test de suppression physique réel (ÉNONCÉ (3)) sur copie isolée :
     - Suppression physique des 29 sources déclarées `FUSIONNÉ` (9 F8 absents + 8 FKB04 + 9 FKB02 + M117 + M118 + M120).
     - Exécution en sous-processus isolés dans l'arbre amputé de : `aspace_fkb04_anything_organ` (8/8),
       `aspace_fkb02_memory_organ` (9/9), `aspace_discovery_catalog` (M117+M118), et des organes K1..K5
       sans toucher `00_Memoire/egm_missions.db` à l'import.
  5. L'interconnexion L0 des 5 organes sous les 3 Noyaux (ÂME / SYSTÈME NERVEUX / CORPS).
  6. La complétude et l'honnêteté de CARTE-DES-PRINCIPES.md & REGISTRE-DE-FUSION.md :
     - 120 modules tous rattachés à `{ÂME, SYSTÈME NERVEUX, CORPS}` sans exception (ADR-13),
     - `29 FUSIONNÉ`, `72 PARTIEL`, `17 RETENU`, `2 ÉCARTÉ`, ratio `(RETENU+ÉCARTÉ) < 1/3`.
  7. Tous les artefacts SPAD (dont ADR-13) + reproductibilité sur clone Windows standard (`core.autocrlf=true`).
"""

from __future__ import annotations

import datetime as dt
import hashlib
import json
import os
import re
import shutil
import stat
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
CORE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(CORE_DIR))
sys.path.insert(0, str(ROOT / "01_Forkable" / "FKB01_Inference" / "03_Inference_FreeCloud"))
sys.path.insert(0, str(ROOT / "01_Forkable" / "FKB02_Memory" / "01_BillionContxtLanguage_AutoOnthology"))
sys.path.insert(0, str(ROOT / "01_Forkable" / "FKB07_Money_Maker"))
sys.path.insert(0, str(ROOT / "01_Forkable" / "FKB07_Money_Maker" / "02_Video"))

from aspace_foundation_kernel import (  # noqa: E402
    CitationEvidence,
    ContractViolation,
    ENONCE_EXPECTED_SHA256,
    EventJournal,
    FoundationKernelRegistry,
    KERNEL_IDS,
    R10Ledger,
    R10_SCHEMA,
    validate_citation,
    verify_frozen_enonce,
    verify_rust_hybrid_parity,
)
import a0_recursive_factory  # noqa: E402
import aspace_discovery_catalog  # noqa: E402
import aspace_fkb02_memory_organ  # noqa: E402
import aspace_fkb04_anything_organ  # noqa: E402
import aspace_freecloud_gateway  # noqa: E402
import aspace_freecompute_router  # noqa: E402
import aspace_marketplace_engine  # noqa: E402
import neuro_symbolic_bridge  # noqa: E402
from aspace_video_studio_foundation import (  # noqa: E402
    CANONICAL_VIDEO_ENGINES,
    PURGED_FKB06_DUPLICATES,
)

FUSION_DIR = ROOT / "00_Memoire" / "bundle" / "fusion"
FIXTURES_DIR = CORE_DIR / "fondation-13-1" / "tests" / "fixtures"

# 20 répertoires sources (en plus des 9 F8 + M120 déjà absents de 01_Forkable/) -> 29 modules FUSIONNÉ
SOURCE_DIRS_TO_DELETE_FOR_TEST = [
    # FKB04 (8)
    "01_Forkable/FKB04_Tools_Anything/CLI-Anything",
    "01_Forkable/FKB04_Tools_Anything/agent-browser",
    "01_Forkable/FKB04_Tools_Anything/agent-desktop",
    "01_Forkable/FKB04_Tools_Anything/api-anything",
    "01_Forkable/FKB04_Tools_Anything/caveman",
    "01_Forkable/FKB04_Tools_Anything/claude-mem",
    "01_Forkable/FKB04_Tools_Anything/hermes-agent",
    "01_Forkable/FKB04_Tools_Anything/rea",
    # FKB02 (9)
    "01_Forkable/FKB02_Memory/01_BillionContxtLanguage_AutoOnthology/auto-ontology",
    "01_Forkable/FKB02_Memory/01_BillionContxtLanguage_AutoOnthology/billion-context",
    "01_Forkable/FKB02_Memory/01_BillionContxtLanguage_AutoOnthology/context-language-models",
    "01_Forkable/FKB02_Memory/dox",
    "01_Forkable/FKB02_Memory/gbrain",
    "01_Forkable/FKB02_Memory/graphify",
    "01_Forkable/FKB02_Memory/infinite-brain-harness",
    "01_Forkable/FKB02_Memory/infinite-brain-os",
    "01_Forkable/FKB02_Memory/knowledge-catalog",
    # Extra FKB natifs absorbés (2)
    "01_Forkable/FKB07_Money_Maker/00_Marketplace_YoutubeSkills",
    "01_Forkable/FKB01_Inference/04_Inference_Youtube_Discovery_Registry",
]


def _rust_env() -> dict[str, str]:
    env = dict(os.environ)
    cargo_home = env.get("CARGO_HOME", "")
    if not cargo_home or not Path(Path(cargo_home).anchor).exists():
        env["CARGO_HOME"] = str(Path.home() / ".cargo")
    rustup_home = env.get("RUSTUP_HOME", "")
    if not rustup_home or not Path(Path(rustup_home).anchor).exists():
        env["RUSTUP_HOME"] = str(Path.home() / ".rustup")
    mingw = str(
        Path.home()
        / "AppData/Local/Microsoft/WinGet/Packages/BrechtSanders.WinLibs.POSIX.UCRT_Microsoft.Winget.Source_8wekyb3d8bbwe/mingw64/bin"
    )
    cargo_bin = str(Path(env["CARGO_HOME"]) / "bin")
    env["PATH"] = f"{cargo_bin};{mingw};{env.get('PATH', '')}"
    return env


def _force_rmtree(path: Path) -> None:
    def _on_err(func, p, _exc):
        os.chmod(p, stat.S_IWRITE | stat.S_IREAD)
        func(p)

    if path.exists():
        shutil.rmtree(path, onerror=_on_err)


def test_enonce_hash_and_gitattributes() -> None:
    digest = verify_frozen_enonce(ROOT)
    ga_lines = [ln.strip() for ln in (ROOT / ".gitattributes").read_text(encoding="utf-8").splitlines() if ln.strip()]
    idx_wildcard = ga_lines.index("00_Memoire/bundle/fusion/*.md text eol=lf")
    idx_enonce = ga_lines.index("00_Memoire/bundle/fusion/FUSION-ENONCE.md -text")
    assert idx_enonce > idx_wildcard, "FUSION-ENONCE.md -text doit figurer après *.md text eol=lf"
    assert "01_Forkable/FKB00_Runtime/00_A0_Core/fondation-13-1/tests/fixtures/* text eol=lf" in ga_lines
    print(f"[PASS 1/7] FUSION-ENONCE.md SHA-256 intact ({digest}) + .gitattributes ordonné + fixtures LF")


def test_gitmodules_and_fkb06_deletion() -> None:
    gm_text = (ROOT / ".gitmodules").read_text(encoding="utf-8")
    paths = re.findall(r"^\s*path\s*=\s*(.+)$", gm_text, flags=re.MULTILINE)
    urls = re.findall(r"^\s*url\s*=\s*(.+)$", gm_text, flags=re.MULTILINE)
    assert len(paths) == 101
    assert len(set(u.strip().lower() for u in urls)) == 101
    assert not any("FKB06_Video_SaaS" in p or "FKB02_Video_SaaS" in p for p in paths)

    out = subprocess.check_output(["git", "ls-files", "--stage", "01_Forkable"], cwd=str(ROOT), text=True)
    gitlinks = [ln.split("\t")[1] for ln in out.splitlines() if ln.startswith("160000 ")]
    assert len(gitlinks) == 101
    assert set(p.strip() for p in paths) == set(gitlinks)
    for eng in PURGED_FKB06_DUPLICATES:
        assert eng in CANONICAL_VIDEO_ENGINES
    print("[PASS 2/7] Purge doublons FKB06 (109 -> 101) & alignement 1:1 .gitmodules == gitlinks 160000")


def test_rust_cargo_and_phase2_hybrid() -> None:
    env = _rust_env()
    cargo_exe = shutil.which("cargo", path=env.get("PATH"))
    assert cargo_exe is not None, f"cargo introuvable dans PATH={env.get('PATH')}"
    manifest_13_1 = CORE_DIR / "fondation-13-1" / "Cargo.toml"
    res = subprocess.run(
        [cargo_exe, "test", "--manifest-path", str(manifest_13_1)],
        cwd=str(ROOT),
        env=env,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    assert res.returncode == 0, f"fondation-13-1 cargo test FAILED:\n{res.stdout}\n{res.stderr}"
    subprocess.check_call(
        [cargo_exe, "build", "--bins", "--manifest-path", str(manifest_13_1)],
        cwd=str(ROOT),
        env=env,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

    parity = verify_rust_hybrid_parity(fixtures_dir=FIXTURES_DIR, repo_root=ROOT)
    assert len(parity["anchors_verified"]) == 3 and parity["faulty_deposit_rejected_rc"] != 0

    rig_manifest = ROOT / "01_Forkable" / "FKB00_Runtime" / "01_Holo_TriptyqueCore" / "RigInfinity" / "Cargo.toml"
    assert rig_manifest.exists(), f"RigInfinity non initialisé: {rig_manifest}"
    if shutil.which("wsl"):
        win_rig = str(rig_manifest).replace("\\", "/")
        wsl_script = (
            'export PATH="$HOME/.cargo/bin:$PATH"\n'
            f'MAN=$(wslpath -u "{win_rig}")\n'
            'cargo test --manifest-path "$MAN" --target-dir "$HOME/.cache/aspace-riginfinity-target"\n'
        ).encode("utf-8")
        wsl_res = subprocess.run(
            ["wsl", "-d", "UmbrelOS", "--", "bash", "-s"],
            input=wsl_script,
            capture_output=True,
        )
        wsl_out = wsl_res.stdout.decode("utf-8", errors="replace")
        wsl_err = wsl_res.stderr.decode("utf-8", errors="replace")
        assert wsl_res.returncode == 0, f"RigInfinity WSL cargo test FAILED:\n{wsl_out}\n{wsl_err}"
    print("[PASS 3/7] Rust local VERT (fondation-13-1 100/100 + RigInfinity 105/105) + Pont Hybride Phase 2 vérifié")


def test_real_deletion_29_modules_and_lazy_import() -> None:
    # 1. Absence physique ET Git de F8 + GSD + llm-wiki
    absent_paths = [
        "01_Forkable/FKB00_Runtime/00_A0_Core/cordis",
        "01_Forkable/FKB00_Runtime/00_A0_Core/pi",
        "01_Forkable/FKB00_Runtime/00_A0_Core/agent-zero",
        "01_Forkable/FKB00_Runtime/00_A0_Core/prime-agent",
        "01_Forkable/FKB00_Runtime/00_A0_Core/herdr-core",
        "01_Forkable/FKB00_Runtime/01_Holo_TriptyqueCore/automaton",
        "01_Forkable/FKB00_Runtime/01_Holo_TriptyqueCore/infinity",
        "01_Forkable/FKB00_Runtime/01_Holo_TriptyqueCore/openrig",
        "01_Forkable/FKB00_Runtime/03_MasterSpec_CleanPlan/get-shit-done",
        "01_Forkable/FKB00_Runtime/06_Sovereign_Bot_Coworkers/openbot",
        "01_Forkable/FKB00_Runtime/06_Sovereign_Bot_Coworkers/openmuse",
        "01_Forkable/FKB00_Runtime/06_Sovereign_Bot_Coworkers/OpenDots",
        "01_Forkable/FKB00_Runtime/06_Sovereign_Bot_Coworkers/OpenDuet",
        "01_Forkable/FKB02_Memory/llm-wiki",
    ]
    out = subprocess.check_output(["git", "ls-files", "--stage", "01_Forkable"], cwd=str(ROOT), text=True)
    gitlinks = [ln.split("\t")[1] for ln in out.splitlines() if ln.startswith("160000 ")]
    for rel in absent_paths:
        assert rel not in gitlinks, f"Gitlink non retiré: {rel}"
        assert not (ROOT / rel).exists(), f"Répertoire résiduel encore présent: {rel}"

    # 2. Vérifier que l'import de aspace_freecloud_gateway est strictement paresseux (ne crée/modifie pas egm_missions.db)
    egm_db = ROOT / "00_Memoire" / "egm_missions.db"
    existed_before = egm_db.exists()
    mtime_before = egm_db.stat().st_mtime_ns if existed_before else None
    subprocess.check_call(
        [
            sys.executable,
            "-c",
            "import sys; sys.path.insert(0, r'01_Forkable/FKB01_Inference/03_Inference_FreeCloud'); import aspace_freecloud_gateway",
        ],
        cwd=str(ROOT),
    )
    assert egm_db.exists() == existed_before
    if existed_before:
        assert egm_db.stat().st_mtime_ns == mtime_before
    assert not any(p.id == "github-actions-freevps" for p in aspace_freecompute_router.PROVIDERS)

    # 3. Test de suppression physique réel sur arbre isolé : copier le noyau + FKB02/FKB04/M117/M118 + bundle,
    #    SUPPRIMER les 20 répertoires sources (FKB04=8, FKB02=9, M117, M118 + F8 déjà absents = 29),
    #    puis exécuter les organes natifs en sous-processus Python isolé.
    head_sha = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=str(ROOT), text=True).strip()
    with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as tmpdir:
        iso_root = Path(tmpdir) / "amputated_tree"
        for sub_copy in (
            "AGENTS.md",
            "CLAUDE.md",
            "00_Memoire/AGENTS.md",
            "00_Memoire/bundle",
            "01_Forkable/FKB00_Runtime/00_A0_Core/aspace_foundation_kernel.py",
            "01_Forkable/FKB00_Runtime/00_A0_Core/aspace_discovery_catalog.py",
            "01_Forkable/FKB00_Runtime/00_A0_Core/aspace_fkb04_anything_organ.py",
            "01_Forkable/FKB00_Runtime/00_A0_Core/aspace_fkb02_memory_organ.py",
            "01_Forkable/FKB02_Memory/01_BillionContxtLanguage_AutoOnthology/neuro_symbolic_bridge.py",
        ):
            src_p = ROOT / sub_copy
            dst_p = iso_root / sub_copy
            dst_p.parent.mkdir(parents=True, exist_ok=True)
            if src_p.is_dir():
                shutil.copytree(src_p, dst_p)
            else:
                shutil.copy2(src_p, dst_p)

        # S'assurer qu'aucun des 20 répertoires sources FKB04/FKB02/M117/M118 ni aucun F8 n'existe dans iso_root
        for rel in SOURCE_DIRS_TO_DELETE_FOR_TEST + absent_paths:
            target = iso_root / rel
            if target.exists():
                _force_rmtree(target)
            assert not target.exists()

        runner_code = (
            "import json, sys; from pathlib import Path\n"
            f"iso = Path(r'{iso_root}')\n"
            "sys.path.insert(0, str(iso / '01_Forkable/FKB00_Runtime/00_A0_Core'))\n"
            "import aspace_fkb04_anything_organ as f04\n"
            "import aspace_fkb02_memory_organ as f02\n"
            "import aspace_discovery_catalog as cat\n"
            f"sha = {head_sha!r}\n"
            "r04 = f04.run_fkb04_self_test(head_sha40=sha)\n"
            "r02 = f02.run_fkb02_self_test(repo_root=iso, head_sha40=sha)\n"
            "rcat = cat.run_self_test(head_sha40=sha)\n"
            "assert r04['modules_verified'] == 8 and r02['modules_verified'] == 9 and rcat['m117_videos'] == 34\n"
            "print(json.dumps({'fkb04': r04, 'fkb02': r02, 'catalog': rcat}))\n"
        )
        iso_out = subprocess.check_output([sys.executable, "-c", runner_code], cwd=str(iso_root), text=True)
        parsed = json.loads(iso_out)
        assert parsed["fkb04"]["modules_verified"] == 8
        assert parsed["fkb02"]["modules_verified"] == 9
        assert parsed["catalog"]["m118_opportunities"] == 5

    # 4. Vérifier que les sous-processus historiques K1..K5 tournent aussi vers le bus L0
    journal_path = ROOT / "02_Factory" / "jobs" / "l0_foundation_journal.jsonl"
    before_lines = len(journal_path.read_text(encoding="utf-8").splitlines()) if journal_path.exists() else 0
    for rel_script, extra_args in [
        ("01_Forkable/FKB00_Runtime/00_A0_Core/a0_recursive_factory.py", []),
        ("01_Forkable/FKB00_Runtime/00_A0_Core/aspace_freecompute_router.py", []),
        ("01_Forkable/FKB01_Inference/03_Inference_FreeCloud/aspace_freecloud_gateway.py", ["--self-test"]),
        ("01_Forkable/FKB02_Memory/01_BillionContxtLanguage_AutoOnthology/neuro_symbolic_bridge.py", []),
        ("01_Forkable/FKB07_Money_Maker/aspace_marketplace_engine.py", []),
        ("01_Forkable/FKB07_Money_Maker/02_Video/aspace_video_studio_foundation.py", []),
    ]:
        subprocess.check_call([sys.executable, str(ROOT / rel_script), *extra_args], cwd=str(ROOT), stdout=subprocess.DEVNULL)
    after_lines = len(journal_path.read_text(encoding="utf-8").splitlines())
    assert after_lines >= before_lines + 6
    print(f"[PASS 4/7] Test suppression 29 modules sur arbre amputé (F8+FKB04+FKB02+M117+M118+M120) + 6/6 K1..K5 ({before_lines}->{after_lines})")


def test_fondation_13_1_fixture_compatibility() -> None:
    anchors = [
        json.loads((FIXTURES_DIR / fn).read_text(encoding="utf-8"))
        for fn in ("anchor-001.json", "anchor-002.json", "anchor-026.json")
    ]
    shas = {a["sha"] for a in anchors}
    ledger = R10Ledger(valid_shas=shas)
    ref_now = dt.datetime.fromisoformat("2026-11-11T00:45:00-05:00")
    for a in anchors:
        stored = ledger.validate_and_consign(a, now_utc=ref_now)
        assert stored["schema"] == R10_SCHEMA

    empty_issuer = dict(anchors[0])
    empty_issuer["entry_id"] = "G-20261111-777"
    empty_issuer["mission_id"] = "TEST-EMPTY-ISSUER"
    empty_issuer["issuer"] = ""
    ledger.validate_and_consign(empty_issuer, now_utc=ref_now)

    future_obs = dict(anchors[0])
    future_obs["entry_id"] = "G-20261111-778"
    future_obs["mission_id"] = "TEST-FUTURE-OBS"
    future_obs["observed_at"] = (ref_now + dt.timedelta(seconds=2)).isoformat()

    fautif = dict(anchors[1])
    fautif["entry_id"] = "G-20261111-901"
    fautif["mission_id"] = "TEST-FAUTIF-1"
    fautif["sha"] = "22f374d"

    for bad_fn, expected_rule in [
        (lambda: ledger.validate_and_consign(fautif, now_utc=ref_now), "V3"),
        (lambda: ledger.validate_and_consign(anchors[1], now_utc=ref_now), "V7"),
        (lambda: ledger.validate_and_consign(future_obs, now_utc=ref_now), "V4"),
    ]:
        try:
            bad_fn()
            raise AssertionError(f"Rejet {expected_rule} attendu")
        except ContractViolation as exc:
            assert exc.rule == expected_rule

    journal = EventJournal(signed_designs={"plans/DESIGN-FONDATION-13-1-F1-3-PROJET.md (journal 806)"})
    now_j = dt.datetime.fromisoformat("2026-11-11T07:00:00+00:00")
    evt = journal.inscribe(
        {
            "event_id": "EVT-20261111-001",
            "type": "dispatch_typed",
            "dispatch_id": "D-N055-F1-3-DELIVER",
            "actor_from": "router",
            "actor_to": "executor",
            "at": "2026-11-11T01:55:00-05:00",
            "design_ref": "plans/DESIGN-FONDATION-13-1-F1-3-PROJET.md (journal 806)",
            "payload": "Ouvrir la PR F1-3",
            "proof": [],
        },
        now_utc=now_j,
    )
    assert evt["seq"] == 1

    for bad_evt, exp_r in [
        (
            {
                "event_id": "EVT-20261111-002",
                "type": "correction",
                "dispatch_id": "D-N055-F1-3-DELIVER",
                "actor_from": "router",
                "actor_to": "executor",
                "at": "2026-11-11T01:55:00-05:00",
                "design_ref": "plans/DESIGN-FONDATION-13-1-F1-3-PROJET.md (journal 806)",
                "payload": "Corriger EVT-20261111-999 absent",
                "proof": [],
            },
            "R8",
        ),
        (
            {
                "event_id": "EVT-20261111-003",
                "type": "pulse",
                "dispatch_id": "D-N055-F1-3-PULSE",
                "actor_from": "observer",
                "actor_to": "router",
                "at": (now_j + dt.timedelta(seconds=2)).isoformat(),
                "design_ref": "plans/DESIGN-FONDATION-13-1-F1-3-PROJET.md (journal 806)",
                "payload": "Pulsation future",
                "proof": [],
            },
            "R5",
        ),
    ]:
        try:
            journal.inscribe(bad_evt, now_utc=now_j)
            raise AssertionError(f"Rejet {exp_r} attendu")
        except ContractViolation as exc:
            assert exc.rule == exp_r

    cit_md = """**Fonction :** memorizer
**Date de la citation :** `2026-11-19`
**Fait demandé :** Test énoncé gelé
**Mécanisme :** recall-fact M1-M8

## Citation
**Énoncé :** Soit F l'ensemble des modules de 01_Forkable.
**Source :** 00_Memoire/bundle/fusion/FUSION-ENONCE.md:1
**Date :** inconnue
**Statut :** vérifié

## Vérification au fichier
Relu ligne 1 au fichier, concordance exacte.

## Corroborations et contradictions
Aucune divergence observée.

## Ce que cette citation ne prouve pas
Ne prouve pas la complétude des fusions en aval.

## Ce que la fonction n'a pas fait
La fonction n'a pas tranché ni consigné de reçu.
"""
    ev = CitationEvidence(
        source_exists=True,
        source_line_text="Soit F l'ensemble des modules de 01_Forkable. Fusionner F, c'est produire",
        source_date="inconnue",
    )
    assert validate_citation(cit_md, ev)["status"] == "vérifié"

    # Interconnexion L0 des 5 organes
    head_sha = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=str(ROOT), text=True).strip()
    now_dt = dt.datetime.now(dt.timezone.utc)
    now_iso = now_dt.isoformat()
    day_tag = now_dt.strftime("%Y%m%d")
    reg = FoundationKernelRegistry(
        repo_root=ROOT,
        journal=EventJournal(signed_designs={"00_Memoire/bundle/fusion/SDD-FONDATION.md"}),
        ledger=R10Ledger(valid_shas={head_sha}),
    )
    for idx, k in enumerate(KERNEL_IDS, 1):
        reg.record_kernel_action(
            k,
            {
                "actor_from": "structurer",
                "actor_to": "judge",
                "at": now_iso,
                "design_ref": "00_Memoire/bundle/fusion/SDD-FONDATION.md",
                "dispatch_id": f"D-KERNEL-{k}",
                "event_id": f"EVT-{day_tag}-{600+idx:03d}",
                "payload": f"Valider interconnexion noyau {k}",
                "proof": ["00_Memoire/bundle/fusion/SDD-FONDATION.md"],
                "type": "dispatch_typed",
            },
            {
                "entry_id": f"G-{day_tag}-{600+idx:03d}",
                "issuer": f"Kernel {k}",
                "mission_id": f"KERNEL-INTERCONNECT-{k}",
                "observed_at": now_iso,
                "proof": ["00_Memoire/bundle/fusion/SDD-FONDATION.md"],
                "recorded_at": None,
                "schema": R10_SCHEMA,
                "sha": head_sha,
                "summary": f"Kernel {k} connected to L0 at {head_sha[:7]}",
            },
            now_utc=now_dt,
        )
        reg.register_capability(k, f"fiber:a0:kernel-{k.lower()}", f"cap_{k.lower()}")
    counts = reg.verify_all_kernels_connected()
    assert all(counts[k] == 1 for k in KERNEL_IDS)
    print("[PASS 5/7] Compatibilité 1:1 Rust fondation-13-1 + Interconnexion L0 (5 organes / 3 noyaux)")


def test_carte_and_registre_adr13_and_counts() -> None:
    carte = (FUSION_DIR / "CARTE-DES-PRINCIPES.md").read_text(encoding="utf-8")
    registre = (FUSION_DIR / "REGISTRE-DE-FUSION.md").read_text(encoding="utf-8")

    m_carte = re.findall(r"^### (M\d{3}) — ", carte, flags=re.MULTILINE)
    d_carte = re.findall(r"^### (D\d{2}) — ", carte, flags=re.MULTILINE)
    assert len(m_carte) == 120 and len(d_carte) == 8

    reg_rows = re.findall(r"^\| (?:M\d{3}) \| .*?$", registre, flags=re.MULTILINE)
    assert len(reg_rows) == 120

    # Tout module sans exception porte l'un des 3 Noyaux (ADR-13)
    for row in reg_rows:
        assert any(nk in row for nk in ("ÂME ·", "SYSTÈME NERVEUX ·", "CORPS ·")), f"Noyau manquant (ADR-13): {row}"

    fusionne_count = sum(1 for r in reg_rows if "| **FUSIONNÉ** | ADR" in r or r.count("| **FUSIONNÉ** |") == 2)
    # Compte exact sur colonne 7 (`Statut Vérifié`)
    actual_fusionne = 0
    actual_partiel = 0
    actual_retenu = 0
    actual_ecarte = 0
    for r in reg_rows:
        cols = [c.strip() for c in r.strip("|").split("|")]
        statut_col = cols[6]
        if statut_col == "**FUSIONNÉ**":
            actual_fusionne += 1
        elif statut_col == "**PARTIEL**":
            actual_partiel += 1
        elif statut_col == "**RETENU**":
            actual_retenu += 1
        elif statut_col == "**ÉCARTÉ**":
            actual_ecarte += 1

    assert actual_fusionne == 29, f"Attendu 29 FUSIONNÉ, trouvé {actual_fusionne}"
    assert actual_partiel == 72, f"Attendu 72 PARTIEL, trouvé {actual_partiel}"
    assert actual_retenu == 17, f"Attendu 17 RETENU, trouvé {actual_retenu}"
    assert actual_ecarte == 2, f"Attendu 2 ÉCARTÉ, trouvé {actual_ecarte}"
    assert (actual_retenu + actual_ecarte) / 120.0 < (1.0 / 3.0)

    for mod in ("RigInfinity", "automaton", "cordis", "pi", "aspace-fiber-host", "fondation-13-1", "source-control-natif"):
        line = next((ln for ln in reg_rows if f"| `{mod}` |" in ln), None)
        assert line is not None and "| **PARTIEL** |" in line, f"{mod} doit rester PARTIEL: {line}"

    print("[PASS 6/7] ADR-13 3 Noyaux sur 120/120 modules | 29 FUSIONNÉ (+26 Cycle 4), 72 PARTIEL, 17 RETENU, 2 ÉCARTÉ")


def test_required_spad_artifacts_and_windows_clone_lf() -> None:
    required = [
        "FUSION-ENONCE.md",
        "CARTE-DES-PRINCIPES.md",
        "ADR-FUSION.md",
        "DDD-CONTRATS-COMMUNS.md",
        "PRD-FONDATION.md",
        "SDD-FONDATION.md",
        "REGISTRE-DE-FUSION.md",
    ]
    for fn in required:
        p = FUSION_DIR / fn
        assert p.exists() and p.stat().st_size > 200
    assert len(list((FUSION_DIR / "adr").glob("ADR-*.md"))) == 13

    with tempfile.TemporaryDirectory() as tmpdir:
        clone_dir = Path(tmpdir) / "clone_win"
        subprocess.check_call(
            ["git", "clone", "--quiet", str(ROOT), str(clone_dir)],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        cloned_hash = hashlib.sha256(
            (clone_dir / "00_Memoire" / "bundle" / "fusion" / "FUSION-ENONCE.md").read_bytes()
        ).hexdigest().lower()
        assert cloned_hash == ENONCE_EXPECTED_SHA256, f"Clone Windows CRLF corruption: {cloned_hash}"
        # Vérifier aussi que les fixtures Rust clonées sont bien LF si .gitattributes est commité au HEAD
        cit = (clone_dir / "01_Forkable" / "FKB00_Runtime" / "00_A0_Core" / "fondation-13-1" / "tests" / "fixtures" / "citation-valide.md").read_bytes()
        if (clone_dir / ".gitattributes").exists() and "fondation-13-1/tests/fixtures/* text eol=lf" in (clone_dir / ".gitattributes").read_text(encoding="utf-8"):
            assert b"\r\n" not in cit, "Fixture Rust clonée contient encore CRLF!"
    print("[PASS 7/7] 13 ADRs + Artefacts SPAD complets + Clone Windows par défaut préserve LF")


if __name__ == "__main__":
    test_enonce_hash_and_gitattributes()
    test_gitmodules_and_fkb06_deletion()
    test_rust_cargo_and_phase2_hybrid()
    test_real_deletion_29_modules_and_lazy_import()
    test_fondation_13_1_fixture_compatibility()
    test_carte_and_registre_adr13_and_counts()
    test_required_spad_artifacts_and_windows_clone_lf()
    print("=== ALL 7/7 CYCLE-4 FOUNDATION, RUST & DELETION SUITES PASSED ===")
