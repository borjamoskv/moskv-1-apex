import sys
import os
import hashlib
import threading
import time
import random
import sqlite3

try:
    import moskv_dag_core
except ImportError as e:
    print(f"[C5-REAL] Error Crítico: Módulo nativo moskv_dag_core no encontrado. {e}")
    sys.exit(1)

def agent_worker(graph, agent_id, payload):
    entropy_hash = hashlib.sha256(payload.encode()).hexdigest()[:12]
    try:
        # FFI Call de latencia cero
        graph.inject_mutation(f"Agent-{agent_id}", payload, "stress_test_bft", entropy_hash)
    except ValueError:
        pass  # Death Protocol silencioso para el test de estrés

def verify_disk_crystallization(expected_nodes):
    print("Sincronizando MPSC channel hacia Disco (SQLite WAL)...")
    time.sleep(1.5) # Tiempo suficiente para que el Sentinel limpie el buffer
    
    db_path = "cortex_dag.sqlite"
    if not os.path.exists(db_path):
        print(f"[ERROR C5-REAL] No se encontró la DB en {db_path}")
        return False
        
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM mutations")
    count = cursor.fetchone()[0]
    conn.close()
    
    print(f"[AUDITORIA FISICA] {count} Nodos cristalizados permanentemente en Disco.")
    if count == expected_nodes:
        print("[AXIOMA] Filtrado Termodinámico Absoluto. Las alucinaciones no tocaron el disco.")
    else:
        print(f"[ADVERTENCIA] Corrupción: Se esperaban {expected_nodes}, pero hay {count}.")

def run_thermodynamic_stress_test():
    print(f"\\n[MOSKV-1] INICIANDO PRUEBA DE ESTRÉS EXTREMA (Quorum BFT)")
    
    # Destruimos la DB física anterior para una prueba estéril
    if os.path.exists("cortex_dag.sqlite"):
        os.remove("cortex_dag.sqlite")
        
    graph = moskv_dag_core.CausalGraph()
    
    # Configuración del estrés
    VALID_MISSIONS = 1000 # 1000 verdades matemáticas
    AGENTS_PER_MISSION = 3 # Requieren 3 votos para Quorum
    HALLUCINATING_AGENTS = 5000 # 5000 agentes inyectando ruido único
    
    TOTAL_AGENTS = (VALID_MISSIONS * AGENTS_PER_MISSION) + HALLUCINATING_AGENTS
    
    print(f"-> Nodos Con Quorum Esperados: {VALID_MISSIONS}")
    print(f"-> Alucinaciones Aisladas (Purgatorio): {HALLUCINATING_AGENTS}")
    print(f"-> Hilos Concurrentes (Swarm Total): {TOTAL_AGENTS}")
    
    threads = []
    
    # 1. Cargar agentes de consenso
    for mission_id in range(VALID_MISSIONS):
        payload = f"AST_VALID_MUTATION_MISSION_{mission_id}"
        for i in range(AGENTS_PER_MISSION):
            t = threading.Thread(target=agent_worker, args=(graph, f"Consenso_M{mission_id}_A{i}", payload))
            threads.append(t)
            
    # 2. Cargar agentes alucinando (ruido puro)
    for i in range(HALLUCINATING_AGENTS):
        # Cada payload es único y errático
        payload = f"AST_HALLUCINATION_NOISE_{random.random()}_{i}"
        t = threading.Thread(target=agent_worker, args=(graph, f"Alucinante_{i}", payload))
        threads.append(t)
        
    # Mezclamos los hilos para simular entropía real (caos de llegada)
    random.shuffle(threads)
    
    print("\\n[MOSKV-1] Detonando inyección simultánea de latencia cero...")
    
    start_time = time.time()
    for t in threads:
        t.start()
        
    for t in threads:
        t.join()
        
    end_time = time.time()
    total_time = end_time - start_time
    
    total_nodes_ram = graph.state_size()
    purgatory_size = graph.purgatory_size()
    
    print("\\n--- RESULTADOS C5-REAL (Stress Test) ---")
    print(f"Tiempo Total de Resolución BFT: {total_time:.4f} segundos.")
    print(f"Rendimiento de Filtrado Quorum: {TOTAL_AGENTS / total_time:.2f} agentes evaluados/segundo.")
    
    print(f"\\n[MEMORIA RAM (Rust DashMap)]")
    print(f"-> Nodos Oficiales (Verdades Cristalizadas): {total_nodes_ram}")
    print(f"-> Purgatorio (Alucinaciones Atrapadas): {purgatory_size}")
    
    verify_disk_crystallization(VALID_MISSIONS)

if __name__ == "__main__":
    run_thermodynamic_stress_test()
