#!/usr/bin/env python3
"""
A'Space OS V5 — Level 5 Semantic Gate & Invariant Engine
Remplace le scanning textuel 1D par une validation topologique, sémantique et formelle (7R).
"""

import os
import sys
import json
import re
import ast
from pathlib import Path

FORKABLE_DIRS = {"01_Forkable", "graphify-out"}
STRICT_SECRET_PATTERNS = [
    re.compile(r"ghp_[A-Za-z0-9]{36,}"),
    re.compile(r"sk-ant-[A-Za-z0-9\-_]{30,}"),
    re.compile(r"AIza[0-9A-Za-z\-_]{35}"),
    re.compile(r"-----BEGIN (?:RSA|OPENSSH|EC) PRIVATE KEY-----"),
]

MOCK_OR_SAMPLE_INDICATORS = [
    "example", "sample", "dummy", "placeholder", "test", "fake", "xxx", "your_", "mock"
]


def is_forkable_or_vendor(path: Path) -> bool:
    parts = path.parts
    return any(p in FORKABLE_DIRS for p in parts)


def verify_okf_frontmatter(path: Path) -> list:
    errors = []
    if path.suffix != ".md":
        return errors
    try:
        content = path.read_text(encoding="utf-8")
        if not content.startswith("---\n") and not content.startswith("---\r\n"):
            errors.append(f"{path}: En-tête YAML frontmatter manquant (---).")
            return errors
        lines = content.splitlines()
        if not any(line.startswith("type:") for line in lines[:30]):
            errors.append(f"{path}: Clé 'type:' absente du frontmatter OKF v0.2.")
    except Exception as e:
        errors.append(f"{path}: Erreur de lecture OKF ({e}).")
    return errors


def analyze_code_for_live_secrets(path: Path) -> list:
    errors = []
    try:
        content = path.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return errors

    if path.suffix == ".py":
        try:
            tree = ast.parse(content, filename=str(path))
            for node in ast.walk(tree):
                if isinstance(node, ast.Assign):
                    for target in node.targets:
                        target_id = getattr(target, "id", "").lower()
                        if any(k in target_id for k in ("token", "secret", "key", "password")):
                            if isinstance(node.value, ast.Constant) and isinstance(node.value.value, str):
                                val = node.value.value
                                for pat in STRICT_SECRET_PATTERNS:
                                    if pat.search(val) and not any(m in val.lower() for m in MOCK_OR_SAMPLE_INDICATORS):
                                        errors.append(f"{path}:{node.lineno}: Secret actif détecté dans la variable '{target_id}'.")
            return errors
        except SyntaxError:
            pass

    lines = content.splitlines()
    for idx, line in enumerate(lines, 1):
        stripped = line.strip()
        if stripped.startswith(("#", "//", "/*", "*")):
            continue
        for pat in STRICT_SECRET_PATTERNS:
            match = pat.search(line)
            if match:
                matched_str = match.group(0)
                if not any(m in line.lower() for m in MOCK_OR_SAMPLE_INDICATORS):
                    errors.append(f"{path}:{idx}: Token authentique non masqué détecté hors Holon.")
    return errors


def run_gate(root_dir: Path) -> bool:
    violations = []
    print("=" * 60)
    print("A'SPACE OS V5 — LEVEL 5 DETERMINISTIC GATE (AGENT-NATIVE)")
    print("=" * 60)

    required_files = [
        root_dir / "AGENTS.md",
        root_dir / "CLAUDE.md",
        root_dir / "00_Memoire/AGENTS.md",
        root_dir / "00_Memoire/bundle/index.md",
        root_dir / "00_Memoire/bundle/log.md",
        root_dir / "factory/config.json",
    ]
    for rf in required_files:
        if not rf.exists():
            violations.append(f"Structure: Fichier requis absent : {rf.relative_to(root_dir)}")

    concepts_dir = root_dir / "00_Memoire/bundle/concepts"
    if concepts_dir.is_dir():
        for cf in concepts_dir.glob("*.md"):
            violations.extend(verify_okf_frontmatter(cf))

    scanned_core = 0
    scanned_forkable = 0

    for path in root_dir.rglob("*"):
        if not path.is_file():
            continue
        rel = path.relative_to(root_dir)

        if any(part in {".git", ".github"} for part in rel.parts) or str(rel).replace("\\", "/") == "00_Memoire/ledger.jsonl":
            continue

        if is_forkable_or_vendor(rel):
            scanned_forkable += 1
            continue

        scanned_core += 1
        violations.extend(analyze_code_for_live_secrets(path))

    print(f"Topologie : {scanned_core} fichiers Core audités | {scanned_forkable} fichiers Holons CAS isolés.")

    if violations:
        print(f"\n[ÉCHEC] {len(violations)} violation(s) d'invariant détectée(s) :")
        for v in violations:
            print(f"  - {v}")
        return False

    print("\n[SUCCÈS] Tous les invariants 5D sont validés. Baux conformes.")
    return True


if __name__ == "__main__":
    root = Path(__file__).resolve().parent.parent
    success = run_gate(root)
    sys.exit(0 if success else 1)
