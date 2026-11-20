---
okf_version: "0.2"
type: Specification
title: "CARTE DES PRINCIPES — Vecteurs de Principe des 120 Modules de 01_Forkable"
enonce_ref: "00_Memoire/bundle/fusion/FUSION-ENONCE.md"
enonce_sha256: "41889edb9c468ea62ee4641328c0e6f4bac2c618b81da751eebd2af4c05f648d"
---

# CARTE-DES-PRINCIPES — Inventaire Exhaustif & Vecteurs de Principe (120 Modules + 8 Doublons)

> **Note de méthode (§2 & §3)** : Chaque fiche ci-dessous a été établie par lecture directe des sources brutes présentes au HEAD `5cfffa9f4c15aad97e278dbc78c8a895a9dff012` (`.gitmodules`, `git ls-files --stage`, `MODULES-LOCK.json`, manifestes `*.manifest.json`, fiches `*-ADAPTATION.md`, `README*`, `package.json`, `Cargo.toml`, `pyproject.toml`, et moteurs natifs `.py`/`.ts`/`.rs`).

---

## 0. Mesure Zéro & Réconciliation des Écarts Documentaires

Les documents historiques du dépôt annoncent des chiffres divergents. La mesure directe au système de fichiers et à l'index Git établit la vérité suivante :

| Source / Document | Nombre annoncé | Vérité vérifiée au HEAD & Explication exacte de l'écart |
|---|---|---|
| `propositions-unification-forks-fusions-autoresearch.md` (2026-11-09) | **120 entrées** (111 distincts, 21 amont, 9 doublons) | Instantané antérieur à : rapatriement du gist `llm-wiki` (120→119), retrait doublon `hermes-agent` (119→118), retraits F8 (`agent-zero`, 3 bots, 7 modules pas 8 + `herdr-core` : 118→106), puis ajouts de `agent-browser`, `agent-desktop`, `bifrost` (+3 → 109 entrées `.gitmodules`). |
| `.gitmodules` (fichier brut) | **109 entrées** (101 URLs distinctes) | Toutes pointent vers `Amdkn/*.git` (**0 pointeur amont restant**). Contient **8 entrées doublons orphelines** `[submodule "01_Forkable/FKB02_Video_SaaS/*"]` pointant vers `01_Forkable/FKB06_Video_SaaS/*` sans gitlink `160000` dans l'index. |
| Index Git (`git ls-files --stage 01_Forkable`, mode `160000`) | **101 gitlinks actifs** | Exactement les 101 URLs distinctes actives : FKB00 (27), FKB01 (14), FKB02 (10), FKB03 (4), FKB04 (8), FKB06 (**0**), FKB07 (34), FKB08 (4). |
| `FKB01/index.md` | 12 sous-modules listés | Omet `FreeVPS` et `bifrost` (réel : 14 gitlinks + 1 registre `04_Inference_Youtube_Discovery_Registry`). |
| `FKB02/index.md` | « 8 Sous-Modules » annoncés | Omet `gbrain`, `infinite-brain-os`, `infinite-brain-harness` ; cite `llm-wiki` qui n'est plus un gitlink (réel : 10 gitlinks + 1 dossier `llm-wiki`). |
| `FKB04/index.md` | 6 sous-modules listés | Omet `caveman` et `claude-mem` (réel : 8 gitlinks). |
| `FKB07/index.md` | 30 sous-modules listés | Omet `Scrapling`, `dify`, `presenton`, `BusinessOS` (réel : 34 gitlinks + 2 dossiers natifs/app `00_Marketplace_YoutubeSkills`, `LibertyRide2`). |
| Modules F8 dé-pointés (FKB00) | 12 modules à manifeste | `cordis`, `automaton`, `pi`, `infinity`, `openrig`, `agent-zero`, `prime-agent`, `openbot`, `openmuse`, `OpenDots`, `OpenDuet`, `herdr-core` ont quitté `.gitmodules` lors de F8 mais leurs manifestes/fiches vivent dans `00_A0_Core/`. |
| Natifs L0 (FKB00) + Extra FKB | 3 natifs + 4 unités | `fondation-13-1`, `aspace-fiber-host`, `source-control-natif` + `04_Inference_Youtube_Discovery_Registry`, `llm-wiki`, `00_Marketplace_YoutubeSkills`, `LibertyRide2`. |
| **Total Corpus $F$ audité** | **120 modules distincts + 8 doublons** | **101 gitlinks actifs + 12 F8 dé-pointés + 3 natifs L0 + 4 unités extra = 120 fiches (`M001..M120`) + 8 fiches doublons `.gitmodules` (`D01..D08`).** |

---

## 1. Fiches des 120 Modules (`M001` à `M120`)

### M001 — `a0-plugins` (GITLINK)
- **Provenance & Sources Brutes Lues** : chemin `01_Forkable/FKB00_Runtime/00_A0_Core/a0-plugins` | repo `https://github.com/Amdkn/a0-plugins.git` | SHA/pin `fa8df8527a3c` | licence `MIT` | sources : `01_Forkable/FKB00_Runtime/00_A0_Core/a0-plugins.manifest.json`, `01_Forkable/FKB00_Runtime/00_A0_Core/a0-plugins-ADAPTATION.md`, `01_Forkable/MODULES-LOCK.json`
- **Noyau Cible & Destination ÉNONCÉ §1(1)** : **CORPS · Organe K2 (Exécution, Anything & 3D)** · Destination : **`FUSIONNÉ`** · Statut Vérifié (§5.8) : **`PARTIEL`** (Adapter `fa8df85` vérifié (235 dossiers, 230 indexés) ; reste à absorber le registre dynamique de plugins dans K2 et retirer le gitlink.)
- **Principe** : Catalogue modulaire d'extensions dynamiques d'Agent Zero (outils, prompts, intégrations) découpé par capacité.
- **Invariants** : Aucun plugin exécuté sans audit télémétrie ni déclaration de capacité ; séparation stricte extension vs noyau.
- **Interfaces** : Index des 230 plugins a0-plugins + chargeur d'extensions A0.
- **Perte au Retrait & Conflits** : Perte sans fusion : bibliothèque de connecteurs et d'outils prêts à l'emploi pour A0. Conflit : formats de plugins hétérogènes -> ADR-10. (*Arbitrage : ADR-10*)

### M002 — `deepseek-harness` (GITLINK)
- **Provenance & Sources Brutes Lues** : chemin `01_Forkable/FKB00_Runtime/00_A0_Core/deepseek-harness` | repo `https://github.com/Amdkn/deepseek-harness.git` | SHA/pin `fcc0ad462172` | licence `voir-source-brute` | sources : `01_Forkable/FKB00_Runtime/00_A0_Core/deepseek-harness.manifest.json`, `01_Forkable/FKB00_Runtime/00_A0_Core/deepseek-harness-ADAPTATION.md`
- **Noyau Cible & Destination ÉNONCÉ §1(1)** : **SYSTÈME NERVEUX · Bus L0 & Fibres** · Destination : **`FUSIONNÉ`** · Statut Vérifié (§5.8) : **`PARTIEL`** (Adapté état 2 (`fcc0ad4`) ; reste à porter les profils dsh/superagent en pur contrat de fibre K2/K1 et retirer le gitlink.)
- **Principe** : Harnais « Everything-is-a-Plugin » motorisé par Cordis avec gestion de threads, Eval->Ticket->Assignment et règle 5s background shell.
- **Invariants** : Séparation stricte Eval vs Executor abonnés ; commandes > 5s basculées en background ; préfixe agent obligatoire sur GitHub.
- **Interfaces** : dsh web (:3081) / dsh headless / cordis.patch.yml / 00_Memoire/dsh-superagent.
- **Perte au Retrait & Conflits** : Perte sans fusion : perte du protocole Superagent de filtrage d'attention humaine et du routage dsh. Conflit : web UI séparée -> ADR-02, ADR-10. (*Arbitrage : ADR-02, ADR-10*)

### M003 — `spynel` (GITLINK)
- **Provenance & Sources Brutes Lues** : chemin `01_Forkable/FKB00_Runtime/00_A0_Core/spynel` | repo `https://github.com/Amdkn/spynel.git` | SHA/pin `fa9fe416159d` | licence `voir-source-brute` | sources : `01_Forkable/FKB00_Runtime/00_A0_Core/spynel.manifest.json`, `01_Forkable/FKB00_Runtime/00_A0_Core/spynel-ADAPTATION.md`
- **Noyau Cible & Destination ÉNONCÉ §1(1)** : **SYSTÈME NERVEUX · Bus L0 & Fibres** · Destination : **`FUSIONNÉ`** · Statut Vérifié (§5.8) : **`PARTIEL`** (Adapter Go `fa9fe41` livré ; reste à unifier ses sondes de sentinelle dans le bus d'observabilité RigInfinity et retirer le gitlink.)
- **Principe** : Sentinelle et télémétrie temps réel locale de l'exécution agentique (détection d'anomalies, boucle de contrôle).
- **Invariants** : Télémétrie strictement locale (0 fuite externe) ; arrêt d'urgence déterministe sur dérive.
- **Interfaces** : Binaire/package Go spynel + sonde d'orchestration.
- **Perte au Retrait & Conflits** : Perte sans fusion : perte de l'instrumentation sentinelle temps réel des agents bas niveau. Conflit : télémétrie amont vs zéro-fuite -> ADR-08. (*Arbitrage : ADR-08*)

### M004 — `tuxee` (GITLINK)
- **Provenance & Sources Brutes Lues** : chemin `01_Forkable/FKB00_Runtime/00_A0_Core/tuxee` | repo `https://github.com/Amdkn/tuxee.git` | SHA/pin `5cad42ae0682` | licence `voir-source-brute` | sources : `01_Forkable/FKB00_Runtime/00_A0_Core/tuxee.manifest.json`, `01_Forkable/FKB00_Runtime/00_A0_Core/tuxee-ADAPTATION.md`
- **Noyau Cible & Destination ÉNONCÉ §1(1)** : **CORPS · Organe K2 (Exécution, Anything & 3D)** · Destination : **`FUSIONNÉ`** · Statut Vérifié (§5.8) : **`PARTIEL`** (Adapter Go `5cad42a` livré ; reste à brancher son interface conteneur/Linux dans K2 sans redondance avec Agent-Zero/Orca et retirer le gitlink.)
- **Principe** : Exécution système isolée en environnement Linux/conteneur avec interface D10 découplée du code OS hôte.
- **Invariants** : Zéro code OS hôte dans l'adapter ; isolation stricte des commandes système.
- **Interfaces** : Interface D10 tuxee / exécuteur conteneurisé Linux.
- **Perte au Retrait & Conflits** : Perte sans fusion : abstraction d'exécution Linux/conteneur propre. Conflit : recouvrement avec sandbox Orca/Infinity -> ADR-02, ADR-05. (*Arbitrage : ADR-02, ADR-05*)

### M005 — `RigInfinity` (GITLINK)
- **Provenance & Sources Brutes Lues** : chemin `01_Forkable/FKB00_Runtime/01_Holo_TriptyqueCore/RigInfinity` | repo `https://github.com/Amdkn/RigInfinity.git` | SHA/pin `95e95f9b7a60` | licence `Apache-2.0` | sources : `01_Forkable/FKB00_Runtime/00_A0_Core/riginfinity.manifest.json`, `01_Forkable/FKB00_Runtime/00_A0_Core/riginfinity-ADAPTATION.md`, `01_Forkable/MODULES-LOCK.json`
- **Noyau Cible & Destination ÉNONCÉ §1(1)** : **SYSTÈME NERVEUX · Bus L0 & Fibres** · Destination : **`FUSIONNÉ`** · Statut Vérifié (§5.8) : **`PARTIEL`** (Cœur Rust initialisé (`95e95f9`) et **VERT 105/105 (`cargo test` WSL2 Linux)** ; part manquante : gitlink `160000` encore actif dans `.gitmodules`, `lifecycle.{dispose,health,lease,rollback}` & `cordis_host` = `PENDING`, compilation native POSIX (`cfg(unix)`).)
- **Principe** : Daemon Maître Unique Rust unifiant boucle agentique, hibernation RAP, lignage ULID, proxy MCP, source-control WAL et plateforme bots incarnés.
- **Invariants** : 1 seul processus daemon sur 127.0.0.1 uniquement ; strace 0 connect() externe ; clés providers jamais portées (D9, routage gateway :31415).
- **Interfaces** : riginfinity-daemon (crates/infinity-daemon/src/lib.rs) / mcp_proxy.rs / session_store.rs.
- **Perte au Retrait & Conflits** : Perte sans fusion : retour à la fragmentation des daemons et saturation RAM des 578 Holons. Conflit : multi-daemons historiques -> ADR-02. (*Arbitrage : ADR-02*)

### M006 — `MiroFish` (GITLINK)
- **Provenance & Sources Brutes Lues** : chemin `01_Forkable/FKB00_Runtime/02_PredictiveWargame_MachineLearning/MiroFish` | repo `https://github.com/Amdkn/MiroFish.git` | SHA/pin `9b49ac4fc682` | licence `AGPL-3.0` | sources : `01_Forkable/FKB00_Runtime/00_A0_Core/MiroFish.manifest.json`, `01_Forkable/FKB00_Runtime/00_A0_Core/MiroFish-ADAPTATION.md`, `01_Forkable/FKB00_Runtime/02_PredictiveWargame_MachineLearning/MiroFish/README-ZH.md`, `01_Forkable/FKB00_Runtime/02_PredictiveWargame_MachineLearning/MiroFish/package.json`
- **Noyau Cible & Destination ÉNONCÉ §1(1)** : **SYSTÈME NERVEUX · Organe K3-ML (Cortex Prédictif & Wargame)** · Destination : **`FUSIONNÉ`** · Statut Vérifié (§5.8) : **`PARTIEL`** (Adapté état 1 (`9b49ac4` / `dff2f01`), isolé en service AGPL-3.0 ; reste à connecter ses sorties wargame à K5 via contrat REST/R10 sans contamination de licence et archiver le gitlink.)
- **Principe** : Moteur de simulation Wargame multi-agents par essaim (prédiction de scénarios complexes par simulation d'acteurs).
- **Invariants** : Confinement strict en service isolé séparé (AGPL-3.0, zéro linkage statique dans le noyau Apache-2.0/MIT) ; validation sur hold-out.
- **Interfaces** : Service API isolé MiroFish (simulation Wargame S3-RORY 4P).
- **Perte au Retrait & Conflits** : Perte sans fusion : perte de la simulation multi-agents générative dans les wargames stratégiques. Conflit : licence AGPL-3.0 contaminante -> ADR-09. (*Arbitrage : ADR-09*)

### M007 — `PathFM` (GITLINK)
- **Provenance & Sources Brutes Lues** : chemin `01_Forkable/FKB00_Runtime/02_PredictiveWargame_MachineLearning/PathFM` | repo `https://github.com/Amdkn/PathFM.git` | SHA/pin `8a3a42c05ce8` | licence `LICENSE fichier lu` | sources : `01_Forkable/FKB00_Runtime/00_A0_Core/PathFM.manifest.json`, `01_Forkable/FKB00_Runtime/00_A0_Core/PathFM-ADAPTATION.md`, `01_Forkable/FKB00_Runtime/02_PredictiveWargame_MachineLearning/PathFM/README.md`, `01_Forkable/FKB00_Runtime/02_PredictiveWargame_MachineLearning/PathFM/pyproject.toml`
- **Noyau Cible & Destination ÉNONCÉ §1(1)** : **SYSTÈME NERVEUX · Organe K3-ML (Cortex Prédictif & Wargame)** · Destination : **`FUSIONNÉ`** · Statut Vérifié (§5.8) : **`PARTIEL`** (Adapté état 1 (`8a3a42c` / `8bcdd5b`), confiné usage interne CC BY-NC 4.0 ; reste à finaliser le wrapper de contrat K5 interne et archiver le gitlink.)
- **Principe** : Modèle fondation génératif de trajectoires multivariées (un ensemble de prévisions pour plusieurs questions en aval).
- **Invariants** : Interdiction absolue d'exposition en profil commercial b2b_commercial (licence CC BY-NC 4.0 restreinte à a0_internal_wargame).
- **Interfaces** : aspace_pathfm_adapter / assert_commercial_safe() dans aspace_precheck_weights.py.
- **Perte au Retrait & Conflits** : Perte sans fusion : perte de la prévision générative multi-trajectoires sur wargames internes. Conflit : usage commercial B2B vs CC BY-NC 4.0 -> ADR-09. (*Arbitrage : ADR-09*)

### M008 — `autogluon` (GITLINK)
- **Provenance & Sources Brutes Lues** : chemin `01_Forkable/FKB00_Runtime/02_PredictiveWargame_MachineLearning/autogluon` | repo `https://github.com/Amdkn/autogluon.git` | SHA/pin `e3cb3b71386c` | licence `LICENSE fichier lu` | sources : `01_Forkable/FKB00_Runtime/00_A0_Core/autogluon.manifest.json`, `01_Forkable/FKB00_Runtime/00_A0_Core/autogluon-ADAPTATION.md`, `01_Forkable/FKB00_Runtime/02_PredictiveWargame_MachineLearning/autogluon/README.md`, `01_Forkable/FKB00_Runtime/02_PredictiveWargame_MachineLearning/autogluon/pyproject.toml`
- **Noyau Cible & Destination ÉNONCÉ §1(1)** : **SYSTÈME NERVEUX · Organe K3-ML (Cortex Prédictif & Wargame)** · Destination : **`FUSIONNÉ`** · Statut Vérifié (§5.8) : **`PARTIEL`** (Intégré dans triptych_autogluon_engine.py et wargame_tabular_engine.py (Apache-2.0) ; reste test de suppression du gitlink.)
- **Principe** : Orchestrateur unifié AutoML tabulaire et séries temporelles servant d'ossature au banc de tests prédictifs.
- **Invariants** : Exécution exclusivement sur poids montés et vérifiés (WeightsNotMountedError) ; aucune extrapolation linéaire factice.
- **Interfaces** : TriptychWargameOrchestrator / PredictiveWargameEngine (b2b_commercial | a0_internal_wargame).
- **Perte au Retrait & Conflits** : Perte sans fusion : perte de l'orchestrateur tabulaire/séries Apache-2.0 commercialisable. Conflit : résolu avec Chronos/TimesFM via profils -> ADR-09. (*Arbitrage : ADR-09*)

### M009 — `chronos-forecasting` (GITLINK)
- **Provenance & Sources Brutes Lues** : chemin `01_Forkable/FKB00_Runtime/02_PredictiveWargame_MachineLearning/chronos-forecasting` | repo `https://github.com/Amdkn/chronos-forecasting.git` | SHA/pin `e049fe2e20c0` | licence `LICENSE fichier lu` | sources : `01_Forkable/FKB00_Runtime/00_A0_Core/chronos-forecasting.manifest.json`, `01_Forkable/FKB00_Runtime/00_A0_Core/chronos-forecasting-ADAPTATION.md`, `01_Forkable/FKB00_Runtime/02_PredictiveWargame_MachineLearning/chronos-forecasting/README.md`, `01_Forkable/FKB00_Runtime/02_PredictiveWargame_MachineLearning/chronos-forecasting/pyproject.toml`
- **Noyau Cible & Destination ÉNONCÉ §1(1)** : **SYSTÈME NERVEUX · Organe K3-ML (Cortex Prédictif & Wargame)** · Destination : **`FUSIONNÉ`** · Statut Vérifié (§5.8) : **`PARTIEL`** (Intégré comme axe temporel commercial dans triptych_autogluon_engine.py ; reste découplage/archivage du gitlink.)
- **Principe** : Modèle fondation pré-entraîné de prévision de séries temporelles produisant des quantiles probabilistes calibrés (q10/q50/q90).
- **Invariants** : Chargement exclusif depuis poids locaux montés ; obligatoire en profil b2b_commercial (Apache-2.0) à la place de TimesFM.
- **Interfaces** : TriptychWargameOrchestrator._load_chronos() -> temporal_q10/median/q90.
- **Perte au Retrait & Conflits** : Perte sans fusion : perte du prédicteur temporel probabiliste commercialisable. Conflit : coexistence TimesFM -> ADR-09. (*Arbitrage : ADR-09*)

### M010 — `mitra-2` (GITLINK)
- **Provenance & Sources Brutes Lues** : chemin `01_Forkable/FKB00_Runtime/02_PredictiveWargame_MachineLearning/mitra-2` | repo `https://github.com/Amdkn/mitra-2.git` | SHA/pin `3f277e5aa1b0` | licence `LICENSE fichier lu` | sources : `01_Forkable/FKB00_Runtime/00_A0_Core/mitra-2.manifest.json`, `01_Forkable/FKB00_Runtime/00_A0_Core/mitra-2-ADAPTATION.md`, `01_Forkable/FKB00_Runtime/02_PredictiveWargame_MachineLearning/mitra-2/README.md`, `01_Forkable/FKB00_Runtime/02_PredictiveWargame_MachineLearning/mitra-2/pyproject.toml`
- **Noyau Cible & Destination ÉNONCÉ §1(1)** : **SYSTÈME NERVEUX · Organe K3-ML (Cortex Prédictif & Wargame)** · Destination : **`FUSIONNÉ`** · Statut Vérifié (§5.8) : **`PARTIEL`** (Adapter natif `2676f75` intégré dans wargame_tabular_engine.py ; reste test de suppression complet du gitlink.)
- **Principe** : Modèle fondation tabulaire In-Context Learning (classification & régression 12L) sans réentraînement par tâche.
- **Invariants** : Aucun fallback heuristique (sommes pondérées interdites) ; évaluation stricte sur hold-out.
- **Interfaces** : autogluon/mitra-classifier-2 & mitra-regressor-2 via PredictiveWargameEngine.
- **Perte au Retrait & Conflits** : Perte sans fusion : perte du classifieur tabulaire zéro-shot Apache-2.0 pour les offres LD01. Conflit : dual-jury avec TabFM -> ADR-09. (*Arbitrage : ADR-09*)

### M011 — `tabfm` (GITLINK)
- **Provenance & Sources Brutes Lues** : chemin `01_Forkable/FKB00_Runtime/02_PredictiveWargame_MachineLearning/tabfm` | repo `https://github.com/Amdkn/tabfm.git` | SHA/pin `a8d6be922db6` | licence `LICENSE fichier lu` | sources : `01_Forkable/FKB00_Runtime/00_A0_Core/tabfm.manifest.json`, `01_Forkable/FKB00_Runtime/00_A0_Core/tabfm-ADAPTATION.md`, `01_Forkable/FKB00_Runtime/02_PredictiveWargame_MachineLearning/tabfm/README.md`, `01_Forkable/FKB00_Runtime/02_PredictiveWargame_MachineLearning/tabfm/pyproject.toml`
- **Noyau Cible & Destination ÉNONCÉ §1(1)** : **SYSTÈME NERVEUX · Organe K3-ML (Cortex Prédictif & Wargame)** · Destination : **`FUSIONNÉ`** · Statut Vérifié (§5.8) : **`PARTIEL`** (Intégré en profil interne dans wargame_tabular_engine.py ; reste test de suppression du gitlink.)
- **Principe** : Modèle fondation tabulaire 24L compatible scikit-learn pour jury dual interne de vérification croisée.
- **Invariants** : Confiné au profil interne a0_internal_wargame (jamais chargé en profil b2b_commercial) ; comparaison dual-jury avec Mitra-v2.
- **Interfaces** : google/tabfm-1.1.0-pytorch -> tabfm_win_probability.
- **Perte au Retrait & Conflits** : Perte sans fusion : perte du second juge tabulaire indépendant sur wargames internes. Conflit : confinement licence/profil -> ADR-09. (*Arbitrage : ADR-09*)

### M012 — `timesfm` (GITLINK)
- **Provenance & Sources Brutes Lues** : chemin `01_Forkable/FKB00_Runtime/02_PredictiveWargame_MachineLearning/timesfm` | repo `https://github.com/Amdkn/timesfm.git` | SHA/pin `105057005b5f` | licence `LICENSE fichier lu` | sources : `01_Forkable/FKB00_Runtime/00_A0_Core/timesfm.manifest.json`, `01_Forkable/FKB00_Runtime/00_A0_Core/timesfm-ADAPTATION.md`, `01_Forkable/FKB00_Runtime/02_PredictiveWargame_MachineLearning/timesfm/README.md`, `01_Forkable/FKB00_Runtime/02_PredictiveWargame_MachineLearning/timesfm/pyproject.toml`
- **Noyau Cible & Destination ÉNONCÉ §1(1)** : **SYSTÈME NERVEUX · Organe K3-ML (Cortex Prédictif & Wargame)** · Destination : **`FUSIONNÉ`** · Statut Vérifié (§5.8) : **`PARTIEL`** (Intégré dans triptych_autogluon_engine.py (axe temporel interne) ; reste nettoyage sous-module modifié et test de suppression.)
- **Principe** : Modèle fondation de séries temporelles haute précision (Google Research) pour prévisions multi-horizons internes.
- **Invariants** : Confiné au profil interne ; jamais émulé par extrapolation linéaire ; poids vérifiés avant inférence.
- **Interfaces** : google/timesfm-3.0-pytorch -> TriptychForecastReport (temporal_model='timesfm-3.0').
- **Perte au Retrait & Conflits** : Perte sans fusion : perte de la référence temporelle interne dual-jury. Conflit : profil commercial vs interne -> ADR-09. (*Arbitrage : ADR-09*)

### M013 — `elephant-goldfish-model` (GITLINK)
- **Provenance & Sources Brutes Lues** : chemin `01_Forkable/FKB00_Runtime/03_MasterSpec_CleanPlan/elephant-goldfish-model` | repo `https://github.com/Amdkn/elephant-goldfish-model.git` | SHA/pin `4f4a07625745` | licence `LICENSE fichier lu` | sources : `01_Forkable/FKB00_Runtime/00_A0_Core/elephant-goldfish-model.manifest.json`, `01_Forkable/FKB00_Runtime/00_A0_Core/elephant-goldfish-model-ADAPTATION.md`, `01_Forkable/FKB00_Runtime/03_MasterSpec_CleanPlan/elephant-goldfish-model/README.md`, `01_Forkable/FKB00_Runtime/03_MasterSpec_CleanPlan/elephant-goldfish-model/pyproject.toml`
- **Noyau Cible & Destination ÉNONCÉ §1(1)** : **ÂME · Organe K1 (Gouvernance & RSI)** · Destination : **`FUSIONNÉ`** · Statut Vérifié (§5.8) : **`PARTIEL`** (Modèle EGM implémenté dans a0_egm_bridge.py et aspace_freecloud_gateway.py (SQLite WAL egm_missions.db) ; reste test de suppression du gitlink.)
- **Principe** : Architecture Mémoire Éléphant (état macro SQLite WAL durable) × Exécution Poisson Rouge (fenêtre courte amnésique sans pollution de contexte).
- **Invariants** : Séparation stricte persistance macro vs contexte d'exécution éphémère ; chaque mission valide une commande déterministe.
- **Interfaces** : ElephantStateLedger (egm_missions.db) / goldfish_missions / a0_egm_bridge.py.
- **Perte au Retrait & Conflits** : Perte sans fusion : pollution et dégradation rapide des contextes longs. Conflit : contextes longs bruts vs fenêtres poisson rouge -> ADR-05. (*Arbitrage : ADR-05*)

### M014 — `gsd-core` (GITLINK)
- **Provenance & Sources Brutes Lues** : chemin `01_Forkable/FKB00_Runtime/03_MasterSpec_CleanPlan/gsd-core` | repo `https://github.com/Amdkn/gsd-core.git` | SHA/pin `adc42da74fb8` | licence `voir-source-brute` | sources : `01_Forkable/FKB00_Runtime/00_A0_Core/gsd-core.manifest.json`, `01_Forkable/FKB00_Runtime/00_A0_Core/gsd-core-ADAPTATION.md`
- **Noyau Cible & Destination ÉNONCÉ §1(1)** : **ÂME · Organe K1 (Gouvernance & RSI)** · Destination : **`FUSIONNÉ`** · Statut Vérifié (§5.8) : **`PARTIEL`** (Adapté état 1 (`adc42da`) ; reste extraction de sa machine d'état/beads dans K1 et archivage du gitlink (et purge dossier résiduel get-shit-done).)
- **Principe** : Protocole d'exécution déterministe piloté par specs vérifiables et unités atomiques (beads) sans dérive d'étape.
- **Invariants** : Aucune exécution sans spec bornée ; validation d'étape avant transition.
- **Interfaces** : Workflows GSD / check-gates / beads specs.
- **Perte au Retrait & Conflits** : Perte sans fusion : perte de la discipline de découpage atomique des livrables. Conflit : doublon historique get-shit-done -> ADR-11. (*Arbitrage : ADR-11*)

### M015 — `gstack` (GITLINK)
- **Provenance & Sources Brutes Lues** : chemin `01_Forkable/FKB00_Runtime/03_MasterSpec_CleanPlan/gstack` | repo `https://github.com/Amdkn/gstack.git` | SHA/pin `6cb6da784bba` | licence `MIT` | sources : `01_Forkable/FKB00_Runtime/00_A0_Core/gstack.manifest.json`, `01_Forkable/FKB00_Runtime/00_A0_Core/gstack-ADAPTATION.md`, `01_Forkable/FKB00_Runtime/03_MasterSpec_CleanPlan/gstack/README.md`, `01_Forkable/FKB00_Runtime/03_MasterSpec_CleanPlan/gstack/package.json`
- **Noyau Cible & Destination ÉNONCÉ §1(1)** : **ÂME · Organe K1 (Gouvernance & RSI)** · Destination : **`FUSIONNÉ`** · Statut Vérifié (§5.8) : **`PARTIEL`** (Adapté état 1 (`6cb6da7`) ; reste extraction de ses rôles de revue (CEO/Eng/QA) dans les templates K1 et retrait gitlink.)
- **Principe** : Équipe d'ingénierie virtuelle structurée par rôles critiques (rethink CEO, plan eng, QA navigateur rapide, revue de diff).
- **Invariants** : Séparation stricte entre le rôle qui conçoit, celui qui code et celui qui QA.
- **Interfaces** : Skills gstack (CEO/Eng/QA/Ship) + browser QA.
- **Perte au Retrait & Conflits** : Perte sans fusion : perte des grilles de revue produit/ingénierie multi-casquettes. Conflit : chevauchement partiel avec superpowers -> ADR-06. (*Arbitrage : ADR-06*)

### M016 — `superpowers` (GITLINK)
- **Provenance & Sources Brutes Lues** : chemin `01_Forkable/FKB00_Runtime/03_MasterSpec_CleanPlan/superpowers` | repo `https://github.com/Amdkn/superpowers.git` | SHA/pin `5813de0eba84` | licence `LICENSE fichier lu` | sources : `01_Forkable/FKB00_Runtime/00_A0_Core/superpowers.manifest.json`, `01_Forkable/FKB00_Runtime/00_A0_Core/superpowers-ADAPTATION.md`, `01_Forkable/FKB00_Runtime/03_MasterSpec_CleanPlan/superpowers/README.md`, `01_Forkable/FKB00_Runtime/03_MasterSpec_CleanPlan/superpowers/package.json`
- **Noyau Cible & Destination ÉNONCÉ §1(1)** : **ÂME · Organe K1 (Gouvernance & RSI)** · Destination : **`FUSIONNÉ`** · Statut Vérifié (§5.8) : **`PARTIEL`** (Adapté état 1 (`5813de0`, 139/139 tests verts) ; reste unification des skills TDD/debugging dans K4/K1 et retrait gitlink.)
- **Principe** : Méthodologie d'ingénierie chirurgicale par skills composables : TDD strict, débogage par cause racine, revue systématique avant merge.
- **Invariants** : Test rouge avant implémentation ; interdiction d'affirmer un succès sans re-vérification complète après la dernière édition.
- **Interfaces** : Skills TDD / Systematic-Debugging / Verification-Before-Completion.
- **Perte au Retrait & Conflits** : Perte sans fusion : perte de la rigueur TDD et anti-régression au niveau des prompts d'exécution. Conflit : harmonisation catalogue skills -> ADR-10. (*Arbitrage : ADR-10*)

### M017 — `claude-code` (GITLINK)
- **Provenance & Sources Brutes Lues** : chemin `01_Forkable/FKB00_Runtime/04_ADE_OpenRig/claude-code` | repo `https://github.com/Amdkn/claude-code.git` | SHA/pin `0ed94698aa0a` | licence `voir-source-brute` | sources : `01_Forkable/FKB00_Runtime/00_A0_Core/claude-code.manifest.json`, `01_Forkable/FKB00_Runtime/00_A0_Core/claude-code-ADAPTATION.md`
- **Noyau Cible & Destination ÉNONCÉ §1(1)** : **CORPS · Organe K2 (Exécution, Anything & 3D)** · Destination : **`RETENU`** · Statut Vérifié (§5.8) : **`RETENU`** (RETENU (Justification de fondation : binaire/harness CLI tiers sans licence amont D12 — exécuté comme worker externe par K2 via contrat OpenRig/Herdr, zéro copie de code).)
- **Principe** : Harnais CLI agentique orienté architecture et édition de code multi-fichiers avec permissions configurables et MCP.
- **Invariants** : Règle D12 Clean-Room (zéro copie de code sans licence) ; pilotage exclusif par contrat externe (hooks `.claude/settings.json`, bypass sécurisé, route `:31415`).
- **Interfaces** : CLI `claude --dangerously-skip-permissions` + `.claude/agents/*.md` + `.mcp.json`.
- **Perte au Retrait & Conflits** : Perte si écarté : perte d'un des exécuteurs CLI principaux orchestrés par K2. Conflit : absence de licence amont -> ADR-09, ADR-10. (*Arbitrage : ADR-09, ADR-10*)

### M018 — `codex` (GITLINK)
- **Provenance & Sources Brutes Lues** : chemin `01_Forkable/FKB00_Runtime/04_ADE_OpenRig/codex` | repo `https://github.com/Amdkn/codex.git` | SHA/pin `27fcd7cbedd7` | licence `voir-source-brute` | sources : `01_Forkable/FKB00_Runtime/00_A0_Core/codex.manifest.json`, `01_Forkable/FKB00_Runtime/00_A0_Core/codex-ADAPTATION.md`
- **Noyau Cible & Destination ÉNONCÉ §1(1)** : **CORPS · Organe K2 (Exécution, Anything & 3D)** · Destination : **`RETENU`** · Statut Vérifié (§5.8) : **`RETENU`** (RETENU (Justification de fondation : harnais CLI externe Apache-2.0 — exécuté comme worker d'exécution massive par K2 via OpenRig/Herdr et pont web zéro-télémétrie).)
- **Principe** : Harnais CLI agentique dédié à l'exécution rapide et aux revues batch en sandbox.
- **Invariants** : Exécution sans télémétrie via `codex-chatgpt-web` et gateway `:31415` ; isolation par worktree (`writerLock`).
- **Interfaces** : CLI `codex --no-daemon --dangerously-bypass-approvals-and-sandbox` + `~/.codex/config.toml`.
- **Perte au Retrait & Conflits** : Perte si écarté : perte du worker CLI parallèle spécialisé exécution/review. Conflit : télémétrie & quotas API -> ADR-08, ADR-10. (*Arbitrage : ADR-08, ADR-10*)

### M019 — `herdr` (GITLINK)
- **Provenance & Sources Brutes Lues** : chemin `01_Forkable/FKB00_Runtime/04_ADE_OpenRig/herdr` | repo `https://github.com/Amdkn/herdr.git` | SHA/pin `2387c8abbd22` | licence `voir-source-brute` | sources : `01_Forkable/FKB00_Runtime/00_A0_Core/herdr.manifest.json`, `01_Forkable/FKB00_Runtime/00_A0_Core/herdr-ADAPTATION.md`
- **Noyau Cible & Destination ÉNONCÉ §1(1)** : **CORPS · Organe K2 (Exécution, Anything & 3D)** · Destination : **`FUSIONNÉ`** · Statut Vérifié (§5.8) : **`PARTIEL`** (Adapté état 1 (`2387c8a`, contrat CLI seul) ; reste absorption définitive de ses templates de session dans RigInfinity et retrait du gitlink.)
- **Principe** : Cockpit CLI de gestion des workspaces et templates de sessions terminales (`worker`, `reviewer`).
- **Invariants** : Zéro connexion réseau externe (strace 0 socket) ; notes/version_check désactivés.
- **Interfaces** : Templates `~/.config/herdr-core/config.toml` / contrat CLI `hc`.
- **Perte au Retrait & Conflits** : Perte sans fusion : perte des gabarits de sessions de développement persistantes. Conflit : daemon herdr vs RigInfinity -> ADR-02, ADR-08. (*Arbitrage : ADR-02, ADR-08*)

### M020 — `herdr-app` (GITLINK)
- **Provenance & Sources Brutes Lues** : chemin `01_Forkable/FKB00_Runtime/04_ADE_OpenRig/herdr-app` | repo `https://github.com/Amdkn/herdr-app.git` | SHA/pin `b1a2a67efb9d` | licence `voir-source-brute` | sources : `01_Forkable/FKB00_Runtime/00_A0_Core/herdr-app.manifest.json`, `01_Forkable/FKB00_Runtime/00_A0_Core/herdr-app-ADAPTATION.md`
- **Noyau Cible & Destination ÉNONCÉ §1(1)** : **CORPS · Organe K2 (Exécution, Anything & 3D)** · Destination : **`RETENU`** · Statut Vérifié (§5.8) : **`RETENU`** (RETENU (Justification de fondation : application desktop GPU GPUI compilée — surface visuelle cockpit hébergeant les 7 programmes et tabs d'agents, non remplaçable par du code serveur).)
- **Principe** : Interface graphique desktop GPU (GPUI) orchestrant espaces, onglets, panneaux et boutons de lancement multi-harnesses.
- **Invariants** : Zéro télémétrie ; fichier `~/.config/herdr-app/programs.json` auto-réparé par `.vscode/doctor.ps1`.
- **Interfaces** : GUI desktop `herdr-app.exe` + `~/.config/herdr-app/programs.json`.
- **Perte au Retrait & Conflits** : Perte si écarté : perte de l'interface cockpit native multi-terminaux sur Windows. Conflit : aucun (surface client pure de K2) -> ADR-02. (*Arbitrage : ADR-02*)

### M021 — `openclaw` (GITLINK)
- **Provenance & Sources Brutes Lues** : chemin `01_Forkable/FKB00_Runtime/04_ADE_OpenRig/openclaw` | repo `https://github.com/Amdkn/openclaw.git` | SHA/pin `ce7788f5a24e` | licence `voir-source-brute` | sources : `01_Forkable/FKB00_Runtime/00_A0_Core/openclaw.manifest.json`, `01_Forkable/FKB00_Runtime/00_A0_Core/openclaw-ADAPTATION.md`
- **Noyau Cible & Destination ÉNONCÉ §1(1)** : **CORPS · Organe K2 (Exécution, Anything & 3D)** · Destination : **`FUSIONNÉ`** · Statut Vérifié (§5.8) : **`PARTIEL`** (Adapté état 2 (`ce7788f`) ; reste migration complète de sa politique gateway/canaux vers RigInfinity et retrait du gitlink.)
- **Principe** : Séparation stricte Gateway de confiance / Exécution non fiable + politique de permissions en code + HEARTBEAT.md comme organe de présence.
- **Invariants** : Jamais d'exécution sans vérification de politique ; heartbeat à checklist (jamais de sondage aveugle) ; zéro téléphonie maison non opt-in.
- **Interfaces** : Gateway multicanal (20+ plateformes) / HEARTBEAT.md / policy-in-code.
- **Perte au Retrait & Conflits** : Perte sans fusion : perte du modèle de sécurité Gateway vs Execution non fiable. Conflit : daemon concurrent à RigInfinity -> ADR-02, ADR-08. (*Arbitrage : ADR-02, ADR-08*)

### M022 — `orca` (GITLINK)
- **Provenance & Sources Brutes Lues** : chemin `01_Forkable/FKB00_Runtime/04_ADE_OpenRig/orca` | repo `https://github.com/Amdkn/orca.git` | SHA/pin `5d154641332a` | licence `voir-source-brute` | sources : `01_Forkable/FKB00_Runtime/00_A0_Core/orca.manifest.json`, `01_Forkable/FKB00_Runtime/00_A0_Core/orca-ADAPTATION.md`
- **Noyau Cible & Destination ÉNONCÉ §1(1)** : **CORPS · Organe K2 (Exécution, Anything & 3D)** · Destination : **`FUSIONNÉ`** · Statut Vérifié (§5.8) : **`PARTIEL`** (Adapté état 1 (`5d15464`, MIT, CLI-contrat + 11 skills) ; reste unification des primitives worktree/DAG/computer-use avec source-control-natif/agent-desktop et retrait gitlink.)
- **Principe** : Isolation systématique par worktree Git, orchestration DAG multi-agents supervisée (ask/reply/heartbeat) et contrôle GUI par arbre d'accessibilité.
- **Invariants** : `ORCA_TELEMETRY_DISABLED=1`, `DO_NOT_TRACK=1`, auto-update coupée ; jamais de serveur concurrent sur `:31415`.
- **Interfaces** : orca worktree | orchestration | computer / skills orca-*.
- **Perte au Retrait & Conflits** : Perte sans fusion : perte de l'isolation de worktrees Git et du protocole DAG supervisé. Conflit : daemon Orca vs RigInfinity / Scion sparse -> ADR-02, ADR-05. (*Arbitrage : ADR-02, ADR-05*)

### M023 — `t3code` (GITLINK)
- **Provenance & Sources Brutes Lues** : chemin `01_Forkable/FKB00_Runtime/04_ADE_OpenRig/t3code` | repo `https://github.com/Amdkn/t3code.git` | SHA/pin `dc7270581800` | licence `voir-source-brute` | sources : `01_Forkable/FKB00_Runtime/00_A0_Core/t3code.manifest.json`, `01_Forkable/FKB00_Runtime/00_A0_Core/t3code-ADAPTATION.md`
- **Noyau Cible & Destination ÉNONCÉ §1(1)** : **CORPS · Organe K2 (Exécution, Anything & 3D)** · Destination : **`FUSIONNÉ`** · Statut Vérifié (§5.8) : **`PARTIEL`** (Adapté état 2 (`dc72705`, MIT) ; reste intégration de sa revue de diffs dans la surface K2/3D et retrait du gitlink.)
- **Principe** : Interface légère multi-modèles centrée sur l'inspection visuelle des diffs et la validation humaine des patchs.
- **Invariants** : Zéro télémétrie ; consommation exclusive des diffs émis par K2.
- **Interfaces** : UI web/desktop de revue de diffs / adaptateur t3code.
- **Perte au Retrait & Conflits** : Perte sans fusion : perte du patron UX léger de revue de diffs multi-modèles. Conflit : surface parallèle -> ADR-02. (*Arbitrage : ADR-02*)

### M024 — `adk-recipes` (GITLINK)
- **Provenance & Sources Brutes Lues** : chemin `01_Forkable/FKB00_Runtime/05_Recursive_RSI/adk-recipes` | repo `https://github.com/Amdkn/adk-recipes.git` | SHA/pin `f14f79fadbd5` | licence `voir-source-brute` | sources : `01_Forkable/FKB00_Runtime/00_A0_Core/adk-recipes.manifest.json`, `01_Forkable/FKB00_Runtime/00_A0_Core/adk-recipes-ADAPTATION.md`
- **Noyau Cible & Destination ÉNONCÉ §1(1)** : **ÂME · Organe K1 (Gouvernance & RSI)** · Destination : **`FUSIONNÉ`** · Statut Vérifié (§5.8) : **`PARTIEL`** (Adapté état 2 (`f14f79f` / `a93b9cc`, Apache-2.0) ; principe AQuA partiellement porté dans `aspace-aqua-adapter` et `a0_recursive_factory.py` ; reste test de suppression et retrait gitlink.)
- **Principe** : Ambient Quality Agent (AQuA) : observateur qualité passif analysant les traces d'exécution en arrière-plan pour détecter les régressions et dérives.
- **Invariants** : Exécution ambiante en lecture seule sur les journaux ; aucune mutation directe sans passage par la porte de validation.
- **Interfaces** : aspace-aqua-adapter/src/aqua_factory_reader.py / aspace-wikiskill-gate/src/aqua_gate.py.
- **Perte au Retrait & Conflits** : Perte sans fusion : perte du diagnostic qualité ambiant continu (Horizon 2 RSI). Conflit : auto-mutation non contrôlée -> ADR-06. (*Arbitrage : ADR-06*)

### M025 — `dream-rsi` (GITLINK)
- **Provenance & Sources Brutes Lues** : chemin `01_Forkable/FKB00_Runtime/05_Recursive_RSI/dream-rsi` | repo `https://github.com/Amdkn/dream-rsi.git` | SHA/pin `fa0c8f085955` | licence `Apache-2.0` | sources : `01_Forkable/FKB00_Runtime/00_A0_Core/dream-rsi.manifest.json`, `01_Forkable/FKB00_Runtime/00_A0_Core/dream-rsi-ADAPTATION.md`, `01_Forkable/MODULES-LOCK.json`
- **Noyau Cible & Destination ÉNONCÉ §1(1)** : **ÂME · Organe K1 (Gouvernance & RSI)** · Destination : **`FUSIONNÉ`** · Statut Vérifié (§5.8) : **`PARTIEL`** (Adapté état 2 (`fa0c8f0` / `8ec35bd`, Apache-2.0) ; principe porté dans `aspace-dream-daemon` & `aspace-dream-loop` ; reste validation finale sur K1 et retrait gitlink.)
- **Principe** : Auto-amélioration récursive hors-ligne à coût nul (Dream-RSI) : exploration d'arbre (règle beta) et replay de trajectoires passées pendant les phases d'inactivité.
- **Invariants** : Zéro appel API payant durant la phase Dream ; validation sur hold-out avant promotion d'une variante.
- **Interfaces** : aspace-dream-daemon/src/dream_daemon.py / aspace-dream-loop/src/dream_loop.py.
- **Perte au Retrait & Conflits** : Perte sans fusion : perte de la consolidation nocturne/hors-ligne par replay à coût nul. Conflit : mutations sans hold-out -> ADR-06. (*Arbitrage : ADR-06*)

### M026 — `rrsi` (GITLINK)
- **Provenance & Sources Brutes Lues** : chemin `01_Forkable/FKB00_Runtime/05_Recursive_RSI/rrsi` | repo `https://github.com/Amdkn/rrsi.git` | SHA/pin `cc424ccde51d` | licence `voir-source-brute` | sources : `01_Forkable/FKB00_Runtime/00_A0_Core/rrsi.manifest.json`, `01_Forkable/FKB00_Runtime/00_A0_Core/rrsi-ADAPTATION.md`
- **Noyau Cible & Destination ÉNONCÉ §1(1)** : **ÂME · Organe K1 (Gouvernance & RSI)** · Destination : **`FUSIONNÉ`** · Statut Vérifié (§5.8) : **`PARTIEL`** (Adapté état 2 (`cc424cc` / `be50316`, Apache-2.0) ; logique d'évolution sur worktrees décrite dans `a0_recursive_factory.py` ; reste test de suppression et retrait gitlink.)
- **Principe** : Recursive Self-Improvement (RRSI) par évolution contrôlée sur branches/worktrees Git isolés avec évaluation comparative.
- **Invariants** : Toute mutation évolutive opère sur branche/worktree jetable, jamais en direct sur master ou FKB00 ; promotion soumise au Juge externe.
- **Interfaces** : Evolution worktree loop (Horizon 3 RSI) dans a0_recursive_factory.py.
- **Perte au Retrait & Conflits** : Perte sans fusion : perte du mécanisme d'auto-évolution architecturale à long terme. Conflit : risque de dérive non bornée du noyau -> ADR-06. (*Arbitrage : ADR-06*)

### M027 — `wikiskill` (GITLINK)
- **Provenance & Sources Brutes Lues** : chemin `01_Forkable/FKB00_Runtime/05_Recursive_RSI/wikiskill` | repo `https://github.com/Amdkn/wikiskill.git` | SHA/pin `59a6a041ba22` | licence `MIT` | sources : `01_Forkable/FKB00_Runtime/00_A0_Core/wikiskill.manifest.json`, `01_Forkable/FKB00_Runtime/00_A0_Core/wikiskill-ADAPTATION.md`, `01_Forkable/MODULES-LOCK.json`
- **Noyau Cible & Destination ÉNONCÉ §1(1)** : **ÂME · Organe K1 (Gouvernance & RSI)** · Destination : **`FUSIONNÉ`** · Statut Vérifié (§5.8) : **`PARTIEL`** (Adapté état 2 (`59a6a04` / `cdc291c`, MIT) ; porte `aspace-wikiskill-gate` implémentée ; reste branchement complet sur K4 et retrait gitlink.)
- **Principe** : Compilation de playbooks et skills en 4 rôles séparés (Worker -> Note-Taker -> Playbook Writer -> Strict Manager) validée par Holdout Set (seuil δ ≥ 1.7 %).
- **Invariants** : Séparation stricte des 4 rôles ; aucune règle promue si le gain sur l'ensemble de validation (hold-out) est inférieur au seuil de bruit δ=0.017.
- **Interfaces** : aspace-wikiskill-gate/src/gate_runner.py & bench_backend.py.
- **Perte au Retrait & Conflits** : Perte sans fusion : perte du filtre anti-bruit statistique sur la création de skills. Conflit : écriture directe de skills sans hold-out -> ADR-06. (*Arbitrage : ADR-06*)

### M028 — `GLiNER2.5-multi-Decide` (GITLINK)
- **Provenance & Sources Brutes Lues** : chemin `01_Forkable/FKB01_Inference/01_Inference_Locale/GLiNER2.5-multi-Decide` | repo `https://github.com/Amdkn/GLiNER2.5-multi-Decide.git` | SHA/pin `9bd91c72a782` | licence `voir-source-brute` | sources : `01_Forkable/FKB01_Inference/01_Inference_Locale/GLiNER2.5-multi-Decide/README.md`
- **Noyau Cible & Destination ÉNONCÉ §1(1)** : **SYSTÈME NERVEUX · Organe K3 (Inférence & FreeCloud)** · Destination : **`RETENU`** · Statut Vérifié (§5.8) : **`RETENU`** (RETENU (Justification de fondation : modèle neuronal 287M paramètres mDeBERTa-v3-base et poids sur HuggingFace Amdkn7/GLiNER2.5-multi-Decide — actif binaire local indispensable au premier étage System-1).)
- **Principe** : Barrière d'entrée cognitive multilingue System-1 (< 10ms CPU/GPU) : extraction d'entités et classification multi-labels dynamique zéro-hallucination.
- **Invariants** : Zéro génération de prose libre ; évaluation purement discriminative ; bilinguisme natif FR/EN.
- **Interfaces** : Modèle HuggingFace Amdkn7/GLiNER2.5-multi-Decide -> labels d'intention, langue et priorité typés.
- **Perte au Retrait & Conflits** : Perte si écarté : impossibilité de classifier/filtrer le signal entrant en <10ms hors ligne. Conflit : appel LLM System-2 pour du simple routage -> ADR-03. (*Arbitrage : ADR-03*)

### M029 — `LFM3-Omni-2B` (GITLINK)
- **Provenance & Sources Brutes Lues** : chemin `01_Forkable/FKB01_Inference/01_Inference_Locale/LFM3-Omni-2B` | repo `https://github.com/Amdkn/LFM3-Omni-2B.git` | SHA/pin `a85707105b1b` | licence `LICENSE fichier lu` | sources : `01_Forkable/FKB01_Inference/01_Inference_Locale/LFM3-Omni-2B/README.md`
- **Noyau Cible & Destination ÉNONCÉ §1(1)** : **SYSTÈME NERVEUX · Organe K3 (Inférence & FreeCloud)** · Destination : **`RETENU`** · Statut Vérifié (§5.8) : **`RETENU`** (RETENU (Justification de fondation : modèle multimodal 2B paramètres et poids locaux souverains sur 127.0.0.1:9931 — actif neuronal local non absorbable en pur code).)
- **Principe** : Backbone multimodal local (2B paramètres, texte + audio discret) servant de cerveau local souverain pour A0 sans dépendance cloud.
- **Invariants** : Poids gelés et adaptés uniquement par LoRA ; servi exclusivement en loopback (`127.0.0.1:9931`).
- **Interfaces** : Endpoint OpenAI-compatible `http://127.0.0.1:9931/v1/chat/completions`.
- **Perte au Retrait & Conflits** : Perte si écarté : perte de l'autonomie d'inférence multimodale locale hors-ligne. Conflit : dépendance API cloud -> ADR-08. (*Arbitrage : ADR-08*)

### M030 — `LoRA` (GITLINK)
- **Provenance & Sources Brutes Lues** : chemin `01_Forkable/FKB01_Inference/01_Inference_Locale/LoRA` | repo `https://github.com/Amdkn/LoRA.git` | SHA/pin `c70de242aeea` | licence `LICENSE fichier lu` | sources : `01_Forkable/FKB01_Inference/01_Inference_Locale/LoRA/README.md`
- **Noyau Cible & Destination ÉNONCÉ §1(1)** : **SYSTÈME NERVEUX · Organe K3 (Inférence & FreeCloud)** · Destination : **`FUSIONNÉ`** · Statut Vérifié (§5.8) : **`PARTIEL`** (Spécifié dans `mimi-lora-lfm3-omni.md` et `principes-fusion-runtime.md` §6.2 ; reste intégration du chargeur d'adaptateurs PEFT dans K3 et retrait gitlink.)
- **Principe** : Adaptation par matrices de décomposition bas-rang (Low-Rank Adaptation) permettant de spécialiser voix, style et outils métier sans réentraîner les poids gelés.
- **Invariants** : Les poids de base restent immuables ; l'identité et les domaines métier vivent dans des adaptateurs versionnés légers.
- **Interfaces** : loralib / connecteurs audio Mimi->LFM3 & adaptateurs Needle.
- **Perte au Retrait & Conflits** : Perte sans fusion : coût GPU prohibitif si réentraînement complet requis. Conflit : aucun -> ADR-03. (*Arbitrage : ADR-03*)

### M031 — `mimi` (GITLINK)
- **Provenance & Sources Brutes Lues** : chemin `01_Forkable/FKB01_Inference/01_Inference_Locale/mimi` | repo `https://github.com/Amdkn/mimi.git` | SHA/pin `ca3e804510f8` | licence `voir-source-brute` | sources : `01_Forkable/FKB01_Inference/01_Inference_Locale/mimi/README.md`
- **Noyau Cible & Destination ÉNONCÉ §1(1)** : **SYSTÈME NERVEUX · Organe K3 (Inférence & FreeCloud)** · Destination : **`RETENU`** · Statut Vérifié (§5.8) : **`RETENU`** (RETENU (Justification de fondation : codec audio neuronal Kyutai 24kHz -> 12.5Hz/1.1kbps et poids Amdkn7/mimi — actif codec binaire local).)
- **Principe** : Discrétisation neuronale de l'audio temps réel en tokens discrets compacts (12.5 Hz / 1.1 kbps) évitant de saturer la fenêtre de contexte par des ondes brutes.
- **Invariants** : Traitement 100 % local ; flux discret compatible avec l'attention multimodale LFM3.
- **Interfaces** : Encodeur/décodeur streaming 24 kHz (`rustymimi` / Transformers).
- **Perte au Retrait & Conflits** : Perte si écarté : impossibilité de tokeniser efficacement la voix en local. Conflit : aucun -> ADR-03. (*Arbitrage : ADR-03*)

### M032 — `moshi` (GITLINK)
- **Provenance & Sources Brutes Lues** : chemin `01_Forkable/FKB01_Inference/01_Inference_Locale/moshi` | repo `https://github.com/Amdkn/moshi.git` | SHA/pin `36ac6ea8b494` | licence `LICENSE fichier lu` | sources : `01_Forkable/FKB01_Inference/01_Inference_Locale/moshi/README.md`
- **Noyau Cible & Destination ÉNONCÉ §1(1)** : **SYSTÈME NERVEUX · Organe K3 (Inférence & FreeCloud)** · Destination : **`RETENU`** · Statut Vérifié (§5.8) : **`RETENU`** (RETENU (Justification de fondation : moteur de dialogue vocal full-duplex temps réel et poids Kyutai — runtime audio binaire dédié).)
- **Principe** : Dialogue vocal temps réel full-duplex à latence sub-seconde avec modélisation conjointe parole/texte.
- **Invariants** : Zéro envoi audio vers des tiers sans consentement ; intégration loopback locale.
- **Interfaces** : Serveur/client audio Kyutai Moshi + `rustymimi`.
- **Perte au Retrait & Conflits** : Perte si écarté : perte de la capacité de conversation vocale full-duplex souveraine. Conflit : aucun -> ADR-03. (*Arbitrage : ADR-03*)

### M033 — `needle` (GITLINK)
- **Provenance & Sources Brutes Lues** : chemin `01_Forkable/FKB01_Inference/01_Inference_Locale/needle` | repo `https://github.com/Amdkn/needle.git` | SHA/pin `978471feea22` | licence `LICENSE fichier lu` | sources : `01_Forkable/FKB01_Inference/01_Inference_Locale/needle/README.md`, `01_Forkable/FKB01_Inference/01_Inference_Locale/needle/pyproject.toml`
- **Noyau Cible & Destination ÉNONCÉ §1(1)** : **SYSTÈME NERVEUX · Organe K3 (Inférence & FreeCloud)** · Destination : **`RETENU`** · Statut Vérifié (§5.8) : **`RETENU`** (RETENU (Justification de fondation : modèle edge Cactus Needle 8-29 Mo quantifié 2-bit et ASR Whistle, poids Amdkn7/needle3 — exécutable edge binaire).)
- **Principe** : Tool-calling déterministe contraint par grammaire (8-29 Mo 2-bit) mappant texte/voix vers des appels JSON `function_calls` typés avec confiance calibrée.
- **Invariants** : Zéro hallucination syntaxique (grammaire contrainte) ; exécution 100 % edge sans GPU massif.
- **Interfaces** : Cactus Needle + ASR Whistle -> JSON `function_calls` + score de confiance.
- **Perte au Retrait & Conflits** : Perte si écarté : perte du routage d'outils edge rapide en millisecondes. Conflit : génération LLM libre d'appels d'outils -> ADR-03. (*Arbitrage : ADR-03*)

### M034 — `DeepInfer` (GITLINK)
- **Provenance & Sources Brutes Lues** : chemin `01_Forkable/FKB01_Inference/02_Inference_Cooperative/DeepInfer` | repo `https://github.com/Amdkn/DeepInfer.git` | SHA/pin `14267cd7243f` | licence `LICENSE fichier lu` | sources : `01_Forkable/FKB01_Inference/02_Inference_Cooperative/DeepInfer/README.md`, `01_Forkable/FKB01_Inference/02_Inference_Cooperative/DeepInfer/pyproject.toml`
- **Noyau Cible & Destination ÉNONCÉ §1(1)** : **SYSTÈME NERVEUX · Organe K3 (Inférence & FreeCloud)** · Destination : **`RETENU`** · Statut Vérifié (§5.8) : **`RETENU`** (RETENU (Justification de fondation : moteur d'inférence C++/CUDA bas niveau avec noyaux FP8 et KV-cache paginé — moteur système natif compilé).)
- **Principe** : Optimisation matérielle de l'inférence LLM par micro-kernels C++/CUDA (FP8/INT4, PagedAttention, MLA, décodage spéculatif).
- **Invariants** : Allocateurs mémoire bornés ; zéro fuite réseau ; exposition OpenAI/gRPC locale.
- **Interfaces** : Bindings FFI Rust/C++ / moteur local DeepInfer.
- **Perte au Retrait & Conflits** : Perte si écarté : perte d'accélération matérielle bas niveau sur GPU local/VPS. Conflit : aucun. (*Arbitrage : ADR-08*)

### M035 — `cross-platform-llm-client` (GITLINK)
- **Provenance & Sources Brutes Lues** : chemin `01_Forkable/FKB01_Inference/02_Inference_Cooperative/cross-platform-llm-client` | repo `https://github.com/Amdkn/cross-platform-llm-client.git` | SHA/pin `232e6d5057b6` | licence `LICENSE fichier lu` | sources : `01_Forkable/FKB01_Inference/02_Inference_Cooperative/cross-platform-llm-client/README.md`
- **Noyau Cible & Destination ÉNONCÉ §1(1)** : **SYSTÈME NERVEUX · Organe K3 (Inférence & FreeCloud)** · Destination : **`FUSIONNÉ`** · Statut Vérifié (§5.8) : **`PARTIEL`** (Spécifié dans `02_Inference_Cooperative/index.md` ; reste unification dans la surface client K2/K3 et retrait du gitlink.)
- **Principe** : Surface client omnicanale (Desktop/Mobile/Web) unifiant inférence locale et endpoints distants OpenAI-compatibles via streaming SSE.
- **Invariants** : Stockage local chiffré des historiques ; connexion exclusive aux gateways souverains (`:8080` / `:31415`).
- **Interfaces** : Client SSE vers `http://localhost:8080/v1/chat/completions`.
- **Perte au Retrait & Conflits** : Perte sans fusion : perte du patron client mobile/desktop multi-endpoints. Conflit : surfaces UI multiples -> ADR-02. (*Arbitrage : ADR-02*)

### M036 — `mesh-llm` (GITLINK)
- **Provenance & Sources Brutes Lues** : chemin `01_Forkable/FKB01_Inference/02_Inference_Cooperative/mesh-llm` | repo `https://github.com/Amdkn/mesh-llm.git` | SHA/pin `d6031cb0dc41` | licence `LICENSE fichier lu` | sources : `01_Forkable/FKB01_Inference/02_Inference_Cooperative/mesh-llm/README.md`, `01_Forkable/FKB01_Inference/02_Inference_Cooperative/mesh-llm/Cargo.toml`
- **Noyau Cible & Destination ÉNONCÉ §1(1)** : **SYSTÈME NERVEUX · Organe K3 (Inférence & FreeCloud)** · Destination : **`FUSIONNÉ`** · Statut Vérifié (§5.8) : **`PARTIEL`** (Spécifié dans `02_Inference_Cooperative/index.md` ; reste intégration du routeur Pipeline Parallelism P2P dans K3 et retrait du gitlink.)
- **Principe** : Agrégation de mémoire VRAM/RAM hétérogène sur réseau local/VPS par Pipeline Parallelism (partitionnement par couches + libp2p/mDNS) plutôt que Tensor Parallelism.
- **Invariants** : Seules les activations de couche charnière transitent sur le réseau (viable sur Wi-Fi/Ethernet 1Gbps) ; tolérance au départ d'un nœud.
- **Interfaces** : Routeur mDNS/libp2p -> gRPC activations inter-nœuds -> gateway OpenAI `:8080`.
- **Perte au Retrait & Conflits** : Perte sans fusion : impossibilité d'exécuter de grands modèles distribués sur parc hétérogène sans NVLink. Conflit : aucun -> ADR-08. (*Arbitrage : ADR-08*)

### M037 — `FreeVPS` (GITLINK)
- **Provenance & Sources Brutes Lues** : chemin `01_Forkable/FKB01_Inference/03_Inference_FreeCloud/FreeVPS` | repo `https://github.com/Amdkn/FreeVPS.git` | SHA/pin `7f6b1dc14291` | licence `LICENSE fichier lu` | sources : `01_Forkable/FKB01_Inference/03_Inference_FreeCloud/FreeVPS/README.md`
- **Noyau Cible & Destination ÉNONCÉ §1(1)** : **SYSTÈME NERVEUX · Organe K3 (Inférence & FreeCloud)** · Destination : **`ÉCARTÉ`** · Statut Vérifié (§5.8) : **`ÉCARTÉ`** (ÉCARTÉ (Raison vérifiée : dépend d'abus de runners GitHub Actions éphémères pour du calcul continu — incompatible avec la règle d'hygiène CGU, la sécurité GitHub et le contrat de stabilité V5).)
- **Principe** : Provisionnement de machines virtuelles gratuites temporaires sur GitHub Actions.
- **Invariants** : Violation potentielle des CGU GitHub Actions et instabilité temporelle (sessions éphémères non durables).
- **Interfaces** : Workflows GitHub Actions VM.
- **Perte au Retrait & Conflits** : Perte à l'écartement : nulle (remplacé avantageusement par le maillage local mesh-llm, FreeLLMAPI et VPS souverains réels). Conflit : sécurité/CGU -> ADR-08. (*Arbitrage : ADR-08*)

### M038 — `bifrost` (GITLINK)
- **Provenance & Sources Brutes Lues** : chemin `01_Forkable/FKB01_Inference/03_Inference_FreeCloud/bifrost` | repo `https://github.com/Amdkn/bifrost.git` | SHA/pin `19c7af62cc7c` | licence `LICENSE fichier lu` | sources : `01_Forkable/FKB01_Inference/03_Inference_FreeCloud/bifrost/README.md`
- **Noyau Cible & Destination ÉNONCÉ §1(1)** : **SYSTÈME NERVEUX · Organe K3 (Inférence & FreeCloud)** · Destination : **`FUSIONNÉ`** · Statut Vérifié (§5.8) : **`PARTIEL`** (Intégré localement (commit `19c7af6`, catalogue modèles + règles de routage vérifiées) ; reste fusion des règles de routage multi-providers avec freellmapi/gateway `:31415` et test de suppression.)
- **Principe** : Passerelle AI haute performance unifiant routage multi-providers, règles de gouvernance, catalogue de modèles et compatibilité Anthropic/OpenAI.
- **Invariants** : Zéro fuite SQLite/dlock (TTL corrigé) ; conformité `/v1/models`, `/v1/chat/completions`, `/anthropic/v1/messages`.
- **Interfaces** : HTTP `/health`, `/api/providers`, `/api/governance/routing-rules`, `/v1/chat/completions`.
- **Perte au Retrait & Conflits** : Perte sans fusion : perte des primitives de gouvernance de routage haute performance et traduction OpenAI<->Anthropic. Conflit : chevauchement port avec freellmapi -> ADR-08. (*Arbitrage : ADR-08*)

### M039 — `codex-chatgpt-web` (GITLINK)
- **Provenance & Sources Brutes Lues** : chemin `01_Forkable/FKB01_Inference/03_Inference_FreeCloud/codex-chatgpt-web` | repo `https://github.com/Amdkn/codex-chatgpt-web.git` | SHA/pin `48f014e46b37` | licence `MIT` | sources : `01_Forkable/FKB01_Inference/03_Inference_FreeCloud/codex-chatgpt-web/README.ja.md`, `01_Forkable/FKB01_Inference/03_Inference_FreeCloud/codex-chatgpt-web/package.json`
- **Noyau Cible & Destination ÉNONCÉ §1(1)** : **SYSTÈME NERVEUX · Organe K3 (Inférence & FreeCloud)** · Destination : **`FUSIONNÉ`** · Statut Vérifié (§5.8) : **`PARTIEL`** (Adapté et durci (`48f014e`, bouclier `aspace-telemetry-shield.cjs`, `start-aspace-codex-web.ps1`) ; reste intégration dans le routeur K3 unifié et test de suppression.)
- **Principe** : Façade Web Pro locale exposant les sessions ChatGPT authentifiées sous contrat `/responses` sans consommer de quota API payant.
- **Invariants** : 24 patterns de télémétrie bloqués localement ; blocage des auto-updates ; zéro secret dans les logs.
- **Interfaces** : Bridge local `:31418` -> `/v1/chat/completions` & `/responses`.
- **Perte au Retrait & Conflits** : Perte sans fusion : perte de la Voie B Web zéro-coût pour modèles Pro. Conflit : télémétrie Electron/Web amont -> ADR-08. (*Arbitrage : ADR-08*)

### M040 — `freebuff` (GITLINK)
- **Provenance & Sources Brutes Lues** : chemin `01_Forkable/FKB01_Inference/03_Inference_FreeCloud/freebuff` | repo `https://github.com/Amdkn/freebuff.git` | SHA/pin `7e2e21a972e9` | licence `Apache-2.0` | sources : `01_Forkable/FKB01_Inference/03_Inference_FreeCloud/freebuff/README.md`, `01_Forkable/FKB01_Inference/03_Inference_FreeCloud/freebuff/package.json`
- **Noyau Cible & Destination ÉNONCÉ §1(1)** : **SYSTÈME NERVEUX · Organe K3 (Inférence & FreeCloud)** · Destination : **`FUSIONNÉ`** · Statut Vérifié (§5.8) : **`PARTIEL`** (Inscrit dans `aspace_freecloud_gateway.py` (port `:31417`) ; reste intégration de son radar de crédits sponsors dans le discovery K3 et test de suppression.)
- **Principe** : Agent/radar multi-surfaces gratuit captant les crédits sponsors (ex. Exa) pour alimenter les pools gratuits.
- **Invariants** : Isolement strict des annonces sponsors (jamais injectées dans les prompts système de production) ; quota tracé dans SQLite.
- **Interfaces** : Backend tier 1 `http://127.0.0.1:31417/v1/chat/completions`.
- **Perte au Retrait & Conflits** : Perte sans fusion : perte d'une source de failover gratuit et d'ingestion d'offres de crédits. Conflit : contenu sponsorisé -> ADR-08. (*Arbitrage : ADR-08*)

### M041 — `freellmapi` (GITLINK)
- **Provenance & Sources Brutes Lues** : chemin `01_Forkable/FKB01_Inference/03_Inference_FreeCloud/freellmapi` | repo `https://github.com/Amdkn/freellmapi.git` | SHA/pin `7ea7db854c8d` | licence `LICENSE fichier lu` | sources : `01_Forkable/FKB01_Inference/03_Inference_FreeCloud/freellmapi/README.md`, `01_Forkable/FKB01_Inference/03_Inference_FreeCloud/freellmapi/package.json`
- **Noyau Cible & Destination ÉNONCÉ §1(1)** : **SYSTÈME NERVEUX · Organe K3 (Inférence & FreeCloud)** · Destination : **`FUSIONNÉ`** · Statut Vérifié (§5.8) : **`PARTIEL`** (Actif sur `:31415`/`:31416` et couplé à `aspace_freecloud_gateway.py` ; reste fusion du pool/failover natif dans K3 et test de suppression.)
- **Principe** : Agrégation de 34 providers gratuits (635+ endpoints) derrière un endpoint OpenAI unique avec rotation automatique et backoff sur quota épuisé.
- **Invariants** : Failover automatique sur `exhaustedPatterns` avec ré-essai temporisé (15 min) ; aucune clé en clair dans le repo.
- **Interfaces** : Endpoint unifié `127.0.0.1:31415` -> `freellmapi/auto` + table `provider_health`.
- **Perte au Retrait & Conflits** : Perte sans fusion : perte du socle d'inférence gratuite multi-providers assurant l'immortalité métabolique d'A0. Conflit : overlap routage avec bifrost -> ADR-08. (*Arbitrage : ADR-08*)

### M042 — `auto-ontology` (GITLINK)
- **Provenance & Sources Brutes Lues** : chemin `01_Forkable/FKB02_Memory/01_BillionContxtLanguage_AutoOnthology/auto-ontology` | repo `https://github.com/Amdkn/auto-ontology.git` | SHA/pin `b90c17cb4bcb` | licence `LICENSE fichier lu` | sources : `01_Forkable/FKB02_Memory/01_BillionContxtLanguage_AutoOnthology/auto-ontology/README.md`, `01_Forkable/FKB02_Memory/01_BillionContxtLanguage_AutoOnthology/auto-ontology/pyproject.toml`
- **Noyau Cible & Destination ÉNONCÉ §1(1)** : **ÂME · Organe K4 (Mémoire & Skills)** · Destination : **`FUSIONNÉ`** · Statut Vérifié (§5.8) : **`PARTIEL`** (Organe `aspace_fkb02_memory_organ.py` présent ; part manquante : aucune comparaison différentielle automatisée exécutant la source d'origine et l'organe sur des entrées identiques avant/après suppression physique.)
- **Principe** : Compilateur ontologique transformant les textes bruts en graphe acyclique (DAG) d'entités typées et relations dédoublonnées avec détection de contradictions.
- **Invariants** : Acyclicité stricte du graphe ; réconciliation d'entités sans doublons ; détection de contradictions formelles.
- **Interfaces** : compile_ontology(chunk) -> (entities[], relations[]) vers `memory.jsonl`.
- **Perte au Retrait & Conflits** : Perte sans fusion : dérive sémantique et explosion de nœuds redondants dans Shared Brain. Conflit : graphe libre vs DAG vérifié -> ADR-04. (*Arbitrage : ADR-04*)

### M043 — `billion-context` (GITLINK)
- **Provenance & Sources Brutes Lues** : chemin `01_Forkable/FKB02_Memory/01_BillionContxtLanguage_AutoOnthology/billion-context` | repo `https://github.com/Amdkn/billion-context.git` | SHA/pin `0a49433cbe0b` | licence `MIT` | sources : `01_Forkable/FKB02_Memory/01_BillionContxtLanguage_AutoOnthology/billion-context/README.md`, `01_Forkable/FKB02_Memory/01_BillionContxtLanguage_AutoOnthology/billion-context/package.json`
- **Noyau Cible & Destination ÉNONCÉ §1(1)** : **ÂME · Organe K4 (Mémoire & Skills)** · Destination : **`FUSIONNÉ`** · Statut Vérifié (§5.8) : **`PARTIEL`** (Organe `aspace_fkb02_memory_organ.py` présent ; part manquante : aucune comparaison différentielle automatisée exécutant la source d'origine et l'organe sur des entrées identiques avant/après suppression physique.)
- **Principe** : Compression et partitionnement hiérarchique de contextes massifs avec adressage par contenu immuable (CAS SHA-256) et déchargement disque NVMe.
- **Invariants** : Zéro saturation RAM ; chaque tranche de contexte est adressée de façon immuable par SHA-256.
- **Interfaces** : ingest_chunk(content, source_id) -> {cas_hash, tokens_est}.
- **Perte au Retrait & Conflits** : Perte sans fusion : perte de l'ingestion à grande échelle des corpus historiques. Conflit : accumulation brute vs isolation EGM -> ADR-05. (*Arbitrage : ADR-05*)

### M044 — `context-language-models` (GITLINK)
- **Provenance & Sources Brutes Lues** : chemin `01_Forkable/FKB02_Memory/01_BillionContxtLanguage_AutoOnthology/context-language-models` | repo `https://github.com/Amdkn/context-language-models.git` | SHA/pin `42db219d7302` | licence `LICENSE fichier lu` | sources : `01_Forkable/FKB02_Memory/01_BillionContxtLanguage_AutoOnthology/context-language-models/README.md`, `01_Forkable/FKB02_Memory/01_BillionContxtLanguage_AutoOnthology/context-language-models/pyproject.toml`
- **Noyau Cible & Destination ÉNONCÉ §1(1)** : **ÂME · Organe K4 (Mémoire & Skills)** · Destination : **`FUSIONNÉ`** · Statut Vérifié (§5.8) : **`FUSIONNÉ`** (Modules `context_string`, `edit_gate`, `finish_policy`, `lm_compat` portés 1:1 dans `01_Forkable/FKB00_Runtime/00_A0_Core/aspace_fkb02_memory_organ.py` ; test différentiel couvrant 100 % des fonctions et cas limites + sabotage de chaque fonction avant/après suppression physique PASS (gitlink conservé en attente du verdict Juge Cycle 6).)
- **Principe** : Conditionnement explicite des modèles de langage sur des représentations latentes ancrées dans l'ontologie (Zero Lost-in-the-Middle).
- **Invariants** : Aucune génération hors des invariants du schéma contextuel injecté.
- **Interfaces** : ContextLM_Decoder / cross-attention sur sous-graphe validé.
- **Perte au Retrait & Conflits** : Perte sans fusion : perte du mécanisme d'attention ciblée sur gros graphes de connaissances. Conflit : RAG vectoriel non ancré -> ADR-04. (*Arbitrage : ADR-04*)

### M045 — `dox` (GITLINK)
- **Provenance & Sources Brutes Lues** : chemin `01_Forkable/FKB02_Memory/dox` | repo `https://github.com/Amdkn/dox.git` | SHA/pin `7ed016b153d6` | licence `LICENSE fichier lu` | sources : `01_Forkable/FKB02_Memory/dox/README.md`
- **Noyau Cible & Destination ÉNONCÉ §1(1)** : **ÂME · Organe K4 (Mémoire & Skills)** · Destination : **`FUSIONNÉ`** · Statut Vérifié (§5.8) : **`PARTIEL`** (Organe `aspace_fkb02_memory_organ.py` présent ; part manquante : aucune comparaison différentielle automatisée exécutant la source d'origine et l'organe sur des entrées identiques avant/après suppression physique.)
- **Principe** : Contrat hiérarchique de gouvernance documentaire imposant la propagation des règles système et des conventions d'architecture à travers chaque dossier.
- **Invariants** : Transmission descendante des invariants ; porte de vérification automatique (`checks.ps1` étape 4).
- **Interfaces** : AGENTS.md / CLAUDE.md / règles DOX dans `02_Factory/checks.ps1`.
- **Perte au Retrait & Conflits** : Perte sans fusion : perte de l'alignement contractuel multi-harnesses. Conflit : aucun -> ADR-10. (*Arbitrage : ADR-10*)

### M046 — `gbrain` (GITLINK)
- **Provenance & Sources Brutes Lues** : chemin `01_Forkable/FKB02_Memory/gbrain` | repo `https://github.com/Amdkn/gbrain.git` | SHA/pin `de4968f5f5cb` | licence `MIT` | sources : `01_Forkable/FKB02_Memory/gbrain/README.md`, `01_Forkable/FKB02_Memory/gbrain/package.json`
- **Noyau Cible & Destination ÉNONCÉ §1(1)** : **ÂME · Organe K4 (Mémoire & Skills)** · Destination : **`FUSIONNÉ`** · Statut Vérifié (§5.8) : **`PARTIEL`** (Organe `aspace_fkb02_memory_organ.py` présent ; part manquante : aucune comparaison différentielle automatisée exécutant la source d'origine et l'organe sur des entrées identiques avant/après suppression physique.)
- **Principe** : Cerveau de connaissances personnel natif base de données combinant recherche lexicale, graphe de liens et recherche vectorielle hybride.
- **Invariants** : Tout fait remonté par recherche hybride doit porter sa source et passer le contrôle M1-M8 avant citation.
- **Interfaces** : Index hybride requête -> citations sourcées.
- **Perte au Retrait & Conflits** : Perte sans fusion : perte de la recherche hybride structurée haute performance sur gros corpus. Conflit : recherche sémantique floue vs citation exacte M1-M8 -> ADR-04. (*Arbitrage : ADR-04*)

### M047 — `graphify` (GITLINK)
- **Provenance & Sources Brutes Lues** : chemin `01_Forkable/FKB02_Memory/graphify` | repo `https://github.com/Amdkn/graphify.git` | SHA/pin `4b35e015207d` | licence `LICENSE fichier lu` | sources : `01_Forkable/FKB02_Memory/graphify/README.md`, `01_Forkable/FKB02_Memory/graphify/pyproject.toml`
- **Noyau Cible & Destination ÉNONCÉ §1(1)** : **ÂME · Organe K4 (Mémoire & Skills)** · Destination : **`FUSIONNÉ`** · Statut Vérifié (§5.8) : **`PARTIEL`** (Organe `aspace_fkb02_memory_organ.py` présent ; part manquante : aucune comparaison différentielle automatisée exécutant la source d'origine et l'organe sur des entrées identiques avant/après suppression physique.)
- **Principe** : Extraction AST de graphes de codebases, détection de communautés structurelles et requêtage topologique explicable.
- **Invariants** : Traçabilité exacte vers fichiers/lignes du code source ; mise à jour incrémentale (`graphify update .`).
- **Interfaces** : graphify.exe query|explain|update -> graphify-out/graph.json.
- **Perte au Retrait & Conflits** : Perte sans fusion : perte de la cartographie AST automatique du monorepo. Conflit : aucun -> ADR-04. (*Arbitrage : ADR-04*)

### M048 — `infinite-brain-harness` (GITLINK)
- **Provenance & Sources Brutes Lues** : chemin `01_Forkable/FKB02_Memory/infinite-brain-harness` | repo `https://github.com/Amdkn/infinite-brain-harness.git` | SHA/pin `ee81abb42939` | licence `LICENSE fichier lu` | sources : `01_Forkable/FKB02_Memory/infinite-brain-harness/README.md`
- **Noyau Cible & Destination ÉNONCÉ §1(1)** : **ÂME · Organe K4 (Mémoire & Skills)** · Destination : **`FUSIONNÉ`** · Statut Vérifié (§5.8) : **`PARTIEL`** (Organe `aspace_fkb02_memory_organ.py` présent ; part manquante : aucune comparaison différentielle automatisée exécutant la source d'origine et l'organe sur des entrées identiques avant/après suppression physique.)
- **Principe** : Harnais d'isolation multi-cerveaux permettant à un même agent d'opérer à travers plusieurs bases de connaissances cloisonnées sans fuite croisée.
- **Invariants** : Étanchéité des espaces de connaissances par domaine/client ; sélection explicite de la portée.
- **Interfaces** : Configuration multi-workspace / sélecteur de brain actif.
- **Perte au Retrait & Conflits** : Perte sans fusion : risque de mélange entre mémoire personnelle, Tech OS et clients B2B. Conflit : mémoire unique globale vs cloisonnement -> ADR-04. (*Arbitrage : ADR-04*)

### M049 — `infinite-brain-os` (GITLINK)
- **Provenance & Sources Brutes Lues** : chemin `01_Forkable/FKB02_Memory/infinite-brain-os` | repo `https://github.com/Amdkn/infinite-brain-os.git` | SHA/pin `cca8f707144e` | licence `LICENSE fichier lu` | sources : `01_Forkable/FKB02_Memory/infinite-brain-os/README.md`
- **Noyau Cible & Destination ÉNONCÉ §1(1)** : **ÂME · Organe K4 (Mémoire & Skills)** · Destination : **`FUSIONNÉ`** · Statut Vérifié (§5.8) : **`PARTIEL`** (Organe `aspace_fkb02_memory_organ.py` présent ; part manquante : aucune comparaison différentielle automatisée exécutant la source d'origine et l'organe sur des entrées identiques avant/après suppression physique.)
- **Principe** : Système d'exploitation de connaissances versionné sous Git en pur Markdown/YAML, lisible et auditable par tout agent de fichiers.
- **Invariants** : Format texte brut versionné Git (aucune boîte noire binaire propriétaire).
- **Interfaces** : Arborescence Markdown/YAML + Git commits.
- **Perte au Retrait & Conflits** : Perte sans fusion : perte des patrons d'organisation métier en Markdown git-backed. Conflit : doublon partiel avec WikiLLM/OKF -> ADR-04, ADR-11. (*Arbitrage : ADR-04, ADR-11*)

### M050 — `knowledge-catalog` (GITLINK)
- **Provenance & Sources Brutes Lues** : chemin `01_Forkable/FKB02_Memory/knowledge-catalog` | repo `https://github.com/Amdkn/knowledge-catalog.git` | SHA/pin `0069938857de` | licence `LICENSE fichier lu` | sources : `01_Forkable/FKB02_Memory/knowledge-catalog/README.md`
- **Noyau Cible & Destination ÉNONCÉ §1(1)** : **ÂME · Organe K4 (Mémoire & Skills)** · Destination : **`FUSIONNÉ`** · Statut Vérifié (§5.8) : **`FUSIONNÉ`** (Modules `document`, `index`, `synthesizer`, `paths` OKF v0.2 portés 1:1 dans `01_Forkable/FKB00_Runtime/00_A0_Core/aspace_fkb02_memory_organ.py` ; test différentiel couvrant 100 % des fonctions (dont `okf_is_stale` expirée/frontière) + sabotage de chaque fonction avant/après suppression physique PASS (gitlink conservé en attente du verdict Juge Cycle 6).)
- **Principe** : Format ouvert OKF v0.2 de documents atomiques avec frontmatter YAML typé, index central et journal chronologique append-only.
- **Invariants** : Frontmatter YAML `type:` obligatoire sur chaque concept ; indexation stricte dans `index.md` ; `log.md` strictement append-only.
- **Interfaces** : Validateur OKF v0.2 dans `02_Factory/checks.ps1`.
- **Perte au Retrait & Conflits** : Perte sans fusion : désagrégation structurelle du bundle mémoire. Conflit : aucun -> ADR-04. (*Arbitrage : ADR-04*)

### M051 — `servers` (GITLINK)
- **Provenance & Sources Brutes Lues** : chemin `01_Forkable/FKB02_Memory/servers` | repo `https://github.com/Amdkn/servers.git` | SHA/pin `1031b7f6d554` | licence `SEE LICENSE IN LICENSE` | sources : `01_Forkable/FKB02_Memory/servers/README.md`, `01_Forkable/FKB02_Memory/servers/package.json`
- **Noyau Cible & Destination ÉNONCÉ §1(1)** : **ÂME · Organe K4 (Mémoire & Skills)** · Destination : **`RETENU`** · Statut Vérifié (§5.8) : **`RETENU`** (RETENU (Justification de fondation : implémentation de référence officielle `@modelcontextprotocol/server-memory` exécutée via Stdio/JSONL avec verrou `FileLock O_EXCL` sur `memory.jsonl` pour tous les harnesses).)
- **Principe** : Gateway MCP officielle de graphe de connaissances JSONL exposant les 9 primitives CRUD/recherche standardisées à tous les clients MCP.
- **Invariants** : Chemin absolu unique `MEMORY_FILE_PATH` ; interdiction d'appeler `read_graph` complet en routine ; verrou concurrentiel O_EXCL.
- **Interfaces** : 9 outils MCP : create/delete_entities, create/delete_relations, add/delete_observations, search_nodes, open_nodes, read_graph.
- **Perte au Retrait & Conflits** : Perte si écarté : rupture d'interopérabilité native MCP entre Claude, Codex, OpenCode, Pi et Antigravity. Conflit : verrou concurrentiel -> ADR-04. (*Arbitrage : ADR-04*)

### M052 — `agent-office` (GITLINK)
- **Provenance & Sources Brutes Lues** : chemin `01_Forkable/FKB03_3DWorlds/agent-office` | repo `https://github.com/Amdkn/agent-office.git` | SHA/pin `70ebb106d0bd` | licence `MIT` | sources : `01_Forkable/FKB03_3DWorlds/agent-office/README.md`, `01_Forkable/FKB03_3DWorlds/agent-office/package.json`
- **Noyau Cible & Destination ÉNONCÉ §1(1)** : **CORPS · Organe K2 (Exécution, Anything & 3D)** · Destination : **`FUSIONNÉ`** · Statut Vérifié (§5.8) : **`PARTIEL`** (Synchronisé (`70ebb10`) et intégré conceptuellement dans `city-office` (anneau routier + Tab Portal Boards 2D) ; reste unification finale du code dans `city-office` et retrait gitlink.)
- **Principe** : Bureaux 3D temps réel à bureaux assignés, flux terminaux en direct et Tableaux-Portails 2D (touche Tab) pour les managers S2/B2..I2.
- **Invariants** : Repli propre si backend `:4600` absent ; aucun timer zombie à la destruction R3F (CanvasTexture synchrone).
- **Interfaces** : Mezzanine 3D / Tab Portal Boards / socket /ws.
- **Perte au Retrait & Conflits** : Perte sans fusion : perte des Tableaux-Portails 2D et de la visualisation temps réel des terminaux managers. Conflit : 2 mondes 3D séparés -> ADR-02. (*Arbitrage : ADR-02*)

### M053 — `city-office` (GITLINK)
- **Provenance & Sources Brutes Lues** : chemin `01_Forkable/FKB03_3DWorlds/city-office` | repo `https://github.com/Amdkn/city-office.git` | SHA/pin `fff356ed4b0f` | licence `voir-source-brute` | sources : `01_Forkable/FKB03_3DWorlds/city-office/README.md`, `01_Forkable/FKB03_3DWorlds/city-office/package.json`
- **Noyau Cible & Destination ÉNONCÉ §1(1)** : **CORPS · Organe K2 (Exécution, Anything & 3D)** · Destination : **`FUSIONNÉ`** · Statut Vérifié (§5.8) : **`PARTIEL`** (Sous-module fusionnant déjà CubeFarm (centre) + Agent-Office (anneau) + 7 districts FKB ; reste absorption comme surface unifiée L2 et retrait/promotion hors 01_Forkable.)
- **Principe** : Métropole 3D concentrique unifiant le sanctuaire voxel central, l'anneau de trafic MCP et les districts fonctionnels FKB.
- **Invariants** : Déployable Vercel Edge sans backend bloquant ; montable en couche 8L.
- **Interfaces** : vercel.json (`city.aspaceos.tech`) / 02_Factory/mount-fractal.ps1.
- **Perte au Retrait & Conflits** : Perte sans fusion : fragmentation des vues 3D en applications incompatibles. Conflit : redondance avec cubefarm/agent-office -> ADR-02. (*Arbitrage : ADR-02*)

### M054 — `cubefarm` (GITLINK)
- **Provenance & Sources Brutes Lues** : chemin `01_Forkable/FKB03_3DWorlds/cubefarm` | repo `https://github.com/Amdkn/cubefarm.git` | SHA/pin `3d2a90d67363` | licence `MIT` | sources : `01_Forkable/FKB03_3DWorlds/cubefarm/README.md`, `01_Forkable/FKB03_3DWorlds/cubefarm/package.json`
- **Noyau Cible & Destination ÉNONCÉ §1(1)** : **CORPS · Organe K2 (Exécution, Anything & 3D)** · Destination : **`RETENU`** · Statut Vérifié (§5.8) : **`RETENU`** (RETENU (Justification de fondation : application WebGL/Three.js déployable incarnant les 3 Étages OS et les 578 Holons — surface 3D opérationnelle active avec fallback autonome).)
- **Principe** : Incarnation spatiale 3D de l'organisation agentique en 3 étages OS (Tech/Life/Areas) avec lobby A0 et monitoring visuel des issues/agents.
- **Invariants** : Fallback autonome 1,5s anti-blocage WebSocket sur déploiement Edge ; zéro secret client.
- **Interfaces** : UI 3D React Three Fiber + shared/aspaceHolons.ts + /ws.
- **Perte au Retrait & Conflits** : Perte si écarté : perte de l'interface spatiale principale des 578 Holons et du Lobby A0. Conflit : duplication avec city-office -> ADR-02. (*Arbitrage : ADR-02*)

### M055 — `space-agent` (GITLINK)
- **Provenance & Sources Brutes Lues** : chemin `01_Forkable/FKB03_3DWorlds/space-agent` | repo `https://github.com/Amdkn/space-agent.git` | SHA/pin `10f4ffdaf50a` | licence `voir-source-brute` | sources : `01_Forkable/FKB03_3DWorlds/00_A0_Core/space-agent.manifest.json`, `01_Forkable/FKB03_3DWorlds/00_A0_Core/space-agent-ADAPTATION.md`
- **Noyau Cible & Destination ÉNONCÉ §1(1)** : **CORPS · Organe K2 (Exécution, Anything & 3D)** · Destination : **`FUSIONNÉ`** · Statut Vérifié (§5.8) : **`PARTIEL`** (Adapté état 2 (`10f4ffd`) ; reste portage du protocole d'agent spatial dans la scène 3D unifiée K2 et retrait du gitlink.)
- **Principe** : Protocole de représentation d'agents mobiles autonomes navigant et exécutant des tâches dans un espace 3D partagé.
- **Invariants** : Télémétrie zéro ; événements d'état synchronisés sur le journal K2.
- **Interfaces** : fiber:a0:space-agent -> événements spatiaux 3D.
- **Perte au Retrait & Conflits** : Perte sans fusion : perte de la cinématique d'agents mobiles dans l'espace 3D. Conflit : aucun -> ADR-02. (*Arbitrage : ADR-02*)

### M056 — `CLI-Anything` (GITLINK)
- **Provenance & Sources Brutes Lues** : chemin `01_Forkable/FKB04_Tools_Anything/CLI-Anything` | repo `https://github.com/Amdkn/CLI-Anything.git` | SHA/pin `34f519533bc1` | licence `LICENSE fichier lu` | sources : `01_Forkable/FKB04_Tools_Anything/CLI-Anything/README.md`
- **Noyau Cible & Destination ÉNONCÉ §1(1)** : **CORPS · Organe K2 (Exécution, Anything & 3D)** · Destination : **`FUSIONNÉ`** · Statut Vérifié (§5.8) : **`FUSIONNÉ`** (Extracteur Click/Docstring, générateur `SKILL.md` Jinja2 et clé de cache preview portés 1:1 dans `01_Forkable/FKB00_Runtime/00_A0_Core/aspace_fkb04_anything_organ.py` ; test différentiel contre `cli-anything-plugin` (`zotero`, `audacity` & harnesses synthétiques) + sabotage de chaque fonction avant/après suppression physique PASS (gitlink conservé en attente du verdict Juge Cycle 6).)
- **Principe** : Génération automatisée de wrappers CLI structurés (JSON stdout, sous-commandes typées) pour piloter n'importe quel logiciel GUI/desktop par des agents.
- **Invariants** : Sorties structurées machine-readable ; aucune dépendance à la manipulation souris si une interface CLI peut être générée.
- **Interfaces** : Générateur CLI-Anything -> wrappers JSON.
- **Perte au Retrait & Conflits** : Perte sans fusion : obligation de recourir au Computer Use fragile sur des logiciels scriptables. Conflit : Computer Use GUI vs CLI -> ADR-10. (*Arbitrage : ADR-10*)

### M057 — `agent-browser` (GITLINK)
- **Provenance & Sources Brutes Lues** : chemin `01_Forkable/FKB04_Tools_Anything/agent-browser` | repo `https://github.com/Amdkn/agent-browser.git` | SHA/pin `f88c40b7ed7c` | licence `Apache-2.0` | sources : `01_Forkable/FKB04_Tools_Anything/00_A0_Core/agent-browser.manifest.json`, `01_Forkable/FKB04_Tools_Anything/00_A0_Core/agent-browser-ADAPTATION.md`, `01_Forkable/FKB04_Tools_Anything/agent-browser/README.md`, `01_Forkable/FKB04_Tools_Anything/agent-browser/package.json`
- **Noyau Cible & Destination ÉNONCÉ §1(1)** : **CORPS · Organe K2 (Exécution, Anything & 3D)** · Destination : **`FUSIONNÉ`** · Statut Vérifié (§5.8) : **`PARTIEL`** (Organe `aspace_fkb04_anything_organ.py` présent ; part manquante (rétrogradé au Cycle 5) : aucune comparaison différentielle automatisée exécutant la source d'origine et l'organe sur des entrées identiques avant/après suppression physique.)
- **Principe** : Automatisation navigateur déterministe par daemon CDP et snapshots d'arbre d'accessibilité à références stables (`@ref`).
- **Invariants** : Zéro CAPTCHA/anti-bot contourné ; isolation stricte de session ; zéro télémétrie Vercel.
- **Interfaces** : agent-browser open|snapshot|click|fill|eval via daemon CDP.
- **Perte au Retrait & Conflits** : Perte sans fusion : fragilité des sélecteurs CSS/DOM dans les automates web. Conflit : automation Playwright ad-hoc vs arbre `@ref` -> ADR-10. (*Arbitrage : ADR-10*)

### M058 — `agent-desktop` (GITLINK)
- **Provenance & Sources Brutes Lues** : chemin `01_Forkable/FKB04_Tools_Anything/agent-desktop` | repo `https://github.com/Amdkn/agent-desktop.git` | SHA/pin `54855b6225ae` | licence `LICENSE fichier lu` | sources : `01_Forkable/FKB04_Tools_Anything/00_A0_Core/agent-desktop.manifest.json`, `01_Forkable/FKB04_Tools_Anything/00_A0_Core/agent-desktop-ADAPTATION.md`, `01_Forkable/FKB04_Tools_Anything/agent-desktop/README.md`, `01_Forkable/FKB04_Tools_Anything/agent-desktop/Cargo.toml`
- **Noyau Cible & Destination ÉNONCÉ §1(1)** : **CORPS · Organe K2 (Exécution, Anything & 3D)** · Destination : **`FUSIONNÉ`** · Statut Vérifié (§5.8) : **`PARTIEL`** (Pilote UIA Win32 dans `aspace_fkb04_anything_organ.py` (`headless-fallback` supprimé) ; part manquante : aucune interaction vérifiée sur une vraie fenêtre Windows (`live_window_verified = False`, `0` fenêtres UIA en session headless) et absence de comparaison différentielle contre la source `agent-desktop`.)
- **Principe** : Automatisation native des applications desktop (Windows/macOS/Linux) via l'arbre d'accessibilité OS sans vol de focus.
- **Invariants** : Zéro vol de focus humain ; priorité aux voies CLI/API avant GUI.
- **Interfaces** : Serveur MCP `agent-desktop mcp` / primitives d'accessibilité OS.
- **Perte au Retrait & Conflits** : Perte sans fusion : impossibilité de piloter proprement les apps desktop fermées sans bloquer l'utilisateur. Conflit : chevauchement avec `orca computer` -> ADR-02, ADR-10. (*Arbitrage : ADR-02, ADR-10*)

### M059 — `api-anything` (GITLINK)
- **Provenance & Sources Brutes Lues** : chemin `01_Forkable/FKB04_Tools_Anything/api-anything` | repo `https://github.com/Amdkn/api-anything.git` | SHA/pin `3372d36560ad` | licence `MIT` | sources : `01_Forkable/FKB04_Tools_Anything/api-anything/README.md`, `01_Forkable/FKB04_Tools_Anything/api-anything/package.json`
- **Noyau Cible & Destination ÉNONCÉ §1(1)** : **CORPS · Organe K2 (Exécution, Anything & 3D)** · Destination : **`FUSIONNÉ`** · Statut Vérifié (§5.8) : **`PARTIEL`** (Organe `aspace_fkb04_anything_organ.py` présent ; part manquante (rétrogradé au Cycle 5) : aucune comparaison différentielle automatisée exécutant la source d'origine et l'organe sur des entrées identiques avant/après suppression physique.)
- **Principe** : Apprentissage d'opérations API réutilisables à partir du trafic réseau navigateur pour exposer tout service web en CLI, librairie ou serveur MCP.
- **Invariants** : Aucune fuite de credentials capturés hors coffre local ; contrats typés.
- **Interfaces** : Capture HAR/trafic -> serveur MCP / CLI / SDK.
- **Perte au Retrait & Conflits** : Perte sans fusion : réécriture manuelle coûteuse des intégrations web sans API publique. Conflit : aucun -> ADR-10. (*Arbitrage : ADR-10*)

### M060 — `caveman` (GITLINK)
- **Provenance & Sources Brutes Lues** : chemin `01_Forkable/FKB04_Tools_Anything/caveman` | repo `https://github.com/Amdkn/caveman.git` | SHA/pin `1e91f1306d60` | licence `Apache-2.0` | sources : `01_Forkable/FKB04_Tools_Anything/00_A0_Core/caveman.manifest.json`, `01_Forkable/FKB04_Tools_Anything/00_A0_Core/caveman-ADAPTATION.md`, `01_Forkable/FKB04_Tools_Anything/caveman/README.md`, `01_Forkable/FKB04_Tools_Anything/caveman/package.json`
- **Noyau Cible & Destination ÉNONCÉ §1(1)** : **ÂME · Organe K4 (Mémoire & Skills)** · Destination : **`FUSIONNÉ`** · Statut Vérifié (§5.8) : **`PARTIEL`** (Organe `aspace_fkb04_anything_organ.py` présent ; part manquante (rétrogradé au Cycle 5) : aucune comparaison différentielle automatisée exécutant la source d'origine et l'organe sur des entrées identiques avant/après suppression physique.)
- **Principe** : Compression télégraphique maximale des prompts et réponses inter-agents afin de réduire de 60-75 % la consommation de tokens sans perte d'information.
- **Invariants** : Préservation 100 % des identifiants, chemins, SHA et faits vérifiables lors de la compression.
- **Interfaces** : Mode/filtre Caveman (style télégraphique inter-agents).
- **Perte au Retrait & Conflits** : Perte sans fusion : gaspillage massif de tokens et saturation prématurée des contextes. Conflit : verbosité humaine vs télégraphie interne -> ADR-05. (*Arbitrage : ADR-05*)

### M061 — `claude-mem` (GITLINK)
- **Provenance & Sources Brutes Lues** : chemin `01_Forkable/FKB04_Tools_Anything/claude-mem` | repo `https://github.com/Amdkn/claude-mem.git` | SHA/pin `3ab6e1a215c7` | licence `Apache-2.0` | sources : `01_Forkable/FKB04_Tools_Anything/00_A0_Core/claude-mem.manifest.json`, `01_Forkable/FKB04_Tools_Anything/00_A0_Core/claude-mem-ADAPTATION.md`, `01_Forkable/FKB04_Tools_Anything/claude-mem/README.md`, `01_Forkable/FKB04_Tools_Anything/claude-mem/package.json`
- **Noyau Cible & Destination ÉNONCÉ §1(1)** : **ÂME · Organe K4 (Mémoire & Skills)** · Destination : **`FUSIONNÉ`** · Statut Vérifié (§5.8) : **`PARTIEL`** (Organe `aspace_fkb04_anything_organ.py` présent ; part manquante (rétrogradé au Cycle 5) : aucune comparaison différentielle automatisée exécutant la source d'origine et l'organe sur des entrées identiques avant/après suppression physique.)
- **Principe** : Capture continue inter-sessions et indexation automatique des observations de travail pour démarrer chaque session là où la précédente s'est arrêtée.
- **Invariants** : Injection bornée dans le contexte (anti-saturation) ; écriture dans le store partagé unifié.
- **Interfaces** : Hooks session-start / post-tool-use -> index observations.
- **Perte au Retrait & Conflits** : Perte sans fusion : amnésie entre sessions CLI isolées. Conflit : double base mémoire avec `memory.jsonl` -> ADR-04. (*Arbitrage : ADR-04*)

### M062 — `hermes-agent` (GITLINK)
- **Provenance & Sources Brutes Lues** : chemin `01_Forkable/FKB04_Tools_Anything/hermes-agent` | repo `https://github.com/Amdkn/hermes-agent.git` | SHA/pin `ab91bcdba023` | licence `MIT` | sources : `01_Forkable/FKB04_Tools_Anything/hermes-agent/README.es.md`, `01_Forkable/FKB04_Tools_Anything/hermes-agent/package.json`, `01_Forkable/FKB04_Tools_Anything/hermes-agent/pyproject.toml`
- **Noyau Cible & Destination ÉNONCÉ §1(1)** : **ÂME · Organe K4 (Mémoire & Skills)** · Destination : **`FUSIONNÉ`** · Statut Vérifié (§5.8) : **`PARTIEL`** (Organe `aspace_fkb04_anything_organ.py` présent ; part manquante (rétrogradé au Cycle 5) : aucune comparaison différentielle automatisée exécutant la source d'origine et l'organe sur des entrées identiques avant/après suppression physique.)
- **Principe** : Boucle d'apprentissage fermée autonome : fabrication de skills depuis l'expérience, recherche FTS5 sur conversations passées et modélisation progressive utilisateur.
- **Invariants** : Toute compétence créée par `/learn` doit être validée par hold-out avant promotion globale.
- **Interfaces** : Loop `/learn` + index FTS5 + standard `SKILL.md`.
- **Perte au Retrait & Conflits** : Perte sans fusion : agents statiques incapables de capitaliser automatiquement leurs découvertes. Conflit : création libre vs validation hold-out -> ADR-06, ADR-11. (*Arbitrage : ADR-06, ADR-11*)

### M063 — `rea` (GITLINK)
- **Provenance & Sources Brutes Lues** : chemin `01_Forkable/FKB04_Tools_Anything/rea` | repo `https://github.com/Amdkn/rea.git` | SHA/pin `8a2bf2149015` | licence `MIT` | sources : `01_Forkable/FKB04_Tools_Anything/rea/README.md`, `01_Forkable/FKB04_Tools_Anything/rea/package.json`
- **Noyau Cible & Destination ÉNONCÉ §1(1)** : **CORPS · Organe K2 (Exécution, Anything & 3D)** · Destination : **`FUSIONNÉ`** · Statut Vérifié (§5.8) : **`PARTIEL`** (Organe `aspace_fkb04_anything_organ.py` présent ; part manquante (rétrogradé au Cycle 5) : aucune comparaison différentielle automatisée exécutant la source d'origine et l'organe sur des entrées identiques avant/après suppression physique.)
- **Principe** : Rétro-ingénierie unifiée d'artefacts, binaires, APIs et protocoles depuis un seul CLI et serveur MCP.
- **Invariants** : Respect des bornes clean-room D12 (extraction de spécifications, jamais de copie illicite).
- **Interfaces** : CLI `rea` + serveur MCP de rétro-ingénierie.
- **Perte au Retrait & Conflits** : Perte sans fusion : perte de la capacité de rétro-ingénierie outillée en phase Discover. Conflit : aucun -> ADR-09, ADR-10. (*Arbitrage : ADR-09, ADR-10*)

### M064 — `LLM-Trading-Lab` (GITLINK)
- **Provenance & Sources Brutes Lues** : chemin `01_Forkable/FKB07_Money_Maker/01_Trading/LLM-Trading-Lab` | repo `https://github.com/Amdkn/LLM-Trading-Lab.git` | SHA/pin `028148eb8031` | licence `voir-source-brute` | sources : `01_Forkable/FKB07_Money_Maker/01_Trading/LLM-Trading-Lab/README.md`
- **Noyau Cible & Destination ÉNONCÉ §1(1)** : **CORPS · Organe K5 (Métabolisme B2B, Vidéo & Finance S0)** · Destination : **`ÉCARTÉ`** · Statut Vérifié (§5.8) : **`ÉCARTÉ`** (ÉCARTÉ (Raison vérifiée : simple expérience empirique/benchmark historique micro-caps sans infrastructure réutilisable non couverte par TradingAgents/Vibe-Trading/AVERTISSEMENTS.md).)
- **Principe** : Journal empirique expérimental d'un portefeuille micro-caps géré par ChatGPT.
- **Invariants** : Hors périmètre exécution autonome (données expérimentales uniquement).
- **Interfaces** : Scripts d'analyse de journaux CSV.
- **Perte au Retrait & Conflits** : Perte à l'écartement : nulle (toutes les capacités d'analyse et backtest sont couvertes par Vibe-Trading, Daily Stock Analysis et TradingAgents). Conflit : redondance -> ADR-07. (*Arbitrage : ADR-07*)

### M065 — `TradingAgents` (GITLINK)
- **Provenance & Sources Brutes Lues** : chemin `01_Forkable/FKB07_Money_Maker/01_Trading/TradingAgents` | repo `https://github.com/Amdkn/TradingAgents.git` | SHA/pin `6ee58345d680` | licence `LICENSE fichier lu` | sources : `01_Forkable/FKB07_Money_Maker/01_Trading/TradingAgents/README.md`, `01_Forkable/FKB07_Money_Maker/01_Trading/TradingAgents/pyproject.toml`
- **Noyau Cible & Destination ÉNONCÉ §1(1)** : **CORPS · Organe K5 (Métabolisme B2B, Vidéo & Finance S0)** · Destination : **`FUSIONNÉ`** · Statut Vérifié (§5.8) : **`PARTIEL`** (Intégré en architecture copilote ; reste extraction du protocole de débat Bull/Bear et gestion de risque dans K5 et retrait gitlink.)
- **Principe** : Débat contradictoire multi-agents (analystes fondamentaux/techniques, débat Bull/Bear, gestionnaire de risque) avant toute recommandation financière.
- **Invariants** : Mode READ-ONLY strict (AVERTISSEMENTS.md) ; aucun passage d'ordre automatique sans signature S0 ; déduction des frais.
- **Interfaces** : Graphe décisionnel multi-agents -> rapport de recommandation typé.
- **Perte au Retrait & Conflits** : Perte sans fusion : perte de la contradiction systématique Bull/Bear en analyse financière. Conflit : exécution autonome vs veto S0 -> ADR-07. (*Arbitrage : ADR-07*)

### M066 — `TradingView-Unified-MCP` (GITLINK)
- **Provenance & Sources Brutes Lues** : chemin `01_Forkable/FKB07_Money_Maker/01_Trading/TradingView-Unified-MCP` | repo `https://github.com/Amdkn/TradingView-Unified-MCP.git` | SHA/pin `378c9c963dd2` | licence `MIT` | sources : `01_Forkable/FKB07_Money_Maker/01_Trading/TradingView-Unified-MCP/README.md`, `01_Forkable/FKB07_Money_Maker/01_Trading/TradingView-Unified-MCP/package.json`
- **Noyau Cible & Destination ÉNONCÉ §1(1)** : **CORPS · Organe K5 (Métabolisme B2B, Vidéo & Finance S0)** · Destination : **`FUSIONNÉ`** · Statut Vérifié (§5.8) : **`PARTIEL`** (Actif FKB07/01_Trading ; reste fusion avec le pont MCP K5/agent-browser et retrait gitlink.)
- **Principe** : Contrôle headless local de TradingView via MCP pour inspecter graphiques, watchlists et alertes vérifiées.
- **Invariants** : Opération purement locale sur session utilisateur ; lecture seule sur comptes.
- **Interfaces** : Outils MCP TradingView Unified.
- **Perte au Retrait & Conflits** : Perte sans fusion : perte de l'inspection automatisée des graphes et alertes TradingView. Conflit : aucun -> ADR-07. (*Arbitrage : ADR-07*)

### M067 — `Vibe-Trading` (GITLINK)
- **Provenance & Sources Brutes Lues** : chemin `01_Forkable/FKB07_Money_Maker/01_Trading/Vibe-Trading` | repo `https://github.com/Amdkn/Vibe-Trading.git` | SHA/pin `7f95b483c2bf` | licence `LICENSE fichier lu` | sources : `01_Forkable/FKB07_Money_Maker/01_Trading/Vibe-Trading/README.md`, `01_Forkable/FKB07_Money_Maker/01_Trading/Vibe-Trading/pyproject.toml`
- **Noyau Cible & Destination ÉNONCÉ §1(1)** : **CORPS · Organe K5 (Métabolisme B2B, Vidéo & Finance S0)** · Destination : **`FUSIONNÉ`** · Statut Vérifié (§5.8) : **`PARTIEL`** (Actif FKB07/01_Trading ; reste extraction du moteur de backtest réaliste/paper-trading dans K5 et retrait gitlink.)
- **Principe** : Synthèse de stratégies quantitatives depuis le langage naturel avec backtest réaliste intégrant slippage/frais et mémoire d'erreurs.
- **Invariants** : Backtest obligatoirement net de frais ; exécution limitée au paper-trading sans veto S0.
- **Interfaces** : Pipeline NL -> stratégie -> backtest réaliste.
- **Perte au Retrait & Conflits** : Perte sans fusion : perte du prototypage et backtesting réaliste de stratégies. Conflit : passage réel Alpaca vs veto S0 -> ADR-07. (*Arbitrage : ADR-07*)

### M068 — `ai-hedge-fund` (GITLINK)
- **Provenance & Sources Brutes Lues** : chemin `01_Forkable/FKB07_Money_Maker/01_Trading/ai-hedge-fund` | repo `https://github.com/Amdkn/ai-hedge-fund.git` | SHA/pin `b1d1df04b958` | licence `LICENSE fichier lu` | sources : `01_Forkable/FKB07_Money_Maker/01_Trading/ai-hedge-fund/README.md`, `01_Forkable/FKB07_Money_Maker/01_Trading/ai-hedge-fund/pyproject.toml`
- **Noyau Cible & Destination ÉNONCÉ §1(1)** : **CORPS · Organe K5 (Métabolisme B2B, Vidéo & Finance S0)** · Destination : **`FUSIONNÉ`** · Statut Vérifié (§5.8) : **`PARTIEL`** (Actif FKB07/01_Trading ; reste absorption des profils d'évaluation multi-personas dans le comité K5 et retrait gitlink.)
- **Principe** : Comité d'investissement multi-personas simulant des philosophies d'investissement complémentaires (Value, Croissance, Contrarian).
- **Invariants** : Mode simulation/analyse uniquement (zéro ordre réel autonome).
- **Interfaces** : Agents analystes par philosophie -> synthèse comité.
- **Perte au Retrait & Conflits** : Perte sans fusion : perte de la grille multi-philosophies d'évaluation d'actifs. Conflit : exécution auto -> ADR-07. (*Arbitrage : ADR-07*)

### M069 — `claude-trading-skills` (GITLINK)
- **Provenance & Sources Brutes Lues** : chemin `01_Forkable/FKB07_Money_Maker/01_Trading/claude-trading-skills` | repo `https://github.com/Amdkn/claude-trading-skills.git` | SHA/pin `652a0aecd5ad` | licence `LICENSE fichier lu` | sources : `01_Forkable/FKB07_Money_Maker/01_Trading/claude-trading-skills/README.ja.md`, `01_Forkable/FKB07_Money_Maker/01_Trading/claude-trading-skills/pyproject.toml`
- **Noyau Cible & Destination ÉNONCÉ §1(1)** : **CORPS · Organe K5 (Métabolisme B2B, Vidéo & Finance S0)** · Destination : **`FUSIONNÉ`** · Statut Vérifié (§5.8) : **`PARTIEL`** (Actif FKB07/01_Trading ; reste extraction de la formule déterministe de position sizing (Stop-Loss <= 1%) dans K5 et retrait gitlink.)
- **Principe** : Calcul déterministe du dimensionnement de position (risk sizing ≤ 1 % par trade) et listes de contrôle pré-trade.
- **Invariants** : Le dimensionnement vient toujours d'une formule mathématique déterministe, jamais d'une estimation LLM.
- **Interfaces** : Calculateur de risque déterministe & skills day-trading.
- **Perte au Retrait & Conflits** : Perte sans fusion : risque d'estimation probabiliste hasardeuse des tailles de position par un LLM. Conflit : aucun -> ADR-03, ADR-07. (*Arbitrage : ADR-03, ADR-07*)

### M070 — `daily_stock_analysis` (GITLINK)
- **Provenance & Sources Brutes Lues** : chemin `01_Forkable/FKB07_Money_Maker/01_Trading/daily_stock_analysis` | repo `https://github.com/Amdkn/daily_stock_analysis.git` | SHA/pin `06d58611af49` | licence `LICENSE fichier lu` | sources : `01_Forkable/FKB07_Money_Maker/01_Trading/daily_stock_analysis/README.md`, `01_Forkable/FKB07_Money_Maker/01_Trading/daily_stock_analysis/pyproject.toml`
- **Noyau Cible & Destination ÉNONCÉ §1(1)** : **CORPS · Organe K5 (Métabolisme B2B, Vidéo & Finance S0)** · Destination : **`FUSIONNÉ`** · Statut Vérifié (§5.8) : **`PARTIEL`** (Actif FKB07/01_Trading ; reste portage du pipeline de scoring quotidien /100 et alertes pré-marché dans K5 et retrait gitlink.)
- **Principe** : Analyse multi-marchés automatisée produisant un score /100 reproductible et des synthèses de risque pré-marché.
- **Invariants** : Lecture seule ; alerte asynchrone uniquement ; aucun ordre envoyé.
- **Interfaces** : Pipeline scoring quotidien -> rapport structuré.
- **Perte au Retrait & Conflits** : Perte sans fusion : perte de la veille matinale structurée multi-marchés. Conflit : cron vs déclenchement événementiel -> ADR-01, ADR-07. (*Arbitrage : ADR-01, ADR-07*)

### M071 — `financial-services` (GITLINK)
- **Provenance & Sources Brutes Lues** : chemin `01_Forkable/FKB07_Money_Maker/01_Trading/financial-services` | repo `https://github.com/Amdkn/financial-services.git` | SHA/pin `4b7d7e5dbc9d` | licence `LICENSE fichier lu` | sources : `01_Forkable/FKB07_Money_Maker/01_Trading/financial-services/README.md`
- **Noyau Cible & Destination ÉNONCÉ §1(1)** : **CORPS · Organe K5 (Métabolisme B2B, Vidéo & Finance S0)** · Destination : **`FUSIONNÉ`** · Statut Vérifié (§5.8) : **`PARTIEL`** (Actif FKB07/01_Trading ; reste intégration des grilles de valorisation et d'analyse financière dans K5/K4 et retrait gitlink.)
- **Principe** : Protocoles institutionnels de recherche actions, modélisation de valorisation, revue de résultats et due diligence.
- **Invariants** : Sourcing chiffré obligatoire des ratios financiers ; zéro chiffre inventé.
- **Interfaces** : Skills & connecteurs d'analyse financière institutionnelle.
- **Perte au Retrait & Conflits** : Perte sans fusion : perte des standards de modélisation financière pro pour LD02/B2B. Conflit : aucun -> ADR-07. (*Arbitrage : ADR-07*)

### M072 — `freqtrade` (GITLINK)
- **Provenance & Sources Brutes Lues** : chemin `01_Forkable/FKB07_Money_Maker/01_Trading/freqtrade` | repo `https://github.com/Amdkn/freqtrade.git` | SHA/pin `43760fe804f6` | licence `LICENSE fichier lu` | sources : `01_Forkable/FKB07_Money_Maker/01_Trading/freqtrade/README.md`, `01_Forkable/FKB07_Money_Maker/01_Trading/freqtrade/pyproject.toml`
- **Noyau Cible & Destination ÉNONCÉ §1(1)** : **CORPS · Organe K5 (Métabolisme B2B, Vidéo & Finance S0)** · Destination : **`RETENU`** · Statut Vérifié (§5.8) : **`RETENU`** (RETENU (Justification de fondation : moteur complet d'exécution/backtest/hyperopt crypto Python avec connecteurs CCXT CEX/DEX et dry-run — infrastructure métier spécialisée bridée en dry-run sous veto S0).)
- **Principe** : Moteur algorithmique crypto complet (backtesting vectorisé, optimisation ML FreqAI, dry-run, passerelles exchanges).
- **Invariants** : Bridé en `dry_run: true` tant que le veto humain S0 (`human:amdkn`) n'a pas ratifié explicitement ; clés API via env isolé.
- **Interfaces** : CLI `freqtrade backtesting|hyperopt|trade` (dry-run).
- **Perte au Retrait & Conflits** : Perte si écarté : perte de l'infrastructure éprouvée de backtest et d'interface exchange crypto. Conflit : auto-trading live vs veto S0 -> ADR-07. (*Arbitrage : ADR-07*)

### M073 — `nansen-cli` (GITLINK)
- **Provenance & Sources Brutes Lues** : chemin `01_Forkable/FKB07_Money_Maker/01_Trading/nansen-cli` | repo `https://github.com/Amdkn/nansen-cli.git` | SHA/pin `fac5f35e2ec1` | licence `MIT` | sources : `01_Forkable/FKB07_Money_Maker/00_A0_Core/nansen-cli.manifest.json`, `01_Forkable/FKB07_Money_Maker/00_A0_Core/nansen-cli-ADAPTATION.md`, `01_Forkable/FKB07_Money_Maker/01_Trading/nansen-cli/README.md`, `01_Forkable/FKB07_Money_Maker/01_Trading/nansen-cli/package.json`
- **Noyau Cible & Destination ÉNONCÉ §1(1)** : **CORPS · Organe K5 (Métabolisme B2B, Vidéo & Finance S0)** · Destination : **`FUSIONNÉ`** · Statut Vérifié (§5.8) : **`PARTIEL`** (Adapté état 2 (`0b39ae5` / `fac5f35`, MIT) ; reste portage des connecteurs on-chain Smart Money read-only dans K5 et retrait gitlink.)
- **Principe** : Interface CLI agent-first d'analyse on-chain et de suivi des flux Smart Money.
- **Invariants** : Exposition strictement limitée aux endpoints analytiques en lecture seule (aucun swap/transfert autonome : règle `a2p` Scion).
- **Interfaces** : CLI `nansen` read-only -> flux Smart Money JSON.
- **Perte au Retrait & Conflits** : Perte sans fusion : perte des signaux on-chain institutionnels. Conflit : capacité swap/trading DEX vs lecture seule -> ADR-07. (*Arbitrage : ADR-07*)

### M074 — `tradingview-indicator-search-mcp-server` (GITLINK)
- **Provenance & Sources Brutes Lues** : chemin `01_Forkable/FKB07_Money_Maker/01_Trading/tradingview-indicator-search-mcp-server` | repo `https://github.com/Amdkn/tradingview-indicator-search-mcp-server.git` | SHA/pin `cde68c7265ca` | licence `MIT` | sources : `01_Forkable/FKB07_Money_Maker/01_Trading/tradingview-indicator-search-mcp-server/README.md`, `01_Forkable/FKB07_Money_Maker/01_Trading/tradingview-indicator-search-mcp-server/package.json`
- **Noyau Cible & Destination ÉNONCÉ §1(1)** : **CORPS · Organe K5 (Métabolisme B2B, Vidéo & Finance S0)** · Destination : **`FUSIONNÉ`** · Statut Vérifié (§5.8) : **`FUSIONNÉ`** (Portage 1:1 dans `aspace_trading_copilot_foundation.py` prouvé en différentiel `==` vs Node v24 sur 6 fixtures avant/après suppression physique en `iso_root` + 20 sabotages + reçu R10 ; gitlink conservé pour Phase A oracle amont.)
- **Principe** : Recherche et extraction directe du code source Pine Script d'indicateurs publics via MCP sans hallucination de syntaxe.
- **Invariants** : Lecture seule ; citation exacte de l'indicateur source.
- **Interfaces** : Serveur MCP search/fetch Pine Script.
- **Perte au Retrait & Conflits** : Perte sans fusion : hallucination fréquente de syntaxe Pine Script par les LLM. Conflit : aucun -> ADR-07. (*Arbitrage : ADR-07*)

### M075 — `OpenMontage` (GITLINK)
- **Provenance & Sources Brutes Lues** : chemin `01_Forkable/FKB07_Money_Maker/02_Video/OpenMontage` | repo `https://github.com/Amdkn/OpenMontage.git` | SHA/pin `fef367879943` | licence `LICENSE fichier lu` | sources : `01_Forkable/FKB07_Money_Maker/02_Video/OpenMontage/README.md`
- **Noyau Cible & Destination ÉNONCÉ §1(1)** : **CORPS · Organe K5 (Métabolisme B2B, Vidéo & Finance S0)** · Destination : **`FUSIONNÉ`** · Statut Vérifié (§5.8) : **`PARTIEL`** (Rattaché à `aspace_video_studio_foundation.py` (F4) ; reste portage complet de la chaîne de montage e-commerce et retrait du gitlink.)
- **Principe** : Pipeline de montage vidéo agentique productisé orienté publicités courtes e-commerce à haut volume.
- **Invariants** : Rendu déterministe local/ffmpeg ; journalisation R10 des rendus livrés.
- **Interfaces** : aspace_video_studio_foundation.py -> rôle `montage_ecommerce`.
- **Perte au Retrait & Conflits** : Perte sans fusion : perte du moteur de montage publicitaire B2B. Conflit : overlap moteurs vidéo -> ADR-11. (*Arbitrage : ADR-11*)

### M076 — `argo` (GITLINK)
- **Provenance & Sources Brutes Lues** : chemin `01_Forkable/FKB07_Money_Maker/02_Video/argo` | repo `https://github.com/Amdkn/argo.git` | SHA/pin `dc0e80803772` | licence `MIT` | sources : `01_Forkable/FKB07_Money_Maker/02_Video/argo/README.md`, `01_Forkable/FKB07_Money_Maker/02_Video/argo/package.json`
- **Noyau Cible & Destination ÉNONCÉ §1(1)** : **CORPS · Organe K5 (Métabolisme B2B, Vidéo & Finance S0)** · Destination : **`FUSIONNÉ`** · Statut Vérifié (§5.8) : **`PARTIEL`** (Doublon FKB06 purgé de `.gitmodules` (F4) ; rattaché à `aspace_video_studio_foundation.py` ; reste extraction du pipeline Playwright->vidéo et retrait gitlink FKB07.)
- **Principe** : Conversion de scripts de parcours Playwright en vidéos démo produit montées avec voix off synchronisée.
- **Invariants** : Exécution headless reproductible depuis scénario Playwright typé.
- **Interfaces** : aspace_video_studio_foundation.py -> rôle `demo_playwright`.
- **Perte au Retrait & Conflits** : Perte sans fusion : perte de la capture vidéo automatisée de démos SaaS. Conflit : doublon FKB06 -> ADR-11. (*Arbitrage : ADR-11*)

### M077 — `earshot` (GITLINK)
- **Provenance & Sources Brutes Lues** : chemin `01_Forkable/FKB07_Money_Maker/02_Video/earshot` | repo `https://github.com/Amdkn/earshot.git` | SHA/pin `8812d4fc32f9` | licence `LICENSE fichier lu` | sources : `01_Forkable/FKB07_Money_Maker/02_Video/earshot/README.md`, `01_Forkable/FKB07_Money_Maker/02_Video/earshot/pyproject.toml`
- **Noyau Cible & Destination ÉNONCÉ §1(1)** : **CORPS · Organe K5 (Métabolisme B2B, Vidéo & Finance S0)** · Destination : **`FUSIONNÉ`** · Statut Vérifié (§5.8) : **`PARTIEL`** (Doublon FKB06 purgé de `.gitmodules` (F4) ; rattaché à `aspace_video_studio_foundation.py` ; reste portage du mixeur audio SFX et retrait gitlink FKB07.)
- **Principe** : Conception et synchronisation sonore (voix, musique, SFX) pilotée par agents pour accompagner les séquences visuelles.
- **Invariants** : Calage temporel exact sur timecodes ; mixage normalisé.
- **Interfaces** : aspace_video_studio_foundation.py -> rôle `audio_sfx`.
- **Perte au Retrait & Conflits** : Perte sans fusion : vidéos muettes ou désynchronisées. Conflit : doublon FKB06 -> ADR-11. (*Arbitrage : ADR-11*)

### M078 — `explainroo` (GITLINK)
- **Provenance & Sources Brutes Lues** : chemin `01_Forkable/FKB07_Money_Maker/02_Video/explainroo` | repo `https://github.com/Amdkn/explainroo.git` | SHA/pin `be4c19c43a76` | licence `MIT` | sources : `01_Forkable/FKB07_Money_Maker/02_Video/explainroo/README.md`, `01_Forkable/FKB07_Money_Maker/02_Video/explainroo/package.json`
- **Noyau Cible & Destination ÉNONCÉ §1(1)** : **CORPS · Organe K5 (Métabolisme B2B, Vidéo & Finance S0)** · Destination : **`FUSIONNÉ`** · Statut Vérifié (§5.8) : **`PARTIEL`** (Doublon FKB06 purgé de `.gitmodules` (F4) ; rattaché à `aspace_video_studio_foundation.py` ; reste extraction du moteur JS/voix locale et retrait gitlink FKB07.)
- **Principe** : Génération de vidéos explicatives narrées en pur JavaScript avec synthèse vocale locale sans clé API tierce.
- **Invariants** : Zéro dépendance à une clé API cloud payante pour la voix de base.
- **Interfaces** : aspace_video_studio_foundation.py -> rôle `explainer_local`.
- **Perte au Retrait & Conflits** : Perte sans fusion : perte du générateur de tutoriels locaux 0-API. Conflit : doublon FKB06 -> ADR-11. (*Arbitrage : ADR-11*)

### M079 — `flute` (GITLINK)
- **Provenance & Sources Brutes Lues** : chemin `01_Forkable/FKB07_Money_Maker/02_Video/flute` | repo `https://github.com/Amdkn/flute.git` | SHA/pin `2ed7b5337502` | licence `voir-source-brute` | sources : `01_Forkable/FKB07_Money_Maker/02_Video/flute/` + `01_Forkable/FKB*/index.md` + `FUSIONS-REGISTRY.md`
- **Noyau Cible & Destination ÉNONCÉ §1(1)** : **CORPS · Organe K5 (Métabolisme B2B, Vidéo & Finance S0)** · Destination : **`FUSIONNÉ`** · Statut Vérifié (§5.8) : **`PARTIEL`** (Rattaché à `aspace_video_studio_foundation.py` (F4) ; reste checkout/extraction du canvas SaaS interactif et retrait gitlink.)
- **Principe** : Studio SaaS vidéo avec canevas de montage interactif UI/UX pour édition client en self-service.
- **Invariants** : Exposition souveraine sans verrou cloud externe.
- **Interfaces** : aspace_video_studio_foundation.py -> rôle `canvas_saas`.
- **Perte au Retrait & Conflits** : Perte sans fusion : perte de l'éditeur canvas SaaS interactif. Conflit : overlap moteurs vidéo -> ADR-11. (*Arbitrage : ADR-11*)

### M080 — `huashu-motion` (GITLINK)
- **Provenance & Sources Brutes Lues** : chemin `01_Forkable/FKB07_Money_Maker/02_Video/huashu-motion` | repo `https://github.com/Amdkn/huashu-motion.git` | SHA/pin `71f4a85ed6c0` | licence `MIT` | sources : `01_Forkable/FKB07_Money_Maker/02_Video/huashu-motion/README.en.md`, `01_Forkable/FKB07_Money_Maker/02_Video/huashu-motion/package.json`
- **Noyau Cible & Destination ÉNONCÉ §1(1)** : **CORPS · Organe K5 (Métabolisme B2B, Vidéo & Finance S0)** · Destination : **`FUSIONNÉ`** · Statut Vérifié (§5.8) : **`PARTIEL`** (Doublon FKB06 purgé de `.gitmodules` (F4) ; rattaché à `aspace_video_studio_foundation.py` ; reste portage du moteur motion-design et retrait gitlink FKB07.)
- **Principe** : Création de motion graphics locaux avec son et édition ciblée par désignation de frame.
- **Invariants** : Rendu local reproductible ; itération frame-par-frame adressable.
- **Interfaces** : aspace_video_studio_foundation.py -> rôle `motion_graphics`.
- **Perte au Retrait & Conflits** : Perte sans fusion : perte de l'édition ciblée par frame en motion design. Conflit : doublon FKB06 -> ADR-11. (*Arbitrage : ADR-11*)

### M081 — `reanimate` (GITLINK)
- **Provenance & Sources Brutes Lues** : chemin `01_Forkable/FKB07_Money_Maker/02_Video/reanimate` | repo `https://github.com/Amdkn/reanimate.git` | SHA/pin `859ea61fea57` | licence `LICENSE fichier lu` | sources : `01_Forkable/FKB07_Money_Maker/02_Video/reanimate/README.md`
- **Noyau Cible & Destination ÉNONCÉ §1(1)** : **CORPS · Organe K5 (Métabolisme B2B, Vidéo & Finance S0)** · Destination : **`FUSIONNÉ`** · Statut Vérifié (§5.8) : **`PARTIEL`** (Doublon FKB06 purgé de `.gitmodules` (F4) ; rattaché à `aspace_video_studio_foundation.py` ; reste portage de l'extracteur vectoriel et retrait gitlink FKB07.)
- **Principe** : Rétro-ingénierie d'animations web/CSS/SVG existantes pour reconstruire des composants animés réutilisables.
- **Invariants** : Respect strict des droits sur les assets finaux (réutilisation du pattern technique, pas de copie brute d'image de marque).
- **Interfaces** : aspace_video_studio_foundation.py -> rôle `vector_reanimation`.
- **Perte au Retrait & Conflits** : Perte sans fusion : perte de la capture/recomposition d'animations vectorielles. Conflit : doublon FKB06 -> ADR-11. (*Arbitrage : ADR-11*)

### M082 — `rossark-motion-skill` (GITLINK)
- **Provenance & Sources Brutes Lues** : chemin `01_Forkable/FKB07_Money_Maker/02_Video/rossark-motion-skill` | repo `https://github.com/Amdkn/rossark-motion-skill.git` | SHA/pin `e4cfb15f4b7b` | licence `LICENSE fichier lu` | sources : `01_Forkable/FKB07_Money_Maker/02_Video/rossark-motion-skill/README.md`
- **Noyau Cible & Destination ÉNONCÉ §1(1)** : **CORPS · Organe K5 (Métabolisme B2B, Vidéo & Finance S0)** · Destination : **`FUSIONNÉ`** · Statut Vérifié (§5.8) : **`PARTIEL`** (Doublon FKB06 purgé de `.gitmodules` (F4) ; rattaché à `aspace_video_studio_foundation.py` ; reste intégration des primitives de personnages/scènes et retrait gitlink FKB07.)
- **Principe** : Animation programmatique de personnages/mascottes et séquences visuelles composées par code.
- **Invariants** : Rendu déterministe piloté par keyframes déclaratives.
- **Interfaces** : aspace_video_studio_foundation.py -> rôle `character_motion`.
- **Perte au Retrait & Conflits** : Perte sans fusion : perte du motion design de personnages/mascottes. Conflit : doublon FKB06 -> ADR-11. (*Arbitrage : ADR-11*)

### M083 — `take-one` (GITLINK)
- **Provenance & Sources Brutes Lues** : chemin `01_Forkable/FKB07_Money_Maker/02_Video/take-one` | repo `https://github.com/Amdkn/take-one.git` | SHA/pin `42d23679bf3f` | licence `MIT` | sources : `01_Forkable/FKB07_Money_Maker/02_Video/take-one/README.md`, `01_Forkable/FKB07_Money_Maker/02_Video/take-one/package.json`
- **Noyau Cible & Destination ÉNONCÉ §1(1)** : **CORPS · Organe K5 (Métabolisme B2B, Vidéo & Finance S0)** · Destination : **`FUSIONNÉ`** · Statut Vérifié (§5.8) : **`PARTIEL`** (Doublon FKB06 purgé de `.gitmodules` (F4) ; rattaché à `aspace_video_studio_foundation.py` ; reste portage du pipeline Chrome headless + ffmpeg et retrait gitlink FKB07.)
- **Principe** : Production de courts-métrages de lancement depuis une phrase unique via équipe de rôles virtuels et rendu par code (headless Chrome + ffmpeg).
- **Invariants** : Zéro rendu propriétaire fermé ; tout est reproductible via navigateur headless + ffmpeg.
- **Interfaces** : aspace_video_studio_foundation.py -> rôle `launch_film`.
- **Perte au Retrait & Conflits** : Perte sans fusion : perte du pipeline script->rendu par code headless Chrome+ffmpeg. Conflit : doublon FKB06 -> ADR-11. (*Arbitrage : ADR-11*)

### M084 — `video-director` (GITLINK)
- **Provenance & Sources Brutes Lues** : chemin `01_Forkable/FKB07_Money_Maker/02_Video/video-director` | repo `https://github.com/Amdkn/video-director.git` | SHA/pin `6e67b886bb2f` | licence `LICENSE fichier lu` | sources : `01_Forkable/FKB07_Money_Maker/02_Video/video-director/README.md`
- **Noyau Cible & Destination ÉNONCÉ §1(1)** : **CORPS · Organe K5 (Métabolisme B2B, Vidéo & Finance S0)** · Destination : **`FUSIONNÉ`** · Statut Vérifié (§5.8) : **`FUSIONNÉ`** (Scripts `check_timeline.py` & fonctions d'analyse `qa_video.py` portés 1:1 dans `01_Forkable/FKB07_Money_Maker/02_Video/aspace_video_studio_foundation.py` (`vd_validate_timeline`, `vd_check_timeline_cli`, `vd_analyse_picture`, `vd_compare_cuts`, `vd_measure_text`, `vd_load_timeline`, `vd_beat_times`, `vd_runs`) ; test différentiel + sabotage sur chaque fonction avant/après suppression physique PASS (gitlink conservé en attente du verdict Juge Cycle 6).)
- **Principe** : Orchestration de découpage technique, cadrage, rythmes et transitions entre plans par agent réalisateur.
- **Invariants** : Sortie storyboard/timeline structurée consommable par les moteurs de rendu.
- **Interfaces** : aspace_video_studio_foundation.py -> rôle `director_storyboard`.
- **Perte au Retrait & Conflits** : Perte sans fusion : manque de cohérence narrative entre scènes générées séparément. Conflit : doublon FKB06 -> ADR-11. (*Arbitrage : ADR-11*)

### M085 — `changedetection.io` (GITLINK)
- **Provenance & Sources Brutes Lues** : chemin `01_Forkable/FKB07_Money_Maker/03_Website_and_Infra/changedetection.io` | repo `https://github.com/Amdkn/changedetection.io.git` | SHA/pin `f0d955ff19c7` | licence `LICENSE fichier lu` | sources : `01_Forkable/FKB07_Money_Maker/03_Website_and_Infra/changedetection.io/README-pip.md`
- **Noyau Cible & Destination ÉNONCÉ §1(1)** : **CORPS · Organe K5 (Métabolisme B2B, Vidéo & Finance S0)** · Destination : **`RETENU`** · Statut Vérifié (§5.8) : **`RETENU`** (RETENU (Justification de fondation : serveur Python/Flask complet de surveillance de pages web et appels d'offres avec diffing historique — moteur d'infrastructure produit B2B).)
- **Principe** : Détection continue de changements sur pages web et portails d'appels d'offres publics avec alertes différentielles.
- **Invariants** : Respect des limites de débit et robots ; zéro contournement anti-bot CAPTCHA.
- **Interfaces** : Service Web/API changedetection.io -> webhooks événements vers K2/K5.
- **Perte au Retrait & Conflits** : Perte si écarté : perte de la brique de veille B2B marchés publics (350$/mois). Conflit : polling vs événement -> ADR-01. (*Arbitrage : ADR-01*)

### M086 — `impeccable` (GITLINK)
- **Provenance & Sources Brutes Lues** : chemin `01_Forkable/FKB07_Money_Maker/03_Website_and_Infra/impeccable` | repo `https://github.com/Amdkn/impeccable.git` | SHA/pin `4bafcb3cc8f4` | licence `Apache-2.0` | sources : `01_Forkable/FKB07_Money_Maker/03_Website_and_Infra/impeccable/README.md`, `01_Forkable/FKB07_Money_Maker/03_Website_and_Infra/impeccable/package.json`, `01_Forkable/FKB07_Money_Maker/03_Website_and_Infra/impeccable/Cargo.toml`
- **Noyau Cible & Destination ÉNONCÉ §1(1)** : **CORPS · Organe K5 (Métabolisme B2B, Vidéo & Finance S0)** · Destination : **`FUSIONNÉ`** · Statut Vérifié (§5.8) : **`PARTIEL`** (Actif FKB07/03 (Apache-2.0) ; reste intégration de ses règles d'audit anti-Look-IA dans les skills frontend K4/K5 et retrait gitlink.)
- **Principe** : Vocabulaire de design frontend et détecteur d'anti-patterns IA (`polish`, `critique`, `audit`) pour éliminer le rendu générique « AI slop ».
- **Invariants** : Audit visuel/UX systématique avant livraison de toute vitrine B2B.
- **Interfaces** : Commandes/skills design `polish`, `bolder`, `critique`, `audit`.
- **Perte au Retrait & Conflits** : Perte sans fusion : vitrines B2B génériques à faible conversion. Conflit : aucun -> ADR-10. (*Arbitrage : ADR-10*)

### M087 — `uptime-kuma` (GITLINK)
- **Provenance & Sources Brutes Lues** : chemin `01_Forkable/FKB07_Money_Maker/03_Website_and_Infra/uptime-kuma` | repo `https://github.com/Amdkn/uptime-kuma.git` | SHA/pin `0e05943e1b6d` | licence `MIT` | sources : `01_Forkable/FKB07_Money_Maker/03_Website_and_Infra/uptime-kuma/README.md`, `01_Forkable/FKB07_Money_Maker/03_Website_and_Infra/uptime-kuma/package.json`
- **Noyau Cible & Destination ÉNONCÉ §1(1)** : **CORPS · Organe K5 (Métabolisme B2B, Vidéo & Finance S0)** · Destination : **`RETENU`** · Statut Vérifié (§5.8) : **`RETENU`** (RETENU (Justification de fondation : outil complet de monitoring SSL/HTTP/TCP Node.js auto-hébergé avec base SQLite et dashboard client — offre B2B clé en main 99$/mois).)
- **Principe** : Surveillance permanente de disponibilité, certificats SSL et latence de services web avec pages de statut.
- **Invariants** : Auto-hébergement souverain sans dépendance SaaS ; alertes raccordées aux webhooks K2.
- **Interfaces** : Dashboard/API Uptime Kuma + sondes HTTP/TCP/SSL.
- **Perte au Retrait & Conflits** : Perte si écarté : perte de l'offre produit Wholesale Uptime de The OMK Office. Conflit : polling -> ADR-01. (*Arbitrage : ADR-01*)

### M088 — `DeepTutor` (GITLINK)
- **Provenance & Sources Brutes Lues** : chemin `01_Forkable/FKB07_Money_Maker/04_Learning/DeepTutor` | repo `https://github.com/Amdkn/DeepTutor.git` | SHA/pin `547dbb4dd591` | licence `LICENSE fichier lu` | sources : `01_Forkable/FKB07_Money_Maker/04_Learning/DeepTutor/README.md`, `01_Forkable/FKB07_Money_Maker/04_Learning/DeepTutor/pyproject.toml`
- **Noyau Cible & Destination ÉNONCÉ §1(1)** : **CORPS · Organe K5 (Métabolisme B2B, Vidéo & Finance S0)** · Destination : **`FUSIONNÉ`** · Statut Vérifié (§5.8) : **`PARTIEL`** (Actif FKB07/04 ; reste intégration de son moteur pédagogique RAG/tuteur dans K5/K4 et retrait gitlink.)
- **Principe** : Tuteur IA interactif personnalisé exploitant les supports de cours pour générer parcours d'apprentissage, exercices et remédiations.
- **Invariants** : Ancrage strict sur les documents sources du client (zéro hallucination pédagogique) ; passage par gateway K3.
- **Interfaces** : Pipeline DeepTutor ingestion cours -> session tutorat interactive.
- **Perte au Retrait & Conflits** : Perte sans fusion : perte de l'offre produit B2B Éducation/Formation. Conflit : RAG vectoriel vs citation vérifiée -> ADR-04. (*Arbitrage : ADR-04*)

### M089 — `open-notebook` (GITLINK)
- **Provenance & Sources Brutes Lues** : chemin `01_Forkable/FKB07_Money_Maker/04_Learning/open-notebook` | repo `https://github.com/Amdkn/open-notebook.git` | SHA/pin `982f74ecd20c` | licence `LICENSE fichier lu` | sources : `01_Forkable/FKB07_Money_Maker/04_Learning/open-notebook/README.dev.md`, `01_Forkable/FKB07_Money_Maker/04_Learning/open-notebook/pyproject.toml`
- **Noyau Cible & Destination ÉNONCÉ §1(1)** : **CORPS · Organe K5 (Métabolisme B2B, Vidéo & Finance S0)** · Destination : **`FUSIONNÉ`** · Statut Vérifié (§5.8) : **`PARTIEL`** (Actif FKB07/04 ; reste unification de sa synthèse audio multi-locuteurs sur documents avec K5/K3 et retrait gitlink.)
- **Principe** : Synthèse de carnets de recherche multi-sources et génération de podcasts d'entreprise hebdomadaires auto-hébergés.
- **Invariants** : Souveraineté des documents clients ; exécution sur LLM/TTS routés via K3.
- **Interfaces** : Service notebook/podcast -> audio MP3 + notes sourcées.
- **Perte au Retrait & Conflits** : Perte sans fusion : perte du produit B2B Podcast d'entreprise clé en main. Conflit : aucun -> ADR-08. (*Arbitrage : ADR-08*)

### M090 — `OpenMausBot` (GITLINK)
- **Provenance & Sources Brutes Lues** : chemin `01_Forkable/FKB07_Money_Maker/05_Executive_and_BI/OpenMausBot` | repo `https://github.com/Amdkn/OpenMausBot.git` | SHA/pin `059275a68c86` | licence `Apache-2.0` | sources : `01_Forkable/FKB07_Money_Maker/05_Executive_and_BI/OpenMausBot/README.md`, `01_Forkable/FKB07_Money_Maker/05_Executive_and_BI/OpenMausBot/package.json`
- **Noyau Cible & Destination ÉNONCÉ §1(1)** : **CORPS · Organe K5 (Métabolisme B2B, Vidéo & Finance S0)** · Destination : **`FUSIONNÉ`** · Statut Vérifié (§5.8) : **`PARTIEL`** (Actif FKB07/05 (Apache-2.0) ; reste alignement de l'interface de chat multi-bots locaux sur la plateforme bots RigInfinity/K2 et retrait gitlink.)
- **Principe** : Application de chat local-first permettant à une équipe de direction de piloter une escouade d'agents spécialisés en local.
- **Invariants** : Données locales prioritaires ; zéro fuite externe ; gouvernance K1.
- **Interfaces** : App chat locale multi-bots -> routage gateway `:31415`.
- **Perte au Retrait & Conflits** : Perte sans fusion : perte de l'emballage UX dirigeant local-first pour l'offre B2B Direction. Conflit : duplication avec OpenBot/RigInfinity -> ADR-02. (*Arbitrage : ADR-02*)

### M091 — `Scrapling` (GITLINK)
- **Provenance & Sources Brutes Lues** : chemin `01_Forkable/FKB07_Money_Maker/05_Executive_and_BI/Scrapling` | repo `https://github.com/Amdkn/Scrapling.git` | SHA/pin `bc602488b44e` | licence `LICENSE fichier lu` | sources : `01_Forkable/FKB07_Money_Maker/00_A0_Core/scrapling.manifest.json`, `01_Forkable/FKB07_Money_Maker/00_A0_Core/scrapling-ADAPTATION.md`, `01_Forkable/FKB07_Money_Maker/05_Executive_and_BI/Scrapling/README.md`, `01_Forkable/FKB07_Money_Maker/05_Executive_and_BI/Scrapling/pyproject.toml`
- **Noyau Cible & Destination ÉNONCÉ §1(1)** : **CORPS · Organe K5 (Métabolisme B2B, Vidéo & Finance S0)** · Destination : **`FUSIONNÉ`** · Statut Vérifié (§5.8) : **`PARTIEL`** (Adapté état 2 (`c5121c7` / `bc60248`, BSD-3-Clause) ; reste intégration comme extracteur DOM adaptatif dans K2/K5 et retrait gitlink.)
- **Principe** : Extraction web adaptative conservant la résilience face aux changements de structure DOM via apprentissage de signatures d'éléments.
- **Invariants** : Zéro contournement CAPTCHA/anti-bot ; respect de l'hygiène réseau et télémétrie zéro.
- **Interfaces** : Adaptateur Python `Scrapling` / serveur MCP `D4Vinci/Scrapling`.
- **Perte au Retrait & Conflits** : Perte sans fusion : casse répétée des extracteurs HTML à la moindre mise à jour CSS. Conflit : chevauchement partiel avec `agent-browser` -> ADR-10. (*Arbitrage : ADR-10*)

### M092 — `dify` (GITLINK)
- **Provenance & Sources Brutes Lues** : chemin `01_Forkable/FKB07_Money_Maker/05_Executive_and_BI/dify` | repo `https://github.com/Amdkn/dify.git` | SHA/pin `208a2489f05f` | licence `LICENSE fichier lu` | sources : `01_Forkable/FKB07_Money_Maker/00_A0_Core/dify.manifest.json`, `01_Forkable/FKB07_Money_Maker/00_A0_Core/dify-ADAPTATION.md`, `01_Forkable/FKB07_Money_Maker/05_Executive_and_BI/dify/README.md`, `01_Forkable/FKB07_Money_Maker/05_Executive_and_BI/dify/package.json`
- **Noyau Cible & Destination ÉNONCÉ §1(1)** : **CORPS · Organe K5 (Métabolisme B2B, Vidéo & Finance S0)** · Destination : **`RETENU`** · Statut Vérifié (§5.8) : **`RETENU`** (RETENU (Justification de fondation : plateforme complète LLMOps/workflow builder visuel auto-hébergée Apache-2.0 modifiée — environnement d'assemblage visuel B2B adapté état 2 `b29552a`).)
- **Principe** : Plateforme visuelle d'orchestration de workflows LLM, gestion de jeux de prompts et déploiement d'apps client B2B.
- **Invariants** : Licence Apache-2.0 modifiée respectée (mentions conservées) ; télémétrie coupée ; routage via FreeLLMAPI.
- **Interfaces** : API Workflows Dify + UI Studio auto-hébergée.
- **Perte au Retrait & Conflits** : Perte si écarté : perte de l'atelier visuel no-code livrable aux clients B2B. Conflit : orchestration parallèle à RigInfinity -> ADR-02, ADR-09. (*Arbitrage : ADR-02, ADR-09*)

### M093 — `powerbi-to-ai-visuals` (GITLINK)
- **Provenance & Sources Brutes Lues** : chemin `01_Forkable/FKB07_Money_Maker/05_Executive_and_BI/powerbi-to-ai-visuals` | repo `https://github.com/Amdkn/powerbi-to-ai-visuals.git` | SHA/pin `86583180c347` | licence `LICENSE fichier lu` | sources : `01_Forkable/FKB07_Money_Maker/05_Executive_and_BI/powerbi-to-ai-visuals/README.md`
- **Noyau Cible & Destination ÉNONCÉ §1(1)** : **CORPS · Organe K5 (Métabolisme B2B, Vidéo & Finance S0)** · Destination : **`FUSIONNÉ`** · Statut Vérifié (§5.8) : **`PARTIEL`** (Actif FKB07/05 ; reste portage de l'extracteur sémantique `.pbix` -> modèle requêtable + visuels interactifs dans K5 et retrait gitlink.)
- **Principe** : Conversion de rapports Power BI fermés en modèle de données ouvert requêtable et visualisations web dynamiques pilotes par IA.
- **Invariants** : Exactitude des agrégations numériques vérifiées contre le modèle source.
- **Interfaces** : Pipeline `.pbix` -> schéma requêtable + composants de visualisation.
- **Perte au Retrait & Conflits** : Perte sans fusion : incapacité d'ingérer et moderniser l'existant BI Power BI des clients B2B. Conflit : aucun. (*Arbitrage : ADR-04*)

### M094 — `presenton` (GITLINK)
- **Provenance & Sources Brutes Lues** : chemin `01_Forkable/FKB07_Money_Maker/05_Executive_and_BI/presenton` | repo `https://github.com/Amdkn/presenton.git` | SHA/pin `9af2b47dda31` | licence `LICENSE fichier lu` | sources : `01_Forkable/FKB07_Money_Maker/00_A0_Core/presenton.manifest.json`, `01_Forkable/FKB07_Money_Maker/00_A0_Core/presenton-ADAPTATION.md`, `01_Forkable/FKB07_Money_Maker/05_Executive_and_BI/presenton/README.md`, `01_Forkable/FKB07_Money_Maker/05_Executive_and_BI/presenton/package.json`
- **Noyau Cible & Destination ÉNONCÉ §1(1)** : **CORPS · Organe K5 (Métabolisme B2B, Vidéo & Finance S0)** · Destination : **`FUSIONNÉ`** · Statut Vérifié (§5.8) : **`PARTIEL`** (Adapté état 2 (`9af2b47`, Apache-2.0) ; reste intégration du moteur de génération de présentations PPTX/PDF dans K5 et retrait gitlink.)
- **Principe** : Générateur de présentations structurées (PPTX/PDF) piloté par contenu métier avec gabarits contrôlés.
- **Invariants** : Zéro télémétrie ; modèles routés via K3 ; conformité données.
- **Interfaces** : API/CLI Presenton -> livrable `.pptx` / `.pdf`.
- **Perte au Retrait & Conflits** : Perte sans fusion : perte de la génération automatisée de decks clients et rapports exécutifs. Conflit : aucun -> ADR-08. (*Arbitrage : ADR-08*)

### M095 — `BlenderWorld` (GITLINK)
- **Provenance & Sources Brutes Lues** : chemin `01_Forkable/FKB07_Money_Maker/06_3D_and_CAD/BlenderWorld` | repo `https://github.com/Amdkn/BlenderWorld.git` | SHA/pin `9a37086deca2` | licence `LICENSE fichier lu` | sources : `01_Forkable/FKB07_Money_Maker/06_3D_and_CAD/BlenderWorld/README.md`, `01_Forkable/FKB07_Money_Maker/06_3D_and_CAD/BlenderWorld/pyproject.toml`
- **Noyau Cible & Destination ÉNONCÉ §1(1)** : **CORPS · Organe K5 (Métabolisme B2B, Vidéo & Finance S0)** · Destination : **`FUSIONNÉ`** · Statut Vérifié (§5.8) : **`PARTIEL`** (Actif FKB07/06 ; reste intégration de la boucle `Render-Critique-Refine` (`bpy` -> `.glb`) dans K5/K2 et retrait gitlink.)
- **Principe** : Génération procédurale de scènes et d'actifs 3D via Python Blender (`bpy`) par boucle itérative Render-Critique-Refine exportant en `.glb`.
- **Invariants** : Vérification visuelle des rendus intermédiaires ; export standardisé `.glb`.
- **Interfaces** : Pipeline `bpy` -> rendu critique -> `.glb` pour City Office / CubeFarm.
- **Perte au Retrait & Conflits** : Perte sans fusion : perte du pipeline de création d'assets 3D procéduraux pour les mondes K2 et offres B2B. Conflit : aucun. (*Arbitrage : ADR-02*)

### M096 — `text-to-cad` (GITLINK)
- **Provenance & Sources Brutes Lues** : chemin `01_Forkable/FKB07_Money_Maker/06_3D_and_CAD/text-to-cad` | repo `https://github.com/Amdkn/text-to-cad.git` | SHA/pin `333d8af79341` | licence `LICENSE fichier lu` | sources : `01_Forkable/FKB07_Money_Maker/06_3D_and_CAD/text-to-cad/README.md`, `01_Forkable/FKB07_Money_Maker/06_3D_and_CAD/text-to-cad/package.json`
- **Noyau Cible & Destination ÉNONCÉ §1(1)** : **CORPS · Organe K5 (Métabolisme B2B, Vidéo & Finance S0)** · Destination : **`FUSIONNÉ`** · Statut Vérifié (§5.8) : **`PARTIEL`** (Actif FKB07/06 ; reste intégration du synthétiseur paramétrique CAO dans K5 et retrait gitlink.)
- **Principe** : Synthèse de pièces mécaniques 3D paramétriques (STEP/STL/GLB) à partir de descriptions techniques ou contraintes géométriques.
- **Invariants** : Validation géométrique manifold avant export pour impression/usinage.
- **Interfaces** : Service/API `text-to-cad` -> modèles CAO STEP/STL.
- **Perte au Retrait & Conflits** : Perte sans fusion : perte de la verticale B2B modélisation CAO (300$/pièce). Conflit : aucun. (*Arbitrage : ADR-03*)

### M097 — `BusinessOS` (GITLINK)
- **Provenance & Sources Brutes Lues** : chemin `01_Forkable/FKB07_Money_Maker/BusinessOS` | repo `https://github.com/Amdkn/BusinessOS.git` | SHA/pin `e9f1366d357c` | licence `voir-source-brute` | sources : `01_Forkable/FKB07_Money_Maker/BusinessOS/README.md`, `01_Forkable/FKB07_Money_Maker/BusinessOS/package.json`
- **Noyau Cible & Destination ÉNONCÉ §1(1)** : **CORPS · Organe K5 (Métabolisme B2B, Vidéo & Finance S0)** · Destination : **`FUSIONNÉ`** · Statut Vérifié (§5.8) : **`PARTIEL`** (Actif FKB07 (`e9f1366`) ; bridge `_runtime/bridge/adapters.mjs` déjà référencé dans Scion/FKB00 ; reste fusion finale de ses 13 apps/contrats dans K5/Areas OS et retrait gitlink.)
- **Principe** : OS d'entreprise à 13 modules (Dashboard, Clients, Marketplace, Opérations, Finance) + protocole de négociation de surfaces `adapters.mjs`.
- **Invariants** : Aucune surface orpheline non lue (règle Scion sparse) ; `a2p` (paiement) jamais exécutable autonomement par un agent.
- **Interfaces** : _runtime/bridge/adapters.mjs (24 adaptateurs, 39/39 autotests) + aspace_marketplace_engine.py.
- **Perte au Retrait & Conflits** : Perte sans fusion : perte du pont métier BusinessOS et des primitives de négociation de surfaces. Conflit : recouvrement surface avec Areas OS -> ADR-05, ADR-07. (*Arbitrage : ADR-05, ADR-07*)

### M098 — `anthropic-skills` (GITLINK)
- **Provenance & Sources Brutes Lues** : chemin `01_Forkable/FKB08_Plugins/anthropic-skills` | repo `https://github.com/Amdkn/skills.git` | SHA/pin `d267f9ab8ab7` | licence `voir-source-brute` | sources : `01_Forkable/FKB08_Plugins/anthropic-skills/README.md`
- **Noyau Cible & Destination ÉNONCÉ §1(1)** : **ÂME · Organe K4 (Mémoire & Skills)** · Destination : **`FUSIONNÉ`** · Statut Vérifié (§5.8) : **`PARTIEL`** (Pattern déjà adopté dans `.agents/skills/` et `.claude/skills/` ; reste consolidation dans le registre unique de skills K4 et retrait du gitlink.)
- **Principe** : Standard `SKILL.md` à divulgation progressive (frontmatter court -> corps -> ressources/scripts) et patron d'évaluation `skill-creator`.
- **Invariants** : Chargement paresseux (progressive disclosure) pour sanctuariser le contexte ; structure dossier reproductible.
- **Interfaces** : Format `SKILL.md` YAML + `scripts/` + `references/`.
- **Perte au Retrait & Conflits** : Perte sans fusion : perte du standard structurel de compétences modulaires. Conflit : 4 catalogues de skills/plugins concurrents -> ADR-10, ADR-11. (*Arbitrage : ADR-10, ADR-11*)

### M099 — `claude-video` (GITLINK)
- **Provenance & Sources Brutes Lues** : chemin `01_Forkable/FKB08_Plugins/claude-video` | repo `https://github.com/Amdkn/claude-video.git` | SHA/pin `4a088ceb310b` | licence `LICENSE fichier lu` | sources : `01_Forkable/FKB08_Plugins/00_A0_Core/claude-video.manifest.json`, `01_Forkable/FKB08_Plugins/00_A0_Core/claude-video-ADAPTATION.md`, `01_Forkable/FKB08_Plugins/claude-video/README.md`
- **Noyau Cible & Destination ÉNONCÉ §1(1)** : **ÂME · Organe K4 (Mémoire & Skills)** · Destination : **`FUSIONNÉ`** · Statut Vérifié (§5.8) : **`PARTIEL`** (Adapté état 2 (`03ceb42` / `4a088ce`, MIT) ; skill `/watch` déjà intégré dans `.agents/skills/watch` ; reste retrait du gitlink après vérification de suppression.)
- **Principe** : Ingestion vidéo Dual-Engine : extraction locale économique (ffmpeg I-frames + WhisperX) ou analyse vidéo native pour transformer une vidéo en preuve horodatée.
- **Invariants** : Triage épistémique strict : « Comment » -> Super-Skill, « Quoi » -> Mémoire K4 ; zéro token gaspillé sur les frames brutes.
- **Interfaces** : Skill `watch` / `msci-primitives-weighting` / `omni-compiler`.
- **Perte au Retrait & Conflits** : Perte sans fusion : cécité des agents face aux tutoriels/preuves vidéo. Conflit : overlap catalogue skills -> ADR-10. (*Arbitrage : ADR-10*)

### M100 — `mattpocock-skills` (GITLINK)
- **Provenance & Sources Brutes Lues** : chemin `01_Forkable/FKB08_Plugins/mattpocock-skills` | repo `https://github.com/Amdkn/mattpocock-skills.git` | SHA/pin `bbf8902c4ff2` | licence `MIT` | sources : `01_Forkable/FKB08_Plugins/00_A0_Core/mattpocock-skills.manifest.json`, `01_Forkable/FKB08_Plugins/00_A0_Core/mattpocock-skills-ADAPTATION.md`, `01_Forkable/FKB08_Plugins/mattpocock-skills/README.md`, `01_Forkable/FKB08_Plugins/mattpocock-skills/package.json`
- **Noyau Cible & Destination ÉNONCÉ §1(1)** : **ÂME · Organe K4 (Mémoire & Skills)** · Destination : **`FUSIONNÉ`** · Statut Vérifié (§5.8) : **`PARTIEL`** (Adapté état 2 (`4ae2317` / `bbf8902`, MIT) ; principes déjà distillés dans `.agents/skills/skill-creator` ; reste fusion dans le catalogue unique K4 et retrait gitlink.)
- **Principe** : Conventions d'ingénierie logicielle non-présomptive (vérification de types, TDD vertical, zéro duplication, refactoring local).
- **Invariants** : Aucune implémentation spéculative ; vérification explicite des contrats TypeScript/tests.
- **Interfaces** : Skills d'ingénierie TypeScript/TDD.
- **Perte au Retrait & Conflits** : Perte sans fusion : baisse de qualité chirurgicale sur le code produit. Conflit : fusion catalogue skills -> ADR-10, ADR-11. (*Arbitrage : ADR-10, ADR-11*)

### M101 — `openai-plugins` (GITLINK)
- **Provenance & Sources Brutes Lues** : chemin `01_Forkable/FKB08_Plugins/openai-plugins` | repo `https://github.com/Amdkn/openai-plugins.git` | SHA/pin `fad12227eaa7` | licence `voir-source-brute` | sources : `01_Forkable/FKB08_Plugins/00_A0_Core/openai-plugins.manifest.json`, `01_Forkable/FKB08_Plugins/00_A0_Core/openai-plugins-ADAPTATION.md`, `01_Forkable/FKB08_Plugins/openai-plugins/README.md`
- **Noyau Cible & Destination ÉNONCÉ §1(1)** : **ÂME · Organe K4 (Mémoire & Skills)** · Destination : **`RETENU`** · Statut Vérifié (§5.8) : **`RETENU`** (RETENU (Justification de fondation : collection de spécifications/exemples de plugins Codex sans licence amont — règle D12 Clean-Room : gardée en référence externe seule, zéro copie de code).)
- **Principe** : Patron de déclaration de plugins Codex (`plugins/<name>/` avec manifestes d'outils et compétences associées).
- **Invariants** : D12 Clean-Room stricte (sans licence amont) : zéro copie/importation de fichiers dans le code natif.
- **Interfaces** : Spécification de référence `plugins/<name>/`.
- **Perte au Retrait & Conflits** : Perte si écarté : perte de la référence d'interopérabilité avec l'écosystème de plugins Codex. Conflit : absence de licence -> ADR-09. (*Arbitrage : ADR-09*)

### M102 — `OpenDots` (F8_UNPINNED)
- **Provenance & Sources Brutes Lues** : chemin `01_Forkable/FKB00_Runtime/06_Sovereign_Bot_Coworkers/OpenDots` | repo `interne A'Space` | SHA/pin `natif/dossie` | licence `MIT` | sources : `01_Forkable/FKB00_Runtime/00_A0_Core/OpenDots.manifest.json`, `01_Forkable/FKB00_Runtime/00_A0_Core/OpenDots-ADAPTATION.md`, `01_Forkable/FKB00_Runtime/06_Sovereign_Bot_Coworkers/OpenDots/README.md`, `01_Forkable/FKB00_Runtime/06_Sovereign_Bot_Coworkers/OpenDots/package.json`
- **Noyau Cible & Destination ÉNONCÉ §1(1)** : **CORPS · Organe K2 (Exécution, Anything & 3D)** · Destination : **`FUSIONNÉ`** · Statut Vérifié (§5.8) : **`FUSIONNÉ`** (Skin/trait « coworkers always-on » porté dans `RigInfinity` (`bots_proof`) ; source retirée F8 pas 7 ; `cargo test` 100 % vert et preuve de suppression PASS.)
- **Principe** : Coéquipiers permanents traversant canaux synchrones et asynchrones (texte, appels, Slack) avec règle Review-Before-Saving.
- **Invariants** : Revue obligatoire avant sauvegarde persistante ; aucun processus autonome hors contrôle RigInfinity.
- **Interfaces** : Trait OpenDots dans RigInfinity / canaux Threads & Channels.
- **Perte au Retrait & Conflits** : Perte sans fusion : perte du pont multicanal synchrone/asynchrone des coworkers. Conflit : multi-daemons vs daemon unique -> ADR-02. (*Arbitrage : ADR-02*)

### M103 — `OpenDuet` (F8_UNPINNED)
- **Provenance & Sources Brutes Lues** : chemin `01_Forkable/FKB00_Runtime/06_Sovereign_Bot_Coworkers/OpenDuet` | repo `interne A'Space` | SHA/pin `natif/dossie` | licence `MIT` | sources : `01_Forkable/FKB00_Runtime/00_A0_Core/OpenDuet.manifest.json`, `01_Forkable/FKB00_Runtime/00_A0_Core/OpenDuet-ADAPTATION.md`, `01_Forkable/FKB00_Runtime/06_Sovereign_Bot_Coworkers/OpenDuet/README.md`, `01_Forkable/FKB00_Runtime/06_Sovereign_Bot_Coworkers/OpenDuet/package.json`
- **Noyau Cible & Destination ÉNONCÉ §1(1)** : **CORPS · Organe K2 (Exécution, Anything & 3D)** · Destination : **`FUSIONNÉ`** · Statut Vérifié (§5.8) : **`FUSIONNÉ`** (Skin/trait « agent proactif » porté dans `RigInfinity` (`bots_proof`) ; source retirée F8 pas 7 ; `cargo test` 100 % vert et preuve de suppression PASS.)
- **Principe** : Agent proactif bâti sur le socle OpenBot exécutant les tâches de fond tout en maintenant l'humain dans la boucle sur les points d'arbitrage.
- **Invariants** : Copie vendue OpenDuet 0.2.0 abandonnée avec preuve ; zéro télémétrie.
- **Interfaces** : Trait OpenDuet dans RigInfinity / bots_proof.
- **Perte au Retrait & Conflits** : Perte sans fusion : perte du schéma d'escalade proactive vers S0. Conflit : duplication plateforme OpenBot -> ADR-02, ADR-11. (*Arbitrage : ADR-02, ADR-11*)

### M104 — `agent-zero` (F8_UNPINNED)
- **Provenance & Sources Brutes Lues** : chemin `F8/agent-zero` | repo `Amdkn/agent-zero` | SHA/pin `a042ddde19e5` | licence `NOASSERTION` | sources : `01_Forkable/FKB00_Runtime/00_A0_Core/agent-zero.manifest.json`, `01_Forkable/FKB00_Runtime/00_A0_Core/agent-zero-ADAPTATION.md`, `01_Forkable/MODULES-LOCK.json`
- **Noyau Cible & Destination ÉNONCÉ §1(1)** : **CORPS · Organe K2 (Exécution, Anything & 3D)** · Destination : **`FUSIONNÉ`** · Statut Vérifié (§5.8) : **`FUSIONNÉ`** (Boucle agentique, client gateway-only et scheduler portés dans `RigInfinity` (`agent_zero_proof`) ; source retirée F8 pas 5 ; `cargo test` 100 % vert et preuve de suppression PASS.)
- **Principe** : Moteur d'exécution autonome disposant d'un espace système complet (terminal, fichiers, navigateur, sous-tâches) subordonné à la constitution A0.
- **Invariants** : Zéro appel sortant télémétrique (abandon contrôle api.agent-zero.ai) ; modèle routé via gateway :31415 exclusivement.
- **Interfaces** : agent.rs (430 l.) / provider.rs (http://127.0.0.1:31415/v1/chat/completions) / job.rs.
- **Perte au Retrait & Conflits** : Perte sans fusion : absence de boucle d'exécution système générique sous la doctrine. Conflit : boucle monolithique vs fibers modulaires -> ADR-02, ADR-08. (*Arbitrage : ADR-02, ADR-08*)

### M105 — `automaton` (F8_UNPINNED)
- **Provenance & Sources Brutes Lues** : chemin `01_Forkable/FKB00_Runtime/01_Holo_TriptyqueCore/automaton` | repo `Amdkn/automaton` | SHA/pin `7cdaa00fb746` | licence `MIT` | sources : `01_Forkable/FKB00_Runtime/00_A0_Core/automaton.manifest.json`, `01_Forkable/FKB00_Runtime/00_A0_Core/automaton-ADAPTATION.md`, `01_Forkable/FKB00_Runtime/01_Holo_TriptyqueCore/automaton/README.md`, `01_Forkable/FKB00_Runtime/01_Holo_TriptyqueCore/automaton/package.json`, `01_Forkable/MODULES-LOCK.json`
- **Noyau Cible & Destination ÉNONCÉ §1(1)** : **ÂME · Organe K1 (Gouvernance & RSI)** · Destination : **`FUSIONNÉ`** · Statut Vérifié (§5.8) : **`PARTIEL`** (Doctrine/templates portés et gitlink retiré F8 pas 8 ; part manquante : `riginfinity.manifest.json` indique `lease: PENDING — baux = Automaton, P3, non implémentés dans RigInfinity`.)
- **Principe** : Souveraineté CEO 24/7 incarnée : boucle ReAct bornée par constitution inviolable, baux TTL et réserve d'inférence locale/gratuite.
- **Invariants** : Mort par marché (0 USDC) inapplicable (substituée par perte de confiance S0) ; sanctuaire nocturne 00h-05h ; budget borné.
- **Interfaces** : AutomatonReserveState / Heartbeat checklist / SOUL.md / lease_ttl_seconds=300 / constitution.md.
- **Perte au Retrait & Conflits** : Perte sans fusion : absence de gouvernance constitutionnelle et de budgets de survie sur les agents. Conflit : cron 30min vs réveil événementiel -> ADR-01. (*Arbitrage : ADR-01, ADR-02*)

### M106 — `cordis` (F8_UNPINNED)
- **Provenance & Sources Brutes Lues** : chemin `F8/cordis` | repo `Amdkn/cordis` | SHA/pin `a40cc749c0a7` | licence `MIT` | sources : `01_Forkable/FKB00_Runtime/00_A0_Core/cordis.manifest.json`, `01_Forkable/FKB00_Runtime/00_A0_Core/cordis-ADAPTATION.md`, `01_Forkable/MODULES-LOCK.json`
- **Noyau Cible & Destination ÉNONCÉ §1(1)** : **SYSTÈME NERVEUX · Bus L0 & Fibres** · Destination : **`FUSIONNÉ`** · Statut Vérifié (§5.8) : **`PARTIEL`** (Gitlink retiré F8 pas 8 ; part manquante : `aspace-fiber-host/package.json` référence encore `file:../cordis/*` (inexistant sur disque) et le socket Unix `cordis_socket` vers RigInfinity est `PENDING`.)
- **Principe** : Composabilité spatio-temporelle : tout composant est une Fiber dotée de co-effets réactifs (PENDING si dépendance absente) et d'une pile de nettoyage réversible.
- **Invariants** : Zéro crash en cascade lors du redémarrage d'un service amont ; disposition LIFO atomique sur arrêt ; adresse fiber:a0:* unique.
- **Interfaces** : Context.plugin / fiber_id / coeffects[] / cleanup_stack / on_dispose() (porté dans aspace-fiber-host/src/host.ts et a0_recursive_factory.py).
- **Perte au Retrait & Conflits** : Perte sans fusion : couplage dur au démarrage et fuites d'état sur arrêt partiel. Conflit : silos CLI hétérogènes vs bus de fibres -> ADR-10. (*Arbitrage : ADR-10*)

### M107 — `herdr-core` (F8_UNPINNED)
- **Provenance & Sources Brutes Lues** : chemin `F8/herdr-core` | repo `interne A'Space` | SHA/pin `natif/dossie` | licence `voir-source-brute` | sources : `01_Forkable/FKB00_Runtime/00_A0_Core/herdr-core.manifest.json`, `01_Forkable/FKB00_Runtime/00_A0_Core/herdr-core-ADAPTATION.md`
- **Noyau Cible & Destination ÉNONCÉ §1(1)** : **CORPS · Organe K2 (Exécution, Anything & 3D)** · Destination : **`FUSIONNÉ`** · Statut Vérifié (§5.8) : **`FUSIONNÉ`** (Transport PTY/socket porté dans `RigInfinity` (`openrig_terminal.rs` + `pty_proof`) ; source retirée F8 pas 8 ; `cargo test` 100 % vert et preuve de suppression PASS.)
- **Principe** : Gestionnaire de terminaux persistants multiplexés avec protocole JSON-RPC client/serveur pour envoyer, attendre et relire les sorties d'agents.
- **Invariants** : Zéro daemon `hc` concurrent au daemon maître RigInfinity ; zéro appel réseau externe (strace 0 connect hors loopback) ; notes=false, version_check=false.
- **Interfaces** : hc ls|send|wait|read|run --bg / openrig_terminal.rs (socket UNIX/loopback).
- **Perte au Retrait & Conflits** : Perte sans fusion : perte du contrôle déterministe des PTY persistants. Conflit : second daemon persistant vs daemon unique RigInfinity -> ADR-02. (*Arbitrage : ADR-02*)

### M108 — `infinity` (F8_UNPINNED)
- **Provenance & Sources Brutes Lues** : chemin `01_Forkable/FKB00_Runtime/01_Holo_TriptyqueCore/infinity` | repo `Amdkn/infinity` | SHA/pin `007409e242f2` | licence `Apache-2.0` | sources : `01_Forkable/FKB00_Runtime/00_A0_Core/infinity.manifest.json`, `01_Forkable/FKB00_Runtime/00_A0_Core/infinity-ADAPTATION.md`, `01_Forkable/FKB00_Runtime/01_Holo_TriptyqueCore/infinity/README.md`, `01_Forkable/FKB00_Runtime/01_Holo_TriptyqueCore/infinity/Cargo.toml`, `01_Forkable/MODULES-LOCK.json`
- **Noyau Cible & Destination ÉNONCÉ §1(1)** : **SYSTÈME NERVEUX · Bus L0 & Fibres** · Destination : **`FUSIONNÉ`** · Statut Vérifié (§5.8) : **`FUSIONNÉ`** (Pure Data / hibernation / RAP portés en Rust dans `RigInfinity` (`crates/infinity-daemon`) ; source retirée F8 pas 8 ; `cargo test` sur `RigInfinity` 100 % vert (WSL2 Linux) et preuve de suppression PASS.)
- **Principe** : Pure Data Between Turns : entre deux tours, l'agent est uniquement un état sérialisé à coût CPU/RAM nul ; outils découplés via Reactive Agent Protocol (RAP).
- **Invariants** : Aucun thread bloqué entre deux événements ; réveil uniquement sur trigger ; capacité 75k agents frugaux sans saturation.
- **Interfaces** : SessionRapManager / rap.rs / rap_callback.rs / rap_servers.rs / session_store.rs (hibernation idle -> shut_down).
- **Perte au Retrait & Conflits** : Perte sans fusion : effondrement mémoire dès qu'on héberge les 578 Holons. Conflit : multi-processus actifs permanents vs hibernation pure-data -> ADR-01, ADR-02. (*Arbitrage : ADR-01, ADR-02*)

### M109 — `openbot` (F8_UNPINNED)
- **Provenance & Sources Brutes Lues** : chemin `01_Forkable/FKB00_Runtime/06_Sovereign_Bot_Coworkers/openbot` | repo `interne A'Space` | SHA/pin `natif/dossie` | licence `MIT` | sources : `01_Forkable/FKB00_Runtime/00_A0_Core/openbot.manifest.json`, `01_Forkable/FKB00_Runtime/00_A0_Core/openbot-ADAPTATION.md`, `01_Forkable/FKB00_Runtime/06_Sovereign_Bot_Coworkers/openbot/README.md`, `01_Forkable/FKB00_Runtime/06_Sovereign_Bot_Coworkers/openbot/package.json`
- **Noyau Cible & Destination ÉNONCÉ §1(1)** : **CORPS · Organe K2 (Exécution, Anything & 3D)** · Destination : **`FUSIONNÉ`** · Statut Vérifié (§5.8) : **`FUSIONNÉ`** (Plateforme bots incarnés portée en Rust dans `RigInfinity` (`bots_proof`) ; source retirée F8 pas 8 ; `cargo test` 100 % vert et preuve de suppression PASS.)
- **Principe** : Coéquipiers persistants incarnés : chacun possède son workspace, son ordinateur virtuel et son navigateur avec reprise en main humaine.
- **Invariants** : Zéro télémétrie CopilotKit/PostHog ; zéro cron ; interdiction d'approvalPolicy: never ; suppression du sprawl à 10 processus/bot.
- **Interfaces** : agent-computer / AG-UI 16 adaptateurs / bots_proof.rs dans RigInfinity.
- **Perte au Retrait & Conflits** : Perte sans fusion : perte de la persistance incarnée multi-bots et du contrôle navigateur partagé. Conflit : sprawl 10 proc/bot vs daemon unique -> ADR-02, ADR-08. (*Arbitrage : ADR-02, ADR-08*)

### M110 — `openmuse` (F8_UNPINNED)
- **Provenance & Sources Brutes Lues** : chemin `01_Forkable/FKB00_Runtime/06_Sovereign_Bot_Coworkers/openmuse` | repo `interne A'Space` | SHA/pin `natif/dossie` | licence `MIT` | sources : `01_Forkable/FKB00_Runtime/00_A0_Core/openmuse.manifest.json`, `01_Forkable/FKB00_Runtime/00_A0_Core/openmuse-ADAPTATION.md`, `01_Forkable/FKB00_Runtime/06_Sovereign_Bot_Coworkers/openmuse/README.md`, `01_Forkable/FKB00_Runtime/06_Sovereign_Bot_Coworkers/openmuse/package.json`
- **Noyau Cible & Destination ÉNONCÉ §1(1)** : **CORPS · Organe K2 (Exécution, Anything & 3D)** · Destination : **`FUSIONNÉ`** · Statut Vérifié (§5.8) : **`FUSIONNÉ`** (Skin/trait « agent personnel » porté dans `RigInfinity` (`bots_proof`) ; source retirée F8 pas 7 ; `cargo test` 100 % vert et preuve de suppression PASS.)
- **Principe** : Agent personnel continu (navigateur + terminal + fichiers) permettant à l'humain de suivre le plan, relire les actions et reprendre la main à tout moment.
- **Invariants** : Revue humaine explicite avant effets irréversibles ; compatibilité multi-harness.
- **Interfaces** : Trait OpenMuse dans RigInfinity (plateforme OpenBot + skin OpenMuse) / openmuse_takeover_url.
- **Perte au Retrait & Conflits** : Perte sans fusion : absence de mode prise de relais fluide sur agent personnel. Conflit : processus séparé vs skin unifié -> ADR-02. (*Arbitrage : ADR-02*)

### M111 — `openrig` (F8_UNPINNED)
- **Provenance & Sources Brutes Lues** : chemin `01_Forkable/FKB00_Runtime/01_Holo_TriptyqueCore/openrig` | repo `Amdkn/openrig` | SHA/pin `649376c803f7` | licence `Apache-2.0` | sources : `01_Forkable/FKB00_Runtime/00_A0_Core/openrig.manifest.json`, `01_Forkable/FKB00_Runtime/00_A0_Core/openrig-ADAPTATION.md`, `01_Forkable/FKB00_Runtime/01_Holo_TriptyqueCore/openrig/README.md`, `01_Forkable/FKB00_Runtime/01_Holo_TriptyqueCore/openrig/package.json`, `01_Forkable/MODULES-LOCK.json`
- **Noyau Cible & Destination ÉNONCÉ §1(1)** : **CORPS · Organe K2 (Exécution, Anything & 3D)** · Destination : **`FUSIONNÉ`** · Statut Vérifié (§5.8) : **`FUSIONNÉ`** (Rigs déclaratifs, context packs et lignage ULID portés en Rust dans `RigInfinity` ; source retirée F8 pas 8 ; `cargo test` sur `RigInfinity` 100 % vert et preuve de suppression PASS.)
- **Principe** : Multiplexage déclaratif d'équipes multi-harnesses (« A harness wraps a model; a rig wraps your harnesses ») avec sièges typés et lignage vérifiable.
- **Invariants** : Un seul écrivain actif par rig/worktree ; séparation lead/worker/reviewer ; pas de serveur HTTP externe non loopback.
- **Interfaces** : openrig_state.rs / openrig_context_packs.rs / openrig_lineage.rs (ULID) / openrig_terminal.rs / rigs.yaml.
- **Perte au Retrait & Conflits** : Perte sans fusion : orchestration ad-hoc sans lignage ni isolation des sièges. Conflit : daemon TS OpenRig séparé vs daemon maître Rust RigInfinity -> ADR-02, ADR-10. (*Arbitrage : ADR-02, ADR-10*)

### M112 — `pi` (F8_UNPINNED)
- **Provenance & Sources Brutes Lues** : chemin `F8/pi` | repo `interne A'Space` | SHA/pin `natif/dossie` | licence `voir-source-brute` | sources : `01_Forkable/FKB00_Runtime/00_A0_Core/pi.manifest.json`, `01_Forkable/FKB00_Runtime/00_A0_Core/pi-ADAPTATION.md`
- **Noyau Cible & Destination ÉNONCÉ §1(1)** : **SYSTÈME NERVEUX · Bus L0 & Fibres** · Destination : **`FUSIONNÉ`** · Statut Vérifié (§5.8) : **`PARTIEL`** (Gitlink retiré F8 pas 8 ; part manquante : `pi.manifest.json` est à `levels.current: 1`, `.pi/extensions/aspace-factory.ts` a une erreur TS2305, `crash_counts` absent de `factory.sqlite` (`H-P2-11` / Phase D en attente).)
- **Principe** : Durabilité par checkpoint avant exécution et minimalisme à 4 outils atomiques (Read, Write, Edit, Bash) avec idempotence par requestId.
- **Invariants** : Zero ré-exécution d'effets externes non idempotents après crash (replay:'safe' lectures seules) ; verrou d'écriture unique par worktree (writerLock).
- **Interfaces** : subagents(run/chain/send/status/resume) / handoff / search_history / requestId -> 02_Factory/factory.sqlite.
- **Perte au Retrait & Conflits** : Perte sans fusion : perte de progression sur crash ou double exécution destructrice. Conflit : threads mémoire vivants vs checkpoints SQLite -> ADR-01. (*Arbitrage : ADR-01*)

### M113 — `prime-agent` (F8_UNPINNED)
- **Provenance & Sources Brutes Lues** : chemin `F8/prime-agent` | repo `Amdkn/prime-agent` | SHA/pin `3bac96af3451` | licence `NOASSERTION` | sources : `01_Forkable/FKB00_Runtime/00_A0_Core/prime-agent.manifest.json`, `01_Forkable/FKB00_Runtime/00_A0_Core/prime-agent-ADAPTATION.md`, `01_Forkable/MODULES-LOCK.json`
- **Noyau Cible & Destination ÉNONCÉ §1(1)** : **ÂME · Organe K1 (Gouvernance & RSI)** · Destination : **`FUSIONNÉ`** · Statut Vérifié (§5.8) : **`FUSIONNÉ`** (Paradigme RLM (`/refine`, snapshots rollback) porté dans `RigInfinity` (`prime_agent_proof` 6/6) ; source retirée F8 pas 8 ; `cargo test` 100 % vert et preuve de suppression PASS.)
- **Principe** : Récursivité disciplinée (RLM : appels de sous-agents comme fonctions dans REPL persistant) et Continual Harness raffiné par preuves avec rollback instantané.
- **Invariants** : Prompt système constitutionnel immuable ; aucune mise à jour d'état conservée si le score de hold-out baisse ; zéro télémétrie api.primeintellect.ai.
- **Interfaces** : /refine / ContinualSnapshot / refine_available() / prime_agent_proof (6/6 tests).
- **Perte au Retrait & Conflits** : Perte sans fusion : dérive des prompts et absence de raffinement itératif réversible. Conflit : auto-modification non bornée -> ADR-06, ADR-08. (*Arbitrage : ADR-06, ADR-08*)

### M114 — `aspace-fiber-host` (NATIF_L0)
- **Provenance & Sources Brutes Lues** : chemin `01_Forkable/FKB00_Runtime/00_A0_Core/aspace-fiber-host` | repo `Amdkn/Aspace_OS_V5` | SHA/pin `natif/dossie` | licence `MIT` | sources : `01_Forkable/FKB00_Runtime/00_A0_Core/aspace-fiber-host.manifest.json`, `01_Forkable/FKB00_Runtime/00_A0_Core/aspace-fiber-host-ADAPTATION.md`, `01_Forkable/FKB00_Runtime/00_A0_Core/aspace-fiber-host/README.md`, `01_Forkable/FKB00_Runtime/00_A0_Core/aspace-fiber-host/package.json`, `01_Forkable/MODULES-LOCK.json`
- **Noyau Cible & Destination ÉNONCÉ §1(1)** : **SYSTÈME NERVEUX · Bus L0 & Fibres** · Destination : **`FUSIONNÉ`** · Statut Vérifié (§5.8) : **`PARTIEL`** (Implémentation TypeScript L0 présente ; part manquante : `package.json` référence encore `file:../cordis/*` (inexistant sur disque après retrait `cordis`), `node_modules` absent et socket Unix vers RigInfinity non branché.)
- **Principe** : Hôte d'exécution dynamique des Fibres Cordis : registre vivant, activation par dépendances, baux (leases), reçus, idempotence et récupération sur HMR/crash.
- **Invariants** : Activation réactive sans panique sur dépendance absente ; tolérance aux redémarrages à chaud ; idempotence des transitions.
- **Interfaces** : src/host.ts, src/journal.ts, src/manifest.ts, src/transports.ts, tests/*.spec.ts.
- **Perte au Retrait & Conflits** : Perte sans fusion : absence de couche d'hébergement concrète des fibres TS/JS dans L0. Conflit : couplage avec le daemon Rust -> ADR-02, ADR-10. (*Arbitrage : ADR-02, ADR-10*)

### M115 — `fondation-13-1` (NATIF_L0)
- **Provenance & Sources Brutes Lues** : chemin `01_Forkable/FKB00_Runtime/00_A0_Core/fondation-13-1` | repo `interne A'Space` | SHA/pin `natif/dossie` | licence `voir-source-brute` | sources : `01_Forkable/FKB00_Runtime/00_A0_Core/fondation-13-1.manifest.json`, `01_Forkable/FKB00_Runtime/00_A0_Core/fondation-13-1/Cargo.toml`
- **Noyau Cible & Destination ÉNONCÉ §1(1)** : **ÂME · Organe K1 (Gouvernance & RSI)** · Destination : **`FUSIONNÉ`** · Statut Vérifié (§5.8) : **`PARTIEL`** (Cœur Rust L0 **VERT 100/100 (`cargo test` Windows/GNU)** + 6 binaires compilés en Phase 2 Hybride ; part manquante : fonctions `F1-8..F1-11` restantes.)
- **Principe** : Unification des 13 fonctions de gouvernance en 1 Lead + Juge interne séparé avec vérification pure déterministe (Recevoir, Router, Découvrir, Juger, Exécuter, Mémoriser).
- **Invariants** : 0 dépendance externe, 0 télémétrie, rejet motivé (jamais de correction silencieuse), SHA-40 vérifié, séparation producteur/juge/exécutant.
- **Interfaces** : r10-receive, route-dispatch, validate-discover, judge-pr, execute-merge, recall-fact (lib r10_validator).
- **Perte au Retrait & Conflits** : Perte sans fusion : perte du noyau de vérité formelle (R10, Journal seq, Épistémique M1-M8). Conflit : aucun (établit les invariants L0) -> ADR-04. (*Arbitrage : ADR-04*)

### M116 — `source-control-natif` (NATIF_L0)
- **Provenance & Sources Brutes Lues** : chemin `01_Forkable/FKB00_Runtime/00_A0_Core/source-control-natif` | repo `interne A'Space` | SHA/pin `natif/dossie` | licence `voir-source-brute` | sources : `01_Forkable/FKB00_Runtime/00_A0_Core/source-control-natif.manifest.json`
- **Noyau Cible & Destination ÉNONCÉ §1(1)** : **CORPS · Organe K2 (Exécution, Anything & 3D)** · Destination : **`FUSIONNÉ`** · Statut Vérifié (§5.8) : **`PARTIEL`** (Étapes SC-1 et SC-2 portées dans `RigInfinity` (`source_control.rs`, `changeset_proof` 75/75 tests au pin) ; part manquante : chemin `00_A0_Core/source-control-natif` absent sur disque (code vit dans le sous-module `RigInfinity`) et étapes SC-3..SC-10 restantes.)
- **Principe** : Contrôle de source comme service et changesets WAL sans copie (inspiré Scion clean-room) : diff, blame, ancêtre via API + stockage CAS SHA-256 unique.
- **Invariants** : Zéro invocation de sous-processus git ; 0 copie sur changeset (blob stocké 1 fois) ; réécriture interdit ; token GitHub via env uniquement.
- **Interfaces** : source_control.rs / changeset_proof / source_control_proof / Scion sparse API.
- **Perte au Retrait & Conflits** : Perte sans fusion : coût linéaire des clones/copies multi-agents et verrou global de merge. Conflit : rebuild complet de Git vs API sparse -> ADR-05. (*Arbitrage : ADR-05*)

### M117 — `00_Marketplace_YoutubeSkills` (EXTRA_FKB)
- **Provenance & Sources Brutes Lues** : chemin `01_Forkable/FKB07_Money_Maker/00_Marketplace_YoutubeSkills` | repo `interne A'Space` | SHA/pin `natif/dossie` | licence `voir-source-brute` | sources : `01_Forkable/FKB07_Money_Maker/00_Marketplace_YoutubeSkills/README.md`
- **Noyau Cible & Destination ÉNONCÉ §1(1)** : **CORPS · Organe K5 (Métabolisme B2B, Vidéo & Finance S0)** · Destination : **`FUSIONNÉ`** · Statut Vérifié (§5.8) : **`FUSIONNÉ`** (Absorbé nativement dans `01_Forkable/FKB00_Runtime/00_A0_Core/aspace_discovery_catalog.py` (`MARKETPLACE_SKILL_CATEGORIES`, `YOUTUBE_SKILL_VIDEOS`, `MARKETPLACE_PLAYBOOKS`, `get_marketplace_playbook`, `query_marketplace_skills`) ; test différentiel strict (`==`, zéro clé en trop) + sabotage avant/après suppression physique PASS.)
- **Principe** : Cartographie et compilation de 34 ressources vidéo en offres et skills actionnables pour ASpace MarketPlace.
- **Invariants** : Traçabilité source -> skill -> offre ; évaluation MSCI.
- **Interfaces** : 00_Marketplace_YoutubeSkills/ + MSCI_ARCH_MARKETPLACE_YOUTUBE_SKILLS.md.
- **Perte au Retrait & Conflits** : Perte sans fusion : perte de la traçabilité entre veille MSCI et catalogue d'offres LD01. Conflit : aucun. (*Arbitrage : ADR-04*)

### M118 — `04_Inference_Youtube_Discovery_Registry` (EXTRA_FKB)
- **Provenance & Sources Brutes Lues** : chemin `01_Forkable/FKB01_Inference/04_Inference_Youtube_Discovery_Registry` | repo `interne A'Space` | SHA/pin `natif/dossie` | licence `voir-source-brute` | sources : `01_Forkable/FKB01_Inference/04_Inference_Youtube_Discovery_Registry/` + `01_Forkable/FKB*/index.md` + `FUSIONS-REGISTRY.md`
- **Noyau Cible & Destination ÉNONCÉ §1(1)** : **SYSTÈME NERVEUX · Organe K3 (Inférence & FreeCloud)** · Destination : **`FUSIONNÉ`** · Statut Vérifié (§5.8) : **`FUSIONNÉ`** (Absorbé nativement dans `01_Forkable/FKB00_Runtime/00_A0_Core/aspace_discovery_catalog.py` (`INFERENCE_DISCOVERY_REGISTRY`, `OPPORTUNITY_DOSSIERS`, `get_opportunity_dossier`, `qualify_inference_opportunity`) ; test différentiel strict (`==`, zéro clé en trop, zéro normalisation lossy) + sabotage sur chaque fonction et champ avant/après suppression physique PASS.)
- **Principe** : Qualification anti-clickbait à 5 filtres des opportunités d'inférence gratuites (API pure vs app desktop, risque CB, TTL).
- **Invariants** : Zéro carte bancaire exposée ; priorité absolue aux API pures sur les apps propriétaires ; traçabilité JSON.
- **Interfaces** : registry.json + SKILL_WATCH.md -> injection Voie A (FreeLLMAPI) ou Voie B (Codex Web).
- **Perte au Retrait & Conflits** : Perte sans fusion : admission de plateformes pièges ou éphémères dans le routeur K3. Conflit : aucun. (*Arbitrage : ADR-08*)

### M119 — `LibertyRide2` (EXTRA_FKB)
- **Provenance & Sources Brutes Lues** : chemin `01_Forkable/FKB07_Money_Maker/LibertyRide2` | repo `interne A'Space` | SHA/pin `natif/dossie` | licence `voir-source-brute` | sources : `01_Forkable/FKB07_Money_Maker/LibertyRide2/package.json`
- **Noyau Cible & Destination ÉNONCÉ §1(1)** : **CORPS · Organe K5 (Métabolisme B2B, Vidéo & Finance S0)** · Destination : **`RETENU`** · Statut Vérifié (§5.8) : **`RETENU`** (RETENU (Justification de fondation : application produit client Next.js/TypeScript/Three.js réelle de l'aire B1 SOB/Liberty Ride — livrable applicatif autonome opéré par Areas OS LD01).)
- **Principe** : Portail business opérationnel réel (Liberty Ride 2.0 Contractor Launchpad) incarnant un cas client concret de B1/LD01.
- **Invariants** : Isolation complète des règles et hooks hors racine (correctif `.claude/settings.json` appliqué) ; déploiement applicatif autonome.
- **Interfaces** : Next.js App Router + Tailwind + Three.js.
- **Perte au Retrait & Conflits** : Perte si écarté : perte d'un actif applicatif business en production dans l'aire B1. Conflit : aucun. (*Arbitrage : ADR-02*)

### M120 — `llm-wiki` (EXTRA_FKB)
- **Provenance & Sources Brutes Lues** : chemin `01_Forkable/FKB02_Memory/llm-wiki` | source `gist 34a4b4bf6d54b1828ba8c256615619e8` (`Amdkn`, 11 985 o LF, sha256 `dc3efe98ae62f23dd08acad13aba2e95287beb20b6bec2f4af0423557fe37401`) | historique git : intro `c507bbf` (`ac46de1`) -> bind `852cc19` (`537de1c` + `aspace-plugin.json` 819 o) -> rapatrié & dé-pointé `D-N048 V0` (`26ca7cb` / PR #6 `d515872`, `log.md` `8626424`) | licence : contenu propre Amdkn (repo V5 sans LICENSE) | sources : `00_Memoire/bundle/concepts/llm-wiki.md` + `01_Forkable/FORKS-AMONT-21-FREEZE.md` + `01_Forkable/FUSIONS-REGISTRY.md`
- **Noyau Cible & Destination ÉNONCÉ §1(1)** : **ÂME · Organe K4 (Mémoire & Skills)** · Destination : **`FUSIONNÉ`** · Statut Vérifié (§5.8) : **`PARTIEL`** (Rapatriement historique `D-N048 V0` prouvé et gitlink retiré, mais rétrogradé `PARTIEL` au correctif audit Cycle 6 : aucune fonction exécutable M120 dans `K4` `aspace_fkb02_memory_organ.py`, aucun test différentiel/sabotage ni reçu R10, page orpheline dans `index.md` et références `00_Memoire/wikillm/llm-wiki.md` obsolètes dans `00_Memoire/AGENTS.md`.)
- **Principe** : Architecture Wiki continu à 3 couches (Raw sources immuables, Wiki maintenu par les agents, Schema de gouvernance).
- **Invariants** : Raw immuables ; opérations obligatoires Query à l'entrée et Ingest/Lint à la sortie.
- **Interfaces** : 00_Memoire/raw/ + 00_Memoire/bundle/ + AGENTS.md.
- **Perte au Retrait & Conflits** : Perte sans fusion : absence de boucle de compilation documentaire continue. Conflit : aucun -> ADR-04. (*Arbitrage : ADR-04*)

---

## 2. Fiches des 8 Entrées Doublons `.gitmodules` (`D01` à `D08` — `FKB06_Video_SaaS`)

> Chaque entrée `[submodule "01_Forkable/FKB02_Video_SaaS/<nom>"]` dans `.gitmodules` pointe vers `01_Forkable/FKB06_Video_SaaS/<nom>` qui n'a **aucun gitlink `160000`** dans l'index Git et dont l'URL est déjà active sous `01_Forkable/FKB07_Money_Maker/02_Video/<nom>`.

### D01 — `argo` (Doublon `.gitmodules` FKB06 → FKB07/02_Video)
- **Provenance Brute** : entrée `.gitmodules` `01_Forkable/FKB02_Video_SaaS/argo` | path `01_Forkable/FKB06_Video_SaaS/argo` | url `https://github.com/Amdkn/argo.git` | gitlink index `160000` : **absent (0)**.
- **Principe / Invariant / Interface** : Doublon exact du module `FKB07_Money_Maker/02_Video/argo` (qui porte déjà le principe, les invariants et l'interface dans `aspace_video_studio_foundation.py`).
- **Perte au Retrait & Conflit** : Perte **nulle** ; conserve la source canonique unique dans `FKB07/02_Video` et élimine la dérive documentaire (**ADR-11**). Statut : **`ÉCARTÉ`** (purgé de `.gitmodules` en Cycle 1).

### D02 — `earshot` (Doublon `.gitmodules` FKB06 → FKB07/02_Video)
- **Provenance Brute** : entrée `.gitmodules` `01_Forkable/FKB02_Video_SaaS/earshot` | path `01_Forkable/FKB06_Video_SaaS/earshot` | url `https://github.com/Amdkn/earshot.git` | gitlink index `160000` : **absent (0)**.
- **Principe / Invariant / Interface** : Doublon exact du module `FKB07_Money_Maker/02_Video/earshot` (qui porte déjà le principe, les invariants et l'interface dans `aspace_video_studio_foundation.py`).
- **Perte au Retrait & Conflit** : Perte **nulle** ; conserve la source canonique unique dans `FKB07/02_Video` et élimine la dérive documentaire (**ADR-11**). Statut : **`ÉCARTÉ`** (purgé de `.gitmodules` en Cycle 1).

### D03 — `explainroo` (Doublon `.gitmodules` FKB06 → FKB07/02_Video)
- **Provenance Brute** : entrée `.gitmodules` `01_Forkable/FKB02_Video_SaaS/explainroo` | path `01_Forkable/FKB06_Video_SaaS/explainroo` | url `https://github.com/Amdkn/explainroo.git` | gitlink index `160000` : **absent (0)**.
- **Principe / Invariant / Interface** : Doublon exact du module `FKB07_Money_Maker/02_Video/explainroo` (qui porte déjà le principe, les invariants et l'interface dans `aspace_video_studio_foundation.py`).
- **Perte au Retrait & Conflit** : Perte **nulle** ; conserve la source canonique unique dans `FKB07/02_Video` et élimine la dérive documentaire (**ADR-11**). Statut : **`ÉCARTÉ`** (purgé de `.gitmodules` en Cycle 1).

### D04 — `huashu-motion` (Doublon `.gitmodules` FKB06 → FKB07/02_Video)
- **Provenance Brute** : entrée `.gitmodules` `01_Forkable/FKB02_Video_SaaS/huashu-motion` | path `01_Forkable/FKB06_Video_SaaS/huashu-motion` | url `https://github.com/Amdkn/huashu-motion.git` | gitlink index `160000` : **absent (0)**.
- **Principe / Invariant / Interface** : Doublon exact du module `FKB07_Money_Maker/02_Video/huashu-motion` (qui porte déjà le principe, les invariants et l'interface dans `aspace_video_studio_foundation.py`).
- **Perte au Retrait & Conflit** : Perte **nulle** ; conserve la source canonique unique dans `FKB07/02_Video` et élimine la dérive documentaire (**ADR-11**). Statut : **`ÉCARTÉ`** (purgé de `.gitmodules` en Cycle 1).

### D05 — `reanimate` (Doublon `.gitmodules` FKB06 → FKB07/02_Video)
- **Provenance Brute** : entrée `.gitmodules` `01_Forkable/FKB02_Video_SaaS/reanimate` | path `01_Forkable/FKB06_Video_SaaS/reanimate` | url `https://github.com/Amdkn/reanimate.git` | gitlink index `160000` : **absent (0)**.
- **Principe / Invariant / Interface** : Doublon exact du module `FKB07_Money_Maker/02_Video/reanimate` (qui porte déjà le principe, les invariants et l'interface dans `aspace_video_studio_foundation.py`).
- **Perte au Retrait & Conflit** : Perte **nulle** ; conserve la source canonique unique dans `FKB07/02_Video` et élimine la dérive documentaire (**ADR-11**). Statut : **`ÉCARTÉ`** (purgé de `.gitmodules` en Cycle 1).

### D06 — `rossark-motion-skill` (Doublon `.gitmodules` FKB06 → FKB07/02_Video)
- **Provenance Brute** : entrée `.gitmodules` `01_Forkable/FKB02_Video_SaaS/rossark-motion-skill` | path `01_Forkable/FKB06_Video_SaaS/rossark-motion-skill` | url `https://github.com/Amdkn/rossark-motion-skill.git` | gitlink index `160000` : **absent (0)**.
- **Principe / Invariant / Interface** : Doublon exact du module `FKB07_Money_Maker/02_Video/rossark-motion-skill` (qui porte déjà le principe, les invariants et l'interface dans `aspace_video_studio_foundation.py`).
- **Perte au Retrait & Conflit** : Perte **nulle** ; conserve la source canonique unique dans `FKB07/02_Video` et élimine la dérive documentaire (**ADR-11**). Statut : **`ÉCARTÉ`** (purgé de `.gitmodules` en Cycle 1).

### D07 — `take-one` (Doublon `.gitmodules` FKB06 → FKB07/02_Video)
- **Provenance Brute** : entrée `.gitmodules` `01_Forkable/FKB02_Video_SaaS/take-one` | path `01_Forkable/FKB06_Video_SaaS/take-one` | url `https://github.com/Amdkn/take-one.git` | gitlink index `160000` : **absent (0)**.
- **Principe / Invariant / Interface** : Doublon exact du module `FKB07_Money_Maker/02_Video/take-one` (qui porte déjà le principe, les invariants et l'interface dans `aspace_video_studio_foundation.py`).
- **Perte au Retrait & Conflit** : Perte **nulle** ; conserve la source canonique unique dans `FKB07/02_Video` et élimine la dérive documentaire (**ADR-11**). Statut : **`ÉCARTÉ`** (purgé de `.gitmodules` en Cycle 1).

### D08 — `video-director` (Doublon `.gitmodules` FKB06 → FKB07/02_Video)
- **Provenance Brute** : entrée `.gitmodules` `01_Forkable/FKB02_Video_SaaS/video-director` | path `01_Forkable/FKB06_Video_SaaS/video-director` | url `https://github.com/Amdkn/video-director.git` | gitlink index `160000` : **absent (0)**.
- **Principe / Invariant / Interface** : Doublon exact du module `FKB07_Money_Maker/02_Video/video-director` (qui porte déjà le principe, les invariants et l'interface dans `aspace_video_studio_foundation.py`).
- **Perte au Retrait & Conflit** : Perte **nulle** ; conserve la source canonique unique dans `FKB07/02_Video` et élimine la dérive documentaire (**ADR-11**). Statut : **`ÉCARTÉ`** (purgé de `.gitmodules` en Cycle 1).
