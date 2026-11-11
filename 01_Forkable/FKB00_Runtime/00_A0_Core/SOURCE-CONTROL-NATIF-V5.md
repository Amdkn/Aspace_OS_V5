# Source control natif V5 — fiche (D-N054, H-M7)

**Mission :** D-N054 — Source control natif V5, au-delà du paradigme Scion.
**Design :** `SOURCE-CONTROL-NATIF-V5-SCION-plan-borne.md` (Clara, signé, 28 728 o, D1–D15).
**Adresse :** `fiber:a0:source-control-natif`. **Hôte :** daemon unique RigInfinity (`crates/infinity-daemon`, Rust).
**Propriétaire :** cœur Buzz (S2-D12 ; S3-BILL, S3-CLARA, S3-NARDOLE).

## Substrat (H-M1)

- V5 master `e68f130` (à la livraison SC-0 ; le master bouge par les pulses workgraph — re-vérifier avant chaque merge).
- `.gitmodules` : 118 entrées, 118 URL Amdkn, 0 dehors.
- Clone complet : 28,33 Go (openclaw 13,0 Go, 46 %) — l'argument du natif.
- Check `r10-receipt` : 0 occurrence dans V5 (décision signée H-02-A1-2, mécanisme à implémenter à SC-4).
- Branches : 21 (18 mergées, 3 en vie au design).

## Base daemon (SC-0)

- RigInfinity `aspace-v5-native`, pin **`e866578`** (re-pin SC-0 ; ancien pin `86f1139`, squelette).
- **34 fichiers suivis** au pin (`git ls-tree -r --name-only | wc -l`) — correction : le design citait 35.
- Commits déposés : `bd7c946` (pas 3 infinity) + `a372582` + `e190645` (pas 4 openrig) + `e866578` (pas 5 agent-zero).
- Preuve SC-0 : le pin pointe le daemon ; le Runtime démarre sur le pin (suite `cargo test -p infinity-daemon` re-vérifiée au pin).

## Référence clean-room

- **CarterT27/scion** (Rust, Apache-2.0, 3 972 Ko, 295 étoiles, 25 forks, push 2026-10-16, non affilié Anthropic, pas un fork) — **référence seule, jamais copiée** ; clean-room si transposition.
- Scion dans V5 avant D-N054 : nommé en 10 endroits, documenté en 1, implémenté en 0.
- Benchmark retenu : git gagne le commit ; le natif doit battre git à la *question* (pas de clone de 28 Go pour un diff) et à la *coordination* (le changeset porte son jugement).

## Dette de divergence

- **Le manifeste du daemon (`aspace-plugin.json` dans RigInfinity) ne nomme pas encore le module source-control-natif** — à ajouter quand le module atterrit (SC-1), pas un blocage du re-pin. Ce manifeste V5 est la nomination en attendant.
- Aucune divergence de code au SC-0 : le re-pin n'ajoute aucune ligne (changement de pointeur seul).

## Contraintes (§2 du design)

- Plafonds : 1 % le natif, 5 % par pas (SC-0..SC-10), 20 % mission-wide, alerte 80 %.
- Calendrier : 1 jour max par pas, 11 jours max. Un pas ne commence que quand le précédent est vert — sauf ordre S0.
- Le natif ne reconstruit pas git (BYB §3 OUT, garde-fou) ; local-first ; `enforce_admins` reste false ; pas de verrou global.
- Saisine explicite au 13e à chaque livraison ; merge true merge commit (2 parents, DVG-01), jamais par le runner ; reçu R10 par pas.
- Arbitrages vision possibles (via Rick → A0) : (a) store séparé de `factory.sqlite` ; (b) preuve finale avant les pas intermédiaires.
