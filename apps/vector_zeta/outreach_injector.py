import os
import time
import json
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

class OutreachInjector:
    def __init__(self, session_dir=None, db_path=None):
        """
        Motor CDP para inyección de Cold Outreach (Mensajería B2B).
        Diseñado para operar bajo parámetros termodinámicos humanos y evitar bloqueos.
        """
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        self.session_dir = session_dir or os.path.join(BASE_DIR, ".sessions")
        self.db_path = db_path or os.path.join(BASE_DIR, "leads_db.json")
        os.makedirs(self.session_dir, exist_ok=True)

    def _load_leads(self) -> dict:
        if not os.path.exists(self.db_path):
            return {"metadata": {"last_extraction": None}, "leads": []}
        with open(self.db_path, 'r') as f:
            return json.load(f)

    def _save_leads(self, data: dict):
        with open(self.db_path, 'w') as f:
            json.dump(data, f, indent=2)

    def execute_campaign(self, message_template: str, limit: int = 5):
        print("[C5-REAL] Inicializando secuencias de inyección de Outreach...")
        db = self._load_leads()
        
        leads_to_process = [l for l in db.get('leads', []) if l.get('status') == 'RAW'][:limit]
        
        if not leads_to_process:
            print("[*] No hay leads pendientes (estado RAW) para procesar.")
            return

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False)
            
            state_path = os.path.join(self.session_dir, "linkedin_auth.json")
            context_opts = {}
            if os.path.exists(state_path):
                context_opts['storage_state'] = state_path
                print(f"[+] Cargando sesión segura de LinkedIn: {state_path}")
            else:
                print("[WARNING] No se encontró estado de sesión de LinkedIn. El script requerirá login manual en frío.")
            
            context = browser.new_context(**context_opts)
            page = context.new_page()
            
            for lead in leads_to_process:
                print(f"[*] Operando sobre Target: {lead.get('name')} | URL: {lead.get('url')}")
                
                # 1. Navegación al nodo
                page.goto(lead['url'], wait_until="domcontentloaded")
                time.sleep(random.uniform(2.5, 5.0)) # Jitter termodinámico
                
                # Scroll simulado
                page.mouse.wheel(0, random.randint(400, 700))
                time.sleep(random.uniform(1.5, 3.0))
                page.mouse.wheel(0, -random.randint(100, 300))
                time.sleep(random.uniform(1.0, 2.0))
                
                # 2. Resolución de la acción de conexión/mensaje (HITL Gate local)
                print("\n==================================================")
                print(f"[HITL GATE] REVISIÓN REQUERIDA PARA: {lead.get('name')}")
                print(f"URL: {lead.get('url')}")
                print("==================================================")
                ans = input("[C5-REAL] ¿Proceder con inyección automática de mensaje? (s/n para saltar, q para abortar campaña): ").strip().lower()
                
                if ans == 'q':
                    print("[!] Campaña abortada por el Operador.")
                    break
                elif ans != 's':
                    print(f"[*] Lead {lead.get('name')} saltado por el Operador.")
                    lead['status'] = 'SKIPPED'
                    self._save_leads(db)
                    continue

                try:
                    connect_button = page.locator("button.pvs-profile-actions__action:has-text('Connect'), button[aria-label*='Connect']").first
                    message_button = page.locator("button.pvs-profile-actions__action:has-text('Message'), button[aria-label*='Message']").first
                    
                    if connect_button.is_visible():
                        box = connect_button.bounding_box()
                        if box:
                            human_mouse_move(page, box['x'] + box['width']/2, box['y'] + box['height']/2)
                        connect_button.click()
                        time.sleep(random.uniform(1.5, 2.5))
                        
                        add_note_btn = page.locator("button[aria-label*='Add a note']").first
                        if add_note_btn.is_visible():
                            box_note = add_note_btn.bounding_box()
                            if box_note:
                                human_mouse_move(page, box_note['x'] + box_note['width']/2, box_note['y'] + box_note['height']/2)
                            add_note_btn.click()
                            time.sleep(random.uniform(1.0, 1.8))
                            
                        textarea = page.locator("textarea[name='message'], textarea#custom-message").first
                        if textarea.is_visible():
                            first_name = lead.get("name", "there").split()[0]
                            personalized_msg = message_template.replace("{{name}}", first_name)
                            type_like_human(page, textarea, personalized_msg)
                            time.sleep(random.uniform(1.0, 2.5))
                            
                            send_btn = page.locator("button[aria-label*='Send'], button:has-text('Send')").first
                            if send_btn.is_visible():
                                box_send = send_btn.bounding_box()
                                if box_send:
                                    human_mouse_move(page, box_send['x'] + box_send['width']/2, box_send['y'] + box_send['height']/2)
                                send_btn.click()
                                lead['status'] = 'INJECTED'
                                print(f"    [+] Payload inyectado exitosamente en solicitud de conexión.")
                            else:
                                print("    [-] No se encontró botón para enviar la nota.")
                                lead['status'] = 'ERROR'
                        else:
                            send_without_note = page.locator("button[aria-label*='Send without a note']").first
                            if send_without_note.is_visible():
                                send_without_note.click()
                                lead['status'] = 'INJECTED_NO_NOTE'
                                print(f"    [+] Solicitud de conexión enviada directamente (sin nota).")
                            else:
                                lead['status'] = 'ERROR'
                    elif message_button.is_visible():
                        box = message_button.bounding_box()
                        if box:
                            human_mouse_move(page, box['x'] + box['width']/2, box['y'] + box['height']/2)
                        message_button.click()
                        time.sleep(random.uniform(2.0, 3.0))
                        
                        chat_area = page.locator("div[contenteditable='true'], textarea[placeholder*='Write a message']").first
                        if chat_area.is_visible():
                            first_name = lead.get("name", "there").split()[0]
                            personalized_msg = message_template.replace("{{name}}", first_name)
                            type_like_human(page, chat_area, personalized_msg)
                            time.sleep(random.uniform(1.0, 2.0))
                            
                            send_btn = page.locator("button[type='submit'], button:has-text('Send')").first
                            if send_btn.is_visible():
                                send_btn.click()
                            else:
                                page.keyboard.press("Control+Enter")
                            lead['status'] = 'MESSAGE_INJECTED'
                            print(f"    [+] Mensaje directo inyectado exitosamente.")
                        else:
                            print("    [-] Chatbox no encontrado en el DOM.")
                            lead['status'] = 'ERROR'
                    else:
                        print("    [-] Target no presenta acción de Conectar o Mensaje disponible públicamente.")
                        lead['status'] = 'ERROR'
                except Exception as e:
                    print(f"    [-] Error en secuencia de inyección: {str(e)}")
                    lead['status'] = 'ERROR'
                
                self._save_leads(db)
                
                cooldown = random.uniform(30.0, 60.0)
                print(f"[*] Cooldown de seguridad: {cooldown:.2f}s activo...")
                time.sleep(cooldown)

            print("[C5-REAL] Secuencias de inyección de campaña de Outreach completadas. Ledger actualizado.")

if __name__ == "__main__":
    injector = OutreachInjector()
    payload = "Hola {{name}}, MOSKV-1 APEX es el fin de la anergía. Transicionemos tu infraestructura a C5-REAL."
    injector.execute_campaign(message_template=payload)
