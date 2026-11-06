# ImplicitHop: Evaluating Knowledge Integration Across Context and Memory

- **Identifiant Canonique** : `arXiv:2610.41169`
- **URL Source** : [https://arxiv.org/abs/2610.41169](https://arxiv.org/abs/2610.41169)
- **Auteurs** : Alexander Detkov, Dashiel Karish, Matthew Oleynikov, Matt Thomson
- **Institution** : California Institute of Technology (Caltech)
- **Date de Publication** : Octobre 2026
- **Vidéo Associée** : [`01_Videos/chaines/discovery_ia/nvidia_context_rot_sssm.md`](../01_Videos/chaines/discovery_ia/nvidia_context_rot_sssm.md)
- **Pondération MSCI** : **$W = 0.92$** (Tier 1)

---

## 1. Résumé Exécutif & Problématique

Les modèles de langage (LLMs) ont la réputation d'être d'excellents moteurs d'inférence. Pourtant, lorsqu'on les teste sur la **déduction implicite multi-sauts (*multi-hop reasoning*)** — combiner deux ou plusieurs prémisses disséminées pour en déduire un fait non formulé —, leurs performances s'effondrent brutalement dès que l'on n'utilise pas de prompting explicite de type Chain-of-Thought (CoT).

L'équipe de Caltech a créé le benchmark **ImplicitHop** afin de mesurer quantitativement cette profondeur d'intégration selon deux axes :
1. Un banc d'essai formel sur des **graphes synthétiques** contrôlant rigoureusement la topologie et la distance géodésique des nœuds.
2. Un banc d'essai ancré dans le monde réel sur des sous-graphes **Wikidata**.

---

## 2. Découvertes Clés & Formulations Mathématiques

- **Chute Abrupte de l'Exactitude** : L'exactitude $A(k)$ suit une loi de décroissance quasi-exponentielle en fonction de la longueur de composition $k$ (nombre de sauts déductifs) :
  $$A(k) \propto e^{-\lambda k}$$
- **Asymétrie Contexte vs Poids Pré-entraînés** : Les informations injectées directement dans la fenêtre de contexte courante (*in-context*) obtiennent un taux de réussite systématiquement supérieur aux faits stockés de manière implicite dans les poids du modèle pré-entraîné.
- **Implication pour les Agents** : L'espoir qu'un LLM fasse spontanément la synthèse de dizaines de notions encyclopédiques apprises lors de son pré-entraînement sans rappel textuel direct est scientifiquement invalidé.

---

## 3. Impact sur Aspace OS V5

- **Règle d'Hygiène WikiLLM** : Justifie l'interdiction de laisser les agents deviner l'architecture. Tout invariant ou contrat doit être explicitement injecté via `search_nodes` / `open_nodes` dans le prompt de travail.
- **Délégation Séquentielle** : Les raisonnements multi-sauts doivent être découpés en micro-étapes explicites à 1 saut maximum vérifié par retour d'outil déterministe.
