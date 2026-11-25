"""Boards for the ten v9 designs (1600 x 1200) + two overviews. Usage: python3 src/render/v9_board.py <render_root> <out_dir>"""
import sys, os, textwrap
os.environ.setdefault('CRESCENT', '1'); os.environ.setdefault('PINCH', '1')
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from PIL import Image, ImageDraw, ImageFont
import v9_concepts as V
R, OUT = sys.argv[1], sys.argv[2]; os.makedirs(OUT, exist_ok=True)
F = lambda s, b=False: ImageFont.truetype(f'/usr/share/fonts/truetype/dejavu/DejaVuSans{"-Bold" if b else ""}.ttf', s)
BG, INK, SUB = (238, 236, 231), (26, 26, 28), (100, 100, 102)
def crop(p, pad=(60, 80)):
    im = Image.open(p).convert('RGB'); W, H = im.size; return im.crop((pad[0], pad[1], W - pad[0], H - pad[1]))
def fit(im, w, h):
    s = min(w / im.width, h / im.height); return im.resize((int(im.width * s), int(im.height * s)), Image.LANCZOS)
def hexrgb(h): return tuple(int(h[i:i + 2], 16) for i in (1, 3, 5))
def paste(im, src, box, pad=(60, 80)):
    x, y, w, h = box; p = fit(crop(src, pad), w, h); im.paste(p, (x + (w - p.width) // 2, y + (h - p.height) // 2))
order = list(V.CONCEPTS)
for n, k in enumerate(order, 1):
    c = V.CONCEPTS[k]; b = f'{R}/v9_{k}'
    im = Image.new('RGB', (1600, 1200), BG); d = ImageDraw.Draw(im)
    paste(im, f'{b}/v7_front.png', (20, 20, 500, 760)); paste(im, f'{b}/v7_back.png', (530, 20, 500, 760))
    for i, (v, lab, pad) in enumerate((('open', 'open', (40, 220)), ('edge', 'thumb crescent', (120, 160)), ('pinch', 'pinch zone', (120, 160)))):
        paste(im, f'{b}/v7_{v}.png', (20 + i * 340, 800, 330, 360), pad); d.text((26 + i * 340, 1164), lab, fill=SUB, font=F(15))
    x = 1070; d.text((x, 30), f'{n:02d}', fill=SUB, font=F(24, True)); d.text((x, 60), c['name'], fill=INK, font=F(56, True))
    y = 136
    for line in textwrap.wrap(c['ref'], 40): d.text((x, y), line, fill=SUB, font=F(17)); y += 24
    y += 14
    for line in textwrap.wrap(c['idea'], 42): d.text((x, y), line, fill=INK, font=F(18)); y += 25
    y += 18; d.text((x, y), 'COLOURS · Bambu PETG HF', fill=INK, font=F(16, True)); y += 30
    jobs = {}
    for key, lab in (('cover', 'cover'), ('tray', 'tray'), ('sleeve', 'hinge sleeve'), ('acc1', 'accent'), ('acc2', 'accent')):
        if key in c: jobs.setdefault(c[key], []); (lab not in jobs[c[key]]) and jobs[c[key]].append(lab)
    for col, labs in jobs.items():
        d.rounded_rectangle([x, y, x + 30, y + 30], 6, fill=hexrgb(V.C[col]), outline=(120, 120, 120))
        d.text((x + 42, y + 5), f'{V.NAMES[col]}  ·  {" + ".join(labs)}', fill=INK, font=F(17)); y += 38
    nf = len({c[q] for q in ('cover', 'tray', 'sleeve', 'acc1', 'acc2') if q in c})
    d.text((x, y + 2), f'{nf} filament{"s" if nf > 1 else ""}' + ('  ·  initials engraved' if c['mono'] == 'engrave' else ''), fill=SUB, font=F(16)); y += 40
    for title, key in (('FRONT', 'front'), ('BACK', 'back')):
        d.text((x, y), title, fill=INK, font=F(16, True)); y += 26
        for line in textwrap.wrap(c[key], 42): d.text((x, y), line, fill=INK, font=F(17)); y += 23
        y += 10
    d.text((x, 1140), 'continuous-curvature corners · R4.5 edges · crescent', fill=SUB, font=F(14))
    d.text((x, 1162), 'pinch zone · sealed magnets · 65 × 13.5 × 88', fill=SUB, font=F(14))
    im.save(f'{OUT}/{n:02d}_{k}.png')
for half, keys in (('A', order[:5]), ('B', order[5:])):
    im = Image.new('RGB', (1600, 1200), BG); d = ImageDraw.Draw(im)
    d.text((30, 20), f'Rollie Book v9 · ten designs ({"1–5" if half == "A" else "6–10"})', fill=INK, font=F(36, True))
    d.text((30, 68), 'form, texture and restraint · front (top) and back (bottom)', fill=SUB, font=F(19))
    for i, k in enumerate(keys):
        x0 = 20 + i * 314
        paste(im, f'{R}/v9_{k}/v7_front.png', (x0, 110, 300, 480)); paste(im, f'{R}/v9_{k}/v7_back.png', (x0, 600, 300, 480))
        d.text((x0 + 6, 1110), f'{order.index(k) + 1:02d} {V.CONCEPTS[k]["name"]}', fill=INK, font=F(24, True))
    im.save(f'{OUT}/00_overview_{half}.png')
print('boards written')
