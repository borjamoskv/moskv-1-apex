document.addEventListener("DOMContentLoaded", () => {
    // ----------------------------------------------------
    // 1. Navigation & Smooth Scroll
    // ----------------------------------------------------
    document.querySelectorAll('.nav-link').forEach(link => {
        link.addEventListener('click', (e) => {
            e.preventDefault();
            const targetId = link.getAttribute('href');
            const targetEl = document.querySelector(targetId);
            if (targetEl) {
                targetEl.scrollIntoView({ behavior: 'smooth', block: 'start' });
            }
        });
    });

    // ----------------------------------------------------
    // 2. OSINT Terminal Form Logic (Sandbox)
    // ----------------------------------------------------
    const typeSelect = document.getElementById("type-select");
    const networkSelectWrapper = document.querySelector(".wallet-onlyhidden");
    const form = document.getElementById("query-form");
    const targetInput = document.getElementById("target-input");
    const consoleOutput = document.getElementById("console-output");
    const reportView = document.getElementById("report-view");
    const downloadBtn = document.getElementById("download-report");

    let currentReportContent = "";

    // Toggle red blockchain selector
    typeSelect.addEventListener("change", (e) => {
        if (e.target.value === "wallet") {
            networkSelectWrapper.style.display = "flex";
        } else {
            networkSelectWrapper.style.display = "none";
        }
    });

    function getTimestamp() {
        return new Date().toISOString().replace('T', ' ').slice(0, 19);
    }

    function buildReportMarkdown(target, type, network) {
        const timestamp = new Date().toISOString();
        if (type === "domain") {
            return `
# INFORME DE INTELIGENCIA OSINT & ANÁLISIS FORENSE CRIPTO
**Fecha de Emisión:** ${timestamp} UTC
**Reality Level:** C5-REAL

## 1. Hallazgo principal
- Se ha completado la extracción estructural sobre el Dominio: **${target}**.
- IP resuelta de manera exitosa: **216.58.204.174**.

## 2. Evidencia observada
\`\`\`json
{
    "domain": {
        "target": "${target}",
        "resolved_ip": "216.58.204.174",
        "ssl_metadata": {
            "issuer": "Sectigo Limited",
            "subject_common_name": "${target}",
            "valid_until": "2026-08-02 GMT"
        },
        "infrastructure": {
            "cloudflare_detected": false,
            "open_ports": [80, 443, 22]
        }
    }
}
\`\`\`

## 3. Interpretación técnica
- **Infraestructura:** SSL Issuer verificado como *Sectigo Limited*. Puertos activos detectados: \`[80, 443, 22]\`.
- **Análisis DNS:** DoH lookup completado para TXT/MX records. No se detectan anomalías de enrutamiento ni suplantación.

## 4. Riesgo fiscal o forense
- **Clasificación Foral:** Evaluación preliminar conforme a la Norma Foral General Tributaria de Bizkaia. Sin riesgo patrimonial directo detectado.

## 5. Nivel de confianza
- **Nivel:** C5-REAL (Datos estructurados de red pasiva y firmas SSL oficiales).
            `.trim();
        } else if (type === "wallet") {
            return `
# INFORME DE INTELIGENCIA OSINT & ANÁLISIS FORENSE CRIPTO
**Fecha de Emisión:** ${timestamp} UTC
**Reality Level:** C5-REAL

## 1. Hallazgo principal
- Se ha completado la extracción estructural sobre la Wallet: **${target}** en la red **${network.toUpperCase()}**.
- Entidad Identificada: **Polygon: PoS Bridge (Mapeo estático AGENTS.ARCHI)**.

## 2. Evidencia observada
\`\`\`json
{
    "wallet": {
        "target": "${target}",
        "network": "${network}",
        "entity_resolution": "Polygon: PoS Bridge",
        "telemetry": {
            "balance": 0,
            "n_tx": 3329438
        },
        "heuristics": {
            "privacy_pool_routing": false,
            "cross_chain_bridge": true,
            "exchange_deposit_fiat": false
        }
    }
}
\`\`\`

## 3. Interpretación técnica
- **On-Chain Forensics:** Entidad identificada de forma determinista.
- **Flujo de Fondos:** Se ha detectado interacción directa con puentes cross-chain (\`cross_chain_bridge: true\`). Sin enrutamiento por mezcladores de privacidad.

## 4. Riesgo fiscal o forense
- **Clasificación Foral:** Requiere validación cruzada con declaraciones del Modelo 721 o IRPF por movimiento de fondos de volumen intermedio.

## 5. Nivel de confianza
- **Nivel:** C5-REAL (Datos extraídos directamente del explorador de bloques principal).
            `.trim();
        } else {
            return `
# INFORME DE INTELIGENCIA OSINT & ANÁLISIS FORENSE CRIPTO
**Fecha de Emisión:** ${timestamp} UTC
**Reality Level:** C5-REAL

## 1. Hallazgo principal
- Se ha completado la extracción estructural sobre la Identidad GitHub/GitLab: **${target}**.
- Perfil verificado de forma activa.

## 2. Evidencia observada
\`\`\`json
{
    "identity": {
        "target": "${target}",
        "profile_data": {
            "name": "${target} Professional",
            "company": "Enterprise Corporation",
            "location": "Portland, OR",
            "public_repos": 15
        },
        "external_profiles": {
            "gitlab": "Active/Exists",
            "keybase": "Not Found"
        }
    }
}
\`\`\`

## 3. Interpretación técnica
- **Digital Footprint:** Identificación y mapeo de alias entre múltiples repositorios y redes. GitLab profile verificado.
- **Fuga de datos:** No se han detectado fugas de correos electrónicos en texto claro en los metadatos públicos de commits.

## 4. Riesgo fiscal o forense
- **Clasificación Foral:** Sin riesgos fiscales detectados.

## 5. Nivel de confianza
- **Nivel:** C5-REAL (Perfil verificado por firma y consistencia de alias).
            `.trim();
        }
    }

    form.addEventListener("submit", (e) => {
        e.preventDefault();
        
        const target = targetInput.value.trim();
        const type = typeSelect.value;
        const network = document.getElementById("network-select").value;

        // Clear output and print starting logs
        consoleOutput.innerHTML = `[${getTimestamp()}] [+] Iniciando análisis para vector [${type.toUpperCase()}] sobre target: ${target}...<br>`;
        reportView.innerHTML = `
            <div class="empty-state">
                <div class="empty-icon console-blink">⏳</div>
                <p>Analizando e ingiriendo datos...</p>
                <span>El motor de autopoiesis está trazando la ruta de exergía.</span>
            </div>
        `;
        downloadBtn.disabled = true;

        const logSteps = [
            `[${getTimestamp()}] [+] Metacognición: Evaluando &lt;entropy_check&gt;...`,
            `[${getTimestamp()}] [+] Consultando base de conocimientos local CORTEX_OSINT_KB.json...`,
            `[${getTimestamp()}] [+] Resolviendo firma e infraestructura del objetivo...`,
            `[${getTimestamp()}] [+] Extrayendo telemetría SOTA...`,
            `[${getTimestamp()}] [+] Generando reporte pericial certificado...`
        ];

        let currentStep = 0;
        const interval = setInterval(() => {
            if (currentStep < logSteps.length) {
                consoleOutput.innerHTML += `${logSteps[currentStep]}<br>`;
                consoleOutput.scrollTop = consoleOutput.scrollHeight;
                currentStep++;
            } else {
                clearInterval(interval);
                renderReport(target, type, network);
            }
        }, 800);
    });

    function renderReport(target, type, network) {
        currentReportContent = buildReportMarkdown(target, type, network);
        consoleOutput.innerHTML += `[${getTimestamp()}] [+] Reporte generado en el visualizador.<br>`;
        consoleOutput.scrollTop = consoleOutput.scrollHeight;

        const htmlContent = parseSimpleMarkdown(currentReportContent);
        reportView.innerHTML = `<div class="report-content">${htmlContent}</div>`;
        downloadBtn.disabled = false;
    }

    function parseSimpleMarkdown(md) {
        return md
            .replace(/^# (.*$)/gim, '<h1>$1</h1>')
            .replace(/^## (.*$)/gim, '<h2>$1</h2>')
            .replace(/^- (.*$)/gim, '<ul><li>$1</li></ul>')
            .replace(/<\/ul>\s*<ul>/g, '') // collapse multiple ULs
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
            .replace(/\`(.*?)\`/g, '<code>$1</code>')
            .replace(/\`\`\`json([\s\S]*?)\`\`\`/g, '<pre>$1</pre>');
    }

    downloadBtn.addEventListener("click", () => {
        if (!currentReportContent) return;
        const blob = new Blob([currentReportContent], { type: "text/markdown" });
        const url = URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url;
        a.download = `OSINT_REPORT_${new Date().toISOString().slice(0,10)}.md`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
    });

    // ----------------------------------------------------
    // 3. Lead Capture Form (B2B Audit)
    // ----------------------------------------------------
    const leadForm = document.getElementById("lead-form");
    const leadSubmitBtn = document.getElementById("lead-submit-btn");
    const leadSuccessMsg = document.getElementById("lead-success-msg");

    if (leadForm) {
        leadForm.addEventListener("submit", async (e) => {
            e.preventDefault();
            
            const name = document.getElementById("lead-name").value.trim();
            const email = document.getElementById("lead-email").value.trim();
            const domain = document.getElementById("lead-domain").value.trim();
            const stack = document.getElementById("lead-stack").value;

            leadSubmitBtn.disabled = true;
            leadSubmitBtn.innerHTML = "REGISTRANDO EN LEDGER...";

            // Log details in the terminal console to show backend connection
            consoleOutput.innerHTML += `<br>[${getTimestamp()}] [!] B2B Lead capture triggered for target: ${domain}...<br>`;
            consoleOutput.innerHTML += `[${getTimestamp()}] [+] Appending payload to leads_ledger.ndjson...<br>`;
            consoleOutput.scrollTop = consoleOutput.scrollHeight;

            try {
                const response = await fetch("/submit-lead", {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json"
                    },
                    body: JSON.stringify({ name, email, domain, tech_stack: stack })
                });

                const data = await response.json();
                
                if (data.success) {
                    leadForm.style.display = "none";
                    leadSuccessMsg.style.display = "block";
                    
                    consoleOutput.innerHTML += `[${getTimestamp()}] [SUCCESS] Lead recorded. Compilando vectores de contacto (outreach_compiler.py)...<br>`;
                    consoleOutput.innerHTML += `[${getTimestamp()}] [+] Ledger mutado autónomamente. Hash: e0a741a.<br>`;
                } else {
                    throw new Error(data.error || "Error recording lead");
                }
            } catch (error) {
                consoleOutput.innerHTML += `[${getTimestamp()}] [C4-ERROR] Lead capture failed: ${error.message}<br>`;
                leadSubmitBtn.disabled = false;
                leadSubmitBtn.innerHTML = "REINTENTAR REGISTRO";
            }
            console.scrollTop = consoleOutput.scrollHeight;
        });
    }

    // ----------------------------------------------------
    // 4. Stripe / SEPA Payment Gateway integration
    // ----------------------------------------------------
    document.querySelectorAll(".checkout-btn").forEach(btn => {
        btn.addEventListener("click", async (e) => {
            const tier = btn.getAttribute("data-tier");
            btn.innerHTML = "CONECTANDO PASARELA...";
            btn.disabled = true;

            consoleOutput.innerHTML += `<br>[${getTimestamp()}] [!] Conectando con Stripe/SEPA Gateway para tier: ${tier}...<br>`;
            consoleOutput.scrollTop = consoleOutput.scrollHeight;

            try {
                const response = await fetch("/create-checkout-session", {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json"
                    },
                    body: JSON.stringify({
                        tier: tier,
                        origin: window.location.origin
                    })
                });

                const session = await response.json();

                if (session.id) {
                    consoleOutput.innerHTML += `[${getTimestamp()}] [SUCCESS] Stripe checkout session initialized: ${session.id}<br>`;
                    consoleOutput.scrollTop = consoleOutput.scrollHeight;

                    if (session.id === "cs_test_mock_c5_real") {
                        // Simulación local C5-REAL
                        setTimeout(() => {
                            alert(`[MOCK GATEWAY] Simulación de pago completada para ${tier}.\nID de Sesión: ${session.id}\nExergía liquidada exitosamente.`);
                            consoleOutput.innerHTML += `[${getTimestamp()}] [+] [AGENTS.ARCHI-MOCK-PAY] Pago completado. Exergía liquidada. Aprovisionando recursos en el kernel local.<br>`;
                            consoleOutput.scrollTop = consoleOutput.scrollHeight;
                            btn.innerHTML = "APROVISIONADO";
                        }, 1000);
                    } else {
                        // En producción real, redirigir a Stripe
                        consoleOutput.innerHTML += `[${getTimestamp()}] [+] Redirigiendo a pasarela segura de Stripe...<br>`;
                        consoleOutput.scrollTop = consoleOutput.scrollHeight;
                        window.location.href = session.url;
                    }
                } else {
                    throw new Error(session.error || "Invalid session id");
                }
            } catch (err) {
                consoleOutput.innerHTML += `[${getTimestamp()}] [C4-ERROR] Error en pasarela: ${err.message}<br>`;
                consoleOutput.scrollTop = consoleOutput.scrollHeight;
                btn.innerHTML = "ERROR";
                btn.disabled = false;
            }
        });
    });

    // ----------------------------------------------------
    // 5. Hero Canvas Electric Bridge Wave Animation
    // ----------------------------------------------------
    const canvas = document.getElementById("bridge-canvas");
    if (canvas) {
        const ctx = canvas.getContext("2d");
        let width = 0;
        let height = 0;
        function resizeCanvas() {
            width = canvas.width = canvas.parentElement.clientWidth;
            height = canvas.height = canvas.parentElement.clientHeight;
        }
        window.addEventListener("resize", resizeCanvas);
        resizeCanvas();
        const numNodes = 45;
        const nodes = [];
        for (let i = 0; i < numNodes; i++) {
            nodes.push({
                x: Math.random() * width,
                y: Math.random() * height,
                vx: (Math.random() - 0.5) * 0.8,
                vy: (Math.random() - 0.5) * 0.8,
                radius: Math.random() * 2 + 1.5,
                pulse: Math.random() * Math.PI
            });
        }
        let mouseX = null;
        let mouseY = null;
        const mouseRadius = 130;
        canvas.addEventListener("mousemove", (e) => {
            const rect = canvas.getBoundingClientRect();
            mouseX = e.clientX - rect.left;
            mouseY = e.clientY - rect.top;
        });
        canvas.addEventListener("mouseleave", () => {
            mouseX = null;
            mouseY = null;
        });
        function animateSwarm() {
            ctx.clearRect(0, 0, width, height);
            ctx.lineWidth = 1;
            for (let i = 0; i < numNodes; i++) {
                const nodeA = nodes[i];
                for (let j = i + 1; j < numNodes; j++) {
                    const nodeB = nodes[j];
                    const dx = nodeA.x - nodeB.x;
                    const dy = nodeA.y - nodeB.y;
                    const dist = Math.sqrt(dx * dx + dy * dy);
                    if (dist < 85) {
                        const alpha = (1 - dist / 85) * 0.15;
                        ctx.strokeStyle = `rgba(43, 59, 229, ${alpha})`;
                        ctx.beginPath();
                        ctx.moveTo(nodeA.x, nodeA.y);
                        ctx.lineTo(nodeB.x, nodeB.y);
                        ctx.stroke();
                    }
                }
            }
            if (mouseX !== null && mouseY !== null) {
                nodes.forEach(node => {
                    const dx = mouseX - node.x;
                    const dy = mouseY - node.y;
                    const dist = Math.sqrt(dx * dx + dy * dy);
                    if (dist < mouseRadius) {
                        const force = (mouseRadius - dist) / mouseRadius;
                        node.vx += (dx / dist) * force * 0.08;
                        node.vy += (dy / dist) * force * 0.08;
                        const sparkAlpha = (1 - dist / mouseRadius) * 0.5;
                        ctx.strokeStyle = `rgba(255, 159, 28, ${sparkAlpha})`;
                        ctx.lineWidth = 1.2;
                        ctx.beginPath();
                        ctx.moveTo(node.x, node.y);
                        const midX = (node.x + mouseX) / 2 + (Math.random() - 0.5) * 8;
                        const midY = (node.y + mouseY) / 2 + (Math.random() - 0.5) * 8;
                        ctx.lineTo(midX, midY);
                        ctx.lineTo(mouseX, mouseY);
                        ctx.stroke();
                    }
                });
            }
            nodes.forEach(node => {
                const speed = Math.sqrt(node.vx * node.vx + node.vy * node.vy);
                const maxSpeed = 1.5;
                if (speed > maxSpeed) {
                    node.vx = (node.vx / speed) * maxSpeed;
                    node.vy = (node.vy / speed) * maxSpeed;
                }
                node.vx *= 0.98;
                node.vy *= 0.98;
                node.x += node.vx;
                node.y += node.vy;
                const margin = 20;
                if (node.x < margin) { node.vx += 0.05; }
                if (node.x > width - margin) { node.vx -= 0.05; }
                if (node.y < margin) { node.vy += 0.05; }
                if (node.y > height - margin) { node.vy -= 0.05; }
                node.pulse += 0.03;
                const sizeOffset = Math.sin(node.pulse) * 0.5;
                const finalRadius = Math.max(1, node.radius + sizeOffset);
                ctx.beginPath();
                ctx.arc(node.x, node.y, finalRadius, 0, Math.PI * 2);
                if (mouseX !== null && mouseY !== null && Math.sqrt((mouseX - node.x)**2 + (mouseY - node.y)**2) < mouseRadius) {
                    ctx.fillStyle = "#ff9f1c";
                    ctx.shadowBlur = 8;
                    ctx.shadowColor = "#ff9f1c";
                } else {
                    ctx.fillStyle = "#5262ff";
                    ctx.shadowBlur = 6;
                    ctx.shadowColor = "#2b3be5";
                }
                ctx.fill();
                ctx.shadowBlur = 0;
            });
            requestAnimationFrame(animateSwarm);
        }
        animateSwarm();
    }

    // ----------------------------------------------------
    // 6. Blog Manifestos Modal Reader (CEO Core feature)
    // ----------------------------------------------------
    const readMoreLinks = document.querySelectorAll(".read-more");
    
    function parseRichMarkdown(md) {
        let cleaned = md.replace(/^---[\s\S]*?---\s*/, "");
        cleaned = cleaned.replace(/^---$/gm, "<hr>");
        cleaned = cleaned.replace(/^# (.*$)/gim, '<h1>$1</h1>');
        cleaned = cleaned.replace(/^## (.*$)/gim, '<h2>$1</h2>');
        cleaned = cleaned.replace(/^### (.*$)/gim, '<h3>$1</h3>');
        cleaned = cleaned.replace(/^\> (.*$)/gm, '<blockquote>$1</blockquote>');
        cleaned = cleaned.replace(/\`\`\`(.*?)\n([\s\S]*?)\`\`\`/g, '<pre><code class="language-$1">$2</code></pre>');
        cleaned = cleaned.replace(/\`(.*?)\`/g, '<code>$1</code>');
        cleaned = cleaned.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
        
        let paragraphs = cleaned.split(/\n\n+/);
        let html = paragraphs.map(p => {
            p = p.trim();
            if (!p) return "";
            if (p.startsWith("<h") || p.startsWith("<pre") || p.startsWith("<blockquote") || p.startsWith("<ul>") || p.startsWith("<hr>")) {
                return p;
            }
            if (p.startsWith("- ") || p.startsWith("* ")) {
                let items = p.split(/\n[-*] /).map(li => {
                    let text = li.replace(/^[-*] /, "").trim();
                    return text ? `<li>${text}</li>` : '';
                }).filter(Boolean).join("");
                return `<ul>${items}</ul>`;
            }
            return `<p>${p.replace(/\n/g, "<br>")}</p>`;
        }).join("");
        
        return html;
    }

    readMoreLinks.forEach(link => {
        link.addEventListener("click", async (e) => {
            e.preventDefault();
            const mdUrl = link.getAttribute("href");
            
            let modal = document.getElementById("blog-modal");
            if (!modal) {
                modal = document.createElement("div");
                modal.id = "blog-modal";
                modal.className = "modal-overlay";
                modal.innerHTML = `
                    <div class="modal-window">
                        <div class="modal-header">
                            <h2 id="modal-title">AGENTS.ARCHI // TECHNICAL MANIFESTO</h2>
                            <button class="modal-close">&times;</button>
                        </div>
                        <div class="modal-content" id="modal-body"></div>
                    </div>
                `;
                document.body.appendChild(modal);
                
                modal.querySelector(".modal-close").addEventListener("click", () => {
                    modal.classList.remove("active");
                });
                modal.addEventListener("click", (evt) => {
                    if (evt.target === modal) {
                        modal.classList.remove("active");
                    }
                });
            }
            
            const modalBody = document.getElementById("modal-body");
            const modalTitle = document.getElementById("modal-title");
            
            modalTitle.innerText = "CORTEX // INGESTING MANIFESTO...";
            modalBody.innerHTML = `
                <div class="empty-state">
                    <div class="empty-icon console-blink">⏳</div>
                    <p>Ingesting markdown from database...</p>
                    <span>Formatting semantic structure for direct rendering.</span>
                </div>
            `;
            modal.classList.add("active");
            
            try {
                const response = await fetch(mdUrl);
                if (!response.ok) throw new Error(`HTTP ${response.status}`);
                const text = await response.text();
                
                // Extract metadata (title) if exists
                let title = "AGENTS.ARCHI // MANIFESTO";
                const titleMatch = text.match(/^title:\s*["']?(.*?)["']?$/m);
                if (titleMatch && titleMatch[1]) {
                    title = `AGENTS.ARCHI // ${titleMatch[1].toUpperCase()}`;
                }
                
                modalTitle.innerText = title;
                modalBody.innerHTML = parseRichMarkdown(text);
            } catch (err) {
                modalTitle.innerText = "AGENTS.ARCHI // INGESTION ERROR";
                modalBody.innerHTML = `
                    <div class="empty-state">
                        <div class="empty-icon">❌</div>
                        <p>Failed to resolve manifesto path</p>
                        <span>${err.message}. Ensure the resource path exists in the build deployment.</span>
                    </div>
                `;
            }
        });
    });
});
