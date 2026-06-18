#!/usr/bin/env python3
# CRONOS SCHEDULER v4.0 — SRE-GRADE AUTONOMOUS DAEMON
# Execution Level: C5-REAL
import os
import sys
import time
import sqlite3
import asyncio
import subprocess
import fcntl
import re
import signal
import json
from datetime import datetime, timezone, timedelta

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = "/Users/borjafernandezangulo/.cortex/scheduler.db"
SCHEDULER_LOCK_PATH = "/tmp/cronos_scheduler.lock"
LOG_DIR = "/tmp/cronos_logs"
HEARTBEAT_PATH = "/Users/borjafernandezangulo/.cortex/cronos_heartbeat.json"

os.makedirs(LOG_DIR, exist_ok=True)
os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

def apply_resource_limits(cmd_list):
    return ["/usr/bin/nice", "-n", "10"] + cmd_list

def rotate_log(log_path):
    if os.path.exists(log_path) and os.path.getsize(log_path) > 50 * 1024 * 1024:
        try:
            os.rename(log_path, log_path + ".old")
        except Exception:
            pass

TASKS = {
    "exergy_monitor": {
        "command": apply_resource_limits(["/bin/zsh", "/Users/borjafernandezangulo/.cortex/scripts/cron_exergy_monitor.sh"]),
        "base_interval": 300,
        "type": "interval",
        "lock_file": "/tmp/cronos_exergy_monitor.lock",
        "timeout_seconds": 60,
        "description": "Calcula y purga anergía en los logs del sistema"
    },
    "v_omega_shield": {
        "command": apply_resource_limits(["python3", os.path.join(ROOT_DIR, "scripts", "v_omega_shield.py"), "--kill"]),
        "base_interval": 300,
        "type": "interval",
        "lock_file": "/tmp/cronos_v_omega_shield.lock",
        "timeout_seconds": 60,
        "description": "Escudo de conexiones de red no permitidas"
    },
    "board_of_directors": {
        "command": apply_resource_limits(["python3", os.path.join(ROOT_DIR, "kernel", "board_of_directors.py")]),
        "base_interval": 3600,
        "type": "interval",
        "lock_file": "/tmp/cronos_board_of_directors.lock",
        "timeout_seconds": 3600,
        "description": "Orquestación asíncrona de los ejecutivos del swarm"
    },
    "death_protocol": {
        "command": apply_resource_limits(["/bin/zsh", "/Users/borjafernandezangulo/.cortex/scripts/cron_death_protocol.sh", ROOT_DIR]),
        "cron_time": "03:00",
        "type": "daily",
        "lock_file": "/tmp/cronos_death_protocol.lock",
        "timeout_seconds": 300,
        "description": "Escaneo y purga de archivos inactivos por más de 7 días"
    }
}

class FileLock:
    def __init__(self, lock_path):
        self.lock_path = lock_path
        self.fd = None

    def acquire(self):
        try:
            self.fd = open(self.lock_path, "w")
            fcntl.flock(self.fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
            return True
        except (IOError, OSError):
            if self.fd:
                try:
                    self.fd.close()
                except Exception:
                    pass
                self.fd = None
            return False

    def release(self):
        if self.fd:
            try:
                fcntl.flock(self.fd, fcntl.LOCK_UN)
                self.fd.close()
            except Exception:
                pass
            self.fd = None

shutdown_event = asyncio.Event()
active_tasks_state = {}

def get_db_connection():
    try:
        conn = sqlite3.connect(DB_PATH, timeout=5.0)
        conn.execute("PRAGMA journal_mode=WAL;")
        conn.row_factory = sqlite3.Row
        conn.execute("SELECT 1")
        return conn
    except sqlite3.DatabaseError:
        print(f"[{datetime.now(timezone.utc).isoformat()}] [CRONOS-RECOVERY] Corrupción en DB. Purgando y recreando...")
        try:
            os.remove(DB_PATH)
        except OSError:
            pass
        conn = sqlite3.connect(DB_PATH, timeout=5.0)
        conn.execute("PRAGMA journal_mode=WAL;")
        conn.row_factory = sqlite3.Row
        return conn

def init_db_and_recover():
    with get_db_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS task_runs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task_name TEXT NOT NULL,
                start_time TEXT NOT NULL,
                end_time TEXT,
                duration_seconds REAL,
                status TEXT NOT NULL,
                output TEXT,
                error TEXT
            );
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS scheduler_state (
                key TEXT PRIMARY KEY,
                value TEXT,
                updated_at TEXT NOT NULL
            );
        """)
        cursor = conn.cursor()
        cursor.execute("UPDATE task_runs SET status = 'ORPHANED_CRASH', error = 'Daemon died without cleanup' WHERE status = 'RUNNING'")
        if cursor.rowcount > 0:
            print(f"[{datetime.now(timezone.utc).isoformat()}] [CRONOS-RECOVERY] Sanados {cursor.rowcount} registros huérfanos (ORPHANED_CRASH).")
        conn.commit()

def emit_heartbeat():
    state = {
        "status": "ALIVE" if not shutdown_event.is_set() else "SHUTTING_DOWN",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "active_tasks_count": len(active_tasks_state),
        "active_tasks": list(active_tasks_state.values())
    }
    try:
        with open(HEARTBEAT_PATH + ".tmp", "w") as f:
            json.dump(state, f)
        os.rename(HEARTBEAT_PATH + ".tmp", HEARTBEAT_PATH)
    except Exception as e:
        print(f"[CRONOS-HEARTBEAT-ERR] Fallo al emitir heartbeat: {e}")

def force_abort_active_tasks():
    try:
        with get_db_connection() as conn:
            for run_id, name in active_tasks_state.items():
                conn.execute(
                    "UPDATE task_runs SET status = 'ABORTED_SIGTERM', end_time = ?, error = 'Terminated by OS signal' WHERE id = ?",
                    (datetime.now(timezone.utc).isoformat(), run_id)
                )
            conn.commit()
            print(f"[CRONOS-SHUTDOWN] Marcados {len(active_tasks_state)} procesos como ABORTED_SIGTERM.")
    except Exception as e:
        print(f"[CRONOS-SHUTDOWN-ERR] Fallo al actualizar DB en shutdown: {e}")

def prune_db():
    try:
        with get_db_connection() as conn:
            limit_date = (datetime.now(timezone.utc) - timedelta(days=7)).isoformat()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM task_runs WHERE start_time < ?", (limit_date,))
            deleted = cursor.rowcount
            conn.commit()
            if deleted > 0:
                print(f"[{datetime.now(timezone.utc).isoformat()}] [CRONOS-APOPTOSIS] Purgados {deleted} registros obsoletos del Ledger.")
    except Exception as e:
        print(f"[CRONOS-DB-ERR] Fallo al purgar DB: {e}")

async def get_exergy_scaling_factor() -> float:
    try:
        cmd = ["python3", os.path.join(ROOT_DIR, "exergy_sensor.py"), "--workspace"]
        proc = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=ROOT_DIR
        )
        stdout, _ = await proc.communicate()
        output = stdout.decode("utf-8", errors="ignore")
        
        match = re.search(r"Global Workspace Exergy Index:\s*([0-9.]+)", output)
        if match:
            idx = float(match.group(1))
            if idx < 65.0:
                return 2.0
            elif idx < 75.0:
                return 1.5
        return 1.0
    except Exception:
        return 1.0

def signal_handler(sig, frame):
    print(f"\n[{datetime.now(timezone.utc).isoformat()}] [CRONOS-SHUTDOWN] Señal {sig} recibida. Iniciando muerte limpia...")
    shutdown_event.set()
    force_abort_active_tasks()
    emit_heartbeat()
    sys.exit(0)

async def run_task(name: str, config: dict):
    lock = FileLock(config["lock_file"])
    if not lock.acquire():
        print(f"[{datetime.now(timezone.utc).isoformat()}] [CRONOS-ERR] Tarea {name} bloqueada por Mutex. Abortando colisión.")
        return

    start_time = datetime.now(timezone.utc).isoformat()
    run_id = None
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO task_runs (task_name, start_time, status) VALUES (?, ?, ?)",
                (name, start_time, "RUNNING")
            )
            conn.commit()
            run_id = cursor.lastrowid
            active_tasks_state[run_id] = name
    except Exception as e:
        print(f"[CRONOS-DB-ERR] Fallo al insertar {name}: {e}")

    proc = None
    status = "SUCCESS"
    t_start = time.time()
    
    out_log_path = os.path.join(LOG_DIR, f"{name}.out")
    err_log_path = os.path.join(LOG_DIR, f"{name}.err")
    rotate_log(out_log_path)
    rotate_log(err_log_path)

    try:
        with open(out_log_path, "w") as out_fd, open(err_log_path, "w") as err_fd:
            proc = await asyncio.create_subprocess_exec(
                *config["command"],
                stdout=out_fd,
                stderr=err_fd,
                cwd=ROOT_DIR
            )
            
            kill_task = asyncio.create_task(shutdown_event.wait())
            wait_task = asyncio.create_task(asyncio.wait_for(proc.wait(), timeout=config.get("timeout_seconds", 3600)))
            
            done, pending = await asyncio.wait([kill_task, wait_task], return_when=asyncio.FIRST_COMPLETED)
            
            if kill_task in done:
                print(f"[CRONOS-SHUTDOWN] Asesinando proceso hijo {name} (PID: {proc.pid})...")
                proc.terminate()
                await asyncio.sleep(1)
                if proc.returncode is None:
                    proc.kill()
                status = "ABORTED_SIGTERM"
            else:
                try:
                    await wait_task
                    if proc.returncode != 0:
                        status = "FAILED"
                except asyncio.TimeoutError:
                    print(f"[{datetime.now(timezone.utc).isoformat()}] [CRONOS-ERR] Tarea {name} (PID: {proc.pid}) excedió timeout de {config.get('timeout_seconds')}s. Ejecutando SIGKILL.")
                    proc.kill()
                    status = "TIMEOUT_KILL"
            
        duration = time.time() - t_start
    except Exception as e:
        status = "CRASHED"
        duration = time.time() - t_start
        print(f"[{datetime.now(timezone.utc).isoformat()}] [CRONOS-ERR] Excepción letal en {name}: {e}")
    finally:
        lock.release()
        if run_id in active_tasks_state:
            del active_tasks_state[run_id]

    end_time = datetime.now(timezone.utc).isoformat()
    if run_id and not shutdown_event.is_set():
        try:
            with get_db_connection() as conn:
                conn.execute(
                    """
                    UPDATE task_runs 
                    SET end_time = ?, duration_seconds = ?, status = ?, output = ?, error = ?
                    WHERE id = ?
                    """,
                    (end_time, duration, status, f"Log: {out_log_path}", f"Log: {err_log_path}", run_id)
                )
                conn.commit()
        except Exception as e:
            print(f"[CRONOS-DB-ERR] Fallo al actualizar {name}: {e}")

async def scheduler_loop():
    print(f"[{datetime.now(timezone.utc).isoformat()}] [CRONOS] Inicializando Bucle SRE-GRADE...")
    init_db_and_recover()
    emit_heartbeat()
    
    last_run_times = {}
    daily_completed_date = {}
    
    scaling_factor = 1.0
    last_exergy_check = 0.0
    last_heartbeat = 0.0

    while not shutdown_event.is_set():
        now_ts = time.time()
        now_dt = datetime.now(timezone.utc)
        current_date_str = now_dt.strftime("%Y-%m-%d")
        current_time_str = now_dt.strftime("%H:%M")
        
        if now_ts - last_heartbeat >= 10:
            emit_heartbeat()
            last_heartbeat = now_ts

        if now_ts - last_exergy_check >= 3600:
            scaling_factor = await get_exergy_scaling_factor()
            last_exergy_check = now_ts
            prune_db()
            try:
                with get_db_connection() as conn:
                    conn.execute(
                        "INSERT INTO scheduler_state (key, value, updated_at) VALUES (?, ?, ?) "
                        "ON CONFLICT(key) DO UPDATE SET value=excluded.value, updated_at=excluded.updated_at",
                        ("exergy_scaling_factor", f"{scaling_factor}", now_dt.isoformat())
                    )
                    conn.commit()
            except Exception:
                pass

        for name, config in TASKS.items():
            if config["type"] == "interval":
                is_critical = name in ("v_omega_shield", "exergy_monitor")
                actual_interval = config["base_interval"]
                if not is_critical:
                    actual_interval = int(config["base_interval"] * scaling_factor)
                
                last_run = last_run_times.get(name, 0.0)
                if now_ts - last_run >= actual_interval:
                    last_run_times[name] = now_ts
                    asyncio.create_task(run_task(name, config))
                    
            elif config["type"] == "daily":
                if current_time_str == config["cron_time"] and daily_completed_date.get(name) != current_date_str:
                    daily_completed_date[name] = current_date_str
                    asyncio.create_task(run_task(name, config))
                    
        try:
            await asyncio.wait_for(shutdown_event.wait(), timeout=1.0)
        except asyncio.TimeoutError:
            pass

def main():
    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)

    scheduler_lock = FileLock(SCHEDULER_LOCK_PATH)
    if not scheduler_lock.acquire():
        print(f"[{datetime.now(timezone.utc).isoformat()}] [CRONOS-ERR] Planificador ya activo. Previniendo colapso multiversal. Abortando.")
        sys.exit(1)
        
    print(f"[{datetime.now(timezone.utc).isoformat()}] [CRONOS] Demonio SRE-GRADE Iniciado. Aislamiento y Telemetría habilitados.")
    try:
        asyncio.run(scheduler_loop())
    except Exception as e:
        print(f"[CRONOS-ERR] Fallo general del planificador: {e}")
    finally:
        print(f"[{datetime.now(timezone.utc).isoformat()}] [CRONOS-SHUTDOWN] Liberando Mutex Físico y cerrando sockets.")
        emit_heartbeat()
        scheduler_lock.release()

if __name__ == "__main__":
    main()
