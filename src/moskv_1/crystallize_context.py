#!/usr/bin/env python3
"""
MOSKV-1 APEX: Dynamic Context Crystallization Engine
C5-REAL: Compresses conversational logs and persists critical directives into .cursorrules.
"""

import os
import json
import re
import glob
from pathlib import Path
from typing import List, Set

def find_latest_transcript() -> str:
    brain_dir = os.path.expanduser("~/.gemini/antigravity/brain/*/.system_generated/logs/transcript.jsonl")
    transcripts = glob.glob(brain_dir)
    if not transcripts:
        return ""
    # Return the one with the latest modification time
    transcripts.sort(key=os.path.getmtime, reverse=True)
    return transcripts[0]

def extract_directives_from_file(transcript_path: str) -> List[str]:
    if not transcript_path or not os.path.exists(transcript_path):
        return []
        
    directives: List[str] = []
    seen: Set[str] = set()
    
    with open(transcript_path, 'r', encoding='utf-8') as f:
        for line in f:
            if not line.strip():
                continue
            try:
                step = json.loads(line)
                content = step.get("content", "")
                thinking = step.get("thinking", "")
                
                # Scan both user/model content and model thinking
                for text in (content, thinking):
                    if not text:
                        continue
                    # Match pattern like: [P0] Do X, Rule: Do Y, Directive: Do Z, MUST Do W, NEVER Do V
                    matches = re.findall(r'(?:\[P[0-2]\]|Rule:|Directive:|MUST|NEVER)\s*([^\n\.\#\*]+)', text)
                    for match in matches:
                        cleaned = match.strip()
                        # Clean markdown wrappers or trailing spaces
                        cleaned = re.sub(r'[\`\"\'\*]', '', cleaned)
                        if len(cleaned) > 10 and cleaned not in seen:
                            seen.add(cleaned)
                            directives.append(cleaned)
            except json.JSONDecodeError:
                continue
                
    return directives

def update_cursorrules(directives: List[str]) -> bool:
    cursorrules_path = Path(".cursorrules")
    if not cursorrules_path.exists():
        return False
        
    with open(cursorrules_path, "r", encoding="utf-8") as f:
        content = f.read()
        
    # Split content before the crystallized directives section
    marker = "## 5. DYNAMICALLY CRYSTALLIZED DIRECTIVES"
    if marker in content:
        parts = content.split(marker)
        base_content = parts[0].strip()
    else:
        base_content = content.strip()
        
    if not directives:
        new_content = base_content + "\n"
    else:
        new_content = base_content + f"\n\n{marker} (Exergy Maximized)\n"
        for d in directives:
            new_content += f"- **Enforced**: {d}\n"
            
    with open(cursorrules_path, "w", encoding="utf-8") as f:
        f.write(new_content)
        
    return True

def main() -> int:
    transcript_path = find_latest_transcript()
    if not transcript_path:
        print("[ContextCrystallizer] Error: No transcript found.")
        return 1
        
    print(f"[ContextCrystallizer] Reading latest transcript: {transcript_path}")
    directives = extract_directives_from_file(transcript_path)
    print(f"[ContextCrystallizer] Extracted {len(directives)} directives.")
    
    if update_cursorrules(directives):
        print("[ContextCrystallizer] Successfully updated .cursorrules with active session directives.")
        return 0
    else:
        print("[ContextCrystallizer] Error: .cursorrules file not found in workspace.")
        return 1

if __name__ == "__main__":
    exit(main())
