import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

TW, TH = 720, 960   # 3:4 grid tile
BG = (18, 13, 10); OR = (232, 105, 42); CR = (239, 230, 219)
FD = "/home/claude/fonts/"
URB4 = FD + "fontsource-urbanist-5.3.0/package/files/urbanist-latin-400-normal.woff"
MONO = FD + "fontsource-dm-mono-5.3.0/package/files/dm-mono-latin-400-normal.woff"
SER = FD + "fontsource-instrument-serif-5.3.0/package/files/instrument-serif-latin-400-italic.woff"
F = lambda p, s: ImageFont.truetype(p, s)
S = "/home/claude/site/stills/"; M = "/home/claude/site/build/media/"; R = "/home/claude/reel/"

def cover(path, cx=0.5, cy=0.5, zoom=1.0):
    im = Image.open(path).convert("RGB")
    sc = max(TW / im.width, TH / im.height) * zoom
    im = im.resize((int(im.width * sc), int(im.height * sc)), Image.LANCZOS)
    x = int(min(max(im.width * cx - TW / 2, 0), im.width - TW)); y = int(min(max(im.height * cy - TH / 2, 0), im.height - TH))
    return im.crop((x, y, x + TW, y + TH))

def warm(im, s=0.10):  # one consistent warm grade for every tile
    a = np.asarray(im).astype(np.float32)
    g = a.mean(2, keepdims=True); a = g + (a - g) * 0.88
    a = a * np.array([1 + s * .5, 1, 1 - s]) ; a = (a / 255) ** 1.06 * 255
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))

def brand(im, label, title, serif=False):
    a = np.asarray(im).astype(np.float32)
    ys = np.linspace(0, 1, TH)[:, None, None]
    m = np.clip((ys - 0.45) / 0.55, 0, 1) ** 1.3 * 0.9
    a = a * (1 - m) + np.array(BG) * m
    im = Image.fromarray(a.astype(np.uint8)); d = ImageDraw.Draw(im)
    fm = F(MONO, 30); x = 48; nl = title.count("\n") + 1
    ly = TH - 150 - 74 * (nl - 1) - 62
    for c in label: d.text((x, ly), c, font=fm, fill=OR); x += fm.getlength(c) + 5
    ft = F(SER, 72) if serif else F(URB4, 70)
    lines = title.split("\n"); y = TH - 170 if len(lines) == 1 else TH - 205
    if len(lines) == 2:
        d.text((x - x + 46, TH - 175), "", font=ft)
    yy = TH - 160 - 72 * (len(lines) - 1) + (0 if len(lines) == 1 else 40)
    for i, ln in enumerate(lines):
        d.text((46, TH - 150 - 74 * (len(lines) - 1 - i)), ln, font=ft, fill=CR)
    d.ellipse((TW - 70, 46, TW - 46, 70), fill=OR)       # brand dot, every tile
    return im

tiles = []
# row 1 — launch
t = cover(R + "feed_01_cover.jpg", cy=0.55); tiles.append(t)                                   # carousel cover (already branded)
t = cover("reel_cover.jpg", cy=0.62); tiles.append(t)                                           # reel cover
tiles.append(brand(warm(cover(S + "01_ohlio_closeup_4k.jpg", cy=0.35)), "LIVE AT OHLIO · EP.01", "the room\nwent quiet."))
# row 2
tiles.append(brand(warm(cover(M + "jam-tabla-harmonium.jpg", cx=0.74, cy=0.5)), "GHAZAL SESSIONS", "gulon mein\nrang bhare", serif=True))
# quote tile
q = Image.new("RGB", (TW, TH), BG); dq = ImageDraw.Draw(q)
nap = Image.open(M + "note.jpg").convert("RGB"); nap = nap.resize((300, int(nap.height * 300 / nap.width))).rotate(-4, expand=True, fillcolor=BG)
q.paste(nap, (TW - 340, 60))
fm = F(MONO, 26); x = 48
for c in "LOVE NOTES": dq.text((x, 70), c, font=fm, fill=OR); x += fm.getlength(c) + 5
fq = F(SER, 64)
for i, ln in enumerate(["“thank you for", "making our evening", "very pleasant", "and soothing.”"]):
    dq.text((48, 470 + i * 74), ln, font=fq, fill=CR)
dq.ellipse((TW - 70, TH - 70, TW - 46, TH - 46), fill=OR)
tiles.append(q)
tiles.append(cover(R + "feed_03_book.jpg", cy=0.45))
# row 3
tiles.append(brand(warm(cover(S + "03_ohlio_front_4k.jpg", cy=0.45, zoom=1.15)), "LIVE AT OHLIO · EP.02", "one take.\none guitar."))
tiles.append(brand(cover(S + "06_ohlio_bw_beams_4k.jpg", cy=0.4), "LIVE AT OHLIO · EP.03", "under the\nlights."))
tiles.append(brand(warm(cover(S + "08_home_session.jpg", cy=0.4)), "AT HOME", "one lamp,\none guitar."))
# row 4
tiles.append(brand(warm(cover(S + "02_ohlio_side_angle_4k.jpg", cy=0.4)), "MID-SONG", "felt, not\nperformed."))
tiles.append(brand(warm(cover(M + "throwback-2014.jpg", cy=0.62)), "WHERE IT STARTED", "2014."))
tiles.append(brand(warm(cover(S + "13_ohlio_duo_wide.jpg", cx=0.55, cy=0.55)), "DUO NIGHTS", "two voices,\none stage."))
for i, t in enumerate(tiles):
    t.save(f"tile_{i:02d}.jpg", quality=90)

# highlight covers
def hl(name, kind):
    s = 240; im = Image.new("RGB", (s, s), BG); d = ImageDraw.Draw(im)
    if kind == "book":
        d.ellipse((0, 0, s - 1, s - 1), fill=OR); f = F(URB4, 64); w = f.getlength("book")
        d.text(((s - w) / 2, s / 2 - 42), "book", font=f, fill=BG)
    else:
        src = {"live": S + "01_ohlio_closeup_4k.jpg", "notes": M + "note.jpg", "sessions": M + "jam-tabla-harmonium.jpg", "venues": M + "portrait-bw.jpg"}[kind]
        p = Image.open(src).convert("RGB"); sc = max(s / p.width, s / p.height) * (1.0 if kind != "sessions" else 1.0)
        p = p.resize((int(p.width * sc) + 1, int(p.height * sc) + 1))
        cx = {"sessions": .74, "venues": .74}.get(kind, .5)
        x = int(min(max(p.width * cx - s / 2, 0), p.width - s)); y = int(max(0, p.height * .35 - s / 2)) if kind == "live" else int((p.height - s) / 2)
        im = warm(p.crop((x, y, x + s, y + s)))
    im.save(f"hl_{name}.jpg", quality=90)
for n, k in [("Book", "book"), ("Live", "live"), ("Love notes", "notes"), ("Sessions", "sessions"), ("Venues", "venues")]:
    hl(n.replace(" ", "_"), k)
# avatar
a = Image.open(M + "portrait-bw.jpg").convert("RGB"); s = a.height
a.crop((int(a.width * .75 - s * .32), 0, int(a.width * .75 + s * .32), int(s * .64))).resize((300, 300)).save("avatar.jpg", quality=90)
print("ok", len(tiles))
