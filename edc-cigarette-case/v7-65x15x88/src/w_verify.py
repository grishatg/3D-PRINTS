"""Verify a wood-PLA 3MF made by w_export.py, reading ONLY the file. Usage: python3 src/w_verify.py <file.3mf> <work_dir>
1  Bambu loader check (emulated from Bambu's source at v02.03.01.51 / v02.08.04.61 / v02.09.01.70) must match the baseline's 26 flags.
2  Settings: proven key set + order, 4 x Bambu PLA Wood @BBL A1, A1 0.4, by object, no prime tower, profile values as declared.
3  Plate: object order cover -> tray -> sleeve, meshes valid and on the bed, A1 by-object clearance (>= 73 mm hulls, < 25 mm tall).
4  Magnet pockets, from the meshes sliced layer by layer at the real layer heights (0.2 then 0.16):
     production: two Ø5.35 pockets open on every layer up to the pause and sealed from the pause layer; pocket fits Ø5 x 2.
     test (glue): two Ø5.35 pockets open from their floor right up to the closing face; floor at the production depth; no pause.
5  A1-emulated PrusaSlicer slice of the file's own meshes / filaments / positions (4 wood filaments, by object):
     time, grams per filament, toolchanges, layers, and every M400 U1 pause with the object and z it lands on."""
import sys, os, re, json, zipfile, subprocess, numpy as np, manifold3d as m3
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from shapely.geometry import Polygon
import a1_safe as S
F, WD = os.path.abspath(sys.argv[1]), os.path.abspath(sys.argv[2]); os.makedirs(WD, exist_ok=True)
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
ok = True
def chk(name, cond, info=''):
    global ok
    ok &= bool(cond); print(('PASS ' if cond else 'FAIL ') + name + (f'  [{info}]' if info else ''))

# ---- 1 loader
res = subprocess.run([sys.executable, f'{HERE}/bbsvalidate.py', F, 'v02.03.01.51', 'v02.08.04.61', 'v02.09.01.70'], capture_output=True, text=True, cwd=HERE)
base = open(f'{ROOT}/test-slice/bambu_loader_check_baseline.txt').read().splitlines()[:39]
chk('1 Bambu loader: identical to the 26-flag baseline at all 3 releases', res.stdout.splitlines() == base, ' '.join(re.findall(r'\d+ problem\(s\)', res.stdout)))
open(f'{WD}/bbs.txt', 'w').write(res.stdout)

# ---- 2 settings
z = zipfile.ZipFile(F)
chk('2 zip CRC', z.testzip() is None)
cfg = json.loads(z.read('Metadata/project_settings.config'))
ref = json.loads(zipfile.ZipFile(f'{ROOT}/superseded/v7.0-first-print/AB_Rollie_Book_v7_A1_by_object.3mf').read('Metadata/project_settings.config'))
chk('2 settings: same 366 keys, same order as the v7.0 file that opened in Bambu', list(cfg) == list(ref), f'{len(cfg)} keys')
chk('2 settings: all values strings / string lists', all(isinstance(v, str) or (isinstance(v, list) and all(isinstance(x, str) for x in v)) for v in cfg.values()))
n = len(cfg['filament_colour'])
chk('2 settings: 4 x Bambu PLA Wood @BBL A1 (GFA16), A1 0.4, by object, no prime tower, textured PEI',
    n == 4 and cfg['filament_settings_id'] == ['Bambu PLA Wood @BBL A1'] * 4 and cfg['filament_ids'] == ['GFA16'] * 4 and cfg['filament_type'] == ['PLA'] * 4
    and cfg['printer_settings_id'] == 'Bambu Lab A1 0.4 nozzle' and cfg['print_sequence'] == 'by object' and cfg['enable_prime_tower'] == '0'
    and cfg['curr_bed_type'] == 'Textured PEI Plate', f'colours {cfg["filament_colour"]}, nozzle {cfg["nozzle_temperature"][0]} C, bed {cfg["textured_plate_temp"][0]} C')
chk('2 settings: flush matrix 4 x 4, vector 8, different_settings_to_system 6', len(cfg['flush_volumes_matrix']) == 16 and len(cfg['flush_volumes_vector']) == 8 and len(cfg['different_settings_to_system']) == 6)
lg = cfg['layer_change_gcode']
pm = re.search(r'current_object_idx == 0 and layer_z > ([\d.]+) and layer_z < ([\d.]+)\) or \(current_object_idx == 1 and layer_z > ([\d.]+) and layer_z < ([\d.]+)', lg)
TEST = pm is None
prof = 'test (glue-in magnets)' if TEST else 'production (sealed magnets)'
print(f'     profile: {prof}; infill {cfg["sparse_infill_density"]} {cfg["sparse_infill_pattern"]}, walls {cfg["wall_loops"]}, top/bottom {cfg["top_shell_layers"]}/{cfg["bottom_shell_layers"]} (top min {cfg["top_shell_thickness"]} mm), brim {cfg["brim_type"]} {cfg["brim_width"]}')
if TEST:
    chk('2 test file: NO pause in the layer-change G-code', 'M400 U1' not in lg and 'PAUSE' not in lg and lg.startswith('; layer num/total_layer_count'))
else:
    chk('2 production file: pause block once, ends with M400 U1, chimes first', lg.count('M400 U1') == 1 and lg.count('{if') == lg.count('{endif}') == 1 and 'M1006 W' in lg and lg.startswith('; layer num/total_layer_count'))
    zc = (float(pm.group(1)) + float(pm.group(2))) / 2; zt = (float(pm.group(3)) + float(pm.group(4))) / 2

# ---- 3 plate
top = z.read('3D/3dmodel.model').decode(); ms = z.read('Metadata/model_settings.config').decode()
names = re.findall(r'<object id="\d+">\s*<metadata key="name" value="([^"]+)"', ms)
chk('3 object order cover -> tray -> sleeve (= by-object print order)', names == ['Cover', 'Tray', 'Spine sleeve'], ' / '.join(names))
def mesh(p):
    x = z.read(p.lstrip('/')).decode()
    V = np.array(re.findall(r'<vertex x="([^"]+)" y="([^"]+)" z="([^"]+)"', x), dtype=np.float32)
    T = np.array(re.findall(r'<triangle v1="(\d+)" v2="(\d+)" v3="(\d+)"', x), dtype=np.uint32)
    return m3.Manifold(m3.Mesh(vert_properties=V, tri_verts=T))
place = {o: (float(a), float(b)) for o, a, b in re.findall(r'<item objectid="(\d+)"[^>]*transform="1 0 0 0 1 0 0 0 1 ([-\d.]+) ([-\d.]+) 0"', top)}
objs = re.findall(r'<object id="(\d+)" p:UUID="[^"]+" type="model">\s*<components>(.*?)</components>', top, flags=re.S)
hull, body, prusa, used = {}, {}, [], set()
for oid, comp in objs:
    oset = re.search(rf'<object id="{oid}">(.*?)</object>', ms, flags=re.S).group(1)
    name = re.search(r'<metadata key="name" value="([^"]+)"', oset).group(1)
    parts = []
    for path, pid in re.findall(r'p:path="([^"]+)" objectid="(\d+)"', comp):
        pdef = re.search(rf'<part id="{pid}" subtype="normal_part">(.*?)</part>', oset, flags=re.S)
        ext = int(re.search(r'key="extruder" value="(\d)"', pdef.group(1)).group(1)); used.add(ext)
        parts.append((mesh(path), 'part', ext, {}))
    U = m3.Manifold.batch_boolean([q for q, *_ in parts], m3.OpType.Add)
    bb = U.bounding_box(); px, py = place[oid]
    hull[oid] = (px + bb[0], py + bb[1], px + bb[3], py + bb[4], bb[5]); body[oid] = parts[0][0]
    ovl = sum((parts[i][0] ^ parts[j][0]).volume() for i in range(len(parts)) for j in range(i + 1, len(parts)))
    chk(f'3 {name}: {len(parts)} meshes valid, on the bed, parts do not overlap', all(q.status() == m3.Error.NoError for q, *_ in parts) and abs(bb[2]) < 1e-3 and ovl < 1e-3,
        f'filaments {sorted({e for _, _, e, _ in parts})}, h {bb[5]:.2f}, overlap {ovl:.4f}')
    prusa.append((name, parts, (px, py)))
    if name != 'Spine sleeve':
        # colour work only in the face-down first layers (inlays <= 5 layers): no colour swaps up the walls
        zmax = max([q.bounding_box()[5] for q, *_ in parts[1:]] or [0])
        chk(f'3 {name}: every inlay / mark sits in the first 5 layers (z <= 0.84)', zmax <= 0.84 + 1e-3, f'{len(parts) - 1} inlay parts, top z {zmax:.2f}')
        # rounded long edges: the first layer is inset from the full width by the R4.5 round + its 45 deg run-out to the bed
        # (R4.5 -> 2.6-2.75 mm a side; the old v7 R3 edge -> 1.7-2.0)
        def width(zz):
            xs = [x for q in parts[0][0].slice(zz).to_polygons() for x, y in q]; return max(xs) - min(xs)
        inset = (65.0 - width(0.1)) / 2          # 65 mm = the case's full width (the thin cover never reaches it: it ends inside the edge round)
        chk(f'3 {name}: R4.5 rounded long edges (first layer inset 2.2-3.0 mm a side)', 2.2 < inset < 3.0, f'inset {inset:.2f} mm')
ids = [o for o, _ in objs]
gap = lambda a, b: float(np.hypot(max(hull[b][0] - hull[a][2], hull[a][0] - hull[b][2], 0), max(hull[b][1] - hull[a][3], hull[a][1] - hull[b][3], 0)))
gaps = [gap(a, b) for i, a in enumerate(ids) for b in ids[i + 1:]]
chk('3 A1 by-object clearance: hull gaps >= 73, heights < 25, inside the bed with the brim', min(gaps) >= 73 and max(h[4] for h in hull.values()) < 25 and
    all(4 <= h[0] and 4 <= h[1] and h[2] <= 252 and h[3] <= 252 for h in hull.values()), f'min gap {min(gaps):.1f}, max h {max(h[4] for h in hull.values()):.1f}')

# ---- 4 pockets (layer mid-heights: first layer 0.2, then 0.16)
def pockets(man, zz):
    g = None
    for q in man.slice(zz).to_polygons():
        p = Polygon(q).buffer(0); g = p if g is None else g.symmetric_difference(p)
    out = []
    for q in getattr(g, 'geoms', [g]):
        for h in q.interiors:
            P = Polygon(h); x0, y0, x1, y1 = P.bounds; d = 2 * np.sqrt(P.area / np.pi)
            if 5.1 < d < 5.8 and abs((x1 - x0) - d) < 0.25 and abs((y1 - y0) - d) < 0.25: out.append(round(d, 2))
    return out
mids = [0.1] + [0.2 + 0.08 + 0.16 * k for k in range(160)]
for nm, oid in (('cover', ids[0]), ('tray', ids[1])):
    man = body[oid]; H = hull[oid][4]
    cnt = [(zz, pockets(man, zz)) for zz in mids if zz < H]
    open_layers = [zz for zz, p in cnt if len(p) == 2]
    if not open_layers: chk(f'4 {nm}: two magnet pockets found', False); continue
    z0, z1 = open_layers[0], open_layers[-1]
    contiguous = all(len(p) == 2 for zz, p in cnt if z0 <= zz <= z1)
    depth = (z1 + 0.08) - (z0 - 0.08); dia = min(min(p) for zz, p in cnt if len(p) == 2)
    if TEST:
        zp = None
        # open to the closing face: above the last open layer there is no material at the pocket centres
        from shapely.geometry import Point
        cen = []
        for q in man.slice(z1).to_polygons():
            P = Polygon(q)
            if 5.1 < 2 * np.sqrt(abs(P.area) / np.pi) < 5.8: cen.append(P.centroid)
        def solid_at(zz, pt):
            g = None
            for q in man.slice(zz).to_polygons():
                p_ = Polygon(q).buffer(0); g = p_ if g is None else g.symmetric_difference(p_)
            return g is not None and g.contains(pt)
        top_open = len(cen) == 2 and not any(solid_at(zz, c) for c in cen for zz in np.arange(z1 + 0.04, H, 0.04))
        chk(f'4 {nm}: two Ø5.35 pockets open from their floor (z {z0 - 0.08:.2f}) right up to the closing face (z {H:.2f}): glue the magnet at the floor',
            contiguous and top_open and dia > 5.15, f'Ø{dia:.2f}, open depth {depth:.2f} mm')
    else:
        zp = zc if nm == 'cover' else zt
        # the pause fires at the change INTO the layer whose top is zp (layer_z), i.e. the layer from zp - 0.16 to zp: that layer must be the first sealing one
        sealed = len(pockets(man, zp - 0.08)) == 0 and len(pockets(man, zp + 0.08)) == 0
        chk(f'4 {nm}: two pockets open on every layer up to the pause, sealed by the layer the printer pauses before (layer top z {zp:.2f})',
            contiguous and abs((z1 + 0.08) - (zp - 0.16)) < 0.02 and sealed, f'open z {z0 - 0.08:.2f} -> {z1 + 0.08:.2f}')
        chk(f'4 {nm}: each pocket fits a Ø5 x 2 magnet (Ø > 5.15, depth > 2.1)', dia > 5.15 and depth > 2.1, f'Ø{dia:.2f} x {depth:.2f} mm')
    print(f'     {nm}: pocket floor z {z0 - 0.08:.2f}, top of pocket z {z1 + 0.08:.2f}, part height {H:.2f}')

# ---- 5 slice (PrusaSlicer, A1 emulation from Bambu's released presets)
sys.argv = [sys.argv[0], WD]
import slicetest as ST
mach = S.TP.resolve(S.TAG_VALUES, 'machine', 'Bambu Lab A1 0.4 nozzle'); pr = S.TP.resolve(S.TAG_VALUES, 'process', '0.16mm High Quality @BBL A1')
s = lambda v: str(v[0] if isinstance(v, list) else v)
L = lambda key, k=4: ','.join([s(cfg[key])] * k) if isinstance(cfg[key], list) and len(set(cfg[key])) == 1 else ','.join(cfg[key])
ST.prusa_3mf(f'{WD}/wood.3mf', prusa, [])
ini = f'{WD}/a1_wood_0.16.ini'; ST.config(0.16, ini); txt = open(ini).read()
M = cfg['flush_volumes_matrix']
fan = lambda k: ','.join(cfg[k])
rep = {'nozzle_diameter': '0.4,0.4,0.4,0.4', 'retract_length': '0.8,0.8,0.8,0.8', 'retract_speed': '30,30,30,30', 'retract_length_toolchange': '2,2,2,2',
       'filament_toolchange_delay': '0,0,0,0', 'filament_cooling_moves': '0,0,0,0', 'filament_diameter': '1.75,1.75,1.75,1.75',
       'wiping_volumes_matrix': ','.join(M), 'wiping_volumes_extruders': ','.join(['70'] * 8),
       'filament_type': 'PLA;PLA;PLA;PLA', 'filament_density': L('filament_density'), 'filament_colour': ';'.join(cfg['filament_colour']),
       'temperature': L('nozzle_temperature'), 'first_layer_temperature': L('nozzle_temperature_initial_layer'),
       'bed_temperature': L('textured_plate_temp'), 'first_layer_bed_temperature': L('textured_plate_temp_initial_layer'),
       'filament_max_volumetric_speed': L('filament_max_volumetric_speed'), 'fan_always_on': '1,1,1,1', 'min_fan_speed': fan('fan_min_speed'), 'max_fan_speed': fan('fan_max_speed'),
       'slowdown_below_layer_time': fan('slow_down_layer_time'), 'min_print_speed': fan('slow_down_min_speed'),
       'wipe_tower': '0', 'complete_objects': '1', 'extruder_clearance_radius': s(mach.get('extruder_clearance_max_radius', 73)),
       'extruder_clearance_height': s(mach.get('extruder_clearance_height_to_rod', 25)),
       'machine_max_acceleration_extruding': f"{s(mach['machine_max_acceleration_extruding'])},{s(mach['machine_max_acceleration_extruding'])}",
       'machine_max_acceleration_x': f"{s(mach['machine_max_acceleration_x'])},{s(mach['machine_max_acceleration_x'])}",
       'machine_max_acceleration_y': f"{s(mach['machine_max_acceleration_y'])},{s(mach['machine_max_acceleration_y'])}",
       'external_perimeter_speed': s(pr['outer_wall_speed']), 'perimeter_speed': s(pr['inner_wall_speed']), 'infill_speed': s(pr['sparse_infill_speed']),
       'top_solid_infill_speed': s(pr['top_surface_speed']), 'external_perimeter_acceleration': s(pr['outer_wall_acceleration']), 'default_acceleration': s(pr['default_acceleration']),
       'filament_load_time': ','.join([s(mach['machine_load_filament_time'])] * 4), 'filament_unload_time': ','.join([s(mach['machine_unload_filament_time'])] * 4),
       'perimeters': cfg['wall_loops'], 'top_solid_layers': cfg['top_shell_layers'], 'bottom_solid_layers': cfg['bottom_shell_layers'],
       'top_solid_min_thickness': cfg['top_shell_thickness'], 'bottom_solid_min_thickness': cfg['bottom_shell_thickness'],
       'fill_density': cfg['sparse_infill_density'], 'fill_pattern': 'gyroid', 'top_fill_pattern': 'concentric',
       'brim_width': cfg['brim_width'] if cfg['brim_type'] != 'no_brim' else '0', 'brim_type': 'outer_only' if cfg['brim_type'] != 'no_brim' else 'no_brim',
       'layer_gcode': 'G92 E0' + (lg[lg.find('\n{if'):].replace('\n', '\\n') if not TEST else '')}
for k, v in rep.items():
    if re.search(rf'^{k} = ', txt, flags=re.M): txt = re.sub(rf'^{k} = .*$', lambda _m, k=k, v=v: f'{k} = {v}', txt, flags=re.M)
    else: txt += f'{k} = {v}\n'
# the pause block's syntax ({if ...}, current_object_idx, layer_z) is valid in both Bambu Studio and PrusaSlicer, so it is sliced as shipped
open(ini, 'w').write(txt)
gc = f'{WD}/wood_0.16.gcode'
res = ST.slice_one(f'{WD}/wood.3mf', ini, gc)
if res.returncode != 0:
    chk('5 slice', False, (res.stdout + res.stderr)[-800:]); print('SOMETHING FAILED'); sys.exit(1)
r5 = ST.report(gc); r5.pop('zs')
g = open(gc).read().split('\n'); obj, zs, hits = None, None, []
labels = dict(re.findall(r'M486 S(\d+)\nM486 A(.+)', '\n'.join(g)))
for l in g:
    if l.startswith('M486 S') and not l.startswith('M486 S-1'): obj = labels.get(l.split()[1][1:], l)
    if l.startswith(';Z:'): zs = float(l[3:])
    if l.startswith('M400 U1'): hits.append((obj, zs))
warn = [l.strip() for l in (res.stdout + res.stderr).splitlines() if l.strip() and not l.startswith('Slicing') and not re.match(r'^\d+ =>', l.strip())]
print('     slice:', json.dumps(dict(r5, pauses_at=hits, filaments_used=sorted(used))))
for w in warn[-6:]: print('     slicer says:', w[:200])
if TEST:
    chk('5 slice: OK, no pauses', r5['pauses'] == 0 and not hits)
else:
    hits = [(o, zz) for o, zz in hits]
    good = len(hits) == 2 and hits[0][0].startswith('Cover') and hits[1][0].startswith('Tray') and abs(hits[0][1] - zc) < 0.02 and abs(hits[1][1] - zt) < 0.02
    chk('5 slice: exactly 2 pauses, cover then tray, on the first sealing layer', good, str(hits))
print('ALL PASS' if ok else 'SOMETHING FAILED')
