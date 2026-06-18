import math
import wave
import struct
import random

SAMPLE_RATE = 44100
DURATION = 60  # 60 seconds full videoclip track
BPM = 140
BEAT_DURATION = 60.0 / BPM
TOTAL_SAMPLES = int(SAMPLE_RATE * DURATION)

print(f"Synthesizing 60s Extended Audio for Silicon videoclip at {BPM} BPM...")

def get_whistle_freq(t):
    # Melodía silbada (Oeste Americano / Pentatónica)
    # A4=440, C5=523.25, D5=587.33, E5=659.25, G5=783.99, A5=880, B5=987.77
    if t < 2.0: return 440.0
    elif t < 4.0: return 523.25
    elif t < 6.0: return 587.33
    elif t < 8.0: return 523.25
    elif t < 10.0: return 440.0
    elif t < 15.0: return 0.0 # Silencio pre-build
    # Build
    elif t < 18.0: return 587.33
    elif t < 21.0: return 659.25
    elif t < 24.0: return 783.99
    elif t < 27.0: return 880.00
    elif t < 30.0: return 987.77 # Nota de tensión máxima
    # Drop (Unísono con Shamisen)
    elif t < 34.0: return 880.00
    elif t < 38.0: return 783.99
    elif t < 42.0: return 587.33
    elif t < 46.0: return 523.25
    elif t < 50.0: return 440.0
    # Outro
    elif t < 55.0: return 440.0
    return 0.0

def get_guitar_freq(t):
    if t < 15.0:
        return 110.0 # A2
    elif t < 30.0:
        # Tensión subiendo
        if int(t / 4.0) % 2 == 0: return 98.0 # G2
        else: return 82.41 # E2
    elif t < 48.0:
        # Drop riff
        if int(t / 2.0) % 2 == 0: return 110.0
        else: return 82.41
    else:
        return 82.41 # E2 outro

def synth():
    audio_data = bytearray(TOTAL_SAMPLES * 2)
    pi2 = 2 * math.pi
    
    # Generar plucks orientales (Yo Scale)
    guzheng_notes = [440.0, 493.88, 587.33, 659.25, 783.99, 880.00, 987.77]
    guzheng_triggers = []
    
    # Rellenar triggers de Guzheng/Shamisen
    for step in range(0, int(DURATION / (BEAT_DURATION / 4.0))):
        t_trigger = step * (BEAT_DURATION / 4.0)
        
        # Section 2: Build-up (15s a 30s) - Plucks lentos de Guzheng
        if 15.0 <= t_trigger < 30.0:
            if step % 8 == 0 or step % 8 == 3:
                note_idx = (step // 8) % len(guzheng_notes)
                guzheng_triggers.append((t_trigger, guzheng_notes[note_idx], 0.12, 12.0)) # (t, freq, vol, decay)
                
        # Section 3: Drop (30s a 48s) - Riff de Shamisen ultra veloz
        elif 30.0 <= t_trigger < 48.0:
            # Rítmica sincopada de semicorcheas
            if step % 4 != 3:
                note_idx = (step * 3) % len(guzheng_notes)
                guzheng_triggers.append((t_trigger, guzheng_notes[note_idx] * 1.5, 0.15, 15.0))
                
        # Section 4: Outro (48s a 60s) - Notas flotantes con mucha reverberación
        elif 48.0 <= t_trigger < 58.0:
            if step % 16 == 0:
                guzheng_triggers.append((t_trigger, guzheng_notes[0] * 0.5, 0.1, 4.0))

    for i in range(TOTAL_SAMPLES):
        t = i / SAMPLE_RATE
        t_beat = t % BEAT_DURATION
        
        # --- CONTROL DE SECCIONES ---
        in_intro = t < 15.0
        in_build = 15.0 <= t < 30.0
        in_drop = 30.0 <= t < 48.0
        in_outro = t >= 48.0
        
        # 1. KICK DRUM (Dinámica variable)
        kick_sound = 0.0
        if not in_outro:
            kick_env = math.exp(-15.0 * t_beat)
            kick_freq = 150.0 * kick_env
            kick_phase = pi2 * kick_freq * t
            
            # El kick en la intro es más sutil y amortiguado (low-pass)
            if in_intro:
                kick_raw = math.sin(kick_phase) * math.exp(-6.0 * t_beat)
                kick_sound = math.tanh(kick_raw * 1.5) * 0.45
            # Build subiendo
            elif in_build:
                # El kick acelera a doble tempo en los últimos 4 segundos del build (26s a 30s)
                if t >= 26.0:
                    double_t_beat = t % (BEAT_DURATION / 2.0)
                    kick_env = math.exp(-18.0 * double_t_beat)
                    kick_freq = 160.0 * kick_env
                    kick_phase = pi2 * kick_freq * t
                    kick_sound = math.tanh(math.sin(kick_phase) * kick_env) * 0.65
                else:
                    kick_sound = math.tanh(math.sin(kick_phase) * kick_env) * 0.6
            # Clímax total
            elif in_drop:
                kick_sound = math.tanh(math.sin(kick_phase) * kick_env * 3.5) * 0.78
        
        # 2. HI-HATS (Noisy)
        hat_sound = 0.0
        if in_build or in_drop:
            sixteenth = BEAT_DURATION / 4.0
            hat_t = t % sixteenth
            # Entra poco a poco en el build y explota en el drop
            hat_vol = 0.05 if in_build else 0.12
            if t_beat > sixteenth:
                hat_env = math.exp(-42.0 * hat_t)
                hat_sound = random.uniform(-1.0, 1.0) * hat_env * hat_vol

        # 3. SILBIDO DEL OESTE (Whistle)
        whistle_freq = get_whistle_freq(t)
        whistle_sound = 0.0
        if whistle_freq > 0:
            vibrato = 1.0 + 0.014 * math.sin(pi2 * 5.8 * t)
            target_freq = whistle_freq * vibrato
            whistle_phase = pi2 * target_freq * t
            
            breath = random.uniform(-1.0, 1.0) * 0.015
            whistle_sound = (math.sin(whistle_phase) + breath) * 0.2
            
            # Envolvente por nota
            note_t = t % 2.0 if in_intro else (t % 3.0 if in_build else t % 4.0)
            note_env = 1.0
            if note_t < 0.1: note_env = note_t / 0.1
            elif note_t > 1.8 and in_intro: note_env = (2.0 - note_t) / 0.2
            elif note_t > 2.8 and in_build: note_env = (3.0 - note_t) / 0.2
            elif note_t > 3.8: note_env = (4.0 - note_t) / 0.2
            
            # Atenuar silbido en el drop
            if in_drop:
                note_env *= 0.7
                
            whistle_sound *= note_env

        # 4. TREMOLO GUITAR
        guitar_sound = 0.0
        if not in_outro or t < 55.0:
            guitar_freq = get_guitar_freq(t)
            mod_freq = guitar_freq * 2.0
            mod_phase = pi2 * mod_freq * t
            guitar_fm = math.sin(pi2 * guitar_freq * t + 0.9 * math.sin(mod_phase))
            
            tremolo = 0.65 + 0.35 * math.sin(pi2 * 6.0 * t)
            
            # El ritmo del rasgueo depende de la sección
            guitar_period = BEAT_DURATION * 4.0 if in_intro else (BEAT_DURATION * 2.0 if in_build else BEAT_DURATION)
            guitar_beat_t = t % guitar_period
            guitar_env = math.exp(-2.2 * guitar_beat_t)
            
            # Volumen
            guitar_vol = 0.25 if in_intro else (0.2 if in_build else 0.18)
            if in_outro: guitar_vol *= ((55.0 - t) / 7.0)
            
            guitar_sound = guitar_fm * guitar_env * tremolo * guitar_vol

        # 5. SHAMISEN/GUZHENG ORIENTAL
        guzheng_sound = 0.0
        for trigger_t, freq, vol, decay in guzheng_triggers:
            if t >= trigger_t:
                time_since_trigger = t - trigger_t
                if time_since_trigger < 0.8:
                    guz_env = math.exp(-decay * time_since_trigger)
                    phase = pi2 * freq * time_since_trigger
                    guz_wave = 0.7 * math.sin(phase) + 0.3 * ((phase % pi2) - math.pi) / math.pi
                    buzz = math.tanh(guz_wave * 1.5)
                    guzheng_sound += buzz * guz_env * vol

        # 6. HAZ LÁSER EUV (Pulsante e industrial en el drop)
        scan_sound = 0.0
        if in_drop:
            scan_period = 3.0
            scan_phase = (t % scan_period) / scan_period
            scan_freq = 400.0 + 1100.0 * math.sin(scan_phase * math.pi)
            scan_sound = math.sin(pi2 * scan_freq * t) * (1.0 - (kick_env if 'kick_env' in locals() else 0)) * 0.03
            
        # 7. DRONE PAD DE FONDO (Atmosférico)
        drone_freq = 55.0 + math.sin(t * 0.05) * 1.5 # A1 base
        drone = (math.sin(pi2 * drone_freq * t) + math.sin(pi2 * drone_freq * 1.5 * t) * 0.4)
        drone = math.tanh(drone * 4.0) * 0.06
        if in_outro:
            drone *= ((60.0 - t) / 12.0) # Fade out largo del drone al final

        # MEZCLA DE AUDIO
        mix = kick_sound + hat_sound + whistle_sound + guitar_sound + guzheng_sound + scan_sound + drone
        
        # Soft clipping final
        mix = math.tanh(mix * 1.1)
        
        # Master fade in/out general
        if t < 1.0:
            mix *= t
        elif t > DURATION - 1.0:
            mix *= (DURATION - t)
            
        mix = max(-1.0, min(1.0, mix))
        
        sample_int = int(mix * 32767)
        struct.pack_into('<h', audio_data, i * 2, sample_int)

    output_path = "apps/brt-video/public/silicon_loop.wav"
    print(f"Writing 60s wav to {output_path}...")
    with wave.open(output_path, 'w') as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(SAMPLE_RATE)
        wav_file.writeframes(audio_data)

if __name__ == "__main__":
    synth()
    print("Synthesis complete.")
