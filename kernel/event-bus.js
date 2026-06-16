const { connect, StringCodec } = require('@nats-io/transport-node');
const crypto = require('crypto');

const sc = StringCodec();

class EventBus {
    constructor(serverUrl = 'nats://localhost:4222') {
        this.serverUrl = serverUrl;
        this.nc = null;
        this.js = null;
        this.lastHash = 'GENESIS';
    }

    async init() {
        this.nc = await connect({ servers: this.serverUrl });
        this.js = this.nc.jetstream();
        console.log('[EventBus] NATS JetStream Connected. Ready for C5-REAL execution.');
    }

    _hash(payload, prevHash) {
        return crypto.createHash('sha256')
            .update(prevHash + JSON.stringify(payload))
            .digest('hex');
    }

    async emit(subject, payload) {
        if (!this.js) throw new Error("EventBus not initialized");

        const currentHash = this._hash(payload, this.lastHash);
        const event = {
            timestamp: Date.now(),
            payload,
            prevHash: this.lastHash,
            hash: currentHash
        };

        this.lastHash = currentHash;
        await this.js.publish(subject, sc.encode(JSON.stringify(event)));
        return currentHash;
    }

    async subscribe(subject, callback) {
        if (!this.js) throw new Error("EventBus not initialized");
        const sub = await this.js.consumers.get('cortex_stream', {
            durable_name: 'cortex_durable'
        }); // Simplified for PoC. Real code would map consumers properly.

        // Standard subscription as fallback
        const standardSub = this.nc.subscribe(subject);
        (async () => {
            for await (const msg of standardSub) {
                const event = JSON.parse(sc.decode(msg.data));
                callback(event);
            }
        })();
    }

    close() {
        if (this.nc) this.nc.close();
    }
}

module.exports = { EventBus };
