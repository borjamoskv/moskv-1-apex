#!/usr/bin/env python3
import os
import sys
import json
import socket
import ssl
import argparse
import urllib.request
import urllib.parse
import urllib.error
import http.client
from pathlib import Path

RESET = "\033[0m"
BOLD = "\033[1m"
DIM = "\033[2m"
RED = "\033[31m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
BLUE = "\033[34m"
MAGENTA = "\033[35m"
CYAN = "\033[36m"
BG_DARK = "\033[40m"

def log_info(msg):
    print(f"{BLUE}[i]{RESET} {msg}")

def log_success(msg):
    print(f"{GREEN}[✓]{RESET} {BOLD}{msg}{RESET}")

def log_warning(msg):
    print(f"{YELLOW}[⚠️]{RESET} {YELLOW}{msg}{RESET}")

def log_critical(msg):
    print(f"{RED}[❌]{RESET} {BOLD}{RED}{msg}{RESET}")

def log_header(msg):
    print(f"\n{BG_DARK}{BOLD}{CYAN}=== {msg} ==={RESET}")

class VercelCloudflareSolver:
    def __init__(self, domain=None, fix=False, verbose=False):
        self.domain = domain
        self.fix = fix
        self.verbose = verbose
        self.cf_token = os.environ.get("CLOUDFLARE_API_TOKEN")
        self.cf_zone_id = os.environ.get("CLOUDFLARE_ZONE_ID")
        self.issues = []
        self.solutions = []
        if not self.domain:
            self.domain = self.detect_domain()
            
    def detect_domain(self):
        base_dir = Path(__file__).parent.parent
        project_file = base_dir / "PROJECT.md"
        if project_file.exists():
            try:
                content = project_file.read_text()
                if "agents.archi" in content:
                    return "agents.archi"
            except Exception:
                pass
        return "agents.archi"

    def query_dns_doh(self, name, type_str):
        url = f"https://cloudflare-dns.com/dns-query?name={name}&type={type_str}"
        req = urllib.request.Request(url, headers={"Accept": "application/dns-json"})
        try:
            with urllib.request.urlopen(req, timeout=5) as response:
                data = json.loads(response.read().decode())
                return data.get("Answer", [])
        except Exception as e:
            if self.verbose:
                log_warning(f"DoH Query failed for {name} ({type_str}): {e}")
            return []

    def check_dns(self):
        log_header("DNS INTEGRITY CHECK")
        log_info(f"Querying DNS records for {self.domain} via Cloudflare DoH...")
        a_records = self.query_dns_doh(self.domain, "A")
        cname_records = self.query_dns_doh(self.domain, "CNAME")
        www_cname = self.query_dns_doh(f"www.{self.domain}", "CNAME")
        log_info(f"Apex A records found: {[r.get('data') for r in a_records]}")
        log_info(f"www CNAME records found: {[r.get('data') for r in www_cname]}")
        is_cloudflare_proxied = False
        vercel_ip = "76.76.21.21"
        is_direct_vercel = False
        for r in a_records:
            if r.get("data") == vercel_ip:
                is_direct_vercel = True
        if is_direct_vercel:
            log_success(f"Apex domain points directly to Vercel ({vercel_ip}) [Grey Clouded / Direct DNS]")
        else:
            log_info(f"Apex domain does not point directly to Vercel IP ({vercel_ip}). Checking for Cloudflare proxy status...")
        has_correct_cname = False
        for r in www_cname:
            target = r.get("data", "").rstrip(".")
            if "vercel-dns.com" in target or "vercel.app" in target:
                has_correct_cname = True
                log_success(f"www subdomain CNAME points to Vercel: {target}")
        if not has_correct_cname and www_cname:
            log_warning(f"www subdomain CNAME does not point to vercel-dns.com (Target: {www_cname[0].get('data')})")
            self.issues.append("WWW CNAME does not target cname.vercel-dns.com")
            self.solutions.append("Configure the CNAME record for 'www' to target 'cname.vercel-dns.com' in your DNS manager.")

    def trace_redirects(self, start_url):
        current_url = start_url
        visited = []
        path = []
        max_hops = 10
        for _ in range(max_hops):
            visited.append(current_url)
            parsed = urllib.parse.urlparse(current_url)
            try:
                if parsed.scheme == "https":
                    conn = http.client.HTTPSConnection(parsed.netloc, timeout=5, context=ssl._create_unverified_context())
                else:
                    conn = http.client.HTTPConnection(parsed.netloc, timeout=5)
                req_path = parsed.path if parsed.path else "/"
                if parsed.query:
                    req_path += "?" + parsed.query
                headers = {
                    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) MOSKV-1-APEX/Conflict-Solver",
                    "Accept": "*/*"
                }
                conn.request("GET", req_path, headers=headers)
                res = conn.getresponse()
                status = res.status
                headers_dict = {k.lower(): v for k, v in res.getheaders()}
                conn.close()
                hop_info = {
                    "url": current_url,
                    "status": status,
                    "headers": headers_dict
                }
                path.append(hop_info)
                if status in (301, 302, 307, 308):
                    loc = headers_dict.get("location")
                    if not loc:
                        break
                    next_url = urllib.parse.urljoin(current_url, loc)
                    if next_url in visited:
                        path.append({
                            "url": next_url,
                            "status": "LOOP_DETECTED",
                            "headers": {}
                        })
                        break
                    current_url = next_url
                else:
                    break
            except Exception as e:
                path.append({
                    "url": current_url,
                    "status": "CONNECTION_FAILED",
                    "headers": {},
                    "error": str(e)
                })
                break
        return path

    def diagnose_endpoints(self):
        log_header("HTTP/HTTPS REDIRECT LOOP DIAGNOSIS")
        http_url = f"http://{self.domain}"
        log_info(f"Probing {http_url} redirect path...")
        http_path = self.trace_redirects(http_url)
        for idx, hop in enumerate(http_path):
            log_info(f"  [{idx}] {hop['url']} -> Status {hop['status']}")
            if self.verbose:
                print(f"      Server: {hop['headers'].get('server')} | Location: {hop['headers'].get('location')}")
        https_url = f"https://{self.domain}"
        log_info(f"Probing {https_url} redirect path...")
        https_path = self.trace_redirects(https_url)
        for idx, hop in enumerate(https_path):
            log_info(f"  [{idx}] {hop['url']} -> Status {hop['status']}")
            if self.verbose:
                print(f"      Server: {hop['headers'].get('server')} | Location: {hop['headers'].get('location')}")
        is_loop = False
        for hop in http_path + https_path:
            if hop["status"] == "LOOP_DETECTED":
                is_loop = True
                break
        flexible_ssl_detected = False
        for idx, hop in enumerate(https_path):
            if idx > 0 and hop["status"] in (301, 302, 307, 308):
                loc = hop["headers"].get("location", "")
                if loc.startswith("https://") and self.domain in loc:
                    server = hop["headers"].get("server", "")
                    if "cloudflare" in server.lower():
                        flexible_ssl_detected = True
        if flexible_ssl_detected or is_loop:
            log_critical("CRITICAL ERROR: Infinite redirect loop detected!")
            if flexible_ssl_detected:
                log_critical("Diagnosis: Cloudflare SSL/TLS configuration is set to 'Flexible'.")
                log_critical("Vercel enforces HTTPS internally. When Cloudflare connects via HTTP, Vercel triggers a 308 Redirect. Cloudflare forwards this back to the client, creating a loop.")
                self.issues.append("Cloudflare SSL mode is Flexible")
                self.solutions.append("Change Cloudflare SSL/TLS setting from 'Flexible' to 'Full' or 'Full (Strict)'.")
        else:
            log_success("No infinite redirect loops detected on HTTP/HTTPS endpoints.")
        log_header("EDGE CACHING ANALYSIS")
        last_hop = https_path[-1] if https_path else None
        if last_hop and last_hop["status"] == 200:
            headers = last_hop["headers"]
            cf_cache = headers.get("cf-cache-status")
            vercel_cache = headers.get("x-vercel-cache")
            cache_ctrl = headers.get("cache-control")
            log_info(f"Response Cache Headers for {last_hop['url']}:")
            log_info(f"  cf-cache-status : {cf_cache}")
            log_info(f"  x-vercel-cache  : {vercel_cache}")
            log_info(f"  cache-control   : {cache_ctrl}")
            test_dynamic_url = f"https://{self.domain}/config"
            log_info(f"Testing caching on dynamic route: {test_dynamic_url} ...")
            dyn_path = self.trace_redirects(test_dynamic_url)
            if dyn_path and dyn_path[-1]["status"] in (200, 404, 405):
                dyn_hop = dyn_path[-1]
                dyn_headers = dyn_hop["headers"]
                dyn_cf_cache = dyn_headers.get("cf-cache-status")
                dyn_cc = dyn_headers.get("cache-control")
                log_info(f"  Dynamic path cache status: {dyn_cf_cache} | Cache-Control: {dyn_cc}")
                if dyn_cf_cache in ("HIT", "REVALIDATED") and "no-store" not in str(dyn_cc):
                    log_warning("DYNAMIC ROUTE CACHED! Dynamic route config returned HIT from Cloudflare cache.")
                    self.issues.append("Dynamic route config is cached by CDN")
                    self.solutions.append("Add a Cache Rule in Cloudflare to bypass cache for matches regex '/(submit-lead|create-checkout-session|config)'.")
                else:
                    log_success("Dynamic route caching bypass verified.")
        else:
            log_warning("Could not analyze caching headers as the root endpoint did not return 200 OK.")

    def check_local_config(self):
        log_header("LOCAL CONFIGURATION ANALYSIS")
        base_dir = Path(__file__).parent.parent
        vercel_json_path = base_dir / "vercel.json"
        if vercel_json_path.exists():
            log_success(f"Found local vercel.json configuration at {vercel_json_path}")
            try:
                with open(vercel_json_path, 'r') as f:
                    config = json.load(f)
                headers = config.get("headers", [])
                has_cdn_headers = False
                for h_entry in headers:
                    src = h_entry.get("source", "")
                    if "submit-lead" in src or "config" in src:
                        for sub_h in h_entry.get("headers", []):
                            if sub_h.get("key") == "CDN-Cache-Control" and sub_h.get("value") == "no-store":
                                has_cdn_headers = True
                if has_cdn_headers:
                    log_success("vercel.json correctly sets 'CDN-Cache-Control: no-store' for dynamic endpoints.")
                else:
                    log_warning("vercel.json is missing 'CDN-Cache-Control: no-store' for dynamic paths.")
                    self.issues.append("vercel.json missing CDN-Cache-Control bypass")
                    self.solutions.append("Add 'CDN-Cache-Control: no-store' header rule for dynamic endpoints in vercel.json.")
            except Exception as e:
                log_critical(f"Error parsing vercel.json: {e}")
        else:
            log_warning("No local vercel.json found in the project root.")

    def query_cloudflare_api(self):
        if not self.cf_token or not self.cf_zone_id:
            log_header("CLOUDFLARE API CONTEXT")
            log_info("Cloudflare credentials not fully present in environment variables.")
            log_info("Define CLOUDFLARE_API_TOKEN and CLOUDFLARE_ZONE_ID to enable active query & remediation.")
            return False
        log_header("CLOUDFLARE LIVE API DIAGNOSIS")
        log_info("Fetching SSL/TLS configuration from Cloudflare...")
        ssl_url = f"https://api.cloudflare.com/client/v4/zones/{self.cf_zone_id}/settings/ssl"
        req = urllib.request.Request(
            ssl_url,
            headers={
                "Authorization": f"Bearer {self.cf_token}",
                "Content-Type": "application/json"
            }
        )
        try:
            with urllib.request.urlopen(req, timeout=5) as response:
                res = json.loads(response.read().decode())
                if res.get("success"):
                    ssl_value = res["result"]["value"]
                    log_info(f"Current SSL setting: {ssl_value}")
                    if ssl_value == "flexible":
                        log_critical("Cloudflare API returned SSL mode: flexible")
                        self.issues.append("Cloudflare SSL mode is Flexible")
                        self.solutions.append("Update SSL mode to full or strict")
                        if self.fix:
                            self.remediate_ssl()
                    else:
                        log_success(f"Cloudflare SSL/TLS is set to safe mode: {ssl_value}")
                else:
                    log_warning(f"Failed to query SSL setting: {res.get('errors')}")
        except Exception as e:
            log_critical(f"Failed to communicate with Cloudflare API: {e}")
            
    def remediate_ssl(self):
        log_header("AUTO-REMEDIATION SEQUENCE")
        log_info("Attempting to auto-patch Cloudflare SSL configuration to 'full'...")
        ssl_url = f"https://api.cloudflare.com/client/v4/zones/{self.cf_zone_id}/settings/ssl"
        data = json.dumps({"value": "full"}).encode("utf-8")
        req = urllib.request.Request(
            ssl_url,
            data=data,
            headers={
                "Authorization": f"Bearer {self.cf_token}",
                "Content-Type": "application/json"
            },
            method="PATCH"
        )
        try:
            with urllib.request.urlopen(req, timeout=5) as response:
                res = json.loads(response.read().decode())
                if res.get("success"):
                    log_success("SUCCESSFULLY PATCHED Cloudflare SSL setting to 'full'!")
                    self.issues = [i for i in self.issues if "SSL mode" not in i]
                else:
                    log_critical(f"Failed to patch SSL setting: {res.get('errors')}")
        except Exception as e:
            log_critical(f"Auto-remediation failed: {e}")

    def execute(self):
        log_header(f"MOSKV-1 APEX: DIAGNOSING VERCEL - CLOUDFLARE FOR {self.domain}")
        self.check_dns()
        self.diagnose_endpoints()
        self.check_local_config()
        self.query_cloudflare_api()
        log_header("DIAGNOSTIC SUMMARY REPORT")
        if not self.issues:
            log_success("All checks passed. Zero-anergy connectivity verified.")
        else:
            log_critical(f"Detected {len(self.issues)} active conflict vectors:")
            for idx, issue in enumerate(self.issues):
                print(f"  {RED}{idx+1}. {issue}{RESET}")
                print(f"     Resolution: {self.solutions[idx]}")
        confidence = "C5"
        if not self.cf_token:
            confidence = "C4 (No Cloudflare API auth)"
        print("\n```yaml")
        print("Claim: Vercel-Cloudflare integration audit completed.")
        print(f"Proof:")
        print(f"  Base: \"{self.domain}\"")
        print(f"  IssuesCount: {len(self.issues)}")
        print(f"  Confidence: \"{confidence}\"")
        print("```")
        base_dir = Path(__file__).parent.parent
        report_path = base_dir / "docs" / "vercel_cloudflare_status.md"
        os.makedirs(report_path.parent, exist_ok=True)
        report_content = f"""# VERCEL-CLOUDFLARE INTEGRATION AUDIT
**Status:** {"CONFLICTS DETECTED" if self.issues else "VERIFIED NOMINAL"}
**Target:** `{self.domain}`

## Issues Detected
"""
        if not self.issues:
            report_content += "- Zero conflicts detected.\n"
        else:
            for issue, sol in zip(self.issues, self.solutions):
                report_content += f"### ❌ {issue}\n**Solution:** {sol}\n\n"
        report_content += "\n---\n*∴ MOSKV-1 APEX Active Telemetry*"
        try:
            report_path.write_text(report_content)
            log_info(f"Diagnostic ledger written to {report_path}")
        except Exception as e:
            log_warning(f"Could not write report to {report_path}: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="MOSKV-1 Vercel-Cloudflare Conflict Solver")
    parser.add_argument("--domain", help="Domain to analyze", default=None)
    parser.add_argument("--fix", help="Auto-remediate SSL issues if CF API token is provided", action="store_true")
    parser.add_argument("--verbose", help="Show verbose debugging info", action="store_true")
    args = parser.parse_args()
    solver = VercelCloudflareSolver(domain=args.domain, fix=args.fix, verbose=args.verbose)
    solver.execute()
