#!/usr/bin/env python3
# Execution Level: C5-REAL
import os, json
import sys
from datetime import datetime, timezone

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(ROOT_DIR)

from kernel.memory_store import get_memory_db, init_memory_schema, _sign, HMAC_SECRET
from kernel.cortex_schema import EventEnvelope
from kernel.event_projector import migrate_event

LOG_PATH = "/Users/borjafernandezangulo/.cortex/cortex_events.jsonl"

def derive_narrative(event: EventEnvelope) -> str:
    t = event.event_type
    actor = event.metadata.actor or "Unknown"
    if t == "TASK_STARTED":
        return f"Task '{event.aggregate.id}' initiated by {actor}."
    elif t == "TASK_SUCCESS":
        dur = event.payload.get('duration_seconds', 0)
        return f"Task '{event.aggregate.id}' completed successfully in {dur:.2f}s."
    elif t == "TASK_FAILED":
        return f"Task '{event.aggregate.id}' failed. Logs at {event.payload.get('error_log')}."
    elif t == "SYSTEM_SHUTDOWN":
        return "Daemon received OS termination signal."
    elif t == "SYSTEM_RECOVERY":
        return "Daemon recovered from dirty state."
    return f"Raw structural mutation: {t} on {event.aggregate.id}."

def project_memory(cursor, event: EventEnvelope):
    narrative = derive_narrative(event)
    
    payload_to_sign = {
        "event_id": event.event_id,
        "timestamp": event.timing.occurred_at,
        "narrative": narrative
    }
    signature = _sign(payload_to_sign, HMAC_SECRET)
    
    cursor.execute(
        "INSERT OR IGNORE INTO episodic_memory (event_id, timestamp, correlation_id, actor, narrative, hmac_signature) VALUES (?, ?, ?, ?, ?, ?)",
        (event.event_id, event.timing.occurred_at, event.causality.correlation_id, event.metadata.actor, narrative, signature)
    )

def replay_memory_ledger():
    if not os.path.exists(LOG_PATH): return

    with get_memory_db() as conn:
        init_memory_schema()
        cursor = conn.cursor()

        cursor.execute("SELECT last_global_position FROM memory_checkpoints WHERE projector_id = 'semantic_core'")
        row = cursor.fetchone()
        last_global_pos = row["last_global_position"] if row else 0

        new_global_pos = last_global_pos
        processed = 0

        with open(LOG_PATH, "r") as f:
            for line in f:
                if not line.strip(): continue
                data = json.loads(line)
                
                g_pos = data.get("ordering", {}).get("global_position")
                if not g_pos: g_pos = data.get("causal_seq", 0)

                if g_pos <= last_global_pos:
                    continue

                event = migrate_event(data)
                project_memory(cursor, event)
                new_global_pos = event.ordering.global_position
                processed += 1

        if processed > 0:
            cursor.execute(
                "INSERT INTO memory_checkpoints (projector_id, last_global_position) VALUES (?, ?) ON CONFLICT(projector_id) DO UPDATE SET last_global_position=excluded.last_global_position",
                ("semantic_core", new_global_pos)
            )
            conn.commit()
            print(f"[{datetime.now(timezone.utc).isoformat()}] [MEMORY-KERNEL] Derived {processed} new episodes. Tail GlobalPos: {new_global_pos}")

if __name__ == "__main__":
    replay_memory_ledger()
