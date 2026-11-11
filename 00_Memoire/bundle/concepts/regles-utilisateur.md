---
type: Playbook
title: Règles de collaboration avec l'utilisateur
description: Échecs passés de Claude Code dans V5/Herdr et règles qui en découlent.
tags: [regles, echecs, comportement]
generated: { by: agent/claude-code, at: 2026-11-03T13:35:00-05:00 }
status: active
---

# Échecs récurrents
- Poser des questions au lieu d'agir quand l'action est claire.
- Reformuler / dénaturer la demande ; ajouter des actions non demandées (ouvrir des tabs, subagents).
- Envoyer à un agent Herdr sans consigne de retour → orchestration morte.
- Mode de permission « manual » au lieu de bypass ; demander des flags à la main.
- Compte de nettoyage faux (créés vs fermés).

# Règles
Voir `CLAUDE.md` à la racine : littéralité, pas de questions inutiles, rien de créé hors demande, résultat plutôt qu'analyse, vérifier avant de dire « fait ».
