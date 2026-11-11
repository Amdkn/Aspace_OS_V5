# Audit télémétrie — source control natif V5, SC-0 (D-N054, H-M4)

**Portée :** le pas SC-0 (re-pin RigInfinity `86f1139` → `e866578`). Le re-pin est un changement de pointeur seul : **0 ligne de code ajoutée, 0 dépendance ajoutée, 0 appel réseau ajouté par ce pas.**

## Le daemon au pin `e866578`

- **Code natif :** Rust, std-only + `rusqlite` 0.32 (bundled) + `serde_yaml` 0.9 (portages pas 3/4/5). Aucun SDK d'analytics, aucun client HTTP sortant dans le code natif.
- **Lecture locale seule :** la surface de lecture `/api/telemetry/*` du daemon openrig (6 routes sur le SQLite du daemon, faits seulement, aucune identité de compte) est reprise en lecture locale (`usage_series()`) — aucun site sortant.
- **Sites sortants fermés par défaut (audit pas 4) :** Slack clé-gaté, OpenRouter opt-in, pairing opérateur, plugin-vendor tolérant — tous fermés par défaut.
- **Agent-zero (pas 5) :** le fork contient 1 signal (`helpers/update_check.py` → `https://api.agent-zero.ai/a0-update-check`, défaut `True`) — **non porté dans le natif : 0 signal dans le daemon.**

## Verdict SC-0

**0 exporteur, 0 SDK, 0 appel sortant par défaut au pin `e866578`.** Le re-pin n'ajoute rien : la télémétrie du daemon est inchangée par ce pas. Tout déclencheur futur (SC-1+) sera tranché et consigné dans cet audit.
