# Rapport — Fusion F8 pas 8 : RigInfinity natif, l'incorporation

**Exécutant :** Ryan (continuation — phases A et B du prédécesseur reprises et re-vérifiées, fin de la Phase A + Phase C exécutées ici)
**Plan :** Clara, `FUSION-F8-PAS8-RIGINFINITY-NATIF-plan-borne.md` (signé, D1–D18)
**Discover :** Bill, `discover-fusion-f8-pas8-riginfinity-natif.md`
**Base :** V5 master `0b16b3a` (`0b16b3ac06f66d161da761c6c5a46ca66637f76d`) — 0 PR ouverte au départ
**Branche :** `ryan/d-n051-f8-pas8` — PR ouverte SANS MERGE (le 13e juge, le coordinateur merge)
**Date :** 2026-11-12 (exécution ~11:10–17:00 EST)

## 0. Ce qui était déjà fait (prédécesseur, re-vérifié ici — rien repris sur parole)

| Fait | Re-vérification par Ryan |
|---|---|
| Merge `9050a1f` déposé : `95e95f9b7a60b4e8e45564842bf380ee5d0c2aa4`, 2 parents (`11a82ba` + `9050a1f`), tête de `aspace-v5-native` | API GitHub : commit + branche confirmés |
| Suite cargo sur le merge 105/105, clippy + fmt verts | **Re-cours propre** sur le SHA exact : 105/105 (lib 70 + 5 + 7 + 8 + 4 + 6 + 1 PTY + 4), EXIT 0 ; clippy `--all-targets -D warnings` EXIT 0 ; `fmt --check` EXIT 0 |
| Arbre natif 46 fichiers (40 + 5 prime\* + 1 PTY) | `git ls-tree -r` : 46 fichiers, 5 prime\* |
| `/refine` re-prouvé par comportement | `bots.rs` lu : `refine_available()` planifie + applique une vraie refinement en mémoire ; `bots_proof.rs` + `pty_proof.rs` verts dans la suite |
| Strace 0 `connect()`, 0 non-loopback | **Re-cours** : `strace -f -e trace=connect` sur le daemon, 0 `connect()` |
| Daemon lancé + compté live : 1 processus, 0 `hc` | **Re-cours** : 1 processus `riginfinity-daemon` (comm `riginfinity-dae`), 0 `hc`, log « infinity-daemon ready », arrêt propre après timeout |
| LICENSE V5 construite (11 338 o, `Copyright 2026 A'Space`) | Retrouvée dans `/home/f8p8/v5/LICENSE` ; diff vs LICENSE RigInfinity = 1 seule ligne (ligne 189) |
| H-P7-1-PIN 7/7 | **Re-cours complet à l'API** (compares pin...main + adapter...pin + gitlinks V5 @`0b16b3a`) : 7/7 |
| Fiches C2 : 8 fiches corrigées, 0 occurrence de « Pin (bind) » | **Re-grep** sur les 37 fiches `*-ADAPTATION.md` : 0 occurrence |
| Liste fermée §D14 établie par lecture | Relue et appliquée (voir Phase C) |

## 1. Phase A — fin (manifeste lu par l'API, re-pin, LICENSE)

- **Manifeste** `riginfinity.manifest.json` lu par l'API GitHub (`contents`, base64) — l'incident du prédécesseur (chemin hors home) ne s'est pas reproduit : aucun chemin hors home utilisé.
- **Re-pin V5 du gitlink RigInfinity** sur le commit de merge `95e95f9` (§D3) — staged dans l'index (`git ls-files -s` : `160000 95e95f9…`).
- **LICENSE V5 déposée à la racine** (§D2) : Apache-2.0 verbatim de RigInfinity (11 358 o → 11 338 o), seule la ligne de l'Appendix change : `Copyright 2026 A'Space`.
- **H-P7-1-PIN 7/7** couru AVANT tout retrait (§D8) — voir tableau §0. Détail par pointeur : pin ancêtre du `main` HEAD (cordis ahead 2, automaton/pi/infinity/openrig/prime-agent ahead 1, openbot identical), pin contient l'adapter (identical sauf openrig ahead 2, openbot ahead 1), pin ≠ gel.
- **Fiches C2** : les 8 fiches du prédécesseur conservées (agent-zero, automaton, cordis, infinity, openbot, openrig, pi, prime-agent) ; les 3 fiches bots (openmuse, OpenDots, OpenDuet) déjà corrigées au pas 7. Toutes portent « Pin V5 » + « Bind » distincts.

## 2. Phase B — natif + daemon (re-cours Ryan)

- **Suite cargo @`95e95f9`** : 105/105, EXIT 0 (log `logs/cargo-95e95f9-ryan.log`).
- **Clippy / fmt** : verts (logs `logs/clippy-95e95f9-ryan.log`, `logs/fmt-95e95f9-ryan.log`).
- **Strace** : 0 `connect()`, 0 non-loopback (log `logs/strace-95e95f9-ryan.log`).
- **Daemon unique, compté live** : 1 processus `riginfinity-daemon`, 0 `hc` ; `fn main` unique ; un seul `[[bin]]` (`riginfinity-daemon`). Socket `/tmp/herdr-core.sock` absent (= muet) ; aucun socket créé au démarrage (serveurs RAP paresseux, cf. manifeste — observation, pas un écart).
- **Test PTY (H-P8-4)** : `pty_proof.rs` 1/1 vert — le daemon ouvre une session PTY via le transport natif (`openrig_terminal.rs`, NDJSON sur socket Unix) contre un stub local et y exécute une commande avec reçu (`echo pas8-pty-ok`).
- **Suites adapter re-courues au pas 8 (H-M3, 7/7 vertes)** :

| Module | Petit check | Résultat | Commande / log |
|---|---|---|---|
| cordis | smoke.spec.ts (vitest) | **3/3** | `vitest run …/smoke.spec.ts` — build workspace préalable (`yakumo esbuild`, lib/ absente sinon) — `logs-adapter-cordis3.log` |
| automaton | smoke_test.ts | **21/21** | `bun` (runner TS ; canonique `npx tsx` — node strip-types ne résout pas les imports `.js`→`.ts`) — `logs-adapter-automaton-bun.log` |
| pi | smoke_test.ts | **45/45** | `node --experimental-strip-types`, `V5_CONFIG` pointé sur le clone — `logs-adapter-pi.log` |
| infinity | cargo test adapter | **13/13** | lib 4 + smoke 3 + mcp_rap_proof 6 — `logs-adapter-infinity.log` |
| openrig | smoke_test.ts + tsc | **61/61**, tsc EXIT 0 | `npm ci` (444 paquets) puis `node --experimental-strip-types`, branche `main` — `logs-adapter-openrig2.log` |
| prime-agent | cargo test adapter | **18/18**, fmt EXIT 0 | lib 12 + smoke 5 + guard 1 — `logs-adapter-prime-agent.log` |
| openbot | adapter.checks.ts | **9/9** | `bun test` — `logs-adapter-openbot.log` |

Les suites complètes des forks sont citées de leur pas, pas re-courues (§D18) : cordis harnais 9/9 ; automaton 1 646/0/1 (réserve js-tiktoken) ; pi 4 431/9 qualifiés ; infinity 385/42 ROUGE QUALIFIÉ ; openrig test:repo 334 (333/0/1) ; prime-agent suite propre non re-courue (R-A2) ; openbot bun 10 891/345/285 ROUGE QUALIFIÉ. 0 échec imputable à un adapter dans tous les cas.

- **Extension pi (§D5, H-P8-5)** : imports par nom npm uniquement (`@earendil-works/pi-coding-agent`, `typebox`, `node:child_process`), 0 import du sous-module, 0 import relatif. Compilation vérifiée sans le gitlink : `tsc --noEmit --strict` EXIT 0 avec les seuls paquets npm installés (`@earendil-works/pi-coding-agent@1.5.0`, `typebox`, `typescript`) — log `logs-pi-ext-tsc.log`. Aucun re-pointage nécessaire.

## 3. Phase C — retraits + registres

- **`.gitmodules` 114 → 106** : 7 pointeurs des 11 (cordis, automaton, pi, infinity, openrig, prime-agent, openbot) + gitlink herdr-core `14a3772` retirés. **Les gitlinks sont aussi retirés de l'arbre** (`git rm --cached`, 106 → 98 gitlinks dans l'index) — la suppression de `.gitmodules` seule ne les retirait pas. Pointeur RigInfinity RESTE (§D1), re-piné `95e95f9`.
- **Daemon herdr-core (§D4)** : fibre `fiber:ade:herdr-core-pty` retirée du superviseur (`daemon_supervisor_cordis.py`, commentaire de retrait consigné ; nettoyage réversible `detach_pty_panes` + `save_terminal_scrollback` nommé) ; aucun processus `hc` sur la machine (vérifié au `ps`) ; socket `/tmp/herdr-core.sock` absent. Le module herdr-core n'est PAS touché (ni fork, ni adapter, ni fiche — D-N053 F1).
- **Références d'exécution coupées (§D14, liste fermée)** :
  - `clone-forkables.ps1` : 3 entrées (automaton, infinity, openrig — `$repos` + `$paths` + `$coreModules`, commentaire d'en-tête ajusté) ;
  - matrice sync (`sync-a0-sovereign-factory.ps1`) : 3 entrées (cordis, pi, prime-agent) — herdr / herdr-core / orca survivent (D-N053 F1/F2) ;
  - `mutate-and-push-forks.py` : 3 branches (`/automaton`, `/openrig`, `/infinity`) — la fonction reste un no-op documenté pour les modules restants, Python valide ;
  - `mount-fractal.ps1` : 1 chemin (automaton, couche 8L) ;
  - `02_Factory/README.md` : 1 phrase (`herdr-core` retiré de l'énumération des sous-daemons).
  - Vérifié survivant (documentaire / chaîne, §D14 b–c) : `MODULES-LOCK.json` (registre, aligné ci-dessous), `aspace_marketplace_engine.py` (chaînes `Amdkn/openbot`, le fork existe toujours — pas de chemin de sous-module), `openrig_demo_qc_578.py` (prose), `02_Factory/config.json` (prose), `factory.ps1` (aucune mention), `.pi/settings.json` (aucune mention), workflows `.github/workflows/` (aucun chemin de sous-module retiré).
- **`MODULES-LOCK.json` aligné** (précédent pas 5, agent-zero) : RigInfinity re-piné (`gitlink` + `pin` = `95e95f9…`) ; les 5 modules couverts par le lock (cordis, automaton, openrig, infinity, prime-agent) passent `gitlink: null`, pin conservé, état 2 inchangé jusqu'au jugement. Vérification : `check-modules-lock.py` — vérifications 2/3/4 VERTES, vérification 1 : les 5 retirés en SKIP (comme agent-zero), RigInfinity PASSera sur la tête de PR (le script lit `HEAD`, encore `0b16b3a` ici). `v5_head` du lock reste périmé (`7fe71a3`, pré-existant — pas corrigé ici, voir réserves). Vérification 6 : 1 trou pré-existant (fiche `riginfinity-ADAPTATION.md` absente — le natif n'a pas de fiche, pré-existant).
- **Manifeste (§D11)** : pin `95e95f9` ; 46 fichiers (26 src / 7 tests, 9 203 + 2 082 = 11 285 lignes) ; suite 105/105 ; ports D-N054 SC-2 + pas 7 + pas 8 ; `single_daemon` PROUVÉ (H-P8-6) ; `prime_agent_non_merge` RÉSOLU ; prime-agent rayé de `restant_a_integrer` (4 dettes restantes) ; `gitlink_verified` re-daté (branche `ryan/d-n051-f8-pas8`, base `0b16b3a`) ; `state: 2` inchangé (§D1, pas d'état 3 pour le natif).
- **Registre (§D13)** : ligne 89 corrigée (pas 6 CLOSE journal 789, pas 7 CLOSE journal 914, pas 8 en cours) ; ligne 90 compteurs → **0/0/11/0** (pi sous condition H-P8-pi nommée) ; segment pas 8 consigné ; mention cordis corrigée (« pin réel `a40cc74` (adapter, parent de `6aab659`) »).
- **Compteurs** : F8 **0/0/11/0** visés (état 3 effectif au jugement) ; D-N053 **25 → 3 INCHANGÉ** (herdr, herdr-core, orca).

## 4. Harnais — comptes

`RESULTS-F8-P8.json` : **97 checks — 87 PASS, 6 QUALIFIÉ, 4 PARTIEL, 0 FAIL.**

- H-M1..M7 × 11 modules : 77 checks (H-M3 QUALIFIÉ pour les 4 déjà retirés — petits checks cités de leur pas, pas re-courus).
- H-P8-1..H-P8-11 : 10 PASS + 1 PARTIEL (H-P8-7, cycle complet en suivi).
- H-F8-1/2/3/4/5/8/9 : 3 PASS (H-F8-1, H-F8-4, H-F8-5), 3 PARTIEL (H-F8-2, H-F8-3, H-F8-8 — validation 13e à rendre), 1 QUALIFIE (H-F8-9, plafonds).
- COMPTEUR-F8, COMPTEUR-D-N053 : PASS.
- Dérive amont 774 commits consignée comme candidats de revisite, jamais suivie (§D15).

## 5. Écarts et réserves (nommés, pas masqués)

1. **openrig smoke, 1er run 60/61** : l'unique échec (« branch is main ») venait du checkout détaché (HEAD détaché, `branch=HEAD`) — artefact de la méthode, pas du code. Re-run sur une branche locale `main` au même pin : **61/61**. La substance (HEAD = adapter commit, 3 commits devant le gel, tous dans l'adapter) passait déjà au 1er run.
2. **automaton, runner bun au lieu de `npx tsx`** : `node --experimental-strip-types` ne résout pas les imports `…/src/index.js` → `.ts`. Bun exécute les mêmes checks (21/21). Écart de runner uniquement, consigné dans le harnais.
3. **cordis, build préalable requis** : le smoke vitest exige les `lib/` construites (`yakumo esbuild`, EXIT 0) — sans build, `Failed to resolve entry for package "cordis"`. Le build est une étape d'environnement, pas une modification du fork (les `lib/` sont gitignorées).
4. **Daemon : aucun socket créé au démarrage** — serveurs RAP paresseux (manifeste). Le daemon est compté par processus (1), pas par socket. Pas un écart, une observation.
5. **`MODULES-LOCK.json`, `v5_head` périmé (`7fe71a3`)** — pré-existant (le lock n'avait déjà pas suivi `0b16b3a`). Non corrigé ici : la valeur ne peut être la tête de PR qu'après création du commit. Suivi pour le coordinateur.
6. **`check-modules-lock.py`, vérification 6** : 1 trou pré-existant (fiche `riginfinity-ADAPTATION.md` absente, `adapter_commit` null — le natif n'a pas d'adapter). Inchangé par ce pas.
7. **Chaînes `Amdkn/openbot` dans `aspace_marketplace_engine.py`** : survivent — elles nomment le fork (qui existe toujours) et un ID de conteneur, pas le chemin du sous-module V5. Classées chaîne (§D14 c).
8. **Aucune mesure de pool** (H-F8-9 QUALIFIE, patron p5) — comme à tous les pas précédents.

## 6. Suivis dus après le merge (§D9–D10, H-P8-pi)

- **Reçu de suivi n° 1 (Ryan)** : cycle complet Intake → Éveil → Rig → Résolution → Validation + comptage live du daemon unique sur machine réelle (Alpha / PC). Un seul reçu couvre cycle + comptage.
- **Reçu de suivi n° 2 (pi, H-P8-pi)** : quand la Phase D du pas 2 devient verte, re-preuve de la durabilité native de pi et levée de la condition sur son état 3.
- **Mesure du pool à la comptabilité fournisseur (D12)** : due en principe, jamais mesurée dans aucun reçu.
- **Registre Nardole** : non touché par Ryan (append-only, coordinateur seul).

## 7. Fichiers livrés

Dossier de preuves local : `~/workspace/v4-factory/evidence/D-N051/p8/` — `RESULTS-F8-P8.json` (97 checks), `RAPPORT-PAS8.md` (ce fichier), `logs/` (25 logs : cargo/clippy/fmt/strace/daemon du merge, 7 suites adapter, tsc extension pi, install cordis, merge commit+tree).
Déposés dans la PR (sous `evidence/D-N051/p8/`) : `RESULTS-F8-P8.json` + `RAPPORT-PAS8.md` (suivant le précédent du pas 7).

## 8. PR — contenu (28 chemins, base `0b16b3a`)

- **Ajoutés (3)** : `LICENSE`, `evidence/D-N051/p8/RESULTS-F8-P8.json`, `evidence/D-N051/p8/RAPPORT-PAS8.md`.
- **Modifiés (17)** : 8 fiches `*-ADAPTATION.md`, `riginfinity.manifest.json`, `FUSIONS-REGISTRY.md`, `MODULES-LOCK.json`, `.gitmodules`, `clone-forkables.ps1`, `daemon_supervisor_cordis.py`, `mutate-and-push-forks.py`, `sync-a0-sovereign-factory.ps1`, `mount-fractal.ps1`, `02_Factory/README.md`, gitlink RigInfinity (`11a82ba` → `95e95f9`).
- **Supprimés (8 gitlinks)** : cordis, pi, automaton, infinity, openrig, herdr-core, prime-agent, openbot.
- Arbre local de référence (index stagé) : `6237df09…` avant ajout des preuves (re-mesuré après ajout, voir reçu de dépôt).

**Aucun merge par Ryan.** La PR attend le jugement du 13e, puis le merge par le coordinateur (true merge, 2 parents, DVG-01).
