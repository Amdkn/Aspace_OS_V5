#!/usr/bin/env python3
"""
Refactorisation Holonique de LD01 :
1. Déplacement de B_LD01_Business_OMK -> B_LD01_Business_AMP via Git
2. Structuration de la Pyramide C0 -> C3 :
   - C0 : AMP (A'Space MarketPlace) - Platform Engine & Infrastructure Transactionnelle
   - C1 : Coachs CEO & Architecture (FDE + GTME + FOA)
   - C2 : Offres CEO First-Party (1P) : The OMK Office, Ali Kaly Bana Real Estate, Liberty Ride
   - C3 : Catalogue Grand Public & Bots IA
3. Création du dossier et du manifeste The_OMK_Office/README.md
4. Mise à jour de toutes les références dans les fichiers de configuration, scripts et index
"""

import os
import re
import sys
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

def run_cmd(cmd, check=True):
    print(f"Running: {cmd}")
    res = subprocess.run(cmd, shell=True, cwd=str(ROOT), capture_output=True, text=True)
    if res.returncode != 0 and check:
        print(f"STDERR: {res.stderr}")
        raise RuntimeError(f"Command failed: {cmd}")
    return res.stdout.strip()

def main():
    old_dir = ROOT / "00_Memoire" / "bundle" / "areas_os" / "B_LD01_Business_OMK"
    new_dir = ROOT / "00_Memoire" / "bundle" / "areas_os" / "B_LD01_Business_AMP"

    # 1. Copie vers le nouveau dossier puis git add et git rm
    if old_dir.exists() and not new_dir.exists():
        import shutil
        print(f"Copying {old_dir} to {new_dir}...")
        shutil.copytree(str(old_dir), str(new_dir))
        run_cmd('git add "00_Memoire/bundle/areas_os/B_LD01_Business_AMP"')
        run_cmd('git rm -r --cached "00_Memoire/bundle/areas_os/B_LD01_Business_OMK"')
        shutil.rmtree(str(old_dir))
        print("Folder migrated and staged in Git successfully.")
    elif new_dir.exists():
        print("Target B_LD01_Business_AMP already exists.")
        if old_dir.exists():
            import shutil
            run_cmd('git rm -r --cached "00_Memoire/bundle/areas_os/B_LD01_Business_OMK"', check=False)
            shutil.rmtree(str(old_dir), ignore_errors=True)
    else:
        print("Neither old_dir nor new_dir in expected state.")

    # 2. Création de The_OMK_Office sous B_LD01_Business_AMP
    omk_showcase_dir = new_dir / "The_OMK_Office"
    omk_showcase_dir.mkdir(parents=True, exist_ok=True)

    omk_readme_content = """---
title: "The OMK Office — Vitrine First-Party (1P) Couche C2 d'A'Space MarketPlace"
type: concept
status: active
updated: 2026-11-09
tags:
  - omk-office
  - first-party-showcase
  - 1p-services
  - couche-c2
  - b2b-automation
  - proof-first
---

# The OMK Office — Vitrine First-Party (1P) Couche C2

> **Positionnement Holonique & Rôle dans l'Écosystème** :
> **The OMK Office** est la vitrine de services B2B et d'automatisation de référence opérée directement par `A0 Amadeus` et le holon `B1-BOOK` sur **AMP (A'Space MarketPlace)**.
> De la même manière qu'**Amazon Basics** prouve la rentabilité et les cas d'usage d'**Amazon.com / AWS**, The OMK Office délivre des services à fort ROI contractuel pour prouver l'excellence industrielle d'A'Space MarketPlace aux clients C1 et C2.

---

## 1. La Pyramide C0 → C3 d'A'Space MarketPlace

| Strate | Rôle dans l'Écosystème | Équivalent Amazon | Offre & Mécanisme de Revenu |
|---|---|---|---|
| **C0 · Architecte** | **AMP (A'Space MarketPlace) + CoolEmbrl OS** | **AWS + Blue Origin** | Infrastructure souveraine, baux SQL Fencing Token (TTL 300s), compute gratuit FreeLLMAPI/FreeComputeAPI, mémoire et gouvernance. |
| **C1 · Coachs CEO** | **FDE + GTME + FOA** | **AWS Solutions Architects** | Audits chirurgicaux, déploiement sur site (Palantir/Veric) et architecture patrimoniale. |
| **C2 · Offres CEO (1P)** | **The OMK Office / Ali Kaly Bana / Liberty Ride** | **Amazon Basics (1P)** | **Services B2B livrés par RigInfinity avec ROI contractuel garanti (Administration, Workflows Make/Openbot, Automatisation).** |
| **C3 · Grand Public** | **Assistants & Bots IA** | **Amazon.com Retail** | Catalogue de bots souverains et d'humains à la demande (CEL sandbox, Escrow déterministe). |

---

## 2. Modèle Économique & Objectifs de The OMK Office (C2 1P)

- **Modèle Tarifaire** : 100 clients récurrents à **$300/an** (ou $30/mois) = **$360 000/an brut** (ou $36 000/an récurrents de base) $\rightarrow$ **$10 000/mois net injecté dans A0**.
- **Services Délivrés** :
  1. *Audit Proof-First & Détection de Failles* (SEO, IA, Processus) sans engagement initial.
  2. *Automatisation Documentaire & Workflows* (Make, Openbot, n8n, GWS).
  3. *Système de Standardisation Opérationnelle* (SOP, Dify, RAG local).
- **Garantie Souveraine** : Tout flux opéré par The OMK Office respecte l'**ADR-004** (Juridiction US / Cincinnati-NKY Metro, exclusion stricte France/UE).
"""
    (omk_showcase_dir / "README.md").write_text(omk_readme_content, encoding="utf-8")
    print("Created The_OMK_Office/README.md successfully.")

    # 3. Mise à jour de README.md de B_LD01_Business_AMP
    readme_path = new_dir / "README.md"
    readme_content = """# B1-BOOK — OwnerBook B1 · Carrière & Business (AMP A'Space MarketPlace [C0] × The OMK Office [C2 1P] / SOB / Concordia)

- **Domaine (`Area`)** : `LD01` (Carrière & Business : Moteur de Plateforme C0 AMP & Vitrine 1P C2 The OMK Office)
- **Colonne Holonique** : `B` (`B1` Directeur -> `B2` 8 Managers DC -> `B3` 8 Squads Marvel)
- **Ancrage PARA (`Life OS`)** : `24_PARA_Enterprise` (`Troi` Areas) × `22_Wheel_Discovery` (`Book`)
- **Garde-Fou (`Gatekeeper`)** : A1-Morty (Read-back GWS & Fencing Token TTL 300s, ADR-004 US Geo-Fencing)

---

## Pyramide Holonique des 4 Strates Commerciales (C0 → C3)

```mermaid
flowchart TD
    C0["C0 · Infrastructure Souveraine & Moteur de Plateforme<br/><b>AMP (A'Space MarketPlace) + CoolEmbrl OS</b><br/><i>(Équivalent AWS / Blue Origin)</i>"]
    C1["C1 · Services Architecture & Accompagnement CEO<br/><b>FDE + GTME + FOA</b><br/><i>(Équivalent Solutions Architects)</i>"]
    C2["C2 · Vitrines Propriétaires First-Party (1P)<br/><b>The OMK Office</b> (B2B Admin & Auto) · <b>Ali Kaly Bana</b> · <b>Liberty Ride</b><br/><i>(Équivalent Amazon Basics 1P)</i>"]
    C3["C3 · Catalogue Grand Public & Bots IA Autonomes<br/><b>Assistants Spécialisés & Humains à la Demande</b><br/><i>(Équivalent Amazon.com Retail)</i>"]

    C0 --> C1
    C1 --> C2
    C2 --> C3
```

- **Moteur de Plateforme (C0)** : [Aspace_MarketPlace/](Aspace_MarketPlace/) — Master Plan, Mission, Specs, Design, Roadmap, PRD, BMC.
- **Vitrine Propriétaire 1P (C2)** : [The_OMK_Office/](The_OMK_Office/) — Offres B2B, Services d'automatisation, Proof-First Cohorte 25.
- **Règles d'Exclusion & Juridiction** : ADR-004 (`Cincinnati / Northern Kentucky Metro`, interdiction formelle France & UE).
"""
    readme_path.write_text(readme_content, encoding="utf-8")
    print("Updated B_LD01_Business_AMP/README.md.")

    # 4. Remplacer B_LD01_Business_OMK par B_LD01_Business_AMP dans les fichiers ciblés
    files_to_update = [
        ROOT / "00_Memoire" / "bundle" / "index.md",
        ROOT / "00_Memoire" / "bundle" / "areas_os" / "J1_Jerry_Macro_CrossOS" / "registry-578-holons.json",
        ROOT / "00_Memoire" / "google_tasks_ld01_state.json",
        ROOT / "01_Forkable" / "FKB00_Runtime" / "02_PredictiveWargame_MachineLearning" / "wargame_business_launch_auditor.py",
        ROOT / "01_Forkable" / "FKB07_Money_Maker" / "aspace_road_to_market_engine.py",
        ROOT / "01_Forkable" / "FKB07_Money_Maker" / "proof_first_outbound_pipeline.py",
        ROOT / "02_Factory" / "02_Holons_578_QualityControl" / "scaffold-578-holons.py",
        ROOT / "02_Factory" / "gws_tasks_road_to_market_activator.py",
        ROOT / "02_Factory" / "hooks" / "aspace_turn_persistence_daemon.py",
    ]

    for p in files_to_update:
        if p.exists():
            txt = p.read_text(encoding="utf-8")
            if "B_LD01_Business_OMK" in txt:
                new_txt = txt.replace("B_LD01_Business_OMK", "B_LD01_Business_AMP")
                p.write_text(new_txt, encoding="utf-8")
                print(f"Updated references in: {p.relative_to(ROOT)}")

    # 5. Mettre à jour l'index.md pour ajouter la référence à The_OMK_Office
    index_path = ROOT / "00_Memoire" / "bundle" / "index.md"
    idx_content = index_path.read_text(encoding="utf-8")
    if "The_OMK_Office" not in idx_content:
        # Insérer après COHORTE_25_PROSPECTS_AUDITS.md
        target = "- [COHORTE_25_PROSPECTS_AUDITS.md](areas_os/B_LD01_Business_AMP/COHORTE_25_PROSPECTS_AUDITS.md)"
        replacement = target + "\n- [The_OMK_Office/README.md](areas_os/B_LD01_Business_AMP/The_OMK_Office/README.md) — Vitrine First-Party (1P) Couche C2 opérée sur AMP (The OMK Office B2B Services)."
        if target in idx_content:
            idx_content = idx_content.replace(target, replacement)
            index_path.write_text(idx_content, encoding="utf-8")
            print("Added The_OMK_Office reference to 00_Memoire/bundle/index.md.")

    # 6. Append-only au log.md
    log_path = ROOT / "00_Memoire" / "bundle" / "log.md"
    log_entry = "* **Note**: [2026-11-09 · Refactorisation Holonique LD01 B_LD01_Business_AMP & Sanctuarisation C0/C2] Renommage physique du dossier `00_Memoire/bundle/areas_os/B_LD01_Business_OMK` vers `B_LD01_Business_AMP` via git mv. Sanctuarisation de la Pyramide Commerciale C0->C3 : AMP (C0 Platform Engine) et The OMK Office (C2 Vitrine 1P / First-Party B2B Showcase avec `The_OMK_Office/README.md`). Mise a jour des 9 fichiers de references et d indexation.\n"
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(log_entry)
    print("Appended log entry to log.md.")

if __name__ == "__main__":
    main()
