const buffer = new Map();
function recordEvent(branch, event) {
  if (!buffer.has(branch)) buffer.set(branch, []);
  buffer.get(branch).push({
    ts: Date.now(),
    revenue: event.amount,
  });
}
function evaluateBranch(branch) {
  const events = buffer.get(branch) || [];
  const timeWindow = 1000 * 60 * 60 * 24;
  const now = Date.now();
  const filtered = events.filter(e => now - e.ts < timeWindow);
  return filtered.reduce((a, b) => a + b.revenue, 0);
}
module.exports = { recordEvent, evaluateBranch };
