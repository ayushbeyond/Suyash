import sys; sys.argv=[sys.argv[0]]
from lib import *
CW,CH=1080,1350; M=84
def hq(t,box):
    fr=[cv2.imread(f"/home/claude/dp/hq_{t}_{i}.png",cv2.IMREAD_UNCHANGED)[...,::-1].astype(np.float32)/65535 for i in (2,3,4)]
    img=np.median(np.stack(fr),0); x0,y0,w,h=box; c=img[y0:y0+h,x0:x0+w]
    c=cv2.resize(c,(CW,CH),interpolation=cv2.INTER_LANCZOS4); bl=cv2.GaussianBlur(c,(0,0),1.3); c=np.clip(c+0.45*(c-bl),0,1)
    return mono((c*255).astype(np.uint8))
def photo(f,box,kind):
    im=cv2.imread(UP+f)[...,::-1]; x0,y0,w,h=box; c=im[y0:y0+h,x0:x0+w]; c=cv2.resize(c,(CW,CH),interpolation=cv2.INTER_LANCZOS4)
    c=cv2.fastNlMeansDenoisingColored(np.ascontiguousarray(c),None,3,3,7,21).astype(np.float32)
    bl=cv2.GaussianBlur(c,(0,0),1.3); c=np.clip(c+0.4*(c-bl),0,255)
    if kind=="mono": return mono(c.astype(np.uint8))
    l=c.mean(-1,keepdims=True); return np.clip(l+(c-l)*.92,0,255)
yy=np.arange(CH)[:,None,None]
def finish(arr,i,n,line,big=None):
    g=np.clip(0.45+ (CH-yy)/700,0,1); arr=BG+(arr-BG)*(1-np.clip((yy-820)/530,0,1)**1.2*0.72)
    arr=arr+np.random.default_rng(i).normal(0,4,(CH,CW,1))
    img=Image.fromarray(np.clip(arr,0,255).astype(np.uint8)); d=ImageDraw.Draw(img,"RGBA")
    if big:
        T(d,M-6,CH-330,big,U(500,112),CREAM,-112*.045); T(d,M,CH-196,line,SI(56),OR)
    else:
        T(d,M,CH-150,line,SI(58),CREAM)
    T(d,M,CH-72,f"{i:02d} / {n:02d}",MO(22,500),OR,4); T(d,CW-M,CH-72,"@SUYASHISLIVE",MO(22,500),MUT,4,"r")
    return img
N=7; slides=[]
slides.append(finish(photo("f4908353-image.png",(154,640,1359,1699),"mono"),1,N,"swipe for the whole evening","a night on stage."))
slides.append(finish(photo("edec14b1-image.png",(154,420,1359,1699),"col"),2,N,"the light changes."))
slides.append(finish(hq("1.0",(560,1000,816,1020)),3,N,"the song doesn't."))
slides.append(finish(photo("0599fba6-image.jpg",(24,150,1018,1272),"col"),4,N,"eyes on the room."))
slides.append(finish(hq("46.0",(100,780,1280,1600)),5,N,"the part where it gets loud."))
slides.append(finish(hq("2.5",(300,960,1080,1350)),6,N,"and the quiet after."))
# CTA slide
base=hq("7.0",(100,1000,1280,1600)); im=Image.fromarray(np.clip(base,0,255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(22))
arr=np.asarray(im).astype(np.float32)*0.45+BG*0.55; img=Image.fromarray(arr.clip(0,255).astype(np.uint8))
glass(img,(M-10,300,CW-M+10,1030),46,.06,24,.8); d=ImageDraw.Draw(img,"RGBA"); X=M+46; Y=356
d.ellipse([X,Y+8,X+12,Y+20],fill=OR); T(d,X+26,Y+2,"BOOKINGS OPEN",MO(22,500),CREAM,4)
T(d,X-4,Y+56,"book a live",U(400,100),CREAM,-100*.04); T(d,X-4,Y+156,"evening.",U(500,100),CREAM,-100*.04)
T(d,X,Y+290,"weddings · private events · live venues",SI(44),OR)
d.line([(X,Y+370),(CW-M-46,Y+370)],fill=(239,230,219,120),width=1)
T(d,X,Y+404,"DM",MO(20),MUT,3); T(d,X+120,Y+396,"@suyashislive",U(500,38),CREAM)
T(d,X,Y+468,"WEB",MO(20),MUT,3); T(d,X+120,Y+460,"suyash.live",U(500,38),CREAM)
T(d,X,Y+532,"BASED",MO(20),MUT,3); T(d,X+120,Y+524,"Indore · available across India",U(500,38),CREAM)
d.rounded_rectangle([M,1090,M+420,1190],50,fill=OR); d.ellipse([M+44,1134,M+56,1146],fill=INK); T(d,M+80,1120,"DM FOR BOOKINGS",U(700,30),INK,2.4)
T(d,M,CH-72,f"{N:02d} / {N:02d}",MO(22,500),OR,4)
slides.append(img)
for i,s in enumerate(slides,1): s.convert("RGB").save(f"carousel/Carousel_{i:02d}.jpg",quality=96)
pv=Image.new("RGB",(7*270+6*6,338),"white")
for i,s in enumerate(slides): pv.paste(s.resize((270,338),Image.LANCZOS),(i*276,0))
pv.save("carousel/preview.jpg")
