# When Context Changes: Understanding Update Failures in LLMs

- **Identifiant Canonique** : `arXiv:2609.38866`
- **URL Source** : [https://arxiv.org/abs/2609.38866](https://arxiv.org/abs/2609.38866)
- **Auteurs** : Junyu Guo, Yuchen Fang, Shangding Gu, Costas Spanos, James Demmel, Javad Lavaei
- **Institution** : University of California, Berkeley (UC Berkeley)
- **Date de Publication** : Septembre 2026
- **Vidéo Associée** : [`01_Videos/chaines/discovery_ia/nvidia_math_breaking_agents.md`](../01_Videos/chaines/discovery_ia/nvidia_math_breaking_agents.md)
- **Pondération MSCI** : **$W = 0.94$** (Tier 1)

---

## 1. Résumé Exécutif & Problématique

Dans les applications agentiques réelles, les variables changent continuellement d'état (ex. `status = "pending"` devient `status = "completed"`, ou les coordonnées d'un holon sont révisées). Les versions obsolètes restent souvent visibles dans l'historique de conversation aux côtés des versions récentes.
Les chercheurs de Berkeley identifient la pathologie majeure qui en résulte : le **Stale Binding** (liaison obsolète), où le modèle continue à utiliser la valeur passée malgré la présence explicite de la mise à jour dans le prompt.

---

## 2. Découvertes Clés & Mécanisme Mathématique

- **Benchmark CICM (Controlled In-Context Memory)** : Même les modèles les plus avancés échouent fréquemment à extraire la valeur la plus récente d'une entité dynamique.
- **Preuve par Sonde Linéaire (Linear Probing)** : La valeur mise à jour *est bel et bien encodée* dans les représentations internes cachées du réseau. L'échec n'est donc **pas un défaut de mémorisation**, mais un **défaut de sélection**.
- **Mécanisme de Dérive d'Attention (Attention Drift)** :
  Dans une couche d'attention :
  $$\text{Score}(\text{Old}) = \sum_{i=1}^M \text{Attn}(\text{Old}_i) \quad \text{vs} \quad \text{Score}(\text{New}) = \text{Attn}(\text{New})$$
  Si plusieurs occurrences de l'ancienne valeur existent dans l'historique, la somme cumulée de leurs scores d'attention finit par surpasser l'unique score de la nouvelle valeur, trompant la tête de sortie.
- **Solution (Attention Realignment)** : Une intervention sans ré-entraînement forçant la réorientation des poids d'attention vers l'élément temporellement le plus récent restaure quasi-parfaitement l'exactitude.

---

## 3. Impact sur Aspace OS V5

- **Principe d'Immutabilité & Nettoyage de Contexte** :
  - Empêcher l'accumulation de valeurs contradictoires ou obsolètes dans les prompts des agents.
  - Utiliser SQLite (`factory.sqlite`) comme seule source de vérité d'état avec ID de requête idempotent (`requestId`), plutôt que de laisser l'agent relire un fil de discussion pollué par 10 révisions intermédiaires.
