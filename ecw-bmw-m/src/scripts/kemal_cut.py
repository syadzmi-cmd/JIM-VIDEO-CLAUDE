"""Cut the KEMALKIMUN x ECW sticker pack into transparent PNGs (labels removed)."""
import sys, numpy as np
from PIL import Image, ImageFilter
from scipy import ndimage
src, out = sys.argv[1], sys.argv[2]
im = np.array(Image.open(src).convert("RGB")).astype(int)
BG = im[5, 5]
NAMES = [["hai", "hahaha", "alamak"], ["hmmm", "geram", "sedih"], ["mantap", "suka", "sebab"]]
XS = [(95, 560), (655, 1125), (1215, 1680)]
ROWS = [(150, 628), (754, 1232), (1358, 1838)]   # bottom = just above the text label
for r, (y0, y1) in enumerate(ROWS):
    for c, (x0, x1) in enumerate(XS):
        a = im[y0:y1, x0:x1]
        bg = np.abs(a - BG).sum(2) < 42
        lab, n = ndimage.label(bg)
        edge = set(np.unique(np.concatenate([lab[0], lab[:, 0], lab[:, -1]]))) - {0}
        bgm = np.isin(lab, list(edge))
        alpha = (~bgm).astype(np.uint8) * 255
        A = Image.fromarray(alpha).filter(ImageFilter.MinFilter(3)).filter(ImageFilter.GaussianBlur(0.8))
        rgba = Image.fromarray(a.astype(np.uint8)).convert("RGBA"); rgba.putalpha(A)
        bb = rgba.getbbox(); rgba = rgba.crop(bb)
        rgba.save(f"{out}/{NAMES[r][c]}.png")
        print(NAMES[r][c], rgba.size)
