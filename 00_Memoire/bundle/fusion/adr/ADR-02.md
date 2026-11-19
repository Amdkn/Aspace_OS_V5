---
okf_version: "0.2"
type: Decision
title: "ADR-02 — Daemon Maître Unique (`RigInfinity`) vs Multi-Daemons Concurrents"
enonce_ref: "00_Memoire/bundle/fusion/FUSION-ENONCE.md"
enonce_sha256: "41889edb9c468ea62ee4641328c0e6f4bac2c618b81da751eebd2af4c05f648d"
---

# ADR-02 — Daemon Maître Unique (`RigInfinity`) vs Multi-Daemons Concurrents
- **Statut** : `ACCEPTÉE`
- **Conflit** : `OpenBot` spawne jusqu'à 10 processus par bot ; `herdr-core`, `openrig`, `openclaw`, `orca`, `agent-desktop`, `cubefarm`/`agent-office` et `OpenMausBot` introduisent chacun leur propre démon ou serveur local concurrent.
- **Décision** : **Loi du Daemon Maître Unique** : un seul processus superviseur Rust (`riginfinity-daemon` sur `127.0.0.1` loopback uniquement) porte l'état d'exécution, les sessions PTY (`openrig_terminal.rs`), les proxys MCP (`mcp_proxy.rs`), les callbacks RAP et le source-control WAL. Les skins bots (`OpenMuse`, `OpenDots`, `OpenDuet`) sont fusionnés comme traits sur la plateforme `OpenBot` unifiée en Rust. Les applications visuelles (`herdr-app`, `cubefarm`, `city-office`) sont de pures surfaces clientes sans autorité de daemon concurrent.
- **Invariant** : `ps` en production runtime ne compte qu'**1 processus daemon maître** pour l'orchestration agentique.
- **Modules résolus** : `RigInfinity`, `infinity`, `openrig`, `agent-zero`, `openbot`, `openmuse`, `OpenDots`, `OpenDuet`, `herdr-core`, `herdr`, `openclaw`, `orca`, `t3code`, `OpenMausBot`, `cubefarm`, `agent-office`, `city-office`.
