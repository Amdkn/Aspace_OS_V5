---
type: Architecture
title: Gateway MCP & Mémoire Partagée Multi-Harness
description: Cerveau partagé unifié (Shared Brain) basé sur @modelcontextprotocol/server-memory synchronisant Claude, Codex, OpenCode, Pi, Antigravity, Herdr, Orca et ChatGPT Web sur memory.jsonl.
tags: [memoire, mcp, shared-brain, agnosticite, multi-harness]
generated: { by: agent/antigravity, at: 2026-11-06T06:44:00-05:00 }
status: active
---

# Gateway MCP & Mémoire Partagée Multi-Harness (`FKB02_Memory`)

La Gateway MCP Mémoire Partagée constitue la 4ème couche du système de mémoire d'Aspace OS V5. Elle résout la fragmentation épistémique entre les différents harnesses d'agents (**Claude Code/Desktop**, **OpenAI Codex**, **OpenCode**, **Pi**, **DeepSeek**, **Antigravity**, **Herdr**, **Orca**, et **ChatGPT Web**).

## 1. Principe & Standard Ouvert

Tous les agents pointent sur le serveur officiel Anthropic `@modelcontextprotocol/server-memory` (fork souverain [Amdkn/servers](https://github.com/Amdkn/servers) dans `01_Forkable/FKB02_Memory/servers/src/memory`).

- **Chemin Universel Déterministe** :
  `MEMORY_FILE_PATH = "C:\Users\amado\Aspace OS V5\00_Memoire\shared_brain\memory.jsonl"`
- **Persistance Atomique** : Format JSONL avec verrou concurrentiel `FileLock` (`O_EXCL`) interdisant toute collision d'écriture lors de sessions multi-agents simultanées.
- **9 Outils Exposés** : `create_entities`, `delete_entities`, `create_relations`, `delete_relations`, `add_observations`, `delete_observations`, `read_graph`, `search_nodes`, `open_nodes`.

## 2. Intégration Holonique (5 Composants Forkés)

1. **`servers` (`src/memory`)** : Moteur de graphe MCP officiel.
2. **`graphify`** : Moteur d'analyse AST et de graphe sémantique global.
3. **`dox`** : Contrat de gouvernance AGENTS.md.
4. **`knowledge-catalog`** : Spécification OKF v0.2 des pages de concepts.
5. **`llm-wiki`** : Pattern de base de connaissances continue de Karpathy (Gist souverain Amdkn).

## 3. Instruction Système Universelle

> *Avant de répondre, interroger la mémoire partagée (`search_nodes`, `read_graph`) ; après toute décision/action, enregistrer dans le graphe (`create_entities`, `add_observations`, `create_relations`).*
