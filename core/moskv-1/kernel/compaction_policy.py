#!/usr/bin/env python3
# Execution Level: C5-REAL
import sys, os, hashlib, math, sqlite3
from datetime import datetime, timezone

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(ROOT_DIR)

from kernel.memory_store import get_memory_db
from kernel.retrieval_index import RetrievalIndex

class CompactionPolicy:
    """
    Transforms Episodic logs into Dense Semantic Knowledge.
    Autopoietically modulated by C5-REAL Reinforcement Learning State.
    """
    
    @staticmethod
    def _get_rl_forgetting_rate() -> float:
        """
        Retrieves Lambda penalty from RL state to modulate memory decay.
        Base strength 10.0 days. High lambda -> Faster decay (lower strength).
        """
        try:
            db_path = os.path.join(ROOT_DIR, "..", ".agents", "rl_state.db")
            if os.path.exists(db_path):
                with sqlite3.connect(db_path, timeout=5.0) as conn:
                    conn.execute("PRAGMA journal_mode=WAL;")
                    cursor = conn.execute("SELECT lambda_weight FROM rl_weights ORDER BY id DESC LIMIT 1")
                    row = cursor.fetchone()
                    if row:
                        rl_lambda = row[0]
                        # If lambda penalty is high, we shrink memory retention window (forget faster)
                        strength = max(1.0, 10.0 - (rl_lambda * 20.0))
                        return strength
        except Exception:
            pass
        return 10.0

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
        # Ebbinghaus-style cognitive decay modulated by RL
        base_strength = CompactionPolicy._get_rl_forgetting_rate()
        
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
                
                # Dynamic Ebbinghaus decay
                decay_factor = math.exp(-days_elapsed / base_strength)
                new_confidence = row['confidence'] * decay_factor
                
                cursor.execute(
                    "UPDATE semantic_memory SET confidence = ?, last_updated = ? WHERE concept_name = ?",
                    (new_confidence, now.isoformat(), row['concept_name'])
                )
                decayed_count += 1
            conn.commit()
            if decayed_count > 0:
                print(f"[{now.isoformat()}] [MEMORY-DECAY] Applied RL-modulated Ebbinghaus decay (S={base_strength:.2f}) to {decayed_count} concepts.")

if __name__ == "__main__":
    CompactionPolicy.compact_episodes_to_semantic()
    CompactionPolicy.promote_session_to_agent()
    CompactionPolicy.apply_cognitive_decay()
