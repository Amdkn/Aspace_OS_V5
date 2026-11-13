# Audit télémétrie — fondation-13-1 (fonction Recevoir, D-N055 F1-2)

**Module :** `fiber:a0:fondation-13-1` — validateur R10 v1 + consignateur
(`01_Forkable/FKB00_Runtime/00_A0_Core/fondation-13-1/`).
**Date :** 2026-11-11 (pas F1-2). **Verdict : 0 appel sortant.**

## Ce qui est vérifié

- **Dépendances :** 0. `Cargo.toml` ne déclare aucune dépendance — le crate
  est std seul (parseur JSON minimal écrit pour le module, arithmétique
  calendaire de Howard Hinnant). Aucun accès au registre crates.io à la
  compilation (vérifié : `cargo test` et `cargo build --release` sans
  téléchargement de dépendance).
- **Appels réseau du code :** 0. La bibliothèque ne fait aucun appel sortant
  (ni HTTP, ni DNS, ni socket). La résolution du SHA (V3) est injectée par
  l'appelant via le trait `ShaResolver` — le validateur ne contacte ni le
  git local ni l'API lui-même.
- **CLI `r10-receive` :** ne lit que des fichiers locaux (`--deposit`,
  `--ledger`, `--shas`) et n'écrit que sur stdout/stderr. Aucun appel
  sortant.
- **Horloge :** seule lecture extérieure au dépôt — `SystemTime::now()`,
  pour poser `recorded_at` à la consignation (D-F1-2-1).

## Les seuls appels sortants du pas (hors code — opérateur, nommés et comptés)

1. Vérifications API GitHub R10-OK du reçu de livraison (lecture du HEAD
   master, de la PR, du commit tête) — effectuées par l'exécutant, pas par
   le code.
2. `git clone` / `git push` / `gh pr create` — transport du changeset,
   pas de la télémétrie.

Aucune télémétrie, aucun identifiant, aucun secret dans le code ni dans les
fixtures (les `mission_id` `TEST-F1-2-FAUTIF-*` sont des identifiants de
test, jamais consignés).

---

# Audit télémétrie — routeur (fonction Router, D-N055 F1-3)

**Module :** `fiber:a0:fondation-13-1` — routeur de dispatch
(`01_Forkable/FKB00_Runtime/00_A0_Core/fondation-13-1/src/router.rs`,
CLI `route-dispatch`).
**Date :** 2026-11-11 (pas F1-3). **Verdict : 0 appel sortant.**

## Ce qui est vérifié

- **Dépendances :** 0. `Cargo.toml` ne déclare aucune dépendance — le crate
  est std seul (le routeur réutilise le parseur JSON minimal et
  l'arithmétique calendaire du validateur). Aucun accès au registre
  crates.io à la compilation (vérifié : `cargo test` et
  `cargo build --release` sans téléchargement de dépendance).
- **Appels réseau du code :** 0. La bibliothèque ne fait aucun appel sortant
  (ni HTTP, ni DNS, ni socket). La liste des designs signés (R2) est
  injectée par l'appelant via le trait `DesignResolver` — le routeur ne
  contacte ni le système de fichiers ni l'API lui-même.
- **CLI `route-dispatch` :** ne lit que des fichiers locaux (`--dispatch`,
  `--journal`, `--designs`) et n'écrit que dans le journal (`--journal`,
  append-only) et sur stdout/stderr. Aucun appel sortant.
- **Horloge :** seule lecture extérieure au dépôt — `SystemTime::now()`,
  pour la vérification R5 (`at` pas dans le futur) et l'horodatage
  d'inscription.

## Les seuls appels sortants du pas (hors code — opérateur, nommés et comptés)

1. Vérifications API GitHub R10-OK des reçus de livraison et de merge
   (lecture du HEAD master, de la PR, du commit tête) — effectuées par
   l'exécutant, pas par le code.
2. `git clone` / `git push` / `gh pr create` — transport du changeset,
   pas de la télémétrie.

Aucune télémétrie, aucun identifiant, aucun secret dans le code ni dans les
fixtures (les `dispatch_id` `D-N055-F1-3-FAUTIF-*` et `TEST-F1-3-*` sont
des identifiants de test, jamais inscrits au journal de production).
---

# Audit télémétrie — fonction Découvrir (D-N055 F1-4)

**Module :** `fiber:a0:fondation-13-1` — validateur de Discover
(`01_Forkable/FKB00_Runtime/00_A0_Core/fondation-13-1/src/discover.rs`,
CLI `validate-discover`).
**Date :** 2026-11-12 (pas F1-4). **Verdict : 0 appel sortant.**

## Ce qui est vérifié

- **Dépendances :** 0. `Cargo.toml` ne déclare aucune dépendance — le crate
  est std seul. Aucun accès au registre crates.io à la compilation
  (vérifié : `cargo test` et `cargo build --release` sans téléchargement
  de dépendance).
- **Appels réseau du code :** 0. La bibliothèque ne fait aucun appel sortant
  (ni HTTP, ni DNS, ni socket). La résolution des SHA complets (D2/D3) est
  injectée par l'appelant via le trait `ShaResolver` — la fonction ne
  contacte ni le git local ni l'API elle-même.
- **CLI `validate-discover` :** ne lit que des fichiers locaux
  (`--discover`, `--shas`) et n'écrit que sur stdout/stderr. Aucun appel
  sortant.
- **Horloge :** aucune lecture d'horloge — la validation D1–D8 ne dépend
  pas de l'instant (la mesure zéro est un instantané daté dans le
  document, pas l'état courant).

## Les seuls appels sortants du pas (hors code — opérateur, nommés et comptés)

1. Vérifications API GitHub R10-OK du reçu de livraison (lecture du HEAD
   master, de la PR, du commit tête) — effectuées par l'exécutant, pas par
   le code.
2. `git clone` / `git push` / `gh pr create` — transport du changeset,
   pas de la télémétrie.

Aucune télémétrie, aucun identifiant, aucun secret dans le code ni dans les
fixtures (le `G-20261112-018` du fautif n° 5 est un identifiant de test,
jamais consigné — le vrai reçu de livraison est `G-20261112-020`).
---

# Audit télémétrie — fonction Juger (D-N055 F1-5)

**Module :** `fiber:a0:fondation-13-1` — jugement de PR
(`01_Forkable/FKB00_Runtime/00_A0_Core/fondation-13-1/src/judge.rs`,
CLI `judge-pr`).
**Date :** 2026-11-12 (pas F1-5). **Verdict : 0 appel sortant.**

## Ce qui est vérifié

- **Dépendances :** 0. `Cargo.toml` ne déclare aucune dépendance — le crate
  est std seul. Aucun accès au registre crates.io à la compilation
  (vérifié : `cargo test` et `cargo build --release` sans téléchargement
  de dépendance).
- **Appels réseau du code :** 0. La bibliothèque ne fait aucun appel sortant
  (ni HTTP, ni DNS, ni socket). La résolution des SHA complets (J2/J5),
  la lecture CI (J3) et les résultats de suite (J4) sont injectés par
  l'appelant — la fonction ne contacte ni le git local ni l'API elle-même.
- **CLI `judge-pr` :** ne lit que des fichiers locaux (`--judgment`,
  `--shas`, `--ci`, `--suite`) et n'écrit que sur stdout/stderr. Aucun
  appel sortant.
- **Horloge :** aucune lecture d'horloge — le jugement J1–J8 ne dépend
  pas de l'instant (la date du jugement est un fait du dossier, pas
  l'état courant).

## Les seuls appels sortants du pas (hors code — opérateur, nommés et comptés)

1. Vérifications API GitHub R10-OK du reçu de livraison (lecture du HEAD
   master, de la PR, du commit tête, des check-runs) — effectuées par
   l'exécutant, pas par le code.
2. `git clone` / `git push` / `gh pr create` — transport du changeset,
   pas de la télémétrie.

Aucune télémétrie, aucun identifiant, aucun secret dans le code ni dans les
fixtures (le `G-20261112-901` du fautif n° 5 est un identifiant de test,
jamais consigné — le vrai reçu de livraison est `G-20261112-028` à
l'ouverture de la PR, mission `LE1-FAB-D-N055-009`).
---

# Audit télémétrie — fonction Exécuter (D-N055 F1-6)

**Module :** `fiber:a0:fondation-13-1` — exécution de merge
(`01_Forkable/FKB00_Runtime/00_A0_Core/fondation-13-1/src/execute.rs`,
CLI `execute-merge`).
**Date :** 2026-11-12 (pas F1-6). **Verdict : 0 appel sortant dans le code ; 1 appel en écriture d'état nommé, compté et tracé, par la CLI.**

## Ce qui est vérifié

- **Dépendances :** 0. `Cargo.toml` ne déclare aucune dépendance — le crate
  est std seul. Aucun accès au registre crates.io à la compilation
  (vérifié : `cargo test` sans téléchargement de dépendance).
- **Appels réseau du code :** 0. Le module `execute` ne fait aucun appel
  sortant (ni HTTP, ni DNS, ni socket). La résolution des SHA complets
  (E1/E2/E6/E7), la lecture CI (E3), le mergeable (E4) et les preuves
  post-merge (E7) sont injectés par l'appelant — la fonction ne contacte
  ni le git local ni l'API elle-même.
- **CLI `execute-merge` :** ne lit que des fichiers locaux (`--execution`,
  `--shas`, `--ci`) et n'écrit que sur stdout/stderr. Aucun appel sortant
  dans la CLI elle-même — elle ne fait pas d'HTTPS (std seul, zéro
  dépendance).
- **Horloge :** aucune lecture d'horloge — l'exécution E1–E8 ne dépend
  pas de l'instant (la date de l'exécution est un fait du dossier, pas
  l'état courant).

## Le seul appel en écriture d'état du pas (hors code — opérateur, nommé, compté et tracé)

1. **Le merge** (`gh pr merge --merge`, ou `POST /pulls/{n}/merge`,
   méthode `merge`) — 1 appel par merge exécuté, effectué par l'opérateur
   sur instruction du dossier validé en pré-merge par la CLI
   (`execute-merge check --pre-merge`, ACCEPTÉ E1–E5), et consigné dans
   le dossier d'exécution (E6 : commande exacte, paramètres, horodatage,
   sortie — merge commit SHA, `merged: true`), puis vérifié post-merge
   par un tiers (E7). C'est le premier appel API en écriture d'état du 1
   (D-F1-6-7, A-F1-6-3) : les vérifications R10-OK sont des lectures, le
   transport `clone`/`push`/`pr create` est une écriture de contenu — le
   merge est une écriture d'état (il change `merged`, il crée le commit
   de merge, il ferme la PR).

## Les seuls appels sortants du pas (hors code — opérateur, nommés et comptés)

1. Vérifications API GitHub R10-OK du reçu de livraison (lecture du HEAD
   master, de la PR, du commit tête, des check-runs, du mergeable) —
   effectuées par l'exécutant, pas par le code.
2. `git clone` / `git push` / `gh pr create` — transport du changeset,
   pas de la télémétrie.
3. `gh workflow run` (déclenchement manuel de la CI du témoin sur sa tête,
   base jetable hors `pull_request` branches master) + `gh pr merge
   --merge` (l'appel de merge, § ci-dessus).

Aucune télémétrie, aucun identifiant, aucun secret dans le code ni dans les
fixtures (le `G-20261112-901` du fautif n° 5 est un identifiant de test,
jamais consigné — le vrai reçu de livraison est `G-20261112-031` à
l'ouverture de la PR, mission `LE1-FAB-D-N055-011` PROPOSÉE, assignation
au dépôt).

---

# Audit télémétrie — fonction Mémoriser (D-N055 F1-7)

**Module :** `fiber:a0:fondation-13-1` — citation de fait
(`01_Forkable/FKB00_Runtime/00_A0_Core/fondation-13-1/src/memory.rs`,
CLI `recall-fact`).
**Date :** 2026-11-13 (pas F1-7). **Verdict : 0 appel sortant.**

## Ce qui est vérifié

- **Dépendances :** 0. `Cargo.toml` ne déclare aucune dépendance — le crate
  est std seul. Aucun accès au registre crates.io à la compilation
  (vérifié : `cargo test` sans téléchargement de dépendance).
- **Appels réseau du code :** 0. Le module `memory` ne fait aucun appel
  sortant (ni HTTP, ni DNS, ni socket). La ligne source (M2), la date de
  la source (M3), les corroborations (M5) et le fautif planté (M6) sont
  injectés par l'appelant — la fonction ne contacte ni le fichier local
  ni l'API elle-même.
- **CLI `recall-fact` :** ne lit que des fichiers locaux (`--citation`,
  `--source`, `--corroboration`, `--fautif`) et n'écrit que sur
  stdout/stderr. Aucun appel sortant — elle ne fait pas de recherche
  sémantique (A-F1-7-5) : elle lit un index re-compilé et relit la source
  au fichier. Les lectures sont nommées, comptées et tracées (1 source +
  N corroborations + 1 fautif).
- **Horloge :** la CLI lit l'horloge système pour l'horodatage de la
  consignation (UTC, comme `recorded_at` du validateur R10) — la
  validation M1–M8 elle-même ne dépend pas de l'instant (la date de la
  citation est un fait du dossier, pas l'état courant).

## Les seuls appels sortants du pas (hors code — opérateur, nommés et comptés)

1. Vérifications API GitHub R10-OK du reçu de livraison (lecture du HEAD
   master, de la PR, du commit tête, des check-runs) — effectuées par
   l'exécutant, pas par le code.
2. `git clone` / `git push` / `gh pr create` — transport du changeset,
   pas de la télémétrie.

Aucune télémétrie, aucun identifiant, aucun secret dans le code ni dans les
fixtures (les chemins `~/MEMORY.md` et `~/side-chats/…/MEMORY.md` des
fixtures sont des chemins de sources personnelles, pas des secrets ; les
identifiants de test `G-20261112-901` des pas précédents ne sont pas repris
ici — le vrai reçu de livraison est `G-20261112-034` PROPOSÉ à l'ouverture
de la PR, mission `LE1-FAB-D-N055-013` PROPOSÉE, assignation au dépôt).
