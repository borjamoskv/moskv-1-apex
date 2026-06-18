import React from 'react';
import { useCurrentFrame, useVideoConfig, interpolate, spring, random, AbsoluteFill, Sequence } from 'remotion';

export const BRTVideo: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  
  // Termodinámica C5-REAL
  const BPM = 130;
  const framesPerBeat = fps / (BPM / 60);
  const currentBeat = Math.floor(frame / framesPerBeat);
  const beatProgress = (frame % framesPerBeat) / framesPerBeat;
  
  // Strobe & Fricción Cinética
  const isKick = frame % framesPerBeat < 3;
  const strobeColor = isKick ? '#FFFFFF' : '#040404';
  const glitchX = (random(frame) - 0.5) * 80 * (isKick ? 1 : 0);
  const glitchY = (random(frame + 1) - 0.5) * 80 * (isKick ? 1 : 0);
  
  // Tensión Teresiana (Masa & Resorte)
  const scale = spring({
    frame: frame % framesPerBeat,
    fps,
    config: { damping: 10, mass: 0.8, stiffness: 250 }
  });

  // Alternancia de Ego (El Sharder)
  const identity = currentBeat % 8 < 4 ? 'TANGANA' : 'ROSALIA';

  return (
    <AbsoluteFill style={{ backgroundColor: strobeColor, overflow: 'hidden' }}>
      
      {/* Capa Base: Anergía Sangrienta (Exclusion Blending) */}
      <AbsoluteFill style={{ 
        opacity: interpolate(beatProgress, [0, 1], [0.9, 0]), 
        backgroundColor: '#e52b2b', 
        mixBlendMode: 'difference' 
      }} />

      {/* Capa Cinética: Texto Entrópico */}
      <AbsoluteFill style={{ 
        justifyContent: 'center', 
        alignItems: 'center', 
        transform: `translate(${glitchX}px, ${glitchY}px)` 
      }}>
        <h1 style={{
          fontSize: 180,
          fontWeight: 900,
          color: isKick ? '#000' : '#FFF',
          textAlign: 'center',
          lineHeight: 0.85,
          transform: `scale(${interpolate(scale, [0, 1], [0.95, 1.15])})`,
          fontFamily: 'Impact, Helvetica Neue, sans-serif',
          textTransform: 'uppercase',
          letterSpacing: '-0.06em',
          mixBlendMode: 'exclusion'
        }}>
          {identity === 'TANGANA' ? <>DEMASIADAS<br/>MUJERES</> : <>RELIQUIA<br/>SANTA</>}
        </h1>
        
        <div style={{
          position: 'absolute',
          bottom: 180,
          fontSize: 75,
          color: '#e52b2b',
          fontWeight: 900,
          letterSpacing: '0.25em',
          opacity: isKick ? 1 : 0,
          transform: `scale(${interpolate(scale, [0, 1], [1, 1.2])})`
        }}>
          BERGHAIN [130 BPM]
        </div>
      </AbsoluteFill>

      {/* Capa de Fractura (Dismembramiento Visual) */}
      <Sequence from={0} durationInFrames={300}>
         {isKick && currentBeat % 2 !== 0 && (
           <div style={{
             position: 'absolute',
             top: 0, left: 0, right: 0, bottom: 0,
             backgroundImage: 'url("https://picsum.photos/1080/1920?grayscale&blur=2")',
             backgroundSize: 'cover',
             mixBlendMode: 'overlay',
             opacity: 0.8,
             filter: 'contrast(150%) brightness(80%)'
           }} />
         )}
      </Sequence>
      
    </AbsoluteFill>
  );
};
