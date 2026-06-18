import os
import csv
import json
import time
import argparse

def add_targets(csv_path, blacklist_path, min_received=10, max_open_rate=0.10, exclude_emails=None):
    if exclude_emails is None:
        exclude_emails = []
    
    exclude_set = {email.strip().lower() for email in exclude_emails}
    
    if not os.path.exists(csv_path):
        print(f"[-] CSV file not found at {csv_path}")
        return
        
    if not os.path.exists(blacklist_path):
        print(f"[-] Blacklist JSON not found at {blacklist_path}")
        return

    with open(blacklist_path, 'r', encoding='utf-8') as f:
        blacklist_data = json.load(f)

    existing_emails = {t.get('email', '').strip().lower() for t in blacklist_data.get('spam_traps', [])}

    added_count = 0
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            email = row.get('Email', '').strip().lower()
            if not email:
                continue
            if email in existing_emails or email in exclude_set:
                continue
                
            name = row.get('Name', '').strip()
            opened_6mo = int(row.get('Emails opened (6mo)', '0') or '0')
            received_6mo = int(row.get('Emails received (6mo)', '0') or '0')
            
            if received_6mo >= min_received:
                open_rate = opened_6mo / received_6mo
                if open_rate < max_open_rate:
                    new_target = {
                        "email": email,
                        "alias": name or email.split('@')[0],
                        "detected_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                        "platform": "Substack",
                        "behavior": f"Low engagement (open rate {open_rate:.2%}, received {received_6mo})",
                        "status": "PURGE_REQUIRED"
                    }
                    blacklist_data.setdefault('spam_traps', []).append(new_target)
                    existing_emails.add(email)
                    added_count += 1
                    print(f"[+] Added to purge list: {email} ({open_rate:.2%})")

    if added_count > 0:
        with open(blacklist_path, 'w', encoding='utf-8') as f:
            json.dump(blacklist_data, f, indent=2)
        print(f"\n[+] Successfully added {added_count} new targets to {blacklist_path}")
    else:
        print("\n[*] No new low engagement targets added.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Ingest low engagement subscribers to purge list")
    parser.add_argument("--csv", default="/Users/borjafernandezangulo/Documents/Archivos_Muertos/2026-06/subscriber-export-2026-05-29-00-39-30.csv", help="Path to Substack subscriber export CSV")
    parser.add_argument("--blacklist", default=os.path.join(os.path.dirname(os.path.abspath(__file__)), "spam_blacklist.json"), help="Path to spam_blacklist.json")
    parser.add_argument("--min-received", type=int, default=10, help="Minimum emails received to evaluate")
    parser.add_argument("--max-rate", type=float, default=0.10, help="Maximum open rate to qualify (default 0.10)")
    args = parser.parse_args()

    # Exclude high-profile key contacts by default to avoid accidental deletion
    exclusions = [
        "naval@angel.co",
        "tobi@shopify.com",
        "chamath@socialcapital.com",
        "illia@near.org",
        "jeff@google.com",
        "shane@openai.com"
    ]
    
    add_targets(args.csv, args.blacklist, min_received=args.min_received, max_open_rate=args.max_rate, exclude_emails=exclusions)
