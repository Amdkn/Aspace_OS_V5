# 01_Trading — Boîte à Outils d'Analyse Quantitative & Copilote de Marché

> [!WARNING]
> Avant toute utilisation, lire impérativement le protocole [AVERTISSEMENTS.md](AVERTISSEMENTS.md).
> L'IA opère ici exclusivement comme **copilote d'analyse outillé en lecture seule**, jamais comme décideur autonome de passage d'ordres.

---

## 1. Topologie des Composants (11 Sous-Modules Git)

### A. Infrastructure & MCP TradingView / On-Chain
| Composant | Répertoire Source | Fonction Native | Rôle dans Aspace OS V5 |
|---|---|---|---|
| **TradingView Indicator Search** | [tradingview-indicator-search-mcp-server](https://github.com/Amdkn/tradingview-indicator-search-mcp-server) | Serveur MCP de recherche d'indicateurs et stratégies Pine Script. | Recherche d'algorithmes communautaires sans hallucination. |
| **TradingView Unified MCP** | [TradingView-Unified-MCP](https://github.com/Amdkn/TradingView-Unified-MCP) | Contrôle headless du navigateur TradingView (alertes, charts, watchlists). | Automatisation de captures et suivi de graphiques. |
| **Nansen Smart Money CLI** | [nansen-cli](https://github.com/nansen-ai/nansen-cli) | Interface CLI officielle de surveillance on-chain et flux institutionnels. | Injection de flux réels de liquidité on-chain. |

### B. Les 8 Moteurs IA Trading & Portefeuille (Miles Deutscher Top-8)
| Tier | Composant | Fork Amdkn | Repo Amont | Fonction Clé |
|---|---|---|---|---|
| **Tier S** | **TradingAgents** | [Amdkn/TradingAgents](https://github.com/Amdkn/TradingAgents) | [TauricResearch/TradingAgents](https://github.com/TauricResearch/TradingAgents) | Framework multi-agents reproduisant une société de gestion (12 agents spécialisés, débat bull/bear, risk management, exécution). |
| **Tier A** | **Daily Stock Analysis** | [Amdkn/daily_stock_analysis](https://github.com/Amdkn/daily_stock_analysis) | [ZhuLinsen/daily_stock_analysis](https://github.com/ZhuLinsen/daily_stock_analysis) | Analyse quotidienne automatique multi-marchés avec scoring /100, alertes risque et rapports Telegram pré-marché. |
| **Tier A** | **Vibe Trading** | [Amdkn/Vibe-Trading](https://github.com/Amdkn/Vibe-Trading) | [HKUDS/Vibe-Trading](https://github.com/HKUDS/Vibe-Trading) | Assistant de recherche HKU multi-agents auto-améliorant avec mémoire (langage naturel, backtest réaliste, paper trading Alpaca). |
| **Tier A** | **Anthropic Financial Services** | [Amdkn/financial-services](https://github.com/Amdkn/financial-services) | [anthropics/financial-services](https://github.com/anthropics/financial-services) | Toolkit institutionnel Anthropic (IB, equity research, private equity, earnings reviewer, valuation). |
| **Tier B** | **Freqtrade** | [Amdkn/freqtrade](https://github.com/Amdkn/freqtrade) | [freqtrade/freqtrade](https://github.com/freqtrade/freqtrade) | Bot de trading crypto algorithmique complet (Telegram, CEX/DEX, backtesting, ML optimization, dry-run). |
| **Tier B** | **Day Trader Skill** | [Amdkn/claude-trading-skills](https://github.com/Amdkn/claude-trading-skills) | [tradermonty/claude-trading-skills](https://github.com/tradermonty/claude-trading-skills) | Suite de compétences Claude spécialisées day trading & calcul strict du position sizing (Stop-Loss $\le 1\%$). |
| **Tier B** | **AI Hedge Fund** | [Amdkn/ai-hedge-fund](https://github.com/Amdkn/ai-hedge-fund) | [virattt/ai-hedge-fund](https://github.com/virattt/ai-hedge-fund) | Comité d'investissement simulant les profils d'investisseurs légendaires (Buffett, Munger, Burry, Wood) avec exécution Alpaca. |
| **Tier C** | **LLM Trading Lab** | [Amdkn/LLM-Trading-Lab](https://github.com/Amdkn/LLM-Trading-Lab) | [LuckyOne7777/LLM-Trading-Lab](https://github.com/LuckyOne7777/LLM-Trading-Lab) | Framework d'étude empirique de portefeuilles micro-caps gérés par LLM et analyse de journaux de transactions (CSV). |

---

## 2. Checklist d'Audit Avant Toute Simulation

- [ ] Les clés d'API sont-elles isolées dans les variables d'environnement système (zéro clé dans le chat ou les logs) ?
- [ ] Le serveur MCP opère-t-il strictement en mode **Lecture Seule** (`Read-Only`) sur les soldes du compte ?
- [ ] Le dimensionnement de la position découle-t-il d'une formule déterministe (TraderMonty) et non d'une estimation LLM ?
- [ ] Les frais d'infrastructure (tokens d'inférence, hébergement, spreads et commissions d'échange) ont-ils été déduits du calcul de rentabilité ?
- [ ] Tout ordre sur capital réel est-il soumis au **veto humain explicite d'Amadou Kone (`human:amdkn`)** ?
