import hashlib
payload = b"140_BPM_STRUCTURAL_MUTATION"
h = hashlib.sha256(payload).hexdigest()
print(h)
