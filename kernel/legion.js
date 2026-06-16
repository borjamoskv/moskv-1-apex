const { Worker } = require('worker_threads');
const path = require('path');
const { AutopoiesisEngine } = require('./autopoiesis');
const { MetacognitionEngine } = require('./metacognition');

const LEGION_SIZE = 10;
const SPECIALISTS_PER_LEGION = 10; // Total 100 specialists simulated

async function executeOuroborosLegion() {
    console.log('[OUROBOROS-∞] Bootstrapping High-Exergy Swarm (True Multi-Core execution)...');

    // 1. Boot the Core Engines (Main Thread)
    const autopoiesis = new AutopoiesisEngine();
    await autopoiesis.boot();

    const metacognition = new MetacognitionEngine();
    await metacognition.boot();

    const workers = [];
    let readyCount = 0;
    let completedCount = 0;

    // 2. Spawn 10 Centurias as Isolated Node.js Worker Threads
    console.log(`[OUROBOROS-∞] Spawning ${LEGION_SIZE} Isolated Worker Threads...`);
    
    for (let i = 1; i <= LEGION_SIZE; i++) {
        const worker = new Worker(path.resolve(__dirname, 'centuria-worker.js'), {
            workerData: { regionName: `Centuria-Forge-${i}`, specialistsCount: SPECIALISTS_PER_LEGION }
        });

        worker.on('message', (msg) => {
            if (msg.type === 'READY') {
                readyCount++;
                if (readyCount === LEGION_SIZE) {
                    console.log(`[OUROBOROS-∞] All ${LEGION_SIZE} Centurias Online. Igniting Exergy...`);
                    workers.forEach(w => w.postMessage({ type: 'IGNITE' }));
                }
            } else if (msg.type === 'DONE') {
                console.log(`[OUROBOROS-∞] ${msg.regionName} injected ${msg.emitted} mutations.`);
                completedCount++;
                if (completedCount === LEGION_SIZE) {
                    console.log('[OUROBOROS-∞] Massive Exergy Injection Complete. Swarm processing backend mutations.');
                }
            } else if (msg.type === 'ERROR') {
                console.error(`[OUROBOROS-∞] Error in ${msg.regionName}:`, msg.error);
            }
        });

        worker.on('error', (err) => console.error('[OUROBOROS-∞] Worker Thread Error:', err));
        worker.on('exit', (code) => {
            if (code !== 0) console.error(`[OUROBOROS-∞] Worker stopped with exit code ${code}`);
        });

        workers.push(worker);
    }

    process.on('SIGINT', async () => {
        console.log('\n[OUROBOROS-∞] Collapsing Legion & Thread Pool...');
        workers.forEach(w => w.postMessage({ type: 'SHUTDOWN' }));
        await metacognition.shutdown();
        await autopoiesis.shutdown();
        process.exit(0);
    });
}

executeOuroborosLegion().catch(err => {
    console.error('[OUROBOROS-∞] Fatal Error:', err);
    process.exit(1);
});
