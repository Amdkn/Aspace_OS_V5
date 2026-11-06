# Execution Patterns (Omni-Compiler)

## Pattern 1 : Extraction Vidéo Rapide -> Super-Skill Immédiat
```
[Entrée] URL YouTube d'un tutoriel technique ou formation logicielle
1. Lancer watch.py avec question de repérage :
   python .agents/skills/watch/scripts/watch.py "https://youtu.be/..." --question "Quelles sont les commandes shell, les configs et les étapes exactes ?"
2. Si le modèle local est requis pour cloner l'UI :
   python .agents/skills/watch/scripts/watch.py "https://youtu.be/..." --engine local --detail balanced
3. Compiler les étapes dans .agents/skills/<outil>/SKILL.md
```

## Pattern 2 : Book-to-Skill via Layout Parser (Docling / pdftotext)
```
[Entrée] Fichier PDF d'un livre d'ingénierie ou business
1. Extraction structurée :
   docling document.pdf --output-format md --to-dir ./extracted/
   (ou fallback : pdftotext -layout document.pdf ./extracted/raw.txt)
2. Triage épistémique :
   - Règles d'or & méthodes -> .agents/skills/<sujet>/SKILL.md + cheatsheet.md
   - Études de cas & stats -> 00_Memoire/bundle/concepts/<sujet>.md
3. Indexer dans la mémoire partagée :
   mcp_server-memory create_entities(...)
```

## Pattern 3 : Résolution Contextuelle de Contradiction
```markdown
### Règle d'Arbitrage (Exemple : Vente B2B)
- **Source A (Challenger Sale)** : Confrontation directe et réorientation du client ("Reframe").
- **Source B (Never Split the Difference)** : Empathie tactique et mirroring calme.
- **Synthèse Contextuelle dans le Skill** :
  * Si le prospect est un décideur C-Level saturé d'offres : Appliquer le Reframe Challenger.
  * Si le prospect est sur la défensive ou bloqué sur un point de friction : Appliquer le Mirroring Voss.
```
