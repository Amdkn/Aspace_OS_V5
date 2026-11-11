#!/usr/bin/env python3
"""
A'Space OS V5 — 02_PredictiveWargame_MachineLearning/aspace_precheck_weights.py
D-N052 R1 — Pré-check réel : résolution des poids montés + chargeur de nœuds MiroFish réels.

Règles dures (design Clara, D2/D3/D9) :
- Aucun chargement de poids depuis le Hub à l'exécution. Les poids sont montés
  UNE FOIS (mount-weights.sh des miroirs, vérifiés taille + sha256 LFS) puis
  lus en local. Si le dossier d'un modèle est absent, l'inférence lève une
  erreur — elle ne télécharge rien, ne simule rien.
- TabFM / TimesFM / PathFM (Non-Commercial) ne sont jamais chargés par le
  profil commercial — voir les gardes dans les moteurs (commercial_apache2 /
  b2b_commercial) et le test de confinement.
- Les nœuds MiroFish sont RÉELS : lus depuis la trace de la factory
  (factory.sqlite, R0) ou depuis un export MiroFish. Si aucune source n'est
  disponible, le chargeur rapporte « pas de données » — il ne simule pas.
"""

from __future__ import annotations

import json
import os
import sqlite3
from pathlib import Path
from typing import Any

# Racine des poids montés. Réglable par l'environnement (la machine qui fait
# tourner le pré-check — le PC en production). Défaut = le montage R1 de
# cette VM (~/workspace/.tmp/d-n052-r1-weights).
DEFAULT_WEIGHTS_ROOT = Path.home() / "workspace" / ".tmp" / "d-n052-r1-weights"

# Modèles R1 : (fichiers de poids attendus, licence, sha256 LFS vérifié à l'API).
# CORRECTION 2026-11-10 ~22:00 EST : la vérification d'origine (git blob oid
# = sha1 du contenu) est FAUSSE pour les poids LFS — l'oid de l'arbre Hub est
# le sha1 du POINTEUR LFS (134 o), jamais celui du contenu. La vérification
# correcte est taille + sha256 == lfs.oid de l'arbre Hub (valeurs ci-dessous,
# révisions épinglées, vérifiées à l'API). Le sha256 git blob oid reste
# consigné dans les MIRROR-MANIFEST.json (c'est l'oid du pointeur, pas du
# contenu) — les mount-weights.sh des miroirs doivent être corrigés de même
# (correction à porter par le parent : les 4 miroirs sont faits, ne pas les
# retoucher ici).
MODELS: dict[str, dict[str, Any]] = {
    "mitra-classifier-2": {
        "weights": ["model.safetensors"],
        "weights_sha256": {
            "model.safetensors": "5ffab0e2cf52f61c5b7c7eb1e8542996736d1023a0212190cc09abc2119a1e09"
        },
        "license": "Apache-2.0",
        "hub_id": "autogluon/mitra-classifier-2",
    },
    "chronos-2": {
        "weights": ["model.safetensors"],
        "weights_sha256": {
            "model.safetensors": "ddcda3c7508bf2528087723e98a20707cc04b7f370ae275a9fd88078ddba4f42"
        },
        "license": "Apache-2.0",
        "hub_id": "autogluon/chronos-2",
    },
    "tabfm-1.1.0-pytorch": {
        "weights": ["classification/model.safetensors"],
        "optional_weights": ["regression/model.safetensors"],
        "weights_sha256": {
            "classification/model.safetensors": "c34b2acf1274b2e7e2ccaf60b191e625a35da5416f1548dcd5b732f2aad1e717",
            "regression/model.safetensors": "6b75cf04d5ace29209dde0106c7969233fda9808983a145b3a742aaee0903d0e",
        },
        "license": "Non-Commercial (tabfm-non-commercial-v1.0)",
        "hub_id": "google/tabfm-1.1.0-pytorch",
    },
    "timesfm-3.0-pytorch": {
        "weights": ["model.safetensors"],
        "weights_sha256": {
            "model.safetensors": "a7592b0a8432baee54483254e5647856911ce69e09d09a9bb65904b2d98f17da"
        },
        "license": "Non-Commercial (timesfm-non-commercial-license-v1.0)",
        "hub_id": "google/timesfm-3.0-pytorch",
    },
    "pathfm-chaotic-75m": {
        "weights": ["model.safetensors"],
        "weights_sha256": {
            "model.safetensors": "6958980c5d72823f7505615bfa4a7751eeb8a21c26c6c70bcb4a800613a8177e"
        },
        # CORRECTION : licence CC-BY-NC-4.0 (Non-Commercial, README Hub) —
        # pas Apache-2.0. PathFM est donc confiné au profil interne (§D3).
        "license": "Non-Commercial (CC-BY-NC-4.0)",
        "hub_id": "autogluon/pathfm-chaotic-75m",
    },
}

# Modèles interdits au profil commercial (licence Non-Commercial, §D3).
NON_COMMERCIAL = {"tabfm-1.1.0-pytorch", "timesfm-3.0-pytorch", "pathfm-chaotic-75m"}


class WeightsNotMountedError(FileNotFoundError):
    """Un poids attendu n'est pas monté — l'inférence refuse de continuer."""


class NoDataError(RuntimeError):
    """Aucune source de nœuds réels disponible — « pas de données », pas de simulation."""


def weights_root() -> Path:
    return Path(os.environ.get("ASPACE_PRECHECK_WEIGHTS", DEFAULT_WEIGHTS_ROOT))


def model_dir(model: str, root: Path | None = None) -> Path:
    """Dossier assemblé d'un modèle (config + poids, prêt pour from_pretrained).

    L'assemblage est fait au montage (voir evidence/D-N052/r1-inference/
    assemble-model-dirs.py), pas à l'exécution : ce module ne fait que
    VÉRIFIER la présence des fichiers attendus.
    """
    root = root or weights_root()
    d = root / model
    missing = [rel for rel in MODELS[model]["weights"] if not (d / rel).is_file()]
    if missing:
        raise WeightsNotMountedError(
            f"poids manquants pour {model} dans {d} : {missing} — "
            "monter les poids (mount-weights.sh) avant l'inférence"
        )
    return d


def assert_commercial_safe(models_used: list[str]) -> None:
    """Garde §D3 : le profil commercial n'utilise jamais TabFM/TimesFM."""
    banned = [m for m in models_used if m in NON_COMMERCIAL]
    if banned:
        raise ValueError(
            f"modèles non-commerciaux interdits au profil commercial : {banned}"
        )


# ---------------------------------------------------------------------------
# Chargeur de nœuds MiroFish réels (§D9)
#
# Source 1 (prioritaire) : factory.sqlite — la trace de la factory (R0).
# Chaque durable_step est un nœud du swarm : l'agent qui agit, son statut,
# ses tentatives, ses steers. L'encodage est documenté, déterministe, et ne
# lit QUE des champs réels de la trace :
#   type            : status failed -> Anomaly ; completed/success -> Decision ;
#                     sinon Journal.
#   influence_weight: writer=1 -> 1.0 (écrit l'état partagé) ; sinon 0.5.
#   sentiment       : completed/success -> +0.6 ; failed -> -0.6 ; sinon 0.0.
#   certainty       : max(0.1, 0.9 - 0.2 * (attempts - 1)) ; attempts>=1.
#   stance_flips    : nombre d'entrées de steers_json (0 si absent/illisible).
# Source 2 : un export MiroFish (JSONL, un nœud par ligne, format MiroFish).
# Aucune source -> NoDataError (« pas de données »), jamais de simulation.
# ---------------------------------------------------------------------------

_TERMINAL_OK = {"completed", "success", "succeeded", "done"}


def _step_to_node(row: dict[str, Any]) -> dict[str, Any]:
    status = str(row.get("status") or "").strip().lower()
    attempts = row.get("attempts")
    try:
        attempts = int(attempts) if attempts is not None else 1
    except (TypeError, ValueError):
        attempts = 1
    attempts = max(1, attempts)
    try:
        steers = json.loads(row.get("steers_json") or "[]")
        stance_flips = len(steers) if isinstance(steers, list) else 0
    except (TypeError, ValueError):
        stance_flips = 0
    if status == "failed":
        node_type, sentiment = "Anomaly", -0.6
    elif status in _TERMINAL_OK:
        node_type, sentiment = "Decision", 0.6
    else:
        node_type, sentiment = "Journal", 0.0
    return {
        "type": node_type,
        "influence_weight": 1.0 if row.get("writer") in (1, "1", True) else 0.5,
        "sentiment": sentiment,
        "certainty": round(max(0.1, 0.9 - 0.2 * (attempts - 1)), 4),
        "stance_flips": stance_flips,
        "provenance": {
            "wid": row.get("wid"),
            "step_key": row.get("step_key"),
            "agent": row.get("agent"),
            "task": row.get("task"),
            "status": status,
            "updated_at": row.get("updated_at"),
        },
    }


def load_mirofish_nodes_from_factory_sqlite(db_path: str | Path) -> list[dict[str, Any]]:
    """Lit les nœuds réels depuis factory.sqlite (lecture seule)."""
    db_path = Path(db_path)
    if not db_path.is_file():
        raise NoDataError(f"pas de données : factory.sqlite absent ({db_path})")
    con = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
    try:
        con.execute("PRAGMA query_only = ON")
        rows = con.execute(
            "SELECT wid, step_key, agent, task, writer, status, steers_json, attempts, updated_at "
            "FROM durable_steps ORDER BY wid, seq"
        ).fetchall()
    except sqlite3.Error as exc:
        raise NoDataError(f"pas de données : factory.sqlite illisible ({exc})") from exc
    finally:
        con.close()
    if not rows:
        raise NoDataError(f"pas de données : factory.sqlite sans durable_steps ({db_path})")
    cols = ["wid", "step_key", "agent", "task", "writer", "status", "steers_json", "attempts", "updated_at"]
    return [_step_to_node(dict(zip(cols, r))) for r in rows]


def load_mirofish_nodes_from_export(export_path: str | Path) -> list[dict[str, Any]]:
    """Lit les nœuds réels depuis un export MiroFish (JSONL, un nœud par ligne)."""
    export_path = Path(export_path)
    if not export_path.is_file():
        raise NoDataError(f"pas de données : export MiroFish absent ({export_path})")
    nodes: list[dict[str, Any]] = []
    for line in export_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        node = json.loads(line)
        for field in ("type", "influence_weight", "sentiment", "certainty", "stance_flips"):
            if field not in node:
                raise NoDataError(
                    f"pas de données : nœud MiroFish incomplet (champ {field} manquant)"
                )
        nodes.append(node)
    if not nodes:
        raise NoDataError(f"pas de données : export MiroFish vide ({export_path})")
    return nodes


def load_mirofish_nodes(
    factory_sqlite: str | Path | None = None,
    export_path: str | Path | None = None,
) -> list[dict[str, Any]]:
    """Nœuds MiroFish réels, par ordre de priorité : factory.sqlite, puis export.

    Sans source disponible : NoDataError — le moteur rapporte « pas de
    données » et ne simule pas (§D9).
    """
    errors: list[str] = []
    if factory_sqlite is not None:
        try:
            return load_mirofish_nodes_from_factory_sqlite(factory_sqlite)
        except NoDataError as exc:
            errors.append(str(exc))
    if export_path is not None:
        try:
            return load_mirofish_nodes_from_export(export_path)
        except NoDataError as exc:
            errors.append(str(exc))
    raise NoDataError("pas de données : aucune source de nœuds réels — " + " ; ".join(errors))
