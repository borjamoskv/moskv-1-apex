import math
import wave
import struct
import random

SAMPLE_RATE = 44100
DURATION = 10  # 10 seconds loop
BPM = 140
BEAT_DURATION = 60.0 / BPM
TOTAL_SAMPLES = int(SAMPLE_RATE * DURATION)

print(f"Synthesizing Spaghetti Western + Oriental Silicon Loop at {BPM} BPM...")

def get_whistle_freq(t):
    # Melodía silbada (Oeste Americano / Escala Pentatónica)
    # A4=440, C5=523.25, D5=587.33, E5=659.25, G5=783.99, A5=880
    if 0.0 <= t < 0.85: return 440.0 # A4
    elif 0.85 <= t < 1.71: return 523.25 # C5
    elif 1.71 <= t < 2.57: return 587.33 # D5
    elif 2.57 <= t < 3.42: return 523.25 # C5
    elif 3.42 <= t < 4.28: return 440.0 # A4
    elif 4.28 <= t < 5.14: return 0.0 # Silencio transicional
    # Tema oriental + oeste en unísono
    elif 5.14 <= t < 6.0: return 659.25 # E5
    elif 6.0 <= t < 6.85: return 783.99 # G5
    elif 6.85 <= t < 7.71: return 880.00 # A5
    elif 7.71 <= t < 8.57: return 783.99 # G5
    elif 8.57 <= t < 9.5: return 659.25 # E5
    return 0.0

def get_guitar_freq(t):
    # Bajo de guitarra tremolo Spaghetti Western (A2, G2, E2)
    # A2=110.0, G2=98.0, E2=82.41
    if 0.0 <= t < 1.71: return 110.0
    elif 1.71 <= t < 3.42: return 98.0
    elif 3.42 <= t < 5.14: return 82.41
    elif 5.14 <= t < 6.85: return 110.0
    elif 6.85 <= t < 8.57: return 98.0
    return 82.41

def synth():
    audio_data = bytearray(TOTAL_SAMPLES * 2)
    pi2 = 2 * math.pi
    
    # Historial de disparos de plucks orientales (Guzheng/Shamisen)
    # Triggers a intervalos de corcheas/semicorcheas en la escala Yo
    guzheng_triggers = []
    # Generar tiempos de disparo
    guzheng_notes = [440.0, 493.88, 587.33, 659.25, 783.99, 880.00, 987.77]
    for step in range(16, 40): # De beat 4 a beat 10
        t_trigger = step * (BEAT_DURATION / 2.0)
        # Rítmica sincopada para el feeling de cuerdas orientales
        if step % 3 != 0:
            note_idx = (step * 2) % len(guzheng_notes)
            guzheng_triggers.append((t_trigger, guzheng_notes[note_idx]))
            
    # Segunda sección de plucks orientales veloces (Beats 14 a 20)
    for step in range(56, 80):
        t_trigger = step * (BEAT_DURATION / 4.0) # Semicorcheas rápidas
        if step % 5 < 3:
            note_idx = (step * 3) % len(guzheng_notes)
            guzheng_triggers.append((t_trigger, guzheng_notes[note_idx] * 1.5))
            
    for i in range(TOTAL_SAMPLES):
        t = i / SAMPLE_RATE
        t_beat = t % BEAT_DURATION
        
        # 1. TECHNO KICK DRUM (140 BPM, Sub y Pegada)
        kick_env = math.exp(-15.0 * t_beat)
        kick_freq = 150.0 * kick_env
        kick_phase = pi2 * kick_freq * t
        kick = math.sin(kick_phase) * math.exp(-7.5 * t_beat)
        kick = math.tanh(kick * 3.5)
        
        # 2. HI-HATS (Noisy, off-beat)
        sixteenth = BEAT_DURATION / 4.0
        hat_t = t % sixteenth
        if t_beat > sixteenth:
            hat_env = math.exp(-40.0 * hat_t)
            hat = random.uniform(-1.0, 1.0) * hat_env * 0.08
        else:
            hat = 0.0

        # 3. SILBIDO DEL OESTE AMERICANO (Whistle Synth)
        whistle_freq = get_whistle_freq(t)
        whistle_sound = 0.0
        if whistle_freq > 0:
            # Vibrato de factor humano (5.8 Hz)
            vibrato = 1.0 + 0.015 * math.sin(pi2 * 5.8 * t)
            # Portamento/Glide suave entre frecuencias para imitar labios
            # Buscamos la frecuencia objetivo en la vecindad temporal
            target_freq = whistle_freq * vibrato
            whistle_phase = pi2 * target_freq * t
            
            # Onda de silbido: Seno puro + sutil ruido blanco de respiración
            breath_noise = random.uniform(-1.0, 1.0) * 0.02
            whistle_sound = (math.sin(whistle_phase) + breath_noise) * 0.22
            
            # Envolvente suave de ataque/caída por nota para evitar clics
            note_t = t % 0.85
            note_env = 1.0
            if note_t < 0.08: note_env = note_t / 0.08
            elif note_t > 0.77: note_env = (0.85 - note_t) / 0.08
            whistle_sound *= note_env

        # 4. GUITARRA SPAGHETTI WESTERN (Bajo con Tremolo de 6Hz)
        guitar_freq = get_guitar_freq(t)
        # FM Synthesis: Portadora y moduladora para timbre metálico de cuerda de metal
        mod_freq = guitar_freq * 2.0
        mod_phase = pi2 * mod_freq * t
        guitar_fm = math.sin(pi2 * guitar_freq * t + 0.8 * math.sin(mod_phase))
        
        # Tremolo clásico optoacoplado del oeste a 6.2 Hz
        tremolo = 0.7 + 0.3 * math.sin(pi2 * 6.2 * t)
        # Envolvente de rasgueo
        guitar_beat_t = t % (BEAT_DURATION * 2.0)
        guitar_env = math.exp(-2.5 * guitar_beat_t)
        guitar_sound = guitar_fm * guitar_env * tremolo * 0.25

        # 5. SHAMISEN/GUZHENG ORIENTAL (Karplus-Strong plucks programados)
        guzheng_sound = 0.0
        for trigger_t, freq in guzheng_triggers:
            if t >= trigger_t:
                time_since_trigger = t - trigger_t
                if time_since_trigger < 0.6: # Duración física de resonancia
                    # Envolvente del punteo
                    guz_env = math.exp(-12.0 * time_since_trigger)
                    # Añadir distorsión "sawari" (zumbido de puente de madera oriental)
                    # Combinamos seno y sierra para emular Shamisen
                    phase = pi2 * freq * time_since_trigger
                    guz_wave = 0.75 * math.sin(phase) + 0.25 * ((phase % pi2) - math.pi) / math.pi
                    # Zumbido del puente
                    buzz = math.tanh(guz_wave * 1.6)
                    guzheng_sound += buzz * guz_env * 0.14
                    
        # 6. HAZ LÁSER EUV (Resonancia pulsante de barrido)
        scan_period = 3.0
        scan_phase = (t % scan_period) / scan_period
        scan_freq = 400.0 + 1200.0 * math.sin(scan_phase * math.pi)
        scan_sound = math.sin(pi2 * scan_freq * t) * (1.0 - kick_env) * 0.025

        # MEZCLA FINAL DE SEÑALES (Mixdown)
        mix = kick * 0.7 + hat * 0.25 + whistle_sound + guitar_sound + guzheng_sound + scan_sound
        
        # Soft-limiting
        mix = math.tanh(mix * 1.1)
        
        # Loop transition smoothing
        if t < 0.15:
            mix *= (t / 0.15)
        elif t > DURATION - 0.15:
            mix *= ((DURATION - t) / 0.15)
            
        mix = max(-1.0, min(1.0, mix))
        
        # Write to bytearray
        sample_int = int(mix * 32767)
        struct.pack_into('<h', audio_data, i * 2, sample_int)

    output_path = "apps/brt-video/public/silicon_loop.wav"
    print(f"Writing to {output_path}...")
    with wave.open(output_path, 'w') as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(SAMPLE_RATE)
        wav_file.writeframes(audio_data)

if __name__ == "__main__":
    synth()
    print("Synthesis complete.")
