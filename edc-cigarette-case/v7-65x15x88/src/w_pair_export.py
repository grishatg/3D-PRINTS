"""Two wood-PLA designs in ONE Bambu Studio project, ONE plate, print by object, on a Bambu Lab A1 + AMS lite (v10.1).
Owner, 24 Nov: all magnets are GLUED after printing (pockets open, no pauses); two designs per project so a plate prints two cases.

Layout: 4 objects (cover A, tray A, cover B, tray B) in a pinwheel, so every pair of objects is >= 74 mm apart hull to hull
(Bambu's by-object check for the A1: each convex hull grows by extruder_clearance_max_radius / 2 = 36.4 mm).
The two hinge sleeves ride along inside a same-coloured object (cover or tray of either design), so they keep their accent wood
and add no colour swaps; the pairs are chosen so this always works:
    KUMIKO + DIAL, RIVA + PARQUET, ENDGRAIN + CUBES.
Fixed AMS slots: 1 Oak, 2 Teak, 3 Cherry, 4 Walnut.
Usage: python3 src/w_pair_export.py <out_dir> <template_dir> <designA> <designB> <initials|noinit>
"""
import os, sys, json, uuid, zipfile
os.environ.setdefault('PLATFORM', 'v10')
sys.path.insert(0, os.path.dirname(__file__))
import w_concepts as W      # FIRST: sets the wood platform env (squircle R4.5, crescent, pinch, back mark) before v7 is imported
import v7, v6_final, a1_safe, manifold3d as m3
import numpy as np
from shapely.geometry import MultiPoint
from shapely import affinity
from w_export import SLOTS, FIL, FLUSH, PLATFORM_FLAGS, FINAL, FINAL_PRESET
assert (v7.PLATFORM, v7.OUTLINE, v7.EDGE_R, v7.CORNER_OPEN, v7.CORNER_SPINE, v7.CRESCENT, v7.PINCH, v7.INITIALS_POS) == PLATFORM_FLAGS

PAIRS = [('kumiko', 'dial'), ('riva', 'parquet'), ('endgrain', 'cubes')]
GAP = 74.0           # hull-to-hull (Bambu needs > 72.8 on the A1)
BED = 256.0
BRIM = 3.0
SLEEVE_GAP = 4.0     # sleeve stands this far from its host object (brims merge)

def design_parts(key, initials):
    """Cover / tray parts in print orientation (canonical frame: spine at -x, length along y), plus the sleeve."""
    v7.MAGNET_MODE = 'glue'
    cfgd = W.DESIGNS[key]
    r, chk, _parts, fil = W.build(key, initials)
    bad = {k: chk[k] for k in ('pieces', 'overlap', 'pocket_material', 'rollups_vs_tray', 'swing_contacts') if
           (k == 'pieces' and chk[k] != (1, 1)) or (k in ('overlap', 'rollups_vs_tray') and abs(chk[k]) > 1e-3) or
           (k == 'pocket_material' and max(abs(v) for v in chk[k]) > 1e-3) or (k == 'swing_contacts' and chk[k])}
    assert not bad, (key, bad)
    slot = lambda wood: SLOTS.index(wood) + 1
    tray_rot = lambda m: m.rotate((-90, 0, 0)); cover_rot = lambda m: m.rotate((90, 0, 0))
    N = cfgd['name']
    cov = [(cover_rot(r['cover']), f'{N} lid ({cfgd["cover"]})', slot(cfgd['cover']))] + \
          [(cover_rot(y), f'{N} inlay ({cfgd[a]})', slot(cfgd[a])) for y, p, a in r['acc'] if p == 'c']
    tra = [(tray_rot(r['tray']), f'{N} tray ({cfgd["tray"]})', slot(cfgd['tray']))] + \
          [(tray_rot(y), f'{N} inlay ({cfgd[a]})', slot(cfgd[a])) for y, p, a in r['acc'] if p == 't']
    if r.get('y4') is not None: tra.append((tray_rot(r['y4']), f'{N} A·B ({cfgd["mono"]})', slot(cfgd['mono'])))
    sleeve = (r['sleeve'], f'{N} hinge sleeve ({cfgd["sleeve"]})', slot(cfgd['sleeve']))
    return dict(cover=cov, tray=tra, sleeve=sleeve, chk=chk, cfg=cfgd)

U = lambda vs: m3.Manifold.batch_boolean(vs, m3.OpType.Add) if len(vs) > 1 else vs[0]

def centre(parts):
    bb = U([q for q, n_, e in parts]).bounding_box()
    return [(q.translate((-(bb[0] + bb[3]) / 2, -(bb[1] + bb[4]) / 2, -bb[2])), n_, e) for q, n_, e in parts]

def attach_sleeve(parts, sleeve):
    """Stand the sleeve beside the host's spine side (canonical -x), half way along, on the bed."""
    bb = U([q for q, n_, e in parts]).bounding_box(); sb = sleeve[0].bounding_box()
    sx = bb[0] - SLEEVE_GAP - sb[3]; sy = (bb[1] + bb[4]) / 2 - (sb[1] + sb[4]) / 2
    return parts + [(sleeve[0].translate((sx, sy, bb[2] - sb[2])), sleeve[1], sleeve[2])]   # on the bed with its host

def hull2d(parts):
    pts = []
    for q, n_, e in parts:
        mm = q.to_mesh(); v = np.asarray(mm.vert_properties)[:, :2]; pts.append(v)
    return MultiPoint(np.vstack(pts)).convex_hull

def body_slot(parts): return parts[0][2]

def plan(A, B):
    """Objects: [cover A, tray A, cover B, tray B]; each sleeve rides with a same-coloured object (prefer its own design)."""
    objs = {'cA': list(A['cover']), 'tA': list(A['tray']), 'cB': list(B['cover']), 'tB': list(B['tray'])}
    order = [('tA', 'cA', 'tB', 'cB'), ('tB', 'cB', 'tA', 'cA')]
    for sl, pref in ((A['sleeve'], order[0]), (B['sleeve'], order[1])):
        host = next((h for h in pref if body_slot(objs[h]) == sl[2]), None)
        assert host is not None, f'no object in this pair has the colour of {sl[1]}'
        objs[host] = attach_sleeve(objs[host], sl)
    return objs

def layout(objs):
    """Pinwheel: cover A portrait (bottom-left), tray A landscape (bottom-right), cover B landscape (top-left), tray B portrait (top-right)."""
    rot = {'cA': 0, 'tA': 90, 'cB': 90, 'tB': 0}
    H = {k: affinity.rotate(hull2d(centre(v)), rot[k], origin=(0, 0)) for k, v in objs.items()}
    bx = {k: h.bounds for k, h in H.items()}
    w = lambda k: bx[k][2] - bx[k][0]; h = lambda k: bx[k][3] - bx[k][1]
    pos = {}                                                    # bbox min corner of each rotated object
    pos['cA'] = (0.0, 0.0)
    pos['tA'] = (w('cA') + GAP, 0.0)
    pos['cB'] = (0.0, h('cA') + GAP)
    pos['tB'] = (pos['cB'][0] + w('cB') + GAP, pos['tA'][1] + h('tA') + GAP)   # right of cover B, above tray A (cover A is diagonal)
    W_ = max(pos[k][0] + w(k) for k in pos); H_ = max(pos[k][1] + h(k) for k in pos)
    ox, oy = (BED - W_) / 2, (BED - H_) / 2
    place = {}
    for k in pos:   # translation of the object's (centred, rotated) origin
        place[k] = (ox + pos[k][0] - bx[k][0], oy + pos[k][1] - bx[k][1])
    world = {k: affinity.translate(H[k], *place[k]) for k in H}
    ks = list(world)
    dmin = min(world[a].distance(world[b]) for i, a in enumerate(ks) for b in ks[i + 1:])
    gb = [min(world[k].bounds[0] for k in ks), min(world[k].bounds[1] for k in ks), max(world[k].bounds[2] for k in ks), max(world[k].bounds[3] for k in ks)]
    assert dmin >= 73.0, dmin
    assert gb[0] >= BRIM + 1 and gb[1] >= BRIM + 1 and gb[2] <= BED - BRIM - 1 and gb[3] <= BED - BRIM - 1, gb
    return rot, place, dmin, gb

def transform(rot, x, y):
    c, s = (1, 0) if rot == 0 else (0, 1)        # 90 deg about z: x' = -y, y' = x
    # 3MF: m00 m01 m02 m10 m11 m12 m20 m21 m22 tx ty tz, row vectors (p' = p M)
    return f'{c} {s} 0 {-s} {c} 0 0 0 1 {x:.3f} {y:.3f} 0'

def export_pair(kA, kB, initials, out, orig):
    os.makedirs(out, exist_ok=True)
    A, B = design_parts(kA, initials), design_parts(kB, initials)
    objs = plan(A, B)
    rot, place, dmin, gb = layout(objs)
    names = {'cA': f'{A["cfg"]["name"]} cover', 'tA': f'{A["cfg"]["name"]} tray', 'cB': f'{B["cfg"]["name"]} cover', 'tB': f'{B["cfg"]["name"]} tray'}
    for k in objs:
        if any('sleeve' in n_ for q, n_, e in objs[k]): names[k] += ' + sleeve'
    files, rels, res, build, sets, inst = {}, [], [], [], [], []
    pid, top, ident = 1, 1000, 300
    pr = FINAL
    for k in ('cA', 'tA', 'cB', 'tB'):                         # object-list order = by-object print order
        parts = centre(objs[k]); comps, pcfg = [], []
        for i, (man, nm, ext) in enumerate(parts):
            path = f'3D/Objects/object_{pid}.model'; files[path] = v6_final.model_xml(pid, man); rels.append(path)
            comps.append(f'    <component p:path="/{path}" objectid="{pid}" p:UUID="{uuid.uuid4()}" transform="1 0 0 0 1 0 0 0 1 0 0 0" />')
            pcfg.append(f'    <part id="{pid}" subtype="normal_part">\n      <metadata key="name" value="{nm} {i}"/>\n'
                        f'      <metadata key="matrix" value="1 0 0 0 0 1 0 0 0 0 1 0 0 0 0 1"/>\n      <metadata key="extruder" value="{ext}"/>\n    </part>')
            pid += 1
        top += 1; ident += 1
        res.append(f'  <object id="{top}" p:UUID="{uuid.uuid4()}" type="model">\n   <components>\n' + '\n'.join(comps) + '\n   </components>\n  </object>')
        build.append(f'  <item objectid="{top}" p:UUID="{uuid.uuid4()}" transform="{transform(rot[k], *place[k])}" printable="1" />')
        sets.append(f'  <object id="{top}">\n    <metadata key="name" value="{names[k]}"/>\n    <metadata key="extruder" value="{parts[0][2]}"/>\n'
                    f'    <metadata key="sparse_infill_density" value="{pr["sparse_infill_density"]}"/>\n    <metadata key="sparse_infill_pattern" value="gyroid"/>\n'
                    f'    <metadata key="wall_loops" value="{pr["wall_loops"]}"/>\n    <metadata key="flush_into_infill" value="1"/>\n' +
                    '\n'.join(pcfg) + '\n  </object>')
        inst.append(f'    <model_instance>\n      <metadata key="object_id" value="{top}"/>\n      <metadata key="instance_id" value="0"/>\n'
                    f'      <metadata key="identify_id" value="{ident}"/>\n    </model_instance>')
    nA, nB = A['cfg']['name'].title(), B['cfg']['name'].title()
    stem = ('AB_' if initials else '') + f'Rollie_Book_wood_{nA}_{nB}_A1' + ('' if initials else '_no_initials')
    title = f'{"AB " if initials else ""}Rollie Book wood PLA: {nA} + {nB} - A1, one plate, by object, 0.16 mm High Quality'
    woods = ', '.join(f'{i + 1} {w.title()}' for i, w in enumerate(SLOTS))
    desc = (f'Two slim rollie cases (65x13.5x88 mm) in wood PLA: {A["cfg"]["craft"]}; {B["cfg"]["craft"]}. A1 + AMS lite slots: {woods}. '
            'No pauses: glue 4 x Ø5x2 mm magnets per case into the open pockets after printing (cover marked face UP, tray marked face DOWN). '
            'Hinge pin: 1.75 mm PETG filament. No supports. Each hinge sleeve is printed in its own accent wood, beside a part of the same colour.')
    files['3D/3dmodel.model'] = ('<?xml version="1.0" encoding="UTF-8"?>\n<model unit="millimeter" xml:lang="en-US" xmlns="http://schemas.microsoft.com/3dmanufacturing/core/2015/02" '
        'xmlns:BambuStudio="http://schemas.bambulab.com/package/2021" xmlns:p="http://schemas.microsoft.com/3dmanufacturing/production/2015/06" requiredextensions="p">\n'
        ' <metadata name="Application">BambuStudio-01.10.02.76</metadata>\n <metadata name="BambuStudio:3mfVersion">1</metadata>\n'
        f' <metadata name="Title">{title}</metadata>\n <metadata name="Description">{desc}</metadata>\n'
        ' <resources>\n' + '\n'.join(res) + '\n </resources>\n <build>\n' + '\n'.join(build) + '\n </build>\n</model>\n')
    files['3D/_rels/3dmodel.model.rels'] = ('<?xml version="1.0" encoding="UTF-8"?>\n<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">\n' +
        '\n'.join(f' <Relationship Target="/{q}" Id="rel-{i+1}" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/>' for i, q in enumerate(rels)) + '\n</Relationships>\n')
    files['Metadata/model_settings.config'] = ('<?xml version="1.0" encoding="UTF-8"?>\n<config>\n' + '\n'.join(sets) +
        f'\n  <plate>\n    <metadata key="plater_id" value="1"/>\n    <metadata key="plater_name" value="{nA} + {nB}"/>\n'
        '    <metadata key="locked" value="false"/>\n    <metadata key="print_sequence" value="by object"/>\n' + '\n'.join(inst) + '\n  </plate>\n</config>\n')
    tmpl = json.load(open(f'{orig}/Metadata/project_settings.config'))
    base_lc = tmpl['layer_change_gcode'].split('\n{if (current_object_idx')[0]
    overrides = dict(FINAL, layer_change_gcode=base_lc)
    cfg, _src = a1_safe.project_config(tmpl, [W.WOOD[w].upper() for w in SLOTS], overrides, fil_name=FIL, flush=FLUSH, proc_name=FINAL_PRESET)
    probs = a1_safe.check(cfg, tmpl); assert not probs, probs
    files['Metadata/project_settings.config'] = json.dumps(cfg, indent=4)
    files['[Content_Types].xml'] = open(f'{orig}/[Content_Types].xml').read()
    files['_rels/.rels'] = ('<?xml version="1.0" encoding="UTF-8"?>\n<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">\n'
                            ' <Relationship Target="/3D/3dmodel.model" Id="rel-1" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/>\n</Relationships>\n')
    fn = f'{out}/{stem}.3mf'
    with zipfile.ZipFile(fn, 'w', zipfile.ZIP_DEFLATED) as z:
        for k_, v_ in files.items(): z.writestr(k_, v_)
    return fn, dict(dmin=round(dmin, 1), extent=[round(v, 1) for v in gb], names=[names[k] for k in ('cA', 'tA', 'cB', 'tB')],
                    chk={kA: A['chk'], kB: B['chk']})

if __name__ == '__main__':
    out, orig, kA, kB, ini = sys.argv[1:6]
    fn, info = export_pair(kA, kB, ini == 'initials', out, orig)
    print(fn)
    print('objects (print order):', ' | '.join(info['names']))
    print('min hull gap', info['dmin'], 'mm (A1 needs > 72.8) | plate extent', info['extent'])
    for k, c in info['chk'].items():
        print(k, {q: c[q] for q in ('env', 'pieces', 'overlap', 'pocket_material', 'rollups_vs_tray', 'swing_contacts', 'magnet_gap')})
