# `@aspace/fiber-host` — AspaceFiberHost (P1)

Cordis devient le vrai hôte Fiber. Le host tourne sur le vrai `Context` Cordis
(construit par `@aspace/cordis-adapter` 0.1.0, gel `b38ef58`) et fournit :

- registre dynamique des Fibers (contrat **AspaceFiberManifest v1**) ;
- activation par dépendances (`requires`, ordre topologique, cycle refusé) et
  co-effets (handlers `apply`/`revert` fournis par l'appelant) ;
- registre des processus gérés + health checks (par transport) ;
- baux réels : expiration (minuteur + `sweepExpired()`), renouvellement plafonné
  (10 × ttl initial), bail expiré non renouvelable ;
- démarrage paresseux (`register` ne démarre rien) et arrêt propre
  (ordre inverse de l'activation) ;
- reçus, idempotence (`request_id` + hash du payload, reçu stocké rejoué sans
  ré-exécution) et reprise après crash (journal JSONL, `appendFileSync`) ;
- nettoyage et rollback **exécutés** (fonctions, jamais des noms), en ordre inverse ;
- réconciliation HMR explicite (`watch` OFF, jamais de rechargement automatique).

## Isolation de l'API amont (dure)

L'API Cordis amont est annoncée instable. Le host n'importe `cordis` et
`@cordisjs/plugin-hmr` que via `@aspace/cordis-adapter` (`createAspaceApp`,
`reconcile`, `hasHmr`) — sauf l'import de types `Context`/`Fiber` (effacé à la
compilation). Surface épinglée : `PINNED_HOST_SURFACE` (`src/host.ts`).
Toute dérive est un événement de design, pas une rupture silencieuse.

## Transports

| Transport | Fil | Santé | Invoke |
|---|---|---|---|
| `in-process` | plugin Cordis installé par `ctx.plugin` (ancre de cycle de vie) | `health()` de l'impl ou `alive` | appel direct |
| `unix-socket` | JSON-lines (une requête par ligne, une réponse JSON par ligne), protocole client RigInfinity (`client.rs`) : `create_session`, `resume_session`, `list_sessions`, `send_input`, `cleanup_session` | op `list_sessions` (pas d'op `health` en amont) | `operation` → op RigInfinity ; op hors table refusée avant envoi |
| `http-loopback` | `POST` de l'enveloppe JSON (EGM : `http://127.0.0.1:31415/v1/chat/completions`) | connexion TCP (prouve l'écoute, n'envoie rien) | `POST` ; HTTP ≠ 2xx = erreur consignée |

Garde loopback : tout hôte ≠ `127.0.0.1` / `::1` est rejeté. Socket par défaut :
`$INFINITY_STATE_DIR/daemon.sock`, sinon `~/.infinity/daemon.sock`.
RAP est hors P1 : `callback_url` est porté et ignoré avec un avertissement
consigné (`rap-deferred`) ; livraison asynchrone en P2.

## Enveloppe

Requête : `request_id` (obligatoire, clé d'idempotence), `trace_id`, `parent_id`,
`session_id`, `holon_id`, `fiber_id`, `operation`, `deadline` (ISO 8601 avec
offset), `lease_token` (obligatoire pour tout `invoke`), `replay_policy`
(`safe` = rejeu retourne le reçu stocké ; `replay` = rejeu d'un id terminé
refusé, nouveau `request_id` exigé), `payload`.
Réponse : `status`, `result`, `artefacts`, `errors`, `receipt_id`
(`rcpt-<request_id>`).

## Prérequis

- **Node.js ≥ 24.16** (`engines` dans `package.json` ; vérifié 24.22.1).
  La résolution ESM via lien retargeté du HMR n'observe la nouvelle cible que
  sur 24.16+ / 26.1+.
- Le sous-module Cordis **doit être initialisé** avant install/test :
  `git submodule update --init 01_Forkable/FKB00_Runtime/00_A0_Core/cordis`
  (les dépendances `file:../cordis/...` pointent dessus ; les tests résolvent
  les sources du gel via les alias de `vitest.config.ts`).
- HMR exige `--expose-internals` (voir `test` ci-dessous).

## Tests

```sh
cd 01_Forkable/FKB00_Runtime/00_A0_Core/aspace-fiber-host
npm install --legacy-peer-deps   # yarn bloqué par le proxy de la VM (fiche cordis)
npm test                          # node --expose-internals vitest run
```

Hold-outs : `H-P1-1` baux, `H-P1-2` idempotence, `H-P1-3` reprise crash
(dont SIGKILL réel), `H-P1-4` HMR, `H-P1-5` socket Rust, `H-P1-6` loopback,
`H-P1-7` rollback, `H-P1-8` dépendances, `H-P1-9` verrou, `H-P1-10` local.
Les tests HMR vivent dans le seul `tests/hmr.spec.ts` (une instance HMR par thread).

## Supersession

`02_Factory/01_Kernel_Gates/daemon_supervisor_cordis.py` est une maquette
(états et baux en mémoire, nettoyages nommés jamais exécutés, aucun processus
lancé — Discover P1). Le host est l'implémentation réelle. Le fichier Python
reste intact en P1 (référence historique) ; sa suppression ou sa réécriture
comme fine couche sur le host relève d'une piste ultérieure.
