---
okf_version: "0.2"
type: Report
title: "Certification Organe Natif M071 financial-services (CORPS · Organe K5)"
enonce_ref: "00_Memoire/bundle/fusion/FUSION-ENONCE.md"
enonce_sha256: "41889edb9c468ea62ee4641328c0e6f4bac2c618b81da751eebd2af4c05f648d"
---

# M071-CERTIFICATION-REPORT — `financial-services` → `aspace_financial_services_organ.py`

- **Branche** : `fusion/cycle-7`
- **Module certifié** : `M071` · `financial-services` (`GITLINK`, pin `4b7d7e5dbc9de0187eb21c49d7a0de7a2859eed1`, licence `Apache-2.0`)
- **Noyau & Organe (`ADR-15`)** : `CORPS` (`OpenRig`) · `Organe K5` (Métabolisme B2B, Vidéo & Finance S0)
- **Organe natif cible** : `01_Forkable/FKB07_Money_Maker/01_Trading/aspace_financial_services_organ.py`
- **Verrou de sécurité S0 (`ADR-07`)** : `READ_ONLY_VETO_S0 = True` (lecture/validation pure uniquement, zéro passage d'ordre, zéro auto-certification : `run_financial_services_self_test()["source_parity_verified"] == []`)
- **Statut certifié** : **`FUSIONNÉ`** (Corpus porté à **`18 / 120` `FUSIONNÉ`**, **`83` `PARTIEL`**, **`17` `RETENU`**, **`2` `ÉCARTÉ`** ; `M058`, `M066`, `M095` et `M120` maintenus **`PARTIEL`**).

---

## 1. Périmètre Porté 1:1 & Fidélité Amont Documentée

1. **`DCFModelValidator` (`validate_dcf.py`)** :
   - Validation de structure d'onglets (`DCF`, `WACC`, `Sensitivity`), détection des 7 codes d'erreur Excel (`#VALUE!`, `#DIV/0!`, `#REF!`, `#NAME?`, `#NULL!`, `#NUM!`, `#N/A`) et comptage des formules, vérification `terminal_growth < wacc` (y compris cas limite `0.10 == 0.10` vs `0.0999 < 0.10`), plage `WACC` (`5 %..20 %`) et part `Terminal Value / EV` (`< 0.40`, `0.40..0.80`, `> 0.80`).
   - **Quirk amont #1 préservé 1:1** : à la ligne `validate_dcf.py:163`, `self.workbook_values.get('WACC')` lève `AttributeError` sur un `openpyxl.Workbook` réel, capturée en avertissement (`"Could not validate WACC range: 'Workbook' object has no attribute 'get'"`). Les bornes exactes `[0.0499, 0.05, 0.20, 0.2001]` de `_check_wacc_range()` et `evaluate_wacc_range()` sont néanmoins testées directement sur `workbook_values = {"WACC": ...}` contre l'oracle amont.
2. **`PitchDeckNumberExtractor` (`extract_numbers.py`)** :
   - Extraction regex sur diapositives Markdown, filtre d'années `1900..2099` (`1899` et `2100` conservés), 9 catégories (`revenue`, `ebitda_margin`, `ebitda`, `margin`, `growth`, `multiple`, `valuation`, `percentage`, `other`), regroupement d'incohérences à tolérance strictement `< 5 %` et sortie CLI `--output <json> --check`.
   - **Quirk amont #2 préservé 1:1** : `normalize_number()` évalue `unit_key.lower() in unit.lower()`, conservant l'appariement historique `'b' in 'bps'` (`1e9`).
3. **`FSICatalogAndSkillValidator` (`check.py`, `validate.py`, `orchestrate.py`, `version_bump.py`, `sync-agent-skills.py`, `quick_validate.py`, `init_skill.py`, `package_skill.py`)** :
   - Audit catalogue `lint_fsi_catalog()` (YAML via file stream `yml.open(encoding="utf-8")`, JSON, frontmatter `agent/*.md`, résolution de références, comparaison `filecmp.dircmp` skills verticales vs agent, backticks prose, marketplace, fichiers requis `managed-agent-cookbooks`, détection non-ASCII sur `.ps1` sans BOM UTF-8). Comparé `==` sur le **vrai catalogue réel `82` fichiers** (`rc=1`, exactes 3 erreurs `bundled-skill` sur `meeting-prep-agent`) ET sur un catalogue synthétique déclenchant **18 erreurs** multi-sections.
   - Validation JSON Schema (`validate.py` vs `validate_json_schema`), semver (`parse_semver`, `patch_bump`, `is_ahead`), synchronisation `sync_agent_skills`, et outils `skill-creator` (`validate_skill` sur 15 cas limites, gabarits exacts `SKILL_TEMPLATE`/`EXAMPLE_SCRIPT`/`EXAMPLE_REFERENCE`/`EXAMPLE_ASSET` + `0o755`, refus du `[TODO:...]` YAML `list` avant édition puis archive `.skill` via `package_skill`).
   - **Quirk amont #3 préservé 1:1 (`orchestrate.py:40`)** : la regex amont `HANDOFF_RE = r'\{"type":\s*"handoff_request".*?\}'` s'arrête sur la première accolade fermante (celle de l'objet `payload`), de sorte que `extract_handoff()` renvoie `None` sur tout payload objet imbriqué. Ce comportement brut est conservé 1:1 (`"default"`), tout en vérifiant séparément `"nested_re"` (allowlist 10 cibles, `event` `<= 2000`, `context_ref` `<= 256` et `additionalProperties: False`) contre le même `orchestrate.py` amont.
4. **`M365ManifestBuilder` (`build-manifest.mjs`, oracle Node v24)** :
   - Validation complète des 28 clés `M365_KEYS` (dans l'ordre exact `build-manifest.mjs`), séparation query publique vs fragment sensible `#` (`M365_SENSITIVE_KEYS`), échappement XML `&amp;`, politiques `access_policies` et modèles `available_models`, testés **contre `node build-manifest.mjs` réel** via serveur HTTP loopback éphémère sur 17 scénarios.
   - Parité d'encodage **WHATWG `URLSearchParams`** (`urllib.parse.quote_plus(..., safe="*-._").replace("~", "%7E")`, validée notamment via `otlp_headers=tok~!*()_.-/\u00e9`).
   - **Normalisation V8/Python explicite** : pour le cas volontairement invalide JSON (`available_models={bad json`), le suffixe spécifique au moteur JSON après `"is not valid JSON:"` est normalisé afin d'éviter toute divergence entre le parseur V8 et `json.loads`.

---

## 2. Hors Périmètre Offline Explicitement Assumé

Conformément à `ORGAN-CERTIFICATION-CONTRACT.md` et `WAVE-2-READINESS.md`, les opérations dépendantes de services cloud/secrets externes restent hors preuve offline :
- Bootstrap d'authentification live Microsoft Entra ID / Azure AD / PowerShell M365 (`examples/python-bootstrap/*`).
- Streaming réseau Anthropic Managed Agents (`orchestrate.py::run` / `client.beta.agents.sessions.stream`).
- Récupération distante HTTPS sur `https://pivot.claude.ai/*` (remplacée en Phase A par un serveur HTTP loopback local servant des gabarits XML déterministes).

---

## 3. Preuves Vérifiées (Local + CI Porte B)

- **Phase A (Oracle amont réel)** : exécution directe des scripts Python amont de `financial-services` (`PYTHONUTF8=1`) ET de `node build-manifest.mjs` sur `127.0.0.1`.
- **Phase B (Suppression physique)** : destruction effective de `01_Forkable/FKB07_Money_Maker/01_Trading/financial-services` dans `iso_root` par `_force_rmtree` suivie de `assert not target.exists()`. Le gitlink dans `.gitmodules` n'est conservé que pour rejouer l'oracle Phase A.
- **Phase C (Parité `==` & Anti-Sabotage)** : égalité stricte `==` sur les 9 sous-ensembles `M071`, auto-test L0 `source_parity_verified == []`, reçu R10 `D-FSI-PARITY` consigné sur `aspace_foundation_kernel.py` (`L0 221->230`), et **42 sabotages/mutations dédiés `M071`** (31 stubs de tous les symboles publics, 10 mutations de bornes/encodage dont `*` et `~`, et 1 injection de clé parasite sur `validate_dcf_model`), portant la suite totale à **`171` sabotages détectés** (`>= 165`).
