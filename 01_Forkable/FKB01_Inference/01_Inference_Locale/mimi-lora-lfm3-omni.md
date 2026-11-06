# Mimi + LoRA sur LFM3-Omni-2B — Synthèse préservée

Source : reconstitué par le Capitaine depuis les réponses Gemini, 2026-11-04.
Perdu par Gemini, préservé ici. Texte intégral ci-dessous, non modifié.

---

Intégrer la logique de tokenisation de **Mimi** (12.5 Hz, 1.1 kbps) dans une démarche de type **LoRA** (Low-Rank Adaptation) sur un modèle omnimodal comme **LFM3-Omni-2B** est tout à fait pertinent pour alléger le système tout en injectant la dimension paralinguistique (le flow, les souffles, le timbre des rappeurs) dans le `SOUL.md`.

Voici comment articuler cette fusion en évitant d'alourdir l'infrastructure :

---

### 1. Pourquoi utiliser LoRA pour adapter le codec audio ?

Plutôt que réentraîner ou fine-tuner l'intégralité du modèle de 2,2 milliards de paramètres de Liquid AI (ce qui exploderait les ressources de calcul), l'approche LoRA consiste à geler les couches principales du modèle et à injecter de petites matrices de poids entraînables (*rank decomposition matrices*) spécifiquement sur :

* Les **connecteurs audio** (qui font la passerelle entre les tokens du codec Mimi et l'espace latent du modèle LFM).
* Les têtes d'attention du modèle de langage pour lier les tokens de texte et les tokens audio discrets à 12.5 Hz.

### 2. Architecture du Pipeline LoRA « Mimi + LFM3-Omni »

```text
[ Corpus Audio / Raps / Voix ] 
            │
            ▼ (1. Encodage Stream 24 kHz)
    [ Codec Mimi (Kyutai) ] ──(Flux discret 12.5 Hz / 1.1 kbps)
            │
            ▼ (2. Projection Adaptateur LoRA)
   [ LFM3-Omni-2B Backbone (Gelé) + LoRA Layers (Entraînables) ]
            │
            ▼ (3. Restitution croisée)
  [ Génération Interleaved Text + Audio / Alignement SOUL.md ]

```

1. **Phase d'Ingestion (Mimi en amont) :** Le corpus audio brut (les morceaux de rap et les enregistrements d'identité vocale) est passé dans l'encodeur de Mimi pour le compresser en séquences de tokens discrets à basse fréquence (12.5 Hz). Cela évite de saturer la fenêtre de contexte avec des ondes brutes.
2. **Injection par LoRA :** Les séquences de tokens Mimi sont injectées dans LFM3-Omni-2B via des adaptateurs LoRA ciblés sur les couches de projection audio. Le modèle apprend ainsi à associer la structure rythmique et le timbre de ces tokens audio aux concepts sémantiques décrits dans le `SOUL.md`.
3. **Optimisation Mémoire :** Cette méthode permet de cibler uniquement quelques millions de paramètres d'adaptation, rendant l'entraînement tout à fait réalisable en local ou sur un VPS de calcul modeste sans nécessiter un cluster lourd de GPUs.

---

### 3. Plan d'Action Technique pour le Mono-Repo

* **Étape 1 (Extraction) :** Utiliser la crate Rust ou les liaisons Python (`rustymimi`) du dépôt de Moshi pour extraire les embeddings de tokens Mimi de votre corpus audio de référence.
* **Étape 2 (Configuration LoRA) :** Configurer un script d'entraînement PEFT/LoRA compatible avec l'architecture de LFM3-Omni-2B, en ciblant les modules d'encodage/décodage audio du processeur multimodal.
* **Étape 3 (Ancrage identitaire) :** Associer les lots d'entraînement audio aux métadonnées textuelles correspondantes pour que l'adaptateur LoRA relie les caractéristiques du "flow" vocal aux balises contextuelles du jumeau numérique.
