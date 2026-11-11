# RUNBOOK — Procédure Opérationnelle Standard (G1-BURNHAM)

1. Lire l'état dans `00_Memoire/egm_missions.db` et `00_Memoire/shared_brain/memory.jsonl`.
2. Compiler une mission Poisson Rouge (`Goldfish Worker`, contexte < 4 Ko).
3. Exécuter dans un worktree isolé ou via `jules.google.com` / `codex-chatgpt-web`.
4. Vérifier le read-back natif GWS et passer `02_Factory/checks.ps1`.
