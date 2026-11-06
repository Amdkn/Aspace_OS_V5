# NVIDIA Solves Context Rot, Invents New State Space Model

- **Source Vidéo** : [YouTube - Discover AI](https://youtu.be/4yaNxPU9pxI)
- **ID Vidéo** : `4yaNxPU9pxI`
- **Chaîne** : Discover AI (`@code4AI`)
- **Articles Rattachés** :
  - Caltech : [`ImplicitHop: Evaluating knowledge integration across context and memory`](../../03_Articles/implicit_hop_caltech_2026.md) (`arXiv:2610.41169`)
  - NVIDIA : [`You don't need long context`](../../03_Articles/you_dont_need_long_context_nvidia_2026.md) (`arXiv:2611.05306`)
- **Pondération Globale MSCI** : **$W_{composite} = 0.93$** (Tier 1 — Core Invariant)

---

## 1. Primitives Extraites

1. **Primitive P1 · Context Rot (Pourrissement de Contexte)** :
   - Dégradation progressive de l'attention et de la cohérence logique à mesure que le nombre de tokens injectés dans le prompt actif augmente.
   - Même si la fenêtre technique accepte 128k+ tokens, l'efficacité réelle de transduction décroît de manière non linéaire.
2. **Primitive P2 · SSSM (Semantic State Space Model)** :
   - Architecture alternative au tout-attention qui encode l'historique sous forme d'états latents continus compressés sémantiquement, éliminant l'explosion quadratique du cache KV.
3. **Primitive P3 · Multi-Hop Integration Gap** :
   - Écart mesurable entre la capacité d'un modèle à restituer des faits unitaires et son incapacité à déduire implicitement une vérité résultant de la composition de ces faits sans chaîne de pensée forcée.

---

## 2. Principes Invariants & Lois de Dynamique

### Principe 1 : Loi de Compaction Fréquente de Belcak (NVIDIA)
> *« Une stratégie de compaction fréquente d'état avec note de passage (handoff note) sur de petites fenêtres de contexte (16k–48k) égale ou dépasse la précision d'un contexte étendu monolithique tout en réduisant le coût de calcul de 3.6x à 7x. »*

- **Preuve Empirique** : Validation sur SWE-bench Verified et benchmarks long-horizon par l'équipe de Peter Belcak et Pavlo Molchanov (NVIDIA).
- **Application Aspace OS V5** : Justifie mathématiquement le protocole `handoff` de Pi Durable Subagents et l'interdiction de `read_graph` brut en routine.

### Principe 2 : Loi de Décroissance Exponentielle Multi-Hop (Caltech)
> *« L'exactitude déductive d'un modèle chute exponentiellement avec le nombre de sauts logiques requis (hop length), et les faits fournis directement in-context surclassent massivement les connaissances implicites figées dans les poids pré-entraînés. »*

- **Application Aspace OS V5** : Privilégier systématiquement l'injection d'extraits chirurgicaux ciblés via `search_nodes` / `open_nodes` plutôt que d'espérer une déduction magique issue de la mémoire dormante du LLM.

---

## 3. Matrice de Pondération Multi-Critères ($W_{composite}$)

| Critère | Score | Justification |
|---|---|---|
| **R (Rigueur Épistémique)** | 0.95 | Deux publications académiques de pointe (Caltech & NVIDIA Research). |
| **E (Preuve Empirique)** | 0.90 | Benchmarks contrôlés sur SWE-bench, graphes synthétiques et Wikidata. |
| **A (Actionnabilité)** | 0.92 | Immédiatement applicable via notre commande `subagents -Action handoff`. |
| **H (Pertinence Holonique)** | 0.96 | Valide et sanctuarise l'hygiène de contexte de nos 578 holons. |
| **Score Composite ($W$)** | **0.93** | **Tier 1 (Core Invariant)** |
