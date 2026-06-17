import json
import time
import os
import subprocess
from datetime import datetime

TARGET_SUBREDDITS = ["LocalLLaMA", "singularity", "cybersecurity", "autonomousagents"]
LEDGER_FILE = os.path.join(os.path.dirname(__file__), "osint_ledger.json")

def fetch_subreddit_cdp(subreddit):
    js_code = f'fetch("https://www.reddit.com/r/{subreddit}/hot.json?limit=5").then(r => r.json()).then(d => d.data.children.map(c => ({{title: c.data.title, score: c.data.score, num_comments: c.data.num_comments, url: c.data.url}})))'
    
    driver_path = os.path.join(os.path.dirname(__file__), "reddit_cdp_driver.py")
    result = subprocess.run(["python3", driver_path, js_code], capture_output=True, text=True)
    try:
        data = json.loads(result.stdout.strip())
        if isinstance(data, dict) and "error" in data:
            print(f"[C4-ERROR] CDP Error: {data['error']}")
            return None
        return data
    except Exception as e:
        print(f"[C4-ERROR] Failed to parse CDP output: {result.stdout}")
        return None

def ingest_trends():
    print("[C5-REAL] Initiating CDP-Driven Reddit OSINT Cartography (WAF Bypass Active)...")
    
    if os.path.exists(LEDGER_FILE):
        with open(LEDGER_FILE, 'r') as f:
            ledger = json.load(f)
    else:
        ledger = {"history": []}
        
    current_run = {"timestamp": datetime.utcnow().isoformat(), "trends": {}}
    
    for sub in TARGET_SUBREDDITS:
        print(f"[*] Ingesting r/{sub}...")
        data = fetch_subreddit_cdp(sub)
        if data:
            current_run["trends"][sub] = data
        time.sleep(2) # Biological rhythm simulation
    
    ledger["history"].append(current_run)
    
    # Prune history to last 24 runs
    if len(ledger["history"]) > 24:
        ledger["history"] = ledger["history"][-24:]
        
    with open(LEDGER_FILE, 'w') as f:
        json.dump(ledger, f, indent=2)
    print(f"[C5-REAL] Ledger updated: {LEDGER_FILE}")

if __name__ == "__main__":
    ingest_trends()
