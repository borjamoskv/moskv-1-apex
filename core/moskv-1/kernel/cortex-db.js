const Database = require('better-sqlite3');
const path = require('path');

class CortexDB {
    constructor(dbPath) {
        // Resolve to project root by default
        const targetPath = dbPath || path.resolve(__dirname, '../../../cortex.sqlite');
        
        console.log(`[CORTEX-DB] Initializing SQLite C5-REAL Ledger at ${targetPath}`);
        this.db = new Database(targetPath, { timeout: 5000 });
        
        // R10: Prevención de deadlocks termodinámicos en hilos concurrentes
        this.db.pragma('journal_mode = WAL');
        this.db.pragma('busy_timeout = 5000');
        
        this.initSchema();
    }
    
    initSchema() {
        this.db.exec(`
            CREATE TABLE IF NOT EXISTS ledger (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp INTEGER NOT NULL,
                module TEXT NOT NULL,
                payload TEXT NOT NULL,
                hash TEXT,
                signature TEXT,
                noise TEXT
            );
        `);
    }

    insertCompilerLedger(timestamp, type, target, payloadHash, ledgerHash) {
        const stmt = this.db.prepare('INSERT INTO ledger (timestamp, module, payload, hash) VALUES (?, ?, ?, ?)');
        stmt.run(timestamp, 'AUTO-COMPILER', `${type}|${target}|${payloadHash}`, ledgerHash);
    }

    insertEscrowLedger(timestamp, subAgentId, actionType, exergyDelta, signature, noiseVector) {
        const stmt = this.db.prepare('INSERT INTO ledger (timestamp, module, payload, signature, noise) VALUES (?, ?, ?, ?, ?)');
        stmt.run(timestamp, 'PQ-ESCROW', `${subAgentId}|${actionType}|${exergyDelta}`, signature, noiseVector);
    }

    insertExergyLedger(timestamp, type, nodeId, value, currentExergy, ledgerHash) {
        const stmt = this.db.prepare('INSERT INTO ledger (timestamp, module, payload, hash) VALUES (?, ?, ?, ?)');
        stmt.run(timestamp, 'EXERGY-MONITOR', `${type}|${nodeId}|${value}|${currentExergy}`, ledgerHash);
    }
}

// Singleton export
module.exports = new CortexDB();
