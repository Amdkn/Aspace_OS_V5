---
name: pi-durable-subagents
description: Operate crash-safe, idempotent Durable Subagents (Pi Durable + pi-durable-subagents + DeepSeek Superagent) across ANY harness (Pi 1.5.0, DeepSeek dsh, Claude Code, OpenCode, Codex, Herdr, Orca).
---
# Pi Durable & Durable Subagents Skill (`pi-durable-subagents`)

Ce skill rend l'architecture **Pi Durable** (`https://earendil.com/posts/pi-durable/`) et **`pi-durable-subagents`** (`https://pi.dev/packages/pi-durable-subagents`) **100 % agnostique et exploitable par tous les agents et harnesses** d'Aspace OS V5 (`pi`, `dsh`, `dsh-superagent`, `claude`, `opencode`, `codex`, `agy`, `hc`, `orca`).

## 1. Les 6 Garanties Fondamentales (Pi Durable + `pi-durable-subagents`)

1. **Idempotence & Zéro Perte (`requestId` + Checkpoints SQLite)** :
   - Chaque tâche, appel d'outil ou workflow enregistre son intention et son `requestId` dans `factory/factory.sqlite` **avant** exécution.
   - Si un flux coupe, qu'un processus crashe ou que la machine redémarre, `resume` reprend exactement au dernier checkpoint sans jamais exécuter deux fois une étape terminée (`replay: "safe"` vs effets externes non rejouables).
2. **Verrou d'Écriture par Worktree (`writerLock`)** :
   - Un seul sous-agent écrivain (`writer: true`, utilisant `edit`/`write`) peut modifier un worktree Git donné à la fois (`waiting for writer lock: <root> held by <wid>/<key>`).
   - Les agents en lecture seule (`writer: false` : `reviewer-code`, `reviewer-security`, `reviewer-ux-ui`, `reviewer-drift`, `scout`) s'exécutent en parallèle sans attendre. Pour écrire en parallèle, isoler via `orca worktree create`.
3. **Bascule Automatique de Pool de Modèles (`modelPool` Failover)** :
   - En cas de limite de quota (`exhaustedPatterns`), l'exécution bascule **dans la même session** sur le modèle suivant du pool (`freellmapi/auto` → `claude-sonnet-4-5` → `qwen3.8-max` → `gemini-3.8-flash` → `deepseek-v4-flash`) et re-sonde le provider épuisé après 15 minutes.
4. **Hibernation sur Question (`person/answer`) & Réveil (`--wake caller`)** :
   - Un sous-agent qui pose une question libère son slot mémoire/modèle et hiberne dans SQLite jusqu'à réception de la réponse, puis reprend exactement une fois.
5. **Arbre de Propriété (`ownership: task | conversation | ownerless`) & Tâches de Fond (`background: true`)** :
   - Annuler une tâche parente annule ses enfants `foreground` de bas en haut (nettoyage propre).
   - Une tâche `background: true` (`hc run --bg --outlive-parent`) survit à la fin du tour et réveille l'appelant à sa complétion.
6. **État Applicatif Atomique (`defineDoc`) & Handoff sans Perte (`handoff` + `search_history`)** :
   - L'état applicatif (tickets, todos, specs, verrous) est commité atomiquement avec le transcript.
   - `handoff` démarre une fenêtre de contexte fraîche à partir d'une note de synthèse tout en gardant l'intégralité de l'historique interrogeable via `search_history`.

## 2. Utilisation Agnostique (depuis n'importe quel Agent ou Terminal)

```powershell
# Lister les agents, templates hc, harnesses et le pool de modèles
pwsh -NoProfile -File factory/factory.ps1 subagents -Action agents

# Lancer un sous-agent durable (idempotent via -RequestId, avec writerLock automatique)
pwsh -NoProfile -File factory/factory.ps1 subagents -Action run -Agent "builder" -Harness "dsh" -Task "Implémenter la spec" -RequestId "job-01"

# Lancer une chaîne séquentielle durable (avec interpolation automatique de {previous})
pwsh -NoProfile -File factory/factory.ps1 subagents -Action chain -ChainJson '[{"agent":"builder","task":"Coder la feature"},{"agent":"reviewer-code","task":"Auditer: {previous}","writer":false}]'

# Steer (remplace les steers précédents) ou Notify un sous-agent en cours
pwsh -NoProfile -File factory/factory.ps1 subagents -Action send -To "<wid>/step-1" -Kind steer -Message "Vérifie d'abord les logs"

# Voir le statut global ou filtrer la sortie d'un workflow (tail + grep regex borné)
pwsh -NoProfile -File factory/factory.ps1 subagents -Action status -Wid "<wid>" -Tail 20 -Grep "PASS|ERROR"

# Reprendre tous les workflows interrompus après un crash ou un quit
pwsh -NoProfile -File factory/factory.ps1 subagents -Action resume

# Effectuer un Handoff de contexte ou fouiller l'historique avant handoff
pwsh -NoProfile -File factory/factory.ps1 subagents -Action handoff -Note "Phase 1 terminée, prêt pour review"
pwsh -NoProfile -File factory/factory.ps1 subagents -Action search-history -Query "Phase 1"
```

## 3. Utilisation Native dans Pi 1.5.0
Dans Pi, l'extension `.pi/extensions/aspace-factory.ts` expose directement les outils natifs :
- `subagents({ action: "agents" | "status" | "run" | "chain" | "send" | "resume", ... })`
- `handoff({ note: "..." })`
- `search_history({ text: "..." })`
- Commandes slash : `/subagents` et `/factory`.
