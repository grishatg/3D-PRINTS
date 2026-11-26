"""Verification for the A1 one-plate rework: fit, clearances, support-free check, print-time estimate.

usage: WP_SRC=<designer 3mf> WP_WORK=<cache dir> python3 checks.py [fit|overhang|time|all] [out.json]
"""
import sys, os, json, math, time
import numpy as np
import manifold3d as m3
import trimesh
from shapely.geometry import Point
from shapely.ops import unary_union
import build as B
import estimate as E

BED = 256.0
ZMAX = 256.0
WRAP_ZONE = (226.0, 224.0, 256.0, 256.0)        # A1 nozzle wrap-detection corner (head_wrap_detect_zone)

# Proposed Bambu Studio settings, expressed for the time model (see estimate.DEFAULT for the stock 0.20 Standard @BBL A1)
QUALITY = dict(walls=2, top_layers=5, bottom_layers=3, infill=0.10,
               v_outer=120, v_inner=200, v_sparse=250, v_solid=220, v_top=150,
               a_default=5000, a_outer=3000, v_ovh=(120, 50, 30, 10))
STANDARD = dict(walls=2, top_layers=5, bottom_layers=3, infill=0.10)
SWAP_S = 100.0          # AMS lite: unload 29 s + load 25 s + flush + wipe (preset values plus purge)
START_S = 8 * 60.0      # heat-up, bed levelling, flow calibration
N_SWAPS = 8 + 2         # one per layer through the 8 accent layers, then spire and finial


def fit(parts):
    p = B.P
    out = {}
    lay = B.plate_layout(parts)
    bbs = {k: np.array(v.bounding_box()) for k, v in lay.items()}
    out['plate_bbox'] = {k: np.round(v, 2).tolist() for k, v in bbs.items()}
    out['min_edge_margin_mm'] = round(float(min(min(v[0], v[1], BED - v[3], BED - v[4]) for v in bbs.values())), 2)
    out['max_height_mm'] = round(float(max(v[5] for v in bbs.values())), 2)
    out['height_ok'] = bool(out['max_height_mm'] <= ZMAX)
    # footprints must not overlap, and must stay out of the wrap-detection corner
    foot = {}
    for k, m in lay.items():
        foot[k] = unary_union([Point(*pt) for pt in []]) if False else m.project()
    keys = list(lay)
    gaps = {}
    for i in range(len(keys)):
        for j in range(i + 1, len(keys)):
            a, b = foot[keys[i]], foot[keys[j]]
            inter = (a ^ b).area()
            # smallest gap between the two outlines, by growing one until they touch
            g = None
            for d in np.arange(0.5, 12.01, 0.25):
                if (a.offset(d, m3.JoinType.Round) ^ b).area() > 1e-6:
                    g = float(d - 0.25)
                    break
            gaps[f'{keys[i]}-{keys[j]}'] = dict(overlap_mm2=round(inter, 3), gap_mm=g if g is not None else '>12')
    out['plan_gaps'] = gaps
    wz = m3.CrossSection.square((WRAP_ZONE[2] - WRAP_ZONE[0], WRAP_ZONE[3] - WRAP_ZONE[1])).translate((WRAP_ZONE[0], WRAP_ZONE[1]))
    out['in_wrap_zone_mm2'] = {k: round((foot[k] ^ wz).area(), 3) for k in keys}

    # ---- assembled: nothing may intersect
    pal, ros = B.assembled(parts)
    base = parts['base']
    out['palace_vs_base_mm3'] = round((pal ^ base).volume(), 4)
    out['rosette_vs_base_mm3'] = round((ros ^ base).volume(), 4)
    tl = B.tealight_solids()
    cups = B.union([c for c, f in tl])
    flames = B.union([f for c, f in tl])
    out['tealights_vs_base_mm3'] = round(((cups + flames) ^ base).volume(), 4)
    out['tealights_vs_palace_mm3'] = round(((cups + flames) ^ pal).volume(), 4)
    # radial clearance around each tealight cup: grow the cup until it touches the base
    cl = []
    for (tx, ty) in B.TEALIGHTS:
        g = None
        for d in np.arange(0.1, 3.01, 0.1):
            cup = m3.Manifold.cylinder(19.5, p['TL_D'] / 2 + d, p['TL_D'] / 2 + d, 96).translate((tx, ty, p['FLOOR'] + 0.3))
            if (cup ^ base).volume() > 0.05:
                g = round(float(d - 0.1), 1)
                break
        cl.append(g if g is not None else '>3.0')
    out['tealight_radial_clearance_mm'] = cl
    # can each tealight be lowered straight in through the opening? (a 37 mm disc must fit inside the opening)
    op = parts['info']['opening']
    drop = []
    for i, (tx, ty) in enumerate(B.TEALIGHTS):
        disc = Point(tx, ty).buffer(p['TL_D'] / 2, quad_segs=48)
        if op.contains(disc):
            drop.append('straight in')
        else:
            # slide: find the smallest shift towards the front that makes it fit
            s = next((d for d in np.arange(0.5, 12, 0.25) if op.contains(Point(tx, ty - d).buffer(p['TL_D'] / 2, quad_segs=48))), None)
            drop.append(f'lower in {s} mm forward, then slide back' if s else 'does not fit')
    out['tealight_insertion'] = drop
    out['flame_tip_above_palace_rim_mm'] = round(p['FLOOR'] + p['TL_H'] - p['LEDGE'], 2)
    # how far the palace flange bears on the ledge
    fp = parts['fp']
    out['flange_bearing_mm'] = round(float(fp['outer'].difference(op).area / fp['outer'].exterior.length), 2)
    out['recess_depth_mm'] = p['TERR'] - p['LEDGE']
    out['assembled_height_mm'] = round(p['LEDGE'] + 248.0, 1)
    out['base_size_mm'] = np.round(np.array(base.bounding_box())[3:] - np.array(base.bounding_box())[:3], 1).tolist()
    out['volumes_cm3'] = {k: round(parts[k].volume() / 1000, 1) for k in ('base', 'palace', 'rosette')}
    return out


def overhang(man, name, lh=0.2, zmax=None):
    """Layer-by-layer support test: material in layer k that lies further than `reach` outside layer k-1."""
    t = B.tm(man)
    top = t.bounds[1][2] if zmax is None else min(zmax, t.bounds[1][2])
    zs = np.arange(lh / 2, top, lh)
    sl = E.slice_mesh(t, zs)
    worst = []
    tot = {0.25: 0.0, 0.6: 0.0, 2.0: 0.0, 6.0: 0.0}
    for k in range(1, len(zs)):
        if sl[k].is_empty or sl[k - 1].is_empty:
            continue
        rec = {}
        for reach in tot:
            u = sl[k].difference(sl[k - 1].buffer(reach, quad_segs=4))
            a = sum(g.area for g in E._polys(u) if g.area > 0.05)
            rec[reach] = a
            tot[reach] += a
        if rec[2.0] > 0.3:
            u = sl[k].difference(sl[k - 1].buffer(2.0, quad_segs=4))
            big = max(E._polys(u), key=lambda g: g.area)
            worst.append(dict(z=round(float(zs[k]), 2), area_mm2=round(rec[2.0], 2), where=[round(c, 1) for c in big.centroid.coords[0]],
                              span_mm=round(float(2 * big.area / max(big.length, 1e-6) + 4.0), 1)))
    worst.sort(key=lambda d: -d['area_mm2'])
    return dict(part=name, layers=len(zs),
                beyond_45deg_mm2=round(tot[0.25], 1), beyond_0p6mm_mm2=round(tot[0.6], 1),
                beyond_2mm_mm2=round(tot[2.0], 1), beyond_6mm_mm2=round(tot[6.0], 1), worst=worst[:12])


def print_time(parts, prof_palace, prof_rest, label, infill_base=0.08):
    """Palace and the rest are estimated separately so each can carry its own speed profile (per-object settings)."""
    lay = B.plate_layout(parts)
    t0 = time.time()
    rp = E.estimate({'palace': B.tm(lay['palace'])}, prof_palace, per_object_infill={'palace': 0.15})
    rb = E.estimate({'base': B.tm(lay['base']), 'rosette': B.tm(lay['rosette'])}, prof_rest, per_object_infill={'base': infill_base, 'rosette': 0.15})
    motion = rp['time_s'] + rb['time_s']
    total = motion + START_S + N_SWAPS * SWAP_S
    grams = dict(rp['grams']); grams.update(rb['grams'])
    return dict(profile=label, palace=E.fmt(rp['time_s']), base_and_rosette=E.fmt(rb['time_s']), swaps=N_SWAPS, start_and_swaps=E.fmt(START_S + N_SWAPS * SWAP_S),
                total=E.fmt(total), total_s=round(total), with_15pct_margin=E.fmt(total * 1.15),
                palace_features={k: E.fmt(v) for k, v in rp['features'].items()}, base_features={k: E.fmt(v) for k, v in rb['features'].items()},
                grams={k: round(v, 1) for k, v in grams.items()}, grams_total=round(sum(grams.values()), 1),
                layers=rp['layers'], calc_s=round(time.time() - t0))


if __name__ == '__main__':
    what = sys.argv[1] if len(sys.argv) > 1 else 'all'
    parts = B.build(os.environ.get('WP_SRC') or None)
    res = {}
    if what in ('fit', 'all'):
        res['fit'] = fit(parts)
    if what in ('overhang', 'all'):
        res['overhang'] = [overhang(parts['base'], 'new base (below the scenery tops)', zmax=B.P['TERR'] + 1.0),
                           overhang(parts['palace'], 'palace (designer, unchanged)', zmax=60.0)]
    if what in ('time', 'all'):
        res['time'] = [print_time(parts, QUALITY, STANDARD, 'palace: outer wall 120 mm/s, accel 3000 | base: stock 0.20 Standard speeds'),
                       print_time(parts, STANDARD, STANDARD, 'everything at stock 0.20 Standard @BBL A1 speeds')]
    js = json.dumps(res, indent=1, default=str)
    print(js)
    if len(sys.argv) > 2:
        open(sys.argv[2], 'w').write(js)
