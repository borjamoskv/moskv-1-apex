import math
import wave
import struct
import random

SAMPLE_RATE = 44100
DURATION = 260 # 4:20
BPM = 140
BEAT_DURATION = 60.0 / BPM
TOTAL_SAMPLES = int(SAMPLE_RATE * DURATION)

print(f"Synthesizing {DURATION} seconds of Industrial Techno at {BPM} BPM...")

def synth():
    audio_data = bytearray(TOTAL_SAMPLES * 2)
    
    # Pre-calculate envelopes for speed where possible, but a loop is fine.
    # To optimize pure python loop, we use local variable lookups.
    pi2 = 2 * math.pi
    
    for i in range(TOTAL_SAMPLES):
        t = i / SAMPLE_RATE
        t_beat = t % BEAT_DURATION
        
        # 1. KICK DRUM (909 Style, saturated)
        # Pitch envelope drops rapidly
        kick_env = math.exp(-15.0 * t_beat)
        kick_freq = 150.0 * kick_env
        kick_phase = pi2 * kick_freq * t
        kick = math.sin(kick_phase) * math.exp(-10.0 * t_beat)
        # Saturation
        kick = math.tanh(kick * 3.0)
        
        # 2. OFF-BEAT DUB BASS
        bass_t = (t - BEAT_DURATION * 0.5) % BEAT_DURATION
        if bass_t < 0: bass_t += BEAT_DURATION
        bass_env = math.exp(-8.0 * bass_t) if bass_t < BEAT_DURATION * 0.5 else 0
        fm_mod = math.sin(pi2 * 55 * t) * 2.0
        bass = math.sin(pi2 * 55 * t + fm_mod) * bass_env
        bass = max(-1.0, min(1.0, bass * 1.5)) * 0.6
        
        # 3. 16TH NOTE HI-HATS (White noise filtered)
        sixteenth = BEAT_DURATION / 4.0
        hat_t = t % sixteenth
        # Avoid hat on the kick
        if t_beat > sixteenth:
            hat_env = math.exp(-40.0 * hat_t)
            hat = random.uniform(-1.0, 1.0) * hat_env * 0.15
        else:
            hat = 0.0
            
        # 4. DARK DRONE PAD
        drone_freq = 40.0 + math.sin(t * 0.1) * 2.0
        drone = (math.sin(pi2 * drone_freq * t) + math.sin(pi2 * drone_freq * 1.5 * t) * 0.5)
        drone = math.tanh(drone * 5.0) * 0.1
        
        # 5. MIXDOWN
        mix = kick * 0.85 + bass + hat + drone
        
        # Fade in / Fade out
        if t < 5.0:
            mix *= (t / 5.0)
        elif t > DURATION - 5.0:
            mix *= ((DURATION - t) / 5.0)
            
        # Hard clip
        mix = max(-1.0, min(1.0, mix))
        
        # Convert to 16-bit PCM
        sample_int = int(mix * 32767)
        
        # Write to bytearray (little endian)
        struct.pack_into('<h', audio_data, i * 2, sample_int)
        
        if i % (SAMPLE_RATE * 10) == 0 and i > 0:
            print(f"Rendered {i / SAMPLE_RATE:.1f}s / {DURATION}s")

    print("Writing to master_audio.wav...")
    with wave.open("apps/brt-video/public/master_audio.wav", 'w') as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(SAMPLE_RATE)
        wav_file.writeframes(audio_data)
        
synth()
print("Audio synthesis complete.")
