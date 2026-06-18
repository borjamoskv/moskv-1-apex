import asyncio
import json
import hashlib
import time
import sqlite3
import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), 'core', 'moskv-1'))
from src.moskv_1.brain import BrainRegion
from quorum_bus import emit_pheromone, init_db

DB_PATH = "swarm_os.sqlite"
THREADS = 5

async def worker_node(node_id: int, task_prompt: str):
    region = BrainRegion(f"worker-{node_id}")
    
    print(f"[Worker-{node_id}] Requesting JSON Inference from Ollama...")
    # Zero-Shot Landauer compression
    response = await region.infer_local(task_prompt, model="llama3")
    
    if "[ERROR]" in response or "[QUARANTINE]" in response:
        print(f"[Worker-{node_id}] Inference failed or quarantined: {response}")
        # Fallback to deterministic mockup if Ollama isn't running locally
        payload = {"status": "success", "data": "DETERMINISTIC_FALLBACK_C5_REAL"}
    else:
        try:
            payload = json.loads(response)
        except json.JSONDecodeError:
            print(f"[Worker-{node_id}] Invalid JSON. Slop detected.")
            payload = {"status": "failure"}

    # Calculate Intent Hash (BFT)
    payload_str = json.dumps(payload, sort_keys=True)
    intent_hash = hashlib.sha256(payload_str.encode()).hexdigest()
    
    # 1. Emit Pheromone
    emit_pheromone(region.region_name, intent_hash, db_path=DB_PATH)
    
    # 2. Enqueue Mutation
    filename = f"cortex_git_stress/llm_entropy_{node_id}.json"
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    with open(filename, "w") as f:
        f.write(payload_str)
        
    msg = f"feat(llm): autonomous swarm mutation from {region.region_name}"
    
    conn = sqlite3.connect(DB_PATH, timeout=5.0)
    conn.execute("INSERT INTO git_commit_queue (file_path, message, intent_hash) VALUES (?, ?, ?)", (filename, msg, intent_hash))
    conn.commit()
    conn.close()

async def main():
    print("=== C5-REAL LLM INFERENCE SWARM (BFT) ===")
    prompt = "Output a JSON object with keys 'status' (set to 'success') and 'data' (set to 'C5_REAL_ZERO_SHOT'). No markdown. No text outside JSON."
    
    tasks = []
    for i in range(THREADS):
        tasks.append(worker_node(i, prompt))
        
    start_time = time.time()
    await asyncio.gather(*tasks)
    print(f"[CORTEX] Swarm Execution Time: {time.time() - start_time:.2f}s")

if __name__ == "__main__":
    init_db(DB_PATH)
    asyncio.run(main())
