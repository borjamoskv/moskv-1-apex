function computeReward(archetype, revenue, latency) {
  switch (archetype) {
    case "ALPHA":
      return revenue * 2 - latency * 0.1;
    case "BETA":
      return revenue * 0.5 - latency * 2;
    case "GAMMA":
      return revenue * Math.random();
    default:
      return 0;
  }
}
module.exports = { computeReward };
