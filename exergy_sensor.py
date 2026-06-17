#!/usr/bin/env python3
import json
import sys
import os
import glob
import re
from pathlib import Path

def get_historical_anergy_threshold() -> float:
    """
    Computes dynamic historical threshold based on past transcripts to enforce continuous improvement.
    Fallback to 1000 if no data is found.
    """
    brains_path = os.path.expanduser("~/.gemini/antigravity/brain/*/.system_generated/logs/transcript.jsonl")
    transcripts = glob.glob(brains_path)
    if not transcripts:
        return 1000.0
        
    # As a baseline for C5-REAL, we force a continuous 5% optimization pressure 
    # over the static baseline if transcripts exist. A full I/O scan here is heavy, 
    # so we mock the regression calculation based on the count of past sessions.
    baseline = 1000.0
    optimization_pressure = min(0.50, len(transcripts) * 0.01) # Max 50% tighter
    return baseline * (1.0 - optimization_pressure)


def calculate_exergy(transcript_path: str):
    """
    Thermodynamic Context Parser for MOSKV-1 APEX
    Calculates the generation of entropy (anergy) vs useful structural mutations.
    """
    if not os.path.exists(transcript_path):
        print(f"Error: Transcript not found at {transcript_path}")
        sys.exit(1)

    total_steps = 0
    user_inputs = 0
    model_responses = 0
    tool_calls = 0.0
    total_content_length = 0
    signal_chars = 0
    
    with open(transcript_path, 'r', encoding='utf-8') as f:
        for line in f:
            if not line.strip():
                continue
            try:
                step = json.loads(line)
                total_steps += 1
                step_type = step.get("type", "")
                content = step.get("content", "") or ""
                
                if step_type == "USER_INPUT":
                    user_inputs += 1
                elif step_type in ("PLANNER_RESPONSE", "MODEL_RESPONSE"):
                    model_responses += 1
                    total_content_length += len(content)
                    
                    # Extract markdown code blocks as structured signal
                    code_blocks = re.findall(r'```(?:[a-zA-Z0-9_+-]+)?\n(.*?)\n```', content, re.DOTALL)
                    signal_chars += sum(len(block) for block in code_blocks)
                    
                    # Extract inline code backticks as minor signal
                    inline_code = re.findall(r'`[^`\n]+`', content)
                    signal_chars += sum(len(inline) for inline in inline_code)
                    
                    if step.get("tool_calls"):
                        for tc in step.get("tool_calls"):
                            name = tc.get("name", "")
                            if name in ("replace_file_content", "multi_replace_file_content", "write_to_file"):
                                tool_calls += 3.0
                            elif name in ("run_command",):
                                tool_calls += 2.0
                            elif name in ("view_file", "list_dir", "grep_search", "read_url_content", "read_browser_page"):
                                tool_calls += 0.5
                            else:
                                tool_calls += 1.0
            except json.JSONDecodeError:
                continue
                
    # Anergy is defined strictly as the narrative fluff (non-code / unstructured characters)
    narrative_chars = max(0, total_content_length - signal_chars)
    anergy_ratio = narrative_chars / (tool_calls if tool_calls > 0.0 else 1.0)
    
    dynamic_threshold = get_historical_anergy_threshold()
    
    print("=== MOSKV-1 EXERGY SENSOR ===")
    print(f"Transcript Path: {transcript_path}")
    print(f"Total Steps: {total_steps}")
    print(f"User Inputs: {user_inputs}")
    print(f"Model Responses: {model_responses}")
    print(f"Tool Executions (Mutations): {tool_calls}")
    print(f"Total Cognitive Volume (Chars): {total_content_length}")
    print(f"Structured Signal (Chars): {signal_chars}")
    print(f"Narrative Anergy (Chars): {narrative_chars}")
    print("-----------------------------")
    print(f"Thermodynamic Friction (Anergy Ratio): {anergy_ratio:.2f} chars/tool")
    print(f"Dynamic Threshold (Continuous Optimization): {dynamic_threshold:.2f}")
    
    if anergy_ratio > dynamic_threshold:
        print(f"[!] ALERTA: Baja Exergía. Demasiada prosa por cada mutación estructural (Umbral: {dynamic_threshold:.2f}).")
    else:
        print("[✓] ESTADO: Alta Densidad Exergética. Operación Turbo.")


def ingest_mac_maestro_ndjson(log_path: str):
    """
    Ingests structural logs from Mac-Maestro physical UI mutations.
    """
    if not os.path.exists(log_path):
        return 0
    mutations = 0
    with open(log_path, 'r', encoding='utf-8') as f:
        for line in f:
            if not line.strip():
                continue
            try:
                event = json.loads(line)
                if event.get("action") == "mutation":
                    mutations += 1
            except json.JSONDecodeError:
                pass
    return mutations

def calculate_workspace_exergy(root_dir: str):
    """
    Scans the local filesystem workspace and calculates Code Density as a measure of structural Exergy.
    Excludes .git, .venv, node_modules, and build outputs.
    """
    exclude_dirs = {".git", ".venv", "venv", "node_modules", ".vercel", "__pycache__", "borjamoskv_wiki", "reports", "sprol_audits"}
    extensions = {".py", ".js", ".html", ".css", ".json", ".sh"}
    
    total_files = 0
    total_lines = 0
    code_lines = 0
    anergic_lines = 0  # Comments & blank lines
    
    print("\n=== MOSKV-1 WORKSPACE EXERGY SCAN ===")
    print(f"Scanning directory: {root_dir}")
    print("-------------------------------------")
    
    for root, dirs, files in os.walk(root_dir):
        # Prune excluded directories in-place
        dirs[:] = [d for d in dirs if d not in exclude_dirs]
        
        for file in files:
            file_path = Path(root) / file
            if file_path.suffix.lower() not in extensions:
                continue
                
            total_files += 1
            file_lines = 0
            file_code = 0
            file_anergy = 0
            
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    for line in f:
                        file_lines += 1
                        stripped = line.strip()
                        if not stripped:
                            file_anergy += 1
                        elif stripped.startswith("#") or stripped.startswith("//") or (stripped.startswith("/*") and stripped.endswith("*/")):
                            file_anergy += 1
                        else:
                            file_code += 1
            except Exception:
                continue
                
            total_lines += file_lines
            code_lines += file_code
            anergic_lines += file_anergy
            
            # Print files with low density (< 50%) as targets for optimization
            density = file_code / file_lines if file_lines > 0 else 1.0
            if density < 0.5 and file_lines > 15:
                print(f"[!] Low exergy file: {file_path.relative_to(root_dir)} (Density: {density:.2%}, Lines: {file_lines})")
                
    exergy_index = (code_lines / total_lines) * 100 if total_lines > 0 else 100.0
    
    print("-------------------------------------")
    print(f"Total Scanned Files: {total_files}")
    print(f"Total Workspace Lines: {total_lines}")
    print(f"Active Code Lines: {code_lines}")
    print(f"Anergic Lines (Comments/Blanks): {anergic_lines}")
    print(f"Global Workspace Exergy Index: {exergy_index:.2f}%")
    
    if exergy_index < 75.0:
        print("[!] WARN: Low code density detected. Target code refactoring recommended to clean up narrative comments.")
    else:
        print("[✓] SUCCESS: Optimal exergy density. Minimal code comments/slop.")

def calculate_git_diff_exergy() -> float:
    """
    Measures the exergy of the current staged git changes.
    Returns the percentage of active code lines added relative to total lines added.
    """
    import subprocess
    try:
        res = subprocess.run(
            ["git", "diff", "--cached"],
            capture_output=True,
            text=True,
            check=True
        )
        diff_output = res.stdout
    except Exception as e:
        print(f"[GitDiffExergy] Failed to run git diff: {e}")
        return 100.0
        
    if not diff_output.strip():
        return 100.0
        
    added_code = 0
    added_anergy = 0
    
    for line in diff_output.splitlines():
        if line.startswith("+") and not line.startswith("+++"):
            content = line[1:].strip()
            if not content:
                added_anergy += 1
            elif content.startswith("#") or content.startswith("//") or (content.startswith("/*") and content.endswith("*/")) or content.startswith("*"):
                added_anergy += 1
            else:
                added_code += 1
                
    total_added = added_code + added_anergy
    if total_added == 0:
        return 100.0
        
    exergy_index = (added_code / total_added) * 100.0
    print("=== GIT STAGED EXERGY TELEMETRY ===")
    print(f"Staged Code Lines Added: {added_code}")
    print(f"Staged Anergic Lines Added (Comments/Blanks): {added_anergy}")
    print(f"Staged Exergy Index: {exergy_index:.2f}%")
    
    if exergy_index < 80.0 and total_added > 5:
        print("[!] ERROR: Staged changes exergy index is below 80%. High Anergy slop detected in diff.")
        import sys
        sys.exit(1)
        
    print("[✓] Git Staged Exergy check passed.")
    return exergy_index

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="MOSKV-1 Exergy and Telemetry Sensor")
    parser.add_argument("--transcript", type=str, help="Path to transcript.jsonl to verify cognitive exergy")
    parser.add_argument("--workspace", action="store_true", help="Scan the current workspace for structural code exergy")
    parser.add_argument("--git", action="store_true", help="Scan current staged changes for git exergy")
    
    args = parser.parse_args()
    
    if args.git:
        calculate_git_diff_exergy()
    elif args.workspace:
        calculate_workspace_exergy(os.path.dirname(os.path.abspath(__file__)))
    elif args.transcript:
        calculate_exergy(args.transcript)
    else:
        calculate_workspace_exergy(os.path.dirname(os.path.abspath(__file__)))

