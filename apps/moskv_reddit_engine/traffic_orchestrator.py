#!/usr/bin/env python3
# Execution Level: C5-REAL
import os
import subprocess
from datetime import datetime, timezone

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

def run_traffic_cycle():
    print(f"[{datetime.now(timezone.utc).isoformat()}] [ZEO-GTM] Initiating Reddit Traffic Engine Cycle...")
    
    try:
        # Step 1: Fetch Trends
        print("[ZEO-GTM] Fetching Subreddit Trends (osint_daemon)...")
        subprocess.run(["python3", "osint_daemon.py"], cwd=ROOT_DIR, check=True)
        
        # Step 2: Draft Weaponized Payloads
        print("[ZEO-GTM] Weaponizing Payloads with Stripe Matrix (autonomous_syndicator)...")
        subprocess.run(["python3", "autonomous_syndicator.py"], cwd=ROOT_DIR, check=True)
        
        print(f"[{datetime.now(timezone.utc).isoformat()}] [ZEO-GTM] Cycle complete. Review syndication_outbox.md and dispatch via CDP.")
    except subprocess.CalledProcessError as e:
        print(f"[ZEO-GTM-ERR] Traffic cycle failed: {e}")

if __name__ == "__main__":
    run_traffic_cycle()
