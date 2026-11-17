import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

TW, TH = 1080, 1440
PW, PH = TW * 3, TH
BG = np.array([13, 11, 9], np.float32)
OR = (232, 105, 42); CR = (240, 233, 224); MU = (165, 155, 146)
FD = "/home/claude/fonts/"
URB4 = FD + "fontsource-urbanist-5.3.0/package/files/urbanist-latin-400-normal.woff"
URB5 = FD + "fontsource-urbanist-5.3.0/package/files/urbanist-latin-500-normal.woff"
URB6 = FD + "fontsource-urbanist-5.3.0/package/files/urbanist-latin-600-normal.woff"
MONO = FD + "fontsource-dm-mono-5.3.0/package/files/dm-mono-latin-400-normal.woff"
SER = FD + "fontsource-instrument-serif-5.3.0/package/files/instrument-serif-latin-400-italic.woff"
F = lambda p, s: ImageFont.truetype(p, s)

src = Image.open("c1782_48.jpg").convert("RGB")          # real 4K frame, 2160x3840
SW, SH = src.size

def mono(a):
    y = a[..., 0] * .3 + a[..., 1] * .59 + a[..., 2] * .11
    y = np.clip((y / 255 - .5) * 1.16 + .5, 0, 1) ** 1.1
    return np.stack([y * 255 + 3, y * 251 + 1.5, y * 243], -1)

# ---- background: the same frame, huge + blurred, so light and haze flow across all three tiles
bg = src.resize((PW, int(SH * PW / SW)), Image.LANCZOS)
by = int(bg.height * 0.06)
bg = bg.crop((0, by, PW, by + PH)).filter(ImageFilter.GaussianBlur(60))
bgA = mono(np.asarray(bg).astype(np.float32)) * 0.55

# ---- the sharp photo, centred, covering the middle tile and a little of each side
sc = TW / SW
ph = src.resize((int(SW * sc), int(SH * sc)), Image.LANCZOS)
py0 = int(ph.height * 0.045)
ph = ph.crop((0, py0, ph.width, py0 + PH))
phA = mono(np.asarray(ph).astype(np.float32))
pw = ph.width; px = TW
canvas = bgA.copy()
feather = 150
xs = np.arange(pw)
mask = np.minimum(np.clip(xs / 70, 0, 1), np.clip((pw - 1 - xs) / 14, 0, 1)) ** 1.2
canvas[:, px:px + pw] = canvas[:, px:px + pw] * (1 - mask[None, :, None]) + phA * mask[None, :, None]

# ---- shading: darker toward the outer edges (for text) + bottom fade, all continuous
X = np.linspace(0, 1, PW)[None, :, None]; Y = np.linspace(0, 1, PH)[:, None, None]
edge = np.clip(np.abs(X - .5) * 2 - .28, 0, 1) ** 1.2 * .78
bottom = np.clip((Y - .66) / .34, 0, 1) ** 1.3 * .88
top = np.clip((.11 - Y) / .11, 0, 1) ** .8 * .85
m = np.clip(edge + bottom + top, 0, .95)
canvas = canvas * (1 - m) + BG * m
canvas += np.random.default_rng(7).normal(0, 4.2, (PH, PW, 1))
img = Image.fromarray(np.clip(canvas, 0, 255).astype(np.uint8))
d = ImageDraw.Draw(img)

def tr(x, y, t, f, fill, sp=6):
    for c in t: d.text((x, y), c, font=f, fill=fill); x += f.getlength(c) + sp
    return x
def twidth(t, f, sp=6): return sum(f.getlength(c) for c in t) + sp * (len(t) - 1)

# shared top bar across the panorama
for i, lab in enumerate(["SUYASH GOSWAMI", "LIVE AT OHLIO, INDORE", "NOW BOOKING"]):
    x0 = i * TW
    tr(x0 + 64, 64, f"0{i + 1}", F(MONO, 28), OR, 4); tr(x0 + 128, 64, lab, F(MONO, 28), CR, 6)
d.ellipse((PW - 64 - 26, 66, PW - 64, 92), fill=OR)

# LEFT tile — identity
fb = F(URB4, 176)
d.text((60, 820), "suyash", font=fb, fill=CR)
d.text((60, 978), "goswami", font=fb, fill=CR)
dx = 60 + fb.getlength("goswami") + 10; d.ellipse((dx, 1118, dx + 28, 1146), fill=OR)
d.text((66, 1200), "some songs are meant to be felt.", font=F(SER, 50), fill=OR)
tr(66, 1300, "LIVE ACOUSTIC VOCALIST", F(MONO, 26), MU, 7)

# CENTRE tile — genre line, low and quiet
g = "BOLLYWOOD · 90s · 2000s · GHAZAL"
f = F(MONO, 26); tr(TW + (TW - twidth(g, f, 6)) / 2, 1300, g, f, MU, 6)

# RIGHT tile — offer + CTA
x0 = 2 * TW + 64
fr = F(URB4, 96)
for i, ln in enumerate(["voice & guitar,", "for evenings", "that deserve", "a soundtrack."]):
    d.text((x0, 640 + i * 108), ln, font=fr, fill=CR)
tr(x0 + 4, 1110, "INDORE  ·  MUMBAI", F(MONO, 30), OR, 8)
# Book now button
bx, by_, bw, bh = x0, 1186, 360, 96
d.rounded_rectangle((bx, by_, bx + bw, by_ + bh), 48, fill=OR)
fbtn = F(URB6, 40); t = "Book now"
d.text((bx + 44, by_ + 22), t, font=fbtn, fill=(18, 13, 10))
ax = bx + 44 + fbtn.getlength(t) + 26; ay = by_ + bh // 2 + 2
d.line((ax, ay, ax + 46, ay), fill=(18, 13, 10), width=5)
d.line((ax + 30, ay - 16, ax + 47, ay), fill=(18, 13, 10), width=5); d.line((ax + 30, ay + 16, ax + 47, ay), fill=(18, 13, 10), width=5)
tr(bx + bw + 40, by_ + 32, "SUYASH.LIVE", F(MONO, 28), CR, 7)

img.save("pinned_panorama_full.jpg", quality=95)
names = ["cover_1_left.jpg", "cover_2_centre.jpg", "cover_3_right.jpg"]
for i, n in enumerate(names):
    img.crop((i * TW, 0, (i + 1) * TW, TH)).save(n, quality=96)
# profile-row preview with Instagram's thin gaps
row = Image.new("RGB", (PW + 8, PH), (10, 12, 16))
for i, n in enumerate(names): row.paste(Image.open(n), (i * (TW + 4), 0))
row.resize((row.width // 3, row.height // 3), Image.LANCZOS).save("cover_row_preview.jpg", quality=90)
print("ok", ph.size, px)
