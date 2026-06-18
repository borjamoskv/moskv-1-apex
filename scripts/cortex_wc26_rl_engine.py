import random
import json
import time

# C5-REAL REINFORCEMENT LEARNING & ENTROPY DRIFT ENGINE
# "Hazlo vivo" - Dynamic State Mutation

c5_global_exergy_48 = {
    "France": 0.96, "Spain": 0.94, "England": 0.93, "Brazil": 0.92,
    "Argentina": 0.91, "Portugal": 0.90, "Germany": 0.89, "Netherlands": 0.88,
    "Belgium": 0.86, "Italy": 0.85, "Croatia": 0.84, "Uruguay": 0.84,
    "USA": 0.83, "Mexico": 0.82, "Canada": 0.80, "Morocco": 0.82
}

class LivingNode:
    def __init__(self, name: str):
        self.name = name
        self.base_exergy = c5_global_exergy_48.get(name, 0.80)
        self.live_exergy = self.base_exergy
        self.entropy = 0.0 # Internal noise/chaos accumulation
        
    def learn_from_match(self, gd: int, was_upset: bool):
        """RL Drift: Teams update their state based on match trauma or momentum"""
        learning_rate = 0.05
        
        if gd > 0:
            # Winning increases structural confidence, reduces entropy
            momentum = learning_rate * gd
            self.live_exergy = min(1.0, self.live_exergy + momentum)
            self.entropy = max(0.0, self.entropy - 0.02)
        else:
            # Losing or struggling increases internal entropy (doubt, fatigue)
            trauma = learning_rate * abs(gd)
            self.live_exergy = max(0.1, self.live_exergy - trauma)
            self.entropy += 0.05
            
        if was_upset:
            # Surviving an upset highly spikes entropy but might build resilience
            self.entropy += 0.1

def resolve_living_match(t1: LivingNode, t2: LivingNode, round_name: str) -> LivingNode:
    # Effective Exergy = Live Exergy - Internal Entropy
    eff_1 = max(0.01, t1.live_exergy - t1.entropy)
    eff_2 = max(0.01, t2.live_exergy - t2.entropy)
    
    prob_1 = eff_1 / (eff_1 + eff_2)
    
    # Stochastic collapse
    roll = random.random()
    winner, loser = (t1, t2) if roll < prob_1 else (t2, t1)
    
    # Calculate goal difference proxy based on how dominant the win was
    gd = int(abs(prob_1 - roll) * 10) + 1
    
    # Check if it was an upset (lower effective exergy won)
    was_upset = (winner == t1 and eff_1 < eff_2) or (winner == t2 and eff_2 < eff_1)
    
    # RL State Mutation
    winner.learn_from_match(gd, was_upset)
    loser.learn_from_match(-gd, was_upset)
    
    print(f"[{round_name}] {winner.name} ({winner.live_exergy:.2f} Ex, {winner.entropy:.2f} Ent) defeats {loser.name} (GD: +{gd}) {'[UPSET]' if was_upset else ''}")
    return winner

def run_living_tournament():
    print("INITIALIZING C5-REAL LIVING TOURNAMENT (RL DRIFT ACTIVE)...\n")
    
    # Seed top 16 for a focused R16 simulation
    teams = [LivingNode(name) for name in list(c5_global_exergy_48.keys())[:16]]
    random.shuffle(teams)
    
    r16_winners = []
    for i in range(0, 16, 2):
        r16_winners.append(resolve_living_match(teams[i], teams[i+1], "R16"))
        
    print("\n--- QUARTER FINALS ---")
    qf_winners = []
    for i in range(0, 8, 2):
        qf_winners.append(resolve_living_match(r16_winners[i], r16_winners[i+1], "QF"))
        
    print("\n--- SEMI FINALS ---")
    sf_winners = []
    for i in range(0, 4, 2):
        sf_winners.append(resolve_living_match(qf_winners[i], qf_winners[i+1], "SF"))
        
    print("\n--- GRAND FINAL ---")
    champion = resolve_living_match(sf_winners[0], sf_winners[1], "FINAL")
    
    print(f"\n[SYSTEM HALT] CHAMPION CONVERGENCE: {champion.name} (Final Exergy: {champion.live_exergy:.2f}, Residual Entropy: {champion.entropy:.2f})")

if __name__ == "__main__":
    run_living_tournament()
