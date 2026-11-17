from lib import *
M=84; S09=UP+"2ed75674-009_DYfRK-vz6Vm.mp4"
CUT=5.4; NOW_SS=0.2; NOW_LEN=13.9; DUR=CUT+NOW_LEN
a1=fade(lufs_norm(aload(S09,37.0,CUT+.04)),.06,.04)
a2=fade(lufs_norm(aload(S83,NOW_SS,NOW_LEN,"0:2")),.01,.05)
write_mix([(a1,0),(a2,CUT)],DUR,"then_now2.wav",1.6)
enc=encoder("Reel_2014_vs_2026_v3.mp4","then_now2.wav")
d1=Dec(S09,37.0,CUT,"crop=720:414:0:431,scale=1080:621:flags=bicubic",1080,621)
CLOSE=TM+"crop=1900:3378:0:300,scale=1080:1920:flags=lanczos"
WIDE=TM+"crop=1300:2311:0:1000,scale=1080:1920:flags=lanczos"
SWITCH=2.6   # seconds into NOW where we cut close -> wide (same take, sync kept)
P17=UP+"2c7c416b-13003417_1920_1080_30fps.mp4"
CUTS=[(5.0,5.8,5.0),(9.4,10.2,7.6)]
px=[Dec(P17,ps,e-s_,"crop=405:720:1250:0,scale=1080:1920:flags=lanczos") for s_,e,ps in CUTS]
dc=Dec(S83,NOW_SS,SWITCH,CLOSE); dw=Dec(S83,NOW_SS+SWITCH,NOW_LEN-SWITCH,WIDE)
def native(d,y,txt,size=66,a=1.0):
    f=U(700,size); w=tw(txt,f); x=(W-w)/2
    for dx,dy in ((0,3),(0,4)): T(d,x+dx,y+dy,txt,f,(0,0,0,int(110*a)))
    T(d,x,y,txt,f,(255,255,255,int(255*a)))
def grade_now(f):
    f=f.astype(np.float32); l=f.mean(-1,keepdims=True)
    f=l+(f-l)*0.72                                  # calm the purple
    f=f*np.array([1.08,0.97,0.9])                   # warm skin
    f=np.clip((f-16)*1.12,0,255)                    # deeper blacks, contrast
    return f
rng=np.random.default_rng(9)
for n in range(int(DUR*FPS)):
    t=n/FPS
    if t<CUT:
        fr=d1.read().astype(np.float32)
        l=fr.mean(-1,keepdims=True); fr=l+(fr-l)*0.8; fr=fr*np.array([1.04,1.0,.93])
        # old phone: chroma bleed, noise, soft
        fr[...,0]=np.roll(fr[...,0],2,1); fr[...,2]=np.roll(fr[...,2],-2,1)
        fr=cv2.GaussianBlur(fr,(0,0),0.8)+rng.normal(0,9,(621,1080,1))
        canvas=np.zeros((H,W,3),np.float32); y0=(H-621)//2-40; canvas[y0:y0+621]=fr
        img=Image.fromarray(np.clip(canvas,0,255).astype(np.uint8)); d=ImageDraw.Draw(img,"RGBA")
        T(d,W-60,y0+621-58,"2014",MO(30,500),(255,236,170,220),2,"r")       # camcorder date stamp
        native(d,y0-190,"how it started",62); native(d,y0-110,"2014",56,.9)
    else:
        u=t-CUT
        fr=dc.read() if u<SWITCH else dw.read()
        cut=None
        for ci,(s_,e,ps) in enumerate(CUTS):
            if s_<=u<e: cut=ci
        z=1+0.035*((u if u<SWITCH else u-SWITCH)/ (SWITCH if u<SWITCH else NOW_LEN-SWITCH)); cw,ch=W/z,H/z
        im=Image.fromarray(fr).resize((W,H),Image.BILINEAR,box=((W-cw)/2,(H-ch)/2,(W+cw)/2,(H+ch)/2))
        v=grade_now(np.asarray(im))
        if cut is not None:
            cf=px[cut].read().astype(np.float32); lum=(cf[...,0]*.3+cf[...,1]*.59+cf[...,2]*.11)[...,None]; b=np.clip((lum-28)*1.45,0,255); v=np.clip(b*np.array([0.9,0.36,1.3]),0,255)
        v=v+GRAIN[n%6]*0.7
        if u<0.08: v=v*0.2+255*0.8
        img=Image.fromarray(np.clip(v,0,255).astype(np.uint8)); d=ImageDraw.Draw(img,"RGBA")
        if u<3.2:
            a=1-eo((u-2.7)/.5); native(d,1150,"how it's going",62,a); native(d,1230,"2026",56,.9*a)
        if u>NOW_LEN-3.0:
            a=eo((u-(NOW_LEN-3.0))/.6); f=U(600,112)
            w=tw("suyash",f,-112*.04); x=(W-w-30)/2
            T(d,x,1010,"suyash",f,(255,255,255,int(255*a)),-112*.04); d.ellipse([x+w+8,1010+92,x+w+30,1010+114],fill=OR+(int(255*a),))
            native(d,1170,"@suyashislive  ·  DM for bookings",36,a)
    enc.stdin.write(img.convert("RGB").tobytes())
enc.stdin.close(); enc.wait()
