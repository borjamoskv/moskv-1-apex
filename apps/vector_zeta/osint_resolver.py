import os
import json
import time
import random
import urllib.parse
import urllib.request
import re

class OSINTResolver:
    def __init__(self, thermal_mass_path=None, leads_db_path=None):
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        self.thermal_mass_path = thermal_mass_path or os.path.join(BASE_DIR, "thermal_mass.json")
        self.leads_db_path = leads_db_path or os.path.join(BASE_DIR, "leads_db.json")
        
    def _search_linkedin_ddg(self, name: str, email: str) -> str:
        """
        Búsqueda stealth en DuckDuckGo Lite para evitar bloqueo de API.
        Extrae el primer enlace de linkedin.com/in/.
        """
        if not name:
            name = email.split('@')[0]
        query = f'"{name}" "LinkedIn" site:linkedin.com/in'
        url = f"https://lite.duckduckgo.com/lite/"
        data = urllib.parse.urlencode({'q': query}).encode('utf-8')
        req = urllib.request.Request(url, data=data, headers={'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:109.0) Gecko/20100101 Firefox/111.0'})
        
        try:
            with urllib.request.urlopen(req, timeout=10) as response:
                html = response.read().decode('utf-8')
                
                # Regex para extraer links de duckduckgo que apuntan a linkedin
                links = re.findall(r'href="([^"]+linkedin\.com/in/[^"]+)"', html)
                if links:
                    # Duckduckgo lite a veces wrappea los enlaces. Extraer la URL limpia.
                    raw_link = links[0]
                    # Limpiar tracking (si aplica)
                    if "uddg=" in raw_link:
                        parsed = urllib.parse.parse_qs(urllib.parse.urlparse(raw_link).query)
                        if 'uddg' in parsed:
                            return parsed['uddg'][0]
                    return raw_link
        except Exception as e:
            print(f"[!] Fallo OSINT en nodo {name}: {e}")
        return None

    def execute_bridge(self):
        if not os.path.exists(self.thermal_mass_path):
            print("[-] Thermal Mass no encontrada. Ejecute substack_exergy_analyzer.py --export-thermal-mass primero.")
            return

        with open(self.thermal_mass_path, 'r') as f:
            data = json.load(f)
            
        leads = data.get('leads', [])
        if not leads:
            print("[*] No hay Masa Térmica para procesar.")
            return

        # Cargar Base de Datos Actual de Leads
        db = {"metadata": {"last_extraction": None}, "leads": []}
        if os.path.exists(self.leads_db_path):
            with open(self.leads_db_path, 'r') as f:
                db = json.load(f)

        existing_emails = {l.get('email') for l in db['leads']}

        print(f"[C5-REAL] Iniciando Pipeline OSINT Resolver sobre {len(leads)} nodos pasivos...")
        
        for idx, lead in enumerate(leads):
            email = lead.get('email')
            name = lead.get('name', '').strip()
            
            if email in existing_emails:
                print(f"[*] {email} ya existe en el Ledger (leads_db). Omitiendo.")
                continue
                
            print(f"[*] Extrayendo Identidad Vectorial para: {email} / {name}")
            
            # Rate limiting heurístico para no quemar el IP con DDG
            time.sleep(random.uniform(2.5, 5.0))
            
            linkedin_url = self._search_linkedin_ddg(name, email)
            
            status = 'RAW' if linkedin_url else 'MANUAL_REVIEW'
            
            new_lead = {
                "name": name if name else email.split('@')[0],
                "email": email,
                "url": linkedin_url,
                "status": status,
                "exergy_origin": lead.get('exergy', 0)
            }
            db['leads'].append(new_lead)
            existing_emails.add(email)
            
            if linkedin_url:
                print(f"    [+] Resuelto: {linkedin_url} (Status: RAW)")
            else:
                print(f"    [-] Requiere Revisión: No se encontró URL (Status: MANUAL_REVIEW)")

        with open(self.leads_db_path, 'w') as f:
            json.dump(db, f, indent=2)

        print("[C5-REAL] OSINT Bridge completado. Masa Térmica inyectada al flujo de Asalto.")

if __name__ == "__main__":
    resolver = OSINTResolver()
    resolver.execute_bridge()
