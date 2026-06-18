const { selectMutationDelayed } = require("../evolution/selector.js");
const { execSync } = require("child_process");
function runEvolutionSweep(branches) {
  branches.forEach(branch => {
    const result = selectMutationDelayed(branch);
    if (result === "die") {
      try {
        execSync(`git branch -D ${branch}`);
      } catch (err) {
        console.error(`[CRON-ERR] Failed to delete branch ${branch}:`, err.message);
      }
    }
    if (result === "survive") {
      try {
        execSync(`git checkout master && git merge ${branch}`);
      } catch (err) {
        console.error(`[CRON-ERR] Failed to merge branch ${branch} into master:`, err.message);
      }
    }
  });
}
module.exports = { runEvolutionSweep };
