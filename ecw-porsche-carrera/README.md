# ECW — Porsche 911 Carrera line-up (Hyperframes)

Explainer TikTok (9:16, ~71 s) where the ECW chibi virtual host walks through the 992.2 Carrera line-up:
Carrera, Carrera T, Carrera S, Carrera 4S, Carrera GTS T-Hybrid, plus Cabriolet/Targa.
Theme: maroon `#430107`, cream `#FFEFEF`, yellow `#FECD00`. Internet photos are shown as taped polaroids.

## Pipeline
```bash
python3 src/scripts/cut_host.py assets/host/sheet.webp assets/host   # 9 expressions -> transparent PNGs
python3 src/scripts/tts.py          # src/script.json -> assets/audio/voice.wav + src/timing.json (edge-tts ms-MY-OsmanNeural)
python3 src/scripts/music.py 71.3   # music bed (ducked), shutter SFX, src/voice_env.json (host talk bounce)
python3 src/build.py                # src/template.html + timing -> index.html
npm run check
npx hyperframes render -q draft -o renders/preview.mp4
```
- `src/script.json` — each chunk is `[tts_text, caption_text]` (TTS text is spelled phonetically, e.g. "Karera", "tiga ratus...").
- `src/build.py` — model data (specs, sticker, tile timing), scenes, SFX list, captions in the speech bubble.
- Edit `src/template.html` / `src/build.py`, never `index.html`.

## Specs used (Porsche newsroom / configurator, 992.2)
| Model | PS | 0-100 | Notes |
|---|---|---|---|
| Carrera | 394 | 4.1 s | 3.0L twin-turbo, PDK 8, RWD |
| Carrera T | 394 | 4.5 s | 6-speed manual, lighter, rear-axle steering |
| Carrera S | 480 | 3.3 s* | top speed 308 km/h |
| Carrera 4S | 480 | 3.3 s* | AWD |
| Carrera GTS T-Hybrid | 541 | 3.0 s | 3.6L + eTurbo + e-motor, 610 Nm |
\* with Sport Chrono.

## Photo credits
See `assets/img/CREDITS.json` (Wikimedia Commons, CC0 and CC BY-SA 4.0). Credits are shown on each polaroid and on the end card.
Note: the Carrera, Carrera T and Carrera 4S photos are 992.1-era cars (visually near-identical); Carrera S, GTS, Cabriolet and Targa are 992.2.
