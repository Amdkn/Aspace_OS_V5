#!/usr/bin/env python3
"""
02_Factory/01_Kernel_Gates/hooks/aspace_deterministic_hooks.py
==============================================================
Miroir canonique dans 01_Kernel_Gates du moteur de Hooks déterministes (exit 0 / exit 2).
Délègue directement à 02_Factory/hooks/aspace_deterministic_hooks.py.
"""

import runpy
from pathlib import Path

TARGET = Path(__file__).resolve().parents[2] / "hooks" / "aspace_deterministic_hooks.py"

if __name__ == "__main__":
    runpy.run_path(str(TARGET), run_name="__main__")
