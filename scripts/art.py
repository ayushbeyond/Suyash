import sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

THEME = sys.argv[1] if len(sys.argv) > 1 else "dark"
TW, TH = 1080, 1440; PW, PH = TW * 3, TH
FD = "/home/claude/fonts/"
URB4 = FD + "fontsource-urbanist-5.3.0/package/files/urbanist-latin-400-normal.woff"
URB6 = FD + "fontsource-urbanist-5.3.0/package/files/urbanist-latin-600-normal.woff"
MONO = FD + "fontsource-dm-mono-5.3.0/package/files/dm-mono-latin-400-normal.woff"
SER = FD + "fontsource-instrument-serif-5.3.0/package/files/instrument-serif-latin-400-italic.woff"
F = lambda p, s: ImageFont.truetype(p, s)
OR = (232, 105, 42)
if THEME == "dark":
    BGC = (17, 13, 10); WORD = (238, 230, 220); ACC = OR; TXT = (238, 230, 220); MUT = (150, 138, 128); BTN_T = (17, 13, 10)
else:
    BGC = (226, 98, 36); WORD = (20, 14, 10); ACC = (20, 14, 10); TXT = (20, 14, 10); MUT = (70, 32, 12); BTN_T = (238, 230, 220)

rng = np.random.default_rng(4)
X = np.linspace(-1, 1, PW)[None, :]; Y = np.linspace(-1, 1, PH)[:, None]

# ---------- background: paper-like base + spotlight + beam ----------
base = np.ones((PH, PW, 3), np.float32) * np.array(BGC, np.float32)
spot = np.exp(-((X * 1.7) ** 2 + ((Y + .05) * 1.15) ** 2) * 1.6)[..., None]
if THEME == "dark":
    base += spot * np.array([70, 58, 48])
    beam = np.clip(1 - np.abs(X) / (0.10 + (Y + 1) * 0.16), 0, 1) ** 2 * np.clip((0.4 - Y) / 1.4, 0, 1)
    base += beam[..., None] * np.array([40, 36, 32])
else:
    base += spot * np.array([22, 14, 6]); base *= (1 - .18 * np.clip(np.sqrt(X**2*.5 + Y**2) - .5, 0, 1))[..., None]
canvas = Image.fromarray(np.clip(base, 0, 255).astype(np.uint8))

# ---------- giant name behind him ----------
wordL = Image.new("L", (PW, PH), 0); dw = ImageDraw.Draw(wordL)
size = 900
fw = F(URB4, size)
while fw.getlength("suyash") > PW - 150: size -= 10; fw = F(URB4, size)
tw = fw.getlength("suyash"); bb = fw.getbbox("suyash")
wx = (PW - tw) / 2 - bb[0]; wy = 300 - bb[1]
dw.text((wx, wy), "suyash", font=fw, fill=255)
word_alpha = 0.94 if THEME == "dark" else 1.0
canvas.paste(Image.new("RGB", (PW, PH), WORD), (0, 0), wordL.point(lambda v: int(v * word_alpha)))

# ---------- him (real 4K cutout) in front ----------
cut = Image.open("cutout_full.png")
alpha = cut.split()[3]
bbox = alpha.point(lambda v: 255 if v > 40 else 0).getbbox()
cut = cut.crop(bbox)
target_h = 1520
sc = target_h / cut.height
cut = cut.resize((int(cut.width * sc), target_h), Image.LANCZOS)
rgb = np.asarray(cut.convert("RGB")).astype(np.float32); a = np.asarray(cut.split()[3]).astype(np.float32) / 255
# B&W, punchy
yv = rgb[..., 0] * .3 + rgb[..., 1] * .59 + rgb[..., 2] * .11
yv = np.clip((yv / 255 - .5) * 1.25 + .52, 0, 1) ** 1.05 * 255
tone = np.stack([yv + 4, yv + 1, yv - 4], -1)
# fade legs out toward the bottom
h, w = a.shape; fy = np.linspace(0, 1, h)[:, None]
a = a * np.clip((0.86 - fy) / 0.24, 0, 1) ** 1.3
person = Image.fromarray(np.clip(tone, 0, 255).astype(np.uint8)); pa = Image.fromarray((a * 255).astype(np.uint8))
cx = PW // 2 - w // 2 + 20; cy = PH - target_h + 230
# soft shadow for depth
sh = pa.filter(ImageFilter.GaussianBlur(40)).point(lambda v: int(v * (.65 if THEME == "dark" else .45)))
canvas.paste((0, 0, 0), (cx + 30, cy + 20), sh)
canvas.paste(person, (cx, cy), pa)

# ---------- grain over everything ----------
arr = np.asarray(canvas).astype(np.float32) + rng.normal(0, 6 if THEME == "dark" else 7, (PH, PW, 1))
canvas = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8))
d = ImageDraw.Draw(canvas)

def tr(x, y, t, f, fill, sp=6):
    for c in t: d.text((x, y), c, font=f, fill=fill); x += f.getlength(c) + sp
    return x
def twd(t, f, sp=6): return sum(f.getlength(c) for c in t) + sp * (len(t) - 1)

# top rail
fm = F(MONO, 27)
tr(64, 70, "SINGER  ·  GUITARIST", fm, TXT, 6)
s = "INDORE  ·  MUMBAI"; tr(PW - 64 - twd(s, fm), 70, s, fm, TXT, 6)
d.line((64, 128, PW - 64, 128), fill=MUT, width=1)

# surname in serif, bottom-left
fs = F(SER, 230)
d.text((60, PH - 360), "goswami", font=fs, fill=ACC)
dx = 60 + fs.getlength("goswami") + 6
d.ellipse((dx, PH - 165, dx + 30, PH - 135), fill=ACC)

# centre bottom: genres
s = "BOLLYWOOD  ·  90s  ·  2000s  ·  GHAZAL  ·  SUFI"; f = F(MONO, 24)
tr(TW + (TW - twd(s, f)) / 2, PH - 78, s, f, TXT if THEME == "dark" else (20, 14, 10), 4)

# right bottom: line + CTA
x0 = 2 * TW + 120
d.text((x0, PH - 400), "some songs are", font=F(SER, 66), fill=TXT)
d.text((x0, PH - 330), "meant to be felt.", font=F(SER, 66), fill=TXT)
bw, bh = 330, 92; bx, by = x0, PH - 210
d.rounded_rectangle((bx, by, bx + bw, by + bh), 46, fill=ACC)
fb = F(URB6, 38); t = "Book now"
d.text((bx + 42, by + 22), t, font=fb, fill=BTN_T)
ax = bx + 42 + fb.getlength(t) + 24; ay = by + bh // 2 + 2
for seg in [((ax, ay), (ax + 42, ay)), ((ax + 27, ay - 15), (ax + 43, ay)), ((ax + 27, ay + 15), (ax + 43, ay))]:
    d.line(seg, fill=BTN_T, width=5)
tr(bx + bw + 34, by + 30, "SUYASH.LIVE", F(MONO, 28), TXT, 6)

out = f"art_{THEME}"
canvas.save(out + "_full.jpg", quality=95)
for i in range(3):
    canvas.crop((i * TW, 0, (i + 1) * TW, TH)).save(f"{out}_{i + 1}.jpg", quality=96)
row = Image.new("RGB", (PW + 8, PH), (10, 12, 16))
for i in range(3): row.paste(Image.open(f"{out}_{i + 1}.jpg"), (i * (TW + 4), 0))
row.resize((row.width // 3, row.height // 3), Image.LANCZOS).save(out + "_preview.jpg", quality=90)
print("ok", size, cut.size)
