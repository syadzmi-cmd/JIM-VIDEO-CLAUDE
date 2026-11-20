"""Parametric neon car side-profiles (inline SVG) in the ECW hologram style.

car_svg(kind, id, ...) -> inline <svg> with stroke paths classed `draw` so the
GSAP timeline can stroke-draw them. Car faces left. viewBox 0 0 680 260.
"""
import math

GROUND = 236

# fractions are of body length L, measured from the nose
KINDS = {
    #            L    r   wf    wr   sill nose hood  wsb   r0    r1    deck  tail  roof deckY doors fast  conv  hatch
    "coupe":   (470, 41, .18, .79, 200, 172, 146, .36, .50, .64, .84, .99, 82, 128, 2, True, False, False),
    "sedan":   (560, 42, .17, .77, 200, 172, 146, .33, .46, .66, .86, .99, 76, 124, 4, False, False, False),
    "coupe4":  (560, 42, .17, .77, 200, 172, 146, .33, .47, .64, .87, .99, 82, 126, 2, True, False, False),
    "conv":    (560, 42, .17, .77, 200, 172, 146, .33, .47, .64, .87, .99, 82, 126, 2, True, True, False),
    "big":     (620, 44, .16, .77, 200, 170, 144, .32, .45, .68, .87, .99, 72, 122, 4, False, False, False),
    "suv":     (600, 50, .17, .79, 190, 150, 120, .30, .41, .86, .97, .995, 42, 100, 4, False, False, True),
    "xm":      (610, 56, .17, .79, 178, 132, 102, .29, .41, .70, .93, .995, 22, 90, 4, True, False, False),
    "wagon":   (580, 42, .17, .77, 200, 172, 146, .32, .45, .88, .975, .995, 74, 112, 4, False, False, True),
    "hatch":   (480, 40, .18, .81, 200, 168, 142, .34, .46, .80, .95, .995, 72, 116, 4, False, False, True),
}


def f(v):
    return f"{v:.1f}"


def body_path(k):
    L, r, wf, wr, sill, nose, hood, wsb, r0, r1, deck, tail, roofY, deckY, doors, fast, conv, hatch = KINDS[k]
    x0 = (680 - L) / 2
    X = lambda p: x0 + p * L
    cy = GROUND - r
    R = r + 11
    fx, rx = X(wf), X(wr)
    dy = sill - cy
    dx = math.sqrt(max(R * R - dy * dy, 1))
    roof_top = roofY if not conv else hood - 6
    p = []
    p.append(f"M{f(X(0.03))} {f(sill)}")
    p.append(f"Q{f(X(0.0))} {f(sill)} {f(X(0.0))} {f(nose + 12)}")           # chin
    p.append(f"L{f(X(0.004))} {f(nose)}")
    p.append(f"Q{f(X(0.02))} {f(hood - 2)} {f(X(0.10))} {f(hood)}")         # nose to hood
    p.append(f"L{f(X(wsb))} {f(hood - 10)}")                                 # hood
    if conv:
        p.append(f"L{f(X(wsb + 0.07))} {f(hood - 46)}")                      # windshield frame
        p.append(f"L{f(X(wsb + 0.085))} {f(hood - 44)}")
        p.append(f"L{f(X(wsb + 0.04))} {f(hood - 8)}")
        p.append(f"L{f(X(deck - 0.07))} {f(deckY - 4)}")                      # open cabin rim
        p.append(f"Q{f(X(deck - 0.02))} {f(deckY - 22)} {f(X(deck + 0.02))} {f(deckY - 4)}")  # folded top
    else:
        p.append(f"Q{f(X(r0 - 0.03))} {f(roof_top + 4)} {f(X(r0))} {f(roof_top)}")  # windshield
        p.append(f"Q{f(X((r0 + r1) / 2))} {f(roof_top - 6)} {f(X(r1))} {f(roof_top + 2)}")  # roof
        if hatch:
            p.append(f"Q{f(X(deck))} {f(roof_top + 6)} {f(X(deck + 0.02))} {f(deckY)}")
        elif fast:
            p.append(f"Q{f(X(r1 + (deck - r1) * 0.45))} {f(roof_top + 12)} {f(X(deck))} {f(deckY)}")
        else:
            p.append(f"Q{f(X(r1 + 0.05))} {f(roof_top + 10)} {f(X(deck - 0.02))} {f(deckY)}")
    p.append(f"L{f(X(tail - 0.03))} {f(deckY + 2)}")
    p.append(f"Q{f(X(tail))} {f(deckY + 4)} {f(X(tail))} {f(deckY + 22)}")   # tail
    p.append(f"L{f(X(tail - 0.004))} {f(sill - 6)}")
    p.append(f"Q{f(X(tail - 0.01))} {f(sill)} {f(X(tail - 0.04))} {f(sill)}")
    p.append(f"L{f(rx + dx)} {f(sill)}")
    p.append(f"A{R} {R} 0 0 0 {f(rx - dx)} {f(sill)}")                        # rear arch
    p.append(f"L{f(fx + dx)} {f(sill)}")
    p.append(f"A{R} {R} 0 0 0 {f(fx - dx)} {f(sill)}")                        # front arch
    p.append("Z")
    return " ".join(p), dict(x0=x0, X=X, r=r, cy=cy, fx=fx, rx=rx, L=L, sill=sill, hood=hood, roofY=roof_top,
                             deckY=deckY, doors=doors, conv=conv, wsb=wsb, r0=r0, r1=r1, deck=deck, fast=fast, hatch=hatch, tail=tail)


def glass_path(g):
    if g["conv"]:
        return ""
    X = g["X"]
    belt = g["hood"] - 12
    top = g["roofY"] + 9
    a = X(g["wsb"] + 0.035)
    b = X(g["r0"] + 0.01)
    c = X(g["r1"] - 0.005)
    if g["hatch"]:
        d = X(g["deck"] - 0.005)
    elif g["fast"]:
        d = X(g["deck"] - 0.07)
    else:
        d = X(g["deck"] - 0.075)
    p = f"M{f(a)} {f(belt)} Q{f(b - 6)} {f(top + 4)} {f(b + 4)} {f(top)} L{f(c)} {f(top + 1)} Q{f(c + 22)} {f(top + 6)} {f(d)} {f(belt)} Z"
    # pillars
    if g["doors"] == 4:
        bp = X((g["r0"] + g["r1"]) / 2 + 0.02)
        p += f" M{f(bp)} {f(top)} L{f(bp - 4)} {f(belt)}"
    else:
        bp = X(g["r1"] - 0.02)
        p += f" M{f(bp)} {f(top + 1)} L{f(bp + 6)} {f(belt)}"
    return p


def details_path(g):
    X, sill, belt = g["X"], g["sill"], g["hood"] - 12
    p = []
    # door shut lines
    if g["doors"] == 4:
        d1, d2, d3 = X(g["wsb"] + 0.03), X((g["r0"] + g["r1"]) / 2 + 0.02), X(g["r1"] + 0.04)
        p += [f"M{f(d1)} {f(belt + 4)} L{f(d1 + 6)} {f(sill - 8)}", f"M{f(d2 - 4)} {f(belt + 4)} L{f(d2 - 2)} {f(sill - 8)}",
              f"M{f(d3)} {f(belt + 4)} Q{f(d3 + 14)} {f(sill - 30)} {f(d3 - 4)} {f(sill - 8)}"]
    else:
        d1, d3 = X(g["wsb"] + 0.03), X(g["r1"] - 0.0)
        p += [f"M{f(d1)} {f(belt + 4)} L{f(d1 + 6)} {f(sill - 8)}", f"M{f(d3)} {f(belt + 4)} Q{f(d3 + 12)} {f(sill - 30)} {f(d3 - 4)} {f(sill - 8)}"]
    p.append(f"M{f(g['fx'] + 60)} {f(sill - 10)} L{f(g['rx'] - 60)} {f(sill - 12)}")
    p.append(f"M{f(X(0.015))} {f(sill - 16)} L{f(X(0.08))} {f(sill - 14)}")
    # shoulder line
    p.append(f"M{f(X(0.06))} {f(belt + 18)} L{f(X(g['tail'] - 0.05))} {f(belt + 10)}")
    return " ".join(p)


def wheel(cx, cy, r, i):
    spokes = []
    for k in range(5):
        a = math.radians(-90 + k * 72)
        spokes.append(f"M{f(cx + math.cos(a) * r * 0.18)} {f(cy + math.sin(a) * r * 0.18)} L{f(cx + math.cos(a) * r * 0.6)} {f(cy + math.sin(a) * r * 0.6)}")
    return (f'<g class="whl" data-cx="{f(cx)}" data-cy="{f(cy)}">'
            f'<circle class="draw tyre" cx="{f(cx)}" cy="{f(cy)}" r="{r - 3}"/>'
            f'<circle class="draw rim" cx="{f(cx)}" cy="{f(cy)}" r="{f(r * 0.66)}"/>'
            f'<path class="spk" d="{" ".join(spokes)}"/>'
            f'<path class="cal" d="M{f(cx - r * 0.5)} {f(cy - r * 0.32)} A{f(r * 0.6)} {f(r * 0.6)} 0 0 1 {f(cx - r * 0.12)} {f(cy - r * 0.58)}"/></g>')


def car_svg(kind, cid, cls="", style=""):
    body, g = body_path(kind)
    X = g["X"]
    head = f"M{f(X(0.012))} {f(g['hood'] + 12)} L{f(X(0.07))} {f(g['hood'] + 4)} L{f(X(0.075))} {f(g['hood'] + 14)} Z"
    taill = f"M{f(X(g['tail'] - 0.004))} {f(g['deckY'] + 12)} L{f(X(g['tail'] - 0.06))} {f(g['deckY'] + 10)} L{f(X(g['tail'] - 0.06))} {f(g['deckY'] + 22)} L{f(X(g['tail'] - 0.004))} {f(g['deckY'] + 24)} Z"
    gl = glass_path(g)
    roof = ""
    if kind == "coupe4":  # removable roof for the convertible trick
        pass
    return (f'<svg id="{cid}" class="car {cls}" viewBox="0 0 680 260" style="{style}">'
            f'<ellipse class="shadow" cx="340" cy="{GROUND + 6}" rx="{g["L"] * 0.52:.0f}" ry="12"/>'
            f'<path class="fillb" d="{body}"/>'
            f'<path class="draw body" d="{body}"/>'
            + (f'<path class="glass" d="{gl}"/><path class="draw gl" d="{gl}"/>' if gl else "")
            + f'<path class="draw det" d="{details_path(g)}"/>'
            f'<path class="lamp" d="{head}"/><path class="lamp tl" d="{taill}"/>'
            + wheel(g["fx"], g["cy"], g["r"], 0) + wheel(g["rx"], g["cy"], g["r"], 1)
            + "</svg>")


CAR_CSS = """
      .car { position: absolute; overflow: visible; }
      .car .shadow { fill: rgba(0,0,0,0.45); filter: blur(6px); }
      .car .fillb { fill: rgba(67,1,7,0.78); }
      .car .glass { fill: rgba(254,239,239,0.10); }
      .car .draw { fill: none; stroke: var(--cream); stroke-width: 5; stroke-linecap: round; stroke-linejoin: round;
                   filter: drop-shadow(0 0 6px rgba(254,205,0,0.95)) drop-shadow(0 0 18px rgba(254,205,0,0.45)); }
      .car .draw.det { stroke-width: 3; stroke: rgba(255,239,239,0.7); }
      .car .draw.gl { stroke-width: 3.5; stroke: var(--yellow); }
      .car .draw.tyre { stroke-width: 7; stroke: var(--cream); }
      .car .draw.rim { stroke-width: 4; stroke: var(--yellow); }
      .car .spk { stroke: var(--yellow); stroke-width: 4; stroke-linecap: round; fill: none; }
      .car .cal { stroke: var(--yellow); stroke-width: 9; stroke-linecap: round; fill: none; opacity: 0.9; }
      .car .lamp { fill: var(--yellow); filter: drop-shadow(0 0 10px var(--yellow)); }
      .car .lamp.tl { fill: #ff3b3b; filter: drop-shadow(0 0 10px #ff3b3b); }
      .car.y .draw.body { stroke: var(--yellow); }
      .car.dim { opacity: 0.35; }
"""

if __name__ == "__main__":
    import sys
    cells = []
    for i, k in enumerate(KINDS):
        cells.append(f'<div style="position:relative;width:520px;height:220px;display:inline-block">{car_svg(k, "c" + k, style="left:0;top:0;width:520px;height:200px")}<div style="position:absolute;bottom:0;width:100%;text-align:center;color:#fff;font:700 28px monospace">{k}</div></div>')
    html = f"""<!doctype html><html><head><style>:root{{--maroon:#430107;--cream:#FFEFEF;--yellow:#FECD00}}
    body{{margin:0;background:radial-gradient(ellipse at 50% 40%,#5a0710,#14000a);width:1080px}}{CAR_CSS}</style></head><body>{''.join(cells)}</body></html>"""
    open(sys.argv[1], "w").write(html)
