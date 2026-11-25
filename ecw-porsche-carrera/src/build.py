"""Build index.html from src/template.html + src/timing.json (voice timing) + model data.

Usage: python3 src/build.py   (run from the project root)
"""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
T = json.load(open(ROOT / "src/timing.json"))
ENV = json.load(open(ROOT / "src/voice_env.json"))
CRED = {Path(c["file"]).stem: c for c in json.load(open(ROOT / "assets/img/CREDITS.json"))}
SC = {s["id"]: s for s in T["scenes"]}
VOICE_END = T["voice_end"]
DUR = round(VOICE_END + 1.6, 2)
EXPRS = ["shock", "laugh", "angry", "excited", "thinking", "wink", "shrug", "cry", "love"]


def ch(scene, i):
    """start time of chunk i of a scene"""
    return SC[scene]["chunks"][i]["s"]


# ---------------- MODELS ----------------
MODELS = [
    dict(id="carrera", name="911 Carrera", pip="CARRERA", img="carrera", rot=-3, tape="", ps=394, acc=4.1,
         x=("ENJIN", "3.0L", True), spec="3.0L TWIN-TURBO · PDK 8 · RWD", sticker=("HARIAN ✓", 5),
         t_x=1, t_ps=2, t_acc=3, accfn="", expr={5: "wink"}),
    dict(id="carrera_t", name="911 Carrera T", pip="T", img="carrera_t", rot=3, tape="p", ps=394, acc=4.5,
         x=("GEARBOX", "MANUAL 6", False), spec="RINGAN · STERENG RODA BELAKANG ✓", sticker=("KAKI DRIVE", 1),
         t_x=3, t_ps=2, t_acc=4, accfn="", expr={}, spec_at=5),
    dict(id="carrera_s", name="911 Carrera S", pip="S", img="carrera_s", rot=-2.5, tape="r", ps=480, acc=3.3,
         x=("MAKS", "308", True, "km/j"), spec="3.0L TWIN-TURBO · PDK 8 · RWD", sticker=("GANAS!", 0),
         t_x=4, t_ps=2, t_acc=3, accfn="*Sport Chrono", expr={}),
    dict(id="carrera_4s", name="911 Carrera 4S", pip="4S", img="carrera_4s", rot=2.5, tape="", ps=480, acc=3.3,
         x=("PACUAN", "AWD", True), spec="4 RODA · YAKIN MASA HUJAN", sticker=("4 RODA", 2),
         t_x=2, t_ps=1, t_acc=3, accfn="*Sport Chrono", expr={3: "laugh"}, rain=True),
    dict(id="gts", name="911 Carrera GTS", pip="GTS", img="gts", rot=-2, tape="r", ps=541, acc=3.0,
         x=("ENJIN", "3.6L+E", True), spec="T-HYBRID · eTURBO · MOTOR ELEKTRIK", sticker=("RAJA CARRERA", 0),
         t_x=2, t_ps=3, t_acc=4, accfn="", expr={}, crown=True),
]

# ---------------- helpers ----------------
TAPE_CLIP = "polygon(0 8%,5% 0,9% 10%,13% 0,100% 0,96% 12%,100% 25%,95% 38%,100% 52%,96% 66%,100% 80%,95% 92%,100% 100%,0 100%,4% 88%,0 75%,5% 62%,0 48%,4% 34%,0 20%)"


def credit(img):
    c = CRED[img]
    a = re.sub(r"\s+", " ", c["author"])[:40]
    return f"Foto: {a} · {c['license']} · Wikimedia Commons"


def polaroid(pid, img, caption, x, y, w, tape="", fs=None, tapes="corners", cred=True):
    p = round(w * 0.035)
    ph = round((w - 2 * p) * 0.64)
    cb = round(w * 0.16)
    fs = fs or round(w * 0.085)
    tw, th = round(w * 0.3), round(w * 0.075)
    if tapes == "corners":
        tp = [(-round(tw * 0.28), -round(th * 0.35), -38), (w - round(tw * 0.72), -round(th * 0.35), 38)]
    else:
        tp = [(round((w - tw) / 2), -round(th * 0.55), -3)]
    tape_html = "".join(
        f'<div class="tape {tape}" style="left:{tx}px;top:{ty}px;width:{tw}px;height:{th}px;transform:rotate({r}deg);clip-path:{TAPE_CLIP}"></div>'
        for tx, ty, r in tp)
    cr = f'<div class="cr">{credit(img)}</div>' if cred else ""
    return (f'<div id="{pid}" class="pol" style="left:{x}px;top:{y}px;width:{w}px;--p:{p}px;--ph:{ph}px;--cb:{cb}px;--fs:{fs}px">'
            f'<div class="ph"><img src="assets/img/{img}.jpg" alt="">{cr}<div class="flashx"></div></div>'
            f'<div class="cp">{caption}</div>{tape_html}</div>')


body, js, sfx = [], [], []
S = lambda t, n, v: sfx.append((round(t, 2), n, v))

# ================= HOOK =================
h = SC["hook"]; hs, he = 0, SC["intro"]["s"]
body.append(f'''      <!-- HOOK -->
      <div id="hook" class="clip layer" data-start="{hs}" data-duration="{he - hs:.2f}" data-track-index="3" style="z-index:10">
        <div id="hkLbl" class="row" style="top:170px;font-family:var(--font-mono);font-weight:700;font-size:34px;letter-spacing:0.3em;color:var(--yellow)">PORSCHE 911 · 992.2</div>
        <div id="hkA" class="row big" style="top:220px;font-size:220px"><span class="skew">CARRERA</span></div>
        <div class="row" style="top:440px"><span id="hkB" class="sticker" style="font-size:76px;transform:rotate(-3deg)">MANA SATU?</span></div>
        {polaroid("hkP1", "carrera_t", "Carrera T", 40, 640, 420, "p", cred=False)}
        {polaroid("hkP3", "gts", "GTS", 620, 660, 420, "r", cred=False)}
        {polaroid("hkP2", "carrera_s", "Carrera S", 320, 590, 450, "", cred=False)}
        <div class="row" style="top:1010px"><span id="hk5" class="sticker m" style="font-size:60px;transform:rotate(4deg)">5 MODEL!</span></div>
        <svg id="hkS1" class="sparkle" style="left:900px;top:250px"><use href="#star"/></svg>
        <svg id="hkS2" class="sparkle" style="left:110px;top:470px;width:46px;height:46px"><use href="#star"/></svg>
      </div>''')
js.append(f'''      // HOOK (frame 0 fully composed for thumbnail)
      tl.set(["#hkLbl", "#hkA", "#hkB"], {{ opacity: 1 }}, 0);
      tl.fromTo("#hkA", {{ scale: 1 }}, {{ scale: 1.06, duration: 4, ease: "sine.out" }}, 0);
      tl.fromTo("#hkP1", {{ rotation: -9 }}, {{ rotation: -6, duration: 4, ease: "sine.inOut" }}, 0);
      tl.fromTo("#hkP3", {{ rotation: 10 }}, {{ rotation: 7, duration: 4, ease: "sine.inOut" }}, 0);
      tl.fromTo("#hkP2", {{ rotation: -1, y: 0 }}, {{ rotation: 1, y: -16, duration: 4, ease: "sine.inOut" }}, 0);
      tl.fromTo("#hkB", {{ rotation: -3, scale: 1 }}, {{ rotation: 2, scale: 1.08, duration: 0.18, yoyo: true, repeat: 3, ease: "sine.inOut" }}, {ch("hook", 1):.2f});
      twinkle("#hkS1", 0.1); twinkle("#hkS2", 0.4);
      pop("#hk5", {ch("hook", 2) + 1.0:.2f}, {{ rotation: 4 }});
      polOut("#hkP1", {ch("hook", 3):.2f}, -1); polOut("#hkP3", {ch("hook", 3) + 0.08:.2f}, 1); polOut("#hkP2", {ch("hook", 3) + 0.16:.2f}, -1);
      out(["#hk5", "#hkB"], {ch("hook", 3) + 0.1:.2f});
      tl.to(["#hkA", "#hkLbl"], {{ y: -60, opacity: 0, duration: 0.3, ease: "power2.in" }}, {he - 0.35:.2f});''')
S(0, "impact", 0.6); S(0.02, "shutter", 0.5); S(0.05, "shimmer", 0.25)
S(ch("hook", 1), "pop", 0.35); S(ch("hook", 2) + 1.0, "pop", 0.45)
S(ch("hook", 3), "whoosh", 0.25)

# ================= INTRO =================
i0, i1 = SC["intro"]["s"], SC["carrera"]["s"]
bez = ch("intro", 3); pw = SC["intro"]["chunks"][4]
pt = [pw["s"], pw["s"] + (pw["e"] - pw["s"]) * 0.33, pw["s"] + (pw["e"] - pw["s"]) * 0.7]
body.append(f'''      <!-- INTRO -->
      <div id="intro" class="clip layer" data-start="{i0:.2f}" data-duration="{i1 - i0:.2f}" data-track-index="3" style="z-index:10">
        {polaroid("inP", "rear", "enjin kat belakang!", 150, 260, 780, "r", tapes="top")}
        <svg id="inArrow" class="abs" viewBox="0 0 300 260" style="left:640px;top:880px;width:300px;height:260px">
          <path class="ink" d="M250 240 C 260 150 200 80 90 40"/><path class="ink" d="M90 40 L 140 30 M90 40 L 118 84"/>
        </svg>
        <div id="inChip" class="hand" style="position:absolute;left:150px;top:930px;font-size:66px;transform:rotate(-4deg)">FLAT-6 BOXER</div>
        <div id="inQ" class="row big y" style="top:300px;font-size:170px"><span class="skew">BEZANYA?</span></div>
        <div id="inP1" class="pill" style="top:540px"><div class="n">1</div><div class="t">POWER</div></div>
        <div id="inP2" class="pill" style="top:720px"><div class="n">2</div><div class="t">GEARBOX</div></div>
        <div id="inP3" class="pill" style="top:900px"><div class="n">3</div><div class="t">PACUAN</div></div>
      </div>''')
js.append(f'''      // INTRO
      polIn("#inP", {i0 + 0.05:.2f}, -2);
      drawPath("#inArrow path", {ch("intro", 2) - 0.2:.2f}, 0.45);
      tl.fromTo("#inChip", {{ clipPath: "inset(0 100% 0 0)" }}, {{ clipPath: "inset(0 0% 0 0)", duration: 0.5, ease: "steps(12)" }}, {ch("intro", 1) + 0.3:.2f});
      polOut("#inP", {bez - 0.15:.2f}, 1); out(["#inArrow", "#inChip"], {bez - 0.15:.2f});
      slam("#inQ", {bez:.2f});
      tl.fromTo("#inP1", {{ x: -1100 }}, {{ x: 0, duration: 0.35, ease: "back.out(1.4)" }}, {pt[0]:.2f});
      tl.fromTo("#inP2", {{ x: 1100 }}, {{ x: 0, duration: 0.35, ease: "back.out(1.4)" }}, {pt[1]:.2f});
      tl.fromTo("#inP3", {{ x: -1100 }}, {{ x: 0, duration: 0.35, ease: "back.out(1.4)" }}, {pt[2]:.2f});
      out(["#inQ", "#inP1", "#inP2", "#inP3"], {i1 - 0.25:.2f});''')
S(i0 + 0.05, "whoosh", 0.2); S(i0 + 0.5, "shutter", 0.55); S(i0 + 0.55, "thud", 0.3)
S(ch("intro", 2) - 0.2, "whoosh", 0.12); S(bez - 0.15, "whoosh", 0.22); S(bez, "impact", 0.3)
for t in pt:
    S(t, "pop", 0.4)

# ================= HEADER + PIPS (model section) =================
m0, m1 = SC["carrera"]["s"], SC["body"]["s"]
pips = "".join(f'<div id="pip{k}" class="pip">{m["pip"]}</div>' for k, m in enumerate(MODELS))
body.append(f'''      <!-- HEADER -->
      <div id="hdr" class="clip layer" data-start="{m0:.2f}" data-duration="{m1 - m0:.2f}" data-track-index="2" style="z-index:9">
        <div class="hdr">PORSCHE 911 <b>·</b> CARRERA LINE-UP</div>
        <div class="pips">{pips}</div>
      </div>''')
js.append(f'      rise("#hdr .hdr", {m0:.2f}, 0.3); qa("#hdr .pip").forEach((el, i) => pop(el, {m0 + 0.1:.2f} + i * 0.05));')

# ================= MODEL SCENES =================
for k, m in enumerate(MODELS):
    sid = m["id"]; s0 = SC[sid]["s"]
    s1 = SC[MODELS[k + 1]["id"]]["s"] if k + 1 < len(MODELS) else SC["body"]["s"]
    p = f"m{k}"
    xv = m["x"]
    xunit = f"<small>{xv[3]}</small>" if len(xv) > 3 else ""
    xcls = "v" if xv[2] else "v sm"
    accfn = f'<div class="fn">{m["accfn"]}</div>' if m["accfn"] else ""
    extra = ""
    if m.get("crown"):
        extra += f'<svg id="{p}crown" class="abs" style="left:770px;top:205px;width:170px;height:128px"><use href="#crown"/></svg>'
        extra += "".join(f'<svg id="{p}sp{j}" class="sparkle" style="left:{x}px;top:{y}px"><use href="#star"/></svg>'
                         for j, (x, y) in enumerate([(110, 290), (930, 600), (150, 760)]))
    if m.get("rain"):
        extra += "".join(f'<svg class="abs {p}drop" style="left:{x}px;top:{y}px;width:44px;height:62px"><use href="#drop"/></svg>'
                         for x, y in [(120, 330), (930, 420), (90, 700), (960, 760), (180, 520)])
    body.append(f'''      <!-- {m["name"]} -->
      <div id="{sid}" class="clip layer" data-start="{s0:.2f}" data-duration="{s1 - s0:.2f}" data-track-index="3" style="z-index:10">
        {polaroid(p + "pol", m["img"], m["name"], 170, 270, 740, m["tape"])}
        <div id="{p}stk" class="abs" style="left:610px;top:300px"><span class="sticker" style="font-size:44px;transform:rotate(7deg)">{m["sticker"][0]}</span></div>
        {extra}
        <div id="{p}t1" class="tile" style="left:60px;top:910px"><div class="k">KUASA</div><div class="v"><span id="{p}ps">{m["ps"]}</span><small>PS</small></div></div>
        <div id="{p}t2" class="tile" style="left:390px;top:910px"><div class="k">0-100</div><div class="v"><span id="{p}acc">{m["acc"]:.1f}</span><small>s</small></div>{accfn}</div>
        <div id="{p}t3" class="tile" style="left:720px;top:910px"><div class="k">{xv[0]}</div><div class="{xcls}">{xv[1]}{xunit}</div></div>
        <div id="{p}spec" class="spec" style="top:1118px"><span>{m["spec"]}</span></div>
      </div>''')
    sat = ch(sid, m["sticker"][1]) if m["sticker"][1] > 0 else s0 + 0.75
    spec_at = ch(sid, m["spec_at"]) if "spec_at" in m else s0 + 1.2
    js.append(f'''      // {m["name"]}
      tl.set("#pip{k}", {{ className: "pip on" }}, {s0:.2f}); {"" if k == 0 else f'tl.set("#pip{k-1}", {{ className: "pip" }}, {s0:.2f});'}
      tl.fromTo("#pip{k}", {{ scale: 1.4 }}, {{ scale: 1, duration: 0.3, ease: "back.out(3)" }}, {s0:.2f});
      polIn("#{p}pol", {s0 + 0.02:.2f}, {m["rot"]}, {-1 if k % 2 == 0 else 1});
      pop("#{p}stk", {sat:.2f}, {{ rotation: 0 }});
      pop("#{p}t1", {ch(sid, m["t_ps"]):.2f}); count("#{p}ps", {m["ps"]}, {ch(sid, m["t_ps"]):.2f}, 0.7);
      pop("#{p}t2", {ch(sid, m["t_acc"]):.2f}); count("#{p}acc", {m["acc"]}, {ch(sid, m["t_acc"]):.2f}, 0.6, 1);
      pop("#{p}t3", {ch(sid, m["t_x"]):.2f});
      rise("#{p}spec", {spec_at:.2f}, 0.35);''')
    if m.get("crown"):
        js.append(f'''      tl.fromTo("#{p}crown", {{ y: -300, rotation: -30, opacity: 0 }}, {{ y: 0, rotation: 12, opacity: 1, duration: 0.5, ease: "bounce.out" }}, {s0 + 0.6:.2f});
      twinkle("#{p}sp0", {s0 + 0.8:.2f}); twinkle("#{p}sp1", {s0 + 1.1:.2f}); twinkle("#{p}sp2", {ch(sid, 4):.2f});''')
        S(s0 - 1.0, "riser", 0.3); S(s0 + 0.6, "ding", 0.35); S(ch(sid, 4), "shimmer", 0.3)
    if m.get("rain"):
        js.append(f'''      qa(".{p}drop").forEach((el, i) => tl.fromTo(el, {{ y: -260, opacity: 0 }}, {{ y: 60, opacity: 1, duration: 0.9, ease: "power1.in", repeat: 2 }}, {ch(sid, 3) - 0.2:.2f} + i * 0.13));''')
    js.append(f'      polOut("#{p}pol", {s1 - 0.3:.2f}, {1 if k % 2 == 0 else -1}); out(["#{p}stk", "#{p}t1", "#{p}t2", "#{p}t3", "#{p}spec"{", " + chr(34) + "#" + p + "crown" + chr(34) if m.get("crown") else ""}], {s1 - 0.3:.2f}, 0.2);')
    S(s0 + 0.02, "whoosh", 0.2); S(s0 + 0.47, "shutter", 0.55); S(s0 + 0.5, "thud", 0.3)
    for j in (1, 2):
        S(s0 + 0.52 + j * 0.1 - 0.1, "tick", 0.35)
    S(sat, "pop", 0.4)
    for key in ("t_ps", "t_acc", "t_x"):
        S(ch(sid, m[key]), "pop", 0.32)
    S(ch(sid, m["t_ps"]) + 0.05, "tick", 0.3)

# ================= BODY (Cabriolet / Targa) =================
b0, b1 = SC["body"]["s"], SC["outro"]["s"]
body.append(f'''      <!-- BODY -->
      <div id="bodyS" class="clip layer" data-start="{b0:.2f}" data-duration="{b1 - b0:.2f}" data-track-index="3" style="z-index:10">
        <div id="bdQ" class="row big" style="top:170px;font-size:120px"><span class="skew">BUKA <span style="color:var(--yellow)">BUMBUNG?</span></span></div>
        {polaroid("bdP1", "cabrio", "Cabriolet", 40, 360, 500, "p")}
        {polaroid("bdP2", "targa", "Targa", 540, 420, 500, "r")}
        <div class="row" style="top:930px"><span id="bdC" class="sticker m" style="font-size:46px;transform:rotate(-2deg)">TARGA = 4S &amp; 4 GTS SAHAJA</span></div>
      </div>''')
js.append(f'''      // BODY
      rise("#bdQ", {b0 + 0.05:.2f}, 0.35);
      polIn("#bdP1", {ch("body", 1) - 0.2:.2f}, -5, -1);
      polIn("#bdP2", {ch("body", 2) - 0.2:.2f}, 5, 1);
      pop("#bdC", {ch("body", 3) + 0.4:.2f}, {{ rotation: -2 }});
      out(["#bdQ", "#bdC"], {b1 - 0.25:.2f}); polOut("#bdP1", {b1 - 0.3:.2f}, -1); polOut("#bdP2", {b1 - 0.3:.2f}, 1);''')
S(b0 + 0.05, "whoosh", 0.2)
for t in (ch("body", 1) - 0.2, ch("body", 2) - 0.2):
    S(t, "whoosh", 0.15); S(t + 0.45, "shutter", 0.5); S(t + 0.5, "thud", 0.25)
S(ch("body", 3) + 0.4, "pop", 0.4)

# ================= OUTRO =================
o0 = SC["outro"]["s"]
grid = [("carrera", "Carrera", 50, 330, -5), ("carrera_t", "Carrera T", 395, 300, 3), ("carrera_s", "Carrera S", 740, 330, -2),
        ("carrera_4s", "Carrera 4S", 200, 640, 4), ("gts", "GTS", 570, 630, -4)]
mini = "\n        ".join(polaroid(f"ouP{j}", img, cap, x, y, 300, ["", "p", "r"][j % 3], fs=34, tapes="top", cred=False)
                       for j, (img, cap, x, y, r) in enumerate(grid))
body.append(f'''      <!-- OUTRO -->
      <div id="outro" class="clip layer" data-start="{o0:.2f}" data-duration="{DUR - o0:.2f}" data-track-index="3" style="z-index:10">
        <div id="ouQ" class="row big" style="top:160px;font-size:112px"><span class="skew">KORANG PILIH <span style="color:var(--yellow)">MANA?</span></span></div>
        {mini}
        <div class="row" style="top:890px"><span id="ouC" class="sticker" style="font-size:52px;transform:rotate(-3deg)">KOMEN KAT BAWAH ⬇</span></div>
        <div id="ouF" class="row" style="top:1010px;font-family:var(--font-mono);font-weight:700;font-size:30px;letter-spacing:0.3em;color:var(--cream)">FOLLOW</div>
        <div id="ouE" class="row big y" style="top:1048px;font-size:92px"><span class="skew">ECW MOTORSPORTS</span></div>
        <div id="ouCr" class="row" style="top:1868px;font-family:var(--font-ui);font-weight:500;font-size:17px;color:rgba(255,239,239,0.6)" data-layout-ignore>Foto: Wikimedia Commons — Mathious Ier, TTTNIS, Charles from Port Chester NY (CC0) · Calreyn88, Ethan Llamas (CC BY-SA 4.0)</div>
      </div>''')
js.append("      // OUTRO\n      rise(\"#ouQ\", %.2f, 0.35);" % (o0 + 0.02))
for j, (img, cap, x, y, r) in enumerate(grid):
    js.append(f'      polIn("#ouP{j}", {o0 + 0.1 + j * 0.12:.2f}, {r}, {-1 if j % 2 == 0 else 1});')
    S(o0 + 0.55 + j * 0.12, "shutter", 0.25)
js.append(f'''      pop("#ouC", {ch("outro", 1):.2f}, {{ rotation: -3 }});
      tl.to("#ouC", {{ y: 12, duration: 0.3, yoyo: true, repeat: 3, ease: "sine.inOut" }}, {ch("outro", 1) + 0.4:.2f});
      rise("#ouF", {ch("outro", 2) + 0.2:.2f}, 0.3); slam("#ouE", {ch("outro", 2) + 0.6:.2f});''')
S(o0, "whoosh", 0.2); S(ch("outro", 1), "pop", 0.4); S(ch("outro", 2) + 0.6, "impact", 0.4); S(ch("outro", 2) + 0.65, "shimmer", 0.3)

# ================= HOST =================
host_imgs = "\n".join(f'          <img id="h_{e}" src="assets/host/{e}.png" alt="">' for e in EXPRS)
changes = []  # (time, expr)
for s in T["scenes"]:
    changes.append((0 if s["id"] == "hook" else s["s"], s["expr"]))
    over = next((m["expr"] for m in MODELS if m["id"] == s["id"]), {})
    over = {**over, **{"hook": {3: "excited"}, "intro": {3: "thinking"}, "outro": {2: "wink"}}.get(s["id"], {})}
    for ci, e in over.items():
        changes.append((s["chunks"][ci]["s"], e))
changes.append((VOICE_END + 0.2, "love"))
changes.sort()
hj = []
prev = None
for t, e in changes:
    if prev:
        hj.append(f'      tl.set("#h_{prev}", {{ opacity: 0 }}, {t:.2f});')
    hj.append(f'      tl.set("#h_{e}", {{ opacity: 1 }}, {t:.2f});')
    if t > 0:
        hj.append(f'      tl.fromTo("#hostBob", {{ scaleX: 1.12, scaleY: 0.86 }}, {{ scaleX: 1, scaleY: 1, duration: 0.35, ease: "elastic.out(1.2,0.45)" }}, {t:.2f});')
        S(t, "pop", 0.25)
    prev = e
js.append("      // HOST expressions\n" + "\n".join(hj))
# talking bounce from voice envelope (10 fps)
js.append(f'''      const ENV = {json.dumps(ENV)};
      ENV.forEach((e, i) => {{ if (i * 0.1 < {VOICE_END:.2f}) tl.to("#host", {{ y: -18 * e, rotation: (i % 2 ? 1 : -1) * 1.6 * e, duration: 0.1, ease: "sine.inOut" }}, i * 0.1); }});
      tl.to("#host", {{ y: 0, rotation: 0, duration: 0.3 }}, {VOICE_END:.2f});
      tl.fromTo("#host", {{ scale: 1 }}, {{ scale: 1.05, duration: 0.5, yoyo: true, repeat: 2, ease: "sine.inOut", transformOrigin: "50% 100%" }}, {VOICE_END + 0.2:.2f});''')

# ================= CAPTIONS in speech bubble =================
KEYS = re.compile(r"^(porsche|911|carrera|t|s|4s|gts|t-hybrid|394|480|541|0-100|4\.1|3\.3|3\.0|3\.6|3|100|6|4|manual|ganas|raja|cabriolet|targa|ecw|motorsports|boxer|turbo|twin-turbo|elektrik|hujan|power|gearbox|pacuan)[,.?!:]*$", re.I)
cap_html = []
allc = [(c, s["id"]) for s in T["scenes"] for c in s["chunks"]]
for gi, (c, sid) in enumerate(allc):
    nxt = allc[gi + 1][0]["s"] if gi + 1 < len(allc) else VOICE_END + 0.6
    st, en = c["s"], min(nxt, c["e"] + 0.9)
    words = c["text"].split()
    total = sum(len(w) for w in words)
    spans = []
    acc = 0
    for wi, w in enumerate(words):
        wt = st + (c["e"] - st) * acc / max(total, 1)
        acc += len(w)
        cls = ' class="k"' if KEYS.match(w) else ""
        spans.append(f'<span id="cw{gi}_{wi}"{cls}>{w}</span>')
        js.append(f'      tl.fromTo("#cw{gi}_{wi}", {{ scale: 0.5, opacity: 0 }}, {{ scale: 1, opacity: 1, duration: 0.14, ease: "back.out(3)" }}, {wt:.2f});')
    size = " s" if len(c["text"]) > 28 else (" m" if len(c["text"]) > 18 else "")
    cap_html.append(f'      <div id="cap{gi}" class="clip cap{size}" data-start="{st:.2f}" data-duration="{en - st:.2f}" data-track-index="8" style="z-index:43">{"".join(spans)}</div>')
js.append(f'      pop("#bubble", 0.3, {{ duration: 0.3 }});')
js.append(f'      tl.to("#bubble", {{ scale: 0, opacity: 0, duration: 0.25, ease: "back.in(2)" }}, {VOICE_END - 0.25:.2f});')

# ================= SFX lanes =================
SFX_LEN = {"whoosh": 0.55, "pop": 0.12, "ding": 1.2, "thud": 0.45, "impact": 2.2, "shimmer": 1.6, "glitch": 0.25,
           "tick": 0.04, "riser": 1.0, "shutter": 0.32}
lanes, rows = [], []
for i, (t, n, v) in enumerate(sorted(sfx)):
    t = max(t, 0)
    d = min(SFX_LEN[n], DUR - t)
    lane = next((k for k, e in enumerate(lanes) if e <= t), None)
    if lane is None:
        lanes.append(0); lane = len(lanes) - 1
    lanes[lane] = t + d
    rows.append(f'      <audio id="sfx{i}" src="assets/sfx/{n}.wav" data-start="{t:.2f}" data-duration="{d:.2f}" data-track-index="{21 + lane}" data-volume="{v}"></audio>')

s = (ROOT / "src/template.html").read_text()
for k, v in {"__BODY__": "\n".join(body), "__JS__": "\n".join(js), "__HOSTIMGS__": host_imgs, "__CAPTIONS__": "\n".join(cap_html),
             "__SFX__": "\n".join(rows), "__VOICEEND__": f"{VOICE_END:.2f}", "__VOICEDUR__": f"{VOICE_END + 0.3:.2f}",
             "__DUR__": f"{DUR}"}.items():
    s = s.replace(k, v)
(ROOT / "index.html").write_text(s)
print(f"index.html written, duration {DUR}s, {len(rows)} sfx")
