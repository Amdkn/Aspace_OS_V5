# Rapport d'exécution — D-N051 F8 pas 7 : les 4 bots (Ryan, exécutant)

**Plan :** `FUSION-F8-PAS7-BOTS-COEQUIPIERS-plan-borne.md` (signé Clara).
**Harnais :** `run_holdouts_f8_p7.py` → `RESULTS-F8-P7.json` (45 checks).
**Branche V5 :** `ryan/d-n051-f8-pas7`, base master `446e927`, tête `4f73046`.
**Commit natif RigInfinity :** `11a82bab611f849bfdebb19692776ca6da94fac6`
(parent `655b2a4`, branche `aspace-v5-native`, vérifié à l'API).
**PR :** [#42](https://github.com/Amdkn/Aspace_OS_V5/pull/42) (base master),
tête `e8a3496`, état OPEN, MERGEABLE, non mergée — le 13e juge, le
coordinateur merge ensuite. Checks CI en cours à l'ouverture (1 pass,
les autres pending — le jugement porte sur leur atterrissage).

## Verdicts H-M1..M7 par module

| | openbot | openmuse | OpenDots | OpenDuet |
|---|---|---|---|---|
| H-M1 gel | PASS (`2b5b14f`) | PASS (`a4944f4`) | PASS (`d4214af`) | PASS (`f52288f`) |
| H-M2 adapter seul | PASS (ahead 3, 14 f.) | PASS (ahead 3, 14 f.) | PASS (ahead 3, 14 f.) | PASS (ahead 3, 14 f.) |
| H-M3 suite fork | ROUGE QUALIFIÉ (10 929 pass / 306 fail / 263 errors, 1 205 fichiers, identique au gel) | ROUGE QUALIFIÉ | ROUGE QUALIFIÉ | QUALIFIÉ (evals) |
| H-M4 télémétrie zéro | PASS | PASS | PASS | PASS |
| H-M5 manifeste | PASS (`fiber:a0:openbot`, 2) | PASS (`fiber:a0:openmuse`, 2) | PASS (`fiber:a0:opendots`, 2) | PASS (`fiber:a0:openduet`, 2) |
| H-M6 frontière | PASS | PASS | PASS | PASS |
| H-M7 fiche | PASS | PASS | PASS | PASS |

Détail H-M3 :
- **openbot** — `bun test` : 10 891 pass, 292 skip, 345 fail, 285 errors,
  11 528 tests, 1 206 fichiers, 2 191 s ; 38 fichiers en échec
  (dont `app/src/components/channels/composer/triggers.test.ts` :
  111 échecs en cascade). Gel `2b5b14f` (re-couru complet, 792 s) :
  10 929 pass, 292 skip, 306 fail, 263 errors, 11 527 tests,
  1 205 fichiers ; 20 fichiers en échec communs (mêmes causes :
  provider modèle absent, clés Composio/Arcade absentes, garde réseau
  DNS, timeouts). Les 18 fichiers en échec seulement sur la tête
  adaptée, re-courus seuls : **362/363 passent** ; le 1 restant
  (production-loader-boundary, timeout 5 038 ms) passe seul des deux
  côtés (1/1, rc=0) — flake de charge. 1 fichier en échec seulement
  au gel (desktop cli-bundle). triggers.test.ts échoue des deux côtés
  (111 vs 73 — cascade sous charge, même fichier, défauts de clé
  modèle). **ROUGE QUALIFIÉ — 0 échec imputable à l'adapter**
  (l'adapter n'est importé par aucun code du fork).
- **openmuse** — `node --test` (re-run propre, TMPDIR sur /home,
  0 ENOSPC) : 499 sous-tests passent ; 3 fichiers en échec (browser,
  conversation-calendar, conversation-jev — « Agent execution failed:
  Connection interrupted », appels modèle sans provider dans la
  sandbox). Au gel `a4944f4` : browser + conversation-jev échouent
  à l'identique ; conversation-calendar passe seul sur la tête adaptée
  (12/12, rc=0) — flake de charge. **ROUGE QUALIFIÉ.** Le premier run
  (51 ✖) était pollué par ENOSPC (/tmp 100 % plein) et est invalidé.
- **OpenDots** — `vitest` (re-run propre, TMPDIR sur /home) : 340/351 ;
  11 échecs — 7 telemetry (timeouts `captureRuntime`, 5 000 ms) +
  2 transport + 1 setup-telemetry + 1 computer (audit-storage).
  Au gel `d4214af` : les mêmes 10 échouent (noms identiques) ;
  le 11e passe isolément sur les deux têtes (flake de charge).
  **ROUGE QUALIFIÉ.**
- **OpenDuet** — 0 test propre : eval triage rules-only **exécutée**
  (12/62 décidées, 0 wrong, 100 % sur les décidées, 0 désaccord) ;
  6 YAML valides, `emails.jsonl` 62 lignes labellisées ;
  reply-chips/voice = fixtures (stack + Chrome requis, non
  exécutables ici) ; suite openbot 0.3.3 = H-M3-openbot.
  **QUALIFIÉ.**

Suites adapter (toutes vertes) : openbot 9/9, openmuse 8/8,
OpenDots 8/8, OpenDuet 9/9.

## Hold-outs H-P7

- **H-P7-1 PASS** — gels + binds vérifiés à l'API ; triage 181 versé
  (`openbot-DRIFT-TRIAGE-181.md`) : aucune rupture d'API dans une
  surface portée → **gel tenu, pas de re-gel** ; dérives 0/1/8
  tranchées.
- **H-P7-2 PASS** — surface unique dans RigInfinity sans les 4 forks
  (bots_proof 7/7).
- **H-P7-3 PASS** — SKILL.md FKB07 re-pointée (conteneur OpenBot /
  console OpenMuse → computer-service natif + takeover natif).
- **H-P7-4 PASS** — traits prouvés par comportement (plateforme +
  3 skins, coworker survit au redémarrage).
- **H-P7-5 PASS** — un seul daemon ; routines dans le job loop,
  preuve par reçu ; intervalle < 15 min refusé.
- **H-P7-6 QUALIFIÉ (CONDITIONNELLE)** — coworker survit au
  redémarrage sans Intelligence ; aucune clé CPK dans le natif ;
  gateway `:31415` + modelPool, failover 500→200 sans clé ;
  **`/refine` conditionnel au merge pas 6 (`9050a1f`)** — dépendance
  nommée (§D9), pas un gate.
- **H-P7-7 PASS** — 4 audits versionnés, 5 déclencheurs tranchés ;
  strace bots_proof 7/7 : 2 connect(), tous 127.0.0.1, 0 non-loopback.
- **H-P7-8 PASS** — vendu OpenDuet 0.2.0 abandonné avec preuve ;
  commit natif = 4 fichiers seulement, aucun vendu.
- **H-P7-9 PASS** — manifestes + fiches en `00_A0_Core/` + section
  de principe OpenBot réécrite (annexe §7).
- **H-P7-10 PARTIEL** — smoke module (adapters 9/9, 8/8, 8/8, 9/9 +
  natif 7/7) ; cycle complet = harnais.

## Hold-outs H-F8

- **H-F8-1 PASS** — `.gitmodules` : OpenMuse/OpenDots/OpenDuet
  retirés, pointeur OpenBot conservé (pas 8).
- **H-F8-2 PARTIEL** — mécanisme natif livré ; cycle complet = harnais.
- **H-F8-4 PASS** — sprawl ~28 → 1 prouvé : openbot 10 + openmuse 3 +
  OpenDots 5 + OpenDuet 10 processus (Discover §3.2) → 1 daemon
  (`infinity-daemon`, un seul `fn main`) ; Spire, Postgres, compose
  retirés ; supervisor = fonction ; desktops/mobiles/extension =
  surfaces.
- **H-F8-5 PASS** — aucun cron nulle part (adapters + natif) ;
  le job loop EST le scheduler ; présence par heartbeat.
- **H-F8-9 QUALIFIÉ** — dépense non mesurable depuis la factory
  (patron F8 D12) ; adapters 13 fichiers ×4 ; natif 1 module +
  1 preuve + 2 lignes lint pré-existant.

## Compteurs

- **F8 : 0/1/10/0** (0 état 0, 1 état 1 [pi], 10 état 2, 0 état 3).
- **D-N053 : 25 → 3** (restent herdr, herdr-core, orca).

## Écarts rencontrés (nommés pour le juge)

1. **Divergence de séquençage bind/adapter vs p3/p4/p5.** Le plan §D8
   littéral a été suivi (bind AVANT adaptation, parent = gel).
   Les précédents faisaient adapter-d'abord puis bind re-appliqué
   avec parent = adapter. Le plan prévaut ; la divergence est
   consignée dans les 4 fiches.
2. **Renommage `adapter.test.ts` → `adapter.checks.ts`.** vitest et
   `bun test` ramassent tout `*.test.ts` du repo — le fichier de
   checks polluait les suites des forks (OpenDots : 1 suite parasite).
   Correctif bun : le runner est `bun test ./tests/adapter.checks.ts`
   (le `./` est obligatoire, sinon bun traite le chemin comme filtre).
3. **Renommage de casse du fork** : `Amdkn/openbot` → `Amdkn/OpenBot`
   (push : « This repository moved. Please use the new location »).
   Pushes réussis via redirection. Non tranché par l'exécutant.
4. **`/tmp` 512 Mo saturé à 100 %.** Le tmpfs a tué 17 tests natifs
   (ENOSPC), faussé 2 runs OpenDots (29 suites en échec à l'import)
   et le 1er run openmuse (51 ✖), et tué l'install gel OpenDots
   (rc=137). Cause : `/tmp/opendots-gel` (313 Mo) + `/tmp/f8p7`
   (182 Mo, copies dont l'origine n'est pas établie — laissées
   intactes). Correctif : TMPDIR sur `/home` pour tous les re-runs ;
   tous les résultats cités ici sont des re-runs propres.
5. **Preuve native `telemetry_zero` corrigée 3×.** La preuve
   scannait `bots.rs` entier pour les clés interdites — mais la
   blocklist, la doc et les tests unitaires NOMMENT les clés pour
   les refuser. La preuve distingue désormais mention et usage
   (code exécutable nettoyé des commentaires/tests + blocklist).
   Même classe d'erreur pour `cron-parser` (doc) et `ABANDONNÉ`
   (mot absent du code — remplacé par vendu + 0.2.0).
6. **Clippy pré-existant du pas 5.** `changeset_proof.rs:31`
   (`&PathBuf` → `&Path`, 2 lignes, sans changement de comportement)
   bloquait `clippy -D warnings`. Corrigé au passage, nommé ici ;
   `changeset_proof` 8/8 toujours vert, clippy + fmt verts.
7. **`riginfinity.manifest.json` en retard sur le gitlink.**
   Son pin (`c6adc8d`) était déjà derrière le gitlink (`655b2a4`)
   à master ; le pas 7 porte le gitlink à `11a82bab` sans mettre
   à jour le manifeste (pin + compteurs de fichiers + ports
   déposés à recalculer — hors périmètre du plan, qui ne demande
   que le gitlink). Écart nommé pour le coordinateur.
8. **Registre : 909 vs 911 lignes.** Le plan dit 909 lignes à la
   vérification Clara ; la tâche dit 911, journal 911 = ce dispatch.
   Écart de comptage non tranché par l'exécutant.

## Les 4 arbitrages vision (non tranchés — remontent via Rick → A0)

1. Re-gel vivant (openbot ~45 commits/jour) — le triage 181 ne prouve
   aucune rupture ; la revisite reste par signal (F8 D3).
2. Rebasage du vendu OpenDuet — abandonné avec preuve (§D2) ;
   rebaser, c'eût été adapter openbot deux fois à deux versions.
3. Intelligence hébergée — remplacée (gateway `:31415` + Shared
   Brain), aucune clé CPK ; le pas ne tranche pas l'hébergement
   futur.
4. Les 4 apps (desktops/mobiles/extensions) — portées comme surfaces,
   pas comme modules.

## Dépenses

Plafonds D12 : 1 % par module, 5 % par pas, 20 % par mission —
**non mesurables depuis la factory** (patron p5, H-F8-9 QUALIFIÉ).
Aucun crédit provider dépensé (0 appel sortant, stubs locaux seuls) ;
aucun secret lu.

## Fichiers d'évidence

`~/workspace/v4-factory/evidence/D-N051/p7/` : 4 fiches, 4 manifestes,
4 audits, `openbot-DRIFT-TRIAGE-181.md`, `run_holdouts_f8_p7.py`,
`RESULTS-F8-P7.json`, `logs/` (suites, cargo, clippy, fmt, strace,
comparaisons au gel, triage 181), `openbot-failing-files.txt`.
