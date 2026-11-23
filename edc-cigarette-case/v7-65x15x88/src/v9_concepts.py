"""v9: ten designs (renders first). Visual language rethought: form, texture and restraint instead of printed graphics.
Most designs use TONE-ON-TONE ENGRAVING (3 stepped layers, 45 deg, support-free face-down), colour blocking, or one precise accent.
Platform for all ten: v8 shape (continuous-curvature corners, R4.5 edges) + CRESCENT thumb scoop across both halves + PINCH zone
at the top of every channel. Usage: python3 src/v9_concepts.py <render_dir> <concept>
"""
import os, sys, json
os.environ.setdefault('CRESCENT', '1'); os.environ.setdefault('PINCH', '1')
sys.path.insert(0, os.path.dirname(__file__))
import numpy as np
import v8_concepts as V8          # sets the v8 shape env and imports v7
from v8_concepts import hexdots, lattice, pk
import v7, v5, manifold3d as m3
from shapely.geometry import Point, LineString, Polygon, box as sbox
from shapely.ops import unary_union
from shapely import affinity

C = dict(V8.C, red='#C8102E', forest='#3B5A2A', lime='#9BD43C', dark2='#3A3B3D', white='#E4E2DC', cream='#E6D9BC')   # whites toned down: the viewer blows pure white out

# ---------------- pattern helpers (face coords) ----------------
def grooves(region, pitch, w, x0=None, x1=None):
    bx0, bz0, bx1, bz1 = region.bounds; x0 = bx0 if x0 is None else x0; x1 = bx1 if x1 is None else x1
    return unary_union([sbox(x - w / 2, bz0 - 1, x + w / 2, bz1 + 1) for x in np.arange(x0 + pitch / 2, x1, pitch)]).intersection(region)

def sunburst(region, cx, cz, w=0.95):
    rays = []
    for n, r0 in ((24, 8.0), (24, 16.0), (48, 32.0)):
        off = {8.0: 0.0, 16.0: 0.5, 32.0: 0.25}[r0]
        for i in range(n):
            a = 2 * np.pi * (i + off) / n
            rays.append(LineString([(cx + r0 * np.cos(a), cz + r0 * np.sin(a)), (cx + 140 * np.cos(a), cz + 140 * np.sin(a))]).buffer(w / 2, cap_style=1, quad_segs=4))
    return unary_union(rays).intersection(region)

def asanoha(region, s=7.0, w=0.85):
    x0, z0, x1, z1 = region.bounds; h = s * np.sqrt(3) / 2; segs = []
    for j, z in enumerate(np.arange(z0 - h, z1 + h, h)):
        for i, x in enumerate(np.arange(x0 - s, x1 + s, s)):
            xo = x + (s / 2 if j % 2 else 0)
            for tri in ([(xo, z), (xo + s, z), (xo + s / 2, z + h)], [(xo + s / 2, z + h), (xo + s * 1.5, z + h), (xo + s, z)]):
                cxg, czg = np.mean([p[0] for p in tri]), np.mean([p[1] for p in tri])
                for k in range(3):
                    segs.append(LineString([tri[k], tri[(k + 1) % 3]])); segs.append(LineString([tri[k], (cxg, czg)]))
    return unary_union([q.buffer(w / 2, cap_style=1, quad_segs=4) for q in segs]).intersection(region)

def twill(region, w=0.9, L=3.2, px=2.6, pz=1.9):
    x0, z0, x1, z1 = region.bounds; out = []
    for j, z in enumerate(np.arange(z0 - 2, z1 + 2, pz)):
        for x in np.arange(x0 - 4 + (j % 4) * px / 4 * 2, x1 + 4, px * 2):
            out.append(LineString([(x - L / 2 * 0.707, z - L / 2 * 0.707), (x + L / 2 * 0.707, z + L / 2 * 0.707)]).buffer(w / 2, cap_style=1, quad_segs=4))
    return unary_union(out).intersection(region)

def stitch(poly, inset=2.8, step=2.7, L=1.8, w=0.85, slant=28):
    ring = poly.buffer(-inset, quad_segs=24).exterior; out = []
    for t in np.arange(0, ring.length, step):
        p = ring.interpolate(t); q = ring.interpolate(min(t + 0.5, ring.length))
        ang = np.degrees(np.arctan2(q.y - p.y, q.x - p.x)) + slant
        a = np.radians(ang)
        out.append(LineString([(p.x - L / 2 * np.cos(a), p.y - L / 2 * np.sin(a)), (p.x + L / 2 * np.cos(a), p.y + L / 2 * np.sin(a))]).buffer(w / 2, cap_style=1, quad_segs=6))
    return unary_union(out)

def vulcanite(region, pitch=2.2, w=0.8):
    return lattice(region, pitch, w, ang=60)

# ---------------- the ten ----------------
def full(k, side): return (k['FRONT'] if side == 'f' else k['BACK']).buffer(-1.4)
def p_porcelain(k):
    zd = k['zd']; F, B = full(k, 'f'), full(k, 'b')
    return {'front': [(sbox(-60, zd - 0.5, 60, zd + 0.5).intersection(F), 'engrave')], 'back': [(sbox(-60, zd - 0.5, 60, zd + 0.5).intersection(B), 'engrave')]}
def p_ridge(k):
    F, B = full(k, 'f'), full(k, 'b'); bx0 = B.bounds[0]
    return {'front': [(grooves(F, 3.6, 1.5), 'engrave')], 'back': [(grooves(B, 3.6, 1.5, bx0, bx0 + 5 * 3.6), 'engrave')]}
def p_dial(k):
    F, B = full(k, 'f'), full(k, 'b')
    return {'front': [(sunburst(F, k['MX'], k['MZ']), 'engrave')], 'back': [(lattice(B, 2.8, 0.95, ang=45), 'engrave')]}
def p_leica(k):
    F = full(k, 'f')
    dot = Point(k['MX'], k['MZ']).buffer(2.4, quad_segs=32)
    tex = vulcanite(F.difference(Point(k['MX'], k['MZ']).buffer(5.0)), 2.3, 0.85)
    return {'front': [(tex, 'engrave'), (dot, 'acc1')], 'back': []}
def p_kumiko(k):
    F, B = full(k, 'f'), full(k, 'b'); bx1 = B.bounds[2]
    band = sbox(bx1 - 13.0, -10, bx1, 100).intersection(B)
    return {'front': [(asanoha(F), 'engrave')], 'back': [(asanoha(band, s=6.0), 'engrave')]}
def p_saddle(k):
    F, B = k['FRONT'], k['BACK']
    return {'front': [(stitch(F, 2.6), 'acc1')], 'back': [(stitch(B, 2.6), 'acc1'), (Point(-k['MX'] + 2, k['zd']).buffer(4.0, quad_segs=32).difference(Point(-k['MX'] + 2, k['zd']).buffer(3.1, quad_segs=32)), 'engrave')]}
def p_horizon(k):
    zd = k['zd']; Ff = k['BASE'].intersection(sbox(-60, -1, 60, zd)); Bb = k['BACKO'].intersection(sbox(-60, zd + 0.0, 60, 100))
    Ff = Ff.intersection(sbox(k['FRONT'].bounds[0], -1, 60, 100))
    return {'front': [(Ff, 'acc1')], 'back': [(Bb, 'acc2')]}
def p_carbon(k):
    F, B = full(k, 'f'), full(k, 'b')
    edge = sbox(F.bounds[2] - 1.0, -10, F.bounds[2] + 3, 100).intersection(k['FRONT'].buffer(0.6))
    return {'front': [(twill(F.difference(sbox(F.bounds[2] - 2.2, -10, 99, 100))), 'engrave'), (edge, 'acc1')], 'back': [(sbox(-60, k['zd'] - 0.5, 60, k['zd'] + 0.5).intersection(B), 'engrave')]}
def p_stripe(k):
    xs0, xs1 = -15.0, -7.0
    f = k['BASE'].intersection(sbox(xs0, -2, xs1, 100)); b = k['BACKO'].intersection(sbox(-xs1, -2, -xs0, 100))
    return {'front': [(f, 'acc1')], 'back': [(b, 'acc1')]}
def p_field(k):
    F, B = full(k, 'f'), full(k, 'b'); x0, z0, x1, z1 = F.bounds
    grille = hexdots(sbox(x0 + 3, z1 - 30, x1 - 3, z1 - 3).intersection(F), 2.5, lambda x, z: 1.2)
    knob = Point(k['MX'] - 1.0, k['MZ']).buffer(5.0, quad_segs=48)
    bx0, bz0, bx1, bz1 = B.bounds
    grid = unary_union([sbox(x - 0.45, z - 2, x + 0.45, z + 2).union(sbox(x - 2, z - 0.45, x + 2, z + 0.45)) for x in np.arange(bx0 + 6, bx1 - 3, 8) for z in np.arange(bz0 + 6, bz1 - 3, 8)]).intersection(B)
    return {'front': [(grille, 'engrave'), (knob, 'acc1')], 'back': [(grid, 'engrave')]}

CONCEPTS = {
 'porcelain': dict(name='PORCELAIN', ref='AirPods-case calm, in Pantone 2026 Cloud Dancer white', cover='white', tray='white', sleeve='white', mono='engrave', fn=p_porcelain,
                   idea='One material, no colour, no graphics. The form carries it: continuous-curvature corners, soft edges, a single engraved hairline at the golden section. Prints with zero colour swaps.',
                   front='One engraved hairline at the golden section', back='The same hairline, so the line circles the object'),
 'ridge':     dict(name='RIDGE', ref='Rimowa: aluminium grooves since 1950, after the first all-metal aircraft', cover='gray', tray='gray', sleeve='darkgray', mono='engrave', fn=p_ridge,
                   idea='Engineering as ornament. Deep parallel grooves you can feel, tone-on-tone, like a Rimowa shell. Grip and identity in one move.',
                   front='Full-face engraved grooves, 3.6 mm pitch', back='Five grooves along the opening edge only: a quieter echo'),
 'dial':      dict(name='DIAL', ref='Swiss watch dials: guilloché sunburst and clous de Paris', cover='cream', tray='darkgray', sleeve='darkgray', mono='engrave', fn=p_dial,
                   idea='Two classic watch-dial finishes, engraved tone-on-tone. Light rakes across the rays and pyramids, so the surface changes as you turn it.',
                   front='Sunburst rays radiating from the magnet clasp (rayon de gloire)', back='Clous de Paris: crossing grooves forming tiny pyramids'),
 'leica':     dict(name='LEICA', ref='Leica M: black body, diamond-pattern leatherette, one red dot', cover='black', tray='black', sleeve='black', acc1='red', mono='red', fn=p_leica,
                   idea='Black, textured, serious, with one red dot. The dot sits exactly over the magnet: it tells you where the case opens.',
                   front='Diamond leatherette texture (engraved) + a red dot over the clasp', back='Smooth, plain black, like the back of an M'),
 'kumiko':    dict(name='KUMIKO', ref='Japanese kumiko joinery: the asanoha (hemp leaf) lattice, a wish for growth and strength', cover='cream', tray='peanut', sleeve='peanut', mono='engrave', fn=p_kumiko,
                   idea='Hinoki-pale cover, darker wood tray. The asanoha lattice is engraved tone-on-tone across the front and repeats as a narrow band on the back.',
                   front='Asanoha lattice across the whole face', back='A narrow asanoha band along the opening edge'),
 'saddle':    dict(name='SADDLE', ref='Hermès-style leather goods: orange, tan, saddle stitching', cover='orange', tray='peanut', sleeve='peanut', acc1='cream', mono='cream', fn=p_saddle,
                   idea='A leather wallet in plastic. Slanted saddle-stitch dashes trace both faces, with a blind-stamped ring on the back.',
                   front='Saddle stitch 2.6 mm inside the edge', back='Saddle stitch + a blind-stamped (engraved) ring'),
 'horizon':   dict(name='HORIZON', ref='Mid-century colour blocking: Swiss rail, Braun, vintage transistor radios', cover='cream', tray='forest', sleeve='cream', acc1='forest', acc2='cream', mono='cream', fn=p_horizon,
                   idea='Two colours meet at the golden section on both faces, so a forest-green band wraps right round the lower case, like a vintage radio or Swiss rail livery.',
                   front='Cream above, forest green below the golden section', back='The same split, so the green band wraps round'),
 'carbon':    dict(name='CARBON', ref='Motorsport carbon fibre: 2/2 twill weave, one signal colour', cover='black', tray='dark2', sleeve='lime', acc1='lime', mono='engrave', fn=p_carbon,
                   idea='Twill weave engraved tone-on-tone on black, with one lime signal line on the opening edge where your thumb goes.',
                   front='Engraved 2/2 twill + lime edge line at the opening side', back='Plain dark grey with one engraved hairline'),
 'stripe':    dict(name='STRIPE', ref='Racing livery: one bold stripe, Porsche Design restraint', cover='darkgray', tray='darkgray', sleeve='yellow', acc1='yellow', mono='yellow', fn=p_stripe,
                   idea='One continuous 8 mm yellow stripe runs over the top, down the front, under the bottom and up the back. Uses your yellow spool.',
                   front='One yellow stripe, end to end', back='The same stripe, in line'),
 'field':     dict(name='FIELD', ref='Teenage Engineering: greys and whites, orange knob, speaker-grille dots', cover='white', tray='gray', sleeve='gray', acc1='orange', mono='orange', fn=p_field,
                   idea='A tiny instrument. An engraved speaker grille, an orange "knob" over the magnet (press here), and a fine engraved grid on the back.',
                   front='Engraved dot grille at the top + an orange disc over the clasp', back='Fine engraved plus-grid'),
}

NAMES = dict(V8.__dict__.get('NAMES', {}), gray='Gray', darkgray='Dark Gray', black='Black', white='White', cream='Cream', peanut='Peanut Brown', orange='Orange',
             lake='Lake Blue', yellow='Yellow', red='Red', forest='Forest Green', lime='Lime Green', dark2='Dark Gray')

def build(key):
    cfg = CONCEPTS[key]; v7.PATTERN_HOOK = cfg['fn']
    v7.INITIALS_MODE = 'engrave' if cfg['mono'] == 'engrave' else 'inlay'
    r = v7.build(); chk = v7.checks(r)
    col = lambda n: C[n]
    parts = [(r['cover'], col(cfg['cover']), 'c'), (r['tray'], col(cfg['tray']), 't'), (r['sleeve'], col(cfg['sleeve']), 's')]
    parts += [(y, col(cfg[a]), p) for y, p, a in r['acc']]
    if r.get('y4') is not None: parts.append((r['y4'], col(cfg['mono']), 't'))
    fil = sorted({cfg[k] for k in ('cover', 'tray', 'sleeve', 'acc1', 'acc2') if k in cfg} | ({cfg['mono']} if cfg['mono'] != 'engrave' else set()))
    return r, chk, parts, fil

if __name__ == '__main__':
    out, key = sys.argv[1], sys.argv[2]
    r, chk, parts, fil = build(key)
    d = r['d']; XA, YA = d['axis']
    T = lambda m: m.translate((-XA, -YA, 0)).rotate((0, 0, -150)).translate((XA, YA, 0))
    R = v5.rollups(d)
    tips = [m3.Manifold.cylinder(13, 2.96, 2.96, 32).translate(((q.bounding_box()[0] + q.bounding_box()[3]) / 2, (q.bounding_box()[1] + q.bounding_box()[4]) / 2, q.bounding_box()[2])) for q in R]
    json.dump([pk(m, c) for m, c, g in parts], open(f'{out}/v7_closed.json', 'w'))
    json.dump([pk(T(m) if g == 'c' else m, c) for m, c, g in parts] + [pk(q, '#f1ede4') for q in R] + [pk(t, '#d9b27a') for t in tips], open(f'{out}/v7_open.json', 'w'))
    print(key, 'filaments', fil, '| checks', {k: chk[k] for k in ('env', 'pieces', 'overlap', 'pocket_material', 'pocket_unsealed', 'rollups_vs_tray', 'swing_contacts', 'magnet_gap')})
