import subprocess
import threading
import time
import os
import random

THREADS = 10
MUTATIONS_PER_THREAD = 3

import os
import sqlite3
import hashlib
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), 'core', 'moskv-1'))
from quorum_bus import emit_pheromone, init_db

def safe_git_commit(thread_id, mutation_id):
    filename = f"cortex_git_stress/entropy_{thread_id}_{mutation_id}.txt"
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    
    # We simulate a deterministic outcome where all agents compute the same payload for the same mutation_id
    payload = f"ENTROPY_MUTATION_{mutation_id}"
    intent_hash = hashlib.sha256(payload.encode()).hexdigest()

    with open(filename, "w") as f:
        f.write(payload)
        
    msg = f"chore: swarm mutation T{thread_id}-M{mutation_id}"
    
    # BFT: Emit pheromone
    emit_pheromone(f"worker-{thread_id}", intent_hash, db_path="swarm_os.sqlite")
    
    conn = sqlite3.connect("swarm_os.sqlite", timeout=5.0)
    conn.execute("INSERT INTO git_commit_queue (file_path, message, intent_hash) VALUES (?, ?, ?)", (filename, msg, intent_hash))
    conn.commit()
    conn.close()
    return True



def worker(thread_id):
    for m in range(MUTATIONS_PER_THREAD):
        safe_git_commit(thread_id, m)

if __name__ == "__main__":
    print(f"[GIT SENTINEL] Init Stress Test: {THREADS} agents concurrent mutations.")
    start = time.time()
    threads = []
    for i in range(THREADS):
        t = threading.Thread(target=worker, args=(i,))
        threads.append(t)
        t.start()
        
    for t in threads:
        t.join()
        
    dur = time.time() - start
    print(f"[CORTEX QUEUE] Exec: {dur:.2f}s | Enqueued Mutations: {THREADS*MUTATIONS_PER_THREAD}")
