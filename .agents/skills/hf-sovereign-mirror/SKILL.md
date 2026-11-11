---
name: hf-sovereign-mirror
description: Duplique tout modèle ou dataset Hugging Face sur le compte souverain de l'opérateur (sans télécharger les poids dans Git), génère sa fiche d'architecture .md sur le modèle LFM3/GLiNER/Mimi, et met à jour l'index central HF-SOVEREIGN-INDEX.md dans A'Space OS V5.
version: 1.0.0
platforms: [macos, linux, windows]
metadata:
  hermes:
    tags: [huggingface, models, mirror, safetensors, lazy-loading, tabular, timeseries, autogluon, google]
    category: inference
---

# Skill : Souveraineté & Indexation Légère des Modèles Hugging Face (V5)

## 1. Invariants de Sobriété (Règles d'Acier)
1. **Zéro binaire dans Git** : Ne jamais commiter de fichiers `.safetensors`, `.bin`, `.gguf`, `.pt` ou `.onnx` dans `Amdkn/Aspace_OS_V5`.
2. **Double Référencement (`Sovereign` + `Upstream`)** : Chaque modèle doit être dupliqué sur le namespace Hugging Face souverain (`$env:HF_NAMESPACE`, ex: `Amdkn`) et référencé par un fichier `.md` léger dans son pôle `01_Forkable/FKB*` respectif.
3. **Montage par Couche Fractale (`4L` à `20L`)** : Les poids restent sur le Hub HF (ou dans `~/.cache/huggingface/hub/`) et ne sont hydratés localement que lorsque la couche fractale correspondante est activée.

---

## 2. Procédure de Duplication Server-Side (0 Bande Passante Locale)

Lorsqu'un nouveau modèle Hugging Face (`<org>/<model_name>`) doit être intégré à A'Space OS V5 :

1. Exécuter la duplication côté serveur via `huggingface_hub` :
   ```python
   from huggingface_hub import HfApi
   import os

   api = HfApi(token=os.environ.get("HF_TOKEN"))
   sovereign_ns = os.environ.get("HF_NAMESPACE", "Amdkn")
   source_repo = "autogluon/mitra-classifier-2"
   target_repo = f"{sovereign_ns}/{source_repo.split('/')[-1]}"

   # Copie server-side instantanée sur Hugging Face
   api.duplicate_repo(from_id=source_repo, to_id=target_repo, private=False, exist_ok=True)
   ```

2. Générer la fiche `.md` du modèle dans le sous-dossier approprié en respectant le gabarit ci-dessous.
3. Ajouter l'entrée dans `01_Forkable/HF-SOVEREIGN-INDEX.md`.
4. Valider l'intégrité via `pwsh -NoProfile -ExecutionPolicy Bypass -File "02_Factory/checks.ps1"`.

---

## 3. Gabarit Standard de Fiche Modèle `.md` (Style LFM3 / GLiNER / Mimi)

Chaque modèle référencé dans `01_Forkable/` possède un fichier `<nom-modele>.md` structuré ainsi :

```yaml
---
entity_type: hf_model_pointer
model_id_sovereign: "Amdkn/<model_name>"
model_id_upstream: "<upstream_org>/<model_name>"
fractal_layer: "4L | 16L | 20L"
license: "Apache-2.0 | Non-Commercial"
ram_footprint_mb: 300
holon_parent: "FKB00_Runtime | FKB01_Inference | FKB02_Memory"
status: "ACTIVE_POINTER"
---
```

Suivi de :
- **Rôle dans A'Space OS V5**
- **Chemins des Poids & Variantes**
- **Contrat d'Appel Déterministe (Python / CLI)**
