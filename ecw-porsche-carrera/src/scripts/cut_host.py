"""Cut the 3x3 virtual-host sticker sheet into 9 transparent PNGs."""
import sys
from pathlib import Path
import numpy as np
from PIL import Image
from scipy import ndimage

src, out = Path(sys.argv[1]), Path(sys.argv[2])
NAMES = ["shock", "laugh", "angry", "excited", "thinking", "wink", "shrug", "cry", "love"]
im = np.asarray(Image.open(src).convert("RGB")).astype(int)
bg = np.median(np.concatenate([im[:20, :20].reshape(-1, 3), im[-20:, -20:].reshape(-1, 3)]), axis=0)
dist = np.abs(im - bg).sum(-1)
fg = dist > 30
fg = ndimage.binary_closing(fg, iterations=3)
fg = ndimage.binary_fill_holes(fg)
lab, n = ndimage.label(fg)
sizes = ndimage.sum(fg, lab, range(1, n + 1))
keep = [i + 1 for i, s in enumerate(sizes) if s > 50000]
objs = ndimage.find_objects(lab)
boxes = sorted([(objs[k - 1], k) for k in keep], key=lambda b: (round(b[0][0].start / 300), b[0][1].start))
print(len(boxes), "stickers")
H, W = fg.shape
for name, (sl, k) in zip(NAMES, boxes):
    mask = (lab == k)
    # soften edge
    alpha = ndimage.gaussian_filter(mask.astype(float), 0.8)
    rgba = np.dstack([im, (alpha * 255).clip(0, 255)]).astype(np.uint8)
    y0, y1 = max(sl[0].start - 6, 0), min(sl[0].stop + 6, H)
    x0, x1 = max(sl[1].start - 6, 0), min(sl[1].stop + 6, W)
    Image.fromarray(rgba[y0:y1, x0:x1]).save(out / f"{name}.png", optimize=True)
    print(name, x1 - x0, y1 - y0)
