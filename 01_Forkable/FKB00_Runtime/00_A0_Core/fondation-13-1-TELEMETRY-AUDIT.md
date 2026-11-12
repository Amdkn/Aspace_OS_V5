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
