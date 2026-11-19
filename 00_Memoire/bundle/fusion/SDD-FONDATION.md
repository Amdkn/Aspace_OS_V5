---
okf_version: "0.2"
type: Architecture
title: "SDD-FONDATION — Architecture Logicielle en 3 Couches & 3 Noyaux (L0 / L1 / L2 · ADR-13)"
enonce_ref: "00_Memoire/bundle/fusion/FUSION-ENONCE.md"
enonce_sha256: "41889edb9c468ea62ee4641328c0e6f4bac2c618b81da751eebd2af4c05f648d"
---

# SDD-FONDATION — Architecture Technique en 3 Couches & 3 Noyaux (`ADR-13`)

## 1. Vue d'Ensemble & Trajectoire `Python → Hybride → Rust`

```mermaid
flowchart TB
    S0["S0 : Amadou Kone (human:amdkn) · Ratification & Veto a2p"]
    subgraph L2["COUCHE L2 — SURFACES HOLONIQUES 3 OS (578 Holons)"]
        T["Tech OS (13 Holons · S1-S3)"]
        L["Life OS 2026 (43 Holons · 6x8 Cockpit)"]
        A["Areas OS (522 Holons · LD01..LD08 + J1 · LibertyRide2 / OMK)"]
        W3D["Surface 3D & Cockpit (City-Office / CubeFarm / Herdr-App)"]
    end
    subgraph L1["COUCHE L1 — LES TROIS NOYAUX & ORGANES RATTACHÉS (ADR-13)"]
        AME["NOYAU ÂME (Automaton) : Organe K1 (Gouvernance 13->1, RSI) + Organe K4 (Mémoire FKB02, Skills)"]
        SN["NOYAU SYSTÈME NERVEUX (Infinity) : Bus Nerveux / Hibernation L0 + Organe K3 (Inférence & FreeCloud)"]
        CORPS["NOYAU CORPS (OpenRig) : Organe K2 (Multi-Harness, Anything FKB04, 3D) + Organe K5 (Prédictif & B2B)"]
    end
    subgraph L0["COUCHE L0 — SOCLE INVARIANT & PONT HYBRIDE PHASE 2"]
        C1["C1 EventJournal (fondation-13-1/router.rs + aspace_foundation_kernel.py verrou O_EXCL)"]
        C2["C2 R10Receipt (fondation-13-1/lib.rs V1-V8 + r10-receive.exe)"]
        C3["C3 EpistemicCitation (fondation-13-1/memory.rs M1-M8 + memory.jsonl)"]
        C4["C4 FiberContract & RigInfinity Daemon (cargo test WSL/Linux + MODULES-LOCK.json)"]
        C5["C5 DeletionProof (test_foundation_deletion_suite.py · 29 FUSIONNÉ)"]
    end
    S0 --> AME
    L2 <--> L1
    AME <--> L0
    SN <--> L0
    CORPS <--> L0
```

---

## 2. Couche L0 — Socle Invariant & État Vérifié Cycle 4

| Composant L0 | Chemin exact dans le dépôt | Langage / Runtime | État vérifié Cycle 4 |
|---|---|---|---|
| **Fondation 13→1** | `01_Forkable/FKB00_Runtime/00_A0_Core/fondation-13-1/` | Rust (0 dépendance) | **Compilé & VERT 100/100** (`cargo test` Windows/GNU après `.gitattributes` `eol=lf` sur fixtures) ; 6 binaires compilés (`r10-receive`, `route-dispatch`, `recall-fact`, ...) ; fonctions `F1-8..F1-11` restantes (`PARTIEL`) |
| **RigInfinity Daemon** | `01_Forkable/FKB00_Runtime/01_Holo_TriptyqueCore/RigInfinity` | Rust (`crates/infinity-daemon`) | **Compilé & VERT 105/105** sous WSL2 `UmbrelOS` Linux (`cargo test`, POSIX `UnixListener` / PTY / signaux) ; les **9 modules F8** portés sont validés ; `gitlink 160000` + `lease/dispose` restent (`PARTIEL`) |
| **Noyau L0/L1 & Pont Phase 2** | `01_Forkable/FKB00_Runtime/00_A0_Core/aspace_foundation_kernel.py` | Python ↔ Binaires Rust | **ACTIF PHASE 2 HYBRIDE** : verrou atomique `O_EXCL` sur JSONL L0, zéro wrap `% 1000`, parité 1:1 prouvée par invocation directe des binaires Rust `r10-receive` et `route-dispatch` sur `anchor-001/002/026` |
| **AspaceFiberHost** | `01_Forkable/FKB00_Runtime/00_A0_Core/aspace-fiber-host/` | TypeScript / Vitest | **`PARTIEL`** (`file:../cordis/*` et `cordis_socket` vers `RigInfinity` restants) |
| **Verrou & Gates Usine** | `01_Forkable/MODULES-LOCK.json` + `02_Factory/checks.ps1` | Python / PowerShell | **VERT** (6/6 `check-modules-lock.py` ; 7/7 `checks.ps1` ; `CARGO_HOME`/`RUSTUP_HOME` auto-réparés dans `doctor.ps1`) |

---

## 3. Couche L1 — Câblage Effectif des Trois Noyaux (`ADR-13`)

### 3.1 `NOYAU ÂME` (`Automaton` — Organes `K1` et `K4`)
- **Organe `K1`** : `01_Forkable/FKB00_Runtime/00_A0_Core/a0_recursive_factory.py` (orchestration RLM, WikiSkill gate `δ ≥ 1.7 %`, Dream-RSI) câblé sur `EventJournal` + `R10Ledger`.
- **Organe `K4`** :
  - `01_Forkable/FKB00_Runtime/00_A0_Core/aspace_fkb02_memory_organ.py` (absorbe les **9 modules `FKB02_Memory`** : `HierarchicalCASStore`, `AutoOntologyCompiler` DAG+contradictions, `build_clm_anchored_context`, `validate_dox_contract`, `HybridBrainIndex` BM25+n-gram+graphe+`M1-M8`, `ASTCodeGraphBuilder`, `MultiBrainNamespaceManager`, `validate_okf_bundle`).
  - `01_Forkable/FKB02_Memory/01_BillionContxtLanguage_AutoOnthology/neuro_symbolic_bridge.py` (`memory.jsonl`).
  - Primitives `caveman`, `claude-mem`, `hermes-agent` portées dans `aspace_fkb04_anything_organ.py`.

### 3.2 `NOYAU SYSTÈME NERVEUX` (`Infinity` — Bus Nerveux L0 & Organe `K3`)
- **Bus Nerveux & Fibres** : `RigInfinity` (`crates/infinity-daemon` : hibernation pure-data, `RAP`, `MCP proxy`, `openrig_terminal.rs`), `aspace_foundation_kernel.py` (`l0_foundation_journal.jsonl`, `l0_foundation_ledger.jsonl` sous verrou `O_EXCL`).
- **Organe `K3`** :
  - `01_Forkable/FKB01_Inference/03_Inference_FreeCloud/aspace_freecloud_gateway.py` (initialisation SQLite **paresseuse** via `get_ledger()`/`get_router()`, port `:31415`).
  - `01_Forkable/FKB00_Runtime/00_A0_Core/aspace_discovery_catalog.py` (absorbe `M118 04_Inference_Youtube_Discovery_Registry` en code natif hors répertoire source).

### 3.3 `NOYAU CORPS` (`OpenRig` — Organes `K2` et `K5`)
- **Organe `K2`** :
  - `01_Forkable/FKB00_Runtime/00_A0_Core/aspace_freecompute_router.py` (routage exécution sans `FreeVPS`).
  - `01_Forkable/FKB00_Runtime/00_A0_Core/aspace_fkb04_anything_organ.py` (absorbe `CLI-Anything`, `agent-browser` `@ref` + garde anti-CAPTCHA, `agent-desktop` `no_focus_steal`, `api-anything` HAR->MCP, `rea` inspection clean-room D12).
- **Organe `K5`** :
  - `01_Forkable/FKB07_Money_Maker/aspace_marketplace_engine.py` + `02_Video/aspace_video_studio_foundation.py` + `aspace_discovery_catalog.py` (`M117 00_Marketplace_YoutubeSkills` absorbé nativement) + `02_PredictiveWargame_MachineLearning/{triptych_autogluon_engine,wargame_tabular_engine}.py`.
