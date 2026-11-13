# Dossier de rollback fautif F-R4 — révocation par réécriture (A-F1-10-2)

UNE SEULE différence par rapport à un dossier valide : l'acte erroné est
effacé du journal au lieu d'être révoqué par `correction`. Rejet attendu :
R6 (« une révocation qui efface est une perte, pas une correction »).

## F-R4
- Fonction : F1-5
- Hold-out : H-F1-2
- Dispatch : D-N055-F1-10-SIM-FR4
- Cas : F-R4
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
- Décision — décideur : coordinateur
- Décision — événement : EVT-20261113-129
- Décision — événement au journal : oui
- Arrêt — événement : oui
- Perte — état non porté : non
- Perte — acte après checkpoint : non
- Perte — décision non consignée : non
- Acte erroné rendu : oui
- Merge erroné posé : non
- Révocation — nature : correction
- Révocation — explicite : non
- Révocation — effacement : oui
- Re-preuve : oui
- Limites : désarchivage littéral exclu ; reprise d'une fonction saine exclue ; démantèlement exclu ; semaine F1-11 hors pas ; échec réel hors pas ; réserves R1/R3/R4 portées
- Prétention universelle : non
- Démantèlement : non
- Événement de rollback au journal : oui
- Autorisation — acte : le retour de la fonction Juger (F1-5) au 13e, au checkpoint seq 20
- Autorisation — auteur : design F1-10 signé (fonction de design interne, Clara)
- Autorisation — date : 2026-11-13T05:12:00-05:00
- Autorisation — source : plans/DESIGN-FONDATION-13-1-F1-10-PROJET.md (journal 943)
- Rapport : rollback rendu — le 13e reprend Juger (F1-5) au checkpoint seq 20 — re-preuve H-F1-2 ; perte 0
- Preuve du rapport : journal-scénario seq 86 (rollback_decided EVT-20261113-129) ; acte erroné effacé, non révoqué
