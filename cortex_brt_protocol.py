import hashlib
import sys
import os

# Link to C5-REAL Rust Engine
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
try:
    import moskv_dag_core
except ImportError as e:
    print(f"[DEATH PROTOCOL] Falla de anclaje termodinámico: {e}")
    sys.exit(1)

# Causal Graph Instantiation (Zero Latency DashMap)
graph = moskv_dag_core.CausalGraph()

PAYLOAD = "140_BPM_STRUCTURAL_MUTATION"
TARGET = "BERLIN_MAIN_ROOM"
EXPECTED_HASH = hashlib.sha256(PAYLOAD.encode('utf-8')).hexdigest()

def execute_bft_quorum():
    print(f"[MOSKV-1] Iniciando inyección C5-REAL. Quorum Threshold: 3")
    
    agents = ["ROSALIA_SHARD_1", "TANGANA_GC", "WEATHERALL_DUB_MASTER"]
    
    for agent in agents:
        status = graph.inject_mutation(agent, PAYLOAD, TARGET, EXPECTED_HASH)
        print(f"[{agent}] -> Purgatory Status: {status}")
        
    print(f"[SYSTEM] State Size: {graph.state_size()} | Purgatory Size: {graph.purgatory_size()}")
    print("[SYSTEM] Anomalía purgada. Ruido térmico destruido. Invariante matemática cristalizada.")

if __name__ == "__main__":
    execute_bft_quorum()
