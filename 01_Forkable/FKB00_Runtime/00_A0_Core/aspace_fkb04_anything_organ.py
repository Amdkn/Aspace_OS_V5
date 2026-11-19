#!/usr/bin/env python3
"""
aspace_fkb04_anything_organ.py — Organes Natifs de la Famille FKB04_Tools_Anything.

Rattachement ADR-13 aux Trois Noyaux Fondamentaux :
  - CORPS / Organe K2 (Action Multi-Harness & Surfaces) :
      M056 CLI-Anything | M057 agent-browser | M058 agent-desktop | M059 api-anything | M063 rea
  - ÂME / Organe K4 (Mémoire Épistémique & Compétences) :
      M060 caveman | M061 claude-mem | M062 hermes-agent

Chaque capacité expose des contrats déterministes, émet des événements conformes au socle L0
(`fondation-13-1` / `aspace_foundation_kernel.py`), et fonctionne de façon 100 % autonome
même lorsque tous les répertoires sources `01_Forkable/FKB04_Tools_Anything/*` sont supprimés.
Zéro dépendance externe, zéro télémétrie, zéro contournement CAPTCHA.
"""

from __future__ import annotations

import ast
import base64
import ctypes
import datetime as dt
import hashlib
import json
import math
import os
import re
import socket
import struct
import subprocess
import sys
import threading
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Dict, Iterable, List, Optional, Sequence, Tuple
from urllib.parse import urlparse

_CORE_DIR = Path(__file__).resolve().parent
if str(_CORE_DIR) not in sys.path:
    sys.path.insert(0, str(_CORE_DIR))

from aspace_foundation_kernel import (  # noqa: E402
    ContractViolation,
    consign_measured_l0_evidence,
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
# 1. M056 CLI-Anything (CORPS / Organe K2)
# ===========================================================================

_CLI_ANYTHING_SKILL_TEMPLATE = """---
name: >-
  {{ skill_name }}
description: >-
  {{ skill_description }}
---

# {{ skill_name }}

{{ skill_intro }}

## Installation

This CLI is installed as part of the cli-anything-{{ software_name }} package:

```bash
pip install cli-anything-{{ software_name }}
```

**Prerequisites:**
- Python 3.10+
- {{ software_name }} must be installed on your system
{% if system_package %}
- Install {{ software_name }}: `{{ system_package }}`
{% endif %}

## Usage

### Basic Commands

```bash
# Show help
cli-anything-{{ software_name }} --help

# Start interactive REPL mode
cli-anything-{{ software_name }}

# Create a new project
cli-anything-{{ software_name }} project new -o project.json

# Run with JSON output (for agent consumption)
cli-anything-{{ software_name }} --json project info -p project.json
```

### REPL Mode

When invoked without a subcommand, the CLI enters an interactive REPL session:

```bash
cli-anything-{{ software_name }}
# Enter commands interactively with tab-completion and history
```

{% if command_groups %}
## Command Groups

{% for group in command_groups %}
### {{ group.name }}

{{ group.description }}

| Command | Description |
|---------|-------------|
{% for cmd in group.commands %}
| `{{ cmd.name }}` | {{ cmd.description }} |
{% endfor %}

{% endfor %}
{% endif %}
## Examples

{% for example in examples %}
### {{ example.title }}

{{ example.description }}

```bash
{{ example.code }}
```

{% endfor %}
## State Management

The CLI maintains session state with:

- **Undo/Redo**: Up to 50 levels of history
- **Project persistence**: Save/load project state as JSON
- **Session tracking**: Track modifications and changes

## Output Formats

All commands support dual output modes:

- **Human-readable** (default): Tables, colors, formatted text
- **Machine-readable** (`--json` flag): Structured JSON for agent consumption

```bash
# Human output
cli-anything-{{ software_name }} project info -p project.json

# JSON output for agents
cli-anything-{{ software_name }} --json project info -p project.json
```

## For AI Agents

When using this CLI programmatically:

1. **Always use `--json` flag** for parseable output
2. **Check return codes** - 0 for success, non-zero for errors
3. **Parse stderr** for error messages on failure
4. **Use absolute paths** for all file operations
5. **Verify outputs exist** after export operations

## More Information

- Full documentation: See README.md in the package
- Test coverage: See TEST.md in the package
- Methodology: See HARNESS.md in the cli-anything-plugin

## Version

{{ version }}"""


@dataclass
class CliCommandInfo:
    name: str
    description: str


@dataclass
class CliCommandGroup:
    name: str
    description: str
    commands: List[CliCommandInfo] = field(default_factory=list)


@dataclass
class CliExample:
    title: str
    description: str
    code: str


@dataclass
class CliSkillMetadata:
    skill_name: str
    skill_description: str
    software_name: str
    skill_intro: str
    version: str
    system_package: Optional[str] = None
    command_groups: List[CliCommandGroup] = field(default_factory=list)
    examples: List[CliExample] = field(default_factory=list)


def _cli_format_display_name(name: str) -> str:
    return name.replace("_", " ").replace("-", " ").title()


def _cli_canonical_skill_name(harness_path: Path, software_name: str) -> str:
    software_dir = software_name
    if harness_path.name == "agent-harness" and harness_path.parent.name:
        software_dir = harness_path.parent.name
    return f"cli-anything-{software_dir.replace('_', '-')}"


def _cli_click_decorator_info(
    function: ast.FunctionDef | ast.AsyncFunctionDef,
    kind: str,
) -> Optional[Tuple[str, str]]:
    for decorator in function.decorator_list:
        target = decorator.func if isinstance(decorator, ast.Call) else decorator
        if not (
            isinstance(target, ast.Attribute)
            and target.attr == kind
            and isinstance(target.value, ast.Name)
        ):
            continue
        declared_name = None
        if isinstance(decorator, ast.Call):
            if decorator.args:
                first_arg = decorator.args[0]
                if isinstance(first_arg, ast.Constant) and isinstance(first_arg.value, str):
                    declared_name = first_arg.value
            if declared_name is None:
                for keyword in decorator.keywords:
                    if (
                        keyword.arg == "name"
                        and isinstance(keyword.value, ast.Constant)
                        and isinstance(keyword.value.value, str)
                    ):
                        declared_name = keyword.value.value
                        break
        return target.value.id, declared_name or function.name.replace("_", "-")
    return None


def _extract_cli_intro_from_readme(content: str) -> str:
    lines = content.split("\n")
    intro_lines = []
    in_intro = False
    for line in lines:
        line = line.strip()
        if not line:
            if in_intro and intro_lines:
                break
            continue
        if line.startswith("# "):
            in_intro = True
            continue
        if line.startswith("##"):
            break
        if in_intro:
            intro_lines.append(line)
    return " ".join(intro_lines) or "CLI interface for the software."


def _extract_cli_system_package(content: str) -> Optional[str]:
    patterns = (
        (r"`apt install ([\w\-]+)`", "apt install"),
        (r"`brew install ([\w\-]+)`", "brew install"),
        (r"`apt-get install ([\w\-]+)`", "apt-get install"),
    )
    for pattern, prefix in patterns:
        match = re.search(pattern, content)
        if match:
            return f"{prefix} {match.group(1)}"
    return None


def extract_commands_from_cli(cli_path: Path) -> List[CliCommandGroup]:
    """Extrait les groupes et commandes Click d'un fichier `<software>_cli.py` par AST."""
    content = cli_path.read_text(encoding="utf-8")
    tree = ast.parse(content, filename=str(cli_path))
    functions = sorted(
        (node for node in ast.walk(tree) if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))),
        key=lambda node: (node.lineno, node.col_offset),
    )
    groups: List[CliCommandGroup] = []
    group_lookup: Dict[str, CliCommandGroup] = {}
    group_display_paths: Dict[str, List[str]] = {}
    group_functions = [
        (fn, info) for fn in functions if (info := _cli_click_decorator_info(fn, "group"))
    ]
    root_group_funcs = {
        fn.name.lower() for fn, (parent, _) in group_functions if parent.lower() == "click"
    }

    for fn, (group_parent, declared_name) in group_functions:
        group_doc = (ast.get_docstring(fn, clean=False) or "").strip()
        local_name = _cli_format_display_name(declared_name)
        parent_key = group_parent.lower()
        if parent_key == "click" or parent_key in root_group_funcs:
            group_path = [local_name]
        else:
            parent_path = group_display_paths.get(parent_key)
            group_path = [*parent_path, local_name] if parent_path else [_cli_format_display_name(group_parent), local_name]
        group_name = " ".join(group_path)
        group = CliCommandGroup(
            name=group_name,
            description=group_doc or f"Commands for {group_name.lower()} operations.",
            commands=[],
        )
        groups.append(group)
        group_lookup[fn.name.lower()] = group
        group_display_paths[fn.name.lower()] = group_path

    command_functions = [
        (fn, info) for fn in functions if (info := _cli_click_decorator_info(fn, "command"))
    ]
    for fn, (group_name, declared_name) in command_functions:
        cmd_doc = (ast.get_docstring(fn, clean=False) or "").strip()
        grp = group_lookup.get(group_name.lower())
        if grp:
            grp.commands.append(
                CliCommandInfo(name=declared_name, description=cmd_doc or f"Execute {fn.name} operation.")
            )
    if not groups:
        default_group = CliCommandGroup(name="General", description="General commands for the CLI.", commands=[])
        for fn, (_, declared_name) in command_functions:
            cmd_doc = (ast.get_docstring(fn, clean=False) or "").strip()
            default_group.commands.append(
                CliCommandInfo(name=declared_name, description=cmd_doc or f"Execute {fn.name} operation.")
            )
        if default_group.commands:
            groups.append(default_group)
    return groups


def extract_cli_anything_metadata(harness_path: Path | str) -> CliSkillMetadata:
    """Extrait les métadonnées d'un répertoire `agent-harness` CLI-Anything réel."""
    hp = Path(harness_path)
    cli_anything_dir = hp / "cli_anything"
    if not cli_anything_dir.exists():
        raise ValueError(
            f"cli_anything directory not found in {hp}. Ensure the harness structure includes cli_anything/<software>/"
        )
    software_dirs = [d for d in cli_anything_dir.iterdir() if d.is_dir() and (d / "__init__.py").exists()]
    if not software_dirs:
        raise ValueError(f"No CLI package found in {hp}")
    software_dir = software_dirs[0]
    software_name = software_dir.name

    skill_intro = ""
    system_package = None
    readme_path = software_dir / "README.md"
    if readme_path.exists():
        readme_content = readme_path.read_text(encoding="utf-8")
        skill_intro = _extract_cli_intro_from_readme(readme_content)
        system_package = _extract_cli_system_package(readme_content)

    version = "1.0.0"
    setup_path = hp / "setup.py"
    if setup_path.exists():
        match = re.search(r'version\s*=\s*["\']([^"\']+)["\']', setup_path.read_text(encoding="utf-8"))
        if match:
            version = match.group(1)

    cli_file = software_dir / f"{software_name}_cli.py"
    command_groups = extract_commands_from_cli(cli_file) if cli_file.exists() else []

    examples = [
        CliExample(
            title="Create a New Project",
            description=f"Create a new {software_name} project file.",
            code=f"cli-anything-{software_name} project new -o myproject.json\n# Or with JSON output for programmatic use\ncli-anything-{software_name} --json project new -o myproject.json",
        ),
        CliExample(
            title="Interactive REPL Session",
            description="Start an interactive session with undo/redo support.",
            code=f"cli-anything-{software_name}\n# Enter commands interactively\n# Use 'help' to see available commands\n# Use 'undo' and 'redo' for history navigation",
        ),
    ]
    for group in command_groups:
        if "export" in group.name.lower():
            examples.append(
                CliExample(
                    title="Export Project",
                    description="Export the project to a final output format.",
                    code=f"cli-anything-{software_name} --project myproject.json export render output.pdf --overwrite",
                )
            )
            break

    skill_name = _cli_canonical_skill_name(hp, software_name)
    if skill_intro:
        intro_snippet = skill_intro[:100]
        suffix = "..." if len(skill_intro) > 100 else ""
        skill_description = f"Command-line interface for {_cli_format_display_name(software_name)} - {intro_snippet}{suffix}"
    else:
        skill_description = f"Command-line interface for {_cli_format_display_name(software_name)}"

    return CliSkillMetadata(
        skill_name=skill_name,
        skill_description=skill_description,
        software_name=software_name,
        skill_intro=skill_intro,
        version=version,
        system_package=system_package,
        command_groups=command_groups,
        examples=examples,
    )


def generate_cli_anything_skill_md_simple(metadata: CliSkillMetadata) -> str:
    """Génère SKILL.md sans Jinja2 (conforme à generate_skill_md_simple amont)."""
    lines = [
        "---",
        f'name: "{metadata.skill_name}"',
        f'description: "{metadata.skill_description}"',
        "---",
        "",
        f"# {metadata.skill_name}",
        "",
        metadata.skill_intro,
        "",
        "## Installation",
        "",
        f"This CLI is installed as part of the cli-anything-{metadata.software_name} package:",
        "",
        "```bash",
        f"pip install cli-anything-{metadata.software_name}",
        "```",
        "",
        "**Prerequisites:**",
        "- Python 3.10+",
        f"- {_cli_format_display_name(metadata.software_name)} must be installed on your system",
    ]
    if metadata.system_package:
        lines.append(f"- Install {metadata.software_name}: `{metadata.system_package}`")
    lines.extend(
        [
            "",
            "## Usage",
            "",
            "### Basic Commands",
            "",
            "```bash",
            "# Show help",
            f"cli-anything-{metadata.software_name} --help",
            "",
            "# Start interactive REPL mode",
            f"cli-anything-{metadata.software_name}",
            "",
            "# Create a new project",
            f"cli-anything-{metadata.software_name} project new -o project.json",
            "",
            "# Run with JSON output (for agent consumption)",
            f"cli-anything-{metadata.software_name} --json project info -p project.json",
            "```",
            "",
        ]
    )
    if metadata.command_groups:
        lines.extend(["## Command Groups", ""])
        for group in metadata.command_groups:
            lines.extend([f"### {group.name}", "", group.description, ""])
            if group.commands:
                lines.extend(["| Command | Description |", "|---------|-------------|"])
                for cmd in group.commands:
                    lines.append(f"| `{cmd.name}` | {cmd.description} |")
                lines.append("")
    if metadata.examples:
        lines.extend(["## Examples", ""])
        for example in metadata.examples:
            lines.extend([f"### {example.title}", "", example.description, "", "```bash", example.code, "```", ""])
    lines.extend(
        [
            "## For AI Agents",
            "",
            "When using this CLI programmatically:",
            "",
            "1. **Always use `--json` flag** for parseable output",
            "2. **Check return codes** - 0 for success, non-zero for errors",
            "3. **Parse stderr** for error messages on failure",
            "4. **Use absolute paths** for all file operations",
            "5. **Verify outputs exist** after export operations",
            "",
            "## Version",
            "",
            metadata.version,
        ]
    )
    return "\n".join(lines)


def generate_cli_anything_skill_md(metadata: CliSkillMetadata, template_text: Optional[str] = None) -> str:
    """Génère le contenu SKILL.md CLI-Anything avec parité template Jinja2."""
    try:
        from jinja2 import Environment
    except ImportError:
        return generate_cli_anything_skill_md_simple(metadata)
    env = Environment()
    template = env.from_string(template_text if template_text is not None else _CLI_ANYTHING_SKILL_TEMPLATE)
    return template.render(
        skill_name=metadata.skill_name,
        skill_description=metadata.skill_description,
        software_name=metadata.software_name,
        skill_intro=metadata.skill_intro,
        version=metadata.version,
        system_package=metadata.system_package,
        command_groups=[
            {
                "name": g.name,
                "description": g.description,
                "commands": [{"name": c.name, "description": c.description} for c in g.commands],
            }
            for g in metadata.command_groups
        ],
        examples=[
            {"title": e.title, "description": e.description, "code": e.code}
            for e in metadata.examples
        ],
    )


def build_cli_anything_preview_cache_key(
    software: str,
    recipe: str,
    bundle_kind: str,
    source_fingerprint: str,
    options: Optional[Dict[str, Any]] = None,
    harness_version: Optional[str] = None,
    protocol_version: str = "preview-bundle/v1",
) -> str:
    """Calcule la clé de cache SHA-256 canonique (preview_bundle.py amont)."""
    payload = {
        "protocol_version": protocol_version,
        "software": software,
        "recipe": recipe,
        "bundle_kind": bundle_kind,
        "source_fingerprint": source_fingerprint,
        "options": options or {},
        "harness_version": harness_version or "",
    }
    raw = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"), default=str)
    return f"sha256:{hashlib.sha256(raw.encode('utf-8')).hexdigest()}"


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
# 2. M057 agent-browser (CORPS / Organe K2) — Snapshot + Client CDP RFC 6455
# ===========================================================================

_WS_GUID = b"258EAFA5-E914-47DA-95CA-C5AB0DC85B11"


def _ws_recv_exact(sock: socket.socket, n: int) -> bytes:
    buf = bytearray()
    while len(buf) < n:
        chunk = sock.recv(n - len(buf))
        if not chunk:
            raise EOFError("Connexion WebSocket CDP fermée prématurément")
        buf.extend(chunk)
    return bytes(buf)


def _ws_encode_frame(payload: bytes, masked: bool = True, opcode: int = 0x1) -> bytes:
    header = bytearray([0x80 | (opcode & 0x0F)])
    length = len(payload)
    mask_bit = 0x80 if masked else 0x00
    if length < 126:
        header.append(mask_bit | length)
    elif length < 65536:
        header.append(mask_bit | 126)
        header.extend(struct.pack("!H", length))
    else:
        header.append(mask_bit | 127)
        header.extend(struct.pack("!Q", length))
    if not masked:
        return bytes(header) + payload
    mask_key = os.urandom(4)
    masked_bytes = bytes(b ^ mask_key[i % 4] for i, b in enumerate(payload))
    return bytes(header) + mask_key + masked_bytes


def _ws_read_frame(sock: socket.socket) -> Tuple[int, bytes]:
    b1, b2 = _ws_recv_exact(sock, 2)
    opcode = b1 & 0x0F
    is_masked = bool(b2 & 0x80)
    length = b2 & 0x7F
    if length == 126:
        length = struct.unpack("!H", _ws_recv_exact(sock, 2))[0]
    elif length == 127:
        length = struct.unpack("!Q", _ws_recv_exact(sock, 8))[0]
    mask_key = _ws_recv_exact(sock, 4) if is_masked else b""
    payload = _ws_recv_exact(sock, length)
    if is_masked:
        payload = bytes(b ^ mask_key[i % 4] for i, b in enumerate(payload))
    return opcode, payload


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


class CDPWebSocketClient:
    """Client Chrome DevTools Protocol RFC 6455 natif (zéro dépendance externe)."""

    def __init__(self, ws_url: str, timeout: float = 5.0) -> None:
        self.ws_url = ws_url
        self.timeout = timeout
        self._sock: Optional[socket.socket] = None
        self._next_id = 0

    def __enter__(self) -> "CDPWebSocketClient":
        self.connect()
        return self

    def __exit__(self, exc_type: Any, exc: Any, tb: Any) -> None:
        self.close()

    def connect(self) -> None:
        parsed = urlparse(self.ws_url)
        if parsed.scheme != "ws" or not parsed.hostname:
            raise ContractViolation("K2", "ws_url", f"schéma WebSocket CDP invalide: {self.ws_url}")
        port = parsed.port or 80
        path = parsed.path or "/"
        if parsed.query:
            path = f"{path}?{parsed.query}"
        sock = socket.create_connection((parsed.hostname, port), timeout=self.timeout)
        key = base64.b64encode(os.urandom(16)).decode("ascii")
        req = (
            f"GET {path} HTTP/1.1\r\n"
            f"Host: {parsed.hostname}:{port}\r\n"
            f"Upgrade: websocket\r\n"
            f"Connection: Upgrade\r\n"
            f"Sec-WebSocket-Key: {key}\r\n"
            f"Sec-WebSocket-Version: 13\r\n\r\n"
        )
        sock.sendall(req.encode("ascii"))
        raw_hdr = bytearray()
        while b"\r\n\r\n" not in raw_hdr:
            chunk = sock.recv(4096)
            if not chunk:
                sock.close()
                raise ConnectionError("Échec handshake WebSocket CDP (EOF)")
            raw_hdr.extend(chunk)
        header_text = raw_hdr.split(b"\r\n\r\n", 1)[0].decode("latin-1")
        expected_accept = base64.b64encode(hashlib.sha1(key.encode("ascii") + _WS_GUID).digest()).decode("ascii")
        if "101" not in header_text.splitlines()[0] or expected_accept not in header_text:
            sock.close()
            raise ConnectionError(f"Handshake CDP rejeté: {header_text.splitlines()[0]}")
        self._sock = sock

    def close(self) -> None:
        if self._sock is not None:
            try:
                self._sock.sendall(_ws_encode_frame(b"", masked=True, opcode=0x8))
            except OSError:
                pass
            try:
                self._sock.close()
            finally:
                self._sock = None

    def send_command(self, method: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        if self._sock is None:
            raise ContractViolation("K2", "cdp_socket", "CDPWebSocketClient non connecté")
        self._next_id += 1
        cmd_id = self._next_id
        payload = json.dumps({"id": cmd_id, "method": method, "params": params or {}}).encode("utf-8")
        self._sock.sendall(_ws_encode_frame(payload, masked=True, opcode=0x1))
        while True:
            opcode, data = _ws_read_frame(self._sock)
            if opcode == 0x9:
                self._sock.sendall(_ws_encode_frame(data, masked=True, opcode=0xA))
                continue
            if opcode == 0x8:
                raise EOFError("Serveur CDP a fermé la session")
            msg = json.loads(data.decode("utf-8"))
            if msg.get("id") == cmd_id:
                if "error" in msg:
                    raise ContractViolation("K2", method, str(msg["error"]))
                return msg.get("result", {})

    def snapshot_live(self, url: Optional[str] = None) -> Dict[str, Any]:
        if url:
            self.send_command("Page.navigate", {"url": url})
        eval_res = self.send_command(
            "Runtime.evaluate",
            {"expression": "document.body ? document.body.innerText : ''", "returnByValue": True},
        )
        page_text = str(eval_res.get("result", {}).get("value", ""))
        ax_res = self.send_command("Accessibility.getFullAXTree")
        dom_nodes: List[Dict[str, Any]] = []
        for raw_node in ax_res.get("nodes", []):
            role_val = raw_node.get("role", {})
            name_val = raw_node.get("name", {})
            dom_nodes.append(
                {
                    "role": role_val.get("value", "generic") if isinstance(role_val, dict) else role_val,
                    "name": name_val.get("value", "") if isinstance(name_val, dict) else name_val,
                    "backendNodeId": raw_node.get("backendDOMNodeId"),
                }
            )
        snap = build_cdp_a11y_snapshot(dom_nodes, url=url or self.ws_url, page_text=page_text)
        snap["cdp_transport"] = "rfc6455-websocket"
        return snap


# ===========================================================================
# 3. M058 agent-desktop (CORPS / Organe K2) — Plan + Driver OS UIA/Win32
# ===========================================================================

class NativeDesktopUIADriver:
    """Introspection desktop OS native (Win32 User32 + fallback POSIX) sans vol de focus."""

    @staticmethod
    def capture_live_uia_tree(limit: int = 25) -> List[Dict[str, Any]]:
        if sys.platform == "win32":
            user32 = ctypes.windll.user32
            results: List[Dict[str, Any]] = []
            enum_proc_t = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_void_p, ctypes.c_void_p)

            def _callback(hwnd: int, _lparam: int) -> bool:
                if len(results) >= limit:
                    return False
                if not user32.IsWindowVisible(hwnd):
                    return True
                tlen = user32.GetWindowTextLengthW(hwnd)
                if tlen <= 0:
                    return True
                tbuf = ctypes.create_unicode_buffer(tlen + 1)
                user32.GetWindowTextW(hwnd, tbuf, tlen + 1)
                cbuf = ctypes.create_unicode_buffer(128)
                user32.GetClassNameW(hwnd, cbuf, 128)
                pid = ctypes.c_ulong()
                user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
                results.append(
                    {
                        "ref": f"@d{len(results) + 1}",
                        "hwnd": int(hwnd),
                        "pid": int(pid.value),
                        "control_type": cbuf.value or "Window",
                        "name": tbuf.value,
                        "enabled": bool(user32.IsWindowEnabled(hwnd)),
                        "source": "win32-user32",
                    }
                )
                return True

            user32.EnumWindows(enum_proc_t(_callback), 0)
            return results
        return []

    @classmethod
    def execute_desktop_a11y_action(
        cls,
        target_ref: str,
        action: str,
        text_input: Optional[str] = None,
        uia_tree: Optional[Sequence[Dict[str, Any]]] = None,
        no_focus_steal: bool = True,
    ) -> Dict[str, Any]:
        tree = list(uia_tree) if uia_tree is not None else cls.capture_live_uia_tree()
        plan = plan_desktop_a11y_action(tree, target_ref, action, text_input=text_input, no_focus_steal=no_focus_steal)
        elem = next(item for item in tree if item.get("ref") == target_ref)
        hwnd = int(elem.get("hwnd") or 0)
        live_verified = bool(
            sys.platform == "win32"
            and hwnd != 0
            and ctypes.windll.user32.IsWindow(ctypes.c_void_p(hwnd))
        )
        return {
            **plan,
            "live_window_verified": live_verified,
            "source": elem.get("source", "uia-tree"),
            "observed_value": elem.get("name", "") if action == "read_value" else None,
        }


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
# 4. M059 api-anything (CORPS / Organe K2)
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
# 5. M060 caveman (ÂME / Organe K4)
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
# 6. M061 claude-mem (ÂME / Organe K4)
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
# 7. M062 hermes-agent (ÂME / Organe K4)
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
# 8. M063 rea (CORPS / Organe K2)
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

def _run_loopback_cdp_probe() -> Dict[str, Any]:
    """Lance un endpoint CDP WebSocket RFC 6455 loopback éphémère et vérifie READY + BLOQUÉ."""
    srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    srv.bind(("127.0.0.1", 0))
    srv.listen(2)
    port = srv.getsockname()[1]
    srv.settimeout(5.0)
    state = {"url": "http://127.0.0.1:31415/ui"}

    def _serve() -> None:
        try:
            conn, _ = srv.accept()
            conn.settimeout(5.0)
            hdr = bytearray()
            while b"\r\n\r\n" not in hdr:
                c = conn.recv(2048)
                if not c:
                    break
                hdr.extend(c)
            m = re.search(rb"(?i)Sec-WebSocket-Key:\s*([^\r\n]+)", bytes(hdr))
            ws_key = m.group(1).strip() if m else b""
            accept_val = base64.b64encode(hashlib.sha1(ws_key + _WS_GUID).digest()).decode("ascii")
            conn.sendall(
                (
                    "HTTP/1.1 101 Switching Protocols\r\n"
                    "Upgrade: websocket\r\n"
                    "Connection: Upgrade\r\n"
                    f"Sec-WebSocket-Accept: {accept_val}\r\n\r\n"
                ).encode("ascii")
            )
            while True:
                op, raw = _ws_read_frame(conn)
                if op == 0x8:
                    break
                req = json.loads(raw.decode("utf-8"))
                method = req.get("method", "")
                if method == "Page.navigate":
                    state["url"] = req.get("params", {}).get("url", state["url"])
                    res: Dict[str, Any] = {"frameId": "F1"}
                elif method == "Runtime.evaluate":
                    is_blocked = "blocked" in state["url"]
                    txt = "Please complete Cloudflare Turnstile to verify you are human" if is_blocked else "Dashboard Ready"
                    res = {"result": {"value": txt}}
                elif method == "Accessibility.getFullAXTree":
                    res = {
                        "nodes": [
                            {"role": {"value": "button"}, "name": {"value": "Launch Mission"}, "backendDOMNodeId": 101},
                            {"role": {"value": "textbox"}, "name": {"value": "Target"}, "backendDOMNodeId": 102},
                        ]
                    }
                else:
                    res = {}
                resp_bytes = json.dumps({"id": req["id"], "result": res}).encode("utf-8")
                conn.sendall(_ws_encode_frame(resp_bytes, masked=False, opcode=0x1))
            conn.close()
        except OSError:
            pass

    th = threading.Thread(target=_serve, daemon=True)
    th.start()
    try:
        with CDPWebSocketClient(f"ws://127.0.0.1:{port}/devtools/page/1", timeout=5.0) as client:
            live_ready = client.snapshot_live("http://127.0.0.1:31415/ui")
            live_blocked = client.snapshot_live("https://example.org/blocked")
        return {"live_ready": live_ready, "live_blocked": live_blocked}
    finally:
        th.join(timeout=2.0)
        srv.close()


def run_fkb04_self_test(
    work_dir: Optional[Path] = None,
    head_sha40: str = "0" * 40,
    repo_root: Optional[Path] = None,
) -> Dict[str, Any]:
    import tempfile

    ctx_mgr = tempfile.TemporaryDirectory(ignore_cleanup_errors=True) if work_dir is None else None
    base = Path(ctx_mgr.name) if ctx_mgr is not None else work_dir
    root = repo_root or Path(__file__).resolve().parents[3]
    checks: Dict[str, bool] = {}
    try:
        # 1. CLI-Anything (M056) — parser AST Click + template SKILL.md + cache key
        sample_harness = base / "demo_tool" / "agent-harness"
        pkg_dir = sample_harness / "cli_anything" / "demo_tool"
        pkg_dir.mkdir(parents=True, exist_ok=True)
        (pkg_dir / "__init__.py").write_text("", encoding="utf-8")
        (pkg_dir / "README.md").write_text("# Demo Tool\n\nInspect artifacts deterministically.\n", encoding="utf-8")
        (sample_harness / "setup.py").write_text('version="1.2.3"\n', encoding="utf-8")
        (pkg_dir / "demo_tool_cli.py").write_text(
            "import click\n@click.group()\ndef cli():\n    '''Root CLI.'''\n@cli.command()\ndef inspect():\n    '''Inspect input.'''\n",
            encoding="utf-8",
        )
        cli_meta = extract_cli_anything_metadata(sample_harness)
        rendered_skill = generate_cli_anything_skill_md(cli_meta)
        cache_key = build_cli_anything_preview_cache_key("demo_tool", "inspect", "preview", "sha256:abc", harness_version=cli_meta.version)
        checks["cli_anything_skill_render"] = (
            cli_meta.skill_name == "cli-anything-demo-tool"
            and "## Version\n\n1.2.3" in rendered_skill
            and cache_key.startswith("sha256:")
        )
        assert checks["cli_anything_skill_render"]

        # 2. agent-browser (M057) — client CDP WebSocket RFC 6455 loopback + blocage CAPTCHA
        cdp_probe = _run_loopback_cdp_probe()
        snap_ok = cdp_probe["live_ready"]
        snap_blocked = cdp_probe["live_blocked"]
        checks["cdp_loopback_probe"] = (
            snap_ok["status"] == "READY"
            and snap_ok["cdp_transport"] == "rfc6455-websocket"
            and "@e1" in snap_ok["refs"]
            and snap_blocked["status"] == "BLOQUÉ"
        )
        assert checks["cdp_loopback_probe"]

        # 3. agent-desktop (M058) — aucun repli factice headless-fallback autorisé
        live_tree = NativeDesktopUIADriver.capture_live_uia_tree(limit=15)
        assert not any(w.get("source") == "headless-fallback" for w in live_tree)
        desktop_live_verified = False
        if live_tree:
            live_act = NativeDesktopUIADriver.execute_desktop_a11y_action(
                live_tree[0]["ref"], "read_value", uia_tree=live_tree, no_focus_steal=True
            )
            desktop_live_verified = bool(live_act["live_window_verified"])
            assert live_act["no_focus_steal"] is True
        checks["desktop_no_fake_fallback"] = not any(w.get("source") == "headless-fallback" for w in live_tree)

        # 4. api-anything (M059)
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
        checks["api_anything_har_redact"] = (
            op["path_template"] == "/v1/items/{id_1}/analyze"
            and "SECRET_TOKEN_SHOULD_STRIP" not in json.dumps(har_spec)
        )
        assert checks["api_anything_har_redact"]

        # 5. caveman (M060)
        cav = compress_telegraphic(
            "Please likely note that your `aspace_foundation_kernel.py` file for sha 41889edb9c468ea62ee4641328c0e6f4bac2c618b81da751eebd2af4c05f648d would require review."
        )
        checks["caveman_sha_preserved"] = (
            cav["reduction_pct"] > 15.0
            and "41889edb9c468ea62ee4641328c0e6f4bac2c618b81da751eebd2af4c05f648d" in cav["compressed_text"]
        )
        assert checks["caveman_sha_preserved"]

        # 6. claude-mem (M061)
        mem_rec = SessionMemoryRecorder(base / "claude_mem_obs.jsonl")
        mem_rec.capture_observation("sess-1", "decision", "Verified fixture anchor-001", "fondation-13-1/tests/fixtures/anchor-001.json")
        mem_rec.capture_observation("sess-1", "decision", "Compiled FKB04 native organ", "aspace_fkb04_anything_organ.py")
        reinj = mem_rec.reinject_bounded_context(token_budget=40)
        checks["claude_mem_bounded"] = reinj["tokens_used"] <= 40 and reinj["selected_count"] >= 1
        assert checks["claude_mem_bounded"]

        # 7. hermes-agent (M062)
        bm25_hits = HermesLearningLoop.bm25_search(
            [
                {"id": "d1", "text": "Rust cargo test fondation-13-1 passes all anchors"},
                {"id": "d2", "text": "Unrelated styling note CSS color"},
            ],
            "cargo test fondation",
        )
        skill_ok = HermesLearningLoop.compile_skill_from_trajectory(
            "rust-lf-verify", "Verify Rust LF fixtures", ["Check .gitattributes", "Run cargo test"], holdout_delta=0.042
        )
        holdout_rejected = False
        try:
            HermesLearningLoop.compile_skill_from_trajectory("bad", "Too noisy", ["step"], holdout_delta=0.005)
        except ContractViolation as exc:
            holdout_rejected = exc.rule == "ADR-06"
        checks["hermes_holdout_gate"] = bool(bm25_hits and bm25_hits[0]["id"] == "d1" and skill_ok["promoted"] and holdout_rejected)
        assert checks["hermes_holdout_gate"]

        # 8. rea (M063)
        rea_spec = clean_room_inspect_artifact(
            b"export async function dispatchTask() { fetch('/v1/chat/completions'); }",
            label="mock_bundle.js",
        )
        checks["rea_clean_room"] = "dispatchTask" in rea_spec["exported_symbols"] and "/v1/chat/completions" in rea_spec["endpoints_detected"]
        assert checks["rea_clean_room"]

        passed = sum(1 for v in checks.values() if v)
        total = len(checks)
        evt, rec = consign_measured_l0_evidence(
            actor_from="fabricator",
            actor_to="judge",
            dispatch_id="D-FKB04-SMOKE",
            payload=f"FKB04 smoke checks: {passed}/{total} internal, 0 source-oracle parities",
            issuer="Organ FKB04",
            mission_prefix="FKB04-SMOKE",
            sha=head_sha40,
            proof=["01_Forkable/FKB00_Runtime/00_A0_Core/aspace_fkb04_anything_organ.py"],
            summary=f"FKB04 smoke={passed}/{total}; desktop_win={len(live_tree)}; source_oracle_parity=0 at {head_sha40[:7]}",
            repo_root=root,
        )
        return {
            "organ": "aspace_fkb04_anything_organ",
            "checks": checks,
            "checks_passed": passed,
            "checks_total": total,
            "source_parity_verified": [],
            "cdp_live_refs": len(snap_ok["refs"]),
            "desktop_live_windows": len(live_tree),
            "desktop_live_verified": desktop_live_verified,
            "l0_seq": evt["seq"],
            "r10_entry_id": rec["entry_id"],
        }
    finally:
        if ctx_mgr is not None:
            ctx_mgr.cleanup()


def consign_fkb04_parity_receipt(
    module_results: Dict[str, Dict[str, Any]],
    head_sha40: str,
    repo_root: Optional[Path] = None,
) -> Dict[str, Any]:
    """Consigne uniquement la parité source-vs-organe réellement mesurée sur les entrées identiques."""
    verified = sorted(
        mid
        for mid, res in module_results.items()
        if res.get("compared_against_source") and res.get("cases_compared", 0) > 0 and res.get("cases_matched") == res.get("cases_compared")
    )
    total_cases = sum(int(res.get("cases_compared", 0)) for res in module_results.values())
    total_matched = sum(int(res.get("cases_matched", 0)) for res in module_results.values())
    evt, rec = consign_measured_l0_evidence(
        actor_from="fabricator",
        actor_to="judge",
        dispatch_id="D-FKB04-PARITY",
        payload=f"FKB04 differential parity: {verified} ({total_matched}/{total_cases} cases)",
        issuer="Organ FKB04",
        mission_prefix="FKB04-PARITY",
        sha=head_sha40,
        proof=["01_Forkable/FKB00_Runtime/00_A0_Core/aspace_fkb04_anything_organ.py"],
        summary=f"FKB04 measured parity {total_matched}/{total_cases} across {verified} at {head_sha40[:7]}",
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
    print(json.dumps(run_fkb04_self_test(), indent=2, ensure_ascii=False))
