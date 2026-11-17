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
Up="/mnt/user-data/uploads/"
TM="zscale=t=linear:npl=203,format=gbrpf32le,zscale=p=bt709,tonemap=mobius:param=0.4:desat=0,zscale=t=bt709:m=bt709:r=tv,format=yuv420p,"
SEGS=[ # src, ss, dur, mode, vf, size
 (Up+"IMG_1782_9.mov",2.0,3.6,"full",TM+"crop=1564:2160:214:1060,scale=1250:1726:flags=lanczos",(1250,1726),"bw"),
 (Up+"366a3673-007_DaEA4mGC79R.mp4",56.5,4.6,"card","crop=720:900:0:360",(720,900),"warm"),
 (Up+"b33060a0-005_De7SLggiXCi.mp4",37.0,4.4,"card","crop=720:900:0:110",(720,900),"warm"),
 (Up+"IMG_1783_3.mov",0.2,2.7,"full",TM+"crop=1900:3378:0:300,scale=1080:1920:flags=lanczos",(1080,1920),"club"),
 (Up+"IMG_1782_9.mov",30.0,9.0,"full",TM+"crop=1564:2160:214:1060,scale=1250:1726:flags=lanczos",(1250,1726),"bw"),
]
x=np.arange(256)/255.; y=np.clip((x-0.10)/0.86,0,1)**1.08
lo=np.array(BG,float); hi=np.array([248,239,226],float)
BWLUT=(lo+(hi-lo)*y[:,None]).astype(np.uint8)
rng=np.random.default_rng(3); GRAIN=[rng.normal(0,6,(H,W,1)).astype(np.float32) for _ in range(6)]
def T(d,x,y,t,f,fill,sp=0,anchor="l"):
    w=sum(d.textlength(c,font=f) for c in t)+sp*(len(t)-1)
    if anchor=="m": x-=w/2
    if anchor=="r": x-=w
    for c in t: d.text((x,y),c,font=f,fill=fill); x+=d.textlength(c,font=f)+sp
    return w
def tw(d,t,f,sp=0): return sum(d.textlength(c,font=f) for c in t)+sp*(len(t)-1)
def glass(img,box,r,tint=.06,blur=24):
    x0,y0,x1,y1=[int(v) for v in box]; w,h=x1-x0,y1-y0
    sh=Image.new("L",(w+120,h+120),0); ImageDraw.Draw(sh).rounded_rectangle([60,74,60+w,74+h],r,fill=150)
    img.paste((0,0,0),(x0-60,y0-60),sh.filter(ImageFilter.GaussianBlur(26)))
    c=img.crop((x0-40,y0-40,x1+40,y1+40)).filter(ImageFilter.GaussianBlur(blur)).crop((40,40,40+w,40+h))
    a=np.asarray(c).astype(np.float32)*1.1+255*tint; a+=36*np.linspace(1,0,h)[:,None,None]**3
    m=Image.new("L",(w,h),0); ImageDraw.Draw(m).rounded_rectangle([0,0,w-1,h-1],r,fill=255)
    img.paste(Image.fromarray(np.clip(a,0,255).astype(np.uint8)),(x0,y0),m)
    d=ImageDraw.Draw(img,"RGBA"); d.rounded_rectangle([x0,y0,x1-1,y1-1],r,outline=(255,255,255,90),width=2)
    d.rounded_rectangle([x0+3,y0+3,x1-4,y1-4],r-3,outline=(255,255,255,28),width=1)
def grade(rgb,kind):
    if kind=="bw":
        g=(rgb[...,0]*.3+rgb[...,1]*.59+rgb[...,2]*.11).astype(np.uint8); return BWLUT[g].astype(np.float32)
    f=rgb.astype(np.float32)
    l=f.mean(-1,keepdims=True)
    if kind=="club": f=l+(f-l)*0.62; f=f*np.array([1.06,0.94,0.92]); f=(f-14).clip(0)*1.08
    if kind=="warm": f=l+(f-l)*0.85; f=f*np.array([1.04,1.0,0.93]); f=(f-8).clip(0)*1.06
    return f
M=84; VY=420; VHo=int(1726*W/1250)
fade=(np.clip(np.arange(VHo)/260,0,1)**1.6*np.clip((VHo-np.arange(VHo))/120,0,1))[:,None,None].astype(np.float32)
enc=subprocess.Popen(["ffmpeg","-v","error","-y","-f","rawvideo","-pix_fmt","rgb24","-s",f"{W}x{H}","-r",str(FPS),"-i","-","-i","mix.wav",
  "-map","0:v","-map","1:a","-c:v","libx264","-preset","slow","-crf","20","-maxrate","14M","-bufsize","28M","-pix_fmt","yuv420p","-movflags","+faststart",
  "-c:a","aac","-b:a","256k","-shortest","Suyash_Indore_Live_Singer_Ad.mp4"],stdin=subprocess.PIPE)
GEN=[None,("ghazal.","with harmonium & tabla"),("unplugged.","just a voice & a guitar"),("on stage.","Bollywood · 90s · 2000s")]
gn=0; T0=0
for si,(src,ss,dur,mode,vf,(vw,vh),kind) in enumerate(SEGS):
    nf=int(round(dur*FPS))
    dec=subprocess.Popen(["ffmpeg","-v","error","-nostdin","-ss",str(ss),"-t",str(dur+0.2),"-i",src,"-vf",vf+f",fps={FPS}","-f","rawvideo","-pix_fmt","rgb24","-"],stdout=subprocess.PIPE)
    last=None
    for k in range(nf):
        raw=dec.stdout.read(vw*vh*3)
        if len(raw)==vw*vh*3: last=np.frombuffer(raw,np.uint8).reshape(vh,vw,3)
        fr=last; t=k/FPS; u=t/dur; gt=T0+t
        canvas=np.empty((H,W,3),np.float32); canvas[:]=BG
        if mode=="full" and vw==1250:
            if si==0: z,cyr=1.0+0.08*u,.5
            else:
                z,cyr=(1.45+.06*u,.3) if t<2.6 else (1.0+0.05*u,.5)
            cw,ch=vw/z,vh/z; x0=min(max(vw*.48-cw/2,0),vw-cw); y0=min(max(vh*cyr-ch/2,0),vh-ch)
            im=Image.fromarray(fr).resize((W,VHo),Image.BILINEAR,box=(x0,y0,x0+cw,y0+ch))
            v=grade(np.asarray(im),kind)
            endk=eio((t-2.6)/0.8) if si==4 else 0
            vy=VY+150 if si==0 else VY; hh=min(VHo,H-vy)
            canvas[vy:vy+hh]=(np.array(BG)+(v-np.array(BG))*fade*(1-0.55*endk))[:hh]
        elif mode=="full":
            z=1.0+0.07*u; cw,ch=W/z,H/z
            im=Image.fromarray(fr).resize((W,H),Image.BILINEAR,box=((W-cw)*.4,(H-ch)*.3,(W-cw)*.4+cw,(H-ch)*.3+ch))
            v=grade(np.asarray(im),kind); canvas=v*np.clip(0.25+np.arange(H)/700,0,1)[:,None,None]**1.2
            endk=0
        else:  # card
            g=grade(fr,kind)
            bgim=Image.fromarray(np.clip(g,0,255).astype(np.uint8)).resize((W,int(W*900/720))).filter(ImageFilter.GaussianBlur(40))
            b=np.asarray(bgim).astype(np.float32)*0.38; by_=(H-b.shape[0])//2; b=np.array(BG)+(b-np.array(BG))*np.minimum(np.clip(np.arange(b.shape[0])/300,0,1),np.clip((b.shape[0]-np.arange(b.shape[0]))/300,0,1))[:,None,None]
            canvas[by_:by_+b.shape[0]]=b; canvas[:]=canvas*0.9+np.array(BG)*0.1
            endk=0
        canvas+=GRAIN[k%6]
        img=Image.fromarray(np.clip(canvas,0,255).astype(np.uint8))
        if endk>0: img=Image.blend(img,img.filter(ImageFilter.GaussianBlur(22)),endk)
        if mode=="card":
            a=eo(t/0.5); cwid,chei=880,1100; cx0=(W-cwid)//2; cy0=560+int(40*(1-a))
            z=1.0+0.05*u
            win=Image.fromarray(np.clip(g,0,255).astype(np.uint8)).resize((cwid,chei),Image.BICUBIC,box=(720*(1-1/z)/2,900*(1-1/z)/2,720*(1+1/z)/2,900*(1+1/z)/2))
            glass(img,(cx0-14,cy0-14,cx0+cwid+14,cy0+chei+14),46,blur=18)
            mk=Image.new("L",(cwid,chei),0); ImageDraw.Draw(mk).rounded_rectangle([0,0,cwid-1,chei-1],36,fill=255)
            img.paste(win,(cx0,cy0),mk)
        d=ImageDraw.Draw(img)
        # persistent header
        glass(img,(M-6,150,M+220,222),36); d=ImageDraw.Draw(img)
        T(d,M+22,158,"suyash",U(600,40),CREAM,-1.6); d.text((M+22+tw(d,"suyash",U(600,40),-1.6)+2,158),".",font=U(600,40),fill=OR)
        T(d,W-M,176,"LIVE MUSIC · INDORE",MO(22),MUT,3,"r")
        ov=Image.new("RGBA",(W,H),(0,0,0,0)); o=ImageDraw.Draw(ov)
        if si==0:
            a=eo((t-.05)/.45); A=int(255*a); dy=int(30*(1-a))
            o.ellipse([M,288+dy,M+12,300+dy],fill=OR+(A,)); T(o,M+26,282+dy,"FOR YOUR NEXT EVENT",MO(22),MUT+(A,),3.3)
            T(o,M-4,318+dy,"looking for a",U(400,96),CREAM+(A,),-96*.045)
            a2=eo((t-.5)/.45); dy2=int(30*(1-a2))
            T(o,M-4,414+dy2,"live singer",U(500,120),CREAM+(int(255*a2),),-120*.045)
            a3=eo((t-1.0)/.45); T(o,M,548+int(24*(1-a3)),"in Indore?",SI(92),OR+(int(255*a3),))
            a4=eo((t-2.1)/.4)*(1-eo((t-3.3)/.3)); T(o,M,1440,"one artist. every mood.",SI(58),CREAM+(int(255*a4),))
        elif si in (1,2,3):
            gn=si; a=eo(t/.45)*(1-eo((t-(dur-.25))/.25)); A=int(255*a); dy=int(26*(1-a))
            ty=300 if mode=="card" else 1280
            T(o,M,ty+dy,f"0{si} / 03",MO(22),OR+(A,),3)
            T(o,M+120,ty+dy,"ONE ARTIST · EVERY MOOD",MO(22),MUT+(A,),3)
            ttl,sub=GEN[si]; f=U(400,120)
            T(o,M-4,ty+36+dy,ttl[:-1],f,CREAM+(A,),-120*.045); wv=tw(o,ttl[:-1],f,-120*.045)
            T(o,M-4+wv+2,ty+36+dy,".",f,OR+(A,))
            T(o,M,ty+170+dy,sub,SI(54),OR+(A,)) if mode!="card" else T(o,M+tw(o,ttl,f,-120*.045)+40,ty+94+dy,sub,SI(48),OR+(A,))
        elif si==4:
            # occasions chips 0..2.6
            occ=["Weddings & sangeet","House parties","Cafés & restaurants","Corporate evenings"]
            for i,s_ in enumerate(occ):
                a=eo((t-.1-i*.22)/.4)*(1-eo((t-2.4)/.3))
                if a<=0: continue
                layer=img.copy(); bx=M; by=1180+i*86+int(30*(1-a)); bw=int(tw(o,s_,U(500,36))+110)
                glass(layer,(bx,by,bx+bw,by+70),35); lo_=ImageDraw.Draw(layer)
                lo_.ellipse([bx+32,by+30,bx+42,by+40],fill=OR); T(lo_,bx+60,by+12,s_,U(500,36),CREAM)
                img=Image.blend(img,layer,a)
            a=eo((t-.05)/.4)*(1-eo((t-2.4)/.3)); A=int(255*a)
            T(o,M,1080,"for every kind of evening.",SI(64),CREAM+(A,))
            if t>=2.7:
                a=eo((t-2.9)/.6)
                layer=img.copy(); cy0=int(330+50*(1-a)); cx0=M-10; cx1=W-M+10
                glass(layer,(cx0,cy0,cx1,cy0+800),48,.07); q=ImageDraw.Draw(layer)
                X=cx0+56; Y=cy0+60
                q.ellipse([X,Y+8,X+12,Y+20],fill=OR); T(q,X+26,Y+2,"NOW BOOKING · INDORE",MO(22),CREAM,3.3)
                T(q,X-4,Y+56,"bring him to",U(400,96),CREAM,-96*.04)
                T(q,X-4,Y+152,"your evening",U(500,96),CREAM,-96*.04)
                T(q,X,Y+278,"ghazal, Bollywood, 90s & unplugged.",SI(46),OR)
                q.line([(X,Y+370),(cx1-56,Y+370)],fill=(239,230,219),width=1)
                T(q,X,Y+402,"WHATSAPP / CALL",MO(20),MUT,3); T(q,X,Y+432,"+91 91655 53087",U(500,56),CREAM,-.5)
                T(q,X,Y+528,"SEE MORE",MO(20),MUT,3); T(q,X,Y+558,"suyash.live  ·  @_suyashgoswami",U(500,38),CREAM)
                T(q,X,Y+640,"Share your date & venue — get a quote in minutes.",U(400,30),MUT)
                img=Image.blend(img,layer,a)
                b=eo((t-3.5)/.5)
                if b>0:
                    layer=img.copy(); q=ImageDraw.Draw(layer); by=1230+int(30*(1-b))
                    q.rounded_rectangle([M,by,W-M,by+108],54,fill=OR)
                    q.ellipse([M+46,by+49,M+58,by+61],fill=INK); T(q,M+80,by+35,"CHECK MY DATE ON WHATSAPP",U(700,31),INK,2)
                    ax=W-M-76; ay=by+54; q.line([(ax,ay),(ax+36,ay)],fill=INK,width=4); q.line([(ax+22,ay-14),(ax+36,ay),(ax+22,ay+14)],fill=INK,width=4)
                    img=Image.blend(img,layer,b)
        img.paste(ov,(0,0),ov)
        enc.stdin.write(img.convert("RGB").tobytes())
    dec.stdout.close(); dec.wait(); T0+=dur; print("seg",si,file=sys.stderr)
enc.stdin.close(); enc.wait()
