import numpy as np, subprocess, json
SR=48000; DUR=29.8; N=int(SR*DUR)
U="/mnt/user-data/uploads/"
def load(path,ss,dur,stream="0:a:0"):
    r=subprocess.run(["ffmpeg","-nostdin","-v","error","-ss",str(ss),"-t",str(dur),"-i",path,"-map",stream,"-ac","2","-ar",str(SR),"-f","f32le","-"],capture_output=True)
    a=np.frombuffer(r.stdout,np.float32).reshape(-1,2).copy(); return a
def rms(a): return float(np.sqrt(np.mean(a**2))+1e-9)
def norm(a,db): return a*(10**(db/20))/rms(a)
def fades(a,fi=.04,fo=.06):
    n=len(a); i=int(fi*SR); o=int(fo*SR)
    if i: a[:i]*=np.linspace(0,1,i)[:,None]
    if o: a[-o:]*=np.linspace(1,0,o)[:,None]
    return a
mix=np.zeros((N,2),np.float32); music=np.zeros((N,2),np.float32); vo=np.zeros((N,2),np.float32)
def put(buf,a,t):
    s=int(t*SR); e=min(N,s+len(a)); buf[s:e]+=a[:e-s]
# --- voiceover take 1 segments (src start,end) -> timeline
VOF=U+"81d6acd5-ElevenLabs_2026-11-17T14_48_54_Sia_-_Excited__Enthusiastic_Creator_pvc_s50_sim75_v4.mp3"
VO={"A":(0.0,6.12,0.35),"B":(6.36,10.72,6.6),"C":(11.02,11.50,11.32),"D":(11.96,13.66,13.36),"E":(14.03,15.28,15.66),
    "F":(15.55,18.62,17.85),"G":(20.30,24.44,23.45),"H":(24.72,26.20,27.75)}
vo_src=load(VOF,0,27,"0:a:0"); vo_src=vo_src/ (np.abs(vo_src).max()+1e-9)*0.89
timing={}
for k,(a,b,t) in VO.items():
    seg=fades(vo_src[int(a*SR):int(b*SR)].copy(),.02,.05); put(vo,seg,t); timing[k]=[t,t+(b-a)]
# --- radio bed under intro: 1782 stage song, band-limited like a radio
bed=load(U+"IMG_1782_9.mov",30.0,11.3,"0:2")
import scipy.signal as sg
b_,a_=sg.butter(4,[450/(SR/2),3400/(SR/2)],"band"); bed=sg.lfilter(b_,a_,bed,axis=0).astype(np.float32)
bed=fades(norm(bed,-27),0.6,0.25); put(music,bed,0.25)
rng=np.random.default_rng(1)
hiss=rng.normal(0,1,(int(11*SR),2)).astype(np.float32); hiss=sg.lfilter(*sg.butter(2,[2000/(SR/2),9000/(SR/2)],"band"),hiss,axis=0).astype(np.float32)
crack=(rng.random((len(hiss),1))>0.9993)*rng.normal(0,1,(len(hiss),1))*3
hiss=fades(norm(hiss,-44)+crack.astype(np.float32)*0.02,0.05,0.3); put(music,hiss,0.0)
# --- SFX: tuning sweep (filtered noise + heterodyne whistle + click)
def tune(d=0.36,f0=600,f1=4200,big=False):
    n=int(d*SR); t=np.arange(n)/SR
    nz=rng.normal(0,1,n).astype(np.float32); out=np.zeros(n,np.float32); fc=np.geomspace(f0,f1,n)
    for i in range(0,n,256):
        c=fc[i]; bb,aa=sg.butter(2,[max(c*.6,60)/(SR/2),min(c*1.6,20000)/(SR/2)],"band"); out[i:i+256]=sg.lfilter(bb,aa,nz[i:i+256])
    wh=np.sin(2*np.pi*np.cumsum(np.geomspace(2600,900,n))/SR)*0.35*np.sin(np.pi*t/d)**2
    env=np.sin(np.pi*np.clip(t/d,0,1))**0.6
    s=(out/ (np.abs(out).max()+1e-9)*0.8+wh)*env
    if big: s*=1.2
    clk=np.zeros(n,np.float32); m=int(0.012*SR); clk[-m:]=rng.normal(0,1,m)*np.exp(-np.arange(m)/(m/6))*0.9
    return np.stack([s+clk,s*0.92+clk],1).astype(np.float32)
def chime(notes=(659.25,830.6,987.8),gap=.11,dur=1.1):
    n=int((gap*len(notes)+dur)*SR); out=np.zeros(n,np.float32)
    for i,f in enumerate(notes):
        s=int(i*gap*SR); t=np.arange(n-s)/SR
        out[s:]+= (np.sin(2*np.pi*f*t)+0.3*np.sin(2*np.pi*2*f*t)+0.1*np.sin(2*np.pi*3.01*f*t))*np.exp(-t*4.2)*0.28
    return np.stack([out,out],1)
sfx=np.zeros((N,2),np.float32)
put(sfx,norm(tune(0.42,300,3800),-17),0.0)
put(sfx,norm(chime(),-24),0.42)
for t in (10.92,12.98,15.28): put(sfx,norm(tune(),-16),t)
put(sfx,norm(tune(0.34,4000,500,True),-15),17.36)
put(sfx,norm(chime((987.8,830.6,659.25,987.8),.09),-25),28.9)
# --- stations (own audio)
def station(path,ss,d,t,db=-20,stream="0:a:0"):
    a=fades(norm(load(path,ss,d,stream),db),0.03,0.06); put(music,a,t)
station(U+"e31bd15f-instabulkdownloader.com_DRZe_XDgg3E.mp4",109.0,1.72,11.28)
station(U+"IMG_1782_9.mov",40.0,2.02,13.30,-20,"0:2")
station(U+"b33060a0-005_De7SLggiXCi.mp4",37.2,1.75,15.62)
# --- the song: IMG_1783 continuous from 17.7
song=load(U+"IMG_1783_3.mov",0.2,DUR-17.66,"0:2"); song=norm(song,-18.5)
n=len(song); song[-int(1.6*SR):]*=np.linspace(1,0,int(1.6*SR))[:,None]; song[:int(.05*SR)]*=np.linspace(0,1,int(.05*SR))[:,None]
put(music,song,17.66)
# --- ducking music under voice (envelope follower)
env=np.abs(vo).max(1); k=int(0.02*SR); env=np.convolve(env,np.ones(k)/k,"same")
gate=(env>0.02).astype(np.float32); sm=int(0.12*SR); gate=np.convolve(gate,np.ones(sm)/sm,"same")
duck=10**(-9*gate/20)
mix=music*duck[:,None]+vo*1.0+sfx
mix=np.tanh(mix*1.25)/np.tanh(1.25)*0.95
import soundfile as sf; sf.write("fm_mix.wav",mix,SR,subtype="PCM_24")
# envelope for visuals
fr=30; env2=[float(np.sqrt(np.mean(vo[int(i/fr*SR):int((i+1)/fr*SR)]**2))) for i in range(int(DUR*fr))]
musenv=[float(np.sqrt(np.mean(mix[int(i/fr*SR):int((i+1)/fr*SR)]**2))) for i in range(int(DUR*fr))]
json.dump({"vo":timing,"voenv":env2,"mixenv":musenv},open("timing.json","w"))
print(timing)
