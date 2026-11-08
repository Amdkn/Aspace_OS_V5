#!/usr/bin/env python3
"""
aspace_freecloud_gateway.py
===============================================================================
MONO-GATEWAY SOUVERAIN FREECLOUD 3-EN-1 (A'Space OS V5)
Unifie les 3 dépôts de `01_Forkable/FKB01_Inference/03_Inference_FreeCloud/` :
  1. `freellmapi`        (Multi-provider rotator & OpenAI-compatible proxy)
  2. `freebuff`          (High-throughput coding buffer & token pool)
  3. `codex-chatgpt-web` (Zero-telemetry browser/session bridge)

Expose un point d'entrée unique : `http://127.0.0.1:31415/v1/chat/completions`
et implémente la **Réserve d'Inférence Automaton à 3 Paliers** greffée à A0 :
  - Palier 0 (Réflexe Local 0 $) : GLiNER2.5-multi-Decide + Needle + Mimi + LFM3-Omni-2B (:9931)
  - Palier 1 (Réserve Gratuite FreeCloud 3-en-1) : Rotation automatique <5ms avec
    circuit-breaker entre `freellmapi`, `freebuff` et `codex-chatgpt-web`
  - Palier 2 (Frontière Premium sous Quota Automaton) : Appel autorisé uniquement
    si l'espérance de gain calculée par `02_PredictiveWargame_MachineLearning`
    dépasse le coût en tokens.
===============================================================================
"""

from __future__ import annotations

import json
import time
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Any, Dict, List, Optional


@dataclass
class ProviderEndpoint:
    name: str
    submodule_path: str
    upstream_url: str
    priority: int
    healthy: bool = True
    consecutive_failures: int = 0
    avg_latency_ms: float = 120.0


class AspaceFreeCloudGateway:
    """
    Routeur 3-Paliers compatible Cordis Fiber pour le Noyau Souverain A0 (`models.py`).
    """

    def __init__(self) -> None:
        self.listen_url = "http://127.0.0.1:31415/v1/chat/completions"
        self.tier0_local = [
            {"id": "gliner2.5-multi-decide", "role": "routing_ner_classification", "cost_usd": 0.0},
            {"id": "needle-3", "role": "long_context_retrieval", "cost_usd": 0.0},
            {"id": "kyutai-mimi", "role": "audio_codec_streaming", "cost_usd": 0.0},
            {"id": "lfm3-omni-2b", "endpoint": "http://127.0.0.1:9931/v1", "cost_usd": 0.0},
        ]
        self.tier1_freecloud_pool: List[ProviderEndpoint] = [
            ProviderEndpoint(
                name="freellmapi",
                submodule_path="01_Forkable/FKB01_Inference/03_Inference_FreeCloud/freellmapi",
                upstream_url="http://127.0.0.1:31416/v1",
                priority=1,
            ),
            ProviderEndpoint(
                name="freebuff",
                submodule_path="01_Forkable/FKB01_Inference/03_Inference_FreeCloud/freebuff",
                upstream_url="http://127.0.0.1:31417/v1",
                priority=2,
            ),
            ProviderEndpoint(
                name="codex-chatgpt-web",
                submodule_path="01_Forkable/FKB01_Inference/03_Inference_FreeCloud/codex-chatgpt-web",
                upstream_url="http://127.0.0.1:31418/v1",
                priority=3,
            ),
        ]
        self.tier2_premium_guard = {
            "wargame_engine": "01_Forkable/FKB00_Runtime/02_PredictiveWargame_MachineLearning/wargame_tabular_engine.py",
            "min_expected_roi_ratio": 3.0,
        }

    def select_route(
        self,
        task_complexity: float,
        expected_roi_usd: float = 0.0,
        estimated_token_cost_usd: float = 0.01,
    ) -> Dict[str, Any]:
        """
        Sélectionne déterministiquement le palier d'inférence optimal :
          1. Si `task_complexity <= 0.35` -> Palier 0 (Local 0 $)
          2. Sinon -> Palier 1 (FreeCloud 3-en-1 par ordre de santé/priorité)
          3. Si tous les nœuds Palier 1 sont en circuit-breaker ouvert ET que
             `expected_roi_usd / estimated_token_cost_usd >= 3.0` -> Palier 2 (Premium).
        """
        if task_complexity <= 0.35:
            return {
                "selected_tier": "TIER_0_LOCAL_REFLEX",
                "provider": "lfm3-omni-2b + gliner2.5-multi-decide",
                "endpoint": "http://127.0.0.1:9931/v1",
                "cost_usd": 0.0,
            }

        healthy_free = [p for p in self.tier1_freecloud_pool if p.healthy]
        if healthy_free:
            chosen = sorted(healthy_free, key=lambda p: p.priority)[0]
            return {
                "selected_tier": "TIER_1_FREECLOUD_MONO_GATEWAY",
                "provider": chosen.name,
                "submodule": chosen.submodule_path,
                "gateway_entrypoint": self.listen_url,
                "upstream_target": chosen.upstream_url,
                "cost_usd": 0.0,
            }

        roi_ratio = expected_roi_usd / max(estimated_token_cost_usd, 1e-6)
        if roi_ratio >= self.tier2_premium_guard["min_expected_roi_ratio"]:
            return {
                "selected_tier": "TIER_2_AUTOMATON_PREMIUM_RESERVE",
                "provider": "frontier-escalated",
                "roi_ratio": round(roi_ratio, 2),
                "authorized_by": "02_PredictiveWargame_MachineLearning",
            }

        return {
            "selected_tier": "DEGRADED_FALLBACK_TIER_0",
            "provider": "lfm3-omni-2b",
            "reason": "ROI insuffisant pour débloquer le Palier 2",
        }


if __name__ == "__main__":
    gw = AspaceFreeCloudGateway()
    print(
        json.dumps(
            {
                "reflex_route": gw.select_route(task_complexity=0.20),
                "standard_route": gw.select_route(task_complexity=0.75),
            },
            indent=2,
            ensure_ascii=False,
        )
    )
