# You Don't Need Long Context

- **Identifiant Canonique** : `arXiv:2611.05306`
- **URL Source** : [https://arxiv.org/abs/2611.05306](https://arxiv.org/abs/2611.05306)
- **Auteurs** : Peter Belcak, Saurav Muralidharan, Jindong Jiang, Yonggan Fu, Wonmin Byeon, Hanrong Ye, Ryan Angilly, Ali Taghibakhshi, Shih-Yang Liu, Siru Ouyang, Greg Heinrich, Pavlo Molchanov
- **Institution** : NVIDIA Research
- **Date de Publication** : Novembre 2026
- **Vidéo Associée** : [`01_Videos/chaines/discovery_ia/nvidia_context_rot_sssm.md`](../01_Videos/chaines/discovery_ia/nvidia_context_rot_sssm.md)
- **Pondération MSCI** : **$W = 0.96$** (Tier 1)

---

## 1. Résumé Exécutif & Problématique

L'industrie de l'IA fait une course effrénée vers des fenêtres de contexte gigantesques (1M à 10M de tokens). NVIDIA Research démontre dans cette publication fondamentale que cette approche est à la fois économiquement intenable et architectoniquement sous-optimale :
- Servir des tokens en profondeur dans un grand contexte est **3.6x à 7x plus coûteux** en mémoire et en temps de calcul GPU.
- L'attention quadratique s'enlise et disperse l'énergie cognitive du modèle.

Les auteurs prouvent qu'en substituant à un contexte brut massif une procédure de **compaction fréquente avec note de passage (*handoff note*)**, les modèles maintiennent ou améliorent leur taux de réussite sur les tâches complexes de génie logiciel (SWE-bench Verified) et les tâches multi-étapes à long terme.

---

## 2. Découvertes Clés & Formulations Mathématiques

- **Résilience aux Fenêtres Courtes** : Des fenêtres de 16k à 48k tokens suffisent largement pour résoudre les problèmes logiciels les plus ardus, à condition d'épurer périodiquement l'historique d'exécution.
- **Principe de l'Action Unique par Contexte** : Limiter un agent à une seule action décisive par contexte compacté avant réévaluation élimine les dérives d'attention accumulées.
- **Introduction aux SSSM (Semantic State Space Models)** : Fondation d'un nouveau paradigme où le contexte n'est plus une suite linéaire brute de tokens KV mais un état continu récurrent mis à jour sémantiquement.

---

## 3. Impact sur Aspace OS V5

- **Validation Formelle de Pi Durable Subagents** :
  - L'action `pwsh -NoProfile -File 02_Factory/factory.ps1 subagents -Action handoff -Note "..."` implémente exactement la recommandation de NVIDIA.
  - La commande `/compact` dans le chat UI et les résumés compacts automatiques protègent le système contre l'explosion des coûts et le pourrissement de contexte (*context rot*).
