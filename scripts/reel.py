import json, math, subprocess, sys
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H, FPS = 1080, 1920, 30
DUR = 16.0
NF = int(DUR * FPS)
BG = (18, 13, 10); ORANGE = (232, 105, 42); CREAM = (239, 230, 219); MUT = (147, 131, 122)
FD = "/home/claude/fonts/"
URB4 = FD + "fontsource-urbanist-5.3.0/package/files/urbanist-latin-400-normal.woff"
URB5 = FD + "fontsource-urbanist-5.3.0/package/files/urbanist-latin-500-normal.woff"
MONO = FD + "fontsource-dm-mono-5.3.0/package/files/dm-mono-latin-400-normal.woff"
SER = FD + "fontsource-instrument-serif-5.3.0/package/files/instrument-serif-latin-400-italic.woff"
F = lambda p, s: ImageFont.truetype(p, s)

def ease(x):
    x = min(max(x, 0), 1); return 4 * x**3 if x < .5 else 1 - (-2 * x + 2)**3 / 2
def eout(x):
    x = min(max(x, 0), 1); return 1 - (1 - x)**3

# ---------- assets ----------
page = Image.open("page.png").convert("RGB")           # 780 wide, 2x
header = Image.open("header.png").convert("RGB").resize((780, 152), Image.LANCZOS)
offs = json.load(open("offs.json"))
PAGE_H_CSS = page.height / 2
VIEW_CSS = 844
maxs = PAGE_H_CSS - VIEW_CSS

# phone geometry
SCR_W = 700; SCALE = SCR_W / 780
SCR_H = int(VIEW_CSS * 2 * SCALE)                      # 1515
PX, PY = (W - SCR_W) // 2, 300
pageS = page.resize((SCR_W, int(page.height * SCALE)), Image.LANCZOS)
headS = header.resize((SCR_W, int(header.height * SCALE)), Image.LANCZOS)
pageA = np.asarray(pageS)

# scroll stops (css px) and timing inside phase B
stops = [0, offs["#np"] - 40, offs["#artist"] + 560, offs["#live"] + 980, offs["#sessions"] + 430,
         offs["#people"] + 640, offs["#connect"] - 20, maxs]
stops = [min(max(s, 0), maxs) for s in stops]
B0, B1 = 3.0, 11.6
seg = (B1 - B0 - 1.25) / (len(stops) - 1)
def scroll_at(t):
    u = t - B0 - 1.25
    if u <= 0: return stops[0]
    i = min(int(u // seg), len(stops) - 2); k = (u - i * seg) / seg
    k = ease(min(k / 0.6, 1))                           # move in 60% of the slot, then dwell
    return stops[i] + (stops[i + 1] - stops[i]) * k

# rounded mask for the screen
def rmask(w, h, r):
    m = Image.new("L", (w, h), 0); ImageDraw.Draw(m).rounded_rectangle((0, 0, w - 1, h - 1), r, fill=255); return m
SCR_MASK = np.asarray(rmask(SCR_W, SCR_H, 64)).astype(np.float32)[..., None] / 255

# static phone scene background (glow + bezel + shadow)
def phone_bg():
    im = Image.new("RGB", (W, H), BG)
    glow = Image.new("L", (W, H), 0); g = ImageDraw.Draw(glow)
    g.ellipse((PX - 260, PY + 200, PX + SCR_W + 260, PY + SCR_H - 100), fill=120)
    glow = glow.filter(ImageFilter.GaussianBlur(160))
    im = Image.composite(Image.new("RGB", (W, H), (120, 52, 20)), im, glow)
    sh = Image.new("L", (W, H), 0); ImageDraw.Draw(sh).rounded_rectangle((PX - 14, PY + 30, PX + SCR_W + 14, PY + SCR_H + 60), 84, fill=200)
    sh = sh.filter(ImageFilter.GaussianBlur(40)); im = Image.composite(Image.new("RGB", (W, H), (0, 0, 0)), im, sh)
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((PX - 18, PY - 18, PX + SCR_W + 18, PY + SCR_H + 18), 82, fill=(26, 22, 20), outline=(70, 60, 54), width=3)
    return np.asarray(im).astype(np.float32)
PHONE_BG = phone_bg()

def text_layer(items):
    """items: list of (text, font, color, (cx, y), alpha, tracking). returns RGBA np float"""
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    for txt, fnt, col, (cx, y), a, tr in items:
        if a <= 0: continue
        wds = [fnt.getlength(c) for c in txt]; tw = sum(wds) + tr * (len(txt) - 1)
        x = cx - tw / 2 if cx is not None else 80
        for c, w in zip(txt, wds):
            d.text((x, y), c, font=fnt, fill=col + (int(255 * a),)); x += w + tr
    return np.asarray(im).astype(np.float32)

def over(base, layer):
    a = layer[..., 3:4] / 255; base[:] = base * (1 - a) + layer[..., :3] * a

f_eye = F(MONO, 30); f_big = F(URB4, 250); f_dom = F(URB5, 128); f_mid = F(URB4, 92); f_ser = F(SER, 64); f_small = F(MONO, 28)

# ---------- phase A video (his Ohlio set) ----------
cap = cv2.VideoCapture("/home/claude/site/build/media/hero-ohlio.mp4")
cap.set(cv2.CAP_PROP_POS_MSEC, 16000)
A_FRAMES = []
for i in range(int(3.4 * FPS)):
    ok, fr = cap.read()
    A_FRAMES.append(cv2.cvtColor(fr, cv2.COLOR_BGR2RGB) if ok else A_FRAMES[-1])
yy = np.linspace(0, 1, H)[:, None, None].astype(np.float32)
A_GRAD = np.clip((yy - 0.38) / 0.5, 0, 1) ** 1.2 * 0.92

enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                        "-i", "audio.wav", "-map", "0:v", "-map", "1:a", "-c:v", "libx264", "-preset", "slow", "-crf", "18",
                        "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "256k", "-shortest", "-movflags", "+faststart", sys.argv[1]],
                       stdin=subprocess.PIPE)
rng = np.random.default_rng(3)
GRAIN = [rng.normal(0, 3.2, (H, W, 1)).astype(np.float32) for _ in range(6)]

for fi in range(NF):
    t = fi / FPS
    if t < 3.25:  # ---- A: live footage + "it's live."
        fr = A_FRAMES[min(fi, len(A_FRAMES) - 1)].astype(np.float32)
        z = 1.0 + 0.04 * t / 3.25
        M = np.float32([[z, 0, -(z - 1) * W / 2], [0, z, -(z - 1) * H * 0.4]])
        fr = cv2.warpAffine(fr, M, (W, H))
        f = fr * (1 - A_GRAD) + np.array(BG, np.float32) * A_GRAD
        k1 = eout((t - 0.25) / 0.5); k2 = eout((t - 0.55) / 0.6); k3 = eout((t - 1.5) / 0.6)
        items = [("SUYASH GOSWAMI", f_eye, ORANGE, (None, 1150 + 20 * (1 - k1)), k1, 6),
                 ("it's live", f_big, CREAM, (None, 1195 + 40 * (1 - k2)), k2, -4),
                 ("suyash.live", f_dom, ORANGE, (None, 1490 + 30 * (1 - k3)), k3, -2)]
        lay = text_layer(items); over(f, lay)
        if k2 > 0:   # orange dot after "it's live"
            tw = sum(f_big.getlength(c) for c in "it's live") - 4 * 8
            cv2.circle(f, (int(80 + tw + 34), int(1195 + 40 * (1 - k2) + 205)), int(20 * k2), ORANGE, -1, lineType=cv2.LINE_AA)
        out_k = ease((t - 2.95) / 0.3); f = f * (1 - out_k) + np.array(BG, np.float32) * out_k
    elif t < 11.9:  # ---- B: phone scroll through the site
        f = PHONE_BG.copy()
        s = scroll_at(t); y0 = int(s * 2 * SCALE)
        crop = pageA[y0:y0 + SCR_H].astype(np.float32)
        if crop.shape[0] < SCR_H: crop = np.pad(crop, ((0, SCR_H - crop.shape[0]), (0, 0), (0, 0)), constant_values=18)
        if s > 120:
            hh = np.asarray(headS).astype(np.float32); crop[:hh.shape[0]] = hh
        reg = f[PY:PY + SCR_H, PX:PX + SCR_W]
        f[PY:PY + SCR_H, PX:PX + SCR_W] = reg * (1 - SCR_MASK) + crop * SCR_MASK
        kin = eout((t - 3.25) / 0.6)
        lab = [("NOW LIVE  ·  SUYASH.LIVE", f_small, ORANGE, (W / 2, 175), kin, 6)]
        over(f, text_layer(lab))
        # entrance: slide up + fade
        if kin < 1:
            sh = int(120 * (1 - kin)); f = np.roll(f, sh, axis=0) if sh else f
            f = f * kin + np.array(BG, np.float32) * (1 - kin)
        if t > 11.6: f = f * (1 - ease((t - 11.6) / 0.3)) + np.array(BG, np.float32) * ease((t - 11.6) / 0.3)
    elif t < 13.9:  # ---- C: booking CTA
        f = np.empty((H, W, 3), np.float32); f[:] = BG
        k1 = eout((t - 11.95) / 0.5); k2 = eout((t - 12.2) / 0.5); k3 = eout((t - 12.5) / 0.5)
        items = [("BOOK A LIVE EVENING", f_eye, ORANGE, (W / 2, 690 + 20 * (1 - k1)), k1, 6),
                 ("weddings · sangeet", f_mid, CREAM, (W / 2, 760 + 30 * (1 - k2)), k2, -2),
                 ("house concerts · cafés", f_mid, CREAM, (W / 2, 865 + 30 * (1 - k2)), k2, -2),
                 ("suyash.live", f_dom, ORANGE, (W / 2, 1040 + 30 * (1 - k3)), k3, -2),
                 ("LINK IN BIO", f_small, MUT, (W / 2, 1210), k3, 8)]
        over(f, text_layer(items))
        out_k = ease((t - 13.6) / 0.3); f = f * (1 - out_k) + np.array(BG, np.float32) * out_k
    else:  # ---- D: credit end card
        f = np.empty((H, W, 3), np.float32); f[:] = (13, 9, 7)
        k1 = eout((t - 13.95) / 0.6); k2 = eout((t - 14.3) / 0.7)
        items = [("website crafted & designed by", f_ser, CREAM, (W / 2, 830 + 20 * (1 - k1)), k1, 0),
                 ("thebeyondbranding.com", F(URB5, 80), ORANGE, (W / 2, 930 + 30 * (1 - k2)), k2, -1)]
        over(f, text_layer(items))
        lk = ease((t - 14.6) / 0.6)
        if lk > 0:
            cv2.line(f, (int(W / 2 - 230 * lk), 1085), (int(W / 2 + 230 * lk), 1085), CREAM, 2, lineType=cv2.LINE_AA)
        fo = ease((t - 15.5) / 0.5); f = f * (1 - fo)
    f = f + GRAIN[fi % 6]
    enc.stdin.write(np.clip(f, 0, 255).astype(np.uint8).tobytes())
enc.stdin.close(); enc.wait()
print("done")
