const { execSync } = require("child_process");

function createPR(branch, summary) {
    console.log("[EVOLUTION] opening PR for autonomous review");
    try {
        const env = { ...process.env };
        delete env.GITHUB_TOKEN; // Prevent CLI from using broken injected tokens
        
        execSync(`gh pr create --title "cortex mutation ${branch}" --body "${summary}" --base master --head ${branch}`, {
            env,
            stdio: 'inherit'
        });
    } catch (e) {
        console.error("[EVOLUTION-ERR] PR creation failed. Keyring auth required or push missing.");
    }
}

module.exports = { createPR };
