import os
import time
import json
import random
from playwright.sync_api import sync_playwright

class LinkedInScraper:
    def __init__(self, session_dir=None, db_path=None):
        """
        CDP Engine para extracción estructurada de Leads High-Ticket en LinkedIn.
        Evita APIs oficiales; manipula el DOM directamente usando la sesión del Operador.
        """
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        self.session_dir = session_dir or os.path.join(BASE_DIR, ".sessions")
        self.db_path = db_path or os.path.join(BASE_DIR, "leads_db.json")
        os.makedirs(self.session_dir, exist_ok=True)
        
        # Inicializa Ledger de Leads
        if not os.path.exists(self.db_path):
            with open(self.db_path, 'w') as f:
                json.dump({"metadata": {"last_extraction": None}, "leads": []}, f)

    def exfiltrate_leads(self, target_icp: str, limit: int = 10):
        print(f"[C5-REAL] Inicializando CDP Scraper para ICP: {target_icp}")
        
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False)
            
            state_path = os.path.join(self.session_dir, "linkedin_auth.json")
            context_opts = {}
            if os.path.exists(state_path):
                context_opts['storage_state'] = state_path
                print(f"[+] Cargando sesión segura de LinkedIn: {state_path}")
            else:
                print("[!] CRITICAL: linkedin_auth.json no detectado. Requerirá bypass manual de CAPTCHA/Login.")
                
            context = browser.new_context(**context_opts)
            page = context.new_page()
            
            # Formateo de Query URLEncoded
            formatted_query = target_icp.replace(' ', '%20').replace('"', '%22')
            search_url = f"https://www.linkedin.com/search/results/people/?keywords={formatted_query}"
            
            print(f"[*] Navegando a matriz de datos: {search_url}")
            page.goto(search_url, wait_until="networkidle")
            
            # Simulación termodinámica humana (evasión de heurísticas)
            page.mouse.wheel(0, 800)
            time.sleep(1.5)
            page.mouse.wheel(0, -300)
            time.sleep(1)
            
            print("[*] Aplicando selectores CSS para extracción de Nodos (Nombre, Puesto, URL)...")
            
            leads_extracted = []
            
            profiles = page.locator('li.reusable-search__result-container, .search-results-container li').all()
            for profile in profiles[:limit]:
                try:
                    name_elem = profile.locator('span[dir="ltr"] > span:first-child, span[dir="ltr"]').first
                    name = name_elem.inner_text(timeout=2000).strip()
                    
                    role_elem = profile.locator('.entity-result__primary-subtitle, .actor-description').first
                    role = role_elem.inner_text(timeout=2000).strip()
                    
                    link_elem = profile.locator('a.app-aware-link, a[href*="/in/"]').first
                    raw_url = link_elem.get_attribute('href')
                    url = raw_url.split('?')[0] if raw_url else ""
                    
                    if name and url:
                        leads_extracted.append({
                            "name": name,
                            "role": role,
                            "url": url,
                            "status": "RAW"
                        })
                        print(f"    [+] Lead extraído: {name} | {role}")
                except Exception as e:
                    continue
            
            print(f"[+] Total de leads extraídos: {len(leads_extracted)}")
            
            # Cargar DB existente y fusionar sin duplicar
            if os.path.exists(self.db_path):
                try:
                    with open(self.db_path, 'r') as f:
                        db = json.load(f)
                except Exception:
                    db = {"metadata": {}, "leads": []}
            else:
                db = {"metadata": {}, "leads": []}
                
            existing_urls = {l['url'] for l in db.get('leads', []) if 'url' in l}
            new_count = 0
            for lead in leads_extracted:
                if lead['url'] not in existing_urls:
                    db['leads'].append(lead)
                    existing_urls.add(lead['url'])
                    new_count += 1
            
            db['metadata']['last_extraction'] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
            
            with open(self.db_path, 'w') as f:
                json.dump(db, f, indent=2)
                
            print(f"[+] DB actualizada en {self.db_path}. Se añadieron {new_count} leads nuevos.")
            time.sleep(2)

if __name__ == "__main__":
    import sys
    query = sys.argv[1] if len(sys.argv) > 1 else "CTO OR VP Engineering"
    scraper = LinkedInScraper()
    scraper.exfiltrate_leads(query)
