# Audit télémétrie — wikiskill (D-N048 V3a)

**Fork :** `Amdkn/wikiskill`, gel `cdc291c`. **Télémétrie zéro par contrat.**

## 1. Scan statique

- Occurrences de `posthog | segment | sentry | amplitude | mixpanel | telemetry | analytics` dans le paquet `wikiskill/` + `pyproject.toml` + `setup.py` : **0**.
- Appels réseau (`requests. | httpx. | urllib | urlopen | socket.`) dans le paquet : **0**.
- Dépendances déclarées : **aucune** (`dependencies = []`).

## 2. Dépendances

Aucune dépendance runtime. La suite de tests n'exige que `pytest` (venv dédié, hors paquet).

## 3. Preuve d'exécution

`wikiskill init demo --ws <scratch>` + `wikiskill status demo --ws <scratch>` (smoke test, 4/4) : génération locale du bench depuis une graine, lecture de l'état local. **Zéro appel sortant** — aucun code réseau dans le paquet, aucun hôte contacté.

## Conclusion

**Télémétrie zéro.** L'adapter n'expose que `init` / `status` hors-ligne ; `evolve` (backend agent) n'est jamais invoqué.
