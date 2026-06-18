import os
import time
import random
from playwright.sync_api import sync_playwright

def human_mouse_move(page, end_x, end_y):
    start_x = random.randint(100, 500)
    start_y = random.randint(100, 500)
    steps = random.randint(15, 30)
    for i in range(1, steps + 1):
        t = i / steps
        t_smooth = t * t * (3 - 2 * t)
        curr_x = start_x + (end_x - start_x) * t_smooth + random.uniform(-2, 2)
        curr_y = start_y + (end_y - start_y) * t_smooth + random.uniform(-2, 2)
        page.mouse.move(curr_x, curr_y)
        time.sleep(random.uniform(0.01, 0.03))

def type_like_human(page, locator, text):
    locator.click()
    time.sleep(random.uniform(0.2, 0.5))
    for char in text:
        page.keyboard.send_character(char)
        delay = random.uniform(0.05, 0.15)
        if random.random() < 0.05:
            delay += random.uniform(0.3, 0.7)
        time.sleep(delay)

class CDPPublisher:
    def __init__(self, session_dir=None):
        """
        Instanciación del motor de extracción y publicación basado en CDP.
        C5-REAL: Operamos sobre sesiones reales (cookies/localStorage) para evadir Bot-Protection.
        """
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        self.session_dir = session_dir or os.path.join(BASE_DIR, ".sessions")
        os.makedirs(self.session_dir, exist_ok=True)

    def distribute_manifesto(self, target_platform: str, content_path: str):
        if target_platform.lower() == "substack":
            self._publish_substack(content_path)
        else:
            raise NotImplementedError(f"Target {target_platform} no implementado en CDP estructural.")

    def _publish_substack(self, content_path: str):
        if not os.path.exists(content_path):
            raise FileNotFoundError(f"Archivo de contenido no encontrado en {content_path}")
            
        with open(content_path, 'r') as f:
            content = f.read()
            
        # Parsear título y cuerpo
        lines = content.strip().split('\n')
        title = ""
        body_lines = []
        if lines and lines[0].startswith('#'):
            title = lines[0].lstrip('#').strip()
            body_lines = lines[1:]
        else:
            title = "Manifiesto MOSKV-1 APEX"
            body_lines = lines
            
        body = '\n'.join(body_lines).strip()
            
        print(f"[C5-REAL] Inicializando Chromium CDP para {content_path}")
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False)
            
            context_opts = {}
            state_path = os.path.join(self.session_dir, "substack_auth.json")
            if os.path.exists(state_path):
                context_opts['storage_state'] = state_path
                print(f"[+] Cargando sesión segura de Substack: {state_path}")
            else:
                print("[WARNING] No se encontró estado de sesión. El script requerirá login manual en frío.")
                
            context = browser.new_context(**context_opts)
            page = context.new_page()
            
            # Navegación determinista
            print("[*] Navegando a Substack Dashboard...")
            page.goto("https://substack.com/dashboard", wait_until="networkidle")
            
            # Comportamiento humano inicial
            page.mouse.move(random.randint(100, 600), random.randint(100, 600))
            time.sleep(random.uniform(1.0, 2.0))
            
            # Navegar a la página de nuevo post
            print("[*] Navegando a la sección de edición...")
            page.goto("https://substack.com/dashboard/publish", wait_until="networkidle")
            time.sleep(random.uniform(1.5, 3.0))
            
            # Buscar el botón de "New post" y pulsar
            new_post_btn = page.locator("a[href*='/publish/post'], button:has-text('New post'), a:has-text('New post')").first
            if new_post_btn.is_visible():
                box = new_post_btn.bounding_box()
                if box:
                    human_mouse_move(page, box['x'] + box['width']/2, box['y'] + box['height']/2)
                new_post_btn.click()
                time.sleep(random.uniform(3.0, 5.0))
            else:
                # Tratar de navegar directamente a la URL de edición si el botón no es visible
                user_subdomain = page.url.split('/')[2].split('.')[0]
                if user_subdomain and user_subdomain != "substack":
                    page.goto(f"https://{user_subdomain}.substack.com/publish/post", wait_until="networkidle")
                    time.sleep(random.uniform(3.0, 5.0))
            
            # Llenar título y cuerpo
            print("[*] Inyectando borrador con emulación humana...")
            title_field = page.locator("textarea[placeholder='Title'], input[placeholder='Title']").first
            if title_field.is_visible():
                type_like_human(page, title_field, title)
                time.sleep(random.uniform(1.0, 2.0))
            
            body_field = page.locator("div[contenteditable='true'], .ProseMirror").first
            if body_field.is_visible():
                body_field.click()
                time.sleep(random.uniform(0.5, 1.0))
                page.keyboard.insert_text(body)
                time.sleep(random.uniform(2.0, 4.0))
            
            # HITL Gate en local
            print("\n==================================================")
            print("[HITL GATE] ESPERANDO REVISIÓN HUMANA LOCAL...")
            print("==================================================")
            print("El borrador del manifiesto ha sido inyectado en el navegador.")
            print("Por favor, revise el formato y realice los ajustes necesarios en la interfaz.")
            decision = input("[C5-REAL] Escriba 'publicar' para automatizar el envío, o presione ENTER para finalizar y dejar el navegador abierto: ").strip().lower()
            
            if decision == 'publicar':
                print("[*] Ejecutando secuencia de publicación automatizada...")
                publish_btn = page.locator("button:has-text('Publish'), button:has-text('Continue')").first
                if publish_btn.is_visible():
                    box = publish_btn.bounding_box()
                    if box:
                        human_mouse_move(page, box['x'] + box['width']/2, box['y'] + box['height']/2)
                    publish_btn.click()
                    time.sleep(random.uniform(2.0, 3.5))
                    
                    confirm_btn = page.locator("button:has-text('Send to everyone now'), button:has-text('Publish now')").first
                    if confirm_btn.is_visible():
                        box_confirm = confirm_btn.bounding_box()
                        if box_confirm:
                            human_mouse_move(page, box_confirm['x'] + box_confirm['width']/2, box_confirm['y'] + box_confirm['height']/2)
                        confirm_btn.click()
                        print("[+] Publicación inyectada exitosamente.")
                        time.sleep(5)
                    else:
                        print("[-] Botón final de confirmación no encontrado.")
                else:
                    print("[-] Botón de publicación inicial no encontrado.")
            else:
                print("[*] Finalización local. El navegador permanecerá abierto para tu gestión manual.")
                while len(context.pages) > 0:
                    time.sleep(1)

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        publisher = CDPPublisher()
        publisher.distribute_manifesto("substack", sys.argv[1])
