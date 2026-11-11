# Audit télémétrie — tabfm (D-N053 pas A, H-M4)

**Module :** `tabfm` — fork `Amdkn/tabfm`, gel `fbb6655`, adapter `0a56dff`.
**Verdict : TÉLÉMÉTRIE ZÉRO par contrat.** Aucun SDK de télémétrie, aucun appel réseau en arrière-plan, aucun appel à l'import.

## 1. Scan statique du code amont (au gel)

Motifs cherchés dans `src/` (et `tabfm/` pour tabfm) : `wandb|sentry|posthog|mixpanel|amplitude|segment.com|telemetry` → **0 hit**.
Motifs réseau cherchés : `requests.|httpx.|urllib|urlopen|socket.|http.client|aiohttp|fetch(` → **0 hit hors les sites ci-dessous**.

### Sites réseau explicites (tous déclenchés par l'utilisateur, jamais en arrière-plan)

- `tabfm/src/jax/tabfm_v1_0_0.py:205` : `snapshot_download` — dans `from_pretrained`, declencheur explicite.
- `tabfm/src/pytorch/tabfm_v1_0_0.py:77` : `snapshot_download` — meme declencheur.
- Aucun appel reseau a l'import (verifie en namespace sans interface).

## 2. Dépendances

Dependances (`pyproject.toml`) : absl-py, jaxtyping<0.3, numpy, pandas, scikit-learn, scipy, typeguard<3, huggingface-hub (+ extras jax / pytorch). Aucun SDK de telemetrie declare (grep : 0 hit).

## 3. Preuve d'exécution — namespace sans interface

`unshare -n` (aucune interface réseau, DNS en échec) : import du paquet amont + `validate()` + `doctor()` réussissent.
Log : `logs-netns-validate.log`. **0 appel sortant possible dans ce namespace — la preuve est structurelle, pas déclarative.**

## 4. Poids dans le fork

Aucun fichier poids dans le repo (0 fichier *.safetensors / *.bin / *.pt / *.pth).

## 5. Déclencheurs tranchés

| Déclencheur | Décision |
|---|---|
| Téléchargement de poids (`from_pretrained`, `snapshot_download`, `hf_hub_download`) | Explicite, à l'initiative de l'utilisateur, jamais automatique — **conservé tel quel** (c'est le comportement amont, pas une télémétrie) |
| SDK de télémétrie | Aucun — **rien à retirer** |
| Appel réseau à l'import | Aucun (prouvé en netns) — **rien à retirer** |
| Poids montés dans le fork | Aucun (sauf fixtures de test factices chronos, < 200 Ko) — **conforme** (les miroirs HF sont le travail R1) |

## 6. Ré-audit

À chaque changement de commit gelé ou d'adapter, et au minimum à chaque transition d'état.
