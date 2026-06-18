import os
import yaml
from cdp_linkedin_tool import CDPLinkedInTool

def run():
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    campaign_file = os.path.join(BASE_DIR, "campaign_001.yaml")
    
    if not os.path.exists(campaign_file):
        print(f"[-] Campaign file not found at {campaign_file}")
        return
        
    with open(campaign_file, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
        
    vectors = config['Campaign']['Vectors']
    message = ""
    for vector in vectors:
        if vector['Platform'].lower() == 'linkedin':
            message = vector['Message'].strip()
            break
            
    if not message:
        print("[-] LinkedIn message template not found in campaign file.")
        return
        
    print(f"[C5-REAL] Loading campaign template:\n\"\"\"\n{message}\n\"\"\"")
    
    tool = CDPLinkedInTool()
    tool.run_outreach(message, limit=10)

if __name__ == "__main__":
    run()
