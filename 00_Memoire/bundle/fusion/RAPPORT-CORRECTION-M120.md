---
okf_version: "0.2"
type: Assessment
title: "RAPPORT-CORRECTION-M120 — Provenance Historique D-N048 V0 & Rétrogradation Honnête M120 llm-wiki"
enonce_ref: "00_Memoire/bundle/fusion/FUSION-ENONCE.md"
enonce_sha256: "41889edb9c468ea62ee4641328c0e6f4bac2c618b81da751eebd2af4c05f648d"
base_commit: "aae156631212f9759b7d8dff1798e7df015c0933"
branch: "fusion/cycle-6-audit-fix"
---

# Rapport de Correction M120 (`llm-wiki`) — Audit Cycle 6

> **Décision appliquée** : Suppression de l'auto-certification `diff_proven.add("llm-wiki")` dans `test_foundation_deletion_suite.py`, consignation et vérification mécanique de la provenance historique **D-N048 V0**, et **rétrogradation explicite de `M120 llm-wiki` de `FUSIONNÉ` à `PARTIEL`**. Les compteurs vérifiés passent de `16 / 85 / 17 / 2` à **`15 FUSIONNÉ` / `86 PARTIEL` / `17 RETENU` / `2 ÉCARTÉ`**.

---

## 1. Provenance Historique Complète (`D-N048 V0` et lignée Git)

Reconstitution vérifiée au dépôt Git et au cache sous-module local `.git/modules/01_Forkable/FKB02_Memory/llm-wiki` :

1. **Introduction initiale (`c507bbf`)** :
   - Ajout de l'entrée `.gitmodules` `01_Forkable/FKB02_Memory/llm-wiki` pointant vers `https://gist.github.com/34a4b4bf6d54b1828ba8c256615619e8.git`, gitlink `160000` épinglé sur `ac46de1ad27f92b28ac95459c782c07f6b8c964a`.
   - Contenu exact du commit `ac46de1` : **1 seul fichier Markdown** (`llm-wiki.md`, 75 lignes, `11 985` octets LF, SHA-256 `dc3efe98ae62f23dd08acad13aba2e95287beb20b6bec2f4af0423557fe37401`), zéro code exécutable.
2. **Mise à jour du pin (`852cc19`)** :
   - Gitlink déplacé vers `537de1cf02b36e409ccbfb899dd72a4279354649` (`feat(aspace-v5): bind llm-wiki as Cordis Fiber (2L) to A0 EGM Core`).
   - Ajout uniquement d'un descripteur JSON `aspace-plugin.json` (`819` octets, SHA-256 `3ba387f292cbb48986f023dfd923102421f6e7dfd4e5842e8311be65e70de4c2`, propriétaire `S3-GRAHAM`) ; `llm-wiki.md` inchangé (`11 985` octets LF, même SHA-256).
3. **Rapatriement `D-N048 V0` (`2026-11-09`)** :
   - **Commit `26ca7cb7c623fb42c56bffe77d49e9a74473bcf2`** (*« D-N048 V0 — Ordre : gist rapatrié, renommage, baseline, table de gel, registre étendu »*, PR #6 mergée `d515872`, consignée en journal append-only `00_Memoire/bundle/log.md` au commit `86264246963bad237107ca8176c277e7a7f89c42`).
   - Action exécutée : retrait de l'entrée `.gitmodules` et du gitlink `160000` `01_Forkable/FKB02_Memory/llm-wiki`, création de `00_Memoire/bundle/concepts/llm-wiki.md` (91 lignes, frontmatter OKF + 75 lignes de corps) et inscription dans `01_Forkable/FORKS-AMONT-21-FREEZE.md` (§D3) et `01_Forkable/FUSIONS-REGISTRY.md` (ligne 140 : **`rapatrié`**, *« pas un module »*, *« Harnais H-W0 : 5/5 PASS. Zéro code, aucun fork (gate H-W0) »*).
   - **Intégrité vérifiée par octets** : dans `00_Memoire/bundle/concepts/llm-wiki.md`, le corps après frontmatter mesure `11 986` octets LF (car `1` ligne vide `\n` sépare `---` du titre `# LLM Wiki`, fait consigné dans `log.md` au commit `8626424`) ; après `.lstrip(b"\n")`, les `11 985` octets exacts produisent exactement le SHA-256 `dc3efe98ae62f23dd08acad13aba2e95287beb20b6bec2f4af0423557fe37401` identique au gist `ac46de1` / `537de1c`.
4. **Incident & restauration (`feb338e` → `19d2378` / `567595a`)** :
   - Suppression temporaire de `00_Memoire/bundle/concepts/llm-wiki.md` au commit `feb338e`, immédiatement restaurée au contenu identique (`91` lignes) en `19d2378` puis `567595a`.

---

## 2. Verdict Stricte Sous `FUSION-ENONCE.md` §(2)–(5) & `ADR-15`

Le rapatriement historique `D-N048 V0` est **authentique et prouvé au SHA-256**, mais **`M120 llm-wiki` ne satisfait pas les critères de `FUSIONNÉ`** et est donc rétrogradé à **`PARTIEL`** :

1. **`FUSION-ENONCE.md` §(5)** : *« adapter un module (états 0 à 3), le renommer, le déplacer ou le résumer n'est pas le fusionner et ne compte pas. »* Rapatrier un gist Markdown en document `concepts/llm-wiki.md` avec explicitement *« Zéro code »* et *« fichier de concept, pas un module »* prouve un déplacement documentaire, pas une fusion exécutable.
2. **Absence de code `M120` dans l'Organe `K4`** : `01_Forkable/FKB00_Runtime/00_A0_Core/aspace_fkb02_memory_organ.py` (ligne 6) exclut explicitement `M120` en supposant `M120 llm-wiki déjà fusionné` ; aucune fonction exécutable ni test différentiel/anti-sabotage ni reçu `R10` ne couvre `M120`.
3. **Invariants WikiLLM partiels dans V5** :
   - `00_Memoire/bundle/concepts/llm-wiki.md` n'est pas indexé dans `00_Memoire/bundle/index.md` (page orpheline vis-à-vis de l'opération `Query`/`Lint`).
   - `00_Memoire/AGENTS.md` (lignes 10, 20, 42, 54) et `00_Memoire/bundle/concepts/outils-memoire.md` (ligne 14) pointent encore vers `00_Memoire/wikillm/llm-wiki.md`, chemin inexistant dans l'arbre Git V5.
   - L'immutabilité de `00_Memoire/raw/` n'est pas vérifiée mécaniquement par `02_Factory/checks.ps1` ni par `aspace_fkb02_memory_organ.py`.
   - Le descripteur `aspace-plugin.json` présent dans le pin `537de1c` n'existe que dans le cache local `.git/modules/...`, pas dans un clone propre.

---

## 3. Corrections Ciblées & Compteurs Réconciliés

### Modifications appliquées
- **`01_Forkable/FKB00_Runtime/00_A0_Core/test_foundation_deletion_suite.py`** :
  1. Remplacement du test superficiel (`exists() and st_size > 200`) par une vérification stricte de provenance `D-N048 V0` (YAML frontmatter OKF, taille exacte `11 985` octets après `.lstrip(b"\n")`, SHA-256 `dc3efe98ae62f23dd08acad13aba2e95287beb20b6bec2f4af0423557fe37401`, ancre dans `01_Forkable/FORKS-AMONT-21-FREEZE.md`, et `git cat-file -e 26ca7cb7c623fb42c56bffe77d49e9a74473bcf2^{commit}` hors dépôt shallow).
  2. Suppression de l'auto-certification `diff_proven.add("llm-wiki")` (remplacée par `assert "llm-wiki" not in diff_proven`).
  3. Verrouillage explicite `assert parsed["sabotages_detected"] >= 44` (contre `>= 40` précédemment) préservant l'intégralité des 44 tests de sabotage.
  4. Assertion explicite `assert by_name["llm-wiki"][0] == "**PARTIEL**"` dans `test_carte_and_registre_adr15_and_dynamic_counts`.
  5. Inclusion de `RAPPORT-CORRECTION-M120.md` dans `test_required_spad_artifacts_and_windows_clone_lf`.
- **Registre & SPAD (`LF`)** : mise à jour cohérente de `REGISTRE-DE-FUSION.md`, `CARTE-DES-PRINCIPES.md` (fiche `M120` seule), `PRD-FONDATION.md`, `adr/ADR-15.md` et `00_Memoire/bundle/index.md`.

### Tableau des compteurs vérifiés

| Métrique | Cycle 6 rapporté (`aae1566`) | Cycle 6 corrigé (`fusion/cycle-6-audit-fix`) | Delta |
|---|---|---|---|
| `FUSIONNÉ` vérifié | 16 / 120 | **15 / 120** (`9` F8 Rust + `6` parité/sabotage stricts) | **-1** (`M120` rétrogradé) |
| `PARTIEL` | 85 / 120 | **86 / 120** | **+1** (`M120 llm-wiki`) |
| `RETENU` | 17 / 120 | **17 / 120** | 0 |
| `ÉCARTÉ` | 2 / 120 (+8 FKB06) | **2 / 120** (+8 FKB06) | 0 |
| Garde §5.5 (`RETENU + ÉCARTÉ` < 1/3) | 19 / 120 = 15,8 % | **19 / 120 = 15,8 %** | Conforme |
| Tests anti-sabotage | 44 | **44** (verrouillé `>= 44`) | Préservé |

---

## 4. Respect des Contraintes du Manager

- `FUSION-ENONCE.md` : **Intact** (SHA-256 `41889edb9c468ea62ee4641328c0e6f4bac2c618b81da751eebd2af4c05f648d`).
- `master` & `fusion/cycle-6` : **Intacts** (travail isolé sur la nouvelle branche `fusion/cycle-6-audit-fix`, issue de `aae156631212f9759b7d8dff1798e7df015c0933`).
- Les 3 Noyaux (`ÂME`, `SYSTÈME NERVEUX`, `CORPS`) : **Zéro modification de code** (note : le commentaire docstring hérité en ligne 6 de `aspace_fkb02_memory_organ.py` mentionnant `M120 llm-wiki déjà fusionné` est volontairement conservé en l'état pour ne toucher aucun fichier des 3 noyaux ; son actualisation est reportée en Cycle 7).
- Les 15 autres fusions prouvées (`9` F8 Rust + `M044`, `M050`, `M056`, `M084`/`video-director`, `M117`, `M118`) : **Intactes** et toujours exécutées/vérifiées.
- Cycle 7 : **Non lancé** (attente de clôture de l'audit externe).

---

## 5. Conditions pour Re-promouvoir `M120` en Cycle 7 (après clôture de l'audit)

1. Implémenter dans l'Organe `K4` (`aspace_fkb02_memory_organ.py`) le contrat exécutable **WikiLLM 3 couches** : vérification d'immutabilité de `00_Memoire/raw/`, validation d'opérations `Query` / `Ingest` / `Lint` (détection des pages orphelines dans `index.md` et des chemins morts dans `00_Memoire/AGENTS.md` / `outils-memoire.md`), et contrôle append-only de `log.md`.
2. Indexer `concepts/llm-wiki.md` dans `00_Memoire/bundle/index.md` et corriger les chemins obsolètes `00_Memoire/wikillm/llm-wiki.md`.
3. Ajouter des tests différentiels/d'invariants + sabotage dédiés dans `test_foundation_deletion_suite.py` avec reçu `R10` mesuré en `consign_fkb02_parity_receipt` pour que `M120` atteigne `FUSIONNÉ` sans auto-certification.

---

## 6. Les Trois Résultats de Vérification

Mesures exécutées sur la branche `fusion/cycle-6-audit-fix` après correctif M120 :

1. **`python 01_Forkable/FKB00_Runtime/00_A0_Core/test_foundation_deletion_suite.py`** — **Exit `0` (`7/7 PASS`)** :
   - `[PASS 1/7]` `FUSION-ENONCE.md` SHA-256 intact (`41889edb9c468ea62ee4641328c0e6f4bac2c618b81da751eebd2af4c05f648d`) + `.gitattributes` ordonné + fixtures LF
   - `[PASS 2/7]` Purge doublons FKB06 (`109 -> 101`) & alignement 1:1 `.gitmodules == gitlinks 160000`
   - `[PASS 3/7]` Rust local VERT (`fondation-13-1` + Pont Hybride Phase 2 ; `RigInfinity=True -> 9 F8 prouvés`)
   - `[PASS 4/7]` Différentiel strict (`==`) + **`44` sabotages détectés PASS** (`6` prouvés : `00_Marketplace_YoutubeSkills`, `04_Inference_Youtube_Discovery_Registry`, `CLI-Anything`, `context-language-models`, `knowledge-catalog`, `video-director`) + `M058 desktop_live=False` + provenance `D-N048 V0` (`26ca7cb` / `dc3efe98...`) vérifiée sans `diff_proven.add("llm-wiki")`
   - `[PASS 5/7]` Compatibilité 1:1 Rust `fondation-13-1` + Interconnexion L0 (5 organes / 3 noyaux `ADR-15`)
   - `[PASS 6/7]` `ADR-15` 3 Noyaux respectés (`{'ÂME': 29, 'SYSTÈME NERVEUX': 29, 'CORPS': 62}`) | **`15 FUSIONNÉ`** vérifiés dynamiquement, **`17 RETENU`**, **`2 ÉCARTÉ`** (`M120 llm-wiki` vérifié `**PARTIEL**`)
   - `[PASS 7/7]` `15 ADRs` + Artefacts SPAD complets (incluant `RAPPORT-CORRECTION-M120.md`) + Clone Windows par défaut préserve LF

2. **`python 01_Forkable/check-modules-lock.py`** — **Exit `0` (`Vérifications 1-6 VERTES`)** :
   - Vérifications 1 à 4 : **`VERTES`**
   - Vérification 5 (`state >= 1` jugement 13e) : **`12/12 OK, 0 trou(s)`**
   - Vérification 6 (`manifeste + fiche + adapter`) : **`12/12 OK, 0 trou(s)`**

3. **`pwsh -NoProfile -ExecutionPolicy Bypass -File 02_Factory/checks.ps1`** — **Exit `0` (`GATE RESULT: PASS`)** :
   - `[1/6]` Doctor & Tools Check : **PASS**
   - `[2/6]` OpenWiki Purge Check : **PASS**
   - `[3/6]` JSON Schema & Config Check : **PASS**
   - `[4/6]` DOX & OKF v0.2 Bundle Check : **PASS**
   - `[5/6]` Append-Only Log Guard : **PASS**
   - `[6/6]` Secret Scanning Guard : **PASS**
   - `[7/7]` Level 5 Semantic Gate : **PASS** (`801` fichiers Core audités | `8` Holons Forkable CAS isolés)

---

## 7. Réconciliation Canonique `M084` / `M095` (Audit Fix #2)

Suite à la deuxième revue indépendante sur `49e638a`, la correspondance des identifiants dans la carte complète des 120 modules a été réconciliée sans équivoque :

- **`M084` = `video-director`** (`01_Forkable/FKB07_Money_Maker/02_Video/video-director`, `CORPS · Organe K5`, statut **`FUSIONNÉ`** par parité différentielle stricte + 11 sabotages).
- **`M095` = `BlenderWorld`** (`01_Forkable/FKB07_Money_Maker/06_3D_and_CAD/BlenderWorld`, `CORPS · Organe K5`, statut **`PARTIEL`** — exclu des modules fusionnés).
- **`M120` = `llm-wiki`** (`01_Forkable/FKB02_Memory/llm-wiki`, `ÂME · Organe K4`, statut **`PARTIEL`** maintenu).

### Harmonisations appliquées
1. **`01_Forkable/FKB00_Runtime/00_A0_Core/test_foundation_deletion_suite.py`** :
   - Renommage intégral des jeux de données, clés JSON, variables et fonctions liées à `video-director` (`verify_m084`, `inputs["m084"]`, `oracle["m084"]`, `m084_timelines`, `m084_out`, 11 sabotages `M084:vd_*`).
   - Ajout de la bijection mécanique `carte_id_to_name == reg_id_to_name` sur 120/120 modules, contrôle explicite `M084 == video-director`, `M095 == BlenderWorld`, `M120 == llm-wiki`.
   - Assertion stricte sur les 6 identifiants différentiels : `{"M044", "M050", "M056", "M084", "M117", "M118"}`, avec assertion explicite `by_name["BlenderWorld"][0] == "**PARTIEL**"` et garde inter-documents anti-dérive.
2. **`01_Forkable/FKB07_Money_Maker/02_Video/aspace_video_studio_foundation.py`** : correction des 4 libellés textuels (`M084`) sans aucune modification logique ni architecturale.
3. **Documentation SPAD (`LF`)** : mise à jour de `PRD-FONDATION.md`, `SDD-FONDATION.md`, `ADR-FUSION.md`, `adr/ADR-15.md` et `00_Memoire/bundle/index.md` ; préservation de `log.md:178` (append-only) avec nouvelle note d'audit en fin de journal.
4. **Clôture d'audit** : l'audit reste ouvert en attente de reproduction indépendante externe des 3 suites sur clone propre ; Cycle 7 non lancé.
