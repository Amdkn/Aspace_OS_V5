# Discover — D-N055 F1-4 : Découvrir (produire un Discover sans Bill comme session séparée)

**Mission :** D-N055 F1-4 (Découvrir).
**Auteur :** le 1 — fonction Découvrir, exercée en sous-agent borné (pas de session Bill séparée).
**Date :** 2026-11-12 ~13:56 EST.
**Statut :** Discover livré au coordinateur (fonction de design interne) — **pas un design, pas une signature, pas une exécution**.
**Sources lues en entier :** `plans/FONDATION-13-1-plan-borne.md` (plan maître signé Clara, §4 F1-4, §6 H-F1-1 variante, D2, D5, D8) ; `plans/BYB-FONDATION-13-1.md` (BYB maître, mesure zéro des 13 sessions, §5 Q2/Q5/Q8, §8 hold-outs) ; `architecture-compagnons/discover-fondation-13-1.md` (Discover maître de Bill, 67 267 o, 407 lignes — lu en entier, §0–§9) ; `evidence/D-N055/DISCOVER-F1-3.md` (Discover F1-3, la FORME reprise ici) ; `evidence/D-N055/DISCOVER-F1-2.md` (Discover F1-2) ; `plans/DESIGN-FONDATION-13-1-F1-3-PROJET.md` (design F1-3 signé, journal 806) ; `evidence/D-N055/JUGEMENT-F1-3.md` (jugement F1-3) ; `evidence/D-N055/RESULTS-F1-3.json` (reçu de livraison F1-3, lu en entier) ; `plans/BYB-FONDATION-13-1-F1-3.md` (BYB F1-3).
**Règle de ce document :** chaque fait est vérifié au fichier (`grep` / `sed` / `wc` sur le registre et les evidence, `git log` / `git ls-tree` dans `~/workspace/v4-factory/repo-v4-readonly`, sans changer de branche) et/ou à l'API GitHub avant d'être affirmé. Un 404 ou un 422 sur un SHA court n'est pas une preuve d'absence — tous les SHA ci-dessous sont vérifiés à leur forme complète (40 hex).

## 0. Mesure zéro — l'état actuel de Découvrir (vérifié)

Aujourd'hui, découvrir = la session Bill (Compagnons, Buzz, chat `500abaec`). C'est elle qui a produit le Discover maître de la Fondation. Mais ce n'est pas le fait central de ce pas. Le fait central, à ne pas esquiver, est celui-ci : **la fonction Découvrir du 1 a DÉJÀ produit deux Discovers en sous-agent borné, sans session Bill séparée** — DISCOVER-F1-2.md et DISCOVER-F1-3.md portent tous deux l'en-tête « le 1 — fonction Découvrir, exercée en sous-agent borné (pas de session Bill séparée) ». F1-4 ne part donc pas de zéro : il doit définir ce qui fait de H-F1-1 (variante) une vraie preuve et non un ré-étiquetage de ce que F1-2 et F1-3 ont déjà fait incidemment. La mesure zéro porte sur les trois Discovers existants, pas sur un seul.

État vérifié ce jour (2026-11-12 ~13:56 EST) :

- **Le Discover maître de Bill (session) :** `~/workspace/architecture-compagnons/discover-fondation-13-1.md` — **67 267 o, 407 lignes** à l'instantané de ce Discover. Au moment du design signé, il faisait 63 269 o, 398 lignes (plan maître, en-tête) — il a grandi depuis, par ses propres corrections portées en avant (§0.4.5, notes datées 2026-11-10 ~22:54 et ~23:58 EST, l'original non effacé). C'est le Discover d'une mission entière : §0 mesure zéro re-vérifiée + corrections portées (§0.4.1–§0.4.4, puis §0.4.5), §1 le problème mesuré, §2 l'état de l'art (recherche déléguée par Bill à un sous-agent chercheur — la forme C, un lead qui délègue et synthétise), §3 les trois formes + la synthèse (A siège + B corps + C mécanisme), §4 le mapping des 13 fonctions, §5 routeur et registre, §6 la vérification (la question la plus dure, §6.3), §7 mémoire/lignée, §8 migration et rollback, §9 risques, découpage, hold-outs, questions. **Ce que la fonction doit reproduire :** la structure et la discipline (mesure zéro vérifiée, corrections portées en avant, questions nommées sans les trancher, limites avouées — « ce que le champ ne prouve pas »), pas la taille ni le périmètre d'une mission entière.
- **Le Discover F1-2 (fonction du 1) :** `evidence/D-N055/DISCOVER-F1-2.md` — **20 019 o, 141 lignes** (`wc -c` / `wc -l`, ce tour). Produit par la fonction Découvrir en sous-agent borné, ~01:00 EST le 2026-11-11. Contenu : mesure zéro de Recevoir (ledger 247 fichiers / 212 reçus, 37 reçus numérotés vérifiés un à un), format R10 v1 ancré sur les reçus 001/002/026 lus au fichier, règles de validation V1–V8, rejet motivé (4 dépôts fautifs proposés), preuve H-F1-5 cadrée. Sa preuve d'usage : le design F1-2 signé (journal 790) l'a lu et l'a repris ; la PR #26 a été mergée (`1f89b56`) et le reçu H-F1-5 consigné.
- **Le Discover F1-3 (fonction du 1) :** `evidence/D-N055/DISCOVER-F1-3.md` — **20 161 o, 320 lignes** (`wc -c` / `wc -l`, ce tour). Produit par la fonction Découvrir en sous-agent borné, ~01:52 EST le 2026-11-11. Contenu : mesure zéro de Router (registre 805 lignes, 55 lignes de typage / 66 dispatches, 222 accusés, 164 pulsations, 478 mentions Nardole), format de l'événement JSONL à 10 clés, règles de validation R1–R8, relais sans message, rejet motivé (5 dispatches fautifs proposés), preuve H-F1-4 cadrée. Sa preuve d'usage : le design F1-3 signé (journal 806) l'a lu **en entier** et en a **vérifié les ancres par ses propres lectures** (§9 du design : « ancres confirmées par mes propres lectures ») avant de trancher D-F1-3-1..6 — c'est le patron d'acceptation que ce Discover propose de formaliser (§5).
- **Le registre nomme F1-4 une seule fois comme pas à venir :** journal 814 (ligne 814, lue au `sed`) — « F1-3 CLOSE ; F1-4 (Découvrir) peut procéder ». Toutes les autres occurrences de « F1-4 » au registre sont H-F1-4 (la preuve de routage), pas le pas. Aucun BYB F1-4, aucun Discover F1-4 n'existait avant celui-ci.
- **Ce que Bill fait comme session aujourd'hui (et que la fonction ne fait pas encore comme mécanisme) :** mesurer au fichier et corriger son propre dossier après livraison (§0.4.5 — six notes datées, dont la correction de sa propre correction §0.4.1, fausse sur un point) ; déléguer une recherche à un sous-agent chercheur et en citer les sources (§2) ; tenir la mesure zéro d'une mission entière (13 sessions confirmées une à une au `chat.list`, registre 673 lignes, Workgraph, ledger 28 fichiers). La fonction du 1, elle, a produit jusqu'ici des Discovers **de pas** : un pas, un BYB, des ancres re-mesurées à l'instantané.
- **Comptes au registre (grep, ce tour) :** 185 lignes mentionnent « Bill » ; 198 lignes contiennent « découvrir » ou « discover » (insensible à la casse). Le registre a **922 lignes** à l'instantané de ce Discover (dernier journal 922 : F8 CLOSE, ligne 922 lue au `sed`).

**Le point de défaillance, établi au BYB maître §1.4–§1.5 par analogie et confirmé par les faits :** si la session Bill est absente, rien n'est découvert — les BYB attendent leur dossier, les designs attendent leur mesure zéro. C'est le même patron que Recevoir (F1-2) et Router (F1-3) : une session dont l'absence arrête une fonction. La différence, propre à F1-4 : **la fonction a déjà produit deux fois sans la session, sans que personne n'ait défini ce qui distingue ces productions d'un Discover de session** — c'est cette définition qui est l'objet du pas, pas une troisième production incidente.

## 1. Ce que le registre et les Discovers exigent (règles à préserver)

Vérifié au fichier et aux leçons AGENTS.md :

1. **Append-only.** Chaque entrée est ajoutée à la fin ; une correction se fait par une NOUVELLE entrée, jamais par réécriture (leçon 2026-11-10 : « entrée mémoire = après l'envoi, jamais avant » ; le registre ne réécrit pas).
2. **Le journal = la ligne au moment de l'inscription.** Le numéro de journal d'une entrée est sa ligne au moment où elle est inscrite ; les insertions de lignes de table décalent les entrées antérieures (4 insertions à ce jour : D-N052, D-N053, D-N054, D-N055 — lignes 116–119). Le décalage n'est PAS uniforme — il dépend de l'ère de l'entrée (leçon 2026-11-11 ~01:47). Ne jamais appliquer une règle d'offset uniforme sans vérifier les ancres au fichier.
3. **Vérifier avant de citer.** Toujours re-vérifier la ligne au fichier (`sed`) avant de citer, surtout pour les entrées récentes — les confirmations se croisent (ex. journal 560/561, leçon 2026-11-10).
4. **En cas de collision (deux ajouts simultanés), corriger par une NOUVELLE entrée, jamais réécrire.** Les pistes parallèles inscrivent au même registre — la collision est attendue, la correction est une entrée.
5. **Un 404 ou un 422 sur un SHA court n'est pas une preuve d'absence** (leçon 2026-11-10 : `b63ed03` 422, le complet résout).
6. **Documenté vs vérifié.** Un statut déclaré ne tient pas lieu de mesure : chaque fait est vérifié au fichier ou à l'API, jamais repris d'un récit — y compris le récit de l'exécutant (jugement F1-3 : « rendu depuis les sources, non repris du récit de l'exécutant » ; reçu 015 : « le vert complet n'est PAS affirmé ici, il sera re-vérifié à l'API par la fonction de jugement »).
7. **Les corrections se portent en avant, jamais par réécriture.** Le Discover maître de Bill l'a établi en pratique (§0.4.5) : une erreur découverte après livraison devient une note datée, l'original n'est pas effacé. Le design F1-3 l'a confirmé pour le code (corrections R1/R8 « portées en avant, design signé non réécrit » — jugement F1-3 §1, acceptées parce qu'elles précisent sans relâcher).

**Conséquence pour la fonction Découvrir :** ces 7 règles deviennent des règles du mécanisme, pas des habitudes d'une session. L'append-only et le journal = ligne sont déjà des règles du journal d'événements (F1-3) ; la vérification avant citation devient la règle D2 (§4) ; la correction en avant devient la règle D6 (§4) ; « documenté vs vérifié » devient la règle de validation du Discover lui-même.

## 2. Ce que F1-1, F1-2 et F1-3 ont livré (le substrat que F1-4 consomme)

Vérifié à l'API et au fichier :

- **F1-1 CLOSE (journal 787, ligne 787 lue au `sed`) :** BYB F1-2 v2 **accepté comme saisine par la fonction de design interne** — H-F1-1 VERT : le 1 a structuré un BYB sans Rick. La v2 (14 360 o mesurés au `wc -c` ce tour — le registre porte 14 214 o, écart de 146 o porté ici en avant, à re-vérifier : le compte du registre est une mesure d'époque, pas une constante) a été lue en entier et vérifiée section par section ; la v1 était non acceptable (acceptation affirmée à tort, compte 29 faux, preuve 002 impossible — 002 déjà consigné par Graham, jamais réécrit). **C'est le précédent direct de H-F1-1 (variante) :** la preuve n'est pas la production du BYB, c'est sa lecture et son acceptation par la fonction de design — et la v1 non acceptable prouve que l'acceptation n'est pas automatique.
- **F1-2 CLOSE :** PR #26 mergée `1f89b56` (merge_commit_sha `1f89b56890ebfeb2cd06a0c963656cbd57f64a64`, merged_at 2026-11-11T06:11:32Z, 2 parents, DVG-01) ; validateur R10 v1 + consignateur (crate `fondation-13-1`, lib `r10_validator`, binaire `r10-receive`, adresse `fiber:a0:fondation-13-1`) ; suite 20/20 ; reçu H-F1-5 G-20261111-006.
- **F1-3 CLOSE (journal 814, ligne 814 lue au `sed`) :** PR #30 mergée, merge commit `4668305c988422bff91e0a78c1327c7a7875bdd9` (vérifié à l'API ce tour : merged true, merged_at 2026-11-11T07:02:50Z = 02:02:50 EST), 2 parents `63b5816` + `12b7928` (DVG-01, true merge) ; fonction Router (module `router`, CLI `route-dispatch`, suite 44/44) ; **journal d'événements `evidence/D-N055/journal-router.jsonl`, 7 lignes, seq 1–7 contigus** (lus au fichier ce tour : seq 1 `dispatch_typed` DELIVER, seq 2 relayé, seq 3 accusé avec preuve PR #30, seq 4 `judgment_requested` JUDGE, seq 5 relayé, seq 6 `judgment_rendered` à 02:02:33, seq 7 `pulse` de clôture) ; reçu H-F1-4 G-20261111-016 consigné (commit `8bc36e1` sur `work-dn055-ledger`, vérifié au `git log` ce tour : `8bc36e1` ← `35083f0` (reçu 015) ← `cdd7bc1` (reçu 006)).
- **F1-0 (inventaire) :** journal d'inventaire `evidence/D-N055/journal-inventaire.jsonl`, **2 252 lignes** (`wc -l`, ce tour) — la re-typification des 13 mémoires, du registre, du Workgraph et du ledger en entrées du journal. C'est le substrat de mémoire que la fonction Découvrir consulte, pas les 13 mémoires de sessions.
- **Master HEAD à l'instantané de ce Discover :** `d97223538ce905db8df9d0efab57718dcfeae770` (40 hex, vérifié à l'API ce tour, committer date 2026-11-12T18:42:46Z = 13:42:46 EST). **0 PR ouverte** sur V5 (vérifié à l'API ce tour). Registre 922 lignes ; dernier journal 922 (F8 CLOSE).
- **Reçus :** 015/016 pris sur `work-dn055-ledger` (31 fichiers sous `ledger/receipts/` sur cette branche, vérifié au `git ls-tree` ce tour) ; 017 cité au journal 922 (reçu G-20261112-017, F8). Les numéros 018/019 sont à vérifier à l'exécution sur l'union des branches `work-*-ledger` — ils ne sont PAS affirmés libres ici.

**Ce que F1-2/F1-3 ne livrent pas (et que F1-4 ne re-développe pas) :** le validateur R10 v1 (consignation des reçus de ce pas) ; le routeur (typage et relais du dispatch de livraison de F1-4 comme événements du journal) ; le journal d'événements lui-même (seq 8+ pour ce pas, à l'exécution).

## 3. Ce qu'est un Discover — forme et contenu proposés (à trancher au design)

Le Discover est le dossier qui précède le design signé : il mesure, il propose, il nomme les questions — il ne tranche pas, il ne signe pas, il n'exécute pas. La forme proposée (reprise de DISCOVER-F1-3.md, §0–§10, adaptée à Découvrir) :

| Section | Contenu |
|---|---|
| En-tête | Mission ; auteur = « le 1 — fonction Découvrir, exercée en sous-agent borné (pas de session Bill séparée) » ; date ; statut (« livré au coordinateur — pas un design, pas une signature, pas une exécution ») ; **sources lues en entier, nommées une à une** ; règle de vérification du document |
| §0 Mesure zéro | L'état actuel de la fonction, **vérifié au fichier/API et daté** (comptes `grep`/`wc`, lignes lues au `sed`, SHA complets, PR vérifiées à l'API) — l'instantané, pas l'état courant (les ancres périment : le registre croît, master bouge) |
| §1 Règles à préserver | Les règles du registre et des Discovers (§1 ci-dessus) — ce qui ne se négocie pas |
| §2 Substrat consommé | Ce que les pas précédents ont livré, vérifié à la source — ce que ce pas consomme sans re-développer |
| §3 Forme proposée | Ce qu'est l'artefact du pas (ici : le Discover lui-même) — forme et contenu, proposés |
| §4 Règles de validation | Les contrôles déterministes qui décident si l'artefact est recevable (§4 ci-dessous) |
| §5 Relais sans message | Comment la destinataire (fonction de design) reçoit l'artefact sans message (§5 ci-dessous) |
| §6 Rejet motivé | Le rejet d'un artefact mal formé, avec sa raison nommée, dont le fautif planté (§6 ci-dessous) |
| §7 Risques | Risques repris du BYB, avec l'ancrage Discover |
| §8 Questions au design | Les questions, avec les propositions de ce Discover — le design tranche |
| §9 Preuve | La preuve du pas, cadrée, pas exécutée |
| §10 Sources vérifiées | La liste de contrôle : chaque source lue, chaque compte, chaque SHA — vérifiable par un tiers |

**Contenu exigible (proposé) :** chaque fait porte son ancre (fichier + ligne, ou API + champ) ; chaque correction d'un fait antérieur est portée en avant avec sa date, jamais par réécriture silencieuse ; chaque limite est nommée (« ce que ce Discover ne prouve pas » — comme Bill §6.3 : « ce que le champ ne prouve pas ») ; chaque proposition est marquée « à trancher au design ».

**Ce qu'un Discover n'est jamais :** un design (aucune décision D-… tranchée) ; une signature (aucune autorisation d'exécution) ; une exécution (aucun reçu consigné, aucun merge, aucune écriture hors du fichier Discover lui-même) ; un récit du producteur (aucun fait repris d'une affirmation non vérifiée — règle D2).

**Ce qui distingue un Discover de la fonction d'un Discover de session Bill (proposition — le cœur de ce pas, à trancher au design) :** ce n'est ni la taille (20 019 / 20 161 o pour la fonction, 67 267 o pour la session — la taille suit le périmètre, un pas contre une mission), ni la forme (les §0–§10 sont les mêmes). Ce sont **trois conditions cumulatives, vérifiables de l'extérieur** :
1. **Mandat borné écrit dans le document :** un pas, une saisine, des sources nommées lues en entier — le Discover dit ce qu'il a lu et ce qu'il n'a pas lu ;
2. **Règle de vérification écrite dans le document :** chaque fait y porte son ancre (fichier/API) et sa règle de rejet (§4) — le Discover est vérifiable par un tiers sans son auteur ;
3. **Acceptation par la fonction de design, vérifiée indépendamment :** la fonction de design lit le Discover en entier et **re-vérifie ses ancres par ses propres lectures** avant de signer (patron du design F1-3 §9 : « ancres confirmées par mes propres lectures ») — et l'acceptation est sa décision, consignée par elle, jamais affirmée par le Discover lui-même (patron du BYB F1-3 : « Il n'affirme pas sa propre acceptation » ; patron de F1-1 : la v1 non acceptable prouve que l'acceptation n'est pas automatique).
Sans l'une des trois, c'est un ré-étiquetage : un texte produit par le 1 mais non vérifiable (sans 1 ou 2) ou non accepté (sans 3) n'est pas un Discover de la fonction — c'est un brouillon du lead.

## 4. Les règles de validation d'un Discover (fonction Découvrir)

Le Discover est le fichier soumis à la fonction de design avant signature. La validation est **déterministe** : chaque règle est un contrôle vrai/faux, exécutable par la fonction de design comme par la fonction de jugement. Règles (proposées, à trancher au design) :

1. **D1 — En-tête complet.** Le Discover porte : mission, auteur = fonction Découvrir (pas une session), date, statut (pas un design, pas une signature, pas une exécution), sources lues en entier nommées, règle de vérification du document. Un élément manquant = rejet.
2. **D2 — Chaque fait vérifié.** Chaque fait affirmé porte son ancre vérifiable (fichier + ligne lue au `sed`, ou API + champ, ou `wc`/`grep` avec son compte). Un fait sans ancre, ou affirmé depuis un récit (y compris le récit de l'exécutant du pas précédent), = rejet. Un SHA cité est complet (40 hex) et résout — un SHA court = rejet (même leçon que R10 V3).
3. **D3 — Mesure zéro nommée et datée.** Le §0 porte des comptes re-mesurés à l'instantané du Discover (registre en lignes, master HEAD, PR vérifiées), avec leur date. Une mesure zéro reprise d'un Discover antérieur sans re-mesure = rejet (les ancres périment — le design signé porte déjà une ancre périmée, PR #20, cf. Discover maître §0.4.5.5).
4. **D4 — Aucune décision tranchée.** Le Discover propose, il ne tranche pas : aucune décision « ADOPTÉE », aucune signature, aucune autorisation d'exécution. Une décision tranchée dans le Discover = rejet.
5. **D5 — Aucune exécution.** Le Discover ne consigne aucun reçu, n'ouvre aucune PR, ne merge rien, n'écrit rien hors de son propre fichier. Une écriture hors du fichier Discover = rejet.
6. **D6 — Corrections portées en avant.** Une erreur découverte après livraison devient une note datée ajoutée au dossier, jamais une réécriture silencieuse de l'original. Une correction silencieuse (réécriture) = rejet.
7. **D7 — Sources lues en entier.** Chaque source nommée dans l'en-tête et au §10 a été lue en entier par la fonction. Une source citée non lue (ou lue partiellement — comme Bill lisant 200 caractères de la ligne 669 et concluant à tort, §0.4.5.1) = rejet.
8. **D8 — Limites nommées.** Le Discover nomme ce qu'il ne prouve pas (« ce que ce Discover ne prouve pas ») et les questions qu'il laisse au design. Un Discover qui se présente comme complet sans limites nommées = rejet.

Ordre d'application recommandé (du moins cher au plus cher) : D1 → D4 → D5 → D7 → D2 → D3 → D6 → D8. Les contrôles D2/D3 sont les seuls qui touchent aux fichiers et à l'API ; tous les autres sont locaux au document.

## 5. Le relais sans message (comment la destinataire le reçoit)

Le relais n'est pas un message envoyé : c'est **la lecture du fichier par la fonction de design**. Le Discover vit à un chemin connu (`v4-factory/evidence/D-N055/DISCOVER-F1-4.md`) ; la fonction de design le lit en entier, re-vérifie ses ancres par ses propres lectures, et **consigne son acceptation par elle** (dans le projet de design, comme le design F1-3 §9 l'a fait pour DISCOVER-F1-3.md, et comme la fonction de design l'a fait pour le BYB F1-2 v2 au journal 787). La preuve de la lecture n'est pas un accusé de lecture — c'est **l'acte de la destinataire** : le projet de design qui cite le Discover section par section, puis la signature. Si la destinataire n'agit pas, le fichier reste non lu — le silence est visible (aucun projet de design ne le cite), pas deviné. Le dispatch de livraison de F1-4 (ouverture de la PR + demande de jugement) sera, lui, routé comme événement du journal par la fonction Router (F1-3) à l'exécution — le Discover ne le type pas, il le cadre (§9).

## 6. Le rejet motivé d'un Discover mal formé (dont le Discover fautif planté)

**Règle :** un Discover mal formé est **rejeté avec sa raison nommée, jamais corrigé silencieusement, jamais signé quand même** (BYB maître §5 Q2/Q5 ; patron H-F1-2, plan maître §D5). Le Discover est renvoyé corrigé. Le rejet nomme : la règle violée (D1–D8), la section fautive, la valeur reçue (tronquée si longue).

**Patron H-F1-2 (faute plantée) :** le design plante un Discover fautif que la fonction doit rejeter — c'est la preuve que la fonction valide (même patron que H-F1-2 pour le juge, plan maître §D5 ; même patron que F1-2, où le dépôt fautif n° 1 — SHA court — devait être rejeté V3 ; même patron que F1-3, où le dispatch fautif n° 1 — sans design signé — devait être rejeté R2). Le Discover fautif planté pour F1-4 (à spécifier au design, proposition de ce Discover) :

- **Fautif n° 1 (fait non vérifié — affirmé depuis un récit) :** Discover identique à celui-ci sauf qu'un fait central (par exemple le merge de la PR #30, ou le contenu du journal-router seq 1–7) y est affirmé sans ancre, repris du récit de l'exécutant F1-3 — doit être rejeté (D2 : aucun fait sans ancre). C'est la faute centrale : **un Discover qui affirme sans vérifier n'est pas un Discover, c'est un récit**.
- **Fautif n° 2 (décision tranchée) :** Discover portant une décision « ADOPTÉE » ou une signature — doit être rejeté (D4 : le Discover propose, il ne tranche pas).
- **Fautif n° 3 (source citée non lue) :** Discover citant le Discover maître de Bill (§8, ou §6.3) sans l'avoir lu — doit être rejeté (D7). La leçon de Bill §0.4.5.1 (200 caractères lus, conclusion fausse) est l'ancre : une lecture partielle affirmée comme complète est une faute, pas une approximation.
- **Fautif n° 4 (correction silencieuse) :** Discover réécrivant une erreur d'un Discover antérieur (par exemple le compte 14 214 o du BYB F1-2 v2) sans note datée — doit être rejeté (D6 : les corrections se portent en avant).
- **Fautif n° 5 (exécution déguisée) :** Discover consignant un reçu ou ouvrant une PR — doit être rejeté (D5 : le Discover n'exécute rien).

Un seul Discover fautif planté suffit au hold-out (le design en choisit un, les autres restant des cas de test de la fonction — voir projet de design, H-M3).

**Ce qui n'est jamais fait :** corriger silencieusement un fait ; trancher une décision dans le Discover ; signer le Discover ; affirmer un fait sans ancre ; citer une source non lue ; réécrire un Discover antérieur ; consigner un reçu depuis le Discover.

## 7. Risques repris du BYB (avec l'ancrage Discover)

- **R1 — La fonction produit un récit, pas un Discover.** Ancrage : les trois Discovers existants montrent que la validation a toujours été humaine (Bill, puis la fonction de design relisant) ; aucune validation automatique du Discover n'existe aujourd'hui — et F1-2/F1-3 ont été produits sans que la règle de validation soit écrite nulle part. Mitigation : validation déterministe §4 + Discover fautif planté §6.
- **R2 — Le ré-étiquetage : H-F1-1 (variante) est accordée à une production incidente.** Ancrage : §0 — F1-2 et F1-3 ont déjà été produits par la fonction sans définition de ce qui les distingue d'un Discover de session ; sans les trois conditions cumulatives (§3), n'importe quelle production du 1 peut être étiquetée « Discover de la fonction ». Mitigation : les trois conditions (§3) + l'acceptation vérifiée indépendamment (§5).
- **R3 — Deux vérités divergent (Discover du 1 vs Discover de session Bill).** Ancrage : le Discover maître fait 67 267 o, les Discovers de pas ~20 000 o ; deux dossiers de périmètres différents peuvent se contredire sur un même fait (ex. le compte 14 214 o vs 14 360 o du BYB F1-2 v2, §2). Mitigation : chaque Discover re-mesure à son instantané (D3) et porte ses corrections en avant (D6) ; le registre tient la référence, pas le dossier (leçon du ledger qui mute, Discover maître §0.4.3/§0.4.5.2).
- **R4 — Le pas déborde sur le jugement (fonction Juger, F1-5).** Mitigation : F1-4 découvre, il ne juge pas — la validation D1–D8 est un contrôle de recevabilité du dossier, pas un jugement de PR ; le jugement reste F1-5.
- **R5 — L'amorçage est circulaire.** Ancrage : ce Discover définit ce qu'est un Discover de la fonction — il se définit lui-même en se produisant (même patron que F1-2, qui a validé le reçu de son propre merge, et F1-3, dont le routeur a routé sa propre livraison). Mitigation : la preuve n'est pas dans ce document — elle est dans l'acceptation par la fonction de design (§9), vérifiée indépendamment ; l'amorçage est documenté, pas caché.
- **R6 — La mesure zéro périme entre le Discover et l'exécution.** Ancrage : le design signé portait déjà une ancre périmée à sa signature (PR #20 « ouverte » alors que mergée — Discover maître §0.4.5.5) ; master a bougé depuis F1-3 (`4668305` → `d972235`). Mitigation : D3 (re-mesure à l'instantané) + l'exécutant re-mesure à l'exécution (H-M1 = base du Discover, pas l'état courant — patron du design F1-3 §9).

## 8. Ce que le design doit trancher (questions BYB maître §5, avec les propositions de ce Discover)

1. **Qu'est-ce qu'un Discover produit par le 1 ?** Proposé : la forme §3 (en-tête + §0–§10) et le contenu exigible (ancre par fait, corrections en avant, limites nommées). — À trancher au design.
2. **Comment se distingue-t-il d'un Discover de session Bill ?** Proposé : les trois conditions cumulatives (§3) — mandat borné écrit, règle de vérification écrite, acceptation vérifiée indépendamment. Sans l'une des trois : ré-étiquetage, pas preuve. — À trancher au design.
3. **Quelle vérification le prouve ?** Proposé : Clara lit et accepte comme saisine — comme H-F1-1 pour le BYB (le BYB est lu par Clara et accepté comme saisine) : la fonction de design lit ce Discover en entier, re-vérifie ses ancres par ses propres lectures, et consigne son acceptation par elle (§5, §9). — À trancher au design.
4. **Quel est le patron de faute plantée applicable ?** Proposé : le fautif n° 1 (fait non vérifié, rejet D2) — la faute centrale (§6) ; les quatre autres restant des cas de test. — À trancher au design.
5. **La validation D1–D8 est-elle un contrôle ou un jugement ?** Proposé : un contrôle de recevabilité du dossier, pas un jugement de PR — le jugement reste F1-5 (R4, §7). — À trancher au design.
6. **Le Discover F1-4 lui-même compte-t-il comme la preuve, ou faut-il un second Discover produit après le design ?** Proposé : ce Discover-ci est la preuve, complétée par son acceptation (§9) — exiger un second Discover après le design serait exiger une preuve de la preuve, sans fin. — À trancher au design.

## 9. Preuve H-F1-1 (variante) (cadrage, pas exécution)

**H-F1-1 (variante) :** un Discover produit par le 1 sans Bill comme session séparée — **ce Discover-ci** (`evidence/D-N055/DISCOVER-F1-4.md`), lu en entier par la fonction de design interne, ses ancres re-vérifiées par ses propres lectures, et **accepté comme saisine** (le design F1-4 est signé sur sa base). **Ne JAMAIS affirmer sa propre acceptation** (patron du BYB F1-3 : l'acceptation est la décision de la fonction de design, consignée par elle — ce Discover ne l'affirme pas, il la cadre). Les trois conditions du §3 sont vérifiables de l'extérieur : le mandat borné est écrit dans l'en-tête ; la règle de vérification est écrite au §4 ; l'acceptation sera consignée dans le projet de design F1-4 (avec sa section de vérification, patron du design F1-3 §9). Si la fonction de design rejette ce Discover (règle D1–D8 violée), H-F1-1 (variante) échoue et la fonction Découvrir revient à sa session d'origine, Bill — rollback H-F1-9, plan maître §D8.

**Ce que ce Discover ne prouve pas (porté honnêtement) :** que la fonction Découvrir suffise pour un Discover de mission entière (67 267 o, état de l'art délégué, 13 sessions confirmées une à une) — il prouve le Discover de pas, pas le Discover de mission. La montée en périmètre est une question au design (Q6, §8), pas une affirmation de ce document.

## 10. Sources vérifiées (liste de contrôle)

- `plans/FONDATION-13-1-plan-borne.md` — lu en entier (plan maître signé Clara ; §4 F1-4, §6 H-F1-1 variante, D2, D5, D8).
- `plans/BYB-FONDATION-13-1.md` — lu en entier (BYB maître ; §1 mesure zéro, §5 Q2/Q5/Q8, §8 hold-outs).
- `architecture-compagnons/discover-fondation-13-1.md` — lu en entier (Discover maître de Bill ; 67 267 o, 407 lignes au `wc` ce tour — 63 269 o, 398 lignes au design signé, croissance = §0.4.5).
- `evidence/D-N055/DISCOVER-F1-3.md` — lu en entier (Discover F1-3 ; 20 161 o, 320 lignes).
- `evidence/D-N055/DISCOVER-F1-2.md` — lu en entier (Discover F1-2 ; 20 019 o, 141 lignes).
- `plans/DESIGN-FONDATION-13-1-F1-3-PROJET.md` — lu en entier (design F1-3 signé, journal 806 ; D-F1-3-1..6, A-F1-3-1/A-F1-3-2, P-F1-3-1..3).
- `evidence/D-N055/JUGEMENT-F1-3.md` — lu en entier (jugement F1-3 ; PR #30 VALIDÉE, corrections R1/R8 acceptées, heure réelle ~02:02 EST).
- `evidence/D-N055/RESULTS-F1-3.json` — lu en entier (reçu de livraison F1-3, mission LE1-FAB-D-N055-005, 13 preuves).
- `plans/BYB-FONDATION-13-1-F1-3.md` — lu en entier (BYB F1-3 ; 13 900 o).
- Registre `dispatch/REGISTRE-NARDOLE.md` — **922 lignes** (`wc -l`) ; ligne 787 lue au `sed` (F1-1 CLOSE, BYB F1-2 v2 accepté) ; ligne 806 lue au `sed` (design F1-3 signé) ; ligne 814 lue au `sed` (F1-3 CLOSE, « F1-4 (Découvrir) peut procéder ») ; ligne 922 lue au `sed` (dernier journal 922, F8 CLOSE) ; comptes grep : 185 lignes « Bill », 198 lignes « découvrir »/« discover ».
- Journal d'événements `evidence/D-N055/journal-router.jsonl` — 7 lignes, seq 1–7, lues au fichier (DELIVER typé/relayé/accusé, JUDGE demandé/relayé/rendu, pulse de clôture).
- Journal d'inventaire `evidence/D-N055/journal-inventaire.jsonl` — 2 252 lignes (`wc -l`).
- `repo-v4-readonly`, branche `work-dn055-ledger` : log `8bc36e1` (reçu 016) ← `35083f0` (reçu 015) ← `cdd7bc1` (reçu 006) ; 31 fichiers sous `ledger/receipts/`.
- API GitHub : master V5 HEAD `d97223538ce905db8df9d0efab57718dcfeae770` (committer 2026-11-12T18:42:46Z) ; **0 PR ouverte** ; PR #30 (closed, merged true, merged_at 2026-11-11T07:02:50Z, merge `4668305c988422bff91e0a78c1327c7a7875bdd9`).
- `plans/BYB-FONDATION-13-1-F1-2-v2.md` — 14 360 o au `wc -c` ce tour (le registre porte 14 214 o — écart de 146 o porté en avant au §2, à re-vérifier).

*Fin du Discover F1-4. Livré au coordinateur pour design. Aucun reçu consigné par ce Discover ; aucun design signé ici ; aucune exécution.*
