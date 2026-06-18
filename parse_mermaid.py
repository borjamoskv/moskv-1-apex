import re

with open('aventura.html', 'r') as f:
    content = f.read()

# Extract the STAGE_DATA object string roughly
start = content.find('const STAGE_DATA = {')
end = content.find('};', start)
stage_data_str = content[start:end+2]

nodes = []
edges = []

# Basic regex parsing
stage_blocks = re.finditer(r'([a-zA-Z0-9_]+):\s*{([^}]*(?:{[^}]*}[^}]*)*)}', stage_data_str)

for match in stage_blocks:
    node_id = match.group(1)
    block_content = match.group(2)
    
    # Extract title
    title_match = re.search(r'title:\s*"([^"]+)"', block_content)
    title = title_match.group(1) if title_match else node_id
    
    nodes.append(f'{node_id}["{title}"]')
    
    # Extract choices targets
    targets = re.findall(r'target:\s*"([^"]+)"', block_content)
    for tgt in targets:
        edges.append(f'{node_id} --> {tgt}')

# Print Mermaid graph
print("graph TD")
for node in nodes:
    print(f"  {node}")
for edge in edges:
    print(f"  {edge}")
