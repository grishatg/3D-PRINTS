"""MakerWorld image set (4:3, 1600 x 1200) from the Playwright renders.
Usage (from v7-65x15x88/): python3 src/render/makerworld.py <render_root> <out_dir>
Needs <render_root>/<MW_PREFIX>{flow,rings,topo}/v7_{front,open,back,base}.png, magnet_section_v7.1.png and v7_a1_plate.png."""
import sys, os
from PIL import Image, ImageDraw, ImageFont
R, OUT = sys.argv[1], sys.argv[2]; os.makedirs(OUT, exist_ok=True)
PRE = os.environ.get('MW_PREFIX', 'final_')            # 'pub_' = renders without initials
NAME = os.environ.get('MW_NAME', 'Rollie Book')        # public listing name (no initials)
BASE_SUB = os.environ.get('MW_BASE_SUB', 'plain black bottom · rounded edges · ripples run over the edges')
BG = (236, 234, 228); INK = (28, 28, 30); SUB = (95, 95, 95); YEL = (255, 208, 11)
F = lambda s, b=False: ImageFont.truetype(f'/usr/share/fonts/truetype/dejavu/DejaVuSans{"-Bold" if b else ""}.ttf', s)
D = {'flow': ('A', 'FLOW', 'Design 6 ripples, unbroken, edge to edge'),
     'rings': ('B', 'RINGS', 'a stone dropped at the clasp'),
     'topo': ('C', 'TOPO', 'contour lines of a gentle landscape')}
def crop(p, pad=(70, 90)):
    im = Image.open(p).convert('RGB'); W, H = im.size
    return im.crop((pad[0], pad[1], W - pad[0], H - pad[1]))
def canvas(title, sub):
    c = Image.new('RGB', (1600, 1200), BG); d = ImageDraw.Draw(c)
    d.rectangle([0, 1110, 1600, 1200], fill=INK); d.rectangle([0, 1110, 14, 1200], fill=YEL)
    d.text((40, 1128), title, fill=(245, 245, 245), font=F(34, True)); d.text((40 + d.textlength(title, font=F(34, True)) + 22, 1140), sub, fill=(200, 200, 200), font=F(22))
    return c, d
def fit(im, w, h):
    s = min(w / im.width, h / im.height); return im.resize((int(im.width * s), int(im.height * s)), Image.LANCZOS)
for k, (L, name, tag) in D.items():
    base = f'{R}/{PRE}{k}'
    c, d = canvas(f'{NAME} · {L} {name}', tag)
    for i, v in enumerate(('front', 'back')):
        im = fit(crop(f'{base}/v7_{v}.png'), 780, 1080); c.paste(im, (20 + i * 790 + (780 - im.width) // 2, 20 + (1080 - im.height) // 2))
    c.save(f'{OUT}/{L}_{name.lower()}_1_front_back.png')
    c, d = canvas(f'{NAME} · {L} {name}', 'open: 6 rollies (≤ 6 × 60 mm) + 2 filter-tip bays, filament-pin hinge')
    im = fit(crop(f'{base}/v7_open.png', (40, 200)), 1560, 1080); c.paste(im, ((1600 - im.width) // 2, 20 + (1080 - im.height) // 2)); c.save(f'{OUT}/{L}_{name.lower()}_2_open.png')
    if os.environ.get('MW_BASE', '0') != '1': continue      # base close-up only makes sense with the initials (MW_BASE=1)
    c, d = canvas(f'{NAME} · {L} {name}', BASE_SUB)
    im = fit(crop(f'{base}/v7_base.png', (10, 10)), 1560, 1080); c.paste(im, ((1600 - im.width) // 2, 20 + (1080 - im.height) // 2)); c.save(f'{OUT}/{L}_{name.lower()}_3_base.png')
# overview of all three
c, d = canvas(f'{NAME} · 3 designs', 'same case, same print, pick your ripple')
for i, (k, (L, name, tag)) in enumerate(D.items()):
    x0 = 20 + i * 527
    for j, v in enumerate(('front', 'back')):
        im = fit(crop(f'{R}/{PRE}{k}/v7_{v}.png'), 500, 500); c.paste(im, (x0 + (507 - im.width) // 2, 14 + j * 520 + (500 - im.height) // 2))
    d.text((x0 + 8, 1052), f'{L} · {name}', fill=INK, font=F(30, True))
c.save(f'{OUT}/0_all_three_designs.png')
# shared: magnet cut-through and plate
for src, title, sub, fn in (('magnet_section_v7.1.png', 'Magnets sealed inside', 'the printer chimes and pauses twice: drop a 9.53 × 2.53 magnet in, press Resume', '4_magnets_sealed_in.png'),
                            ('v7_a1_plate.png', 'One plate, Bambu Lab A1 + AMS lite', 'print by object · about 2¾–3 h · grey / black / yellow PETG', '5_plate.png')):
    c, d = canvas(title, sub); im = Image.open(src).convert('RGB'); im = fit(im, 1560, 1070)
    c.paste(im, ((1600 - im.width) // 2, 20 + (1080 - im.height) // 2)); c.save(f'{OUT}/{fn}')
print('wrote', sorted(os.listdir(OUT)))
