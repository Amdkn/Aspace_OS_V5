# aspace-dream-daemon — daemon de SUBSTITUTION (D-N052 R4, H3)

## SUBSTITUTION — lire d'abord

**Ce daemon n'est PAS le daemon RigInfinity.** Le daemon RigInfinity
(F8 D8 : daemon Rust basé sur `infinity-daemon`, pas 3 de F8) n'existe pas
encore (F8 en cours, merge bloqué par la restauration de master). Cette
implémentation Python (stdlib uniquement) est une **substitution nommée** :
elle lance la boucle H3 entre 00h et 05h en attendant le vrai daemon.
**Ne jamais la présenter comme le daemon RigInfinity.**

**Condition de retrait :** quand F8 pas 3 livre le daemon Rust, cette
substitution est **retirée** (script + unit supprimés de la branche) et le
point d'entrée — la boucle `aspace-dream-loop` — est repris par le vrai
daemon RigInfinity. Le retrait est un acte nommé, pas un oubli.

## Ce qu'il fait

- Hiberne jusqu'à 00h (heure locale), exécute UN cycle de la boucle
  (rêve → worktree → évaluation → promotion par le gate), hiberne
  jusqu'à 05h, s'arrête (exit 0). Le réveil est interne, depuis
  l'hibernation — **aucun cron, aucun tic planifié comme lanceur**
  (design §D7).
- Checkpoint JSON (`checkpoint.json`) : reprise possible — un cycle
  terminé n'est pas rejoué ; un cycle interrompu (SIGTERM/SIGINT) est
  rejoué (idempotent).
- Log append-only (`daemon.log` + journald via stdout).
- Ne touche jamais à master, n'ouvre jamais de PR, ne merge jamais,
  n'écrit jamais dans `factory.sqlite` ni dans le snapshot (lecture
  seule, sha vérifié avant/après le cycle).

## Installation (par le coordinateur, pas par l'exécutant R4)

1. Prendre un snapshot frais de `factory.sqlite` (API backup SQLite via
   SSH, comme pour R3/R4) et le déposer à
   `/tmp/factory-r4-night-snapshot.sqlite` ; consigner son sha256.
2. Copier l'unit dans `/etc/systemd/system/` :
   `cp aspace-dream-daemon.service /etc/systemd/system/`
   (adapter les chemins `--v5`, `--snapshot`, `--state-dir` si besoin).
3. `systemctl daemon-reload && systemctl enable --now aspace-dream-daemon`
   — à faire AVANT 00h.
4. Vérifier avant 00h : `systemctl status aspace-dream-daemon` actif,
   `journalctl -u aspace-dream-daemon -f` montre « hibernation jusqu'à ».
5. Le lendemain : lire `evidence/D-N052/r4/night/checkpoint.json` et
   `night/cycle-<date>/cycle-report.json` ; le critère de succès de la
   nuit est le MÉCANISME (variante → évaluation en worktree → décision
   du gate, consignée), pas la promotion elle-même — un refus du gate
   est une preuve que le gate fonctionne, pas un échec.

## Test de jour (sans attendre 00h)

```bash
python3 src/dream_daemon.py --v5 ~/workspace/v5-r4 \
  --snapshot /tmp/factory-r4-snapshot.sqlite \
  --state-dir /tmp/dream-daemon-test \
  --reference-time 2026-11-11T14:08:28-05:00 --run-now
# --run-now exécute le cycle immédiatement puis s'arrête à 05h
# (ici : hiberne jusqu'à 05h — interrompre par SIGTERM pour le test court,
#  le checkpoint INTERRUPTED est alors écrit).
```

## Layout

- `src/dream_daemon.py` — le daemon (stdlib : `zoneinfo`, `signal`,
  `json`, `hashlib` ; superviseur : hibernation, relance via systemd,
  checkpoint, log append-only — patron inspiré du superviseur First
  Light, `first-light/supervisor.py`, lu, non modifié).
- `aspace-dream-daemon.service` — unit systemd (`Type=simple`,
  `Restart=on-failure`, `StartLimitBurst=3`, logs journald).
