import subprocess, numpy as np, json, sys, math
from PIL import Image, ImageDraw, ImageFont, ImageFilter
FD="/home/claude/fonts/"
def U(w,s): return ImageFont.truetype(FD+f"fontsource-urbanist-5.3.0/package/files/urbanist-latin-{w}-normal.woff",s)
def MO(s,w=400): return ImageFont.truetype(FD+f"fontsource-dm-mono-5.3.0/package/files/dm-mono-latin-{w}-normal.woff",s)
def SI(s): return ImageFont.truetype(FD+"fontsource-instrument-serif-5.3.0/package/files/instrument-serif-latin-400-italic.woff",s)
W,H,FPS=1080,1920,30; DUR=29.8; NF=int(DUR*FPS)
BG=np.array([18,13,10],np.float32); CREAM=(239,230,219); MUT=(185,168,152); OR=(232,105,42); INK=(36,26,20)
def cl(x): return min(max(x,0),1)
def eo(x): x=cl(x); return 1-(1-x)**3
def eio(x): x=cl(x); return 4*x**3 if x<.5 else 1-(-2*x+2)**3/2
TJ=json.load(open("timing.json")); VOT=TJ["vo"]; VOENV=np.array(TJ["voenv"]); MIXENV=np.array(TJ["mixenv"])
Up="/mnt/user-data/uploads/"
TM="zscale=t=linear:npl=203,format=gbrpf32le,zscale=p=bt709,tonemap=mobius:param=0.4:desat=0,zscale=t=bt709:m=bt709:r=tv,format=yuv420p,"
# shots: (start,end,src,ss,vf,grade,dim,blur)
SH=[(0.0,6.6,Up+"IMG_1782_9.mov",30.0,TM+"crop=1070:1902:300:640,scale=1080:1920","mono",.42,5),
    (6.6,10.95,Up+"2c7c416b-13003417_1920_1080_30fps.mp4",4.6,"crop=608:1080:1080:0,scale=1080:1920","mono",.5,0),
    (10.95,13.0,Up+"e31bd15f-instabulkdownloader.com_DRZe_XDgg3E.mp4",108.67,"scale=1080:1920","warm",1,0),
    (13.0,15.3,Up+"IMG_1782_9.mov",39.7,TM+"crop=1070:1902:300:640,scale=1080:1920","mono",1,0),
    (15.3,17.38,Up+"b33060a0-005_De7SLggiXCi.mp4",36.88,"scale=1080:1920","warm",1,0),
    (17.38,20.4,Up+"IMG_1783_3.mov",-0.08,TM+"crop=1900:3378:0:300,scale=1080:1920","club",1,0),
    (20.4,21.75,Up+"IMG_1783_3.mov",2.94,TM+"crop=1215:2160:0:1680,scale=1080:1920","club",1,0),
    (21.75,23.3,Up+"89bb554f-13003413_1920_1080_30fps.mp4",0.2,"crop=608:1080:260:0,scale=1080:1920","mono",1,0),
    (23.3,DUR,Up+"IMG_1783_3.mov",5.84,TM+"crop=1215:2160:0:1680,scale=1080:1920","club",.55,26)]
STATIC=[(10.92,11.3),(12.98,13.34),(15.28,15.64),(17.36,17.72)]
x=np.arange(256)/255.; y=np.clip((x-0.08)/0.88,0,1)**1.08
LUT=(BG+(np.array([248,239,226])-BG)*y[:,None]).astype(np.uint8)
def grade(f,k):
    f=f.astype(np.float32)
    if k=="mono": return LUT[(f[...,0]*.3+f[...,1]*.59+f[...,2]*.11).astype(np.uint8)].astype(np.float32)
    l=f.mean(-1,keepdims=True)
    if k=="club": f=l+(f-l)*.62; f=f*np.array([1.06,.94,.92]); return (f-14).clip(0)*1.08
    f=l+(f-l)*.72; f=f*np.array([1.06,1.0,.9]); return (f-10).clip(0)*1.07
rng=np.random.default_rng(5); GR=[rng.normal(0,6.5,(H,W,1)).astype(np.float32) for _ in range(6)]
NOISE=[rng.integers(0,255,(H//4,W//4),dtype=np.uint8) for _ in range(8)]
def T(d,x,y,t,f,fill,sp=0,anchor="l"):
    w=sum(f.getlength(c) for c in t)+sp*(len(t)-1)
    if anchor=="m": x-=w/2
    if anchor=="r": x-=w
    for c in t: d.text((x,y),c,font=f,fill=fill); x+=f.getlength(c)+sp
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
# decoders
decs={}
def frame_for(si,t):
    st,en,src,ss,vf,g,dim,bl=SH[si]
    if si not in decs:
        for k in list(decs): decs[k][0].kill(); del decs[k]
        p=subprocess.Popen(["ffmpeg","-v","error","-nostdin","-ss",str(max(ss,0)),"-t",str(en-st+.5),"-i",src,"-vf",vf+f",fps={FPS}","-f","rawvideo","-pix_fmt","rgb24","-"],stdout=subprocess.PIPE)
        decs[si]=[p,None]
    p=decs[si]; raw=p[0].stdout.read(W*H*3)
    if len(raw)==W*H*3: p[1]=np.frombuffer(raw,np.uint8).reshape(H,W,3)
    return p[1]
def shot_at(t):
    for i,s in enumerate(SH):
        if s[0]<=t<s[1]: return i
    return len(SH)-1
TOPG=(np.clip(0.28+np.arange(H)/850,0,1)**1.3)[:,None,None].astype(np.float32)
# frequency per time
def freq(t):
    keys=[(0,87.5),(0.45,91.65),(10.92,91.65),(11.3,88.20),(12.98,88.2),(13.34,94.50),(15.28,94.5),(15.64,101.60),(17.36,101.6),(17.72,91.65),(99,91.65)]
    for (t0,f0),(t1,f1) in zip(keys,keys[1:]):
        if t0<=t<t1: return f0+(f1-f0)*eio((t-t0)/(t1-t0))
    return 91.65
STATION={(11.3,12.98):("88.20","GHAZAL","ghazal"),(13.34,15.28):("94.50","90s BOLLYWOOD","90s"),(15.64,17.36):("101.6","UNPLUGGED","unplugged")}
CAP=[("A","Namaste Indore! Aap sun rahe ho… Suyash FM, 91.65"),("B","Ek request aayi hai Vijay Nagar se —"),
     ("F","Sab milega… ek hi awaaz mein. Live."),("G","Apni date aur venue bhejo WhatsApp pe…"),("H","suyash.live")]
M=84
enc=subprocess.Popen(["ffmpeg","-v","error","-y","-f","rawvideo","-pix_fmt","rgb24","-s",f"{W}x{H}","-r",str(FPS),"-i","-","-i","fm_mix.wav",
  "-map","0:v","-map","1:a","-c:v","libx264","-preset","slow","-crf","19","-maxrate","14M","-bufsize","28M","-pix_fmt","yuv420p","-movflags","+faststart",
  "-c:a","aac","-b:a","256k","-shortest","Suyash_FM_91.65_Reel.mp4"],stdin=subprocess.PIPE)
for n in range(NF):
    t=n/FPS; si=shot_at(t); st,en,src,ss,vf,g,dim,bl=SH[si]; u=(t-st)/(en-st)
    fr=frame_for(si,t)
    z=1.0+0.05*u; cw,ch=W/z,H/z
    im=Image.fromarray(fr).resize((W,H),Image.BILINEAR,box=((W-cw)/2,(H-ch)/2,(W+cw)/2,(H+ch)/2))
    if bl: im=im.filter(ImageFilter.GaussianBlur(bl))
    v=grade(np.asarray(im),g)
    canvas=BG+(v-BG)*TOPG*dim
    # station punch-in flash
    for (a,b) in STATIC:
        if a<=t<b:
            k=math.sin(math.pi*(t-a)/(b-a)); nz=np.asarray(Image.fromarray(NOISE[n%8]).resize((W,H),Image.NEAREST)).astype(np.float32)[...,None]
            sh=int(40*k*(rng.random()-.5)); canvas=np.roll(canvas,sh,axis=1)
            canvas=canvas*(1-.75*k)+nz*.75*k*np.array([1,.93,.86])
            canvas[::4]*=1-.25*k
    if t<0.45:
        k=1-t/0.45; nz=np.asarray(Image.fromarray(NOISE[n%8]).resize((W,H),Image.NEAREST)).astype(np.float32)[...,None]
        canvas=canvas*(1-k)+nz*k*np.array([1,.93,.86])
    canvas+=GR[n%6]
    img=Image.fromarray(np.clip(canvas,0,255).astype(np.uint8))
    endk=eo((t-23.3)/.6)
    # ---------- persistent radio UI ----------
    glass(img,(M-6,272,M+262,344),36); d=ImageDraw.Draw(img,"RGBA")
    f40=U(600,40); w=T(d,M+22,280,"suyash",f40,CREAM,-1.6); d.text((M+22+w+1,280),".",font=f40,fill=OR); T(d,M+22+w+14,280,"live",f40,CREAM,-1.6)
    blink=(int(t*2)%2==0) or t>23.3
    d.ellipse([W-M-206,296,W-M-190,312],fill=OR+((255 if blink else 70),)); T(d,W-M,290,"ON AIR",MO(24,500),CREAM,4,"r")
    ui=1-endk
    if ui>0:
        ov=Image.new("RGBA",(W,H),(0,0,0,0)); o=ImageDraw.Draw(ov); A=int(255*ui)
        f=freq(t); fs=f"{f:6.2f}".strip()
        # LCD with glow
        lcd=Image.new("RGBA",(W,H),(0,0,0,0)); l=ImageDraw.Draw(lcd)
        T(l,M-6,368,fs,MO(150,300),OR+(A,),-2); T(l,M+tw(fs,MO(150,300),-2)+10,450,"FM",MO(34,500),OR+(A,),3)
        glow=lcd.filter(ImageFilter.GaussianBlur(18)); ov.alpha_composite(glow); ov.alpha_composite(lcd)
        lab="SUYASH FM · INDORE · LATE-NIGHT REQUESTS"
        for (a,b),(fq,nm,_) in STATION.items():
            if a<=t<b: lab=f"TUNED · {nm}"
        T(o,M,552,lab,MO(22),MUT+(A,),3.3)
        st_on=max([eo((t-a)/.25)*(1-eo((t-b+.1)/.2)) for (a,b) in [(10.95,13.0),(13.0,15.3),(15.3,17.38)]]+[0]); ui2=ui*(1-st_on)
        # dial
        y0=612; o.line([(M,y0+40),(W-M,y0+40)],fill=(239,230,219,int(90*ui2)),width=1)
        for i in range(0,41):
            fq=88+i*0.5; xx=M+(W-2*M)*i/40; big=(i%4==0)
            o.line([(xx,y0+(10 if big else 24)),(xx,y0+40)],fill=(239,230,219,int((170 if big else 80)*ui2)),width=2 if big else 1)
            if big: T(o,xx,y0+50,f"{int(fq)}",MO(16),MUT+(int(180*ui2),),0,"m")
        nx=M+(W-2*M)*(f-88)/20; o.line([(nx,y0-6),(nx,y0+44)],fill=OR+(int(255*ui2),),width=4); o.ellipse([nx-7,y0-14,nx+7,y0],fill=OR+(int(255*ui2),))
        # VU / waveform reacting to audio
        e=MIXENV[min(n,len(MIXENV)-1)]; ve=VOENV[min(n,len(VOENV)-1)]
        for i in range(48):
            xx=M+i*((W-2*M)/48); hh=6+min(60,(e*220+ve*260)*(0.45+0.55*abs(math.sin(i*1.7+t*9+i*i*.13))))
            o.rounded_rectangle([xx,700-hh/2+20,xx+8,700+hh/2+20],3,fill=(239,230,219,int(150*ui2)) if i%6 else OR+(int(200*ui2),))
        img.paste(ov,(0,0),ov); d=ImageDraw.Draw(img,"RGBA")
    # ---------- scene text ----------
    ov=Image.new("RGBA",(W,H),(0,0,0,0)); o=ImageDraw.Draw(ov)
    # request bubble 6.6-10.95
    if 6.7<=t<11.0:
        a=eo((t-6.75)/.4)*(1-eo((t-10.7)/.25)); A=int(255*a)
        bx=M; by=820+int(30*(1-a)); bw=W-2*M-80
        layer=img.copy(); glass(layer,(bx,by,bx+bw,by+230),36,.08); q=ImageDraw.Draw(layer)
        T(q,bx+40,by+34,"NEW REQUEST  ·  VIJAY NAGAR",MO(20),OR,3)
        if t<8.6:
            for i in range(3):
                ph=(math.sin(t*9-i*1.1)+1)/2; q.ellipse([bx+44+i*34,by+108-ph*8,bx+64+i*34,by+128-ph*8],fill=CREAM)
        else:
            k=eo((t-8.6)/.3); msg="“sangeet hai, kuch live chahiye!”"
            T(q,bx+40,by+86+int(10*(1-k)),msg,SI(60),CREAM)
        T(q,bx+bw-40,by+176,"11:42 PM ✓✓" if False else "11:42 PM",MO(18),MUT,2,"r")
        img=Image.blend(img,layer,a); d=ImageDraw.Draw(img,"RGBA")
    for (a,b),(fq,nm,word) in STATION.items():
        if a<=t<b:
            k=eo((t-a)/.3)*(1-eo((t-(b-.15))/.15)); A=int(255*k); f=U(500,150)
            ww=T(o,M-8,860+int(30*(1-k)),word,f,CREAM+(A,),-150*.045); T(o,M-8+ww+4,860+int(30*(1-k)),"?",f,OR+(A,))
    if 17.72<=t<20.95:
        a1=eo((t-17.85)/.35); T(o,M,860+int(24*(1-a1)),"sab milega.",U(500,110),CREAM+(int(255*a1),),-110*.045)
        a2=eo((t-18.95)/.35); T(o,M,990+int(24*(1-a2)),"ek hi awaaz mein.",SI(84),CREAM+(int(255*a2),))
        if t>20.15:
            a3=eo((t-20.15)/.25); s=1+0.25*(1-a3); f=U(700,int(140*s))
            T(o,M-6,1090+int(20*(1-a3)),"LIVE.",f,OR+(int(255*a3),),6)
    if 20.95<=t<23.35:
        k=eo((t-21.0)/.4)*(1-eo((t-23.1)/.25)); A=int(255*k)
        T(o,M,860,"picture your",SI(110),CREAM+(A,)); T(o,M,980,"guests here.",SI(110),OR+(A,))
    # captions (sound-off)
    if t<23.3:
        for key,txt in CAP:
            a,b=VOT[key]
            if a-.05<=t<b+.25 and key in "AB":
                k=eo((t-a+.05)/.25)*(1-eo((t-b)/.25)); f=U(500,36); bw=int(tw(txt,f)+80); bx=(W-bw)//2; by=1140
                layer=img.copy(); glass(layer,(bx,by,bx+bw,by+72),36,.03,24,.5); T(ImageDraw.Draw(layer),bx+40,by+15,txt,f,CREAM)
                img=Image.blend(img,layer,k)
    img.paste(ov,(0,0),ov)
    # ---------- end card ----------
    if t>=23.3:
        a=eo((t-23.4)/.6); layer=img.copy(); cy0=int(380+40*(1-a)); cx0=M-10; cx1=W-M+10
        glass(layer,(cx0,cy0,cx1,cy0+730),48,.07); q=ImageDraw.Draw(layer,"RGBA"); X=cx0+56; Y=cy0+56
        lcd=Image.new("RGBA",(W,H),(0,0,0,0)); l=ImageDraw.Draw(lcd); T(l,X,Y-6,"91.65",MO(64,300),OR,-1); T(l,X+tw("91.65",MO(64,300),-1)+10,Y+26,"FM",MO(22,500),OR,3)
        T(l,cx1-56,Y+14,"NOW TAKING REQUESTS",MO(18),CREAM,2.6,"r")
        layer.paste(lcd.filter(ImageFilter.GaussianBlur(12)),(0,0),lcd.filter(ImageFilter.GaussianBlur(12))); layer.paste(lcd,(0,0),lcd)
        q=ImageDraw.Draw(layer,"RGBA")
        T(q,X-4,Y+86,"request",U(400,104),CREAM,-104*.04); T(q,X-4,Y+190,"your date",U(500,104),CREAM,-104*.04)
        T(q,X,Y+320,"sangeet, house party, café — live.",SI(44),OR)
        q.line([(X,Y+396),(cx1-56,Y+396)],fill=(239,230,219),width=1)
        T(q,X,Y+426,"SEND",MO(20),MUT,3); T(q,X+120,Y+418,"event  ·  date  ·  venue",U(500,38),CREAM)
        T(q,X,Y+492,"CALL",MO(20),MUT,3); w=T(q,X+120,Y+484,"+91 ",U(500,38),CREAM); w2=T(q,X+120+w,Y+484,"91655",U(600,38),OR); T(q,X+120+w+w2,Y+484," 53087",U(500,38),CREAM)
        T(q,X,Y+558,"SEE",MO(20),MUT,3); T(q,X+120,Y+550,"suyash.live",U(500,38),CREAM)
        img=Image.blend(img,layer,a)
        b=eo((t-24.1)/.5)
        if b>0:
            layer=img.copy(); q=ImageDraw.Draw(layer); by=1140+int(24*(1-b))
            q.rounded_rectangle([M,by,W-M,by+104],52,fill=OR)
            q.ellipse([M+46,by+47,M+58,by+59],fill=INK); T(q,M+80,by+34,"SEND YOUR REQUEST",U(700,32),INK,2.6)
            ax=W-M-80; ay=by+52; q.line([(ax,ay),(ax+38,ay)],fill=INK,width=4); q.line([(ax+24,ay-14),(ax+38,ay),(ax+24,ay+14)],fill=INK,width=4)
            img=Image.blend(img,layer,b)
    enc.stdin.write(img.convert("RGB").tobytes())
    if n%90==0: print(n,file=sys.stderr)
enc.stdin.close(); enc.wait()
