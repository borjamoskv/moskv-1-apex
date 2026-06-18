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
  sweepZ: number;
}

const Chip3D: React.FC<ChipProps> = ({ x, z, isDefect, sweepZ }) => {
  const meshRef = useRef<THREE.Mesh>(null);
  
  // Calcular distancia al láser para el efecto de exposición luminosa
  const distanceToLaser = Math.abs(z - sweepZ);
  const isExposed = distanceToLaser < 0.28;
  
  const color = isDefect 
    ? (isExposed ? '#ff3b30' : '#4a0f0c') // Defecto: Rojo vibrante / Granate apagado
    : (isExposed ? '#ffffff' : '#2b3be5'); // Operativo: Blanco puro / Azul cobalto

  const emissiveIntensity = isExposed ? 5 : (isDefect ? 0.2 : 0.6);
  const scaleY = isExposed ? 0.5 : 0.12;

  return (
    <mesh ref={meshRef} position={[x, 0.06, z]} scale={[0.16, scaleY, 0.16]}>
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
const LaserParticles: React.FC<{ sweepZ: number }> = ({ sweepZ }) => {
  const count = 180;
  const pointsRef = useRef<THREE.Points>(null);

  const [positions, scales] = useMemo(() => {
    const pos = new Float32Array(count * 3);
    const scl = new Float32Array(count);
    for (let i = 0; i < count; i++) {
      pos[i * 3] = (seededRandom(i) - 0.5) * 6.8; // Eje X a lo largo del wafer
      pos[i * 3 + 1] = 0.1 + seededRandom(i + 1) * 0.4; // Eje Y (altura del haz)
      pos[i * 3 + 2] = sweepZ + (seededRandom(i + 2) - 0.5) * 0.15; // Centrado en la línea de barrido
      scl[i] = seededRandom(i + 3);
    }
    return [pos, scl];
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

const Wafer3D: React.FC<{ sweepZ: number }> = ({ sweepZ }) => {
  const waferRef = useRef<THREE.Group>(null);
  const frame = useCurrentFrame();

  useFrame(() => {
    if (waferRef.current) {
      waferRef.current.rotation.y = frame * 0.002;
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
          roughness={0.1} 
          metalness={0.9} 
        />
      </mesh>
      
      {/* Conductor de Potencial (Anillo del Wafer) */}
      <mesh rotation={[-Math.PI / 2, 0, 0]} position={[0, 0.01, 0]}>
        <ringGeometry args={[3.3, 3.34, 64]} />
        <meshStandardMaterial 
          color="#2b3be5" 
          emissive="#2b3be5" 
          emissiveIntensity={2} 
        />
      </mesh>

      {/* Matriz de silicio monocristalino */}
      {chips.map((chip) => (
        <Chip3D 
          key={chip.id} 
          x={chip.x} 
          z={chip.z} 
          isDefect={chip.isDefect} 
          sweepZ={sweepZ}
        />
      ))}

      {/* Haz Láser EUV principal */}
      <mesh position={[0, 0.1, sweepZ]} scale={[6.6, 0.02, 0.04]}>
        <boxGeometry args={[1, 1, 1]} />
        <meshStandardMaterial 
          color="#ffffff" 
          emissive="#ffffff" 
          emissiveIntensity={8} 
        />
      </mesh>
    </group>
  );
};

export const SiliconTaiwanVideo: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const BPM = 140;
  const framesPerBeat = fps / (BPM / 60);
  const currentBeat = Math.floor(frame / framesPerBeat);
  const beatProgress = (frame % framesPerBeat) / framesPerBeat;
  
  const isKick = frame % framesPerBeat < 3;
  
  // Barrido armónico del láser EUV (90 frames)
  const sweepZ = interpolate(
    frame % 90, 
    [0, 45, 90], 
    [-3.4, 3.4, -3.4],
    { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' }
  );

  const beatScale = spring({
    frame: frame % framesPerBeat,
    fps,
    config: { damping: 10, mass: 0.4, stiffness: 350 }
  });

  const uiScale = interpolate(beatScale, [0, 1], [0.992, 1.008]);

  const uiTextOptions = [
    "ASML EUV 3400C // WAVE_LENGTH: 13.5NM",
    "YIELD ACTIVE RATE: 91.9% [C5-REAL]",
    "TSMC FAB 18 // ANISOTROPIC ETCHING",
    "SUBSTRATE: DOPED SILICON WAFER 300MM",
    "THERMODYNAMIC ENTROPY: OPTIMIZED",
    "HSINCHU CLUSTER // LATENCY_MINIMIZED"
  ];
  const activeUIText = uiTextOptions[currentBeat % uiTextOptions.length];

  return (
    <AbsoluteFill style={{ backgroundColor: '#020202', overflow: 'hidden', fontFamily: 'Courier New, monospace' }}>
      <Audio src={staticFile('kick_140.m4a')} />

      {/* Rejilla de diagnóstico */}
      <div style={{
        position: 'absolute',
        top: 0, left: 0, right: 0, bottom: 0,
        backgroundImage: `
          linear-gradient(to right, rgba(43, 59, 229, 0.05) 1px, transparent 1px),
          linear-gradient(to bottom, rgba(43, 59, 229, 0.05) 1px, transparent 1px)
        `,
        backgroundSize: '30px 30px',
        pointerEvents: 'none'
      }} />

      {/* Renderizado 3D */}
      <div style={{ position: 'absolute', width: '100%', height: '100%', top: 0, left: 0 }}>
        <ThreeCanvas width={1920} height={1080} camera={{ position: [0, 4.3, 5.3], fov: 60 }}>
          <ambientLight intensity={0.1} />
          <pointLight 
            position={[0, 1.8, sweepZ]} 
            intensity={5} 
            color="#2b3be5" 
            distance={7}
          />
          <pointLight 
            position={[4, 5, 2]} 
            intensity={isKick ? 8 : 2} 
            color="#ffffff" 
          />
          <pointLight 
            position={[-4, -1, -2]} 
            intensity={1.5} 
            color="#2b3be5" 
          />
          <Wafer3D sweepZ={sweepZ} />
          <LaserParticles sweepZ={sweepZ} />
        </ThreeCanvas>
      </div>

      {/* Capa estroboscópica de scanlines CRT analógicas */}
      <div style={{
        position: 'absolute',
        top: 0, left: 0, right: 0, bottom: 0,
        backgroundImage: 'linear-gradient(rgba(18, 16, 16, 0) 50%, rgba(0, 0, 0, 0.25) 50%)',
        backgroundSize: '100% 4px',
        pointerEvents: 'none',
        opacity: 0.4
      }} />

      {/* HUD de control */}
      <AbsoluteFill style={{ 
        pointerEvents: 'none', 
        padding: 60, 
        display: 'flex', 
        flexDirection: 'column', 
        justifyContent: 'space-between',
        transform: `scale(${uiScale})`
      }}>
        
        {/* Cabecera */}
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
          <div>
            <div style={{ color: '#2b3be5', fontSize: 13, fontWeight: 'bold', letterSpacing: 3 }}>
              SYSTEM STATUS: C5-REAL EXECUTION
            </div>
            <div style={{ color: '#ffffff', fontSize: 32, fontWeight: 900, marginTop: 6, letterSpacing: -1.5, textShadow: '0 0 12px rgba(43, 59, 229, 0.6)' }}>
              EL ESCUDO DE SILICIO
            </div>
          </div>
          
          <div style={{ textAlign: 'right' }}>
            <div style={{ color: '#fff', fontSize: 15, fontWeight: 'bold', letterSpacing: 1 }}>
              LEDGER_HASH: <span style={{ color: '#2b3be5' }}>17bb0d2</span>
            </div>
            <div style={{ color: 'rgba(255, 255, 255, 0.35)', fontSize: 11, marginTop: 4 }}>
              TSMC TIER 1 LITOGRAPHY
            </div>
          </div>
        </div>

        {/* Central */}
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

        {/* Pie de HUD */}
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
            <div style={{ display: 'flex', gap: 4, alignItems: 'flex-end', height: 40 }}>
              {[40, 75, 92, 50, 88, 91.9, 95, 80, 91.9].map((val, idx) => (
                <div 
                  key={idx} 
                  style={{ 
                    width: 5, 
                    height: `${val}%`, 
                    backgroundColor: idx === 8 ? '#ffffff' : '#2b3be5',
                    opacity: idx === 8 ? 1 : 0.5
                  }} 
                />
              ))}
            </div>
            <div style={{ textAlign: 'right' }}>
              <div style={{ color: '#2b3be5', fontSize: 24, fontWeight: 900, lineHeight: 1 }}>
                91.9%
              </div>
              <div style={{ color: 'rgba(255, 255, 255, 0.4)', fontSize: 9, marginTop: 3 }}>
                OPTIMAL YIELD
              </div>
            </div>
          </div>
        </div>

      </AbsoluteFill>

      {/* Contraste del estrobo del kick */}
      <div style={{
        position: 'absolute',
        top: 0, left: 0, right: 0, bottom: 0,
        backgroundColor: '#ffffff',
        opacity: isKick ? 0.05 : 0,
        pointerEvents: 'none',
        mixBlendMode: 'overlay'
      }} />

    </AbsoluteFill>
  );
};
