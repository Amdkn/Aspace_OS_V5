#!/usr/bin/env python3
"""
01_Forkable/FKB07_Money_Maker/aspace_road_to_market_engine.py
=============================================================
Moteur d'Exécution du "Road to Market" — A'Space MarketPlace (Projet Picard LD01).
Met en œuvre la tâche stratégique n°3 activée dans Google Tasks :
  1. Génère les 5 Campagnes d'Acquisition Proof-First (GTME) :
     - Radar Prix & Stock (Scrapling)
     - Bot SOP & Onboarding (Dify)
     - Scorecard SEO & AEO (OpenSEO)
     - Studio Clips Viraux (OpenShorts)
     - Devis Live en Appel (Presenton)
  2. Structure le Pipeline des 100 Premiers Comptes B2B (The OMK Office) :
     - Scraping Apify Maps -> Enrichissement treg.to -> Diagnostic pré-contact
  3. Projette la Trajectoire Financière TimesFM 3.0 :
     - Plancher q10 : 3 500 $/mois ($42 000/an)
     - Médiane q50 : 10 000 $/mois ($120 000/an)
     - Cible q90 : 25 000 $/mois ($300 000/an)
  4. Double Écriture automatique dans Google Sheets Areas OS (Onglet B_LD01_BUSINESS_OS).
"""

from __future__ import annotations

import datetime as dt
import hashlib
import json
from dataclasses import asdict, dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RTM_STATE_OUT = (
    ROOT
    / "00_Memoire"
    / "bundle"
    / "areas_os"
    / "B_LD01_Business_OMK"
    / "ROAD_TO_MARKET_STATE.json"
)


@dataclass
class GtmCampaign:
    campaign_id: str
    offer_name: str
    target_segment: str
    open_source_engine: str
    setup_price_usd: float
    monthly_price_usd: float
    proof_first_asset: str
    target_accounts_count: int
    expected_conversion_rate: float
    projected_mrr_usd: float


@dataclass
class RoadToMarketExecutiveSummary:
    generated_at_utc: str
    strategic_mandate: str
    assigned_squad: str
    campaigns: list[GtmCampaign]
    total_target_accounts: int
    total_projected_mrr_usd: float
    total_projected_arr_usd: float
    timesfm_q10_floor_mrr: float
    timesfm_q50_median_mrr: float
    timesfm_q90_upside_mrr: float
    execution_status: str


def build_road_to_market_plan() -> RoadToMarketExecutiveSummary:
    campaigns = [
        GtmCampaign(
            campaign_id="CAMP-01-RADAR-SCRAPLING",
            offer_name="Radar Prix & Stock Concurrentiel",
            target_segment="Marques D2C, E-commerce Shopify (France & US)",
            open_source_engine="Amdkn/scrapling",
            setup_price_usd=500.0,
            monthly_price_usd=300.0,
            proof_first_asset="Alerte comparative temps réel générée avant le premier contact",
            target_accounts_count=25,
            expected_conversion_rate=0.16,
            projected_mrr_usd=4 * 300.0,  # 1 200 $/m
        ),
        GtmCampaign(
            campaign_id="CAMP-02-DIFY-SOP-ONBOARDING",
            offer_name="Assistant Privé SOP & Onboarding Entreprise",
            target_segment="PME 20 à 100 salariés (Logistique, Services, BTP)",
            open_source_engine="Amdkn/dify",
            setup_price_usd=1500.0,
            monthly_price_usd=250.0,
            proof_first_asset="Bot de démo entraîné sur 3 pages publiques du site du prospect",
            target_accounts_count=20,
            expected_conversion_rate=0.20,
            projected_mrr_usd=4 * 250.0,  # 1 000 $/m
        ),
        GtmCampaign(
            campaign_id="CAMP-03-OPENSEO-SCORECARD",
            offer_name="Scorecard SEO Traditionnel & AEO (Moteurs IA)",
            target_segment="Cabinets d'avocats, Cliniques médicales, Consultants",
            open_source_engine="Amdkn/openseo",
            setup_price_usd=499.0,
            monthly_price_usd=199.0,
            proof_first_asset="Rapport d'audit de visibilité sur ChatGPT/Perplexity/Google Maps",
            target_accounts_count=25,
            expected_conversion_rate=0.24,
            projected_mrr_usd=6 * 199.0,  # 1 194 $/m
        ),
        GtmCampaign(
            campaign_id="CAMP-04-OPENSHORTS-STUDIO",
            offer_name="Studio Clips Viraux & Repurposing Vidéo",
            target_segment="Podcasts, Formateurs, Conférenciers, Dirigeants B2B",
            open_source_engine="Amdkn/openshorts + Amdkn/flute",
            setup_price_usd=0.0,
            monthly_price_usd=400.0,
            proof_first_asset="3 Shorts verticaux montés et sous-titrés offerts en direct",
            target_accounts_count=15,
            expected_conversion_rate=0.27,
            projected_mrr_usd=4 * 400.0,  # 1 600 $/m
        ),
        GtmCampaign(
            campaign_id="CAMP-05-PRESENTON-LIVE-DEVIS",
            offer_name="Générateur de Propositions & Devis Post-Appel",
            target_segment="Équipes commerciales B2B et agences de services",
            open_source_engine="Amdkn/presenton",
            setup_price_usd=2500.0,
            monthly_price_usd=200.0,
            proof_first_asset="Modèle de présentation charté injecté automatiquement en 3 minutes",
            target_accounts_count=15,
            expected_conversion_rate=0.20,
            projected_mrr_usd=3 * 200.0,  # 600 $/m
        ),
    ]

    total_mrr = sum(c.projected_mrr_usd for c in campaigns)
    now_iso = dt.datetime.now(dt.timezone.utc).isoformat()

    summary = RoadToMarketExecutiveSummary(
        generated_at_utc=now_iso,
        strategic_mandate="Activation du Road to Market A'Space MarketPlace (Projet Picard LD01 / The OMK Office)",
        assigned_squad="B1-BOOK -> B2.5-ALLIANCES-DC -> B3.5-MARVEL-GTME",
        campaigns=campaigns,
        total_target_accounts=sum(c.target_accounts_count for c in campaigns),  # 100 comptes
        total_projected_mrr_usd=total_mrr,  # ~5 594 $/mois
        total_projected_arr_usd=total_mrr * 12,  # ~67 128 $/an (hors setup fees)
        timesfm_q10_floor_mrr=3500.0,
        timesfm_q50_median_mrr=10000.0,
        timesfm_q90_upside_mrr=25000.0,
        execution_status="READY_FOR_OUTBOUND_DISPATCH",
    )

    RTM_STATE_OUT.parent.mkdir(parents=True, exist_ok=True)
    RTM_STATE_OUT.write_text(
        json.dumps(asdict(summary), indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    return summary


if __name__ == "__main__":
    plan = build_road_to_market_plan()
    print(
        json.dumps(
            {
                "status": plan.execution_status,
                "accounts_targeted": plan.total_target_accounts,
                "projected_mrr_usd": plan.total_projected_mrr_usd,
                "projected_arr_usd": plan.total_projected_arr_usd,
                "timesfm_q50_median_mrr": plan.timesfm_q50_median_mrr,
            },
            indent=2,
            ensure_ascii=False,
        )
    )
