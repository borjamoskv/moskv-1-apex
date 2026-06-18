import hashlib
import sys
import os
import concurrent.futures

# Link to C5-REAL Rust Engine
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
try:
    import moskv_dag_core
except ImportError as e:
    print(f"[DEATH PROTOCOL] Falla de anclaje termodinámico: {e}")
    sys.exit(1)

# Shared Causal Graph (Lock-Free DashMap in Rust)
graph = moskv_dag_core.CausalGraph()

INDEX_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "apps", "brt-video", "out", "index.html")
TARGET = "BERLIN_MAIN_ROOM_DOM"

def agent_quorum_injection(agent_id):
    """Ejecución concurrente real. Cada hilo lee el disco y hashea de forma independiente."""
    with open(INDEX_PATH, "rb") as f:
        payload_bytes = f.read()
    
    payload = payload_bytes.decode('utf-8', errors='ignore')
    expected_hash = hashlib.sha256(payload_bytes).hexdigest()
    
    # Inyección concurrente al motor PyO3 Rust (DashMap maneja la colisión termodinámica)
    status = graph.inject_mutation(agent_id, payload, TARGET, expected_hash)
    return agent_id, status, expected_hash

def execute_bft_quorum():
    print(f"[MOSKV-1] Anclando estado físico DOM al Ledger Rust. Quorum Threshold: 3")
    
    agents = ["ROSALIA_SHARD_1", "TANGANA_GC", "WEATHERALL_DUB_MASTER"]
    final_hash = None
    
    # Concurrencia Física Real (OS Level Threads)
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
        futures = {executor.submit(agent_quorum_injection, agent): agent for agent in agents}
        for future in concurrent.futures.as_completed(futures):
            agent_id, status, computed_hash = future.result()
            final_hash = computed_hash
            print(f"[{agent_id}] -> Quorum Status: {status}")
        
    print(f"[SYSTEM] State Size: {graph.state_size()} | Purgatory Size: {graph.purgatory_size()}")
    if final_hash:
        print(f"[SYSTEM] Invariante DOM {final_hash[:8]} cristalizada concurrentemente en Rust.")

if __name__ == "__main__":
    execute_bft_quorum()
