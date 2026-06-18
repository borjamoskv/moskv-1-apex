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

                profiles = page.locator('li.reusable-search__result-container, .search-results-container li').all()
                print(f"[*] Found {len(profiles)} result elements on page.")
                
                extracted = []
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
                            extracted.append({
                                "name": name,
                                "role": role,
                                "url": url,
                                "status": "RAW"
                            })
                            print(f"    [+] Extracted: {name} | {role}")
                    except Exception:
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

    def run_outreach(self, message_template, limit=5):
        print(f"[C5-REAL] Connecting to Brave via CDP on port {self.port} for outreach injection...")
        db = self.load_leads()
        raw_leads = [l for l in db.get('leads', []) if l.get('status') == 'RAW'][:limit]
        
        if not raw_leads:
            print("[*] No RAW leads found for outreach.")
            return

        with sync_playwright() as p:
            try:
                browser = p.chromium.connect_over_cdp(f"http://127.0.0.1:{self.port}")
                context = browser.contexts[0]
                page = context.new_page()

                for lead in raw_leads:
                    name = lead['name']
                    url = lead['url']
                    print(f"\n[>] Navigating to target: {name} | {url}")
                    page.goto(url, wait_until="networkidle")
                    time.sleep(3.0)

                    # Simulating scrolling to make connection buttons load
                    page.mouse.wheel(0, 500)
                    time.sleep(1.0)
                    page.mouse.wheel(0, -200)
                    time.sleep(1.0)

                    # Try to locate Connect or Message buttons
                    connect_button = page.locator("button.pvs-profile-actions__action:has-text('Connect'), button[aria-label*='Connect']").first
                    message_button = page.locator("button.pvs-profile-actions__action:has-text('Message'), button[aria-label*='Message']").first

                    # Personalize the note template
                    first_name = name.split()[0]
                    personalized_msg = message_template.replace("{{name}}", first_name)

                    if connect_button.is_visible():
                        print("[*] Connect button found. Clicking Connect...")
                        connect_button.click(force=True)
                        time.sleep(1.5)

                        add_note_btn = page.locator("button[aria-label*='Add a note']").first
                        if add_note_btn.is_visible():
                            add_note_btn.click()
                            time.sleep(1.0)
                            
                        textarea = page.locator("textarea[name='message'], textarea#custom-message").first
                        if textarea.is_visible():
                            textarea.fill(personalized_msg)
                            time.sleep(1.5)

                            send_btn = page.locator("button[aria-label*='Send'], button:has-text('Send')").first
                            if send_btn.is_visible():
                                send_btn.click(force=True)
                                lead['status'] = 'INJECTED'
                                print(f"[+] Injected connection invite note to {name}")
                            else:
                                print("[-] Send button not visible.")
                                lead['status'] = 'ERROR'
                        else:
                            # If no note field, connect without note
                            send_without_note = page.locator("button[aria-label*='Send without a note']").first
                            if send_without_note.is_visible():
                                send_without_note.click()
                                lead['status'] = 'INJECTED_NO_NOTE'
                                print(f"[+] Sent connection request directly (no note) to {name}")
                            else:
                                lead['status'] = 'ERROR'

                    elif message_button.is_visible():
                        print("[*] Message button found. Clicking Message...")
                        message_button.click(force=True)
                        time.sleep(2.0)

                        chat_area = page.locator("div[contenteditable='true'], textarea[placeholder*='Write a message']").first
                        if chat_area.is_visible():
                            chat_area.click()
                            chat_area.fill(personalized_msg)
                            time.sleep(1.5)

                            send_btn = page.locator("button[type='submit'], button:has-text('Send')").first
                            if send_btn.is_visible():
                                send_btn.click(force=True)
                            else:
                                page.keyboard.press("Control+Enter")
                            lead['status'] = 'MESSAGE_INJECTED'
                            print(f"[+] Injected direct message to {name}")
                        else:
                            print("[-] Chat area not found.")
                            lead['status'] = 'ERROR'
                    else:
                        print("[-] Connect/Message buttons not available for this profile.")
                        lead['status'] = 'UNAVAILABLE'

                    self.save_leads(db)
                    
                    # Cool-down to prevent rate limiting
                    cooldown = random.uniform(10.0, 20.0)
                    print(f"[*] Cooldown of {cooldown:.2f}s active...")
                    time.sleep(cooldown)

                page.close()
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
