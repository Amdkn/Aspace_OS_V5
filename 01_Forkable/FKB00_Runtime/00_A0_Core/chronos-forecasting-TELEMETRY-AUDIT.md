# Audit télémétrie — chronos-forecasting (D-N053 pas A, H-M4)

**Module :** `chronos-forecasting` — fork `Amdkn/chronos-forecasting`, gel `1224faf`, adapter `c749362`.
**Verdict : TÉLÉMÉTRIE ZÉRO par contrat.** Aucun SDK de télémétrie, aucun appel réseau en arrière-plan, aucun appel à l'import.

## 1. Scan statique du code amont (au gel)

Motifs cherchés dans `src/` (et `tabfm/` pour tabfm) : `wandb|sentry|posthog|mixpanel|amplitude|segment.com|telemetry` → **0 hit**.
Motifs réseau cherchés : `requests.|httpx.|urllib|urlopen|socket.|http.client|aiohttp|fetch(` → **0 hit hors les sites ci-dessous**.

### Sites réseau explicites (tous déclenchés par l'utilisateur, jamais en arrière-plan)

- `src/chronos/boto_utils.py:48` : `requests.get(url, stream=True)` — telechargement d'un modele depuis CloudFront, dans `download_model_files_from_cloudfront()`, appele uniquement par `from_pretrained` quand le fichier local est absent (jamais a l'import, jamais en arriere-plan).
- `src/chronos/boto_utils.py:62-65` : `boto3` (import differe, dans la fonction) — telechargement S3, meme declencheur explicite.
- Aucun autre site reseau dans `src/` (grep `requests.|httpx.|urllib|urlopen|socket.|http.client|aiohttp|fetch(` : 0 autre hit).

## 2. Dépendances

Dependances (`pyproject.toml`) : torch, transformers, accelerate, numpy, einops, pandas (+ extras boto3, peft, fev). Aucun SDK de telemetrie declare (grep wandb|sentry|posthog|mixpanel|amplitude|telemetry : 0 hit).

## 3. Preuve d'exécution — namespace sans interface

`unshare -n` (aucune interface réseau, DNS en échec) : import du paquet amont + `validate()` + `doctor()` réussissent.
Log : `logs-netns-validate.log`. **0 appel sortant possible dans ce namespace — la preuve est structurelle, pas déclarative.**

## 4. Poids dans le fork

4 fichiers poids dans le repo, tous des fixtures de test factices (< 200 Ko) : `test/dummy-chronos-model/model.safetensors` (112 Ko), `test/dummy-chronos-bolt-model/model.safetensors` (84 Ko), `test/dummy-chronos2-model/model.safetensors` (36 Ko), `test/dummy-chronos2-lora/adapter_model.safetensors` (28 Ko). Aucun vrai poids. Attention : `test_chronos2.py` écrit des checkpoints fine-tunés sous `chronos-2-finetuned/` (gitignored, .gitignore:165) pendant les suites — 66 dossiers / 3,0 Mo pendant mes runs, nettoyés après (`rm -rf chronos-2-finetuned`) ; `doctor()` les signale comme poids inattendus si on le lance sur un arbre sali par une suite (comportement voulu : lancer doctor/smoke sur arbre propre).

## 5. Déclencheurs tranchés

| Déclencheur | Décision |
|---|---|
| Téléchargement de poids (`from_pretrained`, `snapshot_download`, `hf_hub_download`) | Explicite, à l'initiative de l'utilisateur, jamais automatique — **conservé tel quel** (c'est le comportement amont, pas une télémétrie) |
| SDK de télémétrie | Aucun — **rien à retirer** |
| Appel réseau à l'import | Aucun (prouvé en netns) — **rien à retirer** |
| Poids montés dans le fork | Aucun (sauf fixtures de test factices chronos, < 200 Ko) — **conforme** (les miroirs HF sont le travail R1) |

## 6. Ré-audit

À chaque changement de commit gelé ou d'adapter, et au minimum à chaque transition d'état.
