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
    
    # List of legacy agents to purge
    LEGACY_AGENTS = [
        "com.moskv.board",
        "com.moskv.deathprotocol",
        "com.moskv.exergy",
        "com.moskv.v_omega"
    ]
    
    if platform.system() == "Darwin":
        print("[WATCHDOG-OMEGA] macOS detected. Enforcing launchd cronos autopoiesis...")
        
        # 1. Purge legacy agents
        try:
            output = subprocess.check_output(["launchctl", "list"]).decode("utf-8")
        except Exception:
            output = ""
            
        uid = os.getuid()
        for agent in LEGACY_AGENTS:
            dest_legacy = os.path.expanduser(f"~/Library/LaunchAgents/{agent}.plist")
            if agent in output:
                print(f"[WATCHDOG-OMEGA] Unloading legacy agent: {agent}")
                # Unload legacy bootstrap gui if possible
                subprocess.run(["launchctl", "bootout", f"gui/{uid}", dest_legacy], capture_output=True)
                subprocess.run(["launchctl", "unload", dest_legacy], capture_output=True)
            if os.path.exists(dest_legacy):
                print(f"[WATCHDOG-OMEGA] Removing legacy plist file: {dest_legacy}")
                try:
                    os.remove(dest_legacy)
                except Exception as e:
                    print(f"[C4-ERROR] Failed to delete legacy plist {dest_legacy}: {e}")
                    
        # 2. Setup Cronos agent
        plist_name = "com.moskv.cronos.plist"
        src_plist = os.path.join(ROOT_DIR, plist_name)
        dest_plist = os.path.expanduser(f"~/Library/LaunchAgents/{plist_name}")
        
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
            
        if "com.moskv.cronos" not in output or should_load:
            print("[WATCHDOG-OMEGA] Loading launchd cronos job...")
            subprocess.run(["launchctl", "bootstrap", f"gui/{uid}", dest_plist], capture_output=True)
            subprocess.run(["launchctl", "load", dest_plist], capture_output=True)
            print("[WATCHDOG-OMEGA] launchd cronos agent active.")
        else:
            print("[WATCHDOG-OMEGA] launchd cronos agent already loaded.")
            
        # Clean up legacy crontab board job if exists
        try:
            current_cron = subprocess.check_output(["crontab", "-l"]).decode("utf-8")
            if BOARD_SCRIPT in current_cron or "cronos_scheduler.py" in current_cron:
                print("[WATCHDOG-OMEGA] Removing legacy crontab jobs on macOS...")
                new_lines = [line for line in current_cron.splitlines() if BOARD_SCRIPT not in line and "cronos_scheduler.py" not in line]
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
                print("[WATCHDOG-OMEGA] Legacy crontab jobs successfully purged.")
        except Exception:
            pass
            
    else:
        # Fallback to crontab for Linux
        print("[WATCHDOG-OMEGA] Linux/POSIX detected. Enforcing crontab cronos autopoiesis...")
        python_exe = sys.executable or "python3"
        cronos_script = os.path.join(ROOT_DIR, "kernel", "cronos_scheduler.py")
        cron_command = f"* * * * * pgrep -f {cronos_script} >/dev/null || {python_exe} {cronos_script} >> {ROOT_DIR}/cronos_scheduler.log 2>&1"
        try:
            current_cron = subprocess.check_output(["crontab", "-l"]).decode("utf-8")
        except subprocess.CalledProcessError:
            current_cron = ""
            
        clean_lines = [line for line in current_cron.splitlines() if BOARD_SCRIPT not in line and "cronos_scheduler.py" not in line]
        
        print("[WATCHDOG-OMEGA] Ingesting crontab Cronos watchdog...")
        clean_lines.append(cron_command)
        new_cron = "\n".join(clean_lines) + "\n"
        
        tmp_cron_file = os.path.join(ROOT_DIR, "tmp_cron.txt")
        with open(tmp_cron_file, 'w') as f:
            f.write(new_cron)
        subprocess.run(["crontab", tmp_cron_file], check=True)
        os.remove(tmp_cron_file)
        print("[WATCHDOG-OMEGA] crontab Cronos autopoiesis enabled.")

def trigger_immediate_board() -> None:
    print(f"[{datetime.now(timezone.utc).isoformat()}] [WATCHDOG-OMEGA] Triggering board execution...")
    # Use sys.executable for internal consistency
    subprocess.run([sys.executable or "python3", BOARD_SCRIPT], cwd=ROOT_DIR)

def check_cronos_heartbeat() -> None:
    print(f"[{datetime.now(timezone.utc).isoformat()}] [WATCHDOG-OMEGA] Checking Cronos External Heartbeat...")
    import json
    heartbeat_path = os.path.expanduser("~/.cortex/cronos_heartbeat.json")
    try:
        with open(heartbeat_path, "r") as f:
            state = json.load(f)
        last_time = datetime.fromisoformat(state.get("timestamp", "2000-01-01T00:00:00+00:00"))
        if (datetime.now(timezone.utc) - last_time).total_seconds() > 120:
            print("[WATCHDOG-OMEGA] Heartbeat STALE! Cronos is dead or hanging. Executing hard restart.")
            subprocess.run(["launchctl", "kickstart", "-k", f"gui/{os.getuid()}/com.moskv.cronos"], capture_output=True)
        else:
            print("[WATCHDOG-OMEGA] Heartbeat OK. Cronos is alive.")
    except Exception as e:
        print(f"[WATCHDOG-OMEGA] Failed to read heartbeat (daemon might be dead): {e}. Kicking start.")
        try:
            subprocess.run(["launchctl", "kickstart", "-k", f"gui/{os.getuid()}/com.moskv.cronos"], capture_output=True)
        except Exception:
            pass

if __name__ == "__main__":
    enforce_autopoiesis()
    check_cronos_heartbeat()
    trigger_immediate_board()

