from lib import *
M=84; T0,T1,X=23.0,30.5,0.5; L=T1-T0
VF=TM+"crop=1070:1902:300:640,scale=1080:1920:flags=lanczos"
main=aload(S82,T0,L,"0:2",True); pre=aload(S82,T0-X,X,"0:2",True)
n=int(X*SR); w=np.linspace(0,1,n)[:,None]
main[-n:]=main[-n:]*(1-w)+pre[:n]*w
g=10**(-16/20)/(np.sqrt(np.mean(main**2))+1e-9); main*=g
import soundfile as sf; sf.write("loop.wav",main,SR,subtype="PCM_24")
subprocess.run(["ffmpeg","-v","error","-y","-i","loop.wav","-af","volume=2dB,alimiter=limit=0.95","loop2.wav"])
enc=encoder("Reel_Perfect_Loop_Stage.mp4","loop2.wav")
dm=Dec(S82,T0,L,VF); dp=Dec(S82,T0-X,X,VF)
yy=np.arange(H)[:,None,None]; TOPG=np.clip(0.3+yy/850,0,1)**1.3
NF=int(L*FPS); NX=int(X*FPS)
for k in range(NF):
    t=k/FPS; fr=dm.read().astype(np.float32)
    if k>=NF-NX:
        j=k-(NF-NX); w=(j+1)/NX; fr=fr*(1-w)+dp.read().astype(np.float32)*w
    v=mono(fr.clip(0,255).astype(np.uint8)); arr=BG+(v-BG)*TOPG+GRAIN[k%6]
    img=Image.fromarray(np.clip(arr,0,255).astype(np.uint8)); d=ImageDraw.Draw(img,"RGBA")
    T(d,M,390,"LIVE · INDORE",MO(24,500),OR,5)
    T(d,M-4,426,"turn it up.",SI(96),CREAM)
    chip(img); enc.stdin.write(img.convert("RGB").tobytes())
enc.stdin.close(); enc.wait()
