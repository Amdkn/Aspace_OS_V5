#!/usr/bin/env python3
"""
test_foundation_deletion_suite.py — Suite de vérification Cycle 2 de la Fondation A'Space (ÉNONCÉ §1).

Rejoue de façon 100 % déterministe :
  1. L'intégrité SHA-256 de 00_Memoire/bundle/fusion/FUSION-ENONCE.md.
  2. La purge effective des 8 doublons FKB06 dans .gitmodules et l'alignement 1:1
     len(.gitmodules) == len(distinct_urls) == len(gitlinks 160000) == 101.
  3. Le test de suppression réel (ÉNONCÉ (3)) :
     - Absence physique ET Git de tous les modules F8 dé-pointés + get-shit-done dans 01_Forkable/.
     - Exécution réelle des 5 Noyaux natifs (K1..K5) sans ces répertoires sources,
       et vérification que `github-actions-freevps` (FreeVPS ÉCARTÉ) est bien retiré.
  4. L'alignement 1:1 des contrats L0 (`aspace_foundation_kernel.py`) avec `fondation-13-1`
     (`src/lib.rs`, `src/router.rs`, `src/memory.rs`), incluant le rejeu des fixtures réelles
     `fondation-13-1/tests/fixtures/anchor-{001,002,026}.json` et les rejets motivés.
  5. La non-régression dynamique de `neuro_symbolic_bridge.py` (zéro sortie statique codée en dur)
     et du coordinateur honnête F4 `aspace_video_studio_foundation.py` (`PARTIEL`).
  6. La complétude de CARTE-DES-PRINCIPES.md (120+8), REGISTRE-DE-FUSION.md (120 lignes, ratio < 1/3),
     et l'absence d'erreurs de surévaluation sur M005/M105/M106/M112/M114/M115/M116.
"""

from __future__ import annotations

import datetime as dt
import json
import re
import subprocess
import sys
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
    EventJournal,
    FoundationKernelRegistry,
    KERNEL_IDS,
    R10Ledger,
    R10_SCHEMA,
    validate_citation,
    verify_frozen_enonce,
)
import a0_recursive_factory  # noqa: E402
import aspace_freecompute_router  # noqa: E402
import aspace_freecloud_gateway  # noqa: E402
import neuro_symbolic_bridge  # noqa: E402
import aspace_marketplace_engine  # noqa: E402
from aspace_video_studio_foundation import (  # noqa: E402
    CANONICAL_VIDEO_ENGINES,
    PURGED_FKB06_DUPLICATES,
    UnifiedVideoStudioFoundation,
)

FUSION_DIR = ROOT / "00_Memoire" / "bundle" / "fusion"
FIXTURES_DIR = CORE_DIR / "fondation-13-1" / "tests" / "fixtures"


def test_enonce_hash() -> None:
    digest = verify_frozen_enonce(ROOT)
    print(f"[PASS 1/7] FUSION-ENONCE.md SHA-256 intact : {digest}")


def test_gitmodules_and_fkb06_deletion() -> None:
    gm_text = (ROOT / ".gitmodules").read_text(encoding="utf-8")
    paths = re.findall(r"^\s*path\s*=\s*(.+)$", gm_text, flags=re.MULTILINE)
    urls = re.findall(r"^\s*url\s*=\s*(.+)$", gm_text, flags=re.MULTILINE)
    assert len(paths) == 101, f"Attendu 101 entrées .gitmodules, trouvé {len(paths)}"
    assert len(set(u.strip().lower() for u in urls)) == 101, "Doublons d'URL restants dans .gitmodules"
    assert not any("FKB06_Video_SaaS" in p or "FKB02_Video_SaaS" in p for p in paths)

    out = subprocess.check_output(["git", "ls-files", "--stage", "01_Forkable"], cwd=str(ROOT), text=True)
    gitlinks = [ln.split("\t")[1] for ln in out.splitlines() if ln.startswith("160000 ")]
    assert len(gitlinks) == 101
    assert set(p.strip() for p in paths) == set(gitlinks)
    for eng in PURGED_FKB06_DUPLICATES:
        assert eng in CANONICAL_VIDEO_ENGINES
    print("[PASS 2/7] Purge doublons FKB06 (109 -> 101) & alignement 1:1 .gitmodules == gitlinks 160000")


def test_real_deletion_and_5_kernels_execution() -> None:
    # Vérifier l'absence réelle (Git ET disque) des 12 modules F8 + get-shit-done dans 01_Forkable
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
    ]
    out = subprocess.check_output(["git", "ls-files", "--stage", "01_Forkable"], cwd=str(ROOT), text=True)
    gitlinks = [ln.split("\t")[1] for ln in out.splitlines() if ln.startswith("160000 ")]
    for rel in absent_paths:
        assert rel not in gitlinks, f"Gitlink non retiré: {rel}"
        assert not (ROOT / rel).exists(), f"Répertoire résiduel encore présent sur disque: {rel}"

    # Vérifier FreeVPS retiré du routeur K2
    assert not any(p.id == "github-actions-freevps" for p in aspace_freecompute_router.PROVIDERS), (
        "FreeVPS (ÉCARTÉ ADR-08) est encore présent dans aspace_freecompute_router.PROVIDERS"
    )

    # Exécuter les 5 noyaux natifs sans aucun des répertoires supprimés
    head_sha = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=str(ROOT), text=True).strip()
    k1_res = a0_recursive_factory.run_a0_recursive_cycle_demo()
    assert k1_res["l0_dispatch_seq"] >= 1

    k2_res = aspace_freecompute_router.select_compute("sheet_mutation", 15)
    assert k2_res["l0_dispatch_seq"] >= 1

    k3_res = aspace_freecloud_gateway.ROUTER.dispatch_chat_completion(
        {"model": "aspace-a0-auto", "messages": [{"role": "user", "content": "Smoke K3"}]}
    )
    assert k3_res["aspace_routing"]["l0_dispatch_seq"] >= 1

    bridge = neuro_symbolic_bridge.NeuroSymbolicBridge()
    c1 = bridge.ingest_chunk("AlphaEngine compiles KernelGraph via RigInfinity", "chunk_A")
    c2 = bridge.ingest_chunk("BetaValidator checks EpistemicCitation rules", "chunk_B")
    e1, r1 = bridge.compile_ontology(c1)
    e2, r2 = bridge.compile_ontology(c2)
    names_1 = {x["name"] for x in e1}
    names_2 = {x["name"] for x in e2}
    assert "AlphaEngine" in names_1 and "AlphaEngine" not in names_2
    assert "BetaValidator" in names_2 and "BetaValidator" not in names_1
    k4_ctx = bridge.generate_conditioning_context("chunk_A")
    assert k4_ctx["l0_dispatch_seq"] >= 1

    mp = aspace_marketplace_engine.AspaceMarketplaceEngine()
    k5_order = mp.dispatch_order_to_rig_infinity("MPLACE-C1-FDE-SPRINT", "TestOrg", head_sha40=head_sha)
    assert k5_order.status == "PRODUCTION_IN_PROGRESS_RIGINFINITY"

    j = EventJournal(signed_designs={"00_Memoire/bundle/fusion/SDD-FONDATION.md"})
    l = R10Ledger(valid_shas={head_sha})
    studio = UnifiedVideoStudioFoundation(j, l)
    vplan = studio.build_pipeline("CYCLE2", "saas_demo", head_sha)
    assert vplan.fusion_status == "PARTIEL"

    # Vérifier chaque entrypoint en sous-processus isolé (aucun héritage sys.path)
    for rel_script, extra_args in [
        ("01_Forkable/FKB00_Runtime/00_A0_Core/a0_recursive_factory.py", []),
        ("01_Forkable/FKB01_Inference/03_Inference_FreeCloud/aspace_freecloud_gateway.py", ["--self-test"]),
        ("01_Forkable/FKB02_Memory/01_BillionContxtLanguage_AutoOnthology/neuro_symbolic_bridge.py", []),
        ("01_Forkable/FKB07_Money_Maker/aspace_marketplace_engine.py", []),
        ("01_Forkable/FKB07_Money_Maker/02_Video/aspace_video_studio_foundation.py", []),
    ]:
        subprocess.check_call([sys.executable, str(ROOT / rel_script), *extra_args], cwd=str(ROOT), stdout=subprocess.DEVNULL)
    print("[PASS 3/7] Test de suppression réel (0 résidu F8/GSD) + exécution isolée K1..K5 sur L0")


def test_fondation_13_1_fixture_compatibility() -> None:
    """Rejoue les fixtures officielles anchor-001/002/026 de fondation-13-1 contre aspace_foundation_kernel."""
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
        assert stored["entry_id"] == a["entry_id"]

    # Vérifier le rejet sur modification du SHA court (Fautif #1) et réécriture (Fautif #4)
    fautif = dict(anchors[1])
    fautif["entry_id"] = "G-20261111-901"
    fautif["mission_id"] = "TEST-FAUTIF-1"
    fautif["sha"] = "22f374d"
    for bad_fn, expected_rule in [
        (lambda: ledger.validate_and_consign(fautif, now_utc=ref_now), "V3"),
        (lambda: ledger.validate_and_consign(anchors[1], now_utc=ref_now), "V7"),
    ]:
        try:
            bad_fn()
            raise AssertionError(f"Rejet {expected_rule} attendu non déclenché")
        except ContractViolation as exc:
            assert exc.rule == expected_rule, f"Attendu {expected_rule}, reçu {exc.rule}"

    # Vérifier EventJournal (router.rs R1..R8) + citation M1..M8 (memory.rs)
    journal = EventJournal(signed_designs={"plans/DESIGN-FONDATION-13-1-F1-3-PROJET.md (journal 806)"})
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
        now_utc=dt.datetime.fromisoformat("2026-11-11T07:00:00+00:00"),
    )
    assert evt["seq"] == 1

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
    res_cit = validate_citation(cit_md, ev)
    assert res_cit["status"] == "vérifié"
    print("[PASS 4/7] Compatibilité 1:1 avec fixtures Rust fondation-13-1 (V1-V8, R1-R8, M1-M8)")


def test_5_kernels_l0_registry() -> None:
    head_sha = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=str(ROOT), text=True).strip()
    now_dt = dt.datetime.now(dt.timezone.utc)
    now_iso = now_dt.isoformat()
    day_tag = now_dt.strftime("%Y%m%d")
    journal = EventJournal(signed_designs={"00_Memoire/bundle/fusion/SDD-FONDATION.md"})
    ledger = R10Ledger(valid_shas={head_sha})
    reg = FoundationKernelRegistry(repo_root=ROOT, journal=journal, ledger=ledger)
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
    print("[PASS 5/7] Interconnexion L0 vérifiée pour les 5 Noyaux K1..K5")


def test_carte_and_registre_completeness_and_honesty() -> None:
    carte = (FUSION_DIR / "CARTE-DES-PRINCIPES.md").read_text(encoding="utf-8")
    registre = (FUSION_DIR / "REGISTRE-DE-FUSION.md").read_text(encoding="utf-8")

    m_carte = re.findall(r"^### (M\d{3}) — ", carte, flags=re.MULTILINE)
    d_carte = re.findall(r"^### (D\d{2}) — ", carte, flags=re.MULTILINE)
    assert len(m_carte) == 120 and len(d_carte) == 8

    m_reg = re.findall(r"^\| (M\d{3}) \|", registre, flags=re.MULTILINE)
    assert len(m_reg) == 120

    # Vérifier le seuil §5.5
    cible_retenu = len(re.findall(r"\*\*RETENU\*\* \| \*\*RETENU\*\*", registre))
    cible_ecarte = len(re.findall(r"\*\*ÉCARTÉ\*\* \| \*\*ÉCARTÉ\*\*", registre))
    ratio = (cible_retenu + cible_ecarte) / 120.0
    assert ratio < (1.0 / 3.0)

    # Vérifier qu'aucun des 7 modules à dette nommée n'est surévalué FUSIONNÉ
    for mod in ("RigInfinity", "automaton", "cordis", "pi", "aspace-fiber-host", "fondation-13-1", "source-control-natif"):
        line = next((ln for ln in registre.splitlines() if f"| `{mod}` |" in ln), None)
        assert line is not None, f"Module absent du registre: {mod}"
        assert "| **PARTIEL** |" in line, f"Module {mod} doit être PARTIEL honnête, trouvé: {line}"

    # Vérifier qu'il n'y a plus de coquille dans PRD-FONDATION.md
    prd = (FUSION_DIR / "PRD-FONDATION.md").read_text(encoding="utf-8")
    assert "Modules `RETENU` justifiés en K2 (3)" not in prd
    print(f"[PASS 6/7] CARTE (120+8) & REGISTRE honnêtes | RETENU={cible_retenu}, ÉCARTÉ={cible_ecarte}, ratio={ratio:.1%}")


def test_required_spad_artifacts_exist() -> None:
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
    assert len(list((FUSION_DIR / "adr").glob("ADR-*.md"))) == 12
    print(f"[PASS 7/7] 7 artefacts SPAD + 12 fiches ADR présents dans {FUSION_DIR}")


if __name__ == "__main__":
    test_enonce_hash()
    test_gitmodules_and_fkb06_deletion()
    test_real_deletion_and_5_kernels_execution()
    test_fondation_13_1_fixture_compatibility()
    test_5_kernels_l0_registry()
    test_carte_and_registre_completeness_and_honesty()
    test_required_spad_artifacts_exist()
    print("=== ALL 7/7 CYCLE-2 FOUNDATION & DELETION SUITES PASSED ===")
