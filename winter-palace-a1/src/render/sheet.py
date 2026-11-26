"""Copy the rendered scenes into renders/ under stable names and compose the approval sheet.

usage: python3 sheet.py <scene dir> <renders dir>
"""
import os, sys
from PIL import Image, ImageDraw, ImageFont

NAMES = {'frost_hero_day': '01_hero_day', 'frost_hero_night': '02_hero_lit', 'frost_front_night': '03_front_lit',
         'frost_greeting_night': '04_greeting_lit', 'frost_greeting_day': '05_greeting_day', 'frost_plate_top': '06_a1_plate_top',
         'frost_plate_persp': '07_a1_plate', 'frost_cut_x50': '08_cutaway_tealight', 'frost_cut_x0': '09_cutaway_centre',
         'frost_front_day': '10_front_day', 'frost_back_day': '11_back_day', 'frost_top_day': '12_top_day',
         'xmas_hero_day': '13_colourway_red_gold', 'ivory_hero_day': '14_colourway_ivory_only'}


def font(sz, bold=False):
    for p in ('/usr/share/fonts/opentype/inter/Inter-Bold.otf' if bold else '/usr/share/fonts/opentype/inter/Inter-Regular.otf',
              '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'):
        if os.path.exists(p):
            return ImageFont.truetype(p, sz)
    return ImageFont.load_default()


def main(src, out):
    os.makedirs(out, exist_ok=True)
    for a, b in NAMES.items():
        Image.open(f'{src}/{a}.png').convert('RGB').save(f'{out}/{b}.png', optimize=True)

    def tile(name, w, h, cap):
        im = Image.open(f'{out}/{name}.png').convert('RGB')
        r = min(w / im.width, (h - 46) / im.height)
        im = im.resize((int(im.width * r), int(im.height * r)), Image.LANCZOS)
        t = Image.new('RGB', (w, h), '#ffffff')
        t.paste(im, ((w - im.width) // 2, 0))
        ImageDraw.Draw(t).text((w // 2, h - 24), cap, fill='#222222', font=font(22), anchor='mm')
        return t
    W, pad = 2400, 30
    sheet = Image.new('RGB', (W, 2400), '#ffffff')
    d = ImageDraw.Draw(sheet)
    d.text((pad, 28), 'Winter Palace on one A1 plate: proposal for approval', fill='#111111', font=font(46, True))
    d.text((pad, 92), 'Palace and rosette unchanged at 100 %. New lantern plinth: 4 tealight pockets, back-lit greeting, frozen pond. '
                      'Ivory White + Cobalt Blue Metallic + Gold Silk+.', fill='#444444', font=font(24))
    y = 150
    cw = (W - 3 * pad) // 2
    sheet.paste(tile('01_hero_day', cw, 1150, 'Daylight, proposed colours'), (pad, y))
    sheet.paste(tile('03_front_lit', cw, 1150, 'Tealights on (illustration of the light paths, not a photometric simulation)'), (2 * pad + cw, y))
    y += 1150 + pad
    cw3 = (W - 4 * pad) // 3
    sheet.paste(tile('04_greeting_lit', cw3, 480, 'Greeting: 0.6 mm windows lit from inside'), (pad, y))
    sheet.paste(tile('08_cutaway_tealight', cw3, 480, 'Cutaway through an outer tealight'), (2 * pad + cw3, y))
    sheet.paste(tile('06_a1_plate_top', cw3, 480, 'A1 plate, 256 x 256 mm (red corner kept clear)'), (3 * pad + 2 * cw3, y))
    y += 480 + pad
    sheet.paste(tile('13_colourway_red_gold', cw3, 440, 'Alternative: Scarlet Red + Gold'), (pad, y))
    sheet.paste(tile('14_colourway_ivory_only', cw3, 440, 'Alternative: all ivory, blue ice only'), (2 * pad + cw3, y))
    sheet.paste(tile('07_a1_plate', cw3, 440, 'On the plate'), (3 * pad + 2 * cw3, y))
    sheet.crop((0, 0, W, y + 440 + pad)).save(f'{out}/00_approval_sheet.png', optimize=True)
    print('wrote', len(NAMES) + 1, 'images to', out)


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
