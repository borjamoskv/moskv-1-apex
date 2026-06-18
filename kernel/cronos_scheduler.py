#!/usr/bin/env python3
# CRONOS SCHEDULER v2.0 — ANTI-ENTROPIC BRUTALIST DAEMON
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
from datetime import datetime, timezone, timedelta

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = "/Users/borjafernandezangulo/.cortex/scheduler.db"
SCHEDULER_LOCK_PATH = "/tmp/cronos_scheduler.lock"
LOG_DIR = "/tmp/cronos_logs"

os.makedirs(LOG_DIR, exist_ok=True)

TASKS = {
    "exergy_monitor": {
        "command": ["/bin/zsh", "/Users/borjafernandezangulo/.cortex/scripts/cron_exergy_monitor.sh"],
        "base_interval": 300,
        "type": "interval",
        "lock_file": "/tmp/cronos_exergy_monitor.lock",
        "description": "Calcula y purga anergía en los logs del sistema"
    },
    "v_omega_shield": {
        "command": ["python3", os.path.join(ROOT_DIR, "scripts", "v_omega_shield.py"), "--kill"],
        "base_interval": 300,
        "type": "interval",
        "lock_file": "/tmp/cronos_v_omega_shield.lock",
        "description": "Escudo de conexiones de red no permitidas"
    },
    "board_of_directors": {
        "command": ["python3", os.path.join(ROOT_DIR, "kernel", "board_of_directors.py")],
        "base_interval": 3600,
        "type": "interval",
        "lock_file": "/tmp/cronos_board_of_directors.lock",
        "description": "Orquestación asíncrona de los ejecutivos del swarm"
    },
    "death_protocol": {
        "command": ["/bin/zsh", "/Users/borjafernandezangulo/.cortex/scripts/cron_death_protocol.sh", ROOT_DIR],
        "cron_time": "03:00",
        "type": "daily",
        "lock_file": "/tmp/cronos_death_protocol.lock",
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

def get_db_connection():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH, timeout=5.0)
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
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
        conn.commit()

def prune_db():
    """Apoptosis del Ledger: Evita el crecimiento infinito eliminando registros de más de 7 días."""
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

shutdown_event = asyncio.Event()

def signal_handler(sig, frame):
    print(f"[{datetime.now(timezone.utc).isoformat()}] [CRONOS-SHUTDOWN] Señal {sig} recibida. Iniciando muerte controlada...")
    shutdown_event.set()

async def run_task(name: str, config: dict):
    lock = FileLock(config["lock_file"])
    if not lock.acquire():
        print(f"[{datetime.now(timezone.utc).isoformat()}] [CRONOS-ERR] Tarea {name} bloqueada por Mutex físico. Abortando colisión.")
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
    except Exception as e:
        print(f"[CRONOS-DB-ERR] Fallo al insertar {name}: {e}")

    proc = None
    status = "SUCCESS"
    t_start = time.time()
    
    out_log_path = os.path.join(LOG_DIR, f"{name}.out")
    err_log_path = os.path.join(LOG_DIR, f"{name}.err")

    try:
        with open(out_log_path, "w") as out_fd, open(err_log_path, "w") as err_fd:
            proc = await asyncio.create_subprocess_exec(
                *config["command"],
                stdout=out_fd,
                stderr=err_fd,
                cwd=ROOT_DIR
            )
            
            # Wait for either process to finish or shutdown signal
            kill_task = asyncio.create_task(shutdown_event.wait())
            wait_task = asyncio.create_task(proc.wait())
            
            done, pending = await asyncio.wait([kill_task, wait_task], return_when=asyncio.FIRST_COMPLETED)
            
            if kill_task in done:
                print(f"[CRONOS-SHUTDOWN] Asesinando proceso hijo {name} (PID: {proc.pid})...")
                proc.terminate()
                await asyncio.sleep(1)
                if proc.returncode is None:
                    proc.kill()
                status = "KILLED_BY_SIGNAL"
            else:
                if proc.returncode != 0:
                    status = "FAILED"
            
        duration = time.time() - t_start
    except Exception as e:
        status = "CRASHED"
        duration = time.time() - t_start
        print(f"[{datetime.now(timezone.utc).isoformat()}] [CRONOS-ERR] Excepción letal en {name}: {e}")
    finally:
        lock.release()

    end_time = datetime.now(timezone.utc).isoformat()
    if run_id:
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
    print(f"[{datetime.now(timezone.utc).isoformat()}] [CRONOS] Inicializando Bucle C5-REAL...")
    init_db()
    
    last_run_times = {}
    daily_completed_date = {}
    
    scaling_factor = 1.0
    last_exergy_check = 0.0

    while not shutdown_event.is_set():
        now_ts = time.time()
        now_dt = datetime.now(timezone.utc)
        current_date_str = now_dt.strftime("%Y-%m-%d")
        current_time_str = now_dt.strftime("%H:%M")
        
        if now_ts - last_exergy_check >= 3600:
            scaling_factor = await get_exergy_scaling_factor()
            last_exergy_check = now_ts
            prune_db() # Apoptosis periódica
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

    print(f"[{datetime.now(timezone.utc).isoformat()}] [CRONOS-SHUTDOWN] Bucle finalizado limpiamente.")

def main():
    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)

    scheduler_lock = FileLock(SCHEDULER_LOCK_PATH)
    if not scheduler_lock.acquire():
        print(f"[{datetime.now(timezone.utc).isoformat()}] [CRONOS-ERR] Planificador ya activo. Previniendo colapso multiversal. Abortando.")
        sys.exit(1)
        
    print(f"[{datetime.now(timezone.utc).isoformat()}] [CRONOS] Demonio Brutalista Iniciado.")
    try:
        asyncio.run(scheduler_loop())
    except KeyboardInterrupt:
        pass
    finally:
        print(f"[{datetime.now(timezone.utc).isoformat()}] [CRONOS-SHUTDOWN] Liberando Mutex Físico.")
        scheduler_lock.release()

if __name__ == "__main__":
    main()
