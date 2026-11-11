# Registre des fusions — A'Space OS V5

**Source unique des états de fusion.** Aucun autre fichier ne porte ces états.
**Propriétaire du schéma :** Clara (design D-N047, 2026-11-09).
**Écrivain :** l'exécution (Ryan) / le runner (propositions de transitions, avec mesures).
**Validateur :** le 13e, au gate de merge.

**États d'une fusion :** `proposée` → `en cours` → `mesurée` → `acceptée` / `rejetée`.
Les transitions d'état des modules (0→3) y sont enregistrées comme **effets** des fusions acceptées.

**Métrique (D7) :** triple **(H, C, D)** — H = hold-outs verts / total de la fusion ; C = compteur d'état 0 (global) ; D = doublons restants (global). **Règle d'acceptation : H = 100 % ET (C baisse OU D baisse)** par rapport aux valeurs pré-expérience. **H est le veto** : un hold-out rouge rejette toujours. Un candidat vert en H mais sans progrès sur C ni D est rejeté comme **no-op** (enregistré, non appliqué). Métrique et budget écrits dans `program.md` du fork `Amdkn/autoresearch` ; ce registre n'en est que le reflet d'état.
**Budget (D8) :** 5 minutes horloge fixe, 1 modification par expérience, cadence hebdomadaire + à chaque ajout de fork. Coupure mécanique par la minuterie du runner. Coût monétaire : zéro.

**Règle de comptage du compteur d'état 0 (D13) :** un module est en état 0 si son fork est **Amdkn** ET qu'**aucune fiche d'adaptation n'existe** ET qu'il n'est pas déjà en état > 0. **Les 21 pointeurs amont non souverains ne comptent pas** (problème de souveraineté, pas d'état 0) ; un doublon compte **une fois** (le module distinct compte, le pointeur en double alimente D). **États :** 0 Basique (fork Amdkn non adapté) ; 1 Adapté (fiche + adapter + manifeste, tests verts) ; 2 Vérifié (hold-outs verts + validation 13e) ; 3 Publié (état 2 + registre à jour). **Doctrine : zéro module en publication basique.** La première mesure (module par module, liste + nombre) est une sortie de l'étape 1 — aucune valeur n'est inventée avant.

**Statut licence Auto Research (D12) :** `karpathy/autoresearch` est **sans licence** (`license: null`, aucun fichier LICENSE). Le fork `Amdkn/autoresearch` est une **référence seule** : aucune copie, aucun vendoring, aucune importation de ses fichiers dans un artefact A'Space. La transposition est réécrite depuis la spécification du design (clean-room). Vérification : le 13e contrôle par comparaison de contenu à la validation. **Repli nommé :** si l'auteur s'oppose, le fork est supprimé ; si une licence apparaît, le design est **amendé** pour autoriser la réutilisation sous cette licence.

---

## F1 — Inférence souveraine unique (FKB01)

- **Modules :** freellmapi + codex-chatgpt-web + api-anything + freebuff + FreeVPS.
- **Fonction :** un seul point d'entrée d'inférence, avec bascule local → gratuit → distant.
- **Déjà existant :** `gateway-manifest.json` v5.0.0 (entrée `127.0.0.1:31415`) et `aspace_freecloud_gateway.py`. Esquissée en code, pas terminée.
- **Preuve attendue :** une requête traverse les trois tiers et revient ; un provider en panne ne casse pas la requête.
- **État :** proposée
- **Mesures :** — (H : — / C : — / D : —)

## F2 — Voix locale complète (FKB01)

- **Modules :** mimi + moshi + LFM3-Omni-2B + LoRA + needle + GLiNER2.5-multi-Decide.
- **Fonction :** signal brut → tokens → décision → appel d'outil, sans rien envoyer dehors.
- **Déjà existant :** chaîne spécifiée au §6 de `principes-fusion-runtime.md` et dans les synthèses Gemini (`mimi-lora-lfm3-omni.md`, `needle-gliner-edge.md`). Spécifiée, non implémentée.
- **Preuve attendue :** une phrase parlée devient une décision et un appel d'outil, en local, avec latence mesurée.
- **État :** proposée
- **Mesures :** — (H : — / C : — / D : —)

## F3 — Mémoire neuro-symbolique unique (FKB02)

- **Modules :** graphify + gbrain + infinite-brain-os + infinite-brain-harness + billion-context + auto-ontology + context-language-models + servers (MCP) + knowledge-catalog + dox.
- **Fonction :** une seule mémoire partagée (Shared Brain), lisible par tous les harnesses via MCP.
- **Déjà existant :** `00_Memoire/shared_brain/memory.jsonl`, `neuro_symbolic_bridge.py`, `start-memory-gateway.ps1`.
- **Preuve attendue :** un fait écrit par un harness est relu par un autre ; aucune mémoire en double.
- **État :** proposée
- **Mesures :** — (H : — / C : — / D : —)

## F4 — Studio vidéo unique (FKB06 + FKB07/02_Video)

- **Modules :** les 8 moteurs vidéo + OpenMontage + flute.
- **Fonction :** un seul pipeline vidéo agentique (de la démo au SaaS).
- **Déjà existant :** FKB07/02_Video les regroupe déjà en 10 moteurs ; reste à retirer les 8 doublons de FKB06 et à choisir l'emplacement canonique : **FKB07/02_Video**.
- **Preuve attendue :** une vidéo produite de bout en bout par le pipeline unique ; zéro doublon dans `.gitmodules`.
- **État :** proposée
- **Mesures :** — (H : — / C : — / D : —)

## F5 — Monde 3D unique (FKB03)

- **Modules :** cubefarm + agent-office + city-office + space-agent.
- **Fonction :** un seul monde (Cube Farm × Agent Office, city-office en anneau).
- **Déjà existant :** doctrine posée (FKB-INDEX : city-office = anneau routier autour du sanctuaire Cube Farm). `space-agent` est un pointeur amont non souverain : à forker d'abord.
- **Preuve attendue :** un agent visible dans le monde déclenche une action réelle du Runtime.
- **État :** proposée
- **Mesures :** — (H : — / C : — / D : —)

## F6 — Couche « Anything » unique (FKB04)

- **Modules :** api-anything + CLI-Anything + rea + hermes-agent (+ caveman, claude-mem une fois forkés).
- **Fonction :** une seule couche d'appel universel — toute API, tout CLI, tout outil, par le même contrat.
- **Déjà existant :** FKB04 est la première catégorie désignée comme prioritaire par le document de fusion. `hermes-agent` en doublon avec FKB00 à résorber (canonique : FKB04).
- **Preuve attendue :** un même appel traverse API, CLI et agent sans changer de contrat.
- **État :** acceptée (première expérience 2026-11-09, jugement 13e : PR #5 VALIDÉE, H-C1-1..7 CLOS ; mergée `4638ca6`, 2 parents)
- **Mesures :** H 5/5, C 89, D 9→8 (avant : C 89, D 9 ; après : C 89, D 8 — retrait du pointeur doublon hermes-agent FKB00, canonique FKB04)

## F7 — Moteur Money Maker unique (FKB07)

- **Modules :** 11 briques trading + dify + presenton + Scrapling + BusinessOS + les moteurs natifs (`aspace_marketplace_engine.py`, `aspace_road_to_market_engine.py`, `proof_first_outbound_pipeline.py`, `deploy_proof_first_cohort.py`).
- **Fonction :** un seul moteur de services B2B productisés, avec ses garde-fous.
- **Déjà existant :** thèse posée (FKB07 index, inspiration Corey Ganim) ; `AVERTISSEMENTS.md` encadre le trading en copilote strict. Les 4 pointeurs amont (nansen-cli, Scrapling, dify, presenton) sont à forker d'abord.
- **Preuve attendue :** une offre vendue de bout en bout par le moteur unique, avec sa preuve.
- **État :** proposée
- **Mesures :** — (H : — / C : — / D : —)

## F8 — Runtime triptyque natif (FKB00)

- **Modules :** automaton + infinity + openrig + agent-zero + pi + cordis + prime-agent + openbot + openmuse + OpenDots + OpenDuet.
- **Fonction :** le triptyque Âme / Système nerveux / Corps, en natif.
- **Déjà existant :** structure posée (FKB00 index, 6 pôles) et code natif existant (`a0_recursive_factory.py`, `a0_holon_swarm_runtime.py`, `a0_egm_bridge.py`, `aspace_freecompute_router.py`). Fusion la plus lourde : **en dernier**, FKB00 étant sanctuarisé.
- **Preuve attendue :** le Runtime tourne sans aucun des 11 sous-modules d'origine ; présence prouvée par heartbeat, pas par cron.
- **État :** en cours (D-N051, pas 1 mergé, pas 2 en cours — Phase D, pas 3 mergé, pas 4 en cours, pas 5 mergé)
- **Mesures :** compteur états 0–3 — 6 en état 0, 0 en état 1, 5 en état 2 (cordis, automaton, infinity, agent-zero, openrig), 0 en état 3 ; pas 0 : re-pin cordis sur l'adapter `6aab659`, index FKB00 corrigé (pôle 06 + sanctuarisation), bind cordis re-appliqué sur `main` (`726291d`) ; pas 1 : automaton adapté (adapter `7cdaa00`, 2 commits, smoke 21/21, suite 1 646/0/1, H-M3 ROUGE réserve js-tiktoken, jugement 13e), bind automaton re-appliqué sur `main` (`9728a0f`), doctrine native (LICENSE Apache-2.0, constitution, templates S1/S2/S3, heartbeat) déposée dans RigInfinity ; pas 1 mergé `7b46cf8` (jugement 482, H-M3 vert avec réserve : test 500 000 car. non exécuté, ~7 h, à borner ou courir sur une machine plus rapide à un pas ultérieur) ; pas 3 : infinity adapté (adapter `007409e`, smoke 13/13, suite 385/42 ROUGE QUALIFIÉ — 42 environnementaux pré-existants au gel, 0 imputable à l'adapter, daemon 100 % vert ; H-P3-3 hibernation PROUVÉE, H-P3-4 RAP PROUVÉE, H-P3-6 MCP PROUVÉE, H-P3-7 CONDITIONNELLE au pas 2), portage natif des 4 fonctions dans RigInfinity (`bd7c946` + `aad4993`, tests natifs 12/12), bind infinity re-appliqué sur `main` (`b0e6110`), cron 30 min absent (vérifié au fichier — aucune définition dans le repo ; heartbeat événementiel) ; pas 5 : agent-zero adapté (adapter `a042ddde`, 17 fichiers, suite adapter 36/36, suite propre au fork non exécutable sur cette VM — litellm absent, R-A1 ; H-P5-7 tri des 47 plugins 35/9/3 vérifié mécaniquement, écart 0 ; H-P5-8 QUALIFIÉ — 1 signal dans le fork, contrôle de mise à jour vers api.agent-zero.ai, défaut ON, abandonné avec le fork, 0 dans le natif ; H-P5-3 CONDITIONNELLE au pas 2 ; H-P5-6 tâche planifiée prouvée par reçu, cron refusé), portage natif des 4 fonctions du moteur dans RigInfinity (`e866578`, tests natifs lib 47/47 + agent_zero_proof 5/5 + daemon_proof 4/4), bind agent-zero re-appliqué sur `main` (`1a801ebc`), greffe coupée (références retirées des 3 fichiers natifs, gitlink retiré de `.gitmodules`) ; pas 4 : openrig adapté (adapter `b71bf87` + 2 commits de lignée, 13 fichiers, smoke 61/61, tsc 0 erreur ; `test:repo` VERT au re-run complet, 334 tests, 333 pass, 0 fail, 1 skipped ; lint VERT ; cli+tui complets avec échecs amont qualifiés — 13 daemon + 8 cli stables, 0 imputable à l'adapter, daemon incomplet, plafond ~35 min, 162/1 326 fichiers ; H-P4-2 starter 1/2/1, pas 4/5/4 ; télémétrie : 0 exporteur, 0 SDK, surface de lecture locale `/api/telemetry` — le « 0 signal » du design ne tient pas au gel ; H-P4-7 binding 127.0.0.1 seulement, surcharge tailscale refusée), portage natif des 3 fonctions + lignage dans RigInfinity (`a372582` + `e190645`, tests natifs lib 27/27 + daemon_proof 4/4), bind openrig re-appliqué sur `main` (`89f49c9`), gitlink re-pointé sur l'adapter (`649376c`)

## F9 — Moteur prédictif et wargame unique (FKB00)

- **Modules :** MiroFish + PathFM + autogluon + timesfm + chronos-forecasting + mitra-2 + tabfm + elephant-goldfish-model + gstack + superpowers + get-shit-done.
- **Fonction :** un seul moteur de prédiction (séries, tableaux, wargames) et de spécifications propres.
- **Déjà existant :** fiches modèles dans `02_PredictiveWargame_MachineLearning/models/`, moteurs natifs (`triptych_autogluon_engine.py`, `wargame_tabular_engine.py`, `wargame_business_launch_auditor.py`), registre HF (`HF-SOVEREIGN-INDEX.md`).
- **Preuve attendue :** une prévision validée sur données écartées (hold-out), jamais sur les données d'entraînement.
- **État :** proposée
- **Mesures :** 7 modules ML en état 1 (pas A, D-N053) ; 4 modules MasterSpec en état 0 (pas C) ; C (F9) : 4

## F10 — Catalogue de skills unique (FKB08)

- **Modules :** anthropic-skills + mattpocock-skills + openai-plugins + claude-video.
- **Fonction :** un seul catalogue de compétences, versionné, avec ses règles d'usage.
- **Déjà existant :** les trois skills Leon van Zyl installés le 2026-11-05 montrent le pattern (skill = dossier versionné + références). `claude-video` et `mattpocock-skills` sont des pointeurs amont à forker.
- **Preuve attendue :** une skill appelée par son nom unique, sans ambiguïté de source.
- **État :** proposée
- **Mesures :** — (H : — / C : — / D : —)

---

## Adaptations (D-N048 — §D10)

**Un seul registre, deux sections.** Les 21 adaptations ne sont pas des fusions (une fusion merge des modules ; une adaptation souverainise un module). L'Auto Research consomme cette section : il lit les états d'adaptation pour proposer des fusions (une fusion ne merge que des modules dont l'état d'adaptation est connu). Les compteurs C et D sont les mêmes (les adaptations alimentent C, les fusions alimentent D).

**États :** 0 Basique (fork Amdkn non adapté) ; 1 Adapté (fiche + adapter + manifeste, tests verts) ; 2 Vérifié (hold-outs verts + validation 13e) ; 3 Publié (état 2 + registre à jour). Table de gel : `01_Forkable/FORKS-AMONT-21-FREEZE.md` (D-N048 V0).

| Module (fork Amdkn) | État | Commit gelé | Manifeste | Licence |
|---|---|---|---|---|
| deepseek-harness | 2 | `fcc0ad4` | `fiber:a0:deepseek-harness` | MIT |
| herdr-app | 2 | `b1a2a67` | `fiber:a0:herdr-app` | Apache-2.0 |
| t3code | 2 | `dc72705` | `fiber:a0:t3code` | MIT |
| openclaw | 2 | `ce7788f` | `fiber:a0:openclaw` | MIT |
| claude-code | 2 | `0ed9469` | `fiber:a0:claude-code` (D12 validé) | **sans licence** |
| codex | 2 | `27fcd7c` | `fiber:a0:codex` | Apache-2.0 |
| wikiskill | 2 | `cdc291c` | `fiber:a0:wikiskill` | MIT |
| adk-recipes | 2 | `a93b9cc` | `fiber:a0:adk-recipes` | Apache-2.0 |
| rrsi | 2 | `be50316` | `fiber:a0:rrsi` | Apache-2.0 |
| dream-rsi | 2 | `8ec35bd` | `fiber:a0:dream-rsi` | Apache-2.0 |
| space-agent | 2 | `10f4ffd` | `fiber:a0:space-agent` | MIT |
| caveman | 2 | `3dc497a` | `fiber:a0:caveman` | Apache-2.0 |
| claude-mem | 2 | `a926f57` | `fiber:a0:claude-mem` | Apache-2.0 |
| nansen-cli | 2 | `0b39ae5` | `fiber:a0:nansen-cli` | MIT |
| Scrapling | 2 | `c5121c7` | `fiber:a0:scrapling` | BSD-3-Clause |
| dify | 2 | `b29552a` | `fiber:a0:dify` | Apache-2.0 modifiée (§0.1) |
| presenton | 2 | `9af2b47` | `fiber:a0:presenton` | Apache-2.0 |
| mattpocock-skills | 2 | `4ae2317` | `fiber:a0:mattpocock-skills` | MIT |
| openai-plugins | 2 | `d420d13` | `fiber:a0:openai-plugins` | **sans licence** |
| claude-video | 2 | `03ceb42` | `fiber:a0:claude-video` | MIT |
| llm-wiki (gist) | rapatrié | — | — (pas un module) | — (propre) |

**Baseline V0 (D-N048) :** C = 0/21 forkés, 0 adaptés ; D = 8. Renommage enregistré : `Amdkn/mattpocock-skills`, `fiber:a0:mattpocock-skills` (§D2). Gist rapatrié : `00_Memoire/bundle/concepts/llm-wiki.md`, pointeur retiré, compte 119 → 118 (§D3).

---

## Adaptations (D-N053 — Runtime, §D16)

**Compteur d'état 0 du Runtime : 25 → 15 (pas A + F8 pas 3 + F8 pas 5 + F8 pas 4).** 7 modules ML adaptés (état 0 → 1) ; infinity adapté + fusionné par F8 pas 3 (état 0 → 2) ; agent-zero adapté + fusionné par F8 pas 5 (état 0 → 2) ; openrig adapté + fusionné par F8 pas 4 (état 0 → 2) ; 15 restent en état 0 (pas B, C, F1, F2 + 5 coordonnés par leur propre piste). Mesuré au registre, pas déclaré (H-A8).

**États :** 0 Basique (fork Amdkn non adapté) ; 1 Adapté (fiche + adapter + manifeste, tests verts) ; 2 Vérifié (hold-outs verts + validation 13e) ; 3 Publié (état 2 + registre à jour).

| Module (fork Amdkn) | État | Pin (adapter) | Manifeste | Licence |
|---|---|---|---|---|
| autogluon | 1 | `2de7c39` | `fiber:a0:autogluon` | Apache-2.0 |
| mitra-2 (natif) | 1 | `2676f75` | `fiber:a0:mitra-2` | Apache-2.0 |
| chronos-forecasting | 1 | `c749362` | `fiber:a0:chronos-forecasting` | Apache-2.0 |
| timesfm | 1 | `7cb4f64` | `fiber:a0:timesfm` | Apache-2.0 |
| tabfm | 1 | `0a56dff` | `fiber:a0:tabfm` | Apache-2.0 |
| PathFM | 1 | `8bcdd5b` | `fiber:a0:PathFM` | CC BY-NC 4.0 |
| MiroFish | 1 | `dff2f01` | `fiber:a0:mirofish` | AGPL-3.0 |
| elephant-goldfish-model | 0 | `3d643fe` | — | Apache-2.0 |
| get-shit-done → gsd-core | 0 | (nouveau fork) | — | MIT |
| gstack | 0 | `a79170c` | — | MIT |
| superpowers (canonique) | 0 | `4ca2922` | — | MIT |
| a0-plugins | 0 | `f73f767` | — | MIT |
| agent-zero (F8 pas 5) | 2 | `a042ddde` | `fiber:a0:agent-zero` | MIT |
| spynel | 0 | `3e076a1` | — | MIT |
| tuxee | 0 | `5c51b78` | — | MIT |
| infinity (F8 pas 3) | 2 | `007409e` | `fiber:a0:infinity` | Apache-2.0 |
| openrig (F8 pas 4) | 2 | `649376c` | `fiber:a0:openrig` | Apache-2.0 |
| herdr (F1) | 0 | `df9b626` | — | Apache-2.0 |
| herdr-core (F1) | 0 | `14a3772` | — | Apache-2.0 |
| orca (F2) | 0 | `b659760` | — | MIT |
| OpenDots (F8 pas 7) | 0 | `d4214af` | — | MIT |
| OpenDuet (F8 pas 7) | 0 | `f52288f` | — | MIT |
| openbot (F8 pas 7) | 0 | `2b5b14f` | — | MIT |
| openmuse (F8 pas 7) | 0 | `a4944f4` | — | MIT |
| prime-agent (F8 pas 6 + R2) | 0 | `3ba6791` | — | MIT |

**Pas A (ML socle) :** 7/7 adaptés, H-M1..M7 + H-A1..H-A5 verts (bornes nommées : suite autogluon bornée ; PathFM sans suite amont ; MiroFish : aucune simulation réelle, le smoke prouve la frontière) ; MiroFish isolé en service (§D2) ; PathFM confiné au profil interne, ligne du manifeste ML corrigée à CC BY-NC 4.0 (§D3) ; pin = commit adapter (§D8, patron F8 D4 — la proposition « pin = adapter+bind HEAD » des groupes 1 et 3 est consignée à la PR pour arbitrage du 13e).

---

*Registre créé par Ryan (Factory), dispatch D-N047, Phase A2 — design Clara signé 2026-11-09. Dix fusions en « proposée » ; aucune mesure n'est inventée avant la première mesure du compteur d'état 0 (sortie de l'étape 1).*
