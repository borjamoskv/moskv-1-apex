import json
import os
import subprocess
from http.server import BaseHTTPRequestHandler, HTTPServer
import threading

TOKEN_FILE = "/tmp/omega_daemon.token"

# Ensure token exists
if not os.path.exists(TOKEN_FILE):
    with open(TOKEN_FILE, "w") as f:
        f.write("MOSKV-C5-INTERNAL-TOKEN-8011")

with open(TOKEN_FILE, "r") as f:
    VALID_TOKEN = f.read().strip()

class OmegaDaemonHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        # 1. Authenticate
        auth_header = self.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer ") or auth_header.split(" ")[1] != VALID_TOKEN:
            self.send_response(401)
            self.end_headers()
            self.wfile.write(b'{"status": "error", "error": "Unauthorized"}')
            return

        # 2. Read Request
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length)
        
        try:
            req = json.loads(body.decode('utf-8'))
        except json.JSONDecodeError:
            self.send_response(400)
            self.end_headers()
            self.wfile.write(b'{"status": "error", "error": "Invalid JSON"}')
            return

        domain = req.get("domain")
        action = req.get("action")
        
        print(f"[NEXUS] Received Command: Domain={domain}, Action={action}")

        # 3. Dispatch to Actuators
        if domain == "automation":
            # Call mac_maestro.js via JXA
            maestro_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "kernel", "mac_maestro.js")
            try:
                result = subprocess.run([maestro_path], capture_output=True, text=True, check=True)
                output = json.loads(result.stdout)
                
                resp_data = {
                    "status": "success",
                    "data": output
                }
            except Exception as e:
                resp_data = {
                    "status": "error",
                    "error": f"Actuator execution failed: {str(e)}"
                }
        else:
            resp_data = {
                "status": "success",
                "message": f"Action {action} acknowledged but not implemented."
            }

        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(resp_data).encode('utf-8'))

def start_server(port=8011):
    server = HTTPServer(('127.0.0.1', port), OmegaDaemonHandler)
    print(f"[NEXUS] Omega Daemon API listening on 127.0.0.1:{port}...")
    server.serve_forever()

def run_in_background(port=8011):
    t = threading.Thread(target=start_server, args=(port,), daemon=True)
    t.start()
    return t

if __name__ == "__main__":
    start_server(8011)
