import os
import time
import datetime
from pathlib import Path

BLOG_DIR = Path(__file__).parent.absolute()
IMAGES_DIR = BLOG_DIR / "images"
ENTRIES_DIR = BLOG_DIR / "entries"
REMOTE_URL = "https://cortexpersist.com/blog"

def get_images():
    images = set()
    for f in IMAGES_DIR.iterdir():
        if f.is_file() and f.suffix.lower() in ['.jpg', '.jpeg', '.png', '.gif', '.webp']:
            images.add(f.name)
    return images

def create_blog_entry(image_name):
    image_path = IMAGES_DIR / image_name
    date_str = datetime.datetime.now().strftime("%Y-%m-%d")
    title = image_path.stem.replace('-', ' ').replace('_', ' ').title()
    slug = f"{date_str}-{image_path.stem}"
    entry_path = ENTRIES_DIR / f"{slug}.md"
    
    if entry_path.exists():
        return
        
    content = f"""---
title: "{title}"
date: {datetime.datetime.now().isoformat()}
image: /images/{image_name}
url: {REMOTE_URL}/{slug}
---

![{title}](/images/{image_name})
"""
    with open(entry_path, "w") as f:
        f.write(content)
    print(f"[{datetime.datetime.now().isoformat()}] C5-REAL: Ledger mutado. Entrada creada -> {entry_path.name}")

def run_watcher():
    IMAGES_DIR.mkdir(parents=True, exist_ok=True)
    ENTRIES_DIR.mkdir(parents=True, exist_ok=True)
    
    print(f"C5-REAL Daemon Init. Operador: borjamoskv.")
    print(f"Mapping Endpoint: {REMOTE_URL}")
    print(f"Watch Dir: {IMAGES_DIR}")
    
    known_images = get_images()
    
    try:
        while True:
            time.sleep(1)
            current_images = get_images()
            new_images = current_images - known_images
            for img in new_images:
                create_blog_entry(img)
            known_images = current_images
    except KeyboardInterrupt:
        print("Daemon terminated.")

if __name__ == "__main__":
    run_watcher()
