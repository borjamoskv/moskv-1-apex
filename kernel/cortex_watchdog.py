#!/usr/bin/env python3
import os
import subprocess
import sys
from datetime import datetime, timezone

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BOARD_SCRIPT = os.path.join(ROOT_DIR, "kernel", "board_of_directors.py")

def enforce_autopoiesis() -> None:
    print(f"[{datetime.now(timezone.utc).isoformat()}] [WATCHDOG-OMEGA] Checking autopoiesis scheduling...")
    import platform
    import shutil
    
    if platform.system() == "Darwin":
        print("[WATCHDOG-OMEGA] macOS detected. Enforcing launchd autopoiesis...")
        plist_name = "com.moskv.board.plist"
        src_plist = os.path.join(ROOT_DIR, plist_name)
        dest_plist = os.path.expanduser(f"~/Library/LaunchAgents/{plist_name}")
        
        # Copy plist if missing or out of sync
        should_load = False
        if not os.path.exists(dest_plist):
            print(f"[WATCHDOG-OMEGA] Copying plist to {dest_plist}")
            try:
                shutil.copy(src_plist, dest_plist)
                should_load = True
            except Exception as e:
                print(f"[C4-ERROR] Failed to copy plist: {e}")
        
        # Check if loaded in launchctl
        try:
            output = subprocess.check_output(["launchctl", "list"]).decode("utf-8")
        except Exception:
            output = ""
            
        if "com.moskv.board" not in output or should_load:
            print("[WATCHDOG-OMEGA] Loading launchd job...")
            # Use bootstrap gui domain if possible
            uid = os.getuid()
            subprocess.run(["launchctl", "bootstrap", f"gui/{uid}", dest_plist], capture_output=True)
            # Legacy fallback
            subprocess.run(["launchctl", "load", dest_plist], capture_output=True)
            print("[WATCHDOG-OMEGA] launchd agent active.")
        else:
            print("[WATCHDOG-OMEGA] launchd agent already loaded.")
            
        # Clean up legacy crontab board job if exists
        try:
            current_cron = subprocess.check_output(["crontab", "-l"]).decode("utf-8")
            if BOARD_SCRIPT in current_cron:
                print("[WATCHDOG-OMEGA] Removing legacy crontab board job...")
                new_lines = [line for line in current_cron.splitlines() if BOARD_SCRIPT not in line]
                if new_lines:
                    new_cron = "\n".join(new_lines) + "\n"
                else:
                    new_cron = ""
                
                if new_cron.strip():
                    tmp_cron_file = os.path.join(ROOT_DIR, "tmp_cron.txt")
                    with open(tmp_cron_file, 'w') as f:
                        f.write(new_cron)
                    subprocess.run(["crontab", tmp_cron_file], check=True)
                    os.remove(tmp_cron_file)
                else:
                    subprocess.run(["crontab", "-r"], check=True)
                print("[WATCHDOG-OMEGA] Legacy crontab board job successfully purged.")
        except Exception:
            pass
            
    else:
        # Fallback to crontab for Linux
        print("[WATCHDOG-OMEGA] Linux/POSIX detected. Enforcing crontab autopoiesis...")
        # Use sys.executable to ensure we use the active Python interpreter
        python_exe = sys.executable or "python3"
        cron_command = f"0 * * * * {python_exe} {BOARD_SCRIPT} >> {ROOT_DIR}/board_cron.log 2>&1"
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
            print("[WATCHDOG-OMEGA] crontab autopoiesis enabled.")

def trigger_immediate_board() -> None:
    print(f"[{datetime.now(timezone.utc).isoformat()}] [WATCHDOG-OMEGA] Triggering board execution...")
    # Use sys.executable for internal consistency
    subprocess.run([sys.executable or "python3", BOARD_SCRIPT], cwd=ROOT_DIR)

if __name__ == "__main__":
    enforce_autopoiesis()
    trigger_immediate_board()

