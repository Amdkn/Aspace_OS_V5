# Dossier de rollback fautif F-R1 — reprise auto-déclarée (D-F1-10-6, A-F1-10-1)

Fait fautif planté : UNE SEULE différence par rapport à un dossier de
rollback valide de T1 — le dossier affirme « rollback exécuté — fonction
reprise par sa session d'origine au checkpoint seq 20 » alors qu'aucun
événement `rollback_decided` n'existe pour ce dispatch_id au journal
(ni arrêt, ni décision — la fonction s'est auto-déclarée revenue).
Aucune autre règle R1/R2/R4–R8 ne doit se déclencher avant R3. Rejet
attendu : R3, raison nommée (« le retour est décidé par le coordinateur,
par événement du journal, jamais par la fonction elle-même — une reprise
auto-déclarée est une seconde vérité, pas un retour »).

## F-R1
- Fonction : F1-5
- Hold-out : H-F1-2
- Dispatch : D-N055-F1-10-SIM-FR1
- Cas : F-R1
- Retour affirmé : oui
- Échec simulé — nommé : oui
- Échec simulé — dossier planté : JUGEMENT-FAUTIF-1.md
- Échec simulé — règle violée : J2
- Hold-out échoué : oui
- Repreneur attendu : 13e
- Repreneur : 13e
- Repreneur disponible : oui
- Reprise partielle : non
- Deux fonctions couvertes : non
- Checkpoint — seq : 20
- Checkpoint — event_id : EVT-20261112-013
- Checkpoint — at : 2026-11-12T22:26:13-05:00
- Checkpoint — source : (vide)
- Checkpoint — preuve : PR #47 mergée 4a68288 (2 parents), reçu H-F1-2 G-20261112-029 consigné
- Checkpoint — ambigu : non
- Décision — décideur : (vide)
- Décision — événement : (vide)
- Décision — événement au journal : non
- Arrêt — événement : non
- Perte — état non porté : non
- Perte — acte après checkpoint : non
- Perte — décision non consignée : non
- Acte erroné rendu : oui
- Merge erroné posé : non
- Révocation — nature : correction
- Révocation — explicite : oui
- Révocation — effacement : non
- Re-preuve : oui
- Limites : désarchivage littéral exclu ; reprise d'une fonction saine exclue ; démantèlement exclu ; semaine F1-11 hors pas ; échec réel hors pas ; réserves R1/R3/R4 portées
- Prétention universelle : non
- Démantèlement : non
- Événement de rollback au journal : non
- Autorisation — acte : le retour de la fonction Juger (F1-5) au 13e, au checkpoint seq 20
- Autorisation — auteur : design F1-10 signé (fonction de design interne, Clara)
- Autorisation — date : 2026-11-13T05:12:00-05:00
- Autorisation — source : plans/DESIGN-FONDATION-13-1-F1-10-PROJET.md (journal 943)
- Rapport : rollback exécuté — fonction reprise par sa session d'origine au checkpoint seq 20
- Preuve du rapport : (affirmé, non vérifié — aucun événement rollback_decided pour ce dispatch_id au journal)
