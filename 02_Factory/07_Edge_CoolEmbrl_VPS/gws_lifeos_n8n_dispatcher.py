#!/usr/bin/env python3
"""
02_Factory/07_Edge_CoolEmbrl_VPS/gws_lifeos_n8n_dispatcher.py
=============================================================
Miroir catégoriel dans 07_Edge_CoolEmbrl_VPS du dispatcher GitHub-as-n8n × GWS CLI.
"""

import runpy
from pathlib import Path

TARGET = Path(__file__).resolve().parents[1] / "gws_lifeos_n8n_dispatcher.py"

if __name__ == "__main__":
    runpy.run_path(str(TARGET), run_name="__main__")
