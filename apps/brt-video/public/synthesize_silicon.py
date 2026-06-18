import math
import wave
import struct
import random

SAMPLE_RATE = 44100
DURATION = 60  # 60 seconds full videoclip
BPM = 140
BEAT_DURATION = 60.0 / BPM
TOTAL_SAMPLES = int(SAMPLE_RATE * DURATION)

print(f"[C5-REAL] Synthesizing 60s Gemini-Optimized hybrid audio loop...")

def get_whistle_freq(t):
    # Melodía Spaghetti Western (Escala Pentatónica menor/Yo-sen)
    # A4=440, C5=523.25, D5=587.33, E5=659.25, G5=783.99, A5=880, B5=987.77
    if t < 3.0: return 440.0 # A4
    elif t < 6.0: return 523.25 # C5
    elif t < 9.0: return 587.33 # D5
    elif t < 12.0: return 523.25 # C5
    elif t < 15.0: return 440.0 # A4
    elif t < 18.0: return 0.0 # Silencio dramático
    # Build
    elif t < 21.0: return 587.33
    elif t < 24.0: return 659.25
    elif t < 27.0: return 783.99
    elif t < 30.0: return 880.00 # Máxima tensión
    # Drop (Clímax oriental)
    elif t < 34.0: return 880.00
    elif t < 38.0: return 783.99
    elif t < 42.0: return 587.33
    elif t < 46.0: return 523.25
    elif t < 50.0: return 440.0
    # Outro
    elif t < 56.0: return 440.0
    return 0.0

def get_guitar_freq(t):
    # Riff de bajo Spaghetti Western (A2, G2, E2)
    # A2=110.0, G2=98.0, E2=82.41
    if t < 15.0:
        return 110.0
    elif t < 30.0:
        if int(t / 3.0) % 2 == 0: return 98.0
        else: return 82.41
    elif t < 48.0:
        if int(t / 1.5) % 2 == 0: return 110.0
        else: return 82.41
    else:
        return 82.41

def synth():
    audio_data = bytearray(TOTAL_SAMPLES * 2)
    pi2 = 2 * math.pi
    
    # Generar secuencia de plucks orientales (Yo Scale)
    guzheng_notes = [440.0, 493.88, 587.33, 659.25, 783.99, 880.00, 987.77]
    guzheng_triggers = []
    
    # Rellenar triggers de Guzheng/Shamisen
    for step in range(0, int(DURATION / (BEAT_DURATION / 4.0))):
        t_trigger = step * (BEAT_DURATION / 4.0)
        
        # Build-up (15s a 30s)
        if 15.0 <= t_trigger < 30.0:
            if step % 8 in [0, 3, 5]:
                note_idx = (step // 4) % len(guzheng_notes)
                guzheng_triggers.append((t_trigger, guzheng_notes[note_idx], 0.15, 14.0))
                
        # Drop (30s a 48s) - Shamisen veloz a doble tempo
        elif 30.0 <= t_trigger < 48.0:
            if step % 4 != 3: # Semicorches sincopadas
                note_idx = (step * 3) % len(guzheng_notes)
                guzheng_triggers.append((t_trigger, guzheng_notes[note_idx] * 1.5, 0.18, 16.0))
                
        # Outro (48s a 60s)
        elif 48.0 <= t_trigger < 58.0:
            if step % 16 == 0:
                guzheng_triggers.append((t_trigger, guzheng_notes[0] * 0.5, 0.08, 3.5))

    for i in range(TOTAL_SAMPLES):
        t = i / SAMPLE_RATE
        t_beat = t % BEAT_DURATION
        
        # Control de secciones
        in_intro = t < 15.0
        in_build = 15.0 <= t < 30.0
        in_drop = 30.0 <= t < 48.0
        in_outro = t >= 48.0
        
        # 1. KICK DRUM (Bajo distorsionado industrial)
        kick_sound = 0.0
        if not in_outro:
            # Envolvente del kick
            if in_build and t >= 26.0:
                # Aceleración a doble tempo
                double_t_beat = t % (BEAT_DURATION / 2.0)
                kick_env = math.exp(-20.0 * double_t_beat)
                kick_freq = 160.0 * kick_env
                kick_phase = pi2 * kick_freq * t
                kick_sound = math.tanh(math.sin(kick_phase) * kick_env * 2.0) * 0.65
            else:
                kick_env = math.exp(-15.0 * t_beat)
                kick_freq = 150.0 * kick_env
                kick_phase = pi2 * kick_freq * t
                kick_raw = math.sin(kick_phase) * math.exp(-7.0 * t_beat)
                
                if in_intro:
                    kick_sound = math.tanh(kick_raw * 1.5) * 0.45 # Amortiguado
                elif in_build:
                    kick_sound = math.tanh(kick_raw * 2.5) * 0.60
                elif in_drop:
                    kick_sound = math.tanh(kick_raw * 4.5) * 0.82 # Saturación total

        # 2. HI-HATS (Ruido blanco en contratiempo)
        hat_sound = 0.0
        if in_build or in_drop:
            sixteenth = BEAT_DURATION / 4.0
            hat_t = t % sixteenth
            hat_vol = 0.04 if in_build else 0.12
            if t_beat > sixteenth:
                hat_env = math.exp(-42.0 * hat_t)
                hat_sound = random.uniform(-1.0, 1.0) * hat_env * hat_vol

        # 3. SILBIDO DEL OESTE CON PORTAMENTO
        whistle_freq = get_whistle_freq(t)
        whistle_sound = 0.0
        if whistle_freq > 0:
            # Vibrato humano a 5.8Hz
            vibrato = 1.0 + 0.015 * math.sin(pi2 * 5.8 * t)
            
            # Simulación de portamento (glide suave de frecuencia)
            # Buscamos la nota previa y hacemos un promedio ponderado
            note_idx = int(t / 3.0) if in_intro else (int(t / 4.0) if in_drop else int(t / 3.0))
            note_start_t = note_idx * 3.0 if in_intro else (note_idx * 4.0 if in_drop else note_idx * 3.0)
            elapsed_in_note = t - note_start_t
            
            current_target = whistle_freq
            if elapsed_in_note < 0.15: # 150ms glide time
                # Interpolar de la nota previa
                prev_freq = get_whistle_freq(note_start_t - 0.1)
                if prev_freq > 0:
                    weight = elapsed_in_note / 0.15
                    current_target = prev_freq + (whistle_freq - prev_freq) * weight
            
            target_freq = current_target * vibrato
            whistle_phase = pi2 * target_freq * t
            
            # Generar silbido + ruido de respiración
            breath = random.uniform(-1.0, 1.0) * 0.018
            whistle_sound = (math.sin(whistle_phase) + breath) * 0.25
            
            # Envolventes de ganancia suaves
            note_period = 3.0 if in_intro else (4.0 if in_drop else 3.0)
            note_t = t % note_period
            note_env = 1.0
            if note_t < 0.12: note_env = note_t / 0.12
            elif note_t > note_period - 0.15: note_env = (note_period - note_t) / 0.15
            
            if in_drop:
                note_env *= 0.65 # Menor presencia en el drop
            whistle_sound *= note_env

        # 4. GUITARRA TREMOLO SPAGHETTI
        guitar_sound = 0.0
        if not in_outro or t < 55.0:
            guitar_freq = get_guitar_freq(t)
            # FM Synthesis para cuerdas de metal
            mod_freq = guitar_freq * 2.0
            mod_phase = pi2 * mod_freq * t
            guitar_fm = math.sin(pi2 * guitar_freq * t + 0.85 * math.sin(mod_phase))
            
            # LFO de Tremolo clásico a 6.2 Hz
            tremolo = 0.65 + 0.35 * math.sin(pi2 * 6.2 * t)
            
            guitar_period = BEAT_DURATION * 4.0 if in_intro else (BEAT_DURATION * 2.0 if in_build else BEAT_DURATION)
            guitar_beat_t = t % guitar_period
            guitar_env = math.exp(-2.5 * guitar_beat_t)
            
            guitar_vol = 0.26 if in_intro else (0.22 if in_build else 0.18)
            if in_outro: guitar_vol *= ((55.0 - t) / 7.0)
            
            guitar_sound = guitar_fm * guitar_env * tremolo * guitar_vol

        # 5. SHAMISEN/GUZHENG ORIENTAL
        guzheng_sound = 0.0
        for trigger_t, freq, vol, decay in guzheng_triggers:
            if t >= trigger_t:
                time_since_trigger = t - trigger_t
                if time_since_trigger < 0.7:
                    guz_env = math.exp(-decay * time_since_trigger)
                    # Síntesis Shamisen: Combinación de onda sierra y distorsión tanh (sawari)
                    phase = pi2 * freq * time_since_trigger
                    guz_wave = 0.72 * math.sin(phase) + 0.28 * ((phase % pi2) - math.pi) / math.pi
                    buzz = math.tanh(guz_wave * 1.6)
                    guzheng_sound += buzz * guz_env * vol

        # 6. HAZ LÁSER EUV (Sweep de frecuencia)
        scan_sound = 0.0
        if in_drop:
            scan_period = 3.0
            scan_phase = (t % scan_period) / scan_period
            scan_freq = 400.0 + 1100.0 * math.sin(scan_phase * math.pi)
            scan_sound = math.sin(pi2 * scan_freq * t) * (1.0 - (kick_env if 'kick_env' in locals() else 0)) * 0.03

        # 7. DRONE PAD DE CORTEX
        drone_freq = 55.0 + math.sin(t * 0.04) * 1.5
        drone = (math.sin(pi2 * drone_freq * t) + math.sin(pi2 * drone_freq * 1.5 * t) * 0.35)
        drone = math.tanh(drone * 4.0) * 0.06
        if in_outro:
            drone *= ((60.0 - t) / 12.0)

        # MEZCLA DE CANALES
        mix = kick_sound + hat_sound + whistle_sound + guitar_sound + guzheng_sound + scan_sound + drone
        
        # Soft-limiting
        mix = math.tanh(mix * 1.1)
        
        # Loops transiciones
        if t < 0.8:
            mix *= (t / 0.8)
        elif t > DURATION - 0.8:
            mix *= ((DURATION - t) / 0.8)
            
        mix = max(-1.0, min(1.0, mix))
        
        sample_int = int(mix * 32767)
        struct.pack_into('<h', audio_data, i * 2, sample_int)

    output_path = "apps/brt-video/public/silicon_loop.wav"
    print(f"[C5-REAL] Escribiendo archivo WAV final en {output_path}...")
    with wave.open(output_path, 'w') as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(SAMPLE_RATE)
        wav_file.writeframes(audio_data)

if __name__ == "__main__":
    synth()
    print("[C5-REAL] Síntesis finalizada con éxito.")
