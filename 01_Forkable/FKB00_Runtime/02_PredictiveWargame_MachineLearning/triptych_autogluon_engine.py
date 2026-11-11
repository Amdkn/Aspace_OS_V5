#!/usr/bin/env python3
"""
A'Space OS V5 — 01_Forkable/FKB00_Runtime/02_PredictiveWargame_MachineLearning
Triptyque Neuro-Prédictif : AutoGluon (Mitra-v2) x Google TabFM 1.1.0 x Google TimesFM 3.0
D-N052 R1 — INFÉRENCE RÉELLE.

Changements R1 (design Clara, §D2/D3) :
- L'extrapolation linéaire « TimesFM » est MORTE (elle prétendait être
  TimesFM 3.0 : `projected_median = last + drift·horizon·0.25`, spread
  arbitraire). L'axe temporel appelle le vrai Chronos-2
  (`chronos-forecasting`, poids montés) en profil commercial, et le vrai
  TimesFM 3.0 (`timesfm`, poids montés) en profil interne.
- La probabilité « Mitra-v2 » (somme pondérée 0.40/0.35/0.25) est MORTE :
  le volet tabulaire appelle le vrai Mitra-v2 (et TabFM en interne) via le
  moteur tabulaire (`wargame_tabular_engine.py`) — même code, mêmes poids.
- Les champs du rapport sont renommés pour dire la vérité : `temporal_q10`
  / `temporal_median` / `temporal_q90` + `temporal_model` (le modèle qui a
  réellement produit les quantiles) ; `timesfm_*` ne nommait pas le modèle.
- Aucun chargement depuis le Hub à l'exécution : poids montés
  (mount-weights.sh, vérifiés taille + oid) ; absents -> WeightsNotMountedError.
- Confinement §D3 : le profil `b2b_commercial` ne charge ni n'appelle jamais
  TabFM ni TimesFM. L'axe temporel commercial est Chronos-2, pas TimesFM.
"""

from __future__ import annotations

import hashlib
import json
import math
from dataclasses import asdict, dataclass
from typing import Literal

from aspace_precheck_weights import (
    WeightsNotMountedError,
    assert_commercial_safe,
    model_dir,
)
from wargame_tabular_engine import PredictiveWargameEngine

# Contexte minimal pour les modèles temporels (Chronos-2 / TimesFM).
MIN_CONTEXT = 32


@dataclass
class TriptychForecastReport:
    scenario_id: str
    horizon_steps: int
    temporal_q10: float
    temporal_median: float
    temporal_q90: float
    temporal_model: str  # "chronos-2" (commercial) ou "timesfm-3.0" (interne)
    mitra_win_probability: float
    tabfm_win_probability: float | None
    epistemic_consensus: float
    recommended_directive: str
    license_profile: str


class TriptychWargameOrchestrator:
    """
    Orchestre :
      1. Axe Temporel : Chronos-2 (commercial) ou TimesFM 3.0 (interne) — réel.
      2. Axe Tabulaire : AutoGluon Mitra-v2 (12L) + Google TabFM 1.1.0 (24L, interne) — réel.
    """

    def __init__(
        self,
        execution_profile: Literal["b2b_commercial", "a0_internal_wargame"] = "a0_internal_wargame",
        weights_root=None,
    ):
        self.execution_profile = execution_profile
        self.weights_root = weights_root
        self.models = {
            "orchestrator": "autogluon/autogluon",
            "mitra_cls": "autogluon/mitra-classifier-2",
            "mitra_reg": "autogluon/mitra-regressor-2",
            "tabfm": "google/tabfm-1.1.0-pytorch",
            "timesfm3": "google/timesfm-3.0-pytorch",
        }
        self.tabular = PredictiveWargameEngine(
            mode="commercial_apache2"
            if execution_profile == "b2b_commercial"
            else "internal_dual_jury",
            weights_root=weights_root,
        )
        self._chronos = None
        self._timesfm = None

    # -- Chargement paresseux des vrais modèles temporels (poids montés) --
    def _load_chronos(self):
        if self._chronos is None:
            from chronos import Chronos2Pipeline

            local_dir = model_dir("chronos-2", self.weights_root)
            self._chronos = Chronos2Pipeline.from_pretrained(
                str(local_dir), device_map="cpu"
            )
        return self._chronos

    def _load_timesfm(self):
        if self.execution_profile != "a0_internal_wargame":
            raise ValueError(
                "TimesFM est confiné au profil interne (§D3) — profil commercial interdit"
            )
        if self._timesfm is None:
            from timesfm3 import TimesFM3Forecaster

            local_dir = model_dir("timesfm-3.0-pytorch", self.weights_root)
            # from_pretrained accepte un dossier local (pas de téléchargement Hub).
            self._timesfm = TimesFM3Forecaster.from_pretrained(
                str(local_dir), device="cpu"
            )
        return self._timesfm

    def forecast_multivariate_series(
        self,
        series_matrix: list[list[float]],
        horizon: int = 64,
    ) -> dict[str, float]:
        """
        Prévision temporelle RÉELLE sur la série primaire (series_matrix[0]) :
        Chronos-2 en commercial, TimesFM 3.0 en interne. Retourne q10, médiane,
        q90 du premier pas de l'horizon (le pas 1, le plus fiable).
        """
        if not series_matrix or not series_matrix[0]:
            raise ValueError("pas de données : série temporelle vide")
        series = [float(v) for v in series_matrix[0]]
        if len(series) < MIN_CONTEXT:
            raise ValueError(
                f"série trop courte pour le contexte temporel : {len(series)} points "
                f"(minimum {MIN_CONTEXT})"
            )
        if any(not math.isfinite(v) for v in series):
            raise ValueError("série temporelle : valeur non finie (NaN/inf) interdite")
        if horizon <= 0:
            raise ValueError("horizon doit être > 0")
        model_name, q10, med, q90 = self._forecast(series, horizon)
        return {
            "q10": round(q10[0], 4),
            "median": round(med[0], 4),
            "q90": round(q90[0], 4),
            "model": model_name,
        }

    def _forecast(
        self, series: list[float], horizon: int
    ) -> tuple[str, list[float], list[float], list[float]]:
        if self.execution_profile == "b2b_commercial":
            return self._forecast_chronos(series, horizon)
        return self._forecast_timesfm(series, horizon)

    def _forecast_chronos(
        self, series: list[float], horizon: int
    ) -> tuple[str, list[float], list[float], list[float]]:
        import pandas as pd

        pipeline = self._load_chronos()
        n = len(series)
        context_df = pd.DataFrame(
            {
                "item_id": 0,
                "timestamp": pd.date_range("2020-01-01", periods=n, freq="h"),
                "target": series,
            }
        )
        pred_df = pipeline.predict_df(context_df, prediction_length=horizon)
        return (
            "chronos-2",
            self._quantile_col(pred_df, 0.1),
            self._quantile_col(pred_df, 0.5),
            self._quantile_col(pred_df, 0.9),
        )

    @staticmethod
    def _quantile_col(pred_df, q: float) -> list[float]:
        """Extrait la colonne quantile q du DataFrame de prévision Chronos-2.

        Chronos-2 nomme ses colonnes de quantiles par la valeur du quantile
        (0.1 / 0.5 / 0.9) ; on accepte aussi les noms 'q10'/'median'/'q90'.
        """
        candidates = {
            0.1: ["0.1", "q10", "q_0.1", "quantile_0.1"],
            0.5: ["0.5", "median", "q50", "q_0.5", "quantile_0.5", "predictions"],
            0.9: ["0.9", "q90", "q_0.9", "quantile_0.9"],
        }[q]
        cols = {str(c): c for c in pred_df.columns}
        for name in candidates:
            if name in cols:
                return [float(v) for v in pred_df[cols[name]].tolist()]
        raise ValueError(
            f"Chronos-2 : colonne quantile {q} introuvable "
            f"(colonnes : {list(pred_df.columns)})"
        )

    def _forecast_timesfm(
        self, series: list[float], horizon: int
    ) -> tuple[str, list[float], list[float], list[float]]:
        import numpy as np

        forecaster = self._load_timesfm()
        # TimesFM 3.0 : quantiles [0.1..0.9] (9), médiane = index 4.
        out = forecaster.predict(
            context=np.array(series, dtype=float),
            horizon=horizon,
            return_quantiles=True,
        )
        q = np.asarray(out.quantiles)  # [horizon, 9]
        if q.ndim == 1:
            q = q.reshape(horizon, -1)
        return (
            "timesfm-3.0",
            [float(row[0]) for row in q],
            [float(row[4]) for row in q],
            [float(row[8]) for row in q],
        )

    def evaluate_wargame_state(
        self,
        series_matrix: list[list[float]],
        context_rows: list[dict[str, float]],
        context_labels: list[int],
        query_row: dict[str, float],
        horizon: int = 64,
    ) -> TriptychForecastReport:
        """
        1. Projection temporelle réelle (Chronos-2 commercial / TimesFM 3.0 interne).
        2. Probabilité tabulaire réelle via Mitra-v2 (et TabFM 1.1.0 si profil interne).
        Les entrées sont RÉELLES (nœuds MiroFish via le chargeur, série réelle) —
        aucune valeur par défaut inventée.
        """
        if self.execution_profile == "b2b_commercial":
            assert_commercial_safe(["mitra-classifier-2", "chronos-2"])
        ts = self.forecast_multivariate_series(series_matrix, horizon=horizon)
        tab = self.tabular.run_icl_inference(context_rows, context_labels, query_row)

        if self.execution_profile == "a0_internal_wargame":
            consensus = tab.ensemble_confidence
            license_tag = "INTERNAL_R&D (TabFM + TimesFM Non-Commercial + Mitra Apache-2.0)"
        else:
            consensus = tab.ensemble_confidence
            license_tag = "COMMERCIAL_SAFE (AutoGluon + Mitra-v2 + Chronos-2 Apache-2.0)"

        directive = (
            "GREENLIGHT_EXECUTION"
            if (tab.mitra_prob >= 0.65 and consensus >= 0.75)
            else "DEFENSIVE_HOLD_OR_HEDGE"
        )

        scenario_id = "TRIPTYCH-" + hashlib.sha256(
            json.dumps(
                {"series_last": series_matrix[0][-1], "query": query_row},
                sort_keys=True,
            ).encode()
        ).hexdigest()[:8]
        return TriptychForecastReport(
            scenario_id=scenario_id,
            horizon_steps=horizon,
            temporal_q10=ts["q10"],
            temporal_median=ts["median"],
            temporal_q90=ts["q90"],
            temporal_model=ts["model"],
            mitra_win_probability=tab.mitra_prob,
            tabfm_win_probability=tab.tabfm_prob,
            epistemic_consensus=round(consensus, 4),
            recommended_directive=directive,
            license_profile=license_tag,
        )


if __name__ == "__main__":
    import sys

    from aspace_precheck_weights import NoDataError, load_mirofish_nodes

    profile = sys.argv[1] if len(sys.argv) > 1 else "a0_internal_wargame"
    db = sys.argv[2] if len(sys.argv) > 2 else None
    orchestrator = TriptychWargameOrchestrator(execution_profile=profile)  # type: ignore[arg-type]
    try:
        nodes = load_mirofish_nodes(factory_sqlite=db)
    except NoDataError as exc:
        print(f"pas de données : {exc}")
        raise SystemExit(2)
    rows = orchestrator.tabular.extract_mirofish_tabular_matrix(nodes)
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
    # Série d'activité réelle : nombre de steps par jour de la trace.
    from collections import Counter

    days = Counter(
        str(node.get("provenance", {}).get("updated_at") or "")[:10] for node in nodes
    )
    series = [float(days[d]) for d in sorted(days)]
    report = orchestrator.evaluate_wargame_state(
        [series], labeled_rows, labels, rows[-1], horizon=12
    )
    print(json.dumps(asdict(report), indent=2, ensure_ascii=False))
