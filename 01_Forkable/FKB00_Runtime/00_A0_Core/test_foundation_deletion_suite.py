#!/usr/bin/env python3
"""
test_foundation_deletion_suite.py — Suite de vérification Cycle 6 de la Fondation A'Space (ÉNONCÉ §1 & ADR-15).

Rejoue de façon 100 % déterministe, sans compteur codé en dur, sans tolérance aux clés en trop
et avec détection automatique de sabotage sur chaque fonction/donnée déclarée :
  1. L'intégrité SHA-256 de 00_Memoire/bundle/fusion/FUSION-ENONCE.md et protection .gitattributes.
  2. La purge effective des 8 doublons FKB06 dans .gitmodules et l'alignement 1:1 (101 == 101).
  3. L'exécution réelle Rust en local (`fondation-13-1` + `RigInfinity`) et le pont Phase 2 Hybride.
  4. Le test différentiel strict (`==`) + anti-sabotage avant/après suppression physique (ÉNONCÉ (3)) :
     - Phase A : exécution des sources d'origine M044, M050, M056, M084 (`video-director`), M117, M118
       sur toutes leurs fonctions, cas limites et structures -> `oracle_outputs`.
     - Phase B : suppression physique effective des répertoires sources (dont `video-director`).
     - Phase C : exécution des organes natifs dans l'arbre amputé, vérification stricte `organ == oracle`
       (zéro clé en trop, zéro normalisation masqueuse), puis boucle de sabotage de chaque fonction/table
       exigeant l'échec à 100 %, et consignation des reçus R10 mesurés.
  5. L'interconnexion L0 des 5 organes (K1..K5) sous les 3 Noyaux (`ÂME / SYSTÈME NERVEUX / CORPS`).
  6. La complétude et l'honnêteté dynamique de CARTE-DES-PRINCIPES.md & REGISTRE-DE-FUSION.md :
     - 120 modules tous rattachés à `{ÂME, SYSTÈME NERVEUX, CORPS}` sans exception (ADR-15),
     - égalité stricte `registry_fusionne == proven_fusionne` calculée depuis les preuves exécutées,
     - `M058 agent-desktop` maintenu `PARTIEL` tant que `desktop_live_verified` est faux,
     - ratio `(RETENU+ÉCARTÉ) < 1/3` et justifications individuelles non vides.
  7. Tous les artefacts SPAD (>= 15 ADRs dont ADR-15) + reproductibilité sur clone Windows standard.
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
    ROOT_KERNELS,
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

RIG_INFINITY_PROVEN_F8 = frozenset({
    "OpenDots",
    "OpenDuet",
    "agent-zero",
    "herdr-core",
    "infinity",
    "openbot",
    "openmuse",
    "openrig",
    "prime-agent",
})

SUBMODULE_SENTINELS = (
    (
        "01_Forkable/FKB00_Runtime/00_A0_Core/a0-plugins",
        "scripts/plugin_resolution.py",
    ),
    (
        "01_Forkable/FKB02_Memory/01_BillionContxtLanguage_AutoOnthology/context-language-models",
        "clm/clm_harness/context_utils/context_string.py",
    ),
    (
        "01_Forkable/FKB02_Memory/knowledge-catalog",
        "okf/src/reference_agent/bundle/document.py",
    ),
    (
        "01_Forkable/FKB04_Tools_Anything/CLI-Anything",
        "cli-anything-plugin/skill_generator.py",
    ),
    (
        "01_Forkable/FKB07_Money_Maker/02_Video/video-director",
        "video-director/scripts/check_timeline.py",
    ),
    (
        "01_Forkable/FKB07_Money_Maker/01_Trading/tradingview-indicator-search-mcp-server",
        "src/parse.js",
    ),
)

SOURCE_DIRS_TO_DELETE_FOR_TEST = [
    # FKB00 CORPS (M001)
    "01_Forkable/FKB00_Runtime/00_A0_Core/a0-plugins",
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
    # FKB07 M084 video-director + M074 tradingview-indicator-search + Extra FKB natifs absorbés (M117, M118)
    "01_Forkable/FKB07_Money_Maker/02_Video/video-director",
    "01_Forkable/FKB07_Money_Maker/01_Trading/tradingview-indicator-search-mcp-server",
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
    sep = ";" if os.name == "nt" else ":"
    env["PATH"] = f"{cargo_bin}{sep}{mingw}{sep}{env.get('PATH', '')}"
    return env


def _force_rmtree(path: Path) -> None:
    def _on_err(func, p, _exc):
        os.chmod(p, stat.S_IWRITE | stat.S_IREAD)
        func(p)

    if path.exists():
        shutil.rmtree(path, onerror=_on_err)


def _ensure_upstream_submodules() -> None:
    """Initialise les sous-modules requis sur clone neuf (sans masquer une absence)."""
    for sub_rel, sentinel_rel in SUBMODULE_SENTINELS:
        sentinel = ROOT / sub_rel / sentinel_rel
        if sentinel.exists():
            continue
        rc = subprocess.run(
            ["git", "-c", "protocol.file.allow=always", "submodule", "update", "--init", "--depth", "1", "--", sub_rel],
            cwd=str(ROOT),
            capture_output=True,
            text=True,
        ).returncode
        if rc != 0 or not sentinel.exists():
            subprocess.check_call(
                ["git", "-c", "protocol.file.allow=always", "submodule", "update", "--init", "--", sub_rel],
                cwd=str(ROOT),
            )
        assert sentinel.exists(), f"Source amont requise absente après init submodule: {sentinel}"


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


def test_rust_cargo_and_phase2_hybrid() -> set[str]:
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
    if not rig_manifest.exists():
        subprocess.check_call(
            ["git", "-c", "protocol.file.allow=always", "submodule", "update", "--init", "--depth", "1", "--", "01_Forkable/FKB00_Runtime/01_Holo_TriptyqueCore/RigInfinity"],
            cwd=str(ROOT),
        )
    assert rig_manifest.exists(), f"RigInfinity non initialisé: {rig_manifest}"

    rig_verified = False
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
        rig_verified = True
    elif sys.platform.startswith("linux"):
        lin_res = subprocess.run(
            [cargo_exe, "test", "--manifest-path", str(rig_manifest)],
            cwd=str(ROOT),
            env=env,
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
        assert lin_res.returncode == 0, f"RigInfinity Linux cargo test FAILED:\n{lin_res.stdout}\n{lin_res.stderr}"
        rig_verified = True

    proven = set(RIG_INFINITY_PROVEN_F8) if rig_verified else set()
    print(f"[PASS 3/7] Rust local VERT (fondation-13-1 + Pont Hybride Phase 2 ; RigInfinity={rig_verified} -> {len(proven)} F8 prouvés)")
    return proven


def _build_differential_inputs() -> dict:
    return {
        "m044": {
            "content_cases": [
                "abc",
                "",
                ["a", {"type": "text", "text": "b"}, {"text": "c"}],
                [],
                {"text": "abc"},
                ["caption", {"type": "image_url", "image_url": "image"}],
                [{"type": "tool_use", "id": "t1"}],
                None,
                42,
            ],
            "render_msgs": [
                {
                    "role": "assistant",
                    "reasoning_content": "R",
                    "content": [{"type": "text", "text": "C"}],
                    "tool_calls": [{"function": {"name": "bash", "arguments": "ARG"}}],
                },
                {
                    "role": "assistant",
                    "reasoning_content": "R2",
                    "content": "Body",
                    "tool_calls": [
                        {"function": {"name": "read", "arguments": {"x": 1}}},
                        {"function": {"name": "write", "arguments": None}},
                    ],
                },
                {"role": "assistant", "reasoning_content": "OnlyReason", "content": []},
                {"role": "assistant", "content": None, "tool_calls": [{"function": {"name": "ping", "arguments": "{}"}}]},
                {"role": "user", "content": "Simple user"},
                {},
            ],
            "conversations": [
                [
                    {"role": "system", "content": "SYSTEM_SENTINEL"},
                    {"role": "user", "content": "TASK_SENTINEL"},
                    {"role": "assistant", "reasoning_content": "Think", "content": "A"},
                    {"role": "tool", "content": "T", "tool_call_id": "call_1"},
                    {"role": "user", "content": "Follow-up"},
                ],
                [
                    {"role": "system", "content": "S1"},
                    {"role": "system", "content": "S2_must_not_merge"},
                    {"role": "assistant", "content": "Reply"},
                ],
                [
                    {"role": "system", "content": "SYS_B"},
                    {"role": "user", "content": "PROTECTED_U"},
                    {"role": "user", "content": "EDITABLE_U1"},
                    {"role": "user", "content": "EDITABLE_U2"},
                ],
            ],
            "parse_back_cases": [
                ("role_system", "[[CTX_TURN 99 role=system]]\npayload"),
                ("role_tool", "[[CTX_TURN 1 role=tool]]\npayload"),
                ("role_notes", "[[CTX_TURN 1 role=notes]]\npayload"),
                ("role_assistant", "[[CTX_TURN 1 role=ASSISTANT]]\npayload"),
                ("numbered_mixed", "[[CTX_TURN 1 role=assistant]]\nA\n[[CTX_TURN 1 role=user]]\nB"),
                ("empty_str", ""),
                ("whitespace", " \n\t "),
                ("empty_turn", "[[CTX_TURN 1 role=assistant]]\n "),
                (
                    "merge_assistant_drop_empty",
                    "[[CTX_TURN 1 role=assistant]]\n A \n[[CTX_TURN 2 role=tool]]\n \n[[CTX_TURN 3 role=assistant]]\n B \n",
                ),
                ("merge_user_tool", "[[CTX_TURN 1 role=user]]\nA\n[[CTX_TURN 2 role=tool]]\nB"),
                ("loose_only", "  loose note \n"),
                ("loose_plus_hdr", "loose note\n[[CTX_TURN 7 role=assistant]]\nanswer"),
                ("damaged_hdr", "[[CTX_TURN X role=user]]\nnaïve café\n[[CTX_TURN 2 role=assistant]]\nanswer"),
                ("non_str", 98765),
            ],
            "edit_gate_cases": {
                "resolve": [
                    (True, None), (False, None), ("fit", None), ("shrink", None),
                    (None, "fit"), (None, "shrink"), (None, "0"), (None, "1"), (None, ""),
                    ("invalid_gate", None),
                ],
                "may_grow": [
                    (True, 4096, 4000), (True, 4096, 4096), (True, 4096, 4097),
                    (False, 4096, 100), (True, 0, 100),
                ],
                "reject_rule": [(True, 4096), (True, 0), (False, 4096)],
            },
            "finish_policy_cases": {
                "modes": ["submit", "open_ended", "open-ended", "", "unknown_mode"],
                "commands": [
                    "COMPLETE_TASK_AND_SUBMIT_FINAL_OUTPUT",
                    "echo COMPLETE_TASK_AND_SUBMIT_FINAL_OUTPUT",
                    "  /bin/echo 'COMPLETE_TASK_AND_SUBMIT_FINAL_OUTPUT'  ",
                    'echo "COMPLETE_TASK_AND_SUBMIT_FINAL_OUTPUT" && ls',
                    "",
                ],
            },
            "lm_compat_models": [
                "gpt-5-4", "openai/gpt-5-4-mini", "gpt-5-4-nano",
                "gpt-o4-mini", "openrouter/gpt-5-turbo", "claude-3-5-sonnet", "",
            ],
        },
        "m050": {
            "synthetic_docs": [
                (
                    "valid_bq",
                    "---\ntype: BigQuery Table\ntitle: Sample\ndescription: A sample table.\ntags: [a, b]\ntimestamp: 2026-05-27T00:00:00+00:00\n---\n\n# Sample\n\nBody text.\n",
                ),
                ("valid_type_only", "---\ntype: X\n---\nMinimal.\n"),
                ("no_frontmatter", "# Hello\n\nNo frontmatter here.\n"),
                ("missing_type", "---\ntitle: Y\n---\nText.\n"),
                ("empty_type", "---\ntype: ''\ntitle: EmptyType\n---\nText.\n"),
                ("unterminated", "---\ntype: X\nstill in frontmatter\n"),
                ("invalid_yaml", "---\ntype: [unclosed\n---\nBody\n"),
                ("non_dict", "---\n- a\n- b\n---\nBody\n"),
            ],
            "trust_cases": [
                {},
                {"verified": None},
                {"verified": "unexpected-str"},
                {"verified": {"by": "human:amdkn", "at": "2026-06-25T09:00:00Z"}},
                {"verified": [{"by": "process:finance-nightly", "at": "x"}]},
                {"verified": [{"by": "process:ci", "at": "x"}, "bad", {"by": "human:amdkn", "at": "y"}]},
            ],
            "stale_cases": [
                {"stale_after": "2026-09-23T00:00:00Z"},
                {"stale_after": "2026-09-23T12:00:00+00:00"},
                {"stale_after": "2026-09-23T12:00:01+00:00"},
                {"stale_after": "2026-09-24T00:00:00Z"},
                {},
                {"stale_after": "not-a-date"},
                {"stale_after": "2026-09-23"},
                {"stale_after": "2026-09-23T00:00:00"},
            ],
            "stale_now_iso": "2026-09-23T12:00:00+00:00",
            "synth_fallback_cases": [
                [],
                [("A", "desc a"), ("B", "")],
                [("", "desc only")],
            ],
            "concept_id_cases": ["alpha", "datasets/ga4", "sub/my_doc-1.v2", "", "///", "../escape", "-leadingdash"],
        },
        "m056": {
            "cache_key_cases": [
                {
                    "software": "zotero",
                    "recipe": "reference-export",
                    "bundle_kind": "skill-md",
                    "source_fingerprint": "sha256:abc123",
                    "options": {"format": "bibtex", "indent": 2},
                    "harness_version": "0.4.1",
                },
                {
                    "software": "audacity",
                    "recipe": "audio-trim",
                    "bundle_kind": "preview",
                    "source_fingerprint": "sha256:def456",
                    "options": None,
                    "harness_version": None,
                },
                {
                    "software": "zotero",
                    "recipe": "reference-export",
                    "bundle_kind": "skill-md",
                    "source_fingerprint": "sha256:abc123",
                    "options": {"indent": 2, "format": "bibtex"},
                    "harness_version": "0.4.1",
                },
            ],
        },
        "m084": {
            "is_num_cases": [0, 1.5, -2.0, True, False, "1", None],
            "norm_cases": ["  Héllo,   Wörld!  C++ ", "", "A---B   C"],
            "read_time_cases": ["", "Hi", "One two", "One two three four five six"],
            "timelines": [
                {
                    "name": "valid_reads",
                    "tl": {
                        "meta": {"w": 1920, "h": 1080, "fps": 30, "dur": 6.0, "clock": "reads"},
                        "scenes": [
                            {"id": "s1", "start": 0.0, "end": 3.0, "beats": {"intro": 0.5, "hit": 2.0}, "transitionOut": {"why": "reveal"}},
                            {"id": "s2", "start": 3.0, "end": 6.0, "beats": {"end": 5.5}},
                        ],
                        "reads": [{"from": 0.5, "to": 1.5, "what": "card"}],
                        "cuts": [3.0],
                        "hero": {"t": 4.0},
                        "silences": [{"from": 2.8, "to": 3.5}],
                        "sfx": [{"at": "s1.hit"}, {"at": "t.0"}],
                        "captions": [{"from": 0.5, "to": 2.0, "text": "Widget launches now"}],
                        "texts": [
                            {"role": "hook", "text": "Widget", "from": 0.0, "to": 2.5, "px": 96},
                            {"role": "cta", "text": "Try", "in": "s1.hit", "out": "s2.end", "px": 56},
                        ],
                        "terms": ["Widget"],
                        "vo": [{"id": "l1", "text": "Widget overview", "words": [{"t": 0.5, "w": "Widget"}, {"t": 1.1, "w": "overview"}]}],
                    },
                },
                {"name": "bad_meta_early_return", "tl": {"meta": {"w": 0, "h": -1, "fps": True, "dur": "5"}}},
                {"name": "bad_music_loop_and_clock", "tl": {"meta": {"w": 1080, "h": 1920, "fps": 60, "dur": 5.0, "clock": "music", "bpm": 120, "meter": "4/4", "loop": True}}},
                {"name": "bad_clock_missing_bpm", "tl": {"meta": {"w": 1080, "h": 1080, "fps": 30, "dur": 4.0, "clock": "music"}}},
                {
                    "name": "scenes_gaps_beats_cuts_sfx_errors",
                    "tl": {
                        "meta": {"w": 1920, "h": 1080, "fps": 30, "dur": 5.0, "clock": "badclock"},
                        "scenes": [
                            {"id": "s1", "start": 1.0, "end": 0.5},
                            {"id": "s2", "start": 1.0, "end": 3.0, "beats": {"b_str": "x", "b_out": 9.0, "b_warn": 4.0}},
                        ],
                        "reads": [{"from": 0.1, "to": 0.4, "what": "fast"}],
                        "cuts": [0.0, 9.0],
                        "hero": {"t": 1.0},
                        "silences": [{"from": 0.2, "to": 0.4}],
                        "sfx": [{"at": "s2.missing"}],
                        "captions": [{"from": 1.0, "to": 1.5, "text": "Too many fast caption words here"}],
                        "texts": [{"role": "hook", "text": "Small hook", "from": 4.0, "to": 4.5, "px": 40}, {"role": "cta", "text": "Late CTA", "from": 4.0, "to": 5.5}],
                        "terms": ["UnmentionedTerm"],
                        "vo": [{"id": "l1", "status": "ESTIMATED", "words": [{"t": 2.0, "w": "b"}, {"t": 1.0, "w": "a"}]}],
                    },
                },
                {
                    "name": "waived_hook_and_term_warnings",
                    "tl": {
                        "meta": {"w": 1080, "h": 1080, "fps": 30, "dur": 4.0, "clock": "voice", "hookWaiver": "title card"},
                        "scenes": [{"id": "s1", "start": 0.0, "end": 4.0}],
                        "hero": {"t": 2.5},
                        "silences": [{"from": 1.5, "to": 2.2}],
                        "texts": [{"role": "hook", "text": "OnlyShown", "from": 3.5, "to": 4.0, "px": 90}],
                        "terms": ["OnlyShown", "OnlySaid"],
                        "vo": [{"id": "v1", "text": "OnlySaid here"}],
                    },
                },
                {
                    "name": "exact_boundaries_fps16",
                    "tl": {
                        "meta": {"w": 1920, "h": 1080, "fps": 16, "dur": 10.0, "clock": "reads"},
                        "scenes": [
                            {"id": "s1", "start": 0.0, "end": 5.0, "beats": {"b0": 0.0, "b_after": 5.0625}, "transitionOut": {"why": "seam"}},
                            {"id": "s2", "start": 5.0625, "end": 9.9375, "beats": {"b_before": 5.0, "b_end": 10.0}},
                        ],
                        "reads": [{"from": 0.0, "to": 0.6, "what": "exact06"}],
                        "cuts": [10.0],
                        "hero": {"t": 4.0},
                        "silences": [{"from": 0.0, "to": 0.4}],
                        "captions": [{"from": 0.0, "to": 0.7, "text": "Two words"}, {"from": 2.0, "to": 4.0, "text": "one two three four five six seven"}],
                        "texts": [
                            {"role": "hook", "text": "H", "from": 3.0, "to": 4.4375, "px": 84},
                            {"role": "cta", "text": "C", "from": 3.0, "to": 5.0, "px": 48},
                            {"role": "term", "text": "H", "from": 3.0, "to": 5.0, "px": 48},
                        ],
                        "terms": ["H"],
                        "vo": [{"id": "v1", "text": "H Two words"}],
                    },
                },
                {
                    "name": "exact_hero_silence_window",
                    "tl": {
                        "meta": {"w": 1080, "h": 1920, "fps": 16, "dur": 10.0, "clock": "voice"},
                        "scenes": [{"id": "s1", "start": 0.0, "end": 10.0}],
                        "hero": {"t": 5.0},
                        "silences": [{"from": 0.6, "to": 1.0}, {"from": 4.65, "to": 5.05}],
                        "texts": [{"role": "hook", "text": "Go", "from": 0.0, "to": 2.0, "px": 84}],
                        "terms": ["Go"],
                        "vo": [{"id": "v1", "text": "Go"}],
                    },
                },
                {
                    "name": "music_loop_ok_boundary",
                    "tl": {
                        "meta": {"w": 1080, "h": 1080, "fps": 30, "dur": 4.0019, "clock": "music", "bpm": 120, "meter": "4/4", "loop": True},
                        "scenes": [{"id": "s1", "start": 0.0, "end": 4.0}],
                        "hero": {"t": 2.0},
                        "silences": [{"from": 1.0, "to": 1.5}],
                        "texts": [{"role": "hook", "text": "M", "from": 0.0, "to": 2.0, "px": 84}],
                        "terms": ["M"],
                        "vo": [{"id": "v1", "text": "M"}],
                    },
                },
                {
                    "name": "music_loop_fail_boundary",
                    "tl": {
                        "meta": {"w": 1080, "h": 1080, "fps": 30, "dur": 4.0021, "clock": "music", "bpm": 120, "meter": "4/4", "loop": True},
                        "scenes": [{"id": "s1", "start": 0.0, "end": 4.0}],
                        "hero": {"t": 2.0},
                        "silences": [{"from": 1.0, "to": 1.5}],
                        "texts": [{"role": "hook", "text": "M", "from": 0.0, "to": 2.0, "px": 84}],
                        "terms": ["M"],
                        "vo": [{"id": "v1", "text": "M"}],
                    },
                },
            ],
            "compare_cuts_cases": [
                ([], [1.0, 2.0], 30.0),
                ([1.03, 2.0, 4.5], [1.0, 2.0, 8.0], 30.0),
                ([1.5, 2.501], [1.0, 2.0], 30.0),
                ([1.0], [], 30.0),
            ],
            "runs_cases": [[False, True, True, False, True], [True, True, True], []],
        },
        "m117": {
            "categories": [
                "01_Website_and_Funnels",
                "02_Video_and_Motion",
                "03_3D_and_Spatial",
                "04_2D_and_Games",
                "05_AI_Agents_and_Automation",
                "06_SaaS_and_MicroServices",
            ],
            "query_cases": [
                {"category": None, "keyword": None},
                {"category": "03_3D_and_Spatial", "keyword": None},
                {"category": None, "keyword": "Three.js"},
                {"category": None, "keyword": "$1 500"},
                {"category": "06_SaaS_and_MicroServices", "keyword": "Stripe"},
                {"category": "website-and-funnels", "keyword": None},
            ],
        },
        "m118": {
            "opp_ids": ["OPP-001", "OPP-002", "OPP-003", "OPP-004", "OPP-005"],
            "qualify_cases": [
                {"platform": "apinex.com", "verified_model_weights": True, "direct_openai_or_anthropic_api": True, "estimated_ttl_days": 60},
                {"platform": "scam-clickbait.example", "verified_model_weights": False, "clickbait_rebrand": True},
                {"platform": "sovereign-new.example", "requires_credit_card": False, "direct_openai_or_anthropic_api": True, "estimated_ttl_days": 45},
                {"platform": "web-trial.example", "requires_credit_card": False, "direct_openai_or_anthropic_api": False, "estimated_ttl_days": 3},
                {"platform": "stripe-loop.example", "requires_credit_card": True, "direct_openai_or_anthropic_api": False, "estimated_ttl_days": 14},
                {"platform": "ttl6.example", "requires_credit_card": False, "direct_openai_or_anthropic_api": True, "estimated_ttl_days": 6},
                {"platform": "ttl7.example", "requires_credit_card": False, "direct_openai_or_anthropic_api": True, "estimated_ttl_days": 7},
                {"platform": "ttl29.example", "requires_credit_card": False, "direct_openai_or_anthropic_api": False, "estimated_ttl_days": 29},
                {"platform": "ttl30.example", "requires_credit_card": False, "direct_openai_or_anthropic_api": False, "estimated_ttl_days": 30},
            ],
        },
    }


_ORACLE_RUNNER_CODE = r'''
import dataclasses
import datetime as dt
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from types import SimpleNamespace
import numpy as np
from PIL import Image, ImageDraw
import yaml

iso = Path.cwd()
inputs = json.loads((iso / "diff_inputs.json").read_text(encoding="utf-8"))

# ============================================================================
# M044: context-language-models upstream
# ============================================================================
clm_root = iso / "01_Forkable/FKB02_Memory/01_BillionContxtLanguage_AutoOnthology/context-language-models/clm"
sys.path.insert(0, str(clm_root))
from clm_harness.context_utils.context_string import (
    content_text as up_content_text,
    parse_back as up_parse_back,
    render_editable as up_render_editable,
    rendered_text as up_rendered_text,
)
from clm_harness.context_env.edit_gate import (
    fit_rule as up_fit_rule,
    may_grow as up_may_grow,
    reject_rule as up_reject_rule,
    rejected_note as up_rejected_note,
    resolve_allow_edit_growth as up_resolve_allow_edit_growth,
)
from clm_harness.utils.finish_policy import (
    FINISH_INSTRUCTIONS as UP_FINISH_INSTRUCTIONS,
    FinishPolicy as UpFinishPolicy,
    SUBMIT_MARKER as UP_SUBMIT_MARKER,
    is_submit_command as up_is_submit_command,
)
from clm_harness.utils.lm_compat import token_cap_key as up_token_cap_key

def _safe_call(fn, *args, **kwargs):
    try:
        return {"ok": True, "val": fn(*args, **kwargs)}
    except Exception as exc:
        return {"ok": False, "err": type(exc).__name__}

m044_editables = []
m044_parses_conv = []
for conv in inputs["m044"]["conversations"]:
    for p in (0, 1, 2, 10):
        ed = up_render_editable(conv, protect=p)
        m044_editables.append({"protect": p, "text": ed})
        m044_parses_conv.append({"protect": p, "parsed": up_parse_back(ed, conv[:p])})

protected_ref = inputs["m044"]["conversations"][0][:2]
m044_parse_back_edge = {
    lbl: up_parse_back(edited, protected_ref)
    for lbl, edited in inputs["m044"]["parse_back_cases"]
}
m044_resolve_gate = [
    _safe_call(up_resolve_allow_edit_growth, passed, env)
    for passed, env in inputs["m044"]["edit_gate_cases"]["resolve"]
]
m044_finish_modes = []
for md in inputs["m044"]["finish_policy_cases"]["modes"]:
    try:
        fp = UpFinishPolicy(md)
        m044_finish_modes.append({
            "ok": True,
            "mode": fp.mode,
            "open_ended": fp.open_ended,
            "fragment": fp.prompt_fragment(),
            "cmds": [fp.is_finish_command(c) for c in inputs["m044"]["finish_policy_cases"]["commands"]],
        })
    except Exception as exc:
        m044_finish_modes.append({"ok": False, "err": type(exc).__name__})

m044_out = {
    "content_texts": [up_content_text(c) for c in inputs["m044"]["content_cases"]],
    "rendered_texts": [up_rendered_text(m) for m in inputs["m044"]["render_msgs"]],
    "editables": m044_editables,
    "parses_conv": m044_parses_conv,
    "parse_back_edge": m044_parse_back_edge,
    "resolve_gate": m044_resolve_gate,
    "fit_rule": up_fit_rule(4096),
    "may_grow": [up_may_grow(allow_growth=ag, limit=lim, after=af) for ag, lim, af in inputs["m044"]["edit_gate_cases"]["may_grow"]],
    "reject_rule": [up_reject_rule(allow_growth=ag, limit=lim) for ag, lim in inputs["m044"]["edit_gate_cases"]["reject_rule"]],
    "rejected_note": up_rejected_note(baseline=1000, after=1200, before=900, rule=up_fit_rule(1000)),
    "finish_marker": UP_SUBMIT_MARKER,
    "finish_instructions": UP_FINISH_INSTRUCTIONS,
    "finish_modes": m044_finish_modes,
    "submit_commands": [up_is_submit_command(c) for c in inputs["m044"]["finish_policy_cases"]["commands"]],
    "token_cap_keys": [up_token_cap_key(m) for m in inputs["m044"]["lm_compat_models"]],
}

# ============================================================================
# M050: knowledge-catalog upstream
# ============================================================================
okf_root = iso / "01_Forkable/FKB02_Memory/knowledge-catalog/okf/src"
sys.path.insert(0, str(okf_root))
from reference_agent.bundle.document import (
    OKFDocument as UpOKFDocument,
    OKFDocumentError as UpOKFDocumentError,
    is_stale as up_is_stale,
    normalize_verified as up_normalize_verified,
    trust_tier as up_trust_tier,
)
from reference_agent.bundle.index import regenerate_indexes as up_regenerate_indexes
from reference_agent.bundle.paths import (
    concept_id_to_path as up_concept_id_to_path,
    parse_concept_id as up_parse_concept_id,
    path_to_concept_id as up_path_to_concept_id,
)
from reference_agent.bundle.synthesizer import (
    _fallback as up_synth_fallback,
    synthesize_description as up_synth_description,
)

stale_now = dt.datetime.fromisoformat(inputs["m050"]["stale_now_iso"])
doc_samples = list(inputs["m050"]["synthetic_docs"])
concepts_dir = iso / "00_Memoire" / "bundle" / "concepts"
if concepts_dir.exists():
    for md_p in sorted(concepts_dir.glob("*.md"))[:8]:
        doc_samples.append((f"concept:{md_p.name}", md_p.read_text(encoding="utf-8")))

m050_docs_res = []
for label, raw in doc_samples:
    try:
        d = UpOKFDocument.parse(raw)
        try:
            d.validate()
            val_ok = True
        except UpOKFDocumentError:
            val_ok = False
        m050_docs_res.append({
            "label": label,
            "ok": True,
            "validate_ok": val_ok,
            "frontmatter": d.frontmatter,
            "body": d.body,
            "serialized": d.serialize(),
        })
    except UpOKFDocumentError:
        m050_docs_res.append({"label": label, "ok": False, "err": "OKFDocumentError"})

m050_trust_res = [
    {
        "normalized": up_normalize_verified(fm),
        "tier": up_trust_tier(fm),
    }
    for fm in inputs["m050"]["trust_cases"]
]
m050_stale_fixed = [up_is_stale(fm, now=stale_now) for fm in inputs["m050"]["stale_cases"]]
m050_stale_default_now = [
    up_is_stale({"stale_after": "2020-01-01T00:00:00Z"}),
    up_is_stale({"stale_after": "2099-01-01T00:00:00Z"}),
]

# Multi-folder OKF index test + single-child no-synth check + empty dir skip + non-existent dir
b_multi = Path(tempfile.mkdtemp(dir=str(iso), prefix="ora_okf_m_"))
(b_multi / "datasets").mkdir()
(b_multi / "datasets" / "only.md").write_text("---\ntype: BigQuery Dataset\ntitle: Only Dataset\ndescription: Single child desc.\n---\nBody.\n", encoding="utf-8")
(b_multi / "single_no_desc").mkdir()
(b_multi / "single_no_desc" / "only_empty.md").write_text("---\ntype: BigQuery Dataset\ntitle: EmptyDesc\n---\nBody.\n", encoding="utf-8")
(b_multi / "tables").mkdir()
(b_multi / "tables" / "events_.md").write_text("---\ntype: BigQuery Table\ntitle: events_*\ndescription: Sharded events.\n---\nEvents.\n", encoding="utf-8")
(b_multi / "tables" / "users.md").write_text("---\ntype: BigQuery Table\ntitle: users\ndescription: Users table.\n---\nUsers.\n", encoding="utf-8")
(b_multi / "empty_dir").mkdir()
synth_calls = []
def _ora_synth(rel, pairs, *, model):
    synth_calls.append(rel)
    return up_synth_fallback(pairs)
gen_m = up_regenerate_indexes(b_multi, model="stub-test", synthesize=_ora_synth)
b_missing = iso / "does_not_exist_okf_dir"
gen_missing = up_regenerate_indexes(b_missing, model="stub-test", synthesize=_ora_synth)

b_root = Path("/tmp_okf_root")
path_cases = []
for raw_cid in inputs["m050"]["concept_id_cases"]:
    try:
        cid = up_parse_concept_id(raw_cid)
        p = up_concept_id_to_path(b_root, cid)
        back = up_path_to_concept_id(b_root, p)
        path_cases.append({"ok": True, "cid": list(cid), "rel": p.relative_to(b_root).as_posix(), "back": list(back)})
    except ValueError:
        path_cases.append({"ok": False, "err": "ValueError"})
path_cases.append(_safe_call(up_concept_id_to_path, b_root, ()))

m050_out = {
    "docs": m050_docs_res,
    "trust": m050_trust_res,
    "stale_fixed": m050_stale_fixed,
    "stale_default_now": m050_stale_default_now,
    "synth_fallback": [
        up_synth_description("", c, model="stub") if not c else up_synth_fallback(c)
        for c in inputs["m050"]["synth_fallback_cases"]
    ],
    "indexes_multi": {p.relative_to(b_multi).as_posix(): p.read_text(encoding="utf-8") for p in sorted(gen_m)},
    "synth_calls": synth_calls,
    "indexes_missing_len": len(gen_missing),
    "empty_dir_has_index": (b_multi / "empty_dir" / "index.md").exists(),
    "paths": path_cases,
}

# ============================================================================
# M056: CLI-Anything upstream
# ============================================================================
cli_plugin_dir = iso / "01_Forkable/FKB04_Tools_Anything/CLI-Anything/cli-anything-plugin"
sys.path.insert(0, str(cli_plugin_dir))
from preview_bundle import build_cache_key as up_build_cache_key
from skill_generator import (
    extract_cli_metadata as up_extract_cli_metadata,
    extract_commands_from_cli as up_extract_commands_from_cli,
    generate_skill_md as up_generate_skill_md,
    generate_skill_md_simple as up_generate_skill_md_simple,
)

# Synthetic harnesses covering export group, nested group, flat commands -> General, apt install, and ValueError
syn_root = iso / "syn_harnesses"
for name, cli_code, readme_txt in [
    (
        "syn_export",
        "import click\n@click.group()\ndef cli():\n    'Root CLI.'\n@cli.group()\ndef export():\n    'Export ops.'\n@export.command(name='pdf-out')\ndef render_pdf():\n    'Render PDF.'\n    pass\n",
        "# Syn Export\n\nExport workflow helper.\n\nInstall: `apt install syn-export`\n",
    ),
    (
        "syn_flat",
        "import click\n@click.command()\ndef ping():\n    'Ping target.'\n    pass\n@click.command()\ndef info():\n    'Info target.'\n    pass\n",
        "# Syn Flat\n\nFlat command harness.\n",
    ),
    (
        "syn_intro_100",
        "import click\n@click.command()\ndef ok():\n    'Ok.'\n    pass\n",
        "# Syn Intro 100\n\n" + ("A" * 100) + "\n",
    ),
    (
        "syn_intro_101",
        "import click\n@click.command()\ndef ok():\n    'Ok.'\n    pass\n",
        "# Syn Intro 101\n\n" + ("A" * 101) + "\n",
    ),
]:
    hp = syn_root / name / "agent-harness"
    pkg = hp / "cli_anything" / name
    pkg.mkdir(parents=True, exist_ok=True)
    (pkg / "__init__.py").write_text("", encoding="utf-8")
    (pkg / "README.md").write_text(readme_txt, encoding="utf-8")
    (hp / "setup.py").write_text('version="2.4.0"\n', encoding="utf-8")
    (pkg / f"{name}_cli.py").write_text(cli_code, encoding="utf-8")

tpl_path = cli_plugin_dir / "templates" / "SKILL.md.template"
m056_harnesses = {}
for label, h_dir in [
    ("zotero", iso / "01_Forkable/FKB04_Tools_Anything/CLI-Anything/zotero/agent-harness"),
    ("audacity", iso / "01_Forkable/FKB04_Tools_Anything/CLI-Anything/audacity/agent-harness"),
    ("syn_export", syn_root / "syn_export" / "agent-harness"),
    ("syn_flat", syn_root / "syn_flat" / "agent-harness"),
    ("syn_intro_100", syn_root / "syn_intro_100" / "agent-harness"),
    ("syn_intro_101", syn_root / "syn_intro_101" / "agent-harness"),
]:
    meta = up_extract_cli_metadata(str(h_dir))
    cli_files = list((h_dir / "cli_anything").glob("*/*_cli.py"))
    raw_cmds = [dataclasses.asdict(g) for g in up_extract_commands_from_cli(cli_files[0])] if cli_files else []
    m056_harnesses[label] = {
        "meta": dataclasses.asdict(meta),
        "raw_cmds": raw_cmds,
        "skill_md": up_generate_skill_md(meta, template_path=str(tpl_path)),
        "skill_md_simple": up_generate_skill_md_simple(meta),
    }

m056_invalid_res = _safe_call(up_extract_cli_metadata, str(iso / "does_not_exist_harness"))
m056_cache_keys = [
    up_build_cache_key(
        ck["software"], ck["recipe"], ck["bundle_kind"], ck["source_fingerprint"],
        options=ck["options"], harness_version=ck["harness_version"],
    )
    for ck in inputs["m056"]["cache_key_cases"]
]
m056_out = {"harnesses": m056_harnesses, "invalid": m056_invalid_res, "cache_keys": m056_cache_keys}

# ============================================================================
# M084: video-director upstream (check_timeline.py + qa_video.py)
# ============================================================================
vd_scripts = iso / "01_Forkable/FKB07_Money_Maker/02_Video/video-director/video-director/scripts"
sys.path.insert(0, str(vd_scripts))
import check_timeline as up_ct
import qa_video as up_qv

m084_timelines = []
tmp_vd = Path(tempfile.mkdtemp(dir=str(iso), prefix="ora_vd_"))
for item in inputs["m084"]["timelines"]:
    tl_file = tmp_vd / f"{item['name']}.json"
    tl_file.write_text(json.dumps(item["tl"]), encoding="utf-8")
    proc = subprocess.run([sys.executable, str(vd_scripts / "check_timeline.py"), str(tl_file)], capture_output=True, text=True, encoding="utf-8")
    m084_timelines.append({
        "name": item["name"],
        "returncode": proc.returncode,
        "stdout": proc.stdout.replace("\r\n", "\n"),
        "beat_times": up_qv.beat_times(item["tl"]),
        "loaded_tl": up_qv.load_timeline(tl_file),
    })

list_tl_file = tmp_vd / "list_tl.json"
list_tl_file.write_text(json.dumps([0.5, 2.0, 1.0, 2.0]), encoding="utf-8")
list_tl_loaded = up_qv.load_timeline(list_tl_file)

# Synthetic numpy frame stats covering flashes, cuts, pops, frozen, flat, loop
rng = np.zeros(45, dtype=np.float64)
d_arr = np.full(45, 0.8, dtype=np.float64)
d_arr[0] = 0.0
d_arr[5] = 8.0
d_arr[6] = 8.2   # flash at index 5
d_arr[12] = 15.0 # cut at index 12
d_arr[18] = 3.5  # pop at index 18
d_arr[25:42] = 0.05  # frozen stretch
std_arr = np.full(45, 18.0, dtype=np.float64)
std_arr[20:23] = 2.5  # flat frames
skip_arr = np.full(45, 0.9, dtype=np.float64)
skip_arr[0] = np.nan
skip_arr[-1] = np.nan
skip_arr[5] = 0.5  # < 0.35 * 8.0 -> flash confirmed
mean_arr = np.full(45, 120.0, dtype=np.float64)
st_dict = {"n": 45, "mean": mean_arr, "std": std_arr, "d": d_arr, "skip": skip_arr, "seam": 0.4}
args_ns = SimpleNamespace(freeze=0.5, freeze_eps=0.25, loop=True)

d_b = np.full(50, 0.8, dtype=np.float64)
d_b[0] = 0.0
d_b[3] = 6.0
d_b[6] = 0.1
d_b[7] = 2.0
d_b[8] = 0.1
d_b[10:24] = 0.2   # run (10, 24) -> (24-10+1)/30 = 0.5 == freeze -> FROZEN
d_b[25] = 0.2
d_b[26] = 0.25     # == freeze_eps -> NON still
d_b[27] = 0.2
d_b[30:43] = 0.2   # run (30, 43) -> (43-30+1)/30 = 14/30 < 0.5 -> NON FROZEN
std_b = np.full(50, 6.0, dtype=np.float64)  # == 6.0 -> NON flat
skip_b = np.full(50, 0.9, dtype=np.float64)
skip_b[0] = np.nan
skip_b[-1] = np.nan
mean_b = np.full(50, 100.0, dtype=np.float64)
st_boundary = {"n": 50, "mean": mean_b, "std": std_b, "d": d_b, "skip": skip_b, "seam": 0.5}

im_contrast = Image.new("RGB", (200, 100), (0, 0, 0))
draw = ImageDraw.Draw(im_contrast)
draw.rectangle([20, 20, 120, 70], fill=(255, 255, 255))
im_flat = Image.new("RGB", (100, 100), (128, 128, 128))
im_half = Image.new("RGB", (100, 100), (0, 0, 0))
ImageDraw.Draw(im_half).rectangle([0, 0, 49, 99], fill=(255, 255, 255))

m084_out = {
    "is_num": [up_ct.is_num(x) for x in inputs["m084"]["is_num_cases"]],
    "norm": [up_ct.norm(x) for x in inputs["m084"]["norm_cases"]],
    "read_time": [up_ct.read_time(x) for x in inputs["m084"]["read_time_cases"]],
    "timelines": m084_timelines,
    "list_tl_loaded": list_tl_loaded,
    "runs": [[list(p) for p in up_qv.runs(r)] for r in inputs["m084"]["runs_cases"]],
    "analyse_picture": [
        up_qv.analyse_picture(st_dict, 30.0, args_ns),
        up_qv.analyse_picture(st_boundary, 30.0, args_ns),
    ],
    "compare_cuts": [up_qv.compare_cuts(det, exp, fps) for det, exp, fps in inputs["m084"]["compare_cuts_cases"]],
    "measure_text": [
        up_qv.measure_text(im_contrast, [10, 10, 140, 80], 1080),
        up_qv.measure_text(im_contrast, [9.6, 10.4, 140.4, 79.5], 1080),
        up_qv.measure_text(im_flat, [10, 10, 60, 60], 1080),
        up_qv.measure_text(im_half, [0, 0, 100, 100], 1080),
    ],
}

# ============================================================================
# M117: 00_Marketplace_YoutubeSkills raw filesystem oracle
# ============================================================================
m117_dir = iso / "01_Forkable/FKB07_Money_Maker/00_Marketplace_YoutubeSkills"
readme_txt = (m117_dir / "README.md").read_text(encoding="utf-8")
m117_cats = []
for ln in readme_txt.splitlines():
    cm = re.match(r"^\|\s*\*\*\d+\.\s*[^*]+\*\*\s*\|\s*\[`([^`]+)`\][^|]+\|\s*(\d+)\s+vidéos\s*\|\s*(.+?)\s*\|$", ln.strip())
    if cm:
        m117_cats.append({"id": cm.group(1).strip(), "videos": int(cm.group(2)), "offers": cm.group(3).strip()})
m117_vids = []
for ln in readme_txt.splitlines():
    vm = re.match(r"^\d+\.\s+`([A-Za-z0-9_-]{11})`.*?Catégorie\s+(\d+)\s*:\s*(.+)$", ln.strip())
    if vm:
        cat_id = next(c["id"] for c in m117_cats if c["id"].startswith(vm.group(2).zfill(2) + "_"))
        m117_vids.append({"video_id": vm.group(1), "category": cat_id, "topic": vm.group(3).strip()})

m117_pbs = {}
for cat_id in inputs["m117"]["categories"]:
    stxt = (m117_dir / cat_id / "SKILL.md").read_text(encoding="utf-8")
    fm = yaml.safe_load(re.search(r"^---\s*\n(.*?)\n---", stxt, flags=re.S).group(1))
    title_m = re.search(r"^# Skill\s*:\s*(.+)$", stxt, flags=re.M)
    offers_sec = stxt.split("## 1. Offres Productisées Associées")[1].split("## 2.")[0]
    offers = [
        {"offer": om.group(1).strip(), "spec": om.group(2).strip(), "pricing": om.group(3).strip()}
        for om in re.finditer(r"^\d+\.\s+\*\*(.+?)\*\*\s*:\s*(.+?)\s+\(([^()]*\$[^()]*)\)\.?$", offers_sec, flags=re.M)
    ]
    vids = re.findall(r"https://youtu\.be/([A-Za-z0-9_-]{11})", stxt)
    proto_sec = stxt.split("## 3.")[1]
    proto = []
    for ln in proto_sec.splitlines():
        pm = re.match(r"^\d+\.\s+\*\*([^*]+)\*\*\s*:\s*(.+)$", ln.strip())
        if pm:
            proto.append(f"{pm.group(1).strip()} : {pm.group(2).strip().replace('`', '').replace('**', '')}")
    m117_pbs[cat_id] = {
        "skill_name": fm["name"],
        "title": title_m.group(1).strip(),
        "description": fm["description"],
        "productized_offers": offers,
        "foundational_videos": vids,
        "execution_protocol": proto,
    }
m117_out = {"categories": m117_cats, "videos": m117_vids, "playbooks": m117_pbs}

# ============================================================================
# M118: 04_Inference_Youtube_Discovery_Registry raw filesystem oracle
# ============================================================================
m118_dir = iso / "01_Forkable/FKB01_Inference/04_Inference_Youtube_Discovery_Registry"
raw_reg = json.loads((m118_dir / "registry.json").read_text(encoding="utf-8"))
watch_txt = (m118_dir / "SKILL_WATCH.md").read_text(encoding="utf-8")
assert "FILTRE 1" in watch_txt and "FILTRE 5" in watch_txt and "Score A" in watch_txt and "Voie B" in watch_txt

m118_dossiers = {}
for fp in sorted((m118_dir / "opportunities").glob("OPP-*.md")):
    otxt = fp.read_text(encoding="utf-8")
    oid = fp.name.split("_", 1)[0]
    hm = re.search(r"^#\s+OPP-\d+\s*:\s*(.+)$", otxt, flags=re.M)
    tbl = {rm.group(1).strip(): rm.group(2).strip() for rm in re.finditer(r"^\|\s*\*\*([^*]+)\*\*\s*\|\s*(.+?)\s*\|$", otxt, flags=re.M)}
    steps_sec = otxt.split("## 1.")[1].split("## 2.")[0]
    steps = [
        sm.group(1).strip().replace("`", "").replace("**", "").replace("*", "").replace(r"$\rightarrow$", "->")
        for sm in re.finditer(r"^\d+\.\s+(.+)$", steps_sec, flags=re.M)
    ]
    _cl = lambda v: v.replace("`", "").replace("**", "").strip()
    m118_dossiers[oid] = {
        "id": oid,
        "title": hm.group(1).strip(),
        "source_youtube": tbl["Source YouTube"].strip().strip("*").strip('"').strip(),
        "target_platform": _cl(tbl["Plateforme Cible"]),
        "model_offered": _cl(tbl.get("Modèles Offerts") or tbl["Modèle Offert"]),
        "compute_volume": _cl(tbl["Volume de Calcul"]),
        "watch_skill_status": _cl(tbl["Statut Watch Skill"]),
        "injection_vector": _cl(tbl["Vecteur d'Injection"]),
        "mechanism_steps": steps,
    }
m118_out = {"registry": raw_reg, "dossiers": m118_dossiers}


# ============================================================================
# M074: tradingview-indicator-search-mcp-server upstream (Node ESM + node:sqlite)
# ============================================================================
node_exe = shutil.which("node")
assert node_exe is not None, "node (>=22.5) requis pour l'oracle amont M074"
m74_dir = iso / "01_Forkable/FKB07_Money_Maker/01_Trading/tradingview-indicator-search-mcp-server"
m74_fix_dir = m74_dir / "test" / "fixtures"
m74_mjs_path = iso / "m074_oracle.mjs"
m74_out_path = iso / "m074_oracle_out.json"

m74_mjs_code = r"""
import fs from 'node:fs';
import path from 'node:path';
import { pathToFileURL } from 'node:url';

const m74Root = path.resolve(process.argv[2]);
const fixDir = path.resolve(process.argv[3]);
const outFile = path.resolve(process.argv[4]);

const { config: baseConfig } = await import(pathToFileURL(path.join(m74Root, 'src/config.js')).href);
const parseMod = await import(pathToFileURL(path.join(m74Root, 'src/parse.js')).href);
const { Store, utcDay } = await import(pathToFileURL(path.join(m74Root, 'src/db.js')).href);
const { Throttle } = await import(pathToFileURL(path.join(m74Root, 'src/throttle.js')).href);
const { HttpError } = await import(pathToFileURL(path.join(m74Root, 'src/http.js')).href);
const { TradingView, normalizeScriptType } = await import(pathToFileURL(path.join(m74Root, 'src/tradingview.js')).href);
const { createTools } = await import(pathToFileURL(path.join(m74Root, 'src/tools.js')).href);

const loadFix = (f) => JSON.parse(fs.readFileSync(path.join(fixDir, f), 'utf8'));
const safeCall = (fn) => {
  try {
    return { ok: true, val: fn() };
  } catch (err) {
    return { ok: false, name: err?.name ?? 'Error', msg: String(err?.message ?? err) };
  }
};
const safeAsync = async (fn) => {
  try {
    return { ok: true, val: await fn() };
  } catch (err) {
    return { ok: false, name: err?.name ?? 'Error', msg: String(err?.message ?? err) };
  }
};

const genFix = loadFix('slug-feed-general.json');
const edFix = loadFix('slug-feed-editors.json');
const scalpFix = loadFix('slug-feed-scalping.json');
const authFix = loadFix('author-feed.json');
const facOpen = loadFix('facade-open.json');
const facProt = loadFix('facade-protected.json');

const slugGen = parseMod.parseSlugFeed(genFix);
const slugEd = parseMod.parseSlugFeed(edFix);
const slugScalp = parseMod.parseSlugFeed(scalpFix);
const authParsed = parseMod.parseAuthorFeed(authFix);
const longItem = {
  script_id_part: 'PUB;a',
  name: 'Long Winded Indicator',
  description: 'word '.repeat(2000),
};

const parsersOut = {
  slugify: ['trend following', '  Order   Blocks  ', "Elliott's Wave", 'Elliott\u2019s Wave', 'RSI/MACD combo', '   ', '!!!', null, ''].map(parseMod.slugify),
  script_types: ['indicator', 'indicators', 'STRATEGY', 'libraries', 'all', 'nonsense', '', null].map(normalizeScriptType),
  pine_versions: ['//@version=5\nstudy("x")', '// @version = 6\n', 'no pragma here', null].map(parseMod.detectPineVersion),
  chart_ids: [
    'https://www.tradingview.com/script/K0SEi3Ct-TL-PbD/',
    'https://www.tradingview.com/script/abc123/',
    'nonsense',
    null,
  ].map(parseMod.extractIdFromChartUrl),
  snippets: [
    parseMod.snippet('a\n\n  b   c', 100),
    parseMod.snippet('x'.repeat(500), 10),
    parseMod.snippet('hello   ', 10),
    parseMod.snippet('', 10),
    parseMod.snippet('1234567890', 10),
    parseMod.snippet('12345678901', 10),
    parseMod.snippet('ab\uD83D\uDE00', 4),
    parseMod.snippet('ab\uD83D\uDE00c', 4),
  ],
  listings: [
    parseMod.toListing(slugGen.items[0], 300),
    parseMod.toListing(longItem, 300),
  ],
  slug_general: slugGen,
  slug_editors: slugEd,
  slug_scalping: slugScalp,
  slug_invalid: safeCall(() => parseMod.parseSlugFeed({ data: {} })).ok,
  author_feed: authParsed,
  author_invalid: safeCall(() => parseMod.parseAuthorFeed({ count: 3 })).ok,
  facade_cases: [
    parseMod.parseFacade(facOpen, { scriptIdPart: 'PUB;abc' }),
    parseMod.parseFacade(facProt, { scriptIdPart: 'PUB;xyz' }),
    parseMod.parseFacade(null),
    parseMod.parseFacade({}),
    parseMod.parseFacade({ source: 123 }),
    parseMod.parseFacade({ source: '//@version=4\nstrategy("s")', extra: { kind: 'strategy', is_price_study: false }, lastVersionMaj: '3' }, { scriptIdPart: 'PUB;s1' }),
  ],
  utc_days: [utcDay(1784973600000), utcDay(1785060000000), utcDay(0)],
};

const store = new Store(':memory:');
const tBase = 1784973600000;
const upsertCount = store.upsertScripts([
  { script_id_part: 'PUB;a', name: 'Supertrend Pro', author: 'alice', script_type: 'strategy', likes: 100, open_source: true, script_access: 1, description: 'A trend following strategy' },
  { script_id_part: 'PUB;b', name: 'RSI Basic', author: 'bob', script_type: 'indicator', likes: 10, open_source: true, script_access: 1, description: 'A mean reversion oscillator' },
], tBase);
store.upsertScript({ script_id_part: 'PUB;a', name: 'Supertrend Pro', author: 'alice', script_type: 'strategy', likes: 120, open_source: true, script_access: 1, description: 'A trend following strategy' }, tBase + 1);
store.putSource({ script_id_part: 'PUB;a', version: '1', source: '//@version=5\nstrategy("x")\nta.supertrend(3, 10)', pine_version: 5, kind: 'strategy', script_name: 'Supertrend Pro' }, tBase + 2);
store.markProtected('PUB;closed', tBase + 3);
const day1 = 1784973600000;
const day2 = 1785060000000;
store.logRequest({ host: 'h', path: '/a', status: 200, ms: 5, outcome: 'ok' }, day1);
store.logRequest({ host: 'h', path: '/b', status: 200, ms: 5, outcome: 'ok' }, day1);
store.logRequest({ host: 'h', path: '/c', status: 200, ms: 5, outcome: 'ok' }, day2);
store.putCachedSearch('k', 'search', { q: 'supertrend' }, { total: 1, items: [] }, 1_000_000);
store.putCookieJar('h', 'a=1; b=2', 1000);

const storeOut = {
  upsert_count: upsertCount,
  has_source_a: store.hasSource('PUB;a'),
  has_source_b: store.hasSource('PUB;b'),
  source_a_latest: store.getSource('PUB;a')?.source ?? null,
  source_a_v1: store.getSource('PUB;a', '1')?.source ?? null,
  source_missing: store.getSource('PUB;missing'),
  closed_open_source: store.getScript('PUB;closed')?.open_source ?? null,
  closed_access: store.getScript('PUB;closed')?.script_access ?? null,
  req_day1: store.countRequestsToday(day1),
  req_day2: store.countRequestsToday(day2),
  cache_hit: store.getCachedSearch('k', 5000, 1_001_000) !== null,
  cache_eq_ttl: store.getCachedSearch('k', 5000, 1_005_000) !== null,
  cache_gt_ttl_by_1: store.getCachedSearch('k', 5000, 1_005_001) === null,
  cache_miss: store.getCachedSearch('k', 5000, 1_009_000) === null,
  cookie_hit: store.getCookieJar('h', 5000, 2000),
  cookie_eq_age: store.getCookieJar('h', 5000, 6000),
  cookie_gt_age_by_1: store.getCookieJar('h', 5000, 6001),
  cookie_miss: store.getCookieJar('h', 500, 2000),
  q_fts_name: store.queryCorpus({ query: 'supertrend' }).map((r) => r.script_id_part),
  q_fts_desc: store.queryCorpus({ query: 'reversion' }).map((r) => r.script_id_part),
  q_source_contains: store.queryCorpus({ sourceContains: 'ta.supertrend' }).map((r) => r.script_id_part),
  q_type: store.queryCorpus({ scriptType: 'strategy' }).map((r) => r.script_id_part),
  q_author: store.queryCorpus({ author: 'ALICE' }).map((r) => r.script_id_part),
  q_likes: store.queryCorpus({ minLikes: 50 }).map((r) => r.script_id_part),
  q_likes_eq_10: store.queryCorpus({ minLikes: 10 }).map((r) => r.script_id_part),
  q_likes_gt_10: store.queryCorpus({ minLikes: 11 }).map((r) => r.script_id_part),
  q_likes_eq_120: store.queryCorpus({ minLikes: 120 }).map((r) => r.script_id_part),
  q_likes_gt_120: store.queryCorpus({ minLikes: 121 }).map((r) => r.script_id_part),
  q_likes_zero: store.queryCorpus({ minLikes: 0 }).map((r) => r.script_id_part),
  q_with_source: store.queryCorpus({ withSourceOnly: true }).map((r) => r.script_id_part),
  q_sorted_likes: store.queryCorpus({}).map((r) => r.likes),
};
store.close();

function makeThrottleHarness(overrides = {}, deps = {}) {
  let now = 0;
  const slept = [];
  const cfg = {
    minDelayMs: 1000, maxDelayMs: 3000, breakEvery: 3,
    breakMinMs: 20000, breakMaxMs: 30000, dailyBudget: 100,
    breakerThreshold: 3, breakerCooldownMs: 900000, ...overrides,
  };
  const thr = new Throttle(cfg, {
    now: () => now,
    sleep: async (ms) => { slept.push(ms); now += ms; },
    random: () => 0.5,
    ...deps,
  });
  return { thr, slept, advance: (ms) => { now += ms; } };
}

const h1 = makeThrottleHarness();
await h1.thr.run(async () => 'ok1');
await h1.thr.run(async () => 'ok2');
h1.advance(10_000);
await h1.thr.run(async () => 'ok3');
await h1.thr.run(async () => 'ok4');
const errRun = await safeAsync(() => h1.thr.run(async () => { throw new Error('boom'); }));
const afterErr = await h1.thr.run(async () => 'still works');

const h2 = makeThrottleHarness({ breakerThreshold: 3 });
const blocks1 = [h2.thr.noteBlocked(), h2.thr.noteBlocked(), h2.thr.noteBlocked()];
const tripErr = await safeAsync(() => h2.thr.run(async () => 'nope'));
h2.advance(839_999);
const tripMsg60001 = (await safeAsync(() => h2.thr.run(async () => 'nope'))).msg;
h2.advance(1);
const tripMsg60000 = (await safeAsync(() => h2.thr.run(async () => 'nope'))).msg;
h2.advance(59_999);
const tripStillOpen899999 = (await safeAsync(() => h2.thr.run(async () => 'nope'))).ok;
h2.advance(1);
const reopenedOk = await h2.thr.run(async () => 'reopened');
h2.thr.noteBlocked();
h2.thr.noteOk();
const streakReset = h2.thr.noteBlocked();

const h3 = makeThrottleHarness({ dailyBudget: 5 }, { countToday: () => 5 });
const budgetDenied = await safeAsync(() => h3.thr.run(async () => 'x'));
const h4 = makeThrottleHarness({ dailyBudget: 5 }, { countToday: () => 4 });
const budgetAllowed = await safeAsync(() => h4.thr.run(async () => 'x'));

const jitterBoundaries = [];
for (const [mn, mx, rv] of [[1000, 1001, 0.5], [1000, 1001, 0.75], [1000, 1001, 0.49], [1000, 1000, 0.9]]) {
  const hj = makeThrottleHarness({ minDelayMs: mn, maxDelayMs: mx, breakEvery: 0 }, { random: () => rv });
  await hj.thr.run(async () => 1);
  await hj.thr.run(async () => 2);
  jitterBoundaries.push(hj.slept[0]);
}
const hw = makeThrottleHarness({ minDelayMs: 1000, maxDelayMs: 1000, breakEvery: 0 });
await hw.thr.run(async () => 1);
hw.advance(1000);
await hw.thr.run(async () => 2);
const waitTurnAtExactGap = [...hw.slept];
hw.advance(999);
await hw.thr.run(async () => 3);
const waitTurnBelowGap = [...hw.slept];

const throttleOut = {
  slept: h1.slept,
  err_msg: errRun.msg,
  after_err: afterErr,
  status1: h1.thr.status(),
  blocks1,
  trip_is_open: tripErr.ok === false && tripErr.msg.includes('circuit is OPEN'),
  trip_msg_60001: tripMsg60001,
  trip_msg_60000: tripMsg60000,
  trip_still_open_899999: tripStillOpen899999,
  reopened_ok: reopenedOk,
  streak_reset: streakReset,
  budget_denied: budgetDenied.ok === false && budgetDenied.msg.includes('Daily request budget of 5'),
  budget_allowed: budgetAllowed.val,
  jitter_boundaries: jitterBoundaries,
  wait_turn_at_exact_gap: waitTurnAtExactGap,
  wait_turn_below_gap: waitTurnBelowGap,
};

function fakeHttp(routes) {
  const calls = [];
  return {
    calls,
    async warmUp() {},
    async getJson(url) {
      calls.push(url);
      for (const [pat, val] of routes) {
        if (url.includes(pat)) {
          if (val instanceof Error) throw val;
          return typeof val === 'function' ? val(url) : structuredClone(val);
        }
      }
      throw new Error(`No route for ${url}`);
    },
    async getText(url) {
      calls.push(url);
      return '<html>PUB;5bbd9e495f604c3682671a0e8920a188 and USER;747343354ba641a1973907f549b1cd10</html>';
    },
  };
}

const cfg = { ...baseConfig, dbPath: ':memory:', snippetChars: 120, harvestMaxScripts: 200 };
function buildCtx(routes) {
  const st = new Store(':memory:');
  const th = new Throttle(cfg, { sleep: async () => {}, countToday: () => 0 });
  const ht = fakeHttp(routes);
  const tv = new TradingView({ config: cfg, http: ht, store: st });
  const tl = createTools({ config: cfg, tv, store: st, throttle: th, http: ht });
  return { st, th, ht, tv, tl };
}

const ctx1 = buildCtx([
  ['/api/v1/scripts/', authFix],
  ['editors-picks', edFix],
  ['/scripts/', (url) => (url.includes('trend-following') && url.includes('page-3')) ? genFix : scalpFix],
  ['pine-facade', (url) => url.includes('ba544ec71a3945549669f3babb981424') ? facProt : facOpen],
]);
const s1 = await ctx1.tl.search_scripts({ query: 'trend following', script_type: 'strategy', sort: 'latest_popular' });
const s2 = await ctx1.tl.search_scripts({ query: 'trend following', script_type: 'strategy', sort: 'latest_popular' });
const sTop = await ctx1.tl.search_scripts({ query: 'trend following', script_type: 'strategies', page: 3 });
const sEd = await ctx1.tl.list_editors_picks({ script_type: 'indicator' });
const sAuth = await ctx1.tl.list_author_scripts({ username: 'TraderlifestyleYT' });
const srcChart = await ctx1.tl.get_script_source({ chart_url: 'https://www.tradingview.com/script/K0SEi3Ct-TL-PbD-Shape-Pro/' });
const srcCache = await ctx1.tl.get_script_source({ script_id_part: 'PUB;5bbd9e495f604c3682671a0e8920a188' });
const srcProt = await ctx1.tl.get_script_source({ script_id_part: 'PUB;ba544ec71a3945549669f3babb981424' });
const srcProtAgain = await ctx1.tl.get_script_source({ script_id_part: 'PUB;ba544ec71a3945549669f3babb981424' });
const qWide = ctx1.tl.query_corpus({ query: 'Scalping', limit: 50 });
const qDeep = ctx1.tl.query_corpus({ limit: 50, include_source: true });
const stStatus = ctx1.tl.fetch_status();

const scalpProt = loadFix('slug-feed-scalping.json');
scalpProt.data.ideas.data.items[0].script_access = 2;
scalpProt.data.ideas.data.items[1].script_access = 3;
const ctxProt = buildCtx([['/scripts/', scalpProt]]);
const tvProtRes = await ctxProt.tv.searchScripts({ query: 'scalping' });

const ctxErr = buildCtx([
  ['/api/v1/scripts/', new HttpError(400, 'u', '')],
  ['/scripts/', new HttpError(404, 'u', '')],
]);
const err404Slug = await safeAsync(() => ctxErr.tv.searchScripts({ query: 'not a real topic' }));
const err400User = await safeAsync(() => ctxErr.tv.authorScripts({ username: 'baduser' }));
const errBadType = await safeAsync(() => ctxErr.tv.searchScripts({ query: 'x', scriptType: 'nonsense' }));
const errBadId = await safeAsync(() => ctxErr.tv.getSource({ scriptIdPart: 'K0SEi3Ct' }));
const errEmptyGetSrc = await safeAsync(() => ctxErr.tl.get_script_source({}));

const ctxH = buildCtx([
  ['/scripts/', (url) => url.includes('page-') ? { data: { ideas: { data: { total: 0, items: [], next: null } } }, meta: { heading: 'none' } } : scalpFix],
  ['pine-facade', facOpen],
]);
const hRes = await ctxH.tl.harvest_scripts({ query: 'scalping', max_scripts: 5 });
const hAgain = await ctxH.tl.harvest_scripts({ harvest_id: hRes.harvest_id });
const hUnknown = await safeAsync(() => ctxH.tl.harvest_scripts({ harvest_id: 'nope' }));
const hNoAuthor = await safeAsync(() => ctxH.tl.harvest_scripts({ source: 'author' }));

const normHarvest = (obj) => {
  const c = structuredClone(obj);
  if (typeof c.harvest_id === 'string') c.harvest_id = '<HARVEST_ID>';
  return c;
};

const fix999 = structuredClone(scalpFix);
fix999.data.ideas.data.total = 999;
const fix1000 = structuredClone(scalpFix);
fix1000.data.ideas.data.total = 1000;
const ctxBound = buildCtx([
  ['/api/v1/scripts/', authFix],
  ['/scripts/topic-999/', fix999],
  ['/scripts/topic-1000/', fix1000],
]);
await ctxBound.tv.authorScripts({ username: 'U', query: 'q0', perPage: 0 });
await ctxBound.tv.authorScripts({ username: 'U', query: 'q1', perPage: 1 });
await ctxBound.tv.authorScripts({ username: 'U', query: 'q24', perPage: 24 });
await ctxBound.tv.authorScripts({ username: 'U', query: 'q25', perPage: 25 });
const s999 = await ctxBound.tl.search_scripts({ query: 'topic 999' });
const s1000 = await ctxBound.tl.search_scripts({ query: 'topic 1000' });
const qLimits = [
  ctx1.tl.query_corpus({ limit: 3, include_source: true }).limit_applied,
  ctx1.tl.query_corpus({ limit: 4, include_source: true }).limit_applied,
  ctx1.tl.query_corpus({ limit: 100, include_source: false }).limit_applied,
  ctx1.tl.query_corpus({ limit: 101, include_source: false }).limit_applied,
];

const toolsOut = {
  calls_ctx1: ctx1.ht.calls,
  s1, s2, sTop, sEd, sAuth,
  srcChart, srcCache, srcProt, srcProtAgain,
  qWide, qDeep,
  stStatus_keys_and_corpus: { corpus: stStatus.corpus, pacing: stStatus.pacing, throttle_budget: stStatus.throttle.daily_budget },
  filtered_protected_count: tvProtRes.filtered_protected,
  filtered_all_open: tvProtRes.items.every((i) => i.open_source),
  errors: {
    slug404: err404Slug.msg.includes('hyphenated'),
    user400: err400User.msg.includes('rejected the username'),
    badType: errBadType.msg.includes('Unknown script_type'),
    badId: errBadId.msg.includes('not a script_id_part'),
    emptySrc: errEmptyGetSrc.msg.includes('script_id_part or chart_url'),
    hUnknown: hUnknown.msg.includes('Unknown harvest_id'),
    hNoAuthor: hNoAuthor.msg.includes('requires a username'),
  },
  harvest_len_ok: typeof hRes.harvest_id === 'string' && hRes.harvest_id.length === 8,
  hRes: normHarvest(hRes),
  hAgain: normHarvest(hAgain),
  bound_calls: ctxBound.ht.calls,
  bound_notes: [s999.note ?? null, s1000.note ?? null],
  bound_q_limits: qLimits,
};

fs.writeFileSync(outFile, JSON.stringify({ parsersOut, storeOut, throttleOut, toolsOut }, null, 2), 'utf8');
"""
m74_mjs_path.write_text(m74_mjs_code, encoding="utf-8")
subprocess.check_call([node_exe, str(m74_mjs_path), str(m74_dir), str(m74_fix_dir), str(m74_out_path)], cwd=str(iso))
m074_out = json.loads(m74_out_path.read_text(encoding="utf-8"))
m74_mjs_path.unlink()
m74_out_path.unlink()

# ============================================================================
# M001: a0-plugins upstream (scripts/* + aspace-a0-plugins-adapter)
# ============================================================================
import base64
import io
import struct
import urllib.error
import urllib.parse
import urllib.request
import zlib
from contextlib import redirect_stdout
from unittest.mock import patch

m001_root = iso / "01_Forkable/FKB00_Runtime/00_A0_Core/a0-plugins"
m001_scripts = m001_root / "scripts"
m001_adapter_parent = m001_root / "aspace-a0-plugins-adapter"
sys.path.insert(0, str(m001_scripts))
sys.path.insert(0, str(m001_adapter_parent))

import aspace_a0_plugins_adapter as up_a0_adp
import download_index_release as up_dl
import find_orphan_plugin_names as up_orph
import plugin_resolution as up_pres
import publish_index_release as up_pub
import sync_plugin_state as up_sync
import update_index_stars as up_stars
import validate_plugin_submission as up_vps


def _make_exact_png(w: int, h: int, exact_bytes: int) -> bytes:
    buf = io.BytesIO()
    Image.new("RGB", (w, h), (10, 20, 30)).save(buf, format="PNG")
    raw = buf.getvalue()
    if exact_bytes <= len(raw):
        return raw
    pad_len = exact_bytes - len(raw) - 16
    assert pad_len >= 0
    payload = b"pad\x00" + (b"A" * pad_len)
    chunk = struct.pack(">I", len(payload)) + b"tEXt" + payload + struct.pack(">I", zlib.crc32(b"tEXt" + payload) & 0xFFFFFFFF)
    out = raw[:-12] + chunk + raw[-12:]
    assert len(out) == exact_bytes
    return out


class _MockHttpResp:
    def __init__(self, body: bytes = b"", headers: dict | None = None) -> None:
        self._bio = io.BytesIO(body)
        self.headers = headers or {}

    def read(self, n: int = -1) -> bytes:
        return self._bio.read(n)

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False


def _m001_mock_urlopen(req, timeout=30):
    u = urllib.parse.urlparse(req.full_url)
    method = req.get_method()
    if u.hostname == "api.github.com":
        if u.path == "/repos/org/alpha":
            return _MockHttpResp(json.dumps({"full_name": "org/alpha"}).encode("utf-8"))
        if u.path == "/repos/org/alpha/contents/plugin.yaml":
            b64 = base64.b64encode(b"name: alpha\nversion: 1.0.0\n").decode("ascii")
            return _MockHttpResp(json.dumps({"type": "file", "encoding": "base64", "content": b64}).encode("utf-8"))
        if u.path == "/repos/org/wrongname":
            return _MockHttpResp(json.dumps({"full_name": "org/wrongname"}).encode("utf-8"))
        if u.path == "/repos/org/wrongname/contents/plugin.yaml":
            b64 = base64.b64encode(b"name: other\nversion: 1.0.0\n").decode("ascii")
            return _MockHttpResp(json.dumps({"type": "file", "encoding": "base64", "content": b64}).encode("utf-8"))
        raise urllib.error.HTTPError(req.full_url, 404, "Not Found", {}, io.BytesIO(b"{}"))
    if method == "HEAD":
        if "range405" in u.path:
            raise urllib.error.HTTPError(req.full_url, 405, "Method Not Allowed", {}, io.BytesIO(b""))
        if "head_over" in u.path:
            return _MockHttpResp(b"", {"Content-Length": str(2 * 1024 * 1024 + 1)})
        return _MockHttpResp(b"", {"Content-Length": str(2 * 1024 * 1024)})
    if "get_over" in u.path:
        return _MockHttpResp(b"X" * (2 * 1024 * 1024 + 1))
    return _MockHttpResp(b"X" * (2 * 1024 * 1024))


# 1) Resolution + boundaries
all_cat_rel = [
    p.relative_to(m001_root).as_posix()
    for p in sorted((m001_root / "plugins").rglob("*"))
    if p.is_file()
]
m001_res_cases = []
for env_dict, paths_arg, diff_arg, max_p in [
    ({}, all_cat_rel, None, 1000),
    ({"BEFORE_SHA": "0" * 40, "AFTER_SHA": "abc"}, ["plugins/a/index.yaml", "plugins/_res/index.yaml", "plugins/bad-dash/index.yaml"], None, 1000),
    ({"BEFORE_SHA": "111", "AFTER_SHA": "222"}, None, ["plugins/beta/index.yaml", "plugins/alpha/index.yaml", "authors/u/author.yaml"], 1000),
    ({"PLUGIN_NAMES": "zeta, _reserved_ok, bad-dash, alpha", "START_FROM": "0", "MAX_PLUGINS": "10"}, None, None, 10),
    ({"PLUGIN_NAMES": "alpha, beta, gamma", "START_FROM": "1", "MAX_PLUGINS": "10"}, None, None, 10),
    ({"PLUGIN_NAMES": "alpha, beta, gamma", "START_FROM": "2", "MAX_PLUGINS": "10"}, None, None, 10),
    ({"PLUGIN_NAMES": "alpha, beta, gamma", "START_FROM": "-1", "MAX_PLUGINS": "10"}, None, None, 10),
    ({"PLUGIN_NAMES": "alpha, beta, gamma", "START_FROM": "bad", "MAX_PLUGINS": "3"}, None, None, 3),
    ({"PLUGIN_NAMES": "alpha, beta, gamma, delta", "START_FROM": "0", "MAX_PLUGINS": "3"}, None, None, 3),
]:
    with (
        patch.dict(os.environ, env_dict, clear=True),
        patch.object(up_pres, "_git_all_plugin_paths", lambda _c, _p=paths_arg: list(_p or [])),
        patch.object(up_pres, "_git_diff_names", lambda _b, _a, _d=diff_arg: list(_d or [])),
        redirect_stdout(io.StringIO()),
    ):
        m001_res_cases.append(_safe_call(up_pres.get_plugin_names))

# 2) Validation & exact limits (50/51, 500/501, 2000/2001, 5/6 tags & screenshots, 20KB/20KB+1, 2MB/2MB+1)
m001_val_tmp = Path(tempfile.mkdtemp(dir=str(iso), prefix="ora_m001_val_"))
yaml_2000 = "title: Ok\ngithub: https://github.com/org/alpha\ndescription: " + ("d" * (2000 - len("title: Ok\ngithub: https://github.com/org/alpha\ndescription: ")))
assert len(yaml_2000) == 2000
yaml_2001 = yaml_2000 + "x"
png_20480 = _make_exact_png(8, 8, 20 * 1024)
png_20481 = _make_exact_png(8, 8, 20 * 1024 + 1)
png_rect = _make_exact_png(16, 12, 200)

val_pdir = m001_val_tmp / "plugins"
val_pdir.mkdir()
# 5 thumbnail & allowed-file dirs
for sub_n, files_map in [
    ("t_exact_20kb", {"index.yaml": "title: T\n", "thumbnail.png": png_20480}),
    ("t_over_20kb", {"index.yaml": "title: T\n", "thumbnail.png": png_20481}),
    ("t_non_square", {"index.yaml": "title: T\n", "thumbnail.png": png_rect}),
    ("t_two_thumbs", {"index.yaml": "title: T\n", "thumbnail.png": png_20480, "thumbnail.jpg": png_20480}),
    ("t_none", {"index.yaml": "title: T\n"}),
    ("f_extra", {"index.yaml": "title: T\n", "thumbnail.png": png_20480, "README.md": b"bad"}),
]:
    dp = val_pdir / sub_n
    dp.mkdir()
    for fn, content in files_map.items():
        if isinstance(content, bytes):
            (dp / fn).write_bytes(content)
        else:
            (dp / fn).write_text(content, encoding="utf-8")

yaml_dirs = {"y_2000": yaml_2000, "y_2001": yaml_2001, "y_bad": ":\n  - [unclosed", "y_list": "- a\n- b\n"}
for yn, ytxt in yaml_dirs.items():
    ydp = val_pdir / yn
    ydp.mkdir()
    (ydp / "index.yaml").write_text(ytxt, encoding="utf-8")

def _mock_git_exists(_c, rel):
    return (m001_val_tmp / rel).exists()
def _mock_git_text(_c, rel):
    return (m001_val_tmp / rel).read_text(encoding="utf-8")
def _mock_git_bytes(_c, rel):
    return (m001_val_tmp / rel).read_bytes()
def _mock_git_files(_c, pname):
    d = val_pdir / pname
    return sorted(p.name for p in d.iterdir() if p.is_file())

base_meta = {"title": "Alpha", "description": "Valid", "github": "https://github.com/org/alpha"}
field_cases = [
    ("valid_full", {**base_meta, "tags": ["a", "b", "c", "d", "e"], "screenshots": [f"https://example.com/s{i}.png" for i in range(5)]}),
    ("unknown_field", {**base_meta, "extra": "nope"}),
    ("missing_req", {"title": "Only"}),
    ("title_50_ok", {**base_meta, "title": "T" * 50}),
    ("title_51_fail", {**base_meta, "title": "T" * 51}),
    ("desc_500_ok", {**base_meta, "description": "D" * 500}),
    ("desc_501_fail", {**base_meta, "description": "D" * 501}),
    ("tags_5_ok", {**base_meta, "tags": ["t1", "t2", "t3", "t4", "t5"]}),
    ("tags_6_fail", {**base_meta, "tags": ["t1", "t2", "t3", "t4", "t5", "t6"]}),
    ("shots_5_ok", {**base_meta, "screenshots": [f"https://example.com/ok{i}.png" for i in range(5)]}),
    ("shots_6_fail", {**base_meta, "screenshots": [f"https://example.com/ok{i}.png" for i in range(6)]}),
    ("shot_head_over", {**base_meta, "screenshots": ["https://example.com/head_over.png"]}),
    ("shot_range_ok", {**base_meta, "screenshots": ["https://example.com/range405_ok.png"]}),
    ("shot_range_over", {**base_meta, "screenshots": ["https://example.com/range405_get_over.png"]}),
    ("shot_bad_ext", {**base_meta, "screenshots": ["https://example.com/a.gif"]}),
    ("repo_404", {**base_meta, "github": "https://github.com/org/missing"}),
    ("repo_wrong_name", {**base_meta, "github": "https://github.com/org/wrongname"}),
]

with (
    patch.dict(os.environ, {"BASE_SHA": "a", "HEAD_SHA": "b", "GITHUB_TOKEN": "t"}, clear=True),
    patch.object(up_vps, "REPO_ROOT", m001_val_tmp),
    patch.object(up_vps, "PLUGINS_DIR", val_pdir),
    patch.object(up_vps, "_git_path_exists", _mock_git_exists),
    patch.object(up_vps, "_git_read_text", _mock_git_text),
    patch.object(up_vps, "_git_read_bytes", _mock_git_bytes),
    patch.object(up_vps, "_git_plugin_files", _mock_git_files),
    patch("urllib.request.urlopen", _m001_mock_urlopen),
):
    m001_val_out = {
        "urls": [
            [up_vps._parse_repo_url(u), up_vps._normalize_repo_url(u), up_vps._repo_owner_from_url(u)]
            for u in ["https://github.com/Org/Repo.git", "http://github.com/o/r/", "https://gitlab.com/o/r", "bad"]
        ],
        "yaml_strict": [_safe_call(up_vps._read_plugin_yaml, yn) for yn in ("y_2000", "y_2001", "y_bad", "y_list")],
        "fields": [(lbl, _safe_call(up_vps._validate_fields, m, "alpha")) for lbl, m in field_cases],
        "thumbs": [(sn, _safe_call(up_vps._validate_thumbnail, sn)) for sn in ("t_exact_20kb", "t_over_20kb", "t_non_square", "t_two_thumbs", "t_none")],
        "allowed_files": [(sn, _safe_call(up_vps._validate_allowed_files, sn)) for sn in ("t_exact_20kb", "f_extra")],
        "remote_names": [
            _safe_call(up_vps._validate_remote_plugin_name, {"encoding": "base64", "content": base64.b64encode(b"name: alpha\n").decode()}, "alpha"),
            _safe_call(up_vps._validate_remote_plugin_name, {"encoding": "base64", "content": base64.b64encode(b"name: beta\n").decode()}, "alpha"),
            _safe_call(up_vps._validate_remote_plugin_name, {"encoding": "bad", "content": "x"}, "alpha"),
        ],
        "submissions": [
            _safe_call(up_vps._submission_plugin_name, ["plugins/my_plugin/index.yaml"]),
            _safe_call(up_vps._submission_plugin_name, ["README.md"]),
            _safe_call(up_vps._submission_plugin_name, ["plugins/bad-name/index.yaml"]),
            _safe_call(up_vps._submission_plugin_name, ["plugins/a/index.yaml", "plugins/b/index.yaml"]),
        ],
        "is_deletion": [
            up_vps._is_deletion_pr([("D", ["plugins/a/index.yaml"])], "a"),
            up_vps._is_deletion_pr([("M", ["plugins/a/index.yaml"])], "a"),
        ],
    }

# Duplicate repo index check
m001_idx_tmp = Path(tempfile.mkdtemp(dir=str(iso), prefix="ora_m001_idx_"))
(m001_idx_tmp / "index.json").write_text(json.dumps({"plugins": {"other_p": {"github": "https://github.com/org/repo"}}}), encoding="utf-8")
with patch.object(up_vps, "INDEX_JSON_PATH", m001_idx_tmp / "index.json"):
    m001_val_out["dup_repo_checks"] = [
        _safe_call(up_vps._validate_github_repo_not_in_index, "new_p", "https://github.com/ORG/REPO.git"),
        _safe_call(up_vps._validate_github_repo_not_in_index, "other_p", "https://github.com/ORG/REPO.git"),
        _safe_call(up_vps._validate_github_repo_not_in_index, "new_p", "https://github.com/org/fresh"),
    ]

# 3) Full 235-folder catalog compilation via sync_plugin_state
sync_tmp = Path(tempfile.mkdtemp(dir=str(iso), prefix="ora_m001_sync_"))
sync_idx_path = sync_tmp / "index.json"
with (
    patch.dict(os.environ, {"GITHUB_REPOSITORY": "Amdkn/a0-plugins", "GITHUB_TOKEN": "test", "GITHUB_REF_NAME": "main"}, clear=True),
    patch.object(up_sync, "REPO_ROOT", m001_root),
    patch.object(up_sync, "PLUGINS_DIR", m001_root / "plugins"),
    patch.object(up_sync, "AUTHORS_DIR", m001_root / "authors"),
    patch.object(up_sync, "GENERATED_THUMBNAILS_DIR", m001_root / "generated" / "thumbnails"),
    patch.object(up_sync, "INDEX_JSON_PATH", sync_idx_path),
    patch.object(up_sync, "DISCUSSION_TEMPLATE_PATH", m001_scripts / "plugin_discussion_template.md"),
    patch.object(up_pres, "REPO_ROOT", m001_root),
    patch.object(up_pres, "PLUGINS_DIR", m001_root / "plugins"),
    patch.object(up_pres, "_git_all_plugin_paths", lambda _c: all_cat_rel),
    patch.object(up_sync, "_get_repo_and_category", lambda *a: ("rid", "cid")),
    patch.object(up_sync, "_sync_existing_plugin", lambda o, r, _rid, _cid, pn: ("created", f"https://github.com/{o}/{r}/discussions/{pn}")),
    patch.object(up_sync, "_sync_deleted_plugin", lambda *a: "missing"),
    redirect_stdout(io.StringIO()),
):
    assert up_sync.main() == 0
    compiled_index = json.loads(sync_idx_path.read_text(encoding="utf-8"))

# Also test upsert preservation & discussion rendering
up_idx_state = {"version": 1, "plugins": {"alpha": {"stars": 42, "version": "1.2.3", "commit": "abc", "updated": "2026-01-01"}}}
up_sync._upsert_index_plugin(up_idx_state, "alpha", {"title": "Alpha", "github": "https://github.com/u/r"})
up_removed_ok = up_sync._remove_index_plugin(up_idx_state, "alpha")
up_removed_miss = up_sync._remove_index_plugin(up_idx_state, "missing")
with patch.object(up_sync, "DISCUSSION_TEMPLATE_PATH", m001_scripts / "plugin_discussion_template.md"):
    up_disc_body = up_sync._render_discussion_body("alpha", base_meta, "Amdkn", "a0-plugins")

# 4) Orphans + Stars
with (
    patch.object(up_orph, "INDEX_JSON_PATH", sync_idx_path),
    patch.object(up_orph, "PLUGINS_DIR", m001_root / "plugins"),
):
    sync_copy = json.loads(sync_idx_path.read_text(encoding="utf-8"))
    existing_real = next(iter(sync_copy["plugins"]))
    sync_copy["plugins"]["deleted_ok"] = {"discussion": "https://github.com/Amdkn/a0-plugins/discussions/deleted_ok"}
    sync_copy["plugins"]["_example1"] = {"discussion": ""}
    sync_copy["plugins"]["bad-name"] = {"discussion": ""}
    idx_names = set(sync_copy["plugins"].keys())
    cands = sorted(idx_names | {"ghost_plugin", existing_real})
    orph_list = [n for n in cands if up_pres.is_valid_plugin_dirname(n) and not up_orph._plugin_exists(n)]

marker_cases = [
    up_orph._discussion_marker_name("<!-- a0-plugins-discussion -->\n<!-- a0-plugins-plugin:my_mod -->\n"),
    up_orph._discussion_marker_name("no marker here"),
    up_orph._discussion_marker_name("<!-- a0-plugins-plugin:   -->"),
]
stars_idx_path = m001_idx_tmp / "stars_index.json"
stars_upd_path = m001_idx_tmp / "stars_upd.json"
stars_idx_path.write_text(json.dumps({"version": 1, "plugins": {"b": {"stars": 1}, "a": {"stars": 2}}}), encoding="utf-8")
stars_upd_path.write_text(json.dumps({"a": {"stars": 0, "version": "2.0.0", "commit": "def", "updated": "2026-11-20"}, "gone": {"stars": 9}}), encoding="utf-8")
with patch.object(up_stars, "INDEX_PATH", stars_idx_path), redirect_stdout(io.StringIO()):
    assert up_stars._apply_updates(stars_upd_path) == 0
    stars_after = json.loads(stars_idx_path.read_text(encoding="utf-8"))

stars_out = {
    "chunks": [up_stars._chunks([1, 2, 3], 3), up_stars._chunks([1, 2, 3, 4], 3), up_stars._chunks([], 3)],
    "alias_errors": up_stars._extract_alias_errors({"errors": [{"path": ["r0", "sub"], "message": " Could not resolve "}]}),
    "versions": [up_stars._extract_plugin_version("name: x\nversion: '1.2.3' # comment\n"), up_stars._extract_plugin_version("name: x\n")],
    "commits": [up_stars._extract_commit_info({"defaultBranchRef": {"target": {"oid": "abc", "committedDate": "2026-01-01"}}}), up_stars._extract_commit_info({})],
    "applied": stars_after,
}

# 5) 11 Release publish/download scenarios (mirrors test_index_release.py)
REL_OLD = b'{"version":1,"plugins":{"kept":{},"removed":{}}}'
REL_NEW = b'{"version":1,"plugins":{"kept":{}}}'
rel_scenarios = [
    ({"index.json": REL_OLD}, "", REL_NEW),
    ({"index.json": REL_OLD}, "rename_502", REL_NEW),
    ({"index.json": REL_OLD}, "rename_502_twice", REL_NEW),
    ({"index.json": REL_OLD}, "upload_failure", REL_NEW),
    ({"index.json.next": b"", "index.json.previous": REL_OLD}, "upload_failure_empty_next", REL_NEW),
    ({"index.json": REL_OLD}, "incomplete_upload", REL_NEW),
    ({"index.json": REL_OLD}, "promotion_failure", REL_NEW),
    ({"index.json": REL_OLD, "index.json.previous": REL_OLD}, "delete_502", REL_NEW),
    ({"index.json.next": REL_NEW, "index.json.previous": REL_OLD}, "", REL_NEW),
    ({"index.json.previous": REL_OLD}, "", REL_NEW),
    ({}, "", REL_NEW),
    ({"index.json": REL_OLD}, "invalid_index", b'{"error":"Not Found"}'),
    ({"index.json": REL_OLD}, "invalid_index", b'{"plugins":{}}'),
]

def _run_rel_scenario_oracle(initial, fault, content):
    assets, contents, faults, mutations = {}, {}, [], []
    serial = [0]
    def _add(name, data):
        serial[0] += 1
        a = {"id": serial[0], "name": name, "state": "uploaded", "size": len(data)}
        assets[serial[0]] = a
        contents[serial[0]] = data
        return a
    for k, v in initial.items():
        _add(k, v)
    def _err(req, code):
        raise urllib.error.HTTPError(req.full_url, code, "Injected", {}, io.BytesIO(b"{}"))
    def _req(request, timeout):
        u = urllib.parse.urlparse(request.full_url)
        m = request.get_method()
        if m != "GET":
            mutations.append(m)
        if u.hostname == "download.test":
            return io.BytesIO(contents[int(u.path.strip("/"))] if u.query else REL_OLD)
        if "/releases/assets/" in u.path:
            aid = int(u.path.rsplit("/", 1)[1])
            if aid not in assets:
                _err(request, 404)
            asset = assets[aid]
            if m == "DELETE":
                del assets[aid]
                del contents[aid]
                if fault == "delete_502" and not faults:
                    faults.append(fault)
                    _err(request, 502)
                return io.BytesIO()
            if m == "PATCH":
                nm = json.loads(request.data)["name"]
                if fault == "promotion_failure" and asset["name"] == "index.json.next":
                    faults.append(fault)
                    _err(request, 502)
                if fault == "rename_502_twice" and len(faults) < 2:
                    faults.append(fault)
                    _err(request, 502)
                asset["name"] = nm
                if fault == "rename_502" and not faults:
                    faults.append(fault)
                    _err(request, 502)
            return io.BytesIO(json.dumps(asset).encode())
        if m == "POST" and u.hostname == "uploads.github.com":
            if fault in ("upload_failure", "upload_failure_empty_next"):
                faults.append(fault)
                _err(request, 502)
            a = _add(urllib.parse.parse_qs(u.query)["name"][0], request.data)
            if fault == "incomplete_upload":
                faults.append(fault)
                a["state"] = "starter"
            return io.BytesIO(json.dumps(a).encode())
        return io.BytesIO(json.dumps({
            "id": 1,
            "upload_url": "https://uploads.github.com/repos/test/repo/releases/1/assets{?name,label}",
            "assets": [dict(a, browser_download_url=f"https://download.test/{a['id']}") for a in assets.values()],
        }).encode())

    with tempfile.TemporaryDirectory() as d:
        rt = Path(d)
        idx_p = rt / "index.json"
        with (
            patch.dict(os.environ, {"GITHUB_REPOSITORY": "test/repo", "GITHUB_TOKEN": "test"}, clear=True),
            patch.object(up_pub, "INDEX_PATH", idx_p),
            patch.object(up_dl, "INDEX_PATH", idx_p),
            patch.object(up_dl, "REPO_ROOT", rt),
            patch("urllib.request.urlopen", _req),
            patch("time.sleep"),
            redirect_stdout(io.StringIO()),
        ):
            dl1 = idx_p.read_bytes().decode("utf-8") if (initial and fault != "upload_failure_empty_next" and up_dl.main() == 0) else None
            idx_p.write_bytes(content)
            failed = False
            try:
                up_pub.main()
            except up_pub.PublishReleaseError:
                failed = True
            cur = next(a for a in assets.values() if a["name"] == "index.json")
            dl2 = None
            if not failed:
                up_dl.main()
                dl2 = idx_p.read_bytes().decode("utf-8")
            return {"dl1": dl1, "failed": failed, "cur": contents[cur["id"]].decode("utf-8"), "dl2": dl2, "mutations": len(mutations)}

rel_out = [_run_rel_scenario_oracle(ini, flt, cnt) for ini, flt, cnt in rel_scenarios]

dl_retry_seqs = [[499], [500, 500, 200], [500, 500, 500], [429, 429, 200], ["net_err", "net_err", 200]]

def _run_dl_retry_oracle(seq):
    attempts = [0]
    sleeps = []

    def _dl_req(request, timeout):
        u = urllib.parse.urlparse(request.full_url)
        if u.hostname == "download.test":
            attempts[0] += 1
            ev = seq[attempts[0] - 1]
            if ev == 200:
                return io.BytesIO(REL_NEW)
            if ev == "net_err":
                raise OSError("injected connection reset")
            raise urllib.error.HTTPError(request.full_url, ev, "Injected", {}, io.BytesIO(b"err"))
        return io.BytesIO(json.dumps({
            "id": 1,
            "assets": [{
                "id": 1,
                "name": "index.json",
                "state": "uploaded",
                "size": len(REL_NEW),
                "browser_download_url": "https://download.test/1",
            }],
        }).encode())

    with tempfile.TemporaryDirectory() as d:
        rt = Path(d)
        idx_p = rt / "index.json"
        ok = False
        with (
            patch.dict(os.environ, {"GITHUB_REPOSITORY": "test/repo", "GITHUB_TOKEN": "test"}, clear=True),
            patch.object(up_dl, "INDEX_PATH", idx_p),
            patch.object(up_dl, "REPO_ROOT", rt),
            patch("urllib.request.urlopen", _dl_req),
            patch("time.sleep", lambda s: sleeps.append(s)),
            redirect_stdout(io.StringIO()),
        ):
            try:
                ok = up_dl.main() == 0
            except up_dl.DownloadIndexError:
                ok = False
        return {
            "ok": ok,
            "attempts": attempts[0],
            "sleeps": list(sleeps),
            "body": idx_p.read_bytes().decode("utf-8") if ok else None,
        }

dl_retry_out = [_run_dl_retry_oracle(s) for s in dl_retry_seqs]

# 6) Adapter audit counts (real 235 dirs)
adp_v = up_a0_adp.validate()
audit_keys = (
    "plugin_dirs_total", "plugin_names_resolved", "indexed_plugins", "index_yaml_present",
    "legacy_plugin_yaml_only", "blocked_plugins", "index_yaml_invalid", "index_yaml_missing_keys",
    "max_screenshots", "generated_thumbnails", "orphan_thumbnails", "local_thumbnails",
    "plugins_without_any_thumbnail", "abandoned_present", "surfaces_present", "index_coherent",
)
m001_out = {
    "resolution": m001_res_cases,
    "validation": m001_val_out,
    "compiled_index": compiled_index,
    "upsert_preserve": {},
    "upsert_preserved_check": {
        "removed_ok": up_removed_ok,
        "removed_miss": up_removed_miss,
        "discussion_body": up_disc_body,
    },
    "orphans": {"markers": marker_cases, "list": orph_list},
    "stars": stars_out,
    "releases": rel_out,
    "dl_retries": dl_retry_out,
    "audit": {k: adp_v[k] for k in audit_keys},
}
# Capture preserved entry cleanly before removal
tmp_u = {"version": 1, "plugins": {"alpha": {"stars": 42, "version": "1.2.3", "commit": "abc", "updated": "2026-01-01"}}}
up_sync._upsert_index_plugin(tmp_u, "alpha", {"title": "Alpha", "github": "https://github.com/u/r"})
m001_out["upsert_preserve"] = tmp_u["plugins"]["alpha"]

(iso / "oracle_outputs.json").write_text(
    json.dumps(
        {"m001": m001_out, "m044": m044_out, "m050": m050_out, "m056": m056_out, "m074": m074_out, "m084": m084_out, "m117": m117_out, "m118": m118_out},
        ensure_ascii=False,
        indent=2,
    ),
    encoding="utf-8",
)
'''


_ORGAN_RUNNER_CODE = r'''
import copy
import dataclasses
import datetime as dt
import json
import sys
import tempfile
from pathlib import Path
from types import SimpleNamespace
import numpy as np
from PIL import Image, ImageDraw

iso = Path.cwd()
inputs = json.loads((iso / "diff_inputs.json").read_text(encoding="utf-8"))
oracle = json.loads((iso / "oracle_outputs.json").read_text(encoding="utf-8"))
sha = sys.argv[1]

sys.path.insert(0, str(iso / "01_Forkable/FKB00_Runtime/00_A0_Core"))
sys.path.insert(0, str(iso / "01_Forkable/FKB07_Money_Maker/02_Video"))
sys.path.insert(0, str(iso / "01_Forkable/FKB07_Money_Maker/01_Trading"))
import aspace_foundation_kernel as fk
import aspace_fkb02_memory_organ as f02
import aspace_fkb04_anything_organ as f04
import aspace_discovery_catalog as cat
import aspace_plugin_registry_organ as reg
import aspace_video_studio_foundation as vsf
import aspace_trading_copilot_foundation as trd

# Aucune source supprimée ne doit subsister sous iso_root
for _gone in (
    "01_Forkable/FKB00_Runtime/00_A0_Core/a0-plugins",
    "01_Forkable/FKB02_Memory/01_BillionContxtLanguage_AutoOnthology/context-language-models",
    "01_Forkable/FKB02_Memory/knowledge-catalog",
    "01_Forkable/FKB04_Tools_Anything/CLI-Anything",
    "01_Forkable/FKB07_Money_Maker/02_Video/video-director",
    "01_Forkable/FKB07_Money_Maker/01_Trading/tradingview-indicator-search-mcp-server",
    "01_Forkable/FKB07_Money_Maker/00_Marketplace_YoutubeSkills",
    "01_Forkable/FKB01_Inference/04_Inference_Youtube_Discovery_Registry",
):
    assert not (iso / _gone).exists(), f"Source toujours présente avant Phase C: {_gone}"


def _safe_call(fn, *args, **kwargs):
    try:
        return {"ok": True, "val": fn(*args, **kwargs)}
    except Exception as exc:
        return {"ok": False, "err": type(exc).__name__}


def verify_m044() -> int:
    c_texts = [f02.clm_content_text(c) for c in inputs["m044"]["content_cases"]]
    assert c_texts == oracle["m044"]["content_texts"], "M044 clm_content_text mismatch"

    r_texts = [f02.clm_rendered_text(m) for m in inputs["m044"]["render_msgs"]]
    assert r_texts == oracle["m044"]["rendered_texts"], "M044 clm_rendered_text mismatch"

    ed_out, parse_out = [], []
    for conv in inputs["m044"]["conversations"]:
        for p in (0, 1, 2, 10):
            ed = f02.clm_render_editable(conv, protect=p)
            ed_out.append({"protect": p, "text": ed})
            parse_out.append({"protect": p, "parsed": f02.clm_parse_back(ed, conv[:p])})
    assert ed_out == oracle["m044"]["editables"], "M044 clm_render_editable mismatch"
    assert parse_out == oracle["m044"]["parses_conv"], "M044 clm_parse_back conv mismatch"

    protected_ref = inputs["m044"]["conversations"][0][:2]
    edge_out = {
        lbl: f02.clm_parse_back(edited, protected_ref)
        for lbl, edited in inputs["m044"]["parse_back_cases"]
    }
    assert edge_out == oracle["m044"]["parse_back_edge"], "M044 clm_parse_back/_clm_normalize edge mismatch"

    res_gate = [
        _safe_call(f02.clm_resolve_allow_edit_growth, passed, env)
        for passed, env in inputs["m044"]["edit_gate_cases"]["resolve"]
    ]
    assert res_gate == oracle["m044"]["resolve_gate"], "M044 clm_resolve_allow_edit_growth mismatch"
    assert f02.clm_fit_rule(4096) == oracle["m044"]["fit_rule"], "M044 clm_fit_rule mismatch"

    mg = [f02.clm_may_grow(allow_growth=ag, limit=lim, after=af) for ag, lim, af in inputs["m044"]["edit_gate_cases"]["may_grow"]]
    assert mg == oracle["m044"]["may_grow"], "M044 clm_may_grow mismatch"

    rr = [f02.clm_reject_rule(allow_growth=ag, limit=lim) for ag, lim in inputs["m044"]["edit_gate_cases"]["reject_rule"]]
    assert rr == oracle["m044"]["reject_rule"], "M044 clm_reject_rule mismatch"

    rn = f02.clm_rejected_note(baseline=1000, after=1200, before=900, rule=f02.clm_fit_rule(1000))
    assert rn == oracle["m044"]["rejected_note"], "M044 clm_rejected_note mismatch"

    assert f02.CLM_SUBMIT_MARKER == oracle["m044"]["finish_marker"]
    assert f02.CLM_FINISH_INSTRUCTIONS == oracle["m044"]["finish_instructions"]

    f_modes = []
    for md in inputs["m044"]["finish_policy_cases"]["modes"]:
        try:
            fp = f02.CLMFinishPolicy(md)
            f_modes.append({
                "ok": True,
                "mode": fp.mode,
                "open_ended": fp.open_ended,
                "fragment": fp.prompt_fragment(),
                "cmds": [fp.is_finish_command(c) for c in inputs["m044"]["finish_policy_cases"]["commands"]],
            })
        except Exception as exc:
            f_modes.append({"ok": False, "err": type(exc).__name__})
    assert f_modes == oracle["m044"]["finish_modes"], "M044 CLMFinishPolicy mismatch"

    s_cmds = [f02.clm_is_submit_command(c) for c in inputs["m044"]["finish_policy_cases"]["commands"]]
    assert s_cmds == oracle["m044"]["submit_commands"], "M044 clm_is_submit_command mismatch"

    t_keys = [f02.clm_token_cap_key(m) for m in inputs["m044"]["lm_compat_models"]]
    assert t_keys == oracle["m044"]["token_cap_keys"], "M044 clm_token_cap_key mismatch"

    return (
        len(c_texts) + len(r_texts) + len(ed_out) + len(parse_out) + len(edge_out)
        + len(res_gate) + 1 + len(mg) + len(rr) + 1 + len(f_modes) + len(s_cmds) + len(t_keys)
    )


def verify_m050() -> int:
    stale_now = dt.datetime.fromisoformat(inputs["m050"]["stale_now_iso"])
    doc_samples = list(inputs["m050"]["synthetic_docs"])
    concepts_dir = iso / "00_Memoire" / "bundle" / "concepts"
    if concepts_dir.exists():
        for md_p in sorted(concepts_dir.glob("*.md"))[:8]:
            doc_samples.append((f"concept:{md_p.name}", md_p.read_text(encoding="utf-8")))

    docs_res = []
    for label, raw in doc_samples:
        try:
            d = f02.OKFDocument.parse(raw)
            try:
                d.validate()
                val_ok = True
            except f02.OKFDocumentError:
                val_ok = False
            docs_res.append({
                "label": label,
                "ok": True,
                "validate_ok": val_ok,
                "frontmatter": d.frontmatter,
                "body": d.body,
                "serialized": d.serialize(),
            })
        except f02.OKFDocumentError:
            docs_res.append({"label": label, "ok": False, "err": "OKFDocumentError"})
    assert docs_res == oracle["m050"]["docs"], "M050 OKFDocument mismatch"

    trust_res = [
        {"normalized": f02.okf_normalize_verified(fm), "tier": f02.okf_trust_tier(fm)}
        for fm in inputs["m050"]["trust_cases"]
    ]
    assert trust_res == oracle["m050"]["trust"], "M050 okf_normalize_verified / okf_trust_tier mismatch"

    stale_fixed = [f02.okf_is_stale(fm, now=stale_now) for fm in inputs["m050"]["stale_cases"]]
    assert stale_fixed == oracle["m050"]["stale_fixed"], "M050 okf_is_stale fixed-now mismatch"

    stale_def = [
        f02.okf_is_stale({"stale_after": "2020-01-01T00:00:00Z"}),
        f02.okf_is_stale({"stale_after": "2099-01-01T00:00:00Z"}),
    ]
    assert stale_def == oracle["m050"]["stale_default_now"], "M050 okf_is_stale default-now mismatch"

    sf_res = [f02.okf_synthesize_fallback("", c, model="stub") for c in inputs["m050"]["synth_fallback_cases"]]
    assert sf_res == oracle["m050"]["synth_fallback"], "M050 okf_synthesize_fallback mismatch"

    b_multi = Path(tempfile.mkdtemp(dir=str(iso), prefix="org_okf_m_"))
    (b_multi / "datasets").mkdir()
    (b_multi / "datasets" / "only.md").write_text("---\ntype: BigQuery Dataset\ntitle: Only Dataset\ndescription: Single child desc.\n---\nBody.\n", encoding="utf-8")
    (b_multi / "single_no_desc").mkdir()
    (b_multi / "single_no_desc" / "only_empty.md").write_text("---\ntype: BigQuery Dataset\ntitle: EmptyDesc\n---\nBody.\n", encoding="utf-8")
    (b_multi / "tables").mkdir()
    (b_multi / "tables" / "events_.md").write_text("---\ntype: BigQuery Table\ntitle: events_*\ndescription: Sharded events.\n---\nEvents.\n", encoding="utf-8")
    (b_multi / "tables" / "users.md").write_text("---\ntype: BigQuery Table\ntitle: users\ndescription: Users table.\n---\nUsers.\n", encoding="utf-8")
    (b_multi / "empty_dir").mkdir()
    synth_calls = []
    def _org_synth(rel, pairs, *, model):
        synth_calls.append(rel)
        return f02.okf_synthesize_fallback(rel, pairs, model=model)
    gen_m = f02.okf_regenerate_indexes(b_multi, model="stub-test", synthesize=_org_synth)
    gen_missing = f02.okf_regenerate_indexes(iso / "does_not_exist_okf_dir", model="stub-test", synthesize=_org_synth)

    org_indexes = {p.relative_to(b_multi).as_posix(): p.read_text(encoding="utf-8") for p in sorted(gen_m)}
    assert org_indexes == oracle["m050"]["indexes_multi"], "M050 okf_regenerate_indexes mismatch"
    assert synth_calls == oracle["m050"]["synth_calls"], "M050 single-child synth bypass mismatch"
    assert len(gen_missing) == oracle["m050"]["indexes_missing_len"]
    assert (b_multi / "empty_dir" / "index.md").exists() == oracle["m050"]["empty_dir_has_index"]

    b_root = Path("/tmp_okf_root")
    path_cases = []
    for raw_cid in inputs["m050"]["concept_id_cases"]:
        try:
            cid = f02.okf_parse_concept_id(raw_cid)
            p = f02.okf_concept_id_to_path(b_root, cid)
            back = f02.okf_path_to_concept_id(b_root, p)
            path_cases.append({"ok": True, "cid": list(cid), "rel": p.relative_to(b_root).as_posix(), "back": list(back)})
        except ValueError:
            path_cases.append({"ok": False, "err": "ValueError"})
    path_cases.append(_safe_call(f02.okf_concept_id_to_path, b_root, ()))
    assert path_cases == oracle["m050"]["paths"], "M050 OKF paths mismatch"

    return (
        len(docs_res) + len(trust_res) + len(stale_fixed) + len(stale_def)
        + len(sf_res) + len(org_indexes) + 3 + len(path_cases)
    )


def verify_m056() -> int:
    syn_root = iso / "syn_harnesses"
    harnesses_org = {}
    for label, h_dir in [
        ("zotero", iso / "test_input_harnesses/zotero/agent-harness"),
        ("audacity", iso / "test_input_harnesses/audacity/agent-harness"),
        ("syn_export", syn_root / "syn_export" / "agent-harness"),
        ("syn_flat", syn_root / "syn_flat" / "agent-harness"),
        ("syn_intro_100", syn_root / "syn_intro_100" / "agent-harness"),
        ("syn_intro_101", syn_root / "syn_intro_101" / "agent-harness"),
    ]:
        meta = f04.extract_cli_anything_metadata(h_dir)
        cli_files = list((h_dir / "cli_anything").glob("*/*_cli.py"))
        raw_cmds = [dataclasses.asdict(g) for g in f04.extract_commands_from_cli(cli_files[0])] if cli_files else []
        harnesses_org[label] = {
            "meta": dataclasses.asdict(meta),
            "raw_cmds": raw_cmds,
            "skill_md": f04.generate_cli_anything_skill_md(meta),
            "skill_md_simple": f04.generate_cli_anything_skill_md_simple(meta),
        }
    assert harnesses_org == oracle["m056"]["harnesses"], "M056 harnesses mismatch"

    inv_res = _safe_call(f04.extract_cli_anything_metadata, iso / "does_not_exist_harness")
    assert inv_res == oracle["m056"]["invalid"], "M056 error handling mismatch"

    ck_org = [
        f04.build_cli_anything_preview_cache_key(
            ck["software"], ck["recipe"], ck["bundle_kind"], ck["source_fingerprint"],
            options=ck["options"], harness_version=ck["harness_version"],
        )
        for ck in inputs["m056"]["cache_key_cases"]
    ]
    assert ck_org == oracle["m056"]["cache_keys"], "M056 cache keys mismatch"
    return len(harnesses_org) * 4 + 1 + len(ck_org)


def verify_m084() -> int:
    assert [vsf.vd_is_num(x) for x in inputs["m084"]["is_num_cases"]] == oracle["m084"]["is_num"], "M084 vd_is_num mismatch"
    assert [vsf.vd_norm(x) for x in inputs["m084"]["norm_cases"]] == oracle["m084"]["norm"], "M084 vd_norm mismatch"
    assert [vsf.vd_read_time(x) for x in inputs["m084"]["read_time_cases"]] == oracle["m084"]["read_time"], "M084 vd_read_time mismatch"

    tmp_vd = Path(tempfile.mkdtemp(dir=str(iso), prefix="org_vd_"))
    tl_res = []
    for item in inputs["m084"]["timelines"]:
        tl_file = tmp_vd / f"{item['name']}.json"
        tl_file.write_text(json.dumps(item["tl"]), encoding="utf-8")
        rc, out_txt = vsf.vd_check_timeline_cli(["check_timeline.py", str(tl_file)])
        tl_res.append({
            "name": item["name"],
            "returncode": rc,
            "stdout": out_txt.replace("\r\n", "\n"),
            "beat_times": vsf.vd_beat_times(item["tl"]),
            "loaded_tl": vsf.vd_load_timeline(tl_file),
        })
    assert tl_res == oracle["m084"]["timelines"], "M084 check_timeline / beat_times / load_timeline mismatch"

    list_tl_file = tmp_vd / "list_tl.json"
    list_tl_file.write_text(json.dumps([0.5, 2.0, 1.0, 2.0]), encoding="utf-8")
    assert vsf.vd_load_timeline(list_tl_file) == oracle["m084"]["list_tl_loaded"], "M084 list load_timeline mismatch"

    raw_runs = [vsf.vd_runs(r) for r in inputs["m084"]["runs_cases"]]
    assert [[list(p) for p in rs] for rs in raw_runs] == oracle["m084"]["runs"], "M084 vd_runs mismatch"

    d_arr = np.full(45, 0.8, dtype=np.float64)
    d_arr[0] = 0.0
    d_arr[5] = 8.0
    d_arr[6] = 8.2
    d_arr[12] = 15.0
    d_arr[18] = 3.5
    d_arr[25:42] = 0.05
    std_arr = np.full(45, 18.0, dtype=np.float64)
    std_arr[20:23] = 2.5
    skip_arr = np.full(45, 0.9, dtype=np.float64)
    skip_arr[0] = np.nan
    skip_arr[-1] = np.nan
    skip_arr[5] = 0.5
    mean_arr = np.full(45, 120.0, dtype=np.float64)
    st_dict = {"n": 45, "mean": mean_arr, "std": std_arr, "d": d_arr, "skip": skip_arr, "seam": 0.4}
    args_ns = SimpleNamespace(freeze=0.5, freeze_eps=0.25, loop=True)

    d_b = np.full(50, 0.8, dtype=np.float64)
    d_b[0] = 0.0
    d_b[3] = 6.0
    d_b[6] = 0.1
    d_b[7] = 2.0
    d_b[8] = 0.1
    d_b[10:24] = 0.2
    d_b[25] = 0.2
    d_b[26] = 0.25
    d_b[27] = 0.2
    d_b[30:43] = 0.2
    std_b = np.full(50, 6.0, dtype=np.float64)
    skip_b = np.full(50, 0.9, dtype=np.float64)
    skip_b[0] = np.nan
    skip_b[-1] = np.nan
    mean_b = np.full(50, 100.0, dtype=np.float64)
    st_boundary = {"n": 50, "mean": mean_b, "std": std_b, "d": d_b, "skip": skip_b, "seam": 0.5}

    pic_res = [
        vsf.vd_analyse_picture(st_dict, 30.0, args_ns),
        vsf.vd_analyse_picture(st_boundary, 30.0, args_ns),
    ]
    assert pic_res == oracle["m084"]["analyse_picture"], "M084 vd_analyse_picture mismatch"

    cc_res = [vsf.vd_compare_cuts(det, exp, fps) for det, exp, fps in inputs["m084"]["compare_cuts_cases"]]
    assert cc_res == oracle["m084"]["compare_cuts"], "M084 vd_compare_cuts mismatch"

    im_contrast = Image.new("RGB", (200, 100), (0, 0, 0))
    draw = ImageDraw.Draw(im_contrast)
    draw.rectangle([20, 20, 120, 70], fill=(255, 255, 255))
    im_flat = Image.new("RGB", (100, 100), (128, 128, 128))
    im_half = Image.new("RGB", (100, 100), (0, 0, 0))
    ImageDraw.Draw(im_half).rectangle([0, 0, 49, 99], fill=(255, 255, 255))
    mt_res = [
        vsf.vd_measure_text(im_contrast, [10, 10, 140, 80], 1080),
        vsf.vd_measure_text(im_contrast, [9.6, 10.4, 140.4, 79.5], 1080),
        vsf.vd_measure_text(im_flat, [10, 10, 60, 60], 1080),
        vsf.vd_measure_text(im_half, [0, 0, 100, 100], 1080),
    ]
    assert mt_res == oracle["m084"]["measure_text"], "M084 vd_measure_text mismatch"

    return (
        len(inputs["m084"]["is_num_cases"]) + len(inputs["m084"]["norm_cases"]) + len(inputs["m084"]["read_time_cases"])
        + len(tl_res) + 1 + len(inputs["m084"]["runs_cases"]) + 1 + len(cc_res) + len(mt_res)
    )


def verify_m117() -> int:
    assert cat.MARKETPLACE_SKILL_CATEGORIES == oracle["m117"]["categories"], "M117 categories strict == mismatch"
    assert cat.YOUTUBE_SKILL_VIDEOS == oracle["m117"]["videos"], "M117 videos strict == mismatch"
    assert cat.MARKETPLACE_PLAYBOOKS == oracle["m117"]["playbooks"], "M117 playbooks strict == mismatch"

    for c_id in inputs["m117"]["categories"]:
        pb = cat.get_marketplace_playbook(c_id)
        assert set(pb.keys()) == {"category"} | set(oracle["m117"]["playbooks"][c_id].keys()), "M117 playbook keys mismatch"
        assert {k: v for k, v in pb.items() if k != "category"} == oracle["m117"]["playbooks"][c_id]
        assert pb["category"] == c_id

    bad_cat = _safe_call(cat.get_marketplace_playbook, "non-existent-category")
    assert bad_cat == {"ok": False, "err": "ContractViolation"}

    q_checks = 0
    for qc in inputs["m117"]["query_cases"]:
        res = cat.query_marketplace_skills(category=qc["category"], keyword=qc["keyword"])
        # Exact oracle calculation from parsed oracle data
        exp_items = list(oracle["m117"]["videos"])
        exp_pbs = dict(oracle["m117"]["playbooks"])
        if qc["category"]:
            clow = qc["category"].lower()
            exp_items = [it for it in exp_items if it["category"].lower() == clow]
            exp_pbs = {k: v for k, v in exp_pbs.items() if k.lower() == clow or v["skill_name"].lower() == clow}
        if qc["keyword"]:
            kw = qc["keyword"].lower()
            exp_items = [it for it in exp_items if kw in it["topic"].lower() or kw in it["category"].lower()]
            exp_pbs = {
                k: v for k, v in exp_pbs.items()
                if kw in v["description"].lower() or kw in k.lower()
                or any(kw in o["offer"].lower() or kw in o["spec"].lower() or kw in o["pricing"].lower() for o in v["productized_offers"])
                or any(vid["category"] == k for vid in exp_items)
            }
        exp_offers = [{"category": k, **off} for k, pb in exp_pbs.items() for off in pb["productized_offers"]]
        assert res["matches"] == exp_items and res["playbooks"] == exp_pbs and res["productized_offers"] == exp_offers
        q_checks += 1

    return 3 + len(inputs["m117"]["categories"]) + 1 + q_checks


def verify_m118() -> int:
    assert cat.INFERENCE_DISCOVERY_REGISTRY == oracle["m118"]["registry"], "M118 registry strict == mismatch"
    assert cat.OPPORTUNITY_DOSSIERS == oracle["m118"]["dossiers"], "M118 dossiers strict == mismatch"

    for oid in inputs["m118"]["opp_ids"]:
        assert cat.get_opportunity_dossier(oid) == oracle["m118"]["dossiers"][oid], f"M118 get_opportunity_dossier({oid}) mismatch"

    bad_opp = _safe_call(cat.get_opportunity_dossier, "OPP-999")
    assert bad_opp == {"ok": False, "err": "ContractViolation"}

    known = {o["platform"].lower() for o in oracle["m118"]["registry"]["opportunities"]}
    expected_qual = [
        {"platform": "apinex.com", "dedup": "ALREADY_TRACKED", "authentic": True, "score": "A", "durability": "STABLE", "vector": "VOIE_A_API_DIRECT", "decision": "ADMIT_SOVEREIGN"},
        {"platform": "scam-clickbait.example", "decision": "REJECT_CLICKBAIT", "score": "F", "dedup": "NEW_OPPORTUNITY"},
        {"platform": "sovereign-new.example", "dedup": "NEW_OPPORTUNITY", "authentic": True, "score": "A", "durability": "STABLE", "vector": "VOIE_A_API_DIRECT", "decision": "ADMIT_SOVEREIGN"},
        {"platform": "web-trial.example", "dedup": "NEW_OPPORTUNITY", "authentic": True, "score": "B", "durability": "FLASH", "vector": "VOIE_B_WEB_SHIELDED", "decision": "ADMIT_SOVEREIGN"},
        {"platform": "stripe-loop.example", "dedup": "NEW_OPPORTUNITY", "authentic": True, "score": "C", "durability": "MEDIUM", "vector": "VOIE_B_WEB_SHIELDED", "decision": "ADMIT_WITH_MONITORING"},
        {"platform": "ttl6.example", "dedup": "NEW_OPPORTUNITY", "authentic": True, "score": "A", "durability": "FLASH", "vector": "VOIE_A_API_DIRECT", "decision": "ADMIT_SOVEREIGN"},
        {"platform": "ttl7.example", "dedup": "NEW_OPPORTUNITY", "authentic": True, "score": "A", "durability": "MEDIUM", "vector": "VOIE_A_API_DIRECT", "decision": "ADMIT_SOVEREIGN"},
        {"platform": "ttl29.example", "dedup": "NEW_OPPORTUNITY", "authentic": True, "score": "B", "durability": "MEDIUM", "vector": "VOIE_B_WEB_SHIELDED", "decision": "ADMIT_SOVEREIGN"},
        {"platform": "ttl30.example", "dedup": "NEW_OPPORTUNITY", "authentic": True, "score": "B", "durability": "STABLE", "vector": "VOIE_B_WEB_SHIELDED", "decision": "ADMIT_SOVEREIGN"},
    ]
    for cand, exp in zip(inputs["m118"]["qualify_cases"], expected_qual):
        assert cat.qualify_inference_opportunity(cand, known_platforms=known) == exp, f"M118 qualify mismatch for {cand}"

    return 2 + len(inputs["m118"]["opp_ids"]) + 1 + len(expected_qual)



def verify_m074() -> int:
    fix_dir = iso / "test_input_m074_fixtures"
    load_fix = lambda fn: json.loads((fix_dir / fn).read_text(encoding="utf-8"))
    gen_fix = load_fix("slug-feed-general.json")
    ed_fix = load_fix("slug-feed-editors.json")
    scalp_fix = load_fix("slug-feed-scalping.json")
    auth_fix = load_fix("author-feed.json")
    fac_open = load_fix("facade-open.json")
    fac_prot = load_fix("facade-protected.json")

    def _sc_ok(fn):
        try:
            fn()
            return True
        except Exception:
            return False

    def _sc_msg(fn):
        try:
            return {"ok": True, "val": fn(), "msg": ""}
        except Exception as exc:
            return {"ok": False, "err": type(exc).__name__, "msg": str(exc)}

    slug_gen = trd.tv_parse_slug_feed(gen_fix)
    slug_ed = trd.tv_parse_slug_feed(ed_fix)
    slug_scalp = trd.tv_parse_slug_feed(scalp_fix)
    auth_parsed = trd.tv_parse_author_feed(auth_fix)
    long_item = {"script_id_part": "PUB;a", "name": "Long Winded Indicator", "description": "word " * 2000}

    py_parsers = {
        "slugify": [trd.tv_slugify(x) for x in ["trend following", "  Order   Blocks  ", "Elliott's Wave", "Elliott\u2019s Wave", "RSI/MACD combo", "   ", "!!!", None, ""]],
        "script_types": [trd.tv_normalize_script_type(x) for x in ["indicator", "indicators", "STRATEGY", "libraries", "all", "nonsense", "", None]],
        "pine_versions": [trd.tv_detect_pine_version(x) for x in ['//@version=5\nstudy("x")', "// @version = 6\n", "no pragma here", None]],
        "chart_ids": [trd.tv_extract_id_from_chart_url(x) for x in ["https://www.tradingview.com/script/K0SEi3Ct-TL-PbD/", "https://www.tradingview.com/script/abc123/", "nonsense", None]],
        "snippets": [
            trd.tv_snippet("a\n\n  b   c", 100),
            trd.tv_snippet("x" * 500, 10),
            trd.tv_snippet("hello   ", 10),
            trd.tv_snippet("", 10),
            trd.tv_snippet("1234567890", 10),
            trd.tv_snippet("12345678901", 10),
            trd.tv_snippet("ab\U0001F600", 4),
            trd.tv_snippet("ab\U0001F600c", 4),
        ],
        "listings": [trd.tv_to_listing(slug_gen["items"][0], 300), trd.tv_to_listing(long_item, 300)],
        "slug_general": slug_gen,
        "slug_editors": slug_ed,
        "slug_scalping": slug_scalp,
        "slug_invalid": _sc_ok(lambda: trd.tv_parse_slug_feed({"data": {}})),
        "author_feed": auth_parsed,
        "author_invalid": _sc_ok(lambda: trd.tv_parse_author_feed({"count": 3})),
        "facade_cases": [
            trd.tv_parse_facade(fac_open, script_id_part="PUB;abc"),
            trd.tv_parse_facade(fac_prot, script_id_part="PUB;xyz"),
            trd.tv_parse_facade(None),
            trd.tv_parse_facade({}),
            trd.tv_parse_facade({"source": 123}),
            trd.tv_parse_facade({"source": '//@version=4\nstrategy("s")', "extra": {"kind": "strategy", "is_price_study": False}, "lastVersionMaj": "3"}, script_id_part="PUB;s1"),
        ],
        "utc_days": [trd.tv_utc_day(1784973600000), trd.tv_utc_day(1785060000000), trd.tv_utc_day(0)],
    }
    assert py_parsers == oracle["m074"]["parsersOut"], "M074 parsers mismatch"

    store = trd.TradingViewIndicatorStore(":memory:")
    t_base = 1784973600000
    uc = store.upsert_scripts([
        {"script_id_part": "PUB;a", "name": "Supertrend Pro", "author": "alice", "script_type": "strategy", "likes": 100, "open_source": True, "script_access": 1, "description": "A trend following strategy"},
        {"script_id_part": "PUB;b", "name": "RSI Basic", "author": "bob", "script_type": "indicator", "likes": 10, "open_source": True, "script_access": 1, "description": "A mean reversion oscillator"},
    ], t_base)
    store.upsert_script({"script_id_part": "PUB;a", "name": "Supertrend Pro", "author": "alice", "script_type": "strategy", "likes": 120, "open_source": True, "script_access": 1, "description": "A trend following strategy"}, t_base + 1)
    store.put_source({"script_id_part": "PUB;a", "version": "1", "source": '//@version=5\nstrategy("x")\nta.supertrend(3, 10)', "pine_version": 5, "kind": "strategy", "script_name": "Supertrend Pro"}, t_base + 2)
    store.mark_protected("PUB;closed", t_base + 3)
    d1, d2 = 1784973600000, 1785060000000
    store.log_request(host="h", path="/a", status=200, ms=5, outcome="ok", now=d1)
    store.log_request(host="h", path="/b", status=200, ms=5, outcome="ok", now=d1)
    store.log_request(host="h", path="/c", status=200, ms=5, outcome="ok", now=d2)
    store.put_cached_search("k", "search", {"q": "supertrend"}, {"total": 1, "items": []}, 1_000_000)
    store.put_cookie_jar("h", "a=1; b=2", 1000)

    py_store = {
        "upsert_count": uc,
        "has_source_a": store.has_source("PUB;a"),
        "has_source_b": store.has_source("PUB;b"),
        "source_a_latest": (store.get_source("PUB;a") or {}).get("source"),
        "source_a_v1": (store.get_source("PUB;a", "1") or {}).get("source"),
        "source_missing": store.get_source("PUB;missing"),
        "closed_open_source": (store.get_script("PUB;closed") or {}).get("open_source"),
        "closed_access": (store.get_script("PUB;closed") or {}).get("script_access"),
        "req_day1": store.count_requests_today(d1),
        "req_day2": store.count_requests_today(d2),
        "cache_hit": store.get_cached_search("k", 5000, 1_001_000) is not None,
        "cache_eq_ttl": store.get_cached_search("k", 5000, 1_005_000) is not None,
        "cache_gt_ttl_by_1": store.get_cached_search("k", 5000, 1_005_001) is None,
        "cache_miss": store.get_cached_search("k", 5000, 1_009_000) is None,
        "cookie_hit": store.get_cookie_jar("h", 5000, 2000),
        "cookie_eq_age": store.get_cookie_jar("h", 5000, 6000),
        "cookie_gt_age_by_1": store.get_cookie_jar("h", 5000, 6001),
        "cookie_miss": store.get_cookie_jar("h", 500, 2000),
        "q_fts_name": [r["script_id_part"] for r in store.query_corpus(query="supertrend")],
        "q_fts_desc": [r["script_id_part"] for r in store.query_corpus(query="reversion")],
        "q_source_contains": [r["script_id_part"] for r in store.query_corpus(source_contains="ta.supertrend")],
        "q_type": [r["script_id_part"] for r in store.query_corpus(script_type="strategy")],
        "q_author": [r["script_id_part"] for r in store.query_corpus(author="ALICE")],
        "q_likes": [r["script_id_part"] for r in store.query_corpus(min_likes=50)],
        "q_likes_eq_10": [r["script_id_part"] for r in store.query_corpus(min_likes=10)],
        "q_likes_gt_10": [r["script_id_part"] for r in store.query_corpus(min_likes=11)],
        "q_likes_eq_120": [r["script_id_part"] for r in store.query_corpus(min_likes=120)],
        "q_likes_gt_120": [r["script_id_part"] for r in store.query_corpus(min_likes=121)],
        "q_likes_zero": [r["script_id_part"] for r in store.query_corpus(min_likes=0)],
        "q_with_source": [r["script_id_part"] for r in store.query_corpus(with_source_only=True)],
        "q_sorted_likes": [r["likes"] for r in store.query_corpus()],
    }
    store.close()
    assert py_store == oracle["m074"]["storeOut"], "M074 store mismatch"

    def _mk_th(overrides=None, **deps):
        st = {"now": 0}
        slept = []
        cfg = {
            "minDelayMs": 1000, "maxDelayMs": 3000, "breakEvery": 3,
            "breakMinMs": 20000, "breakMaxMs": 30000, "dailyBudget": 100,
            "breakerThreshold": 3, "breakerCooldownMs": 900000, **(overrides or {}),
        }
        def _adv(ms):
            st["now"] += ms
        def _slp(ms):
            slept.append(ms)
            st["now"] += ms
        return trd.TradingViewThrottle(cfg, now=lambda: st["now"], sleep=_slp, random_fn=lambda: 0.5, **deps), slept, _adv

    th1, sl1, adv1 = _mk_th()
    th1.run(lambda: "ok1")
    th1.run(lambda: "ok2")
    adv1(10_000)
    th1.run(lambda: "ok3")
    th1.run(lambda: "ok4")
    er1 = _sc_msg(lambda: th1.run(lambda: (_ for _ in ()).throw(RuntimeError("boom"))))
    aft = th1.run(lambda: "still works")

    th2, _, adv2 = _mk_th({"breakerThreshold": 3})
    b1 = [th2.note_blocked(), th2.note_blocked(), th2.note_blocked()]
    trp = _sc_msg(lambda: th2.run(lambda: "nope"))
    adv2(839_999)
    trp_m_60001 = _sc_msg(lambda: th2.run(lambda: "nope"))["msg"]
    adv2(1)
    trp_m_60000 = _sc_msg(lambda: th2.run(lambda: "nope"))["msg"]
    adv2(59_999)
    trp_open_899999 = _sc_msg(lambda: th2.run(lambda: "nope"))["ok"]
    adv2(1)
    reop = th2.run(lambda: "reopened")
    th2.note_blocked()
    th2.note_ok()
    sr = th2.note_blocked()

    th3, _, _ = _mk_th({"dailyBudget": 5}, count_today=lambda: 5)
    bden = _sc_msg(lambda: th3.run(lambda: "x"))
    th4, _, _ = _mk_th({"dailyBudget": 5}, count_today=lambda: 4)
    ball = _sc_msg(lambda: th4.run(lambda: "x"))

    jitter_b = []
    for mn, mx, rv in ((1000, 1001, 0.5), (1000, 1001, 0.75), (1000, 1001, 0.49), (1000, 1000, 0.9)):
        sj = {"now": 0}
        slj = []
        thj = trd.TradingViewThrottle(
            {**trd.DEFAULT_TRADINGVIEW_CONFIG, "minDelayMs": mn, "maxDelayMs": mx, "breakEvery": 0},
            now=lambda _s=sj: _s["now"],
            sleep=lambda ms, _sl=slj, _s=sj: (_sl.append(ms), _s.__setitem__("now", _s["now"] + ms))[0],
            random_fn=lambda _r=rv: _r,
        )
        thj.run(lambda: 1)
        thj.run(lambda: 2)
        jitter_b.append(slj[0])

    thw, slw, advw = _mk_th({"minDelayMs": 1000, "maxDelayMs": 1000, "breakEvery": 0})
    thw.run(lambda: 1)
    advw(1000)
    thw.run(lambda: 2)
    wait_exact = list(slw)
    advw(999)
    thw.run(lambda: 3)
    wait_below = list(slw)

    py_thr = {
        "slept": sl1,
        "err_msg": er1["msg"],
        "after_err": aft,
        "status1": th1.status(),
        "blocks1": b1,
        "trip_is_open": (not trp["ok"]) and ("circuit is OPEN" in trp["msg"]),
        "trip_msg_60001": trp_m_60001,
        "trip_msg_60000": trp_m_60000,
        "trip_still_open_899999": trp_open_899999,
        "reopened_ok": reop,
        "streak_reset": sr,
        "budget_denied": (not bden["ok"]) and ("Daily request budget of 5" in bden["msg"]),
        "budget_allowed": ball["val"],
        "jitter_boundaries": jitter_b,
        "wait_turn_at_exact_gap": wait_exact,
        "wait_turn_below_gap": wait_below,
    }
    assert py_thr == oracle["m074"]["throttleOut"], "M074 throttle mismatch"

    def _fake_http(routes):
        calls = []
        class _H:
            def get_json(self, url, **kw):
                calls.append(url)
                for pat, val in routes:
                    if pat in url:
                        if isinstance(val, Exception):
                            raise val
                        return copy.deepcopy(val(url) if callable(val) else val)
                raise RuntimeError(f"No route for {url}")
            def get_text(self, url, **kw):
                calls.append(url)
                return "<html>PUB;5bbd9e495f604c3682671a0e8920a188 and USER;747343354ba641a1973907f549b1cd10</html>"
        return calls, _H()

    cfg_t = {**trd.DEFAULT_TRADINGVIEW_CONFIG, "snippetChars": 120, "harvestMaxScripts": 200}
    def _build_ctx(routes):
        st = trd.TradingViewIndicatorStore(":memory:")
        th = trd.TradingViewThrottle(cfg_t, sleep=lambda _m: None, count_today=lambda: 0)
        calls, ht = _fake_http(routes)
        tv = trd.TradingViewClient(config=cfg_t, http=ht, store=st)
        tl = trd.create_tradingview_tools(config=cfg_t, tv=tv, store=st, throttle=th, http=ht)
        return st, calls, tv, tl

    st1, calls1, tv1, tl1 = _build_ctx([
        ("/api/v1/scripts/", auth_fix),
        ("editors-picks", ed_fix),
        ("/scripts/", lambda url: gen_fix if ("trend-following" in url and "page-3" in url) else scalp_fix),
        ("pine-facade", lambda url: fac_prot if "ba544ec71a3945549669f3babb981424" in url else fac_open),
    ])
    s1 = tl1["search_scripts"](query="trend following", script_type="strategy", sort="latest_popular")
    s2 = tl1["search_scripts"](query="trend following", script_type="strategy", sort="latest_popular")
    s_top = tl1["search_scripts"](query="trend following", script_type="strategies", page=3)
    s_ed = tl1["list_editors_picks"](script_type="indicator")
    s_auth = tl1["list_author_scripts"](username="TraderlifestyleYT")
    src_chart = tl1["get_script_source"](chart_url="https://www.tradingview.com/script/K0SEi3Ct-TL-PbD-Shape-Pro/")
    src_cache = tl1["get_script_source"](script_id_part="PUB;5bbd9e495f604c3682671a0e8920a188")
    src_prot = tl1["get_script_source"](script_id_part="PUB;ba544ec71a3945549669f3babb981424")
    src_prot2 = tl1["get_script_source"](script_id_part="PUB;ba544ec71a3945549669f3babb981424")
    q_wide = tl1["query_corpus"](query="Scalping", limit=50)
    q_deep = tl1["query_corpus"](limit=50, include_source=True)
    st_status = tl1["fetch_status"]()
    st1.close()

    scalp_p = copy.deepcopy(scalp_fix)
    scalp_p["data"]["ideas"]["data"]["items"][0]["script_access"] = 2
    scalp_p["data"]["ideas"]["data"]["items"][1]["script_access"] = 3
    st_p, _, tv_p, _ = _build_ctx([("/scripts/", scalp_p)])
    tv_p_res = tv_p.search_scripts(query="scalping")
    st_p.close()

    st_e, _, tv_e, tl_e = _build_ctx([
        ("/api/v1/scripts/", trd.TradingViewHttpError(400, "u", "")),
        ("/scripts/", trd.TradingViewHttpError(404, "u", "")),
    ])
    e404 = _sc_msg(lambda: tv_e.search_scripts(query="not a real topic"))
    e400 = _sc_msg(lambda: tv_e.author_scripts(username="baduser"))
    ebadt = _sc_msg(lambda: tv_e.search_scripts(query="x", script_type="nonsense"))
    ebadi = _sc_msg(lambda: tv_e.get_source(script_id_part="K0SEi3Ct"))
    eempt = _sc_msg(lambda: tl_e["get_script_source"]())
    st_e.close()

    st_h, _, _, tl_h = _build_ctx([
        ("/scripts/", lambda url: {"data": {"ideas": {"data": {"total": 0, "items": [], "next": None}}}, "meta": {"heading": "none"}} if "page-" in url else scalp_fix),
        ("pine-facade", fac_open),
    ])
    hr = tl_h["harvest_scripts"](query="scalping", max_scripts=5)
    ha = tl_h["harvest_scripts"](harvest_id=hr["harvest_id"])
    hu = _sc_msg(lambda: tl_h["harvest_scripts"](harvest_id="nope"))
    hna = _sc_msg(lambda: tl_h["harvest_scripts"](source="author"))
    st_h.close()

    def _norm_h(o):
        c = copy.deepcopy(o)
        if isinstance(c.get("harvest_id"), str):
            c["harvest_id"] = "<HARVEST_ID>"
        return c

    fix999 = copy.deepcopy(scalp_fix)
    fix999["data"]["ideas"]["data"]["total"] = 999
    fix1000 = copy.deepcopy(scalp_fix)
    fix1000["data"]["ideas"]["data"]["total"] = 1000
    st_b, calls_b, tv_b, tl_b = _build_ctx([
        ("/api/v1/scripts/", auth_fix),
        ("/scripts/topic-999/", fix999),
        ("/scripts/topic-1000/", fix1000),
    ])
    tv_b.author_scripts(username="U", query="q0", per_page=0)
    tv_b.author_scripts(username="U", query="q1", per_page=1)
    tv_b.author_scripts(username="U", query="q24", per_page=24)
    tv_b.author_scripts(username="U", query="q25", per_page=25)
    s999 = tl_b["search_scripts"](query="topic 999")
    s1000 = tl_b["search_scripts"](query="topic 1000")
    st_b.close()

    st_q, _, _, tl_q = _build_ctx([])
    q_limits = [
        tl_q["query_corpus"](limit=3, include_source=True)["limit_applied"],
        tl_q["query_corpus"](limit=4, include_source=True)["limit_applied"],
        tl_q["query_corpus"](limit=100, include_source=False)["limit_applied"],
        tl_q["query_corpus"](limit=101, include_source=False)["limit_applied"],
    ]
    st_q.close()

    py_tools = {
        "calls_ctx1": calls1,
        "s1": s1, "s2": s2, "sTop": s_top, "sEd": s_ed, "sAuth": s_auth,
        "srcChart": src_chart, "srcCache": src_cache, "srcProt": src_prot, "srcProtAgain": src_prot2,
        "qWide": q_wide, "qDeep": q_deep,
        "stStatus_keys_and_corpus": {"corpus": st_status["corpus"], "pacing": st_status["pacing"], "throttle_budget": st_status["throttle"]["daily_budget"]},
        "filtered_protected_count": tv_p_res["filtered_protected"],
        "filtered_all_open": all(i["open_source"] for i in tv_p_res["items"]),
        "errors": {
            "slug404": "hyphenated" in e404["msg"],
            "user400": "rejected the username" in e400["msg"],
            "badType": "Unknown script_type" in ebadt["msg"],
            "badId": "not a script_id_part" in ebadi["msg"],
            "emptySrc": "script_id_part or chart_url" in eempt["msg"],
            "hUnknown": "Unknown harvest_id" in hu["msg"],
            "hNoAuthor": "requires a username" in hna["msg"],
        },
        "harvest_len_ok": isinstance(hr["harvest_id"], str) and len(hr["harvest_id"]) == 8,
        "hRes": _norm_h(hr),
        "hAgain": _norm_h(ha),
        "bound_calls": calls_b,
        "bound_notes": [s999.get("note"), s1000.get("note")],
        "bound_q_limits": q_limits,
    }
    assert py_tools == oracle["m074"]["toolsOut"], "M074 tools/TradingViewClient mismatch"
    return len(py_parsers) + len(py_store) + len(py_thr) + len(py_tools)


def verify_m001() -> int:
    import base64
    import io
    import os
    import struct
    import urllib.error
    import urllib.parse
    import urllib.request
    import zlib
    from unittest.mock import patch

    assert not (iso / "01_Forkable/FKB00_Runtime/00_A0_Core/a0-plugins").exists()
    cat_root = iso / "test_input_m001_catalog"

    def _make_exact_png(w: int, h: int, exact_bytes: int) -> bytes:
        buf = io.BytesIO()
        Image.new("RGB", (w, h), (10, 20, 30)).save(buf, format="PNG")
        raw = buf.getvalue()
        if exact_bytes <= len(raw):
            return raw
        pad_len = exact_bytes - len(raw) - 16
        assert pad_len >= 0
        payload = b"pad\x00" + (b"A" * pad_len)
        chunk = struct.pack(">I", len(payload)) + b"tEXt" + payload + struct.pack(">I", zlib.crc32(b"tEXt" + payload) & 0xFFFFFFFF)
        out = raw[:-12] + chunk + raw[-12:]
        assert len(out) == exact_bytes
        return out

    class _MockHttpResp:
        def __init__(self, body: bytes = b"", headers: dict | None = None) -> None:
            self._bio = io.BytesIO(body)
            self.headers = headers or {}

        def read(self, n: int = -1) -> bytes:
            return self._bio.read(n)

        def __enter__(self):
            return self

        def __exit__(self, *args):
            return False

    def _m001_mock_urlopen(req, timeout=30):
        u = urllib.parse.urlparse(req.full_url)
        method = req.get_method()
        if u.hostname == "api.github.com":
            if u.path == "/repos/org/alpha":
                return _MockHttpResp(json.dumps({"full_name": "org/alpha"}).encode("utf-8"))
            if u.path == "/repos/org/alpha/contents/plugin.yaml":
                b64 = base64.b64encode(b"name: alpha\nversion: 1.0.0\n").decode("ascii")
                return _MockHttpResp(json.dumps({"type": "file", "encoding": "base64", "content": b64}).encode("utf-8"))
            if u.path == "/repos/org/wrongname":
                return _MockHttpResp(json.dumps({"full_name": "org/wrongname"}).encode("utf-8"))
            if u.path == "/repos/org/wrongname/contents/plugin.yaml":
                b64 = base64.b64encode(b"name: other\nversion: 1.0.0\n").decode("ascii")
                return _MockHttpResp(json.dumps({"type": "file", "encoding": "base64", "content": b64}).encode("utf-8"))
            raise urllib.error.HTTPError(req.full_url, 404, "Not Found", {}, io.BytesIO(b"{}"))
        if method == "HEAD":
            if "range405" in u.path:
                raise urllib.error.HTTPError(req.full_url, 405, "Method Not Allowed", {}, io.BytesIO(b""))
            if "head_over" in u.path:
                return _MockHttpResp(b"", {"Content-Length": str(2 * 1024 * 1024 + 1)})
            return _MockHttpResp(b"", {"Content-Length": str(2 * 1024 * 1024)})
        if "get_over" in u.path:
            return _MockHttpResp(b"X" * (2 * 1024 * 1024 + 1))
        return _MockHttpResp(b"X" * (2 * 1024 * 1024))

    def _m001_req_json(url: str) -> dict:
        req = urllib.request.Request(url, method="GET")
        try:
            with _m001_mock_urlopen(req, timeout=30) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            raise reg.ValidatePluginSubmissionError(f"HTTP {exc.code}") from exc

    # 1) Resolution + boundaries
    all_cat_rel = [
        p.relative_to(cat_root).as_posix()
        for p in sorted((cat_root / "plugins").rglob("*"))
        if p.is_file()
    ]
    res_cases = []
    for env_dict, paths_arg, diff_arg, max_p in [
        ({}, all_cat_rel, None, 1000),
        ({"BEFORE_SHA": "0" * 40, "AFTER_SHA": "abc"}, ["plugins/a/index.yaml", "plugins/_res/index.yaml", "plugins/bad-dash/index.yaml"], None, 1000),
        ({"BEFORE_SHA": "111", "AFTER_SHA": "222"}, None, ["plugins/beta/index.yaml", "plugins/alpha/index.yaml", "authors/u/author.yaml"], 1000),
        ({"PLUGIN_NAMES": "zeta, _reserved_ok, bad-dash, alpha", "START_FROM": "0", "MAX_PLUGINS": "10"}, None, None, 10),
        ({"PLUGIN_NAMES": "alpha, beta, gamma", "START_FROM": "1", "MAX_PLUGINS": "10"}, None, None, 10),
        ({"PLUGIN_NAMES": "alpha, beta, gamma", "START_FROM": "2", "MAX_PLUGINS": "10"}, None, None, 10),
        ({"PLUGIN_NAMES": "alpha, beta, gamma", "START_FROM": "-1", "MAX_PLUGINS": "10"}, None, None, 10),
        ({"PLUGIN_NAMES": "alpha, beta, gamma", "START_FROM": "bad", "MAX_PLUGINS": "3"}, None, None, 3),
        ({"PLUGIN_NAMES": "alpha, beta, gamma, delta", "START_FROM": "0", "MAX_PLUGINS": "3"}, None, None, 3),
    ]:
        res_cases.append(
            _safe_call(
                reg.resolve_plugin_names,
                all_paths=paths_arg,
                diff_paths=diff_arg,
                plugin_names_env=env_dict.get("PLUGIN_NAMES", ""),
                before_sha=env_dict.get("BEFORE_SHA", ""),
                after_sha=env_dict.get("AFTER_SHA", ""),
                start_from=env_dict.get("START_FROM", ""),
                max_plugins=int(env_dict.get("MAX_PLUGINS", max_p)),
            )
        )
    assert reg.normalize_plugin_names(["alpha", "_res", "bad-dash"]) == ["alpha"]
    assert reg.normalize_plugin_names(["alpha", "_res"], allow_reserved=True) == ["_res", "alpha"]
    assert reg.is_reserved_plugin_dirname("_res") is True and reg.is_reserved_plugin_dirname("alpha") is False

    # 2) Validation & exact limits
    with tempfile.TemporaryDirectory(dir=str(iso), prefix="org_m001_val_") as vtmp:
        vroot = Path(vtmp)
        vpdir = vroot / "plugins"
        vpdir.mkdir()
        yaml_2000 = "title: Ok\ngithub: https://github.com/org/alpha\ndescription: " + ("d" * (2000 - len("title: Ok\ngithub: https://github.com/org/alpha\ndescription: ")))
        yaml_2001 = yaml_2000 + "x"
        png_20480 = _make_exact_png(8, 8, 20 * 1024)
        png_20481 = _make_exact_png(8, 8, 20 * 1024 + 1)
        png_rect = _make_exact_png(16, 12, 200)
        for sub_n, files_map in [
            ("t_exact_20kb", {"index.yaml": "title: T\n", "thumbnail.png": png_20480}),
            ("t_over_20kb", {"index.yaml": "title: T\n", "thumbnail.png": png_20481}),
            ("t_non_square", {"index.yaml": "title: T\n", "thumbnail.png": png_rect}),
            ("t_two_thumbs", {"index.yaml": "title: T\n", "thumbnail.png": png_20480, "thumbnail.jpg": png_20480}),
            ("t_none", {"index.yaml": "title: T\n"}),
            ("f_extra", {"index.yaml": "title: T\n", "thumbnail.png": png_20480, "README.md": b"bad"}),
        ]:
            dp = vpdir / sub_n
            dp.mkdir()
            for fn, content in files_map.items():
                if isinstance(content, bytes):
                    (dp / fn).write_bytes(content)
                else:
                    (dp / fn).write_text(content, encoding="utf-8")

        yaml_texts = {"y_2000": yaml_2000, "y_2001": yaml_2001, "y_bad": ":\n  - [unclosed", "y_list": "- a\n- b\n"}
        base_meta = {"title": "Alpha", "description": "Valid", "github": "https://github.com/org/alpha"}
        field_cases = [
            ("valid_full", {**base_meta, "tags": ["a", "b", "c", "d", "e"], "screenshots": [f"https://example.com/s{i}.png" for i in range(5)]}),
            ("unknown_field", {**base_meta, "extra": "nope"}),
            ("missing_req", {"title": "Only"}),
            ("title_50_ok", {**base_meta, "title": "T" * 50}),
            ("title_51_fail", {**base_meta, "title": "T" * 51}),
            ("desc_500_ok", {**base_meta, "description": "D" * 500}),
            ("desc_501_fail", {**base_meta, "description": "D" * 501}),
            ("tags_5_ok", {**base_meta, "tags": ["t1", "t2", "t3", "t4", "t5"]}),
            ("tags_6_fail", {**base_meta, "tags": ["t1", "t2", "t3", "t4", "t5", "t6"]}),
            ("shots_5_ok", {**base_meta, "screenshots": [f"https://example.com/ok{i}.png" for i in range(5)]}),
            ("shots_6_fail", {**base_meta, "screenshots": [f"https://example.com/ok{i}.png" for i in range(6)]}),
            ("shot_head_over", {**base_meta, "screenshots": ["https://example.com/head_over.png"]}),
            ("shot_range_ok", {**base_meta, "screenshots": ["https://example.com/range405_ok.png"]}),
            ("shot_range_over", {**base_meta, "screenshots": ["https://example.com/range405_get_over.png"]}),
            ("shot_bad_ext", {**base_meta, "screenshots": ["https://example.com/a.gif"]}),
            ("repo_404", {**base_meta, "github": "https://github.com/org/missing"}),
            ("repo_wrong_name", {**base_meta, "github": "https://github.com/org/wrongname"}),
        ]
        # Direct screenshot & repo sanity calls to ensure zero unexercised helpers
        reg.validate_github_repo(base_meta["github"], "alpha", request_json_fn=_m001_req_json)
        reg.validate_screenshot_url("https://example.com/ok0.png", opener=_m001_mock_urlopen)

        dup_index = {"other_p": {"github": "https://github.com/org/repo"}}
        val_out = {
            "urls": [
                [reg.parse_repo_url(u), reg.normalize_repo_url(u), reg.repo_owner_from_url(u)]
                for u in ["https://github.com/Org/Repo.git", "http://github.com/o/r/", "https://gitlab.com/o/r", "bad"]
            ],
            "yaml_strict": [_safe_call(reg.read_plugin_yaml_text_strict, yaml_texts[yn]) for yn in ("y_2000", "y_2001", "y_bad", "y_list")],
            "fields": [
                (lbl, _safe_call(reg.validate_fields, m, "alpha", request_json_fn=_m001_req_json, opener=_m001_mock_urlopen))
                for lbl, m in field_cases
            ],
            "thumbs": [(sn, _safe_call(reg.validate_thumbnail, vpdir / sn)) for sn in ("t_exact_20kb", "t_over_20kb", "t_non_square", "t_two_thumbs", "t_none")],
            "allowed_files": [(sn, _safe_call(reg.validate_allowed_files, vpdir / sn)) for sn in ("t_exact_20kb", "f_extra")],
            "remote_names": [
                _safe_call(reg.validate_remote_plugin_name, {"encoding": "base64", "content": base64.b64encode(b"name: alpha\n").decode()}, "alpha"),
                _safe_call(reg.validate_remote_plugin_name, {"encoding": "base64", "content": base64.b64encode(b"name: beta\n").decode()}, "alpha"),
                _safe_call(reg.validate_remote_plugin_name, {"encoding": "bad", "content": "x"}, "alpha"),
            ],
            "submissions": [
                _safe_call(reg.submission_plugin_name, ["plugins/my_plugin/index.yaml"]),
                _safe_call(reg.submission_plugin_name, ["README.md"]),
                _safe_call(reg.submission_plugin_name, ["plugins/bad-name/index.yaml"]),
                _safe_call(reg.submission_plugin_name, ["plugins/a/index.yaml", "plugins/b/index.yaml"]),
            ],
            "is_deletion": [
                reg.is_deletion_pr([("D", ["plugins/a/index.yaml"])], "a"),
                reg.is_deletion_pr([("M", ["plugins/a/index.yaml"])], "a"),
            ],
            "dup_repo_checks": [
                _safe_call(reg.validate_github_repo_not_in_index, "new_p", "https://github.com/ORG/REPO.git", dup_index),
                _safe_call(reg.validate_github_repo_not_in_index, "other_p", "https://github.com/ORG/REPO.git", dup_index),
                _safe_call(reg.validate_github_repo_not_in_index, "new_p", "https://github.com/org/fresh", dup_index),
            ],
        }

    # 3) Full 235-folder catalog compilation + upsert/remove/discussion
    compiled_index = reg.compile_catalog_index(cat_root, owner="Amdkn", repo="a0-plugins", ref="main")
    idx_state = {"version": 1, "plugins": {"alpha": {"stars": 42, "version": "1.2.3", "commit": "abc", "updated": "2026-01-01"}}}
    reg.upsert_index_plugin(idx_state, "alpha", {"title": "Alpha", "github": "https://github.com/u/r"})
    upsert_preserve = copy.deepcopy(idx_state["plugins"]["alpha"])
    removed_ok = reg.remove_index_plugin(idx_state, "alpha")
    removed_miss = reg.remove_index_plugin(idx_state, "missing")
    disc_tmpl = (cat_root / "plugin_discussion_template.md").read_text(encoding="utf-8")
    disc_body = reg.render_discussion_body("alpha", base_meta, "Amdkn", "a0-plugins", disc_tmpl)

    # 4) Orphans + Stars
    sync_copy = copy.deepcopy(compiled_index)
    existing_real = next(iter(sync_copy["plugins"]))
    sync_copy["plugins"]["deleted_ok"] = {"discussion": "https://github.com/Amdkn/a0-plugins/discussions/deleted_ok"}
    sync_copy["plugins"]["_example1"] = {"discussion": ""}
    sync_copy["plugins"]["bad-name"] = {"discussion": ""}
    orph_list = reg.find_orphan_names(sync_copy, cat_root / "plugins", discussion_marker_names=("ghost_plugin", existing_real))
    marker_cases = [
        reg.discussion_marker_name("<!-- a0-plugins-discussion -->\n<!-- a0-plugins-plugin:my_mod -->\n"),
        reg.discussion_marker_name("no marker here"),
        reg.discussion_marker_name("<!-- a0-plugins-plugin:   -->"),
    ]
    stars_idx = {"version": 1, "plugins": {"b": {"stars": 1}, "a": {"stars": 2}}}
    stars_upd = {"a": {"stars": 0, "version": "2.0.0", "commit": "def", "updated": "2026-11-20"}, "gone": {"stars": 9}}
    assert reg.apply_star_updates(stars_idx, stars_upd) == 1
    stars_out = {
        "chunks": [reg.chunks([1, 2, 3], 3), reg.chunks([1, 2, 3, 4], 3), reg.chunks([], 3)],
        "alias_errors": reg.extract_alias_errors({"errors": [{"path": ["r0", "sub"], "message": " Could not resolve "}]}),
        "versions": [reg.extract_plugin_version("name: x\nversion: '1.2.3' # comment\n"), reg.extract_plugin_version("name: x\n")],
        "commits": [reg.extract_commit_info({"defaultBranchRef": {"target": {"oid": "abc", "committedDate": "2026-01-01"}}}), reg.extract_commit_info({})],
        "applied": stars_idx,
    }

    # 5) 11 Release publish/download scenarios
    REL_OLD = b'{"version":1,"plugins":{"kept":{},"removed":{}}}'
    REL_NEW = b'{"version":1,"plugins":{"kept":{}}}'
    rel_scenarios = [
        ({"index.json": REL_OLD}, "", REL_NEW),
        ({"index.json": REL_OLD}, "rename_502", REL_NEW),
        ({"index.json": REL_OLD}, "rename_502_twice", REL_NEW),
        ({"index.json": REL_OLD}, "upload_failure", REL_NEW),
        ({"index.json.next": b"", "index.json.previous": REL_OLD}, "upload_failure_empty_next", REL_NEW),
        ({"index.json": REL_OLD}, "incomplete_upload", REL_NEW),
        ({"index.json": REL_OLD}, "promotion_failure", REL_NEW),
        ({"index.json": REL_OLD, "index.json.previous": REL_OLD}, "delete_502", REL_NEW),
        ({"index.json.next": REL_NEW, "index.json.previous": REL_OLD}, "", REL_NEW),
        ({"index.json.previous": REL_OLD}, "", REL_NEW),
        ({}, "", REL_NEW),
        ({"index.json": REL_OLD}, "invalid_index", b'{"error":"Not Found"}'),
        ({"index.json": REL_OLD}, "invalid_index", b'{"plugins":{}}'),
    ]

    def _run_rel_scenario(initial, fault, content):
        assets, contents, faults, mutations = {}, {}, [], []
        serial = [0]

        def _add(name, data):
            serial[0] += 1
            a = {"id": serial[0], "name": name, "state": "uploaded", "size": len(data)}
            assets[serial[0]] = a
            contents[serial[0]] = data
            return a

        for k, v in initial.items():
            _add(k, v)

        def _err(req, code):
            raise urllib.error.HTTPError(req.full_url, code, "Injected", {}, io.BytesIO(b"{}"))

        def _req(request, timeout=30):
            u = urllib.parse.urlparse(request.full_url)
            m = request.get_method()
            if m != "GET":
                mutations.append(m)
            if u.hostname == "download.test":
                return io.BytesIO(contents[int(u.path.strip("/"))] if u.query else REL_OLD)
            if "/releases/assets/" in u.path:
                aid = int(u.path.rsplit("/", 1)[1])
                if aid not in assets:
                    _err(request, 404)
                asset = assets[aid]
                if m == "DELETE":
                    del assets[aid]
                    del contents[aid]
                    if fault == "delete_502" and not faults:
                        faults.append(fault)
                        _err(request, 502)
                    return io.BytesIO()
                if m == "PATCH":
                    nm = json.loads(request.data)["name"]
                    if fault == "promotion_failure" and asset["name"] == "index.json.next":
                        faults.append(fault)
                        _err(request, 502)
                    if fault == "rename_502_twice" and len(faults) < 2:
                        faults.append(fault)
                        _err(request, 502)
                    asset["name"] = nm
                    if fault == "rename_502" and not faults:
                        faults.append(fault)
                        _err(request, 502)
                return io.BytesIO(json.dumps(asset).encode())
            if m == "POST" and u.hostname == "uploads.github.com":
                if fault in ("upload_failure", "upload_failure_empty_next"):
                    faults.append(fault)
                    _err(request, 502)
                a = _add(urllib.parse.parse_qs(u.query)["name"][0], request.data)
                if fault == "incomplete_upload":
                    faults.append(fault)
                    a["state"] = "starter"
                return io.BytesIO(json.dumps(a).encode())
            return io.BytesIO(json.dumps({
                "id": 1,
                "upload_url": "https://uploads.github.com/repos/test/repo/releases/1/assets{?name,label}",
                "assets": [dict(a, browser_download_url=f"https://download.test/{a['id']}") for a in assets.values()],
            }).encode())

        with tempfile.TemporaryDirectory() as d:
            idx_p = Path(d) / "index.json"
            dl1 = None
            if initial and fault != "upload_failure_empty_next" and reg.download_index_release(idx_p, owner="test", repo="repo", token="test", opener=_req, sleep_fn=lambda _s: None) == 0:
                dl1 = idx_p.read_bytes().decode("utf-8")
            idx_p.write_bytes(content)
            failed = False
            try:
                reg.publish_index_release(idx_p, owner="test", repo="repo", token="test", opener=_req, sleep_fn=lambda _s: None)
            except reg.PublishReleaseError:
                failed = True
            cur = next(a for a in assets.values() if a["name"] == "index.json")
            dl2 = None
            if not failed:
                reg.download_index_release(idx_p, owner="test", repo="repo", token="test", opener=_req, sleep_fn=lambda _s: None)
                dl2 = idx_p.read_bytes().decode("utf-8")
            return {"dl1": dl1, "failed": failed, "cur": contents[cur["id"]].decode("utf-8"), "dl2": dl2, "mutations": len(mutations)}

    rel_out = [_run_rel_scenario(ini, flt, cnt) for ini, flt, cnt in rel_scenarios]

    dl_retry_seqs = [[499], [500, 500, 200], [500, 500, 500], [429, 429, 200], ["net_err", "net_err", 200]]

    def _run_dl_retry(seq):
        attempts = [0]
        sleeps = []

        def _dl_req(request, timeout=30):
            u = urllib.parse.urlparse(request.full_url)
            if u.hostname == "download.test":
                attempts[0] += 1
                ev = seq[attempts[0] - 1]
                if ev == 200:
                    return io.BytesIO(REL_NEW)
                if ev == "net_err":
                    raise OSError("injected connection reset")
                raise urllib.error.HTTPError(request.full_url, ev, "Injected", {}, io.BytesIO(b"err"))
            return io.BytesIO(json.dumps({
                "id": 1,
                "assets": [{
                    "id": 1,
                    "name": "index.json",
                    "state": "uploaded",
                    "size": len(REL_NEW),
                    "browser_download_url": "https://download.test/1",
                }],
            }).encode())

        with tempfile.TemporaryDirectory() as d:
            idx_p = Path(d) / "index.json"
            ok = False
            try:
                ok = reg.download_index_release(
                    idx_p,
                    owner="test",
                    repo="repo",
                    token="test",
                    opener=_dl_req,
                    sleep_fn=lambda s: sleeps.append(s),
                ) == 0
            except reg.DownloadIndexError:
                ok = False
            return {
                "ok": ok,
                "attempts": attempts[0],
                "sleeps": list(sleeps),
                "body": idx_p.read_bytes().decode("utf-8") if ok else None,
            }

    dl_retry_out = [_run_dl_retry(s) for s in dl_retry_seqs]

    # 6) Adapter audit counts (real 235 dirs)
    audit_keys = (
        "plugin_dirs_total", "plugin_names_resolved", "indexed_plugins", "index_yaml_present",
        "legacy_plugin_yaml_only", "blocked_plugins", "index_yaml_invalid", "index_yaml_missing_keys",
        "max_screenshots", "generated_thumbnails", "orphan_thumbnails", "local_thumbnails",
        "plugins_without_any_thumbnail", "abandoned_present", "surfaces_present", "index_coherent",
    )
    adp_py = reg.audit_plugin_catalog(cat_root)

    py_m001 = json.loads(json.dumps({
        "resolution": res_cases,
        "validation": val_out,
        "compiled_index": compiled_index,
        "upsert_preserve": upsert_preserve,
        "upsert_preserved_check": {
            "removed_ok": removed_ok,
            "removed_miss": removed_miss,
            "discussion_body": disc_body,
        },
        "orphans": {"markers": marker_cases, "list": orph_list},
        "stars": stars_out,
        "releases": rel_out,
        "dl_retries": dl_retry_out,
        "audit": {k: adp_py[k] for k in audit_keys},
    }))
    for sec in ("resolution", "validation", "compiled_index", "upsert_preserve", "upsert_preserved_check", "orphans", "stars", "releases", "dl_retries", "audit"):
        assert py_m001[sec] == oracle["m001"][sec], f"M001 section mismatch: {sec}"
    return (
        len(res_cases)
        + sum(len(v) for v in val_out.values())
        + len(compiled_index["plugins"])
        + len(rel_out)
        + len(dl_retry_out)
        + len(audit_keys)
    )


def verify_all() -> dict[str, int]:
    return {
        "a0-plugins": verify_m001(),
        "context-language-models": verify_m044(),
        "knowledge-catalog": verify_m050(),
        "CLI-Anything": verify_m056(),
        "tradingview-indicator-search-mcp-server": verify_m074(),
        "video-director": verify_m084(),
        "00_Marketplace_YoutubeSkills": verify_m117(),
        "04_Inference_Youtube_Discovery_Registry": verify_m118(),
    }


def run_sabotage_suite() -> int:
    """Sabote chaque fonction/donnée déclarée des 8 modules différentiels et vérifie que verify_all() échoue systématiquement."""
    def _assert_breaks(name: str, check_fn, patch_target_mod, attr: str, fake_val):
        orig = getattr(patch_target_mod, attr)
        setattr(patch_target_mod, attr, fake_val)
        broke = False
        try:
            check_fn()
        except Exception:
            broke = True
        finally:
            setattr(patch_target_mod, attr, orig)
        assert broke, f"SABOTAGE NON DÉTECTÉ : {name} ({attr})!"

    _orig_clm_may_grow = f02.clm_may_grow
    _orig_clm_normalize = f02._clm_normalize
    _orig_okf_is_stale = f02.okf_is_stale
    _orig_cli_meta = f04.extract_cli_anything_metadata
    _orig_qualify_m118 = cat.qualify_inference_opportunity
    _orig_tv_cached = trd.TradingViewIndicatorStore.get_cached_search
    _orig_tv_cookie = trd.TradingViewIndicatorStore.get_cookie_jar
    _orig_tv_qc = trd.TradingViewIndicatorStore.query_corpus
    _orig_tv_note_blocked = trd.TradingViewThrottle.note_blocked
    _orig_tv_thr_run = trd.TradingViewThrottle.run

    def _bad_clm_norm_ge(msgs, protect):
        kept = [m for i, m in enumerate(msgs) if i < protect or (f02.clm_content_text(m.get("content")) or "").strip()]
        merged = []
        for i, m in enumerate(kept):
            if merged and i >= protect and len(merged) >= protect and m.get("role") in ("user", "assistant") and merged[-1].get("role") == m.get("role"):
                prev = f02.clm_content_text(merged[-1].get("content")) or ""
                cur = f02.clm_content_text(m.get("content")) or ""
                merged[-1] = {"role": m["role"], "content": (prev + "\n\n" + cur).strip()}
            else:
                merged.append(m)
        return merged

    def _bad_cli_meta_ge100(hp):
        m = _orig_cli_meta(hp)
        if len(m.skill_intro) == 100 and not m.skill_description.endswith("..."):
            m.skill_description = m.skill_description + "..."
        return m

    def _bad_compare_cuts_ge(det, exp, fps):
        if not exp:
            return None
        errs, missing = [], []
        for t in exp:
            if not det:
                missing.append(t)
                continue
            near = min(det, key=lambda c: abs(c - t))
            if abs(near - t) >= 0.5:
                missing.append(t)
            else:
                errs.append(round((near - t) * fps, 2))
        unplanned = [c for c in det if all(abs(c - t) >= 0.5 for t in exp)]
        return {"max_err_frames": max((abs(e) for e in errs), default=0.0), "errors_frames": errs, "missing": missing, "unplanned": unplanned}

    def _bad_m118_ttl_le7(cand, known_platforms=None):
        res = _orig_qualify_m118(cand, known_platforms=known_platforms)
        if res.get("authentic") and int(cand.get("estimated_ttl_days", 14)) == 7:
            res["durability"] = "FLASH"
        return res

    def _bad_m118_ttl_gt30(cand, known_platforms=None):
        res = _orig_qualify_m118(cand, known_platforms=known_platforms)
        if res.get("authentic") and int(cand.get("estimated_ttl_days", 14)) == 30:
            res["durability"] = "MEDIUM"
        return res

    def _bad_note_blocked_gt(self):
        self._consecutive_blocks += 1
        if self._consecutive_blocks > self.config["breakerThreshold"]:
            self._open_until = self.now() + self.config["breakerCooldownMs"]
            self._consecutive_blocks = 0
            return True
        return False

    def _bad_thr_run_budget_gt(self, fn):
        if self.is_open:
            raise trd.CircuitOpenError(self._open_until - self.now())
        if self.count_today() > self.config["dailyBudget"]:
            raise trd.BudgetExceededError(self.config["dailyBudget"])
        self._wait_turn()
        return fn()

    # Sabotages de fonctions + bornes exactes et arrondis
    sabotages = [
        # M044 (toutes les fonctions déclarées + bornes <= vs < et > protect)
        ("M044:clm_content_text", verify_m044, f02, "clm_content_text", lambda c: "SABOTAGED"),
        ("M044:clm_rendered_text", verify_m044, f02, "clm_rendered_text", lambda m: "SABOTAGED_RENDERED"),
        ("M044:clm_render_editable", verify_m044, f02, "clm_render_editable", lambda ms, protect=2: "BROKEN"),
        ("M044:clm_parse_back", verify_m044, f02, "clm_parse_back", lambda ed, prot: []),
        ("M044:_clm_normalize", verify_m044, f02, "_clm_normalize", lambda ms, protect: ms),
        ("M044:_clm_normalize_ge_protect", verify_m044, f02, "_clm_normalize", _bad_clm_norm_ge),
        ("M044:clm_resolve_allow_edit_growth", verify_m044, f02, "clm_resolve_allow_edit_growth", lambda p, env=None: True),
        ("M044:clm_fit_rule", verify_m044, f02, "clm_fit_rule", lambda lim: "broken"),
        ("M044:clm_may_grow", verify_m044, f02, "clm_may_grow", lambda **kw: False),
        ("M044:clm_may_grow_lt_boundary", verify_m044, f02, "clm_may_grow", lambda *, allow_growth, limit, after: _orig_clm_may_grow(allow_growth=allow_growth, limit=max(0, limit - 1), after=after)),
        ("M044:clm_reject_rule", verify_m044, f02, "clm_reject_rule", lambda **kw: "broken"),
        ("M044:clm_rejected_note", verify_m044, f02, "clm_rejected_note", lambda **kw: "broken"),
        ("M044:CLMFinishPolicy", verify_m044, f02, "CLMFinishPolicy", type("BadFP", (), {"__init__": lambda self, m="submit": None, "mode": "submit", "open_ended": False, "prompt_fragment": lambda s: "", "is_finish_command": lambda s, c: False})),
        ("M044:clm_is_submit_command", verify_m044, f02, "clm_is_submit_command", lambda c: False),
        ("M044:clm_token_cap_key", verify_m044, f02, "clm_token_cap_key", lambda m: "max_tokens"),
        # M050 (toutes les fonctions déclarées + inversion okf_is_stale + borne == vs >)
        ("M050:OKFDocument.validate", verify_m050, f02.OKFDocument, "validate", lambda self: None),
        ("M050:okf_normalize_verified", verify_m050, f02, "okf_normalize_verified", lambda fm: []),
        ("M050:okf_trust_tier", verify_m050, f02, "okf_trust_tier", lambda fm: "unverified"),
        ("M050:okf_is_stale_inverted", verify_m050, f02, "okf_is_stale", lambda fm, now=None, _orig=_orig_okf_is_stale: not _orig(fm, now=now)),
        ("M050:okf_is_stale_gt_boundary", verify_m050, f02, "okf_is_stale", lambda fm, now=None, _orig=_orig_okf_is_stale: _orig(fm, now=(now - dt.timedelta(microseconds=1)) if now else None)),
        ("M050:okf_synthesize_fallback", verify_m050, f02, "okf_synthesize_fallback", lambda r, c, model="": "sabotaged"),
        ("M050:okf_regenerate_indexes", verify_m050, f02, "okf_regenerate_indexes", lambda br, **kw: []),
        ("M050:okf_concept_id_to_path", verify_m050, f02, "okf_concept_id_to_path", lambda br, cid: Path("/bad.md")),
        ("M050:okf_path_to_concept_id", verify_m050, f02, "okf_path_to_concept_id", lambda br, p: ("bad",)),
        ("M050:okf_parse_concept_id", verify_m050, f02, "okf_parse_concept_id", lambda s: ("bad",)),
        # M056 (toutes les fonctions déclarées + borne 100 chars)
        ("M056:extract_commands_from_cli", verify_m056, f04, "extract_commands_from_cli", lambda p: []),
        ("M056:extract_cli_anything_metadata", verify_m056, f04, "extract_cli_anything_metadata", lambda p: None),
        ("M056:extract_meta_intro_ge_100", verify_m056, f04, "extract_cli_anything_metadata", _bad_cli_meta_ge100),
        ("M056:generate_cli_anything_skill_md", verify_m056, f04, "generate_cli_anything_skill_md", lambda m, template_text=None: "BAD"),
        ("M056:generate_cli_anything_skill_md_simple", verify_m056, f04, "generate_cli_anything_skill_md_simple", lambda m: "BAD"),
        ("M056:build_cli_anything_preview_cache_key", verify_m056, f04, "build_cli_anything_preview_cache_key", lambda *a, **kw: "sha256:0000"),
        # M084 (toutes les fonctions déclarées + bornes compare_cuts & read_time)
        ("M084:vd_is_num", verify_m084, vsf, "vd_is_num", lambda v: False),
        ("M084:vd_norm", verify_m084, vsf, "vd_norm", lambda s: ""),
        ("M084:vd_read_time", verify_m084, vsf, "vd_read_time", lambda t: 0.0),
        ("M084:vd_read_time_wrong_floor", verify_m084, vsf, "vd_read_time", lambda t: max(1.65, 1.0 + 0.3 * len(str(t).split()))),
        ("M084:vd_validate_timeline", verify_m084, vsf, "vd_validate_timeline", lambda tl: ([], [])),
        ("M084:vd_check_timeline_cli", verify_m084, vsf, "vd_check_timeline_cli", lambda argv: (0, "")),
        ("M084:vd_runs", verify_m084, vsf, "vd_runs", lambda mask: []),
        ("M084:vd_analyse_picture", verify_m084, vsf, "vd_analyse_picture", lambda st, fps, args: {}),
        ("M084:vd_compare_cuts", verify_m084, vsf, "vd_compare_cuts", lambda d, e, f: None),
        ("M084:vd_compare_cuts_ge_half", verify_m084, vsf, "vd_compare_cuts", _bad_compare_cuts_ge),
        ("M084:vd_measure_text", verify_m084, vsf, "vd_measure_text", lambda im, b, s: {"font_px": 0.0, "contrast": 1.0}),
        ("M084:vd_beat_times", verify_m084, vsf, "vd_beat_times", lambda tl: {}),
        ("M084:vd_load_timeline", verify_m084, vsf, "vd_load_timeline", lambda p: {}),
        # M117
        ("M117:get_marketplace_playbook", verify_m117, cat, "get_marketplace_playbook", lambda c: {}),
        ("M117:query_marketplace_skills", verify_m117, cat, "query_marketplace_skills", lambda **kw: {"matches": [], "playbooks": {}, "productized_offers": []}),
        # M118 + bornes TTL 7 / 30
        ("M118:get_opportunity_dossier", verify_m118, cat, "get_opportunity_dossier", lambda o: {}),
        ("M118:qualify_inference_opportunity", verify_m118, cat, "qualify_inference_opportunity", lambda c, known_platforms=None: {}),
        ("M118:qualify_ttl_le_7", verify_m118, cat, "qualify_inference_opportunity", _bad_m118_ttl_le7),
        ("M118:qualify_ttl_gt_30", verify_m118, cat, "qualify_inference_opportunity", _bad_m118_ttl_gt30),
        # M074 (toutes fonctions + bornes >/>=/<= + arrondis Math.round & banker + émoji UTF-16 + clé parasite)
        ("M074:tv_slugify", verify_m074, trd, "tv_slugify", lambda q: "broken-slug"),
        ("M074:tv_normalize_item", verify_m074, trd, "tv_normalize_item", lambda r: {"script_id_part": None}),
        ("M074:tv_parse_slug_feed", verify_m074, trd, "tv_parse_slug_feed", lambda p: {"total": 0, "has_more": False, "next_path": None, "heading": None, "items": []}),
        ("M074:tv_parse_author_feed", verify_m074, trd, "tv_parse_author_feed", lambda p: {"total": 0, "page_count": 1, "has_more": False, "next_path": None, "items": []}),
        ("M074:tv_parse_facade", verify_m074, trd, "tv_parse_facade", lambda p, **kw: {"ok": False, "protected": True, "reason": "sabotaged", "script_id_part": None}),
        ("M074:tv_detect_pine_version", verify_m074, trd, "tv_detect_pine_version", lambda s: None),
        ("M074:tv_extract_id_from_chart_url", verify_m074, trd, "tv_extract_id_from_chart_url", lambda u: None),
        ("M074:tv_snippet", verify_m074, trd, "tv_snippet", lambda t, m: "SABOTAGED"),
        ("M074:_js_slice_utf16", verify_m074, trd, "_js_slice", lambda t, e: t[:e]),
        ("M074:tv_to_listing", verify_m074, trd, "tv_to_listing", lambda i, n: {}),
        ("M074:tv_to_listing_extra_key", verify_m074, trd, "tv_to_listing", lambda i, n, _o=trd.tv_to_listing: {**_o(i, n), "extra_parasite_key": "must_fail"}),
        ("M074:tv_normalize_script_type", verify_m074, trd, "tv_normalize_script_type", lambda t: None),
        ("M074:tv_utc_day", verify_m074, trd, "tv_utc_day", lambda ts=None: "1999-01-01"),
        ("M074:Store.query_corpus", verify_m074, trd.TradingViewIndicatorStore, "query_corpus", lambda self, **kw: []),
        ("M074:Store.query_corpus_min_likes_gt", verify_m074, trd.TradingViewIndicatorStore, "query_corpus", lambda self, _orig=_orig_tv_qc, **kw: _orig(self, **{**kw, "min_likes": int(kw["min_likes"]) + 1}) if int(kw.get("min_likes") or 0) > 0 else _orig(self, **kw)),
        ("M074:Store.mark_protected", verify_m074, trd.TradingViewIndicatorStore, "mark_protected", lambda self, sid, now=None: None),
        ("M074:Store.get_cached_search", verify_m074, trd.TradingViewIndicatorStore, "get_cached_search", lambda self, k, ttl, now=None: None),
        ("M074:Store.get_cached_search_ge", verify_m074, trd.TradingViewIndicatorStore, "get_cached_search", lambda self, k, ttl, now=None, _orig=_orig_tv_cached: _orig(self, k, ttl - 1, now=now)),
        ("M074:Store.get_cookie_jar_ge", verify_m074, trd.TradingViewIndicatorStore, "get_cookie_jar", lambda self, h, max_age, now=None, _orig=_orig_tv_cookie: _orig(self, h, max_age - 1, now=now)),
        ("M074:Throttle._jitter_floor", verify_m074, trd.TradingViewThrottle, "_jitter", lambda self, mn, mx: mn if mx <= mn else int(trd.math.floor(mn + self.random_fn() * (mx - mn)))),
        ("M074:Throttle._jitter_bankers_round", verify_m074, trd.TradingViewThrottle, "_jitter", lambda self, mn, mx: mn if mx <= mn else int(round(mn + self.random_fn() * (mx - mn)))),
        ("M074:Throttle.note_blocked", verify_m074, trd.TradingViewThrottle, "note_blocked", lambda self: False),
        ("M074:Throttle.note_blocked_gt", verify_m074, trd.TradingViewThrottle, "note_blocked", _bad_note_blocked_gt),
        ("M074:Throttle.run", verify_m074, trd.TradingViewThrottle, "run", lambda self, fn: "sabotaged"),
        ("M074:Throttle.run_budget_gt", verify_m074, trd.TradingViewThrottle, "run", _bad_thr_run_budget_gt),
        ("M074:Throttle.is_open_le", verify_m074, trd.TradingViewThrottle, "is_open", property(lambda self: self.now() <= self._open_until)),
        ("M074:TradingViewClient.get_source", verify_m074, trd.TradingViewClient, "get_source", lambda self, **kw: {"ok": False, "protected": True, "reason": "sabotaged", "script_id_part": None}),
        ("M074:create_tradingview_tools", verify_m074, trd, "create_tradingview_tools", lambda **kw: {k: (lambda *_a, **_kw: {}) for k in ("search_scripts", "list_editors_picks", "list_author_scripts", "get_script_source", "harvest_scripts", "query_corpus", "fetch_status")}),
    ]
    _orig_resolve_m001 = reg.resolve_plugin_names
    _orig_compile_m001 = reg.compile_catalog_index

    import inspect
    import textwrap

    def _mutate_fn(mod, fn_name: str, old_expr: str, bad_expr: str):
        src = textwrap.dedent(inspect.getsource(getattr(mod, fn_name)))
        assert src.count(old_expr) == 1, f"Mutation non unique dans {fn_name}: {old_expr!r}"
        ns = dict(mod.__dict__)
        exec("from __future__ import annotations\n" + src.replace(old_expr, bad_expr, 1), ns)
        return ns[fn_name]

    def _bad_resolve_m001_ge(**kw):
        res = _orig_resolve_m001(**kw)
        if len(res) >= kw.get("max_plugins", reg.DEFAULT_MAX_PLUGINS):
            raise reg.PluginResolutionError("sabotaged >= max_plugins")
        return res

    sabotages.extend([
        ("M001:is_valid_plugin_dirname", verify_m001, reg, "is_valid_plugin_dirname", lambda _n: True),
        ("M001:is_reserved_plugin_dirname", verify_m001, reg, "is_reserved_plugin_dirname", lambda _n: False),
        ("M001:is_zero_sha", verify_m001, reg, "is_zero_sha", lambda _s: False),
        ("M001:normalize_plugin_names", verify_m001, reg, "normalize_plugin_names", lambda names, **_kw: list(names)),
        ("M001:resolve_plugin_names", verify_m001, reg, "resolve_plugin_names", lambda **_kw: []),
        ("M001:resolve_max_plugins_ge", verify_m001, reg, "resolve_plugin_names", _bad_resolve_m001_ge),
        ("M001:submission_plugin_name", verify_m001, reg, "submission_plugin_name", lambda _p: "tampered"),
        ("M001:is_deletion_pr", verify_m001, reg, "is_deletion_pr", lambda _e, _n: False),
        ("M001:parse_repo_url", verify_m001, reg, "parse_repo_url", lambda _u: None),
        ("M001:normalize_repo_url", verify_m001, reg, "normalize_repo_url", lambda _u: None),
        ("M001:repo_owner_from_url", verify_m001, reg, "repo_owner_from_url", lambda _u: None),
        ("M001:read_plugin_yaml_text_strict", verify_m001, reg, "read_plugin_yaml_text_strict", lambda _t, **_kw: {}),
        ("M001:INDEX_YAML_MAX_CHARS_1999", verify_m001, reg, "INDEX_YAML_MAX_CHARS", 1999),
        ("M001:validate_github_repo_not_in_index", verify_m001, reg, "validate_github_repo_not_in_index", lambda *_a: None),
        ("M001:validate_remote_plugin_name", verify_m001, reg, "validate_remote_plugin_name", lambda *_a: None),
        ("M001:validate_github_repo", verify_m001, reg, "validate_github_repo", lambda *_a, **_kw: None),
        ("M001:validate_fields", verify_m001, reg, "validate_fields", lambda *_a, **_kw: None),
        ("M001:TITLE_MAX_LEN_49", verify_m001, reg, "TITLE_MAX_LEN", 49),
        ("M001:DESCRIPTION_MAX_LEN_499", verify_m001, reg, "DESCRIPTION_MAX_LEN", 499),
        ("M001:MAX_TAGS_4", verify_m001, reg, "MAX_TAGS", 4),
        ("M001:MAX_SCREENSHOTS_4", verify_m001, reg, "MAX_SCREENSHOTS", 4),
        ("M001:validate_screenshot_url", verify_m001, reg, "validate_screenshot_url", lambda *_a, **_kw: None),
        ("M001:SCREENSHOT_MAX_BYTES_minus1", verify_m001, reg, "SCREENSHOT_MAX_BYTES", 2 * 1024 * 1024 - 1),
        ("M001:validate_thumbnail", verify_m001, reg, "validate_thumbnail", lambda *_a: None),
        ("M001:THUMBNAIL_MAX_BYTES_20479", verify_m001, reg, "THUMBNAIL_MAX_BYTES", 20 * 1024 - 1),
        ("M001:validate_allowed_files", verify_m001, reg, "validate_allowed_files", lambda *_a: None),
        ("M001:compile_catalog_index", verify_m001, reg, "compile_catalog_index", lambda *_a, **_kw: {"version": 1, "plugins": {}, "authors": {}}),
        ("M001:upsert_index_plugin", verify_m001, reg, "upsert_index_plugin", lambda idx, pn, ent: idx["plugins"].__setitem__(pn, dict(ent))),
        ("M001:remove_index_plugin", verify_m001, reg, "remove_index_plugin", lambda _idx, _pn: False),
        ("M001:render_discussion_body", verify_m001, reg, "render_discussion_body", lambda *_a: "sabotaged\n"),
        ("M001:discussion_marker_name", verify_m001, reg, "discussion_marker_name", lambda _b: None),
        ("M001:find_orphan_names", verify_m001, reg, "find_orphan_names", lambda *_a, **_kw: []),
        ("M001:chunks", verify_m001, reg, "chunks", lambda items, _n: [list(items)] if items else []),
        ("M001:extract_alias_errors", verify_m001, reg, "extract_alias_errors", lambda _p: {}),
        ("M001:extract_plugin_version", verify_m001, reg, "extract_plugin_version", lambda _t: None),
        ("M001:extract_commit_info", verify_m001, reg, "extract_commit_info", lambda _o: None),
        ("M001:apply_star_updates", verify_m001, reg, "apply_star_updates", lambda _idx, _u: 0),
        ("M001:publish_index_release", verify_m001, reg, "publish_index_release", lambda *_a, **_kw: 0),
        ("M001:download_index_release", verify_m001, reg, "download_index_release", lambda *_a, **_kw: 0),
        ("M001:audit_plugin_catalog", verify_m001, reg, "audit_plugin_catalog", lambda _r: {k: 0 for k in ("plugin_dirs_total", "plugin_names_resolved", "indexed_plugins", "index_yaml_present", "legacy_plugin_yaml_only", "blocked_plugins", "index_yaml_invalid", "index_yaml_missing_keys", "max_screenshots", "generated_thumbnails", "orphan_thumbnails", "local_thumbnails", "plugins_without_any_thumbnail", "abandoned_present", "surfaces_present", "index_coherent")}),
        ("M001:resolve_start_from_ne_zero", verify_m001, reg, "resolve_plugin_names", _mutate_fn(reg, "resolve_plugin_names", "if start_idx > 0:", "if start_idx != 0:")),
        ("M001:_pub_rename_asset_max_2", verify_m001, reg, "_pub_rename_asset", _mutate_fn(reg, "_pub_rename_asset", "if attempt == 2:", "if attempt == 1:")),
        ("M001:publish_recover_size_ge_0", verify_m001, reg, "publish_index_release", _mutate_fn(reg, "publish_index_release", 'asset.get("size", 0) > 0', 'asset.get("size", 0) >= 0')),
        ("M001:download_retry_gt_500", verify_m001, reg, "download_index_release", _mutate_fn(reg, "download_index_release", "should_retry = e.code >= 500 or e.code == 429", "should_retry = e.code > 500 or e.code == 429")),
        ("M001:download_retry_ge_499", verify_m001, reg, "download_index_release", _mutate_fn(reg, "download_index_release", "should_retry = e.code >= 500 or e.code == 429", "should_retry = e.code >= 499 or e.code == 429")),
        ("M001:download_retry_no_429", verify_m001, reg, "download_index_release", _mutate_fn(reg, "download_index_release", "should_retry = e.code >= 500 or e.code == 429", "should_retry = e.code >= 500")),
        ("M001:download_retry_attempt_lt_2", verify_m001, reg, "download_index_release", _mutate_fn(reg, "download_index_release", "if should_retry and attempt < 3:", "if should_retry and attempt < 2:")),
        ("M001:download_retry_net_lt_2", verify_m001, reg, "download_index_release", _mutate_fn(reg, "download_index_release", "if attempt < 3:", "if attempt < 2:")),
    ])
    for label, cfn, mod, attr, fake in sabotages:
        _assert_breaks(label, cfn, mod, attr, fake)

    # Sabotage d'ajout de clé parasite dans M118 & M117 (vérifie le refus des clés en trop)
    orig_opps = copy.deepcopy(cat.OPPORTUNITY_DOSSIERS)
    try:
        cat.OPPORTUNITY_DOSSIERS["OPP-001"]["extra_parasite_key"] = "must_fail"
        broke_extra = False
        try:
            verify_m118()
        except Exception:
            broke_extra = True
        assert broke_extra, "SABOTAGE CLÉ EN TROP M118 NON DÉTECTÉ !"
    finally:
        cat.OPPORTUNITY_DOSSIERS = orig_opps

    orig_pbs = copy.deepcopy(cat.MARKETPLACE_PLAYBOOKS)
    try:
        cat.MARKETPLACE_PLAYBOOKS["01_Website_and_Funnels"]["extra_parasite_key"] = "must_fail"
        broke_pb = False
        try:
            verify_m117()
        except Exception:
            broke_pb = True
        assert broke_pb, "SABOTAGE CLÉ EN TROP M117 NON DÉTECTÉ !"
    finally:
        cat.MARKETPLACE_PLAYBOOKS = orig_pbs

    _orig_compile_cat = reg.compile_catalog_index

    def _bad_compile_parasite(*a, **kw):
        out = _orig_compile_cat(*a, **kw)
        first_k = next(iter(out["plugins"]))
        out["plugins"][first_k]["extra_parasite_key"] = "must_fail"
        return out

    reg.compile_catalog_index = _bad_compile_parasite
    broke_m001_extra = False
    try:
        verify_m001()
    except Exception:
        broke_m001_extra = True
    finally:
        reg.compile_catalog_index = _orig_compile_cat
    assert broke_m001_extra, "SABOTAGE CLÉ EN TROP M001 NON DÉTECTÉ !"

    return len(sabotages) + 3


# Phase C : parité stricte -> sabotage complet -> auto-tests honnêtes -> reçus R10 mesurés
case_counts = verify_all()
sabotage_detected_count = run_sabotage_suite()

# Re-vérifier que verify_all() repasse intégralement après restauration des sabotages
verify_all()

r04 = f04.run_fkb04_self_test(head_sha40=sha, repo_root=iso)
r02 = f02.run_fkb02_self_test(repo_root=iso, head_sha40=sha)
rcat = cat.run_self_test(head_sha40=sha, repo_root=iso)
rtrd = trd.run_trading_copilot_self_test(head_sha40=sha, repo_root=iso)
rreg = reg.run_plugin_registry_self_test(head_sha40=sha, repo_root=iso)

assert r04["source_parity_verified"] == [], f"Auto-déclaration interdite: {r04['source_parity_verified']}"
assert r02["source_parity_verified"] == [], f"Auto-déclaration interdite: {r02['source_parity_verified']}"
assert rcat["source_parity_verified"] == [], f"Auto-déclaration interdite: {rcat['source_parity_verified']}"
assert rtrd["source_parity_verified"] == [], f"Auto-déclaration interdite: {rtrd['source_parity_verified']}"
assert rreg["source_parity_verified"] == [], f"Auto-déclaration interdite: {rreg['source_parity_verified']}"
assert "headless-fallback" not in json.dumps(r04) and "HeadlessDesktopSession" not in json.dumps(r04)
assert r04["desktop_live_verified"] is False or r04["desktop_live_windows"] >= 1

rec04 = f04.consign_fkb04_parity_receipt(
    {"CLI-Anything": {"compared_against_source": True, "cases_compared": case_counts["CLI-Anything"], "cases_matched": case_counts["CLI-Anything"]}},
    sha,
    repo_root=iso,
)
rec02 = f02.consign_fkb02_parity_receipt(
    {
        "context-language-models": {"compared_against_source": True, "cases_compared": case_counts["context-language-models"], "cases_matched": case_counts["context-language-models"]},
        "knowledge-catalog": {"compared_against_source": True, "cases_compared": case_counts["knowledge-catalog"], "cases_matched": case_counts["knowledge-catalog"]},
    },
    sha,
    repo_root=iso,
)
reccat = cat.consign_catalog_parity_receipt(
    {
        "00_Marketplace_YoutubeSkills": {"compared_against_source": True, "cases_compared": case_counts["00_Marketplace_YoutubeSkills"], "cases_matched": case_counts["00_Marketplace_YoutubeSkills"]},
        "04_Inference_Youtube_Discovery_Registry": {"compared_against_source": True, "cases_compared": case_counts["04_Inference_Youtube_Discovery_Registry"], "cases_matched": case_counts["04_Inference_Youtube_Discovery_Registry"]},
    },
    sha,
    repo_root=iso,
)
recvd = vsf.consign_video_director_parity_receipt(
    {"video-director": {"compared_against_source": True, "cases_compared": case_counts["video-director"], "cases_matched": case_counts["video-director"]}},
    sha,
    repo_root=iso,
)
rectrd = trd.consign_trading_parity_receipt(
    {"tradingview-indicator-search-mcp-server": {"compared_against_source": True, "cases_compared": case_counts["tradingview-indicator-search-mcp-server"], "cases_matched": case_counts["tradingview-indicator-search-mcp-server"]}},
    sha,
    repo_root=iso,
)
recreg = reg.consign_plugin_registry_parity_receipt(
    {"a0-plugins": {"compared_against_source": True, "cases_compared": case_counts["a0-plugins"], "cases_matched": case_counts["a0-plugins"]}},
    sha,
    repo_root=iso,
)

proven_mods = (
    rec04["verified_modules"]
    + rec02["verified_modules"]
    + reccat["verified_modules"]
    + recvd["verified_modules"]
    + rectrd["verified_modules"]
    + recreg["verified_modules"]
)

print(json.dumps({
    "differential_proven": proven_mods,
    "sabotages_detected": sabotage_detected_count,
    "case_counts": case_counts,
    "desktop_live_verified": bool(r04["desktop_live_verified"]),
    "r10": {"f04": rec04["r10_entry_id"], "f02": rec02["r10_entry_id"], "cat": reccat["r10_entry_id"], "vd": recvd["r10_entry_id"], "trd": rectrd["r10_entry_id"], "reg": recreg["r10_entry_id"]},
}))
'''


def test_real_differential_deletion_and_lazy_import() -> tuple[set[str], bool]:
    _ensure_upstream_submodules()

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

    # Preuve reproductible de provenance/rapatriement historique D-N048 V0 (M120 llm-wiki)
    # sans auto-certification FUSIONNÉ : vérifie l'intégrité SHA-256 du corps rapatrié
    # et l'ancrage D-N048 V0, tout en maintenant M120 en PARTIEL faute de preuve K4/sabotage.
    M120_GIST_BODY_SHA256 = "dc3efe98ae62f23dd08acad13aba2e95287beb20b6bec2f4af0423557fe37401"
    M120_D_N048_COMMIT = "26ca7cb7c623fb42c56bffe77d49e9a74473bcf2"
    llm_wiki_doc = ROOT / "00_Memoire" / "bundle" / "concepts" / "llm-wiki.md"
    assert llm_wiki_doc.exists(), "00_Memoire/bundle/concepts/llm-wiki.md manquant"
    raw_lw_lf = llm_wiki_doc.read_bytes().replace(b"\r\n", b"\n")
    lw_parts = raw_lw_lf.split(b"---\n", 2)
    assert len(lw_parts) == 3, "Frontmatter YAML OKF absent dans llm-wiki.md"
    assert b"source: gist 34a4b4bf6d54b1828ba8c256615619e8" in lw_parts[1]
    assert b"source_size_octets: 11985" in lw_parts[1]
    lw_body_lf = lw_parts[2].lstrip(b"\n")
    assert len(lw_body_lf) == 11985, f"Taille corps llm-wiki inattendue: {len(lw_body_lf)}"
    assert hashlib.sha256(lw_body_lf).hexdigest() == M120_GIST_BODY_SHA256, "SHA-256 corps llm-wiki divergent vs D-N048 V0"
    freeze_md = (ROOT / "01_Forkable" / "FORKS-AMONT-21-FREEZE.md").read_text(encoding="utf-8")
    assert M120_GIST_BODY_SHA256 in freeze_md, "Ancre SHA-256 D-N048 V0 absente de FORKS-AMONT-21-FREEZE.md"
    is_shallow = subprocess.check_output(
        ["git", "rev-parse", "--is-shallow-repository"], cwd=str(ROOT), text=True
    ).strip()
    if is_shallow != "true":
        subprocess.check_call(
            ["git", "cat-file", "-e", f"{M120_D_N048_COMMIT}^{{commit}}"],
            cwd=str(ROOT),
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )

    # Import paresseux : ne touche pas egm_missions.db et exclut github-actions-freevps
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

    head_sha = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=str(ROOT), text=True).strip()
    diff_inputs = _build_differential_inputs()

    with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as tmpdir:
        iso_root = Path(tmpdir) / "diff_tree"
        copy_targets = (
            ".gitmodules",
            "AGENTS.md",
            "CLAUDE.md",
            "00_Memoire/AGENTS.md",
            "00_Memoire/bundle",
            "01_Forkable/FKB00_Runtime/00_A0_Core/aspace_foundation_kernel.py",
            "01_Forkable/FKB00_Runtime/00_A0_Core/aspace_discovery_catalog.py",
            "01_Forkable/FKB00_Runtime/00_A0_Core/aspace_plugin_registry_organ.py",
            "01_Forkable/FKB00_Runtime/00_A0_Core/aspace_fkb04_anything_organ.py",
            "01_Forkable/FKB00_Runtime/00_A0_Core/aspace_fkb02_memory_organ.py",
            "01_Forkable/FKB00_Runtime/00_A0_Core/a0_recursive_factory.py",
            "01_Forkable/FKB00_Runtime/00_A0_Core/aspace_freecompute_router.py",
            "01_Forkable/FKB01_Inference/03_Inference_FreeCloud/aspace_freecloud_gateway.py",
            "01_Forkable/FKB02_Memory/01_BillionContxtLanguage_AutoOnthology/neuro_symbolic_bridge.py",
            "01_Forkable/FKB07_Money_Maker/aspace_marketplace_engine.py",
            "01_Forkable/FKB07_Money_Maker/02_Video/aspace_video_studio_foundation.py",
            "01_Forkable/FKB07_Money_Maker/01_Trading/aspace_trading_copilot_foundation.py",
            # Sources réelles M001, M044, M050, M056, M074, M084, M117, M118 pour Phase A avant suppression
            "01_Forkable/FKB00_Runtime/00_A0_Core/a0-plugins",
            "01_Forkable/FKB02_Memory/01_BillionContxtLanguage_AutoOnthology/context-language-models/clm",
            "01_Forkable/FKB02_Memory/knowledge-catalog/okf",
            "01_Forkable/FKB04_Tools_Anything/CLI-Anything/cli-anything-plugin",
            "01_Forkable/FKB04_Tools_Anything/CLI-Anything/zotero/agent-harness",
            "01_Forkable/FKB04_Tools_Anything/CLI-Anything/audacity/agent-harness",
            "01_Forkable/FKB07_Money_Maker/02_Video/video-director/video-director/scripts",
            "01_Forkable/FKB07_Money_Maker/01_Trading/tradingview-indicator-search-mcp-server/src",
            "01_Forkable/FKB07_Money_Maker/01_Trading/tradingview-indicator-search-mcp-server/test/fixtures",
            "01_Forkable/FKB07_Money_Maker/01_Trading/tradingview-indicator-search-mcp-server/package.json",
            "01_Forkable/FKB07_Money_Maker/00_Marketplace_YoutubeSkills",
            "01_Forkable/FKB01_Inference/04_Inference_Youtube_Discovery_Registry",
        )
        ign = shutil.ignore_patterns(".git", "__pycache__", ".pytest_cache")
        for sub_copy in copy_targets:
            src_p = ROOT / sub_copy
            assert src_p.exists(), f"Copie test différentiel manquante: {src_p}"
            dst_p = iso_root / sub_copy
            dst_p.parent.mkdir(parents=True, exist_ok=True)
            if src_p.is_dir():
                shutil.copytree(src_p, dst_p, ignore=ign)
            else:
                shutil.copy2(src_p, dst_p)

        # Entrées de test zotero/audacity copiées hors CLI-Anything/ pour rejouer extract_cli_anything_metadata après suppression
        for sw in ("zotero", "audacity"):
            shutil.copytree(
                ROOT / "01_Forkable/FKB04_Tools_Anything/CLI-Anything" / sw / "agent-harness",
                iso_root / "test_input_harnesses" / sw / "agent-harness",
                ignore=ign,
            )
        shutil.copytree(
            ROOT / "01_Forkable/FKB07_Money_Maker/01_Trading/tradingview-indicator-search-mcp-server/test/fixtures",
            iso_root / "test_input_m074_fixtures",
            ignore=ign,
        )
        m001_in = iso_root / "test_input_m001_catalog"
        m001_src_cat = ROOT / "01_Forkable/FKB00_Runtime/00_A0_Core/a0-plugins"
        for sub_cat in ("plugins", "authors", "generated"):
            shutil.copytree(m001_src_cat / sub_cat, m001_in / sub_cat, ignore=ign)
        shutil.copy2(m001_src_cat / "scripts" / "plugin_discussion_template.md", m001_in / "plugin_discussion_template.md")

        (iso_root / "diff_inputs.json").write_text(json.dumps(diff_inputs, ensure_ascii=False), encoding="utf-8")

        # PHASE A : exécution des sources amont dans iso_root AVANT suppression
        (iso_root / "oracle_runner.py").write_text(_ORACLE_RUNNER_CODE, encoding="utf-8")
        subprocess.check_call([sys.executable, str(iso_root / "oracle_runner.py")], cwd=str(iso_root))
        (iso_root / "oracle_runner.py").unlink()
        assert (iso_root / "oracle_outputs.json").exists()

        # PHASE B : suppression physique effective de tous les répertoires sources (FKB04, FKB02, M084, M117, M118) + F8
        for rel in SOURCE_DIRS_TO_DELETE_FOR_TEST + absent_paths:
            target = iso_root / rel
            if target.exists():
                _force_rmtree(target)
            assert not target.exists(), f"Suppression physique incomplète: {target}"

        # PHASE C : exécution stricte + sabotage complet dans iso_root amputé
        (iso_root / "organ_runner.py").write_text(_ORGAN_RUNNER_CODE, encoding="utf-8")
        iso_out = subprocess.check_output(
            [sys.executable, str(iso_root / "organ_runner.py"), head_sha],
            cwd=str(iso_root),
            text=True,
        )
        parsed = json.loads(iso_out)
        assert parsed["sabotages_detected"] >= 129, (
            f"Couverture sabotage insuffisante : attendu >= 129, obtenu {parsed['sabotages_detected']}"
        )
        diff_proven = set(parsed["differential_proven"])
        desktop_live = bool(parsed["desktop_live_verified"])

        # Orchestrateurs câblés dans l'arbre physiquement amputé
        for rel_script, extra_args in [
            ("01_Forkable/FKB00_Runtime/00_A0_Core/a0_recursive_factory.py", []),
            ("01_Forkable/FKB00_Runtime/00_A0_Core/aspace_plugin_registry_organ.py", []),
            ("01_Forkable/FKB01_Inference/03_Inference_FreeCloud/aspace_freecloud_gateway.py", ["--self-test"]),
            ("01_Forkable/FKB02_Memory/01_BillionContxtLanguage_AutoOnthology/neuro_symbolic_bridge.py", []),
            ("01_Forkable/FKB07_Money_Maker/aspace_marketplace_engine.py", []),
            ("01_Forkable/FKB07_Money_Maker/02_Video/aspace_video_studio_foundation.py", []),
            ("01_Forkable/FKB07_Money_Maker/01_Trading/aspace_trading_copilot_foundation.py", []),
        ]:
            subprocess.check_call([sys.executable, str(iso_root / rel_script), *extra_args], cwd=str(iso_root), stdout=subprocess.DEVNULL)

    # Sous-processus K1..K5 vers le bus L0 du workspace
    journal_path = ROOT / "02_Factory" / "jobs" / "l0_foundation_journal.jsonl"
    before_lines = len(journal_path.read_text(encoding="utf-8").splitlines()) if journal_path.exists() else 0
    for rel_script, extra_args in [
        ("01_Forkable/FKB00_Runtime/00_A0_Core/a0_recursive_factory.py", []),
        ("01_Forkable/FKB00_Runtime/00_A0_Core/aspace_plugin_registry_organ.py", []),
        ("01_Forkable/FKB00_Runtime/00_A0_Core/aspace_freecompute_router.py", []),
        ("01_Forkable/FKB01_Inference/03_Inference_FreeCloud/aspace_freecloud_gateway.py", ["--self-test"]),
        ("01_Forkable/FKB02_Memory/01_BillionContxtLanguage_AutoOnthology/neuro_symbolic_bridge.py", []),
        ("01_Forkable/FKB07_Money_Maker/aspace_marketplace_engine.py", []),
        ("01_Forkable/FKB07_Money_Maker/02_Video/aspace_video_studio_foundation.py", []),
        ("01_Forkable/FKB07_Money_Maker/01_Trading/aspace_trading_copilot_foundation.py", []),
    ]:
        subprocess.check_call([sys.executable, str(ROOT / rel_script), *extra_args], cwd=str(ROOT), stdout=subprocess.DEVNULL)
    after_lines = len(journal_path.read_text(encoding="utf-8").splitlines())
    assert after_lines >= before_lines + 8

    assert "llm-wiki" not in diff_proven, "M120 llm-wiki ne doit jamais être auto-ajouté à diff_proven"
    print(
        f"[PASS 4/7] Différentiel strict (==) + {parsed['sabotages_detected']} sabotages détectés PASS "
        f"({len(diff_proven)} prouvés : {sorted(diff_proven)}) + M058 desktop_live={desktop_live} + L0 ({before_lines}->{after_lines})"
    )
    return diff_proven, desktop_live


def test_fondation_13_1_fixture_compatibility() -> None:
    assert ROOT_KERNELS == ("ÂME", "SYSTÈME NERVEUX", "CORPS")
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
    print("[PASS 5/7] Compatibilité 1:1 Rust fondation-13-1 + Interconnexion L0 (5 organes / 3 noyaux ADR-15)")


def test_carte_and_registre_adr15_and_dynamic_counts(proven_fusionne: set[str], desktop_live_verified: bool) -> None:
    carte = (FUSION_DIR / "CARTE-DES-PRINCIPES.md").read_text(encoding="utf-8")
    registre = (FUSION_DIR / "REGISTRE-DE-FUSION.md").read_text(encoding="utf-8")

    carte_pairs = re.findall(r"^### (M\d{3}) — `([^`]+)`", carte, flags=re.MULTILINE)
    carte_id_to_name = dict(carte_pairs)
    d_carte = re.findall(r"^### (D\d{2}) — ", carte, flags=re.MULTILINE)
    assert len(carte_pairs) == 120 and len(carte_id_to_name) == 120 and len(d_carte) == 8

    reg_rows = re.findall(r"^\| (?:M\d{3}) \| .*?$", registre, flags=re.MULTILINE)
    assert len(reg_rows) == 120

    kernel_counts = {rk: 0 for rk in ROOT_KERNELS}
    registry_fusionne: set[str] = set()
    by_name: dict[str, tuple[str, str]] = {}
    reg_id_to_name: dict[str, str] = {}
    actual_retenu = 0
    actual_ecarte = 0

    for row in reg_rows:
        cols = [c.strip() for c in row.strip("|").split("|")]
        mod_id = cols[0]
        mod_name = cols[1].strip("`")
        reg_id_to_name[mod_id] = mod_name
        noyau_col = cols[4]
        statut_col = cols[6]
        justification = cols[8] if len(cols) > 8 else ""
        assert len(justification) >= 15, f"Justification insuffisante pour {mod_name}: {justification!r}"

        matched_rk = next((rk for rk in ROOT_KERNELS if noyau_col.startswith(f"{rk} ·")), None)
        assert matched_rk is not None, f"Noyau ADR-15 invalide (attendu ÂME / SYSTÈME NERVEUX / CORPS) pour {mod_name}: {noyau_col!r}"
        kernel_counts[matched_rk] += 1

        by_name[mod_name] = (statut_col, justification)
        if statut_col == "**FUSIONNÉ**":
            registry_fusionne.add(mod_name)
        elif statut_col == "**RETENU**":
            actual_retenu += 1
        elif statut_col == "**ÉCARTÉ**":
            actual_ecarte += 1

    assert sum(kernel_counts.values()) == 120

    assert registry_fusionne == proven_fusionne, (
        f"Divergence entre REGISTRE FUSIONNÉ ({sorted(registry_fusionne)}) et preuves dynamiques ({sorted(proven_fusionne)})"
    )

    if not desktop_live_verified:
        assert by_name["agent-desktop"][0] == "**PARTIEL**", (
            f"M058 agent-desktop doit rester PARTIEL sans fenêtre Win32 vérifiée: {by_name['agent-desktop']}"
        )

    assert (actual_retenu + actual_ecarte) / 120.0 < (1.0 / 3.0)

    for mod in ("RigInfinity", "automaton", "cordis", "pi", "aspace-fiber-host", "fondation-13-1", "source-control-natif"):
        assert by_name[mod][0] == "**PARTIEL**", f"{mod} doit rester PARTIEL: {by_name[mod]}"

    assert len(reg_id_to_name) == 120
    assert carte_id_to_name == reg_id_to_name, "Divergence ID<->Module entre CARTE-DES-PRINCIPES et REGISTRE-DE-FUSION"
    assert reg_id_to_name["M001"] == "a0-plugins"
    assert reg_id_to_name["M074"] == "tradingview-indicator-search-mcp-server"
    assert reg_id_to_name["M084"] == "video-director"
    assert reg_id_to_name["M095"] == "BlenderWorld"
    assert reg_id_to_name["M120"] == "llm-wiki"

    name_to_id = {v: k for k, v in reg_id_to_name.items()}
    diff_ids = {name_to_id[m] for m in (proven_fusionne - RIG_INFINITY_PROVEN_F8)}
    assert diff_ids == {"M001", "M044", "M050", "M056", "M074", "M084", "M117", "M118"}, (
        f"Les 8 preuves différentielles attendues sont {{M001, M044, M050, M056, M074, M084, M117, M118}}, obtenu: {sorted(diff_ids)}"
    )

    assert by_name["TradingView-Unified-MCP"][0] == "**PARTIEL**", (
        f"M066 TradingView-Unified-MCP doit rester PARTIEL (CDP live hors invariants M074): {by_name['TradingView-Unified-MCP']}"
    )
    assert "TradingView-Unified-MCP" not in registry_fusionne and "TradingView-Unified-MCP" not in proven_fusionne

    assert by_name["BlenderWorld"][0] == "**PARTIEL**", (
        f"M095 BlenderWorld doit rester PARTIEL: {by_name['BlenderWorld']}"
    )
    assert "BlenderWorld" not in registry_fusionne and "BlenderWorld" not in proven_fusionne

    assert by_name["llm-wiki"][0] == "**PARTIEL**", (
        f"M120 llm-wiki doit rester PARTIEL sans preuve exécutable K4 + sabotage + reçu R10: {by_name['llm-wiki']}"
    )

    id_pat = re.compile(r"M0" + r"95[^\n]{0,40}video-director|video-director[^\n]{0,40}M0" + r"95")
    for rel_guard in (
        "00_Memoire/bundle/fusion/PRD-FONDATION.md",
        "00_Memoire/bundle/fusion/SDD-FONDATION.md",
        "00_Memoire/bundle/fusion/ADR-FUSION.md",
        "00_Memoire/bundle/fusion/adr/ADR-15.md",
        "00_Memoire/bundle/fusion/REGISTRE-DE-FUSION.md",
        "00_Memoire/bundle/fusion/CARTE-DES-PRINCIPES.md",
        "01_Forkable/FKB07_Money_Maker/02_Video/aspace_video_studio_foundation.py",
    ):
        txt = (ROOT / rel_guard).read_text(encoding="utf-8")
        assert not id_pat.search(txt), f"Confusion M084/M095 encore présente dans {rel_guard}"
    assert ("m0" + "95") not in Path(__file__).read_text(encoding="utf-8"), "Symbole résiduel dans test_foundation_deletion_suite.py"

    print(
        f"[PASS 6/7] ADR-15 3 Noyaux respectés ({kernel_counts}) | "
        f"{len(registry_fusionne)} FUSIONNÉ vérifiés dynamiquement, {actual_retenu} RETENU, {actual_ecarte} ÉCARTÉ"
    )


def test_required_spad_artifacts_and_windows_clone_lf() -> None:
    required = [
        "FUSION-ENONCE.md",
        "CARTE-DES-PRINCIPES.md",
        "ADR-FUSION.md",
        "DDD-CONTRATS-COMMUNS.md",
        "PRD-FONDATION.md",
        "SDD-FONDATION.md",
        "REGISTRE-DE-FUSION.md",
        "RAPPORT-CORRECTION-M120.md",
        "DECISIONS.md",
        "CORPS-CARTE.md",
    ]
    for fn in required:
        p = FUSION_DIR / fn
        assert p.exists() and p.stat().st_size > 200
    adrs = list((FUSION_DIR / "adr").glob("ADR-*.md"))
    assert len(adrs) >= 15, f"Attendu >= 15 ADRs (ADR-01..ADR-15), trouvé {len(adrs)}"

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
        cit = (clone_dir / "01_Forkable" / "FKB00_Runtime" / "00_A0_Core" / "fondation-13-1" / "tests" / "fixtures" / "citation-valide.md").read_bytes()
        if (clone_dir / ".gitattributes").exists() and "fondation-13-1/tests/fixtures/* text eol=lf" in (clone_dir / ".gitattributes").read_text(encoding="utf-8"):
            assert b"\r\n" not in cit, "Fixture Rust clonée contient encore CRLF!"
    checks_ps1_txt = (ROOT / "02_Factory" / "checks.ps1").read_text(encoding="utf-8")
    for bad_sep in ("$root\\", ".claude\\", ".vscode\\", "02_Factory\\"):
        assert bad_sep not in checks_ps1_txt, f"Séparateur Windows non portable dans checks.ps1: {bad_sep}"

    wf_path = ROOT / ".github" / "workflows" / "foundation-proof.yml"
    assert wf_path.exists(), "Workflow CI Porte B absent: .github/workflows/foundation-proof.yml"
    wf_txt = wf_path.read_text(encoding="utf-8")
    assert "continue-on-error" not in wf_txt, "continue-on-error interdit dans foundation-proof.yml"
    assert "|| true" not in wf_txt and "||true" not in wf_txt, "|| true interdit dans foundation-proof.yml"
    for req_token in (
        "fusion/**",
        "01_Forkable/FKB00_Runtime/00_A0_Core/test_foundation_deletion_suite.py",
        "01_Forkable/check-modules-lock.py",
        "pwsh -NoProfile -ExecutionPolicy Bypass -File 02_Factory/checks.ps1",
        "95e95f9b7a60b4e8e45564842bf380ee5d0c2aa4",
        "01_Forkable/FKB00_Runtime/00_A0_Core/a0-plugins",
        "fa8df8527a3c3a90a16906996ea5dc37f6f7a1fa",
        "01_Forkable/FKB07_Money_Maker/01_Trading/tradingview-indicator-search-mcp-server",
        "upload-artifact",
    ):
        assert req_token in wf_txt, f"Jeton requis absent de foundation-proof.yml: {req_token}"

    print(f"[PASS 7/7] {len(adrs)} ADRs + Artefacts SPAD + CI Porte B + Clone Windows par défaut préserve LF")


if __name__ == "__main__":
    test_enonce_hash_and_gitattributes()
    test_gitmodules_and_fkb06_deletion()
    rust_proven = test_rust_cargo_and_phase2_hybrid()
    diff_proven, desktop_live = test_real_differential_deletion_and_lazy_import()
    test_fondation_13_1_fixture_compatibility()
    test_carte_and_registre_adr15_and_dynamic_counts(rust_proven | diff_proven, desktop_live)
    test_required_spad_artifacts_and_windows_clone_lf()
    print("=== ALL 7/7 CYCLE-6 FOUNDATION, RUST, DIFFERENTIAL & ANTI-SABOTAGE SUITES PASSED ===")
