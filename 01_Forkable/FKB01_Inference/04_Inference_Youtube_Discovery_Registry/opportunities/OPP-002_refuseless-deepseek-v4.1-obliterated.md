# OPP-002 : DeepSeek V4.1 Flash Obliterated via Refuseless.com

| Métrique | Valeur |
|---|---|
| **Source YouTube** | *"How to Get FREE API Keys for DeepSeek V4.1 Flash (Abliterated) & HY4"* |
| **Plateforme Cible** | `https://refuseless.com` |
| **Modèle Offert** | **DeepSeek V4.1 Flash Obliterated** (Contexte 512K, Max Output 120K) |
| **Volume de Calcul** | 100 crédits dédiés offerts (solde isolé sans empiéter sur le solde principal) |
| **Statut Watch Skill** | **QUALIFIÉ & EXPLOITABLE IMMÉDIATEMENT** |
| **Vecteur d'Injection** | **Voie A (Passerelle API Directe FreeLLMAPI / Claude Code)** |

---

## 1. Mécanisme d'Accès
1. Connexion sur `refuseless.com` via Google Auth (zéro carte bancaire requise).
2. Accès à l'onglet *Models* : DeepSeek V4.1 Flash marqué comme gratuit avec 100 crédits de bienvenue conservés dans un compte dédié.
3. Génération d'une clé API native dans l'onglet *API keys*.

---

## 2. Analyse Anti-Matraquage & Avantages
- **Séparation des soldes** : Le solde gratuit n'est pas siphonné par d'autres modèles ou requêtes parasites.
- **Modèle Obliterated (Uncensored)** : Débridé de tout garde-fou restrictif, idéal pour le travail de rétro-ingénierie (`rea`) et de red-teaming (`MiroFish`).
- **Compatibilité Totale** : Fournit une base URL compatible avec l'API Anthropic (`/v1`) et OpenAI.

---

## 3. Intégration Aspace OS V5
- **Dans Claude Code** : Remplacer l'URL de base et l'auth token dans `~/.claude/settings.json`.
- **Dans FreeLLMAPI (`:31415`)** : Déclarer un endpoint personnalisé `refuseless/deepseek-v4.1-flash-obliterated` avec son Bearer token.
