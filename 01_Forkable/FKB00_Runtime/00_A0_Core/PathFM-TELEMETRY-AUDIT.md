# Audit télémétrie — PathFM (D-N053 pas A, H-M4)

**Module :** `PathFM` — fork `Amdkn/PathFM`, gel `8a3a42c`, adapter `8bcdd5b`.
**Verdict : TÉLÉMÉTRIE ZÉRO par contrat.** Aucun SDK de télémétrie, aucun appel réseau en arrière-plan, aucun appel à l'import.

## 1. Scan statique du code amont (au gel)

Motifs cherchés dans `src/` (et `tabfm/` pour tabfm) : `wandb|sentry|posthog|mixpanel|amplitude|segment.com|telemetry` → **0 hit**.
Motifs réseau cherchés : `requests.|httpx.|urllib|urlopen|socket.|http.client|aiohttp|fetch(` → **0 hit hors les sites ci-dessous**.

### Sites réseau explicites (tous déclenchés par l'utilisateur, jamais en arrière-plan)

- `src/pathfm/loading.py:55,58` : `hf_hub_download` (config + poids) — dans `from_pretrained`, declencheur explicite.
- `src/pathfm/benchmarks/download.py:23` : `snapshot_download` — telechargement de benchmark, explicite.
- `src/pathfm/benchmarks/panda_data.py:40` : `hf_hub_download` — donnees benchmark, explicite.
- Aucun appel reseau a l'import (verifie en namespace sans interface).

## 2. Dépendances

Dependances (`pyproject.toml`) : torch==2.9.1, chronos-forecasting==2.3.1, transformers==5.13.0, huggingface-hub, safetensors, numpy==1.26.4, pandas==2.3.3, einops. Aucun SDK de telemetrie declare (grep : 0 hit).

## 3. Preuve d'exécution — namespace sans interface

`unshare -n` (aucune interface réseau, DNS en échec) : import du paquet amont + `validate()` + `doctor()` réussissent.
Log : `logs-netns-validate.log`. **0 appel sortant possible dans ce namespace — la preuve est structurelle, pas déclarative.**

## 4. Poids dans le fork

Aucun fichier poids dans le repo (0 fichier *.safetensors / *.bin / *.pt / *.pth). Les poids PathFM-Chaotic-75M sont montes par R1 (D-N052), jamais dans le fork.

## 5. Déclencheurs tranchés

| Déclencheur | Décision |
|---|---|
| Téléchargement de poids (`from_pretrained`, `snapshot_download`, `hf_hub_download`) | Explicite, à l'initiative de l'utilisateur, jamais automatique — **conservé tel quel** (c'est le comportement amont, pas une télémétrie) |
| SDK de télémétrie | Aucun — **rien à retirer** |
| Appel réseau à l'import | Aucun (prouvé en netns) — **rien à retirer** |
| Poids montés dans le fork | Aucun (sauf fixtures de test factices chronos, < 200 Ko) — **conforme** (les miroirs HF sont le travail R1) |

## 6. Ré-audit

À chaque changement de commit gelé ou d'adapter, et au minimum à chaque transition d'état.
