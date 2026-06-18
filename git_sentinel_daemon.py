import sqlite3
import subprocess
import time
import sys
import hashlib
import os

sys.path.append(os.path.join(os.path.dirname(__file__), 'core', 'moskv-1'))
from quorum_bus import check_quorum

DB_PATH = "swarm_os.sqlite"

def init_sentinel():
    conn = sqlite3.connect(DB_PATH, timeout=5.0)
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute('''
        CREATE TABLE IF NOT EXISTS git_commit_queue (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            file_path TEXT NOT NULL,
            message TEXT NOT NULL,
            intent_hash TEXT NOT NULL,
            status TEXT DEFAULT 'PENDING'
        )
    ''')
    conn.commit()
    return conn

def run_sentinel_cycle(total_swarm_nodes: int = 10):
    conn = init_sentinel()
    
    while True:
        try:
            conn.execute("BEGIN IMMEDIATE")
            cursor = conn.execute("SELECT id, file_path, message, intent_hash FROM git_commit_queue WHERE status='PENDING' ORDER BY id ASC LIMIT 1")
            row = cursor.fetchone()
            
            if row:
                task_id, file_path, message, intent_hash = row
                
                # BFT Quorum Check (Rule R3/R4 Synthesis)
                if check_quorum(intent_hash, required_nodes=total_swarm_nodes, db_path=DB_PATH):
                    # Claim it
                    conn.execute("UPDATE git_commit_queue SET status='PROCESSING' WHERE id=?", (task_id,))
                    conn.commit()
                    
                    try:
                        subprocess.run(["git", "add", file_path], check=True, capture_output=True)
                        subprocess.run(["git", "commit", "-m", message], check=True, capture_output=True)
                        
                        conn.execute("DELETE FROM git_commit_queue WHERE id=?", (task_id,))
                        conn.commit()
                        print(f"[Sentinel] Committed Intent {intent_hash[:8]} successfully.")
                    except subprocess.CalledProcessError as e:
                        conn.execute("UPDATE git_commit_queue SET status='FAILED' WHERE id=?", (task_id,))
                        conn.commit()
                        print(f"[Sentinel] Git Error on Intent {intent_hash[:8]}.")
                else:
                    # Consensus not reached yet, yield back lock
                    conn.rollback()
                    time.sleep(0.5)
            else:
                conn.commit()
                break
        except sqlite3.OperationalError:
            conn.rollback()
            break
            
    conn.close()

if __name__ == "__main__":
    run_sentinel_cycle()
