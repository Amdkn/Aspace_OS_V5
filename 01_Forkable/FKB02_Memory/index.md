# FKB02_Memory — Gateway MCP & Mémoire Partagée Multi-Harness

> **Cerveau Partagé Universel (Shared Brain)** : FKB02 unifie la mémoire épistémique de l'intégralité des harnesses de travail (**Claude Code/Desktop**, **Codex**, **OpenCode**, **Pi**, **DeepSeek Harness & Superagent**, **Herdr**, **Orca**, **Antigravity**, et **ChatGPT Web**) autour d'un Graphe de Connaissances MCP local et souverain synchronisé en temps réel.

---

## 1. Topologie des Composants Souverains (5 Sous-Modules)

| Composant | Rôle dans l'Architecture Mémoire | Dépôt Source Amdkn | Type de Ressource |
|---|---|---|---|
| **`servers` (src/memory)** | **Moteur de Graphe MCP Officiel** : Implémentation TypeScript (@modelcontextprotocol/server-memory) avec 9 outils et verrou multi-processus. | [Amdkn/servers](https://github.com/Amdkn/servers) | Serveur MCP Stdio / JSONL |
| **`graphify`** | **Moteur de Graphe Sémantique & Visualisation** : Extraction AST, graphe de dépendances, détection de communautés et rapport HTML/JSON. | [Amdkn/graphify](https://github.com/Amdkn/graphify) | CLI Python (`graphify.exe`) |
| **`dox`** | **Contrat Hiérarchique de Gouvernance** : Standard AGENTS.md / CLAUDE.md imposant la transmission de contexte et les chaînes de commande. | [Amdkn/dox](https://github.com/Amdkn/dox) | Spécification & Templates |
| **`knowledge-catalog`** | **Spécification OKF v0.2 (Open Knowledge Format)** : Standard de documents atomiques (`concepts/`, `log.md`, `index.md`) avec frontmatter YAML. | [Amdkn/knowledge-catalog](https://github.com/Amdkn/knowledge-catalog) | Standard & Validateurs |
| **`llm-wiki`** | **Architecture WikiLLM de Karpathy** : Pattern de base de connaissances continue 3 couches (Raw sources, The Wiki, The Schema). | [Amdkn Gist 34a4b4bf](https://gist.github.com/34a4b4bf6d54b1828ba8c256615619e8.git) | Pattern & Doctrine |

---

## 2. Standard MCP Memory & Chemin Absolu Partagé

La solution repose sur le standard ouvert **Model Context Protocol (MCP)** et le serveur `@modelcontextprotocol/server-memory`.

> [!IMPORTANT]
> **Règle Fondamentale d'Agnosticité** : Tous les agents et tous les harnesses doivent pointer obligatoirement vers le **même chemin absolu unique** sur la machine locale :
> `MEMORY_FILE_PATH = "C:\Users\amado\Aspace OS V5\00_Memoire\shared_brain\memory.jsonl"`
> *L'utilisation de chemins relatifs ou par défaut créerait des bases distinctes et briserait le cerveau partagé.*

### Outils Exposés par la Gateway
1. `create_entities` : Création de nouveaux nœuds typés avec observations initiales.
2. `delete_entities` : Suppression d'entités obsolètes.
3. `create_relations` : Tissage de relations orientées entre entités existantes.
4. `delete_relations` : Élagage de relations.
5. `add_observations` : Enrichissement incrémental des observations d'une entité sans réécrire l'entité.
6. `delete_observations` : Retrait d'observations erronées.
7. `read_graph` : Lecture intégrale du graphe de connaissances partagé.
8. `search_nodes` : Recherche par mot-clé et sous-chaîne dans l'ensemble des entités et observations.
9. `open_nodes` : Inspection détaillée d'un nœud spécifique et de ses relations connectées.

---

## 3. Matrice de Configuration Multi-Harness

Tous les clients de l'écosystème sont configurés pour partager ce graphe :

```
                               ┌────────────────────────┐
                               │  ChatGPT Web (Voie B)  │
                               │  (via Bridge SSE/HTTP) │
                               └───────────┬────────────┘
                                           │ SSE / HTTP Tunnel
                                           ▼
┌──────────────────┐           ┌────────────────────────┐           ┌──────────────────┐
│   Claude Code    │           │                        │           │   OpenCode       │
│ & Claude Desktop ├──────────►│   GATEWAY MCP MEMORY   │◄──────────┤   1.19.5         │
└──────────────────┘   Stdio   │                        │   Stdio   └──────────────────┘
                               │  @modelcontextprotocol │
┌──────────────────┐           │     /server-memory     │           ┌──────────────────┐
│   Codex CLI      ├──────────►│                        │◄──────────┤   Pi Agent       │
│   & Antigravity  │   Stdio   │   Verrou inter-proc    │   Stdio   │   1.5.0          │
└──────────────────┘           │   (FileLock O_EXCL)    │           └──────────────────┘
                               └───────────┬────────────┘
                                           │
                                           ▼
                       ┌────────────────────────────────────────┐
                       │  C:\Users\amado\Aspace OS V5\          │
                       │  00_Memoire\shared_brain\memory.jsonl  │
                       └────────────────────────────────────────┘
```

### Configurations Directes :
* **Claude Code / Antigravity / Cursor** : Déclaré dans `.mcp.json` racine avec `MEMORY_FILE_PATH`.
* **VS Code** : Déclaré dans `.vscode/mcp.json`.
* **Claude Desktop** : `claude_desktop_config.json` avec la commande `npx -y @modelcontextprotocol/server-memory`.
* **Codex** : `~/.codex/config.toml` sous `[mcp_servers.memory]`.
* **OpenCode** : `opencode.json` et `~/.config/opencode/opencode.jsonc` avec `environment: { MEMORY_FILE_PATH: ... }`.
* **Pi 1.5.0** : Outil natif `memory` connecté.
* **DeepSeek Harness (`dsh`) / Superagent** : Profils `worker` et `superagent` branchés sur la mémoire partagée.

---

## 4. Règle de Comportement Universelle (Instruction Système)

Insérée dans la doctrine commune (`AGENTS.md`, `CLAUDE.md`, `.pi/APPEND_SYSTEM.md`) :

> *« Avant de répondre, recherche toujours dans la mémoire partagée (`memory` MCP) si des informations, décisions ou faits passés s'appliquent. Après chaque décision importante, mise à jour ou action réalisée, enregistre le résultat dans la mémoire via `create_entities`, `add_observations` ou `create_relations`. »*
