# ECW — "BMW M Decoded" (Hyperframes)

Explainer TikTok (Bahasa Melayu) for ECW Motorsport: every BMW M badge explained in ~97 s, narrated by Kemal (KEMALKIMUN x ECW sticker pack).
Original script and graphics; voiceover is Edge TTS `ms-MY-OsmanNeural`.
Theme: maroon `#430107`, cream `#FFEFEF`, yellow `#FECD00`, hologram neon + perspective grid.

## Layout
- `index.html` — generated composition (do not hand-edit; edit `src/template.html` + `src/build.py`).
- `src/template.html` — 26 scenes (one per voice line), GSAP timeline keyed to word timings.
- `src/cars.py` — parametric neon car side-profiles (coupe, sedan, coupe4, conv, big, suv, xm, hatch).
- `src/build.py` — fills scene timing, cars, captions, chapter HUD, transitions and SFX from `src/words_edit.json`.
- `src/scripts/script_bm.json` — the Malay script (`show` = on-screen text, `say` = pronunciation for TTS).
- `src/scripts/tts.py` — Edge TTS per line with word boundaries (needs host `speech.platform.bing.com`).
- `src/scripts/voice.py` — trims pauses, joins lines into `assets/audio/voice.wav`, writes `src/words_edit.json`.
- `src/scripts/audio.py` — synth SFX + 104 BPM music ducked under the voice.

## Commands
```bash
python3 -I src/scripts/tts.py src/scripts/script_bm.json <tmpdir>   # regenerate voice lines
python3 src/scripts/voice.py <tmpdir> .                              # voice.wav + words_edit.json
python3 src/scripts/audio.py . <dur>                                 # sfx + music_ducked.wav
python3 src/build.py                                                 # index.html
npx hyperframes lint
npx hyperframes snapshot --at 0,5,10
npx hyperframes render -q draft -o renders/preview.mp4
```
- `assets/kemal/` — Kemal faces cut from the sticker pack (`src/scripts/kemal_cut.py`); `src/build.py` swaps faces per line (`face` in the script) and bounces him on each voice syllable.
