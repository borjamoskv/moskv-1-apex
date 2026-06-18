import os
import re
import json
import requests

api_key = os.environ.get("GEMINI_API_KEY")
if not api_key:
    raise ValueError("GEMINI_API_KEY environment variable not found.")

url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={api_key}"

prompt = """
Eres un ingeniero de procesamiento digital de señales (DSP) y compositor de techno industrial.
Queremos generar un archivo de código Python autodocumentado y optimizado para sintetizar un videoclip de 60 segundos (140 BPM, 44100Hz, 16-bit Mono WAV) a guardarse en 'apps/brt-video/public/silicon_loop.wav'.

El tema es "El Escudo de Silicio" (Taiwán, TSMC, litografía EUV, Hsinchu). Fusionamos la tensión árida del Oeste Americano (Spaghetti Western, silbidos con vibrato, guitarras tremolo) con la precisión milimétrica oriental (punteos Guzheng y Shamisen en escala Yo: A, B, D, E, G).

Escribe el código Python completo para realizar la síntesis:
1. Kick drum: Bombo techno industrial pesado y distorsionado (tanh saturado) con envolvente de pitch rápida. Varía el volumen en la Intro (0-15s), Build (15-30s, acelerando a doble tempo de 26-30s), Drop (30-48s, clímax) y Outro (48-60s, apagado).
2. Hi-hats: Ruido blanco filtrado con envolventes exponenciales en contratiempos.
3. Silbido del Oeste: Onda senoidal pura con vibrato (LFO a 5.8Hz) y un sutil 1.5% de ruido blanco de aire. Aplica portamento (glides de pitch de 120ms) entre notas pentatónicas del oeste.
4. Guitarra Spaghetti Western: Síntesis FM con moduladora a 2x de la portadora y envolvente de rasgueado. Tremolo de amplitud a 6.2Hz.
5. Guzheng/Shamisen Oriental: Punteos rápidos con un timbre de puente zumbante (sawari) sumando una onda de sierra y limitador blando. Programar secuencias rápidas de semicorcheas en escala Yo (A, B, D, E, G).
6. Haz Láser EUV: Sonido de barrido resonante (sweep) sincronizado con el ciclo de 3.0 segundos de la animación visual.
7. Drone pad: Frecuencia de base baja (A1=55Hz) para dar atmósfera industrial.

Escribe el código Python limpio, estructurado y optimizado con bucles rápidos.
Devuelve ÚNICAMENTE el código Python ejecutable dentro de un bloque de código markdown (```python ... ```). No añadas texto explicativo antes ni después.
"""

payload = {
    "contents": [{
        "parts": [{"text": prompt}]
    }]
}

headers = {
    "Content-Type": "application/json"
}

print("[C5-REAL] Conectando con la REST API de Gemini 2.5 Flash...")
response = requests.post(url, headers=headers, json=payload)
response.raise_for_status()

response_json = response.json()
response_text = response_json["candidates"][0]["content"]["parts"][0]["text"]

# Extraer el bloque de código Python de la respuesta
code_match = re.search(r"```python\s*(.*?)\s*```", response_text, re.DOTALL)
if code_match:
    extracted_code = code_match.group(1)
else:
    extracted_code = response_text

output_file = "apps/brt-video/public/synthesize_silicon.py"
print(f"[C5-REAL] Escribiendo código generado por Gemini en {output_file}...")

with open(output_file, "w") as f:
    f.write(extracted_code)

print("[C5-REAL] Escritura completada con éxito.")
