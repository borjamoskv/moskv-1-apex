const { ARCHETYPES } = require("../swarm/archetypes.js");
const { getMetrics } = require("./telemetry.js");
function verifyGuardrails(branch, archetypeKey) {
  const archetype = ARCHETYPES[archetypeKey] || ARCHETYPES.BETA;
  const metrics = getMetrics(archetypeKey);
  console.log(`[GUARDRAIL] Evaluating ${archetypeKey} for branch ${branch}`);
  if (metrics.latency > archetype.latencyTolerance) {
    console.warn(`[GUARDRAIL-FAIL] Latency ${metrics.latency}ms > ${archetype.latencyTolerance}ms`);
    return false;
  }
  if (metrics.errorRate > 0.01) {
    console.warn(`[GUARDRAIL-FAIL] Error rate ${metrics.errorRate * 100}% > 1%`);
    return false;
  }
  return true;
}
module.exports = { verifyGuardrails };
