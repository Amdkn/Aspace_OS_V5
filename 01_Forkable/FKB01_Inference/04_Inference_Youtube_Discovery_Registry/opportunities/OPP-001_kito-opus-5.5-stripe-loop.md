# OPP-001 : Claude Opus 5.5 & Kito Pro (Amazon Coding Agent)

| Métrique | Valeur |
|---|---|
| **Source YouTube** | *"Claude Opus 5.5 is Now 100% FREE (NEW Method)"* |
| **Plateforme Cible** | `https://kito.dev` (Kito Agent / Kiro) |
| **Modèles Offerts** | Claude Opus 5.5, Sonnet 5.5, Claude Haiku, GPT-5.6 Soul, Jimmy K3 |
| **Volume de Calcul** | 50 $ à 200 $ d'utilisation selon le plan choisi (Kito Pro Plus 40$ / Kito Power 200$) |
| **Statut Watch Skill** | **ACTIF (SURVEILLANCE FACTURATION)** |
| **Vecteur d'Injection** | **Voie B (Interface Web & Session)** |

---

## 1. Mécanisme de l'Astuce (Stripe Invoice Loop)
1. Inscription sur `kito.dev` (compte gratuit initial).
2. Sélection d'un forfait supérieur (ex: *Kito Pro Plus* à 40$/mois).
3. La facture Stripe indique **0 € / 0 $ dus immédiatement**, avec prélèvement programmé au 1er du mois suivant.
4. Immédiatement après validation, retourner dans le dashboard et **rétrograder vers le plan gratuit**.
5. L'abonnement payant reste actif avec l'intégralité des crédits jusqu'au 1er du mois sans prélèvement.

---

## 2. Analyse Anti-Matraquage & Risques
- **Fiabilité Modèle** : Le modèle répond authentiquement en tant qu'Opus / Sonnet via les prompts de vérification miroir.
- **Risque Facturation / Frictionalité** : **ÉLEVÉ**. Nécessite la saisie d'une carte bancaire valide. Les banques ou Stripe peuvent déclencher des micro-autorisations ou patcher la fenêtre de grâce (prorata immédiat) après acquisition massive suite à la vidéo.
- **Recommandation Aspace OS** : Ne jamais utiliser de carte bancaire principale. Utiliser exclusivement des cartes virtuelles à plafond 0 € ou à usage unique.

---

## 3. Intégration Aspace OS V5
- Non compatible API directe (pas de clé API fournie en clair).
- **Vecteur d'exploitation** : Embarquer la session Kito dans `Codex-ChatGPT-Web` ou scripter les requêtes d'agent via `API-Anything` (FKB04).
