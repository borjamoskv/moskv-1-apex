import sys
import os
import hashlib
import threading
import time
import sqlite3

try:
    import moskv_dag_core
except ImportError as e:
    print(f"Error: moskv_dag_core no encontrado. {e}")
    sys.exit(1)

def agent_worker(graph, agent_id, total_mutations):
    for i in range(total_mutations):
        payload = f"Agent {agent_id} mutating topology state {i}"
        entropy_hash = hashlib.sha256(payload.encode()).hexdigest()[:12]
        try:
            graph.inject_mutation(payload, "memory_core", entropy_hash)
        except ValueError as e:
            pass

def verify_persistence(expected_count):
    # Damos 1 segundo al hilo Guardián de Rust (Ledger Sentinel) para vaciar el crossbeam channel
    print("Esperando sincronización de MPSC channel hacia disco...")
    time.sleep(1.0) 
    
    db_path = "cortex_dag.sqlite"
    if not os.path.exists(db_path):
        print(f"[ERROR C5-REAL] No se encontró el anclaje físico en {db_path}")
        return False
        
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM mutations")
    count = cursor.fetchone()[0]
    conn.close()
    
    print(f"[AUDITORIA FISICA] {count} Nodos cristalizados permanentemente en SQLite WAL.")
    if count == expected_count:
        print("[AXIOMA] Persistencia Asíncrona confirmada. Cero pérdida térmica.")
    else:
        print(f"[ADVERTENCIA] Desajuste termodinámico: Se esperaban {expected_count}")

def test_rust_concurrency():
    NUM_AGENTS = 1000
    MUTATIONS_PER_AGENT = 10
    total_expected = NUM_AGENTS * MUTATIONS_PER_AGENT
    
    print(f"\\n[MOSKV-1] Iniciando inyección masiva: {NUM_AGENTS} Agentes Concurrentes.")
    
    # Destruir estado físico previo para prueba estéril
    if os.path.exists("cortex_dag.sqlite"):
        os.remove("cortex_dag.sqlite")
        
    graph = moskv_dag_core.CausalGraph()
    
    threads = []
    start_time = time.time()
    
    for i in range(NUM_AGENTS):
        t = threading.Thread(target=agent_worker, args=(graph, i, MUTATIONS_PER_AGENT))
        threads.append(t)
        t.start()
        
    for t in threads:
        t.join()
        
    end_time = time.time()
    total_time = end_time - start_time
    total_nodes_ram = graph.state_size()
    
    print("\\n--- RESULTADOS C5-REAL ---")
    print(f"Nodos registrados en DashMap (RAM): {total_nodes_ram}")
    print(f"Tiempo Total Inyección (RAM): {total_time:.4f} segundos.")
    if total_time > 0:
        print(f"Velocidad de Inyección: {total_nodes_ram / total_time:.2f} mut/seg.")
        
    verify_persistence(total_expected)

if __name__ == "__main__":
    test_rust_concurrency()
