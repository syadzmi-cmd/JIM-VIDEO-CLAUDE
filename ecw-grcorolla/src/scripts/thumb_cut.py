"""Thumbnail person cutout: grab a source frame, punch in on the face, GrabCut the person.

Usage: python3 thumb_cut.py <source.mp4> <time> <outdir>
Writes <outdir>/frame.png (1080x1920 background) and <outdir>/person.png (RGBA cutout).
"""
import subprocess, sys
import cv2, numpy as np

SRC, T, OUT = sys.argv[1], sys.argv[2], sys.argv[3]
subprocess.run(['ffmpeg', '-nostdin', '-v', 'error', '-y', '-ss', T, '-i', SRC, '-frames:v', '1', f'{OUT}/src.png'], check=True)
im = cv2.imread(f'{OUT}/src.png'); H, W = im.shape[:2]
g = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
c = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
f = c.detectMultiScale(cv2.resize(g, (W // 2, H // 2)), 1.1, 6, minSize=(40, 40))
x, y, w, h = [v * 2 for v in max(f, key=lambda r: r[2] * r[3])]
z = 1.12 * 1080 / W                      # light punch-in
cx, cy = x + w / 2, y + h / 2
FACE_Y = 800                             # face centre after shifting the person down
M = np.float32([[z, 0, 540 - cx * z], [0, z, FACE_Y - cy * z]])
out = cv2.warpAffine(im, M, (1080, 1920), flags=cv2.INTER_LANCZOS4, borderMode=cv2.BORDER_REPLICATE)
cv2.imwrite(f'{OUT}/frame.png', out)
fx, fy, fw, fh = 540 - w * z / 2, FACE_Y - h * z / 2, w * z, h * z
mask = np.full((1920, 1080), cv2.GC_PR_BGD, np.uint8)
mask[:int(fy - fh * 0.9), :] = cv2.GC_BGD                                                   # top band = background
mask[int(fy - fh * 0.6):, int(fx - fw * 1.9):int(fx + fw * 2.9)] = cv2.GC_PR_FGD
mask[int(fy + fh * 0.1):int(fy + fh * 0.9), int(fx + fw * 0.2):int(fx + fw * 0.8)] = cv2.GC_FGD  # face
mask[int(fy + fh * 1.3):int(fy + fh * 3.2), int(fx - fw * 0.4):int(fx + fw * 1.4)] = cv2.GC_FGD  # shirt
# hair: dark hair on a dark background gets dropped by GrabCut, so seed it explicitly
hx, hy = int(fx + fw / 2), int(fy + fh * 0.12)
cv2.ellipse(mask, (hx, hy), (int(fw * 0.53), int(fh * 0.42)), 0, 0, 360, cv2.GC_PR_FGD, -1)
cv2.ellipse(mask, (hx, hy), (int(fw * 0.44), int(fh * 0.33)), 0, 0, 360, cv2.GC_FGD, -1)
bg = np.zeros((1, 65), np.float64); fg = np.zeros((1, 65), np.float64)
small = cv2.resize(out, (540, 960)); ms = cv2.resize(mask, (540, 960), interpolation=cv2.INTER_NEAREST)
cv2.grabCut(small, ms, None, bg, fg, 6, cv2.GC_INIT_WITH_MASK)
m = np.where((ms == 1) | (ms == 3), 255, 0).astype(np.uint8)
m = cv2.GaussianBlur(cv2.resize(m, (1080, 1920), interpolation=cv2.INTER_LINEAR), (5, 5), 0)
n, lab, st, _ = cv2.connectedComponentsWithStats((m > 127).astype(np.uint8))
k = 1 + np.argmax(st[1:, cv2.CC_STAT_AREA]); m[lab != k] = 0
rgba = cv2.cvtColor(out, cv2.COLOR_BGR2BGRA); rgba[:, :, 3] = m
cv2.imwrite(f'{OUT}/person.png', rgba)
prev = out.copy(); prev[m < 128] = (prev[m < 128] * 0.25).astype(np.uint8)
cv2.imwrite(f'{OUT}/mask_prev.jpg', cv2.resize(prev, (540, 960)))
print('face box out', round(fx), round(fy), round(fw), round(fh))
