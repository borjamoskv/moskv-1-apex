import React, { useRef, useMemo } from 'react';
import { useCurrentFrame, useVideoConfig, spring, interpolate, AbsoluteFill, random, Audio, staticFile } from 'remotion';
import { ThreeCanvas } from '@remotion/three';
import { useFrame } from '@react-three/fiber';
import * as THREE from 'three';

// Generador pseudo-aleatorio determinista para sembrar los defectos
const seededRandom = (seed: number) => {
  const x = Math.sin(seed) * 10000;
  return x - Math.floor(x);
};

interface ChipProps {
  x: number;
  z: number;
  isDefect: boolean;
  isExposed: boolean;
  isLaserActive: boolean;
  sweepZ: number;
}

const Chip3D: React.FC<ChipProps> = ({ x, z, isDefect, isExposed, isLaserActive, sweepZ }) => {
  const meshRef = useRef<THREE.Mesh>(null);
  
  // Efecto de incandescencia si el láser está justo encima de él
  const distanceToLaser = Math.abs(z - sweepZ);
  const isDirectlyUnderLaser = isLaserActive && distanceToLaser < 0.28;
  
  const color = isDefect 
    ? (isDirectlyUnderLaser ? '#ff3b30' : (isExposed ? '#8a1f1a' : '#1a0504')) // Defect: Bright Red / Dark Red / Silent Black-Red
    : (isDirectlyUnderLaser ? '#ffffff' : (isExposed ? '#2b3be5' : '#0a0a1f')); // Operative: Pure White / Electric Blue / Dark Blue-Gray

  const emissiveIntensity = isDirectlyUnderLaser ? 6 : (isExposed ? (isDefect ? 0.35 : 0.95) : 0.05);
  const scaleY = isDirectlyUnderLaser ? 0.45 : (isExposed ? 0.14 : 0.08);

  return (
    <mesh ref={meshRef} position={[x, 0.04, z]} scale={[0.16, scaleY, 0.16]}>
      <boxGeometry args={[1, 1, 1]} />
      <meshStandardMaterial 
        color={color} 
        emissive={color} 
        emissiveIntensity={emissiveIntensity}
        roughness={0.05}
        metalness={0.95}
      />
    </mesh>
  );
};

// Emisión física de plasma/partículas en el frente de contacto del láser EUV
const LaserParticles: React.FC<{ sweepZ: number; active: boolean }> = ({ sweepZ, active }) => {
  const count = 180;
  const pointsRef = useRef<THREE.Points>(null);

  const [positions] = useMemo(() => {
    const pos = new Float32Array(count * 3);
    for (let i = 0; i < count; i++) {
      pos[i * 3] = (seededRandom(i) - 0.5) * 6.8; // Eje X a lo largo del wafer
      pos[i * 3 + 1] = 0.1 + seededRandom(i + 1) * 0.4; // Eje Y (altura del haz)
      pos[i * 3 + 2] = sweepZ + (seededRandom(i + 2) - 0.5) * 0.15; // Centrado en la línea de barrido
    }
    return [pos];
  }, [sweepZ]);

  useFrame(() => {
    if (pointsRef.current) {
      const geo = pointsRef.current.geometry;
      const posAttr = geo.attributes.position as THREE.BufferAttribute;
      for (let i = 0; i < count; i++) {
        // Micro-excitación atómica en el plano Y
        const currentY = posAttr.getY(i);
        const nextY = currentY + (Math.random() - 0.5) * 0.05;
        posAttr.setY(i, Math.max(0.1, Math.min(0.6, nextY)));
      }
      posAttr.needsUpdate = true;
    }
  });

  if (!active) return null;

  return (
    <points ref={pointsRef}>
      <bufferGeometry>
        <bufferAttribute 
          attach="attributes-position" 
          args={[positions, 3]} 
        />
      </bufferGeometry>
      <pointsMaterial 
        color="#ffffff" 
        size={0.06} 
        transparent 
        opacity={0.9} 
        blending={THREE.AdditiveBlending}
      />
    </points>
  );
};

const Wafer3D: React.FC<{ 
  sweepZ: number; 
  isLaserActive: boolean; 
  frame: number; 
  isExposedFunc: (z: number) => boolean 
}> = ({ sweepZ, isLaserActive, frame, isExposedFunc }) => {
  const waferRef = useRef<THREE.Group>(null);

  useFrame(() => {
    if (waferRef.current) {
      waferRef.current.rotation.y = frame * 0.0018; // Rotación constante
    }
  });

  // Generar matriz de alta densidad (22x22)
  const chips = useMemo(() => {
    const grid: { id: string; x: number; z: number; isDefect: boolean }[] = [];
    const size = 22; 
    const radius = 3.25; 
    let index = 0;

    for (let r = 0; r < size; r++) {
      for (let c = 0; c < size; c++) {
        const x = (r - size / 2 + 0.5) * 0.28;
        const z = (c - size / 2 + 0.5) * 0.28;
        
        if (x * x + z * z <= radius * radius) {
          const rand = seededRandom(index + 101);
          // Tasa de defectos del 8.1% (TSMC Yield ~92%)
          const isDefect = rand < 0.081;
          
          grid.push({
            id: `chip-${r}-${c}`,
            x,
            z,
            isDefect,
          });
          index++;
        }
      }
    }
    return grid;
  }, []);

  return (
    <group ref={waferRef}>
      {/* Sustrato primario de Silicio */}
      <mesh rotation={[-Math.PI / 2, 0, 0]} position={[0, 0, 0]}>
        <cylinderGeometry args={[3.3, 3.3, 0.08, 64]} />
        <meshStandardMaterial 
          color="#060606" 
          roughness={0.12} 
          metalness={0.92} 
        />
      </mesh>
      
      {/* Conductor de Potencial (Anillo del Wafer) */}
      <mesh rotation={[-Math.PI / 2, 0, 0]} position={[0, 0.01, 0]}>
        <ringGeometry args={[3.3, 3.34, 64]} />
        <meshStandardMaterial 
          color="#2b3be5" 
          emissive="#2b3be5" 
          emissiveIntensity={1.8} 
        />
      </mesh>

      {/* Matriz de silicio monocristalino */}
      {chips.map((chip) => (
        <Chip3D 
          key={chip.id} 
          x={chip.x} 
          z={chip.z} 
          isDefect={chip.isDefect} 
          isExposed={isExposedFunc(chip.z)}
          isLaserActive={isLaserActive}
          sweepZ={sweepZ}
        />
      ))}

      {/* Haz Láser EUV principal */}
      {isLaserActive && (
        <mesh position={[0, 0.09, sweepZ]} scale={[6.6, 0.02, 0.04]}>
          <boxGeometry args={[1, 1, 1]} />
          <meshStandardMaterial 
            color="#ffffff" 
            emissive="#ffffff" 
            emissiveIntensity={8} 
          />
        </mesh>
      )}
    </group>
  );
};

export const SiliconTaiwanVideo: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const BPM = 140;
  const framesPerBeat = fps / (BPM / 60);
  const currentBeat = Math.floor(frame / framesPerBeat);
  const isKick = frame % framesPerBeat < 3;

  // --- ESCENARIO DE TIEMPO (VIDEOCLIP DE 60s / 1800 FRAMES) ---
  const inIntro = frame < 450;      // 0s a 15s
  const inBuild = frame >= 450 && frame < 900;   // 15s a 30s
  const inDrop = frame >= 900 && frame < 1440;   // 30s a 48s
  const inOutro = frame >= 1440;    // 48s a 60s

  // 1. DINÁMICA DEL LÁSER EUV (sweepZ & isLaserActive)
  const isLaserActive = inBuild || inDrop;
  
  let sweepZ = -3.5;
  if (inBuild) {
    // Un único barrido lento de abajo arriba (-3.4 a 3.4) a lo largo de 450 frames
    sweepZ = interpolate(frame, [450, 900], [-3.4, 3.4]);
  } else if (inDrop) {
    // Barrido rápido y agresivo de 90 frames (3 segundos por ciclo)
    sweepZ = interpolate(
      frame % 90, 
      [0, 45, 90], 
      [-3.4, 3.4, -3.4],
      { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' }
    );
  }

  // Función determinista de exposición de chips
  const isExposedFunc = (z: number) => {
    if (inIntro) return false;
    if (inBuild) {
      // Exposición progresiva conforme el láser avanza
      const currentLaserMaxZ = interpolate(frame, [450, 900], [-3.4, 3.4]);
      return z < currentLaserMaxZ;
    }
    // En el drop y outro, todo el wafer ya ha sido expuesto
    return true;
  };

  // 2. DINÁMICA DE CÁMERA (Pans & Shakes)
  let camX = 0, camY = 4.3, camZ = 5.3, camFov = 60;
  
  if (inIntro) {
    // Pan lento de izquierda a derecha y acercamiento progresivo
    camX = interpolate(frame, [0, 450], [-2.5, 1.8]);
    camY = interpolate(frame, [0, 450], [2.2, 3.4]);
    camZ = interpolate(frame, [0, 450], [3.2, 4.8]);
    camFov = interpolate(frame, [0, 450], [40, 58]);
  } else if (inBuild) {
    // Rotación de ángulo hacia la vista cenital estándar
    camX = interpolate(frame, [450, 900], [1.8, 0.0]);
    camY = interpolate(frame, [450, 900], [3.4, 4.3]);
    camZ = interpolate(frame, [450, 900], [4.8, 5.3]);
    camFov = interpolate(frame, [450, 900], [58, 60]);
  } else if (inDrop) {
    // Vista angular fija con sacudida sísmica sincronizada al bombo (Kick)
    const shake = isKick ? (random(frame) - 0.5) * 0.16 : 0;
    camX = shake;
    camY = 4.3 + shake;
    camZ = 5.3 + shake;
    camFov = isKick ? 57 : 60;
  } else if (inOutro) {
    // Zoom out hacia perspectiva cenital pura de 90 grados mirando abajo
    camX = 0;
    camY = interpolate(frame, [1440, 1650], [4.3, 6.8], { extrapolateRight: 'clamp' });
    camZ = interpolate(frame, [1440, 1650], [5.3, 0.001], { extrapolateRight: 'clamp' }); // Vista recta abajo
    camFov = interpolate(frame, [1440, 1650], [60, 52], { extrapolateRight: 'clamp' });
  }

  // 3. HUD TEXTS INTERACTIVOS POR SECCIÓN
  let hudSectionLabel = "INITIATING SYSTEM BOOT";
  let activeUIText = "WAITING FOR BEAM INIT // LITHOGRAPHY OFF";
  
  if (inIntro) {
    hudSectionLabel = "SYSTEM INITIALIZATION";
    activeUIText = `SYS_STATUS: CALIBRATING OPTICS (EUV_HAZ) // GRID_HASH: 17bb0d2`;
  } else if (inBuild) {
    hudSectionLabel = "LITHOGRAPHY INITIALIZED";
    activeUIText = `ASML EUV 3400C // WAVE_LENGTH: 13.5NM // SCAN_Z: ${sweepZ.toFixed(3)}`;
  } else if (inDrop) {
    hudSectionLabel = "MAXIMUM EXERGY RUN";
    const diagnosticTexts = [
      "YIELD RATE: 91.9% [C5-REAL ACTIVE]",
      "TSMC FAB 18 // TAIWAN CLUSTER ACTIVE",
      "ANISOTROPIC SILICON ETCHING RUNNING",
      "THERMODYNAMIC ENTROPY: OPTIMIZED",
      "EUV PLASMA PULSES: 100% INTENSITY"
    ];
    activeUIText = diagnosticTexts[currentBeat % diagnosticTexts.length];
  } else if (inOutro) {
    hudSectionLabel = "RUN COMPLETED SUCCESSFULLY";
    activeUIText = "THERMODYNAMIC INVARIANTS COMMITTED TO LEDGER BF9CB18";
  }

  const beatScale = spring({
    frame: frame % framesPerBeat,
    fps,
    config: { damping: 10, mass: 0.4, stiffness: 350 }
  });
  const uiScale = inDrop ? interpolate(beatScale, [0, 1], [0.985, 1.015]) : 1.0;

  return (
    <AbsoluteFill style={{ backgroundColor: '#020202', overflow: 'hidden', fontFamily: 'Courier New, monospace' }}>
      <Audio src={staticFile('silicon_loop.wav')} />

      {/* Rejilla de diagnóstico técnico */}
      <div style={{
        position: 'absolute',
        top: 0, left: 0, right: 0, bottom: 0,
        backgroundImage: `
          linear-gradient(to right, rgba(43, 59, 229, 0.05) 1px, transparent 1px),
          linear-gradient(to bottom, rgba(43, 59, 229, 0.05) 1px, transparent 1px)
        `,
        backgroundSize: '30px 30px',
        pointerEvents: 'none',
        opacity: inOutro ? interpolate(frame, [1440, 1600], [1.0, 0.15], { extrapolateRight: 'clamp' }) : 1.0
      }} />

      {/* Canvas 3D */}
      <div style={{ position: 'absolute', width: '100%', height: '100%', top: 0, left: 0 }}>
        <ThreeCanvas width={1920} height={1080} camera={{ position: [camX, camY, camZ], fov: camFov }}>
          <ambientLight intensity={0.1} />
          {isLaserActive && (
            <pointLight 
              position={[0, 1.8, sweepZ]} 
              intensity={5} 
              color="#2b3be5" 
              distance={7}
            />
          )}
          <pointLight 
            position={[4, 5, 2]} 
            intensity={inDrop && isKick ? 8 : (inIntro ? 0.8 : 2.5)} 
            color="#ffffff" 
          />
          <pointLight 
            position={[-4, -1, -2]} 
            intensity={inIntro ? 0.3 : 1.5} 
            color="#2b3be5" 
          />
          <Wafer3D 
            sweepZ={sweepZ} 
            isLaserActive={isLaserActive} 
            frame={frame} 
            isExposedFunc={isExposedFunc}
          />
          <LaserParticles sweepZ={sweepZ} active={isLaserActive} />
        </ThreeCanvas>
      </div>

      {/* Capa estroboscópica de scanlines CRT analógicas */}
      <div style={{
        position: 'absolute',
        top: 0, left: 0, right: 0, bottom: 0,
        backgroundImage: 'linear-gradient(rgba(18, 16, 16, 0) 50%, rgba(0, 0, 0, 0.25) 50%)',
        backgroundSize: '100% 4px',
        pointerEvents: 'none',
        opacity: inDrop ? 0.45 : 0.2
      }} />

      {/* HUD PRINCIPAL */}
      <AbsoluteFill style={{ 
        pointerEvents: 'none', 
        padding: 60, 
        display: 'flex', 
        flexDirection: 'column', 
        justifyContent: 'space-between',
        transform: `scale(${uiScale})`
      }}>
        
        {/* CABECERA */}
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
          <div>
            <div style={{ color: '#2b3be5', fontSize: 13, fontWeight: 'bold', letterSpacing: 3 }}>
              {hudSectionLabel}
            </div>
            <div style={{ color: '#ffffff', fontSize: 32, fontWeight: 900, marginTop: 6, letterSpacing: -1.5, textShadow: '0 0 12px rgba(43, 59, 229, 0.6)' }}>
              EL ESCUDO DE SILICIO
            </div>
          </div>
          
          <div style={{ textAlign: 'right' }}>
            <div style={{ color: '#fff', fontSize: 15, fontWeight: 'bold', letterSpacing: 1 }}>
              REALITY LEVEL: <span style={{ color: '#2b3be5' }}>C5-REAL</span>
            </div>
            <div style={{ color: 'rgba(255, 255, 255, 0.35)', fontSize: 11, marginTop: 4 }}>
              HASH: 17bb0d2 // bf9cb18
            </div>
          </div>
        </div>

        {/* CONTENIDOS TÍTULOS CENTRALES (INTRO Y OUTRO) */}
        {inIntro && (
          <div style={{ alignSelf: 'center', textAlign: 'center', maxWidth: 800 }}>
            <h3 style={{
              color: '#ffffff',
              fontSize: 24,
              letterSpacing: 8,
              textTransform: 'uppercase',
              margin: '0 0 15px 0',
              opacity: interpolate(frame, [0, 100, 350, 450], [0, 1, 1, 0])
            }}>
              TAIWAN LITOGRAPHY EPISODE
            </h3>
            <div style={{ 
              width: 300, 
              height: 2, 
              backgroundColor: '#2b3be5', 
              margin: '0 auto',
              transform: `scaleX(${interpolate(frame, [0, 350], [0, 1], { extrapolateRight: 'clamp' })})`
            }} />
          </div>
        )}

        {inOutro && (
          <div style={{ 
            alignSelf: 'center', 
            textAlign: 'center', 
            backgroundColor: 'rgba(2, 2, 2, 0.8)', 
            padding: '40px 60px',
            border: '2px solid #2b3be5',
            boxShadow: '0 0 30px rgba(43, 59, 229, 0.3)',
            opacity: interpolate(frame, [1440, 1550], [0, 1], { extrapolateLeft: 'clamp' })
          }}>
            <h2 style={{ color: '#ffffff', fontSize: 42, fontWeight: 900, margin: '0 0 10px 0', letterSpacing: -2 }}>
              LITHOGRAPHY COMPLETED
            </h2>
            <div style={{ color: '#2b3be5', fontSize: 28, fontWeight: 900, letterSpacing: 1 }}>
              FINAL YIELD: 91.9%
            </div>
            <div style={{ color: 'rgba(255, 255, 255, 0.4)', fontSize: 13, marginTop: 15, letterSpacing: 4 }}>
              HECHO EN TAIWÁN // ZERO ENTROPY
            </div>
          </div>
        )}

        {/* SECCIÓN INTERMITENTE RÍTMICA DEL DROP */}
        {inDrop && (
          <div style={{ 
            display: 'flex', 
            flexDirection: 'column', 
            alignItems: 'center', 
            justifyContent: 'center', 
            flexGrow: 1 
          }}>
            <h2 style={{
              fontSize: 140,
              fontWeight: 900,
              color: currentBeat % 8 < 4 ? '#ffffff' : '#2b3be5',
              margin: 0,
              letterSpacing: -5,
              textAlign: 'center',
              textShadow: '0 0 25px rgba(43, 59, 229, 0.4)',
              fontFamily: 'Impact, sans-serif'
            }}>
              {currentBeat % 8 < 4 ? "TAIWAN YIELD" : "91.9% EXERGÍA"}
            </h2>
            
            <div style={{
              color: '#fff',
              fontSize: 16,
              letterSpacing: 10,
              marginTop: 20,
              textTransform: 'uppercase',
              opacity: isKick ? 1 : 0.8,
              backgroundColor: 'rgba(10, 10, 10, 0.85)',
              borderLeft: '4px solid #2b3be5',
              padding: '6px 20px',
              textShadow: isKick ? '0 0 8px #fff' : 'none'
            }}>
              EUV TRANSISTOR EXPOSURE
            </div>
          </div>
        )}

        {/* PIE DE HUD */}
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-end' }}>
          <div>
            <div style={{ color: 'rgba(255, 255, 255, 0.3)', fontSize: 10, letterSpacing: 2 }}>
              LITHOGRAPHIC PROCESS METRIC
            </div>
            <div style={{ color: '#ffffff', fontSize: 13, marginTop: 5, fontWeight: 'bold' }}>
              {activeUIText}
            </div>
          </div>
          
          <div style={{ display: 'flex', alignItems: 'center', gap: 25 }}>
            {/* Medidor HUD de barras decorativo */}
            <div style={{ display: 'flex', gap: 4, alignItems: 'flex-end', height: 40 }}>
              {[40, 75, 92, 50, 88, 91.9, 95, 80, 91.9].map((val, idx) => {
                const isSelected = idx === 8;
                // Hacer parpadear las barras en el drop
                const heightVal = inIntro ? 15 : (inBuild ? val * (frame / 900) : val);
                return (
                  <div 
                    key={idx} 
                    style={{ 
                      width: 5, 
                      height: `${heightVal}%`, 
                      backgroundColor: isSelected ? '#ffffff' : '#2b3be5',
                      opacity: isSelected ? 1.0 : 0.5
                    }} 
                  />
                );
              })}
            </div>
            <div style={{ textAlign: 'right' }}>
              <div style={{ color: '#2b3be5', fontSize: 24, fontWeight: 900, lineHeight: 1 }}>
                {inIntro ? "BOOT" : "91.9%"}
              </div>
              <div style={{ color: 'rgba(255, 255, 255, 0.4)', fontSize: 9, marginTop: 3 }}>
                {inIntro ? "WAITING..." : "OPTIMAL YIELD"}
              </div>
            </div>
          </div>
        </div>

      </AbsoluteFill>

      {/* EFECTO DE FLASH DE ENTRADA AL DROP */}
      {frame >= 900 && frame < 908 && (
        <div style={{
          position: 'absolute',
          top: 0, left: 0, right: 0, bottom: 0,
          backgroundColor: '#ffffff',
          pointerEvents: 'none',
          opacity: interpolate(frame, [900, 908], [1.0, 0.0])
        }} />
      )}

      {/* Contraste estroboscópico al ritmo del kick */}
      <div style={{
        position: 'absolute',
        top: 0, left: 0, right: 0, bottom: 0,
        backgroundColor: '#ffffff',
        opacity: inDrop && isKick ? 0.06 : 0,
        pointerEvents: 'none',
        mixBlendMode: 'overlay'
      }} />

      {/* Fade out total a negro en los últimos 30 frames (59s a 60s) */}
      {frame >= 1770 && (
        <div style={{
          position: 'absolute',
          top: 0, left: 0, right: 0, bottom: 0,
          backgroundColor: '#000000',
          pointerEvents: 'none',
          opacity: interpolate(frame, [1770, 1800], [0.0, 1.0])
        }} />
      )}

    </AbsoluteFill>
  );
};
