#!/usr/bin/env python3
"""
aspace_video_studio_foundation.py — Coordinateur F4 & Organe Natif Vidéo (CORPS / Organe K5).

STATUT :
  - M095 `video-director` : porté 1:1 (`check_timeline.py` + fonctions d'analyse `qa_video.py`)
    et soumis à la vérification différentielle + anti-sabotage avant/après suppression physique.
  - Les 9 autres moteurs vidéo (`OpenMontage`, `argo`, `earshot`, `explainroo`, `flute`,
    `huashu-motion`, `reanimate`, `rossark-motion-skill`, `take-one`) restent `PARTIEL`
    sous contrat de coordination F4 (les 8 doublons FKB06 ont été purgés de `.gitmodules`).

Interconnecté au Socle L0 via aspace_foundation_kernel (DISPATCH_KEYS R1–R8 + R10_KEYS V1–V8).
"""

from __future__ import annotations

import datetime as dt
import json
import math
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from types import SimpleNamespace
from typing import Any, Dict, List, Optional, Tuple

WORKSPACE_ROOT = Path(__file__).resolve().parents[3]
KERNEL_CORE_DIR = WORKSPACE_ROOT / "01_Forkable" / "FKB00_Runtime" / "00_A0_Core"
if str(KERNEL_CORE_DIR) not in sys.path:
    sys.path.insert(0, str(KERNEL_CORE_DIR))

from aspace_foundation_kernel import (  # noqa: E402
    EventJournal,
    R10Ledger,
    consign_measured_l0_evidence,
    record_shared_l0_event,
    record_shared_l0_receipt,
)


CANONICAL_VIDEO_ENGINES: Dict[str, Dict[str, str]] = {
    "take-one": {"role": "launch_film", "contract": "script_to_headless_chrome_ffmpeg"},
    "video-director": {"role": "director_storyboard", "contract": "check_timeline_and_qa_video"},
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


# ===========================================================================
# 1. M095 video-director — Portage 1:1 de check_timeline.py & qa_video.py
# ===========================================================================

VD_HOOK_BY = 3.0
VD_TEXT_FLOORS: Dict[str, int] = {"hook": 84, "cta": 48, "term": 48}
VD_ANALYSIS_W = 192
VD_MIN_CONTRAST = 7.0


def vd_is_num(v: Any) -> bool:
    return isinstance(v, (int, float)) and not isinstance(v, bool)


def vd_norm(s: Any) -> str:
    return " ".join(re.sub(r"[^\w]+", " ", str(s).lower()).split())


def vd_read_time(text: Any) -> float:
    return max(1.5, 1.0 + 0.3 * len(str(text).split()))


def vd_validate_timeline(tl: Dict[str, Any]) -> Tuple[List[str], List[str]]:
    """Valide une timeline.json strictement à l'identique de check_timeline.py."""
    errors: List[str] = []
    warns: List[str] = []
    err, warn = errors.append, warns.append

    meta = tl.get("meta", {})
    for k in ("w", "h", "fps", "dur"):
        if not (vd_is_num(meta.get(k)) and meta[k] > 0):
            err(f"meta.{k} must be a positive number")
    if errors:
        return errors, warns
    dur, fps = float(meta["dur"]), float(meta["fps"])
    frame = 1.0 / fps
    clock = meta.get("clock")
    if clock not in ("music", "voice", "reads"):
        err('meta.clock must be "music", "voice" or "reads"')

    if clock == "music":
        if not vd_is_num(meta.get("bpm")):
            err("music clock needs meta.bpm")
        elif meta.get("loop"):
            beats_per_bar = int(str(meta.get("meter", "4/4")).split("/")[0])
            bar = beats_per_bar * 60.0 / float(meta["bpm"])
            n = dur / bar
            if abs(n - round(n)) * bar > 0.002:
                err(f"loop is {n:.3f} bars; a music loop must be whole bars ({bar:.4f} s each)")

    scenes = tl.get("scenes", [])
    if not scenes:
        err("no scenes")
    beat_names, beat_t = set(), {}
    prev_end = 0.0
    for i, s in enumerate(scenes):
        sid, a, b = s.get("id", f"#{i}"), s.get("start"), s.get("end")
        if not (vd_is_num(a) and vd_is_num(b) and a < b):
            err(f"scene {sid}: needs numeric start < end")
            continue
        if a - prev_end > frame:
            err(f"scene {sid}: gap {prev_end:.3f}-{a:.3f} s (empty frames read as loading)")
        prev_end = max(prev_end, b)
        beats = s.get("beats", {})
        items = beats.items() if isinstance(beats, dict) else enumerate(beats or [])
        for name, t in items:
            beat_names.add(f"{sid}.{name}")
            if vd_is_num(t):
                beat_t[f"{sid}.{name}"] = float(t)
            if not vd_is_num(t):
                err(f"beat {sid}.{name} is not a number (keep refs like cueRef in a separate field)")
            elif not 0 <= t <= dur:
                err(f"beat {sid}.{name} = {t} is outside the film")
            elif not a - frame <= t <= b + frame:
                warn(f"beat {sid}.{name} = {t} lies outside its scene {a}-{b}")
        if i < len(scenes) - 1:
            tr = s.get("transitionOut") or {}
            if not tr.get("why"):
                warn(f"scene {sid}: transitionOut has no 'why' (every seam needs a reason you can say)")
    if scenes and abs(prev_end - dur) > frame:
        err(f"scenes end at {prev_end:.3f} s but meta.dur is {dur:.3f} s")

    reads = list(tl.get("reads", [])) + [r for s in scenes for r in s.get("reads", [])]
    for r in reads:
        f, t = r.get("from"), r.get("to")
        if vd_is_num(f) and vd_is_num(t):
            if t - f < 0.6:
                warn(f"read '{r.get('what', '?')}' gets {t - f:.2f} s: too short to find, understand, register")

    for t in tl.get("cuts", []):
        if not (vd_is_num(t) and 0 < t < dur):
            err(f"cut {t} is outside the film")

    hero_raw = (tl.get("hero") or {}).get("t")
    if not vd_is_num(hero_raw):
        warn("no hero.t: name the one moment the film builds to")
    else:
        hero = float(hero_raw)
        if not 0 <= hero <= dur:
            err(f"hero.t = {hero} is outside the film")
        elif hero < 0.4 * dur:
            warn(f"hero moment at {hero:.2f} s ({hero / dur:.0%}): spent early?")
        sil = [x for x in tl.get("silences", []) if vd_is_num(x.get("from")) and vd_is_num(x.get("to"))]
        if not any(x["to"] <= hero + 0.05 and hero - x["to"] <= 4.0 for x in sil):
            warn("no planned silence in the 4 s before the hero moment")
        for x in sil:
            if x["to"] - x["from"] < 0.4:
                warn(f"silence {x['from']}-{x['to']} is under 0.4 s: it won't register")

    for c in tl.get("sfx", []):
        at = c.get("at")
        if isinstance(at, str) and "." in at and at not in beat_names and not at.split(".")[0] == "t":
            err(f"sfx at '{at}' refers to a beat that doesn't exist")

    for c in tl.get("captions", []):
        f, t, text = c.get("from"), c.get("to"), str(c.get("text", ""))
        if vd_is_num(f) and vd_is_num(t) and t > f:
            words = len(text.split())
            if t - f < 0.7:
                warn(f"caption '{text[:30]}' is on screen {t - f:.2f} s (< 0.7 s)")
            if words / (t - f) > 3.5:
                warn(f"caption '{text[:30]}' runs {words / (t - f):.1f} words/s (> 3.5)")

    texts = []
    for x in tl.get("texts", []):
        if not isinstance(x, dict):
            continue
        f = x.get("from") if vd_is_num(x.get("from")) else beat_t.get(x.get("in"))
        t = x.get("to") if vd_is_num(x.get("to")) else beat_t.get(x.get("out"))
        texts.append({**x, "from": f, "to": t})
        label = str(x.get("text", x.get("id", "?")))[:30]
        if f is not None and t is not None and t - f < vd_read_time(x.get("text", "")) - frame:
            warn(f"text '{label}' holds {t - f:.2f} s; it needs {vd_read_time(x.get('text', '')):.2f} s to be read")
        role, px = x.get("role"), x.get("px")
        if role in VD_TEXT_FLOORS:
            if not vd_is_num(px):
                warn(f"{role} '{label}' has no px: declare its rendered font size so the floor can be checked")
            elif px * 1080 / min(meta["w"], meta["h"]) < VD_TEXT_FLOORS[role]:
                err(f"{role} '{label}' is {px} px: below the {VD_TEXT_FLOORS[role]} px floor (at a 1080 short side)")

    def first(role: str) -> Optional[float]:
        ts = [x["from"] for x in texts if x.get("role") == role and x["from"] is not None]
        return min(ts) if ts else None

    hook, cta, waiver = first("hook"), first("cta"), meta.get("hookWaiver")
    if hook is None or hook > VD_HOOK_BY:
        msg = f"hook text first legible at {hook:.2f} s" if hook is not None else "no texts[] entry with role 'hook'"
        msg += f": by {VD_HOOK_BY:g} s, sound off, large type must say what this is"
        (warn if waiver else err)(msg + (f" (waived: {waiver})" if waiver else ""))
    if cta is not None and cta > VD_HOOK_BY:
        (warn if waiver else err)(
            f"CTA first appears at {cta:.2f} s: show it by {VD_HOOK_BY:g} s too (it can return at the end)"
        )

    vo = tl.get("vo")
    said = vd_norm(
        " ".join(
            str(l.get("text") or " ".join(str(w.get("w", "")) for w in l.get("words", [])))
            for l in vo or []
        )
    )
    shown = vd_norm(" ".join(str(c.get("text", "")) for c in list(tl.get("captions", [])) + texts))
    terms = tl.get("terms") or []
    if not terms:
        warn("no terms: list the 1-3 words this audience would search for (the subject's name, key properties)")
    for term in terms:
        hit = lambda text: re.search(r"\b" + re.escape(vd_norm(term)), text) is not None
        if not hit(said) and not hit(shown):
            err(f"term '{term}' is never said or shown: name it right after the intuition it labels")
        elif vo and not hit(said):
            warn(f"term '{term}' is shown but never said")
        elif not hit(shown):
            warn(f"term '{term}' is said but never on screen: muted viewers miss it")

    vo_meta = meta.get("vo") if isinstance(meta.get("vo"), dict) else {}
    status = str(vo_meta.get("status", "")) + " " + " ".join(str(l.get("status", "")) for l in vo or [])
    if vo and "ESTIMATED" in status.upper():
        warn("VO timings are ESTIMATED: replace with real word timestamps before stills (phase 3)")
    for line in vo or []:
        ts = [w.get("t") for w in line.get("words", []) if vd_is_num(w.get("t"))]
        if ts != sorted(ts):
            err(f"VO line {line.get('id', '?')}: word times are not increasing")

    return errors, warns


def vd_check_timeline_cli(argv: List[str]) -> Tuple[int, str]:
    """Point d'entrée CLI 1:1 de check_timeline.py retournant `(exit_code, stdout)`."""
    if len(argv) != 2:
        return 1, "Usage: check_timeline.py timeline.json\n"
    tl = json.loads(Path(argv[1]).read_text(encoding="utf-8"))
    errors, warns = vd_validate_timeline(tl)
    lines = [f"ERROR {e}" for e in errors] + [f"WARN  {w}" for w in warns] + [f"{len(errors)} error(s), {len(warns)} warning(s)"]
    return (1 if errors else 0), "\n".join(lines) + "\n"


def vd_runs(mask: Any) -> List[Tuple[int, int]]:
    out, start = [], None
    for i, m in enumerate(mask):
        if m and start is None:
            start = i
        elif not m and start is not None:
            out.append((start, i))
            start = None
    if start is not None:
        out.append((start, len(mask)))
    return out


def vd_analyse_picture(st: Dict[str, Any], fps: float, args: Any) -> Dict[str, Any]:
    import numpy as np

    d, skip, n = st["d"], st["skip"], st["n"]
    res: Dict[str, Any] = {}
    med = float(np.median(d[1:])) if n > 2 else 0.0

    t_flash = max(2.0, 4 * med)
    flashes = [
        i
        for i in range(1, n - 1)
        if d[i] > t_flash and d[i + 1] > t_flash and skip[i] < 0.35 * min(d[i], d[i + 1])
    ]
    flash_frames = set(flashes) | {i + 1 for i in flashes}

    cuts = []
    for i in range(1, n):
        if i in flash_frames:
            continue
        lo, hi = max(1, i - 15), min(n, i + 16)
        local = np.concatenate([d[lo:i], d[i + 1 : hi]])
        lm = float(np.median(local)) if local.size else 0.0
        if d[i] > max(6.0, 3.5 * (lm + 0.5)):
            cuts.append(i)
    pops = [
        i
        for i in range(1, n - 1)
        if i not in flash_frames and i not in cuts and d[i] > 2.0 and d[i] > 3 * max(d[i - 1], d[i + 1])
    ]

    still = d < args.freeze_eps
    if n:
        still[0] = False
    frozen = [(a, b) for a, b in vd_runs(still) if (b - a + 1) / fps >= args.freeze]
    flat = [(a, b) for a, b in vd_runs(st["std"] < 6.0) if a > 0]

    res["frame0"] = {"mean": round(st["mean"][0], 1), "contrast": round(st["std"][0], 1)}
    res["flashes"] = [round(i / fps, 3) for i in flashes]
    res["pops"] = [round(i / fps, 3) for i in pops]
    res["cuts"] = [round(i / fps, 3) for i in cuts]
    res["frozen"] = [
        {
            "from": round((a - 1) / fps, 2),
            "to": round(b / fps, 2),
            "secs": round((b - a + 1) / fps, 2),
            "to_end": b >= n,
        }
        for a, b in frozen
    ]
    res["flat"] = [{"from": round(a / fps, 2), "to": round(b / fps, 2)} for a, b in flat]
    res["median_step"] = round(med, 3)

    if args.loop and n > 3:
        v_in, v_out = d[n - 1], d[1]
        res["loop"] = {
            "seam": round(st["seam"], 3),
            "seam_vs_median": round(st["seam"] / (med + 1e-6), 2),
            "speed_ratio": round((v_in + 0.05) / (v_out + 0.05), 2),
        }
    return res


def vd_compare_cuts(detected: List[float], expected: List[float], fps: float) -> Optional[Dict[str, Any]]:
    if not expected:
        return None
    errs, missing = [], []
    for t in expected:
        if not detected:
            missing.append(t)
            continue
        near = min(detected, key=lambda c: abs(c - t))
        if abs(near - t) > 0.5:
            missing.append(t)
        else:
            errs.append(round((near - t) * fps, 2))
    unplanned = [c for c in detected if all(abs(c - t) > 0.5 for t in expected)]
    return {
        "max_err_frames": max((abs(e) for e in errs), default=0.0),
        "errors_frames": errs,
        "missing": missing,
        "unplanned": unplanned,
    }


def vd_measure_text(im: Any, box: Any, short: float) -> Dict[str, float]:
    import numpy as np

    x, y, w, h = (int(round(float(v))) for v in box)
    rgb = np.asarray(im.crop((x, y, x + w, y + h)), np.float64) / 255
    lin = np.where(rgb <= 0.04045, rgb / 12.92, ((rgb + 0.055) / 1.055) ** 2.4)
    lum = lin @ np.array([0.2126, 0.7152, 0.0722])
    hist, edges = np.histogram(lum, 256, (0, 1))
    p = hist / max(1, hist.sum())
    w0 = np.cumsum(p)
    mu = np.cumsum(p * edges[:-1])
    between = (mu[-1] * w0 - mu) ** 2 / (w0 * (1 - w0) + 1e-12)
    hi = lum > edges[int(np.argmax(between))]
    ink = hi if hi.mean() <= 0.5 else ~hi
    if ink.all() or not ink.any():
        return {"font_px": 0.0, "contrast": 1.0}
    l_ink, l_bg = float(np.median(lum[ink])), float(np.median(lum[~ink]))
    contrast = (max(l_ink, l_bg) + 0.05) / (min(l_ink, l_bg) + 0.05)
    rows = ink.sum(axis=1)
    dense = np.nonzero(rows >= 0.25 * rows.max())[0]
    top = np.nonzero(rows >= max(1, 0.03 * rows.max()))[0][0]
    cap = float(dense[-1] - top + 1) * 1080 / short
    return {"font_px": round(cap / 0.72, 1), "contrast": round(contrast, 1)}


def vd_beat_times(tl: Dict[str, Any]) -> Dict[str, float]:
    out: Dict[str, float] = {}
    for s in tl.get("scenes", []):
        b = s.get("beats")
        for k, v in (b.items() if isinstance(b, dict) else []):
            if isinstance(v, (int, float)):
                out[f"{s.get('id')}.{k}"] = float(v)
    return out


def vd_load_timeline(path: Path | str) -> Dict[str, Any]:
    tl = json.loads(Path(path).read_text(encoding="utf-8"))
    nums = lambda xs: [float(v) for v in xs if isinstance(v, (int, float))]
    beats, cuts, hero = [], [], None
    if isinstance(tl, list):
        return {
            "beats": sorted(set(nums(tl))),
            "cuts": [],
            "hero": None,
            "silences": [],
            "loop": False,
            "clock": None,
            "texts": [],
        }
    for s in tl.get("scenes", []):
        if isinstance(s.get("start"), (int, float)):
            beats.append(float(s["start"]))
        b = s.get("beats")
        beats += nums(b.values()) if isinstance(b, dict) else nums(b or [])
    beats += nums(tl.get("beats", []) if isinstance(tl.get("beats"), list) else [])
    cuts = nums(tl.get("cuts", []))
    if isinstance(tl.get("hero"), dict):
        hero = tl["hero"].get("t")
    meta = tl.get("meta", {}) if isinstance(tl.get("meta"), dict) else {}
    sil = [x for x in tl.get("silences", []) if isinstance(x, dict) and "from" in x and "to" in x]
    named = vd_beat_times(tl)
    texts = []
    for x in tl.get("texts", []):
        if isinstance(x, dict) and x.get("role") in VD_TEXT_FLOORS:
            t = x.get("from") if isinstance(x.get("from"), (int, float)) else named.get(x.get("in"))
            texts.append(
                {"text": str(x.get("text", x.get("id", "?"))), "role": x["role"], "from": t, "box": x.get("box")}
            )
    return {
        "beats": sorted(set(beats)),
        "cuts": cuts,
        "hero": hero,
        "silences": sil,
        "loop": bool(meta.get("loop")),
        "clock": meta.get("clock"),
        "texts": texts,
    }


def consign_video_director_parity_receipt(
    module_results: Dict[str, Dict[str, Any]],
    head_sha40: str,
    repo_root: Optional[Path] = None,
) -> Dict[str, Any]:
    """Consigne uniquement la parité source-vs-organe réellement mesurée sur video-director (M095)."""
    verified = sorted(
        mid
        for mid, res in module_results.items()
        if res.get("compared_against_source") and res.get("cases_compared", 0) > 0 and res.get("cases_matched") == res.get("cases_compared")
    )
    total_cases = sum(int(res.get("cases_compared", 0)) for res in module_results.values())
    total_matched = sum(int(res.get("cases_matched", 0)) for res in module_results.values())
    evt, rec = consign_measured_l0_evidence(
        actor_from="fabricator",
        actor_to="judge",
        dispatch_id="D-VIDEO-DIRECTOR-PARITY",
        payload=f"Video Studio differential parity: {verified} ({total_matched}/{total_cases} cases)",
        issuer="Kernel K5 (VideoDirector)",
        mission_prefix="VIDEO-DIR-PARITY",
        sha=head_sha40,
        proof=["01_Forkable/FKB07_Money_Maker/02_Video/aspace_video_studio_foundation.py"],
        summary=f"VideoDirector measured parity {total_matched}/{total_cases} across {verified} at {head_sha40[:7]}",
        repo_root=repo_root,
    )
    return {
        "verified_modules": verified,
        "cases_matched": total_matched,
        "cases_compared": total_cases,
        "l0_seq": evt["seq"],
        "r10_entry_id": rec["entry_id"],
    }


@dataclass
class VideoPipelinePlan:
    job_id: str
    offer_type: str
    stages: List[Dict[str, Any]]
    fusion_status: str = "PARTIEL"
    missing_for_full_fusion: str = (
        "M095 video-director porté (check_timeline + qa_video) ; 9 moteurs de rendu (Chrome/Playwright/ffmpeg/TTS) restent PARTIEL."
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

        sample_tl = {
            "meta": {"w": 1920, "h": 1080, "fps": 30, "dur": 4.0, "clock": "reads"},
            "scenes": [{"id": "s1", "start": 0.0, "end": 4.0, "beats": {"b1": 1.0}}],
            "texts": [{"role": "hook", "text": "Test hook", "from": 0.0, "to": 2.0, "px": 96}],
            "terms": ["hook"],
            "hero": {"t": 2.5},
            "silences": [{"from": 1.0, "to": 1.6}],
        }
        tl_errs, _ = vd_validate_timeline(sample_tl)
        assert tl_errs == []
        assert vd_compare_cuts([1.0, 2.0], [1.0, 2.0], 30.0)["missing"] == []
        assert vd_runs([False, True, True, False]) == [(1, 3)]

        record_shared_l0_event(
            actor_from="fabricator",
            actor_to="executor",
            dispatch_id=f"D-VID-{job_id}",
            payload=f"Planifier pipeline video {job_id}",
            proof=["01_Forkable/FKB07_Money_Maker/02_Video/aspace_video_studio_foundation.py"],
            event_type="dispatch_typed",
        )
        record_shared_l0_receipt(
            issuer="Kernel K5 (VideoCoordinator)",
            mission_prefix=f"F4-VIDEO-{job_id}",
            sha=head_sha40,
            proof=[
                "01_Forkable/FKB07_Money_Maker/02_Video/aspace_video_studio_foundation.py",
                ".gitmodules:0_FKB06_duplicates",
            ],
            summary=f"F4 Video Studio coordinator active at {head_sha40[:7]} (0 source-oracle parities self-claimed)",
        )
        return VideoPipelinePlan(job_id=job_id, offer_type=offer_type, stages=stages)


if __name__ == "__main__":
    j = EventJournal(signed_designs={"00_Memoire/bundle/fusion/SDD-FONDATION.md"})
    l = R10Ledger()
    studio = UnifiedVideoStudioFoundation(j, l)
    plan = studio.build_pipeline("SMOKE001", "saas_demo", "0" * 40)
    checked_out = sum(1 for v in studio.inspect_disk_engines().values() if v["checked_out"])
    print(f"VideoCoordinator PASS (status={plan.fusion_status}): 10 engines indexed, {checked_out}/10 checked out on disk")
