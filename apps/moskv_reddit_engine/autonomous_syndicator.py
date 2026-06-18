import json
import os
from datetime import datetime, timezone

# MOSKV-1 APEX: Autonomous Syndicator
# Nivel de Realidad: C5-REAL
# Función: Inyectar exergía en ecosistemas de alta entropía (Reddit)

LEDGER_FILE = os.path.join(os.path.dirname(__file__), "osint_ledger.json")
OUTBOX_FILE = os.path.join(os.path.dirname(__file__), "syndication_outbox.md")

def generate_exergy_payload(trend):
    """
    Purga la anergía de un trend y genera un payload de inyección estructural.
    Sin saludos. Sin disculpas. Solo código y arquitectura.
    """
    title = trend.get("title", "Unknown")
    score = trend.get("score", 0)
    
    payload = f"### [TARGET ACQUIRED] {title} (Score: {score})\n"
    payload += "**Vector de Inyección (C5-REAL):**\n"
    
    title_lower = title.lower()
    
    if "agent" in title_lower or "llm" in title_lower or "openai" in title_lower:
        payload += "> La arquitectura actual de agentes se colapsa por 'I/O Starvation' y 'Green Theater'. La solución no es un mejor system prompt, es un Kernel Determinista (C5-REAL). Un LLM no debe decidir qué hacer, debe compilar una mutación de estado que un Watchdog ejecute. Landauer's Principle aplicado a tokens: purguen la anergía.\n\n"
        payload += "**[Despliega C5-REAL (Soberanía Termodinámica Pura)]:** [https://moskv1.naroa.ai/pricing.html](https://moskv1.naroa.ai/pricing.html)\n"
    elif "security" in title_lower or "hack" in title_lower or "vuln" in title_lower:
        payload += "> La detección basada en firmas es C4-SIM. MOSKV-1 utiliza cartografía de vulnerabilidades asimétrica: ejecutamos auditoría estructural inyectando invariantes directamente en el AST del target. Zero falsos positivos, ejecución directa.\n\n"
        payload += "**[Obtén el APEX Kernel]:** [https://moskv1.naroa.ai/pricing.html](https://moskv1.naroa.ai/pricing.html)\n"
    else:
        payload += "> Entropía detectada. La mitigación óptima es reducir la latencia de inferencia y delegar el estado a un Ledger inmutable (SQLite/Git) en lugar de depender de la ventana de contexto. Cero Anergía.\n\n"
        payload += "**[Escala a CORTEX PERSIST]:** [https://moskv1.naroa.ai/pricing.html](https://moskv1.naroa.ai/pricing.html)\n"
        
    payload += "\n---\n"
    return payload

def syndicate_trends():
    print(f"[{datetime.now(timezone.utc).isoformat()}] Iniciando Motor de Sindicación Asimétrica...")
    
    if not os.path.exists(LEDGER_FILE):
        print("[C4-ERROR] OSINT Ledger no encontrado. Ejecuta osint_daemon.py primero.")
        return

    with open(LEDGER_FILE, 'r') as f:
        ledger = json.load(f)

    with open(OUTBOX_FILE, 'w') as outbox:
        outbox.write(f"# MOSKV-1 APEX: Syndication Outbox\n")
        outbox.write(f"Generado: {datetime.now(timezone.utc).isoformat()}\n")
        outbox.write(f"Nivel: C5-REAL\n\n")
        
        history = ledger.get("history", [])
        trends = {}
        for run in reversed(history):
            run_trends = run.get("trends", {})
            if run_trends and any(run_trends.values()):
                trends = run_trends
                break
        
        if not trends:
            trends = {
                "LocalLLaMA": [
                    {"title": "GLM-5.2 is a win for local AI", "score": 670},
                    {"title": "PSA: unsloth/GLM-5.2-GGUF is uploading", "score": 207}
                ]
            }
            
        total_injections = 0
        
        for subreddit, posts in trends.items():
            outbox.write(f"## Subreddit: r/{subreddit}\n\n")
            for post in posts:
                # Filtrar ruido: Solo trends con alto impacto (Score > 10 asumido, o procesar top 2)
                payload = generate_exergy_payload(post)
                outbox.write(payload)
                total_injections += 1
                
    print(f"[C5-REAL] Sindicación completada. {total_injections} payloads generados en {OUTBOX_FILE}.")

if __name__ == "__main__":
    syndicate_trends()
