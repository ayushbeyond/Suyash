import subprocess, numpy as np, sys
from PIL import Image, ImageDraw, ImageFont, ImageFilter
FD="/home/claude/fonts/"
def U(w,s): return ImageFont.truetype(FD+f"fontsource-urbanist-5.3.0/package/files/urbanist-latin-{w}-normal.woff",s)
def MO(s): return ImageFont.truetype(FD+"fontsource-dm-mono-5.3.0/package/files/dm-mono-latin-400-normal.woff",s)
def SI(s): return ImageFont.truetype(FD+"fontsource-instrument-serif-5.3.0/package/files/instrument-serif-latin-400-italic.woff",s)
W,H,FPS=1080,1920,30
BG=(18,13,10); CREAM=(239,230,219); MUT=(185,168,152); OR=(232,105,42); INK=(36,26,20)
def cl(x): return min(max(x,0),1)
def eo(x): x=cl(x); return 1-(1-x)**3
def eio(x): x=cl(x); return 4*x**3 if x<.5 else 1-(-2*x+2)**3/2
Up="/mnt/user-data/uploads/"; S82=Up+"IMG_1782_9.mov"; S83=Up+"IMG_1783_3.mov"
P17=Up+"2c7c416b-13003417_1920_1080_30fps.mp4"; P13=Up+"89bb554f-13003413_1920_1080_30fps.mp4"
TM="zscale=t=linear:npl=203,format=gbrpf32le,zscale=p=bt709,tonemap=mobius:param=0.4:desat=0,zscale=t=bt709:m=bt709:r=tv,format=yuv420p,"
A0=2.0  # audio/video sync origin in IMG_1782
CROP={"wide":(TM+"crop=1564:2160:214:1060,scale=1250:1726:flags=lanczos",(1250,1726)),
      "close":(TM+"crop=860:1529:500:860,scale=1080:1920:flags=lanczos",(1080,1920)),
      "medium":(TM+"crop=1070:1902:300:640,scale=1080:1920:flags=lanczos",(1080,1920)),
      "hands":(TM+"crop=1215:2160:0:1680,scale=1080:1920:flags=lanczos",(1080,1920)),
      "px17":("crop=608:1080:1080:0,scale=1080:1920:flags=lanczos",(1080,1920)),
      "px13":("crop=608:1080:260:0,scale=1080:1920:flags=lanczos",(1080,1920))}
x=np.arange(256)/255.; y=np.clip((x-0.08)/0.88,0,1)**1.08
LUT=(np.array(BG,float)+(np.array([248,239,226])-np.array(BG,float))*y[:,None]).astype(np.uint8)
rng=np.random.default_rng(3); GRAIN=[rng.normal(0,6.5,(H,W,1)).astype(np.float32) for _ in range(6)]
def mono(rgb,k=1.0):
    g=(rgb[...,0]*.3+rgb[...,1]*.59+rgb[...,2]*.11)
    if k!=1.0: g=np.clip((g-128)*k+128,0,255)
    return LUT[g.astype(np.uint8)].astype(np.float32)
def club(rgb):
    f=rgb.astype(np.float32); l=f.mean(-1,keepdims=True); f=l+(f-l)*0.6; f=f*np.array([1.06,.94,.92]); return ((f-14).clip(0)*1.08)
def T(d,x,y,t,f,fill,sp=0,anchor="l"):
    w=sum(d.textlength(c,font=f) for c in t)+sp*(len(t)-1)
    if anchor=="m": x-=w/2
    if anchor=="r": x-=w
    for c in t: d.text((x,y),c,font=f,fill=fill); x+=d.textlength(c,font=f)+sp
    return w
def tw(t,f,sp=0): return sum(f.getlength(c) for c in t)+sp*(len(t)-1)
def glass(img,box,r,tint=.06,blur=24,dark=1.0):
    x0,y0,x1,y1=[int(v) for v in box]; w,h=x1-x0,y1-y0
    sh=Image.new("L",(w+120,h+120),0); ImageDraw.Draw(sh).rounded_rectangle([60,74,60+w,74+h],r,fill=140)
    img.paste((0,0,0),(x0-60,y0-60),sh.filter(ImageFilter.GaussianBlur(26)))
    c=img.crop((x0-40,y0-40,x1+40,y1+40)).filter(ImageFilter.GaussianBlur(blur)).crop((40,40,40+w,40+h))
    a=np.asarray(c).astype(np.float32)*1.1*dark+255*tint; a+=36*np.linspace(1,0,h)[:,None,None]**3
    m=Image.new("L",(w,h),0); ImageDraw.Draw(m).rounded_rectangle([0,0,w-1,h-1],r,fill=255)
    img.paste(Image.fromarray(np.clip(a,0,255).astype(np.uint8)),(x0,y0),m)
    d=ImageDraw.Draw(img,"RGBA"); d.rounded_rectangle([x0,y0,x1-1,y1-1],r,outline=(255,255,255,90),width=2)
    d.rounded_rectangle([x0+3,y0+3,x1-4,y1-4],r-3,outline=(255,255,255,28),width=1)
M=84; VY=560; VHo=int(1726*W/1250)
FADE=(np.clip(np.arange(VHo)/300,0,1)**1.6*np.clip((VHo-np.arange(VHo))/140,0,1))[:,None,None].astype(np.float32)
TOPG=(np.clip(0.3+np.arange(H)/900,0,1)**1.3)[:,None,None].astype(np.float32)   # darken top for text
def A(t,a,dur=.45): return eo((t-a)/dur)
def fx(t,a,b,dur=.45): return eo((t-a)/dur)*(1-eo((t-(b-.25))/.25))

# ---- text layers per scene ----
def txt_hook(o,t,d):
    a=A(t,.05); al=int(255*a); dy=int(30*(1-a))
    o.ellipse([M,416+dy,M+12,428+dy],fill=OR+(al,)); T(o,M+26,410+dy,"LIVE MUSIC · INDORE",MO(22),MUT+(al,),3.3)
    a2=A(t,.15); T(o,M-6,452+int(30*(1-a2)),"planning a",U(400,104),CREAM+(int(255*a2),),-104*.045)
    a3=A(t,.35); T(o,M-6,552+int(30*(1-a3)),"celebration",U(500,124),CREAM+(int(255*a3),),-124*.045)
    a4=A(t,.6); T(o,M,690+int(24*(1-a4)),"in Indore?",SI(96),OR+(int(255*a4),))
def txt_live(o,t,d):
    a=fx(t,.0,d); al=int(255*a); dy=int(30*(1-a)); f=U(400,150)
    w=T(o,M-8,330+dy,"make it live",f,CREAM+(al,),-150*.045); T(o,M-8+w,330+dy,".",f,OR+(al,))
def txt_close(o,t,d,img):
    a=fx(t,.1,d)
    return [("pill","LIVE VOCALS  ·  ACOUSTIC GUITAR",1120,a)]
def txt_range(o,t,d):
    a=fx(t,.0,d); al=int(255*a); dy=int(26*(1-a))
    T(o,M,410+dy,"ONE ARTIST · EVERY MOOD",MO(22),MUT+(al,),3.3)
    T(o,M-4,448+dy,"bollywood · 90s · ghazal",U(500,78),CREAM+(al,),-78*.03)
def txt_guests(o,t,d):
    a=fx(t,.0,d); al=int(255*a); dy=int(26*(1-a))
    T(o,M,420+dy,"picture your",SI(112),CREAM+(al,)); T(o,M,540+dy,"guests here.",SI(112),OR+(al,))
def chips_events(t,d):
    occ=["sangeet & weddings","house parties","café evenings","corporate nights"]
    return [("chip",s,780+i*94,fx(t,.05+i*.18,d)) for i,s in enumerate(occ)]
def endcard(img,t,full):
    a=eo((t-.15)/.6)
    if a<=0: return img
    layer=img.copy(); cy0=int(380+50*(1-a)); cx0=M-10; cx1=W-M+10
    glass(layer,(cx0,cy0,cx1,cy0+720),48,.07); q=ImageDraw.Draw(layer)
    X=cx0+56; Y=cy0+58
    q.ellipse([X,Y+8,X+12,Y+20],fill=OR); T(q,X+26,Y+2,"NOW BOOKING · INDORE",MO(22),CREAM,3.3)
    T(q,X-4,Y+52,"check your date",U(400,92),CREAM,-92*.04)
    T(q,X-4,Y+146,"on WhatsApp",U(500,92),CREAM,-92*.04); 
    T(q,X,Y+268,"wedding-season dates are going fast." if full else "make your evening live.",SI(44),OR)
    q.line([(X,Y+344),(cx1-56,Y+344)],fill=(239,230,219),width=1)
    T(q,X,Y+374,"SEND",MO(20),MUT,3); T(q,X+110,Y+366,"event  ·  date  ·  venue",U(500,38),CREAM)
    T(q,X,Y+440,"CALL",MO(20),MUT,3); T(q,X+110,Y+432,"+91 91655 53087",U(500,38),CREAM)
    T(q,X,Y+506,"SEE",MO(20),MUT,3); T(q,X+110,Y+498,"suyash.live",U(500,38),CREAM)
    img=Image.blend(img,layer,a)
    b=eo((t-.7)/.5)
    if b>0:
        layer=img.copy(); q=ImageDraw.Draw(layer); by=1132+int(24*(1-b))
        q.rounded_rectangle([M,by,W-M,by+104],52,fill=OR)
        q.ellipse([M+46,by+47,M+58,by+59],fill=INK); T(q,M+80,by+34,"SEND YOUR DATE",U(700,32),INK,2.6)
        ax=W-M-80; ay=by+52; q.line([(ax,ay),(ax+38,ay)],fill=INK,width=4); q.line([(ax+24,ay-14),(ax+38,ay),(ax+24,ay+14)],fill=INK,width=4)
        img=Image.blend(img,layer,b)
    return img

def render(out,shots,adur,full=True):
    subprocess.run(["ffmpeg","-v","error","-y","-ss",str(A0),"-t",str(adur),"-i",S82,"-map","0:2","-af",
        f"volume=10dB,alimiter=limit=0.95,afade=t=in:d=0.12,afade=t=out:st={adur-1.3}:d=1.3","-ar","48000","-c:a","pcm_s16le","aud.wav"],check=True)
    enc=subprocess.Popen(["ffmpeg","-v","error","-y","-f","rawvideo","-pix_fmt","rgb24","-s",f"{W}x{H}","-r",str(FPS),"-i","-","-i","aud.wav",
      "-map","0:v","-map","1:a","-c:v","libx264","-preset","slow","-crf","19","-maxrate","14M","-bufsize","28M","-pix_fmt","yuv420p","-movflags","+faststart",
      "-c:a","aac","-b:a","256k","-shortest",out],stdin=subprocess.PIPE)
    gt=0
    for (src,ss,dur,crop,scene) in shots:
        if src==S82: ss=A0+gt     # keep lip sync with the continuous audio
        vf,(vw,vh)=CROP[crop]; nf=int(round(dur*FPS))
        dec=subprocess.Popen(["ffmpeg","-v","error","-nostdin","-ss",str(ss),"-t",str(dur+.3),"-i",src,"-vf",vf+f",fps={FPS}","-f","rawvideo","-pix_fmt","rgb24","-"],stdout=subprocess.PIPE)
        last=None
        for k in range(nf):
            raw=dec.stdout.read(vw*vh*3)
            if len(raw)==vw*vh*3: last=np.frombuffer(raw,np.uint8).reshape(vh,vw,3)
            fr=last; t=k/FPS; u=t/dur
            canvas=np.empty((H,W,3),np.float32); canvas[:]=BG
            if crop=="wide":
                z=1.0+0.04*u; cw,ch=vw/z,vh/z; x0=(vw-cw)*.5; y0=(vh-ch)*.5
                im=np.asarray(Image.fromarray(fr).resize((W,VHo),Image.BILINEAR,box=(x0,y0,x0+cw,y0+ch)))
                v=mono(im); endk=eio((t-.0)/.6) if scene=="end" else 0
                canvas[VY:VY+VHo]=(np.array(BG)+(v-np.array(BG))*FADE*(1-.5*endk))[:H-VY]
            else:
                z=1.0+0.05*u; cw,ch=W/z,H/z
                im=np.asarray(Image.fromarray(fr).resize((W,H),Image.BILINEAR,box=((W-cw)/2,(H-ch)/2,(W+cw)/2,(H+ch)/2)))
                v=club(im) if crop=="hands" else mono(im,1.08 if crop.startswith("px") else 1.0)
                canvas=np.array(BG)+(v-np.array(BG))*TOPG; endk=0
                if scene=='events': canvas=np.array(BG)+(canvas-np.array(BG))*np.clip(0.45+np.arange(W)/1100,0,1)[None,:,None]
            canvas+=GRAIN[k%6]
            img=Image.fromarray(np.clip(canvas,0,255).astype(np.uint8))
            if endk>0: img=Image.blend(img,img.filter(ImageFilter.GaussianBlur(24)),endk)
            # brand chip
            glass(img,(M-6,272,M+262,344),36); d=ImageDraw.Draw(img)
            f40=U(600,40); w=T(d,M+22,280,"suyash",f40,CREAM,-1.6); d.text((M+22+w+1,280),".",font=f40,fill=OR); T(d,M+22+w+14,280,"live",f40,CREAM,-1.6)
            extra=[]
            ov=Image.new("RGBA",(W,H),(0,0,0,0)); o=ImageDraw.Draw(ov)
            if scene=="hook": txt_hook(o,t,dur)
            elif scene=="live": txt_live(o,t,dur)
            elif scene=="close": extra=txt_close(o,t,dur,img)
            elif scene=="range": txt_range(o,t,dur)
            elif scene=="guests": txt_guests(o,t,dur)
            elif scene=="events": extra=chips_events(t,dur)
            for kind,s_,yy,a in extra:
                if a<=0: continue
                layer=img.copy(); lo=ImageDraw.Draw(layer)
                if kind=="pill":
                    f=MO(24); bw=int(tw(s_,f,3)+100); bx=(W-bw)//2; by=yy+int(24*(1-a))
                    glass(layer,(bx,by,bx+bw,by+76),38,.03,24,.55); lo=ImageDraw.Draw(layer)
                    lo.ellipse([bx+34,by+33,bx+44,by+43],fill=OR); T(lo,bx+60,by+23,s_,f,CREAM,3)
                else:
                    f=U(500,40); bw=int(tw(s_,f)+108); bx=M; by=yy+int(24*(1-a))
                    glass(layer,(bx,by,bx+bw,by+76),38,.03,24,.55); lo=ImageDraw.Draw(layer)
                    lo.ellipse([bx+34,by+33,bx+44,by+43],fill=OR); T(lo,bx+60,by+14,s_,f,CREAM)
                img=Image.blend(img,layer,a)
            if scene=="events":
                a=fx(t,0,dur); T(o,M,690+int(24*(1-a)),"for every kind of evening.",SI(64),CREAM+(int(255*a),))
            img.paste(ov,(0,0),ov)
            if scene=="end": img=endcard(img,t,full)
            enc.stdin.write(img.tobytes())
        dec.stdout.close(); dec.kill(); gt+=dur; print(out,scene,file=sys.stderr)
    enc.stdin.close(); enc.wait()

which=sys.argv[1]
if which=="master":
    render("Suyash_Ad_15s_Master.mp4",[
      (P17,5.0,1.6,"px17","hook"),(S82,0,2.4,"wide","live"),(S82,0,1.3,"close","close"),
      (S83,0.4,1.2,"hands","range"),(P13,0.2,1.2,"px13","guests"),(S82,0,2.7,"medium","events"),
      (S82,0,4.6,"wide","end")],15.0,True)
else:
    render("Suyash_Ad_8s_Story.mp4",[
      (P17,5.0,1.0,"px17","hook"),(S82,0,1.0,"wide","hook"),(S82,0,2.8,"close","live"),(S82,0,3.2,"wide","end")],8.0,False)
