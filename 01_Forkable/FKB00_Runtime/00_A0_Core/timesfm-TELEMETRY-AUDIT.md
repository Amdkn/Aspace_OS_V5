# Audit télémétrie — timesfm (D-N053 pas A, H-M4)

**Module :** `timesfm` — fork `Amdkn/timesfm`, gel `e51928e`, adapter `7cb4f64`.
**Verdict : TÉLÉMÉTRIE ZÉRO par contrat.** Aucun SDK de télémétrie, aucun appel réseau en arrière-plan, aucun appel à l'import.

## 1. Scan statique du code amont (au gel)

Motifs cherchés dans `src/` (et `tabfm/` pour tabfm) : `wandb|sentry|posthog|mixpanel|amplitude|segment.com|telemetry` → **0 hit**.
Motifs réseau cherchés : `requests.|httpx.|urllib|urlopen|socket.|http.client|aiohttp|fetch(` → **0 hit hors les sites ci-dessous**.

### Sites réseau explicites (tous déclenchés par l'utilisateur, jamais en arrière-plan)

- `src/timesfm/timesfm_2p5/timesfm_2p5_torch.py:324,346` : `hf_hub_download` — dans `from_pretrained` / chargement de checkpoint, declencheur explicite de l'utilisateur.
- `src/timesfm/timesfm_2p5/timesfm_2p5_flax.py:491` : `snapshot_download` — meme declencheur.
- `src/timesfm/timesfm3/mlx/model.py:386-387` : `hf_hub_download` (config + poids) — backend MLX, meme declencheur.
- Aucun appel reseau a l'import (verifie en namespace sans interface : `validate()` + import reussissent sans reseau).

## 2. Dépendances

Dependances (`pyproject.toml`) : numpy, huggingface-hub, safetensors (+ extras torch / flax / mlx). Aucun SDK de telemetrie declare (grep : 0 hit). `huggingface-hub` est une bibliotheque de telechargement, pas de telemetrie.

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
