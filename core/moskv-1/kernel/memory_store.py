#!/usr/bin/env python3
# Execution Level: C5-REAL
import os
import sqlite3
import hmac
import hashlib
import json
from contextlib import contextmanager

HMAC_SECRET = b"moskv-1-c5-real-secret"

def _sign(payload: dict, key: bytes) -> str:
    raw = json.dumps(payload, sort_keys=True).encode()
    return hmac.new(key, raw, hashlib.sha256).hexdigest()

MEMORY_DB_PATH = "/Users/borjafernandezangulo/.cortex/memory.db"

@contextmanager
def get_memory_db():
    os.makedirs(os.path.dirname(MEMORY_DB_PATH), exist_ok=True)
    conn = sqlite3.connect(MEMORY_DB_PATH, timeout=5.0)
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("PRAGMA synchronous=NORMAL;")
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()

def init_memory_schema():
    with get_memory_db() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS episodic_memory (
                event_id TEXT PRIMARY KEY,
                timestamp TEXT NOT NULL,
                correlation_id TEXT NOT NULL,
                actor TEXT,
                narrative TEXT NOT NULL,
                hmac_signature TEXT NOT NULL,
                layer TEXT DEFAULT 'session_memory',
                expires_at TEXT
            );
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS semantic_memory (
                concept_id TEXT PRIMARY KEY,
                concept_name TEXT NOT NULL UNIQUE,
                synthesis TEXT NOT NULL,
                confidence REAL NOT NULL,
                last_updated TEXT NOT NULL
            );
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS procedural_memory (
                procedure_hash TEXT PRIMARY KEY,
                aggregate_type TEXT NOT NULL,
                failure_pattern TEXT,
                resolution_pattern TEXT,
                success_rate REAL
            );
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS memory_checkpoints (
                projector_id TEXT PRIMARY KEY,
                last_global_position INTEGER NOT NULL
            );
        """)
        conn.commit()

if __name__ == "__main__":
    init_memory_schema()
