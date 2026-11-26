"""Build every render scene (binary meshes + json) for the approval sheet.

usage: WP_SRC=<designer 3mf> WP_WORK=<cache dir> python3 make_scenes.py <outdir> [colourway]
then:  node shot.js <outdir> <scene names...>
"""
import sys, os, json, math
import numpy as np
import manifold3d as m3
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..'))
import build as B
from scene import put, scene

# Bambu colours as swatches (approximate sRGB of the delivered spools)
# (slightly deepened so they read true after the renderer's tone mapping)
IVORY, COBALT, GOLD = '#F1EDE3', '#1F4C8F', '#D2951C'
SCARLET, GREEN, COPPER, LAVENDER, BLACK = '#BE2222', '#4FB36B', '#A5623F', '#B9ADD8', '#1b1b1d'
WAYS = {
    'frost':  dict(body=IVORY, band=COBALT, spire=COBALT, finial=GOLD, label='Ivory White + Cobalt Blue Metallic + Gold Silk+'),
    'xmas':   dict(body=IVORY, band=SCARLET, spire=SCARLET, finial=GOLD, label='Ivory White + Scarlet Red + Gold Silk+'),
    'ivory':  dict(body=IVORY, band=COBALT, spire=IVORY, finial=IVORY, label='Ivory White + Cobalt Blue ice only'),
}
MAT = {IVORY: dict(rough=0.9), COBALT: dict(rough=0.42, metal=0.35), GOLD: dict(rough=0.28, metal=0.55),
       SCARLET: dict(rough=0.85), GREEN: dict(rough=0.85), COPPER: dict(rough=0.4, metal=0.4)}


def split_z(man, zs):
    """Cut a manifold at the given heights -> list of slices, bottom to top."""
    out, rest = [], man
    for z in zs:
        top, bot = rest.split_by_plane((0, 0, 1), z)
        out.append(bot)
        rest = top
    out.append(rest)
    return out


def main(outdir, way='frost'):
    os.makedirs(outdir, exist_ok=True)
    W = WAYS[way]
    p = B.P
    parts = B.build(os.environ.get('WP_SRC') or None)
    info = parts['info']
    n = [0]

    def mesh(man, col, **kw):
        if man.is_empty():
            return None
        v, f = B.mesh_of(man)
        n[0] += 1
        d = dict(put(outdir, f'{way}_{n[0]:02d}', v, f), c=col)
        d.update(MAT.get(col, {}))
        d.update(kw)
        return d

    def coloured(part, place=lambda m: m, **kw):
        """Meshes of one printed part, split into its filament zones, then moved with `place`."""
        if part == 'base':
            lo, hi = split_z(parts['base'], [p['BAND'] + 0.002])        # hair above the pond floor, so the two zones never share a face
            return [mesh(place(lo), W['band'], **kw), mesh(place(hi), W['body'], **kw)]
        if part == 'palace':
            b, c, d = split_z(parts['palace'], [p['SPIRE_Z'], p['FINIAL_Z']])
            return [mesh(place(b), W['body'], **kw), mesh(place(c), W['spire'], **kw), mesh(place(d), W['finial'], **kw)]
        if part == 'rosette':
            lo, hi = split_z(parts['rosette'], [p['BAND'] + 0.002])
            return [mesh(place(lo), W['band'], **kw), mesh(place(hi), W['body'], **kw)]

    seat = lambda m: m.translate((0, 0, p['LEDGE']))
    ros_place = lambda m: m.translate((0, 0, -1.6)).rotate((-90, 0, 0)).translate((0, -34.15, 58.0 + p['LEDGE']))
    asm = [m for m in coloured('base') + coloured('palace', seat) + coloured('rosette', ros_place) if m]

    # tealights (for the cutaway and the night views)
    cups, flames = [], []
    for cup, fl in B.tealight_solids():
        cups.append(cup)
        flames.append(fl)
    cup_m = mesh(B.union(cups), '#f4f1ea', rough=0.6)
    flame_m = mesh(B.union(flames), '#ffb347', emissive='#ffb347', ei=3.0, rough=0.6, cast=False)
    glow_m = mesh(info['glow'], '#ffd9a0', emissive='#ffcf8a', ei=1.0, cast=False, recv=False)

    day = [{'t': 'hemi', 'c': '#ffffff', 'g': '#9aa0aa', 'i': 1.7},
           {'t': 'dir', 'i': 2.7, 'p': [220, -360, 460], 'shadow': True, 'sd': 300, 'sr': 4},
           {'t': 'dir', 'i': 0.9, 'c': '#fff1dc', 'p': [-320, -160, 180]},
           {'t': 'dir', 'i': 0.5, 'p': [100, 320, 220]}]
    table = mesh(m3.Manifold.cube((1400, 1400, 2)).translate((-700, -700, -2.02)), '#cfc8bd', rough=0.95, cast=False)
    bg = '#dfe3e8'
    scene(outdir, f'{way}_hero_day', asm + [table], {'p': [250, -610, 330], 'l': [0, -22, 128], 'fov': 30}, day, w=1500, h=1800, shadows=True, bg=bg, exposure=0.84)
    scene(outdir, f'{way}_front_day', asm + [table], {'p': [0, -700, 210], 'l': [0, -20, 132], 'fov': 26}, day, w=1500, h=1800, shadows=True, bg=bg, exposure=0.84)
    scene(outdir, f'{way}_greeting_day', asm + [table], {'p': [40, -300, 150], 'l': [0, -52, 26], 'fov': 26}, day, w=1700, h=1000, shadows=True, bg=bg, exposure=0.84)
    scene(outdir, f'{way}_back_day', asm + [table], {'p': [-260, 560, 330], 'l': [0, -10, 110], 'fov': 30}, day, w=1500, h=1700, shadows=True, bg=bg, exposure=0.84)
    scene(outdir, f'{way}_top_day', asm + [table], {'p': [0, -24, 900], 'l': [0, -24, 0], 'u': [0, 1, 0], 'ortho': 100}, day, w=1700, h=1200, shadows=True, bg=bg, exposure=0.84)

    # ---- night: only the tealights are on. Flames light the inside; thin letter windows are shown glowing.
    night = [{'t': 'hemi', 'c': '#33405c', 'g': '#0c0d12', 'i': 0.55}, {'t': 'dir', 'c': '#8fa6d8', 'i': 0.35, 'p': [200, -300, 500]}]
    for (tx, ty) in B.TEALIGHTS:
        night.append({'t': 'point', 'c': '#ffb766', 'i': 5200, 'p': [tx, ty, p['FLOOR'] + 30.0], 'decay': 2, 'shadow': True})
    # the interior must be lit from behind the walls: draw both faces
    asm_n = [dict(m, double=True) for m in asm]
    # soft glow of the 2.2 mm white walls themselves
    for m in asm_n:
        if m['c'] == W['body']:
            m.update(emissive='#ff9a3c', ei=0.035)
    ntable = mesh(m3.Manifold.cube((1400, 1400, 2)).translate((-700, -700, -2.02)), '#2a2420', rough=0.9, cast=False)
    for name, cam, w, h in [('hero_night', {'p': [250, -610, 330], 'l': [0, -22, 128], 'fov': 30}, 1500, 1800),
                            ('greeting_night', {'p': [40, -300, 150], 'l': [0, -52, 26], 'fov': 26}, 1700, 1000),
                            ('front_night', {'p': [0, -700, 210], 'l': [0, -20, 132], 'fov': 26}, 1500, 1800)]:
        scene(outdir, f'{way}_{name}', asm_n + [glow_m, flame_m, ntable], cam, night, w=w, h=h, shadows=True, bg='#0b0d14', exposure=1.15)

    # ---- cutaway through an outer tealight (x = 50) and through the centre line (x = 0)
    for xc, tag in ((50.0, 'x50'), (0.0, 'x0')):
        def cutp(m):
            return m.trim_by_plane((-1, 0, 0), -xc)            # keep x <= xc
        cut = []
        for src, place in (('base', lambda m: m), ('palace', seat), ('rosette', ros_place)):
            cut += [m for m in coloured(src, lambda m, place=place: cutp(place(m))) if m]
        cut.append(mesh(cutp(B.union(cups)), '#e9e2d2', rough=0.6))
        cut.append(mesh(cutp(B.union(flames)), '#ffb347', emissive='#ffb347', ei=2.0))
        scene(outdir, f'{way}_cut_{tag}', cut + [table], {'p': [700, -40, 60], 'l': [0, -22, 52], 'ortho': 78}, day, w=1900, h=1500, shadows=False, bg=bg, exposure=0.84)

    # ---- the A1 plate, seen from above
    lay = B.plate_layout(parts)
    plate = []
    tf = {}
    for k in ('base', 'palace', 'rosette'):
        # recover each part's plate transform from the laid-out bounding boxes
        tf[k] = lay[k]
    bb = {k: np.round(tf[k].bounding_box(), 2).tolist() for k in tf}
    # colour zones on the plate
    def on_plate(name):
        src = parts[name]
        if name == 'rosette':
            off = np.array(tf[name].bounding_box()[:3]) - np.array(src.bounding_box()[:3])
            return lambda m: m.translate(tuple(off))
        r = src.rotate((0, 0, 90))
        off = np.array(tf[name].bounding_box()[:3]) - np.array(r.bounding_box()[:3])
        return lambda m: m.rotate((0, 0, 90)).translate(tuple(off))
    for k in ('base', 'palace', 'rosette'):
        plate += [m for m in coloured(k, on_plate(k)) if m]
    bed = mesh(m3.Manifold.cube((256, 256, 1.0)).translate((0, 0, -1.02)), '#3a3d42', rough=0.85, cast=False)
    lines = []
    for i in range(0, 257, 32):
        lines.append(m3.Manifold.cube((256, 0.5, 0.06)).translate((0, i - 0.25, -0.02)))
        lines.append(m3.Manifold.cube((0.5, 256, 0.06)).translate((i - 0.25, 0, -0.02)))
    grid = mesh(B.union(lines), '#5a5e66', cast=False)
    zone = mesh(m3.Manifold.cube((30, 32, 0.08)).translate((226, 224, -0.02)), '#7a4040', cast=False)   # nozzle wrap-detect corner
    scene(outdir, f'{way}_plate_top', plate + [bed, grid, zone], {'p': [128, 128, 900], 'l': [128, 128, 0], 'u': [0, 1, 0], 'ortho': 140},
          [{'t': 'hemi', 'c': '#ffffff', 'g': '#777777', 'i': 2.0}, {'t': 'dir', 'i': 2.0, 'p': [300, -200, 700], 'tg': [128, 128, 0], 'shadow': True, 'sd': 260}],
          w=1500, h=1500, shadows=True, bg='#eceae4')
    scene(outdir, f'{way}_plate_persp', plate + [bed, grid, zone], {'p': [128 + 330, 128 - 420, 380], 'l': [128, 128, 70], 'fov': 30},
          [{'t': 'hemi', 'c': '#ffffff', 'g': '#777777', 'i': 1.8}, {'t': 'dir', 'i': 2.4, 'p': [400, -300, 600], 'tg': [128, 128, 0], 'shadow': True, 'sd': 300}],
          w=1600, h=1400, shadows=True, bg='#eceae4')
    json.dump(dict(plate_bbox=bb, placed=info['placed'], way=W['label']), open(os.path.join(outdir, f'{way}_meta.json'), 'w'), indent=1)
    print('scenes written for', way, '| plate bboxes', bb)


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else 'frost')
