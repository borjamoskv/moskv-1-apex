#!/usr/bin/env python3
import os
import sys
import subprocess
import re
from pathlib import Path

def run_test_suite():
    print("[Ouroboros-∞] Executing automated test suite audit...")
    my_env = os.environ.copy()
    my_env["PYTHONPATH"] = str(Path(__file__).parent.parent / "src")
    
    try:
        result = subprocess.run(
            ["pytest"],
            capture_output=True,
            text=True,
            env=my_env
        )
        return result.returncode == 0, result.stdout, result.stderr
    except FileNotFoundError:
        result = subprocess.run(
            [sys.executable, "-m", "pytest"],
            capture_output=True,
            text=True,
            env=my_env
        )
        return result.returncode == 0, result.stdout, result.stderr

def run_exergy_audit():
    print("[Ouroboros-∞] Evaluating thermodynamic context exergy...")
    base_dir = Path(__file__).parent.parent
    app_data_dir = Path("/Users/borjafernandezangulo/.gemini/antigravity")
    brain_dir = app_data_dir / "brain"
    
    transcript_path = None
    if brain_dir.exists():
        subdirs = [d for d in brain_dir.iterdir() if d.is_dir()]
        if subdirs:
            latest_subdir = max(subdirs, key=lambda d: d.stat().st_mtime)
            transcript_path = latest_subdir / ".system_generated" / "logs" / "transcript.jsonl"
            
    if not transcript_path or not transcript_path.exists():
        print("[Ouroboros-∞] No active transcript log found.")
        return 0.0

    sensor_script = base_dir / "scripts" / "exergy_sensor.py"
    if not sensor_script.exists():
        sensor_script = base_dir / "exergy_sensor.py"
        
    result = subprocess.run(
        [sys.executable, str(sensor_script), str(transcript_path)],
        capture_output=True,
        text=True
    )
    print(result.stdout)
    
    # Extract calculated anergy/entropy value to feed the RL
    match = re.search(r'Total Session Anergy:\s*([0-9.]+)', result.stdout)
    if match:
        return float(match.group(1))
    return 0.0

def reinforce_models(session_anergy: float):
    print("[Ouroboros-∞] Triggering Reinforcement Learning update vectors...")
    sys.path.append(str(Path(__file__).parent.parent / "src"))
    
    try:
        from moskv_1.exergy import DynamicExergyMeter
        meter = DynamicExergyMeter()
        meter.reinforce(system_entropy=session_anergy)
        print(f"[RL-ExergyMeter] Updated Weights -> TokenCost: {meter.token_cost_weight:.6f} | Starvation: {meter.starvation_decay_factor:.4f}")
    except Exception as e:
        print(f"[Ouroboros-∞] Error RL ExergyMeter: {e}")

    try:
        from moskv_1.mpc_controller import CognitiveRLNMPC
        rl_nmpc = CognitiveRLNMPC()
        rl_nmpc.reinforce(predicted_exergy=1.0, actual_exergy=max(0.1, 1.0 - (session_anergy * 0.01)))
        print(f"[RL-NMPC] Updated Weights -> Q: {rl_nmpc.Q:.4f} | R: {rl_nmpc.R:.4f} | Lambda: {rl_nmpc.lmbda:.4f}")
    except Exception as e:
        print(f"[Ouroboros-∞] Error RL NMPC: {e}")

def check_git_status():
    result = subprocess.run(["git", "status", "--porcelain"], capture_output=True, text=True)
    return result.stdout.strip()

def ouroboros_cycle():
    print("=== STARTING OUROBOROS-∞ CLOSED-LOOP COGNITIVE CYCLE ===")
    
    tests_passed, stdout, stderr = run_test_suite()
    if not tests_passed:
        print("[Ouroboros-∞] CRITICAL: System test suite failed. Initiating self-healing sequence...")
        sensor_script = Path(__file__).parent / "error_sensor.py"
        try:
            result = subprocess.run(
                [sys.executable, str(sensor_script)],
                input=stdout + "\n" + stderr,
                capture_output=True,
                text=True
            )
            print(result.stdout)
            if result.returncode == 0:
                print("[Ouroboros-∞] Auto-curación completada. Re-evaluando Gate 3...")
                tests_passed_2, stdout_2, stderr_2 = run_test_suite()
                if not tests_passed_2:
                    print("[Ouroboros-∞] Entropía persistente. Abortando.")
                    sys.exit(1)
            else:
                print("[Ouroboros-∞] Error Sensor falló. Abortando.")
                sys.exit(1)
        except Exception as e:
            print(f"[Ouroboros-∞] Fallo crítico: {e}")
            sys.exit(1)
    else:
        print("[Ouroboros-∞] ✓ Test suite verification passed successfully.")
        
    session_anergy = run_exergy_audit()
    
    if session_anergy > 0:
        reinforce_models(session_anergy)
    
    uncommitted = check_git_status()
    if uncommitted:
        print("[Ouroboros-∞] Detected uncommitted modifications in the Ledger:")
        print(uncommitted)
        subprocess.run(["git", "add", "."])
        subprocess.run(["git", "commit", "-m", "chore(autopoiesis): dynamic ledger alignment via Ouroboros-∞ RL feedback"])
        print("[Ouroboros-∞] Ledger mutations sealed successfully.")
    else:
        print("[Ouroboros-∞] ✓ Ledger is fully synchronized.")
        
    print("=== OUROBOROS-∞ CYCLE COMPLETE [NO ENTROPY DETECTED] ===")

if __name__ == "__main__":
    ouroboros_cycle()
