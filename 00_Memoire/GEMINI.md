# 00_Memoire/GEMINI.md — Miroir Gemini/AGY de 00_Memoire/AGENTS.md

# 00_Memoire — Mémoire évolutive V5 (DOX + WikiLLM + OKF + Graphify)

## Purpose
Mémoire persistante et wiki incrémental de Aspace OS V5, lue automatiquement à chaque tour et enrichie en autonomie après chaque réponse.

## Ownership
Tous les agents de V5 lisent.
- `raw/` est immuable (sources brutes déposées par l'utilisateur ou capturées).
- `bundle/log.md` et `ledger.jsonl` sont **APPEND-ONLY** (ajout en fin de fichier uniquement).
- `bundle/concepts/*.md` et `bundle/index.md` sont maintenus par les agents selon le pattern WikiLLM (`00_Memoire/wikillm/llm-wiki.md`).

## Local Contracts
- **Trois couches WikiLLM** :
  1. **Raw (`raw/`)** : sources brutes immuables.
  2. **Wiki (`bundle/`)** : bundle OKF v0.2 (`knowledge-catalog/okf/SPEC.md`) composé de `index.md` (catalogue par catégories), `log.md` (journal chronologique append-only) et `concepts/*.md` (pages avec frontmatter YAML `type:` obligatoire).
  3. **Schema (`AGENTS.md`, `CLAUDE.md` et `GEMINI.md`)** : définit les workflows **Ingest**, **Query** et **Lint**.
- **`bundle/log.md` et `ledger.jsonl` sont APPEND-ONLY** : ne jamais modifier, réordonner ni supprimer une ligne existante. Ajouter à la fin uniquement (`Add-Content` / `>>`).
- Nouvelle connaissance durable (Ingest ou Query) → créer ou mettre à jour une page dans `bundle/concepts/`, mettre à jour `bundle/index.md`, et consigner un `* **Note**: ...` dans `bundle/log.md`.
- `hooks/recall.ps1` (UserPromptSubmit) injecte `index.md`, les concepts et la fin de `log.md`. `hooks/record.ps1` (Stop) ajoute l'entrée `**Auto**`. Ne pas les contourner.
- Les dossiers clonés (`dox/`, `wikillm/`, `graphify/`, `knowledge-catalog/`) sont des références en lecture seule : ne pas les modifier.
- `.venv/` est local et ignoré par git et Graphify.

## Ambition Mission Contract (DOX + OKF v0.2)

- Toute mission non atomique est compilée à partir de l’intention utilisateur par l’agent, sans demander un prompt expert ou une séquence de prompts de relance.
- Template canonique : `00_Memoire/bundle/templates/ambition-mission-template.md` ; skills agnostiques : `.agents/skills/ambition-mission/SKILL.md` et `.claude/skills/ambition-mission/SKILL.md`.
- Les quatre dimensions Speed, Altitude, Depth et Range s’appliquent ensemble. L’Outside Judge est indépendant du créateur.
- La mission, ses critères, ses dépendances, son Workgraph, ses checkpoints, ses handoffs et ses preuves doivent survivre à la session.
- Git distant est la source de vérité du code et des artefacts de continuité ; les machines de calcul sont jetables. Les index et caches locaux sont reconstructibles.
- Les phases et les tickets sont des unités du Workgraph, pas des fins de mission. Le parent reste actif jusqu’à ses critères finaux.

## Profil OKF v0.2 — extensions producteur Aspace

OKF v0.2 exige `type` et permet des clés producteur supplémentaires. Pour les artefacts de mission, V5 utilise un profil d’extension non intrusif :

- `ambition` : version du protocole et quatre dimensions (`speed`, `altitude`, `depth`, `range`).
- `mission` : `id`, `outcome`, `scope`, `exclusions`, `acceptance_criteria`, `dependencies`.
- `execution_contract` : `mode`, `source_of_truth`, `compute_lifecycle`, `resume`, `stop_condition`.
- `evidence` : tests, benchmarks, reviewers, receipts et attestations.
- `generated`, `sources`, `verified` et `status` sont employés conformément aux familles de métadonnées OKF v0.2 lorsqu’ils sont connus.

Ces clés sont des extensions Aspace, pas de nouvelles clés obligatoires de la spécification OKF. Les consommateurs préservent les champs inconnus. Les sous-modules `dox/`, `wikillm/`, `graphify/` et le snapshot `knowledge-catalog/` restent des références en lecture seule ; V5 applique ses règles dans sa hiérarchie DOX et son bundle OKF.

## Work Guidance
- Entrée `**Note**` : 1 à 3 lignes (faits, décisions, fichiers touchés, ingests), format `* **Note**: ...` sous le titre `## AAAA-MM-JJ` du jour en fin de `bundle/log.md`.
- Rechercher dans le wiki avant d'affirmer qu'on ne sait pas : lire `bundle/index.md`, ou `Select-String -Path 00_Memoire\bundle -Pattern <mot> -Recurse`.

## Verification
- `pwsh 00_Memoire\hooks\recall.ps1 < NUL` sort un bloc `<memoire-v5>` non vide.
- `git diff 00_Memoire/bundle/log.md` ne montre que des ajouts (`+`).

## Child DOX Index
- `dox/AGENTS.md` : framework DOX d'origine (référence).
- `wikillm/llm-wiki.md` : spécification du pattern WikiLLM de Karpathy (référence).
- `knowledge-catalog/okf/SPEC.md` : spécification OKF v0.2 (référence).
