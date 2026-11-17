import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H = 1080, 1440
BG = (14, 11, 9); OR = (232, 105, 42); CR = (240, 233, 224); MU = (170, 160, 150)
FD = "/home/claude/fonts/"
URB4 = FD + "fontsource-urbanist-5.3.0/package/files/urbanist-latin-400-normal.woff"
URB5 = FD + "fontsource-urbanist-5.3.0/package/files/urbanist-latin-500-normal.woff"
MONO = FD + "fontsource-dm-mono-5.3.0/package/files/dm-mono-latin-400-normal.woff"
SER = FD + "fontsource-instrument-serif-5.3.0/package/files/instrument-serif-latin-400-italic.woff"
F = lambda p, s: ImageFont.truetype(p, s)
S = "/home/claude/site/stills/"; M = "/home/claude/site/build/media/"

def cover(path, cx=.5, cy=.5, zoom=1.0):
    im = Image.open(path).convert("RGB")
    sc = max(W / im.width, H / im.height) * zoom
    im = im.resize((round(im.width * sc), round(im.height * sc)), Image.LANCZOS)
    x = int(min(max(im.width * cx - W / 2, 0), im.width - W)); y = int(min(max(im.height * cy - H / 2, 0), im.height - H))
    return im.crop((x, y, x + W, y + H))

def mono_grade(im, contrast=1.18, lift=6):
    # rich warm black & white: one shared treatment for the whole set
    a = np.asarray(im).astype(np.float32) / 255
    y = a[..., 0] * .3 + a[..., 1] * .59 + a[..., 2] * .11
    y = np.clip((y - .5) * contrast + .5, 0, 1) ** 1.08
    rgb = np.stack([y * 1.0 + .012, y * .985 + .006, y * .955], -1) * 255 + lift * (1 - y[..., None])
    return Image.fromarray(np.clip(rgb, 0, 255).astype(np.uint8))

def finish(im, top=.0, bottom=.55):
    a = np.asarray(im).astype(np.float32)
    ys = np.linspace(0, 1, H)[:, None, None]
    m = np.clip((ys - bottom) / (1 - bottom), 0, 1) ** 1.25 * .93 + np.clip((top - ys) / max(top, 1e-6), 0, 1) * .6 if top else np.clip((ys - bottom) / (1 - bottom), 0, 1) ** 1.25 * .93
    a = a * (1 - m) + np.array(BG) * m
    xs = np.linspace(-1, 1, W)[None, :, None]; yv = np.linspace(-1, 1, H)[:, None, None]
    a *= 1 - .28 * np.clip(np.sqrt(xs ** 2 * .9 + yv ** 2 * .7) - .55, 0, 1)
    a += np.random.default_rng(2).normal(0, 4.5, (H, W, 1))
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))

def tracked(d, x, y, t, f, fill, tr=6):
    for c in t: d.text((x, y), c, font=f, fill=fill); x += f.getlength(c) + tr
    return x

def layout(im, num, label, big, small):
    d = ImageDraw.Draw(im)
    tracked(d, 64, 64, f"{num}", F(MONO, 30), OR, 4)
    tracked(d, 64 + 70, 64, label, F(MONO, 30), CR, 7)
    d.ellipse((W - 64 - 26, 66, W - 64, 92), fill=OR)
    fb = F(URB4, 168)
    lines = big.split("\n"); y = H - 150 - 150 * len(lines)
    for i, ln in enumerate(lines):
        d.text((56, y + i * 150), ln, font=fb, fill=CR)
        if i == len(lines) - 1:
            dx = 56 + fb.getlength(ln) + 8; d.ellipse((dx, y + i * 150 + 132, dx + 26, y + i * 150 + 158), fill=OR)
    d.text((64, H - 118), small, font=F(SER, 46), fill=OR)
    tracked(d, W - 64 - 300, H - 102, "SUYASH.LIVE", F(MONO, 26), MU, 7)
    d.line((64, H - 150, W - 64, H - 150), fill=(80, 70, 62), width=1)
    return im

p1 = finish(mono_grade(cover("/home/claude/faces/hi/home_321.jpg", cx=.5, cy=.36, zoom=1.0)))
layout(p1, "01", "THE VOICE", "suyash", "singer · guitarist · indore").save("pinned_1_the_voice.jpg", quality=95)

p2 = finish(mono_grade(cover(S + "02_ohlio_side_angle_4k.jpg", cx=.5, cy=.38, zoom=1.0)))
layout(p2, "02", "THE STAGE", "live at\nohlio", "bollywood · 90s · 2000s").save("pinned_2_the_stage.jpg", quality=95)

p3 = finish(mono_grade(cover(S + "07_ohlio_bw_singing_4k.jpg", cx=.5, cy=.36, zoom=1.0)))
layout(p3, "03", "YOUR EVENING", "book a\nnight", "weddings · private events").save("pinned_3_your_evening.jpg", quality=95)

# grid preview (how the pinned row reads on the profile)
row = Image.new("RGB", (W * 3 + 8, H), (12, 15, 20))
for i, f in enumerate(["pinned_1_the_voice.jpg", "pinned_2_the_stage.jpg", "pinned_3_your_evening.jpg"]):
    row.paste(Image.open(f), (i * (W + 4), 0))
row.resize((row.width // 3, row.height // 3), Image.LANCZOS).save("pinned_row_preview.jpg", quality=90)
print("ok")
