import os
import sys
import json
import time
import random
import traceback
from playwright.sync_api import sync_playwright

class CDPPurgeTool:
    def __init__(self, port=9222, blacklist_path=None, screenshot_dir=None):
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        self.port = port
        self.blacklist_path = blacklist_path or os.path.join(BASE_DIR, "spam_blacklist.json")
        self.screenshot_dir = screenshot_dir or os.path.join(BASE_DIR, ".sessions", "failures")
        os.makedirs(self.screenshot_dir, exist_ok=True)

    def load_targets(self):
        if not os.path.exists(self.blacklist_path):
            print(f"[-] Ledger not found at {self.blacklist_path}")
            return []
        with open(self.blacklist_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return [t for t in data.get('spam_traps', []) if t.get('status') == 'PURGE_REQUIRED']

    def update_status(self, email, status, message=""):
        if not os.path.exists(self.blacklist_path):
            return
        with open(self.blacklist_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        for t in data.get('spam_traps', []):
            if t.get('email', '').strip().lower() == email.strip().lower():
                t['status'] = status
                t['message'] = message
                t['updated_at'] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        with open(self.blacklist_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)

    def execute(self):
        targets = self.load_targets()
        if not targets:
            print("[+] No targets with status 'PURGE_REQUIRED' found in ledger.")
            return

        print(f"[C5-REAL] Starting CDP Purge Tool for {len(targets)} targets...")
        
        with sync_playwright() as p:
            try:
                print(f"[*] Connecting to browser via CDP on port {self.port}...")
                browser = p.chromium.connect_over_cdp(f"http://127.0.0.1:{self.port}")
                contexts = browser.contexts
                if not contexts:
                    print("[-] No active browser contexts found.")
                    return
                context = contexts[0]
                
                # Try to find an existing subscribers page or open a new one
                page = None
                for pg in context.pages:
                    if "publish/subscribers" in pg.url:
                        page = pg
                        break
                
                if not page:
                    print("[*] Subscribers tab not found. Creating a new one...")
                    page = context.new_page()
                    page.goto("https://borjamoskv.substack.com/publish/subscribers", wait_until="networkidle")
                    time.sleep(4.0)
                
                page.bring_to_front()
                
                def dismiss_popups():
                    try:
                        page.keyboard.press("Escape")
                        time.sleep(0.5)
                        page.keyboard.press("Escape")
                        time.sleep(0.5)
                    except:
                        pass

                for t in targets:
                    email = t['email']
                    print(f"\n[>] Eradicating node: {email}")
                    
                    try:
                        # Clear search input
                        search_input = page.locator("input[placeholder*='Buscar'], input[placeholder*='buscar'], input[placeholder*='Search'], input[placeholder*='search']").first
                        search_input.fill("")
                        time.sleep(1.0)
                        
                        # Set React value
                        react_setter_js = """
                        (el, val) => {
                            const nativeInputValueSetter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, "value").set;
                            nativeInputValueSetter.call(el, val);
                            el.dispatchEvent(new Event('input', { bubbles: true }));
                        }
                        """
                        search_input.evaluate(react_setter_js, email)
                        print(f"[*] Search input populated with: {email}")
                        
                        # Wait for results
                        time.sleep(3.5)
                        row_visible = page.locator(f"tr:has-text('{email}')").first.is_visible()
                        no_results_visible = page.locator(":has-text('No se encontraron resultados'), :has-text('No results found'), :has-text('0 resultados')").first.is_visible()
                        
                        if no_results_visible and not row_visible:
                            print(f"[+] NOT FOUND (Already deleted): {email}")
                            self.update_status(email, "PURGED", "Already deleted")
                            continue
                            
                        if not row_visible:
                            raise Exception("Target row not visible after search")
                            
                        target_row = page.locator(f"tr:has-text('{email}')").first
                        ellipsis = target_row.locator("button[aria-label='Ellipsis']").first
                        ellipsis.click(force=True)
                        time.sleep(1.0)
                        
                        remove_btn = page.locator("[role='menuitem']:has-text('Quitar de la lista'), [role='menuitem']:has-text('Remove from list')").first
                        remove_btn.wait_for(state="visible", timeout=6000)
                        remove_btn.click(force=True)
                        time.sleep(1.0)
                        
                        dialog = page.locator("[role='dialog']:has-text('Eliminar'), [role='dialog']:has-text('Remove'), [role='dialog']:has-text('Delete'), [role='alertdialog']").first
                        dialog.wait_for(state="visible", timeout=5000)
                        dialog_text = dialog.inner_text()
                        
                        if email.lower() in dialog_text.lower():
                            confirm_btn = dialog.locator("button:has-text('Eliminar'), button:has-text('Eliminar y reembolsar'), button:has-text('Remove'), button:has-text('Delete')").first
                            confirm_btn.click(force=True)
                            confirm_btn.wait_for(state="detached", timeout=5000)
                            
                            print(f"[+] Eradication success: {email}")
                            self.update_status(email, "PURGED")
                        else:
                            raise Exception(f"Email mismatch in confirmation dialog: '{dialog_text}'")
                            
                    except Exception as e:
                        print(f"[-] ERROR processing {email}: {e}")
                        traceback.print_exc()
                        
                        safe_email = email.replace('@', '_').replace('.', '_')
                        screenshot_path = os.path.join(self.screenshot_dir, f"fail_{safe_email}.png")
                        try:
                            page.screenshot(path=screenshot_path)
                            print(f"[*] Saved error screenshot to: {screenshot_path}")
                        except Exception as se:
                            print(f"[!] Warning: Could not save screenshot: {se}")
                            
                        self.update_status(email, "FAILED", str(e).replace('\n', ' '))
                        dismiss_popups()
                        
                    time.sleep(random.uniform(2.5, 4.0)) # Jitter
                    
                print("\n[+] Purge tool execution complete.")
                
            except Exception as e:
                print(f"[-] Global CDP Error: {e}")
                traceback.print_exc()

if __name__ == "__main__":
    tool = CDPPurgeTool()
    tool.execute()
