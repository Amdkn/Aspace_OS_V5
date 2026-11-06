# When Reasoning Goes Astray: Attention Dynamics of Uncontrolled Reasoning

- **Identifiant Canonique** : `arXiv:2609.38817`
- **URL Source** : [https://arxiv.org/abs/2609.38817](https://arxiv.org/abs/2609.38817)
- **Auteurs** : Yuanhe Zhang, Ziwei Wang, Jie Ren, Haoran Gao, Zhenhong Zhou, Fanyu Meng, Cong Wu, Li Sun, Sen Su
- **Institutions** : Beijing University of Posts and Telecommunications (BUPT), Wuhan University, JIUTIAN Research, Nanyang Technological University
- **Date de Publication** : Septembre 2026
- **Vidéo Associée** : [`01_Videos/chaines/discovery_ia/nvidia_math_breaking_agents.md`](../01_Videos/chaines/discovery_ia/nvidia_math_breaking_agents.md)
- **Pondération MSCI** : **$W = 0.93$** (Tier 1)

---

## 1. Résumé Exécutif & Problématique

L'avènement des modèles de raisonnement (LRM / Test-time compute scaling, tels que OpenAI o1/o3, DeepSeek-R1, Qwen-QwQ) repose sur de longues chaînes de réflexion explicite (CoT). Cependant, ce processus est vulnérable à des pathologies graves :
- Sur-réflexion (*overthinking*) stérile.
- Boucles de vérification infinies (*persistent loops*).
- Épuisement catastrophique des tokens sans gain qualitatif.

Ce papier propose le premier cadre théorique et diagnostique pour détecter l'amorce de ces dérives avant que la répétition de surface ne se produise.

---

## 2. Découvertes Clés & Cadre RADAR

- **Quatre États Fonctionnels de Raisonnement** :
  1. $D$ : Réponse directe (*Direct answering*).
  2. $R$ : Réflexion efficace (*Effective reflection*).
  3. $O$ : Réflexion excessive (*Excessive reflection / overthinking*).
  4. $L$ : Boucle persistante (*Persistent looping*).
- **Le Système RADAR (Reasoning-state Analysis via Dynamic Attention Responses)** :
  Mesure deux indicateurs attentionnels dynamiques :
  - **PAS (Prompt Attention Share)** : Proportion de l'attention allouée au prompt initial vs aux tokens générés.
  - **CTS (Cross-context Token Similarity)** : Degré de répétition géométrique des schémas attentionnels.
- **Détection Précoce** : Les distributions d'attention s'écartent anormalement des profils sains **bien avant** l'apparition des premiers tokens textuels redondants.
- **Intervention (Attention Realignment)** : Rétablir une distribution attentionnelle équilibrée stoppe immédiatement les boucles et force la conclusion du raisonnement.

---

## 3. Impact sur Aspace OS V5

- **Garde Anti-Boucle Fable 5** : Tout agent doit limiter son texte visible à 1–2 phrases et couper immédiatement toute rumination textuelle non adossée à une exécution d'outil.
- **Règle du Ratio 80/20** : Le CoT profond doit produire un appel d'outil chirurgical dans les 5 secondes sous peine de basculer en tâche de fond (`hc run --bg`) ou d'être interrompu par le superviseur S1 (`S1-RICK`).
