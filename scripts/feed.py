import json
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H = 1080, 1350
BG = (18, 13, 10); OR = (232, 105, 42); CR = (239, 230, 219); MU = (160, 144, 134)
FD = "/home/claude/fonts/"
URB4 = FD + "fontsource-urbanist-5.3.0/package/files/urbanist-latin-400-normal.woff"
URB5 = FD + "fontsource-urbanist-5.3.0/package/files/urbanist-latin-500-normal.woff"
MONO = FD + "fontsource-dm-mono-5.3.0/package/files/dm-mono-latin-400-normal.woff"
SER = FD + "fontsource-instrument-serif-5.3.0/package/files/instrument-serif-latin-400-italic.woff"
F = lambda p, s: ImageFont.truetype(p, s)
M = "/home/claude/site/build/media/"

def track(d, xy, txt, fnt, fill, tr=0, anchor_center=False):
    w = sum(fnt.getlength(c) for c in txt) + tr * (len(txt) - 1)
    x, y = xy
    if anchor_center: x = x - w / 2
    for c in txt:
        d.text((x, y), c, font=fnt, fill=fill); x += fnt.getlength(c) + tr
    return x

def grad(im, top_a, bot_a, start=0.0, side=None):
    a = np.zeros((H, W), np.float32)
    if side == "left":
        xs = np.linspace(0, 1, W)[None, :]
        a[:] = np.clip(1 - (xs - start) / 0.72, 0, 1) ** 1.1 * bot_a
    else:
        ys = np.linspace(0, 1, H)[:, None]
        a[:] = np.clip((ys - start) / (1 - start), 0, 1) ** 1.2 * (bot_a - top_a) + top_a
    m = Image.fromarray((a * 255).astype(np.uint8))
    return Image.composite(Image.new("RGB", (W, H), BG), im, m)

def grain(im, s=5):
    a = np.asarray(im).astype(np.float32) + np.random.default_rng(1).normal(0, s, (H, W, 1))
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))

def footer(d, n):
    track(d, (72, H - 92), "SUYASH.LIVE", F(MONO, 24), OR, 6)
    t = f"0{n} / 04"; f = F(MONO, 24)
    track(d, (W - 72 - sum(f.getlength(c) for c in t) - 6 * len(t), H - 92), t, f, MU, 6)

# ---------- 1. cover ----------
im = Image.open(M + "portrait-cafe.jpg").convert("RGB")
im = im.resize((W, int(im.height * W / im.width)), Image.LANCZOS).crop((0, 0, W, H))
im = grad(im, 0.0, 0.97, start=0.36)
d = ImageDraw.Draw(im)
track(d, (72, 820), "SUYASH GOSWAMI  ·  NEW WEBSITE", F(MONO, 28), OR, 6)
f = F(URB4, 210); d.text((64, 862), "it's live", font=f, fill=CR)
dx = 64 + f.getlength("it's live") + 10; d.ellipse((dx, 1052, dx + 34, 1086), fill=OR)
d.text((72, 1122), "suyash.live", font=F(URB5, 84), fill=OR)
track(d, (W - 72 - 250, 1158), "LINK IN BIO", F(MONO, 26), CR, 6)
grain(im).save("feed_01_cover.jpg", quality=95)

# ---------- 2. two phones ----------
page = Image.open("page.png").convert("RGB")      # 780w @2x mobile
offs = json.load(open("offs.json"))
def phone(scroll_css, w=380):
    sc = w / 780; h = int(844 * 2 * sc)
    crop = page.crop((0, int(scroll_css * 2), 780, int(scroll_css * 2) + 1688)).resize((w, h), Image.LANCZOS)
    m = Image.new("L", (w, h), 0); ImageDraw.Draw(m).rounded_rectangle((0, 0, w - 1, h - 1), 44, fill=255)
    body = Image.new("RGBA", (w + 24, h + 24), (0, 0, 0, 0)); bd = ImageDraw.Draw(body)
    bd.rounded_rectangle((0, 0, w + 23, h + 23), 54, fill=(26, 22, 20, 255), outline=(78, 66, 58, 255), width=3)
    body.paste(crop, (12, 12), m)
    return body
im = Image.new("RGB", (W, H), BG)
glow = Image.new("L", (W, H), 0); ImageDraw.Draw(glow).ellipse((120, 380, 960, 1200), fill=140)
im = Image.composite(Image.new("RGB", (W, H), (120, 52, 20)), im, glow.filter(ImageFilter.GaussianBlur(170)))
p1 = phone(0); p2 = phone(offs["#sessions"] + 380)
for p, (x, y, r) in [(p2, (575, 360, -4)), (p1, (150, 310, 4))]:
    pr = p.rotate(r, resample=Image.BICUBIC, expand=True)
    sh = Image.new("L", pr.size, 0); sh.paste(pr.split()[3]); sh = sh.filter(ImageFilter.GaussianBlur(30))
    im.paste((0, 0, 0), (x + 10, y + 40), sh.point(lambda v: int(v * .7)))
    im.paste(pr, (x, y), pr)
d = ImageDraw.Draw(im)
track(d, (72, 96), "THE NEW WEBSITE", F(MONO, 28), OR, 6)
d.text((70, 140), "every song, every stage,", font=F(URB4, 66), fill=CR)
d.text((70, 214), "one place.", font=F(URB4, 66), fill=CR)
footer(d, 2)
grain(im, 4).save("feed_02_website.jpg", quality=95)

# ---------- 3. book ----------
bw = Image.open(M + "portrait-bw.jpg").convert("RGB")       # 1672x941, subject right
s = H / bw.height; bw = bw.resize((int(bw.width * s), H), Image.LANCZOS)
x0 = int(bw.width * 0.75) - 880; x0 = max(0, min(x0, bw.width - W)); im = bw.crop((x0, 0, x0 + W, H))
im = grad(im, 0, 0.94, start=0.0, side="left")
im = grad(im, 0.0, 0.85, start=0.62)
d = ImageDraw.Draw(im)
track(d, (72, 200), "AVAILABLE FOR", F(MONO, 28), OR, 6)
d.text((70, 248), "book a live", font=F(URB4, 104), fill=CR)
d.text((70, 360), "evening.", font=F(URB4, 104), fill=CR)
y = 560
for item in ["Weddings & sangeet", "House concerts", "Cafés & venues", "Corporate evenings"]:
    d.ellipse((76, y + 22, 88, y + 34), fill=OR); d.text((112, y), item, font=F(URB4, 46), fill=CR); y += 78
d.text((72, 1000), "Bollywood · 90s · 2000s, live with voice & guitar", font=F(SER, 44), fill=OR)
d.text((72, 1080), "suyash.live", font=F(URB5, 72), fill=CR)
track(d, (72, 1172), "WHATSAPP +91 91655 53087", F(MONO, 26), MU, 4)
grain(im).save("feed_03_book.jpg", quality=95)

# ---------- 4. credit ----------
im = Image.new("RGB", (W, H), (13, 9, 7)); d = ImageDraw.Draw(im)
glow = Image.new("L", (W, H), 0); ImageDraw.Draw(glow).ellipse((200, 420, 880, 960), fill=90)
im = Image.composite(Image.new("RGB", (W, H), (110, 45, 16)), im, glow.filter(ImageFilter.GaussianBlur(160))); d = ImageDraw.Draw(im)
fs = F(SER, 64); t = "website crafted & designed by"
d.text(((W - fs.getlength(t)) / 2, 560), t, font=fs, fill=CR)
fb = F(URB5, 88); t2 = "thebeyondbranding.com"
d.text(((W - fb.getlength(t2)) / 2, 650), t2, font=fb, fill=OR)
d.line((W / 2 - 220, 790, W / 2 + 220, 790), fill=CR, width=2)
track(d, (W / 2, 830), "@THEBEYONDBRANDING", F(MONO, 28), MU, 6, anchor_center=True)
footer(d, 4)
grain(im, 4).save("feed_04_credit.jpg", quality=95)
print("ok")
