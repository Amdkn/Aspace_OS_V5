# Hymba: A Hybrid-Head Architecture for Small Language Models

- **Identifiant Canonique** : `arXiv:2411.13676`
- **URL Source** : [https://arxiv.org/abs/2411.13676](https://arxiv.org/abs/2411.13676)
- **Auteurs** : Xin Dong, Saurav Muralidharan, et al.
- **Institution** : NVIDIA Research
- **Date de Publication** : Novembre 2024
- **Vidéo Associée** : [`01_Videos/chaines/discovery_ia/hymba_metatokens_small_lm.md`](../01_Videos/chaines/discovery_ia/hymba_metatokens_small_lm.md)
- **Pondération MSCI** : **$W = 0.90$** (Tier 1)

---

## 1. Résumé Exécutif & Problématique

Les petits modèles de langage (sub-2B paramètres) sont cruciaux pour l'inférence locale sur terminal, mais ils souffrent traditionnellement d'un compromis douloureux :
- Les **Transformers** purs garantissent un excellent rappel mémoire haute résolution mais souffrent d'une explosion de la mémoire du cache KV lors de longues séquences.
- Les modèles **SSM (State-Space Models, ex. Mamba)** offrent une efficacité computationnelle linéaire mais échouent sur les tâches de rappel intensif à granularité fine.

**Hymba** introduit une architecture hybride en têtes parallèles (Parallel Hybrid-Head) combinant simultanément les deux mécanismes au sein de chaque bloc résiduel.

---

## 2. Découvertes Clés & Innovations Techniques

- **MetaTokens** : Embeddings apprenables insérés en début de prompt qui préconditionnent le réseau et éliminent l'effet parasitaire d'« attention sink » des tokens BOS classiques.
- **Cross-Layer KV Sharing & Partial Sliding Window** : Réduction spectaculaire de **11.67x** de la taille du cache mémoire KV.
- **Gain de Débit Inférence** : Multiplié par **3.49x** en vitesse de génération.
- **Surpassement de Modèles Plus Lourds** : Hymba-1.5B surpasse Llama-3.2-3B (+1.32% en exactitude moyenne) tout en consommant une fraction de la mémoire GPU.

---

## 3. Impact sur Aspace OS V5

- **Inférence Locale Souveraine** : Les agents locaux d'Aspace OS V5 (ex. modèles légers `TRINITY` ou `LFM3-Omni-2B` sur `127.0.0.1:9931` et `freellmapi/auto` sur `:31415`) bénéficient directement de ces principes pour exécuter des boucles rapides d'inspection sans requérir de serveurs cloud surpuissants.
