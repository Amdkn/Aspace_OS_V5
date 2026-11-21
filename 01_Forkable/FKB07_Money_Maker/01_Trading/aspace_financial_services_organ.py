#!/usr/bin/env python3
"""
aspace_financial_services_organ.py — Organe Natif FSI & Gouvernance Skills (CORPS / Organe K5).

Porte 1:1 sans perte les 4 sous-systèmes déterministes de `M071` (`financial-services`,
pin `4b7d7e5`, licence Apache-2.0) :
  1. DCFModelValidator (`validate_dcf.py`) — validation Excel DCF sous openpyxl,
  2. PitchDeckNumberExtractor (`extract_numbers.py`) — normalisation et cohérence chiffrée,
  3. FSICatalogAndSkillValidator (`check.py`, `validate.py`, `orchestrate.py::extract_handoff`,
     `version_bump.py`, `sync-agent-skills.py`, `quick_validate.py`, `init_skill.py`,
     `package_skill.py`),
  4. M365ManifestBuilder (`build-manifest.mjs`) — génération déterministe de manifestes XML M365,
raccordé au bus L0 (`fondation-13-1` / `aspace_foundation_kernel.py`) sous veto `READ_ONLY_VETO_S0`.
"""

from __future__ import annotations

import filecmp
import json
import re
import shutil
import sys
import urllib.parse
import zipfile
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple

import jsonschema
import yaml

_TRADING_DIR = Path(__file__).resolve().parent
WORKSPACE_ROOT = _TRADING_DIR.parents[2]
_CORE_DIR = WORKSPACE_ROOT / "01_Forkable" / "FKB00_Runtime" / "00_A0_Core"
if str(_CORE_DIR) not in sys.path:
    sys.path.insert(0, str(_CORE_DIR))

from aspace_foundation_kernel import (  # noqa: E402
    ContractViolation,
    consign_measured_l0_evidence,
)

# ===========================================================================
# Verrou S0 & Constantes M071
# ===========================================================================

READ_ONLY_VETO_S0 = True

EXCEL_FORMULA_ERRORS = ("#VALUE!", "#DIV/0!", "#REF!", "#NAME?", "#NULL!", "#NUM!", "#N/A")
REQUIRED_DCF_SHEETS = ("DCF", "WACC", "Sensitivity")

ALLOWED_HANDOFF_TARGETS = {
    "pitch-agent",
    "market-researcher",
    "earnings-reviewer",
    "meeting-prep-agent",
    "model-builder",
    "gl-reconciler",
    "kyc-screener",
    "valuation-reviewer",
    "month-end-closer",
    "statement-auditor",
}

HANDOFF_PAYLOAD_SCHEMA: Dict[str, Any] = {
    "type": "object",
    "additionalProperties": False,
    "required": ["event"],
    "properties": {
        "event": {"type": "string", "maxLength": 2000},
        "context_ref": {
            "type": "string",
            "maxLength": 256,
            "pattern": r"^[A-Za-z0-9 ._/:#-]+$",
        },
    },
}

HANDOFF_RE = re.compile(r'\{"type":\s*"handoff_request".*?\}', re.DOTALL)

ALLOWED_SKILL_FRONTMATTER_KEYS = {"name", "description", "license", "allowed-tools", "metadata"}
SKILL_NAME_MAX_LEN = 64
SKILL_DESCRIPTION_MAX_LEN = 1024

M365_MANIFESTS = {
    "office": "https://pivot.claude.ai/manifest.xml",
    "outlook": "https://pivot.claude.ai/manifest-outlook-3p.xml",
}

M365_URL_SLOTS = (
    re.compile(r'(<SourceLocation\s+DefaultValue=")([^"]+)(")'),
    re.compile(r'(id="Taskpane\.Url"\s+DefaultValue=")([^"]+)(")'),
)

M365_SENSITIVE_KEYS = {
    "gateway_token",
    "azure_api_key",
    "google_client_secret",
    "otlp_headers",
    "inference_headers",
    "mcp_servers",
}

M365_NEEDS_ENTRA = ("aws_role_arn", "graph_client_id", "entra_scope", "gateway_auth_source")
M365_EFFECTS = ("allow", "deny")
M365_RESOURCE_TYPES = ("open_file", "uploaded_file")
M365_STRING_OPS = ("equals", "startsWith", "endsWith")
M365_OPERATORS_BY_TYPE: Dict[str, Tuple[str, ...]] = {
    "mip_label_guid": ("equals", "exists"),
    "mip_label_name": ("equals", "startsWith", "endsWith", "exists"),
    "file_path": ("equals", "startsWith"),
}


class M365ManifestError(Exception):
    pass


# ===========================================================================
# 1. DCFModelValidator (validate_dcf.py)
# ===========================================================================


def evaluate_wacc_range(wacc: float) -> Dict[str, str]:
    """Vérifie les bornes 5%-20% d'un WACC scalaire."""
    if wacc < 0.05 or wacc > 0.20:
        return {
            "status": "WARN",
            "message": f"WACC ({wacc:.2%}) is outside typical range (5%-20%). Verify calculation.",
        }
    return {
        "status": "OK",
        "message": f"✓ WACC ({wacc:.2%}) in reasonable range",
    }


class DCFModelValidator:
    """Valide un classeur Excel DCF sur la parité stricte de `validate_dcf.py`."""

    def __init__(self, excel_path: str) -> None:
        try:
            import openpyxl
        except ImportError as exc:
            raise ImportError("openpyxl not installed. Run: pip install openpyxl") from exc

        self.excel_path = excel_path
        self.openpyxl = openpyxl

        if not Path(excel_path).exists():
            raise FileNotFoundError(f"File not found: {excel_path}")

        self.workbook_formulas = openpyxl.load_workbook(excel_path, data_only=False)
        self.workbook_values = openpyxl.load_workbook(excel_path, data_only=True)
        self.errors: List[str] = []
        self.warnings: List[str] = []
        self.info: List[str] = []

    def validate_all(self) -> Dict[str, Any]:
        self.check_sheet_structure()
        self.check_formula_errors()
        self.check_dcf_logic()
        return {
            "file": self.excel_path,
            "validation_date": datetime.now().isoformat(),
            "status": "PASS" if len(self.errors) == 0 else "FAIL",
            "error_count": len(self.errors),
            "warning_count": len(self.warnings),
            "errors": self.errors,
            "warnings": self.warnings,
            "info": self.info,
        }

    def check_sheet_structure(self) -> None:
        sheet_names = self.workbook_values.sheetnames
        for sheet in REQUIRED_DCF_SHEETS:
            if sheet not in sheet_names:
                self.warnings.append(f"Recommended sheet missing: {sheet}")
            else:
                self.info.append(f"Found sheet: {sheet}")

    def check_formula_errors(self) -> Tuple[Dict[str, List[str]], int]:
        error_details: Dict[str, List[str]] = {err: [] for err in EXCEL_FORMULA_ERRORS}
        total_errors = 0
        total_formulas = 0

        for sheet_name in self.workbook_values.sheetnames:
            ws_values = self.workbook_values[sheet_name]
            ws_formulas = self.workbook_formulas[sheet_name]

            for row in ws_values.iter_rows():
                for cell in row:
                    formula_cell = ws_formulas[cell.coordinate]
                    if formula_cell.value and isinstance(formula_cell.value, str) and formula_cell.value.startswith("="):
                        total_formulas += 1

                    if cell.value is not None and isinstance(cell.value, str):
                        for err in EXCEL_FORMULA_ERRORS:
                            if err in cell.value:
                                location = f"{sheet_name}!{cell.coordinate}"
                                error_details[err].append(location)
                                total_errors += 1
                                self.errors.append(f"{err} at {location}")
                                break

        self.info.append(f"Total formulas: {total_formulas}")
        if total_errors == 0:
            self.info.append("✓ No formula errors found")
        else:
            self.errors.append(f"Total formula errors: {total_errors}")
        return error_details, total_errors

    def check_dcf_logic(self) -> None:
        self._check_terminal_growth_vs_wacc()
        self._check_wacc_range()
        self._check_terminal_value_proportion()

    def _check_terminal_growth_vs_wacc(self) -> None:
        try:
            dcf_sheet = self.workbook_values["DCF"]
            terminal_growth = None
            wacc = None

            for row in dcf_sheet.iter_rows(max_row=100, max_col=20):
                for cell in row:
                    if cell.value and isinstance(cell.value, str):
                        cell_str = cell.value.lower()
                        if "terminal" in cell_str and "growth" in cell_str:
                            for offset in range(1, 5):
                                adjacent = dcf_sheet.cell(cell.row, cell.column + offset).value
                                if isinstance(adjacent, (int, float)) and 0 < adjacent < 1:
                                    terminal_growth = adjacent
                                    break
                        if "wacc" in cell_str and wacc is None:
                            for offset in range(1, 5):
                                adjacent = dcf_sheet.cell(cell.row, cell.column + offset).value
                                if isinstance(adjacent, (int, float)) and 0 < adjacent < 1:
                                    wacc = adjacent
                                    break

            if terminal_growth is not None and wacc is not None:
                if terminal_growth >= wacc:
                    self.errors.append(
                        f"CRITICAL: Terminal growth ({terminal_growth:.2%}) >= WACC ({wacc:.2%}). "
                        "This creates infinite value and is mathematically invalid."
                    )
                else:
                    self.info.append(f"✓ Terminal growth ({terminal_growth:.2%}) < WACC ({wacc:.2%})")
            else:
                self.warnings.append("Could not locate terminal growth and WACC values")
        except KeyError:
            self.warnings.append("DCF sheet not found")
        except Exception as exc:
            self.warnings.append(f"Could not validate terminal growth vs WACC: {str(exc)}")

    def _check_wacc_range(self) -> None:
        # Préserve 1:1 le comportement amont exact de validate_dcf.py:163 (`Workbook.get('WACC')` -> warning).
        try:
            wacc_sheet = self.workbook_values.get("WACC") or self.workbook_values["DCF"]  # type: ignore[attr-defined]
            wacc = None

            for row in wacc_sheet.iter_rows(max_row=100, max_col=20):
                for cell in row:
                    if cell.value and isinstance(cell.value, str):
                        if "wacc" in cell.value.lower():
                            for offset in range(1, 5):
                                adjacent = wacc_sheet.cell(cell.row, cell.column + offset).value
                                if isinstance(adjacent, (int, float)) and 0 < adjacent < 1:
                                    wacc = adjacent
                                    break

            if wacc is not None:
                evaluated = evaluate_wacc_range(float(wacc))
                if evaluated["status"] == "WARN":
                    self.warnings.append(evaluated["message"])
                else:
                    self.info.append(evaluated["message"])
            else:
                self.warnings.append("Could not locate WACC value")
        except Exception as exc:
            self.warnings.append(f"Could not validate WACC range: {str(exc)}")

    def _check_terminal_value_proportion(self) -> None:
        try:
            dcf_sheet = self.workbook_values["DCF"]
            terminal_value = None
            enterprise_value = None

            for row in dcf_sheet.iter_rows(max_row=200, max_col=20):
                for cell in row:
                    if cell.value and isinstance(cell.value, str):
                        cell_str = cell.value.lower()
                        if "terminal" in cell_str and "value" in cell_str and "pv" in cell_str:
                            for offset in range(1, 5):
                                adjacent = dcf_sheet.cell(cell.row, cell.column + offset).value
                                if isinstance(adjacent, (int, float)) and adjacent > 0:
                                    terminal_value = adjacent
                                    break
                        if "enterprise" in cell_str and "value" in cell_str:
                            for offset in range(1, 5):
                                adjacent = dcf_sheet.cell(cell.row, cell.column + offset).value
                                if isinstance(adjacent, (int, float)) and adjacent > 0:
                                    enterprise_value = adjacent
                                    break

            if terminal_value is not None and enterprise_value is not None and enterprise_value > 0:
                proportion = terminal_value / enterprise_value
                if proportion > 0.80:
                    self.warnings.append(
                        f"Terminal value is {proportion:.1%} of EV (typically should be 50-70%). "
                        "Model may be over-reliant on terminal assumptions."
                    )
                elif proportion < 0.40:
                    self.warnings.append(
                        f"Terminal value is {proportion:.1%} of EV (typically should be 50-70%). "
                        "Check if terminal assumptions are too conservative."
                    )
                else:
                    self.info.append(f"✓ Terminal value is {proportion:.1%} of EV")
            else:
                self.warnings.append("Could not locate terminal value and enterprise value")
        except Exception as exc:
            self.warnings.append(f"Could not validate terminal value proportion: {str(exc)}")


def validate_dcf_model(excel_path: str) -> Dict[str, Any]:
    validator = DCFModelValidator(excel_path)
    return validator.validate_all()


# ===========================================================================
# 2. PitchDeckNumberExtractor (extract_numbers.py)
# ===========================================================================


@dataclass
class NumberInstance:
    value: str
    normalized: float
    unit: str
    slide: int
    context: str
    line_number: int
    category: str


def normalize_number(value_str: str, unit: str) -> float:
    clean = re.sub(r"[,\s]", "", value_str)
    try:
        base_value = float(clean)
    except ValueError:
        return 0.0

    multipliers = {
        "T": 1e12,
        "B": 1e9,
        "bn": 1e9,
        "billion": 1e9,
        "M": 1e6,
        "mm": 1e6,
        "mn": 1e6,
        "million": 1e6,
        "K": 1e3,
        "k": 1e3,
        "thousand": 1e3,
    }
    for unit_key in sorted(multipliers.keys(), key=len, reverse=True):
        if unit_key.lower() in unit.lower():
            return base_value * multipliers[unit_key]
    return base_value


def detect_category(context: str, unit: str) -> str:
    context_lower = context.lower()
    if any(term in context_lower for term in ("revenue", "sales", "top line", "topline")):
        return "revenue"
    if "ebitda" in context_lower:
        if any(term in context_lower for term in ("margin", "%", "percent")):
            return "ebitda_margin"
        return "ebitda"
    if any(term in context_lower for term in ("margin", "profit")):
        return "margin"
    if any(term in context_lower for term in ("growth", "cagr", "yoy", "y/y")):
        return "growth"
    if any(term in context_lower for term in ("multiple", "ev/", "p/e", "ev/ebitda", "ev/revenue")):
        return "multiple"
    if any(term in context_lower for term in ("enterprise value", "ev ", "market cap")):
        return "valuation"
    if unit in ("%", "bps", "percent"):
        return "percentage"
    if unit == "x":
        return "multiple"
    return "other"


_SLIDE_PATTERN = re.compile(r"^#+\s*Slide\s*(\d+)|^<!-- Slide (\d+)")
_NUMBER_PATTERN = re.compile(
    r"(?P<currency>[$€£¥])?"
    r"(?P<number>[\d,]+(?:\.\d+)?)"
    r"\s*"
    r"(?P<unit>%|bps|x|"
    r"[Tt]rillion|[Bb]illion|[Mm]illion|[Tt]housand|"
    r"[TBMKtbmk]n?|mm|MM)?"
    r"(?!\d)"
)


def extract_numbers(content: str) -> List[NumberInstance]:
    numbers: List[NumberInstance] = []
    current_slide = 0

    for line_num, line in enumerate(content.split("\n"), 1):
        slide_match = _SLIDE_PATTERN.match(line)
        if slide_match:
            current_slide = int(slide_match.group(1) or slide_match.group(2))
            continue

        for match in _NUMBER_PATTERN.finditer(line):
            value_str = match.group("number")
            currency = match.group("currency") or ""
            unit = match.group("unit") or ""

            if len(value_str.replace(",", "").replace(".", "")) < 2 and not unit:
                continue

            try:
                num_val = float(value_str.replace(",", ""))
                if 1900 <= num_val <= 2099 and not unit and not currency:
                    continue
            except ValueError:
                pass

            full_value = f"{currency}{value_str}{unit}"
            start = max(0, match.start() - 50)
            end = min(len(line), match.end() + 50)
            context = line[start:end].strip()

            if currency:
                unit = "USD" if not unit else f"USD_{unit}"

            normalized = normalize_number(value_str, unit)
            category = detect_category(context, unit)
            numbers.append(
                NumberInstance(
                    value=full_value,
                    normalized=normalized,
                    unit=unit or "none",
                    slide=current_slide,
                    context=context,
                    line_number=line_num,
                    category=category,
                )
            )
    return numbers


def find_inconsistencies(numbers: Sequence[NumberInstance]) -> List[Dict[str, Any]]:
    inconsistencies: List[Dict[str, Any]] = []
    by_category: Dict[str, List[NumberInstance]] = {}
    for num in numbers:
        if num.category != "other":
            by_category.setdefault(num.category, []).append(num)

    for category, instances in by_category.items():
        if len(instances) < 2:
            continue
        value_groups: List[List[NumberInstance]] = []
        for inst in instances:
            placed = False
            for group in value_groups:
                ref_value = group[0].normalized
                if ref_value > 0:
                    diff_pct = abs(inst.normalized - ref_value) / ref_value
                    if diff_pct < 0.05:
                        group.append(inst)
                        placed = True
                        break
            if not placed:
                value_groups.append([inst])

        if len(value_groups) > 1:
            value_groups.sort(key=len, reverse=True)
            main_group = value_groups[0]
            for other_group in value_groups[1:]:
                inconsistencies.append(
                    {
                        "category": category,
                        "expected": {
                            "value": main_group[0].value,
                            "slides": sorted(set(n.slide for n in main_group)),
                            "count": len(main_group),
                        },
                        "found": {
                            "value": other_group[0].value,
                            "slides": sorted(set(n.slide for n in other_group)),
                            "count": len(other_group),
                        },
                        "severity": "high" if category in ("revenue", "ebitda", "valuation") else "medium",
                    }
                )
    return inconsistencies


def analyze_presentation_numbers(content: str, *, check: bool = False) -> Dict[str, Any]:
    numbers = extract_numbers(content)
    by_category: Dict[str, List[Dict[str, Any]]] = {}
    for num in numbers:
        by_category.setdefault(num.category, []).append(
            {
                "value": num.value,
                "slide": num.slide,
                "context": num.context[:100],
            }
        )
    out: Dict[str, Any] = {
        "total_numbers": len(numbers),
        "by_category": by_category,
        "numbers": [asdict(n) for n in numbers],
    }
    if check:
        out["inconsistencies"] = find_inconsistencies(numbers)
    return out


# ===========================================================================
# 3. FSICatalogAndSkillValidator (`check.py`, `validate.py`, `orchestrate.py`,
#    `version_bump.py`, `sync-agent-skills.py`, `skill-creator/scripts/*`)
# ===========================================================================


def lint_fsi_catalog(root: Path) -> Dict[str, Any]:
    """Port 1:1 des 6 contrôles de `scripts/check.py` (zéro écriture `.git/config`)."""
    root = Path(root)
    plugins = root / "plugins"
    managed = root / "managed-agent-cookbooks"
    errors: List[str] = []
    checked = 0

    def _rel(p: Path) -> str:
        return str(p.relative_to(root))

    # 1. YAML parse under managed-agent-cookbooks/
    for yml in sorted(managed.rglob("*.yaml")):
        checked += 1
        try:
            with yml.open(encoding="utf-8") as _fh:
                yaml.safe_load(_fh)
        except yaml.YAMLError as exc:
            errors.append(f"YAML parse: {_rel(yml)}: {exc}")

    # 2. JSON parse
    json_globs = (
        ".claude-plugin/marketplace.json",
        "plugins/**/.claude-plugin/plugin.json",
        "managed-agent-cookbooks/*/steering-examples.json",
    )
    for pat in json_globs:
        for jf in sorted(root.glob(pat)):
            checked += 1
            try:
                json.loads(jf.read_text(encoding="utf-8"))
            except json.JSONDecodeError as exc:
                errors.append(f"JSON parse: {_rel(jf)}: {exc}")

    # 3. agent.md frontmatter
    for md in sorted(plugins.glob("agent-plugins/*/agents/*.md")):
        checked += 1
        text = md.read_text(encoding="utf-8")
        if not text.startswith("---"):
            errors.append(f"frontmatter: {_rel(md)}: missing leading ---")
            continue
        try:
            _, fm, _ = text.split("---", 2)
            meta = yaml.safe_load(fm)
            for k in ("name", "description"):
                if not isinstance(meta, dict) or k not in meta:
                    errors.append(f"frontmatter: {_rel(md)}: missing '{k}'")
        except (ValueError, yaml.YAMLError) as exc:
            errors.append(f"frontmatter: {_rel(md)}: {exc}")

    # 4. reference resolution
    for yml in sorted(managed.rglob("*.yaml")):
        try:
            with yml.open(encoding="utf-8") as _fh:
                data = yaml.safe_load(_fh) or {}
        except yaml.YAMLError:
            continue
        base = yml.parent
        sys_spec = data.get("system")
        if isinstance(sys_spec, dict) and "file" in sys_spec:
            p = (base / sys_spec["file"]).resolve()
            if not p.is_file():
                errors.append(f"ref: {_rel(yml)}: system.file -> {sys_spec['file']} (not found)")
        for s in data.get("skills") or []:
            if isinstance(s, dict) and "path" in s:
                p = (base / s["path"]).resolve()
                if not p.exists():
                    errors.append(f"ref: {_rel(yml)}: skills.path -> {s['path']} (not found)")
            if isinstance(s, dict) and "from_plugin" in s:
                p = (base / s["from_plugin"]).resolve()
                if not (p / "skills").is_dir():
                    errors.append(f"ref: {_rel(yml)}: skills.from_plugin -> {s['from_plugin']} (no skills/ dir)")
        for c in data.get("callable_agents") or []:
            if isinstance(c, dict) and "manifest" in c:
                p = (base / c["manifest"]).resolve()
                if not p.is_file():
                    errors.append(f"ref: {_rel(yml)}: callable_agents.manifest -> {c['manifest']} (not found)")

    # 4b. bundled skills vs vertical-plugins
    src_by_name = {p.name: p for p in plugins.glob("vertical-plugins/*/skills/*") if p.is_dir()}
    for bundled in sorted(plugins.glob("agent-plugins/*/skills/*")):
        if not bundled.is_dir():
            continue
        src = src_by_name.get(bundled.name)
        if not src:
            errors.append(f"bundled-skill: {_rel(bundled)}: no vertical-plugins source named '{bundled.name}'")
            continue
        cmp = filecmp.dircmp(src, bundled)
        if cmp.diff_files or cmp.left_only or cmp.right_only:
            errors.append(
                f"bundled-skill: {_rel(bundled)}: drifted from {_rel(src)} "
                "(run scripts/sync-agent-skills.py)"
            )

    # 4b2. agent prose backtick skill references
    for md in sorted(plugins.glob("agent-plugins/*/agents/*.md")):
        slug = md.parents[1].name
        sk_dir = plugins / "agent-plugins" / slug / "skills"
        bundle = {p.name for p in sk_dir.iterdir() if p.is_dir()} if sk_dir.is_dir() else set()
        for ref in sorted(set(re.findall(r"`([a-z0-9]+(?:-[a-z0-9]+)+)`", md.read_text(encoding="utf-8")))):
            if ref in src_by_name and ref not in bundle:
                errors.append(
                    f"agent-prose: {_rel(md)}: references `{ref}` but "
                    f"plugins/agent-plugins/{slug}/skills/{ref}/ is not bundled"
                )

    # 4c. marketplace source paths resolve
    mp = root / ".claude-plugin" / "marketplace.json"
    if mp.exists():
        for p_entry in json.loads(mp.read_text(encoding="utf-8")).get("plugins", []):
            src_p = (root / p_entry["source"]).resolve()
            if not (src_p / ".claude-plugin" / "plugin.json").is_file():
                errors.append(f"marketplace: {p_entry['name']} source -> {p_entry['source']} (no plugin.json)")

    # 5. required files per managed-agent
    if managed.is_dir():
        for d in sorted(managed.iterdir()):
            if not d.is_dir():
                continue
            for req in ("agent.yaml", "README.md", "steering-examples.json"):
                if not (d / req).is_file():
                    errors.append(f"missing: {_rel(d)}/{req}")

    # 6. PowerShell scripts pure ASCII (unless UTF-8 BOM)
    for ps in sorted(root.rglob("*.ps1")):
        if any(part in {".git", "node_modules"} for part in ps.parts):
            continue
        checked += 1
        raw = ps.read_bytes()
        if raw.startswith(b"\xef\xbb\xbf"):
            continue
        for lineno, line in enumerate(raw.split(b"\n"), 1):
            bad = sorted({b for b in line if b > 0x7F})
            if bad:
                chars = ", ".join(f"0x{b:02x}" for b in bad[:5])
                errors.append(
                    f"non-ascii: {_rel(ps)}:{lineno}: byte(s) {chars} in a .ps1 with no "
                    "UTF-8 BOM -- Windows PowerShell 5.1 will mis-decode this and may "
                    "fail to parse the file. Use ASCII (-- for an em dash) or add a BOM."
                )
                break

    return {
        "ok": len(errors) == 0,
        "checked": checked,
        "errors": errors,
    }


def validate_json_schema(instance: Any, schema: Any) -> Tuple[bool, str]:
    try:
        jsonschema.validate(instance=instance, schema=schema)
    except jsonschema.ValidationError as exc:
        return False, f"INVALID: {exc.message} at {'/'.join(str(p) for p in exc.absolute_path)}"
    return True, "OK"


def extract_handoff(text: str) -> Optional[Dict[str, Any]]:
    m = HANDOFF_RE.search(text)
    if not m:
        return None
    try:
        obj = json.loads(m.group(0))
    except json.JSONDecodeError:
        return None
    target = obj.get("target_agent")
    payload = obj.get("payload")
    if target not in ALLOWED_HANDOFF_TARGETS:
        return None
    try:
        jsonschema.validate(instance=payload, schema=HANDOFF_PAYLOAD_SCHEMA)
    except jsonschema.ValidationError:
        return None
    return {"target_agent": target, "payload": payload}


def parse_semver(v: str) -> Optional[Tuple[int, int, int]]:
    parts = (v or "").split(".")
    if len(parts) != 3:
        return None
    try:
        vals = tuple(int(x) for x in parts)
    except ValueError:
        return None
    return (vals[0], vals[1], vals[2])


def patch_bump(v: str) -> str:
    sv = parse_semver(v)
    if sv is None:
        return "0.0.1"
    return f"{sv[0]}.{sv[1]}.{sv[2] + 1}"


def is_ahead(work: Optional[str], base: Optional[str]) -> bool:
    if base is None:
        return True
    wv, bv = parse_semver(work or ""), parse_semver(base)
    if wv is None or bv is None:
        return (work or "") != base
    return wv > bv


def sync_agent_skills(root: Path) -> Tuple[int, List[str]]:
    root = Path(root)
    agents = root / "plugins" / "agent-plugins"
    verticals = root / "plugins" / "vertical-plugins"

    src_by_name: Dict[str, Path] = {}
    for sk in verticals.glob("*/skills/*"):
        if sk.is_dir():
            src_by_name[sk.name] = sk

    synced = 0
    missing: List[str] = []
    for bundled in sorted(agents.glob("*/skills/*")):
        if not bundled.is_dir():
            continue
        src = src_by_name.get(bundled.name)
        if not src:
            missing.append(str(bundled.relative_to(root)))
            continue
        shutil.rmtree(bundled)
        shutil.copytree(src, bundled)
        synced += 1
    return synced, missing


def validate_skill(skill_path: Path | str) -> Tuple[bool, str]:
    skill_dir = Path(skill_path)
    skill_md = skill_dir / "SKILL.md"
    if not skill_md.exists():
        return False, "SKILL.md not found"

    content = skill_md.read_text(encoding="utf-8")
    if not content.startswith("---"):
        return False, "No YAML frontmatter found"

    match = re.match(r"^---\n(.*?)\n---", content, re.DOTALL)
    if not match:
        return False, "Invalid frontmatter format"

    frontmatter_text = match.group(1)
    try:
        frontmatter = yaml.safe_load(frontmatter_text)
        if not isinstance(frontmatter, dict):
            return False, "Frontmatter must be a YAML dictionary"
    except yaml.YAMLError as exc:
        return False, f"Invalid YAML in frontmatter: {exc}"

    unexpected_keys = set(frontmatter.keys()) - ALLOWED_SKILL_FRONTMATTER_KEYS
    if unexpected_keys:
        return False, (
            f"Unexpected key(s) in SKILL.md frontmatter: {', '.join(sorted(unexpected_keys))}. "
            f"Allowed properties are: {', '.join(sorted(ALLOWED_SKILL_FRONTMATTER_KEYS))}"
        )

    if "name" not in frontmatter:
        return False, "Missing 'name' in frontmatter"
    if "description" not in frontmatter:
        return False, "Missing 'description' in frontmatter"

    name = frontmatter.get("name", "")
    if not isinstance(name, str):
        return False, f"Name must be a string, got {type(name).__name__}"
    name = name.strip()
    if name:
        if not re.match(r"^[a-z0-9-]+$", name):
            return False, f"Name '{name}' should be hyphen-case (lowercase letters, digits, and hyphens only)"
        if name.startswith("-") or name.endswith("-") or "--" in name:
            return False, f"Name '{name}' cannot start/end with hyphen or contain consecutive hyphens"
        if len(name) > SKILL_NAME_MAX_LEN:
            return False, f"Name is too long ({len(name)} characters). Maximum is {SKILL_NAME_MAX_LEN} characters."

    description = frontmatter.get("description", "")
    if not isinstance(description, str):
        return False, f"Description must be a string, got {type(description).__name__}"
    description = description.strip()
    if description:
        if "<" in description or ">" in description:
            return False, "Description cannot contain angle brackets (< or >)"
        if len(description) > SKILL_DESCRIPTION_MAX_LEN:
            return False, (
                f"Description is too long ({len(description)} characters). "
                f"Maximum is {SKILL_DESCRIPTION_MAX_LEN} characters."
            )

    return True, "Skill is valid!"


def title_case_skill_name(skill_name: str) -> str:
    return " ".join(word.capitalize() for word in skill_name.split("-"))


SKILL_TEMPLATE = '---\nname: {skill_name}\ndescription: [TODO: Complete and informative explanation of what the skill does and when to use it. Include WHEN to use this skill - specific scenarios, file types, or tasks that trigger it.]\n---\n\n# {skill_title}\n\n## Overview\n\n[TODO: 1-2 sentences explaining what this skill enables]\n\n## Structuring This Skill\n\n[TODO: Choose the structure that best fits this skill\'s purpose. Common patterns:\n\n**1. Workflow-Based** (best for sequential processes)\n- Works well when there are clear step-by-step procedures\n- Example: DOCX skill with "Workflow Decision Tree" → "Reading" → "Creating" → "Editing"\n- Structure: ## Overview → ## Workflow Decision Tree → ## Step 1 → ## Step 2...\n\n**2. Task-Based** (best for tool collections)\n- Works well when the skill offers different operations/capabilities\n- Example: PDF skill with "Quick Start" → "Merge PDFs" → "Split PDFs" → "Extract Text"\n- Structure: ## Overview → ## Quick Start → ## Task Category 1 → ## Task Category 2...\n\n**3. Reference/Guidelines** (best for standards or specifications)\n- Works well for brand guidelines, coding standards, or requirements\n- Example: Brand styling with "Brand Guidelines" → "Colors" → "Typography" → "Features"\n- Structure: ## Overview → ## Guidelines → ## Specifications → ## Usage...\n\n**4. Capabilities-Based** (best for integrated systems)\n- Works well when the skill provides multiple interrelated features\n- Example: Product Management with "Core Capabilities" → numbered capability list\n- Structure: ## Overview → ## Core Capabilities → ### 1. Feature → ### 2. Feature...\n\nPatterns can be mixed and matched as needed. Most skills combine patterns (e.g., start with task-based, add workflow for complex operations).\n\nDelete this entire "Structuring This Skill" section when done - it\'s just guidance.]\n\n## [TODO: Replace with the first main section based on chosen structure]\n\n[TODO: Add content here. See examples in existing skills:\n- Code samples for technical skills\n- Decision trees for complex workflows\n- Concrete examples with realistic user requests\n- References to scripts/templates/references as needed]\n\n## Resources\n\nThis skill includes example resource directories that demonstrate how to organize different types of bundled resources:\n\n### scripts/\nExecutable code (Python/Bash/etc.) that can be run directly to perform specific operations.\n\n**Examples from other skills:**\n- PDF skill: `fill_fillable_fields.py`, `extract_form_field_info.py` - utilities for PDF manipulation\n- DOCX skill: `document.py`, `utilities.py` - Python modules for document processing\n\n**Appropriate for:** Python scripts, shell scripts, or any executable code that performs automation, data processing, or specific operations.\n\n**Note:** Scripts may be executed without loading into context, but can still be read by Claude for patching or environment adjustments.\n\n### references/\nDocumentation and reference material intended to be loaded into context to inform Claude\'s process and thinking.\n\n**Examples from other skills:**\n- Product management: `communication.md`, `context_building.md` - detailed workflow guides\n- BigQuery: API reference documentation and query examples\n- Finance: Schema documentation, company policies\n\n**Appropriate for:** In-depth documentation, API references, database schemas, comprehensive guides, or any detailed information that Claude should reference while working.\n\n### assets/\nFiles not intended to be loaded into context, but rather used within the output Claude produces.\n\n**Examples from other skills:**\n- Brand styling: PowerPoint template files (.pptx), logo files\n- Frontend builder: HTML/React boilerplate project directories\n- Typography: Font files (.ttf, .woff2)\n\n**Appropriate for:** Templates, boilerplate code, document templates, images, icons, fonts, or any files meant to be copied or used in the final output.\n\n---\n\n**Any unneeded directories can be deleted.** Not every skill requires all three types of resources.\n'
EXAMPLE_SCRIPT = '#!/usr/bin/env python3\n"""\nExample helper script for {skill_name}\n\nThis is a placeholder script that can be executed directly.\nReplace with actual implementation or delete if not needed.\n\nExample real scripts from other skills:\n- pdf/scripts/fill_fillable_fields.py - Fills PDF form fields\n- pdf/scripts/convert_pdf_to_images.py - Converts PDF pages to images\n"""\n\ndef main():\n    print("This is an example script for {skill_name}")\n    # TODO: Add actual script logic here\n    # This could be data processing, file conversion, API calls, etc.\n\nif __name__ == "__main__":\n    main()\n'
EXAMPLE_REFERENCE = "# Reference Documentation for {skill_title}\n\nThis is a placeholder for detailed reference documentation.\nReplace with actual reference content or delete if not needed.\n\nExample real reference docs from other skills:\n- product-management/references/communication.md - Comprehensive guide for status updates\n- product-management/references/context_building.md - Deep-dive on gathering context\n- bigquery/references/ - API references and query examples\n\n## When Reference Docs Are Useful\n\nReference docs are ideal for:\n- Comprehensive API documentation\n- Detailed workflow guides\n- Complex multi-step processes\n- Information too lengthy for main SKILL.md\n- Content that's only needed for specific use cases\n\n## Structure Suggestions\n\n### API Reference Example\n- Overview\n- Authentication\n- Endpoints with examples\n- Error codes\n- Rate limits\n\n### Workflow Guide Example\n- Prerequisites\n- Step-by-step instructions\n- Common patterns\n- Troubleshooting\n- Best practices\n"
EXAMPLE_ASSET = '# Example Asset File\n\nThis placeholder represents where asset files would be stored.\nReplace with actual asset files (templates, images, fonts, etc.) or delete if not needed.\n\nAsset files are NOT intended to be loaded into context, but rather used within\nthe output Claude produces.\n\nExample asset files from other skills:\n- Brand guidelines: logo.png, slides_template.pptx\n- Frontend builder: hello-world/ directory with HTML/React boilerplate\n- Typography: custom-font.ttf, font-family.woff2\n- Data: sample_data.csv, test_dataset.json\n\n## Common Asset Types\n\n- Templates: .pptx, .docx, boilerplate directories\n- Images: .png, .jpg, .svg, .gif\n- Fonts: .ttf, .otf, .woff, .woff2\n- Boilerplate code: Project directories, starter files\n- Icons: .ico, .svg\n- Data files: .csv, .json, .xml, .yaml\n\nNote: This is a text placeholder. Actual assets can be any file type.\n'


def init_skill(skill_name: str, path: Path | str) -> Optional[Path]:
    skill_dir = Path(path).resolve() / skill_name
    if skill_dir.exists():
        return None
    skill_dir.mkdir(parents=True, exist_ok=False)
    skill_title = title_case_skill_name(skill_name)
    skill_md = SKILL_TEMPLATE.format(skill_name=skill_name, skill_title=skill_title)
    (skill_dir / "SKILL.md").write_text(skill_md, encoding="utf-8")
    scripts_dir = skill_dir / "scripts"
    scripts_dir.mkdir(exist_ok=True)
    example_script = scripts_dir / "example.py"
    example_script.write_text(EXAMPLE_SCRIPT.format(skill_name=skill_name), encoding="utf-8")
    example_script.chmod(0o755)
    refs_dir = skill_dir / "references"
    refs_dir.mkdir(exist_ok=True)
    (refs_dir / "api_reference.md").write_text(EXAMPLE_REFERENCE.format(skill_title=skill_title), encoding="utf-8")
    assets_dir = skill_dir / "assets"
    assets_dir.mkdir(exist_ok=True)
    (assets_dir / "example_asset.txt").write_text(EXAMPLE_ASSET, encoding="utf-8")
    return skill_dir


def package_skill(skill_path: Path | str, output_dir: Optional[Path | str] = None) -> Optional[Path]:
    skill_dir = Path(skill_path).resolve()
    if not skill_dir.exists() or not skill_dir.is_dir():
        return None
    if not (skill_dir / "SKILL.md").exists():
        return None
    valid, _msg = validate_skill(skill_dir)
    if not valid:
        return None
    out_dir = Path(output_dir).resolve() if output_dir else Path.cwd()
    out_dir.mkdir(parents=True, exist_ok=True)
    out_file = out_dir / f"{skill_dir.name}.skill"
    with zipfile.ZipFile(out_file, "w", zipfile.ZIP_DEFLATED) as zf:
        for fp in sorted(skill_dir.rglob("*")):
            if fp.is_file():
                zf.write(fp, fp.relative_to(skill_dir.parent))
    return out_file


# ===========================================================================
# 4. M365ManifestBuilder (`build-manifest.mjs`)
# ===========================================================================


def _js_urlencode(pairs: Sequence[Tuple[str, str]]) -> str:
    def _enc(s: str) -> str:
        return urllib.parse.quote_plus(s, safe="*-._").replace("~", "%7E")

    return "&".join(f"{_enc(k)}={_enc(v)}" for k, v in pairs)


def m365_validate_identifier(ident: Any, at: str) -> List[str]:
    if not isinstance(ident, dict):
        return [f"{at}: expected an object"]
    problems: List[str] = []
    itype = ident.get("type")
    allowed = M365_OPERATORS_BY_TYPE.get(itype) if isinstance(itype, str) else None
    if not allowed:
        problems.append(f"{at}.type: expected {' | '.join(M365_OPERATORS_BY_TYPE.keys())}")
    ops = [op for op in M365_STRING_OPS if op in ident] + (["exists"] if "exists" in ident else [])
    if len(ops) != 1:
        problems.append(f"{at}: expected exactly one operator (equals | startsWith | endsWith | exists), got {len(ops)}")
        return problems
    op = ops[0]
    if allowed and op not in allowed:
        problems.append(f"{at}: {itype} does not support {op} (only {' | '.join(allowed)})")
    else:
        val = ident.get(op)
        if op == "exists":
            if not isinstance(val, bool):
                problems.append(f"{at}.{op}: expected a boolean")
        elif not isinstance(val, str) or not val.strip():
            problems.append(f"{at}.{op}: expected a non-empty string")
    return problems


def m365_validate_statement(st: Any, at: str) -> List[str]:
    if not isinstance(st, dict):
        return [f"{at}: expected an object"]
    problems: List[str] = []
    if st.get("effect") not in M365_EFFECTS:
        problems.append(f'{at}.effect: expected "allow" or "deny"')
    act = st.get("action")
    slugs = act if isinstance(act, list) else [act]
    action_ok = len(slugs) > 0 and all(isinstance(a, str) and bool(a.strip()) for a in slugs)
    if not action_ok:
        problems.append(f"{at}.action: expected a non-empty slug string or array of them")
    if "resource" in st and st["resource"] is not None:
        r = st["resource"]
        if not isinstance(r, dict):
            return problems + [f"{at}.resource: expected an object"]
        if r.get("type") not in M365_RESOURCE_TYPES:
            problems.append(f"{at}.resource.type: expected {' | '.join(M365_RESOURCE_TYPES)}")
        if "description" in r and r["description"] is not None and not isinstance(r["description"], str):
            problems.append(f"{at}.resource.description: expected a string")
        idents = r.get("identifiers")
        if not isinstance(idents, list):
            problems.append(f"{at}.resource.identifiers: expected an array")
        elif len(idents) == 0:
            problems.append(
                f"{at}.resource.identifiers: empty — the statement will never match; drop `resource` to apply everywhere"
            )
        else:
            for j, ident in enumerate(idents):
                problems.extend(m365_validate_identifier(ident, f"{at}.resource.identifiers[{j}]"))
            if r.get("type") == "uploaded_file" and any(
                isinstance(ident, dict) and ident.get("type") == "file_path" for ident in idents
            ):
                problems.append(
                    f"{at}.resource: file_path never matches an uploaded_file (uploads have no path) — use open_file"
                )
    elif "resource" in st and st["resource"] is None:
        return problems + [f"{at}.resource: expected an object"]
    return problems


def m365_validate_available_models(v: str) -> List[str]:
    t = v.strip()
    if not t.startswith("[") and not t.startswith("{"):
        return ["blank entry in comma-separated id list"] if any(not eid.strip() for eid in t.split(",")) else []
    try:
        parsed = json.loads(t)
    except ValueError as exc:
        raise M365ManifestError(f"available_models is not valid JSON: {exc}") from exc
    arr = parsed if isinstance(parsed, list) else [parsed]
    warnings: List[str] = []
    for i, entry in enumerate(arr):
        if isinstance(entry, str):
            if not entry.strip():
                warnings.append(f"entry[{i}]: blank id")
        elif isinstance(entry, dict):
            eid = entry.get("id")
            if not isinstance(eid, str) or not eid.strip():
                warnings.append(f'entry[{i}]: missing string "id"')
        else:
            warnings.append(f"entry[{i}]: expected an id string or {{id, label}} object")
    return warnings


def _validate_access_policies(v: str) -> List[str]:
    try:
        arr = json.loads(v)
    except ValueError as exc:
        raise M365ManifestError(f"access_policies is not valid JSON: {exc}") from exc
    if not isinstance(arr, list):
        return ["expected a JSON array of statements"]
    out: List[str] = []
    for i, st in enumerate(arr):
        out.extend(m365_validate_statement(st, f"statement[{i}]"))
    return out


M365_KEYS: Dict[str, Dict[str, Any]] = {
    "gcp_project_id": {"pattern": re.compile(r"^[a-z][a-z0-9-]{4,28}[a-z0-9]$"), "hint": "GCP project ID"},
    "gcp_region": {"pattern": re.compile(r"."), "hint": "GCP region, e.g. us-east5 or global"},
    "google_client_id": {"pattern": re.compile(r"\.apps\.googleusercontent\.com$"), "hint": "OAuth 2.0 client ID"},
    "google_client_secret": {"pattern": re.compile(r"^GOCSPX-"), "hint": "OAuth 2.0 client secret"},
    "aws_role_arn": {
        "pattern": re.compile(r"^arn:aws:iam::\d{12}:role/"),
        "hint": "e.g. arn:aws:iam::123456789012:role/ClaudeBedrockAccess",
    },
    "aws_region": {"pattern": re.compile(r"^[a-z]{2}-[a-z]+-\d+$"), "hint": "e.g. us-east-1"},
    "azure_resource_name": {
        "pattern": re.compile(r"^[a-z0-9][a-z0-9-]{1,62}$"),
        "hint": "Azure AI Foundry resource name — the subdomain of your endpoint URL, e.g. 'contoso-foundry' from https://contoso-foundry.services.ai.azure.com",
    },
    "azure_api_key": {
        "pattern": re.compile(r"^[A-Za-z0-9]{20,}$"),
        "hint": "From Azure Portal → your Foundry resource → Keys and Endpoint → KEY 1",
    },
    "graph_client_id": {
        "pattern": re.compile(r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$", re.IGNORECASE),
        "hint": "your Entra app registration's Application (client) ID — overrides the default multi-tenant app",
    },
    "gateway_url": {"pattern": re.compile(r"^https://"), "hint": "HTTPS base URL"},
    "gateway_token": {"pattern": re.compile(r"."), "hint": "gateway API key", "secret": True},
    "gateway_auth_header": {"pattern": re.compile(r"^(x-api-key|authorization)$", re.IGNORECASE), "hint": "auth header scheme (default: x-api-key)"},
    "gateway_api_format": {"pattern": re.compile(r"^(anthropic|bedrock|vertex)$", re.IGNORECASE), "hint": "anthropic | bedrock | vertex"},
    "gateway_auth_source": {
        "pattern": re.compile(r"^entra$"),
        "hint": "'entra' to send the Entra SSO access token as the Bearer to your gateway, or to a Foundry resource named by azure_resource_name (no gateway_token / azure_api_key needed); requires entra_scope",
    },
    "mcp_servers": {"pattern": re.compile(r"^\[.*\]$"), "hint": "JSON array of {url, label, headers?, discover?}"},
    "inference_headers": {"pattern": re.compile(r"^\{.*\}$"), "hint": "JSON object of extra headers to attach to every model request"},
    "bootstrap_url": {"pattern": re.compile(r"^https://"), "hint": "HTTPS endpoint returning per-user config"},
    "otlp_endpoint": {"pattern": re.compile(r"^https://"), "hint": "OTLP/HTTP traces collector URL"},
    "otlp_headers": {"pattern": re.compile(r"."), "hint": "comma-separated k=v pairs for the OTLP exporter"},
    "otlp_resource_attributes": {
        "pattern": re.compile(r"^([^=,\s]+=[^,]*)(,[^=,\s]+=[^,]*)*$"),
        "hint": "comma-separated k=v pairs added to the OTEL Resource (same format as OTEL_RESOURCE_ATTRIBUTES)",
    },
    "auto_connect": {"pattern": re.compile(r"^[01]$"), "hint": "0 shows form, 1 (or omit) auto-connects"},
    "entra_sso": {"pattern": re.compile(r"^[01]$"), "hint": "1 enables Entra SSO (required for aws_role_arn)"},
    "entra_scope": {
        "pattern": re.compile(r"\S"),
        "hint": "scope(s) for the resource the token targets: api://<your-app-guid>/.default for your own API, or https://cognitiveservices.azure.com/.default for Foundry direct — comma/space-separated list allowed, requires graph_client_id",
    },
    "graph_cloud": {
        "pattern": re.compile(r"^(global|us-gov-high|us-gov-dod|china)$"),
        "hint": "Microsoft national cloud: global | us-gov-high | us-gov-dod | china — only for sovereign clouds; GCC-High and 21Vianet are also auto-detected at sign-in",
    },
    "allow_1p": {"pattern": re.compile(r"^[01]$"), "hint": "1 allows Claude.ai OAuth alongside 3P (default: locked when other keys present)"},
    "disabled_features": {
        "pattern": re.compile(r"^[\w.]+(,[\w.]+)*$"),
        "hint": "comma-separated feature slugs to lock for users, e.g. skills.authoring or web_search (disables native web search/fetch; pair with mcp_servers for an in-network replacement)",
    },
    "available_models": {
        "pattern": re.compile(r"\S"),
        "hint": 'override the model picker: comma-separated model ids, or JSON like [{"id":"claude-opus-4-8","label":"Opus 4.8"}] — an OVERRIDE, list every model users should see',
        "validate": m365_validate_available_models,
    },
    "access_policies": {
        "pattern": re.compile(r"^\[.*\]$", re.DOTALL),
        "hint": 'JSON array of policy statements — see commands/access-policies.md; e.g. [{"effect":"deny","action":"addin.access","resource":{...}}]',
        "validate": _validate_access_policies,
    },
}


def m365_split_params(params: Dict[str, str]) -> Tuple[List[Tuple[str, str]], List[Tuple[str, str]]]:
    query: List[Tuple[str, str]] = []
    fragment: List[Tuple[str, str]] = []
    for k, v in params.items():
        if k in M365_SENSITIVE_KEYS:
            fragment.append((k, v))
        else:
            query.append((k, v))
    return query, fragment


def m365_xml_escape(s: str) -> str:
    return s.replace("&", "&amp;")


def m365_append_params(
    url: str,
    query: Sequence[Tuple[str, str]],
    fragment: Sequence[Tuple[str, str]],
) -> str:
    if "#" in url:
        raise M365ManifestError(f"template URL already has a fragment: {url}")
    result = url
    qs = _js_urlencode(query)
    if qs:
        result += ("&amp;" if "?" in url else "?") + m365_xml_escape(qs)
    frag = _js_urlencode(fragment)
    if frag:
        result += "#" + m365_xml_escape(frag)
    return result


def m365_build_manifest_xml(host: str, pairs: Sequence[str], template_xml: str) -> Dict[str, Any]:
    warnings: List[str] = []
    try:
        if host not in M365_MANIFESTS or not pairs:
            raise M365ManifestError("Usage: node build-manifest.mjs <office|outlook> <out.xml> key=value [key=value ...]")
        if host == "outlook" and any(p.startswith("aws_") for p in pairs):
            raise M365ManifestError("error: Amazon Bedrock (aws_role_arn/aws_region) is not currently supported for Outlook")

        params: Dict[str, str] = {}
        for p in pairs:
            eq = p.find("=")
            if eq < 1:
                raise M365ManifestError(f"bad arg: {p} (expected key=value)")
            k, v = p[:eq].strip(), p[eq + 1 :].strip()
            spec = M365_KEYS.get(k)
            if not spec:
                raise M365ManifestError(f"unknown key: {k}\n  valid: {', '.join(M365_KEYS.keys())}")
            if not v:
                raise M365ManifestError(f"empty value for {k}")
            if not spec["pattern"].search(v):
                warnings.append(f"warn: {k}={v} — expected {spec['hint']}")
            val_fn = spec.get("validate")
            if val_fn is not None:
                for msg in val_fn(v):
                    warnings.append(f"warn: {k} {msg}")
            if spec.get("secret"):
                warnings.append(
                    f"note: {k} in the manifest applies to every user. If it varies per user, set it via update-user-attrs instead."
                )
            params[k] = v

        needs_entra = next((k for k in M365_NEEDS_ENTRA if k in params), None)
        if needs_entra and params.get("entra_sso") != "1":
            raise M365ManifestError(f"{needs_entra} requires entra_sso=1 (the add-in needs an Entra token to use it)")
        if "entra_scope" in params and "graph_client_id" not in params:
            raise M365ManifestError(
                "entra_scope requires graph_client_id (the scope is requested as your own Entra app, not the default)"
            )
        if "gateway_auth_source" in params and "entra_scope" not in params:
            raise M365ManifestError(
                "gateway_auth_source=entra requires entra_scope (the gateway Bearer must be audienced to your API, not Microsoft Graph)"
            )
        if "gateway_auth_source" in params and "gateway_token" in params:
            warnings.append("note: gateway_auth_source=entra supersedes gateway_token — drop gateway_token from this manifest")
        cloud = params.get("graph_cloud")
        if cloud and cloud != "global" and "graph_client_id" not in params:
            raise M365ManifestError(f"graph_cloud={cloud} requires a graph_client_id registered in that cloud")

        query, fragment = m365_split_params(params)
        xml = template_xml
        for slot in M365_URL_SLOTS:
            if not slot.search(xml):
                raise M365ManifestError(f"manifest missing expected URL slot: {slot.pattern}")
            xml = slot.sub(lambda m: m.group(1) + m365_append_params(m.group(2), query, fragment) + m.group(3), xml)
        return {"ok": True, "xml": xml, "warnings": warnings, "error": None}
    except M365ManifestError as exc:
        return {"ok": False, "xml": None, "warnings": warnings, "error": str(exc)}


# ===========================================================================
# 5. Auto-test interne L0 & Reçu R10 mesuré (zéro auto-certification)
# ===========================================================================


def run_financial_services_self_test(
    head_sha40: Optional[str] = None,
    repo_root: Optional[Path] = None,
) -> Dict[str, Any]:
    """Vérifie le câblage K5 FSI sous veto S0 sans auto-certification."""
    root = repo_root or WORKSPACE_ROOT
    sha = head_sha40 or ("0" * 40)
    if not READ_ONLY_VETO_S0:
        raise ContractViolation("ADR-07", "READ_ONLY_VETO_S0 doit rester True")

    nums = extract_numbers("# Slide 1\nRevenue reached $12.5M in 2026.\n")
    if len(nums) != 1 or nums[0].normalized != 12_500_000.0:
        raise ContractViolation("K5", "fsi_extract_numbers", f"inattendu: {nums}")
    if parse_semver("1.2.3") != (1, 2, 3) or patch_bump("1.2.3") != "1.2.4":
        raise ContractViolation("K5", "fsi_semver", "échec patch_bump")
    if extract_handoff('prefix {"type": "handoff_request", "target_agent": "pitch-agent", "payload": {"event": "ready"}} suffix') is not None:
        raise ContractViolation("K5", "fsi_handoff", "divergence fidélité HANDOFF_RE amont")
    if validate_json_schema({"event": "ready", "context_ref": "doc:1"}, HANDOFF_PAYLOAD_SCHEMA) != (True, "OK"):
        raise ContractViolation("K5", "fsi_handoff_schema", "échec validation HANDOFF_PAYLOAD_SCHEMA")
    if m365_xml_escape("a&b") != "a&amp;b":
        raise ContractViolation("K5", "fsi_m365_escape", "échec xml_escape")

    evt, rec = consign_measured_l0_evidence(
        actor_from="fabricator",
        actor_to="judge",
        dispatch_id="D-FSI-SMOKE",
        payload="K5 FinancialServices smoke passed (0 source-oracle parities self-claimed)",
        issuer="Kernel K5 (FinancialServices)",
        mission_prefix="FSI-SMOKE",
        sha=sha,
        proof=["01_Forkable/FKB07_Money_Maker/01_Trading/aspace_financial_services_organ.py"],
        summary=f"K5 FSI smoke PASS; source_oracle_parity=0 at {sha[:7]}",
        repo_root=root,
    )
    return {
        "organ": "aspace_financial_services_organ",
        "read_only_veto_s0": READ_ONLY_VETO_S0,
        "source_parity_verified": [],
        "l0_seq": evt["seq"],
        "r10_entry_id": rec["entry_id"],
    }


def consign_financial_services_parity_receipt(
    module_results: Dict[str, Dict[str, Any]],
    head_sha40: str,
    repo_root: Optional[Path] = None,
) -> Dict[str, Any]:
    """Consigne uniquement la parité source-vs-organe réellement mesurée pour M071 financial-services."""
    verified = sorted(
        mid
        for mid, res in module_results.items()
        if res.get("compared_against_source")
        and res.get("cases_compared", 0) > 0
        and res.get("cases_matched") == res.get("cases_compared")
    )
    total_cases = sum(int(res.get("cases_compared", 0)) for res in module_results.values())
    total_matched = sum(int(res.get("cases_matched", 0)) for res in module_results.values())
    evt, rec = consign_measured_l0_evidence(
        actor_from="fabricator",
        actor_to="judge",
        dispatch_id="D-FSI-PARITY",
        payload=f"K5 FinancialServices differential parity: {verified} ({total_matched}/{total_cases} cases)",
        issuer="Kernel K5 (FinancialServices)",
        mission_prefix="FSI-PARITY",
        sha=head_sha40,
        proof=["01_Forkable/FKB07_Money_Maker/01_Trading/aspace_financial_services_organ.py"],
        summary=f"K5 FSI measured parity {total_matched}/{total_cases} across {verified} at {head_sha40[:7]}",
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
    print(json.dumps(run_financial_services_self_test(), indent=2, ensure_ascii=False))
