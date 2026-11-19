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
from typing import Any, Dict, List, Optional, Tuple

_CORE_DIR = Path(__file__).resolve().parent
if str(_CORE_DIR) not in sys.path:
    sys.path.insert(0, str(_CORE_DIR))

from aspace_foundation_kernel import ContractViolation, consign_measured_l0_evidence  # noqa: E402

MARKETPLACE_SKILL_CATEGORIES: List[Dict[str, Any]] = [
    {"id": "01_Website_and_Funnels", "videos": 5, "offers": "Funnels VSL, Programmatic SEO, Sites Next.js haute conversion"},
    {"id": "02_Video_and_Motion", "videos": 5, "offers": "Studio Shorts Viraux, Motion Canvas programmatique, Vidéo IA"},
    {"id": "03_3D_and_Spatial", "videos": 3, "offers": "Configurateurs Three.js, Showrooms WebGL, Gaussian Splatting"},
    {"id": "04_2D_and_Games", "videos": 3, "offers": "Advergames 2D, Gamification d'onboarding, Mini-jeux HTML5"},
    {"id": "05_AI_Agents_and_Automation", "videos": 8, "offers": "Scrapers décisionnels, Agents vocaux Twilio, RAG souverain"},
    {"id": "06_SaaS_and_MicroServices", "videos": 10, "offers": "Micro-SaaS, Extensions Chrome, Modélisation financière, Design System"},
]

MARKETPLACE_PLAYBOOKS: Dict[str, Dict[str, Any]] = {
    "01_Website_and_Funnels": {
        "skill_name": "website-and-funnels",
        "title": "Website & Funnels Engine (A'Space MarketPlace · Catégorie 01)",
        "description": "Skill de création et déploiement de Sites Web haute conversion, Programmatic SEO et Funnels B2B pour A'Space MarketPlace (LD01).",
        "productized_offers": [
            {"offer": "Site Vitrine Élite / Funnel VSL", "spec": "Développement Next.js / Tailwind sans template générique", "pricing": "$1 500 setup + $199/m"},
            {"offer": "Programmatic SEO Directory", "spec": "Génération de 500 à 2 000 pages géolocalisées / nichées avec Next.js ISR", "pricing": "$2 500 setup + $350/m"},
            {"offer": "Headless E-commerce / Landing Page", "spec": "Conversion optimisée pour marques D2C et prestataires B2B", "pricing": "$1 200 setup"},
        ],
        "foundational_videos": ["-mb6buCbv8E", "7ggspQNUMYw", "747ZnEtsRbg", "T17DYl_4Z-U", "xWdEfsE_GRA"],
        "execution_protocol": [
            "Structure : Initialisation d'un worktree orca ou branche isolée aspace-v5-native.",
            "Composants : Déploiement du design system A'Space (Glassmorphism, dark luxury, sans dégradés violets IA).",
            "Vérification : Audit Lighthouse (Performance $\\ge 95$, Accessibilité 100, SEO 100).",
            "Livraison : Déploiement Vercel / Cloudflare Pages avec nom de domaine client.",
        ],
    },
    "02_Video_and_Motion": {
        "skill_name": "video-and-motion",
        "title": "Video & Motion Automation (A'Space MarketPlace · Catégorie 02)",
        "description": "Skill de production vidéo automatisée, Motion Design programmatique (Remotion/Motion Canvas) et Viral Shorts pour A'Space MarketPlace (LD01).",
        "productized_offers": [
            {"offer": "Studio Clips Viraux (30-40 Shorts/m)", "spec": "Découpage intelligent de podcasts, sous-titrage cinématique dynamique, b-rolls IA", "pricing": "$400/m"},
            {"offer": "Vidéos Explicatives Motion Code", "spec": "Production vidéo 100% automatisée par code React/TypeScript via Remotion", "pricing": "$800 setup + $250/vidéo"},
            {"offer": "Campagnes Publicitaires IA Multi-Formats", "spec": "Génération de vidéos promotionnelles D2C avec avatars et voix de synthèse ultraréalistes", "pricing": "$1 200/pack"},
        ],
        "foundational_videos": ["zsrj6qpfKbc", "q_1q425nehM", "aD87Q82dpLY", "QCkHIyEPIYo", "CCUSpJkAfgU"],
        "execution_protocol": [
            "Ingestion & Découpage : Script watch ou WhisperX pour transcription horodatée et détection des hooks viraux.",
            "Génération & Rendu : Moteur OpenMontage + Flute (01_Forkable/FKB07_Money_Maker/02_Video/).",
            "Stockage CAS : Fichiers .mp4 lourds déversés dans le Bucket Drive 5 To (00_Memoire/drive_5tb_cas_index.jsonl) et référencés par fichier .cas.json.",
        ],
    },
    "03_3D_and_Spatial": {
        "skill_name": "3d-and-spatial",
        "title": "3D & Spatial Computing (A'Space MarketPlace · Catégorie 03)",
        "description": "Skill de conception d'univers 3D Web interactifs (Three.js, Spline, Gaussian Splatting, Blender to WebGL) pour A'Space MarketPlace (LD01).",
        "productized_offers": [
            {"offer": "Vitrines E-Commerce 3D Interactives", "spec": "Configurateurs de produits 3D Three.js légers (< 5 Mo, 60 FPS mobile)", "pricing": "$2 000 setup + $150/m"},
            {"offer": "Pavillons Virtuels & Showrooms WebGL", "spec": "Mondes immersifs pour marques, galeries d'art et événements virtuels", "pricing": "$3 500 setup"},
            {"offer": "Pipeline Gaussian Splatting / Photogrammétrie", "spec": "Numérisation d'espaces réels et restitution temps réel dans le navigateur", "pricing": "$1 800/scan"},
        ],
        "foundational_videos": ["g3p40vPW_DU", "-Q4SvlX9KyU", "6_MrVEXM06E"],
        "execution_protocol": [
            "Export & Compression : Pipeline Draco / KTX2 pour compresser les maillages et textures GLB.",
            "Garde-Fou Anti-Boucle : Script de surveillance tuant tout worker de rendu 3D bloqué dans une boucle de réflexion.",
            "Stockage CAS : Scènes .glb hébergées sur le Bucket Drive 5 To et chargées via CDN.",
        ],
    },
    "04_2D_and_Games": {
        "skill_name": "2d-and-games",
        "title": "2D Games & Gamification (A'Space MarketPlace · Catégorie 04)",
        "description": "Skill de développement de jeux Web interactifs, mini-jeux promotionnels et expériences 2D (Godot 4, Phaser) pour A'Space MarketPlace (LD01).",
        "productized_offers": [
            {"offer": "Advergame Promotionnel Web", "spec": "Mini-jeu interactif 2D jouable sans téléchargement sur mobile et desktop pour lancements de produits", "pricing": "$2 500 setup"},
            {"offer": "Gamification d'Onboarding Salarié", "spec": "Quêtes interactives et simulations 2D pour accélérer la formation interne", "pricing": "$3 000 setup"},
            {"offer": "Jeux Éducatifs & Lore Interactif", "spec": "Expériences ludo-éducatives pour communautés et marques", "pricing": "$1 500 setup + $200/m"},
        ],
        "foundational_videos": ["SNYu3nqrQuk", "HsB-50ZQF1w", "oFy5PtZtZco"],
        "execution_protocol": [
            "Moteur : Export HTML5 / WebAssembly optimisé pour un chargement en moins de 3 secondes.",
            "Télémétrie : Connexion à Supabase / Google Sheets pour l'enregistrement des scores et leads.",
        ],
    },
    "05_AI_Agents_and_Automation": {
        "skill_name": "ai-agents-and-automation",
        "title": "AI Agents & Autonomous Automation (A'Space MarketPlace · Catégorie 05)",
        "description": "Skill de déploiement de Systèmes Multi-Agents, Scrapers Décisionnels, Agents Vocaux et Inférence Souveraine pour A'Space MarketPlace (LD01).",
        "productized_offers": [
            {"offer": "Radar Concurrentiel & Veille Prix B2B", "spec": "Scraping continu de sites marchands avec alerte Slack/Mail", "pricing": "$500 setup + $300/m"},
            {"offer": "Agent Vocal Téléphonique IA (Twilio / Vapi)", "spec": "Gestion des appels entrants et qualification des leads 24/7", "pricing": "$1 500 setup + $250/m"},
            {"offer": "Assistant RAG Souverain sur Données Internes", "spec": "Recherche vectorielle locale sécurisée sur la documentation de l'entreprise", "pricing": "$2 000 setup + $300/m"},
        ],
        "foundational_videos": ["uUk4sUP7lmw", "XV2PAHWnJN0", "Src-a8GJR20", "Ta8siAhkEOw", "4N1wG0U0reE", "Eg08Lr3zqdw", "NAQyKMdxRT4", "AFRL9dtUHeI"],
        "execution_protocol": [
            "Isolation : Déploiement sur le computer-service natif du daemon unique (:4100, un ordinateur par Bot) sous politiques d'accès CEL strictes.",
            "Supervision : Intégration de la surface native de reprise en main (takeover, même session navigateur) pour reprise en main humaine instantanée.",
            "Escalade : Routage des alertes vers les espaces Google Chat de SOB Hub.",
        ],
    },
    "06_SaaS_and_MicroServices": {
        "skill_name": "saas-and-microservices",
        "title": "SaaS & Micro-Services Architecture (A'Space MarketPlace · Catégorie 06)",
        "description": "Skill de conception de Micro-SaaS, Modélisation Financière, Extensions Chrome et Boilerplates Modernes pour A'Space MarketPlace (LD01).",
        "productized_offers": [
            {"offer": "Micro-SaaS & Extension Chrome Métier", "spec": "Outil d'automatisation ciblé pour un secteur spécifique", "pricing": "$1 500 setup + $29/utilisateur/m"},
            {"offer": "Audit de Modélisation Financière & Pricing SaaS", "spec": "Analyse de la rentabilité unitaire, LTV/CAC et packaging tarifaire", "pricing": "$1 000 par audit"},
            {"offer": "Système de Design & Composants UI/UX Pro", "spec": "Bibliothèque Tailwind chartée pour plateformes SaaS", "pricing": "$1 200 par système"},
        ],
        "foundational_videos": ["_2FlJYE4p3Q", "mV74tDW0mc0", "BI-MNjm1tTQ", "DCwh7SIfWL4", "JhU4V5DzMs0", "lFiY0JukgwU", "iu788WcFARU", "RNIX-Re9k4o", "NBZmxhcz5lo", "KBH8P0z2AL8"],
        "execution_protocol": [
            "Packaging : Structuration de l'offre avec garantie de résultat adossée au modèle prédictif TimesFM 3.0.",
            "Facturation : Gestion des abonnements et encaissement via Stripe / LemonSqueezy.",
        ],
    },
}

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


OPPORTUNITY_DOSSIERS: Dict[str, Dict[str, Any]] = {
    "OPP-001": {
        "id": "OPP-001",
        "title": "Claude Opus 5.5 & Kito Pro (Amazon Coding Agent)",
        "source_youtube": "Claude Opus 5.5 is Now 100% FREE (NEW Method)",
        "target_platform": "https://kito.dev (Kito Agent / Kiro)",
        "model_offered": "Claude Opus 5.5, Sonnet 5.5, Claude Haiku, GPT-5.6 Soul, Jimmy K3",
        "compute_volume": "50 $ à 200 $ d'utilisation selon le plan choisi (Kito Pro Plus 40$ / Kito Power 200$)",
        "watch_skill_status": "ACTIF (SURVEILLANCE FACTURATION)",
        "injection_vector": "Voie B (Interface Web & Session)",
        "mechanism_steps": [
            "Inscription sur kito.dev (compte gratuit initial).",
            "Sélection d'un forfait supérieur (ex: Kito Pro Plus à 40$/mois).",
            "La facture Stripe indique 0 € / 0 $ dus immédiatement, avec prélèvement programmé au 1er du mois suivant.",
            "Immédiatement après validation, retourner dans le dashboard et rétrograder vers le plan gratuit.",
            "L'abonnement payant reste actif avec l'intégralité des crédits jusqu'au 1er du mois sans prélèvement.",
        ],
    },
    "OPP-002": {
        "id": "OPP-002",
        "title": "DeepSeek V4.1 Flash Obliterated via Refuseless.com",
        "source_youtube": "How to Get FREE API Keys for DeepSeek V4.1 Flash (Abliterated) & HY4",
        "target_platform": "https://refuseless.com",
        "model_offered": "DeepSeek V4.1 Flash Obliterated (Contexte 512K, Max Output 120K)",
        "compute_volume": "100 crédits dédiés offerts (solde isolé sans empiéter sur le solde principal)",
        "watch_skill_status": "QUALIFIÉ & EXPLOITABLE IMMÉDIATEMENT",
        "injection_vector": "Voie A (Passerelle API Directe FreeLLMAPI / Claude Code)",
        "mechanism_steps": [
            "Connexion sur refuseless.com via Google Auth (zéro carte bancaire requise).",
            "Accès à l'onglet Models : DeepSeek V4.1 Flash marqué comme gratuit avec 100 crédits de bienvenue conservés dans un compte dédié.",
            "Génération d'une clé API native dans l'onglet API keys.",
        ],
    },
    "OPP-003": {
        "id": "OPP-003",
        "title": "Tencent Hunyuan 4 (HY4) via APINex (20M Tokens / Jour)",
        "source_youtube": "How to Get FREE API Keys for DeepSeek V4.1 Flash (Abliterated) & HY4",
        "target_platform": "https://apinex.com",
        "model_offered": "Tencent Hunyuan 4 (HY4) (Contexte 1 Million de tokens)",
        "compute_volume": "20 Millions de tokens gratuits CHAQUE JOUR",
        "watch_skill_status": "PÉPITE SOUVERAINE (SCORE A+)",
        "injection_vector": "Voie A (Passerelle API Directe FreeLLMAPI)",
        "mechanism_steps": [
            "Inscription sur apinex.com sans carte de crédit.",
            "Dashboard -> Modèles & Tarification -> groupe Free.",
            "Le modèle HY4 est listé avec l'étiquette gratuite, doté d'une fenêtre de contexte de 1M de tokens et d'une recharge quotidienne automatique de 20 000 000 de tokens.",
            "Création immédiate de la clé API.",
        ],
    },
    "OPP-004": {
        "id": "OPP-004",
        "title": "Croton Alpha 1M Context via OpenRouter & Kilo Code",
        "source_youtube": "New Stealth AI Model is FREE! 1M Context | OpenRouter, Kilo & OpenCode",
        "target_platform": "https://openrouter.ai / Killo Gateway",
        "model_offered": "Croton Alpha (Modèle furtif multimodal, Contexte 1M, Zéro entraînement sur data)",
        "compute_volume": "Gratuit pendant 7 jours (phase d'évaluation publique)",
        "watch_skill_status": "ÉPHÉMÈRE / FENÊTRE FLASH (TTL 7 JOURS)",
        "injection_vector": "Voie A (Déjà routé dans FreeLLMAPI)",
        "mechanism_steps": [
            "Connexion sur OpenRouter (ou via la passerelle Killo Gateway / OpenCode).",
            "Clé API OpenRouter sans restriction de crédit (limit: none).",
            "Sélection du modèle croton/croton-alpha (ou alias Killo Gateway).",
            "Accès instantané à une fenêtre de contexte de 1M de tokens avec raisonnement rapide (2-3s par réponse).",
        ],
    },
    "OPP-005": {
        "id": "OPP-005",
        "title": "Tencent Hunyuan 4 via WorkBuddy.ai (Offre Limitée)",
        "source_youtube": "Don't Miss Out! Use Tencent Hy4 for FREE on WorkBuddy",
        "target_platform": "https://workbuddy.ai (App Desktop Mac/Windows ou Web)",
        "model_offered": "Tencent Hunyuan 4 (HY4) (Contexte 200k à 1M, Mode pensée haute)",
        "compute_volume": "200 à 300 crédits quotidiens gratuits (du 4 au 15 novembre)",
        "watch_skill_status": "DOUBLON INFÉRIEUR (PRÉFÉRER APINEX OPP-003)",
        "injection_vector": "Voie B (Application / UI)",
        "mechanism_steps": [
            "Téléchargement de l'application Work Buddy sur Mac ou Windows.",
            "Allocation quotidienne automatique de 200-300 crédits.",
            "Sélection de Tencent Hunyuan 4 dans le picker de modèles avec contexte jusqu'à 1 million de tokens.",
        ],
    },
}


def get_opportunity_dossier(opp_id: str) -> Dict[str, Any]:
    """Retourne la fiche complète OPP-001..005 absorbée de M118."""
    key = opp_id.strip().upper()
    if key not in OPPORTUNITY_DOSSIERS:
        raise ContractViolation("K3", "opp_id", f"opportunité M118 inconnue: {opp_id}")
    return dict(OPPORTUNITY_DOSSIERS[key])


def get_marketplace_playbook(category: str) -> Dict[str, Any]:
    """Retourne le playbook complet (offres chiffrées, seuils, protocole) d'une catégorie M117."""
    key = category.strip().lower()
    for cat_id, pb in MARKETPLACE_PLAYBOOKS.items():
        if cat_id.lower() == key or pb["skill_name"].lower() == key:
            return {"category": cat_id, **pb}
    raise ContractViolation("K5", "category", f"catégorie marketplace M117 inconnue: {category}")


def query_marketplace_skills(category: Optional[str] = None, keyword: Optional[str] = None) -> Dict[str, Any]:
    """Interroge les 34 ressources vidéos, 6 playbooks et 18 offres MarketPlace (M117) depuis CORPS / K5."""
    items = list(YOUTUBE_SKILL_VIDEOS)
    playbooks = {k: v for k, v in MARKETPLACE_PLAYBOOKS.items()}
    if category:
        items = [it for it in items if it["category"].lower() == category.lower()]
        playbooks = {k: v for k, v in playbooks.items() if k.lower() == category.lower() or v["skill_name"].lower() == category.lower()}
    if keyword:
        kw = keyword.lower()
        items = [it for it in items if kw in it["topic"].lower() or kw in it["category"].lower()]
        playbooks = {
            k: v
            for k, v in playbooks.items()
            if kw in v["description"].lower()
            or kw in k.lower()
            or any(kw in o["offer"].lower() or kw in o["spec"].lower() or kw in o["pricing"].lower() for o in v["productized_offers"])
            or any(vid["category"] == k for vid in items)
        }
    offers = [
        {"category": k, **off}
        for k, pb in playbooks.items()
        for off in pb["productized_offers"]
    ]
    return {
        "categories_count": len(MARKETPLACE_SKILL_CATEGORIES),
        "playbooks_count": len(playbooks),
        "productized_offers_count": len(offers),
        "total_catalog_videos": len(YOUTUBE_SKILL_VIDEOS),
        "matched_count": len(items),
        "matches": items,
        "playbooks": playbooks,
        "productized_offers": offers,
    }


def run_self_test(head_sha40: str = "0" * 40, repo_root: Optional[Path] = None) -> Dict[str, Any]:
    """Vérifie le fonctionnement interne autonome de M117 + M118 sans accès aux répertoires sources."""
    checks: Dict[str, bool] = {}
    total_offers = sum(len(pb["productized_offers"]) for pb in MARKETPLACE_PLAYBOOKS.values())
    pb1 = get_marketplace_playbook("01_Website_and_Funnels")
    q_res = query_marketplace_skills(keyword="Three.js")
    qual_a = qualify_inference_opportunity(
        {
            "platform": "sovereign-new-api.example",
            "requires_credit_card": False,
            "direct_openai_or_anthropic_api": True,
            "estimated_ttl_days": 60,
        },
        known_platforms=set(),
    )
    d_opp3 = get_opportunity_dossier("OPP-003")
    checks["m117_catalog_shape"] = (
        len(YOUTUBE_SKILL_VIDEOS) == 34
        and sum(c["videos"] for c in MARKETPLACE_SKILL_CATEGORIES) == 34
        and len(MARKETPLACE_PLAYBOOKS) == 6
        and total_offers == 18
        and any("Lighthouse" in step for step in pb1["execution_protocol"])
        and q_res["matched_count"] >= 1
    )
    checks["m118_dossiers_and_filter"] = (
        len(INFERENCE_DISCOVERY_REGISTRY["opportunities"]) == 5
        and len(OPPORTUNITY_DOSSIERS) == 5
        and qual_a["score"] == "A"
        and qual_a["vector"] == "VOIE_A_API_DIRECT"
        and d_opp3["target_platform"] == "https://apinex.com"
    )
    assert all(checks.values())

    passed = sum(1 for v in checks.values() if v)
    total = len(checks)
    evt, rec = consign_measured_l0_evidence(
        actor_from="discoverer",
        actor_to="fabricator",
        dispatch_id="D-M117-M118-SMOKE",
        payload=f"Catalog smoke checks: {passed}/{total} internal, 0 source-oracle parities",
        issuer="Catalog M117/M118",
        mission_prefix="M117-M118-SMOKE",
        sha=head_sha40,
        proof=["01_Forkable/FKB00_Runtime/00_A0_Core/aspace_discovery_catalog.py"],
        summary=f"Catalog smoke={passed}/{total}; videos={len(YOUTUBE_SKILL_VIDEOS)}; dossiers={len(OPPORTUNITY_DOSSIERS)}; source_oracle_parity=0 at {head_sha40[:7]}",
        repo_root=repo_root,
    )
    if not evt["seq"] or not rec["recorded_at"]:
        raise ContractViolation("C5", "catalog", "échec d'inscription L0")
    return {
        "checks": checks,
        "checks_passed": passed,
        "checks_total": total,
        "source_parity_verified": [],
        "m117_videos": len(YOUTUBE_SKILL_VIDEOS),
        "m117_playbooks": len(MARKETPLACE_PLAYBOOKS),
        "m117_productized_offers": total_offers,
        "m118_opportunities": len(INFERENCE_DISCOVERY_REGISTRY["opportunities"]),
        "m118_dossiers": len(OPPORTUNITY_DOSSIERS),
        "l0_seq": evt["seq"],
        "r10_entry_id": rec["entry_id"],
    }


def consign_catalog_parity_receipt(
    module_results: Dict[str, Dict[str, Any]],
    head_sha40: str,
    repo_root: Optional[Path] = None,
) -> Dict[str, Any]:
    """Consigne uniquement la parité source-vs-organe réellement mesurée pour M117/M118."""
    verified = sorted(
        mid
        for mid, res in module_results.items()
        if res.get("compared_against_source") and res.get("cases_compared", 0) > 0 and res.get("cases_matched") == res.get("cases_compared")
    )
    total_cases = sum(int(res.get("cases_compared", 0)) for res in module_results.values())
    total_matched = sum(int(res.get("cases_matched", 0)) for res in module_results.values())
    evt, rec = consign_measured_l0_evidence(
        actor_from="discoverer",
        actor_to="fabricator",
        dispatch_id="D-M117-M118-PARITY",
        payload=f"Catalog differential parity: {verified} ({total_matched}/{total_cases} cases)",
        issuer="Catalog M117/M118",
        mission_prefix="M117-M118-PARITY",
        sha=head_sha40,
        proof=["01_Forkable/FKB00_Runtime/00_A0_Core/aspace_discovery_catalog.py"],
        summary=f"Catalog measured parity {total_matched}/{total_cases} across {verified} at {head_sha40[:7]}",
        repo_root=repo_root,
    )
    return {
        "verified_modules": verified,
        "cases_matched": total_matched,
        "cases_compared": total_cases,
        "l0_seq": evt["seq"],
        "r10_entry_id": rec["entry_id"],
    }


if __name__ == "__main__":
    import json
    print(json.dumps(run_self_test(), indent=2, ensure_ascii=False))
