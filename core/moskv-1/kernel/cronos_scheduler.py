#!/usr/bin/env python3
# CRONOS SCHEDULER v8.0 — CQRS EVENT ENVELOPE V2 COMPLIANT
# Execution Level: C5-REAL
import os, sys, time, asyncio, subprocess, fcntl, re, signal, json, shlex
from datetime import datetime, timezone, timedelta

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(ROOT_DIR)
from kernel import cortex_event_log

SCHEDULER_LOCK_PATH = "/tmp/cronos_scheduler.lock"
LOG_DIR = "/tmp/cronos_logs"
HEARTBEAT_PATH = "/Users/borjafernandezangulo/.cortex/cronos_heartbeat.json"

os.makedirs(LOG_DIR, exist_ok=True)

def apply_resource_limits(cmd_list, profile="worker_base"):
    cmd_str = " ".join(shlex.quote(arg) for arg in cmd_list)
    profile_path = os.path.join(ROOT_DIR, "profiles", f"{profile}.sb")
    sandbox_wrapper = f"/usr/bin/sandbox-exec -f {shlex.quote(profile_path)} {cmd_str}"
    return ["/bin/zsh", "-c", f"ulimit -v 1572864; ulimit -t 3600; exec {sandbox_wrapper}"]

def rotate_log(log_path):
    if os.path.exists(log_path) and os.path.getsize(log_path) > 50 * 1024 * 1024:
        try: os.rename(log_path, log_path + ".old")
        except Exception: pass

TASKS = {
    "event_projector": {
        "command": ["python3", os.path.join(ROOT_DIR, "kernel", "event_projector.py")],
        "base_interval": 10,
        "type": "interval",
        "lock_file": "/tmp/cronos_event_projector.lock",
        "timeout_seconds": 60,
        "description": "Materializa EventEnvelope V2 a SQLite asíncronamente"
    },
    "board_of_directors": {
        "command": apply_resource_limits(["python3", os.path.join(ROOT_DIR, "kernel", "board_of_directors.py")], profile="worker_network"),
        "base_interval": 3600,
        "type": "interval",
        "lock_file": "/tmp/cronos_board_of_directors.lock",
        "timeout_seconds": 3600,
        "description": "Swarm executive orchestration"
    },
    "reddit_traffic_engine": {
        "command": apply_resource_limits(["python3", os.path.join(ROOT_DIR, "..", "apps", "moskv_reddit_engine", "traffic_orchestrator.py")], profile="worker_network"),
        "base_interval": 21600,
        "type": "interval",
        "lock_file": "/tmp/cronos_reddit_traffic.lock",
        "timeout_seconds": 600,
        "description": "ZEO-GTM Lead Generation & Payload Syndication"
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
                try: self.fd.close()
                except: pass
                self.fd = None
            return False
    def release(self):
        if self.fd:
            try:
                fcntl.flock(self.fd, fcntl.LOCK_UN)
                self.fd.close()
            except: pass
            self.fd = None

shutdown_event = asyncio.Event()
active_tasks_state = {}

def init_db_and_recover():
    cortex_event_log.append_event(
        event_type="SYSTEM_RECOVERY", 
        aggregate_id="daemon_lifecycle", 
        aggregate_type="System",
        payload={"action": "BOOT_RECOVERY_TRIGGERED"},
        correlation_id=f"boot_{int(time.time()*1000)}"
    )

def emit_heartbeat():
    state = {
        "status": "ALIVE" if not shutdown_event.is_set() else "SHUTTING_DOWN",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "active_tasks_count": len(active_tasks_state),
        "active_tasks": list(active_tasks_state.values())
    }
    try:
        with open(HEARTBEAT_PATH + ".tmp", "w") as f: json.dump(state, f)
        os.rename(HEARTBEAT_PATH + ".tmp", HEARTBEAT_PATH)
    except: pass

def force_abort_active_tasks():
    cortex_event_log.append_event(
        event_type="SYSTEM_SHUTDOWN", 
        aggregate_id="daemon_lifecycle", 
        aggregate_type="System",
        payload={"action": "ABORTED_SIGTERM", "tasks_aborted": list(active_tasks_state.values())},
        correlation_id=f"shutdown_{int(time.time()*1000)}"
    )

async def get_exergy_scaling_factor() -> float:
    try:
        cmd = ["python3", os.path.join(ROOT_DIR, "exergy_sensor.py"), "--workspace"]
        proc = await asyncio.create_subprocess_exec(*cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE, cwd=ROOT_DIR)
        stdout, _ = await proc.communicate()
        match = re.search(r"Global Workspace Exergy Index:\s*([0-9.]+)", stdout.decode("utf-8", errors="ignore"))
        if match:
            idx = float(match.group(1))
            if idx < 65.0: return 2.0
            elif idx < 75.0: return 1.5
        return 1.0
    except: return 1.0

def signal_handler(sig, frame):
    shutdown_event.set()
    force_abort_active_tasks()
    emit_heartbeat()
    sys.exit(0)

async def run_task(name: str, config: dict):
    lock = FileLock(config["lock_file"])
    if not lock.acquire(): return

    start_time = datetime.now(timezone.utc).isoformat()
    correlation_id = f"run_{int(time.time()*1000)}_{name}"
    
    ev = cortex_event_log.append_event(
        event_type="TASK_STARTED", 
        aggregate_id=name, 
        aggregate_type="Task",
        payload={"start_time": start_time},
        correlation_id=correlation_id
    )
    
    active_tasks_state[correlation_id] = name

    proc = None
    status = "SUCCESS"
    t_start = time.time()
    out_log_path = os.path.join(LOG_DIR, f"{name}.out")
    err_log_path = os.path.join(LOG_DIR, f"{name}.err")
    rotate_log(out_log_path)
    rotate_log(err_log_path)

    async def stream_and_cap(stream, filepath, max_bytes=50*1024*1024):
        written = 0
        capped = False
        with open(filepath, "ab") as fd:
            while True:
                try:
                    chunk = await stream.read(8192)
                    if not chunk: break
                    if written < max_bytes:
                        fd.write(chunk)
                        written += len(chunk)
                    elif not capped:
                        fd.write(b"\n[CRONOS-ERR] LOG CEILING REACHED (50MB).\n")
                        capped = True
                except: break

    try:
        proc = await asyncio.create_subprocess_exec(
            *config["command"], stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE, cwd=ROOT_DIR
        )
        out_task = asyncio.create_task(stream_and_cap(proc.stdout, out_log_path))
        err_task = asyncio.create_task(stream_and_cap(proc.stderr, err_log_path))
        
        kill_task = asyncio.create_task(shutdown_event.wait())
        wait_task = asyncio.create_task(asyncio.wait_for(proc.wait(), timeout=config.get("timeout_seconds", 3600)))
        
        done, pending = await asyncio.wait([kill_task, wait_task], return_when=asyncio.FIRST_COMPLETED)
        if kill_task in done:
            proc.terminate()
            await asyncio.sleep(1)
            if proc.returncode is None: proc.kill()
            status = "ABORTED_SIGTERM"
        else:
            try:
                await wait_task
                if proc.returncode != 0: status = "FAILED"
            except asyncio.TimeoutError:
                proc.kill()
                status = "TIMEOUT_KILL"
        
        await asyncio.gather(out_task, err_task)
        duration = time.time() - t_start
    except:
        status = "CRASHED"
        duration = time.time() - t_start
    finally:
        lock.release()
        if correlation_id in active_tasks_state: del active_tasks_state[correlation_id]

    if not shutdown_event.is_set():
        cortex_event_log.append_event(
            event_type=f"TASK_{status}", 
            aggregate_id=name, 
            aggregate_type="Task",
            payload={"duration_seconds": duration, "end_time": datetime.now(timezone.utc).isoformat(), "output_log": out_log_path, "error_log": err_log_path},
            correlation_id=correlation_id,
            causation_id=ev.event_id
        )

async def scheduler_loop():
    init_db_and_recover()
    emit_heartbeat()
    
    last_run_times = {}
    scaling_factor = 1.0
    last_exergy_check = 0.0
    last_heartbeat = 0.0

    while not shutdown_event.is_set():
        now_ts = time.time()
        
        if now_ts - last_heartbeat >= 10:
            emit_heartbeat()
            last_heartbeat = now_ts

        if now_ts - last_exergy_check >= 3600:
            scaling_factor = await get_exergy_scaling_factor()
            last_exergy_check = now_ts

        for name, config in TASKS.items():
            if config["type"] == "interval":
                actual_interval = config["base_interval"] if name in ("event_projector",) else int(config["base_interval"] * scaling_factor)
                if now_ts - last_run_times.get(name, 0.0) >= actual_interval:
                    last_run_times[name] = now_ts
                    asyncio.create_task(run_task(name, config))
                    
        try: await asyncio.wait_for(shutdown_event.wait(), timeout=1.0)
        except asyncio.TimeoutError: pass

def main():
    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)
    l = FileLock(SCHEDULER_LOCK_PATH)
    if not l.acquire(): sys.exit(1)
    try: asyncio.run(scheduler_loop())
    except: pass
    finally:
        emit_heartbeat()
        l.release()

if __name__ == "__main__": main()
