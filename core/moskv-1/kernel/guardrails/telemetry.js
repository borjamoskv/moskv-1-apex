const registry = new Map();
function recordRequest(archetype, latency, status) {
  if (!registry.has(archetype)) {
    registry.set(archetype, { latencySum: 0, count: 0, errors: 0 });
  }
  const stats = registry.get(archetype);
  stats.latencySum += latency;
  stats.count += 1;
  if (status >= 500) {
    stats.errors += 1;
  }
}
function getMetrics(archetype) {
  const stats = registry.get(archetype) || { latencySum: 0, count: 0, errors: 0 };
  if (stats.count === 0) return { latency: 0, errorRate: 0 };
  return {
    latency: stats.latencySum / stats.count,
    errorRate: stats.errors / stats.count
  };
}
module.exports = { recordRequest, getMetrics };
