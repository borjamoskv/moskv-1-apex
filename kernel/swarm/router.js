const { selectArchetype } = require("./allocator.js");
function routeTraffic(req) {
  const archetype = selectArchetype();
  req.headers["x-cortex-archetype"] = archetype;
  if (archetype === "ALPHA") return "canary-alpha";
  if (archetype === "BETA") return "stable";
  if (archetype === "GAMMA") return "experimental";
  return "main";
}
module.exports = { routeTraffic };
