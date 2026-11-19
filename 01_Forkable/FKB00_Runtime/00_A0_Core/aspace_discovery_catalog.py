#!/usr/bin/env python3
"""
aspace_discovery_catalog.py — Catalogue Natif d'Offres YouTube & Inférence Gratuite (M117 + M118).

Absorbe en code natif hors de leurs répertoires sources d'origine :
  - M117 (`00_Marketplace_YoutubeSkills`, rattaché à CORPS / Organe K5) :
    6 catégories, 34 ressources vidéos et mapping SKILL -> Offre MarketPlace.
  - M118 (`04_Inference_Youtube_Discovery_Registry`, rattaché à SYSTÈME NERVEUX / Organe K3) :
    grille de qualification anti-clickbait à 5 filtres et registre structuré des opportunités.

Zéro dépendance externe, zéro télémétrie.
"""

from __future__ import annotations

import datetime as dt
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

_CORE_DIR = Path(__file__).resolve().parent
if str(_CORE_DIR) not in sys.path:
    sys.path.insert(0, str(_CORE_DIR))

from aspace_foundation_kernel import ContractViolation, EventJournal, R10Ledger, R10_SCHEMA  # noqa: E402

MARKETPLACE_SKILL_CATEGORIES: List[Dict[str, Any]] = [
    {"id": "01_Website_and_Funnels", "videos": 5, "offers": "Funnels VSL, Programmatic SEO, Sites Next.js haute conversion"},
    {"id": "02_Video_and_Motion", "videos": 5, "offers": "Studio Shorts Viraux, Motion Canvas programmatique, Vidéo IA"},
    {"id": "03_3D_and_Spatial", "videos": 3, "offers": "Configurateurs Three.js, Showrooms WebGL, Gaussian Splatting"},
    {"id": "04_2D_and_Games", "videos": 3, "offers": "Advergames 2D, Gamification d'onboarding, Mini-jeux HTML5"},
    {"id": "05_AI_Agents_and_Automation", "videos": 8, "offers": "Scrapers décisionnels, Agents vocaux Twilio, RAG souverain"},
    {"id": "06_SaaS_and_MicroServices", "videos": 10, "offers": "Micro-SaaS, Extensions Chrome, Modélisation financière, Design System"},
]

YOUTUBE_SKILL_VIDEOS: List[Dict[str, str]] = [
    {"video_id": "uUk4sUP7lmw", "category": "05_AI_Agents_and_Automation", "topic": "Web Scraping & Playwright Crawling"},
    {"video_id": "g3p40vPW_DU", "category": "03_3D_and_Spatial", "topic": "Interactive 3D Web Apps Three.js & Spline"},
    {"video_id": "XV2PAHWnJN0", "category": "05_AI_Agents_and_Automation", "topic": "Agentic Workflows & Advanced n8n"},
    {"video_id": "-mb6buCbv8E", "category": "01_Website_and_Funnels", "topic": "Next.js Fullstack SaaS Architecture"},
    {"video_id": "zsrj6qpfKbc", "category": "02_Video_and_Motion", "topic": "AI Filmmaking & Generative Video"},
    {"video_id": "SNYu3nqrQuk", "category": "04_2D_and_Games", "topic": "2D Game Development & Web Engines"},
    {"video_id": "q_1q425nehM", "category": "02_Video_and_Motion", "topic": "Programmatic Motion Graphics (Remotion)"},
    {"video_id": "-Q4SvlX9KyU", "category": "03_3D_and_Spatial", "topic": "Blender to WebGL Optimization Pipeline"},
    {"video_id": "AFRL9dtUHeI", "category": "05_AI_Agents_and_Automation", "topic": "Voice AI & Audio Generation"},
    {"video_id": "_2FlJYE4p3Q", "category": "06_SaaS_and_MicroServices", "topic": "Micro-SaaS & Chrome Extension Development"},
    {"video_id": "DCwh7SIfWL4", "category": "06_SaaS_and_MicroServices", "topic": "UI/UX Design System (Figma to Code)"},
    {"video_id": "Src-a8GJR20", "category": "05_AI_Agents_and_Automation", "topic": "Multi-Agent Swarms & Autonomous Coordination"},
    {"video_id": "KBH8P0z2AL8", "category": "06_SaaS_and_MicroServices", "topic": "Cross-Platform Mobile Apps (React Native/Flutter)"},
    {"video_id": "Ta8siAhkEOw", "category": "05_AI_Agents_and_Automation", "topic": "RAG Architecture & Vector Database Search"},
    {"video_id": "lFiY0JukgwU", "category": "06_SaaS_and_MicroServices", "topic": "B2B Outbound Funnels & Sales Automation"},
    {"video_id": "iu788WcFARU", "category": "06_SaaS_and_MicroServices", "topic": "E-commerce Automation & Headless Workflows"},
    {"video_id": "QCkHIyEPIYo", "category": "02_Video_and_Motion", "topic": "Video Editing Automation & YouTube Workflows"},
    {"video_id": "7ggspQNUMYw", "category": "01_Website_and_Funnels", "topic": "High-Converting Web Design & Webflow/Framer"},
    {"video_id": "oFy5PtZtZco", "category": "04_2D_and_Games", "topic": "Game AI & Procedural Generation for 2D/3D Assets"},
    {"video_id": "RNIX-Re9k4o", "category": "06_SaaS_and_MicroServices", "topic": "Prompt Architecture & Meta-Prompting"},
    {"video_id": "aD87Q82dpLY", "category": "02_Video_and_Motion", "topic": "Motion Canvas Code-based Animation"},
    {"video_id": "NBZmxhcz5lo", "category": "06_SaaS_and_MicroServices", "topic": "Computer Vision & Automation APIs"},
    {"video_id": "NAQyKMdxRT4", "category": "05_AI_Agents_and_Automation", "topic": "B2B Lead Scraping & Verification Pipeline"},
    {"video_id": "6_MrVEXM06E", "category": "03_3D_and_Spatial", "topic": "3D Gaussian Splatting & Spatial Computing"},
    {"video_id": "mV74tDW0mc0", "category": "06_SaaS_and_MicroServices", "topic": "SaaS Boilerplate Architecture (Auth, Stripe, Multi-tenant)"},
    {"video_id": "CCUSpJkAfgU", "category": "02_Video_and_Motion", "topic": "Content Repurposing (Podcast to Viral Shorts)"},
    {"video_id": "Eg08Lr3zqdw", "category": "05_AI_Agents_and_Automation", "topic": "Local LLM Deployment & Sovereign Inference"},
    {"video_id": "747ZnEtsRbg", "category": "01_Website_and_Funnels", "topic": "Programmatic SEO & Data-Driven Landing Pages"},
    {"video_id": "HsB-50ZQF1w", "category": "04_2D_and_Games", "topic": "Godot 4 Web Publishing & Pixel Art"},
    {"video_id": "JhU4V5DzMs0", "category": "06_SaaS_and_MicroServices", "topic": "Scalable Figma Component Libraries"},
    {"video_id": "xWdEfsE_GRA", "category": "01_Website_and_Funnels", "topic": "High-Converting Copywriting & Sales Funnels"},
    {"video_id": "4N1wG0U0reE", "category": "05_AI_Agents_and_Automation", "topic": "AI Voice Agent (Twilio/Vapi Telephony Integration)"},
    {"video_id": "T17DYl_4Z-U", "category": "01_Website_and_Funnels", "topic": "Webflow to Clean Code Export & Edge Hosting"},
    {"video_id": "BI-MNjm1tTQ", "category": "06_SaaS_and_MicroServices", "topic": "SaaS Financial Modeling & Unit Economics"},
]

INFERENCE_DISCOVERY_REGISTRY: Dict[str, Any] = {
    "registry_version": "1.0.0",
    "name": "Aspace OS V5 - YouTube Inference Discovery Registry",
    "updated_at": "2026-11-06T06:00:00Z",
    "governance": "Filtered by Watch Skill (Anti-Clickbait & Platform Drift Resistant)",
    "opportunities": [
        {
            "id": "OPP-001",
            "platform": "kito.dev",
            "model": "Claude Opus 5.5 / Sonnet 5.5",
            "quota_type": "50$ to 200$ trial credit",
            "mechanism": "Stripe invoice grace loop (downgrade to free immediately)",
            "risk_level": "HIGH (Requires Credit Card)",
            "durability": "FRAGILE (Stripe patch expected)",
            "vector": "VOIE_B_WEB",
            "status": "MONITORED",
        },
        {
            "id": "OPP-002",
            "platform": "refuseless.com",
            "model": "DeepSeek V4.1 Flash Obliterated",
            "quota_type": "100 credits isolated pool",
            "mechanism": "Google Auth without CC, native API key",
            "risk_level": "LOW",
            "durability": "MEDIUM",
            "vector": "VOIE_A_API_DIRECT",
            "status": "QUALIFIED",
        },
        {
            "id": "OPP-003",
            "platform": "apinex.com",
            "model": "Tencent Hunyuan 4 (HY4)",
            "quota_type": "20,000,000 tokens / day",
            "mechanism": "Daily free group quota, 1M context, Anthropic/OpenAI base URL",
            "risk_level": "LOW",
            "durability": "STABLE_DAILY_REFRESH",
            "vector": "VOIE_A_API_DIRECT",
            "status": "PRIORITY_GOLD",
        },
        {
            "id": "OPP-004",
            "platform": "openrouter.ai / Killo Gateway",
            "model": "Croton Alpha (Stealth 1M Context)",
            "quota_type": "Unlimited for 7 days",
            "mechanism": "OpenRouter API key or Killo Gateway",
            "risk_level": "LOW",
            "durability": "FLASH_7_DAYS",
            "vector": "VOIE_A_ALREADY_IN_FLA",
            "status": "ACTIVE_FLASH",
        },
        {
            "id": "OPP-005",
            "platform": "workbuddy.ai",
            "model": "Tencent Hunyuan 4 (HY4)",
            "quota_type": "200-300 credits / day",
            "mechanism": "Desktop App closed environment (Nov 4 to Nov 15)",
            "risk_level": "MEDIUM (Proprietary App)",
            "durability": "FLASH_LIMITED_NOV15",
            "vector": "VOIE_B_SUPERSEDED_BY_OPP003",
            "status": "SUPERSEDED_BY_APINEX",
        },
    ],
}


def qualify_inference_opportunity(candidate: Dict[str, Any], known_platforms: Optional[set[str]] = None) -> Dict[str, Any]:
    """Applique la grille Watch Skill en 5 filtres (M118) avant toute injection dans SYSTÈME NERVEUX / K3."""
    platform = str(candidate.get("platform", "")).strip().lower()
    existing = known_platforms if known_platforms is not None else {o["platform"].lower() for o in INFERENCE_DISCOVERY_REGISTRY["opportunities"]}

    # Filtre 1 : Déduplication FLA / CCW
    dedup = "ALREADY_TRACKED" if platform in existing else "NEW_OPPORTUNITY"
    # Filtre 2 : Authenticité
    authentic = bool(candidate.get("verified_model_weights", True)) and not bool(candidate.get("clickbait_rebrand", False))
    if not authentic:
        return {"platform": platform, "decision": "REJECT_CLICKBAIT", "score": "F", "dedup": dedup}
    # Filtre 3 : Risque / Frictionalité (zéro CB prioritaire)
    requires_cc = bool(candidate.get("requires_credit_card", False))
    is_direct_api = bool(candidate.get("direct_openai_or_anthropic_api", False))
    score = "C" if requires_cc else ("A" if is_direct_api else "B")
    # Filtre 4 & 5 : Durabilité & Vecteur d'injection
    ttl_days = int(candidate.get("estimated_ttl_days", 14))
    durability = "FLASH" if ttl_days < 7 else ("STABLE" if ttl_days >= 30 else "MEDIUM")
    vector = "VOIE_A_API_DIRECT" if is_direct_api else "VOIE_B_WEB_SHIELDED"
    decision = "ADMIT_WITH_MONITORING" if requires_cc else "ADMIT_SOVEREIGN"
    return {
        "platform": platform,
        "dedup": dedup,
        "authentic": True,
        "score": score,
        "durability": durability,
        "vector": vector,
        "decision": decision,
    }


def query_marketplace_skills(category: Optional[str] = None, keyword: Optional[str] = None) -> Dict[str, Any]:
    """Interroge les 34 ressources vidéos et 6 catégories MarketPlace (M117) depuis CORPS / K5."""
    items = list(YOUTUBE_SKILL_VIDEOS)
    if category:
        items = [it for it in items if it["category"].lower() == category.lower()]
    if keyword:
        kw = keyword.lower()
        items = [it for it in items if kw in it["topic"].lower() or kw in it["category"].lower()]
    return {
        "categories_count": len(MARKETPLACE_SKILL_CATEGORIES),
        "total_catalog_videos": len(YOUTUBE_SKILL_VIDEOS),
        "matched_count": len(items),
        "matches": items,
    }


def run_self_test(head_sha40: str = "0" * 40) -> Dict[str, Any]:
    """Vérifie M117 + M118 sans accéder aux anciens répertoires sources de 01_Forkable/."""
    assert len(YOUTUBE_SKILL_VIDEOS) == 34
    assert sum(c["videos"] for c in MARKETPLACE_SKILL_CATEGORIES) == 34
    assert len(INFERENCE_DISCOVERY_REGISTRY["opportunities"]) == 5

    q_res = query_marketplace_skills(keyword="Three.js")
    assert q_res["matched_count"] >= 1

    qual_a = qualify_inference_opportunity(
        {
            "platform": "sovereign-new-api.example",
            "requires_credit_card": False,
            "direct_openai_or_anthropic_api": True,
            "estimated_ttl_days": 60,
        },
        known_platforms=set(),
    )
    assert qual_a["score"] == "A" and qual_a["vector"] == "VOIE_A_API_DIRECT"

    now_dt = dt.datetime.now(dt.timezone.utc)
    day_tag = now_dt.strftime("%Y%m%d")
    journal = EventJournal(signed_designs={"00_Memoire/bundle/fusion/SDD-FONDATION.md"})
    ledger = R10Ledger(valid_shas={head_sha40})
    evt = journal.inscribe(
        {
            "actor_from": "discoverer",
            "actor_to": "fabricator",
            "at": now_dt.isoformat(),
            "design_ref": "00_Memoire/bundle/fusion/SDD-FONDATION.md",
            "dispatch_id": "D-M117-M118-CATALOG",
            "event_id": f"EVT-{day_tag}-901",
            "payload": "Valider catalogue natif M117 M118",
            "proof": ["01_Forkable/FKB00_Runtime/00_A0_Core/aspace_discovery_catalog.py"],
            "type": "dispatch_typed",
        },
        now_utc=now_dt,
    )
    rec = ledger.validate_and_consign(
        {
            "entry_id": f"G-{day_tag}-901",
            "issuer": "Catalog M117/M118",
            "mission_id": "M117-M118-NATIVE-ABSORPTION",
            "observed_at": now_dt.isoformat(),
            "proof": ["01_Forkable/FKB00_Runtime/00_A0_Core/aspace_discovery_catalog.py"],
            "recorded_at": None,
            "schema": R10_SCHEMA,
            "sha": head_sha40,
            "summary": f"M117+M118 absorbed at {head_sha40[:7]}",
        },
        now_utc=now_dt,
    )
    if not evt["seq"] or not rec["recorded_at"]:
        raise ContractViolation("C5", "catalog", "échec d'inscription L0")
    return {
        "m117_videos": len(YOUTUBE_SKILL_VIDEOS),
        "m118_opportunities": len(INFERENCE_DISCOVERY_REGISTRY["opportunities"]),
        "l0_seq": evt["seq"],
        "r10_entry_id": rec["entry_id"],
    }


if __name__ == "__main__":
    import json
    print(json.dumps(run_self_test(), indent=2, ensure_ascii=False))
