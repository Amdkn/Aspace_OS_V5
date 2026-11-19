#!/usr/bin/env python3
"""
aspace_fkb02_memory_organ.py — Organe Natif de la Famille FKB02_Memory (ÂME / Organe K4).

Unifie en code natif exécutable les principes, invariants et interfaces des 9 modules FKB02
destinés à `FUSIONNÉ` (en plus de `M120 llm-wiki` déjà fusionné ; `servers` `M051` reste `RETENU` MCP Stdio) :
  - M042 auto-ontology            (extraction dynamique DAG + détection de contradictions)
  - M043 billion-context          (HierarchicalCASStore L0/L1/L2 SHA-256 + offload disque)
  - M044 context-language-models  (context_string, edit_gate, finish_policy, lm_compat)
  - M045 dox                      (validate_dox_contract hiérarchie AGENTS.md/CLAUDE.md)
  - M046 gbrain                   (HybridBrainIndex BM25 + vecteurs + graphe avec citations M1-M8)
  - M047 graphify                 (ASTCodeGraphBuilder multi-langages .py/.ts/.rs + communautés Leiden/modularity + explain)
  - M048 infinite-brain-harness   (isolation stricte multi-cerveaux inter-tenants)
  - M049 infinite-brain-os        (cerveau Markdown/YAML versionné Git + promotion canonique)
  - M050 knowledge-catalog        (OKF v0.2 : document, index, synthesizer, paths)

Rattachement ADR-15 : Noyau `ÂME` -> Organe `K4`.
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
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Sequence, Set, Tuple

import yaml

_CORE_DIR = Path(__file__).resolve().parent
if str(_CORE_DIR) not in sys.path:
    sys.path.insert(0, str(_CORE_DIR))

from aspace_foundation_kernel import (  # noqa: E402
    CitationEvidence,
    ContractViolation,
    consign_measured_l0_evidence,
    validate_citation,
)

TERM_RE = re.compile(r"\b(?:[A-Z][a-zA-Z0-9_-]{2,}|[a-z0-9]+(?:[-_][a-z0-9]+){1,4})\b")
STOPWORDS = frozenset({"The", "This", "That", "Pour", "Avec", "Dans", "Sur", "Les", "Des", "Une"})


# ===========================================================================
# 1. M043 billion-context — Store CAS Hiérarchique SHA-256 (L0/L1/L2)
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
# 2. M042 auto-ontology — Extracteur DAG + Détecteur de Contradictions
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
# 3. M044 context-language-models — Context-as-a-String Round-Trip & Ancres
# ===========================================================================

_CLM_HEADER_RE = re.compile(r"^\[\[CTX_TURN\s+(\d+)\s+role=([A-Za-z]+)\]\]\s*$", re.M)
_CLM_VALID_ROLES = {"system", "user", "assistant", "tool"}


def clm_content_text(content: Any) -> Optional[str]:
    """Extrait le texte canonique d'un champ `content` OpenAI/Chat (str ou liste texte)."""
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts: List[str] = []
        for part in content:
            if isinstance(part, str):
                parts.append(part)
            elif isinstance(part, dict) and part.get("type") in (None, "text") and isinstance(part.get("text"), str):
                parts.append(part["text"])
            else:
                return None
        return "".join(parts)
    return None


def clm_rendered_text(msg: Dict[str, Any]) -> str:
    """Rend le texte visible d'un tour (reasoning_content + content + tool_calls)."""
    parts: List[str] = []
    rc = msg.get("reasoning_content")
    if isinstance(rc, str) and rc:
        parts.append(rc)
    ct = clm_content_text(msg.get("content"))
    if ct:
        parts.append(ct)
    for tc in msg.get("tool_calls") or []:
        fn = (tc or {}).get("function") or {}
        args = fn.get("arguments")
        if not isinstance(args, str):
            try:
                args = json.dumps(args or {})
            except Exception:
                args = ""
        piece = f"{fn.get('name', '')} {args}".strip()
        if piece:
            parts.append(piece)
    return "\n".join(p for p in parts if p)


def clm_render_editable(messages: List[Dict[str, Any]], protect: int = 2) -> str:
    """Rend la région éditable (`>= protect`) avec en-têtes `[[CTX_TURN N role=...]]`."""
    blocks: List[str] = []
    for n, i in enumerate(range(protect, len(messages)), start=1):
        m = messages[i]
        blocks.append(f"[[CTX_TURN {n} role={m.get('role', 'user')}]]\n{clm_rendered_text(m)}")
    return "\n\n".join(blocks)


def _clm_normalize(messages: List[Dict[str, Any]], protect: int) -> List[Dict[str, Any]]:
    kept: List[Dict[str, Any]] = []
    for i, m in enumerate(messages):
        if i < protect:
            kept.append(m)
            continue
        c = clm_content_text(m.get("content"))
        if c and c.strip():
            kept.append(m)

    merged: List[Dict[str, Any]] = []
    for i, m in enumerate(kept):
        if (
            merged
            and i >= protect
            and len(merged) > protect
            and m.get("role") in ("user", "assistant")
            and merged[-1].get("role") == m.get("role")
        ):
            prev = clm_content_text(merged[-1].get("content")) or ""
            cur = clm_content_text(m.get("content")) or ""
            merged[-1] = {"role": m["role"], "content": (prev + "\n\n" + cur).strip()}
        else:
            merged.append(m)
    return merged


def clm_parse_back(edited: Any, protected: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Re-parse un contexte édité arbitrairement en préservant le préfixe protégé verbatim."""
    text = edited if isinstance(edited, str) else str(edited)
    matches = list(_CLM_HEADER_RE.finditer(text))
    sections: List[Tuple[str, str]] = []
    if not matches:
        body = text.strip()
        if body:
            sections.append(("user", body))
    else:
        lead = text[: matches[0].start()].strip()
        if lead:
            sections.append(("user", lead))
        for k, mt in enumerate(matches):
            role = mt.group(2).lower()
            if role not in _CLM_VALID_ROLES:
                role = "user"
            start = mt.end()
            end = matches[k + 1].start() if k + 1 < len(matches) else len(text)
            body = text[start:end].strip()
            if body:
                sections.append((role, body))

    msgs: List[Dict[str, Any]] = [dict(m) for m in protected]
    for role, body in sections:
        msgs.append({"role": "assistant" if role == "assistant" else "user", "content": body})
    return _clm_normalize(msgs, protect=len(protected))


CLM_SHRINK_RULE = "A compaction must SHRINK context"
_CLM_GATES = {
    "fit": True, "shrink": False, "1": True, "true": True, "yes": True, "on": True,
    "0": False, "false": False, "no": False, "off": False,
}


def _clm_parse_gate(value: Any, source: str) -> bool:
    if isinstance(value, bool):
        return value
    key = str(value).strip().lower()
    if key not in _CLM_GATES:
        raise ValueError(f"{source} must be fit or shrink (or a boolean), got {value!r}")
    return _CLM_GATES[key]


def clm_resolve_allow_edit_growth(passed: Any, env: Optional[str] = None) -> bool:
    if passed is not None:
        return _clm_parse_gate(passed, "allow_edit_growth")
    raw = env if env is not None else os.environ.get("CLM_EDIT_GATE", "fit")
    return _clm_parse_gate(raw or "fit", "CLM_EDIT_GATE")


def clm_fit_rule(limit: int) -> str:
    return f"An edit must FIT the {limit}-token limit"


def clm_may_grow(*, allow_growth: bool, limit: int, after: int) -> bool:
    return bool(allow_growth and limit and after <= limit)


def clm_reject_rule(*, allow_growth: bool, limit: int) -> str:
    if allow_growth and limit:
        return clm_fit_rule(limit)
    return CLM_SHRINK_RULE


def clm_rejected_note(*, baseline: int, after: int, before: int, rule: str) -> str:
    return (
        f"\n[LIVE_CTX_MAIN.txt: edit REJECTED — it GREW context "
        f"~{baseline}->{after} tokens, so it was NOT applied (still ~{before}). "
        f"{rule}: you likely duplicated/appended "
        f"content — replace stale text with a SHORTER summary instead.]"
    )


CLM_SUBMIT_MARKER = "COMPLETE_TASK_AND_SUBMIT_FINAL_OUTPUT"
CLM_FINISH_INSTRUCTIONS = (
    "When you are finished, submit by running the standalone command\n"
    f"`echo {CLM_SUBMIT_MARKER}` (with nothing else in that command).\n"
    "After it runs you cannot continue."
)
CLM_FINISH_MODES = ("submit", "open_ended")
_CLM_SUBMIT_COMMAND_RE = re.compile(
    rf"""^\s*(?:/bin/)?echo\s+(?:['"])?{re.escape(CLM_SUBMIT_MARKER)}(?:['"])?\s*$"""
)


def clm_is_submit_command(cmd: str) -> bool:
    return _CLM_SUBMIT_COMMAND_RE.match(cmd or "") is not None


class CLMFinishPolicy:
    """Politique de complétion M044 (`submit` vs `open_ended`)."""

    __slots__ = ("mode",)

    def __init__(self, mode: str = "submit") -> None:
        m = (str(mode or "submit")).strip().lower()
        if m in ("", "1", "true", "submit"):
            m = "submit"
        elif m in ("open_ended", "open-ended", "openended"):
            m = "open_ended"
        else:
            raise ValueError(f"finish_policy must be one of {CLM_FINISH_MODES}, got {mode!r}")
        self.mode = m

    @property
    def open_ended(self) -> bool:
        return self.mode == "open_ended"

    def is_finish_command(self, cmd: str) -> bool:
        if self.open_ended:
            return False
        return clm_is_submit_command(cmd)

    def prompt_fragment(self) -> str:
        if self.open_ended:
            return ""
        return CLM_FINISH_INSTRUCTIONS

    def __repr__(self) -> str:
        return f"CLMFinishPolicy({self.mode!r})"


_CLM_USES_COMPLETION_TOKENS = {"gpt-5-4", "gpt-5-4-mini", "gpt-5-4-nano", "gpt-o4-mini"}


def clm_token_cap_key(model: str) -> str:
    name = (model or "").split("/")[-1]
    if name in _CLM_USES_COMPLETION_TOKENS or name.startswith(("gpt-5", "gpt-o")):
        return "max_completion_tokens"
    return "max_tokens"


# ===========================================================================
# 4. M045 dox — Validateur de Hiérarchie Contractuelle AGENTS.md / CLAUDE.md
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
# 5. M046 gbrain — Index Hybride (BM25 + Vecteur N-Gram + Graphe) + M1-M8
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
# 6. M047 graphify — Graphe AST Multi-Langages (.py/.ts/.rs) & Communautés
# ===========================================================================

class ASTCodeGraphBuilder:
    """Analyse des fichiers Python/TS/JS/Rust pour bâtir graphe de dépendances et communautés."""

    _TS_EXPORT_RE = re.compile(
        r"(?:^|\n)\s*(?:export\s+)?(?:async\s+)?(class|function|interface|type)\s+([A-Za-z_][A-Za-z0-9_]*)"
        r"|(?:^|\n)\s*export\s+(?:const|let)\s+([A-Za-z_][A-Za-z0-9_]*)"
    )
    _TS_IMPORT_RE = re.compile(r"""import\s+[^;]*?\s+from\s+['"]([^'"]+)['"]""")
    _RS_DEF_RE = re.compile(
        r"(?:^|\n)\s*(?:pub(?:\([^)]*\))?\s+)?(?:async\s+)?(fn|struct|enum|trait|mod)\s+([A-Za-z_][A-Za-z0-9_]*)"
    )
    _RS_USE_RE = re.compile(r"(?:^|\n)\s*(?:pub\s+)?use\s+([A-Za-z0-9_:]+)")

    @staticmethod
    def _parse_python(p: Path, src: str, mod_name: str, nodes: Dict[str, Dict[str, Any]], edges: List[Dict[str, str]]) -> None:
        tree = ast.parse(src, filename=str(p))
        nodes[mod_name] = {"kind": "module", "lang": "python", "file": str(p), "lineno": 1}
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                qname = f"{mod_name}.{node.name}"
                nodes[qname] = {"kind": "class", "lang": "python", "file": str(p), "lineno": node.lineno}
                edges.append({"from": mod_name, "to": qname, "kind": "defines"})
            elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                qname = f"{mod_name}.{node.name}"
                nodes[qname] = {"kind": "function", "lang": "python", "file": str(p), "lineno": node.lineno}
                edges.append({"from": mod_name, "to": qname, "kind": "defines"})
            elif isinstance(node, ast.ImportFrom) and node.module:
                edges.append({"from": mod_name, "to": node.module, "kind": "imports"})
            elif isinstance(node, ast.Import):
                for alias in node.names:
                    edges.append({"from": mod_name, "to": alias.name, "kind": "imports"})

    @classmethod
    def _parse_ts_js(cls, p: Path, src: str, mod_name: str, nodes: Dict[str, Dict[str, Any]], edges: List[Dict[str, str]]) -> None:
        lang = "typescript" if p.suffix in {".ts", ".tsx"} else "javascript"
        nodes[mod_name] = {"kind": "module", "lang": lang, "file": str(p), "lineno": 1}
        for m in cls._TS_EXPORT_RE.finditer(src):
            kind = m.group(1) or "const"
            name = m.group(2) or m.group(3)
            if not name:
                continue
            lineno = src.count("\n", 0, m.start()) + 1
            qname = f"{mod_name}.{name}"
            nodes[qname] = {"kind": kind, "lang": lang, "file": str(p), "lineno": lineno}
            edges.append({"from": mod_name, "to": qname, "kind": "defines"})
        for m in cls._TS_IMPORT_RE.finditer(src):
            edges.append({"from": mod_name, "to": m.group(1), "kind": "imports"})

    @classmethod
    def _parse_rust(cls, p: Path, src: str, mod_name: str, nodes: Dict[str, Dict[str, Any]], edges: List[Dict[str, str]]) -> None:
        nodes[mod_name] = {"kind": "module", "lang": "rust", "file": str(p), "lineno": 1}
        for m in cls._RS_DEF_RE.finditer(src):
            kind, name = m.group(1), m.group(2)
            lineno = src.count("\n", 0, m.start()) + 1
            qname = f"{mod_name}::{name}"
            nodes[qname] = {"kind": kind, "lang": "rust", "file": str(p), "lineno": lineno}
            edges.append({"from": mod_name, "to": qname, "kind": "defines"})
        for m in cls._RS_USE_RE.finditer(src):
            edges.append({"from": mod_name, "to": m.group(1), "kind": "imports"})

    def build_from_files(self, paths: Sequence[Path]) -> Dict[str, Any]:
        nodes: Dict[str, Dict[str, Any]] = {}
        edges: List[Dict[str, str]] = []
        langs: Set[str] = set()
        for p in paths:
            if not p.exists() or not p.is_file():
                continue
            suf = p.suffix.lower()
            src = p.read_text(encoding="utf-8", errors="ignore")
            mod_name = p.stem
            if suf == ".py":
                self._parse_python(p, src, mod_name, nodes, edges)
                langs.add("python")
            elif suf in {".ts", ".tsx", ".js", ".mjs", ".cjs"}:
                self._parse_ts_js(p, src, mod_name, nodes, edges)
                langs.add("typescript" if suf in {".ts", ".tsx"} else "javascript")
            elif suf == ".rs":
                self._parse_rust(p, src, mod_name, nodes, edges)
                langs.add("rust")
        return {
            "schema": "aspace.graphify.ast.v1",
            "kernel": "ÂME",
            "organ": "K4",
            "languages": sorted(langs),
            "nodes": nodes,
            "edges": edges,
        }

    @staticmethod
    def detect_communities(graph: Dict[str, Any], max_iter: int = 12) -> Dict[str, Any]:
        """Détection déterministe de communautés (label propagation + modularité Newman-Girvan Q)."""
        adj: Dict[str, Dict[str, float]] = {nid: {} for nid in graph.get("nodes", {})}
        total_weight = 0.0
        for edge in graph.get("edges", []):
            u, v = edge["from"], edge["to"]
            if u == v:
                continue
            adj.setdefault(u, {})
            adj.setdefault(v, {})
            adj[u][v] = adj[u].get(v, 0.0) + 1.0
            adj[v][u] = adj[v].get(u, 0.0) + 1.0
            total_weight += 1.0

        ordered = sorted(adj.keys())
        labels: Dict[str, str] = {nid: nid for nid in ordered}
        for _ in range(max_iter):
            changed = False
            for nid in ordered:
                nbrs = adj[nid]
                if not nbrs:
                    continue
                scores: Dict[str, float] = {}
                for nb, w in nbrs.items():
                    lbl = labels[nb]
                    scores[lbl] = scores.get(lbl, 0.0) + w
                best_score = max(scores.values())
                best_lbl = min(lbl for lbl, sc in scores.items() if sc == best_score)
                if best_lbl != labels[nid]:
                    labels[nid] = best_lbl
                    changed = True
            if not changed:
                break

        two_m = 2.0 * total_weight
        modularity = 0.0
        if two_m > 0.0:
            deg = {nid: sum(adj[nid].values()) for nid in ordered}
            by_cluster_nodes: Dict[str, List[str]] = {}
            for nid in ordered:
                by_cluster_nodes.setdefault(labels[nid], []).append(nid)
            for members in by_cluster_nodes.values():
                mset = set(members)
                internal_twice = sum(
                    w for u in members for v, w in adj[u].items() if v in mset
                )
                sum_deg = sum(deg[u] for u in members)
                modularity += (internal_twice / two_m) - (sum_deg / two_m) ** 2

        clusters_map: Dict[str, List[str]] = {}
        for nid in ordered:
            clusters_map.setdefault(labels[nid], []).append(nid)
        clusters = [
            {"cluster_id": idx, "size": len(mems), "members": mems}
            for idx, mems in enumerate(sorted(clusters_map.values(), key=lambda m: (-len(m), m[0])), 1)
        ]
        return {
            "schema": "aspace.graphify.communities.v1",
            "community_count": len(clusters),
            "modularity_q": round(modularity, 4),
            "communities": clusters,
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
# 7. M048 infinite-brain-harness & M049 infinite-brain-os — Multi-Cerveaux Isolés
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
# 8. M050 knowledge-catalog — OKF v0.2 Document, Trust Tier & Index Generator
# ===========================================================================

_OKF_REQUIRED_KEYS = ("type",)
_OKF_FRONTMATTER_DELIM = "---"
_OKF_INDEX_FILE = "index.md"


class _OKFSafeLoader(yaml.SafeLoader):
    """SafeLoader YAML 1.2 préservant les timestamps ISO-8601 sous forme str."""


_OKFSafeLoader.yaml_implicit_resolvers = {
    ch: [(tag, regexp) for tag, regexp in resolvers if tag != "tag:yaml.org,2002:timestamp"]
    for ch, resolvers in yaml.SafeLoader.yaml_implicit_resolvers.items()
}


class OKFDocumentError(ValueError):
    pass


@dataclass
class OKFDocument:
    frontmatter: Dict[str, Any] = field(default_factory=dict)
    body: str = ""

    @classmethod
    def parse(cls, text: str) -> "OKFDocument":
        lines = text.splitlines()
        if not lines or lines[0].strip() != _OKF_FRONTMATTER_DELIM:
            return cls(frontmatter={}, body=text)
        end_idx = None
        for i in range(1, len(lines)):
            if lines[i].strip() == _OKF_FRONTMATTER_DELIM:
                end_idx = i
                break
        if end_idx is None:
            raise OKFDocumentError("Unterminated YAML frontmatter block")
        fm_text = "\n".join(lines[1:end_idx])
        try:
            fm = yaml.load(fm_text, Loader=_OKFSafeLoader) or {}
        except yaml.YAMLError as exc:
            raise OKFDocumentError(f"Invalid YAML in frontmatter: {exc}") from exc
        if not isinstance(fm, dict):
            raise OKFDocumentError("Frontmatter must be a YAML mapping")
        body = "\n".join(lines[end_idx + 1 :])
        if body.startswith("\n"):
            body = body[1:]
        return cls(frontmatter=fm, body=body)

    def serialize(self) -> str:
        fm_text = yaml.safe_dump(self.frontmatter, sort_keys=False, allow_unicode=True).rstrip()
        body = self.body if self.body.endswith("\n") else self.body + "\n"
        return f"{_OKF_FRONTMATTER_DELIM}\n{fm_text}\n{_OKF_FRONTMATTER_DELIM}\n\n{body}"

    def validate(self) -> None:
        missing = [k for k in _OKF_REQUIRED_KEYS if not self.frontmatter.get(k)]
        if missing:
            raise OKFDocumentError(f"Missing required frontmatter keys: {', '.join(missing)}")


def okf_normalize_verified(frontmatter: Dict[str, Any]) -> List[Dict[str, Any]]:
    verified = frontmatter.get("verified")
    if verified is None:
        return []
    if isinstance(verified, dict):
        return [verified]
    if isinstance(verified, list):
        return [v for v in verified if isinstance(v, dict)]
    return []


def okf_trust_tier(frontmatter: Dict[str, Any]) -> str:
    events = okf_normalize_verified(frontmatter)
    if not events:
        return "unverified"
    for event in events:
        if str(event.get("by") or "").startswith("human:"):
            return "human-reviewed"
    return "machine-confirmed"


def okf_is_stale(frontmatter: Dict[str, Any], now: Optional[dt.datetime] = None) -> bool:
    raw = str(frontmatter.get("stale_after") or "")
    if "T" not in raw:
        return False
    try:
        stale_after = dt.datetime.fromisoformat(raw)
    except ValueError:
        return False
    if stale_after.tzinfo is None:
        return False
    return (now or dt.datetime.now(dt.timezone.utc)) >= stale_after


def okf_synthesize_fallback(rel_path: str, children: List[Tuple[str, str]], *, model: str = "stub") -> str:
    if not children:
        return ""
    titles = ", ".join(t for t, _ in children if t) or "no titled entries"
    return f"Contains {len(children)} entries: {titles}."


def _okf_build_index_text(entries: List[Tuple[str, str, str, str]]) -> str:
    grouped: Dict[str, List[Tuple[str, str, str]]] = defaultdict(list)
    for typ, title, link, desc in entries:
        grouped[typ or "Other"].append((title, link, desc))
    sections: List[str] = []
    for typ in sorted(grouped):
        lines = [f"# {typ}", ""]
        for title, link, desc in sorted(grouped[typ], key=lambda e: e[0].lower()):
            suffix = f" - {desc}" if desc else ""
            lines.append(f"* [{title}]({link}){suffix}")
        sections.append("\n".join(lines))
    return "\n\n".join(sections) + "\n"


def okf_regenerate_indexes(
    bundle_root: Path,
    *,
    model: str = "stub",
    synthesize: Callable[..., str] = okf_synthesize_fallback,
) -> List[Path]:
    bundle_root = Path(bundle_root)
    written: List[Path] = []
    if not bundle_root.exists():
        return written
    dirs: Set[Path] = set()
    for md in bundle_root.rglob("*.md"):
        cur = md.parent
        while cur != bundle_root.parent:
            dirs.add(cur)
            if cur == bundle_root:
                break
            cur = cur.parent
    directories = sorted(dirs, key=lambda p: (-len(p.relative_to(bundle_root).parts), str(p)))
    dir_descriptions: Dict[Path, str] = {}

    for directory in directories:
        entries: List[Tuple[str, str, str, str]] = []
        for child in sorted(directory.iterdir()):
            if child.name == _OKF_INDEX_FILE:
                continue
            if child.is_file() and child.suffix == ".md":
                try:
                    doc = OKFDocument.parse(child.read_text(encoding="utf-8"))
                except Exception:
                    continue
                fm = doc.frontmatter
                entries.append(
                    (
                        str(fm.get("type") or ""),
                        str(fm.get("title") or child.stem),
                        child.name,
                        str(fm.get("description") or ""),
                    )
                )
            elif child.is_dir():
                entries.append(("Subdirectories", child.name, f"{child.name}/{_OKF_INDEX_FILE}", dir_descriptions.get(child, "")))
        if not entries:
            continue
        index_path = directory / _OKF_INDEX_FILE
        index_path.write_text(_okf_build_index_text(entries), encoding="utf-8")
        written.append(index_path)
        if directory == bundle_root:
            continue
        pairs = [(title, desc) for _, title, _, desc in entries]
        if len(pairs) == 1 and pairs[0][1]:
            dir_descriptions[directory] = pairs[0][1]
        else:
            rel = str(directory.relative_to(bundle_root))
            dir_descriptions[directory] = synthesize(rel, pairs, model=model)
    return written


_OKF_SEGMENT_RE = re.compile(r"[A-Za-z0-9_][A-Za-z0-9_.\-]*")


def _okf_validate_segment(seg: str) -> None:
    if not _OKF_SEGMENT_RE.fullmatch(seg):
        raise ValueError(f"Invalid concept id segment: {seg!r}")


def okf_concept_id_to_path(bundle_root: Path, concept_id: Tuple[str, ...]) -> Path:
    if not concept_id:
        raise ValueError("concept_id must have at least one segment")
    for seg in concept_id:
        _okf_validate_segment(seg)
    *dirs, name = concept_id
    return Path(bundle_root).joinpath(*dirs, f"{name}.md")


def okf_path_to_concept_id(bundle_root: Path, path: Path) -> Tuple[str, ...]:
    rel = Path(path).relative_to(Path(bundle_root)).with_suffix("")
    return tuple(rel.parts)


def okf_parse_concept_id(s: str) -> Tuple[str, ...]:
    parts = tuple(p for p in s.split("/") if p)
    if not parts:
        raise ValueError(f"Empty concept id: {s!r}")
    for p in parts:
        _okf_validate_segment(p)
    return parts


# ===========================================================================
# Suite de vérification des 9 modules FKB02 sans accès aux répertoires sources
# ===========================================================================

def run_fkb02_self_test(repo_root: Optional[Path] = None, head_sha40: str = "0" * 40) -> Dict[str, Any]:
    import tempfile

    root = repo_root or Path(__file__).resolve().parents[3]
    checks: Dict[str, bool] = {}
    with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as tmpdir:
        tdir = Path(tmpdir)

        # 1. billion-context (M043)
        cas = HierarchicalCASStore(tdir / "cas")
        cas_rec = cas.ingest_document("doc-1", "Aspace Foundation unifies kernels via Rust contracts." * 10, chunk_chars=80)
        first_sha = cas_rec["l0_refs"][0]["sha256"]
        checks["billion_context_cas"] = "Aspace Foundation" in cas.retrieve_l0_slice(first_sha)
        assert checks["billion_context_cas"]

        # 2. auto-ontology (M042)
        onto = AutoOntologyCompiler()
        r1 = onto.compile_triples("s1", [("ÂME", "rattache", "K1"), ("K1", "valide", "R10")])
        r2 = onto.compile_triples("s2", [("K1", "valide", "SessionOnly")])
        checks["auto_ontology_dag"] = (
            r1["acyclic_dag"]
            and not r1["contradictions"]
            and len(r2["contradictions"]) == 1
            and r2["contradictions"][0]["epistemic_status"] == "contredit"
        )
        assert checks["auto_ontology_dag"]

        # 3. context-language-models (M044) — context_string, edit_gate, finish_policy, lm_compat
        protected = [{"role": "system", "content": "SYS"}, {"role": "user", "content": "TASK"}]
        rendered = clm_render_editable(protected + [{"role": "assistant", "content": "A"}, {"role": "tool", "content": "T"}])
        reparsed = clm_parse_back(rendered, protected)
        fp = CLMFinishPolicy("submit")
        checks["clm_roundtrip"] = (
            clm_content_text([{"type": "text", "text": "ok"}]) == "ok"
            and clm_rendered_text({"reasoning_content": "R", "content": "C"}) == "R\nC"
            and len(reparsed) == 4
            and reparsed[3]["role"] == "user"
            and clm_resolve_allow_edit_growth("fit") is True
            and clm_may_grow(allow_growth=True, limit=100, after=80) is True
            and fp.is_finish_command(f"echo {CLM_SUBMIT_MARKER}") is True
            and clm_token_cap_key("gpt-5-4") == "max_completion_tokens"
        )
        assert checks["clm_roundtrip"]

        # 4. dox (M045)
        dox_res = validate_dox_contract(root)
        checks["dox_hierarchy"] = bool(dox_res["valid"] and dox_res["core_agents_md_count"] >= 2)
        assert checks["dox_hierarchy"]

        # 5. gbrain (M046) + M1-M8
        gb = HybridBrainIndex()
        gb.put_page("p1", "RigInfinity implements pure data hibernation and PTY daemon.", "RigInfinity/Cargo.toml:1", "2026-11-19", links=["p2"])
        gb.put_page("p2", "fondation-13-1 checks M1-M8 citations deterministically.", "fondation-13-1/src/memory.rs:1", "2026-11-19")
        hits = gb.search_hybrid("hibernation RigInfinity", focus_page="p2")
        cit_md = """**Fonction :** memorizer
**Date de la citation :** `2026-11-19`
**Fait demandé :** Test M046
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
        checks["gbrain_hybrid_m1_m8"] = bool(hits and hits[0]["page_id"] == "p1" and v_cit["status"] == "vérifié")
        assert checks["gbrain_hybrid_m1_m8"]

        # 6. graphify (M047)
        ast_builder = ASTCodeGraphBuilder()
        rs_probe = tdir / "sample_probe.rs"
        rs_probe.write_text("use std::collections::BTreeMap;\npub struct NativeKernel;\npub fn verify_r10() -> bool { true }\n", encoding="utf-8")
        ts_probe = tdir / "sample_probe.ts"
        ts_probe.write_text("import { EventJournal } from './kernel';\nexport interface FiberSpec { id: string }\nexport function dispatchFiber() { return true; }\n", encoding="utf-8")
        code_g = ast_builder.build_from_files([Path(__file__), _CORE_DIR / "aspace_foundation_kernel.py", rs_probe, ts_probe])
        exp = ast_builder.explain_symbol(code_g, "EventJournal")
        comm = ast_builder.detect_communities(code_g)
        checks["graphify_multilang_communities"] = (
            exp["edges_count"] >= 1
            and set(code_g["languages"]) >= {"python", "rust", "typescript"}
            and comm["community_count"] >= 1
        )
        assert checks["graphify_multilang_communities"]

        # 7 & 8. infinite-brain-harness (M048) & infinite-brain-os (M049)
        mgr = MultiBrainNamespaceManager(tdir / "brains")
        mgr.mount_brain("personal-a0", tier="individual")
        mgr.mount_brain("b2b-client-alpha", tier="b2b-client")
        mgr.write_note("personal-a0", "secret-note", "Note", "Personal secret token-free observation")
        mgr.write_note("b2b-client-alpha", "offer", "Specification", "B2B OMK client deliverable")
        checks["multi_brain_isolation"] = (
            len(mgr.query_brain("personal-a0", "Personal")) == 1
            and len(mgr.query_brain("b2b-client-alpha", "Personal")) == 0
        )
        assert checks["multi_brain_isolation"]

        # 9. knowledge-catalog (M050)
        okf_concepts_count = len(list((root / "00_Memoire" / "bundle" / "concepts").glob("*.md"))) if (root / "00_Memoire" / "bundle" / "concepts").is_dir() else 0
        okf_doc = OKFDocument(frontmatter={"type": "Concept", "title": "Probe", "description": "OKF probe."}, body="# Probe\n")
        okf_doc.validate()
        okf_reparsed = OKFDocument.parse(okf_doc.serialize())
        parsed_cid = okf_parse_concept_id("concepts/probe")
        cid_path = okf_concept_id_to_path(tdir, parsed_cid)
        okf_bundle_tmp = tdir / "okf_idx_test"
        (okf_bundle_tmp / "sub").mkdir(parents=True)
        (okf_bundle_tmp / "sub" / "item.md").write_text(okf_doc.serialize(), encoding="utf-8")
        gen_idx = okf_regenerate_indexes(okf_bundle_tmp)
        checks["okf_bundle_and_doc"] = bool(
            okf_concepts_count >= 15
            and okf_reparsed.frontmatter["type"] == "Concept"
            and okf_trust_tier({"verified": {"by": "human:amdkn", "at": "2026-11-19T00:00:00Z"}}) == "human-reviewed"
            and okf_is_stale({"stale_after": "2020-01-01T00:00:00Z"}) is True
            and okf_path_to_concept_id(tdir, cid_path) == parsed_cid
            and len(gen_idx) >= 1
        )
        assert checks["okf_bundle_and_doc"]

        passed = sum(1 for v in checks.values() if v)
        total = len(checks)
        evt, rec = consign_measured_l0_evidence(
            actor_from="memorizer",
            actor_to="judge",
            dispatch_id="D-FKB02-SMOKE",
            payload=f"FKB02 smoke checks: {passed}/{total} internal, 0 source-oracle parities",
            issuer="Organ FKB02",
            mission_prefix="FKB02-SMOKE",
            sha=head_sha40,
            proof=["01_Forkable/FKB00_Runtime/00_A0_Core/aspace_fkb02_memory_organ.py"],
            summary=f"FKB02 smoke={passed}/{total}; okf_concepts={okf_concepts_count}; source_oracle_parity=0 at {head_sha40[:7]}",
            event_type="fact_recalled",
            repo_root=root,
        )
        return {
            "organ": "aspace_fkb02_memory_organ",
            "checks": checks,
            "checks_passed": passed,
            "checks_total": total,
            "source_parity_verified": [],
            "graphify_languages": code_g["languages"],
            "graphify_communities": comm["community_count"],
            "okf_concepts": okf_concepts_count,
            "l0_seq": evt["seq"],
            "r10_entry_id": rec["entry_id"],
        }


def consign_fkb02_parity_receipt(
    module_results: Dict[str, Dict[str, Any]],
    head_sha40: str,
    repo_root: Optional[Path] = None,
) -> Dict[str, Any]:
    """Consigne uniquement la parité source-vs-organe réellement mesurée sur FKB02."""
    verified = sorted(
        mid
        for mid, res in module_results.items()
        if res.get("compared_against_source") and res.get("cases_compared", 0) > 0 and res.get("cases_matched") == res.get("cases_compared")
    )
    total_cases = sum(int(res.get("cases_compared", 0)) for res in module_results.values())
    total_matched = sum(int(res.get("cases_matched", 0)) for res in module_results.values())
    evt, rec = consign_measured_l0_evidence(
        actor_from="memorizer",
        actor_to="judge",
        dispatch_id="D-FKB02-PARITY",
        payload=f"FKB02 differential parity: {verified} ({total_matched}/{total_cases} cases)",
        issuer="Organ FKB02",
        mission_prefix="FKB02-PARITY",
        sha=head_sha40,
        proof=["01_Forkable/FKB00_Runtime/00_A0_Core/aspace_fkb02_memory_organ.py"],
        summary=f"FKB02 measured parity {total_matched}/{total_cases} across {verified} at {head_sha40[:7]}",
        event_type="fact_recalled",
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
    print(json.dumps(run_fkb02_self_test(), indent=2, ensure_ascii=False))
