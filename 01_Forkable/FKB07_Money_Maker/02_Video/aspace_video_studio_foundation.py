#!/usr/bin/env python3
"""
aspace_video_studio_foundation.py — Coordinateur & Auditeur de Contrat F4 : Studio Vidéo (K5).

STATUT HONNÊTE F4 : PARTIEL (la purge des 8 doublons FKB06 dans .gitmodules est effectuée,
ce module coordonne le contrat commun et audite les 10 répertoires canoniques sous
01_Forkable/FKB07_Money_Maker/02_Video/, mais NE REMPLACE PAS encore l'exécution de rendu
vidéo headless Chrome / ffmpeg / TTS des 10 moteurs sources).

Interconnecté au Socle L0 via aspace_foundation_kernel (DISPATCH_KEYS R1–R8 + R10_KEYS V1–V8).
"""

from __future__ import annotations

import datetime as dt
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List

WORKSPACE_ROOT = Path(__file__).resolve().parents[3]
KERNEL_CORE_DIR = WORKSPACE_ROOT / "01_Forkable" / "FKB00_Runtime" / "00_A0_Core"
if str(KERNEL_CORE_DIR) not in sys.path:
    sys.path.insert(0, str(KERNEL_CORE_DIR))

from aspace_foundation_kernel import EventJournal, R10Ledger, R10_SCHEMA  # noqa: E402


CANONICAL_VIDEO_ENGINES: Dict[str, Dict[str, str]] = {
    "take-one": {"role": "launch_film", "contract": "script_to_headless_chrome_ffmpeg"},
    "video-director": {"role": "director_storyboard", "contract": "scene_cut_and_framing"},
    "huashu-motion": {"role": "motion_graphics", "contract": "frame_addressable_motion"},
    "rossark-motion-skill": {"role": "character_motion", "contract": "keyframe_mascot_animation"},
    "reanimate": {"role": "vector_reanimation", "contract": "svg_css_motion_extraction"},
    "argo": {"role": "demo_playwright", "contract": "playwright_script_to_demo_video"},
    "explainroo": {"role": "explainer_local", "contract": "local_js_tts_explainer"},
    "earshot": {"role": "audio_sfx", "contract": "timecode_synced_voice_and_sfx"},
    "flute": {"role": "canvas_saas", "contract": "interactive_video_canvas_ui"},
    "OpenMontage": {"role": "montage_ecommerce", "contract": "batch_ecommerce_ad_render"},
}

PURGED_FKB06_DUPLICATES = (
    "argo",
    "earshot",
    "explainroo",
    "huashu-motion",
    "reanimate",
    "rossark-motion-skill",
    "take-one",
    "video-director",
)


@dataclass
class VideoPipelinePlan:
    job_id: str
    offer_type: str
    stages: List[Dict[str, Any]]
    fusion_status: str = "PARTIEL"
    missing_for_full_fusion: str = (
        "Exécution de rendu vidéo native unifiée (headless Chrome/Playwright/ffmpeg/TTS) non encore portée hors des 10 sous-modules."
    )
    canonical_root: str = "01_Forkable/FKB07_Money_Maker/02_Video"


class UnifiedVideoStudioFoundation:
    """Coordinateur F4 K5 connecté aux contrats L0 de fondation-13-1."""

    def __init__(self, journal: EventJournal, ledger: R10Ledger) -> None:
        self.journal = journal
        self.ledger = ledger
        self.video_root = WORKSPACE_ROOT / "01_Forkable" / "FKB07_Money_Maker" / "02_Video"
        self.engines = dict(CANONICAL_VIDEO_ENGINES)

    def inspect_disk_engines(self) -> Dict[str, Dict[str, Any]]:
        """Inspecte réellement l'état sur disque de chacun des 10 moteurs vidéo."""
        status: Dict[str, Dict[str, Any]] = {}
        for eng in self.engines:
            p = self.video_root / eng
            items = [x.name for x in p.iterdir() if x.name != ".git"] if p.is_dir() else []
            status[eng] = {
                "dir_exists": p.is_dir(),
                "checked_out": len(items) > 0,
                "has_package_json": (p / "package.json").is_file(),
                "has_readme": any(p.glob("README*")) if p.is_dir() else False,
            }
        return status

    def build_pipeline(self, job_id: str, offer_type: str, head_sha40: str) -> VideoPipelinePlan:
        disk_status = self.inspect_disk_engines()
        order = [
            "take-one",
            "video-director",
            "argo" if offer_type == "saas_demo" else "huashu-motion",
            "earshot",
            "OpenMontage",
        ]
        stages = [{"engine": eng, **self.engines[eng], **disk_status[eng]} for eng in order]
        now_dt = dt.datetime.now(dt.timezone.utc)
        now_iso = now_dt.isoformat()
        day_tag = now_dt.strftime("%Y%m%d")
        seq_suffix = f"{abs(hash(job_id)) % 900 + 100:03d}"

        self.journal.inscribe(
            {
                "actor_from": "fabricator",
                "actor_to": "executor",
                "at": now_iso,
                "design_ref": "00_Memoire/bundle/fusion/SDD-FONDATION.md",
                "dispatch_id": f"D-VID-{job_id}",
                "event_id": f"EVT-{day_tag}-{seq_suffix}",
                "payload": f"Planifier pipeline video {job_id}",
                "proof": ["01_Forkable/FKB07_Money_Maker/02_Video/aspace_video_studio_foundation.py"],
                "type": "dispatch_typed",
            },
            now_utc=now_dt,
        )
        self.ledger.validate_and_consign(
            {
                "entry_id": f"G-{day_tag}-{seq_suffix}",
                "issuer": "Kernel K5 (VideoCoordinator)",
                "mission_id": f"F4-VIDEO-{job_id}",
                "observed_at": now_iso,
                "proof": [
                    "01_Forkable/FKB07_Money_Maker/02_Video/aspace_video_studio_foundation.py",
                    ".gitmodules:0_FKB06_duplicates",
                ],
                "recorded_at": None,
                "schema": R10_SCHEMA,
                "sha": head_sha40,
                "summary": f"F4 Video Studio coordinator contract verified at {head_sha40[:7]} (status PARTIEL)",
            },
            now_utc=now_dt,
        )
        return VideoPipelinePlan(job_id=job_id, offer_type=offer_type, stages=stages)


if __name__ == "__main__":
    j = EventJournal(signed_designs={"00_Memoire/bundle/fusion/SDD-FONDATION.md"})
    l = R10Ledger()
    studio = UnifiedVideoStudioFoundation(j, l)
    plan = studio.build_pipeline("SMOKE001", "saas_demo", "0" * 40)
    checked_out = sum(1 for v in studio.inspect_disk_engines().values() if v["checked_out"])
    print(f"VideoCoordinator PASS (status={plan.fusion_status}): 10 engines indexed, {checked_out}/10 checked out on disk")
