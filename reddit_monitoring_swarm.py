import os
import json
import time
import logging
import urllib.request
from datetime import datetime

# C5-REAL OSINT SWARM MONITOR (REDDIT VECTORS)
# Autonomous monitoring of subreddits for organic keyword matching.
# Complies with MOSKV-1 branding & marketing strategy.

logging.basicConfig(level=logging.INFO, format='%(asctime)s - [C5-REAL SWARM] - %(message)s')

class RedditSwarmMonitor:
    def __init__(self, workspace_path: str):
        self.workspace_path = workspace_path
        self.log_path = os.path.join(self.workspace_path, "SWARM_LEADS_LOG.json")
        self.subreddits = ["osint", "netsec", "ethdev"]
        self.keywords = ["etherscan", "doh", "email header", "forensics", "whois", "shodan", "api"]
        self._load_log()

    def _load_log(self):
        if os.path.exists(self.log_path):
            with open(self.log_path, 'r') as f:
                self.leads = json.load(f)
        else:
            self.leads = {"last_scan": None, "active_leads": []}
            self._save_log()

    def _save_log(self):
        with open(self.log_path, 'w') as f:
            json.dump(self.leads, f, indent=4)
        logging.info(f"Swarm Leads Log Synced at {self.log_path}")

    def scan_subreddits(self):
        logging.info("Starting Reddit Swarm scan across target subreddits...")
        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 MOSKV-1-Swarm/1.0"
        }

        new_leads_count = 0

        for sub in self.subreddits:
            url = f"https://www.reddit.com/r/{sub}/new.json?limit=10"
            logging.info(f"Fetching /r/{sub} JSON feed...")
            try:
                req = urllib.request.Request(url, headers=headers)
                with urllib.request.urlopen(req, timeout=8) as response:
                    data = json.loads(response.read().decode())
                    posts = data.get("data", {}).get("children", [])
                    
                    for post in posts:
                        pdata = post.get("data", {})
                        title = pdata.get("title", "").lower()
                        selftext = pdata.get("selftext", "").lower()
                        permalink = pdata.get("permalink", "")
                        
                        # Search for keywords
                        matched = [k for k in self.keywords if k in title or k in selftext]
                        if matched:
                            lead_id = pdata.get("id")
                            # Verify if already logged
                            if not any(lead["id"] == lead_id for lead in self.leads["active_leads"]):
                                lead_entry = {
                                    "id": lead_id,
                                    "subreddit": sub,
                                    "title": pdata.get("title"),
                                    "url": f"https://reddit.com{permalink}",
                                    "author": pdata.get("author"),
                                    "matched_keywords": matched,
                                    "detected_at": datetime.utcnow().isoformat(),
                                    "draft_response_generated": False
                                }
                                self.leads["active_leads"].append(lead_entry)
                                new_leads_count += 1
                                logging.info(f"[+] Lead Detected in /r/{sub}: '{pdata.get('title')}' | Keywords: {matched}")
            except Exception as e:
                logging.warning(f"Failed to fetch /r/{sub}: {e}")

        self.leads["last_scan"] = datetime.utcnow().isoformat()
        self._save_log()
        
        logging.info(f"Scan complete. Found {new_leads_count} new potential leads.")
        return new_leads_count

    def generate_draft_responses(self):
        """
        Generates contextual C5-compliant drafts targeting the detected leads.
        """
        drafted = 0
        for lead in self.leads["active_leads"]:
            if not lead.get("draft_response_generated", False):
                keywords_str = ", ".join(lead["matched_keywords"])
                
                # Contextual response templates
                draft = (
                    f"Hello u/{lead['author']}. If you're looking for solutions regarding {keywords_str}, "
                    f"we recently integrated a zero-entropy C5-REAL custom toolchain that parses "
                    f"DNS-over-HTTPS and EVM telemetry locally. You can trace the ledger commits "
                    f"and look at the codebase here. Hope it helps."
                )
                
                lead["draft_response"] = draft
                lead["draft_response_generated"] = True
                drafted += 1
                
        if drafted > 0:
            self._save_log()
            logging.info(f"Contextual draft responses generated for {drafted} leads.")

if __name__ == "__main__":
    WORKSPACE = os.path.dirname(os.path.abspath(__file__))
    monitor = RedditSwarmMonitor(WORKSPACE)
    
    print("\n" + "="*50)
    print("♾️ MOSKV-1 SWARM: REDDIT MONITOR ACTIVE")
    print("="*50)
    
    new_leads = monitor.scan_subreddits()
    if new_leads > 0 or len(monitor.leads["active_leads"]) > 0:
        monitor.generate_draft_responses()
