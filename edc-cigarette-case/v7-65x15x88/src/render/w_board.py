"""Boards for the wood-PLA designs (1600 x 1200) + overview. Usage: python3 src/render/w_board.py <render_root> <out_dir> [wood_photo.png]"""
import sys, os, textwrap
os.environ.setdefault('CRESCENT', '1'); os.environ.setdefault('PINCH', '1'); os.environ.setdefault('INITIALS_POS', 'back'); os.environ.setdefault('PLATFORM', 'v10')
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from PIL import Image, ImageDraw, ImageFont
import w_concepts as W
R, OUT = sys.argv[1], sys.argv[2]; PHOTO = sys.argv[3] if len(sys.argv) > 3 else None; os.makedirs(OUT, exist_ok=True)
F = lambda s, b=False: ImageFont.truetype(f'/usr/share/fonts/truetype/dejavu/DejaVuSans{"-Bold" if b else ""}.ttf', s)
FD = os.path.join(os.path.dirname(__file__), '..', '..', 'fonts')
BG, INK, SUB = (240, 236, 229), (30, 24, 20), (105, 96, 88)
def crop(p, pad=(60, 80)):
    im = Image.open(p).convert('RGB'); W_, H_ = im.size; return im.crop((pad[0], pad[1], W_ - pad[0], H_ - pad[1]))
def fit(im, w, h):
    s = min(w / im.width, h / im.height); return im.resize((int(im.width * s), int(im.height * s)), Image.LANCZOS)
def hexrgb(h): return tuple(int(h[i:i + 2], 16) for i in (1, 3, 5))
def paste(im, src, box, pad=(60, 80)):
    x, y, w, h = box; p = fit(crop(src, pad), w, h); im.paste(p, (x + (w - p.width) // 2, y + (h - p.height) // 2))
order = list(W.DESIGNS)
for n, k in enumerate(order, 1):
    c = W.DESIGNS[k]; b = f'{R}/w_{k}'
    im = Image.new('RGB', (1600, 1200), BG); d = ImageDraw.Draw(im)
    for i, (f, lab) in enumerate((('v7_front.png', 'front'), ('v7_back.png', 'back · with A·B'), ('noinit_v7_back.png', 'back · without initials'))):
        paste(im, f'{b}/{f}', (20 + i * 350, 20, 340, 640)); d.text((26 + i * 350, 664), lab, fill=SUB, font=F(15))
    for i, (f, lab, pad) in enumerate((('v7_open.png', 'open', (40, 220)), ('v7_inside.png', 'inside: all edges rounded', (100, 140)),
                                       ('v7_mark.png', 'A·B mark', (140, 300)), ('noinit_v7_mark.png', 'no initials', (140, 300)))):
        paste(im, f'{b}/{f}', (20 + i * 262, 700, 252, 450), pad); d.text((26 + i * 262, 1160), lab, fill=SUB, font=F(15))
    x = 1090; d.text((x, 28), f'W{n}', fill=SUB, font=F(24, True)); d.text((x, 58), c['name'], fill=INK, font=F(54, True))
    y = 130
    for line in textwrap.wrap(c['craft'], 40): d.text((x, y), line, fill=SUB, font=F(17)); y += 24
    y += 12
    for line in textwrap.wrap(c['idea'], 41): d.text((x, y), line, fill=INK, font=F(17)); y += 24
    y += 16; d.text((x, y), 'WOOD PLA', fill=INK, font=F(16, True)); y += 28
    jobs = {}
    for key, lab in (('cover', 'cover'), ('tray', 'tray'), ('sleeve', 'hinge sleeve'), ('acc1', 'inlay'), ('acc2', 'inlay'), ('mono', 'A·B')):
        if key in c and c[key] in W.WOOD: jobs.setdefault(c[key], []); (lab not in jobs[c[key]]) and jobs[c[key]].append(lab)
    for col, labs in jobs.items():
        d.rounded_rectangle([x, y, x + 30, y + 30], 6, fill=hexrgb(W.WOOD[col]), outline=(120, 110, 100))
        d.text((x + 42, y + 5), f'{W.NAMES[col]}  ·  {" + ".join(labs)}', fill=INK, font=F(17)); y += 38
    y += 6; d.text((x, y), 'INITIALS', fill=INK, font=F(16, True)); y += 26
    try:
        d.text((x, y - 4), 'A·B', fill=INK, font=ImageFont.truetype(os.path.join(FD, c['font']), 40))
    except Exception: pass
    d.text((x + 110, y + 4), ('engraved' if c['mono'] == 'engrave' else f'inlaid in {W.NAMES[c["mono"]].lower()}'), fill=SUB, font=F(16))
    y += 50
    for line in textwrap.wrap(c['fontname'], 44): d.text((x, y), line, fill=SUB, font=F(15)); y += 21
    y += 10
    for title, key in (('FRONT', 'front'), ('BACK', 'back')):
        d.text((x, y), title, fill=INK, font=F(15, True)); y += 23
        for line in textwrap.wrap(c[key], 44): d.text((x, y), line, fill=INK, font=F(16)); y += 22
        y += 6
    d.text((x, 1120), 'rounded inside · 3 mm ends · light infill', fill=SUB, font=F(14))
    d.text((x, 1142), '2 × Ø5×2 magnets per half, corners, ≈175 g close', fill=SUB, font=F(14))
    d.text((x, 1164), 'crescent thumb scoop · pinch zone · 65 × 13.5 × 88', fill=SUB, font=F(14))
    im.save(f'{OUT}/W{n}_{k}.png')
im = Image.new('RGB', (1600, 1200), BG); d = ImageDraw.Draw(im)
d.text((30, 20), 'Rollie Book · wood PLA', fill=INK, font=F(38, True))
d.text((30, 68), 'six designs in Oak, Teak, Cherry and Walnut · front (top) and back with A·B mark (bottom)', fill=SUB, font=F(18))
if PHOTO:
    p = fit(Image.open(PHOTO).convert('RGB'), 420, 120); im.paste(p, (1600 - 20 - p.width, 10))
for i, k in enumerate(order):
    x0 = 18 + i * 264
    paste(im, f'{R}/w_{k}/v7_front.png', (x0, 140, 254, 440)); paste(im, f'{R}/w_{k}/v7_back.png', (x0, 600, 254, 440))
    d.text((x0 + 6, 1080), f'W{i + 1} {W.DESIGNS[k]["name"]}', fill=INK, font=F(22, True))
    try: d.text((x0 + 6, 1112), 'A·B', fill=SUB, font=ImageFont.truetype(os.path.join(FD, W.DESIGNS[k]['font']), 30))
    except Exception: pass
im.save(f'{OUT}/W0_overview.png'); print('boards written')
