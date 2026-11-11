# OPP-004 : Croton Alpha 1M Context via OpenRouter & Kilo Code

| Métrique | Valeur |
|---|---|
| **Source YouTube** | *"New Stealth AI Model is FREE! 1M Context | OpenRouter, Kilo & OpenCode"* |
| **Plateforme Cible** | `https://openrouter.ai` / Killo Gateway |
| **Modèle Offert** | **Croton Alpha** (Modèle furtif multimodal, Contexte 1M, Zéro entraînement sur data) |
| **Volume de Calcul** | Gratuit pendant 7 jours (phase d'évaluation publique) |
| **Statut Watch Skill** | **ÉPHÉMÈRE / FENÊTRE FLASH (TTL 7 JOURS)** |
| **Vecteur d'Injection** | **Voie A (Déjà routé dans FreeLLMAPI)** |

---

## 1. Mécanisme d'Accès
1. Connexion sur OpenRouter (ou via la passerelle Killo Gateway / OpenCode).
2. Clé API OpenRouter sans restriction de crédit (`limit: none`).
3. Sélection du modèle `croton/croton-alpha` (ou alias Killo Gateway).
4. Accès instantané à une fenêtre de contexte de 1M de tokens avec raisonnement rapide (2-3s par réponse).

---

## 2. Analyse Anti-Matraquage & Durabilité
- **Modèle Stealth (Laboratoire masqué)** : Souvent déployé sous couvert d'anonymat pour recueillir des retours comparatifs avant un lancement officiel payant.
- **Péremption Rapide** : Annoncé gratuit pour 7 jours seulement. Risque de bascule payante sans préavis ou de saturation des serveurs OpenRouter.
- **Déduplication FLA** : OpenRouter fait déjà partie intégrante des 34 providers de `FreeLLMAPI` ! Aucune infrastructure nouvelle n'est nécessaire.

---

## 3. Intégration Aspace OS V5
- Il suffit d'activer l'alias `croton-alpha` dans la configuration existante de `FreeLLMAPI` pour tester sa puissance de raisonnement et de génération de code avant la fin de la fenêtre de gratuité.
