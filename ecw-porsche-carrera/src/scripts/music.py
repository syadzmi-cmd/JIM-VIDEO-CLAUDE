"""Synthesize a 112 BPM driving music bed (ducked under the voice), a camera-shutter SFX,
and the voice loudness envelope used to animate the host.

Usage: python3 src/scripts/music.py <duration_seconds>   (run from the project root)
"""
import json
import subprocess
import sys
import wave
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
SR = 48000
rng = np.random.default_rng(911)
D = float(sys.argv[1])


def save(path, x):
    x = np.clip(x, -1, 1)
    y = (x * 32767).astype(np.int16)
    if y.ndim == 1:
        y = np.stack([y, y], 1)
    w = wave.open(str(path), "wb"); w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(y.tobytes()); w.close()


def t_(d):
    return np.arange(int(SR * d)) / SR


def bp_noise(d, lo, hi):
    n = rng.standard_normal(int(SR * d)); F = np.fft.rfft(n); f = np.fft.rfftfreq(len(n), 1 / SR)
    F[(f < lo) | (f > hi)] = 0
    return np.fft.irfft(F, len(n))


def norm(x, p=0.9):
    return x / (np.abs(x).max() + 1e-9) * p


def load_voice():
    raw = subprocess.check_output(["ffmpeg", "-v", "error", "-i", str(ROOT / "assets/audio/voice.wav"), "-ac", "1", "-ar", str(SR), "-f", "s16le", "-"])
    return np.frombuffer(raw, np.int16).astype(np.float32) / 32768


# ---------- camera shutter SFX ----------
def shutter():
    t = t_(0.32)
    c1 = bp_noise(0.32, 1500, 9000) * np.exp(-t * 90)
    c2 = np.zeros_like(t); k = int(SR * 0.09)
    c2[k:] = (bp_noise(0.32, 800, 6000) * np.exp(-t * 70))[: len(t) - k]
    wind = bp_noise(0.32, 300, 2000) * np.exp(-((t - 0.05) / 0.05) ** 2) * 0.3
    return norm(c1 + 0.8 * c2 + wind, 0.85)


save(ROOT / "assets/sfx/shutter.wav", shutter())

# ---------- MUSIC: 112 BPM, E minor, driving synth ----------
BPM = 112; beat = 60 / BPM; N = int(SR * (D + 1))
mus = np.zeros((N, 2))


def add(sig, at, pan=0.0, g=1.0):
    i = int(at * SR); j = min(N, i + len(sig))
    if i >= N:
        return
    s = sig[: j - i] * g; mus[i:j, 0] += s * (1 - pan); mus[i:j, 1] += s * (1 + pan)


kick = (lambda t: np.sin(2 * np.pi * np.cumsum(50 + 110 * np.exp(-t * 35)) / SR) * np.exp(-t * 8))(t_(0.35))
snare = bp_noise(0.2, 1200, 7000) * np.exp(-t_(0.2) * 22) + 0.4 * np.sin(2 * np.pi * 190 * t_(0.2)) * np.exp(-t_(0.2) * 30)
hat = bp_noise(0.05, 7000, 15000) * np.exp(-t_(0.05) * 100)
mid = lambda m: 440 * 2 ** ((m - 69) / 12)


def saw(f, d, decay=3.0):
    t = t_(d)
    x = sum(np.sin(2 * np.pi * f * k * t) / k for k in range(1, 8))
    return x * np.minimum(1, t / 0.004) * np.exp(-t * decay)


def pad(f, d):
    t = t_(d)
    x = sum(np.sin(2 * np.pi * f * k * t * (1 + 0.002 * (k % 2))) / k for k in (1, 2, 3, 4))
    return x * np.minimum(1, t / 0.3) * np.minimum(1, (d - t) / 0.3)


# Em C G D
prog = [(40, [64, 67, 71]), (36, [60, 64, 67]), (43, [62, 67, 71]), (38, [62, 66, 69])]
arp = [0, 1, 2, 1, 0, 2, 1, 2]
bar = 4 * beat; nb = int(D / bar) + 2
for b in range(nb):
    t0 = b * bar; root, ch = prog[b % 4]
    intro = b < 1
    for k in range(4):
        tb = t0 + k * beat
        add(kick, tb, g=0.85)
        if k in (1, 3) and not intro:
            add(snare, tb, g=0.32)
        for h in range(4):
            add(hat, tb + h * beat / 4, pan=0.35, g=0.12 if h % 2 else 0.06)
        for e in range(2):  # driving 8th-note bass
            add(saw(mid(root), beat * 0.45, 6), tb + e * beat / 2, g=0.16)
    add(sum(pad(mid(m), bar) for m in ch) / 3, t0, g=0.07)
    if not intro:
        for k in range(8):
            add(saw(mid(ch[arp[k]] + 12), beat * 0.4, 9), t0 + k * beat / 2, pan=-0.3 if k % 2 else 0.3, g=0.045)
mus = mus[: int(SR * D)]
fo = int(SR * 1.8); mus[-fo:] *= np.linspace(1, 0, fo)[:, None]
mus = mus / np.abs(mus).max() * 0.8

# ---------- sidechain duck under the voice + host envelope ----------
v = load_voice()
hop = int(SR * 0.01)
ve = np.array([np.sqrt(np.mean(v[i:i + hop] ** 2)) for i in range(0, len(v), hop)])
g = np.ones_like(ve); cur = 1.0
for i, e in enumerate(ve):
    tgt = 0.3 if e > 0.015 else 1.0
    a = 0.5 if tgt < cur else 0.03
    cur += (tgt - cur) * a; g[i] = cur
gs = np.interp(np.arange(len(mus)) / SR, np.arange(len(g)) * 0.01, g, right=1.0)
mus *= gs[:, None]
save(ROOT / "assets/audio/music_ducked.wav", mus * 0.5)

# host talk envelope at 10 fps, 0..1
step = 10
env = [float(ve[i:i + step].mean()) for i in range(0, len(ve), step)]
peak = np.percentile(env, 95) or 1
env = [round(min(1.0, x / peak), 2) for x in env]
json.dump(env, open(ROOT / "src/voice_env.json", "w"))
print("music", D, "env frames", len(env))
