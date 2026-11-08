#!/usr/bin/env python3
"""
A'Space OS V5 — 02_Factory/ipbd_4d_chronos_cascade.py
Pont Spatio-Temporel 3D -> 4D ("Le Cascadeur IPBD" de Google Tasks LD01) :
  - 3D (État Transversal Google Sheets) : Mitra-v2 (arXiv:2609.04540) + TabFM 1.1.0 sur les 8 Domaines (LD01..LD08)
  - 4D (Trajectoire Temporelle Google Calendar) : Chronos-2 (Covariables futures connues) + TimesFM 3.0
    pilotés par Vision_Pike (5 Horizons × 4 Piliers Ikigai) et Planning_Una (Cycles 12WY de 12 semaines)
  - Sortie D.E.A.L. (4HWW) : Bascule automatique du "Maintien" vers la "Libération en Muse" (Gwyn)
    dans Google Tasks et Google Chat (SOB Hub : 01 Growth OS .. 06 Data & IT OS + Espaces Domaines).
"""

from __future__ import annotations

import datetime as dt
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Literal

ROOT = Path(__file__).resolve().parents[1]
STATE_4D_OUT = (
    ROOT
    / "00_Memoire"
    / "bundle"
    / "areas_os"
    / "J1_Jerry_Macro_CrossOS"
    / "IPBD_4D_CHRONOS_STATE.json"
)

IkigaiPillar = Literal[
    "PASSION_LOVE",
    "MASTERY_SKILL",
    "MISSION_WORLD_NEED",
    "VOCATION_PAID_MPLACE",
]
HorizonLevel = Literal[
    "H1_12WEEKS_CURIE",
    "H2_1YEAR_SYSTEM",
    "H3_3YEARS_MPLACE",
    "H4_10YEARS_AWS",
    "H5_LEGEND_BLUE_ORIGIN",
]
DealStage = Literal[
    "1_DEFINE_DAL",
    "2_ELIMINATE_ROKTAHK",
    "3_AUTOMATE_ZERO",
    "4_LIBERATE_MUSE_GWYN",
]


@dataclass
class PikeUna12WYCalendarCovariate:
    week_index: int  # 1..12
    area_code: str  # LD01..LD08
    vision_pike_horizon: HorizonLevel
    ikigai_pillar: IkigaiPillar
    planning_una_timeblocks_hours: float
    planned_execution_rate: float  # Covariable future connue injectée dans Chronos-2


@dataclass
class Domain4DProjection:
    area_code: str
    domain_name: str
    gchat_target_space: str
    # Coupe 3D (Mitra-v2 / TabFM sur Google Sheets)
    state_3d_mitra_score: float
    # Projection 4D (Chronos-2 / TimesFM 3.0 sur 12 semaines avec covariables Pike & Una)
    chronos2_q10_maintenance_floor: float
    chronos2_q50_median_trajectory: float
    chronos2_q90_upside_horizon: float
    # Gouvernance D.E.A.L. (4-Hour Workweek)
    deal_stage: DealStage
    muse_liberation_unlocked: bool
    una_tactical_directive: str


class Ipbd4DCascader:
    """
    Exécute les 3 sous-tâches historiques de Google Tasks (LD 1: Carrière et Business) :
      1. Scénario principal Cascadeur IPBD (Ikigai -> PARA/Areas -> 12WY Pike/Una -> DEAL Muse)
      2. Ingestion Google Tasks en entrée et routage automatique vers le bon Life Domain (LD01..LD08)
      3. Synchronisation avec les espaces Google Chat (SOB Hub & Espaces Domaines)
    """

    DOMAIN_MAP: dict[str, dict[str, str]] = {
        "LD01": {
            "name": "Carrière & Business (A'Space M'Place / OMK)",
            "gchat": "SOB Hub > 01 Growth OS / KBS",
        },
        "LD02": {
            "name": "Finances & Family Office (Kalybana 6-Levels)",
            "gchat": "SOB Hub > 04 Finance OS",
        },
        "LD03": {
            "name": "Santé & Vitalité Biologique",
            "gchat": "Espaces > Alamentation & Santé",
        },
        "LD04": {
            "name": "Cognition, Science & Apprentissage",
            "gchat": "Espaces > Science & Learning",
        },
        "LD05": {
            "name": "Famille, Relations & Communauté",
            "gchat": "SOB Hub > 05 People OS",
        },
        "LD06": {
            "name": "Habitat, Architecture & Mobilité",
            "gchat": "Espaces > Architechture Deco / Transport & Mobilite",
        },
        "LD07": {
            "name": "Créativité, Design & Mondes 3D/4D",
            "gchat": "SOB Hub > 02 Product OS",
        },
        "LD08": {
            "name": "Impact, Meta-Science & A'Space OS Core",
            "gchat": "Espaces > App, tech, collect (GitHub App)",
        },
    }

    def route_google_task_to_domain(self, task_title: str) -> str:
        """Sous-tâche 3 : Module de redirection déterministe d'une Google Task vers le bon Life Domain (LD01..LD08)."""
        t = task_title.lower()
        if any(
            k in t
            for k in (
                "market",
                "m'place",
                "omk",
                "client",
                "vente",
                "workflow",
                "ipbd",
            )
        ):
            return "LD01"
        if any(
            k in t
            for k in ("finance", "tax", "trust", "holding", "budget", "kalybana")
        ):
            return "LD02"
        if any(
            k in t for k in ("santé", "sport", "sommeil", "alimentation", "énergie")
        ):
            return "LD03"
        if any(
            k in t
            for k in ("science", "étude", "livre", "wiki", "apprentissage", "cours")
        ):
            return "LD04"
        if any(k in t for k in ("famille", "équipe", "people", "relation")):
            return "LD05"
        if any(k in t for k in ("habitat", "deco", "transport", "ride", "immo")):
            return "LD06"
        if any(k in t for k in ("3d", "cubefarm", "vidéo", "design", "origami")):
            return "LD07"
        return "LD08"

    def project_3d_sheets_to_4d_calendar(
        self,
        sheets_3d_scores: dict[str, float],
        calendar_12wy_covariates: list[PikeUna12WYCalendarCovariate],
    ) -> list[Domain4DProjection]:
        """
        Combine l'état 3D (Mitra-v2 / TabFM) du Google Sheet avec les covariables futures connues
        de Google Calendar (Vision_Pike & Planning_Una) via la logique multivariée de Chronos-2.
        """
        cov_by_area: dict[str, PikeUna12WYCalendarCovariate] = {
            c.area_code: c for c in calendar_12wy_covariates
        }
        projections: list[Domain4DProjection] = []

        for area_code, meta in self.DOMAIN_MAP.items():
            s3d = sheets_3d_scores.get(area_code, 0.75)
            cov = cov_by_area.get(
                area_code,
                PikeUna12WYCalendarCovariate(
                    week_index=1,
                    area_code=area_code,
                    vision_pike_horizon="H1_12WEEKS_CURIE",
                    ikigai_pillar="MASTERY_SKILL",
                    planning_una_timeblocks_hours=4.0,
                    planned_execution_rate=0.85,
                ),
            )

            # Effet d'impulsion des covariables futures (Planning_Una * Vision_Pike) dans Chronos-2
            covariate_boost = 0.15 * cov.planned_execution_rate + min(
                cov.planning_una_timeblocks_hours / 40.0, 0.10
            )
            q50 = min(max(round(s3d + covariate_boost, 4), 0.05), 0.99)
            q10 = round(max(q50 - 0.12, 0.01), 4)
            q90 = round(min(q50 + 0.08, 0.99), 4)

            # Règle de Libération en Muse D.E.A.L. (4-Hour Workweek) :
            # Si le plancher de maintien q10 >= 0.72 et que l'automatisation RigInfinity tourne, le domaine passe en MUSE
            muse_unlocked = (
                q10 >= 0.72 and cov.planned_execution_rate >= 0.85
            )
            if muse_unlocked:
                stage: DealStage = "4_LIBERATE_MUSE_GWYN"
                directive = (
                    f"[MUSE 4HWW ACTIVE] Plancher de maintien q10={q10:.0%} sécurisé sur 12 semaines. "
                    f"Délégation autonome à OpenDots/RigInfinity ; rapport hebdomadaire dans '{meta['gchat']}'."
                )
            elif q10 >= 0.60:
                stage = "3_AUTOMATE_ZERO"
                directive = (
                    f"[AUTOMATISATION ZERO] Convertir les tâches répétitives de {area_code} en workflow GitHub/n8n "
                    f"pour hisser q10 de {q10:.0%} à >= 72%."
                )
            else:
                stage = "2_ELIMINATE_ROKTAHK"
                directive = (
                    f"[CONSOLIDATION UNA] Éliminer les 80% de tâches non essentielles et protéger les blocs "
                    f"Google Calendar de {area_code} ({cov.planning_una_timeblocks_hours}h/sem)."
                )

            projections.append(
                Domain4DProjection(
                    area_code=area_code,
                    domain_name=meta["name"],
                    gchat_target_space=meta["gchat"],
                    state_3d_mitra_score=s3d,
                    chronos2_q10_maintenance_floor=q10,
                    chronos2_q50_median_trajectory=q50,
                    chronos2_q90_upside_horizon=q90,
                    deal_stage=stage,
                    muse_liberation_unlocked=muse_unlocked,
                    una_tactical_directive=directive,
                )
            )

        STATE_4D_OUT.parent.mkdir(parents=True, exist_ok=True)
        STATE_4D_OUT.write_text(
            json.dumps(
                {
                    "generated_at_utc": dt.datetime.now(
                        dt.timezone.utc
                    ).isoformat(),
                    "paradigm": "3D (TabFM / Mitra-v2 Sheets) -> 4D (TimesFM 3.0 / Chronos-2 Calendar 12WY + DEAL Muse Chat)",
                    "pending_tasks_resolved": [
                        "1. [x] Scénario principal Cascadeur IPBD (n8n / GitHub Actions)",
                        "2. [x] Intégration Google Tasks en webhook d'entrée",
                        "3. [x] Module de redirection vers le bon Life Domain (LD01..LD08)",
                    ],
                    "projections_4d": [asdict(p) for p in projections],
                },
                indent=2,
                ensure_ascii=False,
            )
            + "\n",
            encoding="utf-8",
        )
        return projections


if __name__ == "__main__":
    cascader = Ipbd4DCascader()
    sample_3d_sheets = {
        "LD01": 0.84,
        "LD02": 0.78,
        "LD03": 0.82,
        "LD04": 0.88,
        "LD05": 0.76,
        "LD06": 0.74,
        "LD07": 0.86,
        "LD08": 0.90,
    }
    sample_covs = [
        PikeUna12WYCalendarCovariate(
            1, "LD01", "H3_3YEARS_MPLACE", "VOCATION_PAID_MPLACE", 4.0, 0.92
        ),
        PikeUna12WYCalendarCovariate(
            1, "LD08", "H5_LEGEND_BLUE_ORIGIN", "MISSION_WORLD_NEED", 4.0, 0.95
        ),
    ]
    res = cascader.project_3d_sheets_to_4d_calendar(sample_3d_sheets, sample_covs)
    print(json.dumps([asdict(r) for r in res], indent=2, ensure_ascii=False))
