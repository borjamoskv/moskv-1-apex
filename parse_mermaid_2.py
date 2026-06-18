import re
import json

with open('aventura.html', 'r') as f:
    content = f.read()

start = content.find('const STAGE_DATA = {')
end = content.find('};', start)
stage_data_str = content[start:end+2]

nodes = []
edges = []
visited = set()

# We can regex for node definition
node_pattern = r'([a-zA-Z0-9_]+):\s*{'
# Actually, since it's hard to parse raw js object, we can just extract all "target"
# Let's extract block by block
blocks = re.split(r'\n\s+([a-zA-Z0-9_]+):\s*{', '\n' + stage_data_str)

if len(blocks) > 1:
    for i in range(1, len(blocks), 2):
        node_id = blocks[i]
        block_content = blocks[i+1]
        
        # Title
        title_match = re.search(r'title:\s*"([^"]+)"', block_content)
        title = title_match.group(1) if title_match else node_id
        nodes.append(f'{node_id}["{title}"]')
        
        # Choices targets
        targets = re.findall(r'target:\s*\'?\"?([a-zA-Z0-9_]+)\'?\"?', block_content)
        for tgt in targets:
            edges.append(f'{node_id} --> {tgt}')

with open('ultramap_raw.txt', 'w') as f:
    f.write("graph TD\n")
    for node in nodes:
        f.write(f"  {node}\n")
    for edge in edges:
        f.write(f"  {edge}\n")
