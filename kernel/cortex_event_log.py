#!/usr/bin/env python3
import os
import json
import hashlib
from datetime import datetime, timezone
LOG_PATH = "/Users/borjafernandezangulo/.cortex/cortex_events.jsonl"
def _hash_event(event: dict) -> str:
    content = {k: v for k, v in event.items() if k != "hash"}
    encoded = json.dumps(content, sort_keys=True).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()
def append_event(event_type: str, payload: dict) -> dict:
    os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)
    prev_hash = "0" * 64
    if os.path.exists(LOG_PATH):
        try:
            with open(LOG_PATH, "r") as f:
                lines = f.readlines()
                if lines:
                    last_event = json.loads(lines[-1].strip())
                    prev_hash = last_event.get("hash", prev_hash)
        except Exception:
            pass
    event = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "event_type": event_type.upper(),
        "payload": payload,
        "prev_hash": prev_hash
    }
    event["hash"] = _hash_event(event)
    with open(LOG_PATH, "a") as f:
        f.write(json.dumps(event) + "\n")
    return event
def verify_chain() -> bool:
    if not os.path.exists(LOG_PATH): return True
    expected_prev = "0" * 64
    with open(LOG_PATH, "r") as f:
        for line_num, line in enumerate(f, 1):
            if not line.strip(): continue
            event = json.loads(line)
            if event.get("prev_hash") != expected_prev:
                print(f"[CORTEX-AUDIT] Cadena rota L{line_num}: prev_hash no coincide.")
                return False
            actual_hash = _hash_event(event)
            if event.get("hash") != actual_hash:
                print(f"[CORTEX-AUDIT] Tampering en L{line_num}: hash inválido.")
                return False
            expected_prev = actual_hash
    return True
