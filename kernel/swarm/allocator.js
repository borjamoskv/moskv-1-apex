const { ARCHETYPES } = require("./archetypes.js");
const stats = {
  ALPHA: { reward: 0, pulls: 1 },
  BETA: { reward: 0, pulls: 1 },
  GAMMA: { reward: 0, pulls: 1 },
};
function ucb(archetype) {
  const s = stats[archetype];
  return (s.reward / s.pulls) + Math.sqrt(2 * Math.log(Date.now() + 1) / s.pulls);
}
function selectArchetype() {
  return Object.keys(ARCHETYPES).reduce((best, a) =>
    ucb(a) > ucb(best) ? a : best
  );
}
function updateArchetype(archetype, reward) {
  stats[archetype].reward += reward;
  stats[archetype].pulls += 1;
}
module.exports = { selectArchetype, updateArchetype, stats };
