"""Build index.html from src/template.html + src/words_edit.json (TTS word timings).

Usage: python3 src/build.py
"""
import json
import re
from pathlib import Path

from cars import CAR_CSS, car_svg

ROOT = Path(__file__).resolve().parent.parent
D = json.load(open(ROOT / "src/words_edit.json"))
VODUR = D["dur"]
DUR = round(VODUR + 0.9, 2)
IDS = [l["id"] for l in D["lines"]]
LS = {l["id"]: l["start"] for l in D["lines"]}
LE = {l["id"]: l["end"] for l in D["lines"]}
WORDS = {i: [w for w in D["words"] if w["line"] == i] for i in IDS}
wt = lambda i, k: WORDS[i][k]["s"]


def scene_range(i):
    k = IDS.index(i)
    s = 0.0 if k == 0 else LS[i]
    e = LS[IDS[k + 1]] if k + 1 < len(IDS) else DUR
    return s, e


# ---------------- chapters (HUD, top-right) ----------------
CHAPTERS = [("L01", "01 · HOOK"), ("L03", "02 · M = ?"), ("L06", "03 · MODEL"), ("L12", "04 · BADGE"),
            ("L15", "05 · M PERF"), ("L18", "06 · M SPORT"), ("L20", "07 · DECODE"), ("L21", "ECW")]

# ---------------- SFX (line, word idx | None=line start, offset, name, vol) ----------------
SFX = [
    ("L01", None, 0.0, "impact", 0.75), ("L01", None, 0.05, "shimmer", 0.30), ("L01", 2, 0, "glitch", 0.18),
    ("L02", None, 0, "whoosh", 0.22), ("L02", 2, 0, "whoosh", 0.14), ("L02", 2, 0.25, "whoosh", 0.12), ("L02", 2, 0.5, "whoosh", 0.12),
    ("L02", 5, 0, "pop", 0.35), ("L02", 8, 0, "thud", 0.5),
    ("L03", None, 0, "impact", 0.40), ("L03", 2, 0, "riser", 0.18), ("L03", 2, 0.1, "whoosh", 0.22), ("L03", 3, 0, "tick", 0.35),
    ("L04", None, 0, "whoosh", 0.22), ("L04", 3, 0, "pop", 0.45), ("L04", 4, 0, "pop", 0.35), ("L04", 5, 0, "tick", 0.4),
    ("L04", 5, 0.13, "tick", 0.4), ("L04", 5, 0.26, "tick", 0.4), ("L04", 5, 0.39, "pop", 0.4), ("L04", -1, 0.3, "ding", 0.3),
    ("L05", None, 0, "whoosh", 0.22), ("L05", 1, 0, "pop", 0.3), ("L05", 2, 0, "pop", 0.3), ("L05", 4, 0, "pop", 0.35),
    ("L06", None, 0, "whoosh", 0.24), ("L06", None, 0.02, "pop", 0.4), ("L06", 1, 0, "pop", 0.35),
    ("L07", None, 0, "whoosh", 0.24), ("L07", None, 0.02, "pop", 0.4), ("L07", 1, 0, "pop", 0.35),
    ("L08", None, 0, "whoosh", 0.24), ("L08", None, 0.02, "pop", 0.4), ("L08", 1, 0, "tick", 0.35), ("L08", 4, 0, "pop", 0.35),
    ("L08", 6, 0, "glitch", 0.15), ("L08", 6, 0.02, "pop", 0.4),
    ("L09", None, 0, "whoosh", 0.24), ("L09", None, 0.02, "pop", 0.4), ("L09", 4, -0.1, "riser", 0.2), ("L09", 4, 0, "impact", 0.3), ("L09", 4, 0.9, "ding", 0.3),
    ("L10", None, 0, "pop", 0.35), ("L10", 1, 0, "impact", 0.45), ("L10", 1, 0.02, "glitch", 0.15), ("L10", 2, 0, "whoosh", 0.22), ("L10", 5, 0, "pop", 0.4),
    ("L11", None, 0, "whoosh", 0.24), ("L11", None, 0.02, "pop", 0.4), ("L11", 3, 0, "tick", 0.35), ("L11", 5, 0, "thud", 0.45), ("L11", 5, 0.05, "shimmer", 0.25),
    ("L12", None, 0, "tick", 0.35), ("L12", 1, 0, "pop", 0.45), ("L12", 2, 0, "riser", 0.2), ("L12", 2, 0.05, "impact", 0.4),
    ("L13", None, 0, "whoosh", 0.22), ("L13", None, 0.02, "pop", 0.4), ("L13", 3, 0, "ding", 0.28), ("L13", 5, 0, "ding", 0.28), ("L13", 6, 0, "whoosh", 0.2),
    ("L14", None, 0, "pop", 0.4), ("L14", 2, 0, "impact", 0.35), ("L14", 2, 0.02, "glitch", 0.14), ("L14", 3, 0, "tick", 0.35), ("L14", 5, -0.1, "pop", 0.4),
    ("L15", None, 0, "whoosh", 0.22), ("L15", None, 0.15, "whoosh", 0.12), ("L15", 2, 0, "thud", 0.35), ("L15", 3, 0, "pop", 0.35),
    ("L16", None, 0, "whoosh", 0.2), ("L16", 4, 0, "pop", 0.4), ("L16", 5, 0, "ding", 0.25), ("L16", 6, -0.2, "whoosh", 0.22), ("L16", 6, 0, "pop", 0.4),
    ("L17", None, 0, "whoosh", 0.22), ("L17", 2, 0, "riser", 0.15), ("L17", 6, 0, "riser", 0.15), ("L17", 5, 0, "thud", 0.5),
    ("L18", None, 0, "glitch", 0.2), ("L18", None, 0.02, "whoosh", 0.24), ("L18", 2, 0, "pop", 0.35), ("L18", 4, 0, "impact", 0.45),
    ("L19", None, 0, "thud", 0.5), ("L19", 2, 0, "ding", 0.28), ("L19", 4, 0, "ding", 0.28), ("L19", 6, 0, "thud", 0.5), ("L19", 8, 0, "glitch", 0.14),
    ("L20", None, 0, "tick", 0.35), ("L20", 1, 0, "pop", 0.4), ("L20", 2, 0, "pop", 0.4), ("L20", 3, 0, "pop", 0.4),
    ("L20", 4, 0, "whoosh", 0.18), ("L20", 6, 0, "whoosh", 0.18), ("L20", 8, 0, "whoosh", 0.18), ("L20", 9, 0, "ding", 0.28),
    ("L21", None, -0.6, "riser", 0.22), ("L21", None, 0, "whoosh", 0.24), ("L21", 4, 0, "thud", 0.3), ("L21", 5, 0, "impact", 0.4), ("L21", 8, 0, "shimmer", 0.25),
    ("L22", None, 0, "pop", 0.4), ("L22", 0, 0.05, "impact", 0.35), ("L22", 2, 0, "shimmer", 0.35),
]
SFX_LEN = {"whoosh": 0.55, "pop": 0.12, "ding": 1.2, "thud": 0.45, "impact": 2.2,
           "shimmer": 1.6, "glitch": 0.25, "tick": 0.04, "riser": 1.0}

# ---------------- captions ----------------
FIX = {"kupei": "coupe", "laihtbau": "Leichtbau"}
KEY = {"m", "m2", "m3", "m4", "m5", "x", "suv", "xm", "x5", "competition", "cs", "csl", "leichtbau", "ringan", "laju",
       "power", "lebih", "m340i", "m135", "sport", "performance", "trim", "penuh", "ecw", "motorsports", "motorsport",
       "follow", "besar", "keliru", "xdrive", "hybrid", "plug-in", "betul", "nombor", "sedan", "coupe", "convertible",
       "sahaja", "berbaloi", "tambah", "empat", "roda", "lumba"}
NO_CAP = {"L01"}  # hook title already says it


def caption_words():
    out = []
    for i in IDS:
        if i in NO_CAP:
            continue
        ws = WORDS[i]
        k = 0
        while k < len(ws):
            w = ws[k]
            t = w["w"]
            if t == "E" and k + 2 < len(ws) and ws[k + 1]["w"] == "C" and ws[k + 2]["w"] == "W":
                out.append({"t": "ECW", "s": w["s"], "e": ws[k + 2]["e"], "line": i, "last": False})
                k += 3
                continue
            out.append({"t": FIX.get(t.lower(), t), "s": w["s"], "e": w["e"], "line": i, "last": False})
            k += 1
        out[-1]["last"] = True
    # sentence breaks inside a line: use punctuation from the shown text
    return out


def captions():
    words = caption_words()
    groups, cur = [], []
    for k, w in enumerate(words):
        cur.append(w)
        nxt = words[k + 1] if k + 1 < len(words) else None
        if len(cur) >= 3 or w["last"] or nxt is None or nxt["s"] - w["e"] > 0.12:
            groups.append(cur)
            cur = []
    html, js = [], []
    for gi, g in enumerate(groups):
        start = g[0]["s"]
        nxt_start = groups[gi + 1][0]["s"] if gi + 1 < len(groups) else DUR
        end = min(nxt_start, g[-1]["e"] + 0.5)
        spans = []
        for wi, w in enumerate(g):
            wid = f"cw{gi}_{wi}"
            spans.append(f'<span id="{wid}">{w["t"]}</span>')
            js.append(f'      tl.fromTo("#{wid}", {{ scale: 0.6, opacity: 0, y: 20 }}, {{ scale: 1, opacity: 1, y: 0, duration: 0.12, ease: "back.out(3)" }}, {w["s"]:.3f});')
            js.append(f'      tl.fromTo("#{wid}", {{ color: "#FECD00" }}, {{ color: "{"#FECD00" if w["t"].lower() in KEY else "#FFEFEF"}", duration: 0.1 }}, {max(w["e"], w["s"] + 0.12):.3f});')
        html.append(f'      <div id="cap{gi}" class="clip cap" data-start="{start:.3f}" data-duration="{end - start:.3f}" data-track-index="8" style="z-index:30">{"".join(spans)}</div>')
    return "\n".join(html), "\n".join(js)


def build():
    s = (ROOT / "src/template.html").read_text()
    # scenes
    def scene_attr(m):
        i = m.group(1)
        a, b = scene_range(i)
        return f'data-line="{i}" data-start="{a:.3f}" data-duration="{b - a:.3f}"'
    s = re.sub(r'data-line="(L\d\d)"', scene_attr, s)
    # cars
    def car(m):
        kind, cid, cls, style = m.group(1), m.group(2), m.group(3), m.group(4)
        return car_svg(kind, cid, cls, style)
    s = re.sub(r"__CAR:(\w+):(\w+):(\w*):([^_]+?)__", car, s)
    # chapters
    ch = []
    for k, (lid, label) in enumerate(CHAPTERS):
        a = 0.0 if k == 0 else LS[lid]
        b = LS[CHAPTERS[k + 1][0]] if k + 1 < len(CHAPTERS) else DUR
        ch.append(f'      <div id="ch{k}" class="clip chap" data-start="{a:.3f}" data-duration="{b - a:.3f}" data-track-index="2" style="z-index:21">{label}</div>')
    # transitions: scan bar + flash on every scene change
    trans, exitjs = [], []
    for k, i in enumerate(IDS):
        a, b = scene_range(i)
        if k > 0:
            big = any(c[0] == i for c in CHAPTERS)
            trans.append(f'      <div id="tr{k}" class="clip layer" data-start="{a:.3f}" data-duration="0.32" data-track-index="9" style="z-index:24"><div class="scanbar"></div></div>')
            exitjs.append(f'      tl.fromTo("#tr{k} .scanbar", {{ y: {"-40" if big else "700"}, opacity: {1 if big else 0.6}, scaleY: {1 if big else 0.4} }}, {{ y: {"1940" if big else "1300"}, opacity: 0, duration: 0.3, ease: "power2.out" }}, {a:.3f});')
            exitjs.append(f'      tl.fromTo("#sc_{i}", {{ opacity: 0, scale: 1.04 }}, {{ opacity: 1, scale: 1, duration: 0.12, ease: "power2.out" }}, {a:.3f});')
        if k + 1 < len(IDS):
            exitjs.append(f'      tl.to("#sc_{i}", {{ opacity: 0, scale: 0.97, filter: "blur(6px)", duration: 0.1, ease: "power2.in" }}, {b - 0.1:.3f});')
    # sfx
    rows, lanes = [], []
    items = []
    for lid, wi, off, name, vol in SFX:
        base = LS[lid] if wi is None else (LE[lid] if wi == -1 else wt(lid, wi))
        items.append((max(0.0, round(base + off, 3)), name, vol))
    items.sort()
    for k, (t, n, v) in enumerate(items):
        d = min(SFX_LEN[n], DUR - t)
        lane = next((j for j, e in enumerate(lanes) if e <= t), None)
        if lane is None:
            lanes.append(0)
            lane = len(lanes) - 1
        lanes[lane] = t + d
        rows.append(f'      <audio id="sfx{k}" src="assets/sfx/{n}.wav" data-start="{t:.3f}" data-duration="{d:.3f}" data-track-index="{21 + lane}" data-volume="{v}"></audio>')
    cap_html, cap_js = captions()
    W = {"lines": {i: [round(LS[i], 3), round(LE[i], 3)] for i in IDS}, "words": {i: [w["s"] for w in WORDS[i]] for i in IDS}}
    for k, v in {"__CARCSS__": CAR_CSS, "__CHAPTERS__": "\n".join(ch), "__TRANS__": "\n".join(trans), "__EXITJS__": "\n".join(exitjs),
                 "__SFX__": "\n".join(rows), "__CAPTIONS__": cap_html, "__CAPJS__": cap_js, "__W__": json.dumps(W),
                 "__VODUR__": f"{VODUR:.3f}", "__DUR__": f"{DUR}"}.items():
        s = s.replace(k, v)
    (ROOT / "index.html").write_text(s)
    print(f"index.html written, dur {DUR}s, {len(items)} sfx")


if __name__ == "__main__":
    build()
