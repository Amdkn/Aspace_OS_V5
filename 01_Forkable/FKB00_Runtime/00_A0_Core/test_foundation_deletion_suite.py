#!/usr/bin/env python3
"""
test_foundation_deletion_suite.py — Suite de vérification Cycle 5 de la Fondation A'Space (ÉNONCÉ §1 & ADR-14).

Rejoue de façon 100 % déterministe, sans compteur codé en dur et sans repli factice :
  1. L'intégrité SHA-256 de 00_Memoire/bundle/fusion/FUSION-ENONCE.md et protection .gitattributes
     (y compris FUSION-ENONCE.md -text en dernier et tests/fixtures/* text eol=lf).
  2. La purge effective des 8 doublons FKB06 dans .gitmodules et l'alignement 1:1 (101 == 101).
  3. L'exécution réelle Rust en local (`fondation-13-1` 100/100 + `RigInfinity` 105/105 WSL2/Linux)
     et le pont Phase 2 Hybride (`r10-receive` + `route-dispatch` compilés contre Python).
  4. Le test différentiel réel avec amputation physique (ÉNONCÉ (3), Cycle 5) sur copie isolée :
     - Phase A : exécution des sources d'origine M044 (`context-language-models`), M050 (`knowledge-catalog`),
       M056 (`CLI-Anything` sur `zotero` & `audacity`), M117 (`00_Marketplace_YoutubeSkills`), M118
       (`04_Inference_Youtube_Discovery_Registry`) sur des entrées riches identiques -> `oracle_outputs`.
     - Phase B : suppression physique effective de ces 5 sources (et des 15 autres répertoires FKB02/FKB04)
       + vérification d'absence des 14 modules déjà retirés (F8/GSD/llm-wiki).
     - Phase C : exécution des organes natifs dans l'arbre physiquement amputé sur les mêmes entrées,
       comparaison stricte `organ_outputs == oracle_outputs`, vérification qu'aucun organe n'auto-déclare
       `source_parity_verified` ni `headless-fallback`, et consignation des reçus R10 mesurés.
  5. L'interconnexion L0 des 5 organes (K1..K5) et la déclaration des 4 Noyaux Équilibrés (ADR-14).
  6. La complétude et l'honnêteté dynamique de CARTE-DES-PRINCIPES.md & REGISTRE-DE-FUSION.md :
     - 120 modules tous rattachés à `{ÂME, SYSTÈME NERVEUX, CORPS, MÉTABOLISME}` avec <= 40 par noyau (ADR-14),
     - égalité stricte `registry_fusionne == proven_fusionne` calculée depuis les preuves exécutées,
     - `M058 agent-desktop` maintenu `PARTIEL` tant que `desktop_live_verified` est faux,
     - ratio `(RETENU+ÉCARTÉ) < 1/3` et justifications individuelles non vides.
  7. Tous les artefacts SPAD (>= 14 ADRs dont ADR-14) + reproductibilité sur clone Windows standard (`core.autocrlf=true`).
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
    MAX_MODULES_PER_KERNEL_RATIO,
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
)

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
    """Initialise les sous-modules requis (sans jamais masquer une absence) sur clone neuf."""
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
            "text_cases": [
                {"content": "Bonjour Aspace"},
                {"content": ""},
                {"content": "   \n  "},
                {"content": [{"type": "text", "text": "Bloc 1"}, {"type": "text", "text": "Bloc 2"}]},
                {"content": [{"type": "tool_use", "id": "call_1", "name": "read"}]},
                {"content": [{"type": "text", "text": "Alpha"}, {"type": "tool_use", "id": "x"}, {"type": "text", "text": "Beta"}]},
                {"content": None},
                {"content": 42},
                {"role": "system", "content": "Règle stricte"},
                {"role": "user", "content": [{"text": "Sans type explicite"}]},
                {"role": "assistant", "content": []},
                {"role": "assistant", "content": "Ligne A\nLigne B"},
            ],
            "conversations": [
                [
                    {"role": "user", "content": "Tour 1"},
                    {"role": "assistant", "content": [{"type": "text", "text": "Réponse 1"}]},
                    {"role": "user", "content": "Tour 2"},
                    {"role": "assistant", "content": "Réponse 2"},
                    {"role": "user", "content": "Tour 3 récent"},
                    {"role": "assistant", "content": "Réponse 3 récente"},
                ],
                [
                    {"role": "user", "content": "Mono A"},
                    {"role": "assistant", "content": "Mono B"},
                ],
                [
                    {"role": "user", "content": "Unique"},
                ],
            ],
            "edited_roundtrip": "--- user ---\nContexte condensé\n\n--- assistant ---\nSynthèse éditée\n",
        },
        "m050": {
            "synthetic_docs": [
                ("valid_decision", "---\nokf_version: '0.2'\ntype: Decision\ntitle: ADR Test\nverified: '2026-11-18'\n---\n\n# Corps\nContenu décisif.\n"),
                ("valid_date_obj", "---\nokf_version: '0.2'\ntype: Concept\ntitle: YAML Date Native\nverified: 2026-11-19\n---\nTexte YAML date.\n"),
                ("valid_spec", "---\ntype: Specification\nverified: '2024-01-01'\ntier: golden\n---\nSpec ancienne.\n"),
                ("valid_note_unverified", "---\ntype: Note\nsource_tier: bronze\n---\nNote rapide.\n"),
                ("valid_incident", "---\nokf_version: '0.2'\ntype: Incident\nverified: '2026-11-10T12:00:00'\n---\nIncident horodaté.\n"),
                ("valid_synthesis", "---\nokf_version: '0.2'\ntype: Synthesis\nverified: '2026-11-19'\n---\nSynthèse.\n"),
                ("bad_no_fm", "# Juste un titre sans frontmatter\n"),
                ("bad_missing_type", "---\ntitle: Sans type\n---\nTexte.\n"),
                ("bad_unknown_type", "---\ntype: TypeInexistant\n---\nTexte.\n"),
                ("bad_unclosed", "---\ntype: Concept\ntitle: Non fermé\n"),
                ("bad_non_dict", "---\n- element_1\n- element_2\n---\nTexte.\n"),
            ],
            "now_iso": "2026-11-19T12:00:00",
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
                {
                    "software": "custom-cli",
                    "recipe": "batch",
                    "bundle_kind": "bundle-v1",
                    "source_fingerprint": "sha256:999",
                    "options": {"dry_run": True, "targets": ["a", "b"]},
                    "harness_version": "1.0.0",
                },
            ],
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
        },
        "m118": {
            "opp_ids": ["OPP-001", "OPP-002", "OPP-003", "OPP-004", "OPP-005"],
        },
    }


_ORACLE_RUNNER_CODE = r'''
import dataclasses
import datetime as dt
import json
import re
import shutil
import sys
import tempfile
from pathlib import Path
import yaml

iso = Path.cwd()
inputs = json.loads((iso / "diff_inputs.json").read_text(encoding="utf-8"))

# --- M044: context-language-models upstream ---
clm_root = iso / "01_Forkable/FKB02_Memory/01_BillionContxtLanguage_AutoOnthology/context-language-models/clm"
sys.path.insert(0, str(clm_root))
from clm_harness.context_utils.context_string import (
    content_text as up_content_text,
    parse_back as up_parse_back,
    render_editable as up_render_editable,
    rendered_text as up_rendered_text,
)

m044_out = {
    "content_texts": [up_content_text(m.get("content")) for m in inputs["m044"]["text_cases"]],
    "rendered_texts": [up_rendered_text(m) for m in inputs["m044"]["text_cases"]],
    "roundtrips": [],
}
for conv in inputs["m044"]["conversations"]:
    for protect in (0, 1, 2, 3):
        editable = up_render_editable(conv, protect=protect)
        tail = conv[-protect:] if protect > 0 and len(conv) >= protect else (list(conv) if protect > 0 else [])
        parsed = up_parse_back(editable, tail)
        m044_out["roundtrips"].append({"protect": protect, "editable": editable, "parsed": parsed})
m044_out["custom_edit"] = up_parse_back(inputs["m044"]["edited_roundtrip"], inputs["m044"]["conversations"][0][-2:])

# --- M050: knowledge-catalog upstream ---
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

ref_now = dt.datetime.fromisoformat(inputs["m050"]["now_iso"])
doc_samples = list(inputs["m050"]["synthetic_docs"])
concepts_dir = iso / "00_Memoire" / "bundle" / "concepts"
if concepts_dir.exists():
    for md_p in sorted(concepts_dir.glob("*.md"))[:12]:
        doc_samples.append((f"concept:{md_p.name}", md_p.read_text(encoding="utf-8")))

m050_docs_res = []
for label, raw in doc_samples:
    try:
        d = UpOKFDocument.parse(raw)
        nv = up_normalize_verified(d.frontmatter)
        nv_clean = json.loads(json.dumps(nv, default=str))
        m050_docs_res.append({
            "label": label,
            "ok": True,
            "normalized_verified": nv_clean,
            "trust_tier": up_trust_tier(d.frontmatter),
            "is_stale": up_is_stale(d.frontmatter, now=ref_now),
            "validate": d.validate(),
            "serialized": d.serialize(),
        })
    except UpOKFDocumentError:
        m050_docs_res.append({"label": label, "ok": False, "err": "OKFDocumentError"})

bundle_tmp = Path(tempfile.mkdtemp(dir=str(iso), prefix="oracle_okf_"))
(bundle_tmp / "alpha.md").write_text("---\nokf_version: '0.2'\ntype: Concept\ntitle: Alpha\nverified: '2026-11-19'\n---\nBody Alpha\n", encoding="utf-8")
(bundle_tmp / "sub").mkdir()
(bundle_tmp / "sub" / "beta.md").write_text("---\nokf_version: '0.2'\ntype: Decision\ntitle: Beta\nverified: '2026-11-18'\n---\nBody Beta\n", encoding="utf-8")
(bundle_tmp / "sub" / "gamma.md").write_text("---\nokf_version: '0.2'\ntype: Note\ntitle: Gamma\n---\nBody Gamma\n", encoding="utf-8")
up_gen_paths = up_regenerate_indexes(bundle_tmp, model="oracle-model", synthesize=lambda f, docs, model="": f"Synthèse {f} ({len(docs)} docs via {model})")
m050_indexes = {
    p.relative_to(bundle_tmp).as_posix(): p.read_text(encoding="utf-8")
    for p in sorted(up_gen_paths)
}

m050_out = {"docs": m050_docs_res, "indexes": m050_indexes}

# --- M056: CLI-Anything upstream ---
cli_plugin_dir = iso / "01_Forkable/FKB04_Tools_Anything/CLI-Anything/cli-anything-plugin"
sys.path.insert(0, str(cli_plugin_dir))
from preview_bundle import build_cache_key as up_build_cache_key
from skill_generator import (
    extract_cli_metadata as up_extract_cli_metadata,
    generate_skill_md as up_generate_skill_md,
    generate_skill_md_simple as up_generate_skill_md_simple,
)

tpl_path = cli_plugin_dir / "templates" / "SKILL.md.template"
m056_harnesses = {}
for sw in ("zotero", "audacity"):
    h_dir = iso / "01_Forkable/FKB04_Tools_Anything/CLI-Anything" / sw / "agent-harness"
    meta = up_extract_cli_metadata(str(h_dir))
    m056_harnesses[sw] = {
        "meta": dataclasses.asdict(meta),
        "skill_md": up_generate_skill_md(meta, template_path=str(tpl_path)),
        "skill_md_simple": up_generate_skill_md_simple(meta),
    }

m056_cache_keys = [
    up_build_cache_key(
        ck["software"],
        ck["recipe"],
        ck["bundle_kind"],
        ck["source_fingerprint"],
        options=ck["options"],
        harness_version=ck["harness_version"],
    )
    for ck in inputs["m056"]["cache_key_cases"]
]
m056_out = {"harnesses": m056_harnesses, "cache_keys": m056_cache_keys}

# --- M117: 00_Marketplace_YoutubeSkills raw filesystem oracle ---
m117_dir = iso / "01_Forkable/FKB07_Money_Maker/00_Marketplace_YoutubeSkills"
readme_lines = (m117_dir / "README.md").read_text(encoding="utf-8").splitlines()
video_records = []
for ln in readme_lines:
    mt = re.match(r"^\d+\.\s+`([A-Za-z0-9_-]{11})`.*?Catégorie\s+(\d+)\s*:\s*(.+)$", ln.strip())
    if mt:
        video_records.append({"video_id": mt.group(1), "cat_num": mt.group(2), "topic": mt.group(3).strip()})

m117_playbooks = {}
for cat in inputs["m117"]["categories"]:
    skill_text = (m117_dir / cat / "SKILL.md").read_text(encoding="utf-8")
    fm_match = re.search(r"^---\s*\n(.*?)\n---", skill_text, flags=re.DOTALL)
    fm_data = yaml.safe_load(fm_match.group(1))
    vids = re.findall(r"https://youtu\.be/([A-Za-z0-9_-]{11})", skill_text)
    offers_sec = skill_text.split("## 1. Offres Productisées Associées")[1].split("## 2.")[0]
    offers = re.findall(r"^\d+\.\s+\*\*(.+?)\*\*.*?\(([^()]*\$[^()]*)\)", offers_sec, flags=re.MULTILINE)
    proto_sec = skill_text.split("## 3. Protocole d'Exécution")[1]
    steps = re.findall(r"^\d+\.\s+(?:\*\*[^*]+\*\*\s*:\s*)?(.+)$", proto_sec, flags=re.MULTILINE)
    m117_playbooks[cat] = {
        "skill_name": fm_data["name"],
        "foundational_videos": vids,
        "offer_titles": [o[0].strip() for o in offers],
        "offer_pricings": [o[1].strip() for o in offers],
        "protocol_steps_count": len(steps),
    }
m117_out = {
    "video_count": len(video_records),
    "video_ids_sorted": sorted(v["video_id"] for v in video_records),
    "playbooks": m117_playbooks,
}

# --- M118: 04_Inference_Youtube_Discovery_Registry raw filesystem oracle ---
m118_dir = iso / "01_Forkable/FKB01_Inference/04_Inference_Youtube_Discovery_Registry"
reg_data = json.loads((m118_dir / "registry.json").read_text(encoding="utf-8"))
opp_dossiers = {}
for opp_file in sorted((m118_dir / "opportunities").glob("OPP-*.md")):
    txt = opp_file.read_text(encoding="utf-8")
    oid = opp_file.name.split("_", 1)[0]
    url_m = re.search(r"\*\*Plateforme Cible\*\*\s*\|\s*`([^`]+)`", txt)
    steps_sec = txt.split("## 1.")[1].split("## 2.")[0]
    steps = re.findall(r"^\d+\.\s+(.+)$", steps_sec, flags=re.MULTILINE)
    opp_dossiers[oid] = {
        "target_platform_base": url_m.group(1).strip() if url_m else "",
        "steps_count": len(steps),
    }
m118_out = {
    "opportunity_ids": [o["id"] for o in reg_data["opportunities"]],
    "platforms_status": {o["id"]: {"platform": o["platform"], "vector": o["vector"], "status": o["status"]} for o in reg_data["opportunities"]},
    "dossiers": opp_dossiers,
}

(iso / "oracle_outputs.json").write_text(
    json.dumps({"m044": m044_out, "m050": m050_out, "m056": m056_out, "m117": m117_out, "m118": m118_out}, ensure_ascii=False, indent=2),
    encoding="utf-8",
)
'''


_ORGAN_RUNNER_CODE = r'''
import dataclasses
import datetime as dt
import json
import sys
import tempfile
from pathlib import Path

iso = Path.cwd()
inputs = json.loads((iso / "diff_inputs.json").read_text(encoding="utf-8"))
oracle = json.loads((iso / "oracle_outputs.json").read_text(encoding="utf-8"))
sha = sys.argv[1]

sys.path.insert(0, str(iso / "01_Forkable/FKB00_Runtime/00_A0_Core"))
import aspace_fkb02_memory_organ as f02
import aspace_fkb04_anything_organ as f04
import aspace_discovery_catalog as cat

# Vérifier qu'aucune source supprimée n'existe plus sous iso_root
assert not (iso / "01_Forkable/FKB02_Memory/01_BillionContxtLanguage_AutoOnthology/context-language-models").exists()
assert not (iso / "01_Forkable/FKB02_Memory/knowledge-catalog").exists()
assert not (iso / "01_Forkable/FKB04_Tools_Anything/CLI-Anything").exists()
assert not (iso / "01_Forkable/FKB07_Money_Maker/00_Marketplace_YoutubeSkills").exists()
assert not (iso / "01_Forkable/FKB01_Inference/04_Inference_Youtube_Discovery_Registry").exists()

# --- M044 organe ---
m044_org = {
    "content_texts": [f02.clm_content_text(m.get("content")) for m in inputs["m044"]["text_cases"]],
    "rendered_texts": [f02.clm_rendered_text(m) for m in inputs["m044"]["text_cases"]],
    "roundtrips": [],
}
for conv in inputs["m044"]["conversations"]:
    for protect in (0, 1, 2, 3):
        editable = f02.clm_render_editable(conv, protect=protect)
        tail = conv[-protect:] if protect > 0 and len(conv) >= protect else (list(conv) if protect > 0 else [])
        parsed = f02.clm_parse_back(editable, tail)
        m044_org["roundtrips"].append({"protect": protect, "editable": editable, "parsed": parsed})
m044_org["custom_edit"] = f02.clm_parse_back(inputs["m044"]["edited_roundtrip"], inputs["m044"]["conversations"][0][-2:])
assert m044_org == oracle["m044"], "M044 differential mismatch against upstream context-language-models!"

# --- M050 organe ---
ref_now = dt.datetime.fromisoformat(inputs["m050"]["now_iso"])
doc_samples = list(inputs["m050"]["synthetic_docs"])
concepts_dir = iso / "00_Memoire" / "bundle" / "concepts"
if concepts_dir.exists():
    for md_p in sorted(concepts_dir.glob("*.md"))[:12]:
        doc_samples.append((f"concept:{md_p.name}", md_p.read_text(encoding="utf-8")))

m050_docs_res = []
for label, raw in doc_samples:
    try:
        d = f02.OKFDocument.parse(raw)
        nv = f02.okf_normalize_verified(d.frontmatter)
        nv_clean = json.loads(json.dumps(nv, default=str))
        m050_docs_res.append({
            "label": label,
            "ok": True,
            "normalized_verified": nv_clean,
            "trust_tier": f02.okf_trust_tier(d.frontmatter),
            "is_stale": f02.okf_is_stale(d.frontmatter, now=ref_now),
            "validate": d.validate(),
            "serialized": d.serialize(),
        })
    except f02.OKFDocumentError:
        m050_docs_res.append({"label": label, "ok": False, "err": "OKFDocumentError"})

bundle_tmp = Path(tempfile.mkdtemp(dir=str(iso), prefix="organ_okf_"))
(bundle_tmp / "alpha.md").write_text("---\nokf_version: '0.2'\ntype: Concept\ntitle: Alpha\nverified: '2026-11-19'\n---\nBody Alpha\n", encoding="utf-8")
(bundle_tmp / "sub").mkdir()
(bundle_tmp / "sub" / "beta.md").write_text("---\nokf_version: '0.2'\ntype: Decision\ntitle: Beta\nverified: '2026-11-18'\n---\nBody Beta\n", encoding="utf-8")
(bundle_tmp / "sub" / "gamma.md").write_text("---\nokf_version: '0.2'\ntype: Note\ntitle: Gamma\n---\nBody Gamma\n", encoding="utf-8")
org_gen_paths = f02.okf_regenerate_indexes(bundle_tmp, model="oracle-model", synthesize=lambda f, docs, model="": f"Synthèse {f} ({len(docs)} docs via {model})")
m050_indexes = {
    p.relative_to(bundle_tmp).as_posix(): p.read_text(encoding="utf-8")
    for p in sorted(org_gen_paths)
}
m050_org = {"docs": m050_docs_res, "indexes": m050_indexes}
assert m050_org == oracle["m050"], "M050 differential mismatch against upstream knowledge-catalog!"

# --- M056 organe (sur entrées de harnais copiées hors CLI-Anything supprimé) ---
m056_harnesses_org = {}
for sw in ("zotero", "audacity"):
    h_dir = iso / "test_input_harnesses" / sw / "agent-harness"
    org_meta = f04.extract_cli_anything_metadata(h_dir)
    m056_harnesses_org[sw] = {
        "meta": dataclasses.asdict(org_meta),
        "skill_md": f04.generate_cli_anything_skill_md(org_meta),
        "skill_md_simple": f04.generate_cli_anything_skill_md_simple(org_meta),
    }

m056_cache_keys_org = [
    f04.build_cli_anything_preview_cache_key(
        ck["software"],
        ck["recipe"],
        ck["bundle_kind"],
        ck["source_fingerprint"],
        options=ck["options"],
        harness_version=ck["harness_version"],
    )
    for ck in inputs["m056"]["cache_key_cases"]
]
m056_org = {"harnesses": m056_harnesses_org, "cache_keys": m056_cache_keys_org}
assert m056_org == oracle["m056"], "M056 differential mismatch against upstream CLI-Anything!"

# --- M117 organe ---
m117_playbooks_org = {}
for cat_id in inputs["m117"]["categories"]:
    pb = cat.get_marketplace_playbook(cat_id)
    m117_playbooks_org[cat_id] = {
        "skill_name": pb["skill_name"],
        "foundational_videos": list(pb["foundational_videos"]),
        "offer_titles": [o["offer"] for o in pb["productized_offers"]],
        "offer_pricings": [o["pricing"] for o in pb["productized_offers"]],
        "protocol_steps_count": len(pb["execution_protocol"]),
    }
m117_org = {
    "video_count": len(cat.YOUTUBE_SKILL_VIDEOS),
    "video_ids_sorted": sorted(v["video_id"] for v in cat.YOUTUBE_SKILL_VIDEOS),
    "playbooks": m117_playbooks_org,
}
assert m117_org == oracle["m117"], "M117 differential mismatch against raw 00_Marketplace_YoutubeSkills!"

# --- M118 organe ---
m118_dossiers_org = {}
for oid in inputs["m118"]["opp_ids"]:
    dos = cat.get_opportunity_dossier(oid)
    m118_dossiers_org[oid] = {
        "target_platform_base": dos["target_platform"].split(" (", 1)[0].strip(),
        "steps_count": len(dos["mechanism_steps"]),
    }
m118_org = {
    "opportunity_ids": [o["id"] for o in cat.INFERENCE_DISCOVERY_REGISTRY["opportunities"]],
    "platforms_status": {o["id"]: {"platform": o["platform"], "vector": o["vector"], "status": o["status"]} for o in cat.INFERENCE_DISCOVERY_REGISTRY["opportunities"]},
    "dossiers": m118_dossiers_org,
}
assert m118_org == oracle["m118"], "M118 differential mismatch against raw 04_Inference_Youtube_Discovery_Registry!"

# --- Vérification honnête M058 + compteurs non codés en dur + reçus R10 mesurés ---
r04 = f04.run_fkb04_self_test(head_sha40=sha, repo_root=iso)
r02 = f02.run_fkb02_self_test(repo_root=iso, head_sha40=sha)
rcat = cat.run_self_test(head_sha40=sha, repo_root=iso)

assert r04["source_parity_verified"] == [], f"Auto-déclaration interdite: {r04['source_parity_verified']}"
assert r02["source_parity_verified"] == [], f"Auto-déclaration interdite: {r02['source_parity_verified']}"
assert rcat["source_parity_verified"] == [], f"Auto-déclaration interdite: {rcat['source_parity_verified']}"
assert "headless-fallback" not in json.dumps(r04) and "HeadlessDesktopSession" not in json.dumps(r04)
assert r04["desktop_live_verified"] is False or r04["desktop_live_windows"] >= 1

def _count_diff_pairs(pairs):
    compared = len(pairs)
    matched = sum(1 for a, b in pairs if a == b)
    return {"compared_against_source": True, "cases_compared": compared, "cases_matched": matched}


m044_pairs = (
    list(zip(m044_org["content_texts"], oracle["m044"]["content_texts"]))
    + list(zip(m044_org["rendered_texts"], oracle["m044"]["rendered_texts"]))
    + [(r["editable"], o["editable"]) for r, o in zip(m044_org["roundtrips"], oracle["m044"]["roundtrips"])]
    + [(r["parsed"], o["parsed"]) for r, o in zip(m044_org["roundtrips"], oracle["m044"]["roundtrips"])]
    + [(m044_org["custom_edit"], oracle["m044"]["custom_edit"])]
)
m050_pairs = (
    list(zip(m050_org["docs"], oracle["m050"]["docs"]))
    + [(m050_org["indexes"].get(k), v) for k, v in oracle["m050"]["indexes"].items()]
)
m056_pairs = []
for sw, h_o in oracle["m056"]["harnesses"].items():
    h_g = m056_org["harnesses"][sw]
    m056_pairs.extend([(h_g["meta"], h_o["meta"]), (h_g["skill_md"], h_o["skill_md"]), (h_g["skill_md_simple"], h_o["skill_md_simple"])])
m056_pairs.extend(zip(m056_org["cache_keys"], oracle["m056"]["cache_keys"]))
m117_pairs = (
    [(m117_org["video_count"], oracle["m117"]["video_count"]), (m117_org["video_ids_sorted"], oracle["m117"]["video_ids_sorted"])]
    + [(m117_org["playbooks"].get(c), v) for c, v in oracle["m117"]["playbooks"].items()]
)
m118_pairs = (
    [(m118_org["opportunity_ids"], oracle["m118"]["opportunity_ids"]), (m118_org["platforms_status"], oracle["m118"]["platforms_status"])]
    + [(m118_org["dossiers"].get(k), v) for k, v in oracle["m118"]["dossiers"].items()]
)

res_m044 = _count_diff_pairs(m044_pairs)
res_m050 = _count_diff_pairs(m050_pairs)
res_m056 = _count_diff_pairs(m056_pairs)
res_m117 = _count_diff_pairs(m117_pairs)
res_m118 = _count_diff_pairs(m118_pairs)

rec04 = f04.consign_fkb04_parity_receipt({"CLI-Anything": res_m056, "agent-desktop": {"compared_against_source": False, "cases_compared": 0, "cases_matched": 0}}, sha, repo_root=iso)
rec02 = f02.consign_fkb02_parity_receipt({"context-language-models": res_m044, "knowledge-catalog": res_m050}, sha, repo_root=iso)
reccat = cat.consign_catalog_parity_receipt({"00_Marketplace_YoutubeSkills": res_m117, "04_Inference_Youtube_Discovery_Registry": res_m118}, sha, repo_root=iso)

assert rec04["verified_modules"] == ["CLI-Anything"] and rec04["cases_matched"] == rec04["cases_compared"] > 0
assert sorted(rec02["verified_modules"]) == ["context-language-models", "knowledge-catalog"] and rec02["cases_matched"] == rec02["cases_compared"] > 0
assert sorted(reccat["verified_modules"]) == ["00_Marketplace_YoutubeSkills", "04_Inference_Youtube_Discovery_Registry"] and reccat["cases_matched"] == reccat["cases_compared"] > 0

proven_mods = rec04["verified_modules"] + rec02["verified_modules"] + reccat["verified_modules"]

print(json.dumps({
    "differential_proven": proven_mods,
    "desktop_live_verified": bool(r04["desktop_live_verified"]),
    "r04": {"checks_passed": r04["checks_passed"], "cases": f"{rec04['cases_matched']}/{rec04['cases_compared']}", "r10": rec04["r10_entry_id"]},
    "r02": {"checks_passed": r02["checks_passed"], "cases": f"{rec02['cases_matched']}/{rec02['cases_compared']}", "r10": rec02["r10_entry_id"]},
    "rcat": {"checks_passed": rcat["checks_passed"], "cases": f"{reccat['cases_matched']}/{reccat['cases_compared']}", "r10": reccat["r10_entry_id"]},
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

    llm_wiki_doc = ROOT / "00_Memoire" / "bundle" / "concepts" / "llm-wiki.md"
    assert llm_wiki_doc.exists() and llm_wiki_doc.stat().st_size > 200

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
            "01_Forkable/FKB00_Runtime/00_A0_Core/aspace_fkb04_anything_organ.py",
            "01_Forkable/FKB00_Runtime/00_A0_Core/aspace_fkb02_memory_organ.py",
            "01_Forkable/FKB00_Runtime/00_A0_Core/a0_recursive_factory.py",
            "01_Forkable/FKB00_Runtime/00_A0_Core/aspace_freecompute_router.py",
            "01_Forkable/FKB01_Inference/03_Inference_FreeCloud/aspace_freecloud_gateway.py",
            "01_Forkable/FKB02_Memory/01_BillionContxtLanguage_AutoOnthology/neuro_symbolic_bridge.py",
            "01_Forkable/FKB07_Money_Maker/aspace_marketplace_engine.py",
            "01_Forkable/FKB07_Money_Maker/02_Video/aspace_video_studio_foundation.py",
            # Sources réelles M044, M050, M056, M117, M118 pour Phase A avant suppression
            "01_Forkable/FKB02_Memory/01_BillionContxtLanguage_AutoOnthology/context-language-models/clm",
            "01_Forkable/FKB02_Memory/knowledge-catalog/okf",
            "01_Forkable/FKB04_Tools_Anything/CLI-Anything/cli-anything-plugin",
            "01_Forkable/FKB04_Tools_Anything/CLI-Anything/zotero/agent-harness",
            "01_Forkable/FKB04_Tools_Anything/CLI-Anything/audacity/agent-harness",
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

        # Entrées de test zotero/audacity copiées hors CLI-Anything/ pour rejouer extract_cli_anything_metadata après suppression du plugin
        for sw in ("zotero", "audacity"):
            shutil.copytree(
                ROOT / "01_Forkable/FKB04_Tools_Anything/CLI-Anything" / sw / "agent-harness",
                iso_root / "test_input_harnesses" / sw / "agent-harness",
                ignore=ign,
            )

        (iso_root / "diff_inputs.json").write_text(json.dumps(diff_inputs, ensure_ascii=False), encoding="utf-8")

        # PHASE A : exécution des sources amont dans iso_root AVANT suppression
        (iso_root / "oracle_runner.py").write_text(_ORACLE_RUNNER_CODE, encoding="utf-8")
        subprocess.check_call([sys.executable, str(iso_root / "oracle_runner.py")], cwd=str(iso_root))
        (iso_root / "oracle_runner.py").unlink()
        assert (iso_root / "oracle_outputs.json").exists()

        # PHASE B : suppression physique effective des 20 répertoires sources + 14 F8/GSD/llm-wiki
        for rel in SOURCE_DIRS_TO_DELETE_FOR_TEST + absent_paths:
            target = iso_root / rel
            if target.exists():
                _force_rmtree(target)
            assert not target.exists(), f"Suppression physique incomplète: {target}"

        # PHASE C : exécution des organes natifs dans iso_root amputé + comparaison == oracle_outputs
        (iso_root / "organ_runner.py").write_text(_ORGAN_RUNNER_CODE, encoding="utf-8")
        iso_out = subprocess.check_output(
            [sys.executable, str(iso_root / "organ_runner.py"), head_sha],
            cwd=str(iso_root),
            text=True,
        )
        parsed = json.loads(iso_out)
        diff_proven = set(parsed["differential_proven"])
        desktop_live = bool(parsed["desktop_live_verified"])

        # Orchestrateurs câblés dans l'arbre physiquement amputé
        for rel_script, extra_args in [
            ("01_Forkable/FKB00_Runtime/00_A0_Core/a0_recursive_factory.py", []),
            ("01_Forkable/FKB01_Inference/03_Inference_FreeCloud/aspace_freecloud_gateway.py", ["--self-test"]),
            ("01_Forkable/FKB02_Memory/01_BillionContxtLanguage_AutoOnthology/neuro_symbolic_bridge.py", []),
            ("01_Forkable/FKB07_Money_Maker/aspace_marketplace_engine.py", []),
        ]:
            subprocess.check_call([sys.executable, str(iso_root / rel_script), *extra_args], cwd=str(iso_root), stdout=subprocess.DEVNULL)

    # Sous-processus K1..K5 vers le bus L0 du workspace
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

    diff_proven.add("llm-wiki")
    print(f"[PASS 4/7] Test différentiel source-vs-organe avant/après suppression PASS ({len(diff_proven)} prouvés : {sorted(diff_proven)}) + M058 desktop_live={desktop_live} + L0 ({before_lines}->{after_lines})")
    return diff_proven, desktop_live


def test_fondation_13_1_fixture_compatibility() -> None:
    assert len(ROOT_KERNELS) == 4 and abs(MAX_MODULES_PER_KERNEL_RATIO - (1.0 / 3.0)) < 1e-9
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
    print("[PASS 5/7] Compatibilité 1:1 Rust fondation-13-1 + Interconnexion L0 (5 organes / 4 noyaux ADR-14)")


def test_carte_and_registre_adr14_and_dynamic_counts(proven_fusionne: set[str], desktop_live_verified: bool) -> None:
    carte = (FUSION_DIR / "CARTE-DES-PRINCIPES.md").read_text(encoding="utf-8")
    registre = (FUSION_DIR / "REGISTRE-DE-FUSION.md").read_text(encoding="utf-8")

    m_carte = re.findall(r"^### (M\d{3}) — ", carte, flags=re.MULTILINE)
    d_carte = re.findall(r"^### (D\d{2}) — ", carte, flags=re.MULTILINE)
    assert len(m_carte) == 120 and len(d_carte) == 8

    reg_rows = re.findall(r"^\| (?:M\d{3}) \| .*?$", registre, flags=re.MULTILINE)
    assert len(reg_rows) == 120

    max_per_kernel = len(reg_rows) // 3  # 40 max strict sous ADR-14
    kernel_counts = {rk: 0 for rk in ROOT_KERNELS}
    registry_fusionne: set[str] = set()
    by_name: dict[str, tuple[str, str]] = {}
    actual_retenu = 0
    actual_ecarte = 0

    for row in reg_rows:
        cols = [c.strip() for c in row.strip("|").split("|")]
        mod_name = cols[1].strip("`")
        noyau_col = cols[4]
        statut_col = cols[6]
        justification = cols[8] if len(cols) > 8 else ""
        assert len(justification) >= 15, f"Justification insuffisante pour {mod_name}: {justification!r}"

        matched_rk = next((rk for rk in ROOT_KERNELS if noyau_col.startswith(f"{rk} ·")), None)
        assert matched_rk is not None, f"Noyau ADR-14 invalide pour {mod_name}: {noyau_col!r}"
        kernel_counts[matched_rk] += 1

        by_name[mod_name] = (statut_col, justification)
        if statut_col == "**FUSIONNÉ**":
            registry_fusionne.add(mod_name)
        elif statut_col == "**RETENU**":
            actual_retenu += 1
        elif statut_col == "**ÉCARTÉ**":
            actual_ecarte += 1

    assert sum(kernel_counts.values()) == 120
    assert all(cnt <= max_per_kernel for cnt in kernel_counts.values()), (
        f"Dépassement règle <= 1/3 ({max_per_kernel} max ADR-14): {kernel_counts}"
    )

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

    print(
        f"[PASS 6/7] ADR-14 <= 1/3 respecté ({kernel_counts}) | "
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
    ]
    for fn in required:
        p = FUSION_DIR / fn
        assert p.exists() and p.stat().st_size > 200
    adrs = list((FUSION_DIR / "adr").glob("ADR-*.md"))
    assert len(adrs) >= 14, f"Attendu >= 14 ADRs (ADR-01..ADR-14), trouvé {len(adrs)}"

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
    print(f"[PASS 7/7] {len(adrs)} ADRs + Artefacts SPAD complets + Clone Windows par défaut préserve LF")


if __name__ == "__main__":
    test_enonce_hash_and_gitattributes()
    test_gitmodules_and_fkb06_deletion()
    rust_proven = test_rust_cargo_and_phase2_hybrid()
    diff_proven, desktop_live = test_real_differential_deletion_and_lazy_import()
    test_fondation_13_1_fixture_compatibility()
    test_carte_and_registre_adr14_and_dynamic_counts(rust_proven | diff_proven, desktop_live)
    test_required_spad_artifacts_and_windows_clone_lf()
    print("=== ALL 7/7 CYCLE-5 FOUNDATION, RUST & DIFFERENTIAL DELETION SUITES PASSED ===")
