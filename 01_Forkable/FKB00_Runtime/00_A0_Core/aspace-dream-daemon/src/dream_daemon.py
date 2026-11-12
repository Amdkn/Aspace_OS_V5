#!/usr/bin/env python3
"""Daemon de SUBSTITUTION pour la boucle nocturne H3 (D-N052 R4, §D7).

SUBSTITUTION — ce n'est PAS le daemon RigInfinity. Le daemon RigInfinity
(F8 D8, Rust, basé sur infinity-daemon, pas 3 de F8) n'est pas encore livré.
Ce script Python (stdlib uniquement) le remplace temporairement pour lancer
la boucle rêve -> worktree -> évaluation -> promotion entre 00h et 05h.
Condition de retrait : quand F8 pas 3 livre le daemon Rust, cette
substitution est RETIRÉE et le point d'entrée (la boucle) est repris par
le vrai daemon. Voir README.md du daemon.

Comportement (design §D7 — un daemon, pas un cron) :
* hibernation interne jusqu'à 00h (heure locale, --tz) : le réveil est
  interne, depuis l'hibernation — aucun cron, aucun tic planifié comme
  lanceur ;
* à 00h : vérifie le snapshot (fichier déposé par le coordinateur avant
  00h, sha + taille consignés), exécute UN cycle via
  ``dream_loop.run_dream_cycle`` (rêve -> worktree -> évaluation ->
  promotion par le gate), écrit le rapport de cycle + checkpoint JSON ;
* hiberne ensuite jusqu'à 05h (ou fin du travail), puis s'arrête (exit 0).
  Le coordinateur le redémarre la nuit suivante — le redémarrage n'est
  pas un cron : c'est une décision d'exploitation, pas un lanceur.
* reprise au checkpoint : si un checkpoint dit qu'un cycle est terminé
  pour cette nuit, le daemon ne le rejoue pas ; s'il a été interrompu
  (SIGTERM/SIGINT -> checkpoint INTERRUPTED), il rejoue le cycle
  (idempotent : worktrees réinitialisés, gate workspace re-créé).
* log append-only (fichier + stdout/journald). Ne touche jamais à
  master, n'ouvre jamais de PR, ne merge jamais, n'écrit jamais dans
  factory.sqlite ni dans le snapshot (lecture seule).

Usage (installé par le coordinateur — voir README.md) :
  python3 dream_daemon.py --v5 ~/workspace/v5-r4 \
      --snapshot /tmp/factory-r4-night-snapshot.sqlite \
      --state-dir ~/workspace/v4-factory/evidence/D-N052/r4/night \
      --tz America/New_York
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import signal
import sys
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

STOP = False


def _now(tz) -> datetime:
    return datetime.now(tz)


def log(state_dir: Path, msg: str) -> None:
    line = f"{datetime.now(timezone.utc).isoformat()} [dream-daemon] {msg}"
    print(line, flush=True)
    try:
        with open(state_dir / "daemon.log", "a", encoding="utf-8") as fh:
            fh.write(line + "\n")
    except OSError:
        pass


def sha256_file(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def write_checkpoint(state_dir: Path, data: dict) -> None:
    tmp = state_dir / "checkpoint.json.tmp"
    tmp.write_text(json.dumps(data, indent=2, ensure_ascii=False),
                   encoding="utf-8")
    os.replace(tmp, state_dir / "checkpoint.json")


def read_checkpoint(state_dir: Path) -> dict | None:
    p = state_dir / "checkpoint.json"
    if not p.is_file():
        return None
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None


def next_midnight(now: datetime) -> datetime:
    """Prochain 00:00 local (aujourd'hui si avant 00h, sinon demain)."""
    nxt = now.replace(hour=0, minute=0, second=0, microsecond=0)
    if nxt <= now:
        nxt += timedelta(days=1)
    return nxt


def five_am(now: datetime) -> datetime:
    """05:00 local du jour de ``now`` (ou le lendemain si déjà passé)."""
    t = now.replace(hour=5, minute=0, second=0, microsecond=0)
    if t <= now:
        t += timedelta(days=1)
    return t


def sleep_until(target: datetime, state_dir: Path) -> bool:
    """Hibernation jusqu'à ``target`` (réveil interne). Retourne False si stop."""
    global STOP
    log(state_dir, f"hibernation jusqu'à {target.isoformat()}")
    while not STOP:
        now = datetime.now(target.tzinfo)
        remaining = (target - now).total_seconds()
        if remaining <= 0:
            return True
        time.sleep(min(60.0, remaining))
    return False


def run_cycle(args, state_dir: Path, night: str) -> dict:
    """Exécute un cycle de la boucle (délégué à dream_loop)."""
    gate_src = os.path.join(args.v5, "01_Forkable", "FKB00_Runtime",
                            "00_A0_Core", "aspace-wikiskill-gate", "src")
    wikiskill_dir = os.path.join(
        args.v5, "01_Forkable", "FKB00_Runtime", "05_Recursive_RSI",
        "wikiskill")
    loop_src = os.path.join(args.v5, "01_Forkable", "FKB00_Runtime",
                            "00_A0_Core", "aspace-dream-loop", "src")
    sys.path.insert(0, gate_src)
    sys.path.insert(0, wikiskill_dir)
    sys.path.insert(0, loop_src)
    sys.path.insert(0, args.reader_src)
    sys.path.insert(0, args.rrsi)
    sys.path.insert(0, args.dream_rsi)

    snap = Path(args.snapshot)
    snap_sha = sha256_file(str(snap))
    snap_size = snap.stat().st_size
    log(state_dir, f"snapshot {snap} sha256 {snap_sha[:12]}… {snap_size} o")
    ref = datetime.fromisoformat(args.reference_time) if args.reference_time \
        else datetime.now(ZoneInfo(args.tz))

    from dream_loop import run_dream_cycle

    outdir = state_dir / f"cycle-{night}"
    report = run_dream_cycle(
        snapshot=str(snap), ref=ref, v5_gate_src=gate_src,
        evolve_repo=str(state_dir / "evolve-repo"),
        worktrees_dir=str(state_dir / "worktrees"),
        gate_ws=str(state_dir / "gate-ws"),
        outdir=str(outdir))
    # Le snapshot ne doit pas avoir bougé pendant le cycle.
    assert sha256_file(str(snap)) == snap_sha, "snapshot modifié pendant le cycle"
    return {"night": night, "snapshot_sha256": snap_sha,
            "snapshot_size_o": snap_size,
            "reference_time": ref.isoformat(),
            "promoted": report["gate"]["promoted"],
            "r_best": report["gate"]["r_best"],
            "dream_selected": report["dream_selected"],
            "rrsi_winner": report["rrsi_selection"]["winner"],
            "report_path": str(outdir / "cycle-report.json")}


def main() -> int:
    global STOP
    ap = argparse.ArgumentParser()
    ap.add_argument("--v5", required=True, help="Clone V5 sur la branche R4")
    ap.add_argument("--snapshot", required=True,
                    help="Snapshot factory.sqlite (déposé par le coordinateur)")
    ap.add_argument("--state-dir", required=True)
    ap.add_argument("--tz", default="America/New_York")
    ap.add_argument("--reader-src", default=os.path.expanduser(
        "~/workspace/v4-factory/evidence/D-N052/r0/aspace-aqua-adapter/src"))
    ap.add_argument("--rrsi", default=os.path.expanduser("~/workspace/rrsi-repo"))
    ap.add_argument("--dream-rsi", default=os.path.expanduser(
        "~/workspace/dream-rsi-repo"))
    ap.add_argument("--reference-time", default=None,
                    help="Instant de référence du snapshot (ISO 8601, défaut: maintenant)")
    ap.add_argument("--run-now", action="store_true",
                    help="Exécuter le cycle immédiatement (test / reprise), sans attendre 00h")
    args = ap.parse_args()

    tz = ZoneInfo(args.tz)
    state_dir = Path(args.state_dir)
    state_dir.mkdir(parents=True, exist_ok=True)

    def _stop(signum, frame):
        global STOP
        STOP = True
        log(state_dir, f"signal {signum} reçu — checkpoint INTERRUPTED et arrêt propre")

    signal.signal(signal.SIGTERM, _stop)
    signal.signal(signal.SIGINT, _stop)

    log(state_dir, "démarrage (SUBSTITUTION du daemon RigInfinity — voir README)")
    ckpt = read_checkpoint(state_dir)
    if ckpt:
        log(state_dir, f"checkpoint existant : {ckpt.get('status')} "
                       f"nuit {ckpt.get('night')}")

    now = _now(tz)
    if not args.run_now:
        if now.hour < 5:
            # Démarré entre 00h et 05h : la nuit est en cours, on court.
            log(state_dir, "démarré pendant la fenêtre 00h-05h — cycle immédiat")
        elif now.hour >= 5:
            # Démarré après 05h : hiberner jusqu'au prochain 00h.
            if not sleep_until(next_midnight(now), state_dir):
                write_checkpoint(state_dir, {"status": "INTERRUPTED",
                                             "night": now.strftime("%Y-%m-%d")})
                return 0
            now = _now(tz)
        else:
            # Démarré avant 00h : hiberner jusqu'à 00h.
            if not sleep_until(next_midnight(now), state_dir):
                write_checkpoint(state_dir, {"status": "INTERRUPTED",
                                             "night": now.strftime("%Y-%m-%d")})
                return 0
            now = _now(tz)

    night = now.strftime("%Y-%m-%d")
    if ckpt and ckpt.get("status") == "DONE" and ckpt.get("night") == night:
        log(state_dir, f"cycle de la nuit {night} déjà terminé — rien à rejouer")
    else:
        log(state_dir, f"cycle de la nuit {night} — démarrage")
        write_checkpoint(state_dir, {"status": "RUNNING", "night": night,
                                     "started_at": now.isoformat()})
        try:
            result = run_cycle(args, state_dir, night)
        except Exception as exc:  # checkpoint FAILED, exit non-zero (systemd relance)
            log(state_dir, f"cycle ÉCHOUÉ : {type(exc).__name__}: {exc}")
            write_checkpoint(state_dir, {"status": "FAILED", "night": night,
                                         "error": f"{type(exc).__name__}: {exc}",
                                         "at": _now(tz).isoformat()})
            return 1
        result["status"] = "DONE"
        write_checkpoint(state_dir, result)
        log(state_dir, f"cycle terminé : promu={result['promoted']} "
                       f"R_best={result['r_best']} "
                       f"RRSI winner={result['rrsi_winner']}")

    # Hiberner jusqu'à 05h puis s'arrêter (exit 0). Le coordinateur
    # redémarre le daemon la nuit suivante — pas un cron.
    now = _now(tz)
    if now.hour < 5:
        if not sleep_until(five_am(now), state_dir):
            return 0
    log(state_dir, "fenêtre 00h-05h terminée — arrêt propre (exit 0)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
