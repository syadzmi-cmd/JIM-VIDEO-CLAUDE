"""Generate the host voiceover with edge-tts, one clip per scene, and a timing map.

Usage: python3 src/scripts/tts.py   (run from the project root)
Writes assets/audio/voice.wav and src/timing.json.
Each chunk is [tts_text, display_text]; captions use display_text, timed by the
word boundaries of tts_text.
"""
import asyncio
import json
import os
import subprocess
import tempfile
from pathlib import Path

import edge_tts

ROOT = Path(__file__).resolve().parents[2]
SR = 48000
LEAD = 0.35  # silence before the first word
PROXY = os.environ.get("HTTPS_PROXY") or os.environ.get("https_proxy")


async def synth(text, voice, rate, mp3):
    com = edge_tts.Communicate(text, voice, rate=rate, boundary="WordBoundary", proxy=PROXY)
    words = []
    with open(mp3, "wb") as f:
        async for ch in com.stream():
            if ch["type"] == "audio":
                f.write(ch["data"])
            elif ch["type"] == "WordBoundary":
                words.append({"w": ch["text"], "s": ch["offset"] / 1e7, "e": (ch["offset"] + ch["duration"]) / 1e7})
    return words


def dur(path):
    out = subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(path)])
    return float(out)


def main():
    cfg = json.load(open(ROOT / "src/script.json"))
    tmp = Path(tempfile.mkdtemp())
    t = LEAD
    scenes, parts = [], []
    for i, sc in enumerate(cfg["scenes"]):
        text = " ".join(c[0] for c in sc["chunks"])
        mp3 = tmp / f"{i:02d}.mp3"
        wav = tmp / f"{i:02d}.wav"
        words = asyncio.run(synth(text, cfg["voice"], cfg["rate"], mp3))
        # trim edge-tts leading/trailing silence to the spoken span
        s0 = max(words[0]["s"] - 0.05, 0)
        e1 = words[-1]["e"] + 0.12
        subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", str(mp3), "-ss", f"{s0:.3f}", "-to", f"{e1:.3f}",
                        "-ar", str(SR), "-ac", "1", str(wav)], check=True)
        d = dur(wav)
        # map chunks onto words by word count
        chunks, wi = [], 0
        for tts_txt, disp in sc["chunks"]:
            n = len(tts_txt.split())
            ws = words[wi:wi + n]
            wi += n
            if not ws:
                continue
            chunks.append({"text": disp, "s": round(t + ws[0]["s"] - s0, 3), "e": round(t + ws[-1]["e"] - s0, 3)})
        if wi != len(words):
            print(f"  ! scene {sc['id']}: {len(words)} boundaries vs {wi} script words")
        scenes.append({"id": sc["id"], "expr": sc["expr"], "s": round(t, 3), "e": round(t + d, 3), "chunks": chunks})
        parts.append((wav, t))
        print(f"{sc['id']:12s} {t:6.2f} -> {t + d:6.2f}")
        t += d + cfg["gap"]
    total = t - cfg["gap"]
    # mix onto one timeline
    inputs, filt = [], []
    for k, (wav, at) in enumerate(parts):
        inputs += ["-i", str(wav)]
        filt.append(f"[{k}:a]adelay={int(at * 1000)}:all=1[a{k}]")
    filt.append("".join(f"[a{k}]" for k in range(len(parts))) + f"amix=inputs={len(parts)}:normalize=0[m]")
    out = ROOT / "assets/audio/voice.wav"
    out.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(["ffmpeg", "-y", "-v", "error", *inputs, "-filter_complex", ";".join(filt), "-map", "[m]",
                    "-ar", str(SR), "-ac", "1", str(out)], check=True)
    json.dump({"voice_end": round(total, 3), "scenes": scenes}, open(ROOT / "src/timing.json", "w"), indent=1, ensure_ascii=False)
    print(f"voice total {total:.2f}s")


if __name__ == "__main__":
    main()
