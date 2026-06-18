// C5-REAL CORE: Entropy Tracker, WebGL Shader, and WebAudio Theremin
document.addEventListener('DOMContentLoaded', () => {
  initTelemetry();
  initWebGL();
  initTheremin();
  initTdahSimulator();
});


// 1. Telemetry
function initTelemetry() {
  const coordsEl = document.getElementById('telemetry-coords');
  const entropyEl = document.getElementById('entropy-monitor');
  
  document.addEventListener('mousemove', (e) => {
    coordsEl.textContent = `X:${e.clientX} Y:${e.clientY}`;
    const entropy = (Math.random() * 0.05 + 0.95).toFixed(4);
    if (Math.random() > 0.9) {
      entropyEl.textContent = `ENTROPY: ${entropy}`;
    }
  });
}

// 2. WebGL Kinetic Noise (Brutalismo Cinético)
function initWebGL() {
  const canvas = document.getElementById('gl-canvas');
  const gl = canvas.getContext('webgl');
  if (!gl) return;

  function resize() {
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;
    gl.viewport(0, 0, canvas.width, canvas.height);
  }
  window.addEventListener('resize', resize);
  resize();

  const vsSource = `
    attribute vec2 position;
    void main() {
      gl_Position = vec4(position, 0.0, 1.0);
    }
  `;
  const fsSource = `
    precision highp float;
    uniform float time;
    uniform vec2 resolution;
    
    float random(vec2 st) {
      return fract(sin(dot(st.xy, vec2(12.9898,78.233))) * 43758.5453123);
    }
    
    void main() {
      vec2 st = gl_FragCoord.xy / resolution;
      float noise = random(st + time * 0.001);
      
      // Industrial Noir (#0A0A0A) to Accent (#2B3BE5) interpolation based on noise
      vec3 colorBg = vec3(0.04, 0.04, 0.04);
      vec3 colorAcc = vec3(0.17, 0.23, 0.90);
      
      float intensity = smoothstep(0.8, 1.0, noise) * 0.3;
      vec3 finalColor = mix(colorBg, colorAcc, intensity);
      
      gl_FragColor = vec4(finalColor, 1.0);
    }
  `;

  function createShader(type, source) {
    const shader = gl.createShader(type);
    gl.shaderSource(shader, source);
    gl.compileShader(shader);
    return shader;
  }

  const program = gl.createProgram();
  gl.attachShader(program, createShader(gl.VERTEX_SHADER, vsSource));
  gl.attachShader(program, createShader(gl.FRAGMENT_SHADER, fsSource));
  gl.linkProgram(program);
  gl.useProgram(program);

  const buffer = gl.createBuffer();
  gl.bindBuffer(gl.ARRAY_BUFFER, buffer);
  gl.bufferData(gl.ARRAY_BUFFER, new Float32Array([
    -1,-1,  1,-1, -1, 1,
    -1, 1,  1,-1,  1, 1
  ]), gl.STATIC_DRAW);

  const posLoc = gl.getAttribLocation(program, 'position');
  gl.enableVertexAttribArray(posLoc);
  gl.vertexAttribPointer(posLoc, 2, gl.FLOAT, false, 0, 0);

  const timeLoc = gl.getUniformLocation(program, 'time');
  const resLoc = gl.getUniformLocation(program, 'resolution');

  function render(time) {
    gl.uniform1f(timeLoc, time);
    gl.uniform2f(resLoc, canvas.width, canvas.height);
    gl.drawArrays(gl.TRIANGLES, 0, 6);
    requestAnimationFrame(render);
  }
  requestAnimationFrame(render);
}

// 3. Synthetic Theremin (Web Audio API)
function initTheremin() {
  const pad = document.getElementById('theremin-pad');
  if (!pad) return;

  const dot = document.createElement('div');
  dot.className = 'theremin-cursor-dot';
  pad.appendChild(dot);

  let audioCtx, osc, gainNode;
  let isPlaying = false;

  pad.addEventListener('mousedown', async (e) => {
    if (!audioCtx) {
      audioCtx = new (window.AudioContext || window.webkitAudioContext)();
      osc = audioCtx.createOscillator();
      gainNode = audioCtx.createGain();
      
      osc.type = 'sawtooth';
      osc.connect(gainNode);
      gainNode.connect(audioCtx.destination);
      osc.start();
    }
    
    if (audioCtx.state === 'suspended') {
      await audioCtx.resume();
    }
    
    gainNode.gain.setValueAtTime(0.1, audioCtx.currentTime);
    isPlaying = true;
    dot.classList.add('active');
    updateTheremin(e);
  });

  window.addEventListener('mouseup', () => {
    if (isPlaying && gainNode) {
      gainNode.gain.setTargetAtTime(0, audioCtx.currentTime, 0.05);
      isPlaying = false;
      dot.classList.remove('active');
    }
  });

  pad.addEventListener('mousemove', (e) => {
    if (isPlaying) {
      updateTheremin(e);
    }
  });

  function updateTheremin(e) {
    const rect = pad.getBoundingClientRect();
    let x = e.clientX - rect.left;
    let y = e.clientY - rect.top;
    
    x = Math.max(0, Math.min(x, rect.width));
    y = Math.max(0, Math.min(y, rect.height));

    dot.style.left = x + 'px';
    dot.style.top = y + 'px';

    const freq = 100 + (x / rect.width) * 1000;
    const detune = (1.0 - (y / rect.height)) * 1000;

    if (osc) {
      osc.frequency.setTargetAtTime(freq, audioCtx.currentTime, 0.05);
      osc.detune.setTargetAtTime(detune, audioCtx.currentTime, 0.05);
    }
  }
}

// 4. TDAH Cognitive Thrashing & Exergy Simulator
function initTdahSimulator() {
  const btnRun = document.getElementById('run-sim-btn');
  const btnReset = document.getElementById('reset-sim-btn');
  const btnToggleAdvanced = document.getElementById('advanced-toggle');
  const panelAdvanced = document.getElementById('advanced-params-panel');
  const checkForceSeed = document.getElementById('force-seed');
  
  const consoleEl = document.getElementById('sim-console');
  const stateIndicator = document.getElementById('sim-state-indicator');
  const tapeEl = document.getElementById('sim-tape');
  
  const elEfficiency = document.getElementById('sim-efficiency');
  const elEfficiencyFill = document.getElementById('sim-efficiency-fill');
  const elExergy = document.getElementById('sim-exergy');
  const elAnergy = document.getElementById('sim-anergy');
  
  const sliders = {
    activationProb: { input: document.getElementById('param-activation-prob'), display: document.getElementById('val-activation-prob'), suffix: '%' },
    switchProb: { input: document.getElementById('param-switch-prob'), display: document.getElementById('val-switch-prob'), suffix: '%' },
    hyperfocusProb: { input: document.getElementById('param-hyperfocus-prob'), display: document.getElementById('val-hyperfocus-prob'), suffix: '%' },
    activationCost: { input: document.getElementById('param-activation-cost'), display: document.getElementById('val-activation-cost'), suffix: ' A', divisor: 10 },
    switchCost: { input: document.getElementById('param-switch-cost'), display: document.getElementById('val-switch-cost'), suffix: ' A', divisor: 10 },
    hyperfocusMult: { input: document.getElementById('param-hyperfocus-mult'), display: document.getElementById('val-hyperfocus-mult'), suffix: 'x', divisor: 10 }
  };

  // Preset values
  const presets = {
    typical: {
      activationProb: 10,
      switchProb: 10,
      hyperfocusProb: 5,
      activationCost: 50, // 5.0
      switchCost: 20,     // 2.0
      hyperfocusMult: 25   // 2.5
    },
    tdah_raw: {
      activationProb: 60,
      switchProb: 45,
      hyperfocusProb: 25,
      activationCost: 50, // 5.0
      switchCost: 20,     // 2.0
      hyperfocusMult: 25   // 2.5
    },
    tdah_anchored: {
      activationProb: 15,
      switchProb: 15,
      hyperfocusProb: 20,
      activationCost: 20, // 2.0
      switchCost: 10,     // 1.0
      hyperfocusMult: 25   // 2.5
    }
  };

  // Sync slider inputs and value text displays
  Object.keys(sliders).forEach(key => {
    const s = sliders[key];
    if (s.input) {
      s.input.addEventListener('input', () => {
        let val = parseFloat(s.input.value);
        if (s.divisor) val = val / s.divisor;
        s.display.textContent = val + s.suffix;
      });
    }
  });

  // Advanced toggling
  if (btnToggleAdvanced && panelAdvanced) {
    btnToggleAdvanced.addEventListener('click', () => {
      panelAdvanced.classList.toggle('hidden');
      if (panelAdvanced.classList.contains('hidden')) {
        btnToggleAdvanced.textContent = '// CONFIGURACIÓN AVANZADA (COEFICIENTES) [+]';
      } else {
        btnToggleAdvanced.textContent = '// CONFIGURACIÓN AVANZADA (COEFICIENTES) [-]';
      }
    });
  }

  // Presets handling
  const presetButtons = document.querySelectorAll('.preset-btn');
  presetButtons.forEach(btn => {
    btn.addEventListener('click', () => {
      presetButtons.forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      const presetKey = btn.getAttribute('data-preset');
      const config = presets[presetKey];
      if (config) {
        Object.keys(config).forEach(key => {
          const s = sliders[key];
          if (s && s.input) {
            s.input.value = config[key];
            let val = config[key];
            if (s.divisor) val = val / s.divisor;
            s.display.textContent = val + s.suffix;
          }
        });
        appendLog(`[PRESET] Cambiado a perfil '${presetKey.toUpperCase()}'`, 'system');
      }
    });
  });

  let running = false;
  let animInterval = null;
  let seedValue = 42;

  function seededRandom() {
    const x = Math.sin(seedValue++) * 10000;
    return x - Math.floor(x);
  }

  function appendLog(text, className = '') {
    const line = document.createElement('p');
    line.className = `log-line ${className ? 'log-' + className : ''}`;
    line.textContent = text;
    consoleEl.appendChild(line);
    consoleEl.scrollTop = consoleEl.scrollHeight;
  }

  function updateTelemetry(work, overhead) {
    elExergy.textContent = work.toFixed(1) + " X";
    elAnergy.textContent = overhead.toFixed(1) + " A";
    
    const total = work + overhead;
    const eff = total > 0 ? (work / total) * 100 : 0;
    elEfficiency.textContent = eff.toFixed(2) + "%";
    elEfficiencyFill.style.width = eff.toFixed(1) + "%";
  }

  function resetSim() {
    if (animInterval) {
      clearInterval(animInterval);
      animInterval = null;
    }
    running = false;
    seedValue = 42;
    stateIndicator.textContent = 'STANDBY';
    stateIndicator.className = 'console-state-indicator';
    consoleEl.innerHTML = '';
    tapeEl.innerHTML = '';
    appendLog('[SYSTEM] Núcleo listo. Presione \'INICIAR INYECCIÓN CAUSAL\' para comenzar...', 'system');
    updateTelemetry(0, 0);
  }

  if (btnReset) {
    btnReset.addEventListener('click', resetSim);
  }

  if (btnRun) {
    btnRun.addEventListener('click', () => {
      if (running) {
        resetSim();
      }

      running = true;
      stateIndicator.textContent = 'RUNNING';
      stateIndicator.className = 'console-state-indicator running';
      consoleEl.innerHTML = '';
      tapeEl.innerHTML = '';
      appendLog('[SYSTEM] Inicializando simulación de exergía cognitiva...', 'system');
      appendLog('[SYSTEM] Conectando Ledger CORTEX (C5-REAL)...', 'system');
      
      const forceSeed = checkForceSeed ? checkForceSeed.checked : true;
      if (forceSeed) {
        seedValue = 42; // reset seed
        appendLog('[SEED] Semilla fijada en C5-REAL (42). Simulación determinista.', 'system');
      } else {
        appendLog('[SEED] Semilla dinámica activa. Caos estocástico habilitado.', 'system');
      }

      // Read current values
      const actProb = parseFloat(sliders.activationProb.input.value) / 100;
      const swProb = parseFloat(sliders.switchProb.input.value) / 100;
      const hypProb = parseFloat(sliders.hyperfocusProb.input.value) / 100;
      const actCost = parseFloat(sliders.activationCost.input.value) / 10;
      const swCost = parseFloat(sliders.switchCost.input.value) / 10;
      const hypMult = parseFloat(sliders.hyperfocusMult.input.value) / 10;

      let totalWork = 0;
      let totalOverhead = 0;
      const steps = 30;
      let step = 0;
      let inHyperfocus = false;
      let hyperfocusTimer = 0;
      let currentTaskIdx = 0;
      const tasks = ["AST Parsing", "WAL Sync", "BFT Consenso", "Memory Alloc"];

      function random() {
        return forceSeed ? seededRandom() : Math.random();
      }

      animInterval = setInterval(() => {
        step++;
        
        let stateClass = '';
        let glyph = '';
        let logMsg = '';
        let stepWork = 0;
        let stepOverhead = 0;

        // 1. Activation failure (Executive Dysfunction / Static Friction)
        if (!inHyperfocus && random() < actProb) {
          stateClass = 'friction';
          glyph = '░';
          stepOverhead = actCost;
          totalOverhead += actCost;
          logMsg = `[ciclo ${step}] ░ BARRERA: Fallo de activación ($E_act). Procrastinando...`;
          appendLog(logMsg, 'friction');
        } 
        // 2. Context switching (CPU Thrashing)
        else if (!inHyperfocus && random() < swProb) {
          currentTaskIdx = (currentTaskIdx + 1) % tasks.length;
          stateClass = 'thrashing';
          glyph = '⇄';
          stepOverhead = swCost;
          totalOverhead += swCost;
          logMsg = `[ciclo ${step}] ⇄ THRASHING: Cambio de contexto a '${tasks[currentTaskIdx]}'. Anergia disipada.`;
          appendLog(logMsg, 'thrashing');
        } 
        // 3. Execution (Nominal or Hyperfocus Resonance)
        else {
          // Trigger hyperfocus
          if (!inHyperfocus && random() < hypProb) {
            inHyperfocus = true;
            hyperfocusTimer = Math.floor(random() * 4) + 3; // 3 to 6 cycles
            appendLog(`[ciclo ${step}] █ RESONANCIA: ¡Frecuencia atencional acoplada! Hiperenfoque activo.`, 'hyperfocus');
          }

          if (inHyperfocus) {
            stepWork = hypMult;
            totalWork += hypMult;
            stateClass = 'hyperfocus';
            glyph = '█';
            logMsg = `[ciclo ${step}] █ EXERGÍA: Procesando '${tasks[currentTaskIdx]}' en resonancia (x${hypMult.toFixed(1)}).`;
            appendLog(logMsg, 'hyperfocus');
            
            hyperfocusTimer--;
            if (hyperfocusTimer <= 0) {
              inHyperfocus = false;
            }
          } else {
            stepWork = 1.0;
            totalWork += 1.0;
            stateClass = 'nominal';
            glyph = '▄';
            logMsg = `[ciclo ${step}] ▄ NOMINAL: Procesando '${tasks[currentTaskIdx]}' en estado base.`;
            appendLog(logMsg, 'work');
          }
        }

        // Add to timeline tape
        const block = document.createElement('div');
        block.className = `tape-block ${stateClass}`;
        block.textContent = glyph;
        tapeEl.appendChild(block);
        
        // Update telemetry values
        updateTelemetry(totalWork, totalOverhead);

        if (step >= steps) {
          clearInterval(animInterval);
          animInterval = null;
          running = false;
          stateIndicator.textContent = 'COMPLETED';
          stateIndicator.className = 'console-state-indicator';
          
          const finalEff = totalWork + totalOverhead > 0 ? (totalWork / (totalWork + totalOverhead)) * 100 : 0;
          appendLog(`[COMPLETADO] Simulación finalizada. Eficiencia global: ${finalEff.toFixed(2)}%`, 'system');
        }
      }, 150);
    });
  }
}

