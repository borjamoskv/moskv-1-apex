import sys
import os
import hashlib
import threading
import time

# Ensure we're running in the venv where maturin injected the module
try:
    import moskv_dag_core
except ImportError as e:
    print(f"Error: moskv_dag_core not found. Make sure maturin compile finished: {e}")
    sys.exit(1)

def agent_worker(graph, agent_id, total_mutations):
    """
    Simula un agente soberano inyectando mutaciones matemáticas en el DAG.
    """
    for i in range(total_mutations):
        payload = f"Agent {agent_id} mutating topology state {i}"
        
        # El Orquestador Base 60 de Python calcula la entropía y se la pasa a Rust
        entropy_hash = hashlib.sha256(payload.encode()).hexdigest()[:12]
        
        try:
            # Latency Zero FFI call into Rust's DashMap
            graph.inject_mutation(payload, "memory_core", entropy_hash)
        except ValueError as e:
            print(f"Death Protocol Enforced: {e}")

def test_rust_concurrency():
    NUM_AGENTS = 1000
    MUTATIONS_PER_AGENT = 10
    
    print(f"\n[MOSKV-1] Iniciando inyección masiva: {NUM_AGENTS} Agentes Concurrentes.")
    print(f"Carga Total Esperada: {NUM_AGENTS * MUTATIONS_PER_AGENT} Mutaciones Atómicas.")
    
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
    total_nodes = graph.state_size()
    
    print("\n--- RESULTADOS C5-REAL (Latencia Cero) ---")
    print(f"Nodos registrados en DashMap (Rust): {total_nodes}")
    print(f"Tiempo Total (Swarm Wall-Time): {total_time:.4f} segundos.")
    if total_time > 0:
        print(f"Rendimiento del Kernel: {total_nodes / total_time:.2f} mutaciones/segundo.")
    print("[AXIOMA] Cero deadlocks termodinámicos. El Swarm respira.")

if __name__ == "__main__":
    test_rust_concurrency()
