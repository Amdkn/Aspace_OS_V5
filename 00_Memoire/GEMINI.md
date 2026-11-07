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
  3. **Schema (`AGENTS.md` + `CLAUDE.md`)** : définit les workflows **Ingest**, **Query** et **Lint**.
- **`bundle/log.md` et `ledger.jsonl` sont APPEND-ONLY** : ne jamais modifier, réordonner ni supprimer une ligne existante. Ajouter à la fin uniquement (`Add-Content` / `>>`).
- Nouvelle connaissance durable (Ingest ou Query) → créer ou mettre à jour une page dans `bundle/concepts/`, mettre à jour `bundle/index.md`, et consigner un `* **Note**: ...` dans `bundle/log.md`.
- `hooks/recall.ps1` (UserPromptSubmit) injecte `index.md`, les concepts et la fin de `log.md`. `hooks/record.ps1` (Stop) ajoute l'entrée `**Auto**`. Ne pas les contourner.
- Les dossiers clonés (`dox/`, `wikillm/`, `graphify/`, `knowledge-catalog/`) sont des références en lecture seule : ne pas les modifier.
- `.venv/` est local et ignoré par git et Graphify.

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
