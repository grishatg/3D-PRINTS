"""Wood-PLA designs (renders first). Four wood tones from the owner's filament photo: Oak, Teak, Cherry, Walnut (= 4 AMS lite slots).
Each design takes its cue from a wood craft or brand, and its A·B initials use a matching typeface, placed as a maker's mark
in the bottom corner of the BACK plate (hinge side). Every design also exists without initials.
Platform: v9 (continuous-curvature corners, R4.5 edges, crescent thumb scoop, pinch zone, sealed magnets).
Usage: python3 src/w_concepts.py <render_dir> <design> [noinit]
"""
import os, sys, json
os.environ.setdefault('CRESCENT', '1'); os.environ.setdefault('PINCH', '1'); os.environ.setdefault('INITIALS_POS', 'back'); os.environ.setdefault('PLATFORM', 'v10')
sys.path.insert(0, os.path.dirname(__file__))
import numpy as np
import v9_concepts as V9
from v9_concepts import asanoha, grooves, sunburst
from v8_concepts import lattice, band, pk
import v7, v5, manifold3d as m3
from shapely.geometry import Point, LineString, Polygon, box as sbox
from shapely.ops import unary_union
from shapely import affinity

# sampled from the owner's photo (lit faces; median of 24 x 24 px patches)
WOOD = dict(oak='#CE9775', teak='#BE6E4E', cherry='#4D211A', walnut='#5E3B31')
NAMES = dict(oak='Oak', teak='Teak', cherry='Cherry', walnut='Walnut')

def herringbone(region, w=3.2, L=11.0):
    """Two-tone herringbone: returns (staves A, staves B) as two geometries."""
    x0, z0, x1, z1 = region.bounds; A, B = [], []
    step = w * np.sqrt(2)
    for j, z in enumerate(np.arange(z0 - L, z1 + L, step)):
        for i, x in enumerate(np.arange(x0 - L, x1 + L, L * 0.7071 * 2)):
            a = affinity.rotate(sbox(-L / 2, -w / 2 + 0.25, L / 2, w / 2 - 0.25), 45, origin=(0, 0))
            b = affinity.rotate(sbox(-L / 2, -w / 2 + 0.25, L / 2, w / 2 - 0.25), -45, origin=(0, 0))
            A.append(affinity.translate(a, x, z)); B.append(affinity.translate(b, x + L * 0.7071, z))
    return unary_union(A).intersection(region), unary_union(B).intersection(region)

def butterfly(cx, cz, L=11.0, wmax=5.0, wmin=2.2):
    return Polygon([(cx - L / 2, cz - wmax / 2), (cx, cz - wmin / 2), (cx + L / 2, cz - wmax / 2),
                    (cx + L / 2, cz + wmax / 2), (cx, cz + wmin / 2), (cx - L / 2, cz + wmax / 2)])

def full(k, side): return (k['FRONT'] if side == 'f' else k['BACK']).buffer(-1.4)

def w_kumiko(k):
    F, B = full(k, 'f'), full(k, 'b'); bx0 = B.bounds[0]
    return {'front': [(asanoha(F), 'engrave')], 'back': [(asanoha(sbox(bx0, -10, bx0 + 13.0, 100).intersection(B), s=6.0), 'engrave')]}
def w_tambour(k):
    F, B = full(k, 'f'), full(k, 'b'); bx0 = B.bounds[0]
    return {'front': [(grooves(F, 3.6, 1.5), 'engrave')], 'back': [(grooves(B, 3.6, 1.5, bx0, bx0 + 5 * 3.6), 'engrave')]}
def w_riva(k):
    fx0, fx1 = k['FRONT'].bounds[0] + 1.0, k['FRONT'].bounds[2] - 1.0
    reg = k['BASE'].intersection(sbox(fx0, -2, fx1, 100))
    seams = unary_union([sbox(x - 0.45, -2, x + 0.45, 100) for x in np.arange(fx0 + 4.5, fx1 - 1.0, 5.5)]).intersection(reg)
    wl = sbox(-60, k['zd'] - 1.0, 60, k['zd'] + 1.0).intersection(k['BACKO'])
    return {'front': [(seams, 'acc1')], 'back': [(wl, 'acc1')]}
def w_dial(k):
    F, B = full(k, 'f'), full(k, 'b')
    return {'front': [(sunburst(F, k['MX'], k['MZ']), 'engrave')], 'back': [(lattice(B, 2.8, 0.95, ang=45), 'engrave')]}
def w_parquet(k):
    F, B = full(k, 'f'), full(k, 'b')
    a, b = herringbone(F, w=4.0, L=14.0)
    ea, eb = herringbone(B, w=4.0, L=14.0)
    # marquetry: teak and cherry staves inlaid in the oak lid; the 0.5 mm oak gaps between them read as the joints
    return {'front': [(a, 'acc2'), (b.difference(a.buffer(0.2, join_style=2)), 'acc1')], 'back': [(unary_union([ea.boundary, eb.boundary]).buffer(0.45, quad_segs=4).intersection(B), 'engrave')]}
def w_inlay(k):
    F, B = k['FRONT'], k['BACK']
    key = butterfly(-6.0, k['zd'])
    return {'front': [(band(F, 1.0, 1.0).union(key), 'acc1')], 'back': [(band(B, 1.0, 1.0), 'acc1')]}

def _printable(g, min_w=0.9):
    """keep only pieces at least min_w wide everywhere that matters (no slivers where a cell is clipped by the edge)"""
    keep = [q for q in getattr(g, 'geoms', [g]) if not q.is_empty and not q.buffer(-min_w / 2).is_empty]
    return unary_union(keep) if keep else Polygon()

def chequer(region, c=6.2, gap=0.4):
    """End-grain chequer: every other square (gap/2 inset so diagonal neighbours never touch), centred on the face."""
    x0, z0, x1, z1 = region.bounds; cx, cz = (x0 + x1) / 2, (z0 + z1) / 2
    sq = []
    for i in range(-12, 13):
        for j in range(-16, 17):
            if (i + j) % 2: continue
            a, b = cx + (i - 0.5) * c, cz + (j - 0.5) * c
            sq.append(sbox(a + gap / 2, b + gap / 2, a + c - gap / 2, b + c - gap / 2))
    return _printable(unary_union(sq).intersection(region))

def grid_lines(region, c=6.2, w=0.9):
    x0, z0, x1, z1 = region.bounds; cx, cz = (x0 + x1) / 2, (z0 + z1) / 2
    L = [sbox(cx + (i - 0.5) * c - w / 2, z0 - 5, cx + (i - 0.5) * c + w / 2, z1 + 5) for i in range(-12, 14)]
    L += [sbox(x0 - 5, cz + (j - 0.5) * c - w / 2, x1 + 5, cz + (j - 0.5) * c + w / 2) for j in range(-16, 18)]
    return unary_union(L).intersection(region)

def tumbling_blocks(region, s=4.0, gap=0.4):
    """Marquetry a cubes (tumbling blocks): pointy-top hexagons, each split into top / left / right rhombi.
    Returns (left faces, right faces, all face outlines); the top faces are the lid's own wood."""
    x0, z0, x1, z1 = region.bounds; cx, cz = (x0 + x1) / 2, (z0 + z1) / 2
    v = lambda x, z, a: (x + s * np.cos(np.radians(a)), z + s * np.sin(np.radians(a)))
    Lf, Rf, edges = [], [], []
    dx, dz = s * np.sqrt(3), 1.5 * s
    for j in range(-12, 13):
        for i in range(-9, 10):
            x = cx + i * dx + (dx / 2 if j % 2 else 0); z = cz + j * dz
            top = Polygon([(x, z), v(x, z, 30), v(x, z, 90), v(x, z, 150)])
            left = Polygon([(x, z), v(x, z, 150), v(x, z, 210), v(x, z, 270)])
            right = Polygon([(x, z), v(x, z, 270), v(x, z, 330), v(x, z, 30)])
            Lf.append(left.buffer(-gap / 2, join_style=2)); Rf.append(right.buffer(-gap / 2, join_style=2))
            edges += [top.exterior, left.exterior, right.exterior]
    clip = lambda g: _printable(unary_union(g).intersection(region))
    return clip(Lf), clip(Rf), unary_union(edges)

def w_endgrain(k):
    F, B = full(k, 'f'), full(k, 'b')
    return {'front': [(chequer(F, c=5.2), 'acc1')], 'back': [(chequer(B, c=5.2, gap=0.9), 'engrave')]}
def w_cubes(k):
    F, B = full(k, 'f'), full(k, 'b')
    lf, rf, _ = tumbling_blocks(F)
    _a, _b, eb = tumbling_blocks(B)
    return {'front': [(lf, 'acc2'), (rf, 'acc1')], 'back': [(eb.buffer(0.45, quad_segs=4).intersection(B), 'engrave')]}

DESIGNS = {
 'kumiko':  dict(name='KUMIKO', craft='Japanese kumiko joinery', cover='oak', tray='walnut', sleeve='walnut', mono='engrave',
                 font='ShipporiMinchoB1-ExtraBold-Latin.ttf', fontname='Shippori Mincho (a Japanese foundry’s serif)', cap=6.0, thick=0.12, fn=w_kumiko,
                 idea='Pale oak lid, dark walnut base, like a hinoki box on a walnut tray. The asanoha lattice (growth, strength) is engraved across the lid.',
                 front='Engraved asanoha lattice across the oak lid', back='A narrow lattice band along the opening edge; A·B engraved in the corner'),
 'riva':    dict(name='RIVA', craft='Riva Aquarama: varnished mahogany decks with pale caulking seams', cover='cherry', tray='cherry', sleeve='oak', acc1='oak', mono='oak',
                 font='BodoniModa-Bold.ttf', fontname='Bodoni (Italian Didone, after the Italian boatyard)', cap=6.0, thick=0.10, fn=w_riva,
                 idea='A deep cherry hull with pale oak seams running bow to stern, edge to edge, like a Riva deck. One oak waterline on the back.',
                 front='Oak deck seams, full length', back='One oak waterline; oak A·B in the corner'),
 'dial':    dict(name='DIAL', craft='Swiss watch dials: guilloché sunburst and clous de Paris', cover='teak', tray='walnut', sleeve='walnut', mono='oak',
                 font='Cinzel-Bold.ttf', fontname='Cinzel (Roman inscriptional capitals, as on dials and casebacks)', cap=6.0, thick=0.10, fn=w_dial,
                 idea='A warm teak "dial" with sunburst rays from the opening edge; a walnut caseback with clous de Paris and an oak signature in the corner.',
                 front='Engraved sunburst rays on teak', back='Engraved clous de Paris; oak A·B "signature"'),
 'parquet': dict(name='PARQUET', craft='European herringbone parquet', cover='oak', tray='walnut', sleeve='cherry', acc1='cherry', acc2='teak', mono='oak',
                 font='Jost-Bold.ttf', fontname='Jost (Futura-like, European modernism)', cap=5.0, thick=0.0, fn=w_parquet,
                 idea='Marquetry: a herringbone of teak and cherry staves laid into an oak lid, the oak showing as fine joints. All four woods in one case; the walnut back carries the pattern engraved.',
                 front='Teak and cherry herringbone with oak joints', back='Engraved herringbone outlines; oak A·B in the corner'),
 'endgrain': dict(name='ENDGRAIN', craft='End-grain butcher blocks and two-tone chequered luggage canvas', cover='teak', tray='walnut', sleeve='oak', acc1='walnut', mono='oak',
                 font='Inter-Bold.ttf', fontname='Inter (Helvetica-like, Scandinavian modern)', cap=5.0, thick=0.0, fn=w_endgrain,
                 idea='Two browns, one fine chequer: walnut blocks set into a teak lid like an end-grain board, the quiet two-tone check of old travel trunks. The walnut base repeats the chequer, engraved tone-on-tone.',
                 front='Teak and walnut chequer, full face', back='Engraved chequer, tone-on-tone; oak A·B in the corner'),
 'cubes':   dict(name='CUBES', craft='18th-century French marquetry à cubes (tumbling blocks)', cover='oak', tray='cherry', sleeve='walnut', acc1='walnut', acc2='teak', mono='oak',
                 font='CormorantGaramond-Bold.ttf', fontname='Garamond (the French ébénistes’ typeface)', cap=6.0, thick=0.12, fn=w_cubes,
                 idea='Stacked cubes in three woods: oak tops, teak and walnut sides, the 3D illusion of Louis XV marquetry. A cherry base with the cube outlines engraved.',
                 front='Oak / teak / walnut tumbling blocks, full face', back='Engraved cube outlines; oak A·B in the corner'),
}

def build(key, initials=True):
    cfg = DESIGNS[key]; v7.PATTERN_HOOK = cfg['fn']
    v7.INITIALS = initials; v7.FONT = cfg['font']; v7.CAP = cfg['cap']; v7.MONO_THICKEN = cfg['thick']
    v7.INITIALS_MODE = 'engrave' if cfg['mono'] == 'engrave' else 'inlay'
    r = v7.build(); chk = v7.checks(r)
    col = lambda n: WOOD[n]
    parts = [(r['cover'], col(cfg['cover']), 'c'), (r['tray'], col(cfg['tray']), 't'), (r['sleeve'], col(cfg['sleeve']), 's')]
    parts += [(y, col(cfg[a]), p) for y, p, a in r['acc']]
    if r.get('y4') is not None: parts.append((r['y4'], col(cfg['mono']), 't'))
    fil = sorted({cfg[q] for q in ('cover', 'tray', 'sleeve', 'acc1', 'acc2') if q in cfg} | ({cfg['mono']} if cfg['mono'] != 'engrave' and initials else set()))
    return r, chk, parts, fil

if __name__ == '__main__':
    out, key = sys.argv[1], sys.argv[2]; initials = 'noinit' not in sys.argv[3:]
    r, chk, parts, fil = build(key, initials)
    d = r['d']; XA, YA = d['axis']
    T = lambda m: m.translate((-XA, -YA, 0)).rotate((0, 0, -150)).translate((XA, YA, 0))
    R = v5.rollups(d)
    tips = [m3.Manifold.cylinder(13, 2.96, 2.96, 32).translate(((q.bounding_box()[0] + q.bounding_box()[3]) / 2, (q.bounding_box()[1] + q.bounding_box()[4]) / 2, q.bounding_box()[2])) for q in R]
    json.dump([pk(m, c) for m, c, g in parts], open(f'{out}/v7_closed.json', 'w'))
    json.dump([pk(T(m) if g == 'c' else m, c) for m, c, g in parts] + [pk(q, '#f1ede4') for q in R] + [pk(t, '#d9b27a') for t in tips], open(f'{out}/v7_open.json', 'w'))
    print(key, 'initials' if initials else 'no initials', 'filaments', fil, '| checks', {k: chk[k] for k in ('env', 'pieces', 'overlap', 'pocket_material', 'pocket_unsealed', 'rollups_vs_tray', 'swing_contacts', 'magnet_gap')})
