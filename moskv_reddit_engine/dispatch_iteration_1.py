import time
import json
import websocket
import urllib.request

def dispatch_payload(ws, url, text):
    print(f"[*] Navigating to Node: {url}")
    ws.send(json.dumps({
        "id": 3,
        "method": "Page.navigate",
        "params": {"url": url}
    }))
    time.sleep(5)
    
    js = f"""
    (function() {{
        let header = document.createElement('div');
        header.style.backgroundColor = '#0A0A0A';
        header.style.color = '#2B3BE5';
        header.style.padding = '20px';
        header.style.fontSize = '18px';
        header.style.fontFamily = 'monospace';
        header.style.border = '2px solid #2B3BE5';
        header.style.zIndex = '999999';
        header.style.position = 'fixed';
        header.style.top = '0';
        header.style.width = '100%';
        header.innerHTML = '<strong>[MOSKV-1 APEX] BATCH PAYLOAD INJECTION:</strong><br>{text}';
        document.body.appendChild(header);
        return 'SUCCESS';
    }})();
    """
    ws.send(json.dumps({
        "id": 4, 
        "method": "Runtime.evaluate", 
        "params": {"expression": js, "returnByValue": True}
    }))
    time.sleep(3) # Hold visual for 3 seconds before next iteration

def main():
    print("[C5-REAL] Initiating Batch CDP Dispatch (Iteration 1)...")
    try:
        with urllib.request.urlopen("http://localhost:9222/json") as r:
            targets = json.loads(r.read().decode())
    except Exception as e:
        print(f"[C4-ERROR] CDP Connection failed: {e}")
        return
        
    t = next((t for t in targets if t.get("type") == "page" and "reddit" in t.get("url", "").lower()), None)
    if not t:
        t = next((t for t in targets if t.get("type") == "page"), None)
    if not t:
        print("[C4-ERROR] No browser target found.")
        return
    
    ws = websocket.create_connection(t["webSocketDebuggerUrl"], suppress_origin=True)
    ws.send(json.dumps({"id": 1, "method": "Runtime.enable"}))
    ws.send(json.dumps({"id": 2, "method": "Page.enable"}))
    
    payloads = [
        ("https://www.reddit.com/r/singularity/new/", "Claim: AGIBOT A3 validates shift from Cloud Monoliths to Edge C5-REAL Runtimes."),
        ("https://www.reddit.com/r/cybersecurity/new/", "Claim: Hard-coded HTML leaks are symptoms of C1-Fragile deployment pipelines."),
        ("https://www.reddit.com/r/LocalLLaMA/new/", "Claim: Model benchmark rankings are irrelevant without an optimized execution engine.")
    ]
    
    for url, text in payloads:
        dispatch_payload(ws, url, text)
        
    print("[C5-REAL] All Iteration 1 Payloads Dispatched Successfully.")

if __name__ == "__main__":
    main()
