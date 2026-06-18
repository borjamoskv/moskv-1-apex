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

# H3 / C5-REAL Alignment: Payload is not a mocked string, but the physical hash of the 140BPM DOM state
INDEX_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "apps", "brt-video", "out", "index.html")
with open(INDEX_PATH, "rb") as f:
    PAYLOAD_BYTES = f.read()

PAYLOAD = PAYLOAD_BYTES.decode('utf-8', errors='ignore')
TARGET = "BERLIN_MAIN_ROOM_DOM"
EXPECTED_HASH = hashlib.sha256(PAYLOAD_BYTES).hexdigest()

def execute_bft_quorum():
    print(f"[MOSKV-1] Anclando estado físico DOM al Ledger Rust. Quorum Threshold: 3")
    
    # Concurrent Agents (Quorum sensing)
    agents = ["ROSALIA_SHARD_1", "TANGANA_GC", "WEATHERALL_DUB_MASTER"]
    
    for agent in agents:
        status = graph.inject_mutation(agent, PAYLOAD, TARGET, EXPECTED_HASH)
        print(f"[{agent}] -> Quorum Status: {status}")
        
    print(f"[SYSTEM] State Size: {graph.state_size()} | Purgatory Size: {graph.purgatory_size()}")
    print(f"[SYSTEM] Invariante DOM {EXPECTED_HASH[:8]} cristalizada en Rust.")

if __name__ == "__main__":
    execute_bft_quorum()
