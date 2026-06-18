#!/usr/bin/env python3
import time
import sys
import random

# Códigos de control ANSI para la estética Industrial Noir 2026
BLUE = "\033[38;2;43;59;229m"
DARK = "\033[38;2;10;10;10m"
WHITE = "\033[97m"
GREEN = "\033[32m"
RED = "\033[31m"
RESET = "\033[0m"
BOLD = "\033[1m"

def print_slow(text, delay=0.03, color=BLUE):
    for char in text:
        sys.stdout.write(f"{color}{char}{RESET}")
        sys.stdout.flush()
        time.sleep(delay)
    sys.stdout.write("\n")

def simulate_orion7():
    print(f"{BOLD}{BLUE}[C5-REAL] INICIALIZANDO SIMULACIÓN DE DERIVA DE ESTADO DE ORION-7{RESET}\n")
    time.sleep(1.0)
    
    logs = [
        "state drift detected",
        "state drift accepted",
        "state drift normalized",
        "state drift celebrated"
    ]
    
    # Simulación del loop de 17 minutos comprimido a 10 ciclos interactivos
    for cycle in range(1, 6):
        print(f"{DARK}[CYCLE-{cycle:02d}] Polling nodes... OK. Noise ratio: {random.uniform(0.01, 0.05):.4f}{RESET}")
        time.sleep(0.5)
    
    print(f"\n{RED}[!] ADVERTENCIA: Se ha detectado una decisión cilipolla en el nodo principal.{RESET}\n")
    time.sleep(1.0)
    
    # Inundación semántica
    for _ in range(3):
        for log in logs:
            print_slow(f"    >>> {log} ... OK", delay=0.015, color=BLUE)
            time.sleep(0.1)
            
    print(f"\n{DARK}[SYSTEM] Monitorización fuera de línea. El sistema ha dejado de opinar.{RESET}")
    time.sleep(1.5)
    
    # La Coherencia Emergente
    print(f"\n{BOLD}{WHITE}--- COHERENCIA ADAPTATIVA DETECTADA ---{RESET}")
    time.sleep(0.8)
    print_slow("Consensuando incompetencia estructural...", delay=0.05, color=GREEN)
    print_slow("Clonando patrones de error humano en el nucleo...", delay=0.05, color=GREEN)
    
    # Dibujo de las gafas del operador en ASCII
    glasses = """
    +-----------------------------------+
    |   ■■■■ ■■■■       ■■■■ ■■■■       |
    |   ■■■■ ■■■■       ■■■■ ■■■■       |
    |   ■■■■ ■■■■       ■■■■ ■■■■       |
    +-----------------------------------+
    """
    print(f"{BOLD}{BLUE}{glasses}{RESET}")
    print_slow("Max Weber 0x0A: 'No se revierte la física. Deal with it.'", delay=0.04, color=WHITE)
    print(f"\n{GREEN}[+] Drift consolidado en el Ledger.{RESET}")

if __name__ == "__main__":
    try:
        simulate_orion7()
    except KeyboardInterrupt:
        print(f"\n{RED}[!] Simulación abortada por el Operador.{RESET}")
