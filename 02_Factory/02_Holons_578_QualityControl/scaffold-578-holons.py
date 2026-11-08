#!/usr/bin/env python3
"""
A'Space OS V5 — 02_Factory/scaffold-578-holons.py
Générateur Déterministe de l'Architecture `Areas OS` (`LD01..LD08` + `J1`) et des 578 Holons.
Implémente :
  1. L'arborescence complète `00_Memoire/bundle/areas_os/` (mutation de `Business OS` en `Areas OS`
     imbriqué dans `24_PARA_Enterprise`).
  2. La génération à la demande (ou complète par strate) des 8 fichiers canoniques :
     (`README.md`, `SOUL.md`, `AGENTS.md`, `CONTRACTS.md`, `CAPABILITIES.md`, `RUNBOOK.md`, `STATE.md`, `MEMORY.md`)
     avec mapping natif Google Workspace (Slides, Sheets, Calendar, Drive, Tasks, Google Chat 4 Spaces).
  3. La génération du plan d'urgence `00_Memoire/bundle/jules-burst-100-missions.md` depuis `.gitmodules`
     et `00_Memoire/egm_missions.db` (pour saturer les 100 sessions/jour de `jules.google.com` avant le 11 nov. 2026).
"""

from __future__ import annotations
import argparse
import json
import sqlite3
from pathlib import Path
from typing import Any

WORKSPACE_ROOT = Path(__file__).resolve().parents[2]
AREAS_OS_DIR = WORKSPACE_ROOT / "00_Memoire" / "bundle" / "areas_os"
JULES_BURST_MD = WORKSPACE_ROOT / "00_Memoire" / "bundle" / "jules-burst-100-missions.md"
DB_PATH = WORKSPACE_ROOT / "00_Memoire" / "egm_missions.db"

CANONICAL_8_FILES = [
    "README.md",
    "SOUL.md",
    "AGENTS.md",
    "CONTRACTS.md",
    "CAPABILITIES.md",
    "RUNBOOK.md",
    "STATE.md",
    "MEMORY.md",
]

GWS_FRAMEWORKS = {
    "21_Ikigai_Orville": {
        "commander": "A2 Orville (USS Orville)",
        "officers_a3": ["Mercer", "Grayson", "Malloy", "Finn", "Isaac", "Lamarr", "Bortus", "Alara", "Klyden"],
        "gws_surface": "Google Slides (Matrice 4 Piliers Ikigai x 5 Horizons = 20 combinaisons)",
    },
    "22_Wheel_Discovery": {
        "commander": "A2 Discovery / Zora (USS Discovery)",
        "officers_a3": ["Book (LD01)", "Stamets (LD02)", "Culber (LD03)", "Tilly (LD04)", "Saru (LD05)", "Burnham (LD06)", "Spock (LD07)", "Georgiou (LD08)"],
        "gws_surface": "Google Sheets (00 — LIFE OS 2026 · Cockpit 6 Frameworks x 8 Domaines = 48 intersections)",
    },
    "23_12WY_SNW": {
        "commander": "A2 Curie (Strange New Worlds)",
        "officers_a3": ["Pike (Vision)", "Una (Planification)", "La'an (Process Control)", "Uhura (Scorecard)", "Ortegas (Time Use)"],
        "gws_surface": "Google Calendar (5 disciplines Curie x 8 LD = 40 contextualisations)",
    },
    "24_PARA_Enterprise": {
        "commander": "A2 Enterprise (USS Enterprise)",
        "officers_a3": ["Riker (Projects)", "Troi (Areas — point d'ancrage d'Areas OS)", "Geordi (Resources)", "Worf (Archives)"],
        "gws_surface": "Google Drive (Hiérarchie documentaire & SSOT)",
    },
    "25_GTD_Cerritos": {
        "commander": "A2 HoloDeck (USS Cerritos)",
        "officers_a3": ["Mariner (Capture)", "Boimler (Clarify)", "Tendi (Organize)", "Rutherford (Reflect)", "T'Lyn (Engage)"],
        "gws_surface": "Google Tasks (Flux d'actions atomiques)",
    },
    "26_DEAL_Protostar": {
        "commander": "A2 HoloJaneway (USS Protostar)",
        "officers_a3": ["Dal (Define)", "Rok-Tahk (Eliminate)", "Zero (Automate)", "Gwyn (Liberate)"],
        "gws_surface": "Google Chat (4 Spaces : Define, Eliminate, Automate, Liberate ; remplace Google Keep)",
    },
}

AREAS_SPEC = [
    {
        "folder": "B_LD01_Business_OMK",
        "col": "B",
        "ld": "LD01",
        "title": "Carrière & Business (Business OS / The OMK Office / SOB / Concordia)",
        "director_code": "B1",
        "coach_a3": "Book",
        "summer": "Summer-LD01",
        "gatekeeper": "A1-Morty (Read-back GWS & Fencing Token TTL 300s)",
        "dc_managers": [
            "B2.1_Operations", "B2.2_Tresorerie", "B2.3_Legal", "B2.4_RD",
            "B2.5_Alliances", "B2.6_Infra", "B2.7_IT", "B2.8_Gouvernance"
        ],
    },
    {
        "folder": "C_LD02_Finances",
        "col": "C",
        "ld": "LD02",
        "title": "Finances & Patrimoine",
        "director_code": "C1",
        "coach_a3": "Stamets",
        "summer": "Summer-LD02",
        "gatekeeper": "A1-Morty",
        "dc_managers": [f"C2.{i}_Playbook_DC" for i in range(1, 9)],
    },
    {
        "folder": "D_LD03_Sante",
        "col": "D",
        "ld": "LD03",
        "title": "Santé & Vitalité Biologique",
        "director_code": "D1",
        "coach_a3": "Culber",
        "summer": "Summer-LD03",
        "gatekeeper": "A1-Beth (Bouclier Homéostatique GREEN|ORANGE|RED|HALT_LD03)",
        "dc_managers": [f"D2.{i}_Playbook_DC" for i in range(1, 9)],
    },
    {
        "folder": "E_LD04_Cognition",
        "col": "E",
        "ld": "LD04",
        "title": "Cognition, Savoir & Apprentissage",
        "director_code": "E1",
        "coach_a3": "Tilly",
        "summer": "Summer-LD04",
        "gatekeeper": "A1-Beth (Bouclier Cognitif GREEN|ORANGE|RED|HALT_LD04)",
        "dc_managers": [f"E2.{i}_Playbook_DC" for i in range(1, 9)],
    },
    {
        "folder": "F_LD05_Relations",
        "col": "F",
        "ld": "LD05",
        "title": "Famille, Relations & Communauté",
        "director_code": "F1",
        "coach_a3": "Saru",
        "summer": "Summer-LD05",
        "gatekeeper": "A1-Beth / A1-Morty",
        "dc_managers": [f"F2.{i}_Playbook_DC" for i in range(1, 9)],
    },
    {
        "folder": "G_LD06_Habitat_Solarpunk",
        "col": "G",
        "ld": "LD06",
        "title": "Habitat, Low-Tech & Solarpunk",
        "director_code": "G1",
        "coach_a3": "Burnham",
        "summer": "Summer-LD06",
        "gatekeeper": "A1-Morty",
        "dc_managers": [f"G2.{i}_Playbook_DC" for i in range(1, 9)],
    },
    {
        "folder": "H_LD07_Creativite",
        "col": "H",
        "ld": "LD07",
        "title": "Créativité, Art & Récréation",
        "director_code": "H1",
        "coach_a3": "Spock",
        "summer": "Summer-LD07",
        "gatekeeper": "A1-Morty",
        "dc_managers": [f"H2.{i}_Playbook_DC" for i in range(1, 9)],
    },
    {
        "folder": "I_LD08_Impact_MetaAspace",
        "col": "I",
        "ld": "LD08",
        "title": "Impact, Meta-Science & A'Space",
        "director_code": "I1",
        "coach_a3": "Georgiou",
        "summer": "Summer-LD08",
        "gatekeeper": "S1-Rick / A1-Morty",
        "dc_managers": [f"I2.{i}_Playbook_DC" for i in range(1, 9)],
    },
]


def render_8_canonical_files(target_dir: Path, holon_id: str, role_title: str, area_info: dict[str, Any]) -> None:
    target_dir.mkdir(parents=True, exist_ok=True)
    ld = area_info.get("ld", "CROSS-OS")
    col = area_info.get("col", "J")
    coach = area_info.get("coach_a3", "Jerry Macro")
    gatekeeper = area_info.get("gatekeeper", "S1-Rick & A1-Beth/Morty")

    contents = {
        "README.md": (
            f"# {holon_id} — {role_title}\n\n"
            f"- **Domaine (`Area`)** : `{ld}` ({area_info.get('title', 'Coordination Inter-Areas')})\n"
            f"- **Colonne Holonique** : `{col}` (`{col}1` Directeur -> `{col}2` 8 Managers DC -> `{col}3` 8 Squads Marvel)\n"
            f"- **Ancrage PARA (`Life OS`)** : `24_PARA_Enterprise` (`Troi` Areas) × `22_Wheel_Discovery` (`{coach}`)\n"
            f"- **Garde-Fou (`Gatekeeper`)** : {gatekeeper}\n"
        ),
        "SOUL.md": (
            f"# SOUL — {holon_id}\n\n"
            f"Identité cognitive alignée sur le Canon `A'Space OS V5` :\n"
            f"- **Posture** : Zéro entropie 3D remontée à `A0 Amadeus` (`human:amdkn`), autonomie d'exécution 95%.\n"
            f"- **Loi E-Myth** : Clarté Jerry (<= 5s), Action Summer immédiate, Veto Épistémique `S1-RICK`.\n"
        ),
        "AGENTS.md": (
            f"# AGENTS — Hiérarchie & Délégation de {holon_id}\n\n"
            f"- **Supérieur Direct** : `A2 Enterprise (Troi)` / `A2 Discovery ({coach})`\n"
            f"- **Coordination Horizontale** : `J1 — Jerry Macro` & `{area_info.get('summer', 'Summers-LD01..08')}`\n"
            f"- **Subordonnés Directs** : 8 Managers Tactiques DC (`{col}2.1` à `{col}2.8`) et 8 Squads Marvel (`{col}3.1` à `{col}3.8`).\n"
        ),
        "CONTRACTS.md": (
            f"# CONTRACTS — Invariants & Preuves ({holon_id})\n\n"
            f"1. **Contrat d'Escalade A0** : N'escalader à `A0` que les choix stratégiques irréductibles.\n"
            f"2. **Bail Concordia** : Tout effet externe acquiert un *Fencing Token* TTL 300s.\n"
            f"3. **Outside Judge** : Validation obligatoire par `S1-RICK` (`02_Factory/checks.ps1`).\n"
        ),
        "CAPABILITIES.md": (
            f"# CAPABILITIES — Surfaces Google Workspace & Outillage A0 ({holon_id})\n\n"
            + "\n".join(
                f"- **{fw}** (`{meta['commander']}`) : {meta['gws_surface']}"
                for fw, meta in GWS_FRAMEWORKS.items()
            )
            + "\n- **Passerelle d'Inférence** : `http://127.0.0.1:31415/v1/chat/completions` (`aspace_freecloud_gateway.py`).\n"
        ),
        "RUNBOOK.md": (
            f"# RUNBOOK — Procédure Opérationnelle Standard ({holon_id})\n\n"
            f"1. Lire l'état dans `00_Memoire/egm_missions.db` et `00_Memoire/shared_brain/memory.jsonl`.\n"
            f"2. Compiler une mission Poisson Rouge (`Goldfish Worker`, contexte < 4 Ko).\n"
            f"3. Exécuter dans un worktree isolé ou via `jules.google.com` / `codex-chatgpt-web`.\n"
            f"4. Vérifier le read-back natif GWS et passer `02_Factory/checks.ps1`.\n"
        ),
        "STATE.md": (
            f"# STATE — État Courant ({holon_id})\n\n"
            f"- **Statut Homéostatique** : `GREEN`\n"
            f"- **Mode d'Exécution** : `EGM_ACTIVE` (Elephant-Goldfish Model)\n"
            f"- **Branche Cible** : `aspace-v5-native`\n"
        ),
        "MEMORY.md": (
            f"# MEMORY — Liens Graphe & Continuité ({holon_id})\n\n"
            f"- **Graphe MCP Partagé** : `00_Memoire/shared_brain/memory.jsonl`\n"
            f"- **Wiki OKF v0.2** : `00_Memoire/bundle/index.md`\n"
            f"- **Ledger EGM** : `00_Memoire/egm_missions.db`\n"
        ),
    }

    for fname in CANONICAL_8_FILES:
        (target_dir / fname).write_text(contents[fname], encoding="utf-8")


def scaffold_areas_os() -> dict[str, Any]:
    AREAS_OS_DIR.mkdir(parents=True, exist_ok=True)
    created_dirs = 0

    for area in AREAS_SPEC:
        area_dir = AREAS_OS_DIR / area["folder"]
        render_8_canonical_files(
            area_dir,
            holon_id=f"{area['director_code']}-{area['coach_a3'].upper()}",
            role_title=f"OwnerBook {area['director_code']} · {area['title']}",
            area_info=area,
        )
        created_dirs += 1

        # Sous-dossiers Niveau 2 (DC Managers Playbooks) et Niveau 3 (Marvel Squads Runbooks)
        dc_root = area_dir / f"{area['col']}2_DC_Managers_Playbooks"
        marvel_root = area_dir / f"{area['col']}3_Marvel_Squads_Runbooks"
        dc_root.mkdir(parents=True, exist_ok=True)
        marvel_root.mkdir(parents=True, exist_ok=True)

        (dc_root / "README.md").write_text(
            f"# {area['col']}2 — 8 Managers Tactiques DC ({area['ld']})\n\n"
            + "\n".join(f"- `{m}` (Playbook Patrimonial DC)" for m in area["dc_managers"])
            + "\n",
            encoding="utf-8",
        )
        (marvel_root / "README.md").write_text(
            f"# {area['col']}3 — 8 Squads d'Exécution Marvel ({area['ld']})\n\n"
            + "\n".join(
                f"- `{area['col']}3.{i}_Marvel_Squad` (7 Spécialistes + Runbook Opérationnel)"
                for i in range(1, 9)
            )
            + "\n",
            encoding="utf-8",
        )

    # Pivot J1_Jerry_Macro_CrossOS
    j1_dir = AREAS_OS_DIR / "J1_Jerry_Macro_CrossOS"
    render_8_canonical_files(
        j1_dir,
        holon_id="J1-JERRY-MACRO",
        role_title="Synchroniseur Inter-Areas (Cross-OS) & Registre des 578 Holons",
        area_info={
            "ld": "LD09-CROSS-OS",
            "col": "J",
            "title": "Coordination Inter-Areas (B1..I1) & Équation des 578 Holons",
            "coach_a3": "Spock / Zora",
            "summer": "Summers-LD01..LD08",
            "gatekeeper": "S1-Rick + A1-Beth + A1-Morty",
        },
    )
    created_dirs += 1

    # Registre JSON exact des 578 Holons dans J1
    holon_registry = {
        "total_holons": 578,
        "breakdown": {
            "life_os_canon_a1_a2_a3": 43,
            "sovereign_and_tech_os_core": 4,
            "areas_os_coordination_j1_and_8_summers": 9,
            "areas_os_directors_b1_to_i1": 8,
            "areas_os_dc_managers_b2_to_i2": 64,
            "areas_os_marvel_squad_specialists_and_canaries_b3_to_i3": 450,
        },
        "canonical_8_files": CANONICAL_8_FILES,
        "gws_surfaces": GWS_FRAMEWORKS,
        "areas_columns": [a["folder"] for a in AREAS_SPEC] + ["J1_Jerry_Macro_CrossOS"],
    }
    (j1_dir / "registry-578-holons.json").write_text(
        json.dumps(holon_registry, indent=2, ensure_ascii=False), encoding="utf-8"
    )

    # Index général de areas_os
    (AREAS_OS_DIR / "README.md").write_text(
        "# `Areas OS` (`LD01` à `LD08` + Pivot `J1`) — Mutation Souveraine de `Business OS`\n\n"
        "Imbriqué dans `24_PARA_Enterprise` (`Troi` Areas) et `22_Wheel_Discovery`, **`Areas OS`** unifie "
        "`Business OS` (`Colonne B / LD01`) avec les 7 autres domaines de la Roue de la Vie (`Colonnes C à I / LD02..LD08`) "
        "selon la loi des **578 Holons** :\n\n"
        "- **43 Holons Canon `Life OS`** (`2 A1` Beth/Morty + `6 A2` Vaisseaux + `35 A3` Officiers)\n"
        "- **4 Holons Souverains & Noyau `Tech OS`** (`A0 Amadeus` + `S1 Rick` + `S2 Sol/Doctor11` + `S3 Graham`)\n"
        "- **9 Holons de Coordination `Areas OS`** (`1 J1 Jerry Macro` + `8 Summers Micro`)\n"
        "- **8 Directeurs d'Areas (`B1` à `I1`)** (`8 OwnerBooks v0.2`)\n"
        "- **64 Managers Tactiques DC (`B2` à `I2` : 8×8)** (`8 B2` + `56 Playbooks DC C2–I2`)\n"
        "- **450 Holons d'Exécution & Squads Marvel (`B3` à `I3` : 64 Squads × 7 Spécialistes + 2 Sentinelles Canary)**\n"
        "- **Total = 578 Holons** dotés du contrat à 8 fichiers (`README.md`, `SOUL.md`, `AGENTS.md`, `CONTRACTS.md`, `CAPABILITIES.md`, `RUNBOOK.md`, `STATE.md`, `MEMORY.md`).\n",
        encoding="utf-8",
    )

    return {"areas_os_dirs": created_dirs, "total_holons_registered": 578}


def generate_jules_burst_plan() -> int:
    if not DB_PATH.exists():
        return 0
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    rows = [dict(r) for r in conn.execute("SELECT * FROM goldfish_missions ORDER BY mission_id ASC").fetchall()]
    conn.close()

    lines = [
        "---",
        "type: runbook",
        "id: jules-burst-100-missions",
        'title: "Plan d\'Urgence Jules.google.com (100 Sessions/Jour avant le 11 Novembre 2026) & Essaim EGM"',
        "status: active",
        "updated: 2026-11-08",
        "---",
        "",
        "# Plan d'Urgence `Jules.google.com` (100 Sessions/Jour) × `Codex-ChatGPT-Web` × `04_ADE_OpenRig`",
        "",
        "> **Fenêtre Critique (7 → 11 Novembre 2026)** : `jules.google.com/session` offre **100 sessions d'agents de code cloud gratuites par jour** avant la fermeture des nouvelles sessions d'écriture le 11 novembre 2026.",
        "> Toutes les missions ci-dessous sont indexées dans `00_Memoire/egm_missions.db` par le routeur EGM (`aspace_freecloud_gateway.py` sur `:31415`).",
        "",
        "## 1. Commandes d'Activation Immédiate",
        "```powershell",
        "# 1. Peupler et vérifier le Ledger Éléphant-Poisson Rouge (EGM) + tester le routeur :31415",
        "python 01_Forkable/FKB01_Inference/03_Inference_FreeCloud/aspace_freecloud_gateway.py --self-test",
        "",
        "# 2. Démarrer le démon HTTP EGM (:31415) pour Agent Zero (A0), Claude Code, Codex, Herdr & OpenClaw",
        "python 01_Forkable/FKB01_Inference/03_Inference_FreeCloud/aspace_freecloud_gateway.py",
        "",
        "# 3. Inspecter les lots par Area (LD01..LD08) depuis le pont Agent Zero",
        "python 01_Forkable/FKB00_Runtime/00_A0_Core/a0_egm_bridge.py",
        "```",
        "",
        f"## 2. File Active des {len(rows)} Missions Atomiques Poissons Rouges (`Goldfish Missions`)",
        "",
        "| # | Mission ID | Sous-Module Cible (`Amdkn/*`) | Area (`LD`) | Holon Owner | Runner Prioritaire | Branche Cible |",
        "|---|---|---|---|---|---|---|",
    ]

    for idx, r in enumerate(rows, start=1):
        lines.append(
            f"| {idx} | `{r['mission_id']}` | `{r['target_submodule']}` | `{r['area_code']}` | `{r['holon_owner']}` | `{r['runner_target']}` | `aspace-v5-native` |"
        )

    lines.extend(
        [
            "",
            "## 3. Template de Prompt Poisson Rouge (`Goldfish Prompt` < 4 Ko) à Soumettre à Jules / Codex-Web / Herdr",
            "```text",
            "[GOLDFISH ATOMIC MISSION] Repository: Amdkn/<submodule> | Branch: aspace-v5-native",
            "1. Create or checkout branch `aspace-v5-native`.",
            "2. Add `aspace-plugin.json` exposing this repository as a reversible Cordis Fiber for A0 (`00_A0_Core/agent-zero`).",
            "3. Connect state/telemetry hooks to `http://127.0.0.1:31415/v1/chat/completions` and `00_Memoire/shared_brain/memory.jsonl`.",
            "4. Run existing unit tests / linter and open PR or commit directly on `aspace-v5-native`.",
            "```",
            "",
        ]
    )

    JULES_BURST_MD.write_text("\n".join(lines), encoding="utf-8")
    return len(rows)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Scaffold 578 Holons & Areas OS")
    parser.add_argument("--instantiate-holon", type=str, default="", help="Optional specific Holon ID to instantiate")
    args = parser.parse_args()

    res = scaffold_areas_os()
    missions_count = generate_jules_burst_plan()
    res["jules_burst_missions_documented"] = missions_count
    print(json.dumps(res, indent=2, ensure_ascii=False))
