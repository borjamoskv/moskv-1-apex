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
        # FTS5 Accelerated Semantic Traversal (O(log N) latency)
        # Event-driven decay trigger on recall miss (Bottleneck mitigation)
        with get_memory_db() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT e.event_id, e.timestamp, e.narrative 
                FROM episodic_memory_fts f
                JOIN episodic_memory e ON e.rowid = f.rowid
                WHERE episodic_memory_fts MATCH ?
                ORDER BY e.timestamp DESC
            """, (f'"{concept}"',))
            results = [dict(row) for row in cursor.fetchall()]

            if not results:
                # Recall miss: Event-driven decay execution
                import math
                cursor.execute("SELECT confidence, last_updated FROM semantic_memory WHERE concept_name = ?", (concept,))
                row = cursor.fetchone()
                if row:
                    try:
                        from datetime import datetime, timezone
                        last_str = row['last_updated'].replace('Z', '+00:00')
                        last_updated = datetime.fromisoformat(last_str)
                        days_elapsed = (datetime.now(timezone.utc) - last_updated).total_seconds() / 86400.0
                        if days_elapsed > 0.1:
                            decay_factor = math.exp(-days_elapsed / 10.0)
                            new_confidence = row['confidence'] * decay_factor
                            cursor.execute(
                                "UPDATE semantic_memory SET confidence = ?, last_updated = ? WHERE concept_name = ?",
                                (new_confidence, datetime.now(timezone.utc).isoformat(), concept)
                            )
                            conn.commit()
                    except Exception:
                        pass
                        
            return results

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
