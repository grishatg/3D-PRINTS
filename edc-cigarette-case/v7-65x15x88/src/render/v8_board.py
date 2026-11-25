"""Concept boards for the five v8 directions (1600 x 1200) + overview. Usage: python3 src/render/v8_board.py <render_root> <out_dir>"""
import sys, os, textwrap
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from PIL import Image, ImageDraw, ImageFont
import v8_concepts as V
R, OUT = sys.argv[1], sys.argv[2]; os.makedirs(OUT, exist_ok=True)
F = lambda s, b=False: ImageFont.truetype(f'/usr/share/fonts/truetype/dejavu/DejaVuSans{"-Bold" if b else ""}.ttf', s)
BG, INK, SUB = (238, 236, 231), (26, 26, 28), (96, 96, 98)
NAMES = dict(gray='Gray', darkgray='Dark Gray', black='Black', white='White', cream='Cream', peanut='Peanut Brown', orange='Orange', lake='Lake Blue')
def crop(p, pad=(60, 80)):
    im = Image.open(p).convert('RGB'); W, H = im.size; return im.crop((pad[0], pad[1], W - pad[0], H - pad[1]))
def fit(im, w, h):
    s = min(w / im.width, h / im.height); return im.resize((int(im.width * s), int(im.height * s)), Image.LANCZOS)
def hexrgb(h): return tuple(int(h[i:i + 2], 16) for i in (1, 3, 5))
order = list(V.CONCEPTS)
for n, k in enumerate(order, 1):
    c = V.CONCEPTS[k]; base = f'{R}/v8_{k}'
    im = Image.new('RGB', (1600, 1200), BG); d = ImageDraw.Draw(im)
    for i, v in enumerate(('front', 'back')):
        p = fit(crop(f'{base}/v7_{v}.png'), 520, 720); im.paste(p, (20 + i * 530 + (520 - p.width) // 2, 20 + (720 - p.height) // 2))
    p = fit(crop(f'{base}/v7_open.png', (40, 220)), 1060, 420); im.paste(p, (20 + (1060 - p.width) // 2, 760 + (420 - p.height) // 2))
    x = 1110; d.text((x, 34), f'0{n}', fill=SUB, font=F(26, True)); d.text((x, 66), c['name'], fill=INK, font=F(64, True))
    y = 150
    for line in textwrap.wrap(c['ref'], 34): d.text((x, y), line, fill=SUB, font=F(20)); y += 28
    y += 20; d.text((x, y), 'COLOURS · Bambu PETG HF', fill=INK, font=F(17, True)); y += 34
    roles = [('cover', 'Cover'), ('tray', 'Tray'), ('sleeve', 'Hinge sleeve')] + [(a, 'Accent') for a in ('acc1', 'acc2', 'acc3') if a in c]
    jobs = {}
    for key, lab in roles:
        jobs.setdefault(c[key], [])
        if lab.lower() not in jobs[c[key]]: jobs[c[key]].append(lab.lower())
    for col, labs in jobs.items():                     # one swatch per filament, all its jobs
        d.rounded_rectangle([x, y, x + 34, y + 34], 6, fill=hexrgb(V.C[col]), outline=(120, 120, 120))
        d.text((x + 48, y + 6), f'{NAMES[col]}  ·  {" + ".join(labs)}', fill=INK, font=F(19)); y += 44
    fil = sorted({c[k] for k in ('cover', 'tray', 'sleeve', 'acc1', 'acc2', 'acc3', 'mono') if k in c})
    d.text((x, y + 4), f'{len(fil)} filament{"s" if len(fil) > 1 else ""} in the AMS lite', fill=SUB, font=F(17)); y += 50
    for title, key in (('FRONT', 'front'), ('BACK', 'back')):
        d.text((x, y), title, fill=INK, font=F(17, True)); y += 28
        for line in textwrap.wrap(c[key], 38): d.text((x, y), line, fill=INK, font=F(18)); y += 25
        y += 14
    d.text((x, 1118), 'continuous-curvature corners · R4.5 edges', fill=SUB, font=F(16))
    d.text((x, 1142), 'sealed magnets · filament hinge · 65 × 13.5 × 88', fill=SUB, font=F(16))
    im.save(f'{OUT}/0{n}_{k}.png')
# overview
im = Image.new('RGB', (1600, 1200), BG); d = ImageDraw.Draw(im)
d.text((30, 22), 'Rollie Book v8 · five directions', fill=INK, font=F(40, True))
d.text((30, 76), 'same engineering platform · different CMF and patterns front and back', fill=SUB, font=F(20))
for n, k in enumerate(order):
    x0 = 20 + n * 314
    for j, v in enumerate(('front', 'back')):
        p = fit(crop(f'{R}/v8_{k}/v7_{v}.png'), 300, 470); im.paste(p, (x0 + (300 - p.width) // 2, 120 + j * 490 + (470 - p.height) // 2))
    d.text((x0 + 8, 1112), f'0{n + 1} {V.CONCEPTS[k]["name"]}', fill=INK, font=F(26, True))
im.save(f'{OUT}/00_overview.png'); print('boards written')
