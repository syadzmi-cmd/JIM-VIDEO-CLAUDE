"""Cut list: silences + manual content cuts -> work/edl.json (source/out times, face anchor, zoom).

Usage: python3 edl.py <workdir> <source.mp4>
"""
import json, sys, wave, subprocess
import numpy as np
import cv2

S, SRC = sys.argv[1], sys.argv[2]
w = wave.open(f'{S}/work/thm.wav'); sr = w.getframerate()
x = np.frombuffer(w.readframes(w.getnframes()), np.int16) / 32768.0
DUR = len(x) / sr
hop = int(sr * 0.02); n = len(x) // hop
db = np.array([20 * np.log10(np.sqrt(np.mean(x[i * hop:(i + 1) * hop] ** 2)) + 1e-9) for i in range(n)])
sil = db < -36; runs = []; i = 0
while i < n:
    if sil[i]:
        j = i
        while j < n and sil[j]: j += 1
        if (j - i) * 0.02 >= 0.30: runs.append((i * 0.02, j * 0.02))
        i = j
    else:
        i += 1
rm = []
for a, b in runs:
    a2 = a + 0.20 if a > 0 else 0
    b2 = b - 0.10 if b < DUR - 0.05 else DUR
    if b2 - a2 > 0.05: rm.append((a2, b2))
# manual content cuts (source seconds)
rm += [(3.36, 4.82),    # "Berbanding GR Yaris," repeats the hook
       (43.98, 44.60),  # "Sebab apa?" (2nd)
       (49.52, 50.36),  # stumble + "Sebab apa?" (3rd)
       (64.74, DUR)]    # tail after Assalamualaikum
rm.sort(); merged = []
for a, b in rm:
    if merged and a <= merged[-1][1]: merged[-1] = (merged[-1][0], max(b, merged[-1][1]))
    else: merged.append((a, b))
keep = []; t = 0
for a, b in merged:
    if a > t: keep.append((t, a))
    t = max(t, b)
if t < DUR: keep.append((t, DUR))
fr = lambda v: round(v * 30) / 30
keep = [(fr(a), fr(b)) for a, b in keep if fr(b) - fr(a) >= 2 / 30]

# source shot changes (the raw file is already a multi-angle edit)
SHOTS = [0, 3.3667, 9.8667, 15.2333, 20.5667, 28.8333, 32.0333, 34.7667, 37.7667, 41.6, 48.1333, 53.2667, 55.7667, 999]
shot_of = lambda t: max(k for k, s in enumerate(SHOTS) if s <= t + 1e-3)

casc = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
def face(t):
    raw = subprocess.run(['ffmpeg', '-nostdin', '-v', 'error', '-ss', f'{t:.3f}', '-i', SRC, '-frames:v', '1',
                          '-vf', 'scale=720:1280', '-f', 'rawvideo', '-pix_fmt', 'gray', '-'], capture_output=True).stdout
    g = np.frombuffer(raw, np.uint8).reshape(1280, 720)
    f = casc.detectMultiScale(g, 1.1, 6, minSize=(40, 40))
    if len(f) == 0: return None
    x0, y0, fw, fh = max(f, key=lambda r: r[2] * r[3])
    return ((x0 + fw / 2) * 2, (y0 + fh / 2) * 2)  # in 1440x2560 source px

pieces = []
for a, b in keep:
    cuts = [c for c in SHOTS if a + 0.05 < c < b - 0.05]
    edges = [a] + [fr(c) for c in cuts] + [b]
    for k in range(len(edges) - 1):
        pieces.append((edges[k], edges[k + 1], k > 0))  # flag: starts at a source shot change
segs = []; o = 0; z = 1.0; plen = 99
for a, b, srcchange in pieces:
    if not segs or srcchange or shot_of(a + 0.01) != segs[-1]["shot"]:
        z = 1.0
    elif plen >= 0.7:
        z = 1.0 if z > 1.0 else 1.18
    f = face((a + b) / 2) or face(a + 0.1) or (720, 1000)
    segs.append({"src": a, "end": b, "out": round(o, 4), "fx": f[0], "fy": f[1], "zoom": z, "shot": shot_of(a + 0.01)})
    o += b - a; plen = b - a
print(f"source {DUR:.2f}s -> edit {o:.2f}s, {len(segs)} segs")
for s in segs: print(f"  {s['src']:6.2f}-{s['end']:6.2f} -> {s['out']:6.2f}  z{s['zoom']} shot{s['shot']} face({s['fx']:.0f},{s['fy']:.0f})")
json.dump({"segs": segs, "dur": o}, open(f'{S}/work/edl.json', 'w'), indent=1)
