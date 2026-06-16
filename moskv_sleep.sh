#!/bin/zsh
# MOSKV-1 APEX - C5-REAL ADVANCED SLEEP & EXERGY PURGE PROTOCOL
# Version: 2.0 (Singularity-Ready)

LOG_FILE="/tmp/moskv_exergy_purge.log"
WORKSPACE="/Users/borjafernandezangulo/Documents/antigravity/lively-maxwell"

echo "=== [$(date)] INITIATING MOSKV-1 DEEP SLEEP PROTOCOL ===" >> $LOG_FILE

# 1. Intervención Cognitiva (Aviso Abortable)
RESPONSE=$(osascript -e 'display dialog "MOSKV-1 DEEP SLEEP in 5 minutes.\n\nPurging Memory, TCP Ports, and Orphaned AI Runtimes." with title "MOSKV-1 [SLEEP INITIATION]" buttons {"Abortar", "Proceder"} default button "Proceder" giving up after 300')

if echo "$RESPONSE" | grep -q "Abortar"; then
    osascript -e 'display notification "Secuencia de sueño abortada por el Operador. Exergía sostenida." with title "MOSKV-1 [OVERRIDE]" sound name "Funk"'
    echo "[$(date)] ABORTED by Operator." >> $LOG_FILE
    exit 0
fi

# 2. Sincronización de Seguridad (Git Sentinel Sync)
echo "[$(date)] Sincronizando Ledger C5-REAL..." >> $LOG_FILE
cd $WORKSPACE
git add .
git commit -m "chore(auto): MOSKV-1 pre-sleep state consolidation [$(date +%Y-%m-%d)]" >> $LOG_FILE 2>&1

osascript -e 'display notification "Iniciando purga profunda y colapso de red..." with title "MOSKV-1 [PURGE ACTIVE]" sound name "Basso"'

# 3. Aniquilación de Entropía (Procesos)
echo "[$(date)] Purging Orphaned Processes..." >> $LOG_FILE
pkill -f "run_vesicular.py" || true
pkill -f "ollama" || true
pkill -f "ngrok" || true

# 4. Colapso de Red (Liberación de Puertos Críticos)
echo "[$(date)] Freeing TCP Ports (3000, 8080, 8000)..." >> $LOG_FILE
lsof -ti:3000,8080,8000 | xargs kill -9 2>/dev/null || true

# 5. Flush RAM
purge || true

echo "=== [$(date)] PURGE COMPLETE. EXERGY RESTORED. ===" >> $LOG_FILE

osascript -e 'display notification "Purga APEX completada. Ledger sincronizado. Red y Memoria en Cero-Estado." with title "MOSKV-1 [REBIRTH]" sound name "Glass"'
