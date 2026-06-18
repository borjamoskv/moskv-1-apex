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
  const isExposed = distanceToLaser < 0.25;
  
  const color = isDefect 
    ? (isExposed ? '#ff3b30' : '#8a1f1a') // Defecto: Rojo brillante / Rojo oscuro
    : (isExposed ? '#ffffff' : '#2b3be5'); // Operativo: Blanco brillante / Azul eléctrico

  const emissiveIntensity = isExposed ? 4 : (isDefect ? 0.3 : 0.8);
  const scaleY = isExposed ? 0.4 : 0.15;

  return (
    <mesh ref={meshRef} position={[x, 0.06, z]} scale={[0.22, scaleY, 0.22]}>
      <boxGeometry args={[1, 1, 1]} />
      <meshStandardMaterial 
        color={color} 
        emissive={color} 
        emissiveIntensity={emissiveIntensity}
        roughness={0.1}
        metalness={0.9}
      />
    </mesh>
  );
};

const Wafer3D: React.FC<{ sweepZ: number }> = ({ sweepZ }) => {
  const waferRef = useRef<THREE.Group>(null);
  const frame = useCurrentFrame();

  // Rotación suave del wafer entero
  useFrame(() => {
    if (waferRef.current) {
      waferRef.current.rotation.y = frame * 0.003;
    }
  });

  // Generar la matriz de chips sobre el wafer circular
  const chips = useMemo(() => {
    const grid: { id: string; x: number; z: number; isDefect: boolean }[] = [];
    const size = 18; // Cuadrícula de 18x18
    const radius = 3.2; // Radio del wafer en unidades 3D
    let index = 0;

    for (let r = 0; r < size; r++) {
      for (let c = 0; c < size; c++) {
        // Coordenadas locales centradas
        const x = (r - size / 2 + 0.5) * 0.35;
        const z = (c - size / 2 + 0.5) * 0.35;
        
        // Mantener solo los chips dentro del disco del wafer
        if (x * x + z * z <= radius * radius) {
          const rand = seededRandom(index + 42);
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
      {/* Oblea base de Silicio */}
      <mesh rotation={[-Math.PI / 2, 0, 0]} position={[0, 0, 0]}>
        <cylinderGeometry args={[3.3, 3.3, 0.08, 64]} />
        <meshStandardMaterial 
          color="#0f0f0f" 
          roughness={0.05} 
          metalness={0.95} 
        />
      </mesh>
      
      {/* Anillo exterior del Wafer */}
      <mesh rotation={[-Math.PI / 2, 0, 0]} position={[0, 0.01, 0]}>
        <ringGeometry args={[3.3, 3.35, 64]} />
        <meshStandardMaterial 
          color="#2b3be5" 
          emissive="#2b3be5" 
          emissiveIntensity={1.5} 
        />
      </mesh>

      {/* Rejilla de chips individuales */}
      {chips.map((chip) => (
        <Chip3D 
          key={chip.id} 
          x={chip.x} 
          z={chip.z} 
          isDefect={chip.isDefect} 
          sweepZ={sweepZ}
        />
      ))}

      {/* Línea Láser EUV (Haz físico) */}
      <mesh position={[0, 0.1, sweepZ]} scale={[6.6, 0.05, 0.08]}>
        <boxGeometry args={[1, 1, 1]} />
        <meshStandardMaterial 
          color="#ffffff" 
          emissive="#ffffff" 
          emissiveIntensity={5} 
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
  
  // Ritmo estroboscópico del Kick
  const isKick = frame % framesPerBeat < 3;
  
  // Animación del láser EUV barriendo la oblea (ciclo de 90 frames = 3 seg)
  const sweepZ = interpolate(
    frame % 90, 
    [0, 45, 90], 
    [-3.5, 3.5, -3.5],
    { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' }
  );

  // Escalar interfaz con el ritmo
  const beatScale = spring({
    frame: frame % framesPerBeat,
    fps,
    config: { damping: 12, mass: 0.5, stiffness: 300 }
  });

  const uiScale = interpolate(beatScale, [0, 1], [0.99, 1.01]);

  // Selección de texto de diagnóstico de litografía
  const uiTextOptions = [
    "ASML EUV 3400C // LITHOGRAPHY RUN",
    "YIELD ACTIVE RATE: 91.9%",
    "TSMC FAB 18 // HSINCHU SCIENCE PARK",
    "SUBSTRATE: DOPED SILICON WAFER 300MM",
    "SYS_STATUS: C5-REAL SOTA_KERNEL_RUNNING",
    "THERMODYNAMIC ENTROPY: MINIMIZED"
  ];
  const activeUIText = uiTextOptions[currentBeat % uiTextOptions.length];

  return (
    <AbsoluteFill style={{ backgroundColor: '#050505', overflow: 'hidden', fontFamily: 'Courier New, monospace' }}>
      {/* Audio sincronizado */}
      <Audio src={staticFile('kick_140.m4a')} />

      {/* Capa de rejilla técnica de fondo */}
      <div style={{
        position: 'absolute',
        top: 0, left: 0, right: 0, bottom: 0,
        backgroundImage: `
          linear-gradient(to right, rgba(43, 59, 229, 0.07) 1px, transparent 1px),
          linear-gradient(to bottom, rgba(43, 59, 229, 0.07) 1px, transparent 1px)
        `,
        backgroundSize: '40px 40px',
        pointerEvents: 'none'
      }} />

      {/* Canvas 3D de Silicio */}
      <div style={{ position: 'absolute', width: '100%', height: '100%', top: 0, left: 0 }}>
        <ThreeCanvas width={1920} height={1080} camera={{ position: [0, 4.2, 5.5], fov: 60 }}>
          <ambientLight intensity={0.15} />
          {/* Luz principal del láser que barre la oblea */}
          <pointLight 
            position={[0, 2, sweepZ]} 
            intensity={4} 
            color="#2b3be5" 
            distance={6}
          />
          {/* Luz de acento estroboscópica con el kick */}
          <pointLight 
            position={[5, 6, 2]} 
            intensity={isKick ? 6 : 1.5} 
            color="#ffffff" 
          />
          <pointLight 
            position={[-5, -2, -2]} 
            intensity={1} 
            color="#2b3be5" 
          />
          <Wafer3D sweepZ={sweepZ} />
        </ThreeCanvas>
      </div>

      {/* OVERLAY DE INTERFAZ TÉCNICA (HUD) */}
      <AbsoluteFill style={{ 
        pointerEvents: 'none', 
        padding: 50, 
        display: 'flex', 
        flexDirection: 'column', 
        justifyContent: 'space-between',
        transform: `scale(${uiScale})`
      }}>
        
        {/* Cabecera HUD */}
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
          <div>
            <div style={{ color: '#2b3be5', fontSize: 14, fontWeight: 'bold', letterSpacing: 2 }}>
              SYSTEM: MOSKV-1 APEX
            </div>
            <div style={{ color: '#ffffff', fontSize: 28, fontWeight: 900, marginTop: 5, letterSpacing: -1, textShadow: '0 0 10px rgba(43, 59, 229, 0.5)' }}>
              EL ESCUDO DE SILICIO
            </div>
          </div>
          
          <div style={{ textAlign: 'right' }}>
            <div style={{ color: '#fff', fontSize: 16, fontWeight: 'bold' }}>
              REALITY LEVEL: <span style={{ color: '#2b3be5' }}>C5-REAL</span>
            </div>
            <div style={{ color: 'rgba(255, 255, 255, 0.4)', fontSize: 12, marginTop: 4 }}>
              LEDGER_HASH: 17bb0d2
            </div>
          </div>
        </div>

        {/* Centro HUD: Glitch de Yield y Texto de Impacto */}
        <div style={{ 
          display: 'flex', 
          flexDirection: 'column', 
          alignItems: 'center', 
          justifyContent: 'center', 
          flexGrow: 1 
        }}>
          {currentBeat % 8 < 4 ? (
            <h2 style={{
              fontSize: 120,
              fontWeight: 900,
              color: '#ffffff',
              margin: 0,
              letterSpacing: -4,
              textAlign: 'center',
              textShadow: '0 0 20px rgba(255, 255, 255, 0.3)',
              fontFamily: 'Impact, sans-serif'
            }}>
              TAIWAN <span style={{ color: '#2b3be5', WebkitTextStroke: '2px #ffffff' }}>YIELD</span>
            </h2>
          ) : (
            <h2 style={{
              fontSize: 120,
              fontWeight: 900,
              color: '#2b3be5',
              margin: 0,
              letterSpacing: -4,
              textAlign: 'center',
              textShadow: '0 0 20px rgba(43, 59, 229, 0.5)',
              fontFamily: 'Impact, sans-serif'
            }}>
              91.9% <span style={{ color: '#ffffff' }}>EFICACIA</span>
            </h2>
          )}
          
          <div style={{
            color: '#fff',
            fontSize: 18,
            letterSpacing: 8,
            marginTop: 15,
            textTransform: 'uppercase',
            opacity: isKick ? 1 : 0.7,
            backgroundColor: 'rgba(43, 59, 229, 0.2)',
            padding: '4px 16px',
            border: '1px solid #2b3be5'
          }}>
            {isKick ? ">> EXPOSICIÓN LITOGRÁFICA EUV <<" : "LITHOGRAPHY SCAN ACTIVE"}
          </div>
        </div>

        {/* Pie de página HUD */}
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-end' }}>
          <div>
            <div style={{ color: 'rgba(255, 255, 255, 0.4)', fontSize: 11, letterSpacing: 1 }}>
              DIAGNOSTIC STATUS
            </div>
            <div style={{ color: '#ffffff', fontSize: 14, marginTop: 4, fontWeight: 'bold' }}>
              {activeUIText}
            </div>
          </div>
          
          <div style={{ display: 'flex', alignItems: 'center', gap: 20 }}>
            {/* Gráfico de barras decorativo de Yield */}
            <div style={{ display: 'flex', gap: 3, alignItems: 'flex-end', height: 30 }}>
              {[60, 80, 55, 90, 70, 95, 100, 85, 91.9].map((val, idx) => (
                <div 
                  key={idx} 
                  style={{ 
                    width: 6, 
                    height: `${val}%`, 
                    backgroundColor: idx === 8 ? '#fff' : '#2b3be5',
                    opacity: idx === 8 ? 1 : 0.6
                  }} 
                />
              ))}
            </div>
            <div style={{ textAlign: 'right' }}>
              <div style={{ color: '#2b3be5', fontSize: 20, fontWeight: 900 }}>
                91.9%
              </div>
              <div style={{ color: 'rgba(255, 255, 255, 0.4)', fontSize: 10 }}>
                YIELD METRIC
              </div>
            </div>
          </div>
        </div>

      </AbsoluteFill>

      {/* Efecto estroboscópico de contraste al ritmo del kick */}
      <div style={{
        position: 'absolute',
        top: 0, left: 0, right: 0, bottom: 0,
        backgroundColor: '#ffffff',
        opacity: isKick ? 0.04 : 0,
        pointerEvents: 'none',
        mixBlendMode: 'overlay'
      }} />

    </AbsoluteFill>
  );
};
