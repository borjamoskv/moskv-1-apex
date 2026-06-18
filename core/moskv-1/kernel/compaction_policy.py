#!/usr/bin/env python3
# Execution Level: C5-REAL
import sys, os, hashlib, math
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

    @staticmethod
    def promote_session_to_agent():
        # Mem0-style stratification (GAP 4)
        # Promotes stable episodic elements from session to agent memory layer
        with get_memory_db() as conn:
            cursor = conn.cursor()
            now = datetime.now(timezone.utc).isoformat()
            cursor.execute("""
                UPDATE episodic_memory 
                SET layer = 'agent_memory' 
                WHERE layer = 'session_memory' 
                  AND (narrative LIKE '%success%' OR narrative LIKE '%completed%')
            """)
            promoted = cursor.rowcount
            conn.commit()
            if promoted > 0:
                print(f"[{now}] [MEMORY-STRATIFICATION] Promoted {promoted} episodes from session_memory to agent_memory layer.")

    @staticmethod
    def apply_cognitive_decay():
        # Ebbinghaus-style cognitive decay (GAP 5)
        # Recalculates confidence over time to prevent semantic drift
        with get_memory_db() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT concept_name, confidence, last_updated FROM semantic_memory")
            rows = cursor.fetchall()
            
            now = datetime.now(timezone.utc)
            decayed_count = 0
            for row in rows:
                try:
                    last_str = row['last_updated'].replace('Z', '+00:00')
                    last_updated = datetime.fromisoformat(last_str)
                except ValueError:
                    continue
                
                days_elapsed = (now - last_updated).total_seconds() / 86400.0
                if days_elapsed < 0.1: continue # Decay applied only on older nodes
                
                # Ebbinghaus decay: R = e^(-t/S) assuming base Strength S=10 days
                decay_factor = math.exp(-days_elapsed / 10.0)
                new_confidence = row['confidence'] * decay_factor
                
                cursor.execute(
                    "UPDATE semantic_memory SET confidence = ?, last_updated = ? WHERE concept_name = ?",
                    (new_confidence, now.isoformat(), row['concept_name'])
                )
                decayed_count += 1
            conn.commit()
            if decayed_count > 0:
                print(f"[{now.isoformat()}] [MEMORY-DECAY] Applied Ebbinghaus decay to {decayed_count} concepts.")

if __name__ == "__main__":
    CompactionPolicy.compact_episodes_to_semantic()
    CompactionPolicy.promote_session_to_agent()
    CompactionPolicy.apply_cognitive_decay()
