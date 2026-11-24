"""v7.1 - Design 6 'Hybrid', 65 (W) x 13.5 (D) x 88 (H) mm (first-print feedback, 23 Nov 2026).
Hardware: only 2 x Ø9.53 x 2.53 mm magnets (sealed in during the print: the file pauses itself) + 1.75 mm filament hinge pin.
6 rollie channels (6.6 mm), centred magnet clasp on the opening edge, 2 filter-tip bays, 'A·B' Inter Bold 5 mm on the bottom.
v7.1 vs v7.0: thinner panels (cover 2.0, back 2.0) -> 13.5 mm deep, rounded edges and corners, yellow-filled ripples
(cover and tray), 2 mm datum lines, rounded inside (no octagon frame, no grip notches), magnets sealed in by pause.
"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
import v3
v3.W, v3.D, v3.H = 65.0, 13.5, 88.0                      # must precede every other project import
W, D, H = v3.W, v3.D, v3.H
import numpy as np, manifold3d as m3
import case as K, v5, v6
from v3 import chbox
from shapely.geometry import Polygon, LineString, Point, box as sbox
from shapely.ops import unary_union, linemerge
from shapely import affinity

LAYER0, LAYER = 0.2, 0.16
PLATFORM = os.environ.get('PLATFORM', 'v7')            # 'v7' (v7.1, one Ø9.53 pair, 9 mm ends) | 'v10' (two Ø5x2 pairs at the corners, 2 mm ends, rounded inside)
MAGNET_MODE = os.environ.get('MAGNET_MODE', 'embed')   # 'embed' (sealed in at a pause) | 'glue' (pockets open to the closing face, magnets glued in)
GLUE_RECESS = 0.06   # v10.4 glue mode: magnet FLUSH. Owner, 24 Nov: at 2.4 mm the Ø5x2 pull was "extremely weak", then "not flush, they sink".
                     # Target recess below the closing face AS PRINTED; each pocket floor is snapped to a layer boundary of the
                     # 0.16 mm print grid (LAYER0 + k * LAYER), so no face ever sits on a slicing plane: prints 0.08 mm below the
                     # face, faces 0.30 mm apart when closed, never proud (boss-to-socket clearance prints 0.14).
def printed_top(z):  # the slicer samples layers at mid-height: a solid region ending at print height z ends at this layer boundary
    return LAYER0 + LAYER * int(np.ceil((z - LAYER / 2 - LAYER0) / LAYER - 1e-9))
def layer_boundary(z): return LAYER0 + LAYER * round((z - LAYER0) / LAYER)
MAG_D, MAG_T = 9.53, 2.53            # re-measured by the owner (23 Nov)
POCKET_D, SKIN, GAP = 9.85, 0.96, 0.2   # drop-in pocket (prints ~9.7); 6 layers (~1.0 mm, owner's choice) over each magnet; boss-to-recess clearance
SKIN_OUT = 1.16                      # cover: 7 layers between the magnet and the outside face (no dark disc showing through)
POCKET_H = 2.72                      # 17 layers: magnet sits 0.19 below the pocket top, so the nozzle never touches it
if PLATFORM == 'v10':                # owner bought 100 x Ø5 x 2 mm magnets (24 Nov)
    MAG_D, MAG_T = 5.0, 2.0          # ONE Ø5 x 2 magnet per pocket: owner wants a lighter close (150-200 g; the v7.1 pull felt too strong)
    POCKET_D, SKIN = 5.35, 0.80      # drop-in pocket; 5 layers (0.8 mm) over each magnet: the first layers bond poorly over metal
    POCKET_H = 2.24                  # 14 layers: magnet sits 0.24 below the pocket top (nozzle margin) -> ~2.3 mm apart, two pairs ~190 g
DATUM_W, RIP_W = 2.0, 1.2            # yellow datum line width; yellow ripple stripe width
RIPPLE = os.environ.get('RIPPLE', 'flow')   # 'flow' (Design 6, connected) | 'rings' | 'topo'
RIPPLE_STATS = {}
ROUND_PILLAR = True                  # tray magnet column: round (v7.1) or square (v7.0)
INITIALS = os.environ.get('INITIALS', '1') != '0'   # INITIALS=0: plain bottom (public MakerWorld version, no 'A·B')
RIP_PHASE = 0.10                     # v7.0 used 0.22: neighbouring waves drifted together (0.16 mm gaps) once continuous
EDGE_R = float(os.environ.get('EDGE_R', 3.0))                   # rounded long edges (45 deg at the bed)
CORNER_OPEN, CORNER_SPINE = float(os.environ.get('CORNER_OPEN', 6.0)), float(os.environ.get('CORNER_SPINE', 1.0))   # plan-view corner radii
OUTLINE = os.environ.get('OUTLINE', 'round')                   # 'round' (circular corners) | 'squircle' (continuous-curvature, n=4, Apple-style)
CRESCENT = os.environ.get('CRESCENT', '0') == '1'            # v8: one crescent thumb scoop across both halves (replaces notch + scoop)
PINCH = os.environ.get('PINCH', '0') == '1'                  # v8: pinch zone at the top of every channel (lower ribs + shallow floor dish)
INITIALS_MODE = os.environ.get('INITIALS_MODE', 'inlay')     # 'inlay' (coloured) | 'engrave' (tone-on-tone recess)
PATTERN_HOOK = None                                            # concepts: callable(ctx) -> {'front'|'back'|'inside': [(geom, key)]}
YD = 0.68                      # visible (bed-face) yellow: 4 layers = 0.2 + 3 x 0.16, stops well short of the grey/black body
AB_D = 0.68                    # initials inlay depth on the bottom face
FONT, CAP = 'Inter-Bold.ttf', 5.0
INITIALS_POS = os.environ.get('INITIALS_POS', 'bottom')   # 'bottom' (v7.1: centred on the bottom end) | 'back' (maker's mark in a back-plate corner)
MONO_THICKEN = 0.0             # widen vertical stems (mm each side) for thin serif fonts: the bottom face prints upright
BADGE_LAYERS, BADGE_W, BADGE_H, BADGE_CLR = 6, 17.0, 7.0, 0.10
USE_BADGE = False              # optional: initials as a separate press-fit badge
CAPTURE = True                 # True: magnets sealed in; the 3MF pauses itself (by object, via layer-change G-code). False: snap-in pockets
LIP_H, LIP_INT, LIP_SLOTS, LIP_SLOT_W = 0.4, 0.12, 4, 0.8   # snap lip: height, radial interference, relief slots

P = dict(v5.P)
P.update(TC=2.0, WB=2.0, WS=2.6, END=(2.0 if PLATFORM == 'v10' else 9.0), R=2.8, G=0.3, CF=1.6, CB=2.2, CE=1.0, FACET=6.0,
         PIN_PRESS=1.80, PIN_SLIP=2.0, PIN_SLEEVE=2.1, SLOTS=6, SLOT_W=6.6, RIB_T=0.8, RIB_H=3.0,
         MAG_ENDS=False, INSIDE_PLATE=False, BOTTOM_MONO=False,
         SEGS=[(0, 16), (16, 34), (34, 54), (54, 72), (72, 88)],
         SCOOP_Z=(55, 70), NOTCH_Z=(54, 71),
         LIP_R=3.0, INNER_FRAME=False, GRIP_GROOVES=False, NOTCH_ROUND=True)
if PLATFORM == 'v10':
    P.update(CAV_ROUND=(2.5, 1.2, 0.5), RIB_ROUND=True, LIP_ROUND=True, RIB_TOP=52.0)
TC, WB, WS, END, R = P['TC'], P['WB'], P['WS'], P['END'], P['R']
YS = -D / 2 + TC
CX0, CX1 = -W / 2 + WS, W / 2 - WS
XA = -W / 2 + R + 0.1
BOSS_R = POCKET_D / 2 + 0.8; BOSS_H = SKIN_OUT + POCKET_H + SKIN - TC; REC_R = BOSS_R + GAP   # boss top = cover magnet skin
MX = CX1 + (WS - 1.2) - REC_R                 # recess keeps a 1.2 mm side wall
if PLATFORM == 'v10': MX -= 0.6               # v10: keeps >= 0.8 mm round the pocket where the R4.5 edge rounding curves in
MZ = H / 2
MZS = [MZ]                                   # magnet positions along the opening edge
PILLAR_X0 = MX - REC_R - 1.0                  # 1.0 mm wall between recess and the last channel
P['SLOT_X1'] = PILLAR_X0 - 0.2
if PLATFORM == 'v10':                         # channels left-aligned: the whole strip by the opening edge becomes one long tip bay
    P['SLOT_X1'] = XA + R + P['G'] + 0.4 + P['SLOTS'] * P['SLOT_W'] + (P['SLOTS'] - 1) * P['RIB_T'] + 0.05

# ---- rounded envelope: plan outline with rounded corners, long edges rounded with a 45-degree run-out at each bed face ----
HC = EDGE_R * (1 - np.sqrt(0.5))                       # height where the fillet reaches 45 deg; below it a 45 deg chamfer meets the bed
def edge_inset(h):
    if h >= EDGE_R: return 0.0
    if h >= HC: s = (EDGE_R - h) / EDGE_R; return EDGE_R - EDGE_R * np.sqrt(1 - s * s)
    return 2 * HC - h
def _rrect(x0, z0, x1, z1, r):
    return sbox(x0 + r, z0 + r, x1 - r, z1 - r).buffer(r, quad_segs=24)
def _squircle(x0, z0, x1, z1, r_spine, r_open, n=4.0, k=1.6):
    """Rounded rectangle whose corners are superellipse quadrants (continuous curvature, no tangent break).
    k scales the corner extent so it reads like a circular corner of the same nominal radius."""
    pts = []
    t = np.linspace(0, np.pi / 2, 40)
    u, v = np.cos(t) ** (2 / n), np.sin(t) ** (2 / n)
    for (cx, cz, sx, sz, rr) in ((x1, z1, 1, 1, r_open), (x0, z1, -1, 1, r_spine), (x0, z0, -1, -1, r_spine), (x1, z0, 1, -1, r_open)):
        S = rr * k
        q = list(zip(cx - sx * S + sx * S * u, cz - sz * S + sz * S * v))
        pts += q if sx * sz > 0 else q[::-1]
    return Polygon(pts).buffer(0)
if OUTLINE == 'squircle':
    BASE = _squircle(-W / 2, 0, W / 2, H, CORNER_SPINE, CORNER_OPEN)
else:
    BASE = _rrect(-W / 2, 0, W / 2 + 20, H, CORNER_SPINE).intersection(_rrect(-W / 2 - 20, 0, W / 2, H, CORNER_OPEN))
def round_env(p=None, step=0.1):
    zones = []
    ys_ = list(np.arange(-D / 2, -D / 2 + EDGE_R, step)) + [-D / 2 + EDGE_R, D / 2 - EDGE_R] + list(np.arange(D / 2 - EDGE_R + step, D / 2 + 1e-9, step))
    ys_ = sorted(set(round(y, 4) for y in ys_ + [D / 2]))
    for a, b in zip(ys_[:-1], ys_[1:]):
        ym = (a + b) / 2; ins = max(edge_inset(ym + D / 2), edge_inset(D / 2 - ym))
        zones.append(v5._map_inner(K.shapely_to_cs(BASE.buffer(-ins, quad_segs=24) if ins > 0 else BASE).extrude(b - a), a))
    return m3.Manifold.batch_boolean(zones, m3.OpType.Add)
P['ENV'] = round_env
if CRESCENT: P['THUMB'] = False
if PINCH: P['RIB_TOP'] = 55.0
FACE = BASE.buffer(-(2 * HC + 0.3))                     # flat part of the front/back faces
CRES_Z = 63.0                                            # crescent thumb scoop centre along the opening edge
WALL_MIN = 1.2                                           # v10.1: least plastic between any inside feature and the outside
if PLATFORM == 'v10':
    # v10.1 (owner's first wood test print, 24 Nov: open slots at the opening-edge corners + a hole in the thumb scoop).
    # The squircle corners cut deep into the case, but the cavity, the lip ring / groove and the magnet sockets were still
    # square-cornered boxes: 0.04 mm walls at the corners. Every inside feature now keeps >= WALL_MIN to the outside.
    # Magnet columns: the socket's chamfered mouth (r = REC_R + 0.55, at the parting line, where the long edge's rounding
    # cuts in by edge_inset(TC)) keeps WALL_MIN to the outside; the pocket keeps >= 1.1 mm everywhere.
    MX = W / 2 - edge_inset(TC) - 2.0 - (REC_R + 0.55)        # 2.0 mm there (not just WALL_MIN): lets the columns sit near the corners (z ~7.5)
    PILLAR_X0 = MX - REC_R - 1.0
    _in_pocket, _in_mouth = BASE.buffer(-edge_inset(SKIN_OUT)), BASE.buffer(-(edge_inset(TC) + WALL_MIN))
    _ok = lambda z: (_in_pocket.contains(Point(MX, z).buffer(POCKET_D / 2 + 0.8 + 0.3))
                     and _in_mouth.contains(Point(MX, z).buffer(REC_R + 0.55)))
    _zc = END + (REC_R + 1.0) - 0.6
    while not _ok(_zc): _zc += 0.1
    MZS = [round(_zc, 2), round(H - _zc, 2)]
    # cavity, cover lip ring and tray lip groove follow the rounded outline (END of plastic all round, corners included)
    P['PLAN_CLIP'] = BASE.buffer(-END, quad_segs=24)
    P['LIP_CLIP'] = BASE.buffer(-(END + 0.2), quad_segs=24)
    if CRESCENT:   # no lip ring behind the thumb scoop: a solid backing wall goes there instead
        P['LIP_CUT'] = sbox(W / 2 - 14.0, CRES_Z - 11.5, W / 2 + 5.0, CRES_Z + 11.5)
FRONT = FACE.intersection(sbox(XA + R - 0.8, -1, W, H + 1))
BACK = affinity.scale(FACE, -1, 1, origin=(0, 0))

def snap_down(z):
    return LAYER0 + np.floor((z - LAYER0) / LAYER + 1e-9) * LAYER

def UN(ms): return ms[0] if len(ms) == 1 else m3.Manifold.batch_boolean(ms, m3.OpType.Add)

def ycyl(r, y0, y1, x=MX, z=MZ, seg=72):
    a, b = min(y0, y1), max(y0, y1)
    return m3.Manifold.cylinder(b - a, r, r, seg).rotate((-90, 0, 0)).translate((x, a, z))

def monogram():
    raw = v6.text_poly('A·B', CAP, FONT, thicken=MONO_THICKEN)
    parts = sorted(getattr(raw, 'geoms', [raw]), key=lambda q: q.area)
    dot = parts[0].centroid
    return unary_union(parts[1:] + [Point(dot.x, dot.y).buffer(0.75, quad_segs=16)])

def build():
    d = v5.book('none', p=P); tray, cover, ys = d['tray'], d['cover'], d['ys']
    env = round_env(P)
    # ---- magnet clasp (sealed-in magnets) ----
    boss_top = YS + BOSS_H
    rec_floor = YS + BOSS_H + GAP
    if CAPTURE:
        c_top_z = snap_down((boss_top - SKIN) + D / 2)                # cover prints face-down: z = y + D/2
        c_pocket = UN([ycyl(POCKET_D / 2, c_top_z - POCKET_H - D / 2, c_top_z - D / 2, z=mz) for mz in MZS])
        t_top_z = snap_down(D / 2 - (rec_floor + SKIN))               # tray prints back-down: z = D/2 - y
        t_pocket = UN([ycyl(POCKET_D / 2, D / 2 - t_top_z, D / 2 - (t_top_z - POCKET_H), z=mz) for mz in MZS])
    else:
        # snap-in pockets open to the closing faces: magnet clicks past a slotted 0.4 mm lip (no pause, no glue)
        def snap_pocket(face_y, inward):                              # inward = +1 (into tray) or -1 (into cover)
            lip_r = MAG_D / 2 - LIP_INT
            y_lip = face_y + inward * LIP_H
            body = ycyl(POCKET_D / 2, y_lip - inward * 0.0, y_lip + inward * (MAG_T + 0.05))
            mouth = ycyl(lip_r, face_y - inward * 0.5, y_lip + inward * 0.01)
            slots = []
            for k in range(LIP_SLOTS):
                a = np.pi / 4 + k * 2 * np.pi / LIP_SLOTS
                sl = chbox(-LIP_SLOT_W / 2, LIP_SLOT_W / 2, min(face_y - inward * 0.5, y_lip + inward * 0.01), max(face_y - inward * 0.5, y_lip + inward * 0.01),
                           0, POCKET_D / 2 + 0.05, cv=0.05)
                slots.append(sl.rotate((0, np.degrees(a), 0)).translate((MX, 0, MZ)))
            return body + mouth + m3.Manifold.batch_boolean(slots, m3.OpType.Add), y_lip
        c_pocket, c_lip_y = snap_pocket(boss_top, -1)
        t_pocket, t_lip_y = snap_pocket(rec_floor, +1)
        c_top_z = c_lip_y + D / 2; t_top_z = D / 2 - t_lip_y
    if ROUND_PILLAR:   # v7.1: round magnet column in the tray, matching the cover's round boss (owner request)
        pillar = UN([ycyl(REC_R + 1.0, YS, D / 2 - WB + 0.1, z=mz, seg=96) for mz in MZS])
    else:
        pillar = chbox(PILLAR_X0, CX1 + 0.5, YS, D / 2 - WB + 0.1, MZ - POCKET_D / 2 - 1.4, MZ + POCKET_D / 2 + 1.4, cv=0.1)
    if PLATFORM == 'v10':   # clear the cover's whole lip ring (+GAP) out of the tray: it now crosses two corner columns
        lr = sbox(CX0 + 3.0, END + 0.2, CX1 - 0.2, H - END - 0.2).buffer(-P['LIP_R']).buffer(P['LIP_R'], quad_segs=16)
        if P.get('LIP_CLIP') is not None: lr = lr.intersection(P['LIP_CLIP'])          # v10.1: same shape as the cover's lip ring
        ring = lr.buffer(GAP, quad_segs=16).difference(lr.buffer(-1.0 - GAP, quad_segs=16))
        if P.get('LIP_CUT') is not None: ring = ring.difference(P['LIP_CUT'].buffer(-GAP, join_style=2))   # GAP of end clearance
        lip_slot = v5._map_inner(K.shapely_to_cs(ring).extrude(1.4 + GAP + 1.0), YS - 1.0)
        socket = UN([ycyl(REC_R, YS - 1.0, rec_floor, z=mz) + m3.Manifold.cylinder(0.6, REC_R + 0.55, REC_R - 0.05, 72).rotate((-90, 0, 0)).translate((MX, YS - 0.05, mz))
                     for mz in MZS])                                  # socket with a 0.5 mm chamfered mouth
    else:
        lip_slot = chbox(CX1 - 1.2 - GAP, CX1 + 0.1, YS - 1.0, YS + 1.4 + GAP, MZ - POCKET_D / 2 - 1.6, MZ + POCKET_D / 2 + 1.6, cv=0.1)
        socket = ycyl(REC_R, YS - 1.0, rec_floor)
    tray = (tray + (pillar ^ env)) - socket - lip_slot
    if P.get('INNER_FRAME', True):
        fr_poly = v5.notched_panel(CX0 + 5.0, CX1 - 2.5, END + 3.0, H - END - 3.0, c=3.0, step=3.0)
        frame_ring = fr_poly.buffer(GAP, join_style=2).difference(fr_poly.buffer(-1.6 - GAP, join_style=2))
        tray -= v5._map_inner(K.shapely_to_cs(frame_ring).extrude(0.8 + GAP + 0.5), YS - 0.5)
    if PLATFORM == 'v10':   # bosses with a 0.4 mm chamfered top edge
        boss = UN([ycyl(BOSS_R, YS - 0.3, boss_top - 0.4, z=mz) + m3.Manifold.cylinder(0.4, BOSS_R, BOSS_R - 0.4, 72).rotate((-90, 0, 0)).translate((MX, boss_top - 0.4, mz))
                   for mz in MZS])
        cover = cover + (boss ^ env)
    else:
        cover = cover + (ycyl(BOSS_R, YS - 0.3, boss_top) ^ env)
    tray = max(tray.decompose(), key=lambda q: q.volume()); cover = max(cover.decompose(), key=lambda q: q.volume())
    # pockets AFTER the keep-largest step: a sealed pocket is an internal void, which decompose() returns as its own piece
    c_floor = t_floor = None
    if MAGNET_MODE == 'glue':   # open each pocket up to the closing face; the magnet is glued onto the pocket floor
        if PLATFORM == 'v10':   # v10.4: magnets flush with the PRINTED boss top / socket floor; floors on the 0.16 layer grid
            zc = layer_boundary(printed_top(boss_top + D / 2) - MAG_T - GLUE_RECESS)        # cover prints face-down: z = y + D/2
            zt = layer_boundary(printed_top(D / 2 - rec_floor) - MAG_T - GLUE_RECESS)       # tray prints back-down:  z = D/2 - y
            c_floor = zc - D / 2; t_floor = D / 2 - zt
        else:
            c_floor = c_top_z - POCKET_H - D / 2; t_floor = D / 2 - (t_top_z - POCKET_H)
        c_pocket = UN([ycyl(POCKET_D / 2, c_floor, boss_top + 0.5, z=mz) for mz in MZS])
        t_pocket = UN([ycyl(POCKET_D / 2, rec_floor - 0.5, t_floor, z=mz) for mz in MZS])
    tray = tray - t_pocket; cover = cover - c_pocket
    if CRESCENT:   # ellipsoid dish centred on the split line at the opening edge, above the clasp
        dep = 2.6 if PLATFORM == 'v10' else 3.2                       # v10.1: 3.2 cut through the 2.6 mm side wall
        ctr = (W / 2 + 7.0 - dep, YS - 0.3, CRES_Z)
        cres = m3.Manifold.sphere(1.0, 96).scale((7.0, 5.2, 9.5)).translate(ctr)
        if PLATFORM == 'v10':   # solid backing behind the dish (WALL_MIN all round), so it can never open into the tip bay
            back = m3.Manifold.sphere(1.0, 96).scale((7.0 + WALL_MIN, 5.2 + WALL_MIN, 9.5 + WALL_MIN)).translate(ctr) ^ env
            tray = tray + (back ^ chbox(-W, W, YS, D, -1, H + 1, cv=0.1)); cover = cover + (back ^ chbox(-W, W, -D, YS, -1, H + 1, cv=0.1))
        cover = cover - cres; tray = tray - cres
    if PINCH:      # shallow dish in the channel floor under the top end of each rollie (ribs already stop at z 55)
        dishes = []
        for i in range(P['SLOTS']):
            xc = d['slot_x0'] + i * (P['SLOT_W'] + P['RIB_T']) + P['SLOT_W'] / 2
            dishes.append(m3.Manifold.sphere(1.0, 64).scale((2.6, 0.6, 7.0)).translate((xc, D / 2 - WB, 63.0)))
        tray = tray - m3.Manifold.batch_boolean(dishes, m3.OpType.Add)
    # ---- Design 6 visuals ----
    zr0, zr1 = END + 1.5, H - END - 1.5
    def rip(x0, x1, toward_right):
        out = []
        for xc in np.arange(x0, x1, 2.8):
            t = (xc - x0) / (x1 - x0); t = t if toward_right else 1 - t
            A = 0.05 + 1.6 * t ** 1.6
            zs = np.linspace(-2.0, H + 2.0, 220)          # v7.1: run the full height, edge to edge
            out.append(LineString([(xc + A * np.sin(2 * np.pi * z / 27.0 + RIP_PHASE * xc), z) for z in zs]))
        return out
    xr0 = 2.2
    hw = DATUM_W / 2
    zd = round(0.382 * H, 1)                                           # golden-section datum
    datum_gap = sbox(-60, zd - hw - 1.8, 60, zd + hw + 1.8)
    def stripes(items):                                                # items: (line, width)
        return unary_union([g.buffer(w / 2, quad_segs=8) for l, w in items for g in getattr(l, 'geoms', [l]) if not g.is_empty])
    def keep(lines, region, minlen):
        out = []
        for l, w in lines:
            c = l.intersection(region)
            if c.geom_type == 'MultiLineString': c = linemerge(c)        # rejoin a ring cut at its start point
            out += [(g, w) for g in getattr(c, 'geoms', [c]) if g.geom_type == 'LineString' and g.length > minlen]
        return out
    # full-height fields: lines run out over the top and bottom edges (like the datum wraps the opening edge)
    BACKO = affinity.scale(BASE, -1, 1, origin=(0, 0))
    f_reg = BASE.intersection(sbox(xr0 - 0.6, -1, FRONT.bounds[2] - 1.6, H + 1))
    b_reg = BACKO.intersection(sbox(BACK.bounds[0] + 1.6, -1, -2.2 + 0.6, H + 1)).difference(datum_gap)
    if RIPPLE == 'flow':      # Design 6 ripples, now continuous on the front too (they run over the hidden magnet)
        whole = lambda ls, reg: [(l, w) for l, w in ls if l.intersection(reg).geom_type == 'LineString']   # no broken, dashed lines
        f_all = BASE.intersection(sbox(-60, -1, FRONT.bounds[2] - 1.6, H + 1))
        b_all = BACKO.intersection(sbox(BACK.bounds[0] + 1.6, -1, 60, H + 1))
        fr = keep(whole([(l, RIP_W) for l in rip(xr0, FRONT.bounds[2] - 1.0, True)], f_all), f_all, 8)
        br = keep([(l, RIP_W) for l in rip(BACK.bounds[0] + 1.0, -2.2, False)], b_all.difference(datum_gap), 15)
    elif RIPPLE == 'rings':   # a stone dropped at the clasp: rings spread out and thin as they travel
        def rings(cx):
            out = []
            for k in range(13):                                    # enough rings to reach both ends
                rad = 5.5 + 2.9 * k + 0.12 * k * k; w = max(1.4 - 0.07 * k, 0.95)
                out.append((Point(cx, MZ).buffer(rad, quad_segs=64).exterior, w))
            return out
        fr = keep(rings(MX), f_reg, 4); br = keep(rings(-MX), b_reg, 4)
    elif RIPPLE == 'topo':    # contour lines of a gentle landscape (nod to the v1 Topo Edition)
        from skimage import measure
        def topo(reg, seed):
            rng = np.random.default_rng(seed); x0, z0, x1, z1 = reg.bounds; res = 0.25
            xs = np.arange(x0 - 3, x1 + 3, res); zs_ = np.arange(z0 - 3, z1 + 3, res); X, Z = np.meshgrid(xs, zs_)
            F = 0.0 * X
            for _ in range(5):
                cx, cz = rng.uniform(x0, x1), rng.uniform(z0, z1); sx, sz = rng.uniform(7, 13), rng.uniform(9, 18)
                F += rng.choice([-1, 1]) * rng.uniform(0.6, 1.0) * np.exp(-((X - cx) ** 2 / (2 * sx * sx) + (Z - cz) ** 2 / (2 * sz * sz)))
            F += 0.025 * X                                             # gentle slope so lines run, not just ring
            out = []
            for lv in np.linspace(np.percentile(F, 4), np.percentile(F, 96), 13):
                for c in measure.find_contours(F, lv):
                    out.append((LineString([(xs[0] + q[1] * res, zs_[0] + q[0] * res) for q in c]).simplify(0.05), RIP_W))
            return out
        fr = keep(topo(f_reg, 7), f_reg, 6); br = keep(topo(b_reg, 3), b_reg, 6)
    # yellow ripples: filled flush with yellow (4 layers, same layers as the datum: no extra colour swaps)
    acc = []                                                        # (solid, 'c'|'t', colour key) for concept patterns
    mono_back = zone_back = None
    if INITIALS and INITIALS_POS == 'back':     # back-face coords (as seen from behind): bottom corner on the hinge side
        mg = monogram(); mx0, mz0, mx1, mz1 = mg.bounds; fb = BACK.bounds; m_ = 4.0
        mono_back = affinity.translate(mg, fb[2] - m_ - mx1, fb[1] + m_ - mz0)
        zone_back = mono_back.envelope.buffer(1.8, join_style=2)
    if PATTERN_HOOK is None:
        cover, y5 = v6.inlay(cover, stripes(fr), 'f', YD)
        tray, y6 = v6.inlay(tray, stripes(br), 'b', YD)
        RIPPLE_STATS.update(front=fr, back=br)
        cover, y1 = v6.inlay(cover, sbox(FRONT.bounds[0] + 0.4, zd - hw, xr0 - 2.6, zd + hw), 'f', YD)
        tray, y2 = v6.inlay(tray, sbox(-W / 2 - 2.0, zd - hw, -7.0, zd + hw), 'b', YD)
        cover, y3 = v6.inside_inlay(cover, sbox(-(W / 2 - 10.0), zd - hw, W / 2 - 16.0, zd + hw), ys)
    else:                                                           # concept: its own front / back / inside inlays
        y1 = y2 = y3 = y5 = y6 = None
        pats = PATTERN_HOOK(dict(BASE=BASE, FRONT=FRONT, BACK=BACK, BACKO=affinity.scale(BASE, -1, 1, origin=(0, 0)), MX=MX, MZ=MZ, zd=zd,
                                 XA=XA, R=R, W=W, H=H, D=D, HC=HC, END=END))
        for side, part in (('front', 'c'), ('back', 't')):
            for g, key in pats.get(side, []):
                if side == 'back' and zone_back is not None: g = g.difference(zone_back)   # clean field round the initials
                if key == 'engrave':      # tone-on-tone engraving: 3 stepped layers (45 deg), prints support-free face down
                    for k_, dep in enumerate((LAYER0, LAYER0 + LAYER, LAYER0 + 2 * LAYER)):
                        gk = g.buffer(-0.16 * k_, quad_segs=6) if k_ else g
                        if gk.is_empty: break
                        if part == 'c': cover = v3.recess(cover, gk, 'f', dep)
                        else: tray = v3.recess(tray, gk, 'b', dep)
                    continue
                sh = cover if part == 'c' else tray
                sh, y = v6.inlay(sh, g, 'f' if part == 'c' else 'b', YD)
                if part == 'c': cover = sh
                else: tray = sh
                if y is not None: acc.append((y, part, key))
        for g, key in pats.get('inside', []):
            cover, y = v6.inside_inlay(cover, g, ys)
            if y is not None: acc.append((y, 'c', key))
    mono = monogram()
    badge_black = badge_yellow = None; bt = 0.0
    if USE_BADGE:
        # ---- initials as a separate press-fit badge (prints flat: only BADGE_LAYERS layers of colour changes) ----
        bt = LAYER0 + (BADGE_LAYERS - 1) * LAYER                            # 6 layers -> 1.0 mm
        outline = Polygon(K.chrect(-BADGE_W / 2, BADGE_W / 2, -BADGE_H / 2, BADGE_H / 2, 1.2)).buffer(0.6, join_style=1).buffer(-0.6, join_style=1)
        def bottom_solid(geom, z0, z1):                                     # face coords (gx right, gy up as seen from below) -> world
            return v3.cs(geom).extrude(z1 - z0).translate((0, 0, z0)).mirror((0, 1, 0))
        pocket = bottom_solid(outline.buffer(BADGE_CLR, join_style=1), -0.5, bt + 0.02)
        ribs = []
        for gx in (-BADGE_W / 4, BADGE_W / 4):                              # crush ribs: 0.12 mm interference
            for sgn in (-1, 1):
                ribs.append(Point(gx, sgn * (BADGE_H / 2 + BADGE_CLR)).buffer(BADGE_CLR + 0.12 + 0.0, quad_segs=12))
        for sgn in (-1, 1):
            ribs.append(Point(sgn * (BADGE_W / 2 + BADGE_CLR), 0).buffer(BADGE_CLR + 0.12, quad_segs=12))
        rib_solid = bottom_solid(unary_union(ribs).intersection(outline.buffer(BADGE_CLR + 0.3)), 0.25, bt)
        tray = (tray - pocket) + (rib_solid ^ v5.envelope(P))
        letters = bottom_solid(mono, 0, bt)
        base_ = bottom_solid(outline.difference(mono), 0, bt)
        chamfer_cut = bottom_solid(outline.difference(outline.buffer(-0.3, join_style=1)), 0, 0.3)   # crisp 0.3 mm shadow line
        badge_black = base_ - chamfer_cut
        badge_yellow = letters
        y4 = None
    elif mono_back is not None:                     # maker's mark on the back plate: same 4 bed layers, no upright lettering
        if INITIALS_MODE == 'engrave':
            for k_, dep in enumerate((LAYER0, LAYER0 + LAYER, LAYER0 + 2 * LAYER)):
                gk = mono_back.buffer(-0.1 * k_, quad_segs=6) if k_ else mono_back
                if not gk.is_empty: tray = v3.recess(tray, gk, 'b', dep)
            y4 = None
        else:
            tray, y4 = v6.inlay(tray, mono_back, 'b', YD)
    elif INITIALS and INITIALS_MODE == 'engrave':   # tone-on-tone, 0.5 mm deep, no extra colour
        cut = v3.cs(mono).extrude(0.5 + 0.5).translate((0, 0, -0.5)).mirror((0, 1, 0)); y4 = None; tray = tray - cut
    elif INITIALS:   # inlaid on the bottom face, dead-centre
        cut = v3.cs(mono).extrude(AB_D + 0.5).translate((0, 0, -0.5)).mirror((0, 1, 0)); y4 = cut ^ tray; tray = tray - cut
    else:            # no initials: plain black bottom
        y4 = None
    d['knuckle_mod'] = d['knuckle_mod'] + chbox(PILLAR_X0 - 1, W / 2 + 1, -D, D, MZ - 9, MZ + 9, cv=0.1)
    yel_cover = [y for y in (y1, y5, y3) if y is not None]
    yel_tray = [y for y in (y2, y6, y4) if y is not None]
    if PATTERN_HOOK is not None:   # concept colours travel with acc; keep yel_* for the shared checks
        yel_cover = yel_cover + [y for y, p, k in acc if p == 'c']; yel_tray = yel_tray + [y for y, p, k in acc if p == 't']
    return dict(d=d, tray=tray, cover=cover, sleeve=d['sleeve'], yel_cover=yel_cover, yel_tray=yel_tray, mono=mono, acc=acc, y4=y4,
                badge_black=badge_black, badge_yellow=badge_yellow, badge_t=bt,
                c_pocket=c_pocket, t_pocket=t_pocket, pause_cover_z=(c_top_z + LAYER) if CAPTURE and MAGNET_MODE == 'embed' else None,
                pause_tray_z=(t_top_z + LAYER) if CAPTURE and MAGNET_MODE == 'embed' else None, magnet_mode=MAGNET_MODE,
                c_top_z=c_top_z, t_top_z=t_top_z, zd=zd, c_floor=c_floor, t_floor=t_floor)

def checks(r):
    a, b, s = r['tray'], r['cover'], r['sleeve']
    allp = [a, b, s] + r['yel_cover'] + r['yel_tray']
    ov = sum((x ^ y).volume() for i, x in enumerate(allp) for y in allp[i + 1:])
    ov_ribs = round(((r['badge_black'] + r['badge_yellow']) ^ a).volume(), 3) if r['badge_black'] is not None else None
    bb = (a + b + s).bounding_box()
    RR = m3.Manifold.batch_boolean(v5.rollups(r['d']), m3.OpType.Add)
    XA_, YA_ = r['d']['axis']
    swing = [g for g in range(0, 166, 5) if (b.translate((-XA_, -YA_, 0)).rotate((0, 0, -g)).translate((XA_, YA_, 0)) ^ a).volume() > 0.02]
    def wall(part, pocket, grow=0.8, which=None):
        if CAPTURE:
            bbp = pocket.bounding_box(); g = UN([ycyl(POCKET_D / 2 + grow, bbp[1], bbp[4], z=mz) for mz in MZS])
            return round((g - pocket - part).volume(), 3)
        face, inward = ((YS + BOSS_H, -1) if which == 'cover' else (YS + BOSS_H + GAP, +1))
        y_lip = face + inward * LIP_H; y_bot = y_lip + inward * (MAG_T + 0.05)
        g = ycyl(POCKET_D / 2 + grow, y_lip, y_bot + inward * grow)
        return round((g - ycyl(POCKET_D / 2, y_lip, y_bot) - part).volume(), 3)
    solids = lambda m: len([q for q in m.decompose() if q.volume() > 1.0])          # sealed magnet pockets are voids, not pieces
    pv = lambda m, pk: round((pk ^ m).volume(), 3)                                      # 0 = the pocket is really empty
    def sealed(m, pk, t=0.3):                                                           # 0 = >= 0.3 mm of plastic all round
        bbp = pk.bounding_box(); shell = UN([ycyl(POCKET_D / 2 + t, bbp[1] - t, bbp[4] + t, z=mz) for mz in MZS]) - pk
        return round((shell - m).volume(), 3)
    return dict(env=[round(bb[i + 3] - bb[i], 2) for i in range(3)], pieces=(solids(a), solids(b)), overlap=round(ov, 3),
                pocket_material=(pv(a, r['t_pocket']), pv(b, r['c_pocket'])), pocket_unsealed=(sealed(a, r['t_pocket']), sealed(b, r['c_pocket'])),
                rollups=len(v5.rollups(r['d'])), rollups_vs_tray=round((RR ^ a).volume(), 3), swing_contacts=swing,
                tray_wall_void=wall(a, r['t_pocket'], which='tray'), cover_wall_void=wall(b, r['c_pocket'], which='cover'),
                magnet_gap=round(((r['t_floor'] - MAG_T) - (r['c_floor'] + MAG_T)) if r.get('c_floor') is not None
                                 else ((D / 2 - (r['t_top_z'] - POCKET_H + MAG_T)) - (r['c_top_z'] - POCKET_H + MAG_T - D / 2)) if CAPTURE
                                 else (D / 2 - r['t_top_z']) - (r['c_top_z'] - D / 2), 2),   # magnet face to magnet face, case closed
                pauses=(r['pause_cover_z'], r['pause_tray_z']),
                cover_front_skin=round(r['c_top_z'] - (POCKET_H if CAPTURE else MAG_T + 0.05), 2), MX=round(MX, 2), slot_x1=round(P['SLOT_X1'], 2),
                mono=[round(v, 2) for v in r['mono'].bounds] if INITIALS else None, datum_z=r['zd'], badge_mm=round(r['badge_t'], 2),
                rib_interference_mm3=ov_ribs, yellow_depth_mm=YD)

if __name__ == '__main__':
    r = build(); print(checks(r))
