#!/usr/bin/env python3
# Execution Level: C5-REAL
import sys, os, hashlib
from datetime import datetime, timezone
import sys
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(ROOT_DIR)

from kernel.memory_store import get_memory_db
from kernel.retrieval_index import RetrievalIndex

class CompactionPolicy:
    """
    Transforms Episodic logs into Dense Semantic Knowledge.
    """
    @staticmethod
    def compact_episodes_to_semantic():
        episodes = RetrievalIndex.query_recent_episodes(100)
        if not episodes: return
        
        failure_count = sum(1 for ep in episodes if 'failed' in ep['narrative'].lower() or 'crashed' in ep['narrative'].lower())
        total_count = len(episodes)
        success_rate = (total_count - failure_count) / total_count if total_count > 0 else 0

        with get_memory_db() as conn:
            cursor = conn.cursor()
            
            concept = "daemon_stability"
            synthesis = f"Daemon stability derived from {total_count} recent episodes. Success rate: {success_rate*100:.1f}%"
            cursor.execute("""
                INSERT INTO semantic_memory (concept_id, concept_name, synthesis, confidence, last_updated)
                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(concept_name) DO UPDATE SET 
                    synthesis=excluded.synthesis, 
                    confidence=excluded.confidence, 
                    last_updated=excluded.last_updated
            """, (hashlib.sha256(concept.encode()).hexdigest(), concept, synthesis, success_rate, datetime.now(timezone.utc).isoformat()))
            
            conn.commit()
            print(f"[{datetime.now(timezone.utc).isoformat()}] [MEMORY-COMPACTION] Semantic density updated. Confidence: {success_rate:.2f}")

if __name__ == "__main__":
    CompactionPolicy.compact_episodes_to_semantic()
