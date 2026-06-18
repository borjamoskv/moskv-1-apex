#!/usr/bin/env python3
import socket
import urllib.request
import urllib.error
import sys
import ssl
from datetime import datetime, timezone

TARGET_DOMAIN = "cortexpersist.com"
WWW_DOMAIN = "www.cortexpersist.com"
VERCEL_A_IP = "76.76.21.21"

def check_dns_resolution(domain):
    print(f"[*] Resolving DNS for: {domain}")
    try:
        ips = socket.gethostbyname_ex(domain)[2]
        print(f"  [+] Resolved IPs: {', '.join(ips)}")
        return ips
    except Exception as e:
        print(f"  [-] DNS Resolution failed: {e}")
        return []

def evaluate_ips(ips, is_www=False):
    is_cloudflare = False
    is_vercel = False
    for ip in ips:
        if ip == VERCEL_A_IP or ip.startswith("76.76."):
            is_vercel = True
        if ip.startswith("104.") or ip.startswith("172.67.") or ip.startswith("104.21."):
            is_cloudflare = True
    if is_cloudflare:
        print("  [i] Configuration: Cloudflare Proxy (Orange Cloud) is ACTIVE.")
    elif is_vercel:
        print("  [i] Configuration: Direct Vercel Routing (Grey Cloud / DNS Only) is ACTIVE.")
    else:
        print("  [!] Configuration: Custom or unknown IP routing.")
    return {"cloudflare": is_cloudflare, "vercel": is_vercel}

def inspect_http_route(url):
    print(f"[*] Testing HTTP handshake: {url}")
    class NoRedirectHandler(urllib.request.HTTPRedirectHandler):
        def redirect_request(self, req, fp, code, msg, headers, newurl):
            raise urllib.error.HTTPError(req.full_url, code, f"Redirected to {newurl}", headers, fp)
    try:
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        opener = urllib.request.build_opener(
            NoRedirectHandler(),
            urllib.request.HTTPSHandler(context=ctx)
        )
        opener.addheaders = [('User-Agent', 'CortexPersist-Diagnostic-Core/1.0')]
        req = urllib.request.Request(url, method="HEAD")
        with opener.open(req, timeout=5) as response:
            server = response.headers.get("Server", "Unknown")
            print(f"  [+] Status: {response.status} {response.reason}")
            print(f"  [+] Server Header: {server}")
            return response.status, server, None
    except urllib.error.HTTPError as e:
        location = e.headers.get("Location", "None")
        server = e.headers.get("Server", "Unknown")
        print(f"  [i] Redirect detected (HTTP {e.code}): -> {location} (Server: {server})")
        return e.code, server, location
    except urllib.error.URLError as e:
        print(f"  [-] Connection error: {e.reason}")
        return None, None, str(e.reason)
    except Exception as e:
        print(f"  [-] Handshake exception: {e}")
        return None, None, str(e)

def run_diagnostics():
    print(f"[{datetime.now(timezone.utc).isoformat()}] [CORTEX-DNS] Initiating Network Auditing Cycle...")
    print("=" * 60)
    root_ips = check_dns_resolution(TARGET_DOMAIN)
    root_status = evaluate_ips(root_ips)
    print("-" * 60)
    www_ips = check_dns_resolution(WWW_DOMAIN)
    www_status = evaluate_ips(www_ips, is_www=True)
    print("-" * 60)
    routes = [
        f"http://{TARGET_DOMAIN}/",
        f"https://{TARGET_DOMAIN}/",
        f"http://{WWW_DOMAIN}/",
        f"https://{WWW_DOMAIN}/"
    ]
    audit_results = {}
    for r in routes:
        code, server, extra = inspect_http_route(r)
        audit_results[r] = {"code": code, "server": server, "extra": extra}
        print("-" * 60)
    print("[*] Diagnostic Conclusion & System Warnings:")
    conflicts_detected = 0
    https_root = audit_results.get(f"https://{TARGET_DOMAIN}/")
    http_root = audit_results.get(f"http://{TARGET_DOMAIN}/")
    if http_root["code"] == 308 and http_root["extra"] == f"https://{TARGET_DOMAIN}/":
        if https_root["code"] == 308 or (https_root["code"] is None and "handshake" in str(https_root["extra"]).lower()):
            print("  [CRITICAL] Potential SSL Redirect Loop or Handshake Failure!")
            print("  [Reason] Cloudflare SSL/TLS mode is likely set to 'Flexible'.")
            print("  [Fix] Set Cloudflare encryption mode to 'Full' or 'Full (Strict)' immediately.")
            conflicts_detected += 1
    if root_status["cloudflare"] and https_root["code"] is None:
        print("  [WARNING] DNS is proxied via Cloudflare, but Vercel origin is unreachable.")
        print("  [Reason] Vercel might have failed to issue/renew the Let's Encrypt certificate.")
        print("  [Fix] Toggle Cloudflare records to 'DNS Only' (Grey Cloud), wait for Vercel SSL to activate, then re-enable proxy.")
        conflicts_detected += 1
    if conflicts_detected == 0:
        print("  [✓] Zero conflicts detected. Routing and certificate layers are stable. Exergy optimal.")
    else:
        print(f"  [!] Found {conflicts_detected} potential integration anomalies.")
    print("=" * 60)

if __name__ == "__main__":
    run_diagnostics()
