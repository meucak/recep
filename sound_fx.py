import math
import os
import random
import struct
import subprocess
import wave

SOUNDS_DIR = os.path.expanduser("~/.local/share/cs-bomb/sounds")

def _write_wav(filename, samples, sample_rate=22050):
    filepath = os.path.join(SOUNDS_DIR, filename)
    os.makedirs(SOUNDS_DIR, exist_ok=True)
    with wave.open(filepath, "w") as f:
        f.setnchannels(1)
        f.setsampwidth(2)
        f.setframerate(sample_rate)
        raw = bytearray()
        for s in samples:
            val = max(-32767, min(32767, int(s)))
            raw.extend(struct.pack("<h", val))
        f.writeframes(raw)

def ensure_sounds():
    os.makedirs(SOUNDS_DIR, exist_ok=True)
    rate = 22050

    # 1. Keypad Click / Beep
    f_path = os.path.join(SOUNDS_DIR, "beep.wav")
    if not os.path.exists(f_path):
        duration = 0.04
        samples = []
        for i in range(int(rate * duration)):
            t = i / rate
            env = 1.0 - (t / duration)
            s = math.sin(2.0 * math.pi * 1400 * t) * env * 12000
            samples.append(s)
        _write_wav("beep.wav", samples, rate)

    # 2. Warning Beep (Timer tick)
    f_path = os.path.join(SOUNDS_DIR, "tick.wav")
    if not os.path.exists(f_path):
        duration = 0.05
        samples = []
        for i in range(int(rate * duration)):
            t = i / rate
            env = 1.0 - (t / duration) ** 0.5
            s = (1.0 if math.sin(2.0 * math.pi * 950 * t) > 0 else -1.0) * env * 8000
            samples.append(s)
        _write_wav("tick.wav", samples, rate)

    # 3. Error Buzz
    f_path = os.path.join(SOUNDS_DIR, "error.wav")
    if not os.path.exists(f_path):
        duration = 0.22
        samples = []
        for i in range(int(rate * duration)):
            t = i / rate
            env = 1.0 - (t / duration)
            s = (1.0 if math.sin(2.0 * math.pi * 160 * t) > 0 else -1.0) * env * 15000
            samples.append(s)
        _write_wav("error.wav", samples, rate)

    # 4. Defuse Chime
    f_path = os.path.join(SOUNDS_DIR, "defuse.wav")
    if not os.path.exists(f_path):
        duration = 0.6
        samples = []
        notes = [(0.0, 0.18, 784), (0.18, 0.36, 987), (0.36, 0.6, 1318)]
        for i in range(int(rate * duration)):
            t = i / rate
            sample = 0
            for start, end, freq in notes:
                if start <= t < end:
                    local_t = t - start
                    local_dur = end - start
                    env = (1.0 - local_t / local_dur) ** 0.7
                    sample += math.sin(2.0 * math.pi * freq * local_t) * env * 14000
            samples.append(sample)
        _write_wav("defuse.wav", samples, rate)

    # 5. Explosion Boom & Debris Rumble
    f_path = os.path.join(SOUNDS_DIR, "explode.wav")
    if not os.path.exists(f_path):
        duration = 1.2
        samples = []
        for i in range(int(rate * duration)):
            t = i / rate
            env = math.exp(-3.5 * t)
            # Low frequency rumble + filtered noise
            noise = (random.random() * 2.0 - 1.0)
            sub = math.sin(2.0 * math.pi * 55.0 * (1.0 - 0.5 * t) * t)
            s = (sub * 0.7 + noise * 0.3) * env * 24000
            samples.append(s)
        _write_wav("explode.wav", samples, rate)

    # 6. Beam Scanner Sweep
    f_path = os.path.join(SOUNDS_DIR, "scan.wav")
    if not os.path.exists(f_path):
        duration = 1.2
        samples = []
        for i in range(int(rate * duration)):
            t = i / rate
            freq = 300 + 400 * math.sin(math.pi * t / duration)
            env = math.sin(math.pi * t / duration) ** 0.5
            s = math.sin(2.0 * math.pi * freq * t) * env * 10000
            samples.append(s)
        _write_wav("scan.wav", samples, rate)

def play(name):
    wav_path = os.path.join(SOUNDS_DIR, f"{name}.wav")
    if os.path.exists(wav_path):
        try:
            subprocess.Popen(["aplay", "-q", wav_path], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except Exception:
            pass

if __name__ == "__main__":
    ensure_sounds()
    print("All sounds generated successfully!")
    play("beep")