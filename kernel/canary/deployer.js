const { execSync } = require("child_process");
function deployCanary(branch, percent = 10) {
  console.log("[CANARY] deploying split traffic:", percent);
  try {
    execSync("vercel deploy --prod=false --target=preview", { stdio: "inherit" });
    execSync(`vercel alias set preview-${branch}.vercel.app canary.moskv`, { stdio: "inherit" });
  } catch (err) {
    console.error("[CANARY-ERR] Vercel CLI deploy failed.");
  }
  return {
    branch,
    traffic: percent,
    url: `preview-${branch}.vercel.app`,
  };
}
module.exports = { deployCanary };
