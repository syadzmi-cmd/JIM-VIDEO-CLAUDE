# ECW — GLA35 "Racun Raya" (Hyperframes)

Talking-head edit for ECW Motorsports, built with [Hyperframes](https://hyperframes.heygen.com).
Theme: maroon `#430107`, cream `#FFEFEF`, yellow `#FECD00`.

## Layout
- `index.html` — generated composition (do not hand-edit; edit `src/template.html` + `src/build.py`).
- `src/template.html` — scenes, motion graphics, car line-art, GSAP timeline.
- `src/build.py` — injects b-roll, SFX, and word-by-word captions from `src/transcript_edit.json`.
- `src/edl.json` — cut list (source → edit times, punch-in zoom per segment).
- `src/scripts/` — pipeline: `tx.py` (Whisper), `edl.py` (silence/repeat cuts), `base.py` (4K punch-in base), `audio.py` (music + SFX synth).
- `assets/video/base.mp4` — cut talking head (57 s + 1.5 s end-card tail), voice included.

## Commands
```bash
python3 src/build.py src/transcript_edit.json   # rebuild index.html
npx hyperframes lint
npx hyperframes snapshot --at 0,5,10
npx hyperframes render -q draft -o preview.mp4   # preview
```
