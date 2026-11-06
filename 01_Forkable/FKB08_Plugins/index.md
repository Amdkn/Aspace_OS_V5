# FKB08_Plugins — Écosystème Plugins, Skills Meta-Creators & Ingestion Multimodale

Ce pôle centralise les standards industriels ouverts de plugins agentiques, de bibliothèques de skills et de moteurs d'ingestion multimodale (vidéo/livre/audio).

---

## 1. Sous-Modules Git Intégrés

| Sous-Module | Dépôt Source | Rôle dans l'Architecture Aspace OS V5 |
|---|---|---|
| **`anthropic-skills`** | `Amdkn/skills` (Fork d'`anthropics/skills`) | Standard officiel des Skills Anthropic, patron `skill-creator`, protocoles d'évaluation qualitative/quantitative. |
| **`mattpocock-skills`** | `mattpocock/skills` | Architecture chirurgicale de compétences d'ingénierie TypeScript/Node, conventions d'exploration non-présumptive. |
| **`openai-plugins`** | `openai/plugins` | Spécification historique et schémas d'interconnexion d'outils et de plugins agentiques. |
| **`claude-video`** | `bradautomates/claude-video` | Moteur Dual-Engine de vision vidéo (Gemini Video Understanding + Local I-Frames ffmpeg/WhisperX). |

---

## 2. Synergie Opérationnelle

1. **Compilation de Compétences (`skill-creator`)** :
   - Fusionne les SOPs et la progressive disclosure d'Anthropic avec le modèle d'auto-apprentissage de Hermes Agent et la précision d'écriture de Matt Pocock.
2. **Ingestion & Knowledge-to-Execution (`omni-compiler` & `watch`)** :
   - Ingestion multimodale via `claude-video` (zéro token local pour le scan, extraction de keyframes déictiques pour le code).
   - Triage épistémique strict : Le "Comment" devient un Super-Skill (`.agents/skills/`), le "Quoi" alimente le Second Brain (`00_Memoire/bundle/` et `memory.jsonl`).
