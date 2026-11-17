import subprocess, numpy as np, sys, math, cv2
from PIL import Image, ImageDraw, ImageFont, ImageFilter
FD="/home/claude/fonts/"
def U(w,s): return ImageFont.truetype(FD+f"fontsource-urbanist-5.3.0/package/files/urbanist-latin-{w}-normal.woff",s)
def MO(s,w=400): return ImageFont.truetype(FD+f"fontsource-dm-mono-5.3.0/package/files/dm-mono-latin-{w}-normal.woff",s)
def SI(s): return ImageFont.truetype(FD+"fontsource-instrument-serif-5.3.0/package/files/instrument-serif-latin-400-italic.woff",s)
W,H,FPS=1080,1920,30
BG=np.array([18,13,10],np.float32); CREAM=(239,230,219); MUT=(185,168,152); OR=(232,105,42); INK=(36,26,20)
UP="/mnt/user-data/uploads/"
S82=UP+"IMG_1782_9.mov"; S83=UP+"IMG_1783_3.mov"
TM="zscale=t=linear:npl=203,format=gbrpf32le,zscale=p=bt709,tonemap=mobius:param=0.4:desat=0,zscale=t=bt709:m=bt709:r=tv,format=yuv420p,"
def cl(x): return min(max(x,0),1)
def eo(x): x=cl(x); return 1-(1-x)**3
def eio(x): x=cl(x); return 4*x**3 if x<.5 else 1-(-2*x+2)**3/2
x_=np.arange(256)/255.; y_=np.clip((x_-0.08)/0.88,0,1)**1.08
LUT=(BG+(np.array([248,239,226])-BG)*y_[:,None]).astype(np.uint8)
def mono(f): f=f.astype(np.float32); return LUT[(f[...,0]*.3+f[...,1]*.59+f[...,2]*.11).astype(np.uint8)].astype(np.float32)
def warm(f,sat=.78):
    f=f.astype(np.float32); l=f.mean(-1,keepdims=True); f=l+(f-l)*sat; f=f*np.array([1.06,1.0,.9]); return (f-10).clip(0)*1.07
def T(d,x,y,t,f,fill,sp=0,anchor="l"):
    w=sum(f.getlength(c) for c in t)+sp*(len(t)-1)
    if anchor=="m": x-=w/2
    if anchor=="r": x-=w
    for c in t: d.text((x,y),c,font=f,fill=fill); x+=f.getlength(c)+sp
    return w
def tw(t,f,sp=0): return sum(f.getlength(c) for c in t)+sp*(len(t)-1)
def glass(img,box,r,tint=.05,blur=24,dark=.7):
    x0,y0,x1,y1=[int(v) for v in box]; w,h=x1-x0,y1-y0
    c=img.crop((x0-40,y0-40,x1+40,y1+40)).filter(ImageFilter.GaussianBlur(blur)).crop((40,40,40+w,40+h))
    a=np.asarray(c).astype(np.float32)*dark+255*tint; a+=30*np.linspace(1,0,h)[:,None,None]**3
    m=Image.new("L",(w,h),0); ImageDraw.Draw(m).rounded_rectangle([0,0,w-1,h-1],r,fill=255)
    img.paste(Image.fromarray(np.clip(a,0,255).astype(np.uint8)),(x0,y0),m)
    d=ImageDraw.Draw(img,"RGBA"); d.rounded_rectangle([x0,y0,x1-1,y1-1],r,outline=(255,255,255,85),width=2)
def chip(img,M=84,y=272):
    f=U(600,38); w0=tw("suyashislive",f,-1.4)+46
    glass(img,(M-6,y,M-6+w0+20,y+70),35); d=ImageDraw.Draw(img)
    d.ellipse([M+14,y+30,M+24,y+40],fill=OR); T(d,M+34,y+12,"suyashislive",f,CREAM,-1.4)
GRAIN=[np.random.default_rng(i).normal(0,6,(H,W,1)).astype(np.float32) for i in range(6)]
class Dec:
    def __init__(s,src,ss,dur,vf,w=W,h=H):
        s.w,s.h=w,h; s.p=subprocess.Popen(["ffmpeg","-v","error","-nostdin","-ss",str(ss),"-t",str(dur+.4),"-i",src,"-vf",vf+f",fps={FPS}","-f","rawvideo","-pix_fmt","rgb24","-"],stdout=subprocess.PIPE); s.last=None
    def read(s):
        r=s.p.stdout.read(s.w*s.h*3)
        if len(r)==s.w*s.h*3: s.last=np.frombuffer(r,np.uint8).reshape(s.h,s.w,3)
        return s.last
    def close(s): s.p.kill()
def encoder(out,wav):
    return subprocess.Popen(["ffmpeg","-v","error","-y","-f","rawvideo","-pix_fmt","rgb24","-s",f"{W}x{H}","-r",str(FPS),"-i","-","-i",wav,
      "-map","0:v","-map","1:a","-c:v","libx264","-preset","slow","-crf","18","-maxrate","16M","-bufsize","32M","-pix_fmt","yuv420p","-movflags","+faststart",
      "-c:a","aac","-b:a","256k","-shortest",out],stdin=subprocess.PIPE)
# ---------- audio ----------
SR=48000
ENH="highpass=f=70,afftdn=nr=5:nf=-48:tn=1,equalizer=f=220:t=q:w=1.1:g=-1.5,equalizer=f=3200:t=q:w=1.3:g=1.8,highshelf=f=10000:g=1.2,acompressor=threshold=-22dB:ratio=2:attack=20:release=220:makeup=1.5"
def aload(src,ss,dur,stream="0:a:0",enhance=True):
    af=(ENH+"," if enhance else "")+f"aresample={SR}"
    r=subprocess.run(["ffmpeg","-nostdin","-v","error","-ss",str(ss),"-t",str(dur),"-i",src,"-map",stream,"-af",af,"-ac","2","-f","f32le","-"],capture_output=True)
    return np.frombuffer(r.stdout,np.float32).reshape(-1,2).copy()
def lufs_norm(a,target=-16.0):
    rms=np.sqrt(np.mean(a**2))+1e-9; return a*(10**(target/20))/rms
def fade(a,fi=.03,fo=.05):
    i=int(fi*SR); o=int(fo*SR)
    if i: a[:i]*=np.linspace(0,1,i)[:,None]
    if o: a[-o:]*=np.linspace(1,0,o)[:,None]
    return a
def write_mix(segs,dur,path,end_fade=1.2):
    N=int(dur*SR); mix=np.zeros((N,2),np.float32)
    for a,t in segs:
        s=int(t*SR); e=min(N,s+len(a)); mix[s:e]+=a[:e-s]
    if end_fade: k=int(end_fade*SR); mix[-k:]*=np.linspace(1,0,k)[:,None]
    pk=np.abs(mix).max();
    if pk>0.95: mix=np.tanh(mix/pk*1.6)/np.tanh(1.6)*0.95
    import soundfile as sf; sf.write(path,mix,SR,subtype="PCM_24")
    subprocess.run(["ffmpeg","-v","error","-y","-i",path,"-af","loudnorm=I=-14:TP=-1.2:LRA=11","-ar",str(SR),path+".n.wav"]); 
    import os; os.replace(path+".n.wav",path)
