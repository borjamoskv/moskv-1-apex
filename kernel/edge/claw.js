const { exec } = require('child_process');
const path = require('path');
let lastDeployTime = 0;
const COOLDOWN_MS = 300000;
function mutateInfra(signal) {
    const amount = signal.amount_total || signal.amount || 0;
    const intensity = amount / 100;
    console.log(`[CORTEX-EDGE] Evaluating exergy revenue signal. Intensity: ${intensity} EUR`);
    const now = Date.now();
    if (now - lastDeployTime < COOLDOWN_MS) {
        console.log(`[CORTEX-EDGE] Deploy throttled. Cooldown active. Time remaining: ${Math.round((COOLDOWN_MS - (now - lastDeployTime)) / 1000)}s`);
        return;
    }
    if (intensity > 50) {
        lastDeployTime = now;
        console.log("[CORTEX-EDGE] Scaling up deployment asynchronously (C5-REAL)...");
        exec("vercel --prod --force", { cwd: path.join(__dirname, '../..') }, (error, stdout, stderr) => {
            if (error) {
                console.error(`[CORTEX-EDGE-ERR] Vercel deployment failed: ${error.message}`);
                return;
            }
            console.log(`[CORTEX-EDGE-OK] Vercel deployment completed successfully.\n${stdout}`);
        });
    } else if (intensity < 5) {
        lastDeployTime = now;
        console.log("[CORTEX-EDGE] Reducing infrastructure footprint...");
        exec("vercel env rm OVERPROVISION_FLAG production", { cwd: path.join(__dirname, '../..') }, (error, stdout, stderr) => {
            if (error) {
                console.error(`[CORTEX-EDGE-ERR] Vercel env removal failed: ${error.message}`);
                return;
            }
            console.log(`[CORTEX-EDGE-OK] Vercel env footprint reduced.\n${stdout}`);
        });
    }
}
module.exports = { mutateInfra };
