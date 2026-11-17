from lib import *
M=84
S05=UP+"b33060a0-005_De7SLggiXCi.mp4"; SRZ=UP+"e31bd15f-instabulkdownloader.com_DRZe_XDgg3E.mp4"
SEG=[("01","the bedroom.","where it started.",S05,37.0,"scale=1080:1920:flags=lanczos","warm",4.2,"0:a:0"),
     ("02","the mehfil.","harmonium & tabla, no mic.",SRZ,108.7,"scale=1080:1920:flags=lanczos","warm",4.4,"0:a:0"),
     ("03","the stage.","same voice, louder room.",S82,40.0,TM+"crop=1070:1902:300:640,scale=1080:1920:flags=lanczos","mono",6.4,"0:2")]
DUR=sum(s[7] for s in SEG)
aud=[];t0=0
for s in SEG: aud.append((fade(lufs_norm(aload(s[3],s[4],s[7]+.03,s[8])),.03,.04),t0)); t0+=s[7]
write_mix(aud,DUR,"rooms.wav")
enc=encoder("Reel_Same_Voice_Three_Rooms.mp4","rooms.wav")
yy=np.arange(H)[:,None,None]; TOPG=np.clip(0.32+yy/850,0,1)**1.3; TOPG2=np.clip(0.12+(yy-200)/900,0.12,1)**1.4
t0=0
for k,(num,title,sub,src,ss,vf,g,dur,st) in enumerate(SEG):
    dec=Dec(src,ss,dur,vf)
    for n in range(int(round(dur*FPS))):
        t=n/FPS; fr=dec.read(); z=1+0.05*t/dur; cw,ch=W/z,H/z
        im=Image.fromarray(fr).resize((W,H),Image.BILINEAR,box=((W-cw)/2,(H-ch)/2,(W+cw)/2,(H+ch)/2))
        v=mono(np.asarray(im)) if g=="mono" else warm(np.asarray(im))
        arr=BG+(v-BG)*(TOPG2 if k==1 else TOPG); flash=max(0,1-t/0.12)*(k>0); arr=arr*(1-flash)+255*flash*.6
        arr+=GRAIN[n%6]; img=Image.fromarray(np.clip(arr,0,255).astype(np.uint8)); d=ImageDraw.Draw(img,"RGBA")
        gt=t0+t
        if gt<2.6:   # hook
            a=eo((gt-.05)/.4)*(1-eo((gt-2.3)/.3)); A=int(255*a)
            T(d,M-6,1120,"same voice.",U(500,104),CREAM+(A,),-104*.045); T(d,M,1236,"three rooms.",SI(84),OR+(A,))
        a=eo((t-.1)/.35); A=int(255*a); dy=int(24*(1-a))
        T(d,M,390+dy,f"ROOM {num} / 03",MO(24,500),OR+(A,),5)
        w=T(d,M-6,426+dy,title[:-1],U(500,124),CREAM+(A,),-124*.045); T(d,M-6+w,426+dy,".",U(500,124),OR+(A,))
        a2=eo((t-.45)/.35); T(d,M,580+int(18*(1-a2)),sub,SI(54),CREAM+(int(255*a2),))
        # progress dots
        for i in range(3): d.rounded_rectangle([M+i*54,700,M+i*54+40,706],3,fill=(OR if i<=k else (239,230,219,70)))
        if k==2 and t>dur-2.4:
            a3=eo((t-(dur-2.4))/.45); layer=img.copy(); txt="yours could be next.  DM for bookings"
            f=U(500,38); bw=int(tw(txt,f)+100); bx=(W-bw)//2; glass(layer,(bx,1110,bx+bw,1190),40)
            q=ImageDraw.Draw(layer); q.ellipse([bx+40,1145,bx+52,1157],fill=OR); T(q,bx+66,1128,txt,f,CREAM); img=Image.blend(img,layer,a3)
        chip(img); enc.stdin.write(img.convert("RGB").tobytes())
    dec.close(); t0+=dur
enc.stdin.close(); enc.wait()
