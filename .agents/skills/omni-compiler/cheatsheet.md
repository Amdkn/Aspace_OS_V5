# Quick Decision Cheatsheet (Omni-Compiler)

## Matrice de Sélection d'Ingestion

| Type de Source | Moteur Recommandé | Commande / Outil | Sortie Produite |
|---|---|---|---|
| **Vidéo YouTube (Vue d'ensemble)** | Gemini Video Understanding | `watch.py <url> --question "..."` | Résumé horodaté à 0 token local |
| **Vidéo YouTube (Reproduction UI / Code)** | Local Keyframes + WhisperX | `watch.py <url> --engine local --detail balanced` | Frames I-Frame PNG + transcript horodaté |
| **Livre PDF (Texte simple)** | pdftotext CLI | `pdftotext -layout input.pdf text.txt` | Fichier texte brut sans overhead |
| **Livre PDF (Tableaux, formules, schémas)** | IBM Docling | `docling input.pdf --output-format md` | Markdown avec tableaux et arbres préservés |
| **Ouvrage indisponible en PDF** | Recherche Multi-Sources | 5 résumés écrits longs + 3 analyses vidéo | Synthèse croisée dedupliquée |

---

## Les 5 Archétypes Business en 1 Coup d'Œil

| Auteur / Ouvrage | Problème Résolu | Heuristique Clé |
|---|---|---|
| **Eugene Schwartz** (*Breakthrough Advertising*) | Message publicitaire inadapté | Ne jamais tenter de créer le désir ; canaliser un désir existant selon le niveau de conscience (1 à 5). |
| **Alex Hormozi** (*$100M Offers*) | Prix tiré vers le bas / marge faible | Maximiser le numérateur ($\text{Dream} \times \text{Certainty}$) et réduire à zéro le dénominateur ($\text{Time} \times \text{Effort}$). |
| **Adamson & Dixon** (*The Challenger Sale*) | Vente molle centrée relation | Ne pas demander ce dont le client a besoin ; lui apprendre ce qu'il ignore sur son propre marché. |
| **Blair Enns** (*Pricing Creativity*) | Vente au taux horaire / régie | Facturer la valeur perçue du résultat final ; proposer 3 options de prix déterministes. |
| **Chip & Dan Heath** (*Decisive*) | Biais de confirmation / complaisance IA | Appliquer WRAP systématiquement : Élargir les options, tester la réalité, prendre de la distance, anticiper l'erreur. |
