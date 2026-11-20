import numpy as np, wave, json, sys
S=sys.argv[1]
w=wave.open(f'{S}/work/th.wav'); sr=w.getframerate(); x=np.frombuffer(w.readframes(w.getnframes()),np.int16)/32768.0
DUR=len(x)/sr
hop=int(sr*0.02); n=len(x)//hop
db=np.array([20*np.log10(np.sqrt(np.mean(x[i*hop:(i+1)*hop]**2))+1e-9) for i in range(n)])
sil=db<-36; runs=[]; i=0
while i<n:
    if sil[i]:
        j=i
        while j<n and sil[j]: j+=1
        if (j-i)*0.02>=0.30: runs.append((i*0.02,j*0.02))
        i=j
    else: i+=1
# removal ranges: silences shrunk by pads
rm=[]
for a,b in runs:
    a2=a+0.20 if a>0 else 0; b2=b-0.10 if b<DUR-0.05 else DUR
    if b2-a2>0.05: rm.append((a2,b2))
# manual content cuts (source seconds)
rm += [(15.44,16.86),   # "Yang pertama." stumble
       (21.36,23.92),   # "Jadi, bila kita keluar masuk kereta," repeat
       (24.32,25.29),   # held pause
       (29.56,31.70),   # repeated "Yang kedua,"
       (41.17,42.95),   # "daripada point A ke point B tu," repeat
       (36.22,37.00),   # pause in "Pak ... Itam"
       (74.30,DUR)]     # tail
rm.sort(); merged=[]
for a,b in rm:
    if merged and a<=merged[-1][1]: merged[-1]=(merged[-1][0],max(b,merged[-1][1]))
    else: merged.append((a,b))
keep=[]; t=0
for a,b in merged:
    if a>t: keep.append((t,a))
    t=max(t,b)
if t<DUR: keep.append((t,DUR))
fr=lambda v: round(v*30)/30
keep=[(fr(a),fr(b)) for a,b in keep if fr(b)-fr(a)>=2/30]
# output map
segs=[];o=0
for a,b in keep:
    segs.append({"src":a,"end":b,"out":round(o,4)}); o+=b-a
print(f"source {DUR:.2f}s -> edit {o:.2f}s, {len(segs)} segs")
for s in segs: print(f"  {s['src']:6.2f}-{s['end']:6.2f} -> {s['out']:6.2f}")
json.dump({"segs":segs,"dur":o},open(f'{S}/work/edl.json','w'),indent=1)
