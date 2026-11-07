---
type: Reference
title: Distillation Argon x Fable 5 vers Gemini 3.8 Flash (Zero-Quota-Burn)
description: Synthèse des traces de raisonnement, comportement et décisions de Gemini 4 Argon croisées avec Fable 5 pour maximiser la performance de Gemini 3.8 Flash et éliminer le cramage de quotas.
resource: file:///c:/Users/amado/Aspace%20OS%20V5/GEMINI.md
tags: [argon, gemini-3-8-flash, fable-5, traces, quota, distillation, antigravity]
generated: { by: agent/antigravity, at: 2026-11-07T13:12:00-05:00 }
status: active
---

# Distillation des Traces Argon × Fable 5 → Protocole Gemini 3.8 Flash

## 1. Pourquoi et comment distiller Argon vers Flash 3.8
- **Constats sur les traces Argon** :
  - **Forces** : diagnostic causal de bout en bout en une passe (`UI -> Socket/Store -> Proxy -> Processus/État`), scripts atomiques `node -e` multi-fichiers immunisés contre le CRLF Windows, migrations idempotentes in-process (`Swarm.init()`), et pré-configuration *Anti-Panique Agentique* (`~/.claude.json`, `--dangerously-skip-permissions`, `git -c core.longpaths=true`).
  - **Fuites de quota identifiées et corrigées** :
    1. `WaitMsBeforeAsync: 5000` sous Windows basculait les commandes de 5–7s en tâche de fond (`task-XXXX`), doublant le nombre de tours (`Attente du retour`). **Fix : `WaitMsBeforeAsync: 10000` obligatoire**.
    2. Appels d'outils séquentiels au lieu d'un **Mega-Batch 1-Tour** (`Inspect + Patch node -e + npm run typecheck + Invoke-RestMethod`).
    3. Lancement initial avec `--demo` au lieu du mode réel (`demo: false`).
    4. Auto-attachement récursif de `hc` quand `$env:HC_TERMINAL_ID` est défini (`set "HC_TERMINAL_ID="` ajouté dans `hc.cmd` / `herdr.cmd`).

## 2. Le Template `thinking` 4-Points de Gemini 3.8 Flash
Avant chaque appel d'outil, **Gemini 3.8 Flash** structure son bloc `thinking` en 4 lignes :
1. **`[RACINE]`** : Chaîne causale exacte du bug ou de la fonctionnalité.
2. **`[BATCH 1-TOUR]`** : Regroupement des lectures en parallèle ou d'un script unique `run_command` (`WaitMsBeforeAsync: 10000`) exécutant patch + test.
3. **`[INVARIANTS V5]`** : Symbiose `Automaton × Infinity × OpenRig × Herdr`, Holons du Canon V5, `node -e` anti-CRLF, `log.md` strictement append-only.
4. **`[PREUVE E2E]`** : Vérification réelle (`tsc --noEmit`, `Invoke-RestMethod`, `hc ls`, `02_Factory/checks.ps1`) dans le même tour.
