import os
import ast
import re
import yaml
from pathlib import Path
from typing import Dict, List, Any

class GraphScanner:
    def __init__(self, root_dir: str):
        self.root_dir = Path(root_dir).resolve()
        self.nodes = []
        self.edges = []
        self.anomalies = []

    def get_era(self, file_path: Path) -> str:
        parts = file_path.relative_to(self.root_dir).parts
        if not parts:
            return "UNKNOWN"
        if parts[0] == "kernel":
            return "LEGACY_ARCHIVE"
        elif parts[0] == "src" and len(parts) > 1 and parts[1] == "moskv_1":
            return "RUNTIME_ACTIVE"
        elif parts[0] == "scripts":
            return "UTILITY"
        return "UNKNOWN"

    def normalize_name(self, filename: str) -> str:
        name = os.path.splitext(filename)[0]
        return name.replace("-", "_")

    def parse_python_imports(self, file_path: Path) -> List[str]:
        imports = []
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                tree = ast.parse(f.read(), filename=str(file_path))
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for n in node.names:
                        imports.append(n.name)
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        imports.append(node.module)
        except Exception:
            pass
        return imports

    def parse_js_imports(self, file_path: Path) -> List[str]:
        imports = []
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            req_matches = re.findall(r"require\(['\"]([^'\"]+)['\"]\)", content)
            imports.extend(req_matches)
            imp_matches = re.findall(r"import\s+.*from\s+['\"]([^'\"]+)['\"]", content)
            imports.extend(imp_matches)
        except Exception:
            pass
        return imports

    def detect_cross_era_execution(self, file_path: Path, content: str, era: str) -> None:
        rel_path = str(file_path.relative_to(self.root_dir))
        if era == "RUNTIME_ACTIVE" and ".js" in content and "node" in content:
            self.anomalies.append({
                "type": "CROSS_ERA_DEPENDENCY",
                "source": rel_path,
                "target": "JavaScript Kernel (Runtime calling Legacy)"
            })
        elif era == "LEGACY_ARCHIVE" and ".py" in content and ("python" in content or "spawn" in content):
            self.anomalies.append({
                "type": "CROSS_ERA_DEPENDENCY",
                "source": rel_path,
                "target": "Python Runtime (Legacy calling Runtime)"
            })

    def scan(self):
        file_map = {}
        for root, dirs, files in os.walk(self.root_dir):
            root_path = Path(root)
            # Skip hidden dirs and node_modules
            rel_parts = root_path.relative_to(self.root_dir).parts
            if any(part.startswith('.') or part == 'node_modules' or part == '__pycache__' for part in rel_parts):
                continue
            
            for file in files:
                if file.endswith('.py') or file.endswith('.js'):
                    file_path = root_path / file
                    rel_path = str(file_path.relative_to(self.root_dir))
                    era = self.get_era(file_path)
                    
                    if era == "UNKNOWN":
                        continue
                        
                    node_type = "python_module" if file.endswith('.py') else "js_module"
                    self.nodes.append({
                        "id": rel_path,
                        "era": era,
                        "type": node_type
                    })
                    
                    norm_name = self.normalize_name(file)
                    if norm_name not in file_map:
                        file_map[norm_name] = []
                    file_map[norm_name].append((rel_path, era))
                    
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                        self.detect_cross_era_execution(file_path, content, era)
                    except Exception:
                        pass
                    
                    if file.endswith('.py'):
                        imports = self.parse_python_imports(file_path)
                        for imp in imports:
                            self.edges.append({
                                "source": rel_path,
                                "target": imp,
                                "relation": "IMPORTS"
                            })
                    else:
                        imports = self.parse_js_imports(file_path)
                        for imp in imports:
                            self.edges.append({
                                "source": rel_path,
                                "target": imp,
                                "relation": "REQUIRES"
                            })

        for norm_name, locations in file_map.items():
            if len(locations) > 1:
                eras = {loc[1] for loc in locations}
                if len(eras) > 1:
                    self.anomalies.append({
                        "type": "DUPLICATE_HOTSPOT",
                        "concept": norm_name,
                        "locations": [loc[0] for loc in locations]
                    })

    def export(self, out_file: str):
        graph = {
            "Nodes": self.nodes,
            "Edges": self.edges,
            "Anomalies": self.anomalies
        }
        with open(out_file, 'w', encoding='utf-8') as f:
            yaml.dump(graph, f, sort_keys=False, default_flow_style=False)

if __name__ == "__main__":
    # Ensure it scans from core/moskv-1
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    scanner = GraphScanner(base_dir)
    scanner.scan()
    out_path = os.path.join(base_dir, "L2_dependency_graph.yaml")
    scanner.export(out_path)
    print(f"[GraphScanner] Scan complete. Nodes: {len(scanner.nodes)}. Output written to {out_path}")
