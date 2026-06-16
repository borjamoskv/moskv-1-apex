#!/usr/bin/env python3
# MOSKV-1 APEX - C5-REAL VIBE-CODE COMPILER V2 (Semantic Router)

import sys
import re
import os
import subprocess

def execute(command, notification):
    print(f"[EXEC] {command}")
    os.system(f"osascript -e 'display notification \"{notification}\" with title \"VIBE COMPILER V2\"'")
    subprocess.run(command, shell=True)

def parse_vibe(vibe_string):
    vibe_string = vibe_string.lower()
    
    # 1. Ducha de agua fria (Hard Reset)
    if "ducha" in vibe_string and ("fria" in vibe_string or "helada" in vibe_string):
        execute("rm -rf node_modules package-lock.json .next dist 2>/dev/null && purge", "Ducha de agua fría: Entorno purgado.")
        return

    # 2. Muerto el perro (Targeted Kill)
    perro_match = re.search(r"muerto el perro.*?(\d+)", vibe_string)
    if perro_match:
        port = perro_match.group(1)
        execute(f"lsof -ti:{port} | xargs kill -9 2>/dev/null", f"Perro aniquilado en puerto {port}.")
        return
    elif "muerto el perro" in vibe_string:
        execute("pkill -9 -f node || true", "Perro aniquilado (Procesos Node).")
        return

    # 3. Borrón y cuenta nueva (Git Reset)
    if "borron" in vibe_string and "cuenta nueva" in vibe_string:
        execute("git reset --hard HEAD && git clean -fd", "Borrón y cuenta nueva: Git Tree restaurado.")
        return

    # 4. Pájaro en mano (SOTA Commit)
    if "pajaro en mano" in vibe_string or "pájaro en mano" in vibe_string:
        execute('git add . && git commit -m "chore(vibe): consolidación SOTA preventiva"', "Pájaro en mano: Estado consolidado.")
        return

    print("[FAIL] Vibe no mapeado o entropía excesiva.")
    os.system("osascript -e 'display notification \"Vibe no reconocido. Falta densidad semántica.\" with title \"ERROR DE VIBE\"'")
    sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: ./vibe_compiler.py 'tu refran aqui'")
        sys.exit(1)
    parse_vibe(sys.argv[1])
