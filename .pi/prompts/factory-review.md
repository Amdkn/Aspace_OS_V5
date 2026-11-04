Exécute l'audit **Review Swarm Aspace Software Factory** (Code, Security, UX/UI, Spec/Memory Drift) :
1. Lance `pwsh -NoProfile -File factory/checks.ps1`.
2. Vérifie l'absence de secrets, le respect de `00_Memoire/bundle/` (OKF v0.2 + append-only `log.md`) et la conformité au Mandate.
3. Donne un verdict `APPROVE` ou `REQUEST_CHANGES`.

Cible : {{target}}
