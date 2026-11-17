from lib import *
import sys
M=84; SRZ=UP+"e31bd15f-instabulkdownloader.com_DRZe_XDgg3E.mp4"; SS=102.0; DUR=20.0
ENHANCE=sys.argv[1]=="enh"
a=fade(lufs_norm(aload(SRZ,SS,DUR,"0:a:0",ENHANCE)),.15,.05)
write_mix([(a,0)],DUR,f"mehfil_{sys.argv[1]}.wav",1.5)
out=f"Reel_Mehfil_Ep01_{'enhanced' if ENHANCE else 'original'}_audio.mp4"
if not ENHANCE:   # reuse picture from enhanced render, only swap audio
    subprocess.run(["ffmpeg","-v","error","-y","-i","Reel_Mehfil_Ep01_enhanced_audio.mp4","-i","mehfil_orig.wav","-map","0:v","-map","1:a","-c:v","copy","-c:a","aac","-b:a","256k","-shortest",out]); sys.exit()
enc=encoder(out,f"mehfil_{sys.argv[1]}.wav")
dec=Dec(SRZ,SS,DUR,"scale=1080:1920:flags=lanczos")
yy=np.arange(H)[:,None,None]; TOPG=np.clip(0.12+(yy-200)/900,0.12,1)**1.4
# shot plan on one continuous take (sync kept): (start, zoom, cx, cy)
SHOTS=[(0,1.0,.5,.5),(4.2,1.42,.36,.46),(8.0,1.0,.5,.5),(11.5,1.38,.40,.70),(14.6,1.0,.5,.5)]
def shot(t):
    i=max(k for k,s in enumerate(SHOTS) if t>=s[0]); s=SHOTS[i]; e=SHOTS[i+1][0] if i+1<len(SHOTS) else DUR
    return s,(t-s[0])/(e-s[0])
for n in range(int(DUR*FPS)):
    t=n/FPS; fr=dec.read(); (st,z0,cx,cy),u=shot(t); z=z0*(1+0.035*u)
    cw,ch=W/z,H/z; x0=min(max(cx*W-cw/2,0),W-cw); y0=min(max(cy*H-ch/2,0),H-ch)
    im=Image.fromarray(fr).resize((W,H),Image.BICUBIC,box=(x0,y0,x0+cw,y0+ch))
    v=warm(np.asarray(im),.82); arr=BG+(v-BG)*(TOPG if z0<1.2 else np.clip(0.45+yy/1400,0,1))
    arr+=GRAIN[n%6]; img=Image.fromarray(np.clip(arr,0,255).astype(np.uint8)); d=ImageDraw.Draw(img,"RGBA")
    if t<4.1:
        a=eo((t-.05)/.4)*(1-eo((t-3.8)/.3)); A=int(255*a)
        T(d,M,390,"MEHFIL · EP. 01",MO(24,500),OR+(A,),5)
        T(d,M-4,424,"a harmonium,",SI(66),CREAM+(A,)); T(d,M-4,494,"a tabla,",SI(66),CREAM+(A,))
        a2=eo((t-1.2)/.4)*(1-eo((t-3.8)/.3)); T(d,M-4,564,"and an evening",SI(66),OR+(int(255*a2),)); T(d,M-4,634,"that didn't want to end.",SI(66),OR+(int(255*a2),))
    if 8.0<=t<11.4:
        a=eo((t-8.1)/.4)*(1-eo((t-11.1)/.3)); A=int(255*a)
        T(d,M,390,"LIVE · ONE TAKE",MO(24,500),CREAM+(A,),5)
    if t>=15.2:
        a=eo((t-15.3)/.5); layer=img.copy(); q=ImageDraw.Draw(layer)
        T(q,M-4,400,"bring the mehfil",U(500,96),CREAM,-96*.045); T(q,M-4,500,"home.",U(500,96),OR,-96*.045)
        txt="Private events · Anniversaries · DM for bookings"; f=U(500,34); bw=int(tw(txt,f)+100); bx=M
        glass(layer,(bx,640,bx+bw,712),36); q=ImageDraw.Draw(layer); q.ellipse([bx+38,671,bx+50,683],fill=OR); T(q,bx+64,655,txt,f,CREAM)
        img=Image.blend(img,layer,a)
    chip(img); enc.stdin.write(img.convert("RGB").tobytes())
enc.stdin.close(); enc.wait(); dec.close()
