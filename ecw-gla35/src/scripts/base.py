import json,sys,subprocess
from concurrent.futures import ThreadPoolExecutor
S=sys.argv[1]; e=json.load(open(f'{S}/work/edl.json'))
SRC=f'{S}/drive/TALKING HEAD.mp4'
def job(i):
    s=e['segs'][i]
    z=1.0 if i%2==0 else (1.32 if i%6==3 else 1.18)
    s['zoom']=z
    fx,fy=s['fx']*2,s['fy']*2
    cw,ch=round(2160/z/2)*2,round(3840/z/2)*2
    x0=min(max(0,round(fx*(1-1/z))),2160-cw); y0=min(max(0,round(fy*(1-1/z))),3840-ch)
    n=round((s['end']-s['src'])*30)
    subprocess.run(['ffmpeg','-v','error','-y','-ss',f"{s['src']:.4f}",'-i',SRC,'-frames:v',str(n),'-an',
      '-vf',f'crop={cw}:{ch}:{x0}:{y0},scale=1080:1920:flags=lanczos,fps=30,format=yuv420p',
      '-c:v','libx264','-preset','fast','-crf','16','-r','30',f'{S}/segs/s{i:02d}.mp4'],check=True)
    return i
with ThreadPoolExecutor(3) as ex: list(ex.map(job,range(len(e['segs']))))
for i,s in enumerate(e['segs']): s['zoom']=1.0 if i%2==0 else (1.32 if i%6==3 else 1.18)
json.dump(e,open(f'{S}/work/edl.json','w'),indent=1)
open(f'{S}/segs/list.txt','w').write(''.join(f"file 's{i:02d}.mp4'\n" for i in range(len(e['segs']))))
subprocess.run(['ffmpeg','-v','error','-y','-f','concat','-safe','0','-i',f'{S}/segs/list.txt','-i',f'{S}/work/cut.wav',
  '-c:v','copy','-c:a','aac','-b:a','256k','-shortest',f'{S}/work/base.mp4'],check=True)
