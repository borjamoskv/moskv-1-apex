const { fitness } = require("./fitness.js");
const { execSync } = require("child_process");

function selectMutation(before, after, branch) {
    const score = fitness(before, after);
    console.log(`[EVOLUTION] Evaluating fitness score: ${score}`);

    if (score > 0) {
        console.log("[EVOLUTION] Mutation accepted. Merging to master.");
        execSync(`git checkout master`);
        execSync(`git merge ${branch}`);
    } else {
        console.log("[EVOLUTION] Mutation rejected. Purging branch.");
        execSync(`git checkout master`);
        execSync(`git branch -D ${branch}`);
    }
    return score;
}

module.exports = { selectMutation };
