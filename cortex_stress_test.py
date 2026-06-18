import sqlite3
import threading
import time
import sys

DB_PATH = "swarm_os.sqlite"
THREADS = 100
INSERTS_PER_THREAD = 50

def worker(thread_id):
    # Rule R10 compliance
    conn = sqlite3.connect(DB_PATH, timeout=5.0)
    # PRAGMA is handled at init to avoid exclusive lock race

    for i in range(INSERTS_PER_THREAD):
        try:
            conn.execute("INSERT INTO stress_log (thread_id) VALUES (?)", (thread_id,))
            conn.commit()
        except sqlite3.OperationalError as e:
            print(f"[FATAL] Concurrency Failure on Thread {thread_id}: {e}")
            sys.exit(1)
    conn.close()

if __name__ == "__main__":
    print(f"[CORTEX] Init C5-REAL Stress Test: {THREADS} threads, {THREADS*INSERTS_PER_THREAD} total mutations.")
    
    # Init WAL mode once
    init_conn = sqlite3.connect(DB_PATH)
    init_conn.execute("PRAGMA journal_mode=WAL;")
    init_conn.close()
    
    start_time = time.time()
    threads = []

    
    for i in range(THREADS):
        t = threading.Thread(target=worker, args=(i,))
        threads.append(t)
        t.start()
        
    for t in threads:
        t.join()
        
    duration = time.time() - start_time
    
    # Verify
    conn = sqlite3.connect(DB_PATH)
    count = conn.execute("SELECT COUNT(*) FROM stress_log").fetchone()[0]
    conn.execute("DELETE FROM stress_log") # Cleanup
    conn.commit()
    conn.close()
    
    print(f"[CORTEX] Exec: {duration:.2f}s | Mutations: {count}/{THREADS*INSERTS_PER_THREAD}")
    if count >= (THREADS * INSERTS_PER_THREAD):
        print("EXERGY_YIELD: 1.0 (Zero Deadlocks. R10 Sealed.)")
    else:
        print("ENTROPY_DETECTED: Thermodynamical friction occurred.")
