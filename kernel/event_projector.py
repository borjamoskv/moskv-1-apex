#!/usr/bin/env python3
import os
import json
import sqlite3
from datetime import datetime, timezone
LOG_PATH = "/Users/borjafernandezangulo/.cortex/cortex_events.jsonl"
DB_PATH = "/Users/borjafernandezangulo/.cortex/scheduler.db"
def get_db_connection():
    conn = sqlite3.connect(DB_PATH, timeout=5.0)
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.row_factory = sqlite3.Row
    return conn
def replay_ledger():
    print(f"[{datetime.now(timezone.utc).isoformat()}] [PROJECTOR] Reconstruyendo Estado desde Event Sourcing Ledger...")
    if not os.path.exists(LOG_PATH): return
    with get_db_connection() as conn:
        event_count = 0
        state_cache = {}
        with open(LOG_PATH, "r") as f:
            for line in f:
                if not line.strip(): continue
                event = json.loads(line)
                event_count += 1
                t = event["event_type"]
                p = event["payload"]
                if t == "TASK_STARTED": state_cache[p["task_name"]] = "RUNNING"
                elif t.startswith("TASK_"): state_cache[p.get("task_name", "")] = t.replace("TASK_", "")
        print(f"[{datetime.now(timezone.utc).isoformat()}] [PROJECTOR] Replay Completado. {event_count} eventos procesados.")
if __name__ == "__main__":
    replay_ledger()
