"""A1 by-object test slice in PrusaSlicer: sequential printing, A1 clearance (73 mm / 25 mm), no wipe tower (A1 purges to its chute).
v7.1: 100% infill, concentric top surfaces, 4 mm brim, and the same layer-change magnet-pause block as the Bambu 3MF."""
import sys, os, re, json, subprocess
sys.path.insert(0, os.path.dirname(__file__))
import v7, slicetest as ST, v7_a1_export as AX, a1_profile as A
OUT = sys.argv[1]; os.makedirs(OUT, exist_ok=True)
r = v7.build()
p1, p2, p3 = ST.plate(r)[:3]
pos = AX.layout()
objs = [(p1[0][0], p1[0][1], pos['cover']), (p2[0][0], p2[0][1], pos['tray']), (p3[0][0], p3[0][1], pos['sleeve'])]
ST.prusa_3mf(f'{OUT}/a1_one_plate.3mf', objs, [])
m = A.resolve('machine', 'Bambu Lab A1 0.4 nozzle'); pr = A.resolve('process', '0.16mm High Quality @BBL A1'); f = A.resolve('filament', 'Bambu PETG HF @BBL A1')
s = lambda v: (v[0] if isinstance(v, list) else v)
ini = f'{OUT}/a1_hq_petghf_0.16.ini'; ST.config(0.16, ini)
txt = open(ini).read()
rep = {'wipe_tower': '0', 'complete_objects': '1', 'extruder_clearance_radius': s(m.get('extruder_clearance_max_radius', 73)),
       'extruder_clearance_height': s(m.get('extruder_clearance_height_to_rod', 25)),
       'machine_max_acceleration_extruding': f"{s(m['machine_max_acceleration_extruding'])},{s(m['machine_max_acceleration_extruding'])}",
       'machine_max_acceleration_x': f"{s(m['machine_max_acceleration_x'])},{s(m['machine_max_acceleration_x'])}",
       'machine_max_acceleration_y': f"{s(m['machine_max_acceleration_y'])},{s(m['machine_max_acceleration_y'])}",
       'external_perimeter_speed': s(pr['outer_wall_speed']), 'perimeter_speed': s(pr['inner_wall_speed']), 'infill_speed': s(pr['sparse_infill_speed']),
       'top_solid_infill_speed': s(pr['top_surface_speed']), 'external_perimeter_acceleration': s(pr['outer_wall_acceleration']),
       'default_acceleration': s(pr['default_acceleration']), 'temperature': '240,240,240', 'first_layer_temperature': '240,240,240',
       'filament_load_time': f"{s(m['machine_load_filament_time'])},"*2 + f"{s(m['machine_load_filament_time'])}",
       'filament_unload_time': f"{s(m['machine_unload_filament_time'])},"*2 + f"{s(m['machine_unload_filament_time'])}",
       'filament_max_volumetric_speed': ','.join(AX.MAXVOL),
       'fill_density': '100%', 'fill_pattern': 'rectilinear', 'top_fill_pattern': 'concentric', 'brim_width': f'{AX.BRIM:g}', 'brim_type': 'outer_only',
       'layer_gcode': 'G92 E0' + AX.pause_block(r['pause_cover_z'], r['pause_tray_z'], chime=False).replace('\n', '\\n')}
for k, v in rep.items():
    if re.search(rf'^{k} = ', txt, flags=re.M): txt = re.sub(rf'^{k} = .*$', lambda _m, k=k, v=v: f'{k} = {v}', txt, flags=re.M)
    else: txt += f'{k} = {v}\n'
open(ini, 'w').write(txt)
gc = f'{OUT}/a1_one_plate_0.16.gcode'
res = ST.slice_one(f'{OUT}/a1_one_plate.3mf', ini, gc)
if res.returncode != 0: print('SLICE FAILED', (res.stdout + res.stderr)[-2000:]); sys.exit(1)
rep_ = ST.report(gc); rep_.pop('zs')
warn = [l for l in (res.stdout + res.stderr).splitlines() if re.search(r'warn|error', l, re.I)]
gtxt = open(gc).read().split('\n'); obj, hits = None, []
for i, l in enumerate(gtxt):
    m_ = re.match(r'M486 S(\d+)', l) or re.match(r'; printing object (.+)', l)
    if m_: obj = m_.group(1)
    if l.startswith('M400 U1'):
        z_ = [float(q) for q in re.findall(r'^;Z:([\d.]+)', '\n'.join(gtxt[max(0, i - 400):i]), flags=re.M)]
        hits.append((obj, z_[-1] if z_ else None))
print('magnet pauses (object, layer z):', hits)
print(json.dumps(dict(**rep_, warnings=warn[:4], settings={k: rep[k] for k in ('extruder_clearance_radius', 'extruder_clearance_height', 'external_perimeter_speed', 'external_perimeter_acceleration', 'default_acceleration')})))
