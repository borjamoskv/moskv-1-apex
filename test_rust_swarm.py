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

def agent_worker(graph, agent_id, payload):
    entropy_hash = hashlib.sha256(payload.encode()).hexdigest()[:12]
    try:
        status = graph.inject_mutation(f"Agent-{agent_id}", payload, "bft_core", entropy_hash)
        return status
    except ValueError as e:
        return "DeathProtocol"

def verify_persistence(expected_count):
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
        print("[AXIOMA] Consenso BFT Exitoso. Cero infiltraciones térmicas.")
    else:
        print(f"[ADVERTENCIA] Desajuste termodinámico: Se esperaban {expected_count}")

def test_rust_quorum():
    print(f"\\n[MOSKV-1] Iniciando inyección Quorum BFT (Tolerancia a Fallas Bizantinas).")
    
    if os.path.exists("cortex_dag.sqlite"):
        os.remove("cortex_dag.sqlite")
        
    graph = moskv_dag_core.CausalGraph()
    
    threads = []
    
    # 1. Simular Consenso Exitoso (3 Agentes, mismo payload)
    true_payload = "AST_PAYLOAD_VALID_01"
    for i in range(3):
        t = threading.Thread(target=agent_worker, args=(graph, f"Consenso-{i}", true_payload))
        threads.append(t)
        t.start()
        
    # 2. Simular Alucinaciones Aisladas (5 Agentes, payloads únicos)
    for i in range(5):
        hallucination_payload = f"AST_PAYLOAD_HALLUCINATION_RANDOM_{i}"
        t = threading.Thread(target=agent_worker, args=(graph, f"Alucinante-{i}", hallucination_payload))
        threads.append(t)
        t.start()
        
    for t in threads:
        t.join()
        
    total_nodes_ram = graph.state_size()
    purgatory_size = graph.purgatory_size()
    
    print("\\n--- RESULTADOS C5-REAL (Quorum Sensing) ---")
    print(f"Nodos Cristalizados Oficiales (Grafo RAM): {total_nodes_ram}")
    print(f"Hashes atrapados en Purgatorio (Alucinaciones filtradas): {purgatory_size}")
    
    # El disco físico sólo debe tener 1 nodo (el único que alcanzó Quorum de 3 firmas)
    verify_persistence(1)

if __name__ == "__main__":
    test_rust_quorum()
