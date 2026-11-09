# Audit télémétrie — dream-rsi (D-N048 V3a)

**Fork :** `Amdkn/dream-rsi`, gel `8ec35bd`. **Télémétrie zéro par contrat.**

## 1. Scan statique

- Occurrences de `posthog | segment | sentry | amplitude | mixpanel | telemetry | analytics` dans le paquet `dream_rsi/` + `pyproject.toml` : **0**.
- Appels réseau dans le paquet : **0** — sauf les évaluateurs KernelBench (voir §2).
- Dépendances déclarées : **aucune** (`dependencies = []`) ; extras optionnels `tasks` (`numpy`, `scipy`, `psutil`, `scikit-learn`), `kernel` (`requests`, `pyyaml`), `claude` (`claude-agent-sdk`), `dev` (`pytest`).

## 2. Dépendances et réseau confiné

- Réseau dans le dépôt, **hors de la surface exposée** : `tasks/kernelbench/*/evaluator.py:134` — `requests.post(url, json=..., timeout=...)` vers un serveur GPU explicite, uniquement quand une tâche KernelBench tourne (jamais invoqué par l'adapter).
- La section `learning` exposée (replay, export, allocate, discover, directions) : **zéro import réseau**.

## 3. Preuve d'exécution

Suite `pytest tests/ -q` : 96 passés, 10 skipped, 1 deselected (hors-ligne, `-m 'not integration'`). Smoke test adapter : 5/5 (`--help` + import, hors-ligne). **Zéro appel sortant.**

## Conclusion

**Télémétrie zéro.** Aucun SDK ; le seul réseau du dépôt est confiné aux évaluateurs KernelBench, jamais invoqués par l'adapter.
