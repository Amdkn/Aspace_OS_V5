---
okf_version: "0.2"
type: Decision
title: "ADR-FUSION — Arbitrages d'Architecture de la Fondation A'Space (ADR-01 à ADR-13)"
enonce_ref: "00_Memoire/bundle/fusion/FUSION-ENONCE.md"
enonce_sha256: "41889edb9c468ea62ee4641328c0e6f4bac2c618b81da751eebd2af4c05f648d"
---

# ADR-FUSION — Arbitrages de Conflits entre Principes

Chaque ADR ci-dessous résout un **conflit réel détecté lors de l'extraction des 120 vecteurs de principe** (`CARTE-DES-PRINCIPES.md`). Conformément au §2 de la mission, aucune commodité n'est retenue : chaque arbitrage nomme les modules en conflit, l'option retenue, l'option rejetée, l'invariant résultant et le test de conformité.

---

## ADR-01 — Réveil Événementiel & Hibernation Pure-Data vs Sondage Cron Périodique
- **Statut** : `ACCEPTÉE`
- **Conflit** : `automaton`, `openclaw`, `daily_stock_analysis`, `uptime-kuma`, `changedetection.io` utilisent historiquement des boucles `cron` / sondages périodiques (ex. toutes les 30 min), tandis qu'`infinity` et `pi` imposent l'état **Pure Data Between Turns** et les **checkpoints événementiels**.
- **Décision** : Tout cœur agentique (`K1`, `K2`) hiberne à coût CPU/RAM nul entre deux tours (état sérialisé en SQLite WAL dans `session_store.rs` / `factory.sqlite`) et se réveille uniquement sur événement typé (`RAP`, message, webhook, échéance de bail). Les outils de sondage externe `RETENU` (`uptime-kuma`, `changedetection.io`) sont cantonnés à la périphérie `K5` et émettent des webhooks d'événement vers `K2`, jamais de threads agents permanents.
- **Invariant** : Zéro `cron 30min` sur les 578 Holons ; temps de veille inactif = 0 thread actif.
- **Modules résolus** : `infinity`, `pi`, `automaton`, `openclaw`, `daily_stock_analysis`, `uptime-kuma`, `changedetection.io`.

## ADR-02 — Daemon Maître Unique (`RigInfinity`) vs Multi-Daemons Concurrents
- **Statut** : `ACCEPTÉE`
- **Conflit** : `OpenBot` spawne jusqu'à 10 processus par bot ; `herdr-core`, `openrig`, `openclaw`, `orca`, `agent-desktop`, `cubefarm`/`agent-office` et `OpenMausBot` introduisent chacun leur propre démon ou serveur local concurrent.
- **Décision** : **Loi du Daemon Maître Unique** : un seul processus superviseur Rust (`riginfinity-daemon` sur `127.0.0.1` loopback uniquement) porte l'état d'exécution, les sessions PTY (`openrig_terminal.rs`), les proxys MCP (`mcp_proxy.rs`), les callbacks RAP et le source-control WAL. Les skins bots (`OpenMuse`, `OpenDots`, `OpenDuet`) sont fusionnés comme traits sur la plateforme `OpenBot` unifiée en Rust. Les applications visuelles (`herdr-app`, `cubefarm`, `city-office`) sont de pures surfaces clientes sans autorité de daemon concurrent.
- **Invariant** : `ps` en production runtime ne compte qu'**1 processus daemon maître** pour l'orchestration agentique.
- **Modules résolus** : `RigInfinity`, `infinity`, `openrig`, `agent-zero`, `openbot`, `openmuse`, `OpenDots`, `OpenDuet`, `herdr-core`, `herdr`, `openclaw`, `orca`, `t3code`, `OpenMausBot`, `cubefarm`, `agent-office`, `city-office`.

## ADR-03 — Décision Rapide Typée System-1 vs Génération LLM System-2 Libre
- **Statut** : `ACCEPTÉE`
- **Conflit** : Les boucles ReAct classiques (`agent-zero`, `automaton`, `TradingAgents`) sollicitent un LLM génératif (System-2, 3–300 s, risque d'hallucination syntaxique) pour la classification, l'extraction d'intention, le routage et le dimensionnement financier (`claude-trading-skills`).
- **Décision** : Séparation stricte en 2 étages :
  1. **System-1 (`K3` local / déterministe)** : `GLiNER2.5-multi-Decide` (intention/langue/priorité < 10 ms), `Cactus Needle` (2-bit, grammaire contrainte -> JSON `function_calls`), `claude-trading-skills` (formule mathématique de position sizing ≤ 1 %), `fondation-13-1` (validations purement déterministes V1–V8, R1–R8, D1–D8, J1–J8, E1–E8, M1–M8).
  2. **System-2 (`K3` Fugu / FreeCloud)** : réservé exclusivement au raisonnement complexe, à la synthèse et au code.
- **Invariant** : Aucun calcul financier ni aucune validation de gouvernance (`R10`, `route-dispatch`, `judge-pr`) ne dépend d'une génération textuelle probabiliste.
- **Modules résolus** : `GLiNER2.5-multi-Decide`, `needle`, `mimi`, `moshi`, `LoRA`, `claude-trading-skills`, `fondation-13-1`, `text-to-cad`.

## ADR-04 — Mémoire Épistémique Vérifiée au Fichier (`M1–M8`) vs RAG Sémantique Flou
- **Statut** : `ACCEPTÉE`
- **Conflit** : `gbrain`, `DeepTutor`, `billion-context` utilisent la recherche vectorielle/hybride et l'indexation massive, tandis que `fondation-13-1` (`recall-fact`, règles M1–M8), `auto-ontology` (DAG formel), `knowledge-catalog` (OKF v0.2) et `servers` (`memory.jsonl`) exigent traçabilité exacte au fichier, absence d'inférence implicite et détection de contradictions.
- **Décision** : La recherche hybride (`gbrain`, `graphify`, `billion-context`) sert uniquement de **moteur de rappel candidat**. Aucun fait n'est promu ou cité comme vérité dans la Fondation (`K1`, `K4`) sans passer le contrat épistémique **`EpistemicFact` (`M1–M8`)** qui impose un statut explicite parmi `{vérifié, consigné, contredit, périmé, absent, à venir}` et l'interdiction absolue d'inférer une date ou un SHA absent. Les écritures durables passent par un fichier unique `00_Memoire/shared_brain/memory.jsonl` (verrou `O_EXCL`) + `00_Memoire/bundle/` (OKF v0.2, `log.md` strictement append-only).
- **Invariant** : Toute assertion dans une PR, un jugement ou un livrable B2B cite sa source et sa date vérifiées au fichier ou porte un statut d'absence/contradiction explicite.
- **Modules résolus** : `fondation-13-1`, `auto-ontology`, `context-language-models`, `dox`, `gbrain`, `graphify`, `infinite-brain-harness`, `infinite-brain-os`, `knowledge-catalog`, `servers`, `llm-wiki`, `claude-mem`, `DeepTutor`.

## ADR-05 — Isolation Poisson Rouge (`EGM`) & Sparse (`Scion`) vs Contexte Monolithique
- **Statut** : `ACCEPTÉE`
- **Conflit** : `billion-context` et `claude-mem` tendent à accumuler d'immenses fenêtres historiques, tandis que `elephant-goldfish-model` (EGM), `caveman` et `source-control-natif` (Scion sparse + changeset CAS sans copie) prouvent que l'accumulation dégrade la précision et explose les coûts.
- **Décision** : Couplage obligatoire **Éléphant (`K4`/SQLite WAL) × Poisson Rouge (`K2` exécution bornée)** :
  - L'état macro et les blobs CAS SHA-256 (`billion-context`, `changeset WAL`) restent sur disque/NVMe.
  - Chaque worker ne reçoit qu'un sous-graphe élagué, une vue sparse de ses fichiers cibles (`Scion`), et communique en mode télégraphique (`caveman`) sans perte d'identifiants.
  - Les surfaces `BusinessOS` inutilisées (« trous » non consommés par aucun lecteur) sont supprimées selon la règle sparse.
- **Invariant** : Aucun worker d'exécution ne charge l'intégralité du graphe `memory.jsonl` (`read_graph` interdit en routine).
- **Modules résolus** : `elephant-goldfish-model`, `billion-context`, `caveman`, `source-control-natif`, `orca`, `tuxee`, `BusinessOS`.

## ADR-06 — Auto-Amélioration Bornée par Hold-Out & Juge Externe vs Mutation Autonome
- **Statut** : `ACCEPTÉE`
- **Conflit** : `hermes-agent` (`/learn`), `prime-agent` (`/refine`), `rrsi` et `dream-rsi` proposent l'auto-modification continue des skills, prompts et worktrees, ce qui menace la stabilité de `FKB00` et des contrats L0.
- **Décision** : La boucle RSI à 3 Horizons est **strictement subordonnée au hold-out et au Juge externe** :
  - Horizon 1 (`prime-agent` / `RigInfinity`) : snapshots réversibles avant chaque `/refine`, rollback automatique si métrique baisse.
  - Horizon 2 (`wikiskill` + `adk-recipes` AQuA + `hermes-agent` `/learn`) : séparation des 4 rôles (Worker, Note-Taker, Playbook Writer, Strict Manager) ; promotion interdite si gain sur hold-out `< δ = 1.7 %`.
  - Horizon 3 (`dream-rsi` / `rrsi`) : replay hors-ligne à coût nul et mutations uniquement sur branches/worktrees jetables ; jamais d'écriture directe sur `master` ou `FKB00` sans validation indépendante (`judge-pr` + Juge externe).
- **Invariant** : Un créateur de mutation ne peut jamais valider sa propre promotion.
- **Modules résolus** : `prime-agent`, `wikiskill`, `adk-recipes`, `dream-rsi`, `rrsi`, `hermes-agent`, `gstack`, `superpowers`.

## ADR-07 — Copilote Analytique Financier Read-Only & Veto `S0` vs Auto-Trading
- **Statut** : `ACCEPTÉE`
- **Conflit** : `freqtrade`, `Vibe-Trading`, `ai-hedge-fund`, `nansen-cli` incluent des capacités d'exécution d'ordres (Alpaca, CEX/DEX swaps), en contradiction frontale avec `AVERTISSEMENTS.md` et la règle Scion de sécurité sémantique (`a2p` intention de paiement non exécutable par un agent).
- **Décision** : Toute brique financière (`K5` Trading) fonctionne exclusivement en **Copilote d'Analyse Read-Only + Dry-Run**. Les clés d'échange en lecture seule sont isolées en variables d'environnement ; les capacités de passage d'ordres (`swap`, `order_create`, `a2p`) sont bloquées au niveau de la politique L0 et requièrent une signature humaine explicite d'Amadou Kone (`human:amdkn` S0). `LLM-Trading-Lab` est **ÉCARTÉ** car redondant avec l'outillage quantitatif retenu/fusionné.
- **Invariant** : 0 ordre sur capital réel déclenché sans ratification humaine `S0`.
- **Modules résolus** : `TradingAgents`, `TradingView-Unified-MCP`, `Vibe-Trading`, `ai-hedge-fund`, `claude-trading-skills`, `daily_stock_analysis`, `financial-services`, `freqtrade`, `nansen-cli`, `tradingview-indicator-search-mcp-server`, `LLM-Trading-Lab`, `BusinessOS`.

## ADR-08 — Zéro-Télémétrie & Souveraineté Locale vs Télémétrie Amont & FreeVPS
- **Statut** : `ACCEPTÉE`
- **Conflit** : Plusieurs dépôts amont embarquent des appels sortants ou télémétries par défaut (`agent-zero` -> `api.agent-zero.ai`, `prime-agent` -> `api.primeintellect.ai`, `openbot` -> CopilotKit/PostHog, `codex-chatgpt-web` -> télémétrie Electron, `orca` -> analytics, `spynel`, `dify`), et `FreeVPS` repose sur l'exploitation de GitHub Actions éphémères.
- **Décision** :
  1. Télémétrie sortante = **0** par construction sur tous les noyaux et adaptateurs (vérification `strace` / audit télémétrie). Tout routage d'inférence externe passe uniquement par le routeur unifié `K3` (`aspace_freecloud_gateway` + `freellmapi` + `bifrost` + `codex-chatgpt-web` protégé par `aspace-telemetry-shield.cjs`).
  2. `FreeVPS` est **ÉCARTÉ** pour incompatibilité CGU GitHub Actions et non-durabilité ; remplacé par `mesh-llm` + `DeepInfer` + `FreeLLMAPI`.
- **Invariant** : `H-M4` (zéro appel réseau non sollicité hors loopback `:31415`/`:9931` ou API GitHub authentifiée sur requête explicite).
- **Modules résolus** : `freellmapi`, `bifrost`, `codex-chatgpt-web`, `freebuff`, `FreeVPS`, `LFM3-Omni-2B`, `DeepInfer`, `mesh-llm`, `agent-zero`, `prime-agent`, `openbot`, `orca`, `herdr`, `spynel`, `codex`, `openclaw`, `open-notebook`, `presenton`.

## ADR-09 — Confinement des Licences Restrictives & Règle Clean-Room (`D12`)
- **Statut** : `ACCEPTÉE`
- **Conflit** : Le corpus mélange Apache-2.0/MIT avec `AGPL-3.0` (`MiroFish`), `CC BY-NC 4.0` (`PathFM`), `Apache-2.0 modifiée` (`dify`), et des dépôts **sans licence** (`claude-code`, `openai-plugins`, `autoresearch`).
- **Décision** :
  1. **`AGPL-3.0` (`MiroFish`)** : strict confinement en microservice réseau isolé ; zéro linkage ou inclusion de source dans les binaires Apache-2.0/MIT.
  2. **`CC BY-NC 4.0` (`PathFM`, profil interne `TabFM`/`TimesFM`)** : confinement strict au profil `a0_internal_wargame` ; le profil `b2b_commercial` charge exclusivement la pile Apache-2.0 (`Mitra-v2` + `Chronos-2`), appliqué mécaniquement par `assert_commercial_safe()`.
  3. **Sans licence (`claude-code`, `openai-plugins`, `autoresearch`)** : application stricte de la règle **D12 Clean-Room** — aucune copie de fichier source ; utilisation uniquement comme référence externe (`openai-plugins` -> `RETENU`) ou exécutable CLI externe piloté par contrat (`claude-code` -> `RETENU`).
- **Invariant** : Tout binaire central `L0` (`fondation-13-1`, `RigInfinity`, `aspace-fiber-host`) reste sous licence permissive propre Apache-2.0/MIT sans contamination virale ni violation NC.
- **Modules résolus** : `MiroFish`, `PathFM`, `autogluon`, `chronos-forecasting`, `mitra-2`, `tabfm`, `timesfm`, `dify`, `claude-code`, `openai-plugins`, `rea`.

## ADR-10 — Contrat de Fibre Spatio-Temporel Unique vs Silos d'Outils & Skills
- **Statut** : `ACCEPTÉE`
- **Conflit** : Les catalogues d'outils et compétences sont fragmentés entre `a0-plugins`, `anthropic-skills`, `mattpocock-skills`, `openai-plugins`, `impeccable`, `API-Anything`, `CLI-Anything`, `Scrapling`, `agent-browser`, `agent-desktop`, `rea`, `superpowers`, `dox`, `deepseek-harness`.
- **Décision** : Toute capacité opérationnelle est enregistrée dans l'hôte de fibres (`aspace-fiber-host` / `RigInfinity` avec ID `fiber:a0:*` unique et `capabilities_owned` disjoints dans `MODULES-LOCK.json`) ; toute compétence procédurale suit le format unifié `SKILL.md` à divulgation progressive ; tout pilotage logiciel privilégie la hiérarchie **API (`api-anything`) -> CLI (`CLI-Anything`) -> Arbre d'accessibilité sans vol de focus (`agent-browser` CDP `@ref` / `agent-desktop`)**.
- **Invariant** : 1 capacité = 1 seul propriétaire dans `MODULES-LOCK.json` ; vérification automatisée par `check-modules-lock.py` check #4.
- **Modules résolus** : `cordis`, `aspace-fiber-host`, `a0-plugins`, `deepseek-harness`, `openrig`, `CLI-Anything`, `api-anything`, `agent-browser`, `agent-desktop`, `rea`, `Scrapling`, `impeccable`, `anthropic-skills`, `mattpocock-skills`, `claude-video`, `dox`, `superpowers`.

## ADR-11 — Source Canonique Unique & Purge des Doublons Inter-Pôles
- **Statut** : `ACCEPTÉE`
- **Conflit** : 8 dépôts vidéo existent en double dans `.gitmodules` (`FKB02_Video_SaaS/*` pointant vers `FKB06_Video_SaaS/*` sans gitlink `160000` et déjà présents sous `FKB07_Money_Maker/02_Video/*`), `hermes-agent` existait en doublon FKB00/FKB04, `get-shit-done` a été remplacé par `gsd-core`, `OpenDuet` dupliquait `OpenBot`, et `infinite-brain-os` recouvre partiellement `OKF v0.2`.
- **Décision** :
  - **Cycle 1 exécuté** : suppression immédiate des 8 entrées doublons fantômes `FKB02_Video_SaaS/*` (`FKB06_Video_SaaS/*`) de `.gitmodules` (109 → 101 entrées alignées 1:1 avec les 101 gitlinks `160000`). Tous les moteurs vidéo fusionnent sous l'unique contrat `aspace_video_studio_foundation.py` en `FKB07_Money_Maker/02_Video/`.
  - `hermes-agent` conserve son unique emplacement canonique `FKB04` (avant absorption totale en `K4`) ; `gsd-core` remplace `get-shit-done`.
- **Invariant** : Zéro URL Git dupliquée dans `.gitmodules` (`len(.gitmodules) == len(distinct_urls) == len(gitlinks_160000)`).
- **Modules résolus** : les 10 moteurs vidéo (`OpenMontage`, `argo`, `earshot`, `explainroo`, `flute`, `huashu-motion`, `reanimate`, `rossark-motion-skill`, `take-one`, `video-director`) + 8 entrées doublons `FKB06`, `hermes-agent`, `gsd-core`, `OpenDuet`, `infinite-brain-os`, `anthropic-skills`, `mattpocock-skills`.

## ADR-12 — Topologie de la Fondation : Réfutation de « 3 Noyaux FKB00 + FKB01..08 non fusionnés » → 5 Noyaux Interconnectés (`K1..K5`)
- **Statut** : `ACCEPTÉE`
- **Conflit & Test de l'Hypothèse (§2)** : Le §2 demande explicitement de **tester l'hypothèse** : *« ces trois noyaux pour FKB00 (Automaton/Infinity/OpenRig), et FKB01 à FKB08 sans fusion »*.
- **Réfutation par les faits bruts** :
  1. Dans `FKB00` lui-même, les trois noyaux `Automaton / Infinity / OpenRig` ne couvrent pas la **vérité formelle et vérification déterministe** (`fondation-13-1` + `EGM/GSD/Superpowers` + `RSI hold-out`) ni l'isolation des **modèles ML prédictifs** (`MiroFish`, `PathFM`, `TabFM`, `TimesFM`, `Mitra-v2`, `Chronos-2`) qui obéissent à des contraintes de licences et de hold-outs totalement distinctes du daemon d'exécution.
  2. Laisser `FKB01..FKB08` sans fusion violerait directement les points (1), (2) et (4) de l'ÉNONCÉ :
     - `FKB06_Video_SaaS` est un **doublon mort** de `FKB07/02_Video` (0 gitlink actif, 8 entrées fantômes).
     - `FKB04` (`api-anything`, `CLI-Anything`, `agent-browser`, `agent-desktop`) et `FKB03` (`cubefarm`, `agent-office`, `city-office`) sont directement les interfaces d'action et de surface du système d'exécution (`K2`), pas des silos autonomes.
     - `FKB01` alimente directement le System-1 (`GLiNER/Needle`) et la passerelle (`:31415`) sans lesquels `Automaton`/`Agent-Zero`/`RigInfinity` sont muets (`K3`).
     - `FKB02` et `FKB08` fusionnent la mémoire épistémique vérifiée (`M1–M8`), l'ontologie (`auto-ontology`) et les compétences validées (`wikiskill` / `hermes` / `anthropic-skills`) dans un même noyau de savoir (`K4`).
     - `FKB00/02_PredictiveWargame_MachineLearning` + `FKB07_Money_Maker` forment la couche de prévision probabiliste et de génération de valeur B2B soumise aux mêmes garde-fous financiers et de licence (`K5`).
- **Décision déduite des principes** : La Fondation A'Space tient exactement en **5 Noyaux Interconnectés (`K1..K5`)** posés sur un **Socle L0 Commun** (3 contrats transversaux + fibre + test de suppression) :
  - **K1 — Gouvernance, Âme & Vérification** (11 modules)
  - **K2 — Exécution, Concurrence & Surface Vivante** (33 modules)
  - **K3 — Inférence & Décision Calibrée** (15 modules)
  - **K4 — Mémoire Neuro-Symbolique & Compétences** (18 modules)
  - **K5 — Prédictif, Wargame & Moteurs de Valeur B2B** (43 modules)
- **Invariant** : Chaque noyau `K1..K5` lit et émet via les 3 contrats L0 obligatoires (`EventJournal`, `R10Receipt`, `EpistemicFact`).

## ADR-13 — Amendement ADR-12 : Trois Noyaux (`ÂME / SYSTÈME NERVEUX / CORPS`) & Trajectoire du Cœur (`Python → Hybride → Rust`)
- **Statut** : `ACCEPTÉE` (Amende `ADR-12` — décision architecturale Cycle 4)
- **Conflit** : L'`ADR-12` réfutait la variante « trois noyaux dans FKB00 avec FKB01..08 sans fusion », mais a pris la voie de facilité en érigeant 5 racines (`K1..K5`) au lieu de tout unifier sous les Trois Noyaux doctrinaux, et sans expliciter la trajectoire évolutive d'un seul cœur vers Rust.
- **Décision** :
  1. **Trois Noyaux Fondamentaux** (tous les 120 modules sans exception y sont rattachés) :
     - **`ÂME` (`Automaton`)** : doctrine, gouvernance 13→1, mémoire épistémique & compétences — rattache les organes **`K1`** (Gouvernance & RSI) et **`K4`** (Mémoire Neuro-Symbolique & Compétences) (29 modules).
     - **`SYSTÈME NERVEUX` (`Infinity`)** : journal d'événements L0, reçus R10, hibernation pure-data, fibres réactives & inférence calibrée — rattache le **Bus Nerveux L0 / Fibers** et l'organe **`K3`** (Inférence System-1 & FreeCloud) (22 modules).
     - **`CORPS` (`OpenRig`)** : exécution multi-harness, source-control WAL, outils Anything, surfaces 3D & moteurs prédictifs/B2B — rattache les organes **`K2`** (Atelier Multi-Harness, Anything & Surfaces 3D) et **`K5`** (Prédictif, Wargame, Studio Vidéo & Moteurs B2B) (69 modules).
  2. **Trajectoire d'Un Seul Cœur Qui Évolue (`Python → Hybride → Rust`)** :
     - **Phase 1 (`Python`)** : `aspace_foundation_kernel.py` + organes Python `K1..K5` alignés octet pour octet sur les fixtures Rust (`anchor-001.json`, `anchor-002.json`, `anchor-026.json`). *Critère de passage Phase 1 → Phase 2* : `cargo test` vert sur `fondation-13-1` et `RigInfinity`, 100 % des fixtures validées en Python et pont CLI Rust fonctionnel.
     - **Phase 2 (`Hybride`, atteinte au Cycle 4)** : Python orchestre les organes absorbés (`FKB04`, `FKB02`, etc.) et délègue/contre-valide la mécanique L0 via les binaires Rust compilés (`r10-receive`, `route-dispatch`, `recall-fact`) et `RigInfinity`. *Critère de passage Phase 2 → Phase 3* : tous les modules `FUSIONNÉ` ont passé le test de suppression du Juge externe et la logique des organes `K1..K5` est portée dans les crates Rust unifiées.
     - **Phase 3 (`Rust`, destination)** : workspace Rust souverain unique (`RigInfinity × fondation-13-1`) portant les Trois Noyaux sans dépendance d'exécution Python L0/L1.
- **Invariant** : Les fixtures Rust canoniques font foi à chaque phase ; tout module dans `REGISTRE-DE-FUSION.md` indique son noyau parmi `{ÂME, SYSTÈME NERVEUX, CORPS}`.
- **Modules résolus** : L'intégralité des 120 modules (`M001..M120`). (Détail complet dans [`adr/ADR-13.md`](adr/ADR-13.md)).

## ADR-14 — Amendement ADR-13 : Règle du Tiers Maximal (≤ 40 modules) & Quatre Noyaux (`ÂME / SYSTÈME NERVEUX / CORPS / MÉTABOLISME`)
- **Statut** : `ACCEPTÉE` (Amende `ADR-13` — décision architecturale Cycle 5)
- **Conflit** : Sous `ADR-13`, `CORPS` concentrait `69 / 120` modules (`57,5 %`), formant un fourre-tout mélangeant action d'exécution (`K2`), cortex prédictif ML/Wargame et valeur créative/B2B (`K5`).
- **Décision** :
  1. **Règle du tiers maximal** : aucun noyau ne peut dépasser `120 / 3 = 40` modules (`33,3 %`).
  2. **Scission de `CORPS` en Quatre Noyaux Équilibrés** :
     - **`ÂME` (`Automaton`)** : `K1` (`11`) + `K4` (`18`) = **`29` modules (`24,2 %`)**.
     - **`SYSTÈME NERVEUX` (`Infinity`)** : Bus L0 (`7`) + `K3` (`15`) + **`K3-ML` Cortex Prédictif & Wargame** (`7` : `M006..M012`) = **`29` modules (`24,2 %`)**.
     - **`CORPS` (`OpenRig`)** : `K2` Exécution Multi-Harness, Bots, Source-Control, Anything & 3D = **`26` modules (`21,7 %`)**.
     - **`MÉTABOLISME` (`BusinessOS`)** : `K5` Production Vidéo/CAO, Finance Read-Only veto S0 & Valeur B2B = **`36` modules (`30,0 %`)**.
- **Invariant** : Aucun noyau > `40` modules ; preuve `FUSIONNÉ` réservée aux modules validés par comparaison différentielle directe contre la source d'origine avant/après suppression physique. (Détail complet dans [`adr/ADR-14.md`](adr/ADR-14.md)).

## ADR-15 — Amendement ADR-14 : Retour aux Trois Noyaux (`ÂME / SYSTÈME NERVEUX / CORPS`), Retrait de `MÉTABOLISME` & Preuve Différentielle Anti-Sabotage
- **Statut** : `ACCEPTÉE` (Amende `ADR-14` — décision architecturale Cycle 6)
- **Conflit** : Le plafond mécanique `≤ 1/3` a créé un 4e noyau `MÉTABOLISME` par renommage de `K5`, et l'audit par sabotage du Juge externe Cycle 5 a révélé des fonctions non déclenchées sur `M044` (`clm_rendered_text`), `M050` (`okf_is_stale`) et des comparaisons tolérantes sur `M117`/`M118`.
- **Décision** :
  1. **Trois Noyaux Uniquement** : retrait de `MÉTABOLISME` comme noyau racine (`MÉTABOLISME` redevient l'`Organe K5` du noyau `CORPS`), suppression du plafond mécanique de taille par noyau : **`ÂME` (`29`)**, **`SYSTÈME NERVEUX` (`29`)**, **`CORPS` (`62`, réduit par fusion réelle de modules, dont `M084 video-director` en Cycle 6)**.
  2. **Contrat Anti-Sabotage** : toute fonction et donnée déclarée de `M044`, `M050`, `M056`, `M084`, `M117` et `M118` doit passer une parité stricte (`==` sans clés en trop ni normalisation destructive) **et** faire échouer la suite en cas de sabotage/mutation volontaire ; `M058 agent-desktop` reste `PARTIEL` sans vraie fenêtre Windows. (Détail complet dans [`adr/ADR-15.md`](adr/ADR-15.md)).
