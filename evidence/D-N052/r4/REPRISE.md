# REPRISE — reconstruire le service de nuit R4 depuis Git seul

- **Branche :** `a0/dn052-r4-dream` (repo `Amdkn/Aspace_OS_V5`)
- **Objet :** course de nuit D-N052 R4 (Dream-RSI + RRSI, boucle H3 00h–05h, nuit 2026-11-12)
- **Principe (rectificatif Git-first) :** tout ce qu'il faut pour reprendre
  est versionné sur la branche. Un worker frais (VM remplacée, nouvelle
  session) n'a besoin de rien d'autre que de cette branche + des dépôts
  publics épinglés ci-dessous. Aucun secret n'est requis.

## 0. Vérifier la tête de branche

```bash
gh api repos/Amdkn/Aspace_OS_V5/commits/a0/dn052-r4-dream --jq '{sha: .sha[0:7]}'
# Doit contenir evidence/D-N052/r4/night/ (snapshot + checkpoint),
# evidence/D-N052/r4/REPRISE.md, evidence/D-N052/r4/AUDIT-SERVICE-NUIT.md,
# evidence/D-N052/r4/daemon/aspace-dream-daemon.service.installed,
# evidence/D-N052/r0/aspace-aqua-adapter/src/aqua_factory_reader.py
gh api "repos/Amdkn/Aspace_OS_V5/git/trees/<HEAD>?recursive=1" \
  --jq '.tree[] | select(.path | test("evidence/D-N052/r4/night|evidence/D-N052/r4/REPRISE")) | .path'
```

## 1. Cloner la branche (frais)

```bash
git clone --branch a0/dn052-r4-dream --single-branch \
  https://github.com/Amdkn/Aspace_OS_V5.git v5-r4
cd v5-r4 && git rev-parse HEAD   # noter le SHA
```

## 2. Récupérer rrsi et dream-rsi aux SHAs épinglés

(La branche porte les gitlinks mais pas de `.gitmodules` ; les URLs sont
celles de master `.gitmodules`, dépôts publics `Amdkn`.)

```bash
git clone https://github.com/Amdkn/rrsi.git rrsi-repo
git -C rrsi-repo checkout cc424ccde51d091bbd88d926e2a2306ae89e996d
git clone https://github.com/Amdkn/dream-rsi.git dream-rsi-repo
git -C dream-rsi-repo checkout fa0c8f0859558fc2a2e101a4b3ef4f3b67807053
```

## 3. Reconstruire l'état local depuis la branche

```bash
STATE_DIR=~/workspace/v4-factory/evidence/D-N052/r4/night   # ou tout chemin local
mkdir -p "$STATE_DIR"
git -C v5-r4 show "a0/dn052-r4-dream:evidence/D-N052/r4/night/factory-night-snapshot.sqlite" \
  > "$STATE_DIR/factory-night-snapshot.sqlite"
git -C v5-r4 show "a0/dn052-r4-dream:evidence/D-N052/r4/night/checkpoint.json" \
  > "$STATE_DIR/checkpoint.json"
# Vérification OBLIGATOIRE avant de lancer :
sha256sum "$STATE_DIR/factory-night-snapshot.sqlite"
# attendu : 305c5a28ec0b1076bcd636efe6d158119d404cae093dcb6c5f663ac06cba3595 (61 440 o)
cat "$STATE_DIR/checkpoint.json"
# attendu : {"status": "INTERRUPTED", "night": "2026-11-11"}
```

Règle SQLite (leçon R4) : ne jamais faire un backup dans un fichier
existant (octets résiduels → sha différent) — toujours `rm` la
destination d'abord. Ici on copie un fichier gelé, pas un backup.

## 4. Lancer

### A. Via systemd (préféré — redémarrage auto si le cycle échoue)

```bash
# Prendre l'unit installée versionnée, ADAPTER les chemins à ce worker :
git -C v5-r4 show "a0/dn052-r4-dream:evidence/D-N052/r4/daemon/aspace-dream-daemon.service.installed" \
  > /etc/systemd/system/aspace-dream-daemon.service
# Éditer ExecStart : --v5 <chemin du clone>, --snapshot <STATE_DIR>/factory-night-snapshot.sqlite,
# --state-dir <STATE_DIR>. Garder Environment=HOME=<home du worker>.
systemd-analyze verify /etc/systemd/system/aspace-dream-daemon.service
systemctl daemon-reload && systemctl enable --now aspace-dream-daemon
```

### B. Direct (sans systemd — survit à la déconnexion SSH avec nohup)

```bash
export HOME=/home/hatch   # ou le home du worker ; "~" des défauts en dépend
nohup python3 v5-r4/01_Forkable/FKB00_Runtime/00_A0_Core/aspace-dream-daemon/src/dream_daemon.py \
  --v5 "$PWD/v5-r4" \
  --snapshot "$STATE_DIR/factory-night-snapshot.sqlite" \
  --state-dir "$STATE_DIR" \
  --reader-src "$PWD/v5-r4/evidence/D-N052/r0/aspace-aqua-adapter/src" \
  --rrsi "$PWD/rrsi-repo" \
  --dream-rsi "$PWD/dream-rsi-repo" \
  --tz America/New_York \
  > "$STATE_DIR/daemon-direct.log" 2>&1 &
```

## 5. Vérifier le lancement

```bash
tail -5 "$STATE_DIR/daemon.log"   # ou journalctl -u aspace-dream-daemon
# attendu (lancé avant 00h) :
#   "checkpoint existant : INTERRUPTED nuit 2026-11-11"
#   "hibernation jusqu'à 2026-11-12T00:00:00-05:00"
cat "$STATE_DIR/checkpoint.json"  # toujours INTERRUPTED
sha256sum "$STATE_DIR/factory-night-snapshot.sqlite"  # toujours 305c5a28…
```

## 6. Sémantique du checkpoint (reprise sans duplication)

| Checkpoint | Comportement au démarrage |
|---|---|
| `DONE` + même nuit | Cycle **non rejoué** (« rien à rejouer ») |
| `INTERRUPTED` | Cycle **rejoué** (idempotent) |
| `RUNNING` (tué en cours de cycle) | Cycle **rejoué** depuis le début |
| `FAILED` | Exit 1 → systemd relance (`Restart=on-failure`) |

## 7. Après la nuit (00h–05h)

```bash
cat "$STATE_DIR/checkpoint.json"              # attendu : DONE, nuit 2026-11-12
cat "$STATE_DIR/cycle-2026-11-12/cycle-report.json"
# Critère de succès : le MÉCANISME (variante → évaluation en worktree →
# décision du gate, consignée), pas la promotion elle-même.
```

Committer ensuite sur la branche : `cycle-2026-11-12/cycle-report.json`
+ checkpoint final (preuves de nuit, R4 CLOSE → jugement 13e → PR #37).

## 8. Interdits

- **Ne jamais** merger ou rebaser PR #37 (elle attend le jugement 13e).
- **Ne jamais** commiter sur master.
- **Ne jamais** démarrer quoi que ce soit sur le PC du Capitaine
  (100.77.242.27 — cible de déploiement du système fini, pas machine
  de calcul de Muse ; la copie de sauvegarde R4 qui s'y trouve est inerte).
- **Ne jamais** mettre de secret dans Git.
