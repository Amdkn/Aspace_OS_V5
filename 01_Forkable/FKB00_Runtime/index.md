# FKB00_Runtime — Runtime du jumeau, noyau perpétuel de A0

## Sous-catégories

### Automaton (mappé)
- Emplacement : `01_Forkable/automaton` (non déplacé, voir FKB-INDEX).
- Rôle : Holon CEO 24/7, A0 Amadeus, constitution souveraine, heartbeat, mémoire.
- Ponts : `runAspaceFactoryCommand` vers 02_Factory, `readAspaceWikiPage` vers 00_Memoire.

### Harnesses
- Environnements de développement agentiques : DSH, Pi, OpenCode, Codex.
- Rôle : exécuter les agents sous le même contrat, avec failover de modèles.

### Agents-Durables
- Super agents durables : checkpoints, idempotence, reprise après interruption.
- Rôle : tenir la boucle 24/7 sans mourir à 0 crédit.

### Inference-Locale (dossier physique)
- Emplacement : `01_Forkable/FKB00_Runtime/inference-locale/`.
- Contenu : les 2 synthèses Gemini préservées (Mimi+LoRA, Needle+GLiNER) + pipeline cible.
- Cible : Fugu (Sakana) orchestrant de plus gros modèles via Needle, LFM, GLiNER
  + décisions et scripts déterministes.

### Noyau-Perpétuel-A0
- Le noyau qui doit lancer l'inférence locale et évoluer en Fugu.
- Règle : local d'abord, cloud en renfort, jamais l'inverse.
