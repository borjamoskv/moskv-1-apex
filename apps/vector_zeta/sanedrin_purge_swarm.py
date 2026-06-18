import os
import time
import json
import random
from concurrent.futures import ThreadPoolExecutor
from playwright.sync_api import sync_playwright

class SanedrinSwarm:
    def __init__(self, session_dir=None, blacklist_path=None):
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        self.session_dir = session_dir or os.path.join(BASE_DIR, ".sessions")
        self.blacklist_path = blacklist_path or os.path.join(BASE_DIR, "spam_blacklist.json")
        os.makedirs(self.session_dir, exist_ok=True)

    def execute_purge(self):
        if not os.path.exists(self.blacklist_path):
            print("[SANEDRIN] Ledger vacío. Abortando mitigación.")
            return

        with open(self.blacklist_path, 'r') as f:
            data = json.load(f)

        targets = [t for t in data.get('spam_traps', []) if t.get('status') == 'PURGE_REQUIRED']
        if not targets:
            print("[SANEDRIN] No hay targets con status PURGE_REQUIRED.")
            return

        print(f"[C5-REAL] SANEDRIN SWARM INICIADO. Objetivos detectados: {len(targets)}.")
        
        # Procesamiento en paralelo
        with ThreadPoolExecutor(max_workers=min(5, len(targets))) as executor:
            futures = []
            for target in targets:
                futures.append(executor.submit(self._eradicate_target, target))
            
            for future in futures:
                target, success = future.result()
                if success:
                    target['status'] = 'PURGED_BY_SANEDRIN'
                else:
                    target['status'] = 'FAILED_PURGE'

        # Actualizar Ledger local
        with open(self.blacklist_path, 'w') as f:
            json.dump(data, f, indent=2)

        print("[C5-REAL] Operación de la Legión SANEDRIN completada. Exergía maximizada.")

    def _eradicate_target(self, target):
        email = target['email']
        platform = target.get('platform', 'Substack')
        
        if platform != 'Substack':
            print(f"[!] Target {email} no es de Substack.")
            return target, False

        state_path = os.path.join(self.session_dir, "substack_auth.json")
        context_opts = {'headless': True} # ZERO-GREEN THEATER
        
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                if os.path.exists(state_path):
                    context_opts['storage_state'] = state_path
                else:
                    print(f"[-] SANEDRIN Error: Falta sesión cacheada para {email}.")
                    return target, False
                
                context = browser.new_context(**context_opts)
                page = context.new_page()
                
                # Acceso Directo por API-like a la barra de suscriptores para reducir fricción
                print(f"[SANEDRIN-WORKER] Navegando silenciado para interceptar {email}...")
                page.goto("https://substack.com/dashboard/subscribers", wait_until="domcontentloaded")
                
                # Inyección de busqueda (Rápida, sin emular humanos lentos)
                search_input = page.locator("input[placeholder*='Search']").first
                search_input.wait_for(timeout=15000)
                search_input.fill(email)
                page.keyboard.press("Enter")
                
                # Pequeña espera asíncrona a la respuesta de Substack React
                page.wait_for_timeout(3000)
                
                # Buscar dropdown de opciones del suscriptor
                # Este selector es heurístico de UI Substack.
                more_options = page.locator("button[aria-label*='More'], button.dropdown-toggle, .subscriber-row button").first
                if more_options.is_visible():
                    more_options.click()
                    page.wait_for_timeout(500)
                    remove_btn = page.locator("button:has-text('Remove'), a:has-text('Remove subscriber')").first
                    if remove_btn.is_visible():
                        remove_btn.click()
                        # Podría requerir una segunda confirmación "Are you sure?"
                        confirm_btn = page.locator("button:has-text('Remove'), button:has-text('Confirm')").first
                        if confirm_btn.is_visible():
                            confirm_btn.click()
                        print(f"[+] SANEDRIN: {email} ha sido completamente erradicado.")
                        return target, True
                    else:
                        print(f"[-] SANEDRIN: Botón de Remove no expuesto para {email}.")
                else:
                    print(f"[-] SANEDRIN: No se encontraron opciones (posiblemente {email} ya no exista). Lo marcamos como fallido/revisar.")
                return target, False
        except Exception as e:
            print(f"[-] SANEDRIN ERROR FATAL para {email}: {e}")
            return target, False

if __name__ == "__main__":
    swarm = SanedrinSwarm()
    swarm.execute_purge()
