---
okf_version: "0.2"
---
# Mémoire V5 (bundle OKF)

* [Journal append-only](log.md) - historique chronologique de chaque réponse (le plus récent en bas)
* [Contexte courant](concepts/contexte-v5.md) - état évolutif de V5, préférences, décisions
* [Règles de collaboration](concepts/regles-utilisateur.md) - échecs passés et règles de comportement
* [Environnement Herdr](concepts/herdr.md) - spaces, tabs, hc, protocole d'orchestration
* [Outils mémoire](concepts/outils-memoire.md) - DOX, OKF, WikiLLM, Graphify : usage dans V5
* [Patterns Fable 5 (Mythos)](concepts/fable5-traces.md) - invariants d'exécution extraits des traces HuggingFace Fable 5
* [IDE VS Code, Orca, Herdr, OpenCode & Pi Antifragile](concepts/vscode-antifragile.md) - configuration .vscode, Orca, Herdr, OpenCode 1.19.5, Pi 1.5.0, .mcp.json, doctor.ps1 et 27 outils CLI garantis
* [Aspace Software Factory](concepts/aspace-factory.md) - fusion des 12 architectures Software Factory (cœur DeepSeek Superagent + DeepSeek Harness dsh + GitHub Issues/PRs/Actions/Discussions/Projects/Wiki/Security/Insights)
* [Pi 1.5.0, Pi Durable & Durable Subagents](concepts/pi-durable-subagents.md) - architecture agnostique Pi Durable (earendil.com/posts/pi-durable) + pi-durable-subagents (checkpoints SQLite, requestId idempotent, writerLock, modelPool failover, handoff & search_history)
* [Protocole d'Ambition « Modo de Volar »](concepts/ambition-modo-de-volar.md) - les 4 vecteurs d'ambition de Felix Rieseberg (Speed, Altitude, Depth & Outside Judge, Range)
* [Architecture Holonique des 3 OS (578 Holons)](concepts/aspace-3os-holons.md) - canon Drive : Tech OS (13), Life OS 2026 (43, Cockpit 6×8), Areas OS (522, 3 couches B1–I1/B2–I2/B3–I3 dans PARA, SOB/Liberty Ride, Concordia TTL 300s, OMK Office) & Triangle E-Myth
* [Areas OS, Boucle S0..S3, 0D..10D & Inférence Sakana Fugu](concepts/sakana-fugu-inference.md) - LD00/LD09, Rory 4P + MiroFish, Fugu TRINITY, LFM3 :9931, codex-chatgpt-web zéro télémétrie
* [Jumeau Numérique CEO 24/7 (Automaton) & Cube Farm 3 Étages OS](concepts/ceo-automaton-cubefarm.md) - forks souverains dans `01_Forkable/FKB00_Runtime/01_Holo_TriptyqueCore/automaton` (`A0 Amadeus`) et `01_Forkable/FKB03_3DWorlds/cubefarm` (3 Étages OS Holoniques)
* [Gateway MCP & Mémoire Partagée Multi-Harness](concepts/mcp-shared-memory.md) - Cerveau partagé unifié (`FKB02_Memory`) synchronisant Claude, Codex, OpenCode, Pi, Antigravity, Herdr, Orca et ChatGPT Web sur `memory.jsonl`
* [FKB07 Money Maker & Productized B2B Services](concepts/b2b-money-maker.md) - Moteurs B2B structurés en 6 catégories (Trading, Video, Website/Infra, Learning, Executive/BI, 3D/CAD) (90-98%) inspirés de Corey Ganim (Impeccable, OpenMontage, DeepTutor, OpenMausBot, text-to-cad, open-notebook, changedetection, uptime-kuma)
* [Neuro-Tabular Wargame & Quatuor Prédictif](concepts/neuro-tabular-wargame.md) - AutoGluon (Mitra-v2, Chronos-2, PathFM) x Google (TabFM, TimesFM) x CEO-Bench déterministe (GBrain, Gstack, GSD, Superpowers)
* [Structure code graphifié](concepts/contexte-v5.md) - résultats Graphify V5
* [Distillation Argon × Fable 5 → Gemini 3.8 Flash](concepts/argon-flash38-distillation.md) - Protocole Zero-Quota-Burn & 1-Turn Closure
* [Noyau Souverain A0 : Micro-Noyau Cordis × Agent-Zero × Tri-Horizon RSI](concepts/a0-cordis-recursive-factory.md) - Architecture Fork-Mutant A0 (`00_A0_Core`, `04_ADE_OpenRig`, `05_Recursive_RSI`, Mono-Gateway FreeCloud 3-en-1 `:31415`, Prime-Agent RLM, WikiSkill/AQuA, Dream-RSI/RRSI)
* [Areas OS (`LD01..LD08` + `J1` — 578 Holons)](areas_os/README.md) - Mutation de `Business OS` en `Areas OS` imbriqué dans `24_PARA_Enterprise` (8 Colonnes `B..I`, Directeurs `B1..I1`, 64 Managers DC `B2..I2`, 450 Spécialistes Marvel `B3..I3`, contrat à 8 fichiers)
* [Plan d'Urgence Jules 100 Sessions/Jour & Essaim EGM](jules-burst-100-missions.md) - File active des missions Poissons Rouges (`00_Memoire/egm_missions.db`) pour `jules.google.com`, `codex-chatgpt-web` et `04_ADE_OpenRig`
* [Wargame Au-Delà d'Argon : Hyperviseur Cordis × Automaton Runtime × RigInfinity (Rust) × Reviewer-Security OWASP](concepts/wargame-riginfinity-cordis-daemon.md) - Loi du Daemon Maître unique, fusion `OpenRig × Infinity` en `Amdkn/RigInfinity`, triage OWASP Top 10 et structuration de `02_Factory/` en 6 catégories
- [n8n-hooks-freecompute-scion.md](concepts/n8n-hooks-freecompute-scion.md) — GitHub as n8n Primitive (5 Node Families), Deterministic Hooks (`exit 2`), `FreeComputeAPI` & Anthropic Scion Sparse Checkouts.
- [WARGAME_LAUNCH_AUDIT.md](areas_os/B_LD01_Business_OMK/WARGAME_LAUNCH_AUDIT.md) — Audit Wargame Prédictif de Lancement Business OS (LD01) & Nœuds Jetables (MiroFish x Mitra-v2 x TimesFM 3.0 x PathFM).
- [PLAYBOOK_FDE_SPRINT.md](areas_os/B_LD01_Business_OMK/PLAYBOOK_FDE_SPRINT.md) — Playbook Forward Deployed Engineering (Palantir x Veric 5-Step Model).
- [PLAYBOOK_GTME_CLAY_TREG_APIFY.md](areas_os/B_LD01_Business_OMK/PLAYBOOK_GTME_CLAY_TREG_APIFY.md) — Playbook Go-To-Market Engineering (Clay x Kiln x Treg x Apify).
- [PLAYBOOK_FOA_6_LEVELS.md](areas_os/C_LD02_Finances/PLAYBOOK_FOA_6_LEVELS.md) — Playbook Family Office Agentique en 6 Niveaux (Great Wealth Transfer).
- [4d-ipbd-chronos-muse-cascade.md](concepts/4d-ipbd-chronos-muse-cascade.md) — Le Cascadeur IPBD 4D : Isomorphisme 3D (TabFM/Mitra-v2 Sheets) -> 4D (TimesFM/Chronos-2 Calendar 12WY & DEAL Muse Chat).
- [ROAD_TO_MARKET_PLAN.md](areas_os/B_LD01_Business_OMK/ROAD_TO_MARKET_PLAN.md) — Plan Stratégique Road to Market ASpace MarketPlace (Projet Picard LD01 / 100 Comptes B2B).
- [free-cloud-orchestration-studio-gas-retool.md](concepts/free-cloud-orchestration-studio-gas-retool.md) — Orchestration Cloud Gratuite : Workspace Studio Triggers, Google Apps Script (GAS), Retool, Zenphi & Quota Accounting.
