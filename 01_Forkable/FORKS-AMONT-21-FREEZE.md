# Table de gel — Fork + adaptation des 21 pointeurs amont (D-N048, V0)

**Mission :** D-N048 (suite de D-N047, close 12:41 EST).
**Design :** Clara, `~/workspace/v4-factory/plans/FORKS-AMONT-21-plan-borne-vagues.md` (signé 13:43 EST).
**Ancre :** V5 master HEAD `d93929d` — `.gitmodules` : 119 entrées (98 Amdkn, 21 non-Amdkn) avant V0 ; **118 après V0** (gist rapatrié, pointeur retiré).
**Date V0 :** 2026-11-09.

## Baseline compteurs (V0, avant le premier fork — §D8)

- **C = 0/21 forkés, 0 adaptés.** Chaque fork créé fait entrer son module en C (état 0) ; chaque adaptation validée le fait sortir de C (état ≥ 1). C monte à 21 puis redescend vers 0. Les 2 forks référence-seule restent en C tant qu'aucune adaptation clean-room n'est construite et validée.
- **D = 8** (inchangé par cette mission) — les 8 moteurs vidéo en double : video-director, take-one, rossark-motion-skill, reanimate, huashu-motion, explainroo, earshot, argo. Vérifié par le runner sur la branche V0 (`measure` : C=89 état 0 global, D=8, 118 entrées).
- **Gist rapatrié (§D3) :** `llm-wiki` → `00_Memoire/bundle/concepts/llm-wiki.md` (corps gist 11 985 o, byte-identique, sha256 `dc3efe98ae62f23dd08acad13aba2e95287beb20b6bec2f4af0423557fe37401`) ; source gist `34a4b4bf6d54b1828ba8c256615619e8`, propriétaire Amdkn, créé 2026-11-06 ; le gist reste en place. Pas d'adresse `fiber:a0:*`, pas de manifeste (fichier de concept, pas un module).
- **Renommage enregistré (§D2) :** fork `Amdkn/mattpocock-skills`, adresse `fiber:a0:mattpocock-skills`. Le chemin du sous-module est inchangé (seule l'URL est repointée). `Amdkn/skills` (fork d'`anthropics/skills`) est intouché.

## Correction de prémisse (§D3, portée au jugement du 13e)

Le design dit le fichier rapatrié « versionné sous la licence du repo V5 (vérifiée à l'exécution depuis le fichier LICENSE du repo) ». **Vérifié à l'exécution : le repo V5 ne porte aucun fichier LICENSE** (recherche au fichier + API GitHub `license` : 404, aucune licence détectée). La licence du repo ne peut donc pas être vérifiée ; le fichier rapatrié est un contenu propre (Amdkn), sans licence tierce, versionné dans le repo tel quel. Aucune licence n'est inventée.

## Table des 21 (§2 — gel, licence, adapter, manifeste, vague)

HEAD = commit de tête de la branche par défaut, établi par le Discover. Le gel fige ces HEAD. Adapter = `aspace-<module>-adapter`. Manifeste = `fiber:a0:<module>` (sauf gist : pas d'adresse).

| # | Module (amont → fork Amdkn) | Licence | Branche | HEAD gelé | Taille | Vague | Fork | État |
|---|---|---|---|---|---|---|---|---|
| 1 | deepseek-harness (`deepseek-ai/…`) | MIT | master | `fcc0ad4` | ~352 Mo | V3b | non | 0 |
| 2 | herdr-app (`herdrdev/…`) | Apache-2.0 | master | `b1a2a67` | 13,5 Mo | V3a | non | 0 |
| 3 | t3code (`pingdotgg/…`) | MIT | main | `dc72705` | ~742 Mo | V3b | non | 0 |
| 4 | openclaw (`openclaw/…`) | MIT | main | `ce7788f` | ~13,3 Go | V3b, dernier | non | 0 |
| 5 | claude-code (`anthropics/…`) | **sans licence** | main | `0ed9469` | ~33 Mo | V3b | non | 0 |
| 6 | codex (`openai/…`) | Apache-2.0 | main | `27fcd7c` | ~723 Mo | V3b | non | 0 |
| 7 | wikiskill (`ashutoshsinghpr7/…`) | MIT | main | `cdc291c` | 424 Ko | V3a | non | 0 |
| 8 | adk-recipes (`google/…`) | Apache-2.0 | main | `a93b9cc` | ~309 Mo | V3b | non | 0 |
| 9 | rrsi (`google-research/…`) | Apache-2.0 | main | `be50316` | 2,4 Mo | V3a | non | 0 |
| 10 | dream-rsi (`google-research/…`) | Apache-2.0 | main | `8ec35bd` | 213 Ko | V3a | non | 0 |
| 11 | llm-wiki (gist Amdkn) | — (propre) | — | — | 11 985 o | V0 | rapatrié | — |
| 12 | space-agent (`agent0ai/…`) | MIT | main | `10f4ffd` | ~21 Mo | V2 | non | 0 |
| 13 | caveman (`JuliusBrussee/…`) | Apache-2.0 | main | `3dc497a` | ~21 Mo | V1 | non | 0 |
| 14 | claude-mem (`TheDotMack/…`) | Apache-2.0 | main | `a926f57` | ~770 Mo | V1 | non | 0 |
| 15 | nansen-cli (`nansen-ai/…`) | MIT | main | `0b39ae5` | ~6,2 Mo | V4 | non | 0 |
| 16 | Scrapling (`D4Vinci/…`) | BSD-3-Clause | main | `c5121c7` | ~16 Mo | V4 | non | 0 |
| 17 | dify (`langgenius/…`) | **Apache-2.0 modifiée** (§0.1) | main | `b29552a` | ~687 Mo | V4 | non | 0 |
| 18 | presenton (`presenton/…`) | Apache-2.0 | main | `9af2b47` | ~1,23 Go | V4 | non | 0 |
| 19 | mattpocock-skills → `Amdkn/mattpocock-skills` | MIT | main | `4ae2317` | ~2,2 Mo | V5 | non | 0 |
| 20 | openai-plugins (`openai/…`) | **sans licence** | main | `d420d13` | ~109 Mo | V5 | non | 0 |
| 21 | claude-video (`bradautomates/…`) | MIT | main | `03ceb42` | 366 Ko | V5 | non | 0 |

**Contraintes nommées (§2) :** Scrapling — clause de non-approbation ; dify — mono-tenant uniquement, LOGO/copyright frontend intacts ; nansen-cli — adaptation sans identifiant, sans crédit dépensé ; adk-recipes — signal télémétrie, audit en priorité ; claude-code + openai-plugins — D12, référence seule, clean-room ; openclaw — clone partiel obligatoire, en dernier ; t3code, codex, claude-mem, presenton, dify — clone partiel (> 500 Mo) ; caveman (Go), mattpocock-skills (Shell), space-agent / nansen-cli / openai-plugins (JS) — couture contrat seule (§1.5).

**Politique de gel (§D5) :** revisite par signal de dérive uniquement (inventaire hebdomadaire Auto Research), jamais de fast-forward silencieux. Première revisite nommée : `space-agent` (HEAD de 5 mois).
