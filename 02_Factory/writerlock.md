# Cartographie `writerLock` (D-N049, D6)

Versionné dans V5. Un seul écrivain par zone. Le Shared Brain et `log.md` sont en **ajout seul** (jamais de modification d'une ligne existante).

| Zone | Chemin | Écrivain unique |
|---|---|---|
| Worktree V5 | `~/workspace/v5-repo` (branches `ryan/...`) | **Ryan** |
| Plans | `~/workspace/v4-factory/plans/` | **Clara** |
| Registre | `~/workspace/v4-factory/dispatch/REGISTRE-NARDOLE.md` | **Nardole** |
| Ledger (reçus R10) | fichiers du ledger Graham | **Graham** |
| Dossiers | `~/workspace/architecture-compagnons/` | **Bill** |
| Amendements L00 | `~/workspace/v4-factory/dispatch/L00-*.md` | **Yaz** |
| Shared Brain | `00_Memoire/shared_brain/memory.jsonl` | **Tous, en ajout seul** (FileLock + règle de déduplication D4) |
| `log.md` | `00_Memoire/bundle/log.md` | **Tous, en ajout seul** |

## Dépôts R10

Un dépôt R10 = **un nouveau fichier** (ajout), jamais une modification d'une entrée existante. Graham seul écrivain des fichiers existants du ledger.

## Conflits

Un Worker qui détecte un conflit d'écriture (deux écrivains sur la même zone) **s'arrête sur cette zone, pulse une anomalie à Rick et à Yaz**, et ne force jamais l'écriture.
