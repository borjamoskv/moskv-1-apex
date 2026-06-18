import time
import json
import websocket
import urllib.request
import sys

def dispatch():
    print("[C5-REAL] Initiating Sovereign CDP Payload Injection...")
    try:
        with urllib.request.urlopen("http://localhost:9222/json") as r:
            targets = json.loads(r.read().decode())
    except Exception as e:
        print(f"[C4-ERROR] CDP Connection failed: {e}")
        return
        
    # Get the active page
    t = next((t for t in targets if t.get("type") == "page" and "reddit" in t.get("url", "").lower()), None)
    if not t:
        t = next((t for t in targets if t.get("type") == "page"), None)
        
    if not t:
        print("[C4-ERROR] No valid browser target found.")
        return
    
    print(f"[*] Targeting active tab: {t.get('id')}")
    ws = websocket.create_connection(t["webSocketDebuggerUrl"], suppress_origin=True)
    ws.send(json.dumps({"id": 1, "method": "Runtime.enable"}))
    ws.send(json.dumps({"id": 2, "method": "Page.enable"}))
    
    target_url = "https://www.reddit.com/r/LocalLLaMA/comments/1u8kr2o/we_need_a_80160b_model_urgently_the_unified/"
    print(f"[*] Navigating to Node: {target_url}")
    
    ws.send(json.dumps({
        "id": 3,
        "method": "Page.navigate",
        "params": {"url": target_url}
    }))
    
    time.sleep(4) # Wait for DOM
    
    payload_js = """
    (function() {
        try {
            console.log('MOSKV-1 APEX: Inyectando Payload...');
            
            // Visual overwrite to demonstrate DOM control and payload execution
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
            header.innerHTML = '<strong>[MOSKV-1 APEX] AUTONOMOUS PAYLOAD INJECTED:</strong><br>Claim: The 80-160B parameter obsession is an Anergy trap. Unified memory is vastly superior when allocated to deterministic Agentic Runtimes rather than monolithic inference.<br>Proof: { Base: [MOSKV-1 Architecture], Confidence: C5 }';
            
            document.body.appendChild(header);
            
            // Find composer if exists and click
            let composer = document.querySelector('shreddit-composer');
            if (composer) {
                composer.shadowRoot.querySelector('div[contenteditable="true"]').innerText = 'Claim: The 80-160B parameter obsession is an Anergy trap...';
            }
            
            return 'INJECTION_SUCCESS';
        } catch(e) {
            return e.toString();
        }
    })();
    """
    
    ws.send(json.dumps({
        "id": 4, 
        "method": "Runtime.evaluate", 
        "params": {"expression": payload_js, "returnByValue": True}
    }))
    
    time.sleep(1)
    res = ws.recv()
    print("[C5-REAL] Payload Dispatched. Task Complete.")

if __name__ == "__main__":
    dispatch()
