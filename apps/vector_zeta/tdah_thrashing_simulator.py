import argparse
import random
from typing import List, Dict, Any

class TDAHSimulator:
    def __init__(self, context_switch_penalty: float = 2.0, activation_threshold: float = 5.0, hyperfocus_multiplier: float = 2.5):
        self.switch_penalty = context_switch_penalty
        self.activation_threshold = activation_threshold
        self.hyperfocus_mult = hyperfocus_multiplier

    def simulate(self, profile_name: str, config: Dict[str, Any], steps: int = 20) -> Dict[str, Any]:
        """
        Simula el procesamiento de tareas bajo diferentes perfiles de atención.
        """
        random.seed(42)  # Determinismo
        tasks = ["Task_A", "Task_B", "Task_C", "Task_D"]
        current_task_idx = 0
        active_time = 0.0
        total_work = 0.0
        total_overhead = 0.0
        
        state_history = []
        in_hyperfocus = False
        hyperfocus_timer = 0
        
        # Parámetros del perfil
        switch_probability = config.get("switch_probability", 0.1)
        activation_success_rate = config.get("activation_success_rate", 0.9)
        hyperfocus_probability = config.get("hyperfocus_probability", 0.05)

        for step in range(steps):
            # 1. Intento de activación (vencer la inercia inicial/disfunción ejecutiva)
            if not in_hyperfocus and random.random() > activation_success_rate:
                # Fallo de activación: Procrastinación (Anergia)
                total_overhead += self.activation_threshold
                state_history.append("░") # Inactivo/Fricción
                continue

            # 2. Decisión de Context-Switching (Traspaso de atención / TDAH Thrashing)
            if not in_hyperfocus and random.random() < switch_probability:
                # Cambio de contexto: Penalización por recarga del buffer (Anergia)
                current_task_idx = (current_task_idx + 1) % len(tasks)
                total_overhead += self.switch_penalty
                state_history.append("⇄") # Cambio de contexto
                continue

            # 3. Disparo de Hiperenfoque (Resonancia dopaminérgica)
            if not in_hyperfocus and random.random() < hyperfocus_probability:
                in_hyperfocus = True
                hyperfocus_timer = random.randint(3, 6)

            # 4. Fase de Ejecución de Trabajo (Exergía)
            if in_hyperfocus:
                # Trabajo acelerado por hiperenfoque
                work_done = 1.0 * self.hyperfocus_mult
                total_work += work_done
                state_history.append("█") # Hiperenfoque
                hyperfocus_timer -= 1
                if hyperfocus_timer <= 0:
                    in_hyperfocus = False
            else:
                # Trabajo nominal
                work_done = 1.0
                total_work += work_done
                state_history.append("▄") # Trabajo nominal

        total_energy = total_work + total_overhead
        efficiency = total_work / total_energy if total_energy > 0 else 0.0

        return {
            "profile": profile_name,
            "work": total_work,
            "overhead": total_overhead,
            "efficiency": efficiency,
            "history": "".join(state_history)
        }

def run_simulation():
    # 1. Perfil Neurotípico:
    # - Baja probabilidad de cambio aleatorio de contexto.
    # - Alta tasa de activación de tareas.
    # - Baja probabilidad de hiperenfoque profundo.
    config_typical = {
        "switch_probability": 0.10,
        "activation_success_rate": 0.90,
        "hyperfocus_probability": 0.05
    }

    # 2. Perfil TDAH sin regular:
    # - Alta probabilidad de context-switching (atención dispersa / CPU thrashing).
    # - Baja tasa de activación de tareas (alta fricción estática / disfunción ejecutiva).
    # - Alta probabilidad de hiperenfoque descontrolado una vez superada la barrera.
    config_tdah_raw = {
        "switch_probability": 0.45,
        "activation_success_rate": 0.40,
        "hyperfocus_probability": 0.25
    }

    # 3. Perfil TDAH Anclado (C5-REAL / Divergence-Anchor-OMEGA):
    # - Uso de estructuras físicas externas para mitigar la disfunción (linter, scripts, git sentinels).
    # - Probabilidad de switch reducida mediante bloques de tiempo ininterrumpidos.
    # - Activación garantizada por workflows automáticos (reducción de fricción de inicio).
    # - Aprovechamiento regulado del hiperenfoque.
    config_tdah_anchored = {
        "switch_probability": 0.15,
        "activation_success_rate": 0.85,
        "hyperfocus_probability": 0.20
    }

    sim = TDAHSimulator()
    steps = 30

    res_typical = sim.simulate("Neurotípico Nominal", config_typical, steps)
    res_tdah_raw = sim.simulate("TDAH Sin Filtrar", config_tdah_raw, steps)
    res_tdah_anchored = sim.simulate("TDAH Anclado (C5)", config_tdah_anchored, steps)

    print("=" * 85)
    print(" TDAH COGNITIVE THRASHING & EXERGY SIMULATOR (C5-REAL)")
    print("=" * 85)
    print(f"{'Perfil de Ejecución':<25} | {'Trabajo (X)':<12} | {'Anergia (A)':<12} | {'Eficiencia':<10} | {'Traza de Atención'}")
    print("-" * 85)
    for r in [res_typical, res_tdah_raw, res_tdah_anchored]:
        print(f"{r['profile']:<25} | {r['work']:<12.1f} | {r['overhead']:<12.1f} | {r['efficiency']:<10.2%} | {r['history']}")
    print("=" * 85)
    print("Glosario de Traza:")
    print("  ▄ : Trabajo Nominal (Exergía estándar)")
    print("  █ : Hiperenfoque (Exergía concentrada x2.5)")
    print("  ░ : Fricción Estática / Procrastinación (Anergia por fallo de activación)")
    print("  ⇄ : Context-Switch / Dispersión (Anergia por cambio de contexto)")
    print("=" * 85)

if __name__ == "__main__":
    run_simulation()
