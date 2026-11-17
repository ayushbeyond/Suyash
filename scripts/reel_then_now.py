from lib import *
DUR=14.0; CUT=5.2; M=84
S09=UP+"2ed75674-009_DYfRK-vz6Vm.mp4"
# audio
a1=fade(lufs_norm(aload(S09,37.0,CUT+0.05)),.05,.04)
a2=fade(lufs_norm(aload(S82,40.0,DUR-CUT,"0:2")),.01,.05)
write_mix([(a1,0),(a2,CUT)],DUR,"then_now.wav")
enc=encoder("Reel_2014_vs_2026.mp4","then_now.wav")
d1=Dec(S09,37.0,CUT,"crop=720:414:0:431,scale=900:518:flags=lanczos",900,518)
d2=Dec(S82,40.0,DUR-CUT,TM+"crop=1070:1902:300:640,scale=1080:1920:flags=lanczos")
yy=np.arange(H)[:,None,None]; TOPG=np.clip(0.3+yy/900,0,1)**1.3
for n in range(int(DUR*FPS)):
    t=n/FPS
    if t<CUT:
        fr=d1.read(); v=warm(fr,.55)
        # old-phone look: slight blur + vignette, framed card
        im=Image.fromarray(np.clip(v,0,255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(0.6))
        canvas=Image.fromarray(np.full((H,W,3),BG,np.uint8))
        # blurred fill background from same frame
        bgf=im.resize((W,int(W*518/900))).resize((W,H)).filter(ImageFilter.GaussianBlur(40))
        bgf=Image.fromarray((np.asarray(bgf).astype(np.float32)*0.28+BG*0.6).clip(0,255).astype(np.uint8)); canvas=bgf
        z=1+0.04*(t/CUT); fw,fh=900,518
        fimg=im.resize((int(fw*z),int(fh*z)),Image.BICUBIC).crop((int(fw*(z-1)/2),int(fh*(z-1)/2),int(fw*(z-1)/2)+fw,int(fh*(z-1)/2)+fh))
        mk=Image.new("L",(fw,fh),0); ImageDraw.Draw(mk).rounded_rectangle([0,0,fw-1,fh-1],28,fill=255)
        X0,Y0=(W-fw)//2,690
        canvas.paste(fimg,(X0,Y0),mk); ImageDraw.Draw(canvas,"RGBA").rounded_rectangle([X0,Y0,X0+fw-1,Y0+fh-1],28,outline=(255,255,255,70),width=2)
        arr=np.asarray(canvas).astype(np.float32)+GRAIN[n%6]*1.6
        img=Image.fromarray(np.clip(arr,0,255).astype(np.uint8))
        d=ImageDraw.Draw(img,"RGBA")
        # REC stamp
        if int(t*2)%2==0: d.ellipse([X0+28,Y0+30,X0+44,Y0+46],fill=(232,60,42))
        T(d,X0+56,Y0+26,"REC  2014",MO(24,500),CREAM,3)
        a=eo((t-.1)/.45); A=int(255*a); dy=int(28*(1-a))
        T(d,M,380+dy,"THEN",MO(24,500),OR+(A,),5)
        T(d,M-8,416+dy,"2014.",U(500,170),CREAM+(A,),-170*.045)
        a2=eo((t-.7)/.45); T(d,M,1250+int(20*(1-a2)),"a small room, a friend,",SI(56),CREAM+(int(255*a2),))
        T(d,M,1320+int(20*(1-a2)),"and one song.",SI(56),CREAM+(int(255*a2),))
    else:
        u=t-CUT; fr=d2.read(); z=1.0+0.05*(u/(DUR-CUT)); cw,ch=W/z,H/z
        im=Image.fromarray(fr).resize((W,H),Image.BILINEAR,box=((W-cw)/2,(H-ch)/2,(W+cw)/2,(H+ch)/2))
        v=mono(np.asarray(im)); arr=BG+(v-BG)*TOPG
        flash=max(0,1-u/0.18); arr=arr*(1-flash)+255*flash*0.85
        arr+=GRAIN[n%6]; img=Image.fromarray(np.clip(arr,0,255).astype(np.uint8)); d=ImageDraw.Draw(img,"RGBA")
        a=eo((u-.15)/.4); A=int(255*a); dy=int(28*(1-a))
        T(d,M,380+dy,"NOW",MO(24,500),OR+(A,),5)
        w=T(d,M-8,416+dy,"2026",U(500,170),CREAM+(A,),-170*.045); T(d,M-8+w,416+dy,".",U(500,170),OR+(A,))
        a2=eo((u-1.0)/.45); T(d,M,620+int(20*(1-a2)),"same voice. bigger rooms.",SI(56),CREAM+(int(255*a2),))
        if u>5.6:
            a3=eo((u-5.6)/.5); layer=img.copy(); f=U(500,40); txt="the room changed. the feeling didn't."
            bw=int(tw(txt,SI(44))+90); bx=(W-bw)//2; glass(layer,(bx,1110,bx+bw,1190),40)
            T(ImageDraw.Draw(layer),W//2,1124,txt,SI(44),CREAM,0,"m"); img=Image.blend(img,layer,a3)
    chip(img)
    enc.stdin.write(img.convert("RGB").tobytes())
enc.stdin.close(); enc.wait(); d1.close(); d2.close()
