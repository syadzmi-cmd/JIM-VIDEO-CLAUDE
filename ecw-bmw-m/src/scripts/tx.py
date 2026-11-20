import sys, json, wave, numpy as np
from faster_whisper import WhisperModel
m = WhisperModel(sys.argv[3], device="cpu", compute_type="int8", cpu_threads=4)
w=wave.open(sys.argv[1]); a=np.frombuffer(w.readframes(w.getnframes()),np.int16).astype(np.float32)/32768.0
segs, info = m.transcribe(a, language=sys.argv[4] if len(sys.argv)>4 else None, word_timestamps=True, beam_size=5,
  initial_prompt="BMW M cars explained: M3, M4, M5, XM, M340i, Competition, CS, CSL, M Performance, M Sport, xDrive, Touring.")
print("lang", info.language, info.language_probability)
out=[]
for s in segs:
    out.append({"start":s.start,"end":s.end,"text":s.text,"words":[{"w":w.word,"s":w.start,"e":w.end,"p":w.probability} for w in s.words]})
    print(f"[{s.start:6.2f}-{s.end:6.2f}] {s.text}", flush=True)
json.dump(out, open(sys.argv[2],"w"), ensure_ascii=False, indent=1)
