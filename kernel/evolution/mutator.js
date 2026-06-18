const { execSync } = require("child_process");
const crypto = require("crypto");

function hash(s) {
    return crypto.createHash("sha256").update(s).digest("hex");
}

function proposeMutation(signal, archetype = "ALPHA") {
    const mutationId = hash(JSON.stringify(signal) + Date.now().toString()).slice(0, 12);
    const branch = `cortex/${archetype.toLowerCase()}/${mutationId}`;
    console.log("[SWARM] spawning:", archetype, branch);
    execSync(`git checkout -b ${branch} master`);
    return branch;
}
module.exports = { proposeMutation };
