#!/usr/bin/env python3
"""
A'Space OS V5 — 02_PredictiveWargame_MachineLearning/wargame_business_launch_auditor.py
Exécute un Wargame prédictif (MiroFish Swarm × Mitra-v2 × Chronos-2/TimesFM × PathFM-Chaotic)
pour identifier et combler les points faibles avant le lancement de production de valeur
de Business OS (LD01) au sein d'Areas OS (LD01..LD08).
D-N052 R1 — INFÉRENCE RÉELLE.

Changements R1 (design Clara, §D2/D3/D9) :
- Les 4 scénarios codés en dur avec des nombres inventés sont MORTS
  (friction 0.78/0.71/0.64/0.59, Mitra 0.91/0.95/0.96/0.93, planchers USD
  3200/4500/5000/5400, résilience 0.88/0.94/0.92/0.90). Les TEXTES des
  points faibles et des remédiations sont conservés (connaissance métier) ;
  les NOMBRES viennent désormais des vrais modèles sur la vraie trace :
  - friction = 1 − consensus de l'essaim réel (moteur tabulaire) ;
  - probabilité Mitra = vraie inférence Mitra-v2 sur les nœuds réels ;
  - quantiles temporels = vrai Chronos-2 (commercial) ou vrai TimesFM 3.0
    (interne) sur la série d'activité réelle de la trace (steps/heure) ;
  - résilience = vrais rollouts PathFM-Chaotic-75M (fraction des couples
    (échantillon, pas) restant dans l'enveloppe [q10, q90] sur l'horizon).
- Les champs USD sont renommés : la série réelle est une activité
  (workflows/heure), pas un cashflow — afficher des USD serait un mensonge.
  `temporal_q10` / `temporal_median` + `temporal_model` + `temporal_units`.
- Les 4 scénarios partagent l'état réel courant (même essaim, même série) :
  la différenciation est dans le point faible et la remédiation, pas dans
  des nombres inventés par scénario. La probabilité est celle de l'état
  courant (l'effet de la correction n'est pas modélisé — le champ ne dit
  plus « after fix »).
- Profil : l'auditeur est un wargame INTERNE d'A0 (TabFM, TimesFM et PathFM
  sont Non-Commercial, CC-BY-NC-4.0 pour PathFM) — jamais un produit
  commercial. Sans trace : « pas de données », pas de simulation.
"""

from __future__ import annotations

import json
from collections import Counter
from dataclasses import asdict, dataclass
from pathlib import Path

from aspace_precheck_weights import NoDataError, load_mirofish_nodes
from triptych_autogluon_engine import TriptychWargameOrchestrator
from wargame_tabular_engine import PredictiveWargameEngine

ROOT = Path(__file__).resolve().parents[3]
REPORT_OUT = (
    ROOT
    / "00_Memoire"
    / "bundle"
    / "areas_os"
    / "B_LD01_Business_AMP"
    / "WARGAME_LAUNCH_AUDIT.md"
)
SHEET_SCHEMA_OUT = (
    ROOT
    / "00_Memoire"
    / "bundle"
    / "areas_os"
    / "areas_os_master_sheets_schema.json"
)

# Connaissance métier : les 4 points faibles connus et leurs remédiations.
# Les textes sont conservés ; les nombres sont désormais calculés.
SCENARIOS = [
    {
        "rank": 1,
        "area_code": "LD01 (Business OS / OMK Office)",
        "weak_point": "Absence de pont transactionnel automatique entre les audits Treg/Impeccable et le registre client Google Sheets",
        "remediation_hook_or_module": "02_Factory/gws_lifeos_n8n_dispatcher.py + Onglet B_LD01_BUSINESS_OS",
    },
    {
        "rank": 2,
        "area_code": "LD08 / Tech OS (VPS & WSL Cattle Nodes)",
        "weak_point": "Perte d'état ou divergence Git si le VPS, le WSL CoolEmbrl ou le PC local tombe en cours de session",
        "remediation_hook_or_module": "02_Factory/hooks/aspace_turn_persistence_daemon.py (Branche turns/<hostname>/<date>)",
    },
    {
        "rank": 3,
        "area_code": "LD07 / FKB06_Video_SaaS & FKB03_3DWorlds",
        "weak_point": "Saturation du dépôt Git par les fichiers vidéos .mp4 et scènes 3D .glb de City Office",
        "remediation_hook_or_module": "Offload CAS SHA-256 vers le Bucket Google Drive 5 To (4,99 To disponibles)",
    },
    {
        "rank": 4,
        "area_code": "LD02 (Finances) & FreeComputeAPI",
        "weak_point": "Épuisement silencieux des quotas gratuits (Codespaces, Upstash, Cloud Shell) par oubli d'extinction",
        "remediation_hook_or_module": "Stop Hook Atomique (`aspace_deterministic_hooks.py` + `aspace_freecompute_router.py`)",
    },
]


@dataclass
class WargameWeakPointAudit:
    rank: int
    area_code: str
    weak_point: str
    mirofish_swarm_friction: float
    mitra_win_probability: float
    temporal_q10: float
    temporal_median: float
    temporal_model: str
    temporal_units: str
    pathfm_chaos_resilience: float
    remediation_hook_or_module: str


def get_areas_os_10_sheets_schema() -> dict:
    """Structure les 10 onglets du registre Google Sheets Areas OS."""
    schema = _BASE_SCHEMA
    # Le radar reflète désormais les sorties réelles (modèle temporel nommé,
    # unités de la série réelle, pas d'USD inventés).
    schema["sheets"][0]["columns"] = [
        "Timestamp",
        "Scenario_ID",
        "Target_Area",
        "Weak_Point_Detected",
        "Mitra_Win_Prob",
        "Temporal_q10",
        "Temporal_Median",
        "Temporal_Model",
        "Temporal_Units",
        "PathFM_Chaos_Resilience",
        "Action_Prescribed",
        "Git_Commit_SHA",
    ]
    return schema


_BASE_SCHEMA = {
    "spreadsheet_title": "00 — LIFE OS 2026 · Cockpit 6 Frameworks × 8 Domaines (Areas OS Master Ledger)",
    "sheets": [
        {
            "index": 0,
            "name": "00_WARGAME_RADAR",
            "purpose": "Surveillance prédictive MiroFish × Mitra-v2 × Chronos-2/TimesFM × PathFM",
            "columns": [],
        },
        {
            "index": 1,
            "name": "B_LD01_BUSINESS_OS",
            "purpose": "Pipeline commercial & facturation The OMK Office (300 $/an × 100 clients)",
            "columns": [
                "Deal_ID",
                "Client_Segment",
                "Offre_OMK",
                "Squad_Marvel_Assignee",
                "Manager_DC",
                "Statut_Pipeline",
                "MRR_ARR_USD",
                "Cout_Tokens_Compute",
                "Lien_Artefact_Drive_5TB",
                "Commit_Preuve_GitHub",
            ],
        },
        {
            "index": 2,
            "name": "C_LD02_FINANCES",
            "purpose": "Consolidation Trésorerie, Dividendes A0 & FreeCompute Savings",
            "columns": [
                "Holon_Owner",
                "Objectif_12WY",
                "KPI_Actuel",
                "Cible_Quantile_q90",
                "Statut_Gate_Beth",
                "Dernier_Artefact_Drive_URI",
                "Dernier_Commit_SHA",
            ],
        },
        {
            "index": 3,
            "name": "D_LD03_SANTE_VITAL",
            "purpose": "Bouclier Homéostatique Beth LD03 (Sommeil, VRC, Sanctuaire 00h-05h)",
            "columns": [
                "Holon_Owner",
                "Objectif_12WY",
                "KPI_Actuel",
                "Cible_Quantile_q90",
                "Statut_Gate_Beth",
                "Dernier_Artefact_Drive_URI",
                "Dernier_Commit_SHA",
            ],
        },
        {
            "index": 4,
            "name": "E_LD04_COGNITION",
            "purpose": "Focus Deep Work, Anti-Burnout & Modèles Inférence Souverains",
            "columns": [
                "Holon_Owner",
                "Objectif_12WY",
                "KPI_Actuel",
                "Cible_Quantile_q90",
                "Statut_Gate_Beth",
                "Dernier_Artefact_Drive_URI",
                "Dernier_Commit_SHA",
            ],
        },
        {
            "index": 5,
            "name": "F_LD05_RELATIONS",
            "purpose": "Cercle Intime, Famille & Alignement Éthique",
            "columns": [
                "Holon_Owner",
                "Objectif_12WY",
                "KPI_Actuel",
                "Cible_Quantile_q90",
                "Statut_Gate_Beth",
                "Dernier_Artefact_Drive_URI",
                "Dernier_Commit_SHA",
            ],
        },
        {
            "index": 6,
            "name": "G_LD06_ENVIRONNEMENT",
            "purpose": "Espaces physiques, Infrastructure VPS/WSL, Domotique",
            "columns": [
                "Holon_Owner",
                "Objectif_12WY",
                "KPI_Actuel",
                "Cible_Quantile_q90",
                "Statut_Gate_Beth",
                "Dernier_Artefact_Drive_URI",
                "Dernier_Commit_SHA",
            ],
        },
        {
            "index": 7,
            "name": "H_LD07_CREATIVITE",
            "purpose": "Design, Production Vidéo SaaS (10 Moteurs FKB07), 3D Worlds",
            "columns": [
                "Holon_Owner",
                "Objectif_12WY",
                "KPI_Actuel",
                "Cible_Quantile_q90",
                "Statut_Gate_Beth",
                "Dernier_Artefact_Drive_URI",
                "Dernier_Commit_SHA",
            ],
        },
        {
            "index": 8,
            "name": "I_LD08_IMPACT_ASPACE",
            "purpose": "Rayonnement Planétaire A'Space OS, Open Source & 578 Holons",
            "columns": [
                "Holon_Owner",
                "Objectif_12WY",
                "KPI_Actuel",
                "Cible_Quantile_q90",
                "Statut_Gate_Beth",
                "Dernier_Artefact_Drive_URI",
                "Dernier_Commit_SHA",
            ],
        },
        {
            "index": 9,
            "name": "99_CAS_BUCKET_5TB_INDEX",
            "purpose": "Indexation globale du Bucket Google Drive 5 To (Actifs Multimédias & 3D)",
            "columns": [
                "SHA256_Hash",
                "Nom_Fichier",
                "Categorie",
                "Taille_Mo",
                "Area_LD",
                "Drive_URI",
                "Produit_Par_Noeud",
                "Commit_Git_Associe",
            ],
            "initial_seed_assets": [
                {
                    "Nom_Fichier": "OS_Souverain__Liberté_Digitale.mp4",
                    "Taille_Mo": 48.4,
                    "Categorie": "Video_MP4",
                    "Area_LD": "LD01",
                    "Drive_URI": "https://drive.google.com/file/d/1B1-video-os-souverain/view",
                },
                {
                    "Nom_Fichier": "Legal_OS__Le_Cabinet_Zéro-Admin.mp4",
                    "Taille_Mo": 45.6,
                    "Categorie": "Video_MP4",
                    "Area_LD": "LD01",
                    "Drive_URI": "https://drive.google.com/file/d/1B1-video-legal-os/view",
                },
                {
                    "Nom_Fichier": "A_Space_OS__Haute_Performance.mp4",
                    "Taille_Mo": 44.2,
                    "Categorie": "Video_MP4",
                    "Area_LD": "LD08",
                    "Drive_URI": "https://drive.google.com/file/d/1B1-video-haute-perf/view",
                },
                {
                    "Nom_Fichier": "Le_Jardin_des_Pensées.mp4",
                    "Taille_Mo": 35.6,
                    "Categorie": "Video_MP4",
                    "Area_LD": "LD04",
                    "Drive_URI": "https://drive.google.com/file/d/1B1-video-jardin-pensees/view",
                },
                {
                    "Nom_Fichier": "Designing A'Space Planetary World Map.png",
                    "Taille_Mo": 111.7,
                    "Categorie": "Image_Design_Map",
                    "Area_LD": "LD08",
                    "Drive_URI": "https://drive.google.com/file/d/1B1-design-world-map/view",
                },
            ],
        },
    ],
}


def build_activity_series(nodes: list[dict]) -> tuple[list[float], str]:
    """Série d'activité réelle : nombre de steps par heure de la trace.

    L'heure est lue dans `updated_at` (champ réel de durable_steps).
    Retourne (série, unités).
    """
    hours = Counter(
        str(node.get("provenance", {}).get("updated_at") or "")[:13] for node in nodes
    )
    if not hours:
        raise NoDataError("pas de données : aucun horodatage dans la trace")
    keys = sorted(hours)
    # Comble les heures vides entre la première et la dernière (0 = pas d'activité).
    from datetime import datetime, timedelta

    fmt = "%Y-%m-%dT%H"
    try:
        start = datetime.strptime(keys[0], fmt)
        end = datetime.strptime(keys[-1], fmt)
    except ValueError:
        # Horodatages non ISO : série dans l'ordre d'apparition, sans comblement.
        return [float(hours[k]) for k in keys], "steps/heure (ordre brut)"
    series: list[float] = []
    cur = start
    while cur <= end:
        series.append(float(hours.get(cur.strftime(fmt), 0)))
        cur += timedelta(hours=1)
    return series, "steps/heure"


def pathfm_chaos_resilience(
    series: list[float],
    q10: list[float],
    q90: list[float],
    weights_root=None,
    horizon: int = 12,
    num_samples: int = 16,
) -> float:
    """Résilience chaos réelle (PathFM-Chaotic-75M, CC-BY-NC-4.0, interne).

    Échantillonne `num_samples` trajectoires depuis le contexte réel et
    compte la fraction des couples (échantillon, pas) qui restent dans
    l'enveloppe [q10, q90] du modèle temporel sur l'horizon. 1.0 = toutes
    les trajectoires restent dans la bande plausible, 0.0 = aucune.
    (La variante stricte — fraction des chemins ENTIÈREMENT dans
    l'enveloppe — vaut 0.0 dès que la bande est étroite ; elle n'informe
    pas. La fraction par (échantillon, pas) est graduée.) Sans poids
    montés : WeightsNotMountedError.
    """
    import numpy as np
    from pathfm import PathFMPipeline

    from aspace_precheck_weights import model_dir

    local_dir = model_dir("pathfm-chaotic-75m", weights_root)
    pipeline = PathFMPipeline.from_pretrained(str(local_dir), device="cpu")
    context = np.array(series, dtype=np.float32).reshape(1, 1, -1)
    paths = pipeline.predict_samples(context, prediction_length=horizon)
    # predict_samples retourne une liste de tenseurs [targets, samples, horizon].
    tensor = paths[0]
    samples = tensor.numpy() if hasattr(tensor, "numpy") else np.asarray(tensor)
    # samples : [1, num_samples, horizon] (1 canal).
    samples = samples[0]  # [num_samples, horizon]
    q10_arr = np.array(q10, dtype=float)[:horizon]
    q90_arr = np.array(q90, dtype=float)[:horizon]
    inside = (samples >= q10_arr[None, :]) & (samples <= q90_arr[None, :])
    return float(inside.mean())


def run_launch_wargame_simulation(
    factory_sqlite=None,
    weights_root=None,
    horizon: int = 12,
) -> list[WargameWeakPointAudit]:
    """Audit réel : nœuds de la trace + Mitra-v2 + Chronos-2/TimesFM + PathFM.

    Profil interne (TabFM/TimesFM/PathFM Non-Commercial). Sans trace :
    NoDataError (« pas de données »). Écrit le rapport MD + le schéma JSON.
    """
    nodes = load_mirofish_nodes(factory_sqlite=factory_sqlite)
    engine = PredictiveWargameEngine(mode="internal_dual_jury", weights_root=weights_root)
    rows = engine.extract_mirofish_tabular_matrix(nodes)
    labels: list[int] = []
    labeled_rows: list[dict[str, float]] = []
    for node, row in zip(nodes, rows):
        status = str(node.get("provenance", {}).get("status") or "").lower()
        if status in ("completed", "success", "succeeded", "done"):
            labeled_rows.append(row)
            labels.append(1)
        elif status == "failed":
            labeled_rows.append(row)
            labels.append(0)
    if len(set(labels)) < 2:
        raise NoDataError(
            "pas de données : la trace ne contient pas les deux verdicts "
            "(succès et échec requis pour le contexte ICL)"
        )

    triptych = TriptychWargameOrchestrator(
        execution_profile="a0_internal_wargame", weights_root=weights_root
    )
    series, units = build_activity_series(nodes)
    report = triptych.evaluate_wargame_state(
        [series], labeled_rows, labels, rows[-1], horizon=horizon
    )
    # Enveloppe temporelle complète pour PathFM (pas seulement le pas 1).
    _, q10_full, _, q90_full = triptych._forecast(series, horizon)
    resilience = pathfm_chaos_resilience(
        series, q10_full, q90_full, weights_root=weights_root, horizon=horizon
    )
    friction = round(1.0 - report.epistemic_consensus, 4)

    audits = [
        WargameWeakPointAudit(
            rank=s["rank"],
            area_code=s["area_code"],
            weak_point=s["weak_point"],
            mirofish_swarm_friction=friction,
            mitra_win_probability=report.mitra_win_probability,
            temporal_q10=report.temporal_q10,
            temporal_median=report.temporal_median,
            temporal_model=report.temporal_model,
            temporal_units=units,
            pathfm_chaos_resilience=round(resilience, 4),
            remediation_hook_or_module=s["remediation_hook_or_module"],
        )
        for s in SCENARIOS
    ]

    md_lines = [
        "---",
        "title: Audit Wargame Prédictif de Lancement — Business OS (LD01) & Nœuds Jetables",
        "type: concept",
        "status: ACTIVE_PRODUCTION_GATE",
        "---",
        "",
        "# Wargame MiroFish × Mitra-v2 × Chronos-2/TimesFM × PathFM : Points Faibles & Remédiations",
        "",
        "Nombres réels (D-N052 R1) : Mitra-v2 + TabFM (interne) sur les nœuds réels, "
        f"modèle temporel {report.temporal_model} sur la série d'activité réelle "
        f"({units}, {len(series)} points), PathFM-Chaotic-75M (rollouts). "
        "Les 4 scénarios partagent l'état réel courant ; la différenciation est "
        "dans le point faible et la remédiation.",
        "",
        "| Rang | Domaine | Point Faible | Probabilité Mitra-v2 | Plancher q10 (temporel) | Résilience Chaos (PathFM) | Module Correctif |",
        "|---|---|---|---|---|---|---|",
    ]
    for a in audits:
        md_lines.append(
            f"| {a.rank} | **{a.area_code}** | {a.weak_point} | `{a.mitra_win_probability * 100:.1f}%` "
            f"| `{a.temporal_q10:.2f} {a.temporal_units}` | `{a.pathfm_chaos_resilience * 100:.1f}%` | `{a.remediation_hook_or_module}` |"
        )

    REPORT_OUT.parent.mkdir(parents=True, exist_ok=True)
    REPORT_OUT.write_text("\n".join(md_lines) + "\n", encoding="utf-8")

    schema = get_areas_os_10_sheets_schema()
    SHEET_SCHEMA_OUT.parent.mkdir(parents=True, exist_ok=True)
    SHEET_SCHEMA_OUT.write_text(
        json.dumps(schema, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )

    return audits


if __name__ == "__main__":
    import sys

    db = sys.argv[1] if len(sys.argv) > 1 else None
    try:
        audits = run_launch_wargame_simulation(factory_sqlite=db)
    except NoDataError as exc:
        print(f"pas de données : {exc}")
        raise SystemExit(2)
    print(json.dumps([asdict(a) for a in audits], indent=2, ensure_ascii=False))
