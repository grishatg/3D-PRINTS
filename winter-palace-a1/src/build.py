"""Winter Palace, A1 one-plate rework: geometry.

Keeps the designer's palace and rosette untouched (100 % scale) and replaces the 243 x 241 mm base plate
with a compact "lantern plinth" that shares the A1 plate with the palace:

  * hollow light cavity under the palace with 4 tealight pockets (3 in the hall, 1 under the chapel)
  * the palace drops into a 3 mm recess on top, exactly as on the original base
  * the front is a 60 degree snow bank carrying the greeting as 0.6 mm thin windows, back-lit by the same tealights
  * a low apron with a frozen pond (first 2.4 mm print in the accent colour)
  * the designer's own fir trees, lanterns and ice crystals are lifted off the original base and replanted

All coordinates are the palace's own frame: x to the right, y to the back, z up from the table.
"""
import math, os, pickle
import numpy as np
import manifold3d as m3
import trimesh
from shapely.geometry import Polygon, MultiPolygon, box, Point
from shapely.ops import unary_union
from shapely import affinity
import common

m3.set_circular_segments(96)

# ----------------------------------------------------------------------------- parameters (mm)
P = dict(
    LAYER=0.20,
    BAND=1.6,          # base + rosette print in the accent colour below this (8 layers); the palace stays ivory
    FLOOR=2.4,         # cavity floor: 1.6 accent + 4 white layers on top
    LEDGE=39.0,        # palace rim rests here (a 38 mm tealight's flame tip ends 1.4 mm above it, inside the palace)
    TERR=42.0,         # terrace level (recess is TERR - LEDGE = 3.0 deep, as on the original base)
    REC_CL=0.40,       # clearance per side between palace flange and recess (original: 0.35)
    OPEN_GROW=1.0,     # light opening = palace interior grown by this (leaves ~2.7 mm bearing under the flange)
    TL_D=37.0, TL_H=38.0,          # the owner's tealights
    POCKET_D=38.4, RING_W=1.6, RING_H=2.0,
    HALF_W=122.0,      # base half width
    Y_BACK=50.4,       # back face of the chapel bay
    Y_HALL_BACK=20.4,  # back face behind the hall (the plan is T-shaped, like the palace, to save print time)
    BAY_HW=25.5,       # half width of the chapel bay
    Y_FT=-36.05,       # terrace front edge (top of the snow bank)
    Z_BRK=29.0,        # the bank changes from 45 deg (above) to 60 deg (below, the greeting panel)
    SLAB_T=3.0,        # bank wall thickness, measured square to the face
    MEMBRANE=0.6,      # what is left behind the letters
    APRON_Z=6.0, Y_FRONT=-98.0,
    DRUM_R=13.9, DRUM_X=24.0, DRUM_Y=-34.15,
    LAND_HW=13.0, LAND_Y=-46.0,
    WALL=2.6,
    CAP=8.0,           # greeting cap height
    LINES=('Happy Holidays!', 'For Hider and Family!'),
    FONT=os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'fonts', 'Fredoka-SemiBold.ttf'),
    SPIRE_Z=194.4,     # palace: main spire roof starts (accent colour above)
    FINIAL_Z=221.6,    # palace: collar + finial (second accent above)
)
T60 = math.tan(math.radians(60))
# tealight centres (x, y): three in the hall, one under the chapel
TEALIGHTS = [(-50.0, -8.15), (0.0, -11.6), (50.0, -8.15), (0.0, 28.5)]
# Scenery lifted from the designer's base: (source x, y on the ORIGINAL base, cut radius, cut height, scale, new x, y, level)
TREES = [
    (-100.0, -29.5, 14.5, 17.0, 0.95, -107.6, -20.0, 'terr'), (-99.5, 18.0, 15.5, 18.2, 0.90, -107.6, 5.5, 'terr'),
    (100.0, 14.0, 15.0, 16.8, 0.92, 107.6, -20.0, 'terr'), (94.5, -33.5, 15.5, 17.4, 0.90, 107.6, 5.5, 'terr'),
]
LANTERNS = [(-29.0, -79.0, 6.0, 12.9, 1.0, -98.0, -68.5, 'apron'), (25.0, -79.0, 6.0, 12.9, 1.0, 98.0, -68.5, 'apron')]
CRYSTALS = [(-52.0, 2.0, 13.5, 15.4, 1.0, -106.5, -83.0, 'apron'), (48.0, 2.0, 13.5, 15.6, 1.0, 106.5, -83.0, 'apron')]


# ----------------------------------------------------------------------------- helpers
def to_manifold(V, F):
    m = m3.Manifold(m3.Mesh(vert_properties=np.asarray(V, dtype=np.float32), tri_verts=np.asarray(F, dtype=np.uint32)))
    if m.status() != m3.Error.NoError:
        raise RuntimeError(f'mesh is not a valid manifold: {m.status()}')
    return m


def mesh_of(man):
    mm = man.to_mesh()
    return np.asarray(mm.vert_properties)[:, :3].astype(np.float64), np.asarray(mm.tri_verts).astype(np.int64)


def tm(man):
    v, f = mesh_of(man)
    return trimesh.Trimesh(v, f, process=False)


def cs(geom):
    """shapely (Multi)Polygon -> manifold CrossSection."""
    polys = [geom] if isinstance(geom, Polygon) else [g for g in getattr(geom, 'geoms', []) if isinstance(g, Polygon)]
    cont = []
    for p in polys:
        if p.is_empty or p.area < 1e-9:
            continue
        cont.append(np.asarray(p.exterior.coords)[:-1])
        for h in p.interiors:
            cont.append(np.asarray(h.coords)[:-1])
    if not cont:
        return m3.CrossSection()
    return m3.CrossSection(cont, m3.FillRule.EvenOdd)


def prism(geom, z0, z1):
    c = cs(geom)
    if c.is_empty():
        return m3.Manifold()
    return c.extrude(z1 - z0).translate((0, 0, z0))


def yz_prism(profile_yz, x0, x1):
    """Extrude a polygon drawn in the (y, z) plane along x."""
    m = cs(profile_yz).extrude(x1 - x0)                       # (u=y, v=z, w=x-x0)
    return m.transform(np.array([[0, 0, 1, x0], [1, 0, 0, 0], [0, 1, 0, 0]], dtype=np.float64))


def union(parts):
    parts = [p for p in parts if p is not None and not p.is_empty()]
    return m3.Manifold.batch_boolean(parts, m3.OpType.Add) if parts else m3.Manifold()


def rounded_rect(x0, y0, x1, y1, r_front, r_back):
    """Rectangle with different corner radii at the front (low y) and the back (high y)."""
    a = box(x0, y0, x1, y1 + 4 * r_front).buffer(-r_front).buffer(r_front, quad_segs=24)
    b = box(x0, y0 - 4 * r_back, x1, y1).buffer(-r_back).buffer(r_back, quad_segs=24)
    return a.intersection(b)


# ----------------------------------------------------------------------------- palace footprint
def palace_footprint(palace_tm):
    """outer: flange outline at the bottom.  free: interior that stays open over the first 46 mm."""
    cache = os.path.join(common.WORK, 'footprint.pkl')
    if os.path.exists(cache):
        return pickle.load(open(cache, 'rb'))

    def sec(z):
        s = palace_tm.section(plane_origin=[0, 0, z], plane_normal=[0, 0, 1])
        p, _ = s.to_2D(to_2D=np.eye(4))
        return unary_union(list(p.polygons_full))
    foot = sec(0.5)
    outer = Polygon(foot.exterior) if isinstance(foot, Polygon) else unary_union([Polygon(g.exterior) for g in foot.geoms])
    solid = unary_union([sec(z).buffer(0) for z in np.arange(0.1, 46, 0.5)])
    free = outer.difference(solid).buffer(0)
    if isinstance(free, MultiPolygon):
        free = max(free.geoms, key=lambda g: g.area)
    out = dict(outer=outer.simplify(0.01), free=Polygon(free.exterior).simplify(0.02))
    pickle.dump(out, open(cache, 'wb'))
    return out


# ----------------------------------------------------------------------------- greeting
def text_polys(line, cap, font):
    """One line of text as a shapely geometry, baseline at y=0, starting at x=0, with cap height `cap` mm."""
    from matplotlib.textpath import TextPath
    from matplotlib.font_manager import FontProperties
    fp = FontProperties(fname=font)

    def geom(s):
        tp = TextPath((0, 0), s, size=100, prop=fp)
        pos, neg = [], []
        for loop in tp.to_polygons(closed_only=True):
            if len(loop) < 4:
                continue
            pg = Polygon(loop)
            if not pg.is_valid:
                pg = pg.buffer(0)
            if pg.is_empty:
                continue
            a = 0.5 * np.sum(loop[:-1, 0] * loop[1:, 1] - loop[1:, 0] * loop[:-1, 1])
            (pos if a > 0 else neg).append(pg)
        # the font's outer contours all wind one way, counters the other
        A, B = unary_union(pos) if pos else Polygon(), unary_union(neg) if neg else Polygon()
        return A.difference(B) if A.area >= B.area else B.difference(A)
    h = geom('H')
    k = cap / (h.bounds[3] - h.bounds[1])
    g = geom(line)
    return affinity.scale(g, k, k, origin=(0, 0))


def greeting_layout(p=P):
    """Both lines centred on x=0 in panel coordinates (u along x, v up the 60 degree bank from z=0)."""
    cap = p['CAP']
    v_top = (p['Z_BRK'] - 1.6) / math.sin(math.radians(60))          # stay 1.6 mm (in z) below the break line
    base1 = v_top - cap
    base2 = base1 - cap - 0.56 * cap                                   # line pitch = 1.56 x cap
    out = []
    for line, base in zip(p['LINES'], (base1, base2)):
        g = text_polys(line, cap, p['FONT'])
        cx = (g.bounds[0] + g.bounds[2]) / 2
        out.append(affinity.translate(g, -cx, base))
    return unary_union(out)


def panel_frame(p=P):
    """4x3 placement of panel coordinates (u, v, w) -> world. w points out of the bank."""
    y_foot = p['Y_FT'] - (p['TERR'] - p['Z_BRK']) - p['Z_BRK'] / T60       # where the 60 degree face meets z=0
    c, s = math.cos(math.radians(60)), math.sin(math.radians(60))
    # columns: u = +x, v = up the bank (0, c, s), w = outward normal (0, -s, c)
    return np.array([[1, 0, 0, 0], [0, c, -s, y_foot], [0, s, c, 0]], dtype=np.float64), y_foot


# ----------------------------------------------------------------------------- scenery lifted from the original base
def lift(base_man, sx, sy, r, z_cut, scale=1.0):
    """Cut a feature (tree / lantern / crystal) off the designer's base: everything inside radius r above z_cut,
    returned with its cut face at z=0 and its axis at the origin."""
    cyl = m3.Manifold.cylinder(140, r, r).translate((sx, sy, z_cut))
    piece = (base_man ^ cyl).translate((-sx, -sy, -z_cut))
    return piece.scale((scale, scale, scale)) if scale != 1.0 else piece


def snowflake(r=8.0, w=1.35):
    """Six-armed snowflake outline (for the lit ornaments either side of the greeting)."""
    arm = [box(-w / 2, 0, w / 2, r)]
    for frac, ln in ((0.45, 0.42), (0.72, 0.28)):
        for sgn in (-1, 1):
            b = box(-w / 2, 0, w / 2, r * ln)
            arm.append(affinity.translate(affinity.rotate(b, sgn * 55, origin=(0, 0)), 0, r * frac))
    arm = unary_union(arm)
    return unary_union([affinity.rotate(arm, 60 * k, origin=(0, 0)) for k in range(6)] + [Point(0, 0).buffer(w * 0.9)]).buffer(0.15).buffer(-0.15)


# ----------------------------------------------------------------------------- the new base
def build_base(fp, base_orig_man=None, p=P):
    outer, free = fp['outer'], fp['free']
    W, TERR, LEDGE, FLOOR = p['HALF_W'], p['TERR'], p['LEDGE'], p['FLOOR']
    y_brk = p['Y_FT'] - (TERR - p['Z_BRK'])                    # 45 degrees from the terrace edge down to the break
    y_foot = y_brk - p['Z_BRK'] / T60                           # 60 degrees from the break down to the table

    # ---- outside shape
    profile = Polygon([(p['Y_BACK'], 0), (p['Y_BACK'], TERR), (p['Y_FT'], TERR), (y_brk, p['Z_BRK']), (y_foot, 0)])
    plan = unary_union([rounded_rect(-W, p['Y_FRONT'], W, p['Y_HALL_BACK'], 14.0, 9.0),
                        rounded_rect(-p['BAY_HW'], 0, p['BAY_HW'], p['Y_BACK'], 4.0, 6.0)])
    plan = plan.buffer(5.0, quad_segs=16).buffer(-5.0, quad_segs=16)          # soften the two inside corners
    main = yz_prism(profile, -W, W)
    drums = [m3.Manifold.cylinder(TERR, p['DRUM_R'], p['DRUM_R']).translate((sx * p['DRUM_X'], p['DRUM_Y'], 0)) for sx in (-1, 1)]
    landing = m3.Manifold.cube((2 * p['LAND_HW'], p['Y_FT'] - p['LAND_Y'] + 1, TERR)).translate((-p['LAND_HW'], p['LAND_Y'], 0))
    apron = prism(box(-W, p['Y_FRONT'], W, y_foot + 6), 0, p['APRON_Z'])
    # soft 45 degree edge along the front and the sides of the apron
    ch = 2.0
    edge = yz_prism(Polygon([(p['Y_FRONT'] - 1, p['APRON_Z'] - ch - 1), (p['Y_FRONT'] + ch + 1, p['APRON_Z'] + 1), (p['Y_FRONT'] - 1, p['APRON_Z'] + 1)]), -W - 1, W + 1)
    env = union([main, landing, apron] + drums) - edge
    env = env ^ prism(plan, 0, TERR + 1)

    # ---- frozen pond: accent colour shows where the apron is cut down to the band height
    xs = np.linspace(-82, 82, 165)
    rear = [(x, -74.0 + 1.1 * math.sin(x / 13.0) + 0.5 * math.sin(x / 5.1 + 1.0)) for x in xs]
    front = [(x, -88.0 + 0.9 * math.sin(x / 11.0 + 2.0) + 0.4 * math.sin(x / 4.3)) for x in xs[::-1]]
    pond = Polygon(rear + front).buffer(4.0, quad_segs=16).buffer(-2.0, quad_segs=16)
    bank = []
    steps = 6
    for i in range(steps):                                       # 45 degree banks, in layer-sized steps
        z0 = p['BAND'] + (p['APRON_Z'] - p['BAND']) * i / steps
        z1 = p['BAND'] + (p['APRON_Z'] - p['BAND']) * (i + 1) / steps + (0.5 if i == steps - 1 else 0)
        bank.append(prism(pond.buffer((z0 - p['BAND']), quad_segs=12), z0, z1))
    env = env - union(bank)

    # ---- recess for the palace
    rec = outer.buffer(p['REC_CL'], quad_segs=16)
    env = env - prism(rec, LEDGE, TERR + 2)

    # ---- light cavity
    opening = free.buffer(p['OPEN_GROW'], quad_segs=12).simplify(0.02)
    # same outline carried 10 mm below the table, so the offset only thins the walls and not the floor
    deep = Polygon([(p['Y_BACK'], -10), (p['Y_BACK'], TERR), (p['Y_FT'], TERR), (y_brk, p['Z_BRK']), (y_foot - 10 / T60, -10)])
    inner_profile = deep.buffer(-p['SLAB_T'], join_style=2).intersection(box(-500, FLOOR, 500, LEDGE))
    inner_main = yz_prism(inner_profile, -(W - p['WALL']), W - p['WALL'])
    front_mask = box(-104, -200, 104, -22)
    chapel_mask = box(-20.6, 30, 20.6, p['Y_BACK'] - p['WALL'])
    slabs = []
    dz = p['LAYER']
    z = FLOOR
    flare_top = LEDGE - 3.0                                      # 45 degree corbel starts 3 mm under the ledge
    while z < flare_top - 1e-6:
        d = flare_top - z
        f = unary_union([opening,
                         opening.buffer(d, quad_segs=6).intersection(front_mask),
                         opening.buffer(min(d, 3.4), quad_segs=6).intersection(chapel_mask)])
        slabs.append(prism(f.simplify(0.03), z, z + dz + 1e-3))
        z += dz
    flare = union(slabs)
    cavity = (flare ^ inner_main) + prism(opening, FLOOR, LEDGE + 0.01)
    body = env - cavity

    # ---- tealight locating rings on the cavity floor. The chapel tealight needs none: it is pushed back against
    #      the wall, and the centre ring is left open towards it so it can slide in.
    rings = []
    for (tx, ty) in TEALIGHTS[:3]:
        ring = Point(tx, ty).buffer(p['POCKET_D'] / 2 + p['RING_W'], quad_segs=32).difference(Point(tx, ty).buffer(p['POCKET_D'] / 2, quad_segs=32))
        if abs(tx) < 1:
            ring = ring.difference(box(-16, ty + 6, 16, ty + 40))
        rings.append(prism(ring, FLOOR - 0.1, FLOOR + p['RING_H']))
    body = body + (union(rings) ^ cavity)

    # ---- greeting: letters sunk into the 60 degree panel, leaving a thin window behind each
    letters2d = greeting_layout(p)
    tb = letters2d.bounds
    flakes = [affinity.translate(snowflake(), sx * (tb[2] + 15.0), (tb[1] + tb[3]) / 2 + 0.8) for sx in (-1, 1)]
    letters2d = unary_union([letters2d] + flakes)
    depth = p['SLAB_T'] - p['MEMBRANE']
    frame, _ = panel_frame(p)
    cut = cs(letters2d).extrude(depth + 1.0).translate((0, 0, -depth)).transform(frame)
    body = body - cut
    glow = cs(letters2d).extrude(0.12).translate((0, 0, -depth - 0.06)).transform(frame)      # for the lit render only

    # ---- scenery from the designer's base
    scenery, placed = [], []
    if base_orig_man is not None:
        for (sx, sy, r, zc, k, nx, ny, lvl) in TREES + LANTERNS + CRYSTALS:
            piece = lift(base_orig_man, sx, sy, r, zc, k)
            z_new = (TERR if lvl == 'terr' else p['APRON_Z']) - 0.4            # sink the cut face a little into the snow
            piece = piece.translate((nx, ny, z_new))
            scenery.append(piece)
            placed.append(dict(src=(sx, sy), r=r, scale=k, at=(nx, ny), level=lvl, top=round(piece.bounding_box()[5], 1)))
        sc = union(scenery)
        # keep scenery out of the recess / off the edge
        keep = prism(plan.buffer(-0.6).difference(rec.buffer(1.2)), 0, 400)
        body = body + (sc ^ keep)
    return dict(body=body, glow=glow, cavity=cavity, opening=opening, recess=rec, plan=plan, letters2d=letters2d,
                placed=placed, y_foot=y_foot, y_brk=y_brk, profile=profile)


def tealight_solids(p=P):
    """Bodies used for clearance checks and the renders: a 37 x 20 cup with a flame up to 38 mm."""
    out = []
    for (tx, ty) in TEALIGHTS:
        cup = m3.Manifold.cylinder(20.0, p['TL_D'] / 2, p['TL_D'] / 2, 64).translate((tx, ty, p['FLOOR']))
        fl = m3.Manifold.cylinder(p['TL_H'] - 20.0, 4.2, 1.2).translate((tx, ty, p['FLOOR'] + 20.0))
        out.append((cup, fl))
    return out


# ----------------------------------------------------------------------------- everything
def build(src3mf=None, with_scenery=True, p=P):
    M = common.load_original(src3mf)
    pv, pf = M['palace']
    pv = pv + [0, 0, -pv[:, 2].min()]
    palace = to_manifold(pv, pf)
    fp = palace_footprint(trimesh.Trimesh(pv, pf, process=False))
    rv, rf = M['rosette']
    rosette = to_manifold(rv + [0, 0, -rv[:, 2].min()], rf)          # as printed: frame down on the bed
    base_orig = None
    if with_scenery:
        bv, bf = M['base']
        base_orig = to_manifold(bv + [0, 0, -bv[:, 2].min()], bf)
    b = build_base(fp, base_orig, p)
    return dict(palace=palace, rosette=rosette, base=b['body'], info=b, fp=fp)


def assembled(parts, p=P):
    """Palace seated in the recess and the rosette pressed into the rose window (palace frame)."""
    pal = parts['palace'].translate((0, 0, p['LEDGE']))
    # rosette: frame (lower 1.6 mm as printed) outside the wall, plug in the 2.2 mm wall; window centre x=0, z=58.0
    ros = parts['rosette'].translate((0, 0, -1.6)).rotate((-90, 0, 0)).translate((0, -34.15, 58.0 + p['LEDGE']))
    return pal, ros


def plate_layout(parts, p=P):
    """Transforms (as functions on manifolds) that put everything on the 256 x 256 A1 bed, long sides along Y."""
    def place(m, rot, tx, ty):
        return m.rotate((0, 0, rot)).translate((tx, ty, 0))
    b = parts['base'].rotate((0, 0, 90))
    bb = b.bounding_box()
    base = b.translate((4.0 - bb[0], 128.0 - (bb[1] + bb[4]) / 2, 0))
    pl = parts['palace'].rotate((0, 0, 90))
    pb = pl.bounding_box()
    gap = 4.0
    palace = pl.translate((base.bounding_box()[3] + gap - pb[0], 128.0 - (pb[1] + pb[4]) / 2, 0))
    rosette = parts['rosette'].translate((palace.bounding_box()[0] + 16.0, 238.0, 0))
    return dict(base=base, palace=palace, rosette=rosette)
