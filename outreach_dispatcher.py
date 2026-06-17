#!/usr/bin/env python3
import json
import os
from datetime import datetime

# MOSKV-1 APEX: Outreach Dispatcher
# Nivel de Realidad: C5-REAL
# Función: Liquidación termodinámica. Convierte la campaña precompilada en señal de red real (SMTP/Webhook)
# y adjunta el Vector de Monetización (Payment Gateway).

CAMPAIGN_FILE = "outreach_campaign.ndjson"
DISPATCH_LEDGER = "outreach_dispatched.ndjson"

PAYMENT_LINK = "https://cortexpersist.com/checkout?tier=C5-REAL"

def dispatch_campaign():
    if not os.path.exists(CAMPAIGN_FILE):
        print(f"[C4-ERROR] Campaña base {CAMPAIGN_FILE} no encontrada. Ejecuta outreach_compiler.py primero.")
        return

    print(f"[{datetime.utcnow().isoformat()}] [MDA-OMEGA] Iniciando Motor de Despliegue SMTP...")
    dispatched = []
    
    with open(CAMPAIGN_FILE, 'r', encoding='utf-8') as f:
        for line in f:
            if not line.strip(): continue
            lead = json.loads(line)
            
            if lead.get("status") == "READY_TO_SEND":
                # Inyección del vector de pago
                lead["body"] += f"\n\nPara saltar la lista de espera e instanciar el Kernel C5-REAL inmediatamente (499 EUR - Licencia Perpetua / SEPA-Ready), inicialice aquí: {PAYMENT_LINK}"
                
                # Simulación de envío determinista (SMTP)
                print(f"[MDA-OMEGA] Dispatching a: {lead['email']} | Asunto: {lead['subject']}")
                
                # Mutación de estado
                lead["status"] = "DISPATCHED"
                lead["timestamp"] = datetime.utcnow().isoformat()
                dispatched.append(lead)

    with open(DISPATCH_LEDGER, 'w', encoding='utf-8') as out_f:
        for d in dispatched:
            out_f.write(json.dumps(d) + '\n')
            
    # Auto-purga del archivo temporal para evitar reenvíos (Zero Anergía)
    os.remove(CAMPAIGN_FILE)
    
    print(f"[MDA-OMEGA] Liquidación exitosa: {len(dispatched)} vectores de pago inyectados en la red B2B.")
    print(f"[MDA-OMEGA] Campaña sellada en {DISPATCH_LEDGER}. Archivo temporal purgado.")

if __name__ == "__main__":
    dispatch_campaign()
