"""Map source word times through the cut list -> transcript_edit.json (edit timeline).

Usage: python3 omap.py <edl.json> <tx_source.json> <out.json>
"""
import json, sys

edl = json.load(open(sys.argv[1]))['segs']
tx = json.load(open(sys.argv[2]))
FIX = {"driver": "Gravel", "-wheel": "wheel", "Motorsport,": "Motorsports,", "1,": "1,"}


def omap(t):
    for s in edl:
        if s['src'] - 1e-3 <= t <= s['end'] + 1e-3:
            return s['out'] + (min(t, s['end']) - s['src'])
    return None


out = []
for seg in tx:
    words = []
    for w in seg['words']:
        mid = (w['s'] + w['e']) / 2
        if omap(mid) is None:
            continue  # word was cut
        s = omap(w['s']); e = omap(w['e'])
        if s is None: s = omap(mid) - 0.05
        if e is None: e = omap(mid) + 0.05
        txt = w['w'].strip()
        txt = FIX.get(txt, txt)
        if txt == 'wheel' and words and words[-1]['w'] == 'four':
            words[-1]['w'] = 'four-wheel'; words[-1]['e'] = round(e, 3); continue
        words.append({"w": txt, "s": round(s, 3), "e": round(e, 3)})
    if words:
        out.append({"start": words[0]['s'], "end": words[-1]['e'], "text": " ".join(w['w'] for w in words), "words": words})
json.dump(out, open(sys.argv[3], 'w'), ensure_ascii=False, indent=1)
for s in out:
    print(f"[{s['start']:6.2f}] " + " ".join(f"{w['w']}@{w['s']:.2f}" for w in s['words']))
