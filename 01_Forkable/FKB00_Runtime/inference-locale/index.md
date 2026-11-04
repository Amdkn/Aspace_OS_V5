# Inference-Locale — Pile locale, edge-first, souveraine

## Pipeline cible (signal brut → action souveraine)

1. GLiNER2.5-multi-Decide : intention, langue, classification multi-labels. Zéro hallucination.
2. Cactus Needle : mapping déterministe vers tool calls JSON (grammaire contrainte).
3. Exécution système + rétro-alimentation (Airtable/Supabase via orchestration locale).
4. LFM3-Omni-2B + LoRA Mimi : synthèse, style, identité vocale (SOUL.md).
5. Fugu (Sakana) : orchestration des plus gros modèles par-dessus.

## Composants (faits)

- Mimi (Kyutai) : codec 12.5 Hz, 1.1 kbps, streaming 24 kHz.
- LFM3-Omni-2B (Liquid AI) : backbone gelé, adaptateurs LoRA sur connecteurs audio.
- Needle (cactus-compute/needle) : 8–29 Mo quantifié 2-bit, tool calling + Whistle ASR.
- GLiNER2.5-multi-Decide : 287M paramètres, mDeBERTa-v3-base, multilingue.
- LFM3 local V5 : 127.0.0.1:9931 (docs V5). Needle cloné via clone-forkables.ps1.

## Synthèses préservées

- `mimi-lora-lfm3-omni.md` : reconstitué par le Capitaine, perdu par Gemini.
- `needle-gliner-edge.md` : reconstitué par le Capitaine, perdu par Gemini.
