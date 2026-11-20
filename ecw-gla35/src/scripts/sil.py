import numpy as np, wave, sys
w=wave.open(sys.argv[1]); sr=w.getframerate(); x=np.frombuffer(w.readframes(w.getnframes()),np.int16)/32768.0
hop=int(sr*0.02); n=len(x)//hop
rms=np.array([np.sqrt(np.mean(x[i*hop:(i+1)*hop]**2))+1e-9 for i in range(n)]); db=20*np.log10(rms)
print("peak db",db.max(),"median",np.median(db))
sil=db< -36
runs=[];i=0
while i<n:
    if sil[i]:
        j=i
        while j<n and sil[j]: j+=1
        if (j-i)*0.02>=0.32: runs.append((i*0.02,j*0.02))
        i=j
    else: i+=1
for a,b in runs: print(f"{a:6.2f}-{b:6.2f} ({b-a:.2f})")
