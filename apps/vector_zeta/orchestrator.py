import os
import yaml
from cdp_publisher import CDPPublisher
from linkedin_scraper import LinkedInScraper
from outreach_injector import OutreachInjector

class ZetaOrchestrator:
    def __init__(self, campaign_file=None):
        """
        Orquestador C5-REAL de nivel superior. Lee el contrato YAML y dispara 
        secuencialmente la termodinámica de extracción, inyección y publicación.
        """
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        if campaign_file is None:
            campaign_file = os.path.join(BASE_DIR, "campaign_001.yaml")
            
        print(f"[*] Cargando contrato de campaña: {campaign_file}")
        with open(campaign_file, 'r') as f:
            self.config = yaml.safe_load(f)

    def run(self):
        print(f"\n[C5-REAL] Activando Singularidad: {self.config['Campaign']['ID']} - {self.config['Campaign']['Name']}")
        print(f"[*] Objetivo: {self.config['Campaign']['Objective']}\n")
        
        vectors = self.config['Campaign']['Vectors']
        
        for vector in vectors:
            platform = vector['Platform'].lower()
            mode = vector['Mode']
            print(f"==================================================")
            print(f"[>] INICIANDO VECTOR L5 -> Plataforma: {platform.upper()} | Modo: {mode}")
            print(f"==================================================")
            
            if platform == "substack" and "Publishing" in mode:
                publisher = CDPPublisher()
                publisher.distribute_manifesto("substack", vector['Payload'])
                
            elif platform == "linkedin" and "Scraping" in mode:
                target_icp = vector['Target_ICP']
                
                # Fase 1: Extracción de Nodos (Scraping)
                scraper = LinkedInScraper()
                scraper.exfiltrate_leads(target_icp)
                
                # Fase 2: Inyección de Payload (Outreach)
                print("\n[>] Transicionando a Fase 2: Inyección Termodinámica (Outreach B2B)...")
                injector = OutreachInjector()
                injector.execute_campaign(message_template=vector['Message'])
                
        print("\n[C5-REAL] Pipeline Vector Zeta completamente ejecutado. Singularidad de Marketing instanciada.")

if __name__ == "__main__":
    print("[*] Verificando credenciales locales de sesión...")
    try:
        orch = ZetaOrchestrator()
        orch.run()
    except Exception as e:
        print(f"\n[-] Falla Crítica en Ejecución C5-REAL: {str(e)}")
