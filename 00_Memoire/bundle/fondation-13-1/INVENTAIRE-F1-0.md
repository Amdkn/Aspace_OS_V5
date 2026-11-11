# F1-0 — Inventaire Fondation 13 → 1 (D-N055)

**Pas :** F1-0 (l'inventaire) — premier pas de migration du design signé Clara
`FONDATION-13-1-plan-borne.md` (32 561 o, ~23:03 EST, D-N055).
**Instantané :** 2026-11-11T00:15:56-05:00 (registre 776 lignes).
**Compilateur :** `v4-factory/evidence/D-N055/inventory-f1-0.py` (déterministe).
**Harnais :** `v4-factory/evidence/D-N055/harness-f1-0.py` → `RESULTS-F1-0.json` : **6/6 PASS**.
**Preuve exigée (H-F1-6 partiel) :** l'inventaire est complet, sans perte.

## 1. Mesure zéro (H-M1)

| Source | État à l'instantané |
|---|---|
| 13 sessions | Nommées une à une par Clara (`chat.list`, 2026-11-10 ~22:53 EST) : Rick `2428b187`, 13e `a517ae1d`, 11e `6f410ddd` (8 car. — ID complet non établi), 12e `7489b6f0`, Yaz `e1ac3b2d`, Ryan `a152c901`, Bill `500abaec`, Clara `ef2544e6`, Nardole `ae7d36d1`, Rory `5dba06d6`, Amy `337fb65c`, River `dfd97c8e`, Graham `059b0c23` |
| Registre Nardole | **776 lignes** (`~/workspace/v4-factory/dispatch/REGISTRE-NARDOLE.md`) — 55 structure, 67 table, 654 entrées de journal |
| Workgraph | Sheet `1OFRYjujs81fPSS4HJWrB4M9yeduQAd35UVvaXBiHXrI` + miroir `00_Memoire/WORKGRAPH-MUSE.md` (26 lignes : 15 structure, 11 table) |
| Ledger R10 | 7 branches `work-dn*-ledger` (`~/workspace/v4-factory/repo-v4-readonly`) : **247 fichiers, dont 212 reçus** (voir §3) |
| Mémoire partagée | `~/MEMORY.md` (154 lignes) + `~/AGENTS.md` (35 lignes) |

**Total : 2 252 entrées typées** dans `journal-inventaire.jsonl` (876 264 o).
Chaque entrée : `{seq, source, type, actor, date, text (tronqué à 200 car.), proof}`.
La preuve est un pointeur (`fichier:ligne` ou `branche:chemin`) — l'inventaire ne
recopie pas les contenus, il les référence. Rien n'est perdu : chaque ligne de
chaque source est comptée (entrées + structure = lignes totales).

## 2. Sources — comptes

### 2.1 Les 13 mémoires (1 179 entrées ; 6 absentes, consignées)

| Mémoire | Lignes | Entrées | Structure | État |
|---|---|---|---|---|
| Rick (S1) | 3 142 | 709 | 2 433 | présente |
| 13e Doctor | 0 | 0 | — | **absente** |
| 11e Doctor | 0 | 0 | — | **absente** (ID complet non établi : `6f410ddd`) |
| 12e Doctor | 381 | 228 | 153 | présente |
| Yaz | 16 | 14 | 2 | présente |
| Ryan | 228 | 20 | 208 | présente |
| Bill | 102 | 80 | 22 | présente |
| Clara | 0 | 0 | — | **absente** |
| Nardole | 0 | 0 | — | **absente** |
| Rory | 0 | 0 | — | **absente** |
| Amy | 43 | 23 | 20 | présente |
| River | 0 | 0 | — | **absente** |
| Graham | 964 | 105 | 859 | présente |

7 présentes / 13. Les 6 absentes sont des entrées `absence` dans le journal
(une par mémoire) — l'absence est consignée, pas ignorée. La mémoire de Ryan
(228 lignes, 20 entrées) est surtout de la prose : chaque puce est une entrée,
ses lignes de suite comptent en structure.

### 2.2 Mémoire partagée (88 entrées)

| Fichier | Lignes | Entrées | Structure |
|---|---|---|---|
| `~/MEMORY.md` | 154 | 63 | 91 |
| `~/AGENTS.md` | 35 | 25 | 10 |

### 2.3 Registre (721 entrées : 67 table + 654 journal)

| Type | Entrées |
|---|---|
| livraison | 118 |
| confirmation | 93 |
| jugement | 72 |
| reçu | 65 |
| dispatch | 47 |
| correction | 47 |
| accusé | 41 |
| statut | 40 |
| événement (résiduel, §4) | 38 |
| message | 22 |
| saisine | 15 |
| pulsation | 13 |
| décision | 9 |
| exécution | 3 |
| validation | 1 |
| table | 67 |

### 2.4 Ledger (247 fichiers : 212 reçus + 35 autres)

| Branche | Fichiers | Reçus | Autres |
|---|---|---|---|
| work-dn047-ledger | 33 | 28 | 5 |
| work-dn048-ledger | 44 | 39 | 5 |
| work-dn049-ledger | 32 | 27 | 5 |
| work-dn051-ledger | 40 | 35 | 5 |
| work-dn052-ledger | 34 | 29 | 5 |
| work-dn053-ledger | 32 | 27 | 5 |
| work-dn054-ledger | 32 | 27 | 5 |

Les 29 reçus numérotés G-20261109-001..003 + G-20261110-001..026 sont tous
présents parmi les fichiers (vérifié par le harnais, H-F1-6-4). Les 5 « autres »
par branche sont les fichiers ledger hors `receipts/` (dont `ledger.jsonl`).

## 3. Règles de typage (déterministes, dans le compilateur)

- **Mémoires :** le type vient de la section `##` (fait / préférence / engagement /
  leçon / décision ; doctrine et règle → décision ; objectif → engagement).
  Sans mot-clé : **fait (défaut)**, compté à part (226).
- **Registre :** structure (`#`, `>`, `---`, vide, prose d'en-tête) / table (`| ...`) /
  entrée (`- 2026...` ou `- **2026...`). Le type est lu sur la **tête** de l'entrée
  (texte après « — » jusqu'au premier « . »), pas sur le corps : le corps cite des
  jugements, des reçus et des dispatches que l'entrée ne fait que mentionner.
  Mots-clés prioritaires, insensibles à la casse : jugement > accusé >
  correction (correction, corrige, divergence, addendum, clarification,
  contournement) > confirmation > dispatch (dispatch, typé, typer) > statut (`→`)
  > livraison (merg, clôtur) > reçu > pulsation (pulsation, heartbeat) > saisine >
  livraison (livraison, livré, terminé) > validation (valide, vérification) >
  décision (doctrine, protocole, décision, ordre) > exécution (push, lancé) >
  rapport > message > coordination (déjà traité) > événement (créé, ouvert).
- **Ledger :** 1 entrée par fichier receipt JSON (type `reçu`, `mission_id` et
  `summary` lus dans le JSON) + 1 par autre fichier `ledger/` (type `ledger`).
- **Dates :** première `AAAA-MM-JJ` du texte, sinon nulle.
- **Non classé : 0.** Toute ligne qui n'entre dans aucune règle est listée par le
  compilateur et fait échouer la compilation (exit 1).

## 4. Résiduels — comptés à part, pas cachés

- **`événement` (38) :** têtes de journal sans mot-clé (ex. « D-N002 (suite) »,
  « Registre créé (baseline) »). Le texte et la preuve (ligne) sont conservés.
- **`fait (défaut)` (226) :** puces de mémoire sous une section sans mot-clé de type
  (ex. `## Activation`, `## Périmètre` chez Rick). Le texte et la preuve sont conservés.

## 5. Ce que F1-0 ne fait pas

- Pas de copie des contenus : les textes sont tronqués à 200 caractères, la preuve
  pointe vers la source. La migration des contenus entiers, c'est F1-7.
- Pas de résolution des contradictions entre les 13 mémoires : elles sont portées
  comme événements de correction explicites (F1-7), jamais écrasées silencieusement.
- Pas de manifeste daemon (H-M5) : `aspace-plugin.json` nommant `fiber:a0:fondation-13-1`
  atterrit avec le code du module, pas avec l'inventaire — dette consignée dans la fiche.
- L'inventaire est un instantané : le registre continue de croître (776 lignes à
  00:15:56 EST). La re-compilation du harnais (H-F1-6-5) liste les deltas et les
  explique par le changement de sha des sources.

## 6. Preuves

- `journal-inventaire.jsonl` : 2 252 entrées, seq 1..2252 contiguë, preuves uniques.
- `RESULTS-F1-0.json` : harnais 6/6 PASS (JSONL, cohérence, preuves uniques,
  reçus numérotés, re-compilation, ledger exact).
- `COUNTS-F1-0.json` : comptes + sha12 de chaque source + horodatage de l'instantané.
