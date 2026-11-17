import subprocess, numpy as np, sys
from PIL import Image, ImageDraw, ImageFont, ImageFilter
SRC="/mnt/user-data/uploads/IMG_1782_9.mov"; SS=2.0; DUR=21.0; FPS=30; N=int(DUR*FPS)
W,H=1080,1920; VW,VH=1250,1726
FD="/home/claude/fonts/"
def U(w,s): return ImageFont.truetype(FD+f"fontsource-urbanist-5.3.0/package/files/urbanist-latin-{w}-normal.woff",s)
def MO(s): return ImageFont.truetype(FD+"fontsource-dm-mono-5.3.0/package/files/dm-mono-latin-400-normal.woff",s)
def SI(s): return ImageFont.truetype(FD+"fontsource-instrument-serif-5.3.0/package/files/instrument-serif-latin-400-italic.woff",s)
BG=(18,13,10); CREAM=(239,230,219); MUT=(185,168,152); OR=(232,105,42); INK=(36,26,20)
def cl(x): return min(max(x,0),1)
def eo(x): x=cl(x); return 1-(1-x)**3
def eio(x): x=cl(x); return 4*x**3 if x<.5 else 1-(-2*x+2)**3/2
TM="zscale=t=linear:npl=203,format=gbrpf32le,zscale=p=bt709,tonemap=mobius:param=0.4:desat=0,zscale=t=bt709:m=bt709:r=tv,format=yuv420p"
dec=subprocess.Popen(["ffmpeg","-v","error","-ss",str(SS),"-t",str(DUR),"-i",SRC,"-vf",f"{TM},fps={FPS},crop=1564:2160:214:1060,scale={VW}:{VH}:flags=lanczos","-f","rawvideo","-pix_fmt","gray","-"],stdout=subprocess.PIPE)
enc=subprocess.Popen(["ffmpeg","-v","error","-y","-f","rawvideo","-pix_fmt","rgb24","-s",f"{W}x{H}","-r",str(FPS),"-i","-",
  "-ss",str(SS),"-t",str(DUR),"-i",SRC,"-map","0:v","-map","1:2","-af",f"afade=t=in:d=0.25,afade=t=out:st={DUR-1.6}:d=1.6",
  "-c:v","libx264","-preset","slow","-crf","16","-pix_fmt","yuv420p","-profile:v","high","-movflags","+faststart","-c:a","aac","-b:a","256k","ad_raw.mp4"],stdin=subprocess.PIPE)
# tone LUT: deeper blacks, warm duotone
x=np.arange(256)/255.; y=np.clip((x-0.10)/0.86,0,1)**1.08
lo=np.array(BG,float); hi=np.array([248,239,226],float)
LUT=(lo+(hi-lo)*y[:,None]).astype(np.uint8)
VY=420; VHo=int(VH*W/VW)  # 1491
fade=np.clip((np.arange(VHo)-0)/260,0,1)**1.6; fade*=np.clip((VHo-np.arange(VHo))/120,0,1)
FADE=fade[:,None,None].astype(np.float32)
rng=np.random.default_rng(3); GRAIN=[rng.normal(0,6,(H,W,1)).astype(np.float32) for _ in range(6)]
# shot plan: (start, zoom_from, zoom_to, cy_rel)
shots=[(0,1.00,1.08,.5),(3.4,1.42,1.50,.30),(7.4,1.08,1.14,.5),(11.4,1.70,1.78,.24),(15.0,1.12,1.18,.48),(17.6,1.0,1.06,.5)]
def shot(t):
    i=max(k for k,s in enumerate(shots) if t>=s[0]); s=shots[i]; e=shots[i+1][0] if i+1<len(shots) else DUR
    k=(t-s[0])/(e-s[0]); return s[1]+(s[2]-s[1])*k, s[3], t-s[0]
def glass(img,box,r,tint=.06):
    x0,y0,x1,y1=[int(v) for v in box]; w,h=x1-x0,y1-y0
    sh=Image.new("L",(w+120,h+120),0); ImageDraw.Draw(sh).rounded_rectangle([60,74,60+w,74+h],r,fill=150)
    img.paste((0,0,0),(x0-60,y0-60),sh.filter(ImageFilter.GaussianBlur(26)))
    c=img.crop((x0-40,y0-40,x1+40,y1+40)).filter(ImageFilter.GaussianBlur(24)).crop((40,40,40+w,40+h))
    a=np.asarray(c).astype(np.float32)*1.1+255*tint
    a+=36*np.linspace(1,0,h)[:,None,None]**3
    m=Image.new("L",(w,h),0); ImageDraw.Draw(m).rounded_rectangle([0,0,w-1,h-1],r,fill=255)
    img.paste(Image.fromarray(np.clip(a,0,255).astype(np.uint8)),(x0,y0),m)
    d=ImageDraw.Draw(img,"RGBA"); d.rounded_rectangle([x0,y0,x1-1,y1-1],r,outline=(255,255,255,90),width=2)
    d.rounded_rectangle([x0+3,y0+3,x1-4,y1-4],r-3,outline=(255,255,255,28),width=1)
def T(d,x,y,t,f,fill,sp=0,anchor="l"):
    w=sum(d.textlength(c,font=f) for c in t)+sp*(len(t)-1)
    if anchor=="m": x-=w/2
    if anchor=="r": x-=w
    for c in t: d.text((x,y),c,font=f,fill=fill); x+=d.textlength(c,font=f)+sp
    return w
def tw(d,t,f,sp=0): return sum(d.textlength(c,font=f) for c in t)+sp*(len(t)-1)
def fadein(t,a,b,dur=.45): return eo((t-a)/dur)*(1-eo((t-(b-dur*0.8))/(dur*0.8))) if b else eo((t-a)/dur)
M=84
chips=[(3.6,7.2,"SOUND","Bollywood · 90s · 2000s · Ghazal"),
       (7.6,11.2,"FOR","Private evenings · Cafés · Weddings"),
       (11.6,14.9,"JUST","a voice & an acoustic guitar."),
       (15.2,17.4,"BASED IN","Indore · Mumbai")]
for n in range(N):
    t=n/FPS
    raw=dec.stdout.read(VW*VH)
    if len(raw)<VW*VH: break
    g=np.frombuffer(raw,np.uint8).reshape(VH,VW)
    z,cyr,_=shot(t)
    cw,ch=VW/z,VH/z; cx=VW*.48; cy=VH*cyr
    x0=min(max(cx-cw/2,0),VW-cw); y0=min(max(cy-ch/2,0),VH-ch)
    fr=Image.fromarray(g).resize((W,VHo),Image.BILINEAR,box=(x0,y0,x0+cw,y0+ch))
    v=LUT[np.asarray(fr)].astype(np.float32)
    canvas=np.empty((H,W,3),np.float32); canvas[:]=BG
    # end card: darken + blur video
    endk=eio((t-17.6)/0.8)
    canvas[VY:VY+VHo]=np.array(BG)+(v-np.array(BG))*FADE*(1-0.55*endk)
    canvas+=GRAIN[n%6]
    img=Image.fromarray(np.clip(canvas,0,255).astype(np.uint8))
    if endk>0: img=Image.blend(img,img.filter(ImageFilter.GaussianBlur(22)),endk)
    d=ImageDraw.Draw(img)
    # logo chip always
    glass(img,(M-6,150,M+220,222),36); d=ImageDraw.Draw(img)
    T(d,M+22,158,"suyash",U(600,40),CREAM,-1.6); d.text((M+22+tw(d,"suyash",U(600,40),-1.6)+2,158),".",font=U(600,40),fill=OR)
    T(d,W-M,176,"SUYASH.LIVE",MO(22),MUT,3,"r")
    # HOOK 0-3.4
    if t<3.6:
        a=fadein(t,0.1,3.5,.5); 
        if a>0:
            ov=Image.new("RGBA",(W,H),(0,0,0,0)); o=ImageDraw.Draw(ov); A=int(255*a); dy=int(30*(1-a))
            o.ellipse([M,286+dy,M+12,298+dy],fill=OR+(A,)); T(o,M+26,280+dy,"LIVE · UNPLUGGED · FOR HIRE",MO(22),MUT+(A,),3.3)
            T(o,M-4,318+dy,"imagine this",U(400,112),CREAM+(A,),-112*.045)
            a2=fadein(t,0.7,3.5,.5); T(o,M,440+int(24*(1-a2)),"at your evening.",SI(72),OR+(int(255*a2),))
            img.paste(ov,(0,0),ov); d=ImageDraw.Draw(img)
    # chips
    for s,e,k,v_ in chips:
        a=fadein(t,s,e,.45)
        if a<=0: continue
        f=U(500,40) if k!="JUST" else SI(50)
        wv=tw(d,v_,f); wk=tw(d,k,MO(20),3)
        bw=int(max(wv,wk)+96); bx=M; by=int(1250+40*(1-a))
        layer=img.copy(); glass(layer,(bx,by,bx+bw,by+140),32)
        lo_=ImageDraw.Draw(layer); lo_.ellipse([bx+40,by+36,bx+50,by+46],fill=OR)
        T(lo_,bx+62,by+30,k,MO(20),MUT,3); T(lo_,bx+40,by+62 if k!="JUST" else by+60,v_,f,CREAM)
        img=Image.blend(img,layer,a); d=ImageDraw.Draw(img)
    # END CARD 17.6+
    if t>=17.6:
        a=eo((t-17.9)/0.6)
        if a>0:
            layer=img.copy(); cy0=int(560+50*(1-a)); cx0=M-10; cx1=W-M+10
            glass(layer,(cx0,cy0,cx1,cy0+760),48,.07); o=ImageDraw.Draw(layer)
            X=cx0+56; Y=cy0+60
            o.ellipse([X,Y+8,X+12,Y+20],fill=OR); T(o,X+26,Y+2,"BOOKINGS OPEN",MO(22),CREAM,3.3)
            T(o,X-4,Y+56,"book a live",U(400,104),CREAM,-104*.04)
            T(o,X-4,Y+160,"evening",U(400,104),CREAM,-104*.04)
            T(o,X,Y+290,"for evenings that deserve a soundtrack.",SI(46),OR)
            o.line([(X,Y+378),(cx1-56,Y+378)],fill=(239,230,219),width=1)
            T(o,X,Y+410,"WHATSAPP / CALL",MO(20),MUT,3); T(o,X,Y+440,"+91 91655 53087",U(500,52),CREAM,-.5)
            T(o,X,Y+530,"INSTAGRAM",MO(20),MUT,3); T(o,X,Y+560,"@_suyashgoswami",U(500,40),CREAM)
            img=Image.blend(img,layer,a); d=ImageDraw.Draw(img)
        b=eo((t-18.5)/0.5)
        if b>0:
            layer=img.copy(); o=ImageDraw.Draw(layer); by=1400+int(30*(1-b))
            o.rounded_rectangle([M,by,W-M,by+104],52,fill=OR)
            o.ellipse([M+46,by+47,M+58,by+59],fill=INK); T(o,M+80,by+34,"ENQUIRE ON WHATSAPP",U(700,32),INK,2.4)
            ax=W-M-80; ay=by+52; o.line([(ax,ay),(ax+38,ay)],fill=INK,width=4); o.line([(ax+24,ay-14),(ax+38,ay),(ax+24,ay+14)],fill=INK,width=4)
            T(o,W//2,by+136,"or book at suyash.live",SI(44),CREAM,0,"m")
            img=Image.blend(img,layer,b)
    enc.stdin.write(img.tobytes())
    if n%90==0: print(n,file=sys.stderr)
enc.stdin.close(); enc.wait()
