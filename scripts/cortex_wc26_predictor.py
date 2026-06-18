import random
import json
import hashlib
from typing import List, Dict

# C5-REAL GLOBAL EXERGY ENGINE (48 TEAMS)
# Exergy-weighted Monte Carlo Bracket Solver

c5_global_exergy_48 = {
    "France": 0.96, "Spain": 0.94, "England": 0.93, "Brazil": 0.92,
    "Argentina": 0.91, "Portugal": 0.90, "Germany": 0.89, "Netherlands": 0.88,
    "Belgium": 0.86, "Italy": 0.85, "Croatia": 0.84, "Uruguay": 0.84,
    "USA": 0.83, "Mexico": 0.82, "Canada": 0.80, "Morocco": 0.82,
    "Senegal": 0.81, "Japan": 0.83, "South Korea": 0.82, "Iran": 0.79,
    "Switzerland": 0.80, "Denmark": 0.82, "Austria": 0.81, "Colombia": 0.83,
    "Ecuador": 0.80, "Chile": 0.78, "Peru": 0.77, "Nigeria": 0.80,
    "Ghana": 0.78, "Cameroon": 0.77, "Algeria": 0.79, "Tunisia": 0.76,
    "Egypt": 0.78, "Serbia": 0.81, "Poland": 0.80, "Ukraine": 0.79,
    "Turkey": 0.80, "Czechia": 0.79, "Scotland": 0.78, "Australia": 0.78,
    "New Zealand": 0.73, "Saudi Arabia": 0.77, "Qatar": 0.75, "South Africa": 0.76,
    "Uzbekistan": 0.74, "Costa Rica": 0.74, "Panama": 0.73, "Jamaica": 0.74,
    "Paraguay": 0.78, "Venezuela": 0.77, "Jordan": 0.72,
    "Bosnia": 0.78, "Wales": 0.79, "Ivory Coast": 0.80, "Greece": 0.79, "China": 0.65
}

class TeamNode:
    def __init__(self, name: str):
        self.name = name
        self.base_exergy = c5_global_exergy_48.get(name, 0.75) # Default to 0.75 if missing
        self.current_exergy = self.base_exergy
        self.points = 0
        self.gf = 0
        self.ga = 0
        
    @property
    def gd(self):
        return self.gf - self.ga
        
    def apply_thermal_decay(self, round_depth: int):
        # Teams with higher base exergy resist fatigue better.
        decay_factor = 0.05 * (1.0 - self.base_exergy) * round_depth
        self.current_exergy = self.base_exergy * (1.0 - decay_factor)

class ExergyBracketEngine:
    def __init__(self):
        self.volatility = 0.08 # Reduced noise to let structural exergy dictate the DAG
        self.groups = self._init_groups()

    def _init_groups(self) -> Dict[str, List[TeamNode]]:
        return {
            "A": [TeamNode("Mexico"), TeamNode("Czechia"), TeamNode("South Africa"), TeamNode("South Korea")],
            "B": [TeamNode("Canada"), TeamNode("Switzerland"), TeamNode("Qatar"), TeamNode("Bosnia")],
            "C": [TeamNode("USA"), TeamNode("Colombia"), TeamNode("Uzbekistan"), TeamNode("Ghana")],
            "D": [TeamNode("Argentina"), TeamNode("Denmark"), TeamNode("Costa Rica"), TeamNode("Saudi Arabia")],
            "E": [TeamNode("France"), TeamNode("Senegal"), TeamNode("Ecuador"), TeamNode("Australia")],
            "F": [TeamNode("Spain"), TeamNode("Uruguay"), TeamNode("Iran"), TeamNode("New Zealand")],
            "G": [TeamNode("England"), TeamNode("Morocco"), TeamNode("Chile"), TeamNode("Jamaica")],
            "H": [TeamNode("Brazil"), TeamNode("Croatia"), TeamNode("Japan"), TeamNode("Panama")],
            "I": [TeamNode("Belgium"), TeamNode("Wales"), TeamNode("Cameroon"), TeamNode("Iraq")],
            "J": [TeamNode("Portugal"), TeamNode("Serbia"), TeamNode("Algeria"), TeamNode("Venezuela")],
            "K": [TeamNode("Italy"), TeamNode("Germany"), TeamNode("Peru"), TeamNode("China")],
            "L": [TeamNode("Netherlands"), TeamNode("Poland"), TeamNode("Ivory Coast"), TeamNode("Greece")],
        }

    def _poisson_sim(self, t1: TeamNode, t2: TeamNode):
        # Difference in normalized Exergy (0 to 1 scale)
        diff = t1.current_exergy - t2.current_exergy
        exp_g1 = max(0.1, 1.2 + (diff * 2) + random.uniform(-self.volatility, self.volatility))
        exp_g2 = max(0.1, 1.2 - (diff * 2) + random.uniform(-self.volatility, self.volatility))
        
        g1 = int(round(exp_g1 * random.uniform(0.5, 1.5)))
        g2 = int(round(exp_g2 * random.uniform(0.5, 1.5)))
        
        t1.gf += g1
        t1.ga += g2
        t2.gf += g2
        t2.ga += g1
        
        if g1 > g2: t1.points += 3
        elif g2 > g1: t2.points += 3
        else: t1.points += 1; t2.points += 1

    def run_group_stage(self):
        for g_name, teams in self.groups.items():
            self._poisson_sim(teams[0], teams[1])
            self._poisson_sim(teams[0], teams[2])
            self._poisson_sim(teams[0], teams[3])
            self._poisson_sim(teams[1], teams[2])
            self._poisson_sim(teams[1], teams[3])
            self._poisson_sim(teams[2], teams[3])
            teams.sort(key=lambda x: (x.points, x.gd, x.gf), reverse=True)

    def _resolve_knockout(self, t1: TeamNode, t2: TeamNode, round_depth: int) -> TeamNode:
        t1.apply_thermal_decay(round_depth)
        t2.apply_thermal_decay(round_depth)
        
        # Direct Exergy Ratio probability
        prob_1 = (t1.current_exergy / (t1.current_exergy + t2.current_exergy)) + random.uniform(-self.volatility, self.volatility)
        if random.random() < prob_1:
            return t1
        return t2

    def sample_bracket(self):
        self.run_group_stage()
        winners = {g: self.groups[g][0] for g in self.groups}
        runners = {g: self.groups[g][1] for g in self.groups}
        thirds = [self.groups[g][2] for g in self.groups]
        thirds.sort(key=lambda x: (x.points, x.gd, x.gf), reverse=True)
        best_8_thirds = thirds[:8]
        random.shuffle(best_8_thirds)

        r32 = {
            73: self._resolve_knockout(runners["A"], runners["B"], 1),
            74: self._resolve_knockout(winners["E"], best_8_thirds[0], 1),
            75: self._resolve_knockout(winners["F"], runners["C"], 1),
            76: self._resolve_knockout(winners["C"], runners["F"], 1),
            77: self._resolve_knockout(winners["I"], best_8_thirds[1], 1),
            78: self._resolve_knockout(runners["E"], runners["I"], 1),
            79: self._resolve_knockout(winners["A"], best_8_thirds[2], 1),
            80: self._resolve_knockout(winners["L"], best_8_thirds[3], 1),
            81: self._resolve_knockout(winners["D"], best_8_thirds[4], 1),
            82: self._resolve_knockout(winners["G"], best_8_thirds[5], 1),
            83: self._resolve_knockout(runners["K"], runners["L"], 1),
            84: self._resolve_knockout(winners["H"], runners["J"], 1),
            85: self._resolve_knockout(winners["B"], best_8_thirds[6], 1),
            86: self._resolve_knockout(winners["J"], runners["H"], 1),
            87: self._resolve_knockout(winners["K"], best_8_thirds[7], 1),
            88: self._resolve_knockout(runners["D"], runners["G"], 1),
        }

        r16 = {
            89: self._resolve_knockout(r32[74], r32[77], 2),
            90: self._resolve_knockout(r32[73], r32[75], 2),
            91: self._resolve_knockout(r32[76], r32[78], 2),
            92: self._resolve_knockout(r32[79], r32[80], 2),
            93: self._resolve_knockout(r32[83], r32[84], 2),
            94: self._resolve_knockout(r32[81], r32[82], 2),
            95: self._resolve_knockout(r32[86], r32[88], 2),
            96: self._resolve_knockout(r32[85], r32[87], 2),
        }

        qf = {
            97: self._resolve_knockout(r16[89], r16[90], 3),
            98: self._resolve_knockout(r16[93], r16[94], 3),
            99: self._resolve_knockout(r16[91], r16[92], 3),
            100: self._resolve_knockout(r16[95], r16[96], 3),
        }

        sf = {
            101: self._resolve_knockout(qf[97], qf[98], 4),
            102: self._resolve_knockout(qf[99], qf[100], 4),
        }

        final_winner = self._resolve_knockout(sf[101], sf[102], 5)

        return {
            "Champion": final_winner.name,
            "Quarter_Finals": [t.name for t in qf.values()],
        }

if __name__ == "__main__":
    engine = ExergyBracketEngine()
    results = {"Champions": {}, "QuarterFinals": {}}
    iterations = 20000
    
    for _ in range(iterations):
        bracket = engine.sample_bracket()
        champ = bracket["Champion"]
        results["Champions"][champ] = results["Champions"].get(champ, 0) + 1
        for qf_team in bracket["Quarter_Finals"]:
            results["QuarterFinals"][qf_team] = results["QuarterFinals"].get(qf_team, 0) + 1

    champions_pct = {k: f"{(v/iterations)*100:.1f}%" for k,v in sorted(results["Champions"].items(), key=lambda item: item[1], reverse=True)[:5]}
    
    # Calculate % chance of reaching Quarter Finals for Tier S/A teams
    qf_pct = {k: f"{(v/iterations)*100:.1f}%" for k,v in sorted(results["QuarterFinals"].items(), key=lambda item: item[1], reverse=True)[:8]}
    
    output = {
        "Reality_Level": "C5-REAL",
        "Mode": "Exergy-Weighted Monte Carlo (N=20000)",
        "Ultimate_Convergence (Champion)": champions_pct,
        "Structural_Survivability (Reach QF)": qf_pct
    }
    
    print(json.dumps(output, indent=2))
