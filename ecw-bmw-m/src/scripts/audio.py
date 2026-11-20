import numpy as np, wave, sys
P=sys.argv[1]
SR=48000; rng=np.random.default_rng(7)
def save(path,x):
    x=np.clip(x,-1,1); y=(x*32767).astype(np.int16)
    if y.ndim==1: y=np.stack([y,y],1)
    w=wave.open(path,'wb'); w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(y.tobytes()); w.close()
def t_(d): return np.arange(int(SR*d))/SR
def env(d,a=0.005,r=None):
    t=t_(d); e=np.minimum(1,t/a); 
    if r: e*=np.exp(-t/r)
    return e
def bp_noise(d,lo,hi):
    n=rng.standard_normal(int(SR*d)); F=np.fft.rfft(n); f=np.fft.rfftfreq(len(n),1/SR)
    F[(f<lo)|(f>hi)]=0; return np.fft.irfft(F,len(n))
def norm(x,p=0.9): return x/ (np.abs(x).max()+1e-9)*p
# ---------- SFX ----------
def whoosh(d=0.55):
    t=t_(d); n=rng.standard_normal(len(t)); out=np.zeros_like(t)
    # sweeping bandpass via chunks
    F=np.fft.rfft(n); f=np.fft.rfftfreq(len(n),1/SR)
    lows=bp_noise(d,300,1500); highs=bp_noise(d,1500,7000)
    sh=np.sin(np.pi*np.clip(t/d,0,1))**2
    x=lows*sh*(1-t/d)+highs*sh*(t/d)
    return norm(x,0.9)
def pop():
    t=t_(0.12); f=900*np.exp(-t*30)+300
    return norm(np.sin(2*np.pi*np.cumsum(f)/SR)*np.exp(-t*35),0.9)
def ding():
    t=t_(1.2); x=sum(a*np.sin(2*np.pi*f*t) for f,a in [(1568,1),(2349,.5),(3136,.3),(4699,.12)])*np.exp(-t*4)*np.minimum(1,t/0.002)
    return norm(x,0.8)
def thud():
    t=t_(0.45); f=120*np.exp(-t*8)+45
    x=np.sin(2*np.pi*np.cumsum(f)/SR)*np.exp(-t*9)+0.3*bp_noise(0.45,80,600)*np.exp(-t*30)
    return norm(np.tanh(2*x),0.9)
def impact():
    t=t_(2.2); f=90*np.exp(-t*5)+38
    boom=np.sin(2*np.pi*np.cumsum(f)/SR)*np.exp(-t*2.2)
    crack=bp_noise(2.2,200,9000)*np.exp(-t*14)
    tail=bp_noise(2.2,400,3000)*np.exp(-t*2.5)*0.25
    return norm(np.tanh(1.6*(boom+0.6*crack+tail)),0.95)
def shimmer():
    t=t_(1.6); x=np.zeros_like(t)
    for k,f in enumerate([2093,2637,3136,3951,4186,5274]):
        st=k*0.07; m=t>=st; tt=t[m]-st
        x[m]+=np.sin(2*np.pi*f*tt)*np.exp(-tt*3.5)*0.5
    x+=bp_noise(1.6,5000,12000)*np.exp(-t*3)*0.15
    return norm(x,0.6)
def glitch():
    t=t_(0.25); sq=np.sign(np.sin(2*np.pi*np.where(t<0.1,180,90)*t)); n=rng.standard_normal(len(t))
    g=(np.floor(t*60)%2)
    return norm((0.5*sq+0.5*n)*g*np.exp(-t*8),0.7)
def tick():
    t=t_(0.04); return norm(bp_noise(0.04,2000,8000)*np.exp(-t*150),0.6)
def riser(d=1.0):
    t=t_(d); f=200+1800*(t/d)**2
    x=0.4*np.sin(2*np.pi*np.cumsum(f)/SR)+bp_noise(d,1000,9000)*(t/d)
    return norm(x*(t/d)**1.5,0.8)
for name,fn in [('whoosh',whoosh),('pop',pop),('ding',ding),('thud',thud),('impact',impact),('shimmer',shimmer),('glitch',glitch),('tick',tick),('riser',riser)]:
    save(f'{P}/assets/sfx/{name}.wav',fn())
# ---------- MUSIC: 104 BPM driving beat ----------
BPM=104; beat=60/BPM; D=float(sys.argv[2]); N=int(SR*(D+1))
mus=np.zeros((N,2))
def add(sig,at,pan=0.0,g=1.0):
    i=int(at*SR); j=min(N,i+len(sig)); 
    if i>=N: return
    s=sig[:j-i]*g; mus[i:j,0]+=s*(1-pan); mus[i:j,1]+=s*(1+pan)
kick=(lambda t: np.sin(2*np.pi*np.cumsum(55+90*np.exp(-t*30))/SR)*np.exp(-t*7))(t_(0.4))
clap=bp_noise(0.18,900,5000)*np.exp(-t_(0.18)*25)
hat=bp_noise(0.05,7000,14000)*np.exp(-t_(0.05)*90)
def note(f,d,kind='pluck'):
    t=t_(d)
    if kind=='pluck': return (np.sin(2*np.pi*f*t)+0.4*np.sin(4*np.pi*f*t)+0.15*np.sin(6*np.pi*f*t))*np.exp(-t*6)*np.minimum(1,t/0.003)
    if kind=='bass': return np.tanh(2*np.sin(2*np.pi*f*t))*np.minimum(1,t/0.01)*np.exp(-t*2.5)
    if kind=='pad':
        x=sum(np.sin(2*np.pi*f*k*t+0.3*k)/k for k in (1,2,3))
        return x*np.minimum(1,t/0.4)*np.minimum(1,(d-t)/0.4)
    if kind=='bell': return (np.sin(2*np.pi*f*t)+0.5*np.sin(2*np.pi*f*2.76*t))*np.exp(-t*3)
mid=lambda m: 440*2**((m-69)/12)
# progression Am F C G (each 1 bar = 4 beats)
prog=[(57,[57,60,64]),(53,[53,57,60]),(48,[48,52,55]),(55,[55,59,62])]
scale=[69,72,74,76,79,81]  # A minor pentatonic for melody
mel=[0,2,3,2, 4,3,2,0, 1,2,3,4, 5,4,3,2]
bar=4*beat; nb=int(D/bar)+2
for b in range(nb):
    t0=b*bar; root,ch=prog[b%4]
    intro = b<1
    for k in range(4):
        tb=t0+k*beat
        add(kick,tb,g=0.9)
        if k in (1,3): add(clap,tb,g=0.45)
        if not intro: add(kick,tb+beat*0.75,g=0.35) if k==3 else None
        for h in range(2): add(hat,tb+h*beat/2,pan=0.3,g=0.18 if h else 0.1)
        add(note(mid(root-12),beat*0.9,'bass'),tb,g=0.35)
        add(note(mid(root-12+12*(k%2)),beat*0.45,'bass'),tb+beat/2,g=0.18)
    pad=sum(note(mid(m),bar,'pad') for m in ch)/3
    add(pad,t0,g=0.10)
    if not intro:
        for k in range(8):
            m=scale[mel[(b*8+k)%16]]
            add(note(mid(m),beat*0.5,'pluck'),t0+k*beat/2,pan=-0.25,g=0.11)
        add(note(mid(ch[2]+24),bar,'bell'),t0,pan=0.3,g=0.05)
mus=mus[:int(SR*D)]
fo=int(SR*1.5); mus[-fo:]*=np.linspace(1,0,fo)[:,None]
mus=mus/np.abs(mus).max()*0.8
# sidechain duck under voice
w=wave.open(f'{P}/assets/audio/voice.wav'); vsr=w.getframerate(); v=np.frombuffer(w.readframes(w.getnframes()),np.int16).astype(np.float32)/32768
if w.getnchannels()==2: v=v.reshape(-1,2).mean(1)
hop=int(vsr*0.01); ve=np.array([np.sqrt(np.mean(v[i:i+hop]**2)) for i in range(0,len(v),hop)])
g=np.ones_like(ve); cur=1.0
for i,e in enumerate(ve):
    tgt=0.32 if e>0.02 else 1.0
    a=0.5 if tgt<cur else 0.025   # fast attack (10ms hops), slow release
    cur+= (tgt-cur)*a; g[i]=cur
gs=np.interp(np.arange(len(mus))/SR, np.arange(len(g))*0.01, g)
mus*=gs[:,None]
save(f'{P}/assets/audio/music_ducked.wav',mus*0.55)
print('ok',D)
