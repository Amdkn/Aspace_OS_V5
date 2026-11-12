# Jugement — D-N055 F1-4 : fonction Découvrir (PR #44)

**Fonction :** juge 13e, fonction de jugement indépendante du pas F1-4.
**Date du jugement :** 2026-11-12 ~14:55 EST (`2026-11-12T19:55:41Z`).
**Objet jugé :** PR [#44](https://github.com/Amdkn/Aspace_OS_V5/pull/44) — « D-N055 F1-4 : fonction Découvrir — validateur de Discover D1–D8 + CLI validate-discover ».
**Design jugé contre :** `plans/DESIGN-FONDATION-13-1-F1-4-PROJET.md`, SIGNÉ, journal 923 (D-F1-4-1..6, A-F1-4-1/A-F1-4-2/A-F1-4-3, P-F1-4-1..3).
**Méthode :** rejeu indépendant, rien pris sur parole. Clone frais `/tmp/juge-f1-4` (jamais `~/workspace/v5-repo/`, jamais les fichiers de Ryan tels quels) ; tête PR vérifiée à l'API avant bascule ; diff complet lu ; suite re-courue ; CLI re-courue ; CI re-vérifiée à l'API au moment du jugement.

## Verdict : VALIDÉE

**Recommandation merge : OUI, tel quel, sur la tête `2d38798`.**
Aucun amendement. Le merge est **autorisé tel quel** sur la tête `2d3879808cd165a449016372a8a8ed4e4af03ec3`.
Merge en **true merge commit** (2 parents, DVG-01), jamais par le runner — étape 7 du design.
H-F1-1 (variante) = reçu du merge qui clôt F1-4 (mission `LE1-FAB-D-N055-008`, entry_id proposé `G-20261112-019`) — **après le merge, par un exécutant dédié, pas dans ce pas** (P-F1-4-3). Aucun reçu R10 consigné par ce jugement.

## État de la PR (vérifié à l'API au moment du jugement)

- PR #44 **ouverte**, tête `2d3879808cd165a449016372a8a8ed4e4af03ec3` (1 commit, parent unique `96d64ce8c5fb7626a9a80ef1c5602bfb38b7f273` = base master), base master `96d64ce`.
- `mergeable: true`, `mergeable_state: clean`, 10 fichiers, **+1050/−5**.
- Commit tête : committer date `2026-11-12T19:47:31Z` (14:47:31 EST).
- **CI : 8/8 check-runs `completed/success`, 0 non-success** (re-vérifiée à l'API à 14:55 EST) : CodeQL ; Verify 01 Kernel Gates ; Verify 02 Holons 578 QualityControl ; Verify 03 Submodules EGM Harvester ; Verify 04 Security OWASP RigInfinity ; Deterministic Gate (5D Semantic AST + CAS Holons + 7R + OKF) ; S1-RICK & Reviewer-Security ; Analyze (actions). Note : l'API legacy des statuts combinés retourne `pending` avec 0 statut — ce n'est pas la CI, ce sont les 8 check-runs qui font foi. Le reçu 020 disait honnêtement 7 success + 1 Analyze `in_progress` à son instant, sans affirmer le vert complet ; Analyze est depuis passé `success`.

## Diff lu en entier (10 fichiers, clone frais, tête `2d38798`)

| Fichier | Contenu vérifié |
|---|---|
| `00_Memoire/bundle/concepts/fondation-13-1.md` (+100/−1, §8 nouveau + §7 corrigé) | F1-4 consigné avec sa preuve ; correction §7 portée en avant (« F1-3 PR ouverte, non mergée » → mergée `4668305`, reçu 016) ; Divergence enrichie de 3 notes F1-4 (SHA court = référence, D4/D6 portés par les sections, D7 attestation positive). |
| `00_Memoire/bundle/log.md` (+3) | Note 2026-11-12 : PR OUVERTE (non mergée), suite 51/51, fautif n° 1 rejeté D2, re-validation ACCEPTÉE, H-F1-1 (variante) après le merge. |
| `…/fondation-13-1-TELEMETRY-AUDIT.md` (+37) | § Découvrir : 0 appel sortant, 0 dépendance, résolution SHA injectée ; seuls appels sortants du pas nommés (vérifications API R10-OK + transport git/gh, opérateur). |
| `…/fondation-13-1.manifest.json` (1 ligne) | Fonctions « Recevoir (Graham) + Router (Nardole) + Découvrir (Bill) », surface += `validate_discover(...)` + `validate-discover check …`, `issued_by` += F1-4 (journal 923), `validated_by` : F1-2 VALIDÉE, F1-3 VALIDÉE (jugement journal 813), F1-4 jugement à venir. |
| `…/fondation-13-1/Cargo.toml` | Description += Découvrir ; `[[bin]] validate-discover` ajouté ; **aucune section `[dependencies]`**. |
| `…/src/bin/validate-discover.rs` (91 lignes, neuf) | CLI `check --discover <fichier.md> --shas <shas.txt>` ; sortie 0 accepté / 2 rejeté (raison nommée) ; ne lit que des fichiers locaux, n'écrit que stdout/stderr. |
| `…/src/discover.rs` (531 lignes, neuf) | `validate_discover` D1→D4→D5→D7→D2→D3→D6→D8 ; D2/D3 via `ShaResolver` injecté ; lu en entier (voir § « Lecture du validateur »). |
| `…/src/lib.rs` (+8/−2) | `pub mod discover;` ; adresse `fiber:a0:fondation-13-1` (Recevoir, Router et Découvrir). |
| `…/tests/discover.rs` (119 lignes, neuf) | 7 tests : 1 passant + 5 fautifs (unicité `count == 1` assertée) + document vide D1. |
| `…/tests/fixtures/discover-f1-4.md` (158 lignes, neuf) | Copie du Discover — **vérifiée byte-identique** à `evidence/D-N055/DISCOVER-F1-4.md` (`cmp`, ce jugement). |

## Rejeu indépendant — suite et CLI (clone frais, `cargo test` du daemon)

- **`cargo test` : 51/51 PASS, 0 échec** (re-couru dans le clone frais ; `~/.cargo/bin` ajouté au PATH, `cargo` absent du PATH par défaut) : 7 lib + 7 discover + 17 R10 + 20 router. F1-2/F1-3 en régression verte (17 + 20 inchangés, 0 échec). Sortie conforme au `harness-F1-4.log` de Ryan (mêmes comptes, mêmes noms de tests).
- **CLI `validate-discover check` sur `DISCOVER-F1-4.md` : ACCEPTÉ — D1–D8 passés, 3 SHA complets vérifiés, sortie 0** (re-couru avec les 3 SHA complets vérifiés à l'API par le juge : voir H-F1-1).
- **CLI sur `DISCOVER-FAUTIF-1.md` : REJET D2, sortie 2** — « champ 'ancre' : le merge de la PR #30 est affirmé sans ancre — ni SHA complet du merge, ni vérification à l'API ». Diff re-vérifié par le juge : **une seule différence, ligne 45** (`diff` : 1 ligne changée), conforme à A-F1-4-1.
- **Garde-fous n° 2–5** (dérivés par le juge avec les mêmes remplacements uniques que `tests/discover.rs`, `count == 1` asserté pour chacun) : **n° 2 → REJET D4** (décision tranchée, sortie 2) ; **n° 3 → REJET D7** (source citée non lue, sortie 2) ; **n° 4 → REJET D6** (correction silencieuse, sortie 2) ; **n° 5 → REJET D5** (exécution déguisée, sortie 2). Raisons nommées dans chaque cas.

## Lecture du validateur (`src/discover.rs`, lu en entier)

- Ordre D1 → D4 → D5 → D7 → D2 → D3 → D6 → D8 conforme au design §4 et au Discover §4.
- D4 exclut les §4 et §6 (la règle et le rejet motivé décrivent, ne tranchent pas) — conforme à la Divergence portée dans la fiche ; le fautif n° 2 (décision ajoutée au §8) est bien rejeté D4.
- D7 exige l'attestation positive « lu en entier » au §10 et exclut explicitement « non lu en entier » — c'est la correction portée en avant (fiche §8, reçu 020) : la première version acceptait la négation comme attestation parce que la chaîne contient « lu en entier ». Le fautif n° 3 est bien rejeté D7 après correction.
- D2 : (a) tout SHA 40-hex cité doit résoudre via le résolveur injecté ; (b) la ligne F1-3 CLOSE du §2 doit porter le SHA complet du merge + « vérifié à l'API » ; (c) aucun fait « récit de l'exécutant » non nié aux §0/§2. D3 : §0 daté + Master HEAD complet qui résout. D6 : la correction BYB F1-2 v2 (14 214 o, écart 146 o) doit figurer au §2.
- Le validateur ne contacte ni git ni API (résolution injectée) ; `grep -riE "reqwest|hyper|TcpStream|UdpSocket|std::net|http"` sur `src/` : aucun résultat. `Cargo.lock` ne contient que le crate lui-même.

## Tableau des hold-outs

| Hold-out | Verdict | Preuve (rejeu indépendant) | Source |
|---|---|---|---|
| **H-F1-1 (variante)** — Découverte : ce Discover-ci, lu en entier, ancres re-vérifiées, accepté comme saisine, re-validé par la fonction avec le même verdict | **VERT** | Discover `DISCOVER-F1-4.md` lu en entier par le juge (158 lignes, 32 219 o — `wc` conforme au design §9) ; ancres re-vérifiées : registre 922 lignes à l'instantané (924 aujourd'hui = 922 + journaux 923/924, commit master « registre 924 lignes, journaux 923 + 924 ») ; comptes 185 « Bill » (sensible à la casse) / 198 « découvrir »/« discover » / 3 « F1-4 » au design §9 — aujourd'hui 186/200/4, cohérents avec les 2 journaux ajoutés ; tailles re-mesurées : F1-2 20 019 o/141 l., F1-3 20 161 o/320 l., maître Bill 67 267 o/407 l. ; PR #30 mergée `4668305c…` vérifiée à l'API (merged true, merged_at 2026-11-11T07:02:50Z, **2 parents `63b5816` + `12b7928`**, DVG-01) ; PR #26 mergée `1f89b568…` (merged_at 2026-11-11T06:11:32Z) ; Master HEAD `d97223538c…` résout (committer 2026-11-12T18:42:46Z) ; journal-router seq 1–7 lus (DELIVER typé/relayé/accusé, JUDGE demandé/relayé/rendu 02:02:33, pulse) ; acceptation consignée au design §9 (Discover lu en entier, ancres confirmées par ses propres lectures, D-F1-4-1..6 ADOPTÉES, A-F1-4-3) ; **re-validation par la fonction : CLI ACCEPTÉ D1–D8, 3 SHA vérifiés, même verdict que l'acceptation** (étape 4 du design, sans échec). Portée bornée au Discover de pas, comme designé. | Design §9 ; Discover lu en entier ; `gh api` (PR #30/#26, commits `4668305…`/`1f89b56…`/`d972235…`) ; `journal-router.jsonl` seq 1–7 ; CLI re-courue |
| **H-M1** — Mesure zéro nommée (registre, comptes, master) | **VERT** | Base du Discover (§0) re-vérifiée ci-dessus. Re-mesure à l'exécution (fiche §8) **exacte au fichier aujourd'hui** : registre **924 lignes**, **186** lignes « Bill », **200** « découvrir »/« discover », **4** occurrences « F1-4 » (`wc -l`, `grep -c`/`-ci`, ce jugement) ; master base PR `96d64ce` (tête vérifiée à l'API, base de `a0/f1-4-discover`) ; F1-3 clos (PR #30, `4668305`, reçu 016). | `REGISTRE-NARDOLE.md` ; `gh api pulls/44` ; fiche §8 |
| **H-M2** — Aucun paquet amont modifié | **VERT** | Diff = 10 fichiers, tous sous `00_Memoire/bundle/` ou `01_Forkable/FKB00_Runtime/00_A0_Core/fondation-13-1/` (code A'Space neuf) ; `grep` de contrôle : aucun fichier hors périmètre A'Space ; aucune dépendance ajoutée (`Cargo.toml` sans `[dependencies]`, `Cargo.lock` = le seul crate). | `git diff --name-only 96d64ce..2d38798` |
| **H-M3** — Suite verte | **VERT** | `cargo test` re-couru dans le clone frais : **51/51, 0 échec** (7 lib + 7 discover + 17 R10 + 20 router) ; cas passant = ce Discover-ci ; cas rejetés = les 5 fautifs avec la raison nommée (D2/D4/D7/D6/D5, vérifiés par la CLI aussi, sortie 2) ; document vide rejeté D1. | Clone frais, `cargo test` ; CLI re-courue |
| **H-M4** — Télémétrie zéro | **VERT** | 0 appel sortant dans le code : aucune dépendance, aucun symbole réseau dans `src/` (grep ci-dessus) ; résolution SHA injectée ; CLI fichiers locaux seulement ; audit télémétrie joint et exact. Seuls appels sortants = vérifications API + transport, opérateur, nommés et comptés dans l'audit. | `src/discover.rs` + CLI lus ; `Cargo.toml` ; `Cargo.lock` ; audit télémétrie |
| **H-M5** — Manifeste | **VERT** | Fonction Découvrir nommée au manifeste du module, adresse `fiber:a0:fondation-13-1`, surface += `validate_discover` + CLI ; version 0.2.0. (Le manifeste du daemon RigInfinity reste dû côté RigInfinity — dette portée dans la fiche, § Divergence, comme en F1-3.) | `fondation-13-1.manifest.json` (diff) |
| **H-M6** — Frontière | **VERT** | Seul le code A'Space de la fonction Découvrir (diff ci-dessus) ; section « Divergence » de la fiche remplie (3 notes F1-4 : SHA court = référence, D4/D6 portés par les sections, D7 attestation positive). | Diff ; fiche § Divergence |
| **H-M7** — Fiche versionnée | **VERT** | Fiche `FONDATION-13-1.md` mise à jour : statut F1-3 clos, §7 corrigé (porté en avant), §8 F1-4 complet (design, domicile, suite, fautif planté, re-validation, H-M1 re-mesurée, correction D7, hold-outs). | Diff fiche |
| **H-F8-9** — Plafonds (1 % Fondation / 5 % par pas / 20 % mission) | **VERT avec observation O2** | Aucun dépassement constatable : le pas est un validateur local sans appel sortant, sans dépendance, sans exécution lourde. Mais la mesure tokens à la comptabilité du fournisseur, exigée par le design §2 (« consignée dans le reçu du pas »), **n'apparaît pas dans le reçu 020** — voir observation O2 (non bloquante, même traitement qu'en F1-3). | Design §2 ; `RESULTS-F1-4.json` ; `RESULTS-F1-3.json` / `JUGEMENT-F1-3.md` (aucune mesure tokens non plus) |

## Routage (journal-router.jsonl, seq 8–12, lu au fichier)

Seq 8 `dispatch_typed` DELIVER (14:47:49) → seq 9 relayé à l'exécutant → seq 10 accusé avec preuve PR #44 (tête `2d38798…`, base `96d64ce`, mergeable true, 10 fichiers +1050/−5 — **conforme à l'API**) → seq 11 `judgment_requested` JUDGE → seq 12 relayé à la fonction de jugement. Séquences contigües, sans trou (1–12). Ce jugement est l'événement attendu par seq 11/12 ; le juge ne l'inscrit pas lui-même au journal (c'est au routeur / coordinateur).

## Écarts et observations — nommés, rien lissé

**Aucun écart bloquant. Aucun amendement (C1, C2, … : néant).** Trois observations non bloquantes, qui ne remettent en cause ni un hold-out ni le merge :

- **O1 — Discover §9 : l'acceptation y est formulée au présent alors que le document précède la signature.** Le §9 porte « **accepté comme saisine** (le design F1-4 est signé sur sa base) » — une affirmation au présent dans un document écrit avant la signature. Le même §9 se corrige aussitôt (« ce Discover ne l'affirme pas, il la cadre », « l'acceptation sera consignée dans le projet de design »), et la fonction de design a adopté D-F1-4-3 avec ce texte sous les yeux. L'acte qui compte — l'acceptation consignée au design §9, vérifiée par le juge — existe et est indépendant. La formulation est à la limite de D-F1-4-3, mais elle ne déclenche pas D4 (« accepté » ≠ « ADOPTÉE ») et ne change pas la preuve. **Pas d'amendement** : le texte est signé tel quel, la tension est portée ici, pas lissée.
- **O2 — H-F8-9 : la mesure tokens n'est pas consignée dans le reçu 020.** Le design §2 exige la mesure à la comptabilité du fournisseur « consignée dans le reçu du pas » ; `RESULTS-F1-4.json` ne porte aucun chiffre de tokens. Même lacune en F1-3 (ni `RESULTS-F1-3.json` ni `JUGEMENT-F1-3.md` ne portent de mesure tokens, et F1-3 a été VALIDÉE). Le pas est manifestement loin des plafonds (code local, 0 appel sortant), mais le chiffre manque. **Recommandation (non bloquante, pour le reçu du merge 021) :** y consigner la consommation tokens du pas F1-4 ; à défaut, la lacune se répète à chaque pas et H-F8-9 devient invérifiable en pratique.
- **O3 — `validate_discover` code en dur la mission `D-N055 F1-4` dans `ValidDiscover`.** D1 vérifie la présence de « Mission : », pas sa valeur : un autre Discover passant D1–D8 retournerait quand même `mission: "D-N055 F1-4"`. Cosmétique — la fonction est designée pour ce pas, pas comme validateur générique. **Pas d'amendement.**

**Hors périmètre du jugement de PR (porté honnêtement, pas un écart) :** l'affirmation du reçu 020 sur l'union des branches `work-*-ledger` (23 refs, 018/019 pris, 020/021 et missions 007/008 libres) n'a **pas** été re-vérifiée indépendamment par le juge : le reçu est tenu en local, non suivi (V4 archivé), et sa consignation/ vérification R10 relève du coordinateur après le merge. Cela ne touche pas le diff de la PR #44.

## Décisions du design respectées

D-F1-4-1..6 adoptées (design §9) ; fautif planté = n° 1, fichier distinct, une seule différence, rejet D2 (A-F1-4-1) ; fautifs n° 2–5 = une seule différence chacun, rejets D4/D7/D6/D5 (A-F1-4-2) ; preuve bornée au Discover de pas, récursion arrêtée par l'acte d'acceptation (A-F1-4-3) ; missions 007/008 et entry_id 018/019 proposés, non affirmés libres, assignation au dépôt (P-F1-4-1 — le reçu 020 indique 018/019 pris et a pris 020, à re-vérifier par le coordinateur au dépôt) ; domicile du code nommé dans la livraison et le reçu (P-F1-4-2 — `01_Forkable/FKB00_Runtime/00_A0_Core/fondation-13-1/`, manifeste `fiber:a0:fondation-13-1`) ; ordre d'exécution respecté — l'exécutant a ouvert la PR et s'est arrêté là, sans merger ni consigner H-F1-1 (variante) (P-F1-4-3).

## Conclusion

**PR #44 VALIDÉE — merge OUI, tel quel, sur la tête `2d38798`, en true merge commit (2 parents, DVG-01).**
Aucun amendement. Trois observations non bloquantes (O1, O2, O3) portées ci-dessus.
Prochaine étape (hors de ce jugement) : merge sur instruction du coordinateur, puis H-F1-1 (variante) consigné après le merge par un exécutant dédié (mission `LE1-FAB-D-N055-008`), vérifié R10-OK.

*Fin du jugement F1-4. Le juge ne merge rien, ne consigne pas de reçu R10, n'écrit pas au registre Nardole.*
