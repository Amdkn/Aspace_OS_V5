---
okf_version: "0.2"
type: Decision
title: "ADR-09 — Confinement des Licences Restrictives & Règle Clean-Room (`D12`)"
enonce_ref: "00_Memoire/bundle/fusion/FUSION-ENONCE.md"
enonce_sha256: "41889edb9c468ea62ee4641328c0e6f4bac2c618b81da751eebd2af4c05f648d"
---

# ADR-09 — Confinement des Licences Restrictives & Règle Clean-Room (`D12`)
- **Statut** : `ACCEPTÉE`
- **Conflit** : Le corpus mélange Apache-2.0/MIT avec `AGPL-3.0` (`MiroFish`), `CC BY-NC 4.0` (`PathFM`), `Apache-2.0 modifiée` (`dify`), et des dépôts **sans licence** (`claude-code`, `openai-plugins`, `autoresearch`).
- **Décision** :
  1. **`AGPL-3.0` (`MiroFish`)** : strict confinement en microservice réseau isolé ; zéro linkage ou inclusion de source dans les binaires Apache-2.0/MIT.
  2. **`CC BY-NC 4.0` (`PathFM`, profil interne `TabFM`/`TimesFM`)** : confinement strict au profil `a0_internal_wargame` ; le profil `b2b_commercial` charge exclusivement la pile Apache-2.0 (`Mitra-v2` + `Chronos-2`), appliqué mécaniquement par `assert_commercial_safe()`.
  3. **Sans licence (`claude-code`, `openai-plugins`, `autoresearch`)** : application stricte de la règle **D12 Clean-Room** — aucune copie de fichier source ; utilisation uniquement comme référence externe (`openai-plugins` -> `RETENU`) ou exécutable CLI externe piloté par contrat (`claude-code` -> `RETENU`).
- **Invariant** : Tout binaire central `L0` (`fondation-13-1`, `RigInfinity`, `aspace-fiber-host`) reste sous licence permissive propre Apache-2.0/MIT sans contamination virale ni violation NC.
- **Modules résolus** : `MiroFish`, `PathFM`, `autogluon`, `chronos-forecasting`, `mitra-2`, `tabfm`, `timesfm`, `dify`, `claude-code`, `openai-plugins`, `rea`.
