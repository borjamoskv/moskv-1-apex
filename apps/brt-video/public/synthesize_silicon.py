import math
import wave
import struct
import random

SAMPLE_RATE = 44100
DURATION = 60
BPM = 140
BEAT_DURATION = 60.0 / BPM
TOTAL_SAMPLES = int(SAMPLE_RATE * DURATION)

print(f"[C5-REAL] Synthesizing OMEGA V3 STEREO hybrid audio loop with Sidechain Compression...")

def get_whistle_freq(t):
    if t < 3.0: return 440.0
    elif t < 6.0: return 523.25
    elif t < 9.0: return 587.33
    elif t < 12.0: return 523.25
    elif t < 15.0: return 440.0
    elif t < 18.0: return 0.0
    elif t < 21.0: return 587.33
    elif t < 24.0: return 659.25
    elif t < 27.0: return 783.99
    elif t < 30.0: return 880.00
    elif t < 34.0: return 880.00
    elif t < 38.0: return 783.99
    elif t < 42.0: return 587.33
    elif t < 46.0: return 523.25
    elif t < 50.0: return 440.0
    elif t < 56.0: return 440.0
    return 0.0

def get_guitar_freq(t):
    if t < 15.0: return 110.0
    elif t < 30.0: return 98.0 if int(t / 3.0) % 2 == 0 else 82.41
    elif t < 48.0: return 110.0 if int(t / 1.5) % 2 == 0 else 82.41
    else: return 82.41

def synth():
    audio_data = bytearray(TOTAL_SAMPLES * 4)
    pi2 = 2 * math.pi
    
    guzheng_notes = [440.0, 493.88, 587.33, 659.25, 783.99, 880.00, 987.77]
    guzheng_triggers = []
    for step in range(0, int(DURATION / (BEAT_DURATION / 4.0))):
        t_trigger = step * (BEAT_DURATION / 4.0)
        if 15.0 <= t_trigger < 30.0:
            if step % 8 in [0, 3, 5]:
                note_idx = (step // 4) % len(guzheng_notes)
                guzheng_triggers.append((t_trigger, guzheng_notes[note_idx], 0.15, 14.0))
        elif 30.0 <= t_trigger < 48.0:
            if step % 4 != 3:
                note_idx = (step * 3) % len(guzheng_notes)
                guzheng_triggers.append((t_trigger, guzheng_notes[note_idx] * 1.5, 0.18, 16.0))
        elif 48.0 <= t_trigger < 58.0:
            if step % 16 == 0:
                guzheng_triggers.append((t_trigger, guzheng_notes[0] * 0.5, 0.08, 3.5))

    delay_len_l = int(SAMPLE_RATE * BEAT_DURATION * 0.75)
    delay_len_r = int(SAMPLE_RATE * BEAT_DURATION * 0.50)
    delay_buf_l = [0.0] * delay_len_l
    delay_buf_r = [0.0] * delay_len_r
    delay_idx_l = 0
    delay_idx_r = 0

    for i in range(TOTAL_SAMPLES):
        t = i / SAMPLE_RATE
        t_beat = t % BEAT_DURATION
        
        in_intro = t < 15.0
        in_build = 15.0 <= t < 30.0
        in_drop = 30.0 <= t < 48.0
        in_outro = t >= 48.0
        
        # 1. KICK (Hard-clipped, Massive impact)
        kick_sound = 0.0
        kick_env_sidechain = 0.0
        is_kick_active = False
        if not in_outro:
            if in_build and t >= 26.0:
                double_t_beat = t % (BEAT_DURATION / 2.0)
                kick_env = math.exp(-20.0 * double_t_beat)
                kick_env_sidechain = kick_env
                kick_freq = 160.0 * kick_env
                crush_rate = 4000.0 if double_t_beat < 0.05 else SAMPLE_RATE
                t_c = math.floor(t * crush_rate) / crush_rate
                kick_sound = math.tanh(math.sin(pi2 * kick_freq * t_c) * kick_env * 3.0) * 0.7
            else:
                kick_env = math.exp(-15.0 * t_beat)
                kick_env_sidechain = kick_env
                kick_freq = 150.0 * kick_env
                crush_rate = 3000.0 if t_beat < 0.08 else SAMPLE_RATE
                t_c = math.floor(t * crush_rate) / crush_rate
                kick_raw = math.sin(pi2 * kick_freq * t_c) * math.exp(-7.0 * t_beat)
                if t_beat < 0.08:
                    steps = 8
                    kick_raw = round(kick_raw * steps) / steps
                if in_intro: kick_sound = math.tanh(kick_raw * 2.0) * 0.5
                elif in_build: kick_sound = math.tanh(kick_raw * 3.0) * 0.7
                elif in_drop: kick_sound = math.tanh(kick_raw * 6.0) * 0.90
                
                if kick_env > 0.12: is_kick_active = True

        # SIDECHAIN DUCKING FACTOR
        ducking = 0.15 if is_kick_active and (in_build or in_drop) else 1.0

        # 2. HATS (Stereo Ping-Pong)
        hat_l, hat_r = 0.0, 0.0
        if in_build or in_drop:
            sixteenth = BEAT_DURATION / 4.0
            hat_t = t % sixteenth
            hat_vol = 0.06 if in_build else 0.18
            if t_beat > sixteenth:
                hat_env = math.exp(-42.0 * hat_t)
                noise = random.uniform(-1.0, 1.0) * hat_env * hat_vol
                pan = 0.5 + 0.4 * math.sin(pi2 * 4.0 * t)
                hat_l = noise * (1.0 - pan)
                hat_r = noise * pan

        # 3. WHISTLE
        whistle_freq = get_whistle_freq(t)
        whistle_sound = 0.0
        if whistle_freq > 0:
            vibrato = 1.0 + 0.015 * math.sin(pi2 * 5.8 * t)
            note_idx = int(t / 3.0) if not in_drop else int(t / 4.0)
            note_start_t = note_idx * (3.0 if not in_drop else 4.0)
            elapsed = t - note_start_t
            
            target = whistle_freq
            if elapsed < 0.15:
                prev = get_whistle_freq(note_start_t - 0.1)
                if prev > 0: target = prev + (whistle_freq - prev) * (elapsed / 0.15)
            
            whistle_sound = (math.sin(pi2 * target * vibrato * t) + random.uniform(-1,1)*0.018) * 0.25
            note_period = 3.0 if not in_drop else 4.0
            note_t = t % note_period
            env = 1.0
            if note_t < 0.12: env = note_t / 0.12
            elif note_t > note_period - 0.15: env = (note_period - note_t) / 0.15
            if in_drop: env *= 0.65
            whistle_sound *= env * ducking

        # 4. GUITAR (FM + Tremolo + Ducking)
        guitar_sound = 0.0
        if not in_outro or t < 55.0:
            g_freq = get_guitar_freq(t)
            mod = math.sin(pi2 * g_freq * 2.0 * t)
            guitar_fm = math.sin(pi2 * g_freq * t + 0.85 * mod)
            tremolo = 0.65 + 0.35 * math.sin(pi2 * 6.2 * t)
            g_beat = t % (BEAT_DURATION * (4.0 if in_intro else 2.0 if in_build else 1.0))
            g_env = math.exp(-2.5 * g_beat)
            g_vol = 0.3 if in_intro else 0.25 if in_build else 0.22
            if in_outro: g_vol *= (55.0 - t) / 7.0
            guitar_sound = guitar_fm * g_env * tremolo * g_vol * ducking

        # 5. SHAMISEN/GUZHENG
        guzheng_sound = 0.0
        for trigger_t, freq, vol, decay in guzheng_triggers:
            if t >= trigger_t and t - trigger_t < 0.8:
                dt = t - trigger_t
                env = math.exp(-decay * dt)
                phase = pi2 * freq * dt
                wave_val = 0.72 * math.sin(phase) + 0.28 * ((phase % pi2) - math.pi) / math.pi
                guzheng_sound += math.tanh(wave_val * 1.6) * env * vol * ducking

        # 6. EUV LASER
        scan_sound = 0.0
        if in_drop:
            scan_phase = (t % 3.0) / 3.0
            scan_freq = 400.0 + 1100.0 * math.sin(scan_phase * math.pi)
            scan_sound = math.sin(pi2 * scan_freq * t) * (1.0 - (kick_env if 'kick_env' in locals() else 0)) * 0.05

        # 7. DRONE PAD (STEREO CHORUS 30ms offset)
        drone_freq = 55.0 + math.sin(t * 0.04) * 1.5
        def get_drone(time_val):
            return math.tanh((math.sin(pi2 * drone_freq * time_val) + math.sin(pi2 * drone_freq * 1.5 * time_val) * 0.35) * 4.0) * 0.08
        
        drone_l = get_drone(t)
        drone_r = get_drone(max(0, t - 0.030))
        
        if in_outro: 
            fade_out = (60.0 - t) / 12.0
            drone_l *= fade_out
            drone_r *= fade_out

        # SIDECHAIN ASIMÉTRICO (Ducking Compressor on Guitar & Drone based on Kick)
        ducking_gain = max(0.0, 1.0 - kick_env_sidechain * 2.2)
        guitar_sound *= ducking_gain
        drone_l *= ducking_gain
        drone_r *= ducking_gain

        # CROSS-FEEDBACK DELAY FX
        fx_send = whistle_sound * 0.6 + guzheng_sound * 0.5
        delay_out_l = delay_buf_l[delay_idx_l]
        delay_out_r = delay_buf_r[delay_idx_r]
        
        delay_buf_l[delay_idx_l] = fx_send + delay_out_r * 0.4
        delay_buf_r[delay_idx_r] = fx_send + delay_out_l * 0.4
        
        delay_idx_l = (delay_idx_l + 1) % delay_len_l
        delay_idx_r = (delay_idx_r + 1) % delay_len_r

        # STEREO MIX
        mix_center = kick_sound + scan_sound
        out_l = mix_center + guitar_sound + drone_l + hat_l + whistle_sound * 0.8 + guzheng_sound * 0.9 + delay_out_l * 0.5
        out_r = mix_center + guitar_sound + drone_r + hat_r + whistle_sound * 0.9 + guzheng_sound * 0.8 + delay_out_r * 0.5
        
        # MASTER LIMITER & COMPRESSION
        out_l = math.tanh(out_l * 1.4)
        out_r = math.tanh(out_r * 1.4)
        
        fade = 1.0
        if t < 0.8: fade = t / 0.8
        elif t > DURATION - 0.8: fade = (DURATION - t) / 0.8
        out_l *= fade
        out_r *= fade
        
        out_l = max(-1.0, min(1.0, out_l))
        out_r = max(-1.0, min(1.0, out_r))
        
        struct.pack_into('<hh', audio_data, i * 4, int(out_l * 32767), int(out_r * 32767))

    output_path = "apps/brt-video/public/silicon_loop.wav"
    with wave.open(output_path, 'w') as wav_file:
        wav_file.setnchannels(2)
        wav_file.setsampwidth(2)
        wav_file.setframerate(SAMPLE_RATE)
        wav_file.writeframes(audio_data)

if __name__ == "__main__":
    synth()
