#!/bin/zsh
# MOSKV-1 APEX - C5-REAL VIBE-CODE COMPILER
# Translates abstract metaphors/proverbs into zero-anergy physical mutations.

VIBE="$1"
LOG_FILE="/tmp/moskv_vibe.log"

echo "[$(date)] VIBE RECEIVED: $VIBE" >> $LOG_FILE

case "$VIBE" in
    *"ducha de agua fria"*)
        echo "[EXEC] Cold Shower Protocol" >> $LOG_FILE
        osascript -e 'display notification "Ejecutando: Ducha de Agua Fría (Purga de Caché/RAM)" with title "VIBE COMPILER"'
        rm -rf node_modules package-lock.json .next dist 2>/dev/null || true
        purge 2>/dev/null || true
        ;;
    *"muerto el perro se acabo la rabia"*)
        echo "[EXEC] Lethal Process Termination" >> $LOG_FILE
        osascript -e 'display notification "Ejecutando: Muerto el perro... (Aniquilación de procesos zombis)" with title "VIBE COMPILER"'
        pkill -9 -f "node" || true
        pkill -9 -f "python" || true
        lsof -ti:3000,8000,8080 | xargs kill -9 2>/dev/null || true
        ;;
    *"borron y cuenta nueva"*)
        echo "[EXEC] Hard Reset" >> $LOG_FILE
        osascript -e 'display notification "Ejecutando: Borrón y cuenta nueva (Git Hard Reset)" with title "VIBE COMPILER"'
        git reset --hard HEAD
        git clean -fd
        ;;
    *"mas vale pajaro en mano"*)
        echo "[EXEC] SOTA Commit" >> $LOG_FILE
        osascript -e 'display notification "Ejecutando: Pájaro en mano... (Snapshot SOTA)" with title "VIBE COMPILER"'
        git add .
        git commit -m "chore(vibe): consolidación de estado preventivo"
        ;;
    *"quien mucho abarca poco aprieta"*)
        echo "[EXEC] Thermodynamic Consolidation" >> $LOG_FILE
        osascript -e 'display notification "Ejecutando: Quien mucho abarca... (Cierre de subagentes y liberación de memoria)" with title "VIBE COMPILER"'
        pkill -f "run_vesicular.py" || true
        pkill -f "ollama" || true
        ;;
    *)
        echo "[FAIL] Unrecognized Vibe: $VIBE" >> $LOG_FILE
        osascript -e 'display notification "Metáfora no reconocida. Compilación JIT fallida." with title "VIBE COMPILER"'
        exit 1
        ;;
esac

echo "[$(date)] VIBE COMPILED SUCCESSFULLY." >> $LOG_FILE
