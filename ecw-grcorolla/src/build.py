"""Build index.html from src/template.html + transcript (captions), photo inserts and SFX tables.

Usage: python3 src/build.py src/transcript_edit.json
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DUR = 60.3
END_START = 58.22

# ---------------- FULL-FRAME PHOTO INSERTS (edit time) ----------------
STILLS = [  # id, image, start, dur
    ("f1", "c_engine.jpg", 18.24, 2.42),   # "Enjin dia sama je macam GR Yaris"
    ("f2", "c_burnout.jpg", 24.98, 1.42),  # "Laju ni."
    ("f3", "c_track.jpg", 38.26, 2.40),    # "Mode terakhir pula, memang semua orang nak pakai"
    ("f4", "c_road.jpg", 45.36, 2.20),     # "Kereta ni juga datang dengan tiga mode"
]

# ---------------- SFX (time, name, volume) ----------------
SFX = [
    (0.00, "impact", 0.70), (0.05, "shimmer", 0.30), (1.02, "pop", 0.40), (2.72, "pop", 0.40),
    (3.30, "whoosh", 0.22), (4.16, "impact", 0.30), (4.50, "whoosh", 0.18),
    (5.92, "glitch", 0.20), (5.93, "pop", 0.45), (6.98, "whoosh", 0.22), (7.06, "pop", 0.40), (7.60, "ding", 0.30),
    (8.30, "whoosh", 0.22), (9.30, "pop", 0.35), (9.68, "thud", 0.35),
    (10.78, "whoosh", 0.22), (11.78, "whoosh", 0.18), (11.90, "ding", 0.30), (12.30, "pop", 0.40), (12.66, "ding", 0.22),
    (13.24, "tick", 0.35), (13.36, "tick", 0.35), (13.48, "tick", 0.35), (13.60, "whoosh", 0.18),
    (14.72, "pop", 0.40), (15.90, "pop", 0.40), (16.50, "ding", 0.30), (17.40, "impact", 0.35), (17.42, "shimmer", 0.25),
    (18.22, "whoosh", 0.14), (18.23, "glitch", 0.05), (18.60, "pop", 0.35), (18.90, "thud", 0.30), (19.78, "pop", 0.40),
    (20.70, "tick", 0.35), (20.82, "tick", 0.35), (20.94, "tick", 0.35), (21.00, "whoosh", 0.22),
    (21.40, "riser", 0.25), (22.40, "rev", 0.45), (23.40, "impact", 0.40),
    (24.96, "whoosh", 0.14), (24.97, "glitch", 0.05), (25.00, "rev", 0.30), (25.04, "impact", 0.45),
    (26.50, "whoosh", 0.22), (27.94, "impact", 0.35), (28.20, "tick", 0.35),
    (29.00, "whoosh", 0.22), (30.94, "pop", 0.45),
    (31.76, "whoosh", 0.22), (32.64, "pop", 0.40), (33.66, "pop", 0.40), (34.74, "whoosh", 0.18), (35.92, "pop", 0.40), (37.08, "pop", 0.40),
    (38.24, "whoosh", 0.14), (38.25, "glitch", 0.05), (39.56, "pop", 0.35), (40.20, "pop", 0.35),
    (40.72, "impact", 0.40), (41.72, "pop", 0.40), (42.70, "ding", 0.30),
    (43.86, "whoosh", 0.18), (44.72, "thud", 0.50), (44.76, "pop", 0.40),
    (45.34, "whoosh", 0.14), (45.35, "glitch", 0.05), (46.86, "impact", 0.30), (47.70, "whoosh", 0.20),
    (48.00, "tick", 0.40), (48.54, "tick", 0.40), (49.48, "tick", 0.40), (49.50, "pop", 0.30),
    (50.56, "whoosh", 0.18), (51.52, "impact", 0.35),
    (52.16, "impact", 0.35), (52.96, "pop", 0.40), (54.36, "pop", 0.45), (54.40, "shimmer", 0.25),
    (55.12, "whoosh", 0.22), (55.30, "thud", 0.25), (57.00, "tick", 0.35), (57.12, "tick", 0.35), (57.24, "tick", 0.35),
    (58.22, "pop", 0.40), (58.50, "shimmer", 0.35),
]
SFX_LEN = {"whoosh": 0.55, "pop": 0.12, "ding": 1.2, "thud": 0.45, "impact": 2.2,
           "shimmer": 1.6, "glitch": 0.25, "tick": 0.04, "riser": 1.0, "rev": 1.8}

# ---------------- CAPTIONS ----------------
FIX = {"practical": "praktikal", "ecw": "ECW"}
KEY = {"corolla", "yaris", "praktikal", "empat", "pintu", "manual", "auto", "lelaki", "perempuan", "senang", "enjin",
       "300", "horsepower", "laju", "four-wheel", "drive", "differential", "tiga", "normal", "gravel", "track",
       "60", "40", "70", "30", "50", "cukup", "eco", "comfort", "sport", "jai", "ecw", "motorsports", "bangi"}


def captions(tx_path):
    words = []
    for seg in json.load(open(tx_path)):
        for w in seg["words"]:
            raw = w["w"].strip()
            if raw.startswith("-") and words:  # "four" + "-wheel"
                words[-1]["t"] += raw.rstrip(".,?!"); words[-1]["e"] = w["e"]
                words[-1]["end_punct"] = bool(re.search(r"[.,?!]$", raw)); continue
            core = re.sub(r"[^\w-]", "", raw)
            if not core:
                continue
            txt = FIX.get(core.lower(), core)
            words.append({"t": txt, "s": w["s"], "e": w["e"], "end_punct": bool(re.search(r"[.,?!]$", raw))})
    groups, cur = [], []
    for i, w in enumerate(words):
        cur.append(w)
        nxt = words[i + 1] if i + 1 < len(words) else None
        if len(cur) >= 3 or w["end_punct"] or nxt is None or nxt["s"] - w["e"] > 0.35:
            groups.append(cur); cur = []
    html, js = [], []
    for gi, g in enumerate(groups):
        start = g[0]["s"]
        nxt_start = groups[gi + 1][0]["s"] if gi + 1 < len(groups) else DUR
        end = min(nxt_start, g[-1]["e"] + 0.6)
        if start >= END_START - 0.05:
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
    stills, bfx, bfxjs = [], [], []
    for sid, img, st, d in STILLS:
        stills.append(
            f'      <div id="{sid}" class="clip layer still" data-start="{st}" data-duration="{d}" data-track-index="1" style="z-index:3">'
            f'<img class="bg" src="assets/img/{img}" alt=""><div class="fgwrap"><img class="fg" src="assets/img/{img}" alt=""></div>'
            f'<div class="shade"></div><div class="credit">FOTO: TOYOTA</div></div>')
        bfx.append(f'      <div id="{sid}s" class="clip layer" data-start="{st}" data-duration="0.4" data-track-index="9" style="z-index:40"><div class="scanbar"></div></div>')
        bfx.append(f'      <div id="{sid}f" class="clip layer flash" data-start="{st}" data-duration="0.3" data-track-index="9" style="z-index:39"></div>')
        bfxjs.append(f'      stillIn("#{sid}", {st}, {d});')
    lanes, sfx_rows = [], []
    for i, (t, n, v) in enumerate(sorted(SFX)):
        d = min(SFX_LEN[n], DUR - t)
        lane = next((k for k, e in enumerate(lanes) if e <= t), None)
        if lane is None:
            lanes.append(0); lane = len(lanes) - 1
        lanes[lane] = t + d
        sfx_rows.append(f'      <audio id="sfx{i}" src="assets/sfx/{n}.wav" data-start="{t:.2f}" data-duration="{d:.2f}" data-track-index="{21 + lane}" data-volume="{v}"></audio>')
    cap_html, cap_js = captions(tx_path)
    for k, v in {"__STILLS__": "\n".join(stills), "__BFX__": "\n".join(bfx), "__BFXJS__": "\n".join(bfxjs),
                 "__SFX__": "\n".join(sfx_rows), "__CAPTIONS__": cap_html, "__CAPJS__": cap_js,
                 "__ENDDUR__": f"{DUR - END_START:.2f}", "__DUR__": f"{DUR}"}.items():
        s = s.replace(k, v)
    (ROOT / "index.html").write_text(s)
    print("index.html written")


if __name__ == "__main__":
    build(sys.argv[1])
