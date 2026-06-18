import hashlib
with open("apps/brt-video/out/index.html", "rb") as f:
    content = f.read()
print(hashlib.sha256(content).hexdigest())
