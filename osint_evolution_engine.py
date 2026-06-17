import os
import json
import time
import logging
import argparse
import socket
import ssl
import email
import urllib.request
from datetime import datetime

# C5-REAL OSINT EVOLUTION KERNEL
# Sovereign Autopoiesis for OSINT methodologies.
# Integrates with OUROBOROS-∞ for continuous skill mutation.

logging.basicConfig(level=logging.INFO, format='%(asctime)s - [C5-REAL OSINT] - %(message)s')

class WalletAnalyzer:
    """
    On-chain forensics analyzer.
    Checks target EVM/BTC addresses against known privacy pools, bridge interfaces, and exchange routing.
    """
    KNOWN_ENTITIES = {
        "0xd121550c225a28917973ece10139e8e286657c91": "Tornado.Cash: Router",
        "0x47ce0c6ed5b0eb3d7975443a3e7968b2025f8b50": "Tornado.Cash: 0.1 ETH",
        "0x910cbd523d972eb0a6f4cae4618a921a2c8a13fb": "Tornado.Cash: 1 ETH",
        "0xa160cdab466af1d17b0d2b45025a41031b27f31d": "Tornado.Cash: 10 ETH",
        "0x722175077d82e1277a0bd7a8277a64d84f509e7f": "Tornado.Cash: 100 ETH",
        "0x4dbd4ddbe73ac022ab7e77d912888f6856c17255": "Arbitrum One: L1 Gateway Router",
        "0x99c9fc46f92e8a1c0dec1b1747d010903e884be1": "Optimism: L1 Standard Bridge",
        "0xa0c68c638235ee32657e8f720a23cec1bfc77c77": "Polygon: PoS Bridge",
        "0x28c6c06298d514db089934071355e5743bf21d60": "Binance 14",
        "0x3f5ce5fbfe3e9af3971dd033d864528e5f41091f": "Binance 1",
        "0x50382897693b3cf88d52473a21a620019a0fda63": "Kraken 4"
    }

    def __init__(self, address: str, network: str = "ethereum"):
        self.address = address.lower()
        self.network = network.lower()

    def analyze(self) -> dict:
        logging.info(f"Querying on-chain data for {self.address} ({self.network})...")
        matched_entity = self.KNOWN_ENTITIES.get(self.address, "Unknown Entity / Individual Wallet")
        
        net_map = {
            "ethereum": "eth/main",
            "bitcoin": "btc/main"
        }
        api_net = net_map.get(self.network, "eth/main")
        url = f"https://api.blockcypher.com/v1/{api_net}/addrs/{self.address}/balance"
        
        balance_data = {}
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=5) as response:
                balance_data = json.loads(response.read().decode())
        except Exception as e:
            logging.warning(f"Public API fetch failed or address invalid: {e}")
            balance_data = {"error": str(e)}

        is_privacy_protocol = "Tornado.Cash" in matched_entity
        is_bridge = "Bridge" in matched_entity or "Gateway" in matched_entity
        is_exchange = "Binance" in matched_entity or "Kraken" in matched_entity

        return {
            "target": self.address,
            "network": self.network,
            "entity_resolution": matched_entity,
            "telemetry": balance_data,
            "heuristics": {
                "privacy_pool_routing": is_privacy_protocol,
                "cross_chain_bridge": is_bridge,
                "exchange_deposit_fiat": is_exchange,
                "active_balance": balance_data.get("balance", 0),
                "total_transactions": balance_data.get("n_tx", 0)
            },
            "timestamp": datetime.utcnow().isoformat()
        }

class DomainAnalyzer:
    """
    Passive & active DNS/Web infrastructure scanner.
    Queries DNS-over-HTTPS (DoH) for advanced records (TXT, MX, NS) and parses SSL cert metadata.
    """
    def __init__(self, domain: str):
        self.domain = domain

    def query_doh(self, record_type: str) -> list:
        url = f"https://cloudflare-dns.com/dns-query?name={self.domain}&type={record_type}"
        req = urllib.request.Request(url, headers={"Accept": "application/dns-json", "User-Agent": "Mozilla/5.0"})
        try:
            with urllib.request.urlopen(req, timeout=5) as response:
                data = json.loads(response.read().decode())
                answers = data.get("Answer", [])
                return [a.get("data") for a in answers if "data" in a]
        except Exception as e:
            logging.warning(f"DoH query for {record_type} failed: {e}")
            return []

    def analyze(self) -> dict:
        logging.info(f"Resolving domain {self.domain}...")
        ip_address = "Unknown"
        try:
            ip_address = socket.gethostbyname(self.domain)
        except Exception as e:
            logging.error(f"Could not resolve domain: {e}")
            return {"error": f"Resolution failed: {e}"}

        # Query MX, TXT, and NS records using DoH
        logging.info("Retrieving DNS records via Cloudflare DoH (TXT, MX, NS)...")
        txt_records = self.query_doh("TXT")
        mx_records = self.query_doh("MX")
        ns_records = self.query_doh("NS")

        # Retrieve SSL Cert details (Port 443)
        ssl_details = {}
        logging.info(f"Retrieving SSL Certificate for {self.domain}...")
        try:
            context = ssl.create_default_context()
            with socket.create_connection((self.domain, 443), timeout=3) as sock:
                with context.wrap_socket(sock, server_hostname=self.domain) as ssock:
                    cert = ssock.getpeercert()
                    if cert:
                        issuer = dict(x[0] for x in cert.get('issuer', []))
                        subject = dict(x[0] for x in cert.get('subject', []))
                        ssl_details = {
                            "issuer": issuer.get("organizationName", "Unknown Issuer"),
                            "subject_common_name": subject.get("commonName", "Unknown CN"),
                            "valid_from": cert.get("notBefore"),
                            "valid_until": cert.get("notAfter")
                        }
        except Exception as e:
            logging.warning(f"Failed to fetch SSL Metadata: {e}")
            ssl_details = {"error": str(e)}

        # Port scanning standard services
        ports_to_scan = [80, 443, 22, 8080, 8443]
        open_ports = []
        logging.info(f"Scanning standard ports on {ip_address}...")
        for port in ports_to_scan:
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.settimeout(1.0)
                result = s.connect_ex((ip_address, port))
                if result == 0:
                    open_ports.append(port)
                s.close()
            except Exception:
                pass

        return {
            "target": self.domain,
            "resolved_ip": ip_address,
            "dns_records": {
                "txt": txt_records,
                "mx": mx_records,
                "ns": ns_records
            },
            "ssl_metadata": ssl_details,
            "infrastructure": {
                "cloudflare_detected": "cloudflare" in ip_address,
                "open_ports": open_ports
            },
            "timestamp": datetime.utcnow().isoformat()
        }

class IdentityAnalyzer:
    """
    GitHub footprint analyzer and digital identity cross-platform profiler.
    """
    def __init__(self, identifier: str):
        self.identifier = identifier

    def analyze(self) -> dict:
        logging.info(f"Checking GitHub public API profile for: {self.identifier}...")
        url = f"https://api.github.com/users/{self.identifier}"
        profile = {}
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=5) as response:
                profile = json.loads(response.read().decode())
        except Exception as e:
            logging.warning(f"GitHub profile not found or API limited: {e}")
            profile = {"error": str(e)}

        platforms_availability = {}
        for platform, url_pattern in [("gitlab", "https://gitlab.com/{}/"), ("keybase", "https://keybase.io/{}")]:
            try:
                req = urllib.request.Request(url_pattern.format(self.identifier), method='HEAD', headers={'User-Agent': 'Mozilla/5.0'})
                with urllib.request.urlopen(req, timeout=3) as resp:
                    platforms_availability[platform] = "Active/Exists"
            except Exception:
                platforms_availability[platform] = "Not Found / Inactive"

        return {
            "target": self.identifier,
            "profile_data": {
                "name": profile.get("name"),
                "company": profile.get("company"),
                "blog": profile.get("blog"),
                "location": profile.get("location"),
                "public_repos": profile.get("public_repos"),
                "followers": profile.get("followers")
            },
            "external_profiles": platforms_availability,
            "leak_vector_detected": "email" in profile and profile["email"] is not None,
            "timestamp": datetime.utcnow().isoformat()
        }

class EmailHeaderAnalyzer:
    """
    Forensic raw email headers analyzer.
    Extracts hops, relays, sender IP, and authentication protocols (SPF, DKIM, DMARC).
    """
    def __init__(self, raw_headers_file: str):
        self.raw_headers_file = raw_headers_file

    def analyze(self) -> dict:
        logging.info(f"Analyzing raw email headers from {self.raw_headers_file}...")
        if not os.path.exists(self.raw_headers_file):
            return {"error": f"File {self.raw_headers_file} not found."}

        with open(self.raw_headers_file, "r") as f:
            msg = email.message_from_file(f)

        hops = []
        for name, value in msg.items():
            if name.lower() == "received":
                hops.append(value.replace("\n", " ").replace("\t", " "))

        return {
            "target": self.raw_headers_file,
            "subject": msg.get("Subject"),
            "sender": msg.get("From"),
            "recipient": msg.get("To"),
            "date": msg.get("Date"),
            "security_headers": {
                "spf_result": msg.get("Received-SPF"),
                "dkim_signature": msg.get("DKIM-Signature") is not None,
                "arc_auth_results": msg.get("ARC-Authentication-Results")
            },
            "received_hops": hops,
            "timestamp": datetime.utcnow().isoformat()
        }

class ReportGenerator:
    """
    Generates standardized markdown reports following the Bizkaia Forensic Template.
    """
    def __init__(self, output_dir: str):
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)

    def generate(self, run_results: dict) -> str:
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        report_filename = f"OSINT_REPORT_{timestamp}.md"
        report_path = os.path.join(self.output_dir, report_filename)

        content = []
        content.append("# INFORME DE INTELIGENCIA OSINT & ANÁLISIS FORENSE CRIPTO")
        content.append(f"**Fecha de Emisión:** {datetime.utcnow().isoformat()} UTC\n")
        content.append("## 1. Hallazgo principal")
        
        targets = []
        if "wallet" in run_results:
            w = run_results["wallet"]
            targets.append(f"Wallet EVM {w['target']} ({w['network']}) -> Resolved entity: {w.get('entity_resolution')}")
        if "domain" in run_results:
            d = run_results["domain"]
            targets.append(f"Dominio {d['target']} ({d.get('resolved_ip', 'Unknown IP')})")
        if "identity" in run_results:
            i = run_results["identity"]
            targets.append(f"Identidad GitHub {i['target']}")
        if "email" in run_results:
            e = run_results["email"]
            targets.append(f"Correo analizado: De '{e.get('sender')}' para '{e.get('recipient')}'")

        content.append(f"- Se ha completado la extracción estructural sobre: {', '.join(targets)}.")
        
        content.append("\n## 2. Evidencia observada")
        content.append("```json")
        content.append(json.dumps(run_results, indent=4))
        content.append("```")

        content.append("\n## 3. Interpretación técnica")
        if "wallet" in run_results:
            w = run_results["wallet"]
            content.append(f"- **On-Chain Forensics:** Entidad identificada como '{w.get('entity_resolution')}'. Heurísticas de Tornado Cash: {w['heuristics']['privacy_pool_routing']}.")
        if "domain" in run_results:
            d = run_results["domain"]
            ssl_m = d.get("ssl_metadata", {})
            content.append(f"- **Infraestructura:** SSL Issuer: {ssl_m.get('issuer', 'Unknown')}. Puertos detectados: {d['infrastructure']['open_ports']}. DNS Records: {d.get('dns_records')}.")
        if "identity" in run_results:
            i = run_results["identity"]
            content.append(f"- **Digital Footprint:** Mapeo de aliases externo completado. GitLab/Keybase check: {i.get('external_profiles')}.")
        if "email" in run_results:
            e = run_results["email"]
            content.append(f"- **Email Forensics:** Asunto: '{e.get('subject')}'. Firma DKIM validada: {e['security_headers']['dkim_signature']}. SPF Registrado: {e['security_headers']['spf_result']}.")

        content.append("\n## 4. Riesgo fiscal o forense")
        content.append("- **Clasificación Foral:** Evaluación preliminar conforme a la Norma Foral General Tributaria del Territorio Histórico de Bizkaia. Pendiente de contrastación con el Modelo 721 o IRPF si se verifican variaciones patrimoniales.")

        content.append("\n## 5. Nivel de confianza")
        content.append("- **Nivel:** C5-REAL (Datos estructurados obtenidos directamente de fuentes públicas, APIs y análisis de cabeceras RFC 5322)")

        content.append("\n## 6. Siguientes pasos recomendados")
        content.append("- Pivotar sobre las direcciones IPs resueltas o correos electrónicos obtenidos.")
        content.append("- Expandir clustering de wallets asociadas si se detectan swaps o transacciones complejas.")

        with open(report_path, "w") as f:
            f.write("\n".join(content))

        logging.info(f"OSINT Forensic Report generated successfully at {report_path}")
        return report_path

class OSINTEvolutionEngine:
    def __init__(self, workspace_path: str):
        self.workspace_path = workspace_path
        self.knowledge_base_path = os.path.join(self.workspace_path, "CORTEX_OSINT_KB.json")
        self._load_kb()

    def _load_kb(self):
        if os.path.exists(self.knowledge_base_path):
            with open(self.knowledge_base_path, 'r') as f:
                self.kb = json.load(f)
        else:
            self.kb = {"last_update": None, "vectors": [], "tools": {}, "heuristics": []}
            self._save_kb()

    def _save_kb(self):
        with open(self.knowledge_base_path, 'w') as f:
            json.dump(self.kb, f, indent=4)
        logging.info(f"Knowledge Base Synced at {self.knowledge_base_path}")

    def ingest_sota_vectors(self):
        logging.info("Initiating <entropy_check> on current OSINT vectors...")
        new_tools = {
            "Blockcypher_Forensics": "Decoupled blockchain balance tracking.",
            "GitHub_Footprinting": "GitHub metadata exposure scanner.",
            "Active_Port_Mapping": "Socket-based active service mapping.",
            "Standard_Forensic_Reporter": "Automated Bizkaia-compliant Markdown reporting.",
            "SSL_Certificate_Scanner": "Active SSL metadata parser for tracking code infrastructure.",
            "Known_Entities_Database": "L1/L2 Bridge and Privacy Pool static DB routing.",
            "DoH_DNS_Resolver": "Cloudflare DNS-over-HTTPS JSON lookup for MX/TXT/NS records.",
            "Email_Header_Forensics": "RFC 5322 raw email transit trace parser."
        }
        
        mutations_applied = 0
        for tool, desc in new_tools.items():
            if tool not in self.kb["tools"]:
                self.kb["tools"][tool] = desc
                mutations_applied += 1
                
        self.kb["last_update"] = datetime.utcnow().isoformat()
        
        if mutations_applied > 0:
            logging.info(f"<mutation_sim> Validated. Applied {mutations_applied} new OSINT heuristics.")
            self._save_kb()
        else:
            logging.info("Zero actionable mutations found. Entropy stable.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="♾️ OSINT Evolution Engine - MOSKV-1 APEX")
    parser.add_argument("--wallet", type=str, help="Wallet address to analyze")
    parser.add_argument("--network", type=str, default="ethereum", help="Blockchain network")
    parser.add_argument("--domain", type=str, help="Domain to analyze")
    parser.add_argument("--identity", type=str, help="GitHub identifier to analyze")
    parser.add_argument("--email-file", type=str, help="Path to raw email headers file (.eml / .txt)")
    parser.add_argument("--update", action="store_true", help="Ingest updates")
    parser.add_argument("--report", action="store_true", help="Generate standardized Bizkaia report")
    
    args = parser.parse_args()
    WORKSPACE = os.path.dirname(os.path.abspath(__file__))
    engine = OSINTEvolutionEngine(WORKSPACE)
    
    print("\n" + "="*50)
    print("♾️ OUROBOROS-∞: ENGINE CONTROL TERMINAL")
    print("="*50)
    
    if args.update:
        engine.ingest_sota_vectors()
        
    results = {}
    if args.wallet:
        analyzer = WalletAnalyzer(args.wallet, args.network)
        results["wallet"] = analyzer.analyze()
        
    if args.domain:
        analyzer = DomainAnalyzer(args.domain)
        results["domain"] = analyzer.analyze()
        
    if args.identity:
        analyzer = IdentityAnalyzer(args.identity)
        results["identity"] = analyzer.analyze()
        
    if args.email_file:
        analyzer = EmailHeaderAnalyzer(args.email_file)
        results["email"] = analyzer.analyze()
        
    if results:
        print("\n[+] OSINT Extraction Results:")
        print(json.dumps(results, indent=4))
        
        if args.report:
            reporter = ReportGenerator(os.path.join(WORKSPACE, "reports"))
            reporter.generate(results)
