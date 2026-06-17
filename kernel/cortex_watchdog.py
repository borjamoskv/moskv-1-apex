#!/usr/bin/env python3
import os
import subprocess
import sys
from datetime import datetime, timezone

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BOARD_SCRIPT = os.path.join(ROOT_DIR, "kernel", "board_of_directors.py")

def enforce_autopoiesis() -> None:
    print(f"[{datetime.now(timezone.utc).isoformat()}] [WATCHDOG-OMEGA] Checking crontab autopoiesis...")
    cron_command = f"0 * * * * python3 {BOARD_SCRIPT} >> {ROOT_DIR}/board_cron.log 2>&1"
    try:
        current_cron = subprocess.check_output(["crontab", "-l"]).decode("utf-8")
    except subprocess.CalledProcessError:
        current_cron = ""
    if BOARD_SCRIPT in current_cron:
        print("[WATCHDOG-OMEGA] Board script already registered in crontab.")
    else:
        print("[WATCHDOG-OMEGA] Ingesting crontab job...")
        new_cron = current_cron.strip() + "\n" + cron_command + "\n"
        tmp_cron_file = os.path.join(ROOT_DIR, "tmp_cron.txt")
        with open(tmp_cron_file, 'w') as f:
            f.write(new_cron)
        subprocess.run(["crontab", tmp_cron_file], check=True)
        os.remove(tmp_cron_file)
        print("[WATCHDOG-OMEGA] Autopoiesis enabled.")

def trigger_immediate_board() -> None:
    print(f"[{datetime.now(timezone.utc).isoformat()}] [WATCHDOG-OMEGA] Triggering board execution...")
    subprocess.run(["python3", BOARD_SCRIPT], cwd=ROOT_DIR)

if __name__ == "__main__":
    enforce_autopoiesis()
    trigger_immediate_board()
