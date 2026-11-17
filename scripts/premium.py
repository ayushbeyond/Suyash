import numpy as np, sys
from PIL import Image, ImageDraw, ImageFont, ImageFilter
F="/home/claude/fonts/"
CG=F+"fontsource-cormorant-garamond-5.3.0/package/files/cormorant-garamond-latin-%s.woff"
MR=F+"fontsource-manrope-5.3.0/package/files/manrope-latin-%s-normal.woff"
def cg(w,sz,it=False): return ImageFont.truetype(CG%(f"{w}-{'italic' if it else 'normal'}"),sz)
def mr(w,sz): return ImageFont.truetype(MR%w,sz)
TW,TH=1080,1440; W,H=TW*3,TH
CREAM=(239,230,219); DIM=(239,230,219,150); OR=(232,105,42)
s=float(sys.argv[1]) if len(sys.argv)>1 else 1.47
src=Image.open("/mnt/user-data/uploads/42d21f26-image.png").convert("L")
sw,sh=int(src.width*s),int(src.height*s)
img=src.resize((sw,sh),Image.LANCZOS).filter(ImageFilter.UnsharpMask(1.6,60,2))
a=np.asarray(img).astype(np.float32)/255
# tone: deeper blacks, soft highlights
a=np.clip((a-0.04)/0.96,0,1); a=a**1.12
# place: subject block (src x 525..1240) centred in middle tile
ox=int(TW+(TW-(1240-525)*s)/2-525*s)+6; oy=0
canvas=np.zeros((H,W),np.float32)
canvas[oy:oy+sh,max(ox,0):ox+sw]=a[:, max(-ox,0):][:, :min(sw,W-ox)]
# feather photo edges into black
xx=np.arange(W)[None,:].astype(np.float32); yy=np.arange(H)[:,None].astype(np.float32)
fl=np.clip((xx-ox)/420,0,1); fr=np.clip((ox+sw-xx)/420,0,1); fb=np.clip((oy+sh-yy)/160,0,1)
canvas*=(fl*fr*fb)**1.4
# cinematic vignette + darken text zones
cx,cy=1.5*TW,0.45*H
d=np.sqrt(((xx-cx)/(W*0.62))**2+((yy-cy)/(H*0.95))**2)
canvas*=np.clip(1.15-d**1.8,0.18,1)
canvas*=np.clip(0.35+yy/300,0,1)**1.2
# warm duotone: shadows #0d0a08, highlights cream
lo=np.array([10,8,7],np.float32); hi=np.array([246,236,222],np.float32)
rgb=lo+(hi-lo)*canvas[...,None]
rng=np.random.default_rng(7); rgb+=rng.normal(0,7,(H,W,1))
base=Image.fromarray(np.clip(rgb,0,255).astype(np.uint8)).convert("RGBA")
ov=Image.new("RGBA",(W,H),(0,0,0,0)); d=ImageDraw.Draw(ov)
def tr(x,y,t,f,fill,sp=0,anchor="l"):
    w=sum(d.textlength(c,font=f) for c in t)+sp*(len(t)-1)
    if anchor=="r": x-=w
    if anchor=="m": x-=w/2
    for c in t: d.text((x,y),c,font=f,fill=fill); x+=d.textlength(c,font=f)+sp
    return w
M=96
# folio marks on each tile
for i,lab in enumerate(["THE ARTIST","LIVE AT OHLIO","BOOKINGS"]):
    x0=i*TW
    tr(x0+M,M,f"0{i+1}",mr(600,22),OR,2)
    tr(x0+M+52,M,lab,mr(500,22),DIM,6)
    tr(x0+TW-M,M,"SUYASH.LIVE" if i==2 else "— / 03".replace("—",f"0{i+1}"),mr(500,22),DIM,6,"r")
# LEFT: name
f1=cg(300,250); f2=cg(300,250,True)
tr(M-8,430,"Suyash",f1,CREAM,-2)
tr(M+70,640,"Goswami",f2,CREAM,-2)
d.line([(M,960),(M+120,960)],fill=OR,width=3)
tr(M,1000,"VOCALIST  ·  ACOUSTIC GUITARIST",mr(500,26),CREAM,7)
tr(M,1050,"Bollywood, 90s, 2000s & Ghazal — sung live.",cg(400,40,True),DIM)
tr(M,H-M-22,"INDEPENDENT ARTIST",mr(500,20),(239,230,219,110),6)
# CENTRE: quiet caption
tr(TW+TW/2,H-M-22,"PHOTOGRAPHED LIVE AT OHLIO, INDORE",mr(500,20),(239,230,219,120),6,"m")
# RIGHT: line + CTA
R=2*TW+M
tr(R,430,"Some songs",cg(300,128,True),CREAM,-1)
tr(R,570,"are meant",cg(300,128,True),CREAM,-1)
tr(R,710,"to be felt.",cg(300,128,True),CREAM,-1)
d.line([(R,920),(R+120,920)],fill=OR,width=3)
tr(R,960,"PRIVATE EVENINGS  ·  CAFÉS  ·  WEDDINGS",mr(500,24),CREAM,6)
tr(R,1004,"Now booking — Indore & Mumbai",cg(400,40,True),DIM)
# pill
px,py,pw,ph=R,1120,330,84
d.rounded_rectangle([px,py,px+pw,py+ph],radius=42,outline=CREAM,width=2)
d.ellipse([px+34,py+36,px+46,py+48],fill=OR)
tr(px+68,py+28,"BOOK NOW",mr(600,26),CREAM,6)
ax=px+pw-62; ay=py+ph//2
d.line([(ax,ay),(ax+30,ay)],fill=CREAM,width=2); d.line([(ax+20,ay-10),(ax+30,ay),(ax+20,ay+10)],fill=CREAM,width=2)
tr(px+pw+40,py+29,"suyash.live",cg(400,34,True),CREAM)
out=Image.alpha_composite(base,ov).convert("RGB")
out.save("pano.jpg",quality=95)
for i in range(3): out.crop((i*TW,0,(i+1)*TW,TH)).save(f"pinned_{i+1}.jpg",quality=96)
# grid preview with gaps
g=4; pv=Image.new("RGB",(W+2*g,H),(255,255,255))
for i in range(3): pv.paste(out.crop((i*TW,0,(i+1)*TW,TH)),(i*(TW+g),0))
pv.resize((pv.width//3,pv.height//3),Image.LANCZOS).save("preview.jpg",quality=90)
print(ox,sw,sh)
