import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageChops
F="/home/claude/fonts/"
def U(w,s): return ImageFont.truetype(F+f"fontsource-urbanist-5.3.0/package/files/urbanist-latin-{w}-normal.woff",s)
def MO(w,s): return ImageFont.truetype(F+f"fontsource-dm-mono-5.3.0/package/files/dm-mono-latin-{w}-normal.woff",s)
def SI(s): return ImageFont.truetype(F+"fontsource-instrument-serif-5.3.0/package/files/instrument-serif-latin-400-italic.woff",s)
TW,TH=1080,1440; W,H=TW*3,TH
BG=np.array([18,13,10],np.float32); CREAM=(239,230,219); MUT=(185,168,152); OR=(232,105,42); INK=(36,26,20)
s=1.47
src=Image.open("clean_src.png").convert("L")
sw,sh=int(src.width*s),int(src.height*s)
a=np.asarray(src.resize((sw,sh),Image.LANCZOS).filter(ImageFilter.UnsharpMask(1.6,60,2))).astype(np.float32)/255
a=np.clip((a-0.04)/0.96,0,1)**1.12
ox=int(TW+(TW-(1240-525)*s)/2-525*s)+6
cv=np.zeros((H,W),np.float32); cv[0:sh,ox:ox+sw]=a[:, :W-ox]
xx=np.arange(W)[None,:].astype(np.float32); yy=np.arange(H)[:,None].astype(np.float32)
cv*=(np.clip((xx-ox)/420,0,1)*np.clip((ox+sw-xx)/420,0,1)*np.clip((sh-yy)/160,0,1))**1.4
d=np.sqrt(((xx-1.5*TW)/(W*0.62))**2+((yy-0.45*H)/(H*0.95))**2)
cv*=np.clip(1.15-d**1.8,0.18,1)*np.clip(0.35+yy/300,0,1)**1.2
hi=np.array([246,236,222],np.float32)
rgb=BG+(hi-BG)*cv[...,None]
# ambient orange glows (site accent) for the glass to refract
def glow(cx,cy,r,k):
    g=np.exp(-(((xx-cx)**2+(yy-cy)**2)/(2*r*r)))
    return g[...,None]*np.array([232,105,42],np.float32)*k
rgb+=glow(2*TW+760,1010,260,0.55)+glow(2*TW+260,1240,200,0.35)+glow(140,300,260,0.18)
rng=np.random.default_rng(7); rgb+=rng.normal(0,6.5,(H,W,1))
img=Image.fromarray(np.clip(rgb,0,255).astype(np.uint8)).convert("RGBA")

def glass(img,box,r,tint=0.07):
    x0,y0,x1,y1=box; w,h=x1-x0,y1-y0
    # shadow
    sh_=Image.new("RGBA",img.size,(0,0,0,0)); ImageDraw.Draw(sh_).rounded_rectangle([x0,y0+18,x1,y1+18],r,fill=(0,0,0,140))
    img=Image.alpha_composite(img,sh_.filter(ImageFilter.GaussianBlur(28)))
    pad=60; crop=img.crop((x0-pad,y0-pad,x1+pad,y1+pad)).convert("RGB")
    # lens: slight magnify + heavy blur + lift
    crop=crop.resize((int(crop.width*1.06),int(crop.height*1.06)),Image.LANCZOS)
    cx=(crop.width-(w+2*pad))//2; crop=crop.crop((cx,cx,cx+w+2*pad,cx+h+2*pad))
    bl=crop.filter(ImageFilter.GaussianBlur(26)).crop((pad,pad,pad+w,pad+h))
    arr=np.asarray(bl).astype(np.float32)
    arr=arr*1.12+255*tint
    gy=np.linspace(1,0,h)[:,None,None]; arr+=40*gy**3   # top specular
    m=Image.new("L",(w,h),0); ImageDraw.Draw(m).rounded_rectangle([0,0,w-1,h-1],r,fill=255)
    img.paste(Image.fromarray(np.clip(arr,0,255).astype(np.uint8)),(x0,y0),m)
    # rim: bright top-left -> faint bottom-right
    rim=Image.new("RGBA",(w,h),(0,0,0,0)); ImageDraw.Draw(rim).rounded_rectangle([0,0,w-1,h-1],r,outline=(255,255,255,255),width=2)
    gx=np.linspace(0,1,w)[None,:]; gyy=np.linspace(0,1,h)[:,None]
    al=(0.85-0.7*(gx*0.4+gyy*0.6)).clip(0.12,1)*np.asarray(rim)[...,3]/255*150
    ra=np.asarray(rim).copy(); ra[...,3]=al.astype(np.uint8)
    img.alpha_composite(Image.fromarray(ra),(x0,y0))
    # inner glow line
    il=Image.new("RGBA",(w,h),(0,0,0,0)); ImageDraw.Draw(il).rounded_rectangle([3,3,w-4,h-4],r-3,outline=(255,255,255,40),width=1)
    img.alpha_composite(il,(x0,y0))
    return img

def T(dr,x,y,t,f,fill,sp=0,anchor="l"):
    w=sum(dr.textlength(c,font=f) for c in t)+sp*(len(t)-1)
    if anchor=="r": x-=w
    if anchor=="m": x-=w/2
    for c in t: dr.text((x,y),c,font=f,fill=fill); x+=dr.textlength(c,font=f)+sp
    return w
M=96
# glass elements first
R=2*TW+M
img=glass(img,(R-36,330,2*TW+TW-M+36-0,1060),44)          # booking card
img=glass(img,(TW+TW//2-300,H-M-96,TW+TW//2+300,H-M),48)  # now-playing pill
img=glass(img,(M-4,M-22,M+250,M+52),37)                     # logo chip
dr=ImageDraw.Draw(img)
# folios
T(dr,M+26,M-6,"suyash",U(600,40),CREAM,-1.6); dr.text((M+26+dr.textlength("suyash",font=U(600,40))-8,M-6),".",font=U(600,40),fill=OR)
T(dr,M+176,M+6,"01/03",MO(400,18),MUT,1)
pass
T(dr,3*TW-M,M+4,"SUYASH.LIVE",MO(400,20),MUT,3,"r")
# LEFT tile — mirrors website hero
dr.ellipse([M,452,M+12,464],fill=OR)
T(dr,M+26,446,"SINGER · GUITARIST · LIVE FROM INDORE",MO(400,22),MUT,3.3)
f=U(400,232)
T(dr,M-10,500,"suyash",f,CREAM,-232*.045)
w=T(dr,M-10,705,"goswami",f,CREAM,-232*.045)
T(dr,M-10+w-4,705,".",f,OR)
T(dr,M,1000,"some songs are meant to be felt.",SI(58),OR,-0.5)
dr.multiline_text((M,1092),"Bollywood, the 90s and the 2000s,\nsung live with a voice and an acoustic guitar.",font=U(400,30),fill=MUT,spacing=12)
# CENTRE pill: now playing
cx0=TW+TW//2-300+40; cy=H-M-48
for i,hh in enumerate([16,30,22,36,18]): dr.rounded_rectangle([cx0+i*9,cy-hh//2,cx0+i*9+4,cy+hh//2],2,fill=OR)
T(dr,cx0+66,cy-30,"NOW PLAYING",MO(400,17),MUT,3)
T(dr,cx0+66,cy-8,"A live acoustic evening",U(500,30),CREAM,-0.6)
# RIGHT card
y=400
dr.ellipse([R,y+8,R+12,y+20],fill=OR); T(dr,R+26,y+2,"BOOKINGS OPEN",MO(400,22),CREAM,3.3)
T(dr,R,y+70,"book a live",U(400,104),CREAM,-104*.04)
w=T(dr,R,y+180,"evening",U(400,104),CREAM,-104*.04); T(dr,R+w+8,y+176,"♪" if False else "",U(400,104),OR)
T(dr,R,y+310,"for evenings that deserve a soundtrack.",SI(44),OR)
dr.line([(R,y+400),(3*TW-M,y+400)],fill=(239,230,219,60),width=1)
for i,(k,v) in enumerate([("SETS","Private evenings · Cafés · Weddings"),("SOUND","Bollywood · 90s · 2000s · Ghazal"),("CITIES","Indore · Mumbai")]):
    yy_=y+428+i*62; T(dr,R,yy_+6,k,MO(400,18),MUT,3); T(dr,R+150,yy_,v,U(500,28),CREAM)
# buttons like site .btn
by=1130; bh=76
dr.rounded_rectangle([R,by,R+330,by+bh],38,fill=OR)
dr.ellipse([R+34,by+bh//2-5,R+44,by+bh//2+5],fill=INK); T(dr,R+64,by+24,"BOOK NOW",U(700,26),INK,2.2)
ax=R+268; ay=by+bh//2
dr.line([(ax,ay),(ax+30,ay)],fill=INK,width=3); dr.line([(ax+19,ay-11),(ax+30,ay),(ax+19,ay+11)],fill=INK,width=3)
img=glass(img,(R+356,by,R+356+300,by+bh),38)
dr=ImageDraw.Draw(img)
dr.ellipse([R+356+32,by+bh//2-5,R+356+42,by+bh//2+5],fill=OR); T(dr,R+356+62,by+24,"SUYASH.LIVE",U(700,26),CREAM,2.2)
out=img.convert("RGB"); out.save("web_pano.jpg",quality=95)
for i in range(3): out.crop((i*TW,0,(i+1)*TW,TH)).save(f"web_pinned_{i+1}.jpg",quality=96)
g=4; pv=Image.new("RGB",(W+2*g,H),(255,255,255))
for i in range(3): pv.paste(out.crop((i*TW,0,(i+1)*TW,TH)),(i*(TW+g),0))
pv.resize((pv.width//3,pv.height//3),Image.LANCZOS).save("web_preview.jpg",quality=90)
