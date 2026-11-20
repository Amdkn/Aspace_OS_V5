---
okf_version: "0.2"
type: Decision
title: "ADR-15 — Amendement ADR-14 : Retour aux Trois Noyaux (ÂME / SYSTÈME NERVEUX / CORPS), Retrait de MÉTABOLISME & Contrat Anti-Sabotage"
enonce_ref: "00_Memoire/bundle/fusion/FUSION-ENONCE.md"
enonce_sha256: "41889edb9c468ea62ee4641328c0e6f4bac2c618b81da751eebd2af4c05f648d"
amends: "ADR-14"
---

# ADR-15 — Trois Noyaux Fondamentaux (`ÂME / SYSTÈME NERVEUX / CORPS`), Retrait de `MÉTABOLISME` & Preuve Différentielle Anti-Sabotage

- **Statut** : `ACCEPTÉE` (Décision non négociable de l'architecte et du juge au Cycle 6 ; amende `ADR-14`)
- **Portée** : Suppression du 4e noyau `MÉTABOLISME`, suppression du plafond artificiel `≤ 1/3` par noyau, réduction de `CORPS` par fusion réelle de modules (`M084 video-director`) et exigence de détection de sabotage sur chaque fonction et champ déclaré.

---

## 1. Conflit Identifié au Cycle 5

1. L'application d'un plafond mécanique de taille (`≤ 1/3 = 40` modules) a conduit à promouvoir `MÉTABOLISME` au rang de 4e noyau racine au lieu de conserver l'architecture doctrinale à **3 Noyaux** (`ÂME / SYSTÈME NERVEUX / CORPS`) et de réduire le `CORPS` par fusion réelle des modules `K5`.
2. Le test de sabotage du Juge externe Cycle 5 a mis en évidence 3 lacunes de couverture différentielle :
   - **`M044` (`context-language-models`)** : l'altération de `clm_rendered_text` et de plusieurs helpers n'était pas couverte sur toute la surface d'origine ni sur les cas limites ; présence de fonctions synthétiques non couvertes (`build_clm_anchored_context`).
   - **`M050` (`knowledge-catalog`)** : l'inversion complète de `okf_is_stale` passait inaperçue faute d'entrées expirées/frontières explicites dans le vecteur différentiel ; présence de `validate_okf_bundle` hors surface amont.
   - **`M118` (`04_Inference_Youtube_Discovery_Registry`)** : la comparaison différentielle ne vérifiait que les clés sélectionnées et tolérait les clés en trop ou les normalisations destructives ; il en allait de même pour `M117` (`thresholds` synthétique absent des fichiers `SKILL.md` bruts).

## 2. Décisions (Cycle 6)

1. **Trois Noyaux Fondamentaux Uniquement (`ÂME`, `SYSTÈME NERVEUX`, `CORPS`)** :
   - **`ÂME` (`Automaton`) — `29` modules** : `Organe K1` (Gouvernance 13→1, RSI, `11` modules) + `Organe K4` (Mémoire Neuro-Symbolique & Compétences, `18` modules).
   - **`SYSTÈME NERVEUX` (`Infinity`) — `29` modules** : `Bus L0 & Fibres` (`7` modules) + `Organe K3` (Inférence System-1/2 & Routage FreeCloud, `15` modules) + `Organe K3-ML` (Cortex Prédictif & Wargame, `7` modules : `MiroFish`, `PathFM`, `autogluon`, `chronos-forecasting`, `mitra-2`, `tabfm`, `timesfm`).
   - **`CORPS` (`OpenRig`) — `62` modules** : `Organe K2` (Exécution Multi-Harness, Bots Incarnés, Anything & Surfaces 3D, `26` modules) + `Organe K5` (**Métabolisme B2B, Studio Vidéo & Finance S0**, `36` modules).
   - **Retrait du plafond `≤ 1/3` sur les noyaux** : seul demeure le plafond constitutionnel §5.5 sur les modules non fusionnés (`(RETENU + ÉCARTÉ) < 1/3` du corpus = `19 / 120 = 15,8 %`). La taille effective du `CORPS` diminue par fusion réelle de ses modules actifs (`M084 video-director` fusionné au Cycle 6 dans `01_Forkable/FKB07_Money_Maker/02_Video/aspace_video_studio_foundation.py`).
2. **Contrat Anti-Sabotage Cycle 6** :
   - Aucun module n'est classé **`FUSIONNÉ`** si :
     1. Des clés en trop sont tolérées ou si une normalisation masque une différence entre l'oracle source amont et l'organe natif ;
     2. Le sabotage (altération, inversion logique, ajout de clé parasite ou troncature) de **n'importe quelle fonction déclarée** ou structure de données du module dans l'organe ne fait pas échouer immédiatement la suite `test_foundation_deletion_suite.py`.
   - Les fonctions synthétiques non portées de la source amont (`build_clm_anchored_context`, `validate_okf_bundle`, `compile_cli_anything_spec`, `execute_cli_structured`) sont retirées des sections correspondantes afin que 100 % de la surface déclarée de `M044`, `M050`, `M056`, `M084`, `M117` et `M118` soit couverte par parité stricte et test de sabotage.
   - `M058 agent-desktop` demeure strictement **`PARTIEL`** tant qu'il n'a pas interagi avec une vraie fenêtre Windows interactive (`desktop_live_verified = False`).

| Noyau Fondamental (`ADR-15`) | Incarnation | Organes Rattachés | Modules | Statut Fusionné |
|---|---|---|---|---|
| **`ÂME`** | `Automaton` | `K1` (11) + `K4` (18) | **29** | `2` différentiels durcis (`M044`, `M050`) ; `M120 llm-wiki` rétrogradé `PARTIEL` (audit fix Cycle 6) |
| **`SYSTÈME NERVEUX`** | `Infinity` | Bus L0 (7) + `K3` (15) + `K3-ML` (7) | **29** | `3` F8 (`infinity`, etc. · total `9` F8 Rust sur `RigInfinity`) + `M118` |
| **`CORPS`** | `OpenRig` | `K2` (26) + `K5 · Métabolisme` (36) | **62** | `6` F8 + `M056` + `M084` (`video-director`) + `M117` |
| **Total** | — | **Tous les organes** | **120** | **15 `FUSIONNÉ`** (`9` F8 Rust + `6` parité/sabotage stricts, zéro auto-certification) |
