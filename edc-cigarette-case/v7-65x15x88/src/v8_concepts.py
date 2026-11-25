"""v8 concepts: five premium CMF + pattern directions on the v7.1 engineering platform (renders first, 3MF on approval).
Platform changes shared by all five: continuous-curvature (superellipse) plan corners, R4.5 long edges with the 45-degree
bed run-out, different patterns front and back, PETG HF colours only, max 4 filaments (AMS lite), outside colour 4 layers.
Usage: python3 src/v8_concepts.py <render_dir> [concept ...]   -> <render_dir>/v8_<concept>_{closed,open}.json + checks
"""
import os, sys, json
os.environ.setdefault('OUTLINE', 'squircle'); os.environ.setdefault('EDGE_R', '4.5')
os.environ.setdefault('CORNER_OPEN', '11'); os.environ.setdefault('CORNER_SPINE', '4')
sys.path.insert(0, os.path.dirname(__file__))
import numpy as np
import v7, v5, manifold3d as m3
from shapely.geometry import Point, LineString, Polygon, box as sbox
from shapely.ops import unary_union
from shapely import affinity

# Bambu PETG HF colours (screen approximations of the real filaments)
C = dict(gray='#A7AAAB', darkgray='#4E4F51', black='#1E1E20', white='#F4F4F1', cream='#EEE2C6', peanut='#8B5B2E',
         orange='#F26B21', lake='#4C7FC4', yellow='#FFD00B')

def hexdots(region, pitch, dfun, dmin=0.9):
    x0, z0, x1, z1 = region.bounds; out = []
    for j, z in enumerate(np.arange(z0, z1 + pitch, pitch * 0.866)):
        for x in np.arange(x0 + (pitch / 2 if j % 2 else 0), x1 + pitch, pitch):
            d = max(dfun(x, z), dmin)
            c = Point(x, z).buffer(d / 2, quad_segs=6)
            if region.contains(c): out.append(c)
    return unary_union(out)

def rings(region, cx, cz, r0, pitch, w, n=30):
    g = unary_union([Point(cx, cz).buffer(r0 + k * pitch + w / 2, quad_segs=48).exterior.buffer(w / 2, quad_segs=6) for k in range(n)])
    return g.intersection(region)

def band(poly, inset, w):
    return poly.buffer(-inset, quad_segs=24).difference(poly.buffer(-inset - w, quad_segs=24))

def lattice(region, pitch, w, ang=55):
    x0, z0, x1, z1 = region.bounds; L = 300; ls = []
    for s in (1, -1):
        for c in np.arange(-200, 200, pitch):
            ls.append(affinity.rotate(LineString([(c, -L), (c, L)]), s * (90 - ang), origin=(0, 0)))
    return unary_union([l.buffer(w / 2, cap_style=2) for l in ls]).intersection(region)

def slots(region, w=1.0, L=5.0, px=7.2, pz=2.5):
    x0, z0, x1, z1 = region.bounds; out = []
    for z in np.arange(z0 + 1.2, z1 - 0.5, pz):
        for x in np.arange(x0 + 0.6, x1 - L, px):
            s = LineString([(x + w / 2, z), (x + L - w / 2, z)]).buffer(w / 2, quad_segs=8)
            if region.contains(s): out.append(s)
    return unary_union(out)

def weave(region, cell=6.0, n=3, w=0.9, L=4.8):
    x0, z0, x1, z1 = region.bounds; out = []
    for i, x in enumerate(np.arange(x0, x1, cell)):
        for j, z in enumerate(np.arange(z0, z1, cell)):
            cx, cz = x + cell / 2, z + cell / 2; horiz = (i + j) % 2 == 0
            for k in range(n):
                off = (k - (n - 1) / 2) * (cell / n)
                a, b = ((cx - L / 2, cz + off), (cx + L / 2, cz + off)) if horiz else ((cx + off, cz - L / 2), (cx + off, cz + L / 2))
                s = LineString([a, b]).buffer(w / 2, cap_style=1, quad_segs=6)
                if region.contains(s): out.append(s)
    return unary_union(out)

def grain(region, seed=9, n=11, w=0.9):
    from skimage import measure
    rng = np.random.default_rng(seed); x0, z0, x1, z1 = region.bounds; res = 0.25
    xs = np.arange(x0 - 3, x1 + 3, res); zs = np.arange(z0 - 3, z1 + 3, res); X, Z = np.meshgrid(xs, zs)
    F = 0.32 * X                                                     # long grain runs along the height
    for _ in range(3):                                               # two or three knots
        cx, cz = rng.uniform(x0 + 6, x1 - 6), rng.uniform(z0 + 12, z1 - 12)
        F += rng.uniform(2.5, 4.0) * np.exp(-((X - cx) ** 2 / (2 * 3.5 ** 2) + (Z - cz) ** 2 / (2 * 9.0 ** 2)))
    F += 0.6 * np.sin(Z / 9.0 + 0.3 * X / 6.0)
    out = []
    for lv in np.linspace(np.percentile(F, 3), np.percentile(F, 97), n):
        for c in measure.find_contours(F, lv):
            ls = LineString([(xs[0] + q[1] * res, zs[0] + q[0] * res) for q in c]).simplify(0.05)
            if ls.length > 10 and not (ls.is_ring and ls.length < 22): out.append(ls.buffer(w / 2, quad_segs=6))   # tiny knot loops would fill solid
    return unary_union(out).intersection(region)

def fade(region, up=True, wmax=1.7, wmin=0.8, g0=0.7, g1=7.5):
    x0, z0, x1, z1 = region.bounds; out = []; z = z0 if up else z1; t = 0.0
    while (z < z1 if up else z > z0):
        t = (z - z0) / (z1 - z0) if up else (z1 - z) / (z1 - z0)
        w = wmax + (wmin - wmax) * t; g = g0 + (g1 - g0) * t ** 1.3
        zc = z + (w / 2 if up else -w / 2)
        out.append(sbox(x0 - 1, zc - w / 2, x1 + 1, zc + w / 2)); z = zc + (w / 2 + g if up else -(w / 2 + g))
    return unary_union(out).intersection(region)

def pill(cx, cz, w, h):
    return LineString([(cx, cz - h / 2 + w / 2), (cx, cz + h / 2 - w / 2)]).buffer(w / 2, quad_segs=16)

# ---------------- the five concepts ----------------
def p_aero(k):
    F = k['FRONT'].buffer(-1.4); B = k['BACK'].buffer(-1.4)
    mx, mz = k['MX'], k['MZ']
    dots = hexdots(F, 2.3, lambda x, z: 1.45 - 0.55 * min(np.hypot(x - mx, z - mz) / 45.0, 1.0))
    return {'front': [(dots, 'acc1')], 'back': [(rings(B, -mx, mz, 3.0, 2.3, 0.85), 'acc2')]}
def p_ultra(k):
    F = k['FRONT'].buffer(-0.6); B = k['BACK'].buffer(-1.4); mx, mz = k['MX'], k['MZ']
    act = pill(F.bounds[2] - 2.6, mz, 2.4, 12.0)
    ring = band(F, 2.2, 0.8).difference(act.buffer(1.0))
    return {'front': [(ring, 'acc1'), (act, 'acc2')], 'back': [(lattice(B, 4.2, 0.8), 'acc3')]}
def p_rams(k):
    F = k['FRONT'].buffer(-1.4); B = k['BACK'].buffer(-1.4); mx, mz = k['MX'], k['MZ']
    x0, z0, x1, z1 = F.bounds
    grille = slots(sbox(x0 + 2.0, mz + 8.5, x1 - 1.0, z1 - 4.0).intersection(F))
    dot = Point(mx, mz).buffer(2.2, quad_segs=24)
    bx0, bz0, bx1, bz1 = B.bounds
    ticks = unary_union([sbox(bx1 - (4.0 if i % 5 == 0 else 2.4), bz0 + 6 + i * 3.0 - 0.45, bx1 - 0.2, bz0 + 6 + i * 3.0 + 0.45) for i in range(int((bz1 - bz0 - 12) / 3.0) + 1)]).intersection(B)
    return {'front': [(grille, 'acc1'), (dot, 'acc2')], 'back': [(ticks, 'acc3'), (Point(-mx, mz).buffer(2.2, quad_segs=24), 'acc2')]}
def p_nordic(k):
    F = k['FRONT'].buffer(-1.4); B = k['BACK'].buffer(-1.4)
    return {'front': [(weave(F), 'acc1')], 'back': [(grain(B), 'acc2')]}
def p_tide(k):
    F = k['FRONT'].buffer(-1.4); B = k['BACK'].buffer(-1.4)
    return {'front': [(fade(F, up=True), 'acc1')], 'back': [(fade(B, up=False), 'acc2')]}

CONCEPTS = {
    'aero':   dict(name='AERO', ref='Bang & Olufsen Beosound: anodised aluminium, graded perforation grille',
                   cover='gray', tray='darkgray', sleeve='darkgray', acc1='darkgray', acc2='gray', mono='gray', fn=p_aero,
                   front='Graded micro-perforation field: 1.45 mm holes at the clasp easing to 0.9 mm at the edges',
                   back='Fine concentric rings spreading from the clasp, tone-on-tone'),
    'ultra':  dict(name='ULTRA', ref='Apple Watch Ultra: titanium grey, black, one international-orange control',
                   cover='gray', tray='black', sleeve='orange', acc1='black', acc2='orange', acc3='darkgray', mono='orange', fn=p_ultra,
                   front='One continuous-curvature line traced 2 mm inside the edge + an orange "action" pill exactly where the thumb opens it',
                   back='Precision diamond lattice, dark grey on black'),
    'rams':   dict(name='RAMS', ref='Dieter Rams / Braun: cream and grey, colour only where it does a job',
                   cover='cream', tray='gray', sleeve='gray', acc1='gray', acc2='orange', acc3='cream', mono='orange', fn=p_rams,
                   front='Braun-style slot grille on the upper half + one orange dot over the magnet: "open here"',
                   back='A quiet scale of ticks along the opening edge + the matching orange dot'),
    'nordic': dict(name='NORDIC', ref='B&O Beosound A5 Nordic Weave: natural aluminium, woven paper, light oak',
                   cover='gray', tray='peanut', sleeve='cream', acc1='cream', acc2='cream', mono='cream', fn=p_nordic,
                   front='Basket-weave field in cream, like the woven paper front',
                   back='Oak: long grain with two knots, in cream on peanut brown'),
    'tide':   dict(name='TIDE', ref='Apple iMac colourways: one bold colour paired with white',
                   cover='lake', tray='white', sleeve='white', acc1='white', acc2='lake', mono='lake', fn=p_tide,
                   front='White lines that thin and spread upward, like light leaving the water',
                   back='The same fade in lake blue, running downward'),
}

def build(key):
    cfg = CONCEPTS[key]; v7.PATTERN_HOOK = cfg['fn']
    r = v7.build(); chk = v7.checks(r)
    cols = {k: C[cfg[k]] for k in ('cover', 'tray', 'sleeve', 'mono') if k in cfg}
    parts = [(r['cover'], cols['cover'], 'c'), (r['tray'], cols['tray'], 't'), (r['sleeve'], cols['sleeve'], 's')]
    parts += [(y, C[cfg[a]], p) for y, p, a in r['acc']]
    if r.get('y4') is not None: parts.append((r['y4'], cols['mono'], 't'))
    fil = sorted({cfg[k] for k in ('cover', 'tray', 'sleeve', 'acc1', 'acc2', 'acc3', 'mono') if k in cfg})
    return r, chk, parts, fil

def pk(man, col):
    mm = man.to_mesh(); v = np.asarray(mm.vert_properties)[:, :3]; t = np.asarray(mm.tri_verts)
    return {'v': np.round(v, 3).ravel().tolist(), 't': t.ravel().tolist(), 'c': col}

if __name__ == '__main__':
    out = sys.argv[1]; keys = sys.argv[2:] or list(CONCEPTS)
    for key in keys:
        r, chk, parts, fil = build(key)
        d = r['d']; XA, YA = d['axis']
        T = lambda m: m.translate((-XA, -YA, 0)).rotate((0, 0, -150)).translate((XA, YA, 0))
        R = v5.rollups(d)
        tips = [m3.Manifold.cylinder(13, 2.96, 2.96, 32).translate(((q.bounding_box()[0] + q.bounding_box()[3]) / 2, (q.bounding_box()[1] + q.bounding_box()[4]) / 2, q.bounding_box()[2])) for q in R]
        json.dump([pk(m, c) for m, c, g in parts], open(f'{out}/v7_closed.json', 'w'))
        json.dump([pk(T(m) if g == 'c' else m, c) for m, c, g in parts] + [pk(q, '#f1ede4') for q in R] + [pk(t, '#d9b27a') for t in tips], open(f'{out}/v7_open.json', 'w'))
        json.dump(dict(key=key, filaments=fil, checks={k: (v if not hasattr(v, 'item') else v.item()) for k, v in chk.items() if k in
                  ('env', 'pieces', 'overlap', 'pocket_material', 'pocket_unsealed', 'rollups_vs_tray', 'swing_contacts', 'magnet_gap', 'pauses')}),
                  open(f'{out}/v8_{key}_meta.json', 'w'), default=str)
        print(key, 'filaments', fil, '| checks', {k: chk[k] for k in ('env', 'pieces', 'overlap', 'pocket_material', 'pocket_unsealed', 'rollups_vs_tray', 'swing_contacts', 'magnet_gap')})
        if len(keys) > 1: print('  (render each concept separately: the JSON is overwritten per concept)')
