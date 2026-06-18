#!/usr/bin/env python3
# Execution Level: C5-REAL
import sys, os
from datetime import datetime, timezone
import sys
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(ROOT_DIR)

from kernel.memory_store import get_memory_db

class RetrievalIndex:
    @staticmethod
    def query_recent_episodes(limit: int = 50) -> list:
        with get_memory_db() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT timestamp, actor, narrative 
                FROM episodic_memory 
                ORDER BY timestamp DESC 
                LIMIT ?
            """, (limit,))
            return [dict(row) for row in cursor.fetchall()]

    @staticmethod
    def query_semantic_concept(concept_name: str) -> dict:
        with get_memory_db() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT synthesis, confidence, last_updated 
                FROM semantic_memory 
                WHERE concept_name = ?
            """, (concept_name,))
            row = cursor.fetchone()
            return dict(row) if row else None

    @staticmethod
    def recall(concept: str) -> list:
        # Cognee-style semantic traversal (GAP 2)
        # Navigates from semantic memory down to related episodic logs
        with get_memory_db() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT e.event_id, e.timestamp, e.narrative 
                FROM episodic_memory e
                WHERE e.narrative LIKE ?
                ORDER BY e.timestamp DESC
            """, (f'%{concept}%',))
            return [dict(row) for row in cursor.fetchall()]

    @staticmethod
    def forget(node_id: str) -> bool:
        # Cognee-style node amnesia (GAP 2)
        # Deletes specific nodes from semantic or episodic layers to prevent semantic drift
        with get_memory_db() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM semantic_memory WHERE concept_id = ?", (node_id,))
            rows_affected = cursor.rowcount
            if rows_affected == 0:
                cursor.execute("DELETE FROM episodic_memory WHERE event_id = ?", (node_id,))
                rows_affected = cursor.rowcount
            conn.commit()
            return rows_affected > 0

    @staticmethod
    def get_procedural_failure_pattern(aggregate_type: str) -> list:
        with get_memory_db() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT failure_pattern, resolution_pattern, success_rate 
                FROM procedural_memory 
                WHERE aggregate_type = ?
                ORDER BY success_rate DESC
            """, (aggregate_type,))
            return [dict(row) for row in cursor.fetchall()]

if __name__ == "__main__":
    episodes = RetrievalIndex.query_recent_episodes(5)
    print(f"[{datetime.now(timezone.utc).isoformat()}] [MEMORY-RETRIEVAL] Tail Episodes:")
    for ep in episodes:
        print(f"  - [{ep['timestamp']}] {ep['actor']}: {ep['narrative']}")
