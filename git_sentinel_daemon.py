import sqlite3
import subprocess
import time
import sys

DB_PATH = "swarm_os.sqlite"

def init_sentinel():
    conn = sqlite3.connect(DB_PATH, timeout=5.0)
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute('''
        CREATE TABLE IF NOT EXISTS git_commit_queue (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            file_path TEXT NOT NULL,
            message TEXT NOT NULL,
            status TEXT DEFAULT 'PENDING'
        )
    ''')
    conn.commit()
    return conn

def run_sentinel_cycle():
    conn = init_sentinel()
    
    while True:
        try:
            # Atomic fetch and claim
            conn.execute("BEGIN IMMEDIATE")
            cursor = conn.execute("SELECT id, file_path, message FROM git_commit_queue WHERE status='PENDING' ORDER BY id ASC LIMIT 1")
            row = cursor.fetchone()
            
            if row:
                task_id, file_path, message = row
                # Claim it
                conn.execute("UPDATE git_commit_queue SET status='PROCESSING' WHERE id=?", (task_id,))
                conn.commit()
                
                # C5-REAL Action: Single Writer Git Mutation
                try:
                    subprocess.run(["git", "add", file_path], check=True, capture_output=True)
                    subprocess.run(["git", "commit", "-m", message], check=True, capture_output=True)
                    
                    conn.execute("DELETE FROM git_commit_queue WHERE id=?", (task_id,))
                    conn.commit()
                except subprocess.CalledProcessError as e:
                    # Mark failed
                    conn.execute("UPDATE git_commit_queue SET status='FAILED' WHERE id=?", (task_id,))
                    conn.commit()
            else:
                conn.commit()
                # Empty queue, break for this cycle
                break
        except sqlite3.OperationalError:
            # If lock timeout, rollback and retry next cycle
            conn.rollback()
            break
            
    conn.close()

if __name__ == "__main__":
    run_sentinel_cycle()
