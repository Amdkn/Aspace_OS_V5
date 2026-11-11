---
name: hooks-create
description: Convert workflow/event rules from AGENTS.md or CLAUDE.md into deterministic cross-harness hooks (exit 0 / exit 2) following Cole Medin's File Coupling & Stop Gate pattern.
---

# `hooks-create` — Usine à Hooks Déterministes (`exit 0` / `exit 2`)

## 1. Loi de Triage : Jugement (`AGENTS.md`) vs Événement (`02_Factory/hooks/`)

Avant d'ajouter une consigne dans `AGENTS.md`, `CLAUDE.md` ou `GEMINI.md`, applique cet arbre de décision :

1. **Est-ce une convention de jugement ou d'architecture ?**
   - *Exemples* : « Stocker les montants en centimes entiers », « Respecter la loi des 578 Holons », « Répondre en français télégraphique ».
   - $\rightarrow$ **Conserver dans `AGENTS.md` / `GEMINI.md`**.
2. **Est-ce un événement déclencheur ou une vérification déterministe ?**
   - *Exemples* : « Avant d'éditer un fichier dans `00_A0_Core/`, lire `01_Forkable/FKB00_Runtime/index.md` », « Bloquer la lecture de `.env` », « À la fin du tour, lancer `02_Factory/checks.ps1` et stopper les Codespaces inactifs ».
   - $\rightarrow$ **Coder dans [`02_Factory/hooks/aspace_deterministic_hooks.py`](file:///c:/Users/amado/Aspace%20OS%20V5/02_Factory/hooks/aspace_deterministic_hooks.py) avec `exit 2` sur violation**.

## 2. Protocole Standard des Codes de Sortie

| Code de sortie | Effet sur le Harness (Claude Code, Codex, Pi, OpenCode, Agy) |
|---|---|
| **`exit 0`** | L'action est autorisée (ou le Stop Hook est validé). |
| **`exit 2`** | L'action est **bloquée déterministement**. Le texte écrit sur `stderr` est renvoyé directement au modèle pour qu'il corrige sa trajectoire dans le même tour. |

## 3. Les 3 Familles de Hooks Déployées dans A'Space OS V5

1. **File Coupling (`PreToolUse` — `COUPLED_FILES_MAP`)** :
   - Enregistre chaque fichier lu durant la session dans `00_Memoire/.session_read_files.json`.
   - Si un agent tente d'éditer un fichier critique sans avoir lu son contrat couplé (`index.md`, `README.md`, `registry-578-holons.json`), retourne `exit 2` en indiquant exactement quel fichier lire d'abord.
2. **Secret & Destructive Guard (`PreToolUse`)** :
   - Bloque (`exit 2`) toute lecture directe de `.env`, `.pem`, `id_rsa` et tout `rm -rf` sur les piliers racines (`00_Memoire`, `01_Forkable`, `02_Factory`).
3. **Stop Gate & Atomic Quota Teardown (`Stop`)** :
   - Exécute `pwsh -NoProfile -File 02_Factory/checks.ps1` (`7/7 PASS` exigé, sinon `exit 2` avec trace complète).
   - Exécute `gh codespace stop --all` pour éviter qu'un Codespace oublié ne consomme les 120 core-hours/mois gratuits.

## 4. Commandes de Test Rapide

```powershell
# Tester le Stop Hook (7/7 PASS + Codespace teardown)
python 02_Factory/hooks/aspace_deterministic_hooks.py stop

# Réinitialiser la mémoire de lecture de session
python 02_Factory/hooks/aspace_deterministic_hooks.py reset-session
```
