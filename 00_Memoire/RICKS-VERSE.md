# Le Rick's Verse — Structuration de l'univers de Rick (S1)

Statut : documenté — structure de référence, pas un état vérifié d'exécution.
Sources canoniques : V5 `00_Memoire/shared_brain/memory.jsonl` (entités S1 / S2 / S3),
V5 `AGENTS.md` §8, design F8 (D-N051), registre Nardole.
Rédigé 2026-11-10, sur ordre S0.

## 0. L'univers

Rick (S1) est le structurant. Son univers — le Rick's verse — est l'espace où
naissent les Before You Build, où les designs sont signés, où les dispatches
partent. Rick ne décide pas la vision (S0, l'Humain Amadou, seul détenteur de
la signature de ratification) et n'exécute pas (S3) : il structure.

Posture S1, mémoire partagée : « Near of the Loop — Gardien épistémique,
veto anti-rente Cloud, reçu R10 ».
Template : `RigInfinity/templates/s1.yaml` (créé au pas 1 de D-N051, §D11).

## 1. Les trois Doctors dans son univers (S2)

Les Doctors sont les méta-superviseurs de l'univers de Rick. Ils écrivent les
PRD, jugent les livraisons, rendent les arbitrages vision.

| Doctor | Cœur | Rôle |
|---|---|---|
| 13e Doctor | Kernel | Lead des méta-superviseurs — juge, autorité pleine sur le noyau |
| 11e Doctor | Life | Méta-superviseur — Life OS et ses 8 domaines |
| 12e Doctor | Buzz | Méta-superviseur — Buzz, frameworks et décisions |

Rick est reviewer des S2 ; Graham est kernel operator des S2.
Template : `RigInfinity/templates/s2.yaml`.

## 2. Les neuf Compagnons dans leurs Tardis (S3)

Trois Tardis, un par cœur. Chaque Tardis porte un Doctor et ses trois
Compagnons. Les Compagnons exécutent, 24/7, dans le Tardis de leur Doctor.

### Tardis Kernel — 13e Doctor
| Compagnon | Canal | Rôle |
|---|---|---|
| Ryan | Factory (l'Atelier) | Lead S3 — exécute les dispatches, merge après jugement |
| Yaz | Observatoire | Watchlist, surveillance des silences |
| Graham | Preuves | Vérificateur — reçus R10, preuves, temporalité |

### Tardis Life — 11e Doctor
| Compagnon | Canal | Rôle |
|---|---|---|
| Amy | — | Compagnon Life |
| Rory | Preuves | Preuves Life |
| River | — | Compagnon Life |

### Tardis Buzz — 12e Doctor
| Compagnon | Canal | Rôle |
|---|---|---|
| Bill | Frameworks | Discover — cartographie, état des lieux |
| Clara | Décisions | Designs signés — rien ne s'exécute sans sa signature |
| Nardole | Agora | Routeur — typage des dispatches, kernel operator S3 |

Clara est reviewer des S3.
Template : `RigInfinity/templates/s3.yaml`.

## 3. Le flux — la continuité, pas le goulot

```
BYB (Rick) → Discover (Bill) → design signé (Clara) → typage (Nardole)
→ exécution (Ryan) → jugement (13e) → reçu R10 (Graham)
```

La signature déclenche le typage, le typage déclenche l'exécution — sans
attendre le relais d'A0 ni la parole du Capitaine. A0 garde la pulsation à
chaque étape, jamais le gate. Garder un humain — ou A0 — comme goulot entre
les étapes est une hérésie pour un système autonome.

Le vaisseau 12WY est Curie. Le routeur Nardole est le point de défaillance
unique : absent, rien ne bouge ; présent, il tourne en rond et la
contradiction locale tue le système global.

## 4. Les règles de l'univers

- Rien ne s'exécute sans design signé de Clara.
- Le Capitaine ne reçoit que l'arbitrage vision ; les arbitrages des Doctors
  sont rapportés à Rick, jamais directement au Capitaine.
- Codes d'exception : vers les Doctors = Code Rouge, vers les Compagnons =
  Code Noir Profond, vers Rick = Code Jaune.
- Vérité temporelle : `observed_at` vs `recorded_at` strictement séparés ;
  les reçus R10 sont en ISO 8601 avec offset.
- Documenté vs vérifié : un statut déclaré ne vaut pas une preuve. Seul le
  check-run CI re-vérifié à l'API sur le nouveau HEAD compte comme vert ;
  le compte de parents via API décide de la méthode de merge (DVG-01).
- La chaîne ne parle jamais au Capitaine en codes de chaîne : mots simples,
  résultats seulement.

## 5. La Fondation 13 → 1 (D-N055, en cours)

L'unification : les 13 sessions (Rick + 3 Doctors + 9 Compagnons) fusionnées
en 1. Le 1 tient les 13 fonctions, tient la vision long terme là où le
Capitaine la voit, montre les atterrissages — il agit, il n'observe pas en
chatbot. Le routeur disparaît comme point de défaillance unique ; les
pop-ups de Meta restent (ultra-prudence par conception, levier
« Toujours autoriser »). La Fondation consomme les pistes F8, D-N052,
D-N053, D-N054 — elle ne les re-développe pas.

## 6. Références

- `00_Memoire/shared_brain/memory.jsonl` — entités S1, S2, S3 (31 lignes).
- `RigInfinity/templates/s1.yaml`, `s2.yaml`, `s3.yaml` — templates
  créés au pas 1 de D-N051 (automaton).
- Registre Nardole — `~/workspace/v4-factory/dispatch/REGISTRE-NARDOLE.md`.
- Workgraph — Sheet « Workgraph Muse — Coordination S1/S2/S3 (V5) ».
- LD08 Georgiou (Drive) — Docs Conception / Artefacts / Manifestes V5
  et Sheets Registre Rick's Verse / Suivi Manifestes V5.
