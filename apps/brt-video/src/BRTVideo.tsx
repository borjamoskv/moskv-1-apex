import React from 'react';
import { useCurrentFrame, useVideoConfig } from 'remotion';

export const BRTVideo: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  
  // 130 BPM -> 130 beats per minute -> 2.166 beats per second.
  // Frames per beat at 30 fps = 30 / (130 / 60) = 13.84 frames.
  const framesPerBeat = fps / (130 / 60);
  const currentBeat = Math.floor(frame / framesPerBeat);
  
  // Strobe effect: true if frame is the exact start of a beat
  const isKick = frame % framesPerBeat < 4; 

  const isTangana = currentBeat % 4 < 2;

  return (
    <div
      style={{
        flex: 1,
        backgroundColor: isKick ? '#fff' : '#0a0a0a',
        color: isKick ? '#0a0a0a' : '#fff',
        display: 'flex',
        flexDirection: 'column',
        justifyContent: 'center',
        alignItems: 'center',
        fontFamily: 'Helvetica, Arial, sans-serif',
        textAlign: 'center',
      }}
    >
      <div style={{ fontSize: 100, fontWeight: 'bold', textTransform: 'uppercase', lineHeight: 1.1 }}>
        {isTangana ? 'DEMASIADAS\\nMUJERES' : 'RELIQUIA'}
      </div>
      <div style={{ fontSize: 60, marginTop: 80, opacity: isKick ? 1 : 0.6 }}>
        BERGHAIN // 130 BPM
      </div>
      <div style={{ fontSize: 40, marginTop: 150, letterSpacing: '0.4em', color: isKick ? '#000' : '#e52b2b' }}>
        BRT ARCHITECTURE
      </div>
      <div style={{ fontSize: 24, marginTop: 20, letterSpacing: '0.2em', opacity: 0.5 }}>
        C5-REAL EXECUTION KERNEL
      </div>
    </div>
  );
};
