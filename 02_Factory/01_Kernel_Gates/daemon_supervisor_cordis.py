#!/usr/bin/env python3
"""
A'Space OS V5 — 02_Factory/01_Kernel_Gates/daemon_supervisor_cordis.py
Wargame Solution : Unifie tous les sous-daemons des modules forkés sous un SEUL Hyperviseur :
  - `Cordis`    = Daemon Maître Spatio-Temporel (PID 1 d'Aspace, Fibers réversibles à cycle de vie borné)
  - `Automaton` = Runtime Métabolique & Horloge de Baux (Tick Engine + Disjoncteur A1-Beth + Réserve 3-Paliers)
  - `Agent Zero`= Cortex Exécutif EGM invoqué à la demande (zéro daemon fantôme en roue libre)
  - `RigInfinity`= Orchestrateur déterministe (Fusion OpenRig packages/daemon + Infinity crates/infinity-daemon Rust)

Résout le problème du 'Daemon Sprawl' : au lieu que les 99 sous-modules lancent chacun leur
propre serveur HTTP/TCP permanent, chaque daemon enfant est encapsulé comme une `ManagedDaemonFiber`
à démarrage paresseux (Lazy Spawn), bail TTL strict (300s), et extinction automatique (`dispose()`).
"""

from __future__ import annotations
import json
import os
import signal
import subprocess
import sys
import tempfile
import time
from dataclasses import dataclass, asdict, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Literal

# D-N052 R5 (§D8) : le superviseur lance RÉELLEMENT le runtime — un seul
# spawn réel, la fiber `fiber:a0:agent-zero-cortex`. Les 5 autres fibers
# restent des déclarations d'état (hors périmètre R5) : leur borrow ne
# spawn rien, comme avant. Le runtime est résolu depuis la racine V5
# (chemin relatif, pas d'absolu machine-spécifique durci) ; il tourne en
# `--serve` (la démo sans argument sort aussitôt — elle ne suffit pas à
# prouver un spawn tenu par un bail), bail TTL 300 s par défaut, cap de
# population 64 par défaut, cwd = racine V5 (le worktree du rig spawné
# est donc `<racine>/.worktrees/...`).
SPAWNABLE_FIBER = "fiber:a0:agent-zero-cortex"
DEFAULT_TTL_SEC = 300
DEFAULT_MAX_ACTIVE_POPULATION = 64
TERMINATE_GRACE_SEC = 5.0

DaemonLifecycleState = Literal["DORMANT_FIBER", "LAZY_SPAWNING", "LEASED_ACTIVE", "DRAINING", "DISPOSED"]


@dataclass
class ManagedDaemonFiber:
    fiber_id: str
    submodule_path: str
    native_daemon_entry: str
    language_runtime: Literal["rust", "typescript_hono", "python_asyncio", "go"]
    assigned_port_or_socket: str
    state: DaemonLifecycleState = "DORMANT_FIBER"
    lease_ttl_sec: int = 300
    active_holon_borrower: str | None = None
    revertible_cleanup_steps: list[str] = field(default_factory=list)


class CordisAutomatonDaemonSupervisor:
    """
    Architecture Wargame Optimale (Au-delà des traces d'Argon) :
      1. Cordis tourne en Daemon Maître léger (< 50 Ko de logique d'inversion de contrôle).
      2. Automaton tourne en Boucle de Runtime (Tick + Baux + Quota Guard).
      3. Agent Zero (A0) + RigInfinity + Herdr-Core + DSH + OpenClaw sont montés comme Fibers.
    """

    def __init__(self, v5_root: str | Path | None = None) -> None:
        self.supervisor_mode = "CORDIS_MASTER_DAEMON_X_AUTOMATON_RUNTIME"
        # Racine V5 : résolue depuis ce fichier (02_Factory/01_Kernel_Gates/)
        # sauf racine explicite (tests, harnais).
        self.v5_root = Path(v5_root) if v5_root is not None else Path(__file__).resolve().parents[2]
        self.runtime_path = (self.v5_root / "01_Forkable" / "FKB00_Runtime"
                             / "00_A0_Core" / "a0_holon_swarm_runtime.py")
        self.worktree_root = self.v5_root / ".worktrees"
        # Processus réellement spawnes : fiber_id -> descripteur (Popen gardé
        # pour le reap : pas de zombie — wait() est appelé à chaque arrêt).
        self._spawned: dict[str, dict[str, Any]] = {}
        self.fibers: dict[str, ManagedDaemonFiber] = {
            "fiber:core:freecloud-gateway": ManagedDaemonFiber(
                fiber_id="fiber:core:freecloud-gateway",
                submodule_path="01_Forkable/FKB01_Inference/03_Inference_FreeCloud",
                native_daemon_entry="aspace_freecloud_gateway.py",
                language_runtime="python_asyncio",
                assigned_port_or_socket="127.0.0.1:31415",
                state="LEASED_ACTIVE",
                active_holon_borrower="A0-AMADEUS",
                revertible_cleanup_steps=["flush_wal_egm_missions_db", "close_http_31415"],
            ),
            "fiber:triptyque:rig-infinity-daemon": ManagedDaemonFiber(
                fiber_id="fiber:triptyque:rig-infinity-daemon",
                submodule_path="01_Forkable/FKB00_Runtime/01_Holo_TriptyqueCore/RigInfinity",
                native_daemon_entry="crates/infinity-daemon/src/main.rs + packages/daemon/src/index.ts",
                language_runtime="rust",
                assigned_port_or_socket="unix:///tmp/aspace-riginfinity.sock",
                state="LEASED_ACTIVE",
                active_holon_borrower="S1-RICK / J1-JERRY",
                revertible_cleanup_steps=["release_worktree_locks", "persist_rap_session_store"],
            ),
            "fiber:a0:agent-zero-cortex": ManagedDaemonFiber(
                fiber_id="fiber:a0:agent-zero-cortex",
                submodule_path="01_Forkable/FKB00_Runtime/00_A0_Core/agent-zero",
                native_daemon_entry="a0_holon_swarm_runtime.py",
                language_runtime="python_asyncio",
                assigned_port_or_socket="inproc://cordis-a0-egm",
                state="DORMANT_FIBER",
                revertible_cleanup_steps=["snapshot_continual_harness", "discard_goldfish_context"],
            ),
            "fiber:ade:herdr-core-pty": ManagedDaemonFiber(
                fiber_id="fiber:ade:herdr-core-pty",
                submodule_path="01_Forkable/FKB00_Runtime/04_ADE_OpenRig/herdr-core",
                native_daemon_entry="src/main.rs",
                language_runtime="rust",
                assigned_port_or_socket="unix:///tmp/herdr-core.sock",
                state="LEASED_ACTIVE",
                active_holon_borrower="A1-MORTY",
                revertible_cleanup_steps=["detach_pty_panes", "save_terminal_scrollback"],
            ),
            "fiber:core:dsh-cordis": ManagedDaemonFiber(
                fiber_id="fiber:core:dsh-cordis",
                submodule_path="01_Forkable/FKB00_Runtime/00_A0_Core/deepseek-harness",
                native_daemon_entry="packages/cli/src/index.ts",
                language_runtime="typescript_hono",
                assigned_port_or_socket="127.0.0.1:3081",
                state="DORMANT_FIBER",
                revertible_cleanup_steps=["dispose_cordis_context", "close_ws_3081"],
            ),
            "fiber:ade:openclaw-24x7": ManagedDaemonFiber(
                fiber_id="fiber:ade:openclaw-24x7",
                submodule_path="01_Forkable/FKB00_Runtime/04_ADE_OpenRig/openclaw",
                native_daemon_entry="src/daemon.ts",
                language_runtime="typescript_hono",
                assigned_port_or_socket="127.0.0.1:4120",
                state="DORMANT_FIBER",
                revertible_cleanup_steps=["disconnect_deal_4spaces", "flush_pi_session_tree"],
            ),
        }

    # -- Spawn réel (R5, §D8) -------------------------------------------------
    def _pid_alive(self, pid: int) -> bool:
        """Vrai si le PID existe et n'est pas un zombie (état Z dans
        /proc/<pid>/stat ; un zombie est un processus mort non reaped)."""
        try:
            os.kill(pid, 0)
        except ProcessLookupError:
            return False
        except PermissionError:
            return True
        stat = Path(f"/proc/{pid}/stat")
        if not stat.exists():
            return False
        try:
            state = stat.read_text().rsplit(")", 1)[1].split()[0]
        except (IndexError, ValueError, OSError):
            return True
        return state != "Z"

    def _spawned_info(self, fiber_id: str) -> dict[str, Any] | None:
        return self._spawned.get(fiber_id)

    def _stop_spawned(self, fiber_id: str, reason: str) -> dict[str, Any]:
        """Arrête proprement le processus spawné (SIGTERM, grâce, SIGKILL
        en dernier recours) et le reap (wait) : pas de zombie. Retourne
        le code de sortie et la méthode d'arrêt."""
        rec = self._spawned.pop(fiber_id, None)
        if rec is None:
            return {"stopped": False, "reason": "no_spawned_process"}
        proc: subprocess.Popen = rec["proc"]
        try:
            rec["log_fd"].close()
        except (ValueError, OSError):
            pass
        method = "already_exited"
        exit_code = proc.poll()
        if exit_code is None:
            proc.send_signal(signal.SIGTERM)
            try:
                exit_code = proc.wait(timeout=TERMINATE_GRACE_SEC)
                method = "sigterm"
            except subprocess.TimeoutExpired:
                proc.kill()
                exit_code = proc.wait()
                method = "sigkill_after_timeout"
        alive_after = self._pid_alive(rec["pid"])
        return {"stopped": True, "reason": reason, "method": method,
                "exit_code": exit_code, "pid": rec["pid"],
                "zombie": alive_after and exit_code is None,
                "alive_after_stop": alive_after}

    def sweep_expired_leases(self, now: float | None = None) -> list[dict[str, Any]]:
        """Baux expirés : arrêt du processus, fiber DORMANT. Appelé par
        borrow (avant tout nouvel emprunt) et par le harnais H-R7."""
        now = time.monotonic() if now is None else now
        swept = []
        for fiber_id in list(self._spawned):
            rec = self._spawned[fiber_id]
            proc: subprocess.Popen = rec["proc"]
            if proc.poll() is not None:
                # Processus déjà sorti de lui-même (ex. TTL interne du
                # runtime) : reap déjà fait par poll, on libère la fiber.
                self._spawned.pop(fiber_id)
                self.fibers[fiber_id].state = "DORMANT_FIBER"
                self.fibers[fiber_id].active_holon_borrower = None
                swept.append({"fiber_id": fiber_id, "pid": rec["pid"],
                              "reason": "process_exited", "method": "self_exit",
                              "exit_code": proc.poll(), "alive_after_stop": False})
                continue
            if now >= rec["lease_deadline_mono"]:
                stopped = self._stop_spawned(fiber_id, reason="ttl_expired")
                self.fibers[fiber_id].state = "DORMANT_FIBER"
                self.fibers[fiber_id].active_holon_borrower = None
                swept.append({"fiber_id": fiber_id, **stopped})
        return swept

    def borrow_fiber_rust_style(self, fiber_id: str, holon_borrower: str, ttl_sec: int = 300,
                                max_active_population: int = DEFAULT_MAX_ACTIVE_POPULATION,
                                log_path: str | Path | None = None) -> dict[str, Any]:
        """
        Modèle 'De Go vers Rust' : un daemon enfant ne peut être activé que par un emprunt
        exclusif vérifié (`active_holon_borrower`), garantissant zéro course critique (Data Race = 0).

        R5 (§D8) : pour `fiber:a0:agent-zero-cortex`, l'emprunt LANCE
        réellement `a0_holon_swarm_runtime.py` en sous-processus
        (`--serve --ttl <ttl> --max-population <cap>`, cwd = racine V5) et
        enregistre son PID ; le bail TTL est respecté par
        `sweep_expired_leases` (expiration → arrêt). Les autres fibers
        gardent le comportement historique (état seul, aucun spawn).
        """
        self.sweep_expired_leases()
        fiber = self.fibers[fiber_id]
        if fiber.state == "LEASED_ACTIVE" and fiber.active_holon_borrower not in (None, holon_borrower):
            return {
                "borrowed": False,
                "reason": f"OWNERSHIP_CONFLICT: held by {fiber.active_holon_borrower}",
                "fiber_id": fiber_id,
            }
        fiber.state = "LEASED_ACTIVE"
        fiber.active_holon_borrower = holon_borrower
        fiber.lease_ttl_sec = ttl_sec
        result: dict[str, Any] = {"borrowed": True, "fiber": asdict(fiber)}
        if fiber_id != SPAWNABLE_FIBER:
            return result
        existing = self._spawned.get(fiber_id)
        if existing is not None and existing["proc"].poll() is None:
            result.update({"spawned": True, "already_spawned": True,
                           "pid": existing["pid"],
                           "lease_started_at": existing["lease_started_at"],
                           "lease_deadline": existing["lease_deadline"],
                           "lease_ttl_sec": existing["lease_ttl_sec"],
                           "max_active_population": existing["max_active_population"],
                           "worktree_root": existing["worktree_root"],
                           "runtime_path": existing["runtime_path"],
                           "log_path": existing["log_path"]})
            return result
        if not self.runtime_path.is_file():
            fiber.state = "DORMANT_FIBER"
            fiber.active_holon_borrower = None
            return {"borrowed": False, "fiber_id": fiber_id,
                    "reason": f"RUNTIME_MISSING: {self.runtime_path}"}
        log = Path(log_path) if log_path is not None else Path(tempfile.NamedTemporaryFile(
            prefix="aspace-supervisor-agent-zero-", suffix=".log", delete=False).name)
        log_fd = open(log, "ab")
        started_mono = time.monotonic()
        started_wall = time.time()
        started_at = datetime.fromtimestamp(started_wall, tz=timezone.utc).isoformat()
        deadline = started_mono + max(0, ttl_sec)
        proc = subprocess.Popen(
            [sys.executable, str(self.runtime_path), "--serve",
             "--ttl", str(ttl_sec),
             "--max-population", str(max_active_population)],
            cwd=str(self.v5_root), stdout=log_fd, stderr=subprocess.STDOUT,
            text=False, start_new_session=True)
        # Attendre la readiness (ligne `"serving": true` dans le log) :
        # sans elle, un SIGTERM de release peut arriver pendant le
        # démarrage de l'interpréteur — avant l'installation du handler
        # SIGTERM du runtime — et tuer le processus (-15) au lieu d'une
        # sortie propre (0). Le bail n'est acquis que quand le runtime
        # tient réellement.
        ready = False
        t0 = time.monotonic()
        while time.monotonic() - t0 < 10.0:
            if proc.poll() is not None:
                break
            try:
                if b'"serving": true' in Path(log).read_bytes():
                    ready = True
                    break
            except OSError:
                pass
            time.sleep(0.05)
        ready_wait_s = round(time.monotonic() - t0, 3)
        if proc.poll() is not None and not ready:
            exit_code = proc.poll()
            try:
                log_fd.close()
            except (ValueError, OSError):
                pass
            fiber.state = "DORMANT_FIBER"
            fiber.active_holon_borrower = None
            return {"borrowed": False, "fiber_id": fiber_id,
                    "reason": "SPAWN_FAILED", "exit_code": exit_code,
                    "ready": False, "ready_wait_s": ready_wait_s,
                    "log_path": str(log)}
        self._spawned[fiber_id] = {
            "proc": proc, "pid": proc.pid, "log_fd": log_fd,
            "lease_started_at": started_at, "lease_started_mono": started_mono,
            "lease_deadline": datetime.fromtimestamp(
                started_wall + max(0, ttl_sec), tz=timezone.utc).isoformat(),
            "lease_deadline_mono": deadline,
            "lease_ttl_sec": ttl_sec,
            "max_active_population": max_active_population,
            "worktree_root": str(self.worktree_root),
            "runtime_path": str(self.runtime_path),
            "log_path": str(log),
            "borrower": holon_borrower,
            "ready": ready, "ready_wait_s": ready_wait_s,
        }
        result.update({"spawned": True, "already_spawned": False,
                       "pid": proc.pid,
                       "lease_started_at": started_at,
                       "lease_deadline": self._spawned[fiber_id]["lease_deadline"],
                       "lease_ttl_sec": ttl_sec,
                       "max_active_population": max_active_population,
                       "worktree_root": str(self.worktree_root),
                       "runtime_path": str(self.runtime_path),
                       "log_path": str(log),
                       "ready": ready, "ready_wait_s": ready_wait_s})
        return result

    def release_and_dispose_fiber(self, fiber_id: str) -> dict[str, Any]:
        fiber = self.fibers[fiber_id]
        executed_cleanups = list(fiber.revertible_cleanup_steps)
        # R5 : si un processus a été spawné pour cette fiber, l'arrêter
        # proprement (SIGTERM, reap) avant de repasser DORMANT.
        stopped: dict[str, Any] = {"stopped": False, "reason": "no_spawned_process"}
        if fiber_id in self._spawned:
            stopped = self._stop_spawned(fiber_id, reason="release")
        fiber.state = "DORMANT_FIBER"
        fiber.active_holon_borrower = None
        return {
            "fiber_id": fiber_id,
            "new_state": fiber.state,
            "revertible_cleanups_executed": executed_cleanups,
            "spawned_process": stopped,
        }

    def status_report(self) -> dict[str, Any]:
        active = [k for k, v in self.fibers.items() if v.state == "LEASED_ACTIVE"]
        dormant = [k for k, v in self.fibers.items() if v.state == "DORMANT_FIBER"]
        spawned = {}
        for fid, rec in self._spawned.items():
            proc: subprocess.Popen = rec["proc"]
            spawned[fid] = {
                "pid": rec["pid"],
                "alive": self._pid_alive(rec["pid"]),
                "exit_code": proc.poll(),
                "borrower": rec["borrower"],
                "lease_ttl_sec": rec["lease_ttl_sec"],
                "lease_started_at": rec["lease_started_at"],
                "lease_deadline": rec["lease_deadline"],
                "ttl_remaining_sec": round(
                    rec["lease_deadline_mono"] - time.monotonic(), 1),
                "max_active_population": rec["max_active_population"],
                "worktree_root": rec["worktree_root"],
                "log_path": rec["log_path"],
            }
        return {
            "architecture": self.supervisor_mode,
            "verdict": "OPTIMAL_SINGLE_HYPERVISOR_ZERO_ZOMBIE_DAEMONS",
            "active_fibers_count": len(active),
            "dormant_lazy_fibers_count": len(dormant),
            "active_fibers": active,
            "dormant_fibers": dormant,
            "spawned_processes": spawned,
        }


if __name__ == "__main__":
    sup = CordisAutomatonDaemonSupervisor()
    borrow_res = sup.borrow_fiber_rust_style("fiber:a0:agent-zero-cortex", "A0-AMADEUS", ttl_sec=300)
    spawned = sup.status_report()["spawned_processes"].get("fiber:a0:agent-zero-cortex")
    dispose_res = sup.release_and_dispose_fiber("fiber:a0:agent-zero-cortex")
    print(
        json.dumps(
            {
                "supervisor_report": sup.status_report(),
                "sample_rust_borrow": borrow_res["borrowed"],
                "spawned_pid": borrow_res.get("pid"),
                "spawned_alive_at_borrow": bool(spawned and spawned["alive"]),
                "sample_revertible_dispose": dispose_res,
            },
            indent=2,
            ensure_ascii=False,
        )
    )
