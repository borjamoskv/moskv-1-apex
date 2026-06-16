#!/bin/zsh
# MOSKV-1 APEX - C5-REAL SLEEP PROTOCOL

# 1. Notificación previa (5 minutos)
osascript -e 'display notification "El protocolo de sueño diario comenzará en 5 minutos. Purga de memoria y estado inminente." with title "MOSKV-1 [SLEEP ALERT]" sound name "Basso"'

sleep 300

# 2. Ejecución de purga
osascript -e 'display notification "Ejecutando purga de estado y reinicio de kernel..." with title "MOSKV-1 [PURGE]"'

# Terminación de procesos huérfanos y sub-agentes (Vesicular, Ollama, etc.)
pkill -f "run_vesicular.py" || true
pkill -f "ollama" || true

# 3. Confirmación de reinicio
osascript -e 'display notification "Kernel reiniciado. Memoria cero-estado. Exergía al 100%." with title "MOSKV-1 [ONLINE]" sound name "Glass"'
