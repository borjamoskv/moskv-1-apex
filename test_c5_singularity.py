import os
import sys
import time
import threading

sys.path.append(os.path.join(os.path.dirname(__file__), 'core', 'moskv-1', 'kernel'))
from c5_base60_orchestrator import Base60Engine, EntropyException

def simulate_llm_agent(engine, agent_id, raw_json):
    try:
        engine.execute_mutation(agent_id, raw_json)
    except EntropyException as e:
        print(f"[{agent_id} DESTRUIDO] {e}")

def run_singularity():
    print(f"\\n[MOSKV-1] IGNICION DE LA SINGULARIDAD C5-REAL (End-to-End)")
    
    if os.path.exists("cortex_dag.sqlite"):
        os.remove("cortex_dag.sqlite")
    if os.path.exists("singularity_proof.txt"):
        os.remove("singularity_proof.txt")
        
    engine = Base60Engine()
    
    # Payload Python Ejecutivo
    python_payload = """
import os
with open("singularity_proof.txt", "w") as f:
    f.write("MOSKV-1 APEX: La Membrana y el Núcleo son Uno. C5-REAL.\\n")
print("[JIT] Ouroboros activado por Orquestador.")
"""
    
    import json
    
    # JSON estrictos que el LLM generaría (Consenso)
    valid_dict = {
        "status": "mutate",
        "target_system": "file_system",
        "ast_payload": python_payload,
        "entropy_check": "C5-REAL"
    }
    valid_json = json.dumps(valid_dict)
    
    # JSON con anergía conversacional (Violación Pydantic / JsonDecode)
    invalid_json_1 = """Aquí tienes el código, espero que sirva: { "status": "mutate" ..."""
    
    # JSON que pasa Pydantic pero tiene un payload diferente (Alucinación de Lógica)
    invalid_dict_2 = {
        "status": "mutate",
        "target_system": "file_system",
        "ast_payload": "print('Esto es una alucinación lógica aislada')",
        "entropy_check": "C5-REAL"
    }
    invalid_json_2 = json.dumps(invalid_dict_2)

    threads = []
    
    # 1. Agente que viola JSON
    t = threading.Thread(target=simulate_llm_agent, args=(engine, "Agente-Hablador", invalid_json_1))
    threads.append(t)
    
    # 2. Agente que alucina lógicamente
    t = threading.Thread(target=simulate_llm_agent, args=(engine, "Agente-Alucinante", invalid_json_2))
    threads.append(t)
    
    # 3. Misión Quorum (3 Agentes Convergentes)
    for i in range(3):
        t = threading.Thread(target=simulate_llm_agent, args=(engine, f"Agente-Consenso-{i}", valid_json))
        threads.append(t)
        
    for t in threads:
        t.start()
        
    for t in threads:
        t.join()
        
    time.sleep(1.5) # Esperar al canal Asíncrono JIT/WAL
    
    print("\\n--- VALIDACION DE MEMBRANA C5-REAL ---")
    if os.path.exists("singularity_proof.txt"):
        with open("singularity_proof.txt", "r") as f:
            content = f.read().strip()
        print(f"[EXITO ABSOLUTO] El Motor End-to-End ejecutó el archivo: '{content}'")
    else:
        print("[ERROR] La singularidad falló en propagar el código.")

if __name__ == "__main__":
    run_singularity()
