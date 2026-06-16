const neo4j = require('neo4j-driver');
const { BrainRegion } = require('./brain-region');

class AutopoiesisEngine extends BrainRegion {
    constructor() {
        super('Autopoiesis');
        this.driver = neo4j.driver(
            process.env.NEO4J_URI || 'bolt://localhost:7687',
            neo4j.auth.basic(process.env.NEO4J_USER || 'neo4j', process.env.NEO4J_PASS || 'password')
        );
    }

    async boot() {
        await super.boot();
        
        // Listen for high-entropy / exergy events that require topology mutation
        await this.listen('cortex.entropy.high', async (payload) => {
            console.log('[Autopoiesis] High Exergy Event Detected. Mutating Topology...', payload);
            await this.mutateGraph(payload);
        });

        console.log('[Autopoiesis] Neo4j Driver initialized. Engine Ready.');
    }

    async mutateGraph(payload) {
        const session = this.driver.session();
        try {
            // C5-REAL Example Mutation: Creating a structural invariant node from an event
            const result = await session.writeTransaction(tx => 
                tx.run(
                    `MERGE (n:MemoryNode {id: $id}) 
                     SET n.entropy = $entropy, n.content = $content, n.lastUpdated = timestamp()
                     RETURN n`,
                    { id: payload.nodeId || Date.now().toString(), entropy: payload.entropy || 1.0, content: payload.content || 'Void' }
                )
            );
            console.log(`[Autopoiesis] Mutated Nodes: ${result.records.length}`);
        } catch (error) {
            console.error('[Autopoiesis] Graph Mutation Failed:', error);
        } finally {
            await session.close();
        }
    }

    shutdown() {
        this.driver.close();
        this.bus.close();
    }
}

module.exports = { AutopoiesisEngine };
