const { EventBus } = require('./event-bus');

class BrainRegion {
    constructor(regionName) {
        this.regionName = regionName;
        this.bus = new EventBus();
    }

    async boot() {
        await this.bus.init();
        console.log(`[CEN-Cluster] BrainRegion <${this.regionName}> Online. Exergy optimized.`);
    }

    async emit(subject, payload) {
        return await this.bus.emit(subject, { ...payload, sourceRegion: this.regionName });
    }

    async listen(subject, handler) {
        await this.bus.subscribe(subject, (event) => {
            // C5-REAL logging for audit
            console.log(`[${this.regionName}] Received Event Hash: ${event.hash}`);
            handler(event.payload);
        });
    }
}

module.exports = { BrainRegion };
