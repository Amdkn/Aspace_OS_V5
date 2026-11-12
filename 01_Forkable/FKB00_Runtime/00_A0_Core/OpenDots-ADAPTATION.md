# Fiche d'adaptation — OpenDots (D-N051 F8, pas 7)

**Adresse :** `fiber:a0:opendots` (cœur Buzz)
**Manifeste :** `OpenDots.manifest.json` (même domicile)
**Audit télémétrie :** `OpenDots-TELEMETRY-AUDIT.md` (même domicile)
**Statut :** état 0 Basique → 2 Adapté + Fusionné en un seul pas (§D12)
— adaptation + portage natif livrés ensemble ; le jugement du 13e
reste requis pour la montée d'état.

## Commit gelé

- **Fork :** `Amdkn/OpenDots` (parent `CopilotKit/OpenDots`, MIT,
  branche `main`).
- **Gel : `d4214af`** (`d4214aff10f066911f3253cb3cb870764cd51a9f`) — « chore(deps): update dependency typescript-eslint to v8.72.1 (#143) », 2026-11-03T18:41:41Z.
- **Vérifié à l'API par Ryan :** fork main HEAD = gel avant adaptation ;
  compare gel...amont `main` : behind 1, ahead 0 (amont 46eaf96 — README-only, déjà reprise).
- **Vérifié au fichier :** clone local `~/workspace/f8-p7/OpenDots`,
  HEAD = gel avant adaptation, arbre propre, 207 fichiers.
- **Pin (bind) : `abcb35d`** — 1 fichier :
  `aspace-plugin.json` (blob `83c6b9b`, byte-identique
  entre la branche `aspace-v5-native` `7e21c95` et
  `main`). Parent du bind : le gel `d4214af` (bind AVANT
  l'adaptation, plan §D8 littéral — divergence du précédent p3/p4/p5,
  adapter-d'abord, nommée ici pour le juge : le précédent posait
  l'adapter sur le gel puis re-appliquait le bind au-dessus de
  l'adapter ; le plan §D8 ordonne bind puis adapter, et c'est l'ordre
  suivi ici). Plugin `@aspace-v5/opendots`, famille
  `CORE_A0_KERNEL`, propriétaire `A0-AMADEUS / S1-RICK`, 2L.
  Licence MIT (fichier ; l'API dit MIT).
- **Arbre @gel :** 207 fichiers, 20 371 Ko ; version amont
  0.1.0, statut amont Alpha.

## Adapter

- **Paquet :** `aspace-opendots-adapter/` (TypeScript, stdlib
  seule, version 0.1.0), **3 commits** sur le fork `main` : bind
  `abcb35d` (parent = gel), adapter
  `4051f5c` (parent = bind), correctif
  `c423bcf` (parent = adapter). Tête `main` :
  `c423bcff9691325325a25080a81da61caf481b6f`. Vérifié à l'API après push (compare
  gel...tête = ahead 3, behind 0, 14 fichiers A'Space seuls :
  `aspace-plugin.json` + 13 fichiers adapter, H-M2).
- **Modules :**
  - `lineage.ts` — pins du gel + `verifyGelLineage` (H-M1/H-M2).
  - `skin.ts` — enregistrement des skins sur la plateforme
    (`platformConfigured`, §D10).
  - `computer.ts` — computer-service `:4100` + en-tête
    `x-openbot-bot-id` verbatim, `holder: bot | human`, reprise
    en main (§D11).
  - `telemetry.ts` — les 5 déclencheurs §D4, 0 émetteur (H-M4).
  - `routines.ts` — routine → entrée du job loop, cron refusé,
    minimum 15 min (§D5).
  - `gateway.ts` — gateway EGM `:31415` seul, chaîne modelPool,
    `getApiKey()` → `"None"` (sentinelle de refus, §D6).
  - `triage.ts` — tri porté / surface / abandonné, vérifié
    mécaniquement par la suite.
- **`contract.json`** — le contrat public de l'adapter (gel, bind,
  famille, propriétaire, gateway, chaîne, triage, dépendance nommée
  pas 6).
- **`AGENTS.md`** — le DOX enfant de l'adapter (frontière durable :
  stdlib seule, jamais d'import du fork, jamais de clé, jamais de cron).
- **Suite adapter : 8/8 verte (`node --test tests/adapter.checks.ts`)** — voir
  `logs/logs-opendots-adapter-*.log`. Correctif du pas : le
  fichier de checks s'appelle `adapter.checks.ts` (pas `.test.ts`)
  pour que les suites des forks ne le ramassent pas — découvert
  quand vitest a échoué 1 suite parasite sur OpenDots.
- **Réserve R-A1 :** suite propre au fork : vitest 340 passés / 11 échoués (351) — 7 timeouts tests/telemetry.test.ts (captureRuntime, 5 000 ms) + 2 tests/transport.test.ts + 1 tests/setup-telemetry.test.ts (événements offline, 196 requêtes capturées au lieu de 0) + 1 tests/computer.test.ts (audit-storage) ; les 10 premiers sont reproduits à l'identique au gel d4214af (logs-opendots-gel-telemetry-transport.log, logs-opendots-gel-setup-computer.log) ; le 11e passe isolément sur les deux têtes (logs-opendots-rerun-2files.log) — flake de charge.

## Le tri (6 portés / 3 surfaces / 4 abandonnés, total 13)

Écrit dans l'adapter (`src/triage.ts`), vérifié mécaniquement par la
suite (comptes = table, écart 0). Le détail par item est dans
l'adapter ; les abandons structurants : le sink SDK, la setup telemetry, les requêtes HogQL, le SQLite fichier

## Télémétrie

Voir `OpenDots-TELEMETRY-AUDIT.md` (versionné, même domicile).

- **PASS — télémétrie zéro** Les 5 déclencheurs §D4 sont tranchés
  un par un dans l'audit ; le natif = 0 appel sortant par défaut.
  Aucun SDK PostHog/Sentry dans les `package.json` (grep vérifié) ;
  le sink est prouvé par les docs et le code, pas par le code search
  (§0.4 — le « 0 signal » du code search est faux, deuxième occurrence).
- La capture réseau est celle du portage natif : les preuves
  `bots_proof.rs` tournent sous `strace` (connect() loopback seuls),
  voir `logs/logs-riginfinity-pas7-strace.log`.

## Portage natif (RigInfinity, `aspace-v5-native`)

- **Base :** tête `655b2a4` (pas 5 + D-N054 :
  daemon pas 3, rig pas 4, moteur agent-zero pas 5, source-control
  natif D-N054). Vérifiée présente avant le portage
  (`prime_agent` grep = 0, `cron-parser` grep = 0).
- **Module `bots.rs`** (+ `lib.rs`, preuve `tests/bots_proof.rs`) :
  plateforme + 3 skins, computer-service `:4100` + en-tête verbatim,
  routines dans le job loop (preuve par reçu), coworker persistant
  dans le Shared Brain sans Intelligence, `/refine` conditionnel
  (§D9 — `refine_available()` faux, raison nommant `9050a1f`).
- **Commit natif : `11a82bab`**
  (`11a82bab611f849bfdebb19692776ca6da94fac6`, parent = `655b2a4`,
  branche `aspace-v5-native`, 4 (bots.rs + bots_proof.rs nouveaux, lib.rs +11 lignes, changeset_proof.rs 2 lignes lint pré-existant) fichiers).
  Poussé sans force, vérifié à l'API.
- **Tests natifs : cargo test complet vert : lib 62/62, agent_zero_proof 5/5, bots_proof 7/7, changeset_proof 8/8, daemon_proof 4/4, source_control_proof 4/4 (rc=0)** — voir
  `logs/logs-riginfinity-pas7-cargo-test.log` ;
  `clippy -D warnings` vert (rc=0, -D warnings), `fmt` vert (rc=0).
- **Dépendance nommée (§D9) :** les fonctions pas 6 (RLM, `/refine`,
  Continual Harness) sont une dépendance nommée, pas attendue. Le
  portage est fait contre la base pas 5 + D-N054 ; l'intégration des
  fonctions pas 6 est re-prouvée par un reçu de suivi quand le merge
  de `9050a1f` atterrit (pas un gate, un suivi).
- **Non porté :** les 16 shims `agent-*`, Spire, Postgres, les
  desktops/mobiles/extensions comme modules, `cron-parser`, le vendu
  OpenDuet 0.2.0, les clés CPK / fournisseurs, toute seconde mémoire
  de référence.

## La greffe : il n'y en avait pas (§0.3)

Aucun fichier natif de RigInfinity ne référençait les bots ; les
références V5 sont des chaînes dans 1 fichier de registre FKB07
(`aspace_marketplace_engine.py` — noms de repos, IDs de conteneurs,
URL de reprise, aucun import, aucun appel d'exécution) et de la
doctrine. Le pas 7 ne coupe rien côté natif — il **porte** : il
spécifie la surface depuis les quatre, la dépose dans RigInfinity,
et retire 3 pointeurs. La coupure (retrait des références + des
gitlinks) est faite par Ryan à l'intégration (§D16), pas par ce pas.

## Dérive 1 — déjà reprise

Le seul commit de dérive (gel `d4214af` → amont `46eaf96`) est une
README-only (« Lead with OpenDots as a skin in OpenBot », + image).
Le repositionnement « skin » est repris au §D3 : la surface native
est une plateforme + des skins, pas 4 apps. Aucun triage requis.


## Divergence (dette portée par le cœur Buzz)

- **R-A1** — suite propre au fork : vitest 340 passés / 11 échoués (351) — 7 timeouts tests/telemetry.test.ts (captureRuntime, 5 000 ms) + 2 tests/transport.test.ts + 1 tests/setup-telemetry.test.ts (événements offline, 196 requêtes capturées au lieu de 0) + 1 tests/computer.test.ts (audit-storage) ; les 10 premiers sont reproduits à l'identique au gel d4214af (logs-opendots-gel-telemetry-transport.log, logs-opendots-gel-setup-computer.log) ; le 11e passe isolément sur les deux têtes (logs-opendots-rerun-2files.log) — flake de charge.
- **R-A2** — H-P7-6 CONDITIONNELLE au merge pas 6 pour le chemin
  `/refine` seul ; plateforme + skins + computer-service
  inconditionnels (§D9).
- **R-A3** — le gel openbot vieillit (~45 commits/jour) ; le triage
  181 ne prouve aucune rupture, la revisite reste par signal (F8 D3).
- **R-A4** — les 4 bots sont Alpha / early development (sauf openbot,
  sans badge) ; les suites des forks sont qualifiées ROUGE QUALIFIÉ
  quand l'échec est pré-existant au gel (§D15, tranché par le 13e).

## Hold-outs

- **H-M1 PASS** — HEAD du fork = gel avant adaptation ; bind
  parent = gel ; adapter parent = bind (vérifié à l'API).
- **H-M2 PASS** — compare gel...tête = ahead 3, behind 0,
  14 fichiers A'Space seuls (vérifié à l'API).
- **H-M3 ROUGE QUALIFIÉ (10/11 pré-existants au gel + 1 flake de charge)** — vitest 340/351 (11 échoués) ; au gel d4214af les mêmes 10 échouent (7 telemetry + 2 transport + 1 setup-telemetry, noms identiques) ; le 11e (computer audit-storage) passe isolément sur les deux têtes — flake de charge, pas l'adapter.
- **H-M4 PASS** — audit versionné ; 5 déclencheurs tranchés ;
  0 émetteur dans le natif (R-A1 pour la suite propre, voir § Télémétrie).
- **H-M5 PASS** — ce manifeste (`fiber:a0:opendots`).
- **H-M6 PASS** — adapter seul code A'Space du fork (+ bind
  `aspace-plugin.json`, patron Cordis Fiber) ; triage rempli ;
  propriétaire `A0-AMADEUS / S1-RICK` ; précision §0.3.
- **H-M7 PASS** — cette fiche.
- **H-P7-1 PASS** — gels + binds vérifiés à l'API ; triage
  181 versé (openbot) ; dérives 0/1/8 tranchées (autres bots).
- **H-P7-2 PASS** — la surface unique tourne dans RigInfinity sans
  les 4 forks (plateforme + 3 skins, preuve `bots_proof.rs`).
- **H-P7-4 PASS** — traits prouvés par comportement (always-on,
  humain-dans-la-boucle, agent personnel — voir preuve native).
- **H-P7-5 PASS** — un seul daemon ; routines dans le job loop,
  preuve par reçu ; aucun parseur cron.
- **H-P7-6 CONDITIONNELLE (/refine)** — coworker survit au redémarrage sans
  Intelligence ; aucune clé CPK dans le natif ; `/refine`
  conditionnel au merge pas 6 (§D9).
- **H-P7-7 PASS** — audit versionné par bot, 5 déclencheurs
  tranchés ; 0 appel sortant par défaut (capture réseau native).
- **H-P7-8 N/A** — pas de vendu dans ce module (H-P7-8 ne vise qu'OpenDuet).
- **H-P7-9 PASS** — manifeste + fiche dans `evidence/D-N051/p7/`
  (dépôt V5 `00_A0_Core/` = parent) + section de principe OpenBot
  réécrite (§D7, annexe §7).
- **H-P7-10 PARTIEL** — smoke sans les originaux au niveau module
  (adapter + natif) ; le cycle complet du Runtime sans les
  originaux = harnais du parent.
- **H-F8-2 PARTIEL** — mécanisme natif livré ; cycle complet =
  harnais du parent.
- **H-F8-4 PASS (construction)** — aucun daemon ajouté ; la surface
  vit dans le daemon unique ; ~28 emplacements retirés ou re-pointés
  (Spire, Postgres, compose retirés ; supervisor porté comme
  fonction ; desktops/mobiles/extension = surfaces).
- **H-F8-5 PASS** — aucun cron nulle part (adapter + natif) ; le job
  loop EST le scheduler ; présence par heartbeat.
- **H-F8-9 À JUGER** — adapter 13 fichiers ; natif 1 module +
  preuve ; plafonds jugés par le parent.

## Contraintes nommées du §2 (design pas 7)

- D1 gel tenu, pas de re-gel (triage 181 : aucune rupture prouvée).
  D2 vendu OpenDuet abandonné avec preuve. D3 modèle skin repris.
  D4 télémétrie : 5 déclencheurs tranchés. D5 routines dans le job
  loop, preuve par reçu, cron-parser abandonné. D6 Intelligence
  remplacée (gateway `:31415` + Shared Brain), aucune clé CPK.
  D7 section de principe OpenBot réécrite (annexe §7). D8 binds
  avant adaptation (ordre plan littéral). D9 base pas 5 + D-N054,
  dépendance pas 6 nommée. D10 pont d'enregistrement des skins.
  D11 protocole ordinateur unique `:4100` + `x-openbot-bot-id`.
  D12 plafonds (1 % module / 5 % pas / 20 % mission), état 0 → 2.
  D13 découpage A → B → C. D14 surfaces et infrastructures
  (16 shims, Spire, Postgres abandonnés). D15 H-M3 ROUGE QUALIFIÉ
  + OpenDuet sans suite propre. D16 coordination D-N053 pas E +
  SKILL.md re-pointée.
