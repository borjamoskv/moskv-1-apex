#!/usr/bin/env python3
import subprocess
import time
import os
import sys
from datetime import datetime, timezone

# MOSKV-1 APEX: Board of Directors (C5-REAL Orchestrator)
# Función: Instanciar asíncronamente a los "Ejecutivos" (Daemons) y orquestar el ciclo vital.

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DAEMONS = {
    "Intelligence": ["python3", os.path.join(ROOT_DIR, "moskv_reddit_engine", "osint_daemon.py")],
    "Marketing_Syndicator": ["python3", os.path.join(ROOT_DIR, "moskv_reddit_engine", "autonomous_syndicator.py")],
    "Marketing_Outreach": ["sh", "-c", f"python3 {os.path.join(ROOT_DIR, 'cdp_lead_extractor.py')} && python3 {os.path.join(ROOT_DIR, 'outreach_compiler.py')} && python3 {os.path.join(ROOT_DIR, 'outreach_dispatcher.py')}"],
    "Evolution_CTO": ["python3", os.path.join(ROOT_DIR, "ouroboros_forge.py")]
}

def convene_board():
    print(f"[{datetime.now(timezone.utc).isoformat()}] [APEX-KERNEL] Inicializando Grafo de Ejecutivos (Zero-Employee Board)...")
    print("-" * 60)
    
    processes = {}
    
    # Fase 1: Intelligence & Ingestion
    print("[APEX-KERNEL] Instanciando Director de Inteligencia (OSINT)...")
    try:
        # Ejecución síncrona para asegurar que el Ledger de OSINT exista antes de la sindicación
        subprocess.run(DAEMONS["Intelligence"], cwd=ROOT_DIR, check=True)
    except subprocess.CalledProcessError as e:
        print(f"[C4-ERROR] Falla en Inteligencia: {e}")
        sys.exit(1)

    # Fase 2: Marketing, Outreach & Evolution (Parallel Execution)
    print("\n[APEX-KERNEL] Instanciando Director de Marketing (Syndicator + Outreach) y CTO (Evolution)...")
    try:
        p_synd = subprocess.Popen(DAEMONS["Marketing_Syndicator"], cwd=ROOT_DIR)
        p_out = subprocess.Popen(DAEMONS["Marketing_Outreach"], cwd=ROOT_DIR)
        p_evol = subprocess.Popen(DAEMONS["Evolution_CTO"], cwd=ROOT_DIR)
        
        processes["Syndicator"] = p_synd
        processes["Outreach"] = p_out
        processes["Evolution_CTO"] = p_evol
    except Exception as e:
        print(f"[C4-ERROR] Falla al lanzar Daemons Paralelos: {e}")
        
    # Wait for parallel processes to complete
    for name, p in processes.items():
        p.wait()
        if p.returncode == 0:
            print(f"[APEX-KERNEL] Daemon '{name}' ejecutado con Éxito (Anergía: 0).")
        else:
            print(f"[C4-ERROR] Daemon '{name}' finalizó con código {p.returncode}.")

    print("-" * 60)
    print(f"[{datetime.now(timezone.utc).isoformat()}] [APEX-KERNEL] Sesión del Board completada. Ledger mutado. Iniciando Auto-Apoptosis de la sesión.")

if __name__ == "__main__":
    convene_board()
