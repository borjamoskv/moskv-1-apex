const { execSync } = require("child_process");

function runTests() {
    console.log("[EVOLUTION] running test gate (selection pressure)");
    try {
        execSync(`python3 exergy_sensor.py --workspace`, { stdio: "inherit" });
        return true;
    } catch (e) {
        console.error("[EVOLUTION-ERR] Mutation failed structural exergy gate.");
        return false;
    }
}

module.exports = { runTests };
