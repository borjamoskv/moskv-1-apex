import os
import time
import json
import random
from playwright.sync_api import sync_playwright

class CDPPurgeBot:
    def __init__(self, session_dir=None, blacklist_path=None):
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        self.session_dir = session_dir or os.path.join(BASE_DIR, ".sessions")
        self.blacklist_path = blacklist_path or os.path.join(BASE_DIR, "spam_blacklist.json")
        os.makedirs(self.session_dir, exist_ok=True)

    def execute_purge(self):
        if not os.path.exists(self.blacklist_path):
            print("[*] No blacklist ledger found.")
            return

        with open(self.blacklist_path, 'r') as f:
            data = json.load(f)

        targets = [t for t in data.get('spam_traps', []) if t.get('status') == 'PURGE_REQUIRED' and t.get('platform') == 'Substack']
        
        if not targets:
            print("[*] No purge targets found in ledger.")
            return

        print(f"[C5-REAL] Iniciando secuencia de purga de Spam Traps en Substack...")

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False)
            state_path = os.path.join(self.session_dir, "substack_auth.json")
            context_opts = {}
            if os.path.exists(state_path):
                context_opts['storage_state'] = state_path
            
            context = browser.new_context(**context_opts)
            page = context.new_page()

            page.goto("https://substack.com/dashboard/subscribers", wait_until="networkidle")
            time.sleep(random.uniform(2.0, 4.0))

            for target in targets:
                email = target['email']
                print(f"[*] Localizando y erradicando: {email}")
                
                search_input = page.locator("input[placeholder*='Search']").first
                if search_input.is_visible():
                    search_input.click()
                    time.sleep(0.5)
                    search_input.fill(email)
                    page.keyboard.press("Enter")
                    time.sleep(random.uniform(2.0, 3.5))

                    print("\n==================================================")
                    print(f"[HITL GATE] VERIFICANDO ERRADICACIÓN DE: {email}")
                    print("==================================================")
                    ans = input("[C5-REAL] Por favor, elimina al usuario manualmente en la interfaz y escribe 'ok' para marcarlo en el ledger, o 'q' para abortar: ").strip().lower()
                    
                    if ans == 'ok':
                        target['status'] = 'PURGED'
                        print(f"[+] Entidad {email} purgada del ecosistema.")
                    elif ans == 'q':
                        break

            with open(self.blacklist_path, 'w') as f:
                json.dump(data, f, indent=2)

            print("[C5-REAL] Purga completada. Ledger actualizado.")

if __name__ == "__main__":
    bot = CDPPurgeBot()
    bot.execute_purge()
