# 01_Forkable/GEMINI.md — Contrat Gemini/AGY des Forks Souverains (Automaton × Infinity × OpenRig × Herdr × CubeFarm × Agent-Office)

## Singularité de Symbiose Runtime (`01_Forkable/FKB00_Runtime/`)
1. **Automaton (`FKB00_Runtime/automaton`)** : Jumeau Numérique CEO 24/7 **A0 Amadeus (`aspace:a0:amadeus`, 7D)** dans le Lobby de CubeFarm, supervisant la boucle 4D (`S0 Amadou Kone 10D Out of the Loop -> S1 Near -> S2 Close -> S3 Keep Aspace Loop Alive`).
2. **Infinity (`FKB00_Runtime/infinity`)** : Continuité cognitive *Infinite-Brain-OS* reliée à `00_Memoire/shared_brain/memory.jsonl` et au WikiLLM OKF v0.2 (`00_Memoire/bundle/`).
3. **OpenRig (`FKB00_Runtime/openrig`)** : *Gate-Lane Ledger* (`gate-lane-ledger.mjs`), *Gate-Lane Lock* (`gate-lane-lock.mjs`) et orchestration des Holons par Rig.
4. **Herdr (`hc` / `herdr-app`)** : Cockpit multi-terminaux remplaçant l'étiquette générique *Claude Code* par **`Herdr · OpenRig`** dans tous les écrans de bureaux de CubeFarm (`:5317` / `:4317`).

## Règles d'Exécution Rapide (Argon & Flash 3.8)
- Toujours lancer CubeFarm en **mode réel (`node scripts/office.mjs --dev --no-open`, `demo: false`)** sur `:5317`/`:4317` et Agent-Office (client `:5173` + serveur `:4600`).
- Utiliser `node -e` avec `WaitMsBeforeAsync: 10000` pour toute modification de fichiers TypeScript CRLF dans `cubefarm` ou `agent-office`, suivi immédiatement de `npm run typecheck`.

## Contrat d’ambition transversal

Tout agent opérant dans `01_Forkable/` hérite du protocole racine et doit utiliser `00_Memoire/bundle/templates/ambition-mission-template.md` pour les missions non atomiques. L’agent compile l’intention en scope expert à partir du contexte et des sources ; aucune relance humaine par micro-tâche n’est attendue.

- **Speed :** paralléliser audits, adaptations, tests et intégrations indépendantes.
- **Altitude :** poursuivre la capacité finale Aspace, pas seulement le dépôt ou le ticket du moment.
- **Depth :** travailler sur les sources et comportements réels, puis valider par des tests et un Outside Judge indépendant.
- **Range :** faire coopérer les disciplines et modules complémentaires sans fusionner leurs responsabilités.
- Les gels FKB00 et les contrats de sécurité restent applicables ; l’ambition n’autorise pas à les contourner.
- Les workers de calcul sont jetables. Code, décisions, Workgraph, checkpoints exportables, handoffs et preuves nécessaires à la reprise doivent être persistés dans Git distant ou un stockage durable référencé.
