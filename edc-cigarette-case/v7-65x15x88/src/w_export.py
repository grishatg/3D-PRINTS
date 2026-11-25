"""Bambu Studio 3MFs for the wood-PLA designs (v10 inside) on a Bambu Lab A1 + AMS lite: one plate, print by object.
Fixed AMS slots for every design: 1 Oak, 2 Teak, 3 Cherry, 4 Walnut (load once, print any design).
Profiles:
  production : magnets sealed in (Ø5 x 2, 0.8 mm over each), the printer chimes and pauses itself once per half; 15% gyroid
  test       : magnets GLUED after printing (pockets open, magnets sit where they will be sealed), no pauses, lighter settings
Usage: python3 src/w_export.py <out_dir> <template_dir> <design> <initials|noinit> <production|test>
"""
import os, sys, json, uuid, zipfile
os.environ.setdefault('PLATFORM', 'v10')
sys.path.insert(0, os.path.dirname(__file__))
import w_concepts as W      # FIRST: it (via v8/v9_concepts) sets the wood platform's env (squircle R4.5, crescent, pinch, back mark) before v7 is imported
import v7, v6_final, a1_safe, manifold3d as m3
from v7_a1_export import layout, pause_block
PLATFORM_FLAGS = ('v10', 'squircle', 4.5, 11.0, 4.0, True, True, 'back')
assert (v7.PLATFORM, v7.OUTLINE, v7.EDGE_R, v7.CORNER_OPEN, v7.CORNER_SPINE, v7.CRESCENT, v7.PINCH, v7.INITIALS_POS) == PLATFORM_FLAGS, \
    ('wrong platform env', v7.PLATFORM, v7.OUTLINE, v7.EDGE_R, v7.CORNER_OPEN, v7.CORNER_SPINE, v7.CRESCENT, v7.PINCH, v7.INITIALS_POS)

SLOTS = ['oak', 'teak', 'cherry', 'walnut']
FIL = 'Bambu PLA Wood @BBL A1'
# purge (mm3), row = from, column = to: dark -> light needs the most
FLUSH = [[0, 120, 140, 140],
         [220, 0, 130, 130],
         [380, 300, 0, 160],
         [360, 280, 160, 0]]
# test prints: minimum waste (owner, 24 Nov). Light -> dark at Bambu's suggested floor (~50: the dark wood hides the oak left in the
# 92 mm3 melt zone); dark -> light kept at 100-150 so the oak seams / marks don't come out muddy. ~60 % less purge than FLUSH.
FLUSH_LEAN = [[0, 50, 50, 50],
              [100, 0, 50, 50],
              [150, 110, 0, 60],
              [150, 110, 60, 0]]
# FINAL print profile (owner, 24 Nov: "leave 6h if needed but make quality builds", overnight, 2 designs per plate; the hinge
# sleeves print on their own plate in the morning). Bambu's own 0.12mm High Quality @BBL A1 preset plus: 4 walls, 1.0 mm top
# skin, 0.8 mm bottom skin, slow narrow first layer (the visible face: crisp inlays), scarf seams, no wall crossing.
# (A 0.16 version fitted a 4.5 h / 5 h limit; trials then: 3 walls is slower than 4, a faster first layer saves ~1 min.)
FINAL_PRESET = '0.12mm High Quality @BBL A1'
FINAL = {'layer_height': '0.12', 'initial_layer_print_height': '0.2', 'wall_generator': 'arachne', 'elefant_foot_compensation': '0.15',
         'enable_support': '0', 'enable_prime_tower': '0', 'print_sequence': 'by object', 'curr_bed_type': 'Textured PEI Plate',
         'sparse_infill_pattern': 'gyroid', 'sparse_infill_density': '15%', 'top_surface_pattern': 'concentric',
         'wall_loops': '4', 'top_shell_layers': '8', 'top_shell_thickness': '1.0', 'bottom_shell_layers': '6',
         'initial_layer_speed': '40', 'initial_layer_infill_speed': '80', 'initial_layer_line_width': '0.42',
         'reduce_crossing_wall': '1',
         # v10.6 (owner, 25 Nov): no brim ("why does it need a brim?": every part sits on the plate with its whole face, and the
         # first full print stuck well), and the plate-side faces "show the layers" (rings inside every square / cube where
         # the first layer went down a little high, near the front and back of the bed): 5 % more plastic on the first layer;
         # the faces are laid as one outline + straight lines along the case instead of four rings per cell (per object,
         # see w_pair_export.face_settings).
         'brim_type': 'no_brim', 'initial_layer_flow_ratio': '1.05',
         'filament_scarf_seam_type': ['external'] * 4}
if os.environ.get('WOOD_PROFILE_TRIAL'): FINAL.update(json.loads(os.environ['WOOD_PROFILE_TRIAL']))   # timing trials only
PROFILES = {
    'production': dict(wall_loops='3', top_shell_layers='5', bottom_shell_layers='4', sparse_infill_density='15%', brim_type='outer_only', brim_width='3'),
    # test: ~15% less filament, ~10 min quicker. Same outside look; thinner inner shells (Bambu's 1.0 mm top-shell minimum -> 0.8 mm)
    'test':       dict(wall_loops='2', top_shell_layers='5', top_shell_thickness='0.8', bottom_shell_layers='3', sparse_infill_density='10%', brim_type='outer_only', brim_width='3'),
}

def export(key, initials, profile, out, orig, geometry_only=False):
    raise SystemExit('w_export.export is superseded: since v10.6 the wood designs have no sleeve part (the middle hinge knuckle is on the tray). '
                     'Use src/w_pair_export.py. This module is kept for its shared settings (SLOTS, FIL, FLUSH, FINAL).')
    os.makedirs(out, exist_ok=True)
    v7.MAGNET_MODE = 'glue' if profile == 'test' else 'embed'
    cfgd = W.DESIGNS[key]
    r, chk, _parts, fil = W.build(key, initials)
    slot = lambda wood: SLOTS.index(wood) + 1
    U = lambda vs: m3.Manifold.batch_boolean(vs, m3.OpType.Add) if len(vs) > 1 else vs[0]
    tray_rot = lambda m: m.rotate((-90, 0, 0)); cover_rot = lambda m: m.rotate((90, 0, 0))
    def drop(parts):
        bb = U([q for q, n_, e in parts]).bounding_box()
        return [(q.translate((-(bb[0] + bb[3]) / 2, -(bb[1] + bb[4]) / 2, -bb[2])), n_, e) for q, n_, e in parts]
    cov = [(cover_rot(r['cover']), f'{cfgd["cover"]} lid', slot(cfgd['cover']))] + \
          [(cover_rot(y), f'{cfgd[a]} inlay', slot(cfgd[a])) for y, p, a in r['acc'] if p == 'c']
    tra = [(tray_rot(r['tray']), f'{cfgd["tray"]} tray', slot(cfgd['tray']))] + \
          [(tray_rot(y), f'{cfgd[a]} inlay', slot(cfgd[a])) for y, p, a in r['acc'] if p == 't']
    if r.get('y4') is not None: tra.append((tray_rot(r['y4']), f'{cfgd["mono"]} A·B', slot(cfgd['mono'])))
    pos = layout()
    objs = [('Cover', drop(cov), pos['cover'], slot(cfgd['cover'])), ('Tray', drop(tra), pos['tray'], slot(cfgd['tray'])),
            ('Spine sleeve', drop([(r['sleeve'], f'{cfgd["sleeve"]} sleeve', slot(cfgd['sleeve']))]), pos['sleeve'], slot(cfgd['sleeve']))]
    files, rels, res, build, sets, inst, hulls = {}, [], [], [], [], [], {}
    pid, top, ident = 1, 1000, 300
    for name, parts, (px, py), oext in objs:
        comps, pcfg = [], []
        bb = U([q for q, n_, e in parts]).bounding_box()
        hulls[name] = (px + bb[0], py + bb[1], px + bb[3], py + bb[4], bb[5])
        for k, (man, nm, ext) in enumerate(parts):
            path = f'3D/Objects/object_{pid}.model'; files[path] = v6_final.model_xml(pid, man); rels.append(path)
            comps.append(f'    <component p:path="/{path}" objectid="{pid}" p:UUID="{uuid.uuid4()}" transform="1 0 0 0 1 0 0 0 1 0 0 0" />')
            pcfg.append(f'    <part id="{pid}" subtype="normal_part">\n      <metadata key="name" value="{nm} {k}"/>\n'
                        f'      <metadata key="matrix" value="1 0 0 0 0 1 0 0 0 0 1 0 0 0 0 1"/>\n      <metadata key="extruder" value="{ext}"/>\n    </part>')
            pid += 1
        top += 1; ident += 1
        res.append(f'  <object id="{top}" p:UUID="{uuid.uuid4()}" type="model">\n   <components>\n' + '\n'.join(comps) + '\n   </components>\n  </object>')
        build.append(f'  <item objectid="{top}" p:UUID="{uuid.uuid4()}" transform="1 0 0 0 1 0 0 0 1 {px:.3f} {py:.3f} 0" printable="1" />')
        pr = PROFILES[profile]
        sets.append(f'  <object id="{top}">\n    <metadata key="name" value="{name}"/>\n    <metadata key="extruder" value="{oext}"/>\n'
                    f'    <metadata key="sparse_infill_density" value="{pr["sparse_infill_density"]}"/>\n    <metadata key="sparse_infill_pattern" value="gyroid"/>\n'
                    f'    <metadata key="wall_loops" value="{pr["wall_loops"]}"/>\n' + ('    <metadata key="flush_into_infill" value="1"/>\n' if name != 'Spine sleeve' else '') +
                    '\n'.join(pcfg) + '\n  </object>')
        inst.append(f'    <model_instance>\n      <metadata key="object_id" value="{top}"/>\n      <metadata key="instance_id" value="0"/>\n'
                    f'      <metadata key="identify_id" value="{ident}"/>\n    </model_instance>')
    nm_ = cfgd['name'].title()
    stem = ('TEST_' if profile == 'test' else '') + ('AB_' if initials else '') + f'Rollie_Book_{nm_}_wood_A1' + ('' if initials else '_no_initials') + \
           ('_glue_magnets' if profile == 'test' else '')
    title = f'{"AB " if initials else ""}Rollie Book {nm_} (wood PLA){" TEST, glue-in magnets" if profile == "test" else ""} - A1 by object'
    woods = ', '.join(f'{i + 1} {w.title()}' for i, w in enumerate(SLOTS))
    if profile == 'test':
        mag = ('TEST PRINT: no pauses. Glue 4 x Ø5x2 mm magnets into the open pockets after printing (a drop of super glue at the bottom of each pocket). '
               'Stack the 4, mark the top of each: cover magnets marked face UP, tray magnets marked face DOWN.')
    else:
        mag = (f'4 x Ø5x2 mm magnets SEALED IN: the printer chimes and pauses once for the cover (z {r["pause_cover_z"]:.2f}) and once for the tray (z {r["pause_tray_z"]:.2f}): '
               'drop BOTH magnets in, press Resume. Stack the 4, mark the top of each: cover marked face UP, tray marked face DOWN.')
    desc = (f'Slim rollie case 65x13.5x88 mm in wood PLA ({cfgd["craft"]}). 6 channels (rollies/papers up to ~78 mm) + long filter-tip bay. '
            f'A1 + AMS lite slots: {woods}. {mag} Hinge pin: 1.75 mm PETG filament. No supports.')
    files['3D/3dmodel.model'] = ('<?xml version="1.0" encoding="UTF-8"?>\n<model unit="millimeter" xml:lang="en-US" xmlns="http://schemas.microsoft.com/3dmanufacturing/core/2015/02" '
        'xmlns:BambuStudio="http://schemas.bambulab.com/package/2021" xmlns:p="http://schemas.microsoft.com/3dmanufacturing/production/2015/06" requiredextensions="p">\n'
        ' <metadata name="Application">BambuStudio-01.10.02.76</metadata>\n <metadata name="BambuStudio:3mfVersion">1</metadata>\n'
        f' <metadata name="Title">{title}</metadata>\n <metadata name="Description">{desc}</metadata>\n'
        ' <resources>\n' + '\n'.join(res) + '\n </resources>\n <build>\n' + '\n'.join(build) + '\n </build>\n</model>\n')
    files['3D/_rels/3dmodel.model.rels'] = ('<?xml version="1.0" encoding="UTF-8"?>\n<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">\n' +
        '\n'.join(f' <Relationship Target="/{q}" Id="rel-{i+1}" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/>' for i, q in enumerate(rels)) + '\n</Relationships>\n')
    files['Metadata/model_settings.config'] = ('<?xml version="1.0" encoding="UTF-8"?>\n<config>\n' + '\n'.join(sets) +
        f'\n  <plate>\n    <metadata key="plater_id" value="1"/>\n    <metadata key="plater_name" value="Rollie Book {nm_} - by object"/>\n'
        '    <metadata key="locked" value="false"/>\n    <metadata key="print_sequence" value="by object"/>\n' + '\n'.join(inst) + '\n  </plate>\n</config>\n')
    tmpl = json.load(open(f'{orig}/Metadata/project_settings.config'))
    base_lc = tmpl['layer_change_gcode'].split('\n{if (current_object_idx')[0]
    overrides = {'layer_height': '0.16', 'initial_layer_print_height': '0.2', 'wall_generator': 'arachne', 'seam_position': 'back',
                 'elefant_foot_compensation': '0.15', 'enable_support': '0', 'enable_prime_tower': '0', 'print_sequence': 'by object',
                 'curr_bed_type': 'Textured PEI Plate', 'sparse_infill_pattern': 'gyroid', 'top_surface_pattern': 'concentric'}
    overrides.update(PROFILES[profile])
    overrides['layer_change_gcode'] = base_lc + (pause_block(r['pause_cover_z'], r['pause_tray_z']) if profile == 'production' else '')
    cfg, _src = a1_safe.project_config(tmpl, [W.WOOD[w].upper() for w in SLOTS], overrides, fil_name=FIL, flush=FLUSH_LEAN if profile == 'test' else FLUSH)
    probs = a1_safe.check(cfg, tmpl); assert not probs, probs
    if not geometry_only: files['Metadata/project_settings.config'] = json.dumps(cfg, indent=4)
    files['[Content_Types].xml'] = open(f'{orig}/[Content_Types].xml').read()
    files['_rels/.rels'] = ('<?xml version="1.0" encoding="UTF-8"?>\n<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">\n'
                            ' <Relationship Target="/3D/3dmodel.model" Id="rel-1" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/>\n</Relationships>\n')
    fn = f'{out}/{stem}' + ('_geometry_only' if geometry_only else '') + '.3mf'
    with zipfile.ZipFile(fn, 'w', zipfile.ZIP_DEFLATED) as z:
        for k, v in files.items(): z.writestr(k, v)
    return fn, hulls, cfg, r, chk, fil

if __name__ == '__main__':
    out, orig, key, ini, profile = sys.argv[1:6]
    fn, hulls, cfg, r, chk, fil = export(key, ini == 'initials', profile, out, orig)
    print(fn)
    print('checks', {k: chk[k] for k in ('env', 'pieces', 'overlap', 'pocket_material', 'pocket_unsealed', 'rollups_vs_tray', 'swing_contacts', 'magnet_gap', 'pauses')})
    names = list(hulls)
    def gap(a, b):
        ax0, ay0, ax1, ay1, _ = hulls[a]; bx0, by0, bx1, by1, _ = hulls[b]
        return round(((max(bx0 - ax1, ax0 - bx1, 0)) ** 2 + (max(by0 - ay1, ay0 - by1, 0)) ** 2) ** 0.5, 1)
    print('heights', {k: round(v[4], 2) for k, v in hulls.items()}, '| min gaps', {f'{a}|{b}': gap(a, b) for i, a in enumerate(names) for b in names[i + 1:]})
    print('filaments used', fil, '| slots', SLOTS, '| profile', profile, cfg['sparse_infill_density'], 'walls', cfg['wall_loops'], 'brim', cfg['brim_type'])
