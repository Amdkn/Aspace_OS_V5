# Blackwell Tensor Cores: HYMBA Model w/ MetaTokens (Small LM)

- **Source Vidéo** : [YouTube - Discover AI](https://youtu.be/gzfQpl97c5A)
- **ID Vidéo** : `gzfQpl97c5A`
- **Chaîne** : Discover AI (`@code4AI`)
- **Article Rattaché** :
  - NVIDIA : [`Hymba: A Hybrid-head Architecture for Small Language Models`](../../03_Articles/hymba_hybrid_ssm_nvidia_2024.md) (`arXiv:2411.13676`)
- **Pondération Globale MSCI** : **$W_{composite} = 0.90$** (Tier 1 — Core Invariant)

---

## 1. Primitives Extraites

1. **Primitive P1 · Architecture Hybride Parallèle (Parallel Hybrid-Head)** :
   - Fusion dans une même couche de têtes d'attention Transformer (haute résolution pour le rappel mémoire précis) et de têtes State-Space Model / Mamba (résumé global continu à coût linéaire).
   - Traitement en parallèle éliminant les goulets d'étranglement des architectures hybrides séquentielles classiques.
2. **Primitive P2 · MetaTokens** :
   - Embeddings apprenables préfixés aux séquences d'entrée servant d'initialisations spécifiques à la tâche.
   - Neutralise le phénomène d'« attention sink » des tokens de début de séquence (BOS) et redistribue optimalement la masse d'attention.
3. **Primitive P3 · Cross-Layer KV Sharing & Partial Sliding Window** :
   - Partage des clés/valeurs (KV) entre couches successives et fenêtrage glissant partiel réduisant drastiquement l'empreinte mémoire du cache.

---

## 2. Principes Invariants & Lois de Dynamique

### Principe 1 : Complémentarité Attention-SSM sans Goulot Séquentiel
> *« Traiter en parallèle l'attention (focalisation chirurgicale) et le SSM (contexte global) permet à un modèle sub-2B de surclasser un modèle Transformer classique de 3B (Llama-3.2-3B) en exactitude tout en multipliant le débit par 3.49x. »*

- **Gains Mesurés** :
  - Réduction de **11.67x** de la taille du cache KV.
  - Augmentation de **3.49x** du débit d'inférence (*throughput*).
  - Gain de **+1.32%** d'exactitude moyenne face à Llama-3.2-3B.

### Principe 2 : Élimination du Biais BOS par MetaTokens
> *« Les tokens conventionnels de début de séquence (BOS) absorbent artificiellement une proportion disproportionnée d'attention sans valeur sémantique. L'injection de MetaTokens convertit cette perte d'énergie attentionnelle en ancrage fonctionnel pré-conditionné. »*

---

## 3. Matrice de Pondération Multi-Critères ($W_{composite}$)

| Critère | Score | Justification |
|---|---|---|
| **R (Rigueur Épistémique)** | 0.92 | Publication officielle NVIDIA Research (`arXiv:2411.13676`). |
| **E (Preuve Empirique)** | 0.95 | Benchmarks exhaustifs (commonsense, recall, throughput sur GPU Blackwell/Hopper). |
| **A (Actionnabilité)** | 0.85 | Utilisation directe pour les modèles locaux légers sub-2B (LFM3, TRINITY) d'Aspace OS V5. |
| **H (Pertinence Holonique)** | 0.88 | Clé de voûte pour l'inférence souveraine locale sans explosion de VRAM sur PC portable. |
| **Score Composite ($W$)** | **0.90** | **Tier 1 (Core Invariant)** |
