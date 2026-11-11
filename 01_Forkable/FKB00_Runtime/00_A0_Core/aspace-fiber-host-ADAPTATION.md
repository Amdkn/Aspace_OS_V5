# Fiche d'adaptation — AspaceFiberHost (P1, piste A)

**Adresse :** `fiber:a0:aspace-fiber-host` (capacité `cordis_fiber_host`)
**Manifeste :** `aspace-fiber-host.manifest.json` (même domicile `00_A0_Core/`)
**Code :** `00_A0_Core/aspace-fiber-host/` (`@aspace/fiber-host` 0.1.0, natif V5)
**Statut :** état 1 Adapté (contrat AspaceFiberManifest v1 + manifeste + tests locaux,
jugement 13e à rendre, PR `a0/p1-fiber-host`)
**Design :** `~/workspace/v4-factory/plans/DESIGN-P1-FIBER-HOST.md` (signé)
**Discover :** `~/workspace/v4-factory/plans/DISCOVER-P1-FIBER-HOST.md`

## Ce que P1 livre (vérifié en local, Node v24.22.1)

Cordis devient le vrai hôte Fiber, sur le vrai `Context` (adaptateur 0.1.0, gel `b38ef58`) :

- **Registre dynamique** des Fibers (contrat AspaceFiberManifest v1, schéma
  `schemas/aspace-fiber-manifest-v1.json`, validateur sans dépendance).
- **Activation par dépendances et co-effets** : ordre topologique, cycle et manque
  refusés avant tout démarrage ; co-effets `apply`/`revert` ; activation partielle
  repliée (rollback + dispose des déjà-démarrées).
- **Processus gérés + health checks** : par transport (in-process, unix-socket,
  http-loopback).
- **Baux réels** : expiration par minuteur et par `sweepExpired()`, renouvellement
  plafonné (10 × ttl), expiré non renouvelable ; expiration = dispose + nettoyages.
- **Démarrage paresseux et arrêt propre** : `register` ne démarre rien ; dispose
  en ordre inverse ; `disposeHost()` dispose tout, HMR, puis la racine.
- **Reçus, idempotence, reprise après crash** : journal JSONL (`appendFileSync`),
  `request_id` + hash du payload, reçu stocké rejoué sans ré-exécuter ;
  orphelins marqués `abandoned` et compensés à l'activation ; baux expirés
  pendant l'arrêt disposés à la reprise. Test SIGKILL réel.
- **Nettoyage et rollback exécutés** : fonctions réelles, ordre inverse, erreurs
  consignées sans blocage de la suite.
- **Réconciliation HMR explicite et vérifiée** : `watch` OFF, verdict `applied`
  réel sur module modifié, `noop` sur racines vides (test repris du patron
  amont `packages/hmr/tests/reconcile.spec.ts`).
- **Transports formalisés** : unix-socket JSON-lines, ops RigInfinity verbatim
  de `client.rs` (santé = `list_sessions`, pas d'op `health` en amont) ;
  http-loopback EGM (`127.0.0.1:31415`, santé TCP, garde loopback) ; RAP hors P1
  (`callback_url` porté, `rap-deferred` consigné).
- **Node.js épinglé** : `engines >= 24.16` (HMR : ESM retarget observé seulement
  sur 24.16+ / 26.1+), `--expose-internals` requis pour les tests HMR.

## Limites franches

- `daemon_supervisor_cordis.py` reste une maquette (fichier intact) : le host est
  l'implémentation réelle ; la suppression/réécriture du Python relève d'une
  piste ultérieure.
- Le schéma public `https://aspaceos.tech/schemas/aspace-fiber-manifest-v1.json`
  est un identifiant de contrat ; la publication n'est pas revendiquée (le fichier
  local fait foi). Le `$schema` `cordis-fiber-v5.json` du bind est abandonné
  (inexistant) — le bind n'est pas modifié en P1.
- Yarn bloqué par le proxy de la VM : install/test via npm `--legacy-peer-deps`
  (prouvé : install + build + smoke adaptateur 3/3 + suite host).
- Le test kill réel (H-P1-3) fait tourner un enfant qui n'importe que le Journal :
  il prouve la reprise sur journal après SIGKILL, pas qu'un host tué laisse
  exactement ces lignes — ce point est prouvé par le test déterministe (append
  synchrone avant exécution).
- `register(manifest, impl?)` : l'implémentation est exigée pour `in-process`
  (précision d'exécution du design D-4, qui ne montrait que `register(manifest)`).
- L'activation exige une santé OK (sonde) : une Fiber dont le distant ne répond
  pas ne démarre pas (état `failed`, erreur nommée).
- Le fork `Amdkn/cordis` et le gitlink V5 (`6aab659`) sont intouchés en P1
  (re-pins = piste E).

## Tests

`npm install --legacy-peer-deps && npm test` dans `aspace-fiber-host/` —
hold-outs H-P1-1 à H-P1-10 (voir README). Résultats locaux consignés au reçu
G-20261111-013. Le vert qui compte en CI = check-runs re-vérifiés à l'API sur
la tête PR (jamais un PASS local seul).

## Verrou

Nouvelle entrée `fiber:a0:aspace-fiber-host` dans `01_Forkable/MODULES-LOCK.json`
(état 1, `capabilities_owned: ["cordis_fiber_host"]`, `adapter_commit` = SHA de
tête de la PR) ; `cordis_fiber_host` retiré de `capabilities_unassigned` ;
notes `capabilities_claimed_elsewhere` de cordis / agent-zero / a0-plugins mises
à jour (propriétaire nommé). Harnais `check-modules-lock.py` : 1-4 VERTES,
sans nouveau trou aux vérif 5-6 (hors trou riginfinity pré-existant, piste F).
