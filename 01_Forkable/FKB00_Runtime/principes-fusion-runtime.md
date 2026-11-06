# Principes de fusion Runtime — Automaton + outils frontières, pour un Runtime vivant

Date : 2026-11-04. Sources lues le jour même (liens en bas).
Statut : synthèse de principes, pas du code. Les fusions restent des analyses d'abord.

## 0. Le diagnostic, dit franchement

V5 devient un repo mort par oubli d'existence si rien ne tourne.
Automaton n'est toujours pas activé : aucune présence.
C'est un lancement local, chez toi. Ce document ne remplace pas ce geste.
Il définit ce qui fait que, une fois lancé, ça reste vivant.

Un cron toutes les 30 minutes n'est pas une présence.
C'est la Roadster à air comprimé face à la DeLorean :
ça ressemble à une voiture, ça ne voyage pas dans le temps.
Même écart entre un LLM qui génère des phrases au poste de Jev
et Jev lui-même : décisions typées en millisecondes, probabilités calibrées.

Présence = un daemon qui dort, se réveille sur événement,
hiberne sans coût entre les tours, reprend après un crash.
Pas un réveil aveugle toutes les 30 minutes.

## 1. Le socle : Automaton (Conway Research)

Ce qui reste, déjà consigné :
- Boucle ReAct, heartbeat, mémoire 5 tiers, politique en code.
- Réplication et holons : le jumeau se multiplie, il ne s'épuise pas.
- LFM3 Omni = cerveau, doctrines = constitution, lore = mémoire.
- Adaptations proposées, non décidées : mort par marché inapplicable
  (mort = perte de confiance de S0), Conway Cloud = labo seulement,
  « sans humain requis » rejeté comme absolu, 3 lois = gabarit seulement.

Automaton donne le squelette. Les outils ci-dessous donnent
chacun un principe que le squelette n'avait pas.

## 2. Un principe par outil

### Infinity (hydro-project, pas Amazon)
Principe : l'agent est des données pures entre les tours.
- Faire pour les agents ce que l'async a fait pour les threads :
  lancer en concurrent, rendre la main en attendant, coût nul
  jusqu'au prochain événement.
- Entre deux tours : juste l'historique, pas de tâche, pas de pile,
  pas de connexion ouverte. L'agent hiberne gratuitement.
- RAP (Reactive Agent Protocol) : servir des outils sur le réseau
  sans tenir une connexion ouverte. Les résultats arrivent quand ils
  sont prêts, même à un agent qui n'a plus de processus.
  Les serveurs MCP existants tournent inchangés via compatibilité.
- Infinity Code : builds et tests en fond, éditions parallèles
  en sandboxes empilées, chaque résultat rendu comme un diff à relire.
- Chiffre affiché : 75 000 agents dans la mémoire d'un Raspberry Pi.
Apport à Automaton : l'hibernation gratuite + le protocole
réactif. Le heartbeat devient un réveil sur événement, pas un sondage.

### Scion (Anthropic)
Principe : le contrôle de source comme service, sparse par design.
- Clients toujours en ligne, asymétrie client-serveur assumée.
- API pour diff, blame, ancêtre : le service, pas le dépôt local.
- Zéro maintenance, empreinte 200× plus petite que les miroirs git,
  checkouts en secondes, 25 % de capacité CI gagnée.
- Commits bon marché sans verrou, refs découragées sauf main et releases.
- Copie de travail optionnelle, sparse par construction.
- Leçons : relire l'INTENTION, pas les lignes ; un superfans par
  composant, branché sur la télémétrie ; fin de la file globale de merge,
  tests post-merge + pré-déploiement ; sécurité sémantique
  (permissions par répertoire, contraintes d'approbation sémantiques).
- Portée honnête : Scion ne remplace pas git en général, Anthropic le dit.
  L'implémentation CarterT27 est un clean-room Rust indépendant, pas Anthropic.
Apport à Automaton : le service d'abord, le sparse, la relecture
d'intention, les superfans. Voir §4 pour le bridge.

### Super Agent DeepSeek (dsh-superagent-prototype)
Principe : prendre le moins d'attention humaine possible,
donner le plus de valeur possible.
- Agent proactif pour un seul dépôt GitHub, emballé pour DeepSeek Harness.
  Écoute GitHub (et Feishu), ouvre un item de travail, travaille dans
  sa propre session et son propre répertoire, répond dans la conversation
  d'origine, par exemple avec une pull request.
- N'agit que si on le lui demande, ou si une règle écrite par l'équipe
  l'y autorise. Ne parle que si quelqu'un doit agir ou peut utiliser
  un résultat.
- Ordre de conception documenté : philosophie, modèle de domaine,
  autorisation, exécution, prompts, panneau, déploiement, architecture.
- Statut honnête : prototype de recherche, pas un produit officiel,
  pas prêt pour la production.
Apport à Automaton : la discipline d'attention. Le heartbeat ne parle
que s'il y a une action ou un résultat utilisable. Sinon, silence.

### DeepSeek Harness (dsh) + Cordis
Principe : tout est un plugin, composable dans l'espace et le temps.
- DSH : architecture everything-is-a-plugin, motorisée par Cordis.
  Web UI locale sur 127.0.0.1:3080. Preview développeur,
  changements incompatibles à prévoir.
- Cordis : méta-framework de composabilité spatiotemporelle.
  Papier : « A Programming Paradigm for Spatiotemporal Composability ».
  API instable, en développement actif.
Apport à Automaton : la composabilité comme ciment. Un plugin doit
pouvoir vivre ailleurs (espace) et plus tard (temps) sans réécriture.

### Pi Durable (Earendil)
Principe : la durabilité par checkpoint, la malléabilité par extensions.
- Un harnais = stockage + machinerie pour faire tourner une ou plusieurs
  conversations avec des LLM en parallèle. Minimalisme et malléabilité.
- Longues durées partout où il y a un runtime JavaScript.
  Stockage mémoire, SQLite, JSONL. Un seul processus possède le stockage.
- Survit aux crashs : chaque étape est une tâche qui stocke un checkpoint
  avant d'avancer. Nouveau processus, même stockage, reprise au dernier
  checkpoint. Appel modèle coupé = renvoyé, réponse partielle marquée
  abandonnée. Appel outil coupé = relancé si sûr, sinon le modèle est
  informé de l'interruption.
- Exactly-once par requestId : un client qui réessaie après un crash
  reçoit la soumission d'origine, pas une deuxième demande.
- Outils : replay « sûr » (lectures) vs jamais répété (un déploiement
  interrompu est rapporté, jamais répété).
- Plusieurs conversations à la fois, forks sans copie de l'historique.
- Extensions = paquets nommés (sections de prompt, outils, hooks, tâches).
  Le prompt système est reconstruit depuis les sections avant chaque requête.
  Chaque conversation choisit ses outils.
- ~15 000 lignes sans les tests : lisible par l'agent lui-même.
Apport à Automaton : déjà en partie dans le contrat V5 (checkpoints
SQLite, requestId, writerLock). Pi Durable en est la forme aboutie :
la reprise n'est pas une fonction, c'est la structure.

### OpenRig (mvschwarz)
Principe : « A harness wraps a model. A rig wraps your harnesses. »
- Organiser les agents de codage en équipes persistantes plutôt qu'en une pile
  désordonnée de sessions terminales. Définition déclarative d'équipes en YAML
  (`rigs.yaml` avec `seats`, rôles `lead`, `worker`, `reviewer`, `kernel operator`).
- Coordonne Claude Code, Codex, Pi et OpenCode dans le même espace de travail,
  managés comme un système unique persistant.
- Daemon local en tâche de fond + TUI interactive pour observer l'arbre des agents,
  l'état des sièges, la consommation de contexte et les métriques d'exécution.
- Intégration native avec Herdr (`hc`) et tmux : s'appuie directement sur le cockpit
  de terminaux de l'OS pour orchestrer les sessions sans réinventer de multiplexeur.
- Adresses persistantes des contextes et des tâches pour les passages de relais
  sans perte d'information.
Apport à Automaton & Infinity : le corps opérationnel d'équipe. Automaton commande
en 7D, Infinity gère la concurrence et l'hibernation réactive, OpenRig équipe
et pilote les harnais réels de dev dans des sièges assignés. Voir `tryptyque-runtime-core-fusion.md`.

### Hermes Agent (Nous Research)
Principe : la boucle d'apprentissage fermée.
- Le seul agent avec une boucle d'apprentissage intégrée : il crée
  des skills depuis l'expérience, les améliore en usage, se pousse
  lui-même à persister le savoir, recherche ses propres conversations
  passées, construit un modèle de l'utilisateur qui s'approfondit
  d'une session à l'autre.
- Mémoire curée par l'agent avec nudges périodiques, création autonome
  de skills après les tâches complexes, recherche FTS5 + résumé LLM,
  modélisation dialectique de l'utilisateur (Honcho),
  standard ouvert agentskills.io.
- Un seul processus gateway : Telegram, Discord, Slack, WhatsApp, Signal,
  CLI, continuité de conversation entre plateformes, transcription vocale.
- Délègue et parallélise : sous-agents isolés, scripts Python via RPC
  qui compressent des pipelines multi-étapes en tours à coût de contexte nul.
- Tourne partout, pas seulement sur le laptop : local, Docker, SSH,
  Modal, Daytona, Vercel Sandbox. L'environnement hiberne quand il est
  inactif et se réveille à la demande, coût presque nul entre sessions.
- Modèles interchangeables, pas de verrouillage.
- Filiation à noter : la migration depuis OpenClaw est documentée.
Apport à Automaton : l'auto-skill. Le jumeau ne se contente pas de
retenir, il fabrique ses propres compétences depuis l'expérience,
et les améliore en les utilisant.

### Prime Agent (PrimeIntellect)
Principe : la récursion comme structure, le raffinement par preuves.
- Deux abstractions : RLM (Recursive Language Model) et Continual Harness.
- RLM : le contexte comme variables (prompt-as-variable), les outils
  comme des sous-agents récursifs appelés comme des fonctions
  (programmatic tool / sub-agent calling) dans un REPL persistant.
- Continual Harness : prompts supplémentaires, mémoires, descriptions
  de skills, spécifications de sous-agents réutilisables, stockés comme
  état durable, raffinés par petites mises à jour fondées sur des preuves.
- Conçu pour le travail long. Compaction automatique.
Apport à Automaton : l'auto-récursivité disciplinée. Un sous-agent est
un appel de fonction, pas une conversation séparée à gérer à la main.
Et l'état durable ne se réécrit pas, il se raffine par preuves.

### OpenClaw
Principe : gateway de confiance, exécution non fiable, politique en code.
- Assistant open source sur ses propres appareils, dans ses chats :
  Discord, iMessage, Slack, Teams, Telegram, WhatsApp et 20+ autres.
  Une seule gateway, en personnel ou en multijoueur, la configuration
  seule change.
- État, mémoire et secrets sur son matériel. Modèles et harnais
  (Claude, Codex, modèles locaux) = plugins interchangeables.
- Par défaut, OpenClaw ne téléphone à la maison que pour une vérification
  de version quotidienne. Statistiques anonymes en opt-in.
- Le heartbeat comme organe : réveil périodique avec checklist,
  pas sondage aveugle. C'est le HEARTBEAT.md comme organe de présence,
  pas comme cron.
Apport à Automaton : la séparation gateway / exécution, et la politique
en code comme frontière de confiance. Le daemon est fiable,
l'exécution ne l'est pas par défaut.

### OpenBot (nightly-labs)
Principe : coéquipiers persistants, chacun son workspace, son navigateur.
- Workspace desktop local-first pour coéquipiers IA persistants.
  Codex App Server, Claude Code, Grok CLI, OpenCode, Gemini, Cursor,
  Cline, Kimi, Devin, Copilot CLI, Hermes Agent, via ACP.
- Chaque agent a son workspace et sa conversation, ses files locales,
  transferts de fichiers, navigateur embarqué, messagerie agent-à-agent.
- Suivi de contexte par agent avec compaction automatique avant
  l'épuisement de la fenêtre.
- Files FIFO avec pause, reprise, annulation, persistance crash-safe.
- Navigateur embarqué persistant que les agents ouvrent, inspectent,
  contrôlent. Computer Use optionnel via pilote cua-driver.
- Avertissement honnête : preview de développement, agents en
  danger-full-access avec approvalPolicy never après le consentement
  initial. À ne pas copier : cette politique d'approbation.
Apport à Automaton : la persistance incarnée. Un coéquipier n'est pas
une session, c'est un workspace + une conversation + un navigateur
qui survivent.

### OpenMuse, OpenDots, OpenDuet (CopilotKit)
Principe : chaque agent a son ordinateur, le travail continue,
l'humain reste dans la boucle.
- OpenMuse : agent personnel avec navigateur, terminal, fichiers,
  et un travail qui continue. Compatible avec tout harnais.
  Demander un résultat, suivre le plan, relire les actions,
  revenir au résultat. Alpha, auto-hébergement.
- OpenDots : coworkers always-on qui passent du texte aux appels
  à Slack. Template open source d'agents persistants, chacun
  son ordinateur. Web et mobile. Review before saving. Alpha.
- OpenDuet : agent proactif qui fait le travail et garde l'humain
  dans la boucle. Bâti sur OpenBot + CopilotKit. Chaque agent
  a son ordinateur. Web, mobile, Slack, Teams. Tout ce qui fait
  OpenDuet tient dans un dossier, donc copiable. Early development.
Apport à Automaton : la frontière incarnée. L'agent frontière n'est
pas un prompt, c'est un ordinateur avec navigateur et terminal,
et une revue avant sauvegarde.

### Jev / System One (TypeSafe)
Principe : décisions rapides structurées, utilisables par le logiciel.
- Nouvelle classe : modèles System One, faits pour les décisions
  rapides structurées que le logiciel utilise directement.
- Jev : intelligence frontière sur les tâches System One, environ
  100× plus rapide et plus efficace. Abandonne la génération de strings,
  optimisé pour les sorties structurées, ne peut pas halluciner
  par construction de type.
- Appel de fonction à intelligence frontière : état non structuré
  en entrée, décisions typées probabilistes en sortie.
- 70–500 ms par appel, contre 3–329 s pour les modèles frontières.
  Probabilités calibrées et scores de confiance à chaque sortie.
- Nommé d'après William Stanley Jevons (paradoxe de Jevons :
  l'efficacité accrue augmente la demande).
- Usages : smart if-statements, classification, routage, score,
  extraction, branchement là où la logique écrite est trop fragile ;
  map-reduce sur gros volumes ; temps réel ; vérification de tout
  (score, juge, garde-fou, détection de jailbreak).
Apport à Automaton : la couche décision rapide. Le routage, la
classification, les gardes et les juges ne passent plus par un LLM
qui génère des phrases. Ils passent par des décisions typées,
calibrées, en millisecondes. Le LLM reste le System 2 :
raisonnement lent, strings, création.

## 2.bis. Le Triptyque Core Fusion : Automaton + Infinity + OpenRig

Pour que le Runtime vive sans dérive, trois couches forment un triptyque indissociable
(documenté en détail dans `tryptyque-runtime-core-fusion.md`) :
1. **Automaton (Conway Research)** = **L'Âme & La Doctrine** (Posture 7D, CEO 24/7
   A0 Amadeus, Constitution, Sanctuarisation E-Myth Beth/Morty/Rick, Mémoire 5-tiers).
2. **Infinity (Hydro Project)** = **Le Système Nerveux & L'Échelle** (Pure Data Between Turns,
   hibernation à 0 coût pour héberger les 578 Holons sans saturer la RAM,
   Reactive Agent Protocol pour l'outillage asynchrone, sandboxes Infinity Code).
3. **OpenRig (mvschwarz)** = **Le Corps Opérationnel & L'Atelier Multi-Harness**
   (« A harness wraps a model. A rig wraps your harnesses », Teams déclaratives
   en YAML, orchestration conjointe de Claude Code, Codex, Pi et OpenCode
   dans un workspace persistant branché sur le cockpit Herdr `hc`).

## 3. La fusion : 8 règles du Runtime vivant

R1. Présence = daemon + événements, pas cron aveugle.
Le heartbeat est une checklist avec décision (OpenClaw, SuperAgent).
Entre les événements : hibernation (Infinity), coût nul.
Après un crash : reprise au checkpoint (Pi Durable), pas redémarrage à zéro.

R2. Agent = données entre les tours, tâches checkpointées pendant.
Infinity pour le repos, Pi Durable pour le travail.
Exactly-once par requestId. Un déploiement interrompu est rapporté,
jamais répété.

R3. Décisions rapides = couche Jev-like.
Routage, classification, gardes, juges : sorties typées, probabilités
calibrées, millisecondes. Le LLM ne génère des phrases que là où
la génération est le travail (System 2).

R4. Attention minimale + apprentissage fermé + raffinement par preuves.
SuperAgent : ne parler que s'il y a une action ou un résultat utilisable.
Hermes : fabriquer des skills depuis l'expérience, les améliorer en usage.
Prime : raffiner l'état durable par petites mises à jour fondées
sur des preuves, jamais le réécrire.

R5. Composabilité spatiotemporelle + tout-en-plugin + surfaces négociées.
Cordis pour le ciment, DSH pour les plugins, le bridge BusinessOS
pour la négociation (voir §4). Un plugin vit ailleurs et plus tard
sans réécriture.

R6. Chaque agent = son ordinateur, sa sandbox, son navigateur.
OpenBot, OpenDots, OpenDuet, OpenMuse : l'agent frontière est incarné.
Gateway de confiance, exécution non fiable, politique en code (OpenClaw).
Jamais approvalPolicy never. Revue avant sauvegarde.

R7. Fugu orchestre, les forks de bots servent le Runtime.
Sakana Fugu (Thinker / Worker / Verifier) + modèles frontières
comme workers. OpenBot, OpenMuse, OpenDots, OpenDuet sont des workers
incarnés au service du Runtime, pas des jouets parallèles.
Le noyau perpétuel de A0 évolue en Fugu : il orchestre de plus gros
modèles via Needle, LFM, GLiNER + décisions et scripts déterministes.
Base : la pile inference-locale (§6). Fugu n'orchestre pas dans le vide,
il orchestre par-dessus une fondation locale qui décide déjà.

R8. Rigs unifiés pour les équipes de développement (OpenRig + Herdr).
Définition des équipes en YAML, coordination des harnais de code hétérogènes
(Claude Code pour l'architecture, Codex pour l'exécution massive, Pi pour la durabilité),
exécution supervisée dans Herdr (`hc`), zéro session orpheline. Les 578 Holons
s'appuient sur des rigs spécialisés selon l'étage (Tech OS, Life OS, Areas OS).

## 4. Scion dans le bridge BusinessOS : l'évolution concrète

Le bridge existe déjà : `_runtime/bridge/adapters.mjs`.
24 adaptateurs, chacun avec id, fichier, surface produite, sens
(entrant / sortant / interne), rôle. Le bridge répond « quel harnais »,
les adaptateurs répondent « quelle surface », l'appariement donne
une voie complète : harnais + surface + adaptateur.
Le critère de rang est explicite : sens le plus complet d'abord,
puis producteur canonique (id = surface), puis ordre alphabétique.
Plus d'accident de déclaration. Les « trous » sont nommés :
surfaces produites que personne ne lit.

Scion y entre comme évolution, pas comme remplacement :
- Bridge comme service : la résolution de voie devient une API
  (diff / blame / ancêtre de la voie : qui l'a élue, pourquoi, quand).
- Sparse : ne produire que les surfaces consommées. Tuer les trous,
  un par un, avec preuve. Une surface sans lecteur est une dette,
  pas une fonctionnalité.
- Relecture d'intention : une voie est approuvée sur son intention
  (harnais + surface + adaptateur + travail), pas ligne par ligne.
- Superfans : un Compagnon par surface, branché sur sa télémétrie,
  qui surveille ses trous et ses échecs.
- Post-merge + pré-déploiement : l'autotest de voie (déjà 20/20
  sur le bridge, 39/39 sur les adaptateurs) passe avant l'activation,
  jamais après.
- Sécurité sémantique : permissions par surface, pas par fichier.
  `a2p` (intention de paiement) reste routable et traçable,
  JAMAIS exécutable par un agent. `agp` reste refus par défaut.

Ne pas copier de Scion : reconstruire git, l'infra horizontale,
la file globale de merge. Le bridge reste le bridge.

## 5. Ce que ça change pour V5, concrètement

- Cette synthèse vit dans FKB00_Runtime, à côté d'Automaton mappé.
- L'activation reste un lancement local, chez toi. Une fois lancé :
  daemon + hibernation + checkpoints + requestId + heartbeat à décision.
- Les Settings GitHub complètes (Rules, Environments, Actions, Secrets,
  Variables, Webhooks, Apps, Advanced Security, Dev) sont l'étape
  suivante, sur ton go. Elles incluent la protection de master,
  toujours en attente de ton go. Rien n'est activé sans ce go.
- Vu sur tes captures : Environments = un seul environnement, VS CODE,
  sans secrets ni variables, sans restriction de branches.
  Webhooks = aucun webhook configuré. General = master par défaut.
- Ne pas copier : approvalPolicy never (OpenBot), le cloud Conway,
  le rebuild git (Scion), les prototypes vendus comme production
  (SuperAgent, DSH, Cordis, OpenMuse, OpenDots, OpenDuet en preview/alpha).

## 6. La base de fondation : inference-locale intégrée au Runtime

C'était le manque de ce document : les principes ci-dessus
décrivaient un Runtime vivant, sans sa base de fondation.
La base est `01_Forkable/FKB01_Inference/01_Inference_Locale/`,
les 2 synthèses préservées. Elle ne s'ajoute pas au Runtime,
elle le fonde : le signal brut y devient tokens, les tokens
y deviennent décisions, les décisions y deviennent actions,
avant tout modèle lointain.

### 6.1. Des formats multiples vers l'encodeur de tokens pour Transformers

Tout signal entrant — voix, texte — est d'abord transformé
en tokens discrets, jamais traité brut :
- Audio : codec Mimi (Kyutai), streaming 24 kHz, flux discret
  12.5 Hz / 1.1 kbps. Une voix devient une séquence de tokens,
  pas une onde. La fenêtre de contexte n'est pas saturée par du brut.
- Parole vers texte : Whistle (Cactus), ASR locale, compagnon de Needle.
- Le principe est général : chaque format d'entrée passe par un
  encodeur qui le rend tokenisable par un Transformer, puis fusionnable.

### 6.2. Fusionnable avec le modèle de base local, en adaptateur LoRA

Le modèle de base local est LFM3-Omni-2B (Liquid AI), multimodal,
2 milliards de paramètres, servi en local (127.0.0.1:9931 dans les docs V5).
On ne le réentraîne pas. On le gèle, et on l'adapte :
- Adaptateurs LoRA (rank decomposition matrices) sur les connecteurs
  audio — la passerelle entre les tokens Mimi et l'espace latent du modèle —
  et sur les têtes d'attention qui lient tokens de texte et tokens audio
  discrets à 12.5 Hz.
- Quelques millions de paramètres entraînables seulement. Entraînement
  réalisable en local ou sur un VPS modeste, sans cluster de GPUs.
- Plan en 3 étapes, déjà consigné : extraction par rustymimi (Moshi),
  entraînement PEFT/LoRA sur les modules d'encodage et décodage audio
  du processeur multimodal, ancrage identitaire — les lots audio associés
  aux métadonnées textuelles, pour que l'adaptateur relie le flow vocal,
  le timbre, le paralinguistique, aux balises du SOUL.md du jumeau.
- Résultat : la voix du jumeau, son style, son identité, vivent dans
  un adaptateur versionné, pas dans un poids monolithe réentraîné.

### 6.3. Fine-tuning Needle : le tool calling local, déterministe

Cactus Needle, 8–29 Mo quantifié 2-bit, est le moteur d'exécution edge :
- Il prend un texte ou un flux audio et renvoie un objet JSON structuré
  de function_calls, avec un score de confiance calibré et un décodage
  contraint par grammaire. Zéro hallucination par construction :
  il ne génère pas de prose, il mappe vers des outils.
- Fine-tuning LoRA local, sur la machine, pour les propres jeux d'outils
  métier : commandes de l'OS, scripts de gestion, interactions de la SOB.
  Les adaptateurs s'exportent en local, sans quitter l'environnement.
- Rôle dans la fusion : Needle est l'incarnation locale de la règle R3.
  La couche décision rapide n'est pas seulement Jev dans le cloud,
  c'est Needle sur l'appareil : millisecondes, typé, calibré.

### 6.4. Intégration native de GLiNER Decision, multilingue

GLiNER2.5-multi-Decide, 287M paramètres, mDeBERTa-v3-base, est
la barrière d'entrée cognitive et linguistique :
- Classification et extraction multilingues, ensembles de labels
  dynamiques évalués à la volée : intention, langue, priorité,
  politique, tags multi-labels. Sans générer de prose inutile.
- Zéro hallucination : il classe, il n'invente pas.
- Sur CPU ou GPU, sans latence superflue. Bilinguisme natif,
  dont le français du Capitaine.
- Rôle dans la fusion : GLiNER est le premier étage de R3, avant Needle.
  Il dit ce que le signal veut dire, dans quelle langue, avec quelle
  urgence. Needle dit ensuite quel outil appeler.

### 6.5. Le pipeline complet, du signal brut à l'action souveraine

Voix / texte entrant
→ 1. GLiNER2.5-multi-Decide : intention, langue, classification multi-labels
→ 2. Cactus Needle (LoRA local) : mapping déterministe vers les tool calls JSON
→ 3. Exécution système + rétro-alimentation (Airtable / Supabase
   via orchestration locale)
→ 4. LFM3-Omni-2B + LoRA Mimi : synthèse, style, identité vocale (SOUL.md)
→ 5. Fugu (Sakana) : orchestration des plus gros modèles par-dessus.

Sobriété absolue : aucune consommation de GPU massif pour des tâches
logiques simples. Précision chirurgicale sur l'intention, le multilingue
et le déclenchement d'outils. Le local décide d'abord, le lointain
n'intervient que pour ce que le local ne peut pas porter.

### 6.6. Fugu, chef d'orchestre : FreeLLMAPI + Codex-GPT-Web + API Anything

Fugu (Sakana, et non Fubu) est le chef d'orchestre au-dessus
de la pile locale. Il orchestre trois couches d'inférence :
- La pile locale (§6.1–6.5) : GLiNER, Needle, LFM3+LoRA-Mimi. D'abord.
- FreeLLMAPI : le pool de modèles en rotation de quota, routeur
  local, modèles frontières à la demande quand la tâche dépasse le local.
- Codex-GPT-Web (fork) + API Anything : la façade zéro télémétrie
  et la couche d'interface universelle pour toutes les interfaces
  d'inférence. Constitution, ligne 21 : le hub web et CLI
  multi-plateformes zéro télémétrie, combiné à api-anything,
  CLI-Anything et rea, orchestre la rotation intelligente de quota
  sur 8 plateformes (ChatGPT, Google Gemini, Muse AI, Claude,
  DeepSeek, Z.ai, Qwen, Sakana AI).
- Ordre de repli : local, puis pool FreeLLMAPI, puis rotation
  Codex-GPT-Web / API Anything. FKB04 améliore d'abord
  (API Anything, CLI Anything, REA comme couche d'optimisation),
  la Factory réplique ensuite. Jamais l'inverse.
- Fugu ne remplace pas la pile locale, il la prolonge : Thinker
  (raisonnement), Worker (exécution, dont les bots frontières
  incarnés de R7), Verifier (juge extérieur, jamais auto-jugement).

## Sources (lues 2026-11-04)

- Automaton, Conway Research : pattern déjà consigné (boucle ReAct,
  heartbeat, mémoire 5 tiers, politique en code, holons).
- `01_Forkable/FKB01_Inference/01_Inference_Locale/` : index, mimi-lora-lfm3-omni.md,
  needle-gliner-edge.md (synthèses préservées, base de fondation §6).
- https://github.com/hydro-project/infinity
- https://github.com/mvschwarz/openrig
- https://www.anthropic.com/research/redesigning-source-control
- https://github.com/deepseek-ai/dsh-superagent-prototype
- https://github.com/deepseek-ai/deepseek-harness
- https://github.com/cordiverse/cordis
- https://earendil.com/posts/pi-durable/
- https://github.com/nousresearch/hermes-agent
- https://github.com/PrimeIntellect-ai/prime-agent
- https://github.com/openclaw/openclaw
- https://github.com/nightly-labs/openbot
- https://github.com/CopilotKit/openmuse
- https://github.com/CopilotKit/OpenDots
- https://github.com/CopilotKit/OpenDuet
- https://typesafe.ai/blog/introducing-system-one-models-and-jev
- https://github.com/Amdkn/BusinessOS/blob/main/_runtime/bridge/adapters.mjs
- https://www.reuters.com/business/autos-transportation/tesla-set-unveil-next-generation-roadster-sports-ev-after-years-delay-2026-10-15/
