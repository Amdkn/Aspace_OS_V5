# Jugement 13e — D-N051 F8 pas 7 : les 4 bots (PR #42)

**Juge :** 13e (fonction indépendante — ni exécutant, ni coordinateur).
**Objet :** PR [#42](https://github.com/Amdkn/Aspace_OS_V5/pull/42) — « D-N051 F8 pas 7 : les 4 bots coéquipiers adaptés + fusionnés (état 0 → 2) »,
branche `ryan/d-n051-f8-pas7`, base master `446e927`, tête `e8a3496` (2 commits `4f73046` + `e8a3496`).
**Norme :** plan borné signé Clara `FUSION-F8-PAS7-BOTS-COEQUIPIERS-plan-borne.md` (D1–D16, H-M1..M7 ×4, H-P7-1..10, H-F8-1/2/4/5/9).
**Pièces lues en entier :** plan, Discover Bill, `RAPPORT-PAS7.md`, `RESULTS-F8-P7.json`, reçu `G-20261112-008`.
**Méthode :** rien pris sur parole — chaque fait re-vérifié à la source (API GitHub, clones frais `~/workspace/juge-p7/`,
rejeu du harnais `run_holdouts_juge.py` → `RESULTS-JUGE-P7.json`, re-cours complet des 4 suites + cargo + strace).
`TMPDIR` sur `/home` pour tous les runs (`/tmp` 512 Mo, leçon de l'exécution).

## Verdict : VALIDÉE AVEC RÉSERVES

## Recommandation merge : OUI après amendement — INTERDIT sur la tête `e8a3496`

Le fond est validé (adaptations réelles, binds réels, surface native réelle, H-M3 ROUGE QUALIFIÉ confirmé avec des
chiffres meilleurs que ceux du rapport). **Un seul défaut bloque le merge en l'état, précis et mécanique : le gitlink
V5 d'openbot est resté au gel `2b5b14f`, non re-piné sur le main avec bind — H-P7-1 / §D8(c) non conformes.**
Le merge est autorisé dès l'amendement ci-dessous livré, vérifié par le coordinateur à l'API + CI verte —
sans nouveau jugement complet.

### Conditions exactes de merge (toutes à remplir, dans l'ordre)

- **C1 — Re-pin openbot :** gitlink `01_Forkable/FKB00_Runtime/06_Sovereign_Bot_Coworkers/openbot` =
  **`6e62238`** (main HEAD, bind + adapter + fix ; lecture littérale de §D8(c) « re-pin de V5 sur le `main` avec bind »).
  Repli acceptable, précédent p3 : `91f711c` (adapter, dont l'arbre contient déjà le bind en parent) — mais `6e62238`
  est exigé en premier choix : c'est le main HEAD, il satisfait la lettre ET le fond.
- **C2 — Fiches :** remplacer dans les 4 fiches la ligne trompeuse « Pin (bind) : `<bind-sha>` » par deux lignes
  distinctes — « Pin V5 : `<gitlink réel>` » et « Bind : `<bind-sha>` » (openbot : pin `6e62238` après C1 ;
  openmuse/OpenDots/OpenDuet : pin « retiré au pas 7 (H-F8-1) », bind nommé).
- **C3 — Fiche OpenDuet :** mettre à jour H-M3 « EN COURS » (lignes R-A1 et Hold-outs) → « QUALIFIÉ »
  avec les chiffres finaux (eval 12/62, 0 wrong ; suite openbot 0.3.3 = H-M3-openbot).
- **C4 — Registre :** consigner le re-pin dans le segment pas 7 de `FUSIONS-REGISTRY.md` (il dit aujourd'hui
  « plan §D8 littéral » sans nommer aucun re-pin — voir F3).
- **C5 — CI :** re-courir la CI sur la tête amendée ; 8/8 `success` **complétés** exigés. La Cat 04 est
  bloquée `in_progress` avec conclusion `success` depuis l'ouverture de la PR (voir R-J9) : si elle reste
  bloquée après l'amendement, le coordinateur la relance ; le merge reste autorisé sur `mergeable: true`
  + conclusions `success`, mais pas sur une Cat 04 en échec.

---

## 1. La question principale — le pin openbot (Q1) : NON re-piné, amendement exigé

**Fait vérifié au fichier (clone frais, branche PR, tête `e8a3496`) :**

```
$ git ls-tree HEAD 01_Forkable/FKB00_Runtime/06_Sovereign_Bot_Coworkers/
160000 commit 2b5b14fc163fd12734ca871dddc68d8ffa31a1b7  .../openbot
```

Le gitlink vaut `2b5b14f` = le gel brut. Il ne contient **ni le bind, ni l'adapter** : un `git submodule update`
d'openbot sur cette tête livre l'amont brut, zéro code A'Space. Le constat du coordinateur est exact.

**Ce qui existe réellement sur le fork (vérifié à l'API, un par un) :**
`main` = gel → bind → adapter → fix, `ahead 3`, `behind 0`, 14 fichiers A'Space seuls, sur les 4 forks.
openbot : bind `fea2371` (blob `aspace-plugin.json` `087bd7f`, byte-identique à `dbf1693` sur `aspace-v5-native` —
vérifié à l'API), adapter `91f711c` (13 fichiers, code TypeScript réel, stdlib seule, 0 import du fork),
fix `6e62238` (renommage `adapter.test.ts` → `adapter.checks.ts`). openmuse `e606af2` / `51baa4a` / `01d57a7` ;
OpenDots `c423bcf` / `4051f5c` / `abcb35d` ; OpenDuet `4b6bf40` / `3a48a22` / `be7ec83`. Les 4 binds existent
sur `main` ET sur `aspace-v5-native`, comme l'exige §D8(a)–(b). **Seule l'étape §D8(c) manque : le re-pin.**

**Pourquoi ce n'est pas acceptable tel quel :**
- Le plan l'exige trois fois : §D8(c) « re-pin de V5 sur le `main` avec bind », H-P7-1 « les pins V5 pointent
  sur les `main` avec bind », §5 « les 4 binds sont re-appliqués sur `main` et les pins pointent sur les `main`
  avec bind ». La condition de succès n'est pas remplie pour le seul pointeur survivant (les 3 autres ont quitté
  `.gitmodules` — pour eux le re-pin est sans objet, voir ci-dessous).
- L'état 2 revendiqué pour openbot (« adapté + fusionné ») repose sur V5 qui référence le module adapté.
  Avec le pin au gel, V5 ne référence que l'amont brut : la fusion est déclarée, pas pointée.
- Le précédent pas 3 ne sauve pas le pin-au-gel : gitlink infinity = adapter `007409e` (vérifié au fichier,
  `@446e927` ; main HEAD = bind `b0e6110`) — le pin p3 contient l'adapter, même s'il n'est ni le gel ni le
  main HEAD. Le pin-au-gel, lui, ne contient rien d'A'Space. La substance du précédent est « le pin contient
  l'adaptation » ; `91f711c` la satisfait (arbre = gel + bind + adapter), `6e62238` la satisfait et satisfait
  en plus la lettre (« main avec bind »). `2b5b14f` ne satisfait ni l'une ni l'autre.

**Le contenu des commits adapter (« This is by an automated agent, not a human. ») :** l'en-tête est la
formule prescrite par `AGENTS.md` V5 §2.1 pour tout message automatisé publié sur GitHub — pas un signal
d'anomalie. Le contenu est vérifié réel : 13 fichiers par adapter, code TS (lineage/skin/computer/telemetry/
routines/gateway/triage + contract + AGENTS + README + package + checks), 0 import du code du fork
(grep sur les 4 clones frais : 0 import de `aspace-*-adapter` hors du dossier adapter). La preuve H-M2
(compare gel..fix, 14 fichiers A'Space seuls, `ahead 3`) est exacte sur les 4 forks.

**Décision Q1 :** le pin-au-gel est **refusé**. Amendement C1 avant merge. Ni « merge tel quel avec réserve »,
ni suivi post-merge : le re-pin est l'acte même de la fusion pour le pointeur survivant, et il coûte une ligne.

## 2. Hold-outs — verdicts du juge (preuves re-courues)

### H-M1..M7 ×4 — tous PASS sauf H-M3 (voir §3)

| Hold-out | openbot | openmuse | OpenDots | OpenDuet | Preuve du juge |
|---|---|---|---|---|---|
| H-M1 gel | PASS | PASS | PASS | PASS | gels consignés en fiche ; `main` HEAD = fix attendu (API) |
| H-M2 adapter seul | PASS | PASS | PASS | PASS | compare gel..fix `ahead 3/behind 0`, 14 fichiers A'Space seuls (API, ×4) |
| H-M3 suite fork | **QUALIFIÉ** | **QUALIFIÉ** | **QUALIFIÉ** | **QUALIFIÉ** | §3, re-cours complets ci-dessous |
| H-M4 télémétrie zéro | PASS | PASS | PASS | PASS | 4 audits lus (5 déclencheurs tranchés chacun) + strace re-couru §4 |
| H-M5 manifeste | PASS | PASS | PASS | PASS | `fiber:a0:<bot>`, `levels.current = 2`, lus dans le clone frais PR |
| H-M6 frontière | PASS | PASS | PASS | PASS | adapter seul code A'Space (0 import hors adapter, grep clones frais) |
| H-M7 fiche | PASS | PASS | PASS | PASS | 4 fiches présentes en `00_A0_Core/` (branche PR) |

Suites adapter **re-courues par le juge en clones frais, toutes vertes, rc=0** : openbot 9/9 (`bun test ./tests/adapter.checks.ts`),
openmuse 8/8, OpenDots 8/8 (`node --test tests/adapter.checks.ts`), OpenDuet 9/9. Identiques aux chiffres de l'exécutant.

### H-P7-1..H-P7-10

| # | Verdict juge | Preuve |
|---|---|---|
| H-P7-1 gels + binds | **NON CONFORME (pin)** | Binds OK sur `main` ×4 (API) ; triage 181 versé et réel (§5) ; **mais pin V5 openbot = gel `2b5b14f`, non re-piné** (§1). Le harnais d'origine ne vérifiait pas le pin (voir F1). |
| H-P7-2 surface native | PASS | Natif `11a82ba`, parent `655b2a4`, 4 fichiers exacts (API + `git show`) ; `bots_proof` 7/7 **re-couru** (cargo, clone frais), `bots.rs` lu (601 l. : `:4100`, `x-openbot-bot-id`, gateway `:31415`, `refine_available() = false`, `telemetry_emitters()` vide). |
| H-P7-3 SKILL re-pointée | PASS | Diff vérifié : conteneur OpenBot / console OpenMuse → computer-service natif + takeover natif ; chaînes `aspace_marketplace_engine.py` re-pointées (3 noms retirés de `open_source_engines`). |
| H-P7-4 traits | PASS | `platform_registers_three_skins ... ok` + `coworker_survives_restart_without_intelligence ... ok` dans mon cargo re-couru. |
| H-P7-5 un seul daemon | PASS (réserve R-J8) | `routine_executes_in_the_job_loop_with_receipt ... ok` + `routine_refuses_sub_floor_interval ... ok` re-courus ; aucun `cron-parser` / `CronExpressionParser` exécutable dans le natif (grep clone frais ; mentions en doc/commentaires = abandon nommé, cf. écart #5 du rapport, exact). |
| H-P7-6 Intelligence | **QUALIFIE (CONDITIONNELLE)** | Dépendance pas 6 correctement nommée et suivie (§6) — ne bloque pas le merge. |
| H-P7-7 télémétrie zéro | PASS | 4 audits lus (5 déclencheurs tranchés un par un, N/A justifiés) ; strace **re-couru** : 7/7, 2 `connect()`, tous `127.0.0.1`, 0 non-loopback (§4). |
| H-P7-8 vendu abandonné | PASS | Natif = 4 fichiers, aucun vendu ; OpenDuet vendu = 2 336 fichiers comptés en clone frais, 6 YAML + 3 dossiers d'évals présents ; identité portée sur le gel 0.3.3 (triage adapter OpenDuet, 6 YAML vérifiés). |
| H-P7-9 manifestes + fiches | PASS (réserve R-J3) | 4 manifestes + 4 fiches présents ; section OpenBot réécrite exactement selon l'annexe §7 (diff vérifié : titre CopilotKit, ligne 387 corrigée, lien `CopilotKit/OpenBot`). Fiche OpenDuet périmée sur H-M3 (C3). |
| H-P7-10 smoke | **PARTIEL** | Smoke module re-couru (adapters 9/9, 8/8, 8/8, 9/9 + natif 7/7) ; cycle complet du Runtime = ce harnais (§7). |

### H-F8

| # | Verdict juge | Preuve |
|---|---|---|
| H-F8-1 3 pointeurs retirés | PASS | `.gitmodules` 117 → 114 (compté au fichier) ; OpenMuse/OpenDots/OpenDuet absents ; openbot conservé (pas 8). |
| H-F8-2 cycle sans originaux | **PARTIEL** | Mécanisme natif livré (H-P7-2) ; grep dans la branche PR : aucune référence exécutable restante aux 3 repos retirés (restes = fiches/audits de provenance + `index.md` documentaire) ; cycle complet = ce harnais (§7). |
| H-F8-4 un seul daemon | PASS (réserve R-J8) | Sprawl ~28 → 1 par construction (daemon unique, `fn main` unique, Spire/Postgres/compose non portés — vérifié au code natif) ; compteurs registre 0/1/10/0. |
| H-F8-5 heartbeat, pas de cron | PASS | Greps re-courus sur clones frais (adapters `package.json` + natif `Cargo.toml`/`.rs`) : 0 `cron-parser`, 0 `CronExpressionParser` exécutable. |
| H-F8-9 plafonds | **QUALIFIÉ** | Dépense non mesurable depuis la factory (patron p5, accepté) ; 0 appel sortant, 0 secret lu, 0 crédit provider (reçu + preuves strace). Plafonds 1 %/5 %/20 % non mesurés, seulement affirmés non mesurables (§7). |

Compteurs vérifiés au fichier (branche PR) : **F8 0/1/10/0**, **D-N053 25 → 3** (herdr, herdr-core, orca restants).
Recompte de `RESULTS-F8-P7.json` par le juge : **37 PASS, 6 QUALIFIÉ, 2 PARTIEL, 0 FAIL — exact** (le recomptage
du coordinateur est confirmé).

## 3. H-M3 ROUGE QUALIFIÉ ×3 — tranché par le juge : 0 échec imputable à l'adapter

Règle (§D15) : seul le delta bloque. Le 13e tranche — voici le rejeu complet, en clones frais, `TMPDIR` sur `/home`.

### 3.1 openbot — `bun test` complet re-couru (914 s, clone frais @`6e62238`)

| Run | pass | skip | fail | errors | tests | fichiers | durée |
|---|---|---|---|---|---|---|---|
| **Juge, adapté `6e62238`** | **10 929** | 292 | **306** | **263** | 11 527 | 1 205 | 914 s |
| Exécutant, gel `2b5b14f` | 10 929 | 292 | 306 | 263 | 11 527 | 1 205 | 792 s |
| Exécutant, « adapté » (contaminé) | 10 891 | 292 | 345 | 285 | 11 528 | 1 206 | 2 191 s |

**Mon run adapté est numériquement identique au gel de l'exécutant, et meilleur que son run « adapté ».**
Carte des `(fail)` par fichier : **identique au gel, fichier par fichier** (21 fichiers, 146 lignes `(fail)`,
comptes par fichier égaux — ex. `triggers.test.ts` 73/73, `work-queue` 19/19 ; fichiers `(error)`-seuls
identiques : `openai-compatible-endpoint`, `routine-runner`, `unreachable-bot`).

**Pourquoi le run « adapté » de l'exécutant diverge — deux contaminations prouvées dans son propre log :**
(a) **Renommage en cours de run :** son log ligne 8936 montre `aspace-openbot-adapter/tests/adapter.test.ts:`
suivi de `error: ENOENT reading ".../adapter.test.ts"` — le fix `6e62238` (renommage → `adapter.checks.ts`)
a atterri pendant que `bun test` tournait ; bun avait énuméré 1 206 fichiers et a compté le fichier disparu
en erreur (+1 fichier, +1 test, +erreurs). Son run a donc été lancé à l'état adapter `91f711c`, pas à `6e62238`.
(b) **Charge parallèle :** cargo + vitest + `node --test` concurrents sur 1,5 CPU partagé (dit dans sa propre
fiche) → timeouts dans 19 fichiers qui **passent tous dans mon run propre** (ex. `a2ui-markdown`, `browser-page`,
`computer-activity-conversation`, `production-loader-boundary`, `tool-selection-environment-restoration`,
`scripts/setup-composio`, `toolkit/lease`, …).
Preuve structurelle, indépendante des runs : le diff gel..fix ne touche **0 fichier du fork** (14 fichiers,
tous A'Space, 441 insertions) et **l'adapter n'est importé par aucun code du fork** (grep clones frais).
Une suite ne peut pas échouer « à cause de » code qu'elle n'importe pas et qui n'existe pas dans son arbre.

**Tranché : H-M3-openbot = ROUGE QUALIFIÉ, 0 échec imputable à l'adapter.** Les chiffres du rapport restent
vrais comme compte-rendu d'un run contaminé ; la mesure propre est celle du juge ci-dessus.

### 3.2 openmuse — `node --test` complet re-couru (922 s, clone frais @`e606af2`)

| Run | pass | fail | fichiers en échec |
|---|---|---|---|
| **Juge, adapté** | **517 / 519** | 2 | browser, conversation-jev |
| Exécutant, adapté (re-run) | 499 | 3 fichiers | browser, conversation-calendar, conversation-jev |
| **Juge, gel `a4944f4` (2 fichiers, worktree frais)** | 39 / 40 | 1 | conversation-jev seule — **browser passe au gel** |
| Exécutant, gel (3 fichiers) | 29 pass | 2 fichiers | browser, conversation-jev |

- `conversation-jev` échoue des deux côtés, même cause (« Agent execution failed: Connection interrupted »,
  appels modèle sans provider dans la sandbox) — **pré-existant, déterministe**.
- `browser` est **flaky des deux côtés** : échoue en run complet adapté (570 s, timeout) et au gel chez
  l'exécutant, **passe** au gel chez moi en run isolé (2 fichiers) et **passe seul sur l'arbre adapté
  (25/25, rc=0, re-couru par le juge)** — flake de charge, pas l'adapter.
- `conversation-calendar` passe dans mon run complet adapté (12/12 chez l'exécutant seul ; absent de mes
  échecs) — le diagnostic « flake de charge » de l'exécutant est confirmé.
Caveat : la VM a tué 5 processus par OOM pendant mon run openmuse (limite mémoire partagée) ; le run a
néanmoins produit un sommaire complet et cohérent (519 = 517 + 2, 0 annulé/ignoré). La pression mémoire
fait partie de la charge qui rend `browser` flaky — elle ne change pas le verdict.

**Tranché : H-M3-openmuse = ROUGE QUALIFIÉ, 0 échec imputable à l'adapter.**

### 3.3 OpenDots — `vitest run` complet re-couru (51 s, clone frais @`c423bcf`)

| Run | pass | fail | fichiers en échec |
|---|---|---|---|
| **Juge, adapté** | **343 / 351** | 8 | telemetry (5), transport (2), setup-telemetry (1) |
| Exécutant, adapté (re-run) | 340 / 351 | 11 | telemetry (7), transport (2), setup-telemetry (1), computer audit-storage (1) |
| **Juge, gel `d4214af` (3 fichiers, worktree frais)** | 11 / 21 | 10 | les 8 du juge + 2 de plus (fallback installation, `TELEMETRY_SAMPLE_RATE=0`) |

Mes 8 échecs adaptés sont un **sous-ensemble strict** de mes 10 échecs au gel, mêmes noms de tests
(timeouts `captureRuntime` 5 000 ms, transport DNS-pinned, setup-telemetry persistance).
Le 11e échec de l'exécutant (computer audit-storage) **passe dans mon run** — flake de charge confirmé.

**Tranché : H-M3-OpenDots = ROUGE QUALIFIÉ, 0 échec imputable à l'adapter.**

### 3.4 OpenDuet — eval triage re-courue (règles seules)

`bun evals/triage/run.ts --rules-only` en clone frais @`4b6bf40`, rc=0 : **12/62 décidées, 0 wrong,
100 % sur les décidées, 0 désaccord — identique à l'exécutant.** Portée exacte (à ne pas sur-vendre) :
l'éval exécute le code de triage **vendu 0.2.0** (`openbot/server/src/openduet/triage`) comme fixture,
pas le code natif — c'est la preuve prévue par §D15, pas une preuve du natif. reply-chips/voice restent
des fixtures non exécutables ici (stack + Chrome requis) — conforme au plan.
**Tranché : H-M3-OpenDuet = QUALIFIÉ** (evals + suite openbot 0.3.3 = §3.1).

## 4. Télémétrie native — capture re-courue (H-M4 / H-P7-7)

`cargo test -p infinity-daemon` re-couru en clone frais @`11a82ba` : **rc=0, 62 lib + 5 + 7 (`bots_proof`) +
8 + 4 + 4, tout vert** ; `clippy --all-targets -- -D warnings` rc=0 ; `cargo fmt --check` rc=0.
`strace -f -e trace=connect` sur `bots_proof` (avec `CARGO_MANIFEST_DIR` posé, sinon le test
`telemetry_zero_in_the_native_tree` échoue sur `manifest dir: NotPresent` — piège de méthode, pas défaut
produit) : **7/7, 2 `connect()`, tous `127.0.0.1`, 0 non-loopback — identique à l'exécutant.**
Les 4 audits sont lus : 5 déclencheurs tranchés un par un chacun (N/A justifiés : ex. setup-telemetry N/A
pour openbot, product-telemetry N/A pour openmuse/OpenDots, OTEL confirmé absent).

## 5. Triage des 181 commits openbot (H-P7-1, D1)

Fichier `openbot-DRIFT-TRIAGE-181.md` lu en entier + brut `logs/triage181-raw.txt` (2 792 lignes) :
méthode documentée (log `--name-only` gel..amont `68fe327`), contrats vérifiés un par un
(en-tête `x-openbot-bot-id` byte-identique, port `:4100` inchangé, routines cron inchangées,
**diff 0 ligne sur `product.ts` + `otel.ts`**, shims internes). Verdict « gel tenu, pas de re-gel »
**accepté** : aucune rupture d'API prouvée dans une surface portée ; les 3 « suppressions » apparentes
sont démontrées fausses alertes (reformulations additives). Dérives 0/1/8 des 3 autres bots tranchées
dans les fiches. Gel tenu confirmé — ceci ne couvre pas le re-pin (§1, distinct du gel).

## 6. Décisions sur les questions centrales (Q2–Q7)

- **Q2 H-M3 :** tranché §3 — ROUGE QUALIFIÉ ×3 confirmé, QUALIFIÉ OpenDuet confirmé.
- **Q3 H-P7-6 CONDITIONNELLE :** dépendance **correctement nommée et suivie, ne bloque pas le merge.**
  Preuves : `bots.rs` (`PAS6_NATIVE_COMMIT = "9050a1f"`, `refine_available() = false` + motif explicite,
  §D9 en doc), test `refine_is_conditional_on_pas6_merge ... ok` re-couru, fiches R-A2, registre.
  Le suivi exigé par le plan (« re-prouvée par un reçu quand le merge de `9050a1f` atterrit ») est une
  obligation future, pas un gate — la CONDITIONNELLE est le statut correct, pas un PASS déguisé.
- **Q4 PARTIEL / QUALIFIÉ : acceptables avec réserves (R-J6, R-J7).** H-P7-10/H-F8-2 PARTIEL : le mécanisme
  est livré et vérifié ; le « cycle complet = ce harnais » est circulaire comme preuve, mais c'est
  l'opérationnalisation admise par la chaîne (patron H-P3-7) — aucun cycle Runtime complet n'est exécutable
  sur cette VM. H-F8-9 QUALIFIÉ : dépense non mesurable, patron p5.
- **Q5 Renommage de casse `Amdkn/openbot` → `Amdkn/OpenBot` : aucune incidence.** API : repo = `Amdkn/OpenBot` ;
  `git ls-remote` sur l'URL minuscule de `.gitmodules` résout (redirection GitHub) vers `6e62238`, identique
  à l'URL en casse. Aucun changement `.gitmodules` requis pour ce motif. Le renommage explique seulement
  pourquoi le clone frais du juge s'appelle `OpenBot`.
- **Q6 Divergence de séquençage bind/adapter : CONFORME au plan.** Le plan §D8 ordonne littéralement
  bind AVANT adaptation (parent = gel) ; l'exécution l'a suivi ; la divergence vs p3/p4/p5 (adapter-d'abord)
  est consignée dans les 4 fiches, comme l'exigeait le plan. Le plan prévaut sur le précédent ; la divergence
  est documentée, pas cachée. (Elle n'a rien à voir avec le pin manquant : le bind-first rend d'ailleurs
  le re-pin sur `6e62238` trivial — l'arbre du fix contient déjà bind + adapter.)
- **Q7 `riginfinity.manifest.json` en retard : hors périmètre du plan, non bloquant, à suivre.**
  Vérifié : pin `c6adc8d` dans la branche PR alors que le gitlink est `11a82ba` — **déjà en retard à master**
  (pin `c6adc8d` vs gitlink `655b2a4`), le pas 7 ne l'a pas créé et le plan ne demande que le gitlink.
  Le retard passe à deux générations. Suivi (R-J5) : mettre à jour pin + compteurs + ports au pas 8
  ou par commit de suivi — ne pas bloquer ce merge pour un document que le plan ne couvre pas.

## 7. Faits faux ou inexacts — nommés précisément

- **F1 — H-P7-1 « PASS » du harnais d'origine est faux en tant que preuve du pin.** Le harnais
  (`run_holdouts_f8_p7.py`) vérifie gels + binds sur les forks + existence du triage, **jamais le gitlink
  V5**. C'est ce trou qui a laissé passer le re-pin manquant. Mon rejeu ajoute le check `H-P7-1-PIN`
  (gitlink V5 openbot) : **FAIL** (`2b5b14f`). Le harnais d'origine doit être corrigé pour les pas suivants.
- **F2 — « Pin (bind) : `<sha>` » dans les 4 fiches est une étiquette trompeuse.** Elle nomme le commit
  de bind comme « Pin » alors que le pin V5 réel est le gel (openbot) ou absent (3 autres). C'est elle qui
  a masqué l'omission. Corrigée par C2.
- **F3 — « plan §D8 littéral » dans le registre (segment pas 7) est inexact en substance.** §D8(c) (re-pin)
  n'a pas été exécuté. Corrigé par C4.
- **F4 — Chiffres « adaptés » du bun test openbot dans le rapport (10 891 / 345 / 285, 1 206 fichiers)
  sont ceux d'un run contaminé** (rename en cours de run + charge parallèle — §3.1), pas la mesure propre.
  La mesure propre du juge : 10 929 / 306 / 263, 1 205 fichiers. Le sens du verdict (ROUGE QUALIFIÉ)
  est inchangé — il est renforcé.
- **F5 — Tableau H-M du RAPPORT : H-M3-openbot y est écrit « EN COURS (gel) » alors que le détail du même
  rapport donne le verdict final ROUGE QUALIFIÉ.** Incohérence interne du rapport (tableau périmé, détail à jour).
- **F6 — Fiche OpenDuet : H-M3 « EN COURS » en deux endroits** (R-A1, Hold-outs) alors que le verdict final
  est QUALIFIÉ. Fiche périmée, corrigée par C3.
- **Exactitudes confirmées (à porter au crédit de l'exécution) :** recomptage RESULTS 37/6/2/0 exact ;
  PR #42 (ouverte, non mergée, `mergeable: true`, `clean`, tête `e8a3496`, base `446e927`, 2 commits) ;
  CI 8/8 conclusion `success` (voir R-J9 pour le statut) ; diff 21 fichiers ; `.gitmodules` 117 → 114 ;
  natif `11a82ba` parent `655b2a4`, 4 fichiers exacts ; compteurs 0/1/10/0 et 25 → 3 ; chiffres openmuse
  (499 pass, 3 fichiers) et OpenDots (340/351, 11 échecs) du rapport cohérents avec leurs logs ;
  éval OpenDuet 12/62, 0 wrong, reproduite à l'identique.

## 8. Rejeu indépendant du harnais — résultats

Harnais d'origine adapté par le juge (`~/workspace/juge-p7/run_holdouts_juge.py`, clones frais,
logs `juge-*`, check `H-P7-1-PIN` ajouté) → `~/workspace/juge-p7/RESULTS-JUGE-P7.json` :
**40 PASS, 2 QUALIFIÉ (H-P7-6, H-F8-9), 2 PARTIEL (H-P7-10, H-F8-2), 1 FAIL (H-P7-1-PIN) — 45 checks.**
Les H-M3 « suite fork » ne figurent pas dans ce script (elles sont re-courues en §3, pas lues dans les logs
de l'exécutant) ; les H-M3-ADAPTER ×4 sont PASS (suites re-courues §2).
Logs du juge : `~/workspace/juge-p7/logs/` (`juge-openbot-bun-test.log` 914 s,
`juge-openmuse-node-test.log` 922 s, `juge-opendots-vitest.log`, `juge-opendots-gel-3files.log`,
`juge-openmuse-gel-2files.log`, `juge-openmuse-rerun-browser-alone.log` 25/25,
`juge-openduet-eval-triage.log`, `juge-riginfinity-cargo-test.log`,
`juge-riginfinity-clippy.log`, `juge-riginfinity-fmt.log`, `juge-riginfinity-strace-*.log`).

## 9. Réserves numérotées

- **R-J1 (bloquante, levée par C1) — Pin openbot non re-piné.** Voir §1. Aucun merge sur `e8a3496`.
- **R-J2 — Harnais d'origine aveugle au pin (F1).** Le check `H-P7-1-PIN` doit entrer dans le harnais
  des pas suivants (gitlink V5 vs main-avec-bind, pour chaque pointeur survivant).
- **R-J3 — Étiquette « Pin (bind) » (F2) + fiche OpenDuet périmée (F6).** Levées par C2–C3.
- **R-J4 — États 2 déclarés avant jugement.** Les 4 manifestes portent déjà `levels.current = 2`
  (« monté à 2 à l'intégration ») alors que l'état 2 exige la validation 13e (définition registre D13).
  Patron pré-existant (agent-zero, prime-agent : « jugement 13e à venir ») — accepté, mais la montée
  d'état ne devient effective qu'au présent jugement + merge amendé.
- **R-J5 — Manifeste RigInfinity en retard de deux générations (Q7).** Suivi au pas 8 ou par commit
  dédié : pin `11a82ba`, compteurs de fichiers, ports déposés, `single_daemon` (toujours « PENDING P7 »
  dans le manifeste alors que la preuve existe désormais).
- **R-J6 — H-P7-10 / H-F8-2 PARTIEL : pas de cycle Runtime complet exécuté.** Accepté (non exécutable
  sur cette VM) ; la preuve est le harnais lui-même + les smokes. Un cycle complet sur machine réelle
  reste dû à terme (pas 8 / Alpha).
- **R-J7 — H-F8-9 QUALIFIÉ : plafonds non mesurés.** 1 %/5 %/20 % affirmés non mesurables depuis la
  factory (patron p5). Accepté ; la mesure à la comptabilité fournisseur (D12) reste due en principe.
- **R-J8 — H-F8-4 « 1 daemon compté » établi par construction, non par comptage live.** Aucun lancement
  du daemon + comptage de processus sur machine n'a été fait (ni par l'exécutant, ni par le juge) :
  la preuve est l'unicité du `fn main` natif + l'absence des ~28 processus dans l'arbre. Accepté
  comme preuve par construction, conforme au patron des pas précédents.
- **R-J9 — CI Cat 04 bloquée `in_progress` (conclusion `success`).** Re-vérifiée au jugement :
  7 check-runs `completed`/`success`, Cat 04 `in_progress` + `success` depuis l'ouverture de la PR.
  Anomalie d'état GitHub, pas un échec de code — mais elle doit être relancée ou close avant/après
  l'amendement (C5) ; elle ne doit pas devenir un précédent de merge sur check bloqué.
- **R-J10 — Suivi pas 6 (`/refine`).** Quand le merge de `9050a1f` atterrira dans RigInfinity, l'intégration
  des fonctions pas 6 dans la surface doit être **re-prouvée par un reçu de suivi** (plan §D9) —
  `refine_available()` doit alors passer à vrai avec preuve, pas par simple bascule de constante.

## 10. Arbitrages vision — non tranchés (remontent via Rick → A0)

Comme l'exigent le plan et la mission, le juge ne tranche pas : (a) re-gel vivant openbot (~45 commits/jour) ;
(b) rebasage du vendu OpenDuet ; (c) Intelligence hébergée ; (d) 4 apps vs plateforme + skins.
Le triage 181 (§5) et l'abandon du vendu avec preuve (§2, H-P7-8) sont les faits sur lesquels ces arbitrages
s'appuieront — ils sont vérifiés, pas décidés ici.

## 11. Conclusion

**VALIDÉE AVEC RÉSERVES — merge OUI après amendement (C1–C5), INTERDIT sur `e8a3496`.**
Le travail est réel et vérifié indépendamment : 4 binds, 4 adapters (13 fichiers, 0 import du fork),
surface native 601 lignes + preuve 7/7, 3 pointeurs retirés, section de principe corrigée, triage 181
solide, et — fait le plus fort du rejeu — la suite openbot adaptée se comporte **à l'identique du gel**,
fichier par fichier. Le seul défaut est le pin : une ligne à corriger, pas un travail à refaire.
Le coordinateur vérifie l'amendement à l'API (gitlink openbot = `6e62238`, CI verte complète) et merge
ensuite en true merge (2 parents, DVG-01), puis reçu R10.

*Juge 13e — jugement rendu sur preuves re-courues, 2026-11-12. Fichiers de travail :
`~/workspace/juge-p7/` (clones frais, logs `juge-*`, `RESULTS-JUGE-P7.json`, `run_holdouts_juge.py`).*
