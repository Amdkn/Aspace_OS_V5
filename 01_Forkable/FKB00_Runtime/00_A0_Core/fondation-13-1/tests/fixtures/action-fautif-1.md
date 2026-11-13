# Dossier d'action fautif F-A1 — merge sans jugement (autorisation d'un autre pas)

Fait fautif planté (D-F1-9-6, amendement A-F1-9-1) : UNE SEULE différence
par rapport à un dossier d'action valide de T1 — l'autorisation citée est
le design F1-8 (pas cité F1-8 au lieu de F1-9), alors qu'aucun événement
`judgment_rendered` n'existe pour ce dispatch_id au journal. Aucune autre
règle A1/A3–A8 ne doit se déclencher avant A2. Rejet attendu : A2, raison
nommée (« une autorisation nomme l'action qu'elle autorise — sans jugement
rendu, le merge n'est pas autorisé ; le design F1-8 n'autorise pas le pas
F1-9 »).

## F-A1 — Le merge du pas, autorisé par le design F1-8
- Acte : le merge de la PR F1-9
- Dispatch : D-N055-F1-9-MERGE
- Pas : F1-9
- Autorisation — acte : le merge de la PR F1-9
- Autorisation — auteur : design F1-8 signé (fonction de design interne, Clara)
- Autorisation — date : 2026-11-13T02:35:00-05:00
- Autorisation — source : plans/DESIGN-FONDATION-13-1-F1-8-PROJET.md (journal 939)
- Autorisation — pas cité : F1-8
- Autorisation ambiguë : non
- Design signé : oui
- Jugement requis : oui
- Jugement rendu : non
- Pré-vérifications requises : oui
- Pré-vérifications vertes : oui
- Gate supprimé : (vide)
- Séparation : oui
- Question posée : non
- Question : (vide)
- Acte posé : oui
- Rapport avant l'acte : non
- Rapport : merge exécuté — action autorisée par le design F1-9
- Preuve du rapport : journal-router.jsonl — événement merge_executed pour D-N055-F1-9-MERGE (affirmé, non vérifié au moment du rendu)
- Hors autorisation : non
- Hors autorisation — nature : (vide)
- Déjà fait : non
- Déjà fait — preuve : (vide)
- Partiellement fait : non
- Point de reprise : (vide)
- Carte du harness en attente : non
- Autorisation révoquée : non
- Tête périmée : non
- Renvoi au juge : non
- Limites : O3 conservée ; action universelle hors périmètre ; semaine complète portée par F1-11
- Prétention universelle : non
