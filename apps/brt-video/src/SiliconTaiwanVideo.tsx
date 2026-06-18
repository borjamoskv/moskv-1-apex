import React, { useRef, useMemo } from 'react';
import { useCurrentFrame, useVideoConfig, spring, interpolate, AbsoluteFill, random, Audio, staticFile, Img } from 'remotion';
import { ThreeCanvas } from '@remotion/three';
import { useFrame } from '@react-three/fiber';
import * as THREE from 'three';

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
  const distanceToLaser = Math.abs(z - sweepZ);
  const isDirectlyUnderLaser = isLaserActive && distanceToLaser < 0.28;
  
  const color = isDefect 
    ? (isDirectlyUnderLaser ? '#ff3b30' : (isExposed ? '#8a1f1a' : '#1a0504'))
    : (isDirectlyUnderLaser ? '#ffffff' : (isExposed ? '#2b3be5' : '#0a0a1f'));

  const emissiveIntensity = isDirectlyUnderLaser ? 6 : (isExposed ? (isDefect ? 0.35 : 0.95) : 0.05);
  const scaleY = isDirectlyUnderLaser ? 0.45 : (isExposed ? 0.14 : 0.08);

  return (
    <mesh ref={meshRef} position={[x, 0.04, z]} scale={[0.16, scaleY, 0.16]}>
      <boxGeometry args={[1, 1, 1]} />
      <meshStandardMaterial color={color} emissive={color} emissiveIntensity={emissiveIntensity} roughness={0.05} metalness={0.95} />
    </mesh>
  );
};

const Oscilloscope: React.FC<{ frame: number; inDrop: boolean; isKick: boolean }> = ({ frame, inDrop, isKick }) => {
  const wavePoints = useMemo(() => {
    return Array.from({ length: 100 }).map((_, i) => {
      const x = i * 3;
      const freq = inDrop ? (isKick ? 0.4 : 0.15) : 0.05;
      const amp = inDrop ? (isKick ? 45 : 18) : 5;
      const y = 50 + Math.sin(i * freq + frame * 0.3) * amp + (Math.random() - 0.5) * (isKick ? 15 : 2);
      return `${x},${y}`;
    }).join(' ');
  }, [frame, inDrop, isKick]);

  return (
    <div style={{ position: 'absolute', top: '50%', left: '50%', transform: 'translate(-50%, -50%)', width: 300, height: 100, opacity: 0.85, pointerEvents: 'none' }}>
      <svg width="100%" height="100%" viewBox="0 0 300 100">
        <path d="M 0,50 L 300,50" stroke="rgba(43, 59, 229, 0.4)" strokeWidth="1" strokeDasharray="2 4" />
        <path d="M 150,0 L 150,100" stroke="rgba(43, 59, 229, 0.4)" strokeWidth="1" strokeDasharray="2 4" />
        <circle cx="150" cy="50" r="40" fill="none" stroke="rgba(255,255,255,0.15)" strokeDasharray="4 4" />
        <circle cx="150" cy="50" r="8" fill="none" stroke="#ff3b30" strokeWidth="1" />
        <path d="M 140,50 L 160,50 M 150,40 L 150,60" stroke="#ff3b30" strokeWidth="1" />
        <polyline points={wavePoints} fill="none" stroke={isKick ? "#ffffff" : "#2b3be5"} strokeWidth={isKick ? 2.5 : 1.5} style={{ filter: 'drop-shadow(0 0 6px rgba(43,59,229,0.8))' }} />
      </svg>
      <div style={{ position: 'absolute', top: -20, left: 0, color: '#2b3be5', fontSize: 10, fontFamily: 'monospace' }}>RADAR_VEC // {isKick ? 'PEAK' : 'IDLE'}</div>
      <div style={{ position: 'absolute', bottom: -20, right: 0, color: '#ff3b30', fontSize: 10, fontFamily: 'monospace' }}>C5-REAL_TELEMETRY</div>
    </div>
  );
};

const LaserParticles: React.FC<{ sweepZ: number; active: boolean }> = ({ sweepZ, active }) => {
  const count = 220;
  const pointsRef = useRef<THREE.Points>(null);

  const [positions, colors] = useMemo(() => {
    const pos = new Float32Array(count * 3);
    const col = new Float32Array(count * 3);
    for (let i = 0; i < count; i++) {
      pos[i * 3] = (seededRandom(i) - 0.5) * 6.8;
      pos[i * 3 + 1] = 0.1 + seededRandom(i + 1) * 0.4;
      pos[i * 3 + 2] = sweepZ + (seededRandom(i + 2) - 0.5) * 0.15;
      
      const isCore = seededRandom(i + 3) > 0.5;
      col[i * 3] = isCore ? 1.0 : 0.17;
      col[i * 3 + 1] = isCore ? 1.0 : 0.23;
      col[i * 3 + 2] = isCore ? 1.0 : 0.90;
    }
    return [pos, col];
  }, [sweepZ]);

  useFrame(() => {
    if (pointsRef.current) {
      const geo = pointsRef.current.geometry;
      const posAttr = geo.attributes.position as THREE.BufferAttribute;
      for (let i = 0; i < count; i++) {
        const currentY = posAttr.getY(i);
        const nextY = currentY + (Math.random() - 0.5) * 0.08;
        posAttr.setY(i, Math.max(0.1, Math.min(0.8, nextY)));
      }
      posAttr.needsUpdate = true;
    }
  });

  if (!active) return null;

  return (
    <points ref={pointsRef}>
      <bufferGeometry>
        <bufferAttribute attach="attributes-position" args={[positions, 3]} />
        <bufferAttribute attach="attributes-color" args={[colors, 3]} />
      </bufferGeometry>
      <pointsMaterial size={0.08} vertexColors transparent opacity={0.9} blending={THREE.AdditiveBlending} />
    </points>
  );
};

const Wafer3D: React.FC<{ sweepZ: number; isLaserActive: boolean; frame: number; isExposedFunc: (z: number) => boolean }> = ({ sweepZ, isLaserActive, frame, isExposedFunc }) => {
  const waferRef = useRef<THREE.Group>(null);
  useFrame(() => { if (waferRef.current) waferRef.current.rotation.y = frame * 0.0018; });

  const chips = useMemo(() => {
    const grid: { id: string; x: number; z: number; isDefect: boolean }[] = [];
    let index = 0;
    for (let r = 0; r < 22; r++) {
      for (let c = 0; c < 22; c++) {
        const x = (r - 11 + 0.5) * 0.28;
        const z = (c - 11 + 0.5) * 0.28;
        if (x * x + z * z <= 10.56) {
          grid.push({ id: `chip-${r}-${c}`, x, z, isDefect: seededRandom(index + 101) < 0.081 });
          index++;
        }
      }
    }
    return grid;
  }, []);

  return (
    <group ref={waferRef}>
      <mesh rotation={[-Math.PI / 2, 0, 0]} position={[0, 0, 0]}>
        <cylinderGeometry args={[3.3, 3.3, 0.08, 64]} />
        <meshStandardMaterial color="#060606" roughness={0.12} metalness={0.92} />
      </mesh>
      <mesh rotation={[-Math.PI / 2, 0, 0]} position={[0, 0.01, 0]}>
        <ringGeometry args={[3.3, 3.34, 64]} />
        <meshStandardMaterial color="#2b3be5" emissive="#2b3be5" emissiveIntensity={1.8} />
      </mesh>
      {chips.map((chip) => (
        <Chip3D key={chip.id} x={chip.x} z={chip.z} isDefect={chip.isDefect} isExposed={isExposedFunc(chip.z)} isLaserActive={isLaserActive} sweepZ={sweepZ} />
      ))}
      {isLaserActive && (
        <mesh position={[0, 0.09, sweepZ]} scale={[6.6, 0.02, 0.04]}>
          <boxGeometry args={[1, 1, 1]} />
          <meshStandardMaterial color="#ffffff" emissive="#ffffff" emissiveIntensity={8} />
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

  const inIntro = frame < 450;
  const inBuild = frame >= 450 && frame < 900;
  const inDrop = frame >= 900 && frame < 1440;
  const inOutro = frame >= 1440;

  const isLaserActive = inBuild || inDrop;
  
  let sweepZ = -3.5;
  if (inBuild) sweepZ = interpolate(frame, [450, 900], [-3.4, 3.4]);
  else if (inDrop) sweepZ = interpolate(frame % 90, [0, 45, 90], [-3.4, 3.4, -3.4], { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' });

  const isExposedFunc = (z: number) => {
    if (inIntro) return false;
    if (inBuild) return z < interpolate(frame, [450, 900], [-3.4, 3.4]);
    return true;
  };

  let camX = 0, camY = 4.3, camZ = 5.3, camFov = 60, camRoll = 0;
  
  if (inIntro) {
    camX = interpolate(frame, [0, 450], [-2.5, 1.8]);
    camY = interpolate(frame, [0, 450], [2.2, 3.4]);
    camZ = interpolate(frame, [0, 450], [3.2, 4.8]);
    camFov = interpolate(frame, [0, 450], [40, 58]);
  } else if (inBuild) {
    camX = interpolate(frame, [450, 900], [1.8, 0.0]);
    camY = interpolate(frame, [450, 900], [3.4, 4.3]);
    camZ = interpolate(frame, [450, 900], [4.8, 5.3]);
    camFov = interpolate(frame, [450, 900], [58, 60]);
  } else if (inDrop) {
    const shake = isKick ? (random(frame) - 0.5) * 0.28 : 0;
    camX = shake;
    camY = 4.3 + shake;
    camZ = 5.3 + shake;
    camFov = isKick ? 54 : 60;
    camRoll = Math.sin(frame * 0.15) * 0.2 + (isKick ? (random(frame+1) - 0.5) * 0.15 : 0);
  } else if (inOutro) {
    camX = 0;
    camY = interpolate(frame, [1440, 1650], [4.3, 6.8], { extrapolateRight: 'clamp' });
    camZ = interpolate(frame, [1440, 1650], [5.3, 0.001], { extrapolateRight: 'clamp' });
    camFov = interpolate(frame, [1440, 1650], [60, 52], { extrapolateRight: 'clamp' });
    camRoll = interpolate(frame, [1440, 1600], [0, Math.PI / 4], { extrapolateRight: 'clamp' });
  }

  const beatScale = spring({ frame: frame % framesPerBeat, fps, config: { damping: 10, mass: 0.4, stiffness: 350 } });
  const uiScale = inDrop ? interpolate(beatScale, [0, 1], [0.98, 1.03]) : 1.0;

  const imgOpacity = interpolate(frame, [0, 250, 400], [1, 1, 0], { extrapolateRight: 'clamp' });
  const imgScale = interpolate(frame, [0, 400], [1.0, 1.15]);

  const shadowR = isKick ? '12px 0 0 rgba(255,59,48,0.9)' : '3px 0 0 rgba(255,59,48,0.6)';
  const shadowB = isKick ? '-12px 0 0 rgba(43,59,229,0.9)' : '-3px 0 0 rgba(43,59,229,0.6)';
  const glitchShadow = `${shadowR}, ${shadowB}`;

  return (
    <AbsoluteFill style={{ backgroundColor: '#020202', overflow: 'hidden', fontFamily: 'system-ui, "Humanist Sans", -apple-system, sans-serif' }}>
      <Audio src={staticFile('silicon_loop.wav')} />

      <div style={{ position: 'absolute', width: '100%', height: '100%', top: 0, left: 0 }}>
        <ThreeCanvas width={1920} height={1080} camera={{ position: [camX, camY, camZ], fov: camFov, up: [Math.sin(camRoll), Math.cos(camRoll), 0] }}>
          <ambientLight intensity={0.1} />
          {isLaserActive && <pointLight position={[0, 1.8, sweepZ]} intensity={5} color="#2b3be5" distance={7} />}
          <pointLight position={[4, 5, 2]} intensity={inDrop && isKick ? 8 : (inIntro ? 0.8 : 2.5)} color="#ffffff" />
          <pointLight position={[-4, -1, -2]} intensity={inIntro ? 0.3 : 1.5} color="#2b3be5" />
          <group rotation={[0, 0, camRoll]}>
            <Wafer3D sweepZ={sweepZ} isLaserActive={isLaserActive} frame={frame} isExposedFunc={isExposedFunc} />
            <LaserParticles sweepZ={sweepZ} active={isLaserActive} />
          </group>
        </ThreeCanvas>
      </div>

      {/* Intro Cover Image Overlay */}
      {frame < 400 && (
        <AbsoluteFill style={{ opacity: imgOpacity, pointerEvents: 'none', overflow: 'hidden' }}>
          <Img src={staticFile('portada.png')} style={{ width: '100%', height: '100%', objectFit: 'cover', transform: `scale(${imgScale})`, filter: 'brightness(0.6) contrast(1.2)' }} />
          <div style={{ position: 'absolute', width: '100%', height: '100%', boxShadow: 'inset 0 0 350px rgba(0,0,0,1)' }} />
        </AbsoluteFill>
      )}

      <AbsoluteFill style={{ pointerEvents: 'none', padding: 60, display: 'flex', flexDirection: 'column', justifyContent: 'space-between', transform: `scale(${uiScale})` }}>
        
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
          <div>
            <div style={{ color: '#2b3be5', fontSize: 14, fontWeight: 900, letterSpacing: 4 }}>MOSKV-1 CORE LEDGER</div>
            <div style={{ color: '#ffffff', fontSize: 36, fontWeight: 900, marginTop: 4, letterSpacing: -2, textShadow: glitchShadow }}>
              EL ESCUDO DE SILICIO
            </div>
          </div>
          <div style={{ textAlign: 'right' }}>
            <div style={{ color: '#fff', fontSize: 16, fontWeight: 900, letterSpacing: 1 }}>REALITY LEVEL: <span style={{ color: '#2b3be5' }}>C5-REAL</span></div>
            <div style={{ color: 'rgba(255, 255, 255, 0.4)', fontSize: 12, marginTop: 4, fontFamily: 'monospace' }}>HASH: 17bb0d2 // bf9cb18</div>
          </div>
        </div>

        {inDrop && (
          <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', flexGrow: 1, zIndex: 10 }}>
            <h2 style={{ fontSize: 160, fontWeight: 900, color: currentBeat % 8 < 4 ? '#ffffff' : '#2b3be5', margin: 0, letterSpacing: -6, textAlign: 'center', textShadow: glitchShadow, textTransform: 'uppercase' }}>
              {currentBeat % 8 < 4 ? "TAIWAN YIELD" : "91.9% EXERGÍA"}
            </h2>
            <div style={{ color: '#fff', fontSize: 20, fontWeight: 700, letterSpacing: 12, marginTop: 15, opacity: isKick ? 1 : 0.8, backgroundColor: '#0a0a0a', borderLeft: '6px solid #2b3be5', padding: '10px 25px' }}>
              LA TERMODINÁMICA DE LA EJECUCIÓN
            </div>
          </div>
        )}

        {inIntro && (
          <div style={{ alignSelf: 'center', textAlign: 'center', maxWidth: 800 }}>
            <h3 style={{ color: '#ffffff', fontSize: 28, fontWeight: 900, letterSpacing: 10, margin: '0 0 15px 0', opacity: interpolate(frame, [0, 100, 350, 450], [0, 1, 1, 0]) }}>
              TAIWAN LITOGRAPHY EPISODE
            </h3>
            <div style={{ width: 300, height: 4, backgroundColor: '#2b3be5', margin: '0 auto', transform: `scaleX(${interpolate(frame, [0, 350], [0, 1], { extrapolateRight: 'clamp' })})` }} />
          </div>
        )}

        {inOutro && (
          <div style={{ alignSelf: 'center', textAlign: 'center', backgroundColor: '#0a0a0a', padding: '50px 70px', border: '3px solid #2b3be5', opacity: interpolate(frame, [1440, 1550], [0, 1], { extrapolateLeft: 'clamp' }) }}>
            <h2 style={{ color: '#ffffff', fontSize: 48, fontWeight: 900, margin: '0 0 10px 0', letterSpacing: -2 }}>LITHOGRAPHY COMPLETED</h2>
            <div style={{ color: '#2b3be5', fontSize: 32, fontWeight: 900 }}>FINAL YIELD: 91.9%</div>
            <div style={{ color: 'rgba(255, 255, 255, 0.5)', fontSize: 14, marginTop: 20, letterSpacing: 6, fontWeight: 700 }}>ZERO ENTROPY ACHIVED</div>
          </div>
        )}

        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-end' }}>
          <div>
            <div style={{ color: 'rgba(255, 255, 255, 0.4)', fontSize: 12, fontWeight: 700, letterSpacing: 2 }}>PROCESS METRIC</div>
            <div style={{ color: '#ffffff', fontSize: 16, marginTop: 6, fontWeight: 900, fontFamily: 'monospace' }}>
              {inIntro ? "CALIBRATING OPTICS (EUV_HAZ)" : (inDrop ? "EUV PLASMA PULSES: 100% INTENSITY" : "SCAN Z-AXIS ALIGNED")}
            </div>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: 30 }}>
            <div style={{ color: '#2b3be5', fontSize: 28, fontWeight: 900, lineHeight: 1 }}>{inIntro ? "BOOT" : "91.9%"}</div>
            <Oscilloscope frame={frame} inDrop={inDrop} isKick={isKick} />
          </div>
        </div>
      </AbsoluteFill>
      
      {frame >= 900 && frame < 908 && <div style={{ position: 'absolute', top: 0, left: 0, right: 0, bottom: 0, backgroundColor: '#ffffff', pointerEvents: 'none', opacity: interpolate(frame, [900, 908], [1.0, 0.0]) }} />}
      <div style={{ position: 'absolute', top: 0, left: 0, right: 0, bottom: 0, backgroundColor: '#ffffff', opacity: inDrop && isKick ? 0.12 : 0, pointerEvents: 'none', mixBlendMode: 'overlay' }} />
      <div style={{ position: 'absolute', top: 0, left: 0, right: 0, bottom: 0, boxShadow: 'inset 0 0 250px rgba(0,0,0,0.95)', pointerEvents: 'none' }} />
      {frame >= 1770 && <div style={{ position: 'absolute', top: 0, left: 0, right: 0, bottom: 0, backgroundColor: '#000000', pointerEvents: 'none', opacity: interpolate(frame, [1770, 1800], [0.0, 1.0]) }} />}
    </AbsoluteFill>
  );
};
