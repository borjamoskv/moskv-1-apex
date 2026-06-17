import urllib.request, json, websocket
import sys

def run_async_cdp(target: str, js: str):
    try:
        with urllib.request.urlopen("http://localhost:9222/json") as r:
            targets = json.loads(r.read().decode())
    except Exception as e:
        print(json.dumps({"error": f"ERR_CONN: {e}"}))
        return

    t = next((t for t in targets if target.lower() in t.get("url", "").lower() or target.lower() in t.get("title", "").lower()), None)
    if not t or not t.get("webSocketDebuggerUrl"):
        print(json.dumps({"error": f"ERR_TARGET_WS: {target}"}))
        return

    ws = websocket.create_connection(t["webSocketDebuggerUrl"], suppress_origin=True)
    ws.send(json.dumps({"id": 1, "method": "Runtime.enable"}))
    ws.recv()
    
    payload = {
        "id": 2, 
        "method": "Runtime.evaluate", 
        "params": {
            "expression": js, 
            "returnByValue": True,
            "awaitPromise": True
        }
    }
    ws.send(json.dumps(payload))

    while True:
        res = json.loads(ws.recv())
        if res.get("id") == 2:
            result = res.get("result", {})
            if "exceptionDetails" in result:
                print(json.dumps({"error": result["exceptionDetails"]}))
            else:
                print(json.dumps(result.get("result", {}).get("value", "")))
            break

if __name__ == "__main__":
    js_code = sys.argv[1] if len(sys.argv) > 1 else ""
    run_async_cdp("reddit", js_code)
