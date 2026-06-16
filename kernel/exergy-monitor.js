/**
 * C5-REAL LYAPUNOV EXERGY MONITOR (NODE 3 / L4 APOPTOSIS TRIGGER)
 * Thermodynamically grounds the MOSKV-1 architecture.
 * Equation: Net_Exergy = \sum (Yield_i * S_i) - \int Entropy_Cost(dt) - Death_Debt
 */

const { EventBus } = require('./event-bus.js');

class ExergyMonitor {
    constructor() {
        this.baseMultiplier = 100; // Singularity multiplier (S_i)
        this.currentExergy = 10.0; // Initial threshold buffer
        this.entropyRate = 0.05; // Entropy decay per tick
        this.deathDebt = 0.0; // Accumulated debt from dormant or degraded nodes
        
        this.tickInterval = null;
        this.eventBus = new EventBus();

        // Listen for yield generation from active Centuria Swarm nodes
        this.eventBus.on('C5_YIELD_GENERATED', (data) => this.recordYield(data.value));
        
        // Listen for system bloat (increases death debt)
        this.eventBus.on('C4_SIM_DEGRADATION', (data) => this.increaseDeathDebt(data.penalty));
    }

    startMonitoring() {
        console.log('[EXERGY-MONITOR] Initializing Lyapunov Gate...');
        this.tickInterval = setInterval(() => this.calculateThermodynamics(), 1000);
    }

    stopMonitoring() {
        if (this.tickInterval) {
            clearInterval(this.tickInterval);
            this.tickInterval = null;
        }
    }

    recordYield(value) {
        const grossYield = value * this.baseMultiplier;
        this.currentExergy += grossYield;
        console.log(`[EXERGY-MONITOR] Yield received. Gross Exergy +${grossYield}. Current: ${this.currentExergy.toFixed(2)}`);
    }

    increaseDeathDebt(penalty) {
        this.deathDebt += penalty;
        console.warn(`[EXERGY-MONITOR] Structural degradation detected. Death Debt increased by ${penalty}. Total Debt: ${this.deathDebt.toFixed(2)}`);
    }

    calculateThermodynamics() {
        // \int Entropy_Cost(dt)
        const entropyCost = this.entropyRate;
        
        // Net_Exergy = Current - Entropy - Debt
        this.currentExergy = this.currentExergy - entropyCost - this.deathDebt;

        console.log(`[EXERGY-MONITOR] Tick. Net Exergy: ${this.currentExergy.toFixed(4)}`);

        // L4 Apoptosis Trigger
        if (this.currentExergy <= 0) {
            this.triggerL4Apoptosis();
        }
    }

    triggerL4Apoptosis() {
        this.stopMonitoring();
        console.error('*** [CRITICAL] L4 APOPTOSIS TRIGGERED ***');
        console.error('Net_Exergy <= 0. System decay exceeds yield. Initiating Purge Protocol.');
        
        this.eventBus.emit('L4_APOPTOSIS_PURGE', { reason: 'NEGATIVE_EXERGY' });
        
        // In a true sovereign system, this would kill the process or initiate a hard reset.
        // process.exit(1);
    }
}

module.exports = { ExergyMonitor };
