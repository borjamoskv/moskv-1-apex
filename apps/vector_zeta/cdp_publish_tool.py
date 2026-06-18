import os
import sys
import time
from playwright.sync_api import sync_playwright

def publish_manifesto(content_path, port=9222):
    if not os.path.exists(content_path):
        print(f"[-] Content file not found at {content_path}")
        return

    with open(content_path, 'r', encoding='utf-8') as f:
        content = f.read()

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

    print(f"[C5-REAL] Initializing publishing sequence for: {title}")
    
    with sync_playwright() as p:
        try:
            print(f"[*] Connecting to browser via CDP on port {port}...")
            browser = p.chromium.connect_over_cdp(f"http://127.0.0.1:{port}")
            contexts = browser.contexts
            if not contexts:
                print("[-] No active browser contexts found.")
                return
            context = contexts[0]

            print("[*] Opening Substack editor tab...")
            page = context.new_page()
            page.goto("https://borjamoskv.substack.com/publish/post", wait_until="networkidle")
            time.sleep(4.0)

            page.bring_to_front()

            # Locate title input (post-title ID is language-independent)
            print("[*] Locating editor fields...")
            title_field = page.locator("textarea#post-title").first
            title_field.wait_for(state="visible", timeout=12000)
            
            # Fill title
            title_field.click()
            title_field.fill(title)
            print("[+] Title injected.")
            time.sleep(1.5)

            # Locate body editor (ProseMirror contenteditable)
            body_field = page.locator("div[contenteditable='true'], .ProseMirror").first
            body_field.wait_for(state="visible", timeout=12000)
            
            # Focus and insert body
            body_field.click()
            page.keyboard.insert_text(body)
            print("[+] Body injected successfully.")
            time.sleep(3.0)

            print("\n==================================================")
            print("[C5-REAL] DRAFT INJECTED SUCCESSFULLY")
            print("==================================================")
            print("El borrador del manifiesto ha sido cargado en tu ventana activa de Brave.")
            print("Revisa el formato y haz clic en 'Publish' en tu navegador para realizar el envío.")
            print("==================================================\n")

        except Exception as e:
            print(f"[-] Error during injection: {e}")

if __name__ == "__main__":
    payload_path = "/Users/borjafernandezangulo/.gemini/antigravity/brain/026e1e62-f357-4efc-aab8-0466fa63264d/moskv1_marketing_manifesto.md"
    if len(sys.argv) > 1:
        payload_path = sys.argv[1]
    publish_manifesto(payload_path)
