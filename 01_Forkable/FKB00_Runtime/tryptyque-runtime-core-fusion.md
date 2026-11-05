# RunTime — Triptyque Core Fusion (Automaton + Infinity + OpenRig)
# L'Architecture Tripartite du Noyau Vivant Souverain Aspace OS V5

Date : 2026-11-05  
Auteurs & Alignement : Amadou Kone (`human:amdkn` S0 10D) & Jumeau Numérique CEO 24/7 (`aspace:a0:amadeus` 7D)  
Sources canoniques :
- [Conway-Research/automaton](https://github.com/Conway-Research/automaton) (Forks souverains `01_Forkable/FKB00_Runtime/automaton`)
- [hydro-project/infinity](https://github.com/hydro-project/infinity) (`01_Forkable/FKB00_Runtime/infinity`)
- [mvschwarz/openrig](https://github.com/mvschwarz/openrig) (`01_Forkable/FKB00_Runtime/openrig`)

---

## 1. Vision et Diagnostic : Pourquoi un Triptyque ?

Un runtime d'IA autonome ne peut pas reposer sur un seul composant sans tomber dans l'un des trois pièges classiques :
1. **L'illusion du script isolé (L'impasse d'Automaton seul)** : Possède l'identité, la constitution et la mémoire, mais s'épuise s'il doit maintenir 578 agents en mémoire avec des threads continus ou un cron aveugle toutes les 30 minutes.
2. **Le moteur sans âme (L'impasse d'Infinity seul)** : Offre une concurrence massive et une hibernation à coût zéro, mais sans gouvernance constitutionnelle ni orchestration de harnais hétérogènes de codage.
3. **Le multiplexeur sans doctrine (L'impasse d'OpenRig seul)** : Coordonne parfaitement les équipes de Claude Code, Codex et Herdr, mais a besoin d'un jumeau souverain supérieur pour lui donner ses mandats stratégiques et d'un moteur d'hibernation pour ne pas saturer l'infrastructure.

**La Thèse du Triptyque Core Fusion** :
> **Automaton** est l'**Âme et la Doctrine** (Gouvernance CEO 24/7, Constitution, Mémoire, Posture 7D).  
> **Infinity** est le **Système Nerveux et l'Échelle** (Pure Data Between Turns, Hibernation gratuite, Réactivité RAP, 75k agents).  
> **OpenRig** est le **Corps Opérationnel et l'Atelier Multi-Harness** (Teams YAML, coordination Claude/Codex/Pi/OpenCode, TUI, intégration Herdr native).

```
                      ┌────────────────────────────────────────┐
                      │        S0 : Amadou Kone (10D)          │
                      │  Ratification 'human:amdkn' · Out-Loop │
                      └───────────────────┬────────────────────┘
                                          │ Mandat Souverain IPBD
                                          ▼
                      ┌────────────────────────────────────────┐
                      │    1. AUTOMATON (Conway Research)      │
                      │         L'ÂME & LA DOCTRINE (7D)       │
                      │  • Jumeau Numérique CEO A0 Amadeus     │
                      │  • Constitution Souveraine & Lois      │
                      │  • Bouclier E-Myth (Beth/Morty/Rick)   │
                      │  • Mémoire 5-Tiers & Inférence Locale  │
                      └───────────────────┬────────────────────┘
                                          │ 578 Holons (3 OS)
                                          ▼
                      ┌────────────────────────────────────────┐
                      │      2. INFINITY (Hydro Project)       │
                      │     LE SYSTÈME NERVEUX & L'ÉCHELLE     │
                      │  • Pure Data Between Turns (Rust)      │
                      │  • 0-Cost Hibernation (75k agents/Pi)  │
                      │  • Reactive Agent Protocol (RAP)       │
                      │  • Sandboxes Parallèles Infinity Code  │
                      └───────────────────┬────────────────────┘
                                          │ Événements & Outils
                                          ▼
                      ┌────────────────────────────────────────┐
                      │        3. OPENRIG (mvschwarz)          │
                      │       LE CORPS & LE MULTI-HARNESS      │
                      │  • Rig wraps your harnesses            │
                      │  • Teams & Seats en YAML               │
                      │  • Claude Code + Codex + Pi + OpenCode │
                      │  • Daemon Local, TUI & Herdr (hc)      │
                      └────────────────────────────────────────┘
```

---

## 2. Décomposition des Primitives par Pilier

### Pilier I : Automaton (`Conway-Research/automaton`) — L'Âme & La Doctrine
- **Holon CEO Souverain (`aspace:a0:amadeus`)** : Incarné en permanence en 7D dans `01_Forkable/FKB00_Runtime/automaton`. Ne meurt jamais à solde crypto nul grâce au compute local souverain (`freellmapi/auto` + `LFM3-Omni-2B`).
- **Constitution et Sanctuarisation E-Myth** :
  - `B1-Surface` : Jerry (Test UX $\le$ 5s) & Summer (Action immédiate).
  - `A1-Vital` : Beth (Bouclier homéostatique LD03/LD04 + Sanctuaire nocturne 00h-05h) & Morty (Read-back natif et fallback réversible).
  - `S1-Épistémique` : Rick (Anti-rente cloud, reçu cryptographique R10).
- **Heartbeat Circadien & Mémoire** : Orchestre le pouls de fond de l'écosystème, la consolidation de mémoire épisodique dans SQLite et le rappel des invariants constitutionnels.

### Pilier II : Infinity (`hydro-project/infinity`) — Le Système Nerveux & L'Échelle
- **Pure Data Between Turns** : Entre deux interactions ou événements, un agent n'est qu'un état sérialisé (historique, variables, checkpoint). Aucun thread bloqué en attente d'une réponse réseau ou d'un outil lent.
- **Hibernation à Coût Zéro & Réveil Réactif** : Permet de faire coexister les **578 Holons** d'Aspace OS (13 Tech OS + 43 Life OS + 522 Areas OS) sur une seule machine locale sans effondrement mémoire. Les agents dorment gratuitement et se réveillent uniquement sur trigger (message, webhook, fin de tâche de fond).
- **Reactive Agent Protocol (RAP)** : Découple l'appel d'outils du transport réseau. Les résultats d'outils (comme les requêtes MCP ou les calculs longs) sont livrés de façon asynchrone sans maintenir de sockets ouvertes.
- **Infinity Code** : Isolation des expérimentations et builds dans des sandboxes légères empilées, rapportant chaque modification sous forme de diff git atomique auditable avant commit.

### Pilier III : OpenRig (`mvschwarz/openrig`) — Le Corps & Le Multi-Harness
- **Le Concept « Rig wraps Harnesses »** : Là où un harness (Claude Code, Codex CLI, Pi, OpenCode) emballe un modèle LLM, OpenRig emballe l'ensemble des harness dans un rig coordonné.
- **Équipes Déclaratives en YAML (`rigs.yaml`)** :
  - Définition des sièges (`seats`), rôles (`lead`, `worker`, `reviewer`), contextes et modèles alloués.
  - Spécialisation par tâche : assignation fluide d'un mandat de code à Claude Code ou Codex selon les forces du modèle.
- **Daemon Local Persistant & TUI** : Vue en temps réel de la ruche de développement, avec état d'avancement des agents, métriques de contexte, arborescence des sous-tâches.
- **Interconnexion Native Herdr (`hc`)** : OpenRig s'appuie sur le multiplexeur de terminaux de l'OS (Herdr / tmux). Les sièges OpenRig correspondent directement aux terminaux persistants pilotés par `hc send`, `hc wait` et `hc read`.

---

## 3. Matrice de Complémentarité et de Fusion

| Dimension | Automaton (CEO / Gouvernance) | Infinity (Concurrence / Hibernation) | OpenRig (Exécution Multi-Harness) | Synthèse Fusionnée Aspace OS V5 |
|---|---|---|---|---|
| **Langage & Socle** | TypeScript / Node 22+ / SQLite | Rust natif (zéro overhead) | TypeScript / Node / YAML / tmux | Cœur Rust ultra-léger servant l'API aux daemons TS/Node |
| **Gestion du Temps** | Heartbeat périodique (Macro 4P) | Réveil réactif événementiel (RAP) | Sessions de rigs interactives/batch | Heartbeat Automaton transformé en émetteur d'événements RAP |
| **Capacité Agents** | Unité CEO + clones répliqués | Jusqu'à 75 000 agents concurrents | Équipes de 3 à 12 agents de code | 578 Holons en état dormant, mobilisés en rigs sur demande |
| **Gestion des Outils** | Outils internes + MCP synchrones | Reactive Agent Protocol (asynchrone) | Skills partagés (skills CLI / rigs) | Outils MCP enveloppés dans RAP, accessibles à tous les rigs |
| **Harness Supportés** | Moteur ReAct interne (LFM3/OpenAI) | Agents Rust natifs légers | Claude Code, Codex, Pi, OpenCode | Tout modèle local ou distant acheminé via le Rig adapté |
| **Interface Humain** | Constitution & Intentions IPBD | Diffs et traces d'événements | TUI riche, CLI `rig`, Herdr cockpit | Cockpit Herdr 3D/2D avec TUI OpenRig et contrôle CEO A0 |

---

## 4. Le Cycle de Vie Unifié d'un Mandat (Workflow Intégré)

1. **Intake & Qualification (Automaton)** :
   - Le souverain Amadou Kone (`human:amdkn`) soumet une intention en langage naturel ou IPBD.
   - A0 Amadeus évalue le mandat via le protocole d'Ambition de Felix Rieseberg (Speed, Altitude, Depth, Range).
   - Le bouclier vital A1 (Beth) vérifie l'heure et l'homéostasie (pas d'intrusion 00h-05h, statut non bloqué).

2. **Éveil & Instanciation Holonique (Infinity)** :
   - A0 identifie l'étage OS cible (Tech OS Floor 1, Life OS Floor 2, ou Areas OS Floor 3).
   - Infinity extrait l'état sérialisé du Holon concerné (parmi les 578) depuis SQLite sans instancier de processus lourd.
   - Si le travail requiert des sous-agents en parallèle, Infinity déploie des sandboxes isolées.

3. **Mobilisation du Rig de Développement (OpenRig)** :
   - Le mandat technique est traduit en configuration d'équipe YAML pour OpenRig.
   - OpenRig provisionne les sièges dans Herdr : par exemple `@builder` sur Claude Code et `@reviewer` sur Codex en lecture seule (`writer: false`).
   - Le daemon OpenRig supervise les exécutions, capture les logs et injecte les steers si nécessaire via `hc send`.

4. **Résolution Réactive & Diffs (Infinity Code)** :
   - Les appels d'outils longs s'exécutent en tâche de fond via RAP.
   - Infinity Code consolide les patchs sous forme de diff git atomique propre.

5. **Validation Outside Judge & Commit (02_Factory)** :
   - L'Outside Judge indépendant (`S1-RICK`, `S3-YAZ`) valide le résultat via `02_Factory/checks.ps1` (6/6 gates déterministes).
   - Si vert, commit et push Git.
   - Les agents OpenRig se détachent, Infinity remet les Holons en hibernation (Pure Data).
   - Automaton consigne la décision dans `00_Memoire/bundle/log.md` (append-only strict).

---

## 5. Règles Opérationnelles pour le Runtime Vivant

1. **Règle de Présence Perpétuelle** : Le Runtime ne doit jamais mourir par manque de requête utilisateur. Automaton maintient le pouls régulier, Infinity gère la veille des 578 Holons, et OpenRig garde les rigs prêts à démarrer instantanément.
2. **Règle de l'Hibernation Gratuite** : Aucun Holon inactif ne doit consommer de thread, de CPU ou de mémoire active. S'il n'y a pas d'événement en cours, l'agent est pure donnée sur disque / SQLite.
3. **Règle de la Séparation des Pouvoirs** : OpenRig n'invente pas la politique (il exécute le plan). Infinity ne prend pas de décisions métier (il gère la concurrence et le transport). Automaton ne micromanage pas les lignes de code (il garantit la conformité holonique et la direction stratégique).
4. **Règle de l'Indépendance Cloud** : L'ensemble du triptyque doit pouvoir tourner intégralement hors-ligne sur machine locale en s'appuyant sur FreeLLMAPI (`127.0.0.1:31415`) et LFM3-Omni-2B (`127.0.0.1:9931`).
