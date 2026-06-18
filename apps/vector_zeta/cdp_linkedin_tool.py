import os
import sys
import time
import json
import random
import traceback
from playwright.sync_api import sync_playwright

class CDPLinkedInTool:
    def __init__(self, port=9222, db_path=None):
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        self.port = port
        self.db_path = db_path or os.path.join(BASE_DIR, "leads_db.json")
        
        # Initialize leads ledger if not present
        if not os.path.exists(self.db_path):
            with open(self.db_path, 'w', encoding='utf-8') as f:
                json.dump({"metadata": {"last_extraction": None}, "leads": []}, f, indent=2)

    def load_leads(self):
        with open(self.db_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def save_leads(self, data):
        with open(self.db_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)

    def scrape_leads(self, target_icp, limit=10):
        print(f"[C5-REAL] Connecting to Brave via CDP on port {self.port} for scraping...")
        with sync_playwright() as p:
            try:
                browser = p.chromium.connect_over_cdp(f"http://127.0.0.1:{self.port}")
                context = browser.contexts[0]
                page = context.new_page()

                formatted_query = target_icp.replace(' ', '%20').replace('"', '%22')
                search_url = f"https://www.linkedin.com/search/results/people/?keywords={formatted_query}"
                
                page.goto(search_url, wait_until="domcontentloaded")
                try:
                    page.locator('li.reusable-search__result-container, .search-results-container li').first.wait_for(state="visible", timeout=12000)
                except Exception as te:
                    print(f"[*] Warning: Profiles locator timeout: {te}. Proceeding anyway...")
                time.sleep(2.0)

                # Simulated human scrolls
                page.mouse.wheel(0, 700)
                time.sleep(1.0)
                page.mouse.wheel(0, -300)
                time.sleep(1.0)

                containers = page.locator('a[tabindex="0"][href*="/in/"]').all()
                print(f"[*] Found {len(containers)} result containers on page.")
                
                extracted = []
                for container in containers[:limit]:
                    try:
                        text = container.inner_text().strip()
                        url = container.get_attribute('href').split('?')[0]
                        
                        lines = [line.strip() for line in text.split('\n') if line.strip()]
                        if len(lines) >= 2:
                            name = lines[0]
                            # Detect and strip connection level (e.g. 2º)
                            if any(term in lines[1] for term in ['1º', '2º', '3º', '•']):
                                role = lines[2] if len(lines) > 2 else ''
                            else:
                                role = lines[1]
                                
                            if name and url:
                                extracted.append({
                                    "name": name,
                                    "role": role,
                                    "url": url,
                                    "status": "RAW"
                                })
                                print(f"    [+] Extracted: {name} | {role}")
                    except Exception as e:
                        print(f"[-] Row parse error: {e}")
                        continue

                # Merge into JSON DB
                db = self.load_leads()
                existing_urls = {l['url'] for l in db.get('leads', []) if 'url' in l}
                new_count = 0
                for lead in extracted:
                    if lead['url'] not in existing_urls:
                        db['leads'].append(lead)
                        existing_urls.add(lead['url'])
                        new_count += 1

                db['metadata']['last_extraction'] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
                self.save_leads(db)
                print(f"[+] Scraping done. Added {new_count} new leads to {self.db_path}.")
                page.close()

            except Exception as e:
                print(f"[-] Scraping error: {e}")
                traceback.print_exc()

    def _handle_connect_modal(self, page, personalized_msg, lead):
        # Handle connect invitation modal
        add_note_btn = page.locator("button[aria-label*='Add a note'], button[aria-label*='nota'], button:has-text('Añadir una nota'), button:has-text('Add a note')").first
        if add_note_btn.is_visible():
            add_note_btn.click()
            time.sleep(1.0)
            
        textarea = page.locator("textarea[name='message'], textarea#custom-message").first
        if textarea.is_visible():
            textarea.fill(personalized_msg)
            time.sleep(1.5)

            send_btn = page.locator("button[aria-label*='Send'], button[aria-label*='Enviar'], button:has-text('Send'), button:has-text('Enviar')").first
            if send_btn.is_visible():
                send_btn.click(force=True)
                lead['status'] = 'INJECTED'
                print(f"[+] Injected connection invite note to {lead.get('name')}")
            else:
                print("[-] Send button not visible.")
                lead['status'] = 'ERROR'
        else:
            # If no note field, connect without note
            send_without_note = page.locator("button[aria-label*='Send without a note'], button[aria-label*='sin nota'], button:has-text('Send without a note'), button:has-text('Enviar sin nota')").first
            if send_without_note.is_visible():
                send_without_note.click()
                lead['status'] = 'INJECTED_NO_NOTE'
                print(f"[+] Sent connection request directly (no note) to {lead.get('name')}")
            else:
                lead['status'] = 'ERROR'

    def _handle_message_flow(self, page, personalized_msg, lead):
        chat_area = page.locator("div[contenteditable='true'], textarea[placeholder*='Write a message'], textarea[placeholder*='mensaje'], textarea[placeholder*='Mensaje']").first
        if chat_area.is_visible():
            chat_area.click()
            chat_area.fill(personalized_msg)
            time.sleep(1.5)

            send_btn = page.locator("button[type='submit'], button:has-text('Send'), button:has-text('Enviar')").first
            if send_btn.is_visible():
                send_btn.click(force=True)
            else:
                page.keyboard.press("Control+Enter")
            lead['status'] = 'MESSAGE_INJECTED'
            print(f"[+] Injected direct message to {lead.get('name')}")
        else:
            print("[-] Chat area not found.")
            lead['status'] = 'ERROR'

    def run_outreach(self, message_template, limit=5):
        print(f"[C5-REAL] Initiating Headless Outreach Injection...")
        db = self.load_leads()
        raw_leads = [l for l in db.get('leads', []) if l.get('status') == 'RAW'][:limit]
        
        if not raw_leads:
            print("[*] No RAW leads found for outreach.")
            return

        with sync_playwright() as p:
            try:
                print(f"[C5-REAL] Launching headless browser using extracted session cookies...")
                browser = p.chromium.launch(headless=True)
                context = browser.new_context()
                
                # Load cookies
                cookie_path = os.path.join(os.path.dirname(self.db_path), "linkedin_cookies.json")
                if os.path.exists(cookie_path):
                    with open(cookie_path, 'r') as f:
                        cookies = json.load(f)
                        context.add_cookies(cookies)
                else:
                    print("[-] Error: linkedin_cookies.json not found. Run cookie extraction script first.")
                    return

                for lead in raw_leads:
                    page = None
                    try:
                        page = context.new_page()
                        name = lead['name']
                        url = lead['url']
                        print(f"\n[>] Navigating to target: {name} | {url}")
                        page.goto(url, wait_until="domcontentloaded", timeout=30000)
                        time.sleep(2.0)

                        # Simulating scrolling to make connection buttons load
                        page.mouse.wheel(0, 500)
                        time.sleep(1.0)
                        page.mouse.wheel(0, -200)
                        time.sleep(1.0)

                        # Wait for top card button elements to render
                        try:
                            page.locator("main button:has-text('Connect'), main button:has-text('Conectar'), main button:has-text('Message'), main button:has-text('Mensaje'), main button:has-text('Enviar mensaje'), main button:has-text('Seguir'), main button:has-text('Follow'), main button:has-text('Más'), main button:has-text('More')").first.wait_for(state="visible", timeout=10000)
                        except Exception as e:
                            print(f"[*] Profile action buttons load timeout: {e}")

                        # Try to locate Connect or Message buttons directly under main to avoid chat overlay match
                        connect_button = page.locator("main button:has-text('Connect'), main button:has-text('Conectar'), main button[aria-label*='Connect'], main button[aria-label*='Conectar']").first
                        message_button = page.locator("main button:has-text('Message'), main button:has-text('Mensaje'), main button:has-text('Enviar mensaje'), main button[aria-label*='Message'], main button[aria-label*='Mensaje'], main button[aria-label*='Enviar mensaje']").first

                        # Personalize the note template
                        first_name = name.split()[0]
                        personalized_msg = message_template.replace("{{name}}", first_name)

                        if connect_button.is_visible():
                            print("[*] Connect button found directly under main. Clicking Connect...")
                            connect_button.click(force=True)
                            time.sleep(1.5)
                            self._handle_connect_modal(page, personalized_msg, lead)

                        elif message_button.is_visible():
                            print("[*] Message button found directly under main. Clicking Message...")
                            message_button.click(force=True)
                            time.sleep(2.0)
                            self._handle_message_flow(page, personalized_msg, lead)

                        else:
                            # Try to click More/Más button to find Connect/Conectar in dropdown
                            more_button = page.locator("main button:has-text('Más'), main button:has-text('More'), main button[aria-label*='Más'], main button[aria-label*='More']").first
                            if more_button.is_visible():
                                print("[*] Primary button is not Connect/Message (Creator Mode active). Clicking More...")
                                more_button.click(force=True)
                                time.sleep(1.5)
                                
                                # Look for Connect/Conectar or Message/Mensaje in the dropdown using class-agnostic visible filters
                                dropdown_connect = page.locator("span:has-text('Conectar'), span:has-text('Connect'), button:has-text('Conectar'), button:has-text('Connect')").filter(visible=True).first
                                dropdown_message = page.locator("span:has-text('Enviar mensaje'), span:has-text('Message'), button:has-text('Enviar mensaje'), button:has-text('Message')").filter(visible=True).first
                                
                                if dropdown_connect.is_visible():
                                    print("[*] Connect option found in dropdown. Clicking...")
                                    dropdown_connect.click(force=True)
                                    time.sleep(1.5)
                                    self._handle_connect_modal(page, personalized_msg, lead)
                                elif dropdown_message.is_visible():
                                    print("[*] Message option found in dropdown. Clicking...")
                                    dropdown_message.click(force=True)
                                    time.sleep(2.0)
                                    self._handle_message_flow(page, personalized_msg, lead)
                                else:
                                    print("[-] Connect/Message options not found in More dropdown.")
                                    lead['status'] = 'UNAVAILABLE'
                            else:
                                print("[-] Connect/Message/More buttons not available for this profile.")
                                lead['status'] = 'UNAVAILABLE'

                        self.save_leads(db)
                        
                        # Cool-down to prevent rate limiting
                        cooldown = random.uniform(10.0, 20.0)
                        print(f"[*] Cooldown of {cooldown:.2f}s active...")
                        time.sleep(cooldown)

                    except Exception as e_inner:
                        print(f"[-] Error processing lead {lead.get('name')}: {e_inner}")
                        traceback.print_exc()
                        lead['status'] = 'ERROR'
                        self.save_leads(db)
                        time.sleep(5.0)
                    finally:
                        if page:
                            try:
                                page.close()
                            except Exception:
                                pass

                print("\n[+] Outreach campaign sequence complete.")

            except Exception as e:
                print(f"[-] Outreach error: {e}")
                traceback.print_exc()

if __name__ == "__main__":
    tool = CDPLinkedInTool()
    # Simple CLI dispatch
    if len(sys.argv) > 1 and sys.argv[1] == "scrape":
        query = sys.argv[2] if len(sys.argv) > 2 else "CTO OR VP Engineering OR Head of AI"
        tool.scrape_leads(query)
    elif len(sys.argv) > 1 and sys.argv[1] == "outreach":
        msg = "Hi {{name}}, let's transition your infrastructure to C5-REAL with MOSKV-1 APEX."
        tool.run_outreach(msg)
    else:
        print("Usage: python3 cdp_linkedin_tool.py [scrape|outreach] [query]")
