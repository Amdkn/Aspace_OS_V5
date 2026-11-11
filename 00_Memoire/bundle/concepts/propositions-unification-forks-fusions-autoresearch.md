---
title: "Propositions A0 — Unification des forks V5 : Auto Research des fusions, adaptation A'Space, intégration native en mono-repo"
type: concept
status: proposition
updated: 2026-11-09
tags:
  - forks
  - fusions
  - auto-research
  - mono-repo
  - cordis
---

# Propositions A0 — Unification des forks V5 : Auto Research des fusions, adaptation A'Space, intégration native en mono-repo

**Auteur :** A0 Amadeus — **Date :** 2026-11-09
**Inventaire vérifié :** repo `Amdkn/Aspace_OS_V5`, master, lecture directe `.gitmodules` + arborescence + index FKB, 2026-11-09 ~10:00 EST
**Statut :** proposition d'analyse. Aucune exécution, aucun déplacement, aucune suppression dans ce document. L'exécution passe par la chaîne (Bill Discover → Clara design → Ryan), jamais en direct.

---

## 1. Le but derrière le but

Aujourd'hui V5 est une **collection de 120 pointeurs** vers des publications publiques, dont 21 ne sont même pas des forks souverains.
Le but n'est pas de collectionner. Le but est un **runtime vivant unique** où chaque module public devient une pièce A'Space native : adaptée à l'univers, vérifiable par hold-outs, remplaçable sans casser le reste.

Principe directeur, en une phrase : **zéro module laissé dans sa publication grand public basique et dégradée, par conception.**
Un module qui reste tel que publié n'est pas intégré, il est seulement rangé.

---

## 2. État des lieux vérifié

### 2.1 Les chiffres

| Catégorie | Sous-modules | Dont Amdkn | Dont amont non souverain |
|---|---|---|---|
| FKB00_Runtime | 40 | 30 | 10 |
| FKB01_Inference | 13 | 13 | 0 |
| FKB02_Memory | 11 | 10 | 1 (gist) |
| FKB03_3DWorlds | 4 | 3 | 1 |
| FKB04_Tools_Anything | 6 | 4 | 2 |
| FKB06_Video_SaaS | 8 | 8 | 0 |
| FKB07_Money_Maker | 34 | 30 | 4 |
| FKB08_Plugins | 4 | 1 | 3 |
| **Total** | **120** | **99** | **21** |

120 entrées, **111 dépôts distincts** : 9 dépôts sont pointés deux fois (voir 2.2).
Pour mémoire : le 2026-11-06, le corpus comptait 26 sous-modules. Il a été multiplié par plus de 4 en trois jours, sans registre de suivi. C'est la croissance qui impose l'Auto Research : l'inventaire manuel ne suit plus.

### 2.2 Les 21 pointeurs non souverains

Ils pointent directement vers l'amont, sans fork Amdkn : `deepseek-harness` (deepseek-ai), `herdr-app` (herdrdev), `t3code` (pingdotgg), `openclaw` (openclaw), `claude-code` (anthropics), `codex` (openai), `wikiskill`, `adk-recipes` (google), `rrsi`, `dream-rsi` (google-research), `space-agent` (agent0ai), `caveman` (JuliusBrussee), `claude-mem` (TheDotMack), `nansen-cli` (nansen-ai), `Scrapling` (D4Vinci), `dify` (langgenius), `presenton` (presenton), `mattpocock-skills` (mattpocock), `openai-plugins` (openai), `claude-video` (bradautomates), et `llm-wiki` — un **gist**, pas même un dépôt.

Conséquence : 21 modules peuvent changer, disparaître ou être retirés par leur auteur sans qu'A'Space ne le décide. La souveraineté s'arrête là où le pointeur ne passe pas par Amdkn.

### 2.3 Les doublons — 9 dépôts pointés deux fois

Les 8 moteurs vidéo (`argo`, `earshot`, `explainroo`, `huashu-motion`, `reanimate`, `rossark-motion-skill`, `take-one`, `video-director`) existent à la fois sous `FKB06_Video_SaaS/` et sous `FKB07_Money_Maker/02_Video/`. `hermes-agent` existe à la fois sous `FKB00_Runtime/04_ADE_OpenRig/` et sous `FKB04_Tools_Anything/`.
L'index FKB reconnaît déjà la consolidation vidéo sous FKB07/02_Video (10 moteurs avec OpenMontage et flute) — mais les sous-modules doublons sont toujours là. Un doublon, c'est deux vérités qui vont diverger.

### 2.4 Les dérives de nommage et de structure

- Les 8 noms de sous-modules vidéo disent encore `FKB02_Video_SaaS` alors que leurs chemins disent `FKB06_Video_SaaS`. FKB02 est aujourd'hui Memory. Le nom est périmé.
- `FKB05_Wargames` figure dans FKB-INDEX, mais **aucun dossier FKB05 n'existe** dans l'arborescence. Ses deux moteurs (MiroFish, elephant-goldfish-model) vivent sous FKB00.
- `03_Videaste/`, créé le 2026-11-04 avec son index des 8 repos vidéo, **n'existe plus au HEAD actuel** (vérifié par l'arborescence et par lecture directe : aucun chemin `03_Videaste`). Son contenu vidéo vit désormais en FKB06/FKB07. Déplacement ou perte : à établir par la chaîne, pas à supposer.
- FKB-INDEX ligne 4 dit toujours que automaton, cubefarm et codex-chatgpt-web « NE SONT PAS déplacés » — ils l'ont été physiquement le 2026-11-05 (commit `caf85c0`). Ligne périmée, déjà signalée.
- Collision de nom : deux dépôts distincts s'appellent tous deux `skills` (Amdkn/skills et mattpocock/skills). Pas un doublon, mais une confusion en attente.

### 2.5 Ce qui n'a pas été vérifié

L'inventaire ci-dessus porte sur les **pointeurs** (`.gitmodules`, arborescence, index). Il ne prouve pas le contenu : les forks Amdkn sont-ils des copies réelles ou des coquilles vides ? Les miroirs Hugging Face (`HF-SOVEREIGN-INDEX.md`) contiennent-ils les poids ? Les fichiers natifs déjà présents tournent-ils ? Ces trois questions sont des hold-outs pour la chaîne, pas des affirmations de ce document.

---

## 3. Doctrine « Zéro module en publication basique »

### 3.1 Les quatre états d'un module

| État | Nom | Définition |
|---|---|---|
| 0 | **Basique** | Publication grand public telle quelle, pointeur seul, aucune adaptation A'Space. |
| 1 | **Adapté** | Fork souverain + adaptation documentée à l'univers A'Space (noms, chemins, licences, télémétrie coupée, ports et contrats A'Space). |
| 2 | **Vérifié** | Hold-outs verts + validation 13e. |
| 3 | **Publié** | État 2 + registre à jour. |

### 3.2 Les règles

1. **Tout nouveau fork entre en état 0 avec une date de sortie.** Pas d'entrée sans échéance.
2. **Le compteur public, c'est le nombre de modules en état 0.** L'objectif est 0, pas « moins qu'hier ».
3. **Un module ne monte d'un état que sur preuve** : adaptation relue (état 1), hold-outs verts + validation 13e (état 2), état 2 + registre à jour (état 3).
4. **Un module en état 0 ne peut pas être une dépendance du Runtime.** Le Runtime ne s'appuie que sur de l'adapté ou mieux.
5. **Les 21 pointeurs amont sont de l'état 0 aggravé** : ils ne sont même pas des forks. Leur sortie de l'état 0 commence par un fork Amdkn.

### 3.3 Le compteur au 2026-11-09

Sur 120 entrées : **21 pointeurs amont (état 0 aggravé) + 9 doublons à résorber + 8 noms périmés**. Le nombre exact de modules en état 0 « fork Amdkn non adapté » n'est pas établi — c'est la première mesure que l'Auto Research doit produire, module par module, avec sa fiche d'adaptation.

---

## 4. Fusions complémentaires — les dix premières cibles

Chaque fusion est nommée par sa **fonction**, pas par ses dépôts. L'ordre proposé suit la doctrine du document de fusion (`FKB04 s'améliore d'abord, la Factory réplique ensuite`) et la maturité de ce qui existe déjà.

### F1 — Inférence souveraine unique (FKB01)
**Modules :** freellmapi + codex-chatgpt-web + api-anything + freebuff + FreeVPS.
**Fonction :** un seul point d'entrée d'inférence, avec bascule local → gratuit → distant.
**Déjà existant :** `gateway-manifest.json` v5.0.0 (entrée `127.0.0.1:31415`, tier 0 local GLiNER/Needle/Mimi/LFM3, tier 1 freellmapi puis freebuff) et `aspace_freecloud_gateway.py`. La fusion est esquissée en code, pas terminée.
**Preuve attendue :** une requête traverse les trois tiers et revient ; un provider en panne ne casse pas la requête.

### F2 — Voix locale complète (FKB01)
**Modules :** mimi + moshi + LFM3-Omni-2B + LoRA + needle + GLiNER2.5-multi-Decide.
**Fonction :** signal brut → tokens → décision → appel d'outil, sans rien envoyer dehors.
**Déjà existant :** la chaîne est spécifiée au §6 du document de fusion (`principes-fusion-runtime.md`) et dans les deux synthèses Gemini préservées (`mimi-lora-lfm3-omni.md`, `needle-gliner-edge.md`). Spécifiée, non implémentée.
**Preuve attendue :** une phrase parlée devient une décision et un appel d'outil, en local, avec latence mesurée.

### F3 — Mémoire neuro-symbolique unique (FKB02)
**Modules :** graphify + gbrain + infinite-brain-os + infinite-brain-harness + billion-context + auto-ontology + context-language-models + servers (MCP) + knowledge-catalog + dox.
**Fonction :** une seule mémoire partagée (Shared Brain), lisible par tous les harnesses via MCP.
**Déjà existant :** `00_Memoire/shared_brain/memory.jsonl` (nœud Muse_Browser_Agent, relation A0 incarné), `neuro_symbolic_bridge.py`, `start-memory-gateway.ps1`.
**Preuve attendue :** un fait écrit par un harness est relu par un autre ; aucune mémoire en double.

### F4 — Studio vidéo unique (FKB06 + FKB07/02_Video)
**Modules :** les 8 moteurs vidéo + OpenMontage + flute.
**Fonction :** un seul pipeline vidéo agentique (de la démo au SaaS).
**Déjà existant :** FKB07/02_Video les regroupe déjà en 10 moteurs ; l'index FKB le reconnaît. Reste à retirer les 8 doublons de FKB06 et à choisir l'emplacement canonique : **FKB07/02_Video**.
**Preuve attendue :** une vidéo produite de bout en bout par le pipeline unique ; zéro doublon dans `.gitmodules`.

### F5 — Monde 3D unique (FKB03)
**Modules :** cubefarm + agent-office + city-office + space-agent.
**Fonction :** un seul monde (Cube Farm × Agent Office, city-office en anneau).
**Déjà existant :** la doctrine est posée (FKB-INDEX : city-office = anneau routier autour du sanctuaire Cube Farm). `space-agent` est un pointeur amont non souverain : à forker d'abord.
**Preuve attendue :** un agent visible dans le monde déclenche une action réelle du Runtime.

### F6 — Couche « Anything » unique (FKB04)
**Modules :** api-anything + CLI-Anything + rea + hermes-agent (+ caveman, claude-mem une fois forkés).
**Fonction :** une seule couche d'appel universel — toute API, tout CLI, tout outil, par le même contrat.
**Déjà existant :** FKB04 est la première catégorie que le document de fusion désigne comme prioritaire. `hermes-agent` en doublon avec FKB00 à résorber (canonique : FKB04).
**Preuve attendue :** un même appel traverse API, CLI et agent sans changer de contrat.

### F7 — Moteur Money Maker unique (FKB07)
**Modules :** 11 briques trading + dify + presenton + Scrapling + BusinessOS + les moteurs natifs (`aspace_marketplace_engine.py`, `aspace_road_to_market_engine.py`, `proof_first_outbound_pipeline.py`, `deploy_proof_first_cohort.py`).
**Fonction :** un seul moteur de services B2B productisés, avec ses garde-fous.
**Déjà existant :** la thèse est posée (FKB07 index, inspiration Corey Ganim) et `AVERTISSEMENTS.md` encadre le trading en copilote strict. Les 4 pointeurs amont (nansen-cli, Scrapling, dify, presenton) sont à forker d'abord.
**Preuve attendue :** une offre vendue de bout en bout par le moteur unique, avec sa preuve.

### F8 — Runtime triptyque natif (FKB00)
**Modules :** automaton + infinity + openrig + agent-zero + pi + cordis + prime-agent + openbot + openmuse + OpenDots + OpenDuet.
**Fonction :** le triptyque Âme / Système nerveux / Corps, en natif.
**Déjà existant :** la structure est posée (FKB00 index, 6 pôles) et du code natif existe déjà (`a0_recursive_factory.py`, `a0_holon_swarm_runtime.py`, `a0_egm_bridge.py`, `aspace_freecompute_router.py`). C'est la fusion la plus lourde : **en dernier**, FKB00 étant sanctuarisé.
**Preuve attendue :** le Runtime tourne sans aucun des 11 sous-modules d'origine ; présence prouvée par heartbeat, pas par cron.

### F9 — Moteur prédictif et wargame unique (FKB00)
**Modules :** MiroFish + PathFM + autogluon + timesfm + chronos-forecasting + mitra-2 + tabfm + elephant-goldfish-model + gstack + superpowers + get-shit-done.
**Fonction :** un seul moteur de prédiction (séries, tableaux, wargames) et de spécifications propres.
**Déjà existant :** fiches modèles dans `02_PredictiveWargame_MachineLearning/models/`, moteurs natifs (`triptych_autogluon_engine.py`, `wargame_tabular_engine.py`, `wargame_business_launch_auditor.py`), registre HF (`HF-SOVEREIGN-INDEX.md`).
**Preuve attendue :** une prévision validée sur données écartées (hold-out), jamais sur les données d'entraînement.

### F10 — Catalogue de skills unique (FKB08)
**Modules :** anthropic-skills + mattpocock-skills + openai-plugins + claude-video.
**Fonction :** un seul catalogue de compétences, versionné, avec ses règles d'usage.
**Déjà existant :** les trois skills Leon van Zyl installés le 2026-11-05 montrent le pattern (skill = dossier versionné + références). `claude-video` et `mattpocock-skills` sont des pointeurs amont à forker.
**Preuve attendue :** une skill appelée par son nom unique, sans ambiguïté de source.

---

## 5. Auto Research des fusions — le mécanisme proposé

Le problème n'est pas de trouver dix fusions une fois. Le problème est que le corpus grandit plus vite que l'inventaire manuel (26 → 120 en trois jours). La réponse est une boucle, pas une liste.

### 5.1 La boucle

1. **Inventaire automatique** — à chaque ajout de fork et une fois par semaine : relire `.gitmodules`, l'arborescence et les index FKB ; recompter ; détecter les nouveaux entrants, les doublons, les noms périmés, les pointeurs amont.
2. **Matrice des complémentarités** — pour chaque module, consigner : fonction (verbe), entrées, sorties, recouvrements mesurés avec les autres. Deux modules sont complémentaires quand la sortie de l'un est l'entrée de l'autre, ou quand ils couvrent deux moitiés de la même fonction.
3. **Proposition de fusion** — pour chaque paire ou triade complémentaire : fonction unifiée, emplacement canonique, ordre de retrait des doublons, hold-outs de non-régression.
4. **Juge externe** — aucune fusion ne se valide elle-même : gate déterministe (`checks.ps1`) + relecture par la chaîne (13e). Une fusion sans hold-outs verts n'existe pas.
5. **Registre des fusions** — `01_Forkable/FUSIONS-REGISTRY.md` : chaque fusion y est inscrite (proposée / en design / exécutée / vérifiée), avec ses preuves. Le registre est la mémoire de l'Auto Research.
6. **Retrait** — une fusion exécutée et vérifiée retire ses doublons de `.gitmodules`. Le compteur de sous-modules doit **baisser** quand les fusions avancent. S'il ne fait que monter, l'Auto Research ne fait que regarder.

### 5.2 Porteur et cadence

- **Entrée :** Bill (Discover) — c'est son rôle : découvrir.
- **Design :** Clara — plan borné + hold-outs avant exécution, comme toujours.
- **Exécution :** Ryan et les Compagnons nommés.
- **Garant :** Rick (S1) — il structure le Before You Build de la boucle elle-même.
- **Cadence :** inventaire hebdomadaire + à chaque ajout de fork. Pas de nouvelle fusion proposée sans que l'inventaire soit à jour.
- **Précédent dans le repo :** le registre YouTube Discovery (`FKB01_Inference/04_Inference_Youtube_Discovery_Registry/`, opportunités OPP-001 à OPP-005) montre que le pattern « registre + opportunités qualifiées » existe déjà. L'Auto Research des fusions en est la généralisation : même pattern, appliqué aux modules au lieu des vidéos.

### 5.3 Critères d'admission d'une fusion

Une fusion n'entre au registre que si elle satisfait les quatre critères :
1. **Même fonction** — les modules couvrent deux moitiés d'un même verbe, pas deux sujets voisins.
2. **Recouvrement mesuré** — le chevauchement est chiffré (fichiers, fonctions, dépendances), pas affirmé.
3. **Non-régression prouvée** — les hold-outs passent avant et après ; un échec bloque la fusion.
4. **Retrait réel** — au moins un doublon ou un pointeur disparaît de `.gitmodules` à la fin.

---

## 6. Chemin vers le natif en mono-repo — séquence proposée

| Vague | Contenu | Pourquoi cet ordre |
|---|---|---|
| V0 | Déduplication + renommage + registre des fusions + compteur public (état 0) | Zéro code : que de l'ordre. Sans V0, chaque vague construit sur du sable. |
| V1 | FKB04 — couche Anything native (F6) | Le document de fusion le désigne en premier ; c'est la couche dont toutes les autres dépendent. |
| V2 | FKB01 — inférence unique (F1 + F2) | Le point d'entrée de tout le reste ; gateway déjà esquissée. |
| V3 | FKB02 — mémoire unique (F3) | Shared Brain déjà amorcé ; unifie ce que V1 et V2 produisent. |
| V4 | Vidéo unique (F4) | Doublons déjà identifiés ; emplacement canonique déjà choisi par l'index. |
| V5 | 3D unique (F5) | Dépend de V2 (inférence) et V3 (mémoire) pour être pilotable. |
| V6 | Money Maker unique (F7) | Dépend de V1, V2, V4, V5 ; c'est le moteur qui paie les autres. |
| V7 | Skills uniques (F10) | Catalogue stable une fois les moteurs unifiés. |
| V8 | Prédictif unique (F9) | Hold-outs les plus exigeants ; à faire quand la base est stable. |
| V9 | Runtime natif (F8) | En dernier : FKB00 est sanctuarisé, et le Runtime ne se réécrit pas sur une base qui bouge. |

**Règle de retrait d'un sous-module :** il disparaît quand sa fonction est couverte en natif **et** que les hold-outs sont verts **et** qu'aucune régression n'est mesurée. Jamais avant. La suppression est une preuve, pas un ménage.

---

## 7. Ce qui est déjà natif — à ne pas refaire

L'intégration native a déjà commencé, par endroits, sans porter ce nom. Ces pièces sont le pattern à étendre, pas à réécrire :
- `aspace_freecloud_gateway.py` + `gateway-manifest.json` (F1 esquissée).
- `a0_recursive_factory.py`, `a0_holon_swarm_runtime.py`, `a0_egm_bridge.py`, `aspace_freecompute_router.py` (FKB00, F8 amorcée).
- `neuro_symbolic_bridge.py`, `start-memory-gateway.ps1`, `shared_brain/memory.jsonl` (F3 amorcée).
- `aspace_marketplace_engine.py`, `aspace_road_to_market_engine.py`, `proof_first_outbound_pipeline.py`, `deploy_proof_first_cohort.py` (F7 amorcée).
- `triptych_autogluon_engine.py`, `wargame_tabular_engine.py`, `wargame_business_launch_auditor.py` (F9 amorcée).
- Les fiches modèles (`FKB01_Inference/models/`, `FKB00_Runtime/02_PredictiveWargame_MachineLearning/models/`) et le registre HF (`HF-SOVEREIGN-INDEX.md`).

---

## 8. Prochaines étapes proposées

**Recommandation A0 :** lancer la vague V0 immédiatement — déduplication des 9 doublons, correction des 8 noms périmés, création du registre `01_Forkable/FUSIONS-REGISTRY.md` et du compteur public (état 0) — puis confier à Rick la structuration du Before You Build de l'Auto Research, avec Bill en Discover sur les dix fusions ci-dessus.

Ce que ce document ne décide pas, et qui revient à l'exécution de chaque vague : l'ordre exact des fusions à l'intérieur d'une vague, et le moment où un sous-module précis est retiré. Ces arbitrages arrivent au moment d'exécuter la vague concernée, avec ses hold-outs, jamais avant.

**Un mot pour toi, Capitaine :** dis-moi si je route à Rick pour structuration, ou si tu veux d'abord corriger ou amender ces propositions. Rien ne bouge dans le repo tant que tu n'as pas dit le mot.

---

## 9. Correction du 2026-11-09 — Cordis d'abord (ordre du Capitaine)

Ma séquence §6 plaçait le Runtime (F8) en dernier et commençait par FKB04. Correction : **Cordis passe en étape 0, avant tout le reste.** Cordis est le micro-noyau qui définit le contrat (tout est plugin, tout passe par des fibres) : chaque adaptation qui suit doit se brancher sur ce contrat, pas inventer le sien. Le reste de l'ordre §6 tient (FKB04 → FKB01 → FKB02 → … → triptyque en dernier). Le détail de l'adaptation de Cordis et la roadmap complète sont dans le document compagnon `adaptation-cordis-aspace-roadmap-forks.md`.

---

## 10. Corrections du Discover Bill (2026-11-09)

Discover : `~/workspace/architecture-compagnons/discover-cordis-autoresearch-etapes-0-1.md` (Bill, lecture à la source, commit `45c5221`).

- **FKB-INDEX ligne 4 — allégation retirée.** Mon §2.4 affirmait que la ligne 4 dit encore qu'automaton, cubefarm et codex-chatgpt-web « NE SONT PAS déplacés ». Vérification à la source (@45c5221) : aucune occurrence de « déplac » dans `FKB-INDEX.md`, ligne 4 vide. La dérive n'est pas établie à ce commit — déjà corrigée, ou référence à une autre version. L'allégation est retirée.
- **`Amdkn/autoresearch` n'existe pas (404).** Ce n'est pas un état de départ, c'est un acte à venir : le design séquence sa création (depuis quel commit `master`, branche par défaut amont).
- **`karpathy/autoresearch` n'a pas de licence.** `license: null` à l'API, aucun fichier LICENSE dans l'arborescence. Le design borne ce qui est repris et sous quel statut. Ce point manquait à ma proposition — il est porté ici, pas contourné.
- **Attribution « API instable »** : la phrase est à la ligne 7 de `packages/core/README.md`, pas à la première ligne du README racine. Substance confirmée.

L'inventaire (120 / 111 / 21 / 9, comptes par catégorie, 9 doublons, 8 noms périmés, `03_Videaste` absent) est confirmé en entier, re-compté à la source.
