---
okf_version: "0.2"
type: Specification
title: "Wave 2 Selection — Audit Comparatif M069, M071, M077, M093"
enonce_ref: "00_Memoire/bundle/fusion/FUSION-ENONCE.md"
enonce_sha256: "41889edb9c468ea62ee4641328c0e6f4bac2c618b81da751eebd2af4c05f648d"
---

# WAVE-2-SELECTION — Évaluation Technique des 4 Candidats (`M069`, `M071`, `M077`, `M093`)

Toutes les métriques ci-dessous ont été mesurées directement sur les fichiers présents au dépôt dans `01_Forkable/` (branches et commits actifs).

---

## 1. Fiches Individuelles Mesurées au Fichier

### 1.1 `M069` — `claude-trading-skills` (`F-CORPS-06` · `CORPS · Organe K5`)
- **Provenance & Pin** : `01_Forkable/FKB07_Money_Maker/01_Trading/claude-trading-skills` · SHA `652a0aecd5ad1c1ca97b0a66e874ccab3dfa373d` · Licence **MIT**.
- **Architecture & Périmètre** : Collection massive de 74+ skills day-trading / macros / calendriers économiques / dashboards Streamlit, générateurs HTML, scripts de détection de bulles et calculateurs de position sizing.
- **Taille réelle du code** : **2 197 fichiers**, dont **882 fichiers `.py` (313 582 LOC Python)**, `667 .md` (`140 849 LOC`), `258 .json` (`38 090 LOC`), `131 .yaml` (`10 493 LOC`), `74 .skill` (`requires-python >=3.11,<3.14`, `packages = []` — scripts autonomes).
- **Dépendances externes** : `yfinance>=0.2.0`, `scipy>=1.13.1`, `jsonschema>=4.25.1`, `requests>=2.31.0`, `pyyaml>=6.0`, `pandas-market-calendars==5.2.2`, plus appels réseau live FMP/Yahoo/Finviz et Streamlit/Claude SDK dans les exemples.
- **Complexité du portage & faisabilité parité** : Très élevée à l'échelle du module entier (313,5k LOC Python réparties sur 882 scripts hétérogènes). Le seul sous-lot à forte valeur déterministe (position sizing <= 1 % et calendriers) représente < 2 % du code.
- **Risques sécurité / licence & coût certification** : Licence MIT saine, mais nombreux appels HTTP finance non mockés et données marché fluctuantes ; coût prohibitif si traité en bloc sans découpage en sous-modules explicites. **Verdict : Différé (découpage en sous-lots requis).**

### 1.2 `M071` — `financial-services` (`F-CORPS-06` · `CORPS · Organe K5`)
- **Provenance & Pin** : `01_Forkable/FKB07_Money_Maker/01_Trading/financial-services` · SHA `4b7d7e5dbc9de0187eb21c49d7a0de7a2859eed1` · Licence **Apache-2.0**.
- **Architecture & Périmètre** : Suite modulaire structurée pour l'analyse financière institutionnelle et les workflows B2B (`plugins/vertical-plugins`, `plugins/agent-plugins`, `managed-agent-cookbooks`) dotée d'un **cœur exécutable compact et déterministe** :
  1. `validate_dcf.py` (292 LOC) : validateur Excel DCF (détection des 7 erreurs Excel `#VALUE!/#DIV/0!/#REF!/#NAME?/#NULL!/#NUM!/#N/A`, contrôle des onglets `DCF/WACC/Sensitivity`, invariants `terminal_growth < wacc`, plage `WACC 5%..20%`, proportion `Terminal Value / EV` dans `40%..80%`).
  2. `extract_numbers.py` (305 LOC) : parseur chiffré et détecteur d'incohérences sur présentations Markdown (`11` multiplicateurs `T/B/bn/billion/M/mm/mn/million/K/k/thousand`, devises `$€£¥`, filtre années `1900..2099`, `9` catégories métier, regroupement à tolérance `5%`).
  3. Catalogue & Gouvernance Skills/Plugins (`scripts/check.py` 219 LOC, `scripts/validate.py` 42 LOC, `scripts/orchestrate.py` 89 LOC, `scripts/sync-agent-skills.py` 44 LOC, `scripts/version_bump.py` 209 LOC, `skill-creator/scripts/{init_skill.py 303, package_skill.py 110, quick_validate.py 95}`) : contrôle YAML/JSON/frontmatter, détection de dérive `filecmp.dircmp`, garde anti-injection sur `handoff_request` JSON Schema (`orchestrate.py`), calcul semver, validation stricte ASCII/BOM `.ps1`.
  4. `claude-for-msft-365-install/scripts/build-manifest.mjs` (309 LOC Node) : constructeur déterministe de manifestes XML Office/Outlook séparant paramètres query et fragment sensible (`#`).
- **Taille réelle du code** : **364 fichiers** ; `17 .py` (`2 850` LOC brutes, ramenées par déduplication SHA-256 à **14 fichiers `.py` uniques = 1 961 LOC Python** car `validate_dcf.py` [3 copies] et `extract_numbers.py` [2 copies] sont identiques), **1 `.mjs` (`309` LOC Node)**, `3 .ps1` (`465` LOC), `5 .sh` (`562` LOC), `40 .yaml` (`1 057` LOC), `40 .json` (`454` LOC), `241 .md` (`40 196` LOC). Les 4 scripts d'exemple Azure/Entra (`examples/python-bootstrap/*`, 253 LOC) restent explicitement documentés hors périmètre offline live.
- **Dépendances externes** : `pyyaml` (déjà installé en CI), `openpyxl` (1 package Python pur sans compilation C), `jsonschema` (1 package Python pur) et Node v24 (déjà installé en CI pour `build-manifest.mjs`). Zéro appel réseau requis pour l'oracle déterministe.
- **Complexité du portage & faisabilité parité** : Faible à modérée, très haute testabilité : nombreux seuils mathématiques exacts (`0 < adjacent < 1`, `terminal_growth >= wacc`, `0.05..0.20`, `0.40..0.80`, `1900..2099`, `diff_pct < 0.05`, `len > 64`, `b > 0x7F`), regex strictes et formats JSON/XML comparables en `==` exact.
- **Risques sécurité / licence & coût certification** : Licence Apache-2.0 très permissive ; modèle anti-injection déjà présent dans `orchestrate.py` ; coût de certification faible (~1 vague dédiée). **Verdict : CANDIDAT PRIORITAIRE UNIQUE RETENU (#1).**

### 1.3 `M077` — `earshot` (`F-CORPS-07` · `CORPS · Organe K5`)
- **Provenance & Pin** : `01_Forkable/FKB07_Money_Maker/02_Video/earshot` · SHA `8812d4fc32f91f9979fe13f52463e1af3a508ddc` · Licence **MIT**.
- **Architecture & Périmètre** : Analyse acoustique, critique audio de films, synthèse procédurale (`earshot forge`) et rétro-ingénierie acoustique (`earshot fit`).
- **Taille réelle du code** : **283 fichiers**, dont **168 fichiers `.py` (61 434 LOC Python)**, `63 .json` (`221 306 LOC`), `45 .md` (`8 512 LOC`).
- **Dépendances externes** : `torch>=2.6`, `transformers>=4.40` (embeddings CLAP), `librosa>=0.10`, `scipy>=1.11`, `soundfile>=0.12`, `soxr>=0.3`, `pyloudnorm>=0.1`, `scikit-learn>=1.3`, `matplotlib>=3.8`, `numpy>=1.26`, `pillow>=10`.
- **Complexité du portage & faisabilité parité** : Élevée (61,4k LOC Python DSP + stack ML PyTorch/CLAP/libsndfile volumineuse en CI GitHub Actions et sensible aux variations binaires floating-point CPU).
- **Risques sécurité / licence & coût certification** : Licence MIT ; coût d'intégration et de temps CI très élevé. **Verdict : Différé (postérieur à `M071` et `M093`).**

### 1.4 `M093` — `powerbi-to-ai-visuals` (`F-CORPS-10` · `CORPS · Organe K5`)
- **Provenance & Pin** : `01_Forkable/FKB07_Money_Maker/05_Executive_and_BI/powerbi-to-ai-visuals` · SHA `86583180c3473a95bfa84df344b8a6e014341095` · Licence **MIT**.
- **Architecture & Périmètre** : Extraction de fichiers Power BI (`.pbix`/`.pbip`), parsing TMDL & PBIR, traducteur borné `DAX -> SQL` refusant explicitement les expressions non supportées, couche sémantique DuckDB (`sortByColumn`, hiérarchies, `USERELATIONSHIP`), rendu HTML/JS et script de vérification de fidélité `verify_fidelity.py` (12 cellules matricielles + sous-totaux + grand total `27 921 670,52` à `TOLERANCE = 0.01`).
- **Taille réelle du code** : **33 fichiers**, **11 `.py` (`3 648` LOC Python)** (`tmdl.py` 264, `dax_sql.py` 340, `pbir_parse.py` 591, `semantic.py` 429, `analyze_model.py` 571, `pbi_extract.py` 304, `replicate_html.py` 386, `strategic_html.py` 306, `pbi_chat.py` 276, `verify_fidelity.py` 123, `pbi_common.py` 58), **2 `.js` (`1 079` LOC)**, `13 .md` (`1 199` LOC).
- **Dépendances externes** : Stdlib seule pour `tmdl.py`/`dax_sql.py`/`pbir_parse.py` ; `duckdb` + `pandas` pour la couche sémantique ; `pyarrow` + `pbixray` (extension native pour décompression `.pbix` XPress9) pour `pbi_extract.py`.
- **Complexité du portage & faisabilité parité** : Modérée (3,6k LOC Python propres), avec d'excellents invariants et oracle numérique ; exige néanmoins l'ajout de `duckdb` + `pandas` (et gestion du cas `pbixray` sur `.pbix` binaires ou fixtures `.pbip`/DuckDB pré-extraintes).
- **Risques sécurité / licence & coût certification** : Licence MIT, excellente valeur produit B2B BI, coût moyen. **Verdict : Classé #2 (vague suivant `M071`).**

---

## 2. Matrice Multicritère Comparée

| Critère | `M069 claude-trading-skills` | `M071 financial-services` | `M077 earshot` | `M093 powerbi-to-ai-visuals` |
|---|---|---|---|---|
| **Taille code exécutable** | 882 `.py` (**313 582 LOC**) | 14 `.py` uniques (**1 961 LOC**) + 1 `.mjs` (**309 LOC**) | 168 `.py` (**61 434 LOC**) | 11 `.py` (**3 648 LOC**) + 2 `.js` (**1 079 LOC**) |
| **Valeur architecturale** | Hétérogène (redondante avec `M074`/calculs) | **Forte** (Audit DCF, Extraction Deck, Validation Skills/FSI, M365) | Moyenne (audio/SFX uniquement) | **Forte** (Modernisation BI Power BI -> DuckDB/SQL) |
| **Complexité du portage** | Très élevée (explosion de périmètre) | **Faible à modérée** (modules compacts et découplés) | Élevée (DSP + neural) | Modérée (`3,6k` LOC propres + traducteur DAX->SQL) |
| **Dépendances CI** | `yfinance`, `scipy`, `pandas-market-calendars`, live APIs | **`pyyaml` (déjà CI) + `openpyxl`, `jsonschema` + Node 24 (déjà CI)** | `torch>=2.6`, `transformers`, `librosa`, `soundfile`, `scipy` | `duckdb`, `pandas`, `pyarrow`, `pbixray` (codec binaire) |
| **Portabilité Linux/Win CI** | Moyenne (timeouts réseau live) | **Maximale** (100 % déterministe offline) | Faible (lourde stack native audio/torch) | Bonne sur `.pbip`/DuckDB (nécessite wheel `pbixray` pour `.pbix`) |
| **Faisabilité parité & seuils** | Faible à l'échelle du repo | **Excellente** (plages DCF, tolérance 5%, semver, ASCII/BOM, JSON Schema, XML M365) | Complexe (flottants DSP multi-plates-formes) | Très bonne (`verify_fidelity.py` + bornes `TOLERANCE = 0.01`) |
| **Sécurité & Licence** | MIT · exposition APIs externes | **Apache-2.0 · garde anti-injection `orchestrate.py`** | MIT · poids neuronaux externes | MIT · lecture locale sans réseau |
| **Coût de certification** | Très élevé (sans découpage) | **Bas (1 vague propre)** | Très élevé | Moyen (juste après `M071`) |
| **Classement final** | **Différé (à découper)** | **#1 — SÉLECTIONNÉ PRIORITAIRE** | **Différé** | **#2 — Suivant séquentiel** |

---

## 3. Décision de Sélection

**Le candidat prioritaire unique retenu pour la prochaine vague d'exécution est `M071 financial-services`.**
`M093 powerbi-to-ai-visuals` est officiellement positionné en #2 séquentiel une fois `M071` certifié en `FUSIONNÉ`.
