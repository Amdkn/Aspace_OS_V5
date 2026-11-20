---
okf_version: "0.2"
type: DecisionLog
title: "Journal des Décisions Réversibles — Fusion Fondation (Cycle 7)"
enonce_ref: "00_Memoire/bundle/fusion/FUSION-ENONCE.md"
enonce_sha256: "41889edb9c468ea62ee4641328c0e6f4bac2c618b81da751eebd2af4c05f648d"
---

# DECISIONS — A'Space OS V5 (Cycle 7)

| Date | Décision | Raison | Alternative écartée |
|---|---|---|---|
| 2026-11-19 | Utiliser `ubuntu-latest` dans `.github/workflows/foundation-proof.yml` | Compile et exécute `RigInfinity` nativement en sockets Unix sans WSL tout en exécutant `pwsh` sur `02_Factory/checks.ps1` via chemins `/` portables | `windows-latest` dépourvu de WSL UmbrelOS préinstallé pour `RigInfinity` |
| 2026-11-19 | Initialiser récursivement en CI uniquement les sous-modules exercés par les preuves (dont `RigInfinity == 95e95f9`) | Évite plusieurs Go d'historiques non utilisés dans les 3 suites tout en garantissant 100 % des oracles et tests Rust fail-closed | `git submodule update --init --recursive` global sur l'ensemble des 101 gitlinks |
| 2026-11-19 | Retenir `F-CORPS-05` · `M074 tradingview-indicator-search-mcp-server` seul pour la Vague 1 `CORPS` (maintien explicite de `M066 TradingView-Unified-MCP` en `PARTIEL`) | `M074` possède 100 % de son cœur testable en parité `==` exacte contre Node v24 + 6 fixtures JSON réelles sans réseau ni navigateur, contrairement à `M066` (~3 200 lignes d'automatisation CDP chart/alertes live) | Fusion groupée `M074 + M066` ou choix d'une famille multi-services/3D/Swift/win32 bloquée en CI Linux |
| 2026-11-20 | Retenir `F-CORPS-02` · `M001 a0-plugins` seul pour la Vague 2 `CORPS` (`K2`) dans `aspace_plugin_registry_organ.py` et ajouter sa garde de pin `fa8df85` en CI | `M001` réunit un cœur Python pur déterministe (`scripts/*` + `aspace-a0-plugins-adapter`, 235 dossiers/230 indexés, bornes YAML/PNG/release 3 étapes) vérifiable 1:1 contre l'upstream `fa8df85` sans réseau par défaut, contrairement aux binaires `RETENU` ou aux harnais Electron/PTY/CUA | Fusion groupée de `F-CORPS-02` ou portage de `M058`/`M095` sans environnement graphique natif |
