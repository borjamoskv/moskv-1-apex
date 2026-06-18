const performance = require('perf_hooks').performance;

const BASE_EXERGY = {
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
};

const GROUPS_SEED = {
  "A": ["Mexico", "Czechia", "South Africa", "South Korea"],
  "B": ["Canada", "Switzerland", "Qatar", "Bosnia"],
  "C": ["USA", "Colombia", "Uzbekistan", "Ghana"],
  "D": ["Argentina", "Denmark", "Costa Rica", "Saudi Arabia"],
  "E": ["France", "Senegal", "Ecuador", "Australia"],
  "F": ["Spain", "Uruguay", "Iran", "New Zealand"],
  "G": ["England", "Morocco", "Chile", "Jamaica"],
  "H": ["Brazil", "Croatia", "Japan", "Panama"],
  "I": ["Belgium", "Wales", "Cameroon", "Ivory Coast"],
  "J": ["Portugal", "Serbia", "Algeria", "Venezuela"],
  "K": ["Italy", "Germany", "Peru", "China"],
  "L": ["Netherlands", "Poland", "Austria", "Greece"]
};

function runSingleModelSim(modelType) {
  const sTeams = {};
  Object.keys(BASE_EXERGY).forEach(name => {
    sTeams[name] = {
      name: name,
      baseExergy: BASE_EXERGY[name],
      liveExergy: BASE_EXERGY[name],
      momentum: 0.0,
      volatility: 0.0
    };
  });

  const getTeam = (name) => sTeams[name];
  const sGroups = {};
  for (const [gName, tNames] of Object.entries(GROUPS_SEED)) {
    sGroups[gName] = tNames.map(name => getTeam(name));
  }

  // Run group matches
  for (const [gName, teams] of Object.entries(sGroups)) {
    for (let i = 0; i < teams.length; i++) {
      for (let j = i + 1; j < teams.length; j++) {
        const t1 = teams[i];
        const t2 = teams[j];
        const ea = t1.liveExergy + t1.momentum * 0.2;
        const eb = t2.liveExergy + t2.momentum * 0.2;
        const p = 1 / (1 + Math.exp(-(ea - eb) * 8));
        const win = Math.random() < p;
        
        if (modelType === "apex") {
          if (win) {
            t1.liveExergy += 0.015 * (1.0 - t1.liveExergy);
            t1.momentum += 0.08;
            t2.liveExergy -= 0.02 * t2.liveExergy;
            t2.volatility += 0.05;
          } else {
            t2.liveExergy += 0.015 * (1.0 - t2.liveExergy);
            t2.momentum += 0.08;
            t1.liveExergy -= 0.02 * t1.liveExergy;
            t1.volatility += 0.05;
          }
          t1.momentum *= 0.92; t1.volatility *= 0.95;
          t2.momentum *= 0.92; t2.volatility *= 0.95;
        }
      }
    }
  }

  const winners = {};
  const runners = {};
  const thirds = [];

  for (const [gName, teams] of Object.entries(sGroups)) {
    teams.sort((a, b) => b.liveExergy - a.liveExergy);
    winners[gName] = teams[0];
    runners[gName] = teams[1];
    thirds.push(teams[2]);
  }
  thirds.sort((a, b) => b.liveExergy - a.liveExergy);
  const bestThirds = thirds.slice(0, 8);

  const r32Matches = [];
  const addR32 = (node, t1, t2) => r32Matches.push({ nodeName: node, t1, t2 });
  addR32("M73", runners["A"], runners["B"]);
  addR32("M74", winners["E"], bestThirds[0]);
  addR32("M75", winners["F"], runners["C"]);
  addR32("M76", winners["C"], runners["F"]);
  addR32("M77", winners["I"], bestThirds[1]);
  addR32("M78", runners["E"], runners["I"]);
  addR32("M79", winners["A"], bestThirds[2]);
  addR32("M80", winners["L"], bestThirds[3]);
  addR32("M81", winners["D"], bestThirds[4]);
  addR32("M82", winners["G"], bestThirds[5]);
  addR32("M83", runners["K"], runners["L"]);
  addR32("M84", winners["H"], runners["J"]);
  addR32("M85", winners["B"], bestThirds[6]);
  addR32("M86", winners["J"], runners["H"]);
  addR32("M87", winners["K"], bestThirds[7]);
  addR32("M88", runners["D"], runners["G"]);

  const simKnockout = (t1, t2) => {
    let ea = t1.liveExergy + t1.momentum * 0.2;
    let eb = t2.liveExergy + t2.momentum * 0.2;
    let va = t1.volatility;
    let vb = t2.volatility;

    if (modelType === "poisson") {
      ea = t1.baseExergy; eb = t2.baseExergy;
      va = 0; vb = 0;
    }

    const chaos = (va - vb) * 0.15;
    const p = 1 / (1 + Math.exp(-(ea - eb) * 10));
    const finalProb = Math.max(0.05, Math.min(0.95, p + chaos));
    
    const winner = Math.random() < finalProb ? t1 : t2;
    const loser = winner === t1 ? t2 : t1;

    if (modelType === "apex") {
      winner.liveExergy += 0.015 * (1.0 - winner.liveExergy);
      winner.momentum += 0.08;
      loser.liveExergy -= 0.02 * loser.liveExergy;
      loser.volatility += 0.05;
      winner.momentum *= 0.92; winner.volatility *= 0.95;
      loser.momentum *= 0.92; loser.volatility *= 0.95;
    }

    return { winner, loser };
  };

  const simStage = (pairings) => {
    const res = {};
    pairings.forEach(m => {
      const { winner } = simKnockout(m.t1, m.t2);
      res[m.name || m.nodeName] = winner;
    });
    return res;
  };

  const r32Res = simStage(r32Matches);

  const r16Pairings = [
    { name: "M89", t1: r32Res["M74"], t2: r32Res["M77"] },
    { name: "M90", t1: r32Res["M73"], t2: r32Res["M75"] },
    { name: "M91", t1: r32Res["M76"], t2: r32Res["M78"] },
    { name: "M92", t1: r32Res["M79"], t2: r32Res["M80"] },
    { name: "M93", t1: r32Res["M83"], t2: r32Res["M84"] },
    { name: "M94", t1: r32Res["M81"], t2: r32Res["M82"] },
    { name: "M95", t1: r32Res["M86"], t2: r32Res["M88"] },
    { name: "M96", t1: r32Res["M85"], t2: r32Res["M87"] }
  ];
  const r16Res = simStage(r16Pairings);

  const qfPairings = [
    { name: "M97", t1: r16Res["M89"], t2: r16Res["M90"] },
    { name: "M98", t1: r16Res["M93"], t2: r16Res["M94"] },
    { name: "M99", t1: r16Res["M91"], t2: r16Res["M92"] },
    { name: "M100", t1: r16Res["M95"], t2: r16Res["M96"] }
  ];
  const qfRes = simStage(qfPairings);

  const sfPairings = [
    { name: "M101", t1: qfRes["M97"], t2: qfRes["M98"] },
    { name: "M102", t1: qfRes["M99"], t2: qfRes["M100"] }
  ];
  const sfRes = simStage(sfPairings);

  const { winner: finalWinner } = simKnockout(sfRes["M101"], sfRes["M102"]);
  return finalWinner.name;
}

console.log("\n==========================================");
console.log("🔥 [MOSKV-1] APEX THERMODYNAMIC STRESS TEST 🔥");
console.log("==========================================\n");

const ITERS = 50000;
const models = ["poisson", "apex"];

models.forEach(model => {
  console.log(`[>>] Running ${ITERS.toLocaleString()} simulations for model: [${model.toUpperCase()}]`);
  
  const startMemory = process.memoryUsage().heapUsed;
  const startTime = performance.now();
  
  const champCounts = {};
  
  for (let i = 0; i < ITERS; i++) {
    const champ = runSingleModelSim(model);
    champCounts[champ] = (champCounts[champ] || 0) + 1;
  }
  
  const endTime = performance.now();
  const endMemory = process.memoryUsage().heapUsed;
  const memoryDelta = (endMemory - startMemory) / 1024 / 1024;
  const duration = endTime - startTime;
  
  const sortedChamps = Object.entries(champCounts).sort((a,b) => b[1] - a[1]).slice(0, 5);
  
  console.log(`⏱️ Duration: ${duration.toFixed(2)}ms (${(ITERS / (duration/1000)).toFixed(0)} sims/sec)`);
  console.log(`🧠 Mem Drift: ${memoryDelta.toFixed(2)} MB`);
  console.log(`🏆 Top 5 Champions Divergence:`);
  sortedChamps.forEach(([name, count]) => {
    console.log(`   - ${name}: ${((count / ITERS) * 100).toFixed(2)}%`);
  });
  console.log("------------------------------------------\n");
});
