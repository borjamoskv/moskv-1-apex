const { BrainRegion } = require('./brain-region');
const neo4j = require('neo4j-driver');

class MetacognitionEngine extends BrainRegion {
    constructor() {
        super('Metacognition');
        this.driver = neo4j.driver(
            process.env.NEO4J_URI || 'bolt://localhost:7687',
            neo4j.auth.basic(process.env.NEO4J_USER || 'neo4j', process.env.NEO4J_PASS || 'password')
        );
        this.sleepInterval = null;
    }

    async boot() {
        await super.boot();
        
        // Listen for internal system health requests
        await this.listen('cortex.system.audit', async () => {
            console.log('[Metacognition] Audit requested. Calculating system entropy...');
            await this.auditGraph();
        });

        // Trigger a 'Sleep/Freeze' cycle every 10 minutes (PoC uses 60s for visibility)
        const freezeMs = process.env.FREEZE_MS || 60000;
        this.sleepInterval = setInterval(async () => {
            console.log('\n[Metacognition] Initiating Sleep Cycle (Memory Pruning)...');
            await this.emit('cortex.state.sleep', { phase: 'REM', actionable: true });
            await this.pruneNoise();
        }, freezeMs);

        console.log('[Metacognition] Audit Loop & Sleep Cycles Active.');
    }

    async auditGraph() {
        const session = this.driver.session();
        try {
            const result = await session.executeRead(tx => 
                tx.run('MATCH (n:MemoryNode) RETURN count(n) AS total, avg(n.entropy) AS avgEntropy')
            );
            const total = result.records[0].get('total').toNumber();
            const avgEntropy = result.records[0].get('avgEntropy') || 0;
            console.log(`[Metacognition] Graph Audit -> Nodes: ${total} | Avg Entropy: ${avgEntropy}`);
            
            // If the graph is too chaotic, trigger a global alert
            if (avgEntropy > 0.8) {
                await this.emit('cortex.entropy.critical', { avgEntropy, total });
            }
        } catch (err) {
            console.error('[Metacognition] Audit failed:', err);
        } finally {
            await session.close();
        }
    }

    async pruneNoise() {
        const session = this.driver.session();
        try {
            // Delete high entropy nodes that haven't crystallized
            const result = await session.executeWrite(tx =>
                tx.run(`
                    MATCH (n:MemoryNode)
                    WHERE n.entropy > 0.90 AND n.lastUpdated < (timestamp() - 60000)
                    DETACH DELETE n
                    RETURN count(n) as pruned
                `)
            );
            const pruned = result.records[0].get('pruned').toNumber();
            console.log(`[Metacognition] Sleep Cycle Complete. Pruned ${pruned} high-entropy nodes.`);
        } catch (err) {
            console.error('[Metacognition] Pruning failed:', err);
        } finally {
            await session.close();
        }
    }

    async shutdown() {
        if (this.sleepInterval) clearInterval(this.sleepInterval);
        await this.driver.close();
        await super.shutdown();
    }
}

module.exports = { MetacognitionEngine };
