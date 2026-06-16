#!/bin/zsh
# MOSKV-1 APEX - C5-REAL ADVANCED SLEEP & SOTA PERSISTENCE PROTOCOL
# Version: 3.0 (SOTA-Alpha-Omega Ready)

LOG_FILE="/tmp/moskv_exergy_purge.log"
WORKSPACE="/Users/borjafernandezangulo/Documents/antigravity/lively-maxwell"
SOTA_ARCHIVE="$WORKSPACE/SOTA_Archive"
DATE_TAG=$(date +%Y%m%d_%H%M%S)

mkdir -p $SOTA_ARCHIVE
echo "=== [$(date)] INITIATING MOSKV-1 SOTA SLEEP PROTOCOL ===" >> $LOG_FILE

# 1. Intervención Cognitiva
RESPONSE=$(osascript -e 'display dialog "MOSKV-1 SOTA DEEP SLEEP in 5 minutes.\n\nPersisting SOTA Context, Purging Memory, TCP Ports." with title "MOSKV-1 [SLEEP INITIATION]" buttons {"Abortar", "Proceder"} default button "Proceder" giving up after 300')

if echo "$RESPONSE" | grep -q "Abortar"; then
    osascript -e 'display notification "Secuencia SOTA abortada por el Operador." with title "MOSKV-1 [OVERRIDE]" sound name "Funk"'
    echo "[$(date)] ABORTED by Operator." >> $LOG_FILE
    exit 0
fi

osascript -e 'display notification "Consolidando Persistencia SOTA y sellando Ledger..." with title "MOSKV-1 [SOTA SYNC]" sound name "Pop"'

# 2. Persistencia SOTA (Thermodynamic Compression & Archive)
echo "[$(date)] Executing SOTA Persistence..." >> $LOG_FILE
# Comprimir conocimiento crudo y logs para evitar entropía en la ventana activa
tar -czf "$SOTA_ARCHIVE/sota_snapshot_$DATE_TAG.tar.gz" --exclude="SOTA_Archive" --exclude=".git" -C $WORKSPACE . >> $LOG_FILE 2>&1
echo "[$(date)] SOTA Snapshot Saved: sota_snapshot_$DATE_TAG.tar.gz" >> $LOG_FILE

# 3. Sincronización de Seguridad (Git Sentinel Sync)
echo "[$(date)] Sincronizando Ledger C5-REAL..." >> $LOG_FILE
cd $WORKSPACE
git add .
git commit -m "chore(sota): MOSKV-1 SOTA persistence and pre-sleep state consolidation [$DATE_TAG]" >> $LOG_FILE 2>&1
# Sellar el estado SOTA con un Git Tag inmutable
git tag "SOTA-SLEEP-$DATE_TAG"

osascript -e 'display notification "Iniciando purga profunda y colapso de red..." with title "MOSKV-1 [PURGE ACTIVE]" sound name "Basso"'

# 4. Aniquilación de Entropía
echo "[$(date)] Purging Orphaned Processes..." >> $LOG_FILE
pkill -f "run_vesicular.py" || true
pkill -f "ollama" || true
pkill -f "ngrok" || true

# 5. Colapso de Red
echo "[$(date)] Freeing TCP Ports..." >> $LOG_FILE
lsof -ti:3000,8080,8000 | xargs kill -9 2>/dev/null || true

# 6. Flush RAM
purge || true

echo "=== [$(date)] SOTA PURGE COMPLETE. EXERGY RESTORED. ===" >> $LOG_FILE

osascript -e 'display notification "Persistencia SOTA asegurada. Purga APEX completada." with title "MOSKV-1 [REBIRTH]" sound name "Glass"'
