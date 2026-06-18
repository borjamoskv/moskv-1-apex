function routeTraffic(req) {
  const roll = Math.random() * 100;
  if (roll < 10) {
    req.headers["x-cortex-mode"] = "canary";
    return "canary";
  }
  return "main";
}
module.exports = { routeTraffic };
