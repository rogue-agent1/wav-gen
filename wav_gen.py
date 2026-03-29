#!/usr/bin/env python3
"""WAV audio file generator — sine, square, sawtooth, noise."""
import sys, struct, math, random

def gen_samples(freq, duration, sample_rate=44100, wave="sine", amplitude=0.8):
    n = int(duration * sample_rate); samples = []
    for i in range(n):
        t = i / sample_rate; phase = (freq * t) % 1.0
        if wave == "sine": v = math.sin(2 * math.pi * freq * t)
        elif wave == "square": v = 1.0 if phase < 0.5 else -1.0
        elif wave == "sawtooth": v = 2.0 * phase - 1.0
        elif wave == "noise": v = random.uniform(-1, 1)
        else: v = 0
        samples.append(int(v * amplitude * 32767))
    return samples

def encode_wav(samples, sample_rate=44100, bits=16):
    n = len(samples); data_size = n * (bits // 8)
    header = struct.pack("<4sI4s", b"RIFF", 36 + data_size, b"WAVE")
    fmt = struct.pack("<4sIHHIIHH", b"fmt ", 16, 1, 1, sample_rate, sample_rate * bits // 8, bits // 8, bits)
    data_hdr = struct.pack("<4sI", b"data", data_size)
    raw = b"".join(struct.pack("<h", max(-32768, min(32767, s))) for s in samples)
    return header + fmt + data_hdr + raw

def decode_wav_header(data):
    if data[:4] != b"RIFF" or data[8:12] != b"WAVE": raise ValueError("Not WAV")
    # fmt chunk at offset 20: audio_fmt(H), channels(H), sample_rate(I), byte_rate(I), block_align(H), bits(H)
    afmt, channels, sr, byte_rate, block_align, bits = struct.unpack_from("<HHIIHH", data, 20)
    data_size = struct.unpack_from("<I", data, 40)[0]
    num_samples = data_size // (bits // 8)
    return {"channels": channels, "sample_rate": sr, "bits": bits, "samples": num_samples, "duration": num_samples / sr}

def main():
    if len(sys.argv) < 2: print("Usage: wav_gen.py <demo|test>"); return
    if sys.argv[1] == "test":
        s = gen_samples(440, 0.1)
        assert len(s) == 4410
        assert all(-32768 <= v <= 32767 for v in s)
        wav = encode_wav(s)
        assert wav[:4] == b"RIFF"; assert wav[8:12] == b"WAVE"
        info = decode_wav_header(wav)
        assert info["sample_rate"] == 44100; assert info["samples"] == 4410
        assert abs(info["duration"] - 0.1) < 0.001
        for w in ["sine", "square", "sawtooth", "noise"]:
            s2 = gen_samples(440, 0.01, wave=w)
            assert len(s2) == 441
        try: decode_wav_header(b"NOPE"); assert False
        except ValueError: pass
        print("All tests passed!")
    else:
        s = gen_samples(440, 1.0, wave="sine")
        wav = encode_wav(s)
        print(f"Generated WAV: {len(wav)} bytes, {decode_wav_header(wav)}")

if __name__ == "__main__": main()
