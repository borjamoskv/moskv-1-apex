const { connect, StringCodec } = require('@nats-io/transport-node');
const crypto = require('crypto');

const sc = StringCodec();

class EventBus {
    /**
     * @param {string} serverUrl NATS Server URL
     * @param {string} streamName JetStream Stream Name
     */
    constructor(serverUrl = process.env.NATS_URL || 'nats://localhost:4222', streamName = 'CORTEX_STREAM') {
        this.serverUrl = serverUrl;
        this.streamName = streamName;
        this.nc = null;
        this.js = null;
        this.lastHash = 'GENESIS';
    }

    async init() {
        try {
            this.nc = await connect({ servers: this.serverUrl, maxReconnectAttempts: -1 });
            this.js = this.nc.jetstream();
            const jsm = await this.nc.jetstreamManager();
            
            // Ensure Stream Exists
            try {
                await jsm.streams.info(this.streamName);
            } catch (err) {
                if (err.message.includes('stream not found')) {
                    await jsm.streams.add({
                        name: this.streamName,
                        subjects: ['cortex.>'],
                        retention: 'limits',
                        max_age: 0, // Infinite retention for true memory
                        storage: 'file'
                    });
                    console.log(`[EventBus] Created JetStream: ${this.streamName}`);
                }
            }
            console.log('[EventBus] NATS JetStream Connected & Stream Verified. Ready for C5-REAL execution.');
        } catch (error) {
            console.error('[EventBus] Critical Initialization Error:', error);
            process.exit(1);
        }
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
        const encoded = sc.encode(JSON.stringify(event));
        
        try {
            const ack = await this.js.publish(subject, encoded);
            return { hash: currentHash, seq: ack.seq };
        } catch (error) {
            console.error(`[EventBus] Publish Error on subject ${subject}:`, error);
            throw error;
        }
    }

    async subscribe(subject, callback, durableName = null) {
        if (!this.js) throw new Error("EventBus not initialized");
        
        try {
            const consumerOpts = {
                filter_subject: subject,
                deliver_policy: 'all'
            };
            
            if (durableName) {
                consumerOpts.durable_name = durableName;
            }

            const c = await this.js.consumers.get(this.streamName, consumerOpts);
            const iter = await c.consume();
            
            (async () => {
                for await (const msg of iter) {
                    try {
                        const event = JSON.parse(sc.decode(msg.data));
                        await callback(event, msg);
                        msg.ack();
                    } catch (err) {
                        console.error('[EventBus] Message Processing Error:', err);
                        msg.nak();
                    }
                }
            })();
            return iter;
        } catch (error) {
             console.error(`[EventBus] Subscription Error on subject ${subject}:`, error);
             throw error;
        }
    }

    async close() {
        if (this.nc) {
            await this.nc.drain();
            await this.nc.close();
            console.log('[EventBus] Connection closed.');
        }
    }
}

module.exports = { EventBus };
