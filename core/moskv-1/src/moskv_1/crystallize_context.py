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
                    # Match patterns like: [P0] Do X, Rule: Do Y, Directive: Do Z, Axiom: Do W, MUST Do V, NEVER Do U
                    matches = re.findall(r'(?:\[P[0-2]\]|Rule:|Directive:|Axiom:|Enforce:|Constraint:|Policy:|MUST|NEVER)\s*([^\n\.\#\*]+)', text)
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

def prune_and_deduplicate_directives(directives: List[str], max_limit: int = 10) -> List[str]:
    """
    Applies thermodynamic compression to session directives.
    Deduplicates based on word overlap similarity, filters out noise,
    and caps the list to the latest max_limit directives to keep context exergy high.
    """
    cleaned: List[str] = []
    
    for d in reversed(directives):
        d_clean = d.strip()
        if len(d_clean) < 15 or len(d_clean) > 150:
            continue
        if "|" in d_clean or "\\s" in d_clean or "Rule:" in d_clean:
            continue
            
        is_duplicate = False
        words_new = set(d_clean.lower().split())
        for existing in cleaned:
            words_exist = set(existing.lower().split())
            if not words_new or not words_exist:
                continue
            overlap = len(words_new.intersection(words_exist)) / max(len(words_new), len(words_exist))
            if overlap > 0.60:
                is_duplicate = True
                break
                
        if not is_duplicate:
            cleaned.append(d_clean)
            
    cleaned.reverse()
    return cleaned[-max_limit:]

def update_cursorrules(directives: List[str]) -> bool:
    cursorrules_path = Path(".cursorrules")
    if not cursorrules_path.exists():
        return False
        
    with open(cursorrules_path, "r", encoding="utf-8") as f:
        content = f.read()
        
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
    import sys
    if len(sys.argv) > 1:
        target = sys.argv[1]
        if os.path.exists(target):
            transcript_path = target
        else:
            potential_path = os.path.expanduser(f"~/.gemini/antigravity/brain/{target}/.system_generated/logs/transcript.jsonl")
            if os.path.exists(potential_path):
                transcript_path = potential_path
            else:
                print(f"[ContextCrystallizer] Target path or conversation ID not found: {target}")
                return 1
    else:
        transcript_path = find_latest_transcript()
        
    if not transcript_path:
        print("[ContextCrystallizer] Error: No transcript found.")
        return 1
        
    print(f"[ContextCrystallizer] Reading transcript: {transcript_path}")
    directives = extract_directives_from_file(transcript_path)
    directives = prune_and_deduplicate_directives(directives)
    print(f"[ContextCrystallizer] Extracted & synthesized {len(directives)} directives.")
    
    if update_cursorrules(directives):
        print("[ContextCrystallizer] Successfully updated .cursorrules with active session directives.")
        return 0
    else:
        print("[ContextCrystallizer] Error: .cursorrules file not found in workspace.")
        return 1

if __name__ == "__main__":
    exit(main())
