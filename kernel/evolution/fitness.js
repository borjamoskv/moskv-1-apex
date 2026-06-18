function fitness(before, after) {
    const revenueDelta = after.revenue - before.revenue;
    const latencyDelta = before.latency - after.latency;
    return (revenueDelta * 2) + latencyDelta;
}

module.exports = { fitness };
