---
okf_version: "0.2"
type: Decision
title: "ADR-07 — Copilote Analytique Financier Read-Only & Veto `S0` vs Auto-Trading"
enonce_ref: "00_Memoire/bundle/fusion/FUSION-ENONCE.md"
enonce_sha256: "41889edb9c468ea62ee4641328c0e6f4bac2c618b81da751eebd2af4c05f648d"
---

# ADR-07 — Copilote Analytique Financier Read-Only & Veto `S0` vs Auto-Trading
- **Statut** : `ACCEPTÉE`
- **Conflit** : `freqtrade`, `Vibe-Trading`, `ai-hedge-fund`, `nansen-cli` incluent des capacités d'exécution d'ordres (Alpaca, CEX/DEX swaps), en contradiction frontale avec `AVERTISSEMENTS.md` et la règle Scion de sécurité sémantique (`a2p` intention de paiement non exécutable par un agent).
- **Décision** : Toute brique financière (`K5` Trading) fonctionne exclusivement en **Copilote d'Analyse Read-Only + Dry-Run**. Les clés d'échange en lecture seule sont isolées en variables d'environnement ; les capacités de passage d'ordres (`swap`, `order_create`, `a2p`) sont bloquées au niveau de la politique L0 et requièrent une signature humaine explicite d'Amadou Kone (`human:amdkn` S0). `LLM-Trading-Lab` est **ÉCARTÉ** car redondant avec l'outillage quantitatif retenu/fusionné.
- **Invariant** : 0 ordre sur capital réel déclenché sans ratification humaine `S0`.
- **Modules résolus** : `TradingAgents`, `TradingView-Unified-MCP`, `Vibe-Trading`, `ai-hedge-fund`, `claude-trading-skills`, `daily_stock_analysis`, `financial-services`, `freqtrade`, `nansen-cli`, `tradingview-indicator-search-mcp-server`, `LLM-Trading-Lab`, `BusinessOS`.
