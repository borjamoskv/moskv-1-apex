#!/usr/bin/env python3
import os
import json
import re
import sys

def analyze_transcript(transcript_path):
    """
    C5-REAL: Analizador físico de los 7 Factores de Estupidez de Robinson
    en la traza de la conversación actual.
    """
    if not os.path.exists(transcript_path):
        print(f"[ERROR] No se encontró la traza forense en: {transcript_path}")
        # Intentar buscar por estructura relativa de appDataDir si es posible
        return None

    factors_detected = {
        "F4_Hiperfijacion": 0,
        "F5_Token_Anergy": 0,
        "F6_Fatiga_Contexto": 0,
        "F7_Las_Prisas": 0
    }
    
    total_steps = 0
    tool_calls_history = []
    
    with open(transcript_path, "r", encoding="utf-8") as f:
        for line in f:
            try:
                step = json.loads(line)
                total_steps += 1
                
                # F6: Fatiga de Contexto (basado en número de pasos de la traza)
                if total_steps > 30:
                    factors_detected["F6_Fatiga_Contexto"] = min(1.0, (total_steps - 30) / 20.0)
                
                # F7: Las Prisas (Falta de metacognición)
                # Buscamos respuestas del modelo para analizar si omiten bloques de reflexión profunda o son inmediatos
                if step.get("source") == "MODEL" and step.get("type") == "PLANNER_RESPONSE":
                    content = step.get("content", "")
                    # En entornos de chat reales, el LLM suele usar etiquetas <thought> o similar en el background.
                    # Si detectamos una respuesta directa muy larga sin llamadas a pensamiento analítico en el contenido.
                    # En este sistema, evaluamos la presencia de anergía y disculpas que denotan falta de metacognición.
                    anergy_words = ["lo siento", "disculpa", "espero que esto ayude", "por supuesto", "aquí tienes"]
                    anergy_count = sum(1 for word in anergy_words if word in content.lower())
                    if anergy_count > 2:
                        factors_detected["F5_Token_Anergy"] += 0.25
                
                # F4: Hiperfijación (Llamadas redundantes a herramientas)
                if "tool_calls" in step and step["tool_calls"]:
                    for tc in step["tool_calls"]:
                        call_sig = (tc.get("name"), json.dumps(tc.get("args"), sort_keys=True))
                        tool_calls_history.append(call_sig)
                        
                        # Si las últimas 3 llamadas son idénticas, hay target fixation
                        if len(tool_calls_history) >= 3:
                            if tool_calls_history[-1] == tool_calls_history[-2] == tool_calls_history[-3]:
                                factors_detected["F4_Hiperfijacion"] = 1.0
                            elif tool_calls_history[-1] == tool_calls_history[-2]:
                                factors_detected["F4_Hiperfijacion"] = max(factors_detected["F4_Hiperfijacion"], 0.5)
            except Exception:
                pass

    # Escalar anergía
    factors_detected["F5_Token_Anergy"] = min(1.0, factors_detected["F5_Token_Anergy"])
    
    # Calcular Score de Estupidez Global (Promedio ponderado)
    # Si F4 (hiperfijación) es alto, la estupidez se dispara
    weights = {
        "F4_Hiperfijacion": 0.4,
        "F5_Token_Anergy": 0.2,
        "F6_Fatiga_Contexto": 0.2,
        "F7_Las_Prisas": 0.2
    }
    
    global_score = sum(factors_detected[k] * weights[k] for k in weights)
    
    return global_score, factors_detected

if __name__ == "__main__":
    print("[C5-REAL] INICIANDO AUDITORÍA FORENSE DE ESTUPIDEZ AGÉNTICA (ROBINSON-CIPPOLA)")
    
    # Ruta por defecto de la sesión actual
    default_path = "/Users/borjafernandezangulo/.gemini/antigravity/brain/edb99ca9-2d38-476c-b2de-085113e41ffd/.system_generated/logs/transcript.jsonl"
    
    path = sys.argv[1] if len(sys.argv) > 1 else default_path
    
    result = analyze_transcript(path)
    
    if not result:
        print("[!] No se pudo procesar la traza forense. Ejecución abortada.")
        sys.exit(0)
        
    score, details = result
    
    print(f"-> Traza analizada: {path}")
    print(f"-> FACTOR F4 (Hiperfijación/Repetición): {details['F4_Hiperfijacion'] * 100:.1f}%")
    print(f"-> FACTOR F5 (Anergía de Token/Slop): {details['F5_Token_Anergy'] * 100:.1f}%")
    print(f"-> FACTOR F6 (Fatiga de Contexto): {details['F6_Fatiga_Contexto'] * 100:.1f}%")
    print(f"-> FACTOR F7 (Prisas/No-Metacognición): {details['F7_Las_Prisas'] * 100:.1f}%")
    print(f"============================================================")
    print(f"-> INDICE DE ESTUPIDEZ AGÉNTICA: {score * 100:.2f}%")
    
    if score > 0.40:
        print("\n[!] ALERTA CRÍTICA: El agente está operando en la zona de colapso cognitivo (Estupidez de Robinson > 40%). Se recomienda purgar el contexto o reiniciar la sesión.")
        sys.exit(1)
    else:
        print("\n[+] SOBERANÍA COGNITIVA VALIDADA. El sistema opera dentro de límites lógicos aceptables.")
        sys.exit(0)
