#!/usr/bin/env python3
"""
neuro_symbolic_bridge.py — Pont Opérationnel Neuro-Symbolique Aspace OS V5 (Noyau K4).

Fusionne :
  1. Substrat massif & chunking CAS SHA-256 (billion-context)
  2. Compilateur ontologique dynamique & vérification DAG acyclique (auto-ontology)
  3. Conditionnement latent (context-language-models)
  4. Gateway MCP partagée (00_Memoire/shared_brain/memory.jsonl)
  5. Contrats L0 fondation-13-1 (`aspace_foundation_kernel.py` : EventJournal + M1–M8)
"""

from __future__ import annotations

import datetime as dt
import hashlib
import json
import os
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Set, Tuple

WORKSPACE_ROOT = Path(__file__).resolve().parents[3]
_KERNEL_DIR = WORKSPACE_ROOT / "01_Forkable" / "FKB00_Runtime" / "00_A0_Core"
if str(_KERNEL_DIR) not in sys.path:
    sys.path.insert(0, str(_KERNEL_DIR))
from aspace_foundation_kernel import CitationEvidence, record_shared_l0_event, validate_citation  # noqa: E402

MEMORY_FILE_PATH = os.environ.get(
    "MEMORY_FILE_PATH",
    str(WORKSPACE_ROOT / "00_Memoire" / "shared_brain" / "memory.jsonl"),
)

CONCEPT_TOKEN_RE = re.compile(r"\b(?:[A-Z][a-zA-Z0-9_-]{2,}|[a-z0-9]+(?:[-_][a-z0-9]+){1,4})\b")
STOP_TOKENS = {"The", "This", "That", "Pour", "Avec", "Dans", "Sur", "Les", "Des", "Une"}


class NeuroSymbolicBridge:
    def __init__(self, memory_path: str = MEMORY_FILE_PATH) -> None:
        self.memory_path = Path(memory_path)
        self.memory_path.parent.mkdir(parents=True, exist_ok=True)
        self.existing_entities: Set[str] = set()
        self.existing_relations: Set[Tuple[str, str, str]] = set()
        self._load_existing_knowledge()

    def _load_existing_knowledge(self) -> None:
        """Charge le graphe existant pour garantir le dédoublonnage strict."""
        if not self.memory_path.exists():
            return
        with open(self.memory_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    record = json.loads(line)
                    if record.get("type") == "entity":
                        self.existing_entities.add(record["name"])
                    elif record.get("type") == "relation":
                        self.existing_relations.add((record["from"], record["to"], record["relationType"]))
                except json.JSONDecodeError:
                    continue

    def ingest_chunk(self, content: str, source_id: str) -> Dict[str, Any]:
        """Strate 1 (billion-context) : Chunking, compression et CAS SHA-256."""
        sha = hashlib.sha256(content.encode("utf-8")).hexdigest()
        tokens_est = len(content.split())
        return {
            "source_id": source_id,
            "cas_hash": sha,
            "tokens_est": tokens_est,
            "content": content,
        }

    def compile_ontology(self, chunk: Dict[str, Any]) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
        """Strate 2 (auto-ontology) : Extraction dynamique d'entités et construction de DAG acyclique."""
        text = str(chunk.get("content", ""))
        source_id = str(chunk.get("source_id", "unknown_source"))
        cas_short = str(chunk.get("cas_hash", ""))[:16]

        raw_terms = []
        seen: Set[str] = set()
        for tok in CONCEPT_TOKEN_RE.findall(text):
            if tok in STOP_TOKENS or tok == source_id or tok in seen:
                continue
            seen.add(tok)
            raw_terms.append(tok)

        extracted_entities: List[Dict[str, Any]] = [
            {
                "type": "entity",
                "name": source_id,
                "entityType": "IngestedChunk",
                "observations": [
                    f"CAS_SHA256_PREFIX={cas_short}",
                    f"TOKENS_EST={chunk.get('tokens_est', 0)}",
                    f"EXTRACTED_TERMS={len(raw_terms)}",
                ],
            }
        ]
        for term in raw_terms:
            etype = "TechnicalArtifact" if ("-" in term or "_" in term) else "DomainConcept"
            extracted_entities.append(
                {
                    "type": "entity",
                    "name": term,
                    "entityType": etype,
                    "observations": [f"Extrait de {source_id} (CAS {cas_short})"],
                }
            )

        # Construction DAG acyclique ordonnée : source_id -> terme_0 -> terme_1 ... (ordre strict sans cycle)
        extracted_relations: List[Dict[str, Any]] = []
        for idx, term in enumerate(raw_terms):
            extracted_relations.append(
                {
                    "type": "relation",
                    "from": source_id,
                    "to": term,
                    "relationType": "mentions_concept",
                }
            )
            if idx > 0:
                extracted_relations.append(
                    {
                        "type": "relation",
                        "from": raw_terms[idx - 1],
                        "to": term,
                        "relationType": "precedes_in_chunk",
                    }
                )

        assert not self._has_cycle(extracted_relations), "Cycle détecté dans l'ontologie compilée"
        return extracted_entities, extracted_relations

    @staticmethod
    def _has_cycle(relations: List[Dict[str, Any]]) -> bool:
        adj: Dict[str, List[str]] = {}
        for r in relations:
            adj.setdefault(r["from"], []).append(r["to"])
        state: Dict[str, int] = {}

        def dfs(node: str) -> bool:
            st = state.get(node, 0)
            if st == 1:
                return True
            if st == 2:
                return False
            state[node] = 1
            for nxt in adj.get(node, []):
                if dfs(nxt):
                    return True
            state[node] = 2
            return False

        return any(dfs(n) for n in list(adj.keys()))

    def persist_sync(self, entities: List[Dict[str, Any]], relations: List[Dict[str, Any]]) -> Dict[str, int]:
        """Écrit les nouvelles entités et relations dans memory.jsonl sans doublon."""
        added_entities = 0
        added_relations = 0

        with open(self.memory_path, "a", encoding="utf-8") as f:
            for ent in entities:
                if ent["name"] not in self.existing_entities:
                    f.write(json.dumps(ent, ensure_ascii=False) + "\n")
                    self.existing_entities.add(ent["name"])
                    added_entities += 1

            for rel in relations:
                rel_key = (rel["from"], rel["to"], rel["relationType"])
                if rel_key not in self.existing_relations:
                    f.write(json.dumps(rel, ensure_ascii=False) + "\n")
                    self.existing_relations.add(rel_key)
                    added_relations += 1

        return {"added_entities": added_entities, "added_relations": added_relations}

    def generate_conditioning_context(self, focus_entity: str) -> Dict[str, Any]:
        """Strate 3 (context-language-models) : Extrait le sous-graphe exact + journal L0."""
        related = [
            {"target": r[1], "relation": r[2]}
            for r in self.existing_relations
            if r[0] == focus_entity
        ]
        l0_evt = record_shared_l0_event(
            actor_from="memorizer",
            actor_to="discoverer",
            dispatch_id=f"D-K4-{focus_entity[:24]}",
            payload=f"Conditionner contexte {focus_entity}",
            proof=["01_Forkable/FKB02_Memory/01_BillionContxtLanguage_AutoOnthology/neuro_symbolic_bridge.py"],
            event_type="fact_recalled",
        )
        return {
            "focus": focus_entity,
            "invariants_count": len(related),
            "ontology_dag": related,
            "conditioning_status": "LOCKED_DETERMINISTIC",
            "l0_dispatch_seq": l0_evt["seq"],
        }


def verify_fact_citation(citation_md: str, evidence: CitationEvidence) -> Dict[str, str]:
    """Passe toute citation K4 par les règles M1–M8 de fondation-13-1."""
    return validate_citation(citation_md, evidence)


def main() -> None:
    print("=== ASPACE OS V5 — NEURO-SYMBOLIC MEMORY BRIDGE (K4 -> L0) ===")
    bridge = NeuroSymbolicBridge()
    sample_corpus = (
        "Traces d'exécution Aspace OS V5 multi-agents. Ingestion continue billion-context, "
        "compilation ontologique NVIDIA auto-ontology et décodage guidé context-language-models."
    )
    chunk = bridge.ingest_chunk(sample_corpus, source_id="trace_fable5_bridge")
    entities, relations = bridge.compile_ontology(chunk)
    print(f"[STRATE 1-2] CAS={chunk['cas_hash'][:16]} | {len(entities)} entités | {len(relations)} relations DAG")
    conditioning = bridge.generate_conditioning_context("trace_fable5_bridge")
    print(f"[STRATE 3] L0 seq={conditioning['l0_dispatch_seq']} | status={conditioning['conditioning_status']}")


if __name__ == "__main__":
    main()
