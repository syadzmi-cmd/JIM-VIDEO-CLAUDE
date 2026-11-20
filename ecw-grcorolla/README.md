# ECW — GR Corolla vs GR Yaris (Hyperframes)

Talking-head edit for ECW Motorsports (presenter: Jai), built with [Hyperframes](https://hyperframes.heygen.com).
Theme: maroon `#430107`, cream `#FFEFEF`, yellow `#FECD00` (same hologram look as `ecw-gla35`).

## Edit
- Source: 65.2 s raw (already multi-angle) → 59.1 s + 1.2 s end-card tail.
- Removed: all pauses ≥ 0.3 s (keeping 0.2 s after / 0.1 s before speech), the repeated
  "Berbanding GR Yaris," right after the hook, two of the three "Sebab apa?", and a small stumble after "Tak cukup".
- Jump cuts inside one camera angle alternate 1.0 / 1.18 punch-in anchored on the face.
- Hook (frame 0): GR COROLLA vs GR YARIS photo cards + VS badge.

## Car photos
All car photos are official Toyota press images from the Toyota Global Newsroom (global.toyota):
- GR Corolla premiere album — https://global.toyota/en/newsroom/toyota/37061854.html
- GR Corolla evolved (Japan) — https://global.toyota/en/newsroom/toyota/42165939.html
- GR Corolla upgraded (AT/MT shifters, road) — https://global.toyota/en/newsroom/toyota/43287933.html
- GR Yaris premiere / launch — https://global.toyota/en/newsroom/toyota/30976389.html, https://global.toyota/en/newsroom/toyota/33517029.html

## Layout
- `index.html` — generated composition (do not hand-edit; edit `src/template.html` + `src/build.py`).
- `src/template.html` — scenes, motion graphics, GSAP timeline.
- `src/build.py` — injects photo inserts, SFX and word-by-word captions from `src/transcript_edit.json`.
- `src/edl.json` — cut list (source → edit times, face anchor, punch-in per piece).
- `src/thumb.html` — thumbnail layout (`assets/thumb/` holds the frame + person cutout).
- `src/scripts/` — `tx.py` (Whisper), `edl.py` (silence/repeat cuts), `base.py` (cut base video + voice),
  `omap.py`, `audio.py` (music + SFX synth), `thumb_cut.py` (GrabCut cutout).

## Commands
```bash
python3 src/build.py src/transcript_edit.json   # rebuild index.html
npx hyperframes lint
npx hyperframes snapshot --at 0,5,10
npx hyperframes render -q delivery -o renders/edit.mp4
```
