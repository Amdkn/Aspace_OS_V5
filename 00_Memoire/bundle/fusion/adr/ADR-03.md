---
okf_version: "0.2"
type: Decision
title: "ADR-03 — Décision Rapide Typée System-1 vs Génération LLM System-2 Libre"
enonce_ref: "00_Memoire/bundle/fusion/FUSION-ENONCE.md"
enonce_sha256: "41889edb9c468ea62ee4641328c0e6f4bac2c618b81da751eebd2af4c05f648d"
---

# ADR-03 — Décision Rapide Typée System-1 vs Génération LLM System-2 Libre
- **Statut** : `ACCEPTÉE`
- **Conflit** : Les boucles ReAct classiques (`agent-zero`, `automaton`, `TradingAgents`) sollicitent un LLM génératif (System-2, 3–300 s, risque d'hallucination syntaxique) pour la classification, l'extraction d'intention, le routage et le dimensionnement financier (`claude-trading-skills`).
- **Décision** : Séparation stricte en 2 étages :
  1. **System-1 (`K3` local / déterministe)** : `GLiNER2.5-multi-Decide` (intention/langue/priorité < 10 ms), `Cactus Needle` (2-bit, grammaire contrainte -> JSON `function_calls`), `claude-trading-skills` (formule mathématique de position sizing ≤ 1 %), `fondation-13-1` (validations purement déterministes V1–V8, R1–R8, D1–D8, J1–J8, E1–E8, M1–M8).
  2. **System-2 (`K3` Fugu / FreeCloud)** : réservé exclusivement au raisonnement complexe, à la synthèse et au code.
- **Invariant** : Aucun calcul financier ni aucune validation de gouvernance (`R10`, `route-dispatch`, `judge-pr`) ne dépend d'une génération textuelle probabiliste.
- **Modules résolus** : `GLiNER2.5-multi-Decide`, `needle`, `mimi`, `moshi`, `LoRA`, `claude-trading-skills`, `fondation-13-1`, `text-to-cad`.
