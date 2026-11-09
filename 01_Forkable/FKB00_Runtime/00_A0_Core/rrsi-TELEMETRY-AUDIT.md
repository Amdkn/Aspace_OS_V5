# Audit télémétrie — rrsi (D-N048 V3a)

**Fork :** `Amdkn/rrsi`, gel `be50316`. **Télémétrie zéro par contrat.**

## 1. Scan statique

- Occurrences de `posthog | segment | sentry | amplitude | mixpanel | telemetry | analytics | track(` dans le dépôt : 5 fichiers — **tous des faux positifs** :
  - `rrsi/propose.py:79` — « READ-ONLY rendered trajectory segment » (segment de trajectoire).
  - `domains/coding/briefs.py:79` — « when extracting an ELF, segments are at… » (segments ELF).
  - `domains/workspace/mcp_gateway/gateway.py:273` — `sup.segment.text` (segment de supervision).
  - `third_party/archipelago/harness_eng/main.py`, `harness_workspace/main.py` — segments, runners tiers.
- **Aucun SDK télémétrie** déclaré dans `pyproject.toml` (dépendances : `anthropic[vertex]` ; extras `agentic`, `coding`, `dev` — aucun SDK télémétrie).

## 2. Dépendances et réseau confiné

- Réseau dans le dépôt, **hors du cœur exposé** :
  - `domains/eng/adapter.py:68` — `socket.socket()` + `connect_ex(("127.0.0.1", port))` : vérification locale qu'une passerelle tourne (localhost seul, domaine `eng` — jamais invoqué par l'adapter).
  - `third_party/archipelago/runner/utils/` — `httpx` (runners de benchmark tiers — jamais invoqués par l'adapter).
- Le cœur exposé (`rrsi/schedule.py`, `config.py`, `selection.py`, `history.py`, `calibrate.py`, `components.py`, `evaluate.py`) : **zéro import réseau**.

## 3. Preuve d'exécution

Suite `test_core.py` : 8/8 — « no API, no benchmark ». Smoke test adapter : 5/5 (cœur pur + `--help`, hors-ligne). **Zéro appel sortant.**

## Conclusion

**Télémétrie zéro.** Aucun SDK ; le seul réseau du dépôt est confiné aux domaines de benchmark, jamais invoqués par l'adapter.
