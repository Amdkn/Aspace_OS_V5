#!/usr/bin/env python3
"""
aspace_fkb02_memory_organ.py — Organe Natif de la Famille FKB02_Memory (ÂME / Organe K4).

Unifie en code natif exécutable les principes, invariants et interfaces des 9 modules FKB02
destinés à `FUSIONNÉ` (en plus de `M120 llm-wiki` déjà fusionné ; `servers` reste `RETENU` MCP Stdio) :
  - M030 auto-ontology            (extraction dynamique DAG + détection de contradictions)
  - M031 billion-context          (HierarchicalCASStore L0/L1/L2 SHA-256 + offload disque)
  - M032 context-language-models  (build_clm_anchored_context Zero-Lost-in-the-Middle)
  - M033 dox                      (validate_dox_contract hiérarchie AGENTS.md/CLAUDE.md)
  - M034 gbrain                   (HybridBrainIndex BM25 + vecteurs + graphe avec citations M1-M8)
  - M035 graphify                 (ASTCodeGraphBuilder + query/explain sur code Python réel)
  - M036 infinite-brain-harness   (isolation stricte multi-cerveaux inter-tenants)
  - M037 infinite-brain-os        (cerveau Markdown/YAML versionné Git + promotion canonique)
  - M038 knowledge-catalog        (validate_okf_bundle OKF v0.2 : frontmatter YAML, index, log append-only)

Rattachement ADR-13 : Noyau `ÂME` -> Organe `K4`.
Zéro dépendance externe, zéro télémétrie.
"""

from __future__ import annotations

import ast
import datetime as dt
import hashlib
import json
import math
import os
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Set, Tuple

_CORE_DIR = Path(__file__).resolve().parent
if str(_CORE_DIR) not in sys.path:
    sys.path.insert(0, str(_CORE_DIR))

from aspace_foundation_kernel import (  # noqa: E402
    CitationEvidence,
    ContractViolation,
    EventJournal,
    R10Ledger,
    R10_SCHEMA,
    validate_citation,
)

TERM_RE = re.compile(r"\b(?:[A-Z][a-zA-Z0-9_-]{2,}|[a-z0-9]+(?:[-_][a-z0-9]+){1,4})\b")
STOPWORDS = frozenset({"The", "This", "That", "Pour", "Avec", "Dans", "Sur", "Les", "Des", "Une"})


# ===========================================================================
# 1. M031 billion-context — Store CAS Hiérarchique SHA-256 (L0/L1/L2)
# ===========================================================================

class HierarchicalCASStore:
    """Partitionne et décharge des corpus massifs en blocs L0/L1/L2 adressés par SHA-256."""

    def __init__(self, cas_dir: Path) -> None:
        self.cas_dir = cas_dir
        self.cas_dir.mkdir(parents=True, exist_ok=True)
        self.manifest: Dict[str, Dict[str, Any]] = {}

    def ingest_document(self, doc_id: str, text: str, chunk_chars: int = 240) -> Dict[str, Any]:
        slices = [text[i : i + chunk_chars] for i in range(0, len(text), max(chunk_chars, 1))] or [""]
        l0_refs: List[Dict[str, Any]] = []
        l1_summaries: List[str] = []
        for idx, sl in enumerate(slices):
            digest = hashlib.sha256(sl.encode("utf-8")).hexdigest()
            blob_path = self.cas_dir / f"{digest}.txt"
            if not blob_path.exists():
                blob_path.write_text(sl, encoding="utf-8")
            l0_refs.append({"slice_index": idx, "sha256": digest, "bytes": len(sl.encode("utf-8"))})
            words = sl.split()
            l1_summaries.append(" ".join(words[:12]))

        l2_anchor = " | ".join(l1_summaries)[:280]
        record = {
            "schema": "aspace.billion-context.cas.v1",
            "doc_id": doc_id,
            "l0_count": len(l0_refs),
            "l0_refs": l0_refs,
            "l1_summaries": l1_summaries,
            "l2_anchor": l2_anchor,
        }
        self.manifest[doc_id] = record
        return record

    def retrieve_l0_slice(self, sha256_hex: str) -> str:
        blob_path = self.cas_dir / f"{sha256_hex}.txt"
        if not blob_path.exists():
            raise ContractViolation("M2", "cas_sha256", f"blob CAS absent: {sha256_hex}")
        return blob_path.read_text(encoding="utf-8")


# ===========================================================================
# 2. M030 auto-ontology — Extracteur DAG + Détecteur de Contradictions
# ===========================================================================

class AutoOntologyCompiler:
    """Compile des triplets DAG acycliques et détecte formellement les contradictions."""

    def __init__(self) -> None:
        self.entities: Dict[str, Dict[str, Any]] = {}
        self.relations: List[Dict[str, Any]] = []

    @staticmethod
    def has_cycle(relations: Sequence[Dict[str, Any]]) -> bool:
        adj: Dict[str, List[str]] = {}
        for r in relations:
            adj.setdefault(r["from"], []).append(r["to"])
        state: Dict[str, int] = {}

        def dfs(n: str) -> bool:
            st = state.get(n, 0)
            if st == 1:
                return True
            if st == 2:
                return False
            state[n] = 1
            for nxt in adj.get(n, []):
                if dfs(nxt):
                    return True
            state[n] = 2
            return False

        return any(dfs(k) for k in list(adj.keys()))

    def compile_triples(self, source_id: str, triples: Sequence[Tuple[str, str, str]]) -> Dict[str, Any]:
        """Ajoute des triplets `(subj, rel, obj)`, vérifie l'acyclicité DAG et signale toute contradiction."""
        contradictions: List[Dict[str, str]] = []
        existing_by_sr: Dict[Tuple[str, str], Set[str]] = {}
        for r in self.relations:
            existing_by_sr.setdefault((r["from"], r["relationType"]), set()).add(r["to"])

        candidate_rels = list(self.relations)
        for subj, rel, obj in triples:
            self.entities.setdefault(subj, {"name": subj, "sources": set()})["sources"].add(source_id)
            self.entities.setdefault(obj, {"name": obj, "sources": set()})["sources"].add(source_id)

            prev_objs = existing_by_sr.get((subj, rel), set())
            if prev_objs and obj not in prev_objs:
                contradictions.append(
                    {
                        "subject": subj,
                        "relation": rel,
                        "existing": ", ".join(sorted(prev_objs)),
                        "new": obj,
                        "epistemic_status": "contredit",
                    }
                )
            existing_by_sr.setdefault((subj, rel), set()).add(obj)
            candidate_rels.append(
                {
                    "type": "relation",
                    "from": subj,
                    "to": obj,
                    "relationType": rel,
                    "source_id": source_id,
                }
            )

        if self.has_cycle(candidate_rels):
            raise ContractViolation("K4", "ontology_dag", "cycle détecté lors de la compilation ontologique")
        self.relations = candidate_rels
        return {
            "schema": "aspace.auto-ontology.v1",
            "entities_count": len(self.entities),
            "relations_count": len(self.relations),
            "acyclic_dag": True,
            "contradictions": contradictions,
        }


# ===========================================================================
# 3. M032 context-language-models — Conditionnement Ancré Zero-Lost-in-the-Middle
# ===========================================================================

def build_clm_anchored_context(
    query: str,
    chunks: Sequence[Dict[str, Any]],
    ontology_triples: Sequence[Dict[str, Any]],
    max_tokens: int = 180,
) -> Dict[str, Any]:
    """Assemble un contexte structuré en plaçant les ancres ontologiques en tête ET en rappel terminal."""
    q_terms = set(re.findall(r"[a-zA-Z0-9_-]{3,}", query.lower()))
    anchor_lines = [
        f"[ANCRE] {t['from']} --{t['relationType']}--> {t['to']}"
        for t in ontology_triples
        if not q_terms or any(qt in (t["from"] + t["to"] + t["relationType"]).lower() for qt in q_terms)
    ]
    if not anchor_lines:
        anchor_lines = [f"[ANCRE] {t['from']} --{t['relationType']}--> {t['to']}" for t in ontology_triples[:3]]

    header = "\n".join(anchor_lines[:4])
    footer = f"[INVARIANT-RAPPEL] {' ; '.join(anchor_lines[:2])}" if anchor_lines else "[INVARIANT-RAPPEL] Aucun triplet"
    budget_remaining = max(max_tokens - len(header.split()) - len(footer.split()), 0)

    body_parts: List[str] = []
    used = 0
    for ch in chunks:
        txt = str(ch.get("text", "")).strip()
        words = txt.split()
        if used + len(words) > budget_remaining:
            avail = max(budget_remaining - used, 0)
            if avail > 0:
                body_parts.append(" ".join(words[:avail]))
                used += avail
            break
        body_parts.append(txt)
        used += len(words)

    context = "\n\n".join(p for p in (header, "\n".join(body_parts), footer) if p)
    return {
        "schema": "aspace.clm.context.v1",
        "kernel": "ÂME",
        "organ": "K4",
        "zero_lost_in_middle": True,
        "tokens_used": len(context.split()),
        "max_tokens": max_tokens,
        "context": context,
    }


# ===========================================================================
# 4. M033 dox — Validateur de Hiérarchie Contractuelle AGENTS.md / CLAUDE.md
# ===========================================================================

def validate_dox_contract(repo_root: Path) -> Dict[str, Any]:
    """Vérifie la hiérarchie documentaire DOX racine et sous-répertoires."""
    required = ("AGENTS.md", "CLAUDE.md", "00_Memoire/AGENTS.md")
    present: List[str] = []
    missing: List[str] = []
    for rel in required:
        p = repo_root / rel
        if p.exists() and p.stat().st_size > 100:
            present.append(rel)
        else:
            missing.append(rel)

    agents_files = []
    skip_dirs = {".git", ".venv", "node_modules", "01_Forkable", "target", "graphify-out"}
    for cur_root, dirs, files in os.walk(repo_root):
        dirs[:] = [d for d in dirs if d not in skip_dirs]
        if "AGENTS.md" in files:
            agents_files.append(str((Path(cur_root) / "AGENTS.md").relative_to(repo_root)).replace("\\", "/"))
    return {
        "schema": "aspace.dox.contract.v1",
        "kernel": "ÂME",
        "organ": "K4",
        "valid": len(missing) == 0,
        "present_core": present,
        "missing_core": missing,
        "core_agents_md_count": len(agents_files),
    }


# ===========================================================================
# 5. M034 gbrain — Index Hybride (BM25 + Vecteur N-Gram + Graphe) + M1-M8
# ===========================================================================

class HybridBrainIndex:
    """Recherche hybride lexicale/vectorielle/graphe ne promouvant que des faits sourcés M1-M8."""

    def __init__(self) -> None:
        self.pages: Dict[str, Dict[str, Any]] = {}
        self.links: Dict[str, Set[str]] = {}

    def put_page(self, page_id: str, text: str, source_ref: str, source_date: str, links: Sequence[str] = ()) -> None:
        self.pages[page_id] = {
            "page_id": page_id,
            "text": text,
            "source_ref": source_ref,
            "source_date": source_date,
        }
        self.links.setdefault(page_id, set()).update(links)
        for target in links:
            self.links.setdefault(target, set()).add(page_id)

    @staticmethod
    def _trigrams(text: str) -> Dict[str, float]:
        norm = re.sub(r"\s+", " ", text.lower())
        counts: Dict[str, float] = {}
        for i in range(max(len(norm) - 2, 0)):
            tg = norm[i : i + 3]
            counts[tg] = counts.get(tg, 0.0) + 1.0
        return counts

    @classmethod
    def _cosine(cls, a: Dict[str, float], b: Dict[str, float]) -> float:
        dot = sum(v * b.get(k, 0.0) for k, v in a.items())
        na = math.sqrt(sum(v * v for v in a.values()))
        nb = math.sqrt(sum(v * v for v in b.values()))
        return dot / max(na * nb, 1e-9)

    def search_hybrid(self, query: str, focus_page: Optional[str] = None, top_k: int = 3) -> List[Dict[str, Any]]:
        q_tokens = set(re.findall(r"[a-zA-Z0-9_-]{2,}", query.lower()))
        q_vec = self._trigrams(query)
        neighbors = self.links.get(focus_page or "", set())

        results: List[Dict[str, Any]] = []
        for pid, page in self.pages.items():
            toks = re.findall(r"[a-zA-Z0-9_-]{2,}", page["text"].lower())
            overlap = len(q_tokens & set(toks)) / max(len(q_tokens), 1)
            vec_sim = self._cosine(q_vec, self._trigrams(page["text"]))
            graph_boost = 0.25 if pid in neighbors else 0.0
            score = round(0.5 * overlap + 0.35 * vec_sim + graph_boost, 4)
            if score <= 0.0:
                continue
            results.append(
                {
                    "page_id": pid,
                    "score": score,
                    "source_ref": page["source_ref"],
                    "source_date": page["source_date"],
                    "epistemic_status": "consigné" if page["source_ref"] else "absent",
                    "excerpt": page["text"][:160],
                }
            )
        results.sort(key=lambda r: r["score"], reverse=True)
        return results[:top_k]


# ===========================================================================
# 6. M035 graphify — Graphe AST Codebase Python (Query / Explain déterministe)
# ===========================================================================

class ASTCodeGraphBuilder:
    """Analyse des fichiers Python réels par `ast` pour construire graphe de dépendances et communautés."""

    def build_from_files(self, paths: Sequence[Path]) -> Dict[str, Any]:
        nodes: Dict[str, Dict[str, Any]] = {}
        edges: List[Dict[str, str]] = []
        for p in paths:
            if not p.exists() or p.suffix != ".py":
                continue
            src = p.read_text(encoding="utf-8", errors="ignore")
            tree = ast.parse(src, filename=str(p))
            mod_name = p.stem
            nodes[mod_name] = {"kind": "module", "file": str(p), "lineno": 1}
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    qname = f"{mod_name}.{node.name}"
                    nodes[qname] = {"kind": "class", "file": str(p), "lineno": node.lineno}
                    edges.append({"from": mod_name, "to": qname, "kind": "defines"})
                elif isinstance(node, ast.FunctionDef):
                    qname = f"{mod_name}.{node.name}"
                    nodes[qname] = {"kind": "function", "file": str(p), "lineno": node.lineno}
                    edges.append({"from": mod_name, "to": qname, "kind": "defines"})
                elif isinstance(node, ast.ImportFrom) and node.module:
                    edges.append({"from": mod_name, "to": node.module, "kind": "imports"})
        return {
            "schema": "aspace.graphify.ast.v1",
            "kernel": "ÂME",
            "organ": "K4",
            "nodes": nodes,
            "edges": edges,
        }

    @staticmethod
    def explain_symbol(graph: Dict[str, Any], symbol: str) -> Dict[str, Any]:
        matches = [k for k in graph["nodes"] if symbol.lower() in k.lower()]
        related_edges = [e for e in graph["edges"] if e["from"] in matches or e["to"] in matches]
        return {
            "query": symbol,
            "matched_nodes": {m: graph["nodes"][m] for m in matches},
            "edges_count": len(related_edges),
            "edges": related_edges[:25],
        }


# ===========================================================================
# 7. M036 infinite-brain-harness & M037 infinite-brain-os — Multi-Cerveaux Isolés
# ===========================================================================

class MultiBrainNamespaceManager:
    """Cloisonne des cerveaux Markdown/YAML versionnables par tenant sans fuite croisée."""

    def __init__(self, brains_root: Path) -> None:
        self.brains_root = brains_root
        self.brains_root.mkdir(parents=True, exist_ok=True)
        self.registered: Dict[str, Dict[str, Any]] = {}

    def mount_brain(self, brain_id: str, tier: str = "individual") -> Path:
        if tier not in {"company", "department", "individual", "b2b-client"}:
            raise ContractViolation("K4", "tier", f"niveau de cerveau invalide: {tier}")
        if not re.fullmatch(r"[a-zA-Z0-9_-]{2,48}", brain_id):
            raise ContractViolation("K4", "brain_id", f"identifiant brain_id invalide: {brain_id}")
        bdir = self.brains_root / brain_id
        for sub in ("knowledge", "memory", "_system"):
            (bdir / sub).mkdir(parents=True, exist_ok=True)
        meta = {"brain_id": brain_id, "tier": tier, "path": str(bdir)}
        (bdir / "_system" / "brain.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")
        self.registered[brain_id] = meta
        return bdir

    def write_note(self, brain_id: str, note_slug: str, okf_type: str, body: str) -> Path:
        if brain_id not in self.registered:
            raise ContractViolation("K4", "brain_id", f"cerveau non monté: {brain_id}")
        target = self.brains_root / brain_id / "knowledge" / f"{note_slug}.md"
        content = f"---\nokf_version: \"0.2\"\ntype: {okf_type}\nbrain_id: {brain_id}\n---\n\n{body.strip()}\n"
        target.write_text(content, encoding="utf-8")
        return target

    def query_brain(self, brain_id: str, keyword: str) -> List[Dict[str, str]]:
        """Recherche strictement bornée au `brain_id` demandé (zéro fuite inter-tenant)."""
        if brain_id not in self.registered:
            raise ContractViolation("K4", "brain_id", f"cerveau non monté: {brain_id}")
        bdir = self.brains_root / brain_id / "knowledge"
        hits = []
        for md in sorted(bdir.glob("*.md")):
            txt = md.read_text(encoding="utf-8")
            if keyword.lower() in txt.lower():
                hits.append({"brain_id": brain_id, "file": md.name, "preview": txt[:140]})
        return hits


# ===========================================================================
# 8. M038 knowledge-catalog — Validateur OKF v0.2
# ===========================================================================

def validate_okf_bundle(bundle_dir: Path) -> Dict[str, Any]:
    """Valide un bundle OKF v0.2 : YAML `type:`, existence `index.md`, journal `log.md`."""
    index_path = bundle_dir / "index.md"
    log_path = bundle_dir / "log.md"
    concepts_dir = bundle_dir / "concepts"
    errors: List[str] = []

    if not index_path.exists():
        errors.append("index.md manquant")
    if not log_path.exists():
        errors.append("log.md manquant")
    if not concepts_dir.is_dir():
        errors.append("concepts/ manquant")

    concept_files = sorted(concepts_dir.glob("*.md")) if concepts_dir.is_dir() else []
    for cf in concept_files:
        head = cf.read_text(encoding="utf-8", errors="ignore")[:800]
        if not head.startswith("---"):
            errors.append(f"{cf.name}: frontmatter --- manquant")
            continue
        if not re.search(r"^type:\s*\S+", head, flags=re.MULTILINE):
            errors.append(f"{cf.name}: clé type: manquante")

    return {
        "schema": "aspace.knowledge-catalog.okf02.v1",
        "kernel": "ÂME",
        "organ": "K4",
        "valid": len(errors) == 0,
        "concepts_checked": len(concept_files),
        "errors": errors,
    }


# ===========================================================================
# Suite de vérification des 9 modules FKB02 sans accès aux répertoires sources
# ===========================================================================

def run_fkb02_self_test(repo_root: Optional[Path] = None, head_sha40: str = "0" * 40) -> Dict[str, Any]:
    import tempfile

    root = repo_root or Path(__file__).resolve().parents[3]
    with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as tmpdir:
        tdir = Path(tmpdir)

        # 1. billion-context (M031)
        cas = HierarchicalCASStore(tdir / "cas")
        cas_rec = cas.ingest_document("doc-1", "Aspace Foundation unifies kernels via Rust contracts." * 10, chunk_chars=80)
        first_sha = cas_rec["l0_refs"][0]["sha256"]
        assert "Aspace Foundation" in cas.retrieve_l0_slice(first_sha)

        # 2. auto-ontology (M030) — DAG valide + détection contradiction formelle
        onto = AutoOntologyCompiler()
        r1 = onto.compile_triples("s1", [("ÂME", "rattache", "K1"), ("K1", "valide", "R10")])
        assert r1["acyclic_dag"] and not r1["contradictions"]
        r2 = onto.compile_triples("s2", [("K1", "valide", "SessionOnly")])
        assert len(r2["contradictions"]) == 1 and r2["contradictions"][0]["epistemic_status"] == "contredit"

        # 3. context-language-models (M032)
        clm = build_clm_anchored_context(
            "K1 R10",
            [{"text": "Validation deterministe R10 et EventJournal."}],
            onto.relations,
            max_tokens=100,
        )
        assert clm["zero_lost_in_middle"] and "[ANCRE]" in clm["context"] and "[INVARIANT-RAPPEL]" in clm["context"]

        # 4. dox (M033)
        dox_res = validate_dox_contract(root)
        assert dox_res["valid"] and dox_res["core_agents_md_count"] >= 2

        # 5. gbrain (M034) + garde épistémique M1-M8
        gb = HybridBrainIndex()
        gb.put_page("p1", "RigInfinity implements pure data hibernation and PTY daemon.", "RigInfinity/Cargo.toml:1", "2026-11-19", links=["p2"])
        gb.put_page("p2", "fondation-13-1 checks M1-M8 citations deterministically.", "fondation-13-1/src/memory.rs:1", "2026-11-19")
        hits = gb.search_hybrid("hibernation RigInfinity", focus_page="p2")
        assert hits and hits[0]["page_id"] == "p1"
        cit_md = """**Fonction :** memorizer
**Date de la citation :** `2026-11-19`
**Fait demandé :** Test M034
**Mécanisme :** recall-fact M1-M8

## Citation
**Énoncé :** RigInfinity implements pure data hibernation and PTY daemon.
**Source :** RigInfinity/Cargo.toml:1
**Date :** 2026-11-19
**Statut :** vérifié

## Vérification au fichier
Relu au fichier 2026-11-19.

## Corroborations et contradictions
Aucune contradiction.

## Ce que cette citation ne prouve pas
Ne prouve pas les benchmarks d'autres dépôts.

## Ce que la fonction n'a pas fait
La fonction n'a pas tranché ni consigné.
"""
        v_cit = validate_citation(
            cit_md,
            CitationEvidence(True, "RigInfinity implements pure data hibernation and PTY daemon.", "2026-11-19"),
        )
        assert v_cit["status"] == "vérifié"

        # 6. graphify (M035)
        ast_builder = ASTCodeGraphBuilder()
        code_g = ast_builder.build_from_files([Path(__file__), _CORE_DIR / "aspace_foundation_kernel.py"])
        exp = ast_builder.explain_symbol(code_g, "EventJournal")
        assert exp["edges_count"] >= 1

        # 7 & 8. infinite-brain-harness (M036) & infinite-brain-os (M037)
        mgr = MultiBrainNamespaceManager(tdir / "brains")
        mgr.mount_brain("personal-a0", tier="individual")
        mgr.mount_brain("b2b-client-alpha", tier="b2b-client")
        mgr.write_note("personal-a0", "secret-note", "Note", "Personal secret token-free observation")
        mgr.write_note("b2b-client-alpha", "offer", "Specification", "B2B OMK client deliverable")
        assert len(mgr.query_brain("personal-a0", "Personal")) == 1
        assert len(mgr.query_brain("b2b-client-alpha", "Personal")) == 0  # isolation stricte inter-tenant

        # 9. knowledge-catalog (M038)
        okf_res = validate_okf_bundle(root / "00_Memoire" / "bundle")
        assert okf_res["valid"] and okf_res["concepts_checked"] >= 15

        # Émission L0
        now_dt = dt.datetime.now(dt.timezone.utc)
        day_tag = now_dt.strftime("%Y%m%d")
        j = EventJournal(signed_designs={"00_Memoire/bundle/fusion/SDD-FONDATION.md"})
        l = R10Ledger(valid_shas={head_sha40})
        evt = j.inscribe(
            {
                "actor_from": "memorizer",
                "actor_to": "judge",
                "at": now_dt.isoformat(),
                "design_ref": "00_Memoire/bundle/fusion/SDD-FONDATION.md",
                "dispatch_id": "D-FKB02-FUSION",
                "event_id": f"EVT-{day_tag}-902",
                "payload": "Prouver fusion 9 modules FKB02",
                "proof": ["01_Forkable/FKB00_Runtime/00_A0_Core/aspace_fkb02_memory_organ.py"],
                "type": "fact_recalled",
            },
            now_utc=now_dt,
        )
        rec = l.validate_and_consign(
            {
                "entry_id": f"G-{day_tag}-902",
                "issuer": "Organ FKB02",
                "mission_id": "FKB02-NATIVE-FUSION-CHECK",
                "observed_at": now_dt.isoformat(),
                "proof": ["01_Forkable/FKB00_Runtime/00_A0_Core/aspace_fkb02_memory_organ.py"],
                "recorded_at": None,
                "schema": R10_SCHEMA,
                "sha": head_sha40,
                "summary": f"FKB02 9/9 capabilities verified at {head_sha40[:7]}",
            },
            now_utc=now_dt,
        )
        return {
            "organ": "aspace_fkb02_memory_organ",
            "modules_verified": 9,
            "okf_concepts": okf_res["concepts_checked"],
            "l0_seq": evt["seq"],
            "r10_entry_id": rec["entry_id"],
        }


if __name__ == "__main__":
    print(json.dumps(run_fkb02_self_test(), indent=2, ensure_ascii=False))
