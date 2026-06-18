import subprocess
import threading
import time
import os
import random

THREADS = 10
MUTATIONS_PER_THREAD = 3

import sqlite3

def safe_git_commit(thread_id, mutation_id):
    filename = f"cortex_git_stress/entropy_{thread_id}_{mutation_id}.txt"
    os.makedirs(os.path.dirname(filename), exist_ok=True)

    with open(filename, "w") as f:
        f.write(f"ENTROPY: {time.time()}")
        
    msg = f"chore: swarm mutation T{thread_id}-M{mutation_id}"
    
    conn = sqlite3.connect("swarm_os.sqlite", timeout=5.0)
    conn.execute("INSERT INTO git_commit_queue (file_path, message) VALUES (?, ?)", (filename, msg))
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
