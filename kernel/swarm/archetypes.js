const ARCHETYPES = {
  ALPHA: {
    name: "aggressive-revenue",
    risk: 0.9,
    latencyTolerance: 200,
    strategy: "maximize short-term revenue",
  },
  BETA: {
    name: "homeostatic-stability",
    risk: 0.2,
    latencyTolerance: 20,
    strategy: "minimize variance and preserve UX integrity",
  },
  GAMMA: {
    name: "entropy-explorer",
    risk: 1.0,
    latencyTolerance: 500,
    strategy: "explore unknown execution paths",
  },
};
module.exports = { ARCHETYPES };
