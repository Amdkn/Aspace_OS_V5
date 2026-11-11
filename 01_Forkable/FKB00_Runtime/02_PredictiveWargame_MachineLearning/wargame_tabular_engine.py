#!/usr/bin/env python3
"""
A'Space OS V5 — 02_PredictiveWargame_MachineLearning/wargame_tabular_engine.py
Pont Neuro-Tabulaire : MiroFish Swarm (OASIS) x AutoGluon Mitra-v2 x Google TabFM 1.1.0
D-N052 R1 — INFÉRENCE RÉELLE.

Changements R1 (design Clara, §D2/D3/D9, hold-out H-R2) :
- Le fallback arithmétique est MORT : `mitra_prob = 0.5 + 0.35·sentiment + ...`
  et `tabfm_prob = mitra_prob·0.96 + ...` sont retirés. La probabilité vient
  du vrai Mitra-v2 (AutoGluon, `autogluon.tabular[mitra]`, poids montés en
  local, `fine_tune=False` = ICL zéro-shot, pas de réentraînement) et, en
  mode interne seulement, du vrai TabFM 1.1.0 (`tabfm` PyPI, poids montés).
- L'entrée est les nœuds MiroFish RÉELS (chargeur `aspace_precheck_weights`,
  depuis factory.sqlite ou un export MiroFish). Sans source : « pas de
  données », pas de simulation (§D9).
- Confinement §D3 : le mode `commercial_apache2` ne charge ni n'appelle
  jamais TabFM (ni TimesFM) — `tabfm_prob` y est toujours None, et la garde
  `assert_commercial_safe` lève si un modèle non-commercial est demandé.
- Aucun chargement depuis le Hub à l'exécution : les poids sont montés
  (mount-weights.sh, vérifiés taille + oid) ; absents -> WeightsNotMountedError.

Choix d'implémentation (nommé, le 13e juge) : Mitra est appelé via
`MitraClassifier` (l'interface sklearn d'AutoGluon, même modèle, mêmes
poids, ICL zéro-shot) plutôt que via `TabularPredictor` — le prédicteur
fait du bagging et des splits train/val conçus pour de gros jeux tabulaires,
pas pour une poignée de lignes de contexte MiroFish. `fine_tune=False`
(max_epochs=0) : aucune mise à jour des poids, l'inférence est purement
en contexte.
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Literal

from aspace_precheck_weights import (
    NoDataError,
    WeightsNotMountedError,
    assert_commercial_safe,
    load_mirofish_nodes,
    model_dir,
)

FEATURES = [
    "agent_influence",
    "sentiment_polarity",
    "epistemic_certainty",
    "anomaly_flag",
    "stancereversal_count",
]


@dataclass
class WargameScenarioResult:
    scenario_id: str
    swarm_consensus_score: float
    mitra_prob: float
    tabfm_prob: float | None
    ensemble_confidence: float
    recommended_action: str
    commercial_safe: bool


class PredictiveWargameEngine:
    def __init__(
        self,
        mode: Literal["commercial_apache2", "internal_dual_jury"] = "commercial_apache2",
        weights_root: str | Path | None = None,
    ):
        """
        - commercial_apache2 : Utilise uniquement autogluon/mitra-classifier-2 (Apache-2.0).
          TabFM n'est jamais chargé ni appelé (confinement §D3).
        - internal_dual_jury : Combine Mitra-v2 + google/tabfm-1.1.0-pytorch (Non-Commercial,
          profil interne uniquement).
        """
        self.mode = mode
        self.weights_root = Path(weights_root) if weights_root is not None else None
        self.mitra_model_id = "autogluon/mitra-classifier-2"
        self.tabfm_model_id = "google/tabfm-1.1.0-pytorch"
        self._mitra = None
        self._tabfm = None

    # -- Chargement paresseux des vrais modèles (poids montés, jamais le Hub) --
    def _load_mitra(self):
        if self._mitra is None:
            from autogluon.tabular.models.mitra.sklearn_interface import MitraClassifier

            local_dir = model_dir("mitra-classifier-2", self.weights_root)
            self._mitra = MitraClassifier(
                hf_model=str(local_dir),
                device="cpu",
                fine_tune=False,  # ICL zéro-shot : aucune mise à jour des poids.
            )
        return self._mitra

    def _load_tabfm(self):
        if self.mode != "internal_dual_jury":
            raise ValueError(
                "TabFM est confiné au profil interne (§D3) — mode commercial interdit"
            )
        if self._tabfm is None:
            from tabfm import TabFMClassifier
            from tabfm.src.pytorch.tabfm_v1_0_0 import load as tabfm_load

            local_dir = model_dir("tabfm-1.1.0-pytorch", self.weights_root)
            # load() accepte un dossier local (checkpoint_path) : il utilise
            # le sous-dossier classification/ du dossier assemblé.
            model = tabfm_load(
                model_type="classification",
                checkpoint_path=str(local_dir),
                device="cpu",
            )
            self._tabfm = TabFMClassifier(model=model)
        return self._tabfm

    def extract_mirofish_tabular_matrix(
        self, mirofish_graph_nodes: list[dict[str, Any]]
    ) -> list[dict[str, float]]:
        """
        Convertit les nœuds MiroFish (Journal, Decision, Option, Anomaly)
        en matrice numérique structurée pour l'In-Context Learning tabulaire.
        Les nœuds doivent être RÉELS (chargeur load_mirofish_nodes) — cette
        fonction ne fait que l'encodage, elle ne simule rien.
        """
        rows = []
        for node in mirofish_graph_nodes:
            rows.append(
                {
                    "agent_influence": float(node.get("influence_weight", 0.5)),
                    "sentiment_polarity": float(node.get("sentiment", 0.0)),
                    "epistemic_certainty": float(node.get("certainty", 0.5)),
                    "anomaly_flag": 1.0 if node.get("type") == "Anomaly" else 0.0,
                    "stancereversal_count": float(node.get("stance_flips", 0)),
                }
            )
        return rows

    @staticmethod
    def _rows_to_array(rows: list[dict[str, float]]):
        import numpy as np

        return np.array([[r[f] for f in FEATURES] for r in rows], dtype=float)

    def run_icl_inference(
        self,
        context_rows: list[dict[str, float]],
        context_labels: list[int],
        query_row: dict[str, float],
    ) -> WargameScenarioResult:
        """
        Prédiction In-Context Learning réelle (sans fine-tuning) :
        1. Mitra-v2 (12-layer 2D Transformer, 75.7M) — poids montés, ICL.
        2. TabFM 1.1.0 (24 ICL blocks, optionnel en mode internal_dual_jury).
        Le fallback arithmétique est mort : sans poids montés, une erreur
        est levée (pas de nombre inventé).
        """
        if not context_rows or not context_labels:
            raise NoDataError("pas de données : contexte ICL vide (aucun nœud réel)")
        if len(set(context_labels)) < 2:
            raise ValueError(
                "contexte ICL sans les deux classes (0 et 1 requis pour Mitra)"
            )
        swarm_score = sum(
            r["sentiment_polarity"] * r["agent_influence"] for r in context_rows
        ) / max(len(context_rows), 1)

        X_train = self._rows_to_array(context_rows)
        X_query = self._rows_to_array([query_row])
        # Mitra exige des ndarray (une liste Python échoue dans son
        # préprocesseur : `y < n_classes` n'est pas défini pour une liste).
        import numpy as np

        y_train = np.array(context_labels, dtype=int)

        # Déterminisme (R1, sonde probe_mitra_seed) : l'ICL Mitra varie de
        # ±0.05 d'une passe à l'autre si les graines globales ne sont pas
        # fixées — AutoGluon 1.6.3 puise dans le RNG global numpy/torch
        # (le contexte `mitra_deterministic_context` est un no-op, et la
        # graine par passe est fixe mais le tirage global ne l'est pas).
        # Un moteur de wargame doit être reproductible : mêmes entrées,
        # mêmes poids -> même sortie. On fixe les graines avant chaque
        # inférence (constante, documentée ; ne touche pas aux poids).
        import numpy as np
        import torch

        np.random.seed(42)
        torch.manual_seed(42)

        # Passe 1 : Mitra-v2 réel (AutoGluon, poids montés, ICL zéro-shot).
        mitra = self._load_mitra()
        mitra.fit(X_train, y_train, X_val=X_train, y_val=y_train)
        mitra_prob = float(mitra.predict_proba(X_query)[0][1])

        tabfm_prob = None
        if self.mode == "internal_dual_jury":
            # Passe 2 : TabFM 1.1.0 réel (poids montés, classification).
            tabfm = self._load_tabfm()
            tabfm.fit(X_train, y_train)
            tabfm_prob = float(tabfm.predict_proba(X_query)[0][1])
            divergence = abs(mitra_prob - tabfm_prob)
            confidence = max(0.0, 1.0 - (divergence * 2.0))
            final_prob = (mitra_prob + tabfm_prob) / 2.0
        else:
            assert_commercial_safe(["mitra-classifier-2"])
            confidence = float(query_row.get("epistemic_certainty", 0.75))
            final_prob = mitra_prob

        action = (
            "EXECUTE_STRATEGY"
            if (final_prob >= 0.65 and confidence >= 0.70)
            else "HOLD_COUNTERFACTUAL_REHEARSAL"
        )

        import hashlib

        scenario_id = "WG-" + hashlib.sha256(
            json.dumps(query_row, sort_keys=True).encode()
        ).hexdigest()[:8]
        return WargameScenarioResult(
            scenario_id=scenario_id,
            swarm_consensus_score=round(swarm_score, 4),
            mitra_prob=round(mitra_prob, 4),
            tabfm_prob=round(tabfm_prob, 4) if tabfm_prob is not None else None,
            ensemble_confidence=round(confidence, 4),
            recommended_action=action,
            commercial_safe=(self.mode == "commercial_apache2"),
        )

    def run_from_trace(
        self,
        factory_sqlite: str | Path | None = None,
        export_path: str | Path | None = None,
    ) -> WargameScenarioResult:
        """Chemin réel : nœuds depuis la trace -> matrice -> inférence réelle.

        Le contexte ICL est étiqueté depuis la trace : 1 si le step a réussi
        (completed/success), 0 s'il a échoué (failed) ; les steps sans verdict
        terminal sont exclus du contexte étiqueté. La requête est le dernier
        nœud de la trace. Sans source : NoDataError (« pas de données »).
        """
        nodes = load_mirofish_nodes(factory_sqlite=factory_sqlite, export_path=export_path)
        rows = self.extract_mirofish_tabular_matrix(nodes)
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
        return self.run_icl_inference(labeled_rows, labels, rows[-1])


if __name__ == "__main__":
    import sys

    db = os.environ.get("ASPACE_FACTORY_SQLITE") or str(
        Path(__file__).resolve().parents[3] / "02_Factory" / "factory.sqlite"
    )
    mode = sys.argv[1] if len(sys.argv) > 1 else "commercial_apache2"
    engine = PredictiveWargameEngine(mode=mode)  # type: ignore[arg-type]
    try:
        res = engine.run_from_trace(factory_sqlite=db)
    except NoDataError as exc:
        print(f"pas de données : {exc}")
        raise SystemExit(2)
    print(json.dumps(res.__dict__, indent=2))
