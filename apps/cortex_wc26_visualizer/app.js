// C5-REAL // WORLD CUP 2026 MOVEMENT & RL DRIFT ENGINE
// Absolute Synthesis of Particle Physics and Bayesian State Mutation

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

// --- TEAM NODE CLASS ---
class TeamNode {
  constructor(name) {
    this.name = name;
    this.baseExergy = BASE_EXERGY[name] || 0.75;
    this.liveExergy = this.baseExergy;
    this.momentum = 0.0;
    this.volatility = 0.0;
    this.points = 0;
    this.gf = 0;
    this.ga = 0;
    this.status = "ACTIVE"; // ACTIVE, ELIMINATED, CHAMPION
    
    // Core Learning Vectors
    this.momentum = 0.0;
    this.volatility = 0.0;
    
    // Physics parameters for canvas particle
    this.x = Math.random() * 400 + 50;
    this.y = Math.random() * 400 + 50;
    this.vx = (Math.random() - 0.5) * 0.8;
    this.vy = (Math.random() - 0.5) * 0.8;
    this.radius = 6 + this.baseExergy * 8;
    this.mass = this.radius;
    
    // Graphic target coordinates
    this.targetX = null;
    this.targetY = null;
    this.pulse = 0;
  }

  get gd() {
    return this.gf - this.ga;
  }

  get entropy() {
    return this.volatility;
  }

  set entropy(val) {
    this.volatility = val;
  }

  reset() {
    this.liveExergy = this.baseExergy;
    this.momentum = 0.0;
    this.volatility = 0.0;
    this.points = 0;
    this.gf = 0;
    this.ga = 0;
    this.status = "ACTIVE";
    this.momentum = 0.0;
    this.volatility = 0.0;
    this.x = Math.random() * 400 + 50;
    this.y = Math.random() * 400 + 50;
    this.vx = (Math.random() - 0.5) * 0.8;
    this.vy = (Math.random() - 0.5) * 0.8;
    this.targetX = null;
    this.targetY = null;
  }

  applyThermalDecay(roundDepth) {
    // High base exergy teams decay slower under physical load (fatiga)
    const decayFactor = 0.04 * (1.0 - this.baseExergy) * roundDepth;
    this.liveExergy = Math.max(0.2, this.baseExergy * (1.0 - decayFactor));
  }

  learnFromMatch(gd, wasUpset, lr, upsetPressure) {
    const won = gd > 0;
    if (won) {
      this.liveExergy += 0.015 * (1.0 - this.liveExergy);
      this.momentum = (this.momentum || 0) + 0.08;
    } else {
      this.liveExergy -= 0.02 * this.liveExergy;
      this.volatility = (this.volatility || 0) + 0.05;
    }

    this.momentum *= 0.92;
    this.volatility *= 0.95;

    // clamp
    this.liveExergy = Math.max(0.2, Math.min(0.99, this.liveExergy));

    if (wasUpset) {
      this.volatility += upsetPressure * 0.5;
    }
  }
}

// --- SIMULATOR CONTROLLER ---
class TournamentSimulator {
  constructor() {
    this.teams = {};
    Object.keys(BASE_EXERGY).forEach(name => {
      this.teams[name] = new TeamNode(name);
    });

    this.groups = {};
    this.volatility = 0.08;
    this.lr = 0.05;
    this.upsetPressure = 0.10;
    this.speed = 500;
    
    this.isPlaying = false;
    this.currentMatchIndex = 0;
    this.phase = "GROUP_STAGE"; // GROUP_STAGE, R32, R16, QF, SF, FINAL, COMPLETE
    this.matches = [];
    
    // Bracket results storage
    this.bracketData = {
      groups: {},
      r32: [],
      r16: [],
      qf: [],
      sf: [],
      final: null,
      champion: null
    };

    this.activeClashingNodes = null; // References to currently clashing team particles
    this.clashTimer = 0;
    this.clashDuration = 30; // frames of collision animation
    
    this.initGroups();
    this.generateGroupMatches();
  }

  initGroups() {
    this.groups = {};
    for (const [gName, tNames] of Object.entries(GROUPS_SEED)) {
      this.groups[gName] = tNames.map(name => this.teams[name]);
    }
  }

  generateGroupMatches() {
    this.matches = [];
    this.currentMatchIndex = 0;
    
    // standard round-robin for each group
    for (const [gName, teams] of Object.entries(this.groups)) {
      this.matches.push({ type: "GROUP", group: gName, t1: teams[0], t2: teams[1] });
      this.matches.push({ type: "GROUP", group: gName, t1: teams[2], t2: teams[3] });
      this.matches.push({ type: "GROUP", group: gName, t1: teams[0], t2: teams[2] });
      this.matches.push({ type: "GROUP", group: gName, t1: teams[1], t2: teams[3] });
      this.matches.push({ type: "GROUP", group: gName, t1: teams[0], t2: teams[3] });
      this.matches.push({ type: "GROUP", group: gName, t1: teams[1], t2: teams[2] });
    }
  }

  calculateShannonEntropy() {
    const activeTeams = Object.values(this.teams).filter(t => t.status === "ACTIVE");
    if (activeTeams.length === 0) return 0.00;
    const sumEx = activeTeams.reduce((acc, t) => acc + t.liveExergy, 0);
    let entropy = 0;
    activeTeams.forEach(t => {
      const p = t.liveExergy / sumEx;
      entropy -= p * Math.log2(p);
    });
    // Normalise to 0-1 range based on number of active teams
    return (entropy / Math.log2(activeTeams.length)).toFixed(2);
  }

  reset() {
    this.isPlaying = false;
    this.currentMatchIndex = 0;
    this.phase = "GROUP_STAGE";
    Object.values(this.teams).forEach(t => t.reset());
    this.initGroups();
    this.generateGroupMatches();
    this.activeClashingNodes = null;
    this.clashTimer = 0;
    
    this.bracketData = {
      groups: {},
      r32: [],
      r16: [],
      qf: [],
      sf: [],
      final: null,
      champion: null
    };

    // Update UI elements
    document.getElementById("tel-state").className = "value state-idle";
    document.getElementById("tel-state").innerText = "IDLE";
    document.getElementById("tel-phase").innerText = "INITIALIZED";
    document.getElementById("tel-entropy").innerText = "0.73";
    document.getElementById("tel-nodes").innerText = "48 / 48";
    
    const log = document.getElementById("terminal-log");
    log.innerHTML = `<div class="log-line system-line">[SYSTEM] APEX Kernel online. State reset. Ready.</div>`;
    
    this.renderBracket();
    this.updateLeaderboard();
  }

  logMessage(msg, type = "system") {
    const log = document.getElementById("terminal-log");
    const line = document.createElement("div");
    line.className = `log-line ${type}-line`;
    line.innerHTML = msg;
    log.appendChild(line);
    log.scrollTop = log.scrollHeight;
  }

  simulatePoisson(t1, t2) {
    const ea = t1.liveExergy + (t1.momentum || 0) * 0.2;
    const eb = t2.liveExergy + (t2.momentum || 0) * 0.2;
    const diff = ea - eb;
    
    const va = t1.volatility || 0;
    const vb = t2.volatility || 0;
    
    // Bivariate Poisson expected goals with volatility jitter
    const jitter1 = (Math.random() - 0.5) * (this.volatility + va) * 2;
    const jitter2 = (Math.random() - 0.5) * (this.volatility + vb) * 2;
    
    const expG1 = Math.max(0.1, 1.3 + (diff * 2.5) + jitter1);
    const expG2 = Math.max(0.1, 1.3 - (diff * 2.5) + jitter2);
    
    const g1 = Math.round(expG1 * (0.6 + Math.random() * 0.8));
    const g2 = Math.round(expG2 * (0.6 + Math.random() * 0.8));
    
    t1.gf += g1;
    t1.ga += g2;
    t2.gf += g2;
    t2.ga += g1;
    
    let outcome = 0; // 1 = t1 wins, -1 = t2 wins, 0 = draw
    if (g1 > g2) {
      t1.points += 3;
      outcome = 1;
    } else if (g2 > g1) {
      t2.points += 3;
      outcome = -1;
    } else {
      t1.points += 1;
      t2.points += 1;
    }
    
    return { g1, g2, outcome };
  }

  simulateKnockoutMatch(t1, t2, roundDepth) {
    t1.applyThermalDecay(roundDepth);
    t2.applyThermalDecay(roundDepth);
    
    const ea = t1.liveExergy + (t1.momentum || 0) * 0.2;
    const eb = t2.liveExergy + (t2.momentum || 0) * 0.2;
    
    const va = t1.volatility || 0;
    const vb = t2.volatility || 0;
    
    const chaos = (va - vb) * 0.15;
    
    let p = 1 / (1 + Math.exp(-(ea - eb) * 10));
    const finalProb = Math.max(0.05, Math.min(0.95, p + chaos));
    
    const roll = Math.random();
    const winner = roll < finalProb ? t1 : t2;
    const loser = winner === t1 ? t2 : t1;
    
    const isUpset = (winner === t1 && t1.baseExergy < t2.baseExergy) || (winner === t2 && t2.baseExergy < t1.baseExergy);
    
    winner.learnFromMatch(true);
    loser.learnFromMatch(false);
    
    loser.status = "ELIMINATED";
    
    const gd = Math.max(1, Math.round(Math.abs(finalProb - roll) * 8));
    const g1 = winner === t1 ? gd : 0;
    const g2 = winner === t2 ? gd : 0;
    
    return { winner, loser, g1, g2, isUpset };
  }

  resolveThirdPlaces() {
    const thirds = [];
    for (const [gName, teams] of Object.entries(this.groups)) {
      // Sort each group table properly: points -> gd -> gf -> liveExergy
      teams.sort((a, b) => {
        if (b.points !== a.points) return b.points - a.points;
        if (b.gd !== a.gd) return b.gd - a.gd;
        if (b.gf !== a.gf) return b.gf - a.gf;
        return b.liveExergy - a.liveExergy;
      });
      thirds.push(teams[2]);
    }
    
    // Sort thirds pool
    thirds.sort((a, b) => {
      if (b.points !== a.points) return b.points - a.points;
      if (b.gd !== a.gd) return b.gd - a.gd;
      if (b.gf !== a.gf) return b.gf - a.gf;
      return b.liveExergy - a.liveExergy;
    });
    
    // Return best 8 third place teams
    return thirds.slice(0, 8);
  }

  generateKnockoutDAG() {
    this.logMessage("[SYSTEM] Phase collapse: Group Stage completed. Building Round of 32 DAG...", "system");
    
    const winners = {};
    const runners = {};
    for (const [gName, teams] of Object.entries(this.groups)) {
      winners[gName] = teams[0];
      runners[gName] = teams[1];
      // Eliminate bottom team of each group
      teams[3].status = "ELIMINATED";
    }

    const bestThirds = this.resolveThirdPlaces();
    // Eliminate remaining bottom thirds
    Object.values(this.teams).forEach(t => {
      if (t.status === "ACTIVE" && !Object.values(winners).includes(t) && !Object.values(runners).includes(t) && !bestThirds.includes(t)) {
        t.status = "ELIMINATED";
      }
    });

    // Seed Round of 32 Matches based on FIFA 48-team layout
    this.matches = [];
    this.currentMatchIndex = 0;
    this.phase = "R32";
    
    // Define 16 pairings
    const pairings = [
      { name: "M73", t1: runners["A"], t2: runners["B"] },
      { name: "M74", t1: winners["E"], t2: bestThirds[0] },
      { name: "M75", t1: winners["F"], t2: runners["C"] },
      { name: "M76", t1: winners["C"], t2: runners["F"] },
      { name: "M77", t1: winners["I"], t2: bestThirds[1] },
      { name: "M78", t1: runners["E"], t2: runners["I"] },
      { name: "M79", t1: winners["A"], t2: bestThirds[2] },
      { name: "M80", t1: winners["L"], t2: bestThirds[3] },
      { name: "M81", t1: winners["D"], t2: bestThirds[4] },
      { name: "M82", t1: winners["G"], t2: bestThirds[5] },
      { name: "M83", t1: runners["K"], t2: runners["L"] },
      { name: "M84", t1: winners["H"], t2: runners["J"] },
      { name: "M85", t1: winners["B"], t2: bestThirds[6] },
      { name: "M86", t1: winners["J"], t2: runners["H"] },
      { name: "M87", t1: winners["K"], t2: bestThirds[7] },
      { name: "M88", t1: runners["D"], t2: runners["G"] }
    ];

    pairings.forEach(p => {
      this.matches.push({ type: "R32", nodeName: p.name, t1: p.t1, t2: p.t2 });
    });

    this.renderBracket();
  }

  generateNextKnockoutStage(prevWinners, nextStageName, depth) {
    this.logMessage(`[SYSTEM] Phase collapse: Stage ${this.phase} complete. Building ${nextStageName} nodes...`, "system");
    this.matches = [];
    this.currentMatchIndex = 0;
    this.phase = nextStageName;

    let pairings = [];
    if (nextStageName === "R16") {
      // Mapping R32 match winners to R16 slots
      pairings = [
        { name: "M89", t1: prevWinners["M74"], t2: prevWinners["M77"] },
        { name: "M90", t1: prevWinners["M73"], t2: prevWinners["M75"] },
        { name: "M91", t1: prevWinners["M76"], t2: prevWinners["M78"] },
        { name: "M92", t1: prevWinners["M79"], t2: prevWinners["M80"] },
        { name: "M93", t1: prevWinners["M83"], t2: prevWinners["M84"] },
        { name: "M94", t1: prevWinners["M81"], t2: prevWinners["M82"] },
        { name: "M95", t1: prevWinners["M86"], t2: prevWinners["M88"] },
        { name: "M96", t1: prevWinners["M85"], t2: prevWinners["M87"] }
      ];
    } else if (nextStageName === "QF") {
      pairings = [
        { name: "M97", t1: prevWinners["M89"], t2: prevWinners["M90"] },
        { name: "M98", t1: prevWinners["M93"], t2: prevWinners["M94"] },
        { name: "M99", t1: prevWinners["M91"], t2: prevWinners["M92"] },
        { name: "M100", t1: prevWinners["M95"], t2: prevWinners["M96"] }
      ];
    } else if (nextStageName === "SF") {
      pairings = [
        { name: "M101", t1: prevWinners["M97"], t2: prevWinners["M98"] },
        { name: "M102", t1: prevWinners["M99"], t2: prevWinners["M100"] }
      ];
    } else if (nextStageName === "FINAL") {
      pairings = [
        { name: "M103", t1: prevWinners["M101"], t2: prevWinners["M102"] }
      ];
    }

    pairings.forEach(p => {
      this.matches.push({ type: nextStageName, nodeName: p.name, t1: p.t1, t2: p.t2 });
    });

    this.renderBracket();
  }

  step() {
    if (this.currentMatchIndex >= this.matches.length) {
      this.resolveStageTransition();
      return;
    }

    const match = this.matches[this.currentMatchIndex];
    
    // Set active clashing nodes for physics simulation
    this.activeClashingNodes = [match.t1, match.t2];
    this.clashTimer = this.clashDuration;

    let msg = "";
    let logType = "match";

    if (match.type === "GROUP") {
      const { g1, g2, outcome } = this.simulatePoisson(match.t1, match.t2);
      
      const gd = g1 - g2;
      const isUpset = (gd > 0 && match.t1.baseExergy < match.t2.baseExergy) || (gd < 0 && match.t2.baseExergy < match.t1.baseExergy);
      
      if (outcome === 1) {
        match.t1.learnFromMatch(true);
        match.t2.learnFromMatch(false);
      } else if (outcome === -1) {
        match.t2.learnFromMatch(true);
        match.t1.learnFromMatch(false);
      } else {
        match.t1.momentum *= 0.92;
        match.t1.volatility *= 0.95;
        match.t2.momentum *= 0.92;
        match.t2.volatility *= 0.95;
      }
      
      match.g1 = g1;
      match.g2 = g2;
      
      msg = `[GROUP ${match.group}] ${match.t1.name} <span class="score">${g1}–${g2}</span> ${match.t2.name}`;
      if (isUpset) {
        msg += ` <span class="upset-line">[UPSET COLLAPSE]</span>`;
        logType = "upset";
      }
    } else {
      // Knockout matches
      const depths = { "R32": 1, "R16": 2, "QF": 3, "SF": 4, "FINAL": 5 };
      const depth = depths[match.type] || 1;
      
      const { winner, loser, g1, g2, isUpset } = this.simulateKnockoutMatch(match.t1, match.t2, depth);
      
      match.winner = winner;
      match.loser = loser;
      match.g1 = g1;
      match.g2 = g2;
      
      msg = `[${match.type}] ${winner.name} <span class="score">${g1}–${g2}</span> ${loser.name}`;
      if (isUpset) {
        msg += ` <span class="upset-line">[UPSET NODE TRIGGER]</span>`;
        logType = "upset";
      }
    }

    this.logMessage(msg, logType);
    this.currentMatchIndex++;
    
    // Update Telemetry Header info
    document.getElementById("tel-phase").innerText = `${this.phase} (${this.currentMatchIndex}/${this.matches.length})`;
    document.getElementById("tel-entropy").innerText = this.calculateShannonEntropy();
    const activeCount = Object.values(this.teams).filter(t => t.status === "ACTIVE").length;
    document.getElementById("tel-nodes").innerText = `${activeCount} / 48`;

    this.updateLeaderboard();
    this.renderBracket();
  }

  resolveStageTransition() {
    if (this.phase === "GROUP_STAGE") {
      this.bracketData.groups = JSON.parse(JSON.stringify(this.groups)); // snapshot
      this.generateKnockoutDAG();
    } else {
      const prevWinners = {};
      this.matches.forEach(m => {
        prevWinners[m.nodeName] = m.winner;
      });

      this.bracketData[this.phase.toLowerCase()] = this.matches;

      if (this.phase === "R32") {
        this.generateNextKnockoutStage(prevWinners, "R16", 2);
      } else if (this.phase === "R16") {
        this.generateNextKnockoutStage(prevWinners, "QF", 3);
      } else if (this.phase === "QF") {
        this.generateNextKnockoutStage(prevWinners, "SF", 4);
      } else if (this.phase === "SF") {
        this.generateNextKnockoutStage(prevWinners, "FINAL", 5);
      } else if (this.phase === "FINAL") {
        this.phase = "COMPLETE";
        const champion = this.matches[0].winner;
        champion.status = "CHAMPION";
        this.bracketData.champion = champion;
        
        this.isPlaying = false;
        document.getElementById("btn-play").innerText = "PLAY SIM";
        document.getElementById("tel-state").className = "value state-complete";
        document.getElementById("tel-state").innerText = "COMPLETE";
        
        this.logMessage(`\n🏆 [GRAND COLLAPSE] CHAMPION CONVERGENCE ATTAINED: ${champion.name.toUpperCase()} 🏆<br>` +
                        `Final Exergy Vector: ${champion.liveExergy.toFixed(3)} // Momentum: ${champion.momentum.toFixed(3)}`, "champion");
        
        this.updateLeaderboard();
        this.renderBracket();
      }
    }
  }

  play() {
    if (this.phase === "COMPLETE") {
      this.reset();
    }
    this.isPlaying = true;
    document.getElementById("tel-state").className = "value state-running";
    document.getElementById("tel-state").innerText = "SIMULATING";
    document.getElementById("btn-play").innerText = "PAUSE SIM";
    this.runLoop();
  }

  pause() {
    this.isPlaying = false;
    document.getElementById("tel-state").className = "value state-idle";
    document.getElementById("tel-state").innerText = "PAUSED";
    document.getElementById("btn-play").innerText = "PLAY SIM";
  }

  runLoop() {
    if (!this.isPlaying) return;
    this.step();
    if (this.phase !== "COMPLETE") {
      setTimeout(() => this.runLoop(), this.speed);
    }
  }

  updateLeaderboard() {
    const tbody = document.getElementById("leaderboard-body");
    tbody.innerHTML = "";
    
    const sorted = Object.values(this.teams).sort((a, b) => {
      if (a.status === "CHAMPION") return -1;
      if (b.status === "CHAMPION") return 1;
      if (a.status === "ACTIVE" && b.status === "ELIMINATED") return -1;
      if (b.status === "ACTIVE" && a.status === "ELIMINATED") return 1;
      return b.liveExergy - a.liveExergy;
    });

    sorted.forEach(t => {
      const tr = document.createElement("tr");
      
      let statusBadge = `<span class="badge-status status-active">ACTIVE</span>`;
      if (t.status === "ELIMINATED") {
        statusBadge = `<span class="badge-status status-eliminated">ELIM</span>`;
      } else if (t.status === "CHAMPION") {
        statusBadge = `<span class="badge-status status-champion">CHAMP</span>`;
      }

      tr.innerHTML = `
        <td class="leaderboard-name-cell">${t.name}</td>
        <td align="right" class="leaderboard-exergy-cell">${t.liveExergy.toFixed(3)}</td>
        <td align="right" class="leaderboard-entropy-cell">${(t.volatility || 0).toFixed(2)}</td>
        <td align="center">${statusBadge}</td>
      `;
      tbody.appendChild(tr);
    });
  }

  runBenchmark() {
    this.logMessage("[SYSTEM] Initializing AI Model Benchmark Engine...", "system");
    
    // 1. Generate reference "real results" (ground truth)
    const gtSim = new TournamentSimulator();
    gtSim.volatility = 0.08;
    gtSim.lr = 0.05;
    gtSim.upsetPressure = 0.10;
    while (gtSim.phase !== "COMPLETE") {
      gtSim.step();
    }
    const gt = gtSim.bracketData; // Has R32, R16, QF, SF, Final, Champion

    // Find actual upsets in ground truth
    const gtUpsets = [];
    const collectGtMatches = (matches) => {
      matches.forEach(m => {
        const diff = Math.abs(m.t1.baseExergy - m.t2.baseExergy);
        if (diff > 0.1 && m.winner.baseExergy < Math.max(m.t1.baseExergy, m.t2.baseExergy)) {
          gtUpsets.push({ nodeName: m.nodeName, winnerName: m.winner.name });
        }
      });
    };
    collectGtMatches(gt.r32);
    collectGtMatches(gt.r16);
    collectGtMatches(gt.qf);
    collectGtMatches(gt.sf);
    collectGtMatches([gt.final]);

    // 2. Define competitors
    const models = [
      { name: "MOSKV-1 APEX (C5-REAL)", type: "apex", desc: "Adaptive Exergy + RL Momentum" },
      { name: "Baseline Poisson ELO", type: "poisson", desc: "Static ELO probability" },
      { name: "Conservative LLM (Static)", type: "conservative", desc: "Top Tier favoritism" },
      { name: "High-Entropy Randomizer", type: "random", desc: "Flat probability distributions" }
    ];

    const results = [];

    // 3. Run simulations for each model
    models.forEach(model => {
      let totalAccuracy = 0;
      let totalEntropy = 0;
      let totalUpsetCalib = 0;
      const nRuns = 150;

      for (let run = 0; run < nRuns; run++) {
        // Run a simulation for this model
        const simData = this.runSingleModelSim(model.type, gt);
        
        // Calculate Accuracy (number of correct match winners out of 31 knockout nodes)
        let correct = 0;
        let matchCount = 0;
        let upsetCorrect = 0;

        const compareStages = (stageName, gtStage) => {
          simData[stageName].forEach((m, idx) => {
            const gtMatch = gtStage[idx];
            if (gtMatch && m.winner.name === gtMatch.winner.name) {
              correct++;
              // Check if it was an upset in ground truth
              const isGtUpset = gtUpsets.some(u => u.nodeName === gtMatch.nodeName);
              if (isGtUpset) upsetCorrect++;
            }
            matchCount++;
          });
        };

        compareStages("r32", gt.r32);
        compareStages("r16", gt.r16);
        compareStages("qf", gt.qf);
        compareStages("sf", gt.sf);
        // Final
        if (simData.final && gt.final && simData.final.winner.name === gt.final.winner.name) {
          correct++;
          const isGtUpset = gtUpsets.some(u => u.nodeName === gt.final.nodeName);
          if (isGtUpset) upsetCorrect++;
        }
        matchCount++;

        const acc = correct / matchCount;
        totalAccuracy += acc;

        // Calculate predictive entropy (simulated)
        const avgProb = simData.avgProb || 0.7;
        const shannon = - (avgProb * Math.log2(avgProb) + (1 - avgProb) * Math.log2(1 - avgProb));
        totalEntropy += isNaN(shannon) ? 0 : shannon;

        if (gtUpsets.length > 0) {
          totalUpsetCalib += (upsetCorrect / gtUpsets.length);
        } else {
          totalUpsetCalib += acc; // fallback
        }
      }

      const avgAcc = totalAccuracy / nRuns;
      const avgEnt = totalEntropy / nRuns;
      const avgUpset = totalUpsetCalib / nRuns;

      // Kaggle Score formula: Accuracy * 100 - Entropy * 15 + UpsetCalibration * 25
      const score = (avgAcc * 100) - (avgEnt * 15) + (avgUpset * 25);

      results.push({
        name: model.name,
        accuracy: `${(avgAcc * 100).toFixed(1)}%`,
        entropy: avgEnt.toFixed(2),
        upsets: `${(avgUpset * 100).toFixed(1)}%`,
        score: score.toFixed(1)
      });
    });

    // Sort results by Score descending
    results.sort((a, b) => b.score - a.score);

    // Render to DOM
    const tbody = document.getElementById("benchmark-body");
    tbody.innerHTML = "";
    results.forEach(res => {
      const tr = document.createElement("tr");
      tr.innerHTML = `
        <td class="leaderboard-name-cell">${res.name}</td>
        <td align="right">${res.accuracy}</td>
        <td align="right" class="leaderboard-entropy-cell">${res.entropy}</td>
        <td align="right">${res.upsets}</td>
        <td align="right" class="leaderboard-exergy-cell">${res.score}</td>
      `;
      tbody.appendChild(tr);
    });

    this.logMessage("[SYSTEM] AI Model Benchmark complete. Leaderboard updated.", "system");
  }

  runSingleModelSim(modelType, gt) {
    const sTeams = {};
    Object.keys(BASE_EXERGY).forEach(name => {
      sTeams[name] = {
        name: name,
        baseExergy: BASE_EXERGY[name],
        liveExergy: BASE_EXERGY[name],
        momentum: 0.0,
        volatility: 0.0,
        status: "ACTIVE"
      };
    });

    const getTeam = (name) => sTeams[name];
    
    // Simulate Group Stage: resolve winners
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
          const roll = Math.random();
          const win = roll < p;
          
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

    // Sort group tables
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

    // Setup R32 match pairings matching GT nodes
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

    let sumProbs = 0;
    let probCounts = 0;

    const simKnockout = (t1, t2) => {
      let ea = t1.liveExergy + t1.momentum * 0.2;
      let eb = t2.liveExergy + t2.momentum * 0.2;

      let va = t1.volatility;
      let vb = t2.volatility;

      if (modelType === "poisson") {
        ea = t1.baseExergy;
        eb = t2.baseExergy;
        va = 0; vb = 0;
      } else if (modelType === "conservative") {
        const topTiers = ["France", "Spain", "England", "Brazil", "Argentina", "Portugal"];
        ea = t1.baseExergy + (topTiers.includes(t1.name) ? 0.25 : 0);
        eb = t2.baseExergy + (topTiers.includes(t2.name) ? 0.25 : 0);
        va = 0; vb = 0;
      } else if (modelType === "random") {
        ea = 0.5; eb = 0.5; va = 0; vb = 0;
      }

      const chaos = (va - vb) * 0.15;
      const p = 1 / (1 + Math.exp(-(ea - eb) * 10));
      const finalProb = Math.max(0.05, Math.min(0.95, p + chaos));
      
      sumProbs += finalProb;
      probCounts++;

      const roll = Math.random();
      const winner = roll < finalProb ? t1 : t2;
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

    // Simulate R32 -> resolve winners
    const r32Res = {};
    const r32Out = r32Matches.map(m => {
      const { winner, loser } = simKnockout(m.t1, m.t2);
      r32Res[m.nodeName] = winner;
      return { nodeName: m.nodeName, winner, loser };
    });

    // Simulate R16
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
    const r16Res = {};
    const r16Out = r16Pairings.map(m => {
      const { winner, loser } = simKnockout(m.t1, m.t2);
      r16Res[m.name] = winner;
      return { nodeName: m.name, winner, loser };
    });

    // Simulate QF
    const qfPairings = [
      { name: "M97", t1: r16Res["M89"], t2: r16Res["M90"] },
      { name: "M98", t1: r16Res["M93"], t2: r16Res["M94"] },
      { name: "M99", t1: r16Res["M91"], t2: r16Res["M92"] },
      { name: "M100", t1: r16Res["M95"], t2: r16Res["M96"] }
    ];
    const qfRes = {};
    const qfOut = qfPairings.map(m => {
      const { winner, loser } = simKnockout(m.t1, m.t2);
      qfRes[m.name] = winner;
      return { nodeName: m.name, winner, loser };
    });

    // Simulate SF
    const sfPairings = [
      { name: "M101", t1: qfRes["M97"], t2: qfRes["M98"] },
      { name: "M102", t1: qfRes["M99"], t2: qfRes["M100"] }
    ];
    const sfRes = {};
    const sfOut = sfPairings.map(m => {
      const { winner, loser } = simKnockout(m.t1, m.t2);
      sfRes[m.name] = winner;
      return { nodeName: m.name, winner, loser };
    });

    // Simulate Final
    const { winner: finalWinner, loser: finalRunner } = simKnockout(sfRes["M101"], sfRes["M102"]);
    const finalOut = { nodeName: "M103", winner: finalWinner, loser: finalRunner };

    return {
      r32: r32Out,
      r16: r16Out,
      qf: qfOut,
      sf: sfOut,
      final: finalOut,
      avgProb: sumProbs / probCounts
    };
  }

  renderBracket() {
    const view = document.getElementById("bracket-view");
    view.innerHTML = "";

    if (this.phase === "GROUP_STAGE") {
      // Render Group Tables
      const groupGrid = document.createElement("div");
      groupGrid.className = "group-stage-grid";
      
      for (const [gName, teams] of Object.entries(this.groups)) {
        const card = document.createElement("div");
        card.className = "group-table-card";
        
        let rowsHtml = "";
        teams.forEach((t, i) => {
          let posClass = "elim";
          if (t.status === "ACTIVE") {
            if (i === 0) posClass = "q-winner";
            else if (i === 1) posClass = "q-runner";
            else posClass = "q-third";
          }
          rowsHtml += `
            <div class="group-row ${posClass}">
              <span class="group-row-name">${i+1}. ${t.name}</span>
              <span class="group-row-stats">PTS:${t.points} GD:${t.gd}</span>
            </div>
          `;
        });

        card.innerHTML = `
          <div class="group-title">GROUP ${gName}</div>
          ${rowsHtml}
        `;
        groupGrid.appendChild(card);
      }
      view.appendChild(groupGrid);
      return;
    }

    // Render Knockout DAG columns
    const stages = ["R32", "R16", "QF", "SF", "FINAL"];
    stages.forEach(st => {
      const col = document.createElement("div");
      col.className = "bracket-stage";
      col.innerHTML = `<div class="bracket-stage-title">${st}</div>`;
      
      const container = document.createElement("div");
      container.className = "stage-nodes-container";

      // If we have simulation matches for this stage, draw them
      const stageMatches = this.phase === st ? this.matches : (this.bracketData[st.toLowerCase()] || []);
      
      if (stageMatches.length > 0) {
        stageMatches.forEach((m, idx) => {
          const node = document.createElement("div");
          node.className = "bracket-node";
          if (st !== "FINAL") node.classList.add("has-next");
          
          if (this.phase === st && idx === this.currentMatchIndex) {
            node.classList.add("active-match");
          }

          const hasPlayed = m.winner !== undefined;
          const wName = hasPlayed ? m.winner.name : "";
          
          let t1Class = "";
          let t2Class = "";
          if (hasPlayed) {
            t1Class = m.winner === m.t1 ? "winner" : "loser";
            t2Class = m.winner === m.t2 ? "winner" : "loser";
          }

          node.innerHTML = `
            <div class="bracket-team-row ${t1Class}">
              <span>${m.t1 ? m.t1.name : "TBD"}</span>
              <span class="bracket-score ${t1Class === 'winner' ? 'winner-score' : ''}">${hasPlayed ? m.g1 : ""}</span>
            </div>
            <div class="bracket-team-row ${t2Class}">
              <span>${m.t2 ? m.t2.name : "TBD"}</span>
              <span class="bracket-score ${t2Class === 'winner' ? 'winner-score' : ''}">${hasPlayed ? m.g2 : ""}</span>
            </div>
          `;
          container.appendChild(node);
        });
      } else {
        // Draw placeholder empty nodes based on standard bracket count
        const count = { "R32": 16, "R16": 8, "QF": 4, "SF": 2, "FINAL": 1 }[st];
        for (let i = 0; i < count; i++) {
          const node = document.createElement("div");
          node.className = "bracket-node";
          if (st !== "FINAL") node.classList.add("has-next");
          node.innerHTML = `
            <div class="bracket-team-row"><span>TBD</span></div>
            <div class="bracket-team-row"><span>TBD</span></div>
          `;
          container.appendChild(node);
        }
      }
      col.appendChild(container);
      view.appendChild(col);
    });
  }
}

// --- PHYSICS ENGINE CLASS ---
class ExergyPhysicsEngine {
  constructor(canvas, sim) {
    this.canvas = canvas;
    this.ctx = canvas.getContext("2d");
    this.sim = sim;
    
    this.resize();
    window.addEventListener("resize", () => this.resize());
    
    // Physical gravity/attraction parameters
    this.centerGrav = 0.005;
    this.friction = 0.985;
    
    this.initLoop();
  }

  resize() {
    const rect = this.canvas.parentElement.getBoundingClientRect();
    this.canvas.width = rect.width;
    this.canvas.height = rect.height;
  }

  initLoop() {
    const loop = () => {
      this.updatePhysics();
      this.draw();
      requestAnimationFrame(loop);
    };
    requestAnimationFrame(loop);
  }

  updatePhysics() {
    const teams = Object.values(this.sim.teams);
    const width = this.canvas.width;
    const height = this.canvas.height;
    const cx = width / 2;
    const cy = height / 2;

    // Adjust target points based on tournament phase
    teams.forEach(t => {
      if (t.status === "ELIMINATED") {
        // Drifts to the outer edges/bottom
        t.targetX = t.name.charCodeAt(0) % 2 === 0 ? 30 : width - 30;
        t.targetY = height - 40 - (t.name.charCodeAt(1) % 6) * 15;
      } else if (t.status === "CHAMPION") {
        // Sovereign center lock
        t.targetX = cx;
        t.targetY = cy;
      } else if (this.sim.activeClashingNodes && this.sim.activeClashingNodes.includes(t)) {
        // Clashing match participants converge to collision focus
        const idx = this.sim.activeClashingNodes.indexOf(t);
        t.targetX = cx + (idx === 0 ? -40 : 40);
        t.targetY = cy - 20;
      } else {
        // Default floating behaviour grouped by region or groups
        let clusterIdx = 0;
        for (const [gName, tNames] of Object.entries(GROUPS_SEED)) {
          if (tNames.includes(t.name)) {
            clusterIdx = gName.charCodeAt(0) - 65;
            break;
          }
        }
        const angle = (clusterIdx / 12) * Math.PI * 2;
        const radius = Math.min(width, height) * 0.3;
        t.targetX = cx + Math.cos(angle) * radius;
        t.targetY = cy + Math.sin(angle) * radius;
      }

      // Physics integration
      if (t.targetX !== null) {
        const ax = (t.targetX - t.x) * this.centerGrav;
        const ay = (t.targetY - t.y) * this.centerGrav;
        t.vx += ax;
        t.vy += ay;
      }

      t.x += t.vx;
      t.y += t.vy;
      t.vx *= this.friction;
      t.vy *= this.friction;

      // Dynamic Gravity mapping
      t.radius = 6 + t.liveExergy * 8 + (t.momentum || 0) * 5;
      
      // Cold losers drift effect
      t.vy += (t.volatility || 0) * 0.08;

      // Keep inside boundary canvas margins
      const margin = t.radius + 10;
      if (t.x < margin) { t.x = margin; t.vx *= -0.5; }
      if (t.x > width - margin) { t.x = width - margin; t.vx *= -0.5; }
      if (t.y < margin) { t.y = margin; t.vy *= -0.5; }
      if (t.y > height - margin) { t.y = height - margin; t.vy *= -0.5; }
      
      t.pulse += 0.05 + (t.momentum || 0) * 0.15;
    });

    // Particle-to-particle collisions (Elastic deflection)
    for (let i = 0; i < teams.length; i++) {
      for (let j = i + 1; j < teams.length; j++) {
        const t1 = teams[i];
        const t2 = teams[j];

        // Skip massive collisions for eliminated ones
        if (t1.status === "ELIMINATED" && t2.status === "ELIMINATED") continue;

        const dx = t2.x - t1.x;
        const dy = t2.y - t1.y;
        const dist = Math.hypot(dx, dy);
        const minDist = t1.radius + t2.radius + 4;

        if (dist < minDist) {
          const angle = Math.atan2(dy, dx);
          const tx = t1.x + Math.cos(angle) * minDist;
          const ty = t1.y + Math.sin(angle) * minDist;
          const ax = (tx - t2.x) * 0.1;
          const ay = (ty - t2.y) * 0.1;
          
          t1.vx -= ax;
          t1.vy -= ay;
          t2.vx += ax;
          t2.vy += ay;
        }
      }
    }
  }

  draw() {
    this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
    const width = this.canvas.width;
    const height = this.canvas.height;
    
    // Draw central gravitational node mesh if active clashing nodes
    if (this.sim.activeClashingNodes) {
      const [n1, n2] = this.sim.activeClashingNodes;
      this.ctx.beginPath();
      this.ctx.strokeStyle = "rgba(43, 59, 229, 0.4)";
      this.ctx.lineWidth = 2;
      this.ctx.setLineDash([4, 4]);
      this.ctx.moveTo(n1.x, n1.y);
      this.ctx.lineTo(n2.x, n2.y);
      this.ctx.stroke();
      this.ctx.setLineDash([]);
      
      // Draw collision impact aura
      const cx = (n1.x + n2.x) / 2;
      const cy = (n1.y + n2.y) / 2;
      this.ctx.beginPath();
      const grad = this.ctx.createRadialGradient(cx, cy, 5, cx, cy, 60);
      grad.addColorStop(0, "rgba(255, 159, 28, 0.2)");
      grad.addColorStop(1, "rgba(10, 10, 10, 0)");
      this.ctx.fillStyle = grad;
      this.ctx.arc(cx, cy, 60, 0, Math.PI * 2);
      this.ctx.fill();
    }

    // Draw active connections in groups
    if (this.sim.phase === "GROUP_STAGE") {
      this.ctx.strokeStyle = "rgba(43, 59, 229, 0.03)";
      this.ctx.lineWidth = 1;
      for (const group of Object.values(this.sim.groups)) {
        for (let i = 0; i < group.length; i++) {
          for (let j = i + 1; j < group.length; j++) {
            if (group[i].status === "ACTIVE" && group[j].status === "ACTIVE") {
              this.ctx.beginPath();
              this.ctx.moveTo(group[i].x, group[i].y);
              this.ctx.lineTo(group[j].x, group[j].y);
              this.ctx.stroke();
            }
          }
        }
      }
    }

    // Draw team nodes
    Object.values(this.sim.teams).forEach(t => {
      this.ctx.save();
      
      // Base glow effects
      this.ctx.beginPath();
      
      // Node opacity influenced by volatility
      const nodeAlpha = Math.max(0.1, 1.0 - (t.volatility || 0) * 2.0);
      this.ctx.globalAlpha = t.status === "ELIMINATED" ? 0.2 : nodeAlpha;
      
      let colorGlow = `rgba(43, 59, 229, ${Math.min(0.8, 0.2 + (t.momentum || 0) * 0.6)})`;
      if (t.status === "ELIMINATED") {
        colorGlow = "rgba(243, 244, 246, 0.02)";
      } else if (t.status === "CHAMPION") {
        colorGlow = "rgba(255, 215, 0, 0.8)";
      } else if ((t.volatility || 0) > 0.1) {
        colorGlow = `rgba(255, 159, 28, ${Math.min(0.6, 0.2 + t.volatility)})`;
      }
      
      const pulseAmp = 0.15 + (t.momentum || 0) * 0.3;
      const glowRad = t.radius * (1.3 + Math.sin(t.pulse) * pulseAmp);
      const gradGlow = this.ctx.createRadialGradient(t.x, t.y, t.radius * 0.5, t.x, t.y, glowRad);
      gradGlow.addColorStop(0, colorGlow);
      gradGlow.addColorStop(1, "rgba(10, 10, 10, 0)");
      this.ctx.fillStyle = gradGlow;
      this.ctx.arc(t.x, t.y, glowRad, 0, Math.PI * 2);
      this.ctx.fill();

      // Main Node body
      this.ctx.beginPath();
      let nodeFill = "#2B3BE5"; // YInMn Blue default
      if (t.status === "ELIMINATED") {
        nodeFill = "#222222";
      } else if (t.status === "CHAMPION") {
        nodeFill = "#FFD700";
      } else if ((t.volatility || 0) > 0.1) {
        // Cold fade
        nodeFill = "#FF9F1C";
      } else if ((t.momentum || 0) > 0.2) {
        // Brightness from momentum
        nodeFill = "#4D5FFF";
      }
      
      this.ctx.fillStyle = nodeFill;
      this.ctx.strokeStyle = "#000000";
      this.ctx.lineWidth = 1.5;
      this.ctx.arc(t.x, t.y, t.radius, 0, Math.PI * 2);
      this.ctx.fill();
      this.ctx.stroke();

      this.ctx.globalAlpha = 1.0; // Reset for label
      
      // Node label
      if (t.status !== "ELIMINATED" || t.radius > 9) {
        this.ctx.fillStyle = t.status === "ELIMINATED" ? "rgba(243, 244, 246, 0.2)" : "#F3F4F6";
        this.ctx.font = `${t.status === "CHAMPION" ? "bold 11px" : "10px"} var(--font-sans)`;
        this.ctx.textAlign = "center";
        
        let labelY = t.y - t.radius - 5;
        if (t.status === "CHAMPION") {
          labelY = t.y + t.radius + 15;
          // draw crown or gold ring
          this.ctx.beginPath();
          this.ctx.strokeStyle = "#FFD700";
          this.ctx.lineWidth = 2;
          this.ctx.arc(t.x, t.y, t.radius + 6, 0, Math.PI * 2);
          this.ctx.stroke();
        }
        
        this.ctx.fillText(t.name, t.x, labelY);
      }
      this.ctx.restore();
    });
  }
}

// --- SETUP EVENT LISTENERS & INITS ---
document.addEventListener("DOMContentLoaded", () => {
  const sim = new TournamentSimulator();
  const canvas = document.getElementById("ecosystem-canvas");
  const physics = new ExergyPhysicsEngine(canvas, sim);

  // Bind buttons
  const btnPlay = document.getElementById("btn-play");
  btnPlay.addEventListener("click", () => {
    if (sim.isPlaying) {
      sim.pause();
    } else {
      sim.play();
    }
  });

  const btnStep = document.getElementById("btn-step");
  btnStep.addEventListener("click", () => {
    sim.pause();
    sim.step();
  });

  const btnReset = document.getElementById("btn-reset");
  btnReset.addEventListener("click", () => {
    sim.reset();
  });

  const btnClearLog = document.getElementById("btn-clear-log");
  btnClearLog.addEventListener("click", () => {
    document.getElementById("terminal-log").innerHTML = "";
  });

  // Bind sliders
  const slideVol = document.getElementById("slide-volatility");
  slideVol.addEventListener("input", (e) => {
    sim.volatility = parseFloat(e.target.value);
    document.getElementById("val-volatility").innerText = sim.volatility.toFixed(2);
  });

  const slideLr = document.getElementById("slide-lr");
  slideLr.addEventListener("input", (e) => {
    sim.lr = parseFloat(e.target.value);
    document.getElementById("val-lr").innerText = sim.lr.toFixed(2);
  });

  const slideUpset = document.getElementById("slide-upset");
  slideUpset.addEventListener("input", (e) => {
    sim.upsetPressure = parseFloat(e.target.value);
    document.getElementById("val-upset").innerText = sim.upsetPressure.toFixed(2);
  });

  const slideSpeed = document.getElementById("slide-speed");
  slideSpeed.addEventListener("input", (e) => {
    sim.speed = parseInt(e.target.value);
    document.getElementById("val-speed").innerText = `${sim.speed}ms`;
  });

  // Tabs toggle
  const tabExergy = document.getElementById("tab-exergy");
  const tabBenchmark = document.getElementById("tab-benchmark");
  const containerExergy = document.getElementById("exergy-container");
  const containerBenchmark = document.getElementById("benchmark-container");

  tabExergy.addEventListener("click", () => {
    tabExergy.classList.add("active");
    tabBenchmark.classList.remove("active");
    containerExergy.style.display = "block";
    containerBenchmark.style.display = "none";
  });

  tabBenchmark.addEventListener("click", () => {
    tabBenchmark.classList.add("active");
    tabExergy.classList.remove("active");
    containerExergy.style.display = "none";
    containerBenchmark.style.display = "block";
    // Trigger benchmark calculation
    sim.runBenchmark();
  });

  // Initial render calls
  sim.renderBracket();
  sim.updateLeaderboard();
});
