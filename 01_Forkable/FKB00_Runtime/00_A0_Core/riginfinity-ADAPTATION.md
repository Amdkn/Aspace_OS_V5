# Fiche d'adaptation — riginfinity (D-N051 F8, pas 8)

**Adresse :** `fiber:a0:riginfinity` (le natif — l'arbre dans lequel les 11 modules sont incorporés)
**Manifeste :** `riginfinity.manifest.json` (même domicile)
**Fiche native :** `RIGINFINITY-V5.md` (même domicile)
**Statut :** état 2 — module NATIF, pas un pointeur adapté. Pas de montée en état 3 : l'état 3 s'applique aux 11 pointeurs fusionnés (cordis, automaton, pi, infinity, agent-zero, openrig, prime-agent, openbot, openmuse, OpenDots, OpenDuet), pas au natif qui les reçoit. Jugement 13e F8 pas 8 : VALIDÉE AVEC RÉSERVES, merge PR #43 `6a58b6c` (2026-11-12).

## Module natif

- **Dépôt :** `Amdkn/RigInfinity` (Apache-2.0), branche `aspace-v5-native`. Pas de fork, pas de gel amont, pas d'adapter : **le pin EST la référence** (MODULES-LOCK, `fiber:a0:riginfinity` ; manifeste : « Natif — pas d'adapter. Le pin est la référence »).
- **Pin V5 : `95e95f9`** (`95e95f9b7a60b4e8e45564842bf380ee5d0c2aa4`) — commit de merge, 2 parents `11a82ba` + `9050a1f` (D-N051 F8 pas 8, fusion du portage prime-agent ; DVG-01). Gitlink V5 = pin.
- **Chemin V5 :** `01_Forkable/FKB00_Runtime/01_Holo_TriptyqueCore/RigInfinity` (gitlink, arbre non déplié dans V5).
- **Entrée :** binaire `riginfinity-daemon`, crate `crates/infinity-daemon` (Rust, `run_daemon`).
- **Suite :** **cargo test 105/105** (lib 70 + 5 + 7 + 8 + 4 + 6 + 1 PTY + 4), clippy 0, fmt 0 — re-cours juge 13e, pas 8.
- **Adapter :** aucun. `adapter_commit` = pin `95e95f9` dans MODULES-LOCK (le natif n'a pas d'adapter ; le commit d'incorporation tient lieu de référence — S4 F8 pas 8, R-J14).

## Portages natifs (incorporés)

- agent-zero `e866578`, openrig `a372582` + `e190645`, infinity `bd7c946` + `aad4993`, prime-agent `9050a1f` (mergé en `95e95f9`, F8 pas 8).
- Les 7 pointeurs retirés de l'arbre au pas 8 (cordis, pi, automaton, infinity, openrig, prime-agent, openbot) + gitlink herdr-core : le Runtime tourne sans les originaux (cycle H1 + refinement prouvés en suite ; cycle complet 5 étapes en suivi machine réelle, R-J6).

## Manifeste

- `riginfinity.manifest.json` : `state: 2` (§D1 du plan pas 8 — le natif reste en état 2).
- Dette restante **F-RIG-1** : `aspace-plugin.json` du daemon déclare encore 578-holons + OWASP sans preuve.

## Références

- Jugement 13e F8 pas 8 : `evidence/D-N051/p8/JUGEMENT-PAS8.md` (R-J14, S4).
- Rapport : `evidence/D-N051/p8/RAPPORT-PAS8.md` ; harnais : `evidence/D-N051/p8/RESULTS-F8-P8.json`.
- Registre : `01_Forkable/FUSIONS-REGISTRY.md` ligne 90 (compteurs 0/0/0/11).
- Verrou : `01_Forkable/MODULES-LOCK.json` (`v5_head` = merge PR #43 `6a58b6c`).
