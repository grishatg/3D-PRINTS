"""Wood-PLA print projects for a Bambu Lab A1 + AMS lite (v10.6). Fixed AMS slots: 1 Oak, 2 Teak, 3 Cherry (unused since the owner
ran out, 25 Nov), 4 Walnut.

TWO designs (cover + tray each) in ONE project, ONE plate, print by object, no pauses (magnets are glued in flush after
printing). 4 objects in a pinwheel, every pair of objects >= 74 mm apart hull to hull (Bambu's by-object check for the A1: each
convex hull grows by extruder_clearance_max_radius / 2 = 36.4 mm). Pairs: KUMIKO + DIAL, RIVA + PARQUET, ENDGRAIN + CUBES.
v10.6: no hinge sleeve and no sleeve plate: the middle knuckle is part of the tray (3 knuckles on the back, 2 on the lid).

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
BRIM = 3.0           # margin kept round the plate (the files have no brim since v10.6; the layout is unchanged)
def face_settings(key, kind, rot, initials):
    """Per-object settings for the plate-side face (v10.6, owner: "make it so the layers don't show up ... the side where it touches
    the plate, the ones with cubes and squares"). The first print showed four wall rings and a centre dot inside every inlaid cell.
    - infill_direction: the straight first-layer lines run ALONG the case (bed angle = 90 - the object's turn on the plate), so what
      shows of them reads as wood grain; PARQUET keeps 45 (parallel / square to its staves).
    - only_one_wall_first_layer ('lines' in W.DESIGNS[key]['face']): one outline per cell + those lines, no rings. Never on a tray
      with initials: an inlaid A·B needs its four variable-width walls to fill every letter stroke (checked as sliced)."""
    d = {'infill_direction': '45' if key == 'parquet' else str(int((90 - rot) % 180))}
    mode = W.DESIGNS[key]['face'][0 if kind == 'c' else 1]
    if mode == 'lines' and (kind == 'c' or not initials): d['only_one_wall_first_layer'] = '1'
    if os.environ.get('FACE_FORCE') == 'walls': d.pop('only_one_wall_first_layer', None)      # comparison builds only
    return d
slot = lambda wood: SLOTS.index(wood) + 1
U = lambda vs: m3.Manifold.batch_boolean(vs, m3.OpType.Add) if len(vs) > 1 else vs[0]

def design_parts(key, initials):
    """Cover / tray parts in print orientation (canonical frame: spine at -x, length along y)."""
    v7.MAGNET_MODE = 'glue'
    v7.PRINT_LAYER = float(FINAL['layer_height'])        # glue-pocket floors snap to the print's own layer grid
    cfgd = W.DESIGNS[key]
    r, chk, _parts, fil = W.build(key, initials)
    bad = {k: chk[k] for k in ('pieces', 'overlap', 'pocket_material', 'rollups_vs_tray', 'swing_contacts') if
           (k == 'pieces' and chk[k] != (1, 1)) or (k in ('overlap', 'rollups_vs_tray') and abs(chk[k]) > 1e-3) or
           (k == 'pocket_material' and max(abs(v) for v in chk[k]) > 1e-3) or (k == 'swing_contacts' and chk[k])}
    assert not bad, (key, bad)
    assert r['sleeve'] is None, 'v10.6: the middle knuckle belongs to the tray, there is no sleeve part'
    tray_rot = lambda m: m.rotate((-90, 0, 0)); cover_rot = lambda m: m.rotate((90, 0, 0))
    N = cfgd['name']
    cov = [(cover_rot(r['cover']), f'{N} lid ({cfgd["cover"]})', slot(cfgd['cover']))] + \
          [(cover_rot(y), f'{N} inlay ({cfgd[a]})', slot(cfgd[a])) for y, p, a in r['acc'] if p == 'c']
    tra = [(tray_rot(r['tray']), f'{N} tray ({cfgd["tray"]})', slot(cfgd['tray']))] + \
          [(tray_rot(y), f'{N} inlay ({cfgd[a]})', slot(cfgd[a])) for y, p, a in r['acc'] if p == 't']
    if r.get('y4') is not None: tra.append((tray_rot(r['y4']), f'{N} A·B ({cfgd["mono"]})', slot(cfgd['mono'])))
    return dict(cover=cov, tray=tra, chk=chk, cfg=cfgd)

def centre(parts):
    bb = U([q for q, n_, e in parts]).bounding_box()
    return [(q.translate((-(bb[0] + bb[3]) / 2, -(bb[1] + bb[4]) / 2, -bb[2])), n_, e) for q, n_, e in parts]

def hull2d(parts):
    return MultiPoint(np.vstack([np.asarray(q.to_mesh().vert_properties)[:, :2] for q, n_, e in parts])).convex_hull

def check_layout(H, place):
    world = {k: affinity.translate(H[k], *place[k]) for k in H}
    ks = list(world)
    dmin = min(world[a].distance(world[b]) for i, a in enumerate(ks) for b in ks[i + 1:])
    gb = [min(world[k].bounds[0] for k in ks), min(world[k].bounds[1] for k in ks), max(world[k].bounds[2] for k in ks), max(world[k].bounds[3] for k in ks)]
    assert dmin >= 73.0, dmin
    assert gb[0] >= BRIM + 1 and gb[1] >= BRIM + 1 and gb[2] <= BED - BRIM - 1 and gb[3] <= BED - BRIM - 1, gb
    return dmin, gb

def pinwheel(objs):
    """Cover A portrait (bottom-left), tray A landscape (bottom-right), cover B landscape (top-left), tray B portrait (top-right)."""
    rot = {'cA': 0, 'tA': 90, 'cB': 90, 'tB': 0}
    H = {k: affinity.rotate(hull2d(centre(v)), rot[k], origin=(0, 0)) for k, v in objs.items()}
    bx = {k: h.bounds for k, h in H.items()}
    w = lambda k: bx[k][2] - bx[k][0]; h = lambda k: bx[k][3] - bx[k][1]
    pos = {'cA': (0.0, 0.0), 'tA': (w('cA') + GAP, 0.0), 'cB': (0.0, h('cA') + GAP)}
    pos['tB'] = (pos['cB'][0] + w('cB') + GAP, pos['tA'][1] + h('tA') + GAP)   # right of cover B, above tray A (cover A is diagonal)
    W_ = max(pos[k][0] + w(k) for k in pos); H_ = max(pos[k][1] + h(k) for k in pos)
    ox, oy = (BED - W_) / 2, (BED - H_) / 2
    place = {k: (ox + pos[k][0] - bx[k][0], oy + pos[k][1] - bx[k][1]) for k in pos}
    dmin, gb = check_layout(H, place)
    return rot, place, dmin, gb

def transform(rot, x, y):
    c, s = (1, 0) if rot == 0 else (0, 1)        # 90 deg about z: x' = -y, y' = x
    # 3MF: m00 m01 m02 m10 m11 m12 m20 m21 m22 tx ty tz, row vectors (p' = p M)
    return f'{c} {s} 0 {-s} {c} 0 0 0 1 {x:.3f} {y:.3f} 0'

def write_project(out, orig, stem, title, desc, plate_name, order):
    """order: [(object name, parts, rot, (x, y), {extra per-object settings})] in print order."""
    files, rels, res, build, sets, inst = {}, [], [], [], [], []
    pid, top, ident = 1, 1000, 300
    pr = FINAL
    for name, parts, rot, (px, py), extra in order:
        parts = centre(parts); comps, pcfg = [], []
        for i, (man, nm, ext) in enumerate(parts):
            path = f'3D/Objects/object_{pid}.model'; files[path] = v6_final.model_xml(pid, man); rels.append(path)
            comps.append(f'    <component p:path="/{path}" objectid="{pid}" p:UUID="{uuid.uuid4()}" transform="1 0 0 0 1 0 0 0 1 0 0 0" />')
            pcfg.append(f'    <part id="{pid}" subtype="normal_part">\n      <metadata key="name" value="{nm} {i}"/>\n'
                        f'      <metadata key="matrix" value="1 0 0 0 0 1 0 0 0 0 1 0 0 0 0 1"/>\n      <metadata key="extruder" value="{ext}"/>\n    </part>')
            pid += 1
        top += 1; ident += 1
        res.append(f'  <object id="{top}" p:UUID="{uuid.uuid4()}" type="model">\n   <components>\n' + '\n'.join(comps) + '\n   </components>\n  </object>')
        build.append(f'  <item objectid="{top}" p:UUID="{uuid.uuid4()}" transform="{transform(rot, px, py)}" printable="1" />')
        sets.append(f'  <object id="{top}">\n    <metadata key="name" value="{name}"/>\n    <metadata key="extruder" value="{parts[0][2]}"/>\n'
                    f'    <metadata key="sparse_infill_density" value="{pr["sparse_infill_density"]}"/>\n    <metadata key="sparse_infill_pattern" value="gyroid"/>\n'
                    f'    <metadata key="wall_loops" value="{pr["wall_loops"]}"/>\n    <metadata key="flush_into_infill" value="1"/>\n' +
                    ''.join(f'    <metadata key="{k_}" value="{v_}"/>\n' for k_, v_ in extra.items()) +
                    '\n'.join(pcfg) + '\n  </object>')
        inst.append(f'    <model_instance>\n      <metadata key="object_id" value="{top}"/>\n      <metadata key="instance_id" value="0"/>\n'
                    f'      <metadata key="identify_id" value="{ident}"/>\n    </model_instance>')
    files['3D/3dmodel.model'] = ('<?xml version="1.0" encoding="UTF-8"?>\n<model unit="millimeter" xml:lang="en-US" xmlns="http://schemas.microsoft.com/3dmanufacturing/core/2015/02" '
        'xmlns:BambuStudio="http://schemas.bambulab.com/package/2021" xmlns:p="http://schemas.microsoft.com/3dmanufacturing/production/2015/06" requiredextensions="p">\n'
        ' <metadata name="Application">BambuStudio-01.10.02.76</metadata>\n <metadata name="BambuStudio:3mfVersion">1</metadata>\n'
        f' <metadata name="Title">{title}</metadata>\n <metadata name="Description">{desc}</metadata>\n'
        ' <resources>\n' + '\n'.join(res) + '\n </resources>\n <build>\n' + '\n'.join(build) + '\n </build>\n</model>\n')
    files['3D/_rels/3dmodel.model.rels'] = ('<?xml version="1.0" encoding="UTF-8"?>\n<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">\n' +
        '\n'.join(f' <Relationship Target="/{q}" Id="rel-{i+1}" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/>' for i, q in enumerate(rels)) + '\n</Relationships>\n')
    files['Metadata/model_settings.config'] = ('<?xml version="1.0" encoding="UTF-8"?>\n<config>\n' + '\n'.join(sets) +
        f'\n  <plate>\n    <metadata key="plater_id" value="1"/>\n    <metadata key="plater_name" value="{plate_name}"/>\n'
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
    os.makedirs(out, exist_ok=True)
    fn = f'{out}/{stem}.3mf'
    with zipfile.ZipFile(fn, 'w', zipfile.ZIP_DEFLATED) as z:
        for k_, v_ in files.items(): z.writestr(k_, v_)
    return fn

WOODS_TXT = ', '.join(f'{i + 1} {w.title()}' for i, w in enumerate(SLOTS))

def export_pair(kA, kB, initials, out, orig):
    A, B = design_parts(kA, initials), design_parts(kB, initials)
    objs = {'cA': list(A['cover']), 'tA': list(A['tray']), 'cB': list(B['cover']), 'tB': list(B['tray'])}
    rot, place, dmin, gb = pinwheel(objs)
    names = {'cA': f'{A["cfg"]["name"]} cover', 'tA': f'{A["cfg"]["name"]} tray', 'cB': f'{B["cfg"]["name"]} cover', 'tB': f'{B["cfg"]["name"]} tray'}
    nA, nB = A['cfg']['name'].title(), B['cfg']['name'].title()
    stem = ('AB_' if initials else '') + f'Rollie_Book_wood_{nA}_{nB}_A1' + ('' if initials else '_no_initials')
    title = f'{"AB " if initials else ""}Rollie Book wood PLA: {nA} + {nB} - A1, one plate, by object, 0.12 mm High Quality'
    desc = (f'Two slim rollie cases (65x13.5x88 mm) in wood PLA: {A["cfg"]["craft"]}; {B["cfg"]["craft"]}. A1 + AMS lite slots: {WOODS_TXT}. '
            'No pauses: glue 4 x Ø5x2 mm magnets per case flush into the pockets after printing (lid marked face UP, tray marked face DOWN). '
            'Hinge: 3 knuckles on the tray, 2 on the lid, nothing else to print; push an 88 mm length of 1.75 mm filament through as the pin. No supports.')
    extra = {k: face_settings(kA if k[1] == 'A' else kB, k[0], rot[k], initials) for k in ('cA', 'tA', 'cB', 'tB')}
    fn = write_project(out, orig, stem, title, desc, f'{nA} + {nB}', [(names[k], objs[k], rot[k], place[k], extra[k]) for k in ('cA', 'tA', 'cB', 'tB')])
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
