# Needle + GLiNER — Pile edge-first préservée

Source : reconstitué par le Capitaine depuis les réponses Gemini, 2026-11-04.
Perdu par Gemini, préservé ici. Texte intégral ci-dessous, non modifié.

---

C'est la pièce manquante exacte pour verrouiller une architecture **Edge-First, souveraine et ultra-légère** sans dépendre de services cloud lourds.

En combinant **Cactus Needle** pour le *Tool Calling* déterministe sur l'appareil et **GLiNER2.5-multi-Decide** pour la classification et le routage multilingue, le système passe d'un assemblage théorique à une **pile opérationnelle locale complète**.

---

### 1. Cactus Needle : Le Moteur d'Exécution et de Tool Calling Edge

* **Ce que c'est :** Un modèle fondation agentique ultraléger (disponible en versions quantifiées 2-bit, pesant entre 8 et 29 Mo) conçu spécifiquement pour le *tool calling*, l'extraction structurée et l'ASR (via son module compagnon **Whistle**) sur des appareils aux ressources contraintes (Raspberry Pi, smartphones, microcontrôleurs).
* **Son rôle dans l'architecture :** Au lieu d'interroger un LLM lourd pour exécuter des actions système, **Needle** prend un texte ou un flux audio et renvoie un objet JSON structuré contenant les appels de fonctions précis (`function_calls`), avec un score de confiance calibré et un décodage contraint par grammaire.
* **Fine-Tuning LoRA local :** Il permet d'entraîner et d'exporter des adaptateurs LoRA directement sur votre machine pour vos propres jeux d'outils métier (commandes de l'OS, scripts de gestion, interactions de la *SOB*) sans quitter l'environnement local.

### 2. GLiNER2.5-multi-Decide : Le Routeur Sémantique et Multilingue

* **Ce que c'est :** Un modèle de classification et d'extraction multilingue de 287M de paramètres (construit sur `mDeBERTa-v3-base`) qui permet d'évaluer des ensembles de labels dynamiques à la volée (intention, priorité, politique, tags multi-labels) sans générer de prose inutile.
* **Son rôle dans l'architecture :** Il agit comme la **barrière d'entrée cognitive et linguistique** (notamment pour gérer le bilinguisme ou le traitement des flux textuels/vocaux en entrée). Il classifie instantanément l'intention de la requête, détecte l'urgence, ou extrait les entités clés avec une précision redoutable, sur CPU ou GPU, sans latence superflue.

---

### 3. Matrice de la Pile Complète : Du Signal Brut à l'Action Souveraine

| Composant | Technologie | Rôle Clé dans l'Écosystème A'Space OS |
| --- | --- | --- |
| **Capture & Compression Audio** | **Mimi** (Kyutai) / **Whistle** (Cactus) | Ingestion du flux audio en streaming continu (12.5 Hz / ASR local). |
| **Routage & Classification** | **GLiNER2.5-multi-Decide** (Fastino) | Analyse d'intention multilingue, classification multi-labels et filtrage sémantique à la volée. |
| **Tool Calling & Exécution Déterministe** | **Cactus Needle** (LoRA local) | Cartographie des requêtes vers les outils système, génération de JSON structurés et exécution sans hallucination. |
| **Continuité Omnimodale & Style** | **LFM3-Omni-2B** + LoRA (`SOUL.md`) | Synthèse, coloration identitaire et orchestration globale du jumeau numérique. |

---

### 4. Flux d'Exécution d'une Requête (Pipeline Local)

```text
[ Voix / Texte Entrant ]
         │
         ▼
[ 1. GLiNER2.5-multi-Decide ] ──> Analyse d'intention, langue et classification multi-label (0 hallucination)
         │
         ▼ (Si action système requise)
[ 2. Cactus Needle (Fine-tuned LoRA) ] ──> Mapping déterministe vers les fonctions & Tool Calls JSON
         │
         ▼
[ 3. Exécution Système & Rétro-alimentation ] ──> Mise à jour Airtable/Supabase via l'orchestration locale

```

Cette structure garantit une **sobriété informatique absolue** (pas de consommation de GPU massif pour des tâches logiques simples) tout en offrant une précision chirurgicale sur l'intention, le multilingue et le déclenchement d'outils.
