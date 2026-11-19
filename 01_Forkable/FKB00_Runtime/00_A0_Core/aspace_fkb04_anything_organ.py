#!/usr/bin/env python3
"""
aspace_fkb04_anything_organ.py — Organes Natifs de la Famille FKB04_Tools_Anything.

Rattachement ADR-13 aux Trois Noyaux Fondamentaux :
  - CORPS / Organe K2 (Action Multi-Harness & Surfaces) :
      M058 CLI-Anything | M059 agent-browser | M060 agent-desktop | M061 api-anything | M065 rea
  - ÂME / Organe K4 (Mémoire Épistémique & Compétences) :
      M062 caveman | M063 claude-mem | M064 hermes-agent

Chaque capacité expose des contrats déterministes, émet des événements conformes au socle L0
(`fondation-13-1` / `aspace_foundation_kernel.py`), et fonctionne de façon 100 % autonome
même lorsque tous les répertoires sources `01_Forkable/FKB04_Tools_Anything/*` sont supprimés.
Zéro dépendance externe, zéro télémétrie, zéro contournement CAPTCHA.
"""

from __future__ import annotations

import datetime as dt
import hashlib
import json
import math
import re
import subprocess
import sys
from pathlib import Path
from typing import Any, Callable, Dict, Iterable, List, Optional, Sequence, Tuple
from urllib.parse import urlparse

_CORE_DIR = Path(__file__).resolve().parent
if str(_CORE_DIR) not in sys.path:
    sys.path.insert(0, str(_CORE_DIR))

from aspace_foundation_kernel import (  # noqa: E402
    ContractViolation,
    EventJournal,
    R10Ledger,
    R10_SCHEMA,
)

# ---------------------------------------------------------------------------
# Guard anti-bot / CAPTCHA partagé (ADR-08, règles agent-browser)
# ---------------------------------------------------------------------------
ANTIBOT_MARKERS = (
    "captcha",
    "recaptcha",
    "hcaptcha",
    "cf-turnstile",
    "cloudflare turnstile",
    "verify you are human",
    "vérifier que vous êtes humain",
    "altcha",
)

SENSITIVE_HEADER_KEYS = frozenset({"authorization", "cookie", "set-cookie", "x-api-key", "x-auth-token"})

STOPWORDS_FILLER = frozenset(
    {
        "the", "a", "an", "please", "kindly", "basically", "actually", "literally",
        "simply", "just", "very", "really", "likely", "probably", "therefore",
        "however", "furthermore", "additionally", "would", "recommend", "suggest",
        "is", "are", "was", "were", "that", "which", "your", "their", "these",
        "those", "order", "also", "because", "when", "you", "for", "with", "into",
        "la", "le", "les", "un", "une", "des", "du", "de", "dans", "pour", "avec",
        "que", "qui", "est", "sont", "cette", "cet", "ce", "nous", "vous", "donc",
        "cependant", "simplement", "vraiment", "afin",
    }
)


# ===========================================================================
# 1. M058 CLI-Anything (CORPS / Organe K2)
# ===========================================================================

def compile_cli_anything_spec(binary_name: str, help_text: str) -> Dict[str, Any]:
    """Transforme une sortie `--help` arbitraire en schéma de sous-commandes CLI-Anything JSON."""
    subcommands: List[Dict[str, Any]] = []
    flags: List[Dict[str, Any]] = []
    mode = "scan"
    for raw_ln in help_text.splitlines():
        ln = raw_ln.strip()
        if not ln:
            continue
        low = ln.lower()
        if low.startswith(("commands:", "subcommands:", "available commands:")):
            mode = "commands"
            continue
        if low.startswith(("options:", "flags:")):
            mode = "options"
            continue

        m_flag = re.match(r"^(?:-[a-zA-Z],\s*)?(--[a-zA-Z0-9][a-zA-Z0-9_-]*)(?:\s+<([^>]+)>)?\s+(.*)$", ln)
        if m_flag:
            flags.append(
                {
                    "flag": m_flag.group(1),
                    "arg_type": "string" if m_flag.group(2) else "boolean",
                    "value_placeholder": m_flag.group(2) or "",
                    "description": m_flag.group(3).strip(),
                }
            )
            continue

        if mode == "commands":
            m_cmd = re.match(r"^([a-zA-Z][a-zA-Z0-9_-]*)\s{2,}(.+)$", ln)
            if m_cmd:
                subcommands.append({"name": m_cmd.group(1), "description": m_cmd.group(2).strip()})
                continue

        # Support format "--help" à plat sans entête explicite
        m_flat = re.match(r"^([a-z][a-z0-9_-]{1,24})\s{2,}(.+)$", ln)
        if m_flat and not ln.startswith("-"):
            subcommands.append({"name": m_flat.group(1), "description": m_flat.group(2).strip()})

    return {
        "schema": "aspace.cli-anything.v1",
        "kernel": "CORPS",
        "organ": "K2",
        "binary": binary_name,
        "output_mode": "json",
        "subcommands": subcommands,
        "flags": flags,
    }


def execute_cli_structured(
    spec: Dict[str, Any],
    subcommand: Optional[str],
    kv_args: Optional[Dict[str, Any]] = None,
    runner: Optional[Callable[[List[str]], subprocess.CompletedProcess[str]]] = None,
) -> Dict[str, Any]:
    """Construit et exécute une commande CLI typée (avec enveloppe JSON structurée garantie)."""
    allowed_cmds = {c["name"] for c in spec.get("subcommands", [])}
    if subcommand and allowed_cmds and subcommand not in allowed_cmds:
        raise ContractViolation("K2", "subcommand", f"sous-commande inconnue pour {spec['binary']}: {subcommand}")

    argv = [spec["binary"]]
    if subcommand:
        argv.append(subcommand)
    allowed_flags = {f["flag"]: f["arg_type"] for f in spec.get("flags", [])}
    for k, v in sorted((kv_args or {}).items()):
        flag = k if k.startswith("--") else f"--{k}"
        if allowed_flags and flag not in allowed_flags:
            raise ContractViolation("K2", flag, f"option non déclarée dans la spec de {spec['binary']}")
        if allowed_flags.get(flag) == "boolean":
            if v:
                argv.append(flag)
        else:
            argv.extend([flag, str(v)])

    exec_fn = runner or (lambda cmd: subprocess.run(cmd, capture_output=True, text=True, check=False))
    proc = exec_fn(argv)
    return {
        "binary": spec["binary"],
        "argv": argv,
        "returncode": proc.returncode,
        "stdout": proc.stdout,
        "stderr": proc.stderr,
        "ok": proc.returncode == 0,
    }


# ===========================================================================
# 2. M059 agent-browser (CORPS / Organe K2)
# ===========================================================================

def detect_antibot_gate(page_text: str, url: str = "") -> Optional[str]:
    """Vérifie strictement si une page est protégée par CAPTCHA / anti-bot (jamais contourné)."""
    haystack = f"{url} {page_text}".lower()
    for marker in ANTIBOT_MARKERS:
        if marker in haystack:
            return marker
    return None


def build_cdp_a11y_snapshot(
    dom_nodes: Sequence[Dict[str, Any]],
    url: str,
    page_text: str = "",
) -> Dict[str, Any]:
    """Produit un snapshot CDP d'arbre d'accessibilité à références stables `@e1..@eN`."""
    blocked_marker = detect_antibot_gate(page_text, url=url)
    if blocked_marker:
        return {
            "schema": "aspace.agent-browser.snapshot.v1",
            "kernel": "CORPS",
            "organ": "K2",
            "url": url,
            "status": "BLOQUÉ",
            "block_reason": f"Anti-bot / CAPTCHA détecté ({blocked_marker}) — arrêt strict sans contournement.",
            "refs": {},
            "elements": [],
        }

    elements: List[Dict[str, Any]] = []
    refs: Dict[str, Dict[str, Any]] = {}
    for idx, node in enumerate(dom_nodes, 1):
        role = str(node.get("role", "generic"))
        name = str(node.get("name", "")).strip()
        interactive = role in {"button", "link", "textbox", "checkbox", "combobox", "menuitem", "tab"} or bool(node.get("interactive"))
        if not interactive and not name:
            continue
        ref = f"@e{len(elements) + 1}"
        entry = {
            "ref": ref,
            "role": role,
            "name": name,
            "interactive": interactive,
            "backend_node_id": node.get("backendNodeId", idx),
        }
        elements.append(entry)
        refs[ref] = entry

    return {
        "schema": "aspace.agent-browser.snapshot.v1",
        "kernel": "CORPS",
        "organ": "K2",
        "url": url,
        "status": "READY",
        "telemetry_disabled": True,
        "refs": refs,
        "elements": elements,
    }


# ===========================================================================
# 3. M060 agent-desktop (CORPS / Organe K2)
# ===========================================================================

def plan_desktop_a11y_action(
    uia_tree: Sequence[Dict[str, Any]],
    target_ref: str,
    action: str,
    text_input: Optional[str] = None,
    no_focus_steal: bool = True,
) -> Dict[str, Any]:
    """Planifie une action d'accessibilité OS native en imposant `no_focus_steal=True`."""
    if not no_focus_steal:
        raise ContractViolation("K2", "no_focus_steal", "le vol de focus humain est interdit sur agent-desktop")
    allowed_actions = {"click", "type", "focus_a11y", "read_value", "toggle", "invoke"}
    if action not in allowed_actions:
        raise ContractViolation("K2", "action", f"action desktop inconnue: {action}")

    index: Dict[str, Dict[str, Any]] = {}
    for idx, elem in enumerate(uia_tree, 1):
        rid = str(elem.get("ref") or elem.get("id") or f"@d{idx}")
        index[rid] = elem

    if target_ref not in index:
        raise ContractViolation("K2", "target_ref", f"élément d'accessibilité OS introuvable: {target_ref}")
    target = index[target_ref]
    if target.get("enabled", True) is False:
        raise ContractViolation("K2", "enabled", f"élément désactivé: {target_ref}")

    return {
        "schema": "aspace.agent-desktop.plan.v1",
        "kernel": "CORPS",
        "organ": "K2",
        "target_ref": target_ref,
        "control_type": target.get("control_type", "Control"),
        "name": target.get("name", ""),
        "action": action,
        "text_input": text_input if action == "type" else None,
        "no_focus_steal": True,
        "background_uia_invoke": True,
    }


# ===========================================================================
# 4. M061 api-anything (CORPS / Organe K2)
# ===========================================================================

def _normalize_api_path(raw_path: str) -> Tuple[str, List[str]]:
    segments = []
    params = []
    for seg in raw_path.strip("/").split("/"):
        if not seg:
            continue
        if re.fullmatch(r"(?:\d+|[0-9a-f]{8,}|[0-9a-f-]{32,36})", seg, flags=re.IGNORECASE):
            pname = f"id_{len(params) + 1}"
            segments.append("{" + pname + "}")
            params.append(pname)
        else:
            segments.append(seg)
    return "/" + "/".join(segments), params


def _infer_json_schema(obj: Any) -> Dict[str, Any]:
    if isinstance(obj, dict):
        return {
            "type": "object",
            "properties": {str(k): _infer_json_schema(v) for k, v in sorted(obj.items())},
        }
    if isinstance(obj, list):
        return {"type": "array", "items": _infer_json_schema(obj[0]) if obj else {"type": "unknown"}}
    if isinstance(obj, bool):
        return {"type": "boolean"}
    if isinstance(obj, int):
        return {"type": "integer"}
    if isinstance(obj, float):
        return {"type": "number"}
    if obj is None:
        return {"type": "null"}
    return {"type": "string"}


def learn_api_from_har(har_entries: Sequence[Dict[str, Any]]) -> Dict[str, Any]:
    """Extrait d'une trace réseau HAR des opérations API paramétrées et descripteurs MCP sans credentials."""
    operations: Dict[str, Dict[str, Any]] = {}
    for entry in har_entries:
        req = entry.get("request", {})
        resp = entry.get("response", {})
        method = str(req.get("method", "GET")).upper()
        url_str = str(req.get("url", ""))
        parsed = urlparse(url_str)
        norm_path, path_params = _normalize_api_path(parsed.path or "/")
        op_key = f"{method} {parsed.netloc}{norm_path}"

        redacted_headers = []
        for h in req.get("headers", []):
            hname = str(h.get("name", "")).lower()
            if hname in SENSITIVE_HEADER_KEYS:
                redacted_headers.append({"name": hname, "source": f"local_vault:{hname}"})
            else:
                redacted_headers.append({"name": hname, "value": h.get("value", "")})

        req_body = None
        post_text = (req.get("postData") or {}).get("text")
        if isinstance(post_text, str) and post_text.strip().startswith(("{", "[")):
            try:
                req_body = _infer_json_schema(json.loads(post_text))
            except json.JSONDecodeError:
                req_body = {"type": "string"}

        resp_schema = {"type": "unknown"}
        resp_text = (resp.get("content") or {}).get("text")
        if isinstance(resp_text, str) and resp_text.strip().startswith(("{", "[")):
            try:
                resp_schema = _infer_json_schema(json.loads(resp_text))
            except json.JSONDecodeError:
                resp_schema = {"type": "string"}

        op_id = re.sub(r"[^a-zA-Z0-9_]+", "_", f"{method}_{parsed.netloc}_{norm_path}").strip("_").lower()
        operations[op_key] = {
            "operation_id": op_id,
            "method": method,
            "host": parsed.netloc,
            "path_template": norm_path,
            "path_params": path_params,
            "credentials_stripped": True,
            "headers_spec": redacted_headers,
            "request_schema": req_body,
            "response_schema": resp_schema,
            "mcp_tool": {
                "name": op_id,
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        **{p: {"type": "string"} for p in path_params},
                        **({"body": req_body} if req_body else {}),
                    },
                    "required": path_params,
                },
            },
        }

    return {
        "schema": "aspace.api-anything.spec.v1",
        "kernel": "CORPS",
        "organ": "K2",
        "operations_count": len(operations),
        "operations": list(operations.values()),
    }


# ===========================================================================
# 5. M062 caveman (ÂME / Organe K4)
# ===========================================================================

_PRESERVE_TOKEN_RE = re.compile(
    r"(`[^`]+`|\b[0-9a-fA-F]{40,64}\b|[A-Za-z]:\\[^\s,;]+|(?:[A-Za-z0-9_.-]+/)+[A-Za-z0-9_.-]+|\d+(?:\.\d+)?)"
)


def compress_telegraphic(text: str) -> Dict[str, Any]:
    """Compression télégraphique Caveman préservant 100 % des SHA, chemins, nombres et code."""
    preserved_literals = _PRESERVE_TOKEN_RE.findall(text)
    segments = _PRESERVE_TOKEN_RE.split(text)
    out_parts: List[str] = []
    for idx, seg in enumerate(segments):
        if idx % 2 == 1:
            out_parts.append(seg)
            continue
        kept_words = []
        for raw_w in seg.split():
            bare = re.sub(r"^[^\w]+|[^\w]+$", "", raw_w).lower()
            if bare in STOPWORDS_FILLER:
                continue
            kept_words.append(raw_w)
        if kept_words:
            out_parts.append(" ".join(kept_words))

    compressed = re.sub(r"\s+", " ", " ".join(out_parts)).strip()
    for lit in preserved_literals:
        if lit not in compressed:
            raise ContractViolation("K4", "caveman_invariant", f"littéral critique perdu lors de la compression: {lit}")

    orig_tokens = max(len(text.split()), 1)
    comp_tokens = len(compressed.split())
    reduction_pct = round((orig_tokens - comp_tokens) / orig_tokens * 100.0, 2)
    return {
        "schema": "aspace.caveman.compressed.v1",
        "kernel": "ÂME",
        "organ": "K4",
        "compressed_text": compressed,
        "original_words": orig_tokens,
        "compressed_words": comp_tokens,
        "reduction_pct": reduction_pct,
        "preserved_invariants": len(preserved_literals),
    }


# ===========================================================================
# 6. M063 claude-mem (ÂME / Organe K4)
# ===========================================================================

class SessionMemoryRecorder:
    """Capture continue d'observations inter-sessions avec ré-injection sous plafond de tokens."""

    def __init__(self, store_path: Path) -> None:
        self.store_path = store_path
        self.store_path.parent.mkdir(parents=True, exist_ok=True)

    def capture_observation(
        self,
        session_id: str,
        kind: str,
        fact: str,
        source_file: str,
        epistemic_status: str = "consigné",
    ) -> Dict[str, Any]:
        if not source_file.strip():
            raise ContractViolation("M2", "source_file", "claude-mem exige une source vérifiable")
        entry = {
            "session_id": session_id,
            "kind": kind,
            "fact": fact,
            "source_file": source_file,
            "epistemic_status": epistemic_status,
            "captured_at": dt.datetime.now(dt.timezone.utc).isoformat(),
            "tokens_est": len(fact.split()) + 4,
        }
        with open(self.store_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
        return entry

    def reinject_bounded_context(self, token_budget: int = 120) -> Dict[str, Any]:
        if not self.store_path.exists():
            return {"selected": [], "tokens_used": 0, "token_budget": token_budget}
        records = [
            json.loads(ln)
            for ln in self.store_path.read_text(encoding="utf-8").splitlines()
            if ln.strip()
        ]
        selected: List[Dict[str, Any]] = []
        used = 0
        # Ordre inverse : observations les plus récentes prioritaires sous plafond strict
        for rec in reversed(records):
            cost = int(rec.get("tokens_est", 10))
            if used + cost > token_budget:
                continue
            selected.append(rec)
            used += cost
        selected.reverse()
        return {
            "schema": "aspace.claude-mem.reinject.v1",
            "kernel": "ÂME",
            "organ": "K4",
            "token_budget": token_budget,
            "tokens_used": used,
            "selected_count": len(selected),
            "selected": selected,
        }


# ===========================================================================
# 7. M064 hermes-agent (ÂME / Organe K4)
# ===========================================================================

class HermesLearningLoop:
    """Recherche BM25 sur historique + compilateur `/learn` SKILL.md verrouillé par hold-out."""

    HOLDOUT_MIN_DELTA = 0.017

    @staticmethod
    def bm25_search(corpus: Sequence[Dict[str, Any]], query: str, top_k: int = 3) -> List[Dict[str, Any]]:
        docs_tokens = [re.findall(r"[a-zA-Z0-9_-]{2,}", str(doc.get("text", "")).lower()) for doc in corpus]
        q_terms = set(re.findall(r"[a-zA-Z0-9_-]{2,}", query.lower()))
        if not docs_tokens or not q_terms:
            return []
        n_docs = len(docs_tokens)
        avg_dl = sum(len(d) for d in docs_tokens) / max(n_docs, 1)
        k1, b = 1.5, 0.75

        scored = []
        for doc, tokens in zip(corpus, docs_tokens):
            dl = len(tokens)
            score = 0.0
            tf_map: Dict[str, int] = {}
            for t in tokens:
                tf_map[t] = tf_map.get(t, 0) + 1
            for qt in q_terms:
                df = sum(1 for dt_toks in docs_tokens if qt in dt_toks)
                if df == 0:
                    continue
                idf = math.log((n_docs - df + 0.5) / (df + 0.5) + 1.0)
                tf = tf_map.get(qt, 0)
                denom = tf + k1 * (1.0 - b + b * (dl / max(avg_dl, 1.0)))
                score += idf * ((tf * (k1 + 1.0)) / max(denom, 1e-9))
            if score > 0.0:
                scored.append({"id": doc.get("id"), "score": round(score, 4), "text": doc.get("text")})
        scored.sort(key=lambda x: x["score"], reverse=True)
        return scored[:top_k]

    @classmethod
    def compile_skill_from_trajectory(
        cls,
        skill_name: str,
        description: str,
        trajectory_steps: Sequence[str],
        holdout_delta: float,
    ) -> Dict[str, Any]:
        """Compile un SKILL.md OKF/AgentSkills si et seulement si `holdout_delta >= 0.017` (ADR-06)."""
        if holdout_delta < cls.HOLDOUT_MIN_DELTA:
            raise ContractViolation(
                "ADR-06",
                "holdout_delta",
                f"gain hold-out insuffisant ({holdout_delta:.4f} < {cls.HOLDOUT_MIN_DELTA}) — promotion skill refusée",
            )
        if not trajectory_steps:
            raise ContractViolation("K4", "trajectory_steps", "aucune étape de trajectoire fournie pour /learn")

        steps_md = "\n".join(f"{i}. {step}" for i, step in enumerate(trajectory_steps, 1))
        skill_md = (
            "---\n"
            f"name: {skill_name}\n"
            f'description: "{description}"\n'
            f"holdout_delta: {holdout_delta:.4f}\n"
            "---\n\n"
            f"# Skill `{skill_name}`\n\n"
            f"## Procédure Extraite (/learn)\n{steps_md}\n"
        )
        return {
            "schema": "aspace.hermes.skill.v1",
            "kernel": "ÂME",
            "organ": "K4",
            "promoted": True,
            "holdout_delta": holdout_delta,
            "skill_name": skill_name,
            "skill_markdown": skill_md,
        }


# ===========================================================================
# 8. M065 rea (CORPS / Organe K2)
# ===========================================================================

def clean_room_inspect_artifact(raw_bytes: bytes, label: str = "artifact.bin") -> Dict[str, Any]:
    """Inspection statique clean-room D12 : extrait endpoints, symboles et schémas sans copie source."""
    text = raw_bytes.decode("utf-8", errors="ignore")
    sha256 = hashlib.sha256(raw_bytes).hexdigest()
    ascii_strings = re.findall(r"[A-Za-z0-9_./:@?&=-]{5,}", text)
    endpoints = sorted({s for s in ascii_strings if s.startswith(("/v1/", "/api/", "https://", "http://127.0.0.1"))})
    exported_symbols = sorted(set(re.findall(r"(?:export\s+(?:async\s+)?(?:function|class|const)|def|pub\s+fn)\s+([A-Za-z_][A-Za-z0-9_]*)", text)))
    return {
        "schema": "aspace.rea.cleanroom-spec.v1",
        "kernel": "CORPS",
        "organ": "K2",
        "label": label,
        "sha256": sha256,
        "byte_size": len(raw_bytes),
        "clean_room_only": True,
        "endpoints_detected": endpoints[:50],
        "exported_symbols": exported_symbols[:50],
        "ascii_strings_count": len(ascii_strings),
    }


# ===========================================================================
# Suite de vérification des 8 modules FKB04 sans accès aux sources d'origine
# ===========================================================================

def run_fkb04_self_test(work_dir: Optional[Path] = None, head_sha40: str = "0" * 40) -> Dict[str, Any]:
    import tempfile

    ctx_mgr = tempfile.TemporaryDirectory(ignore_cleanup_errors=True) if work_dir is None else None
    base = Path(ctx_mgr.name) if ctx_mgr is not None else work_dir
    try:
        # 1. CLI-Anything (M058)
        cli_spec = compile_cli_anything_spec(
            "demo-tool",
            "Commands:\n  inspect  Inspect target artifact\nOptions:\n  --format <fmt>  Output format\n  --json  Emit JSON\n",
        )
        assert any(c["name"] == "inspect" for c in cli_spec["subcommands"])
        cli_res = execute_cli_structured(
            cli_spec,
            "inspect",
            {"format": "json", "json": True},
            runner=lambda argv: subprocess.CompletedProcess(argv, 0, '{"ok":true}', ""),
        )
        assert cli_res["ok"] and "--format" in cli_res["argv"]

        # 2. agent-browser (M059) — snapshot @ref + blocage strict CAPTCHA
        snap_ok = build_cdp_a11y_snapshot(
            [{"role": "button", "name": "Submit"}, {"role": "textbox", "name": "Query"}],
            url="http://127.0.0.1:31415/ui",
        )
        assert snap_ok["status"] == "READY" and "@e1" in snap_ok["refs"] and "@e2" in snap_ok["refs"]
        snap_blocked = build_cdp_a11y_snapshot([], url="https://example.org", page_text="Please solve reCAPTCHA to continue")
        assert snap_blocked["status"] == "BLOQUÉ"

        # 3. agent-desktop (M060)
        plan = plan_desktop_a11y_action(
            [{"ref": "@d1", "control_type": "Button", "name": "Save", "enabled": True}],
            target_ref="@d1",
            action="invoke",
            no_focus_steal=True,
        )
        assert plan["no_focus_steal"] is True

        # 4. api-anything (M061)
        har_spec = learn_api_from_har(
            [
                {
                    "request": {
                        "method": "POST",
                        "url": "https://api.example.org/v1/items/42/analyze",
                        "headers": [{"name": "Authorization", "value": "SECRET_TOKEN_SHOULD_STRIP"}],
                        "postData": {"text": '{"mode":"fast","count":3}'},
                    },
                    "response": {"content": {"text": '{"score":0.95,"ok":true}'}},
                }
            ]
        )
        op = har_spec["operations"][0]
        assert op["path_template"] == "/v1/items/{id_1}/analyze"
        assert "SECRET_TOKEN_SHOULD_STRIP" not in json.dumps(har_spec)

        # 5. caveman (M062)
        cav = compress_telegraphic(
            "Please likely note that your `aspace_foundation_kernel.py` file for sha 41889edb9c468ea62ee4641328c0e6f4bac2c618b81da751eebd2af4c05f648d would require review."
        )
        assert cav["reduction_pct"] > 15.0
        assert "41889edb9c468ea62ee4641328c0e6f4bac2c618b81da751eebd2af4c05f648d" in cav["compressed_text"]

        # 6. claude-mem (M063)
        mem_rec = SessionMemoryRecorder(base / "claude_mem_obs.jsonl")
        mem_rec.capture_observation("sess-1", "decision", "Verified fixture anchor-001", "fondation-13-1/tests/fixtures/anchor-001.json")
        mem_rec.capture_observation("sess-1", "decision", "Compiled FKB04 native organ", "aspace_fkb04_anything_organ.py")
        reinj = mem_rec.reinject_bounded_context(token_budget=40)
        assert reinj["tokens_used"] <= 40 and reinj["selected_count"] >= 1

        # 7. hermes-agent (M064)
        bm25_hits = HermesLearningLoop.bm25_search(
            [
                {"id": "d1", "text": "Rust cargo test fondation-13-1 passes all anchors"},
                {"id": "d2", "text": "Unrelated styling note CSS color"},
            ],
            "cargo test fondation",
        )
        assert bm25_hits and bm25_hits[0]["id"] == "d1"
        skill_ok = HermesLearningLoop.compile_skill_from_trajectory(
            "rust-lf-verify", "Verify Rust LF fixtures", ["Check .gitattributes", "Run cargo test"], holdout_delta=0.042
        )
        assert skill_ok["promoted"] is True
        try:
            HermesLearningLoop.compile_skill_from_trajectory("bad", "Too noisy", ["step"], holdout_delta=0.005)
            raise AssertionError("Rejet ADR-06 attendu sous le seuil hold-out 0.017")
        except ContractViolation as exc:
            assert exc.rule == "ADR-06"

        # 8. rea (M065)
        rea_spec = clean_room_inspect_artifact(
            b"export async function dispatchTask() { fetch('/v1/chat/completions'); }",
            label="mock_bundle.js",
        )
        assert "dispatchTask" in rea_spec["exported_symbols"] and "/v1/chat/completions" in rea_spec["endpoints_detected"]

        # Journal L0 + R10 en mémoire isolée (aligné fondation-13-1)
        now_dt = dt.datetime.now(dt.timezone.utc)
        day_tag = now_dt.strftime("%Y%m%d")
        j = EventJournal(signed_designs={"00_Memoire/bundle/fusion/SDD-FONDATION.md"})
        l = R10Ledger(valid_shas={head_sha40})
        evt = j.inscribe(
            {
                "actor_from": "fabricator",
                "actor_to": "judge",
                "at": now_dt.isoformat(),
                "design_ref": "00_Memoire/bundle/fusion/SDD-FONDATION.md",
                "dispatch_id": "D-FKB04-FUSION",
                "event_id": f"EVT-{day_tag}-904",
                "payload": "Prouver fusion 8 modules FKB04",
                "proof": ["01_Forkable/FKB00_Runtime/00_A0_Core/aspace_fkb04_anything_organ.py"],
                "type": "dispatch_typed",
            },
            now_utc=now_dt,
        )
        rec = l.validate_and_consign(
            {
                "entry_id": f"G-{day_tag}-904",
                "issuer": "Organ FKB04",
                "mission_id": "FKB04-NATIVE-FUSION-CHECK",
                "observed_at": now_dt.isoformat(),
                "proof": ["01_Forkable/FKB00_Runtime/00_A0_Core/aspace_fkb04_anything_organ.py"],
                "recorded_at": None,
                "schema": R10_SCHEMA,
                "sha": head_sha40,
                "summary": f"FKB04 8/8 capabilities verified at {head_sha40[:7]}",
            },
            now_utc=now_dt,
        )
        return {
            "organ": "aspace_fkb04_anything_organ",
            "modules_verified": 8,
            "l0_seq": evt["seq"],
            "r10_entry_id": rec["entry_id"],
        }
    finally:
        if ctx_mgr is not None:
            ctx_mgr.cleanup()


if __name__ == "__main__":
    print(json.dumps(run_fkb04_self_test(), indent=2, ensure_ascii=False))
