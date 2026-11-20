"""Build index.html from src/template.html + transcript (captions), b-roll and SFX tables.

Usage: python3 src/build.py <transcript.json>
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DUR = 58.25
END_START = 56.04

# ---------------- B-ROLL (output time) ----------------
BROLL = [  # id, file, start, dur, media_start
    ("br1", "b2.mp4", 1.66, 1.94, 0.2),   # GLA35 badge
    ("br2", "b0.mp4", 10.00, 1.90, 0.3),  # car driving off  -> "berjalan"
    ("br3", "b5.mp4", 18.40, 1.68, 0.5),  # interior        -> "comfort"
    ("br4", "b1.mp4", 29.60, 2.30, 0.5),  # rear            -> "enjoy"
    ("br5", "b4.mp4", 41.90, 3.40, 0.3),  # front hero      -> "memang sesuai"
    ("br6", "b3.mp4", 52.72, 3.30, 0.25), # ECW showroom    -> "jumpa dekat ECW"
]

# ---------------- SFX (time, name, volume) ----------------
SFX = [
    (0.00, "impact", 0.70), (0.05, "shimmer", 0.30),
    (1.60, "whoosh", 0.14), (1.62, "glitch", 0.05), (1.72, "pop", 0.45), (2.72, "pop", 0.40),
    (3.60, "whoosh", 0.22), (4.80, "impact", 0.35), (4.90, "shimmer", 0.22), (6.70, "pop", 0.40), (7.08, "ding", 0.30),
    (7.38, "glitch", 0.22), (7.40, "pop", 0.45),
    (8.66, "whoosh", 0.22), (9.98, "whoosh", 0.14), (9.99, "glitch", 0.05),
    (12.06, "tick", 0.40), (12.18, "tick", 0.40), (12.30, "tick", 0.40), (12.42, "tick", 0.40), (12.54, "tick", 0.40), (12.50, "pop", 0.35),
    (13.22, "whoosh", 0.22), (14.06, "pop", 0.30), (15.74, "whoosh", 0.12), (16.40, "pop", 0.40),
    (18.38, "whoosh", 0.14), (18.39, "glitch", 0.05), (18.82, "ding", 0.32), (19.64, "ding", 0.32),
    (20.12, "whoosh", 0.18), (20.96, "thud", 0.45), (21.54, "thud", 0.45),
    (21.90, "whoosh", 0.22), (22.90, "whoosh", 0.12), (25.00, "pop", 0.40), (25.30, "whoosh", 0.12), (26.16, "pop", 0.45), (26.20, "shimmer", 0.22),
    (27.50, "whoosh", 0.22), (28.00, "thud", 0.30),
    (29.58, "whoosh", 0.14), (29.59, "glitch", 0.05), (29.88, "impact", 0.40), (30.00, "shimmer", 0.22),
    (32.12, "glitch", 0.22), (32.14, "whoosh", 0.22), (35.00, "thud", 0.35),
    (36.12, "whoosh", 0.18), (37.04, "thud", 0.50), (38.30, "thud", 0.50), (39.88, "thud", 0.50),
    (41.10, "riser", 0.30), (41.88, "whoosh", 0.14), (41.89, "glitch", 0.05), (42.90, "impact", 0.35), (43.54, "ding", 0.38),
    (46.84, "whoosh", 0.22), (47.66, "pop", 0.35), (48.82, "whoosh", 0.18), (49.70, "pop", 0.40),
    (50.44, "impact", 0.45), (50.50, "shimmer", 0.30),
    (52.70, "whoosh", 0.14), (52.71, "glitch", 0.05), (53.00, "thud", 0.25), (53.32, "pop", 0.40), (54.44, "tick", 0.40),
    (56.06, "pop", 0.40), (56.10, "shimmer", 0.35),
]
SFX_LEN = {"whoosh": 0.55, "pop": 0.12, "ding": 1.2, "thud": 0.45, "impact": 2.2,
           "shimmer": 1.6, "glitch": 0.25, "tick": 0.04, "riser": 1.0}

# ---------------- CAPTIONS ----------------
FIX = {"cerita": "cita", "rekon": "recond", "ecw": "ECW", "4matic": "4MATIC"}
KEY = {"racun", "raya", "gla35", "4matic", "terbaik", "kenapa", "berjalan", "sedara", "mara", "comfort", "mudah",
       "penat", "letih", "enjoy", "ngantuk", "boring", "semangat", "sesuai", "jojo", "ecw", "motorsports", "bangi",
       "makcik", "itam", "kedua", "destinasi"}


def captions(tx_path):
    words = []
    for seg in json.load(open(tx_path)):
        for w in seg["words"]:
            raw = w["w"].strip()
            core = re.sub(r"[^\w]", "", raw)
            if not core:
                continue
            txt = FIX.get(core.lower(), core)
            words.append({"t": txt, "s": w["s"], "e": w["e"], "end_punct": bool(re.search(r"[.,?!]$", raw))})
    groups, cur = [], []
    for i, w in enumerate(words):
        cur.append(w)
        nxt = words[i + 1] if i + 1 < len(words) else None
        if len(cur) >= 3 or w["end_punct"] or nxt is None or nxt["s"] - w["e"] > 0.35:
            groups.append(cur)
            cur = []
    html, js = [], []
    for gi, g in enumerate(groups):
        start = g[0]["s"]
        nxt_start = groups[gi + 1][0]["s"] if gi + 1 < len(groups) else DUR
        end = min(nxt_start, g[-1]["e"] + 0.6)
        if start >= END_START - 0.05:  # end card has its own text
            continue
        end = min(end, END_START)
        spans = []
        for wi, w in enumerate(g):
            wid = f"cw{gi}_{wi}"
            spans.append(f'<span id="{wid}">{w["t"]}</span>')
            js.append(f'      tl.fromTo("#{wid}", {{ scale: 0.6, opacity: 0 }}, {{ scale: 1, opacity: 1, duration: 0.14, ease: "back.out(3)" }}, {max(start, w["s"]):.2f});')
            hl = "#FECD00"
            js.append(f'      tl.fromTo("#{wid}", {{ color: "{hl}" }}, {{ color: "{hl if w["t"].lower() in KEY else "#FFEFEF"}", duration: 0.12 }}, {max(w["e"], w["s"] + 0.15):.2f});')
        html.append(f'      <div class="clip cap" data-start="{start:.2f}" data-duration="{end - start:.2f}" data-track-index="8" style="z-index:30">{"".join(spans)}</div>')
    return "\n".join(html), "\n".join(js)


def build(tx_path):
    s = (ROOT / "src/template.html").read_text()
    broll, bfx, bfxjs = [], [], []
    for i, (bid, f, st, d, ms) in enumerate(BROLL):
        broll.append(f'      <video id="{bid}" class="clip full" src="assets/video/{f}" data-start="{st}" data-duration="{d}" data-media-start="{ms}" data-track-index="1" muted playsinline style="z-index:3"></video>')
        bfx.append(f'      <div id="{bid}s" class="clip layer" data-start="{st}" data-duration="0.4" data-track-index="9" style="z-index:40"><div class="scanbar"></div></div>')
        bfx.append(f'      <div id="{bid}f" class="clip layer flash" data-start="{st}" data-duration="0.3" data-track-index="9" style="z-index:39"></div>')
        bfxjs.append(f'      brollIn("#{bid}", "#{bid}s .scanbar", "#{bid}f", {st}, {d});')
    people = "\n".join(
        f'          <svg class="abs" style="left:{150 + i * 160}px;top:{20 if i % 2 else 0}px;width:130px;height:156px"><use href="#person"/></svg>'
        for i in range(5))
    lanes, sfx_rows = [], []
    for i, (t, n, v) in enumerate(sorted(SFX)):
        d = min(SFX_LEN[n], DUR - t)
        lane = next((k for k, e in enumerate(lanes) if e <= t), None)
        if lane is None:
            lanes.append(0); lane = len(lanes) - 1
        lanes[lane] = t + d
        sfx_rows.append(f'      <audio id="sfx{i}" src="assets/sfx/{n}.wav" data-start="{t:.2f}" data-duration="{d:.2f}" data-track-index="{21 + lane}" data-volume="{v}"></audio>')
    sfx = "\n".join(sfx_rows)
    cap_html, cap_js = captions(tx_path)
    for k, v in {"__BROLL__": "\n".join(broll), "__BFX__": "\n".join(bfx), "__BFXJS__": "\n".join(bfxjs),
                 "__PEOPLE__": people, "__SFX__": sfx, "__CAPTIONS__": cap_html, "__CAPJS__": cap_js,
                 "__ENDDUR__": f"{DUR - END_START:.2f}", "__DUR__": f"{DUR}"}.items():
        s = s.replace(k, v)
    (ROOT / "index.html").write_text(s)
    print("index.html written")


if __name__ == "__main__":
    build(sys.argv[1])
