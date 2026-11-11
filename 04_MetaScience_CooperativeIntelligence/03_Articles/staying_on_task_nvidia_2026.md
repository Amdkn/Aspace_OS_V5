# Staying on Task: Testing the Foundations of Long-Horizon Agent Reliability

- **Identifiant Canonique** : `arXiv:2609.38712`
- **URL Source** : [https://arxiv.org/abs/2609.38712](https://arxiv.org/abs/2609.38712)
- **Auteurs** : Jeffrey Willette, Krishna C. Puvvada, Boris Ginsburg
- **Institution** : NVIDIA Research
- **Date de Publication** : Septembre 2026
- **Vidéo Associée** : [`01_Videos/chaines/discovery_ia/nvidia_math_breaking_agents.md`](../01_Videos/chaines/discovery_ia/nvidia_math_breaking_agents.md)
- **Pondération MSCI** : **$W = 0.95$** (Tier 1)

---

## 1. Résumé Exécutif & Problématique

Pourquoi les agents autonomes échouent-ils systématiquement lorsqu'on leur confie des tâches à long horizon (exécutions de dizaines d'étapes dépendantes) ?
NVIDIA présente le protocole de diagnostic **Long-Transduction**, qui évalue la capacité des modèles à lire, mettre à jour et propager des structures de données complexes (tableaux, variables, opérations arithmétiques chaînées) sur des trajectoires longues.

---

## 2. Découvertes Clés & Facteurs d'Effondrement

En analysant 7 modèles open-weights de premier plan, les auteurs isolent 3 axes indépendants responsables de la perte de contrôle :
1. **Mise à l'Échelle du Contexte (4k $\rightarrow$ 128k)** : Chute de **-62.8%** de la fiabilité opérationnelle.
2. **Complexité Locale de la Tâche** : Chute de **-39.9%** de la fiabilité.
3. **Variations du Formatage d'Entrée** : Chute de **-36.5%** de la fiabilité.

### Conclusion Épistémique
Le fait qu'un modèle supporte techniquement 128k tokens ne garantit aucunement sa capacité à rester fidèle à une instruction sur cette durée. L'entropie d'attention détruit la fiabilité agentique bien avant la limite physique de contexte.

---

## 3. Impact sur Aspace OS V5

- **Règle des 5 Secondes Shell & Tâches Bornées** : Sanctuarisation de la règle DeepSeek Superagent / Fable 5. Aucune session agentique ne doit accumuler des dizaines d'actions dans un même tour.
- **Vérifications Chirurgicales & Tests Déterministes** : Chaque étape doit être contrôlée par un outil de validation (`02_Factory/checks.ps1`) plutôt que de faire confiance à l'auto-évaluation interne du LLM.
