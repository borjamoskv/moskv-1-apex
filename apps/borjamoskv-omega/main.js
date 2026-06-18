// C5-REAL CORE: Entropy Tracker, WebGL Shader, and WebAudio Theremin
document.addEventListener('DOMContentLoaded', () => {
  initTelemetry();
  initWebGL();
  initTheremin();
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
