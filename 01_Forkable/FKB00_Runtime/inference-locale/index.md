# Inference-Locale — Pile locale, edge-first, souveraine

## Tableau de Bord Souverain (GitHub Amdkn & Hugging Face Amdkn7)

| Composant | Rôle dans A'Space OS V5 | Code Moteur (GitHub Souverain) | Modèle & Poids (Hugging Face Souverain) |
|---|---|---|---|
| **Cactus Needle** | Tool-calling déterministe 2-bit & ASR Whistle | [Amdkn/needle](https://github.com/Amdkn/needle) | [Amdkn7/needle3](https://huggingface.co/Amdkn7/needle3) |
| **Kyutai Moshi / Mimi** | Dialogue vocal & Codec audio streaming 24 kHz | [Amdkn/moshi](https://github.com/Amdkn/moshi) | [Amdkn7/mimi](https://huggingface.co/Amdkn7/mimi) |
| **Fastino GLiNER 2.5** | Classification multi-labels & intention zéro-hallucination | [Amdkn/GLiNER2.5-multi-Decide](https://github.com/Amdkn/GLiNER2.5-multi-Decide) | [Amdkn7/GLiNER2.5-multi-Decide](https://huggingface.co/Amdkn7/GLiNER2.5-multi-Decide) |
| **Liquid AI LFM3-Omni-2B** | Backbone neuronal local (port 127.0.0.1:9931) | [Amdkn/LFM3-Omni-2B](https://github.com/Amdkn/LFM3-Omni-2B) | [Amdkn7/LFM3-Omni-2B](https://huggingface.co/Amdkn7/LFM3-Omni-2B) |
| **Microsoft LoRA** | Adaptateurs d'adaptation bas-rang (loralib) | [Amdkn/LoRA](https://github.com/Amdkn/LoRA) | — |

---

## Pipeline cible (signal brut → action souveraine)

1. **GLiNER 2.5 Multi-Decide** : intention, langue, classification multi-labels. Zéro hallucination.
2. **Cactus Needle** : mapping déterministe vers tool calls JSON (grammaire contrainte).
3. **Exécution système + rétro-alimentation** : orchestration locale (Factory / Holons).
4. **LFM3-Omni-2B + LoRA Mimi** : synthèse, style, identité vocale (SOUL.md).
5. **Sakana Fugu Conductor** : orchestration des plus gros modèles par-dessus.

---

## Synthèses Préservées

- `mimi-lora-lfm3-omni.md` : architecture Mimi + LoRA + LFM3-Omni.
- `needle-gliner-edge.md` : couplage Edge Needle + GLiNER.
