"""Render the cut talking-head base (1080x1920, voice) from work/edl.json.

Usage: python3 base.py <workdir> <source.mp4> <out.mp4>
"""
import json, sys, subprocess, os
from concurrent.futures import ThreadPoolExecutor

S, SRC, OUT = sys.argv[1], sys.argv[2], sys.argv[3]
SW, SH = 1440, 2560
e = json.load(open(f'{S}/work/edl.json'))
os.makedirs(f'{S}/segs', exist_ok=True)


def job(i):
    s = e['segs'][i]; z = s['zoom']
    cw, ch = round(SW / z / 2) * 2, round(SH / z / 2) * 2
    # keep the face at the same screen position: crop around face scaled by 1/z
    x0 = min(max(0, round(s['fx'] * (1 - 1 / z))), SW - cw)
    y0 = min(max(0, round(s['fy'] * (1 - 1 / z))), SH - ch)
    n = round((s['end'] - s['src']) * 30)
    subprocess.run(['ffmpeg', '-nostdin', '-v', 'error', '-y', '-ss', f"{s['src']:.4f}", '-i', SRC, '-frames:v', str(n), '-an',
                    '-vf', f'crop={cw}:{ch}:{x0}:{y0},scale=1080:1920:flags=lanczos,fps=30,format=yuv420p',
                    '-c:v', 'libx264', '-preset', 'fast', '-crf', '16', '-r', '30', f'{S}/segs/s{i:02d}.mp4'], check=True)
    # matching audio with 6 ms edge fades (no clicks at cuts)
    d = n / 30
    subprocess.run(['ffmpeg', '-nostdin', '-v', 'error', '-y', '-ss', f"{s['src']:.4f}", '-t', f'{d:.4f}', '-i', SRC, '-vn',
                    '-af', f'afade=t=in:d=0.006,afade=t=out:st={d - 0.006:.4f}:d=0.006,aresample=48000',
                    '-ac', '2', '-ar', '48000', f'{S}/segs/a{i:02d}.wav'], check=True)
    return i


with ThreadPoolExecutor(3) as ex:
    list(ex.map(job, range(len(e['segs']))))
open(f'{S}/segs/list.txt', 'w').write(''.join(f"file 's{i:02d}.mp4'\n" for i in range(len(e['segs']))))
open(f'{S}/segs/alist.txt', 'w').write(''.join(f"file 'a{i:02d}.wav'\n" for i in range(len(e['segs']))))
subprocess.run(['ffmpeg', '-nostdin', '-v', 'error', '-y', '-f', 'concat', '-safe', '0', '-i', f'{S}/segs/alist.txt',
                '-c:a', 'pcm_s16le', f'{S}/work/cut.wav'], check=True)
subprocess.run(['ffmpeg', '-nostdin', '-v', 'error', '-y', '-f', 'concat', '-safe', '0', '-i', f'{S}/segs/list.txt', '-i', f'{S}/work/cut.wav',
                '-c:v', 'copy', '-c:a', 'aac', '-b:a', '256k', '-shortest', OUT], check=True)
print('base ok')
