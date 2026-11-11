---
type: Reference
title: Outils mémoire installés
description: DOX, OKF, WikiLLM (Karpathy) et Graphify clonés dans 00_Memoire et leur rôle.
tags: [memoire, outils, wikillm]
generated: { by: agent/antigravity, at: 2026-11-03T14:32:00-05:00 }
status: active
---

| Outil | Dossier | Rôle dans V5 |
|---|---|---|
| DOX (agent0ai/dox) | `00_Memoire/dox/` | Contrat `AGENTS.md` hiérarchique : lire la chaîne avant d'éditer, mettre à jour après. Appliqué dans `AGENTS.md` et `00_Memoire/AGENTS.md`. |
| OKF v0.2 (GoogleCloudPlatform/knowledge-catalog) | `00_Memoire/knowledge-catalog/okf/SPEC.md` | Format du bundle `00_Memoire/bundle/` : markdown + frontmatter YAML, `index.md`, `log.md`. |
| WikiLLM (Karpathy gist `442a6bf555914893e9891c11519de94f`) | `00_Memoire/wikillm/llm-wiki.md` | Pattern de wiki incrémental maintenu directement par l'agent (couches `raw/` immuable, `bundle/` wiki, `CLAUDE.md`/`AGENTS.md` schéma ; opérations Ingest, Query, Lint). Remplace OpenWiki (supprimé car trop gourmand en quota LLM et bloquant en TUI). |
| Graphify (Graphify-Labs/graphify) | `00_Memoire/graphify/` (source), CLI via `00_Memoire/.venv` | Graphe de connaissance de V5 : `00_Memoire\.venv\Scripts\graphify`. Sortie : `graphify-out/`. |
