#!/usr/bin/env python3
import os
import json
from datetime import datetime

WORKSPACE_PATH = "/Users/borjafernandezangulo/Documents/antigravity/lively-maxwell"
BRAIN_PATH = "/Users/borjafernandezangulo/.gemini/antigravity/brain"
OUTPUT_FILE = os.path.join(WORKSPACE_PATH, "cortex_index.json")

EXCLUDED_DIRS = {".git", ".venv", "node_modules", "__pycache__", ".pytest_cache", ".moskv_override", ".vercel"}
EXCLUDED_FILES = {".DS_Store", "package-lock.json", "cortex_index.json"}

def format_size(bytes_size):
    for unit in ['B', 'KB', 'MB', 'GB']:
        if bytes_size < 1024.0:
            return f"{bytes_size:.1f} {unit}"
        bytes_size /= 1024.0
    return f"{bytes_size:.1f} TB"

def get_file_category(filename, filepath):
    filename_lower = filename.lower()
    path_lower = filepath.lower()
    
    if "el_espacio_entre_nosotros" in filename_lower or "space_between_us" in filename_lower:
        return "Novel"
    if "cortex_blog" in path_lower and filename_lower.endswith(".md"):
        return "Manifesto"
    if filename_lower.endswith((".py", ".js", ".sh")):
        return "Script"
    if filename_lower.endswith((".json", ".yaml", ".yml", ".toml")):
        return "Config"
    if filename_lower.endswith((".db", ".sqlite", ".ndjson", ".sqlite3")):
        return "Database"
    if filename_lower.endswith(".plist"):
        return "System"
    if filename_lower.endswith(".md"):
        if "audit" in filename_lower or "report" in filename_lower:
            return "Audit"
        return "Doc"
    if filename_lower.endswith((".pdf", ".epub")):
        return "Document"
    return "Other"

def extract_md_title_and_preview(filepath):
    title = ""
    preview = ""
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            lines = [f.readline().strip() for _ in range(15)]
            for line in lines:
                if line.startswith("# "):
                    title = line.replace("# ", "")
                    break
                elif line.startswith("title:"):
                    title = line.replace("title:", "").strip().strip('"').strip("'")
                    break
            content_lines = [l for l in lines if l and not l.startswith("#") and not l.startswith("---") and not l.startswith("title:")][:3]
            preview = " ".join(content_lines)[:180] + "..." if content_lines else ""
    except Exception:
        pass
    return title, preview

def index_workspace():
    indexed_files = []
    
    for root, dirs, files in os.walk(WORKSPACE_PATH):
        dirs[:] = [d for d in dirs if d not in EXCLUDED_DIRS]
        
        for file in files:
            if file in EXCLUDED_FILES:
                continue
                
            filepath = os.path.join(root, file)
            try:
                stat = os.stat(filepath)
                category = get_file_category(file, filepath)
                
                title, preview = "", ""
                if file.endswith(".md"):
                    title, preview = extract_md_title_and_preview(filepath)
                
                indexed_files.append({
                    "name": file,
                    "title": title or file,
                    "path": filepath,
                    "rel_path": os.path.relpath(filepath, WORKSPACE_PATH),
                    "category": category,
                    "size": format_size(stat.st_size),
                    "size_bytes": stat.st_size,
                    "last_modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                    "location": "Workspace",
                    "preview": preview or f"Archivo local de tipo {category}."
                })
            except Exception as e:
                print(f"Error indexando {filepath}: {e}")

    if os.path.exists(BRAIN_PATH):
        for conv_id in os.listdir(BRAIN_PATH):
            conv_dir = os.path.join(BRAIN_PATH, conv_id)
            if not os.path.isdir(conv_dir) or conv_id.startswith("."):
                continue
                
            conv_title = conv_id[:8]
            for root, dirs, files in os.walk(conv_dir):
                dirs[:] = [d for d in dirs if d not in EXCLUDED_DIRS]
                for file in files:
                    if file in EXCLUDED_FILES or file.endswith(".metadata.json") or file.endswith(".jsonl"):
                        continue
                        
                    filepath = os.path.join(root, file)
                    try:
                        stat = os.stat(filepath)
                        category = get_file_category(file, filepath)
                        
                        title, preview = "", ""
                        if file.endswith(".md"):
                            title, preview = extract_md_title_and_preview(filepath)
                            
                        if conv_id == "9b80ea63-c6db-4a94-b668-b8efc6e5389c":
                            conv_title = "Writing The Novel Space Between Us"
                        elif conv_id == "36961822-da76-4ddb-8714-107ef23f3863":
                            conv_title = "Refactoring Agents Archi Landing Page"
                        elif conv_id == "107f626c-e106-440f-9186-c24ea6bd7db7":
                            conv_title = "Vercel Cloudflare Conflict Agent"
                        elif conv_id == "e9af912f-1a3a-495e-b7ef-7efd247727cf":
                            conv_title = "MOSKV-1 CEO Autopoiesis"
                        elif conv_id == "d3fd3d23-b787-4d97-9f10-7e5ba47cba94":
                            conv_title = "Optimizing Operational Work Logic"
                            
                        indexed_files.append({
                            "name": file,
                            "title": title or file,
                            "path": filepath,
                            "rel_path": os.path.join("brain", conv_id, os.path.relpath(filepath, conv_dir)),
                            "category": category,
                            "size": format_size(stat.st_size),
                            "size_bytes": stat.st_size,
                            "last_modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                            "location": f"Brain: {conv_title}",
                            "preview": preview or f"Artefacto generado en la conversación '{conv_title}'."
                        })
                    except Exception as e:
                        print(f"Error indexando cerebro {filepath}: {e}")

    indexed_files.sort(key=lambda x: x["last_modified"], reverse=True)
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump({
            "generated_at": datetime.now().isoformat(),
            "total_files": len(indexed_files),
            "files": indexed_files
        }, f, indent=2, ensure_ascii=False)
        
    print(f"[SUCCESS] Indexado completo: {len(indexed_files)} archivos guardados")

if __name__ == "__main__":
    index_workspace()
