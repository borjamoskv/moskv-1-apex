const { execSync } = require("child_process");
const crypto = require("crypto");

function hash(s) {
    return crypto.createHash("sha256").update(s).digest("hex");
}

function proposeMutation(signal) {
    const mutationId = hash(JSON.stringify(signal) + Date.now().toString()).slice(0, 12);
    const branch = `cortex/mutation/${mutationId}`;
    console.log("[EVOLUTION] spawning mutation branch:", branch);
    
    execSync(`git checkout -b ${branch} master`);
    return branch;
}

module.exports = { proposeMutation };
