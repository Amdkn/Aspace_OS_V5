---
okf_version: "0.2"
type: Decision
title: "ADR-08 — Zéro-Télémétrie & Souveraineté Locale vs Télémétrie Amont & FreeVPS"
enonce_ref: "00_Memoire/bundle/fusion/FUSION-ENONCE.md"
enonce_sha256: "41889edb9c468ea62ee4641328c0e6f4bac2c618b81da751eebd2af4c05f648d"
---

# ADR-08 — Zéro-Télémétrie & Souveraineté Locale vs Télémétrie Amont & FreeVPS
- **Statut** : `ACCEPTÉE`
- **Conflit** : Plusieurs dépôts amont embarquent des appels sortants ou télémétries par défaut (`agent-zero` -> `api.agent-zero.ai`, `prime-agent` -> `api.primeintellect.ai`, `openbot` -> CopilotKit/PostHog, `codex-chatgpt-web` -> télémétrie Electron, `orca` -> analytics, `spynel`, `dify`), et `FreeVPS` repose sur l'exploitation de GitHub Actions éphémères.
- **Décision** :
  1. Télémétrie sortante = **0** par construction sur tous les noyaux et adaptateurs (vérification `strace` / audit télémétrie). Tout routage d'inférence externe passe uniquement par le routeur unifié `K3` (`aspace_freecloud_gateway` + `freellmapi` + `bifrost` + `codex-chatgpt-web` protégé par `aspace-telemetry-shield.cjs`).
  2. `FreeVPS` est **ÉCARTÉ** pour incompatibilité CGU GitHub Actions et non-durabilité ; remplacé par `mesh-llm` + `DeepInfer` + `FreeLLMAPI`.
- **Invariant** : `H-M4` (zéro appel réseau non sollicité hors loopback `:31415`/`:9931` ou API GitHub authentifiée sur requête explicite).
- **Modules résolus** : `freellmapi`, `bifrost`, `codex-chatgpt-web`, `freebuff`, `FreeVPS`, `LFM3-Omni-2B`, `DeepInfer`, `mesh-llm`, `agent-zero`, `prime-agent`, `openbot`, `orca`, `herdr`, `spynel`, `codex`, `openclaw`, `open-notebook`, `presenton`.
