# 01_Trading — Boîte à Outils d'Analyse Quantitative & Copilote de Marché

> [!WARNING]
> Avant toute utilisation, lire impérativement le protocole [AVERTISSEMENTS.md](AVERTISSEMENTS.md).
> L'IA opère ici exclusivement comme **copilote d'analyse outillé en lecture seule**, jamais comme décideur autonome de passage d'ordres.

---

## 1. Topologie des Composants (4 Sous-Modules)

| Composant | Répertoire Source | Fonction Native | Rôle dans Aspace OS V5 |
|---|---|---|---|
| **TradingView Indicator Search** | [tradingview-indicator-search-mcp-server](https://github.com/daviddme/tradingview-indicator-search-mcp-server) | Serveur MCP de recherche d'indicateurs et stratégies Pine Script. | Recherche d'algorithmes communautaires éprouvés sans hallucination de code. |
| **TradingView Unified MCP** | [TradingView-Unified-MCP](https://github.com/daviddme/TradingView-Unified-MCP) | Contrôle headless du navigateur TradingView (alertes, charts, watchlists). | Automatisation de captures et suivi de graphiques sans manipulation manuelle. |
| **Nansen Smart Money CLI** | [nansen-cli](https://github.com/nansen-ai/nansen-cli) | Interface CLI officielle de surveillance on-chain et flux de portefeuilles institutionnels. | Injection de flux réels de liquidité on-chain dans le contexte de décision. |
| **TraderMonty Trading Skills** | [claude-trading-skills](https://github.com/tradermonty/claude-trading-skills) | 52 skills spécialisées de dimensionnement de position, analyse de marché et risk management. | Calcul mathématique strict de la taille de lot par rapport au Stop-Loss (Risque $\le 1\%$). |

---

## 2. Checklist d'Audit Avant Toute Simulation

- [ ] Les clés d'API sont-elles isolées dans les variables d'environnement système (zéro clé dans le chat ou les logs) ?
- [ ] Le serveur MCP opère-t-il strictement en mode **Lecture Seule** (`Read-Only`) sur les soldes du compte ?
- [ ] Le dimensionnement de la position découle-t-il d'une formule déterministe (TraderMonty) et non d'une estimation LLM ?
- [ ] Les frais d'infrastructure (tokens d'inférence, hébergement, spreads et commissions d'échange) ont-ils été déduits du calcul de rentabilité ?
- [ ] Tout ordre sur capital réel est-il soumis au **veto humain explicite d'Amadou Kone (`human:amdkn`)** ?
