import os
from pathlib import Path
root = Path(os.getcwd())
for r, d, f in os.walk(root):
    rp = Path(r)
    if any(p.startswith('.') for p in rp.parts): continue
    for file in f:
        if file.endswith('.js') or file.endswith('.py'):
            fp = rp / file
            parts = fp.relative_to(root).parts
            print(parts)
