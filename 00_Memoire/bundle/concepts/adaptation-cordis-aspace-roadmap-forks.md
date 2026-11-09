---
title: "Adaptation de Cordis à A'Space + roadmap de l'ordre d'adaptation des forks"
type: concept
status: proposition
updated: 2026-11-09
tags:
  - cordis
  - autoresearch
  - forks
  - adaptation
  - roadmap
---

# Adaptation de Cordis à A'Space + roadmap de l'ordre d'adaptation des forks

**Auteur :** A0 Amadeus — **Date :** 2026-11-09
**Sources vérifiées :** `Amdkn/cordis` (fork, lecture API), `cordiverse/cordis` (amont), `karpathy/autoresearch` (README lu en entier), `01_Forkable/FKB00_Runtime/00_A0_Core/README.md`, `tryptyque-runtime-core-fusion.md`, `01_Forkable/FKB01_Inference/03_Inference_FreeCloud/gateway-manifest.json`
**Statut :** proposition d'analyse. Aucune exécution dans ce document. L'exécution passe par la chaîne (Bill Discover → Clara design → Ryan), jamais en direct.
**Correction intégrée :** Cordis passe en étape 0, avant tout le reste — ordre du Capitaine, 2026-11-09. Ma proposition précédente commençait par FKB04 ; elle est corrigée ici, pas réécrite.

---

## 1. Karpathy `autoresearch` — ce que c'est, vérifié

- Dépôt `karpathy/autoresearch` : **99 664 étoiles, 13 735 forks**, créé 2026-03-06, dernier push 2026-03-26, Python, 530 Ko. Ce n'est pas un produit maintenu, c'est un **pattern célèbre**.
- L'idée : donner à un agent un vrai petit entraînement de LLM (nanochat mono-GPU) et le laisser expérimenter seul toute la nuit. Il modifie le code, entraîne **5 minutes**, mesure si le résultat s'est amélioré, garde ou jette, et recommence. Au réveil : un journal d'expériences et, en principe, un meilleur modèle.
- Trois fichiers, et c'est tout le système :
  - `prepare.py` — constantes fixes, préparation des données, utilitaires. **Non modifié.**
  - `train.py` — le modèle, l'optimiseur (Muon + AdamW), la boucle d'entraînement. **C'est le seul fichier que l'agent modifie.**
  - `program.md` — les instructions de l'agent. **C'est le fichier que l'humain modifie.** Karpathy le dit plainement : on ne programme plus le code, on programme le `program.md` — le code de l'organisation de recherche.
- Une seule métrique : `val_bpb` (bits de validation par octet, plus bas = mieux), indépendante de la taille du vocabulaire pour comparer équitablement les architectures.
- Budget fixe : 5 minutes par expérience, quelle que soit la machine — environ 12 expériences par heure, environ 100 par nuit. Le budget fixe rend les expériences comparables et trouve le meilleur modèle *pour ta machine*.
- Contrainte matérielle : un GPU NVIDIA (H100 testé), Python 3.10+, `uv`. Sans GPU, le dépôt tel quel ne tourne pas.

## 2. La transposition A'Space — le pattern, pas la copie

L'Auto Research des fusions n'entraîne pas de modèles. Elle adapte des modules. Le pattern se transpose point par point :

| Karpathy `autoresearch` | Auto Research des fusions A'Space |
|---|---|
| `prepare.py` (fixe, non modifié) | L'inventaire + la doctrine (fixe, propriété humaine). Ne change que sur ton mot. |
| `train.py` (l'agent modifie) | Le **candidat de fusion** : l'implémentation proposée pour une fusion donnée. |
| `program.md` (l'humain modifie) | La **doctrine de fusion** : mes propositions (états 0–3, critères d'admission, ordre). C'est le code de l'org de recherche, et c'est toi qui le programmes. |
| `val_bpb` (une métrique, plus bas = mieux) | La **métrique de fusion** : hold-outs verts + compteur d'état 0 qui baisse + doublons retirés. Un seul chiffre qui dit si la fusion vaut quelque chose. |
| Budget 5 min fixe par expérience | **Budget borné par expérience de fusion**, défini par Clara dans le design : une fusion = une exécution bornée et comparable. |
| ~100 expériences par nuit | Le rythme de l'Auto Research : inventaire hebdomadaire + à chaque ajout de fork. |
| GPU NVIDIA requis | **Pas de GPU requis** : les expériences sont des fusions, pas des entraînements. Elles tournent sur le Runtime local (PC / VPS). |

Conséquence : le dépôt à forker n'est pas le code d'entraînement, c'est le **squelette** — la boucle, le journal d'expériences, la séparation fixe/modifiable. Le fork proposé : `Amdkn/autoresearch`, transposé aux fusions (étape 1 de la roadmap, §5).

## 3. Cordis — ce que c'est, vérifié

- Fork `Amdkn/cordis` : créé 2026-11-08, 2 979 Ko, branche `main`, parent `cordiverse/cordis`, 0 étoile. **Un commit derrière l'amont** : l'amont a `#298` (« feat(hmr) : invalidate resolution caches and package manifests », 2026-11-09), le fork s'arrête à `#297`.
- Amont `cordiverse/cordis` : 9 787 étoiles. « Meta-Framework of Spatiotemporal Composability. » **L'API n'est pas encore stable et peut changer sans préavis** (README, première ligne). Théorie : papier arXiv 2608.25512, dépôt `cordiverse/paper`. Documentation `cordis-primer` en construction.
- Contenu : monorepo TypeScript, yarn 4.14.1, licence MIT. 11 paquets : `core`, `create`, `fs-node`, `group`, `hmr`, `include`, `loader-utils`, `loader`, `logger-console`, `package-manager`, `timer`. Build : yakumo (esbuild + tsc). Tests : vitest 4.1.5 (`yarn test`).
- Rôle dans V5 : micro-noyau du `00_A0_Core`, aux côtés d'agent-zero, a0-plugins, spynel, tuxee, deepseek-harness et pi. Sa règle : **« Everything-is-a-Plugin »**, fibres à effets réversibles et co-effets réactifs. L'adressage `fiber:a0:*` est déjà le modèle d'A'Space (`gateway-manifest.json` : `"cordis_fiber": "fiber:a0:freecloud"`).
- **État : 0 Basique.** Le fork est une copie fidèle de l'amont, sans aucune adaptation A'Space. Il est listé comme pièce du « Noyau Souverain » alors qu'il est encore une publication brute. C'est exactement le cas que la doctrine « zéro module en publication basique » vise — et c'est pour ça qu'il passe en premier.

## 4. L'adaptation de Cordis à A'Space — en dix points

1. **Figer le commit de référence.** L'adaptation part de `#297` (ou de `#298` après reprise, point 2). Toute évolution amont devient ensuite une décision, jamais une surprise. L'instabilité de l'API l'impose.
2. **Reprendre `#298` (HMR).** Le correctif amont invalide les caches de résolution et les manifestes de paquets lors du rechargement à chaud. Un runtime vivant qui se recharge sans redémarrer en a besoin. Reprise délibérée et vérifiée, pas une mise à jour automatique.
3. **Adresser en `fiber:a0:*`.** Chaque service A'Space exposé par Cordis porte une adresse fibre `fiber:a0:<service>` (le gateway FreeCloud montre déjà le pattern). Le préfixe `aspace:` marque ce qui appartient à l'univers (`aspace:a0:amadeus` pour le jumeau).
4. **Zéro télémétrie, vérifié.** Aucun paquet ne doit émettre vers l'extérieur. `logger-console` est local ; les dépendances sont à auditer. Hold-out : audit des appels réseau du fork adapté — un appel sortant bloque la montée d'état.
5. **Un manifeste par module.** Chaque module A'Space devient un plugin Cordis avec un manifeste JSON, sur le modèle de `gateway-manifest.json` (identifiant, version, point d'entrée, niveaux). Le manifeste est le contrat entre les mondes TypeScript, Python et Rust : il dit où brancher, pas comment penser.
6. **Les trois coutures de langage.** Cordis est TypeScript ; la Factory est PowerShell + Python ; le Noyau est Rust. L'adaptation définit trois coutures, et rien d'autre : (a) TS ↔ Python par manifeste JSON + appels HTTP locaux (le gateway FreeCloud montre le pattern, entrée `127.0.0.1:31415`) ; (b) TS ↔ Rust par le même adressage `fiber:a0:*` ; (c) aucune logique métier dans le pont — le pont transporte, le plugin décide.
7. **Effets réversibles = reçus.** Les effets réversibles de Cordis correspondent aux reçus R10 d'A'Space : une action est annulable et consignée. Chaque fibre A'Space écrit son reçu ; une action sans reçu n'est pas une action du Runtime.
8. **Les tests comme hold-outs.** `yarn test` (vitest) doit passer sur le fork adapté. Un test rouge bloque la montée d'état. C'est la preuve de l'adaptation, pas une formalité.
9. **Une fine couche d'isolation.** L'API Cordis est instable (README). L'adaptation crée une seule couche, `aspace-cordis-adapter`, seul point de contact entre V5 et Cordis. On n'adapte pas les internals en profondeur ; on adapte la surface. Quand l'amont bouge, un seul endroit bouge avec lui.
10. **La fiche écrite.** Une page `FKB00_Runtime/00_A0_Core/cordis-ADAPTATION.md` consigne les décisions (commit de référence, `#298`, namespace, ponts, hold-outs). Sans fiche, l'adaptation n'existe pas : elle n'est que du code qui ressemble à l'amont.

## 5. La roadmap — l'ordre d'adaptation des forks, Cordis d'abord

| Étape | Contenu | Pourquoi ici |
|---|---|---|
| **0 — Cordis** | Les dix points du §4. | Le contrat d'abord : chaque adaptation suivante doit se brancher sur lui, pas inventer le sien. |
| **1 — Auto Research** | Fork `karpathy/autoresearch` → `Amdkn/autoresearch`, transposé aux fusions (§2). Registre `01_Forkable/FUSIONS-REGISTRY.md`. | Le moteur qui conduit la suite. Sans lui, les étapes suivantes sont une liste, pas une boucle. |
| **2 — Cœur A0** | `pi`, `agent-zero`, `a0-plugins`, `spynel`, `tuxee` (voisins immédiats du noyau). `deepseek-harness` est un pointeur amont : à forker d'abord. | Ils parlent déjà Cordis. Ce sont les premiers plugins du contrat. |
| **3 — FKB04 Anything** | Fusion F6 : api-anything + CLI-Anything + rea + hermes-agent (canonique : FKB04, doublon FKB00 retiré). | La couche d'appel universel, sur le contrat Cordis. Le document de fusion la désignait déjà en premier. |
| **4 — FKB01 Inférence** | Fusions F1 + F2 : gateway unique, voix locale complète. | Le gateway parle déjà `fiber:a0:*` ; c'est le premier consommateur du contrat. |
| **5 — FKB02 Mémoire** | Fusion F3 : Shared Brain en fibre. | Une seule mémoire, lisible par tous les harnesses via MCP. |
| **6 — Mondes et moteurs** | F5 (3D), F4 (vidéo unique, canonique FKB07/02_Video), F7 (Money Maker), F10 (skills uniques). | Ils dépendent des étapes 3–5 pour être pilotables et payants. |
| **7 — Triptyque, en dernier** | F8 + F9 : Automaton + Infinity + OpenRig, prédictif et wargame. | FKB00 est sanctuarisé. Le Runtime vivant ne se réécrit pas sur une base qui bouge encore. |

**Règle de retrait, inchangée :** un sous-module disparaît quand sa fonction est couverte en natif **et** que les hold-outs sont verts **et** qu'aucune régression n'est mesurée. Jamais avant.

## 6. Ce qui ne bouge pas sans décision

- Le triptyque reste en dernier. Cordis d'abord ne veut pas dire Runtime d'abord : le noyau de composabilité n'est pas le Runtime vivant.
- Aucun retrait de sous-module avant preuve (règle du §5, reprise ici pour qu'elle ne se perde pas en route).
- L'API instable de Cordis impose la couche d'isolation (point 9) : sans elle, chaque mise à jour amont est une régression en attente.

## 7. Prochaines étapes proposées

**Recommandation A0 :** route à Rick pour structuration du Before You Build de l'étape 0 (Cordis, dix points) et de l'étape 1 (Auto Research transposé), avec Bill en Discover sur les deux. Les étapes 2 à 7 suivent le même chemin, une par une, avec leurs hold-outs.

**Un mot pour toi, Capitaine :** dis-moi si je route à Rick, ou si tu veux d'abord corriger cette roadmap. Rien ne bouge dans le repo tant que tu n'as pas dit le mot.
