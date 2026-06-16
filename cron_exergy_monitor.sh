#!/usr/bin/env bash
# MOSKV-1 APEX: Autonomous Exergy Monitor

TARGET_TRANSCRIPT="$1"

if [ -z "$TARGET_TRANSCRIPT" ]; then
    # Por defecto, mapea al cerebro local si no se especifica
    TARGET_TRANSCRIPT="/Users/borjafernandezangulo/.gemini/antigravity/brain/b33d536f-20a9-4a02-a05c-3d7eab16ca42/.system_generated/logs/transcript.jsonl"
fi

echo "[MOSKV-1] Iniciando Sensorización Autónoma sobre: $TARGET_TRANSCRIPT"

# Llama al sensor y captura la salida
python3 /Users/borjafernandezangulo/Documents/antigravity/lively-maxwell/exergy_sensor.py "$TARGET_TRANSCRIPT" > /tmp/exergy_report.log 2>&1

# Extraer métricas básicas para el log
cat /tmp/exergy_report.log

echo "[MOSKV-1] Monitoreo Exergético Terminado. Anergía calculada y purgada."
