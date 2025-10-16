import math
import pathlib
import struct
import wave

out = pathlib.Path("_validation/test_ping.wav")
out.parent.mkdir(parents=True, exist_ok=True)

rate = 16_000
duration = 1.0
freq = 440.0

with wave.open(str(out), "w") as wav_file:
    wav_file.setnchannels(1)
    wav_file.setsampwidth(2)
    wav_file.setframerate(rate)
    for i in range(int(rate * duration)):
        value = int(32767 * 0.5 * math.sin(2 * math.pi * freq * i / rate))
        wav_file.writeframes(struct.pack("<h", value))

print(f"Generated {out} ({duration}s @ {rate} Hz)")*** End Patch
