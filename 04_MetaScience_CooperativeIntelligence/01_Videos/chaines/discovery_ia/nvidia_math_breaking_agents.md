# NVIDIA: We Need a New Math for AI Models

- **Source Vidéo** : [YouTube - Discover AI](https://youtu.be/__SmkVks-Qg)
- **ID Vidéo** : `__SmkVks-Qg`
- **Chaîne** : Discover AI (`@code4AI`)
- **Articles Rattachés** :
  - NVIDIA : [`Staying on Task: Testing the Foundations of Long-Horizon Agent Reliability`](../../03_Articles/staying_on_task_nvidia_2026.md) (`arXiv:2609.38712`)
  - UC Berkeley : [`When Context Changes: Understanding Update Failures in LLMs`](../../03_Articles/when_context_changes_berkeley_2026.md) (`arXiv:2609.38866`)
  - BUPT : [`When Reasoning Goes Astray: Attention Dynamics of Uncontrolled Reasoning`](../../03_Articles/when_reasoning_goes_astray_bupt_2026.md) (`arXiv:2609.38817`)
- **Pondération Globale MSCI** : **$W_{composite} = 0.94$** (Tier 1 — Core Invariant)

---

## 1. Primitives Extraites

1. **Primitive P1 · Long-Transduction Reliability** :
   - Capacité d'un agent autonome à lire, modifier et propager des opérations dépendantes d'un contexte volumineux sur des centaines d'étapes sans dévier ni perdre sa consigne initiale.
2. **Primitive P2 · Stale Binding (Liaison Obsolète)** :
   - Pathologie critique des LLMs dans les environnements dynamiques où le modèle s'accroche à une valeur ancienne d'une variable ou d'un état alors qu'une mise à jour plus récente est présente dans le contexte.
3. **Primitive P3 · Attention Drift (Dérive Attentionnelle)** :
   - Phénomène mathématique démontrable sur un Transformer où la somme cumulée des scores d'attention d'anciennes valeurs historiques surpasse le score d'attention de la valeur actuelle unique.
4. **Primitive P4 · États de Raisonnement LRM & Métriques RADAR** :
   - Les 4 états fonctionnels d'un modèle de raisonnement : Réponse Directe ($D$), Réflexion Efficace ($R$), Réflexion Excessive / Sur-pensée ($O$), Boucle Persistante ($L$).
   - Métriques : **PAS** (*Prompt Attention Share*) et **CTS** (*Cross-context Token Similarity*).

---

## 2. Principes Invariants & Lois de Dynamique

### Principe 1 : Effondrement de Fiabilité sur Long Horizon de Willette (NVIDIA)
> *« La simple extension brute du contexte (de 4k à 128k tokens) provoque un effondrement de 62.8% de la fiabilité d'exécution d'un agent. L'accroissement de la complexité locale de la tâche cause une baisse de 39.9%, et la variation de formatage d'entrée 36.5%. »*

- **Preuve Empirique** : Évaluation Long-Transduction sur 7 modèles open-weights par NVIDIA.
- **Règle Aspace OS V5** : Règle Fable 5 / Pi Durable : limiter les prompts à des formats chirurgicaux stricts et découper les longues tâches en sous-agents durables idempotents avec `requestId`.

### Principe 2 : Loi de Berkeley sur l'Échec de Sélection (Stale Binding)
> *« L'échec face au changement de contexte n'est pas un problème de mémoire (la valeur actuelle est présente et détectable dans les représentations internes par sonde linéaire), mais un pur échec de sélection attentionnelle causé par l'accumulation historique. »*

- **Intervention** : Réalignement d'attention sans entraînement (*training-free intervention*), réorientant l'attention vers l'état actuel.

### Principe 3 : Détection Précoce des Boucles Inutiles de BUPT (RADAR)
> *« La dérive attentionnelle vers la sur-réflexion ou le blocage en boucle infinie est détectable au niveau des poids d'attention dynamiques (baisse anormale du PAS et hausse du CTS) BIEN AVANT que la répétition textuelle de surface ne devienne visible. »*

---

## 3. Matrice de Pondération Multi-Critères ($W_{composite}$)

| Critère | Score | Justification |
|---|---|---|
| **R (Rigueur Épistémique)** | 0.96 | Triple validation expérimentale (NVIDIA Research, UC Berkeley, BUPT/Wuhan). |
| **E (Preuve Empirique)** | 0.94 | Benchmarks dédiés (Long-Transduction, CICM, RADAR classifier). |
| **A (Actionnabilité)** | 0.90 | Détection d'erreurs en amont, reset de contexte et hygiène de prompt. |
| **H (Pertinence Holonique)** | 0.98 | Clé absolue pour la résilience des agents autonomes 24/7 dans Cube Farm. |
| **Score Composite ($W$)** | **0.94** | **Tier 1 (Core Invariant)** |
