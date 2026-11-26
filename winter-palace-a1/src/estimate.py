"""Toolpath-length print-time model (stand-in for a slicer when none can be run in the build container).

For every layer it slices each mesh, generates the wall loops by polygon offsetting, classifies the
interior as solid (top/bottom shells), gap fill or sparse infill, and runs a jerk/acceleration-limited
velocity planner over the walls. It is NOT a slicer: treat the result as +/-15 %. The definitive figure
is the one Bambu Studio shows after slicing.

Speeds and accelerations are passed in a profile dict whose keys mirror the Bambu process preset.
"""
import math
import numpy as np
import trimesh
from shapely.geometry import Polygon, MultiPolygon, GeometryCollection
from shapely.ops import unary_union
from shapely import make_valid

JERK = 9.0          # mm/s, Bambu A1 machine_max_jerk_x/y
SMOOTH_DEG = 18.0   # turning angles below this are treated as a curve, not a corner


def _polys(g):
    if g is None or g.is_empty:
        return []
    if isinstance(g, Polygon):
        return [g]
    if isinstance(g, (MultiPolygon, GeometryCollection)):
        return [p for p in g.geoms if isinstance(p, Polygon) and p.area > 1e-6]
    return []


def slice_mesh(mesh, zs):
    """Return a list of shapely geometries (one per z), each the solid cross-section."""
    out = []
    secs = mesh.section_multiplane(plane_origin=[0, 0, 0], plane_normal=[0, 0, 1], heights=list(zs))
    for s in secs:
        if s is None:
            out.append(Polygon())
            continue
        try:
            ps = list(s.polygons_full)
        except Exception:
            ps = []
        g = unary_union([p if p.is_valid else make_valid(p) for p in ps]) if ps else Polygon()
        out.append(g)
    return out


def _trap(l, v0, v1, vmax, a):
    """Time to cover l mm starting at v0, ending at v1, capped at vmax, with acceleration a."""
    if l <= 0:
        return 0.0
    vp2 = (2 * a * l + v0 * v0 + v1 * v1) / 2.0
    vp = min(vmax, math.sqrt(max(vp2, 1e-9)))
    vp = max(vp, v0, v1, 1e-3)
    d_acc = (vp * vp - v0 * v0) / (2 * a)
    d_dec = (vp * vp - v1 * v1) / (2 * a)
    cruise = max(l - d_acc - d_dec, 0.0)
    return (vp - v0) / a + (vp - v1) / a + cruise / vp


def loop_time(coords, vmax, a, closed=True):
    """Velocity-planned time for one polyline (N x 2 array)."""
    P = np.asarray(coords, dtype=float)
    if closed and np.allclose(P[0], P[-1]):
        P = P[:-1]
    n = len(P)
    if n < 2:
        return 0.0, 0.0
    nxt = np.roll(P, -1, axis=0) if closed else P[1:]
    cur = P if closed else P[:-1]
    seg = nxt - cur
    L = np.hypot(seg[:, 0], seg[:, 1])
    keep = L > 1e-6
    seg, L = seg[keep], L[keep]
    m = len(L)
    if m == 0:
        return 0.0, 0.0
    d = seg / L[:, None]
    # junction i sits at the START of segment i (between segment i-1 and i)
    prev = np.roll(d, 1, axis=0)
    cosang = np.clip((d * prev).sum(1), -1, 1)
    ang = np.arccos(cosang)
    vj = np.full(m, float(vmax))
    sharp = ang > math.radians(SMOOTH_DEG)
    with np.errstate(divide='ignore'):
        vj[sharp] = np.minimum(vmax, JERK / (2 * np.sin(ang[sharp] / 2)))
    # curvature limit on smooth parts: v <= sqrt(a * r), r ~ mean segment length / angle
    sm = (~sharp) & (ang > 1e-4)
    r = (L[sm] + np.roll(L, 1)[sm]) / 2 / ang[sm]
    vj[sm] = np.minimum(vj[sm], np.sqrt(a * r))
    if not closed:
        vj[0] = min(vj[0], JERK)
    else:
        vj[0] = min(vj[0], JERK)       # loop starts/stops at the seam
    vend = np.roll(vj, -1)
    if not closed:
        vend[-1] = JERK
    else:
        vend[-1] = JERK
    # forward / backward passes
    v0 = vj.copy()
    for _ in range(2):
        for i in range(m):
            lim = math.sqrt(v0[i] ** 2 + 2 * a * L[i])
            j = (i + 1) % m if closed else i + 1
            if j < m and (closed and j != 0 or not closed):
                v0[j] = min(v0[j], lim)
        for i in range(m - 1, -1, -1):
            j = (i + 1) % m if closed else i + 1
            v1 = v0[j] if (j < m and not (closed and j == 0)) else JERK
            v0[i] = min(v0[i], math.sqrt(v1 ** 2 + 2 * a * L[i]))
    t = 0.0
    for i in range(m):
        j = i + 1
        v1 = v0[j] if j < m else JERK
        t += _trap(L[i], v0[i], v1, vmax, a)
    return t, float(L.sum())


def rings_of(g):
    out = []
    for p in _polys(g):
        out.append(np.asarray(p.exterior.coords))
        for h in p.interiors:
            out.append(np.asarray(h.coords))
    return out


def fill_time(area, perim, lw, v, a, density=1.0):
    """Zig-zag fill of a region with total area/perimeter. Returns (time, extruded length)."""
    if area <= 1e-6:
        return 0.0, 0.0
    chord = max(math.pi * area / max(perim, 1e-6), lw)      # mean chord of the region
    length = area * density / lw
    n = length / chord
    t_line = _trap(chord, JERK / 2, JERK / 2, v, a)
    return n * t_line, length


DEFAULT = dict(
    layer_height=0.20, first_layer=0.20,
    lw_outer=0.42, lw_inner=0.45, lw_fill=0.45, lw_solid=0.42, lw_first=0.50,
    walls=2, top_layers=5, bottom_layers=3, infill=0.15,
    v_outer=200, v_inner=300, v_sparse=270, v_solid=250, v_top=200, v_gap=250,
    v_first=50, v_first_fill=105, v_travel=700, v_bridge=50,
    v_ovh=(200, 50, 30, 10),                 # outer-wall speed at 0-25 / 25-50 / 50-75 / 75-100 % overhang
    a_default=6000, a_outer=5000, a_top=2000, a_first=500, a_travel=10000,
    max_vol=22.0, min_layer_time=6.0, min_speed=20.0,
    t_travel_fixed=0.30,                     # retract + z-hop + wipe + unretract per island-to-island travel
    t_hop=0.08,                              # short repositioning move inside an island
    v_gap_cap=100.0,                         # gap fill never reaches its nominal speed
    t_layer_fixed=0.6,                       # layer change
    density=1.32, flow=0.98,
)


def estimate(meshes, prof=None, zmax=None, progress=None, per_object_infill=None, per_object_walls=None):
    """meshes: {name: trimesh.Trimesh} already placed on the plate (z=0 is the bed).
    Returns a dict with total time (s), per-feature split, filament mm3/g, and per-layer times."""
    pr = dict(DEFAULT)
    pr.update(prof or {})
    lh, lh0 = pr['layer_height'], pr['first_layer']
    top_z = max(m.bounds[1][2] for m in meshes.values())
    if zmax:
        top_z = min(top_z, zmax)
    nl = int(math.ceil((top_z - lh0) / lh - 1e-6)) + 1
    zs = np.array([lh0 / 2] + [lh0 + (i - 0.5) * lh for i in range(1, nl)])
    zs = zs[zs < top_z]
    nl = len(zs)
    sl = {n: slice_mesh(m, zs) for n, m in meshes.items()}
    feat = dict(outer=0.0, inner=0.0, gap=0.0, solid=0.0, sparse=0.0, travel=0.0, layer=0.0, cool=0.0)
    vol = {n: 0.0 for n in meshes}
    lay_t = np.zeros(nl)
    lay_len = np.zeros(nl)
    lay_vol = np.zeros(nl)          # extruded volume per layer, all objects
    for k in range(nl):
        first = k == 0
        h = lh0 if first else lh
        tl = 0.0
        ll = 0.0
        cents = []          # one entry per island (retract + travel)
        hops = 0            # short moves inside an island (no retract)
        for n in meshes:
            P = sl[n][k]
            if P.is_empty:
                continue
            walls = (per_object_walls or {}).get(n, pr['walls'])
            dens = (per_object_infill or {}).get(n, pr['infill'])
            lw_o = pr['lw_first'] if first else pr['lw_outer']
            lw_i = pr['lw_first'] if first else pr['lw_inner']
            vcap = lambda lw: pr['max_vol'] / (lw * h)
            below = sl[n][k - 1] if k > 0 else None
            # ---- walls
            off = 0.0
            reg = P
            for i in range(walls):
                lw = lw_o if i == 0 else lw_i
                loop = P.buffer(-(off + lw / 2), join_style=1, quad_segs=6)
                if loop.is_empty:
                    break
                v = pr['v_first'] if first else (pr['v_outer'] if i == 0 else pr['v_inner'])
                a = pr['a_first'] if first else (pr['a_outer'] if i == 0 else pr['a_default'])
                v = min(v, vcap(lw))
                ovh_len = [0.0, 0.0, 0.0]
                if i == 0 and not first and below is not None and not below.is_empty:
                    # share of the outer loop hanging past the layer below
                    b = loop.boundary
                    for j, frac in enumerate((0.25, 0.50, 0.75)):
                        try:
                            ovh_len[j] = b.difference(below.buffer(frac * lw - lw / 2 + 0.02, quad_segs=3)).length
                        except Exception:
                            ovh_len[j] = 0.0
                for ring in rings_of(loop):
                    t, L = loop_time(ring, v, a)
                    key = 'outer' if i == 0 else 'inner'
                    feat[key] += t
                    tl += t
                    ll += L
                    vol[n] += L * lw * h
                    hops += 1
                if i == 0 and ovh_len[0] > 0:
                    # replace the fast time on overhanging stretches with the overhang speeds
                    l1 = ovh_len[0] - ovh_len[1]
                    l2 = ovh_len[1] - ovh_len[2]
                    l3 = ovh_len[2]
                    extra = 0.0
                    for L_, v_ in ((l1, pr['v_ovh'][1]), (l2, pr['v_ovh'][2]), (l3, pr['v_ovh'][3])):
                        if L_ > 0 and v_ < v:
                            extra += L_ / v_ - L_ / v
                    feat['outer'] += extra
                    tl += extra
                off += lw
                reg = P.buffer(-off, join_style=1, quad_segs=4)
                if reg.is_empty:
                    break
            for p in _polys(P):
                cents.append(np.array(p.representative_point().coords[0]))
            if reg.is_empty:
                continue
            # ---- interior: thin leftovers are gap fill, the rest solid or sparse
            core = reg.buffer(-0.5, quad_segs=2).buffer(0.5, quad_segs=2)       # parts wider than ~1 mm
            gap = reg.difference(core.buffer(0.04, quad_segs=2)) if not core.is_empty else reg
            gps = [p for p in _polys(gap) if p.area > 0.25]         # ignore offsetting slivers
            if gps:
                ga = sum(p.area for p in gps)
                v = min(pr['v_first_fill'] if first else pr['v_gap'], vcap(pr['lw_fill']))
                L = ga / pr['lw_fill']
                t = L / min(v, pr['v_gap_cap']) + 0.03 * len(gps)
                feat['gap'] += t
                tl += t
                ll += L
                vol[n] += ga * h
                hops += len(gps)
            if core.is_empty:
                continue
            nt, nb = pr['top_layers'], pr['bottom_layers']
            if first or k < nb:
                solid, sparse = core, Polygon()
            else:
                cover = core
                for j in range(1, nt + 1):
                    if k + j >= nl:
                        cover = Polygon()
                        break
                    cover = cover.intersection(sl[n][k + j])
                    if cover.is_empty:
                        break
                if not cover.is_empty:
                    for j in range(1, nb + 1):
                        cover = cover.intersection(sl[n][k - j])
                        if cover.is_empty:
                            break
                sparse = cover.buffer(-0.3, quad_segs=2).buffer(0.3, quad_segs=2) if not cover.is_empty else Polygon()
                solid = core.difference(sparse) if not sparse.is_empty else core
            is_top = False
            if not first and k + 1 < nl:
                is_top = not core.difference(sl[n][k + 1].buffer(0.05)).is_empty
            for p in _polys(solid):
                if p.area < 0.3:            # offsetting slivers, not real toolpaths
                    continue
                v = pr['v_first_fill'] if first else (pr['v_top'] if is_top else pr['v_solid'])
                a = pr['a_first'] if first else (pr['a_top'] if is_top else pr['a_default'])
                lw = pr['lw_first'] if first else pr['lw_solid']
                t, L = fill_time(p.area, p.length, lw, min(v, vcap(lw)), a)
                feat['solid'] += t
                tl += t
                ll += L
                vol[n] += p.area * h
                hops += 1
            for p in _polys(sparse):
                if dens <= 0 or p.area < 0.3:
                    continue
                lw = pr['lw_fill']
                t, L = fill_time(p.area, p.length, lw, min(pr['v_sparse'], vcap(lw)), pr['a_default'], dens)
                feat['sparse'] += t
                tl += t
                ll += L
                vol[n] += p.area * h * dens
                hops += 1
        # ---- travel: greedy nearest-neighbour hop between path starts
        if cents:
            C = np.array(cents)
            left = list(range(len(C)))
            cur = left.pop(0)
            tt = 0.0
            while left:
                dd = np.hypot(C[left, 0] - C[cur, 0], C[left, 1] - C[cur, 1])
                j = int(dd.argmin())
                tt += _trap(float(dd[j]), 0, 0, pr['v_travel'], pr['a_travel']) + pr['t_travel_fixed']
                cur = left.pop(j)
            tt += pr['t_travel_fixed'] + max(hops - len(C), 0) * pr['t_hop']
            feat['travel'] += tt
            tl += tt
        feat['layer'] += pr['t_layer_fixed']
        tl += pr['t_layer_fixed']
        # ---- cooling slow-down on very short layers
        if not first and ll > 0 and tl < pr['min_layer_time']:
            slow = min(pr['min_layer_time'], ll / pr['min_speed'] + pr['t_layer_fixed'])
            if slow > tl:
                feat['cool'] += slow - tl
                tl = slow
        lay_t[k] = tl
        lay_len[k] = ll
        lay_vol[k] = sum(vol.values()) - lay_vol[:k].sum()
        if progress and k % 100 == 0:
            progress(k, nl)
    total = float(lay_t.sum())
    grams = {n: v * pr['flow'] * pr['density'] / 1000.0 for n, v in vol.items()}
    return dict(time_s=total, features=feat, layers=nl, layer_times=lay_t, zs=zs, vol_mm3=vol, grams=grams,
                layer_grams=lay_vol * pr['flow'] * pr['density'] / 1000.0)


def fmt(s):
    return f'{int(s // 3600)}h {int(s % 3600 // 60):02d}m'
