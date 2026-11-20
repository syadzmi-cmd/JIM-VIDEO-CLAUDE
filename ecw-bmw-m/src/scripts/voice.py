"""Assemble per-line TTS clips into one tight voice track.
Trims lead/tail silence, shortens internal pauses > MAXP, joins lines with GAP.
Writes assets/audio/voice.wav and src/words_edit.json (output-time word timings)."""
import json, subprocess, sys, numpy as np, wave
lines_dir, P = sys.argv[1], sys.argv[2]
SR = 48000; HOP = int(SR*0.01); MAXP = 0.16; GAP = 0.09; BIG_GAP = 0.20
BREAK_AFTER = {"L02", "L05", "L09", "L11", "L14", "L17", "L19", "L20"}  # small breath between sections
lines = json.load(open(f"{lines_dir}/words.json"))
def load(p):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", p, "-ac", "1", "-ar", str(SR), "-f", "s16le", "-"], capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.int16).astype(np.float32)/32768
out = []; t = 0.0; allw = []
for L in lines:
    x = load(f"{lines_dir}/{L['id']}.mp3")
    n = len(x)//HOP
    db = 20*np.log10(np.array([np.sqrt(np.mean(x[i*HOP:(i+1)*HOP]**2)) for i in range(n)])+1e-9)
    s0 = max(0, L["words"][0]["s"]-0.03); s1 = min(len(x)/SR, L["words"][-1]["e"]+0.10)
    # keep-ranges: remove part of silent runs longer than MAXP inside [s0,s1]
    sil = db < -40; cuts = []; i = int(s0/0.01)
    while i < int(s1/0.01):
        if sil[i]:
            j = i
            while j < n and sil[j]: j += 1
            if (j-i)*0.01 > MAXP and j*0.01 < s1: cuts.append((i*0.01+MAXP/2, j*0.01-MAXP/2))
            i = j
        else: i += 1
    keep = []; a = s0
    for c0, c1 in cuts: keep.append((a, c0)); a = c1
    keep.append((a, s1))
    def omap(v):
        o = 0
        for k0, k1 in keep:
            if v <= k1: return o + max(0, v-k0)
            o += k1-k0
        return o
    seg = np.concatenate([x[int(k0*SR):int(k1*SR)] for k0, k1 in keep])
    fade = int(SR*0.008); seg[:fade] *= np.linspace(0, 1, fade); seg[-fade:] *= np.linspace(1, 0, fade)
    L["start"] = t
    for w in L["words"]:
        allw.append({"line": L["id"], "w": w["w"], "s": round(t+omap(w["s"]), 3), "e": round(t+omap(w["e"]), 3)})
    out.append(seg); t += len(seg)/SR
    L["end"] = t
    g = BIG_GAP if L["id"] in BREAK_AFTER else GAP
    out.append(np.zeros(int(SR*g))); t += g
y = np.concatenate(out)
y = y/np.abs(y).max()*0.89
w = wave.open(f"{P}/assets/audio/voice.wav", "wb"); w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
w.writeframes((y*32767).astype(np.int16).tobytes()); w.close()
json.dump({"dur": round(t, 3), "lines": [{"id": L["id"], "show": L["show"], "start": round(L["start"], 3), "end": round(L["end"], 3)} for L in lines], "words": allw},
          open(f"{P}/src/words_edit.json", "w"), ensure_ascii=False, indent=1)
for L in lines: print(f"{L['id']} {L['start']:6.2f}-{L['end']:6.2f}  {L['show']}")
print("total", round(t, 2))
