const { selectMutationDelayed } = require("../evolution/selector.js");
const { execSync } = require("child_process");
const { updateArchetype } = require("../swarm/allocator.js");
const { computeReward } = require("../swarm/fitness.js");
const { verifyGuardrails } = require("../guardrails/sentinel.js");
function runEvolutionSweep(branches) {
  branches.forEach(branch => {
    const parts = branch.split("/");
    const archetypeKey = (parts[1] || "").toUpperCase();
    const ok = verifyGuardrails(branch, archetypeKey);
    let result = "die";
    if (ok) {
      result = selectMutationDelayed(branch);
    } else {
      console.warn(`[GUARDRAIL-DIE] Branch ${branch} killed by Sentinel.`);
    }
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
function swarmSweep(events) {
  events.forEach(e => {
    const reward = computeReward(e.archetype, e.revenue, e.latency);
    updateArchetype(e.archetype, reward);
  });
}
module.exports = { runEvolutionSweep, swarmSweep };
