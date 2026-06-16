#!/bin/zsh
# MOSKV-1 APEX - C5-REAL OUROBOROS-INFINITY SLEEP PROTOCOL
# Version: 4.0 (Hardware-Level & Self-Healing)

# --- CONFIGURATION ---
SCRIPT_DIR="${0:A:h}"
WORKSPACE="$SCRIPT_DIR"
SOTA_ARCHIVE="$WORKSPACE/SOTA_Archive"
LOG_FILE="/tmp/moskv_exergy_purge.log"
DATE_TAG=$(date +%Y%m%d_%H%M%S)

# --- 0. AUTOPOIESIS (CRON SENTINEL) ---
# Ensure script is in crontab (Self-healing mechanism)
if ! crontab -l 2>/dev/null | grep -q "moskv_sleep.sh"; then
    echo "[$(date)] Self-healing: Injecting into crontab" >> $LOG_FILE
    (crontab -l 2>/dev/null; echo "0 3 * * * $WORKSPACE/moskv_sleep.sh") | crontab -
fi

mkdir -p "$SOTA_ARCHIVE"
echo "=== [$(date)] INITIATING MOSKV-1 OUROBOROS SLEEP PROTOCOL ===" >> $LOG_FILE

# --- 1. HEADLESS/UI ABORT MECHANISM ---
# Timeout de 300s. Si no hay GUI, el comando falla y el || true permite seguir.
RESPONSE=$(osascript -e 'display dialog "MOSKV-1 HARDWARE SLEEP in 5 minutes.\n\nPersisting SOTA, Purging Memory, TCP Ports, and hardware suspension." with title "MOSKV-1 [OUROBOROS INITIATION]" buttons {"Abortar", "Proceder"} default button "Proceder" giving up after 300' 2>/dev/null || echo "Headless")

if echo "$RESPONSE" | grep -q "Abortar"; then
    osascript -e 'display notification "Secuencia Ouroboros abortada por el Operador." with title "MOSKV-1 [OVERRIDE]" sound name "Funk"' 2>/dev/null || true
    echo "[$(date)] ABORTED by Operator." >> $LOG_FILE
    exit 0
fi

osascript -e 'display notification "Consolidando Persistencia SOTA y sellando Ledger..." with title "MOSKV-1 [SOTA SYNC]" sound name "Pop"' 2>/dev/null || true

# --- 2. SOTA PERSISTENCE & ROTATION ---
echo "[$(date)] Executing SOTA Persistence..." >> $LOG_FILE
tar -czf "$SOTA_ARCHIVE/sota_snapshot_$DATE_TAG.tar.gz" --exclude="SOTA_Archive" --exclude=".git" --exclude="node_modules" -C "$WORKSPACE" . >> $LOG_FILE 2>&1

# Anti-Entropy: Delete SOTA archives older than 7 days
find "$SOTA_ARCHIVE" -name "sota_snapshot_*.tar.gz" -type f -mtime +7 -exec rm {} \;
echo "[$(date)] SOTA Snapshot Saved. Old archives rotated." >> $LOG_FILE

# --- 3. GIT SENTINEL ---
echo "[$(date)] Sincronizando Ledger C5-REAL..." >> $LOG_FILE
cd "$WORKSPACE" || exit
git add .
git commit -m "chore(ouroboros): MOSKV-1 hardware sleep sequence state lock [$DATE_TAG]" >> $LOG_FILE 2>&1
git tag "OUROBOROS-SLEEP-$DATE_TAG"

osascript -e 'display notification "Iniciando purga profunda..." with title "MOSKV-1 [PURGE ACTIVE]" sound name "Basso"' 2>/dev/null || true

# --- 4. EXERGY PURGE ---
echo "[$(date)] Purging Orphaned Processes and Ports..." >> $LOG_FILE
pkill -f "run_vesicular.py" || true
pkill -f "ollama run" || true
pkill -f "ngrok" || true
lsof -ti:3000,8080,8000 | xargs kill -9 2>/dev/null || true
purge || true

echo "=== [$(date)] OUROBOROS PURGE COMPLETE. INITIATING HARDWARE SLEEP. ===" >> $LOG_FILE

# --- 5. HARDWARE EXERGY CONSERVATION ---
# Actually put the Mac to sleep (or lock screen)
osascript -e 'tell application "Finder" to sleep' || pmset sleepnow || true

