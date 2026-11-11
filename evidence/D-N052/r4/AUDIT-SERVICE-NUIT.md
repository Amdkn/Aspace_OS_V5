# Audit du service de nuit R4 — D-N052 (rectificatif §7)

- **Date :** 2026-11-11 ~17:35 EST
- **Auditeur :** coordinateur « Git-first / audit service de nuit » (ordre S0, rectificatif architectural GPT 2026-11-11 ~17:28)
- **Objet :** service de nuit D-N052 R4 (Dream-RSI + RRSI, boucle H3 00h–05h, 2026-11-12)
- **Branche :** `a0/dn052-r4-dream` — tête vérifiée `9f5a5bb5a62d63cde380ba716fa0ebe0603ca4c0` (API GitHub, 2026-11-11 17:30 EST)
- **PR #37 :** ouverte, non mergée, mergeable true, tête `9f5a5bb` — ne pas merger, ne pas rebaser (jugement 13e après la course de nuit)

## 1. Fonction exacte du daemon

Fichier : `01_Forkable/FKB00_Runtime/00_A0_Core/aspace-dream-daemon/src/dream_daemon.py`
(228 lignes, Python stdlib uniquement). **Substitution nommée** du daemon
RigInfinity (F8 D8, Rust, non livré) — ne jamais la présenter comme le
vrai daemon (README du daemon, condition de retrait : F8 pas 3).

Comportement (lu au code, pas au récit) :

- **Démarrage :** lit `checkpoint.json` dans `--state-dir`, le journalise.
- **Si heure locale < 05h :** cycle immédiat (la nuit est en cours).
- **Si heure locale ≥ 05h :** hiberne jusqu'au prochain 00h.
- **Si heure locale avant 00h :** hiberne jusqu'à 00h (réveil interne,
  `sleep_until`, pas de cron comme lanceur — design §D7).
- **À 00h :** vérifie le snapshot (sha256 + taille, lecture seule),
  exécute **UN** cycle via `dream_loop.run_dream_cycle` (rêve → worktree
  → évaluation → promotion par le gate), écrit `cycle-<nuit>/cycle-report.json`
  + checkpoint JSON. Assert : le snapshot n'a pas bougé pendant le cycle.
- **Après le cycle :** hiberne jusqu'à 05h, puis s'arrête (exit 0).
- **Checkpoint :**
  - `DONE` + même nuit → cycle **non rejoué** (« rien à rejouer ») — pas de duplication.
  - `INTERRUPTED` (ou `RUNNING`, ou autre) → cycle **rejoué** (idempotent :
    worktrees réinitialisés, gate workspace re-créé).
  - `FAILED` (exception dans le cycle) → exit 1, systemd `Restart=on-failure`
    relance.
- **SIGTERM / SIGINT :** arrêt propre. En hibernation : écrit `INTERRUPTED`
  et exit 0. Pendant un cycle : le cycle en cours se termine (le signal
  ne l'interrompt pas), puis arrêt.
- **Ne touche jamais** à master, n'ouvre jamais de PR, ne merge jamais,
  n'écrit jamais dans `factory.sqlite` ni dans le snapshot (lecture seule).

Dépendances d'exécution (chemins `~` = `$HOME`, défauts du code) :

- `--v5` : clone V5 sur la branche R4 (explicite).
- `--snapshot` : snapshot `factory.sqlite` gelé (explicite).
- `--state-dir` : état local (checkpoint, log, sorties de cycle).
- `--reader-src` (défaut `~/workspace/v4-factory/evidence/D-N052/r0/aspace-aqua-adapter/src`)
  : `aqua_factory_reader.py`, importé par `dream_loop.py:333`.
- `--rrsi` (défaut `~/workspace/rrsi-repo`) et `--dream-rsi` (défaut
  `~/workspace/dream-rsi-repo`) : adaptateurs RRSI / Dream-RSI.

## 2. Code et configuration dans Git

Branche R4 `9f5a5bb` — 15 blobs + 3 gitlinks (vérifiés à l'API,
arbre récursif) :

| Chemin | Contenu |
|---|---|
| `01_Forkable/FKB00_Runtime/00_A0_Core/aspace-dream-daemon/README.md` | doc substitution, installation, test `--run-now` |
| `01_Forkable/FKB00_Runtime/00_A0_Core/aspace-dream-daemon/aspace-dream-daemon.service` | unit systemd committée |
| `01_Forkable/FKB00_Runtime/00_A0_Core/aspace-dream-daemon/src/dream_daemon.py` | le daemon (228 lignes) |
| `01_Forkable/FKB00_Runtime/00_A0_Core/aspace-dream-loop/README.md`, `smoke_test.py`, `src/dream_loop.py`, `src/dream_variants.py` | la boucle H3 |
| `01_Forkable/FKB00_Runtime/00_A0_Core/aspace-wikiskill-gate/README.md`, `fixtures/traces-v5-structural.jsonl`, `smoke_test.py`, `src/aqua_gate.py`, `src/bench_backend.py`, `src/gate_runner.py` | le gate R3 (Algorithm 1) |
| `01_Forkable/FKB00_Runtime/00_A0_Core/wikiskill-R3-ADAPTATION.md` | fiche R3 |
| `00_Memoire/WORKGRAPH-MUSE.md` | miroir Workgraph (pulse) |
| `01_Forkable/FKB00_Runtime/05_Recursive_RSI/dream-rsi` @ `fa0c8f0` | gitlink |
| `01_Forkable/FKB00_Runtime/05_Recursive_RSI/rrsi` @ `cc424cc` | gitlink |
| `01_Forkable/FKB00_Runtime/05_Recursive_RSI/wikiskill` @ `59a6a04` | gitlink |

**Écart committé vs installé (défaut connu, non corrigé dans la branche) :**
l'unit committée casse sous systemd root (`~` = `/root` →
`ModuleNotFoundError: aqua_factory_reader`, testé rc=1) et son
`--snapshot` pointe `/tmp/factory-r4-night-snapshot.sqlite` (éphémère,
vidé à chaque remplacement de VM). L'unit installée corrige les deux
(`Environment=HOME=/home/hatch`, snapshot en chemin persistant).
Le correctif doit être reporté dans la branche (R5 / jugement) — la
branche reste à `9f5a5bb` pour ce point. L'unit installée est versionnée
par ce commit comme référence (`evidence/D-N052/r4/daemon/`).

## 3. Tâches et résultats produits

**Phase de jour — LIVRÉE et VÉRIFIÉE** (coordinateur R4, reçu R10
G-20261111-044, recorded 14:28:03 EST) :

- PR #37 ouverte 14:25:22 EST, 17 fichiers +2475/−0, tête `9f5a5bb`.
- Harnais rejoué en clone frais : **18/18 PASS** ; smoke rejoué : **8/8 PASS**.
- Beta : grille `0, 0.25, 0.5, 0.75, 1`, λ `0.05`, **0 occurrence de 0.35**.
- Gate : baseline 0.6667 → `v-loose-7d` 1.0 ACCEPTÉE (marge 0.3333 ≥ delta 0.0267) ;
  holdout V5 0.6667 → 1.0 (3/3) ; RRSI winner = aucun (incumbent S\* = 1.0).
- Daemon `--run-now` testé (état séparé) : cycle DONE < 1 s, checkpoint DONE,
  promu `v-loose-7d`, R_best 1.0, exit 0.

**Course de nuit — NON ENCORE EXÉCUTÉE.** Aucun cycle de nuit n'a tourné.
Aucun `cycle-2026-11-11/`, aucun `worktrees/`, aucun `gate-ws/`, aucun
`evolve-repo/` dans le state dir. Le critère de succès de la nuit est le
**mécanisme** (variante → évaluation en worktree → décision du gate,
consignée), pas la promotion elle-même.

## 4. Ce qui a réellement été sauvegardé — et où

| Élément | Emplacement | Dans Git ? |
|---|---|---|
| Code daemon + boucle + gate | branche R4 `9f5a5bb` | **Oui** |
| Gitlinks rrsi / dream-rsi / wikiskill | branche R4 (SHAs épinglés) | **Oui** (URLs dans `.gitmodules` de master : `Amdkn/rrsi`, `Amdkn/dream-rsi`) |
| Snapshot de nuit gelé (sha `305c5a28…`, 61 440 o) | `~/workspace/.../r4/night/` (local) | **Non — versionné par ce commit** |
| `checkpoint.json` (INTERRUPTED) | `~/workspace/.../r4/night/` (local) | **Non — versionné par ce commit** |
| Unit installée | `/etc` (éphémère) + copie `~/workspace/.../r4/daemon/` (local) | **Non — versionnée par ce commit** |
| `aqua_factory_reader.py` (dépendance d'exécution) | `~/workspace/.../r0/aspace-aqua-adapter/` (local) | **Non — versionné par ce commit** |
| Procédure de reprise `REPRISE.md` | — (n'existait pas) | **Oui — créée par ce commit** |
| Cet audit | — (n'existait pas) | **Oui — créé par ce commit** |
| Preuves phase de jour (`H-R5-PROOF.md`, `RESULTS-R4.json`, `smoke-test-coordinator.log`) | `~/workspace/.../r4/` (local) | **Non — reste à faire (R4 CLOSE)** |
| Reçu R10 G-20261111-044 | `~/workspace/.../repo-v4-readonly/ledger/receipts/` (local) | **Non — V4 archivé, consignation impossible** |
| Registre Nardole (892 lignes, journal = ligne) | `~/workspace/.../dispatch/REGISTRE-NARDOLE.md` (local) | **Non — miroir partiel `00_Memoire/WORKGRAPH-MUSE.md` sur master** |
| `daemon.log` (journal d'exécution) | `~/workspace/.../r4/night/` (local) | **Non — cité verbatim §5 ci-dessous** |

Provenance du snapshot (vérifiée, `RESULTS-R4.json`) : source
`/mnt/c/Users/amado/Aspace OS V5/02_Factory/factory.sqlite` (base live du
PC) ; live sha `ea9043cf…` avant == après (base immobile) ;
`reference_time` 2026-11-11T14:08:28-05:00 ; 7 workflows, 9 steps,
6 events ; byte-identique au snapshot R3.

## 5. Pertes et duplications — AUCUNE (preuve par les logs)

Les deux kills ont eu lieu **en hibernation**, aucun cycle n'a tourné :

```
2026-11-11T19:28:10.135003+00:00 [dream-daemon] démarrage (SUBSTITUTION du daemon RigInfinity — voir README)
2026-11-11T19:28:10.136123+00:00 [dream-daemon] hibernation jusqu'à 2026-11-12T00:00:00-05:00
2026-11-11T19:28:56.667026+00:00 [dream-daemon] signal 15 reçu — checkpoint INTERRUPTED et arrêt propre
2026-11-11T19:34:15.056856+00:00 [dream-daemon] démarrage (SUBSTITUTION du daemon RigInfinity — voir README)
2026-11-11T19:34:15.057190+00:00 [dream-daemon] hibernation jusqu'à 2026-11-12T00:00:00-05:00
2026-11-11T19:34:40.327962+00:00 [dream-daemon] signal 15 reçu — checkpoint INTERRUPTED et arrêt propre
2026-11-11T19:35:15.153371+00:00 [dream-daemon] démarrage (SUBSTITUTION du daemon RigInfinity — voir README)
2026-11-11T19:35:15.153744+00:00 [dream-daemon] checkpoint existant : INTERRUPTED nuit 2026-11-11
2026-11-11T19:35:15.153839+00:00 [dream-daemon] hibernation jusqu'à 2026-11-12T00:00:00-05:00
2026-11-11T21:38:12.262203+00:00 [dream-daemon] signal 15 reçu — checkpoint INTERRUPTED et arrêt propre
2026-11-11T21:56:30.586644+00:00 [dream-daemon] démarrage (SUBSTITUTION du daemon RigInfinity — voir README)
2026-11-11T21:56:30.587244+00:00 [dream-daemon] checkpoint existant : INTERRUPTED nuit 2026-11-11
2026-11-11T21:56:30.587392+00:00 [dream-daemon] hibernation jusqu'à 2026-11-12T00:00:00-05:00
```

(Heures UTC ; 19:28 UTC = 14:28 EST, 21:38 UTC = 16:38 EST, 21:56 UTC = 16:56 EST.)

Preuves complémentaires (vérifiées 17:30 EST) :

- State dir = 3 fichiers seulement (`checkpoint.json`, `daemon.log`,
  `factory-night-snapshot.sqlite`) — aucun `cycle-*/`, `worktrees/`,
  `gate-ws/`, `evolve-repo/`.
- Checkpoint = `{"status": "INTERRUPTED", "night": "2026-11-11"}` —
  jamais `RUNNING`, jamais `DONE`, jamais `FAILED`.
- Snapshot sha `305c5a28ec0b1076bcd636efe6d158119d404cae093dcb6c5f663ac06cba3595`
  inchangé depuis 14:27 EST (byte-identique au snapshot R3).
- **Tâches perdues : 0. Tâches dupliquées : 0.** Le cycle de nuit n'a
  pas commencé ; l'état à rejouer à 00h est intact.

## 6. Manques trouvés — et leur statut après ce commit

| Manque | Statut |
|---|---|
| Snapshot, checkpoint, unit installée, procédure de reprise, audit absents du dépôt | **Corrigé par ce commit** (fichiers `evidence/D-N052/r4/…`) |
| `aqua_factory_reader.py` absent du dépôt (dépendance d'exécution, `ModuleNotFoundError` prouvé sans lui) | **Corrigé par ce commit** (`evidence/D-N052/r0/aspace-aqua-adapter/…`) |
| Unit committée cassée sous systemd root + snapshot `/tmp` | **Non corrigé dans la branche** — unit installée versionnée comme référence ; report du correctif à R5 / jugement |
| Preuves phase de jour locales seulement | **Reste à faire** — à committer à R4 CLOSE avec les preuves de nuit |
| Registre local seulement (miroir partiel sur master) | **Noté** — le miroir `00_Memoire/WORKGRAPH-MUSE.md` porte l'état ; le registre complet reste local |
| Reçus R10 locaux seulement | **Bloqué** — V4 archivé, consignation impossible (dépôt local) |
| Déclencheur durable = crons du runtime (pas Git) | **Partiellement corrigé** — crons 23:15 (vérifié Git-first) + 00:00 (lancement conditionnel depuis le dépôt) ; GitHub Actions : voir §7 |

## 7. Déclencheur durable — verdict

**Modèle cible (rectificatif §6) :** Git → Événement / Planificateur →
Worker jetable → Exécution → Commit / Push → Événement suivant.

**Mis en place ce soir (crons du runtime — ils survivent au remplacement
de VM, ils ne vivent pas dans la VM) :**

- `r4-night-daemon-check-2315` (2026-11-11 23:15 EST, runonce) : vérifie
  l'état **Git-first** (tête de branche, checkpoint versionné, snapshot
  sha, daemon vivant OU relançable depuis le dépôt), reconstruit depuis
  le dépôt si besoin.
- `r4-night-daemon-launch-0000` (2026-11-12 00:00 EST, runonce) :
  lancement **conditionnel** — si un daemon est déjà vivant, silence (il
  court le cycle) ; sinon, clone/sync frais de la branche R4, état
  reconstruit depuis le dépôt, lancement, vérification.

**GitHub Actions (déclencheur long terme) : NON construit ce soir.**
Verdict : un workflow planifié (`.github/workflows/*`, `schedule` + runner
jetable qui clone la branche, lance le daemon, committe les preuves)
est le déclencheur conforme au rectificatif, mais les fichiers
`.github/workflows/*` ne passent PAS par l'API (403 sur `git/trees`) —
ils doivent être créés via l'**UI navigateur** (session GitHub du
Capitaine). Reste à faire documenté : créer
`.github/workflows/dream-night.yml` via l'UI, avec `schedule: '0 0 * * *'`
(00:00 America/New_York), runner `ubuntu-latest`, étapes clone branche
R4 → `--run-now` ou daemon → commit des preuves sur la branche.
Ce n'est pas prétendu fait.

**Tension documentée :** le design §D7 dit « aucun cron comme lanceur »
(réveil interne depuis l'hibernation). Le rectificatif S0 (ordre
supérieur) impose des workers déclenchés par événement/planificateur.
Le cron 00:00 ne remplace pas l'hibernation interne — il remplace
seulement le *démarrage* du worker (qui, lancé à 00:00, court le cycle
immédiatement, heure < 05h). L'hibernation interne reste le mécanisme
de fin de fenêtre (05h, exit 0).

## 8. Chronologie des deux remplacements de VM

| Heure (EST) | Événement |
|---|---|
| ~14:28 | VM remplacée (1re fois). Daemon PID 111902 tué 14:28:56 (SIGTERM, en hibernation). Unit `/etc` supprimée, `/tmp` vidé. |
| ~14:35 | Daemon reconstruit (PID 2849), snapshot repris `305c5a28…`, hibernation jusqu'à 00:00. |
| ~16:37 | VM remplacée (2e fois, uptime 16 min). Daemon tué 16:38:12 (SIGTERM, en hibernation). Unit `/etc` supprimée, `/tmp` vidé. |
| ~16:56 | Daemon reconstruit par A0 (PID 4368), unit réinstallée (`Environment=HOME=/home/hatch`, snapshot persistant), copie persistante de l'unit en `evidence/D-N052/r4/daemon/`, hibernation jusqu'à 00:00. |
| 17:30 | Audit : daemon PID 4368 actif, hibernation jusqu'à 2026-11-12T00:00:00-05:00, checkpoint INTERRUPTED, snapshot sha inchangé. |

## 9. Recommandations

1. **R5 / jugement :** reporter le correctif d'unit dans la branche
   (`Environment=HOME=…` + snapshot hors `/tmp`) — la branche ne doit
   plus casser à l'installation fraîche.
2. **R4 CLOSE :** committer les preuves de jour (`H-R5-PROOF.md`,
   `RESULTS-R4.json`, `smoke-test-coordinator.log`) + les preuves de
   nuit (`cycle-2026-11-12/cycle-report.json`, checkpoint final) sur la
   branche avant le jugement 13e.
3. **Long terme :** créer le workflow GitHub Actions `dream-night.yml`
   via l'UI navigateur (voir §7) ; les crons du runtime sont le
   filet, pas la cible.
4. **Ne jamais** redémarrer quoi que ce soit sur le PC du Capitaine
   (cible de déploiement du système fini, pas machine de calcul de
   Muse) — la copie de sauvegarde R4 qui s'y trouve est inerte.
