# OPP-003 : Tencent Hunyuan 4 (HY4) via APINex (20M Tokens / Jour)

| Métrique | Valeur |
|---|---|
| **Source YouTube** | *"How to Get FREE API Keys for DeepSeek V4.1 Flash (Abliterated) & HY4"* |
| **Plateforme Cible** | `https://apinex.com` |
| **Modèle Offert** | **Tencent Hunyuan 4 (HY4)** (Contexte 1 Million de tokens) |
| **Volume de Calcul** | **20 Millions de tokens gratuits CHAQUE JOUR** |
| **Statut Watch Skill** | **PÉPITE SOUVERAINE (SCORE A+)** |
| **Vecteur d'Injection** | **Voie A (Passerelle API Directe FreeLLMAPI)** |

---

## 1. Mécanisme d'Accès
1. Inscription sur `apinex.com` sans carte de crédit.
2. Dashboard $\rightarrow$ *Modèles & Tarification* $\rightarrow$ groupe *Free*.
3. Le modèle **HY4** est listé avec l'étiquette gratuite, doté d'une fenêtre de contexte de 1M de tokens et d'une recharge quotidienne automatique de **20 000 000 de tokens**.
4. Création immédiate de la clé API.

---

## 2. Analyse Anti-Matraquage & Valeur Industrielle
- **Volume Colossal** : 20 millions de tokens quotidiens gratuits constituent l'une des allocations les plus généreuses du marché pour un modèle de classe frontière (contexte 1M).
- **Stabilité** : Contrairement aux essais temporaires de 7 jours, il s'agit d'une politique de quota quotidien renouvelable.
- **Remplacement de Dépendance Payante** : Capable d'absorber l'intégralité du trafic de lecture de contexte lourd de la Factory sans consommer 1 centime.

---

## 3. Intégration Aspace OS V5
- **Dans FreeLLMAPI** : Ajout du provider `apinex` avec le modèle `apinex/tencent-hy4` dans la chaîne de fallback automatique.
- **Dans Claude Code / Pi** : Paramétrage du Base URL APINex pour des sessions à très long contexte (jusqu'à 1 million de tokens).
