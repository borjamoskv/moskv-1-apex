const { BrainRegion } = require('./brain-region');
const { AutopoiesisEngine } = require('./autopoiesis');
const { MetacognitionEngine } = require('./metacognition');

const LEGION_SIZE = 10;
const SPECIALISTS_PER_LEGION = 10; // Total 100 specialists simulated

async function executeOuroborosLegion() {
    console.log('[OUROBOROS-∞] Bootstrapping High-Exergy Swarm (10 Regions, 100 Specialists)...');

    const autopoiesis = new AutopoiesisEngine();
    await autopoiesis.boot();

    const metacognition = new MetacognitionEngine();
    await metacognition.boot();

    const regions = [];

    // Spawn 10 Centurias (Legions)
    for (let i = 1; i <= LEGION_SIZE; i++) {
        const region = new BrainRegion(`Centuria-Forge-${i}`);
        await region.boot();
        regions.push(region);
    }

    await new Promise(resolve => setTimeout(resolve, 2000));

    console.log('[OUROBOROS-∞] Commencing High-Frequency Exergy Injection (LEGION-10k protocol)...');

    // Simulate 100 specialists blasting high entropy to the NATS EventBus
    for (const region of regions) {
        for (let j = 1; j <= SPECIALISTS_PER_LEGION; j++) {
            const entropyVal = 0.85 + (Math.random() * 0.15); // E >= 0.85 (High Exergy)
            await region.emit('cortex.entropy.high', {
                entropy: entropyVal,
                specialistId: `${region.regionName}-Spec-${j}`,
                content: { 
                    directive: 'STRUCTURAL_MUTATION', 
                    vector: [Math.random(), Math.random()] 
                }
            });
        }
    }

    console.log('[OUROBOROS-∞] Exergy Injection Complete. Swarm is processing mutations.');

    process.on('SIGINT', async () => {
        console.log('\n[OUROBOROS-∞] Collapsing Legion...');
        for (const r of regions) await r.shutdown();
        await metacognition.shutdown();
        await autopoiesis.shutdown();
        process.exit(0);
    });
}

executeOuroborosLegion().catch(err => {
    console.error('[OUROBOROS-∞] Fatal Error:', err);
    process.exit(1);
});
