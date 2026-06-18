#!/usr/bin/env python3
# Execution Level: C5-REAL
import os, json, sqlite3
from datetime import datetime, timezone
import sys
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(ROOT_DIR)
from kernel.cortex_schema import EventEnvelope, generate_uuidv7

LOG_PATH = "/Users/borjafernandezangulo/.cortex/cortex_events.jsonl"
DB_PATH = "/Users/borjafernandezangulo/.cortex/scheduler.db"

def get_db_connection():
    conn = sqlite3.connect(DB_PATH, timeout=5.0)
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.row_factory = sqlite3.Row
    return conn

def init_db(conn):
    conn.execute("""
        CREATE TABLE IF NOT EXISTS projector_checkpoints (
            projector_name TEXT PRIMARY KEY,
            last_global_position INTEGER,
            created_at TEXT
        );
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS processed_events (
            event_id TEXT PRIMARY KEY
        );
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS aggregate_versions (
            aggregate_id TEXT PRIMARY KEY,
            version INTEGER
        );
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS task_runs (
            run_id TEXT PRIMARY KEY,
            task_name TEXT NOT NULL,
            start_time TEXT NOT NULL,
            end_time TEXT,
            duration_seconds REAL,
            status TEXT NOT NULL,
            output TEXT,
            error TEXT
        );
    """)
    conn.commit()

def project_event(cursor, event: EventEnvelope):
    t = event.event_type
    p = event.payload
    task_name = event.aggregate.id
    run_id = event.causality.correlation_id

    if t == "TASK_STARTED":
        cursor.execute(
            "INSERT OR IGNORE INTO task_runs (run_id, task_name, start_time, status) VALUES (?, ?, ?, ?)",
            (run_id, task_name, event.timing.occurred_at, "RUNNING")
        )
    elif t.startswith("TASK_") and t != "TASK_STARTED":
        status = t.replace("TASK_", "")
        cursor.execute(
            """
            UPDATE task_runs 
            SET end_time = ?, duration_seconds = ?, status = ?, output = ?, error = ?
            WHERE run_id = ? AND status = 'RUNNING'
            """,
            (p.get("end_time"), p.get("duration_seconds"), status, p.get("output_log"), p.get("error_log"), run_id)
        )
    elif t == "SYSTEM_RECOVERY":
        cursor.execute("UPDATE task_runs SET status = 'ORPHANED_CRASH', error = 'Daemon died' WHERE status = 'RUNNING'")
    elif t == "SYSTEM_SHUTDOWN":
        cursor.execute("UPDATE task_runs SET status = 'ABORTED_SIGTERM', error = 'OS Signal' WHERE status = 'RUNNING'")

def migrate_event(data: dict) -> EventEnvelope:
    v = data.get("schema_version", 1)
    if v == 1:
        now = datetime.now(timezone.utc).isoformat()
        stream_id = data.get("stream_id", "unknown_task")
        seq = data.get("causal_seq", 0)
        p = data.get("payload", {})
        # correlation_id is critical for the new schema. 
        # Since v1 didn't track it properly as run_id globally, we hash the task_name and seq
        corr_id = f"{stream_id}_run_{seq}"
        return EventEnvelope.from_dict({
            "event_id": generate_uuidv7(), # we assign a new identity physically, but map logically
            "event_type": data.get("event_type", "UNKNOWN"),
            "schema_version": 2,
            "aggregate": {"id": stream_id, "type": "Task", "version": seq},
            "causality": {"correlation_id": corr_id, "causation_id": None},
            "ordering": {"global_position": seq, "stream_position": seq},
            "timing": {"occurred_at": data.get("timestamp", now), "recorded_at": now},
            "idempotency": {"key": data.get("idempotency_key", f"legacy_{seq}")},
            "payload": p,
            "metadata": {"actor": data.get("actor", "cronos"), "source": "migration", "trace_id": corr_id, "tags": []},
            "integrity": {"payload_hash": hashlib.sha256(json.dumps(p, sort_keys=True).encode("utf-8")).hexdigest()}
        })
    return EventEnvelope.from_dict(data)

def apply(cursor, event: EventEnvelope, processed_events: set, aggregate_versions: dict) -> bool:
    if event.event_id in processed_events:
        return False
        
    current_version = aggregate_versions.get(event.aggregate.id, 0)
    if event.aggregate.version <= current_version:
        return False

    project_event(cursor, event)
    
    aggregate_versions[event.aggregate.id] = event.aggregate.version
    processed_events.add(event.event_id)
    return True

def replay_ledger(full_replay=False):
    if not os.path.exists(LOG_PATH): return

    with get_db_connection() as conn:
        init_db(conn)
        cursor = conn.cursor()
        
        if full_replay:
            cursor.execute("DELETE FROM task_runs")
            cursor.execute("DELETE FROM processed_events")
            cursor.execute("DELETE FROM aggregate_versions")
            cursor.execute("DELETE FROM projector_checkpoints")
            conn.commit()

        cursor.execute("SELECT last_global_position FROM projector_checkpoints WHERE projector_name = 'sqlite_tasks'")
        row = cursor.fetchone()
        last_global_position = row["last_global_position"] if row else 0

        processed_events = set()
        cursor.execute("SELECT event_id FROM processed_events")
        for r in cursor.fetchall(): processed_events.add(r["event_id"])

        aggregate_versions = {}
        cursor.execute("SELECT aggregate_id, version FROM aggregate_versions")
        for r in cursor.fetchall(): aggregate_versions[r["aggregate_id"]] = r["version"]

        processed_count = 0
        new_global_pos = last_global_position

        with open(LOG_PATH, "r") as f:
            for line in f:
                if not line.strip(): continue
                data = json.loads(line)
                
                g_pos = data.get("ordering", {}).get("global_position")
                if not g_pos:
                    g_pos = data.get("causal_seq", 0)

                if g_pos <= last_global_position:
                    continue

                event = migrate_event(data)
                
                if apply(cursor, event, processed_events, aggregate_versions):
                    new_global_pos = event.ordering.global_position
                    
                    cursor.execute("INSERT OR IGNORE INTO processed_events (event_id) VALUES (?)", (event.event_id,))
                    cursor.execute(
                        "INSERT INTO aggregate_versions (aggregate_id, version) VALUES (?, ?) ON CONFLICT(aggregate_id) DO UPDATE SET version=excluded.version",
                        (event.aggregate.id, event.aggregate.version)
                    )
                    processed_count += 1

        if processed_count > 0:
            cursor.execute(
                "INSERT INTO projector_checkpoints (projector_name, last_global_position, created_at) VALUES (?, ?, ?) ON CONFLICT(projector_name) DO UPDATE SET last_global_position=excluded.last_global_position, created_at=excluded.created_at",
                ("sqlite_tasks", new_global_pos, datetime.now(timezone.utc).isoformat())
            )
            conn.commit()
            print(f"[{datetime.now(timezone.utc).isoformat()}] [PROJECTOR] Projected {processed_count} events up to GlobalPos {new_global_pos}")

if __name__ == "__main__":
    replay_ledger()
