import React, { useRef } from 'react';
import { useCurrentFrame, useVideoConfig, spring, interpolate, AbsoluteFill, Sequence, random, Audio, staticFile } from 'remotion';
import { ThreeCanvas } from '@remotion/three';
import { useFrame } from '@react-three/fiber';
import * as THREE from 'three';

const RelicCross: React.FC = () => {
  const meshRef = useRef<THREE.Mesh>(null);
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const BPM = 140;
  const framesPerBeat = fps / (BPM / 60);
  const currentBeat = Math.floor(frame / framesPerBeat);
  
  // Fricción Cinética Continua
  useFrame(() => {
    if (meshRef.current) {
      meshRef.current.rotation.y = frame * 0.04;
      meshRef.current.rotation.x = frame * 0.03;
      meshRef.current.rotation.z = frame * 0.01;
    }
  });

  // Tensión Teresiana (El Latido)
  const scaleSpring = spring({
    frame: frame % framesPerBeat,
    fps,
    config: { damping: 10, mass: 1, stiffness: 350 }
  });

  const scale = interpolate(scaleSpring, [0, 1], [1, 2.5]);
  const isKick = frame % framesPerBeat < 4;
  
  // Sangrado estroboscópico
  const materialColor = isKick ? '#ffffff' : '#e52b2b';
  const wireframe = currentBeat % 4 !== 0; // Alterna sólido/wireframe

  return (
    <mesh ref={meshRef} scale={scale}>
      <icosahedronGeometry args={[2, 0]} />
      <meshStandardMaterial color={materialColor} wireframe={wireframe} emissive={materialColor} emissiveIntensity={isKick ? 1 : 0.2} />
    </mesh>
  );
};

export const BRTVideo3D: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  
  const BPM = 140;
  const framesPerBeat = fps / (BPM / 60);
  const currentBeat = Math.floor(frame / framesPerBeat);
  const isKick = frame % framesPerBeat < 3;

  const identity = currentBeat % 8 < 4 ? 'DEMASIADAS MUJERES' : 'RELIQUIA SANTA';

  // Glitch
  const glitchX = (random(frame) - 0.5) * 50 * (isKick ? 1 : 0);
  const glitchY = (random(frame + 1) - 0.5) * 50 * (isKick ? 1 : 0);

  return (
    <AbsoluteFill style={{ backgroundColor: isKick ? '#111' : '#000', overflow: 'hidden' }}>
      <Audio src={staticFile('kick_140.m4a')} />
      
      <ThreeCanvas width={1920} height={1080} camera={{ position: [0, 0, 8], fov: 80 }}>
        <ambientLight intensity={0.2} />
        <pointLight position={[10, 10, 10]} intensity={isKick ? 5 : 0.5} color="#e52b2b" />
        <pointLight position={[-10, -10, -10]} intensity={2} color="#ffffff" />
        <RelicCross />
      </ThreeCanvas>

      <AbsoluteFill style={{ 
        justifyContent: 'center', 
        alignItems: 'center', 
        pointerEvents: 'none',
        transform: `translate(${glitchX}px, ${glitchY}px)`
      }}>
        <h1 style={{
          fontSize: 160,
          fontWeight: 900,
          color: isKick ? '#fff' : 'transparent',
          textAlign: 'center',
          lineHeight: 0.9,
          fontFamily: 'Helvetica Neue, sans-serif',
          textTransform: 'uppercase',
          WebkitTextStroke: '3px #e52b2b',
          mixBlendMode: 'difference'
        }}>
          {identity.split(' ').map((word, i) => <React.Fragment key={i}>{word}<br/></React.Fragment>)}
        </h1>
        <div style={{
          position: 'absolute',
          bottom: 200,
          fontSize: 60,
          color: '#e52b2b',
          fontWeight: 900,
          letterSpacing: '0.4em',
          opacity: isKick ? 1 : 0.3
        }}>
          BERGHAIN [140]
        </div>
      </AbsoluteFill>
      
      {/* Resaca Entrópica: Ruido Visual */}
      <AbsoluteFill style={{
        backgroundColor: '#e52b2b',
        opacity: isKick ? 0.1 : 0,
        mixBlendMode: 'color-burn',
        pointerEvents: 'none'
      }} />
    </AbsoluteFill>
  );
};
