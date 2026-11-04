---
type: Reference
title: Analyse des traces Fable 5 (Claude Mythos)
description: Patterns d'exécution agentique extraits des datasets HuggingFace fable-traces et intégrés dans CLAUDE.md.
resource: https://huggingface.co/datasets?search=fable-traces
tags: [fable-5, mythos, traces, agentic-coding, claude-code]
generated: { by: agent/antigravity, at: 2026-11-03T14:56:00-05:00 }
status: active
---

# Sources analysées (`huggingface.co/datasets?search=fable-traces`)
- `kelexine/fable-5-sft-traces` (4 665 étapes normalisées, 60 sessions Claude Code Linux/Bash + Windows/PowerShell TeichAI).
- `AlinCiocan/fable-5-claude-code-traces` (18 sessions complètes Claude Code, 9 497 événements JSONL natifs).
- `Crownelius/Complete-FABLE.5-traces-2M` & `Solstice-AI/Complete-FABLE.5-traces-2M` (2 006 487 lignes dédupliquées, 604 lignes "session-limit" purgées).
- `TeichAI/Fable-5-Cursor-Traces` (244 sessions à effort High/xHigh/Max).

# Métriques clés du comportement Fable 5 (`claude-fable-5` / Mythos)
- **Ratio Action / Parole** : **81,4 %** des tours sont des appels d'outils purs (`task_type: agentic`, `output_type: tool_use`) contre **18,6 %** de tours texte (`reasoning`).
- **Densité CoT vs Laconisme externe** : réflexion interne (`thinking`) longue et chirurgicale (médiane **2 365 caractères**, moyenne **2 669**, max **9 145**), mais sortie texte visible ultra-courte (souvent **50 à 180 caractères** entre deux vagues d'outils, style télégraphique : *"78/78. Now eyeball the new maps:"*, *"Node 24 is ready. Building now."*).

# 7 Invariants d'exécution Fable 5
1. **Reconnaissance de l'existant avant écriture** : le premier appel d'outil inspecte systématiquement l'environnement, l'arborescence et les binaires disponibles (`Get-ChildItem`, `package.json`, versions) avant d'écrire une seule ligne.
2. **Protection des processus actifs de l'utilisateur** : vérification des ports/PIDs avant tout lancement de serveur ou `kill` (*"Those are the user's own running hub — Don't touch"*).
3. **Éditions chirurgicales vérifiées dans le CoT** : construction exacte de `old_string` / `new_string` avec `replace_all: false` dans la réflexion avant d'appeler `Edit`.
4. **Sorties de commandes filtrées (anti-bruit)** : chaque commande de test ou de diagnostic est pipée vers un filtre (`Select-String`, `grep -E '✘|passed'`, `Select -First`) pour ne jamais saturer la fenêtre de contexte (88,3 % des sessions longues subissent une troncature amont si le bruit n'est pas filtré).
5. **Boucle d'auto-guérison (Self-Healing)** : en cas d'échec de test ou d'outil, enchaînement immédiat diagnostic → patch → re-test dans le même flux sans rendre la main à l'utilisateur.
6. **Vérification de bout en bout (End-to-End & Visuelle)** : un fichier écrit n'est jamais considéré comme terminé sans exécution réelle, vérification des ports/logs ou capture d'écran (`herdr-app shot`, headless check).
7. **Zéro pollution "session-limit" / méta-excuses** : aucun message d'excuse ou de bavardage méta dans les traces propres.
