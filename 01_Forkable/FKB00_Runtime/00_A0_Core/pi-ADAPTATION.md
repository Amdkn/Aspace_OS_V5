# Fiche d'adaptation — pi (D-N051 F8, pas 2)

**Adresse :** `fiber:a0:pi` (la durabilité — D2 : émetteur exécution ;
validateur 13e)
**Manifeste :** `pi.manifest.json` (même domicile)
**Audit télémétrie :** `pi-TELEMETRY-AUDIT.md` (même domicile)
**Statut :** état 0 Basique → 1 Adapté en cours (fiche + adapter + manifeste ;
**H-P2-7 RÉSERVE (pwsh absent), H-P2-9 RÉSERVE (1 erreur de type de
l'extension), H-P2-3/6/11 MACHINE (PC) — jugement 13e requis** — voir §
Hold-outs)

## Commit gelé

- **Fork :** `Amdkn/pi` (parent `earendil-works/pi`, MIT, branche
  `main`).
- **Gel : `6e2222a`** (`6e2222a8dda06e3d69fad46d630f152f5873567a`) —
  « docs(p3): layout mocks beyond sidebar, chat, sidebar (19 layouts) »,
  2026-11-07 23:51:39 UTC (18:51:39 -05:00). Version **1.5.0**
  (`packages/durable/package.json` : `@earendil-works/pi-durable`
  1.5.0, Node ≥ 22.19.0).
- **Vérifié au fichier :** clone local `~/workspace/pi-repo`, HEAD =
  gel avant adaptation, arbre propre. `npm ci --ignore-scripts`
  terminé (338 paquets, 58 s) ; le monorepo utilise **npm workspaces**
  (pas de pnpm-lock à la racine).
- **Dérive (D1) :** amont HEAD `750d621` au dispatch — **119 commits
  derrière le gel**. Signal de revisite (inventaire hebdomadaire),
  **PAS de re-gel** : chasser le HEAD vivant viole la sanctuarisation
  (F8 D3). Le candidat de re-gel 1.5.2 (`91d9719`) est déjà périmé.
- **Tout commit amont ultérieur exige un amendement de design**,
  jamais un fast-forward silencieux (D1).
- **Compatibilité 1.5.0 → 1.5.2 : non établie (D2).** Les signatures
  sont épinglées sur le gel comme contrat d'interface (voir § Adapter)
  — aucune affirmation de compatibilité 1.5.2.

## Adapter

- **Paquet :** `aspace-pi-adapter/` (`@aspace/pi-adapter` 0.1.0),
  commit **`13be830`** (`13be83055b4ac6b8281fc9dd9cff523226f23e94`,
  HEAD) sur le fork. **Seul code A'Space du fork** (D6) — l'amont est
  byte-identique au gel (H-P2-1 vérifié : compare gel..HEAD = ahead 1,
  behind 0, exactement les 6 fichiers adapter, 1 commit).
- **Périmètre strict (§D6) :** (a) la surface API du paquet
  `packages/durable` (`submit` / `resume` / `requestId`, contrat
  checkpoint / stockage) ; (b) l'interface de l'extension (outil
  `subagents` : nom, actions, paramètres — préservés verbatim) ; (c)
  les noms de paquets préservés (`@earendil-works/pi-*`, §D8). **Hors
  périmètre :** le reste du monorepo (TUI, evals, MCP, chord,
  `codemode`, `p2` / `p3`, Nix).
- **Surface épinglée (vérifiée contre le gel, D2) :**
  - `createSession()` — `packages/durable/src/session/session.ts`,
    export `src/index.ts:139`.
  - `Harness.resume()` — `packages/durable/src/harness/harness.ts:304`.
  - `ConversationHandle.submit(draft, context)` avec `requestId`
    (README:129-134, exactly-once) ; `submissionByRequest`
    (`types.ts:1013`, `session.ts:2040`, clé
    `req:<conversationId>:<requestId>` dans `session/keys.ts:61`).
  - `defineTask()` — `tasks.ts:4`.
  - `MemoryStorage` (`storage/memory.ts:239`) ;
    `openNodeSqliteStorage` (`storage/sqlite/node.ts:15`).
  - `NOOP_TELEMETRY_CONTEXT` (défauts `harness.ts:220`,
    `scheduler.ts:410`, `submissions.ts:50`) ;
    `DURABLE_TELEMETRY_SCHEMA` (`harness/telemetry.ts`, content-free) ;
    `onWake` (`harness/types.ts:750`).
- **Surface de l'adapter (`src/index.ts`, 17 085 o) :**
  `readModelPoolChain(configPath)` / `resolveModelCall(link, provider?)`
  (D4 — une seule orthographe, noms nus, préfixe fournisseur au moment
  de l'appel) ; `ExactlyOnceRegistry` (H-P2-2) ; `CrashCounter` +
  `CRASH_COUNT_DDL` (D9 — borne 3, table `crash_counts` dans
  `factory.sqlite`) ; `ASPACE_TELEMETRY_CONTRACT` (D5 — contexte
  `NOOP_TELEMETRY_CONTEXT`, zéro exporteur) ; `isOutboundAllowed(url,
  extraHosts?)` / `installOutboundGuard({ allowHosts })` →
  `restore()` (enveloppe le `fetch` global, refuse avant tout accès
  réseau) ; `TELEMETRY_BLOCKLIST` (16 motifs, refusés même
  allow-listés) ; `getFrozenRepoInfo()` / `verifyFrozenCommit()` /
  `verifyFrozenLineage()` (lignée : gel ancêtre de HEAD +
  `gel..HEAD` limité au dossier adapter) ; `PINNED_SURFACE` ;
  `SUBAGENTS_TOOL` (nom `subagents`, 6 actions, 13 paramètres).
- **Smoke tests : 45/45 verts** (`node --experimental-strip-types
  aspace-pi-adapter/smoke_test.ts`), re-courus **45/45 sous `unshare
  -n`** (zéro interface réseau — zéro egress physiquement possible).
  `tsc --noEmit` propre sur l'adapter (avec `"types": ["node"]` et
  `"allowImportingTsExtensions": true` — la convention amont des
  benches utilise des imports `.ts` ; le smoke suit cette convention).
  Log : `logs-pi-smoke.log`.
- **Correction D4 de l'intake (`factory.ps1`) : côté V5, par Ryan à
  l'intégration, PAS par l'adapter.** Vérifié au fichier :
  `factory.ps1` ligne 200 = 5 liens préfixés
  (`freellmapi/auto`, `freellmapi/claude-sonnet-4-5`, …) ; lignes
  227/247 (intake Python run/chain) = 3 liens en forme mélangée
  (`freellmapi/auto,claude-sonnet-4-5,qwen3.8-max`). Après correction,
  chaque consommateur lit la chaîne depuis `config.json` et préfixe
  le fournisseur au moment de l'appel — jamais une seconde liste
  stockée.

## Tests au gel et sur le fork adapté

- **Commande CI du paquet :** `npm run test` (`vitest --run` +
  `PI_DURABLE_DOCUMENT_RETENTION_MS=0 vitest --run` + `test:store` +
  `test:workers`). Préalable exigé par l'amont : `npm run build`
  (les tests de Durable importent `pi-ai` depuis `dist/`).
- **Première passe (`vitest --run`, 236 s) : 1 924 passés / 3 échoués
  / 4 ignorés (1 931) ; 95/100 fichiers verts, 3 en échec.** Les 3
  échecs sont des **timeouts uniquement, aucune assertion en échec** :
  - `test/codemode.test.ts` > « times a script out across a restart,
    without admitting new calls » — **timeout 5 000 ms**.
  - `test/harness-ownership.test.ts` > « tracks ownership chains
    deeper than the call stack » — **timeout 60 000 ms**.
  - `test/harness-scheduler-retention.test.ts` > « forgets a
    20,000-deep chain of ended tasks without recursion » — **timeout
    60 000 ms**.
  - Log : `logs-pi-suite.log`.
- **Qualification : environnemental, pré-existant au gel, non
  imputable à l'adapter.** Preuves : (1) les 3 fichiers sont amont,
  non touchés ; (2) **zéro référence à `aspace-pi-adapter` dans
  `packages/durable/test/` et `packages/durable/src/`** — le bilan de
  la suite au HEAD adapté est donc identique au bilan au gel ;
  (3) la VM partagée (1,5 CPU, 6 Go) a mis 536 s de temps de test
  pour la passe — les tests profonds (chaîne de 20 000 tâches,
  ownership plus profonde que la pile) dépassent leur timeout sur
  cette machine lente. **Re-passe des 3 fichiers avec
  `--testTimeout=300000` terminée : les 3 échouent encore, toujours
  par timeout uniquement, aucune assertion en échec**
  (`logs-pi-suite-retries.log`, 345 s : codemode timeout à 300 000 ms
  — le drapeau s'applique ; ownership et rétention timeout à
  60 000 ms — leurs timeouts sont codés en dur dans les fichiers de
  test et le drapeau CLI ne les remplace pas ; les modifier
  exigerait de toucher des fichiers amont, interdit). Même avec
  5 minutes, ces 3 tests ne terminent pas sur cette VM — même
  patron que le test automaton à ~7 h (H-M3) : ils exigent une
  machine plus rapide (le PC) ou un budget bien plus long.
  **Le 13e juge.**
- **La chaîne `&&` s'est arrêtée au premier `vitest --run` (rc=1) :**
  la passe rétention, `test:store` et `test:workers` ont donc été
  relancés séparément après la re-passe — **les 4 jambes de la
  commande CI ont maintenant tourné** :
  - `vitest --run` : **1 924 passés / 3 échoués (timeouts) / 4
    ignorés** (1 931), 95/100 fichiers.
  - Rétention (`PI_DURABLE_DOCUMENT_RETENTION_MS=0`) : **1 923
    passés / 4 échoués / 4 ignorés**, 94/100 fichiers — les 3 mêmes
    timeouts + **1 échec de seuil de performance** :
    `test/tools-images.test.ts` > « prepares in a worker thread,
    leaving the event loop free » — `expected 101.38… to be less
    than 100` (le test exige que la préparation en worker thread
    prenne < 100 ms ; sur cette VM lente elle a pris 101,39 ms,
    soit 1,4 % au-dessus du seuil codé en dur). Échec de
    performance environnemental, pas de logique : le même test
    passe dans la passe principale.
  - `test:store` : **547 passés / 2 échoués (les 2 mêmes timeouts,
    60 000 ms) / 5 ignorés** (554), 23/25 fichiers.
  - `test:workers` : **37/37 PASS**, 2/2 fichiers.
  - Total des 4 jambes : **4 431 passés** ; 9 échecs dont 8 sont
    les 3 mêmes timeouts récurrents et 1 le seuil de performance
    de 101 ms. **Aucun échec d'assertion sur la logique, aucun
    échec imputable à l'adapter.**
- **H-P2-2 (exactly-once) : prouvé en local par le smoke** (le
  producteur n'est invoqué qu'une fois pour le même `requestId` ;
  la 2e soumission retourne la soumission existante) — la preuve
  machine (reprise réelle sur `factory.sqlite`) est H-P2-3, sur le
  PC.
- **H-P2-4 (writerLock) :** cartographie `02_Factory/writerlock.md`
  (D-N049 D6) lue, **inchangée par ce pas** — aucun conflit, aucun
  écrivain forcé.
- **H-P2-5 (modelPool) :** l'orthographe unique est vérifiée ici
  (chaîne lue depuis `config.json`, 5 noms nus exactement, préfixe
  au moment de l'appel — smoke 45/45). Le **failover live** sur
  `freellmapi/auto` (`127.0.0.1:31415`) est machine : il exige le PC
  (le premier maillon est injoignable depuis cette VM) — réserve
  nommée, pas un vert inventé.
- **H-P2-7 (spine) : RÉSERVE — `pwsh` absent de cette VM Linux.**
  `factory.ps1 status` + `gate` ne sont pas exécutables ici. Ce qui
  est vérifié au fichier : les 6 garanties de la spine survivent
  (les fichiers du §0 du design ne changent pas de comportement —
  la seule modification intentionnelle est l'unification `modelPool`
  §D4, une correction, pas une rupture) ; les 12 skills et les 8
  agents sont ceux du gel ; les commandes `subagents` répondent par
  l'outil épinglé. **Le 13e juge.**
- **H-P2-9 (extension) : RÉSERVE — 1 erreur de type.** L'interface
  est épinglée verbatim (outil `subagents`, 6 actions
  `agents`/`status`/`run`/`chain`/`send`/`resume`, 13 paramètres —
  smoke 45/45, lus depuis `.pi/extensions/aspace-factory.ts`,
  173 lignes). Mais le fichier **ne typecheck pas contre le gel** :
  `error TS2305: Module '"@earendil-works/pi-ai"' has no exported
  member 'Type'` (ligne 2). La convention amont est `import { Type }
  from "typebox"` (ex. `packages/coding-agent/src/extensions/codemode/tool.ts:34`)
  — `packages/ai/src/index.ts` n'exporte pas `Type` à 1.5.0. Le
  correctif est une ligne d'import, à porter à l'intégration V5
  (le fichier vit dans le repo V5, pas dans le fork) ; le
  comportement d'exécution (enregistrement de l'outil) n'est pas
  affecté. **Le 13e juge.**
- **H-P2-3 / H-P2-6 / H-P2-11 : MACHINE (PC).** Non exécutés ici
  (borne OUT : toute exécution d'un hold-out machine hors du PC).
  Procédure exacte dans `p2/machine-holdouts-procedure.md` :
  checkpoint/reprise, hibernation/réveil (`--wake caller`), boucle
  de crash (borne 3, rapport + arrêt).

## Télémétrie

**Zéro par contrat dans le périmètre.** Voir
`pi-TELEMETRY-AUDIT.md` : zéro SDK télémétrie dans les
`package.json` ; **0 `fetch(` dans `packages/durable/src/` et
`packages/telemetry/src/`** ; `NOOP_TELEMETRY_CONTEXT` par défaut
(`harness.ts:220`, `scheduler.ts:410`, `submissions.ts:50`) ;
`DURABLE_TELEMETRY_SCHEMA` content-free ; zéro exporteur branché ;
71 fichiers référencent `TelemetryContext` (311 références), 31
fichiers mentionnent `NOOP_TELEMETRY_CONTEXT` — le contrat est
NOOP par défaut partout où il est consommé.
Réserves : **R-1** télémétrie d'installation défaut ON dans
`coding-agent` (`enableInstallTelemetry: true`,
`settings-defaults.ts:32` — ping `pi.dev/api/report-install`,
version + User-Agent, 5 s, fire-and-forget) — **neutralisée par
le garde-fou de l'adapter** (`pi.dev` n'est ni loopback ni
allow-listé) et par `PI_OFFLINE=1` / `PI_TELEMETRY=0` en
déploiement ; **R-2** `Type` non exporté par `pi-ai` 1.5.0
(voir H-P2-9) ; **R-3** les appels `fetch` de `packages/ai/src/`
(22) sont des appels d'inférence vers les fournisseurs
(OpenRouter, OpenAI, Bedrock, …) — fonctionnels, clé-gatés,
pas de la télémétrie.

## Divergence (dette portée par le cœur Buzz, lane Clara / 12e)

- **Dérive amont : 119 commits derrière le gel** (amont HEAD
  `750d621`). Signal de revisite (inventaire hebdomadaire) ; le
  re-gel est un candidat d'amendement après revue des changements
  d'API — jamais un fast-forward silencieux.
- **Compatibilité 1.5.2 non établie** (D2) : les signatures sont
  épinglées sur le gel ; toute affirmation 1.5.2 exigerait la revue
  des commits amont.
- **Télémétrie d'installation défaut ON** (`coding-agent`,
  `enableInstallTelemetry: true`) : hors périmètre de l'adapter
  (le reste du monorepo), neutralisée par le garde-fou + la règle
  de déploiement (`PI_OFFLINE=1` ou `PI_TELEMETRY=0`).
- **Extension : import `Type` à corriger** (`typebox` au lieu de
  `@earendil-works/pi-ai`) — une ligne, à l'intégration V5.
- **Boucle de crash : borne 3 (D9).** Après 3 crashs consécutifs
  avant un checkpoint, la tâche est rapportée (pulsée à Rick et à
  Yaz, avec son `requestId` et le compteur) et arrêtée (reprise
  désactivée jusqu'à une décision d'un Doctor). La borne est un
  arbitrage vision si le Capitaine veut une autre valeur.
- **Unité « L » du bind (2L, D3) :** retirée comme mesure,
  conservée comme étiquette verbatim. Le bind pi (`75cc3d92`,
  1 fichier `aspace-plugin.json`, sur `aspace-v5-native`) est
  re-appliqué sur `main` par Ryan à ce pas (F8 D2) ; le pin V5 est
  mis à jour sur l'adapter.
- **Ré-audit télémétrie :** à chaque changement de commit gelé ou
  d'adapter, et au minimum à chaque transition d'état (D3).

## Contraintes nommées (§2 du design)

- Monorepo npm workspaces (338 paquets) ; build complet requis
  avant la suite durable (les tests importent `pi-ai` depuis
  `dist/`) ; `tsx` absent du monorepo — le smoke utilise
  `node --experimental-strip-types` (Node 24.22.1) avec des
  imports `.ts` (convention amont des benches).
- Aucune modification d'un paquet amont ; aucun re-gel ; aucune
  affirmation de compatibilité 1.5.2 ; aucun exporteur de
  télémétrie ; aucun renommage de paquet ; aucune seconde liste
  `modelPool` stockée ; aucune reprise d'une tâche en boucle de
  crash après 3 crashs ; aucune exécution d'un hold-out machine
  hors du PC ; aucun merge, aucune PR, aucun dépôt R10
  (intégration par Ryan).
- Le bind pi (`75cc3d92`) est re-appliqué sur `main` par Ryan à
  ce pas, pas par l'adaptation.

## Références

- Design pas 2 (Clara, signé) :
  `~/workspace/v4-factory/plans/FUSION-F8-PAS2-PI-DURABILITE-plan-borne.md`
  (D1–D10, H-P2-1..11 + H-F8 du pas).
- Discover Bill :
  `~/workspace/architecture-compagnons/discover-fusion-f8-pas2-pi-durabilite.md`.
- Design F8 (Clara) :
  `~/workspace/v4-factory/plans/FUSION-F8-RUNTIME-TRIPTYQUE-NATIF-plan-borne.md`.
- Évidences : `~/workspace/v4-factory/evidence/D-N051/p2/` —
  `pi.manifest.json`, `pi-TELEMETRY-AUDIT.md`,
  `machine-holdouts-procedure.md`, `logs-pi-smoke.log` (smoke
  45/45, dont 45/45 sous `unshare -n`),
  `logs-pi-suite.log` (suite durable 1 924/3/4, 95/100 fichiers),
  `logs-pi-suite-retries.log` (re-passe des 3 fichiers en timeout :
  3/3 timeouts, aucune assertion en échec),
  `logs-pi-suite-retention.log` (passe rétention 1 923/4/4),
  `logs-pi-suite-store.log` (547/2/5),
  `logs-pi-suite-workers.log` (37/37).
- Fork : https://github.com/Amdkn/pi (gel `6e2222a`, adapter
  `13be830` — 1 commit, 6 fichiers, 892 insertions).
