import os
import time
from playwright.sync_api import sync_playwright

class SessionInitializer:
    def __init__(self, session_dir=None):
        """
        Utilidad para inicializar el Footprint C5-REAL (Estado de Sesión).
        Permite al Operador realizar un login manual una sola vez.
        El estado (cookies/localStorage) se exfiltra y persiste para automatizaciones CDP futuras.
        """
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        self.session_dir = session_dir or os.path.join(BASE_DIR, ".sessions")
        os.makedirs(self.session_dir, exist_ok=True)

    def generate_state(self, platform: str, target_url: str):
        state_file = os.path.join(self.session_dir, f"{platform}_auth.json")
        
        print(f"[C5-REAL] Inicializando Session Dumper para: {platform.upper()}")
        print(f"[*] Se abrirá una instancia de Chromium. Realiza el login manualmente.")
        print(f"[*] Una vez autenticado, cierra la ventana del navegador. El estado será guardado para futuras automatizaciones.")
        
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False)
            context = browser.new_context()
            page = context.new_page()
            
            page.goto(target_url)
            
            # Espera activa hasta que el Operador cierre la ventana
            print(f"[>] Esperando autenticación y cierre manual del navegador...")
            while len(context.pages) > 0:
                try:
                    time.sleep(1)
                except KeyboardInterrupt:
                    print("\n[!] Interrupción detectada. Guardando estado y saliendo...")
                    break
                    
            # Exfiltrar y persistir el estado (Footprint de la Sesión)
            context.storage_state(path=state_file)
            print(f"[+] Estado de sesión volcado en: {state_file}")

if __name__ == "__main__":
    import sys
    
    initializer = SessionInitializer()
    
    if len(sys.argv) > 1 and sys.argv[1] == "substack":
        initializer.generate_state("substack", "https://substack.com/sign-in")
    else:
        initializer.generate_state("linkedin", "https://www.linkedin.com/login")
