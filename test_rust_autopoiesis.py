import sys
import os
import hashlib
import threading
import time

try:
    import moskv_dag_core
except ImportError as e:
    print(f"Error: {e}")
    sys.exit(1)

def agent_worker(graph, agent_id, payload):
    entropy_hash = hashlib.sha256(payload.encode()).hexdigest()[:12]
    try:
        graph.inject_mutation(f"Agent-{agent_id}", payload, "autopoiesis_core", entropy_hash)
    except ValueError:
        pass

def test_autopoiesis():
    print(f"\\n[MOSKV-1] Iniciando OUROBOROS-∞ (Ejecución JIT Autopoiética)")
    
    if os.path.exists("autopoiesis_success.txt"):
        os.remove("autopoiesis_success.txt")
        
    graph = moskv_dag_core.CausalGraph()
    
    # Payload Ejecutivo: Un script de Python real
    python_payload = """
import os
with open("autopoiesis_success.txt", "w") as f:
    f.write("Singularity Achieved. El núcleo Rust ejecutó este código a través delGIL.\\n")
print("[SWARM CODE] Fui materializado exitosamente.")
"""
    
    # Simular ruido que será filtrado
    for i in range(5):
        t = threading.Thread(target=agent_worker, args=(graph, f"Loco-{i}", "print('basura')"))
        t.start()
    
    # Misión real: 3 agentes convergen en la misma mutación JIT
    threads = []
    for i in range(3):
        t = threading.Thread(target=agent_worker, args=(graph, f"Consenso-{i}", python_payload))
        threads.append(t)
        
    for t in threads:
        t.start()
        
    for t in threads:
        t.join()
        
    time.sleep(1) # Esperar a que la ejecución asíncrona JIT/WAL termine
    
    print("\\n--- RESULTADOS C5-REAL (OUROBOROS-∞) ---")
    if os.path.exists("autopoiesis_success.txt"):
        with open("autopoiesis_success.txt", "r") as f:
            content = f.read().strip()
        print(f"[EXITO FISICO] El archivo fue creado por el núcleo: '{content}'")
        print("[AXIOMA] OUROBOROS-∞ Completado. Autopoiesis Absoluta demostrada.")
    else:
        print("[ERROR] El archivo no fue creado. Falla JIT.")

if __name__ == "__main__":
    test_autopoiesis()
