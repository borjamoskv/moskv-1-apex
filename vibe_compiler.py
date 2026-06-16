#!/usr/bin/env python3
# MOSKV-1 APEX - C5-REAL VIBE-CODE COMPILER V3 (Data-Driven ZSH Hook)

import sys
import re
import os
import subprocess
import yaml

def execute(command, notification):
    print(f"[EXEC] {command}")
    os.system(f"osascript -e 'display notification \"{notification}\" with title \"VIBE COMPILER V3\"'")
    subprocess.run(command, shell=True)

def load_dict():
    dict_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "vibe_dict.yaml")
    try:
        with open(dict_path, 'r') as f:
            return yaml.safe_load(f).get('vibes', [])
    except Exception as e:
        print(f"Error loading vibe_dict.yaml: {e}")
        sys.exit(1)

def parse_vibe(vibe_string):
    vibe_string = vibe_string.lower().strip()
    vibes = load_dict()
    
    for vibe in vibes:
        if vibe.get("regex"):
            for pattern in vibe["patterns"]:
                regex_pattern = pattern.replace("{port}", r"(\d+)")
                match = re.search(regex_pattern, vibe_string)
                if match:
                    port = match.group(1)
                    cmd = vibe["command"].replace("{port}", port)
                    notif = vibe["notification"].replace("{port}", port)
                    execute(cmd, notif)
                    return True
        else:
            for pattern in vibe["patterns"]:
                if pattern in vibe_string:
                    execute(vibe["command"], vibe["notification"])
                    return True
    return False

if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit(1)
    
    # Optional PyYAML install fallback
    try:
        import yaml
    except ImportError:
        os.system("pip3 install pyyaml >/dev/null 2>&1")
        import yaml
        
    found = parse_vibe(sys.argv[1])
    if not found:
        # Silently fail if not found, allowing zsh to handle normal unknown commands
        sys.exit(127)
