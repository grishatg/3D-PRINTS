"""Verify a two-design wood-PLA project made by w_pair_export.py, reading ONLY the 3MF. Usage: python3 src/w_pair_verify.py <file.3mf> <work_dir>
1  Bambu loader check (emulated from Bambu's source at v02.03.01.51 / v02.08.04.61 / v02.09.01.70): identical to the 26-flag baseline.
2  Settings: proven key set + order, 4 x Bambu PLA Wood @BBL A1, A1 0.4, by object, no prime tower, NO pause (magnets are glued).
3  Plate: 4 objects (cover, tray, cover, tray), meshes valid and on the bed, every hull >= 73 mm from every other (A1 by-object rule:
   each hull grows by 36.4 mm), all < 25 mm tall, everything + brim on the 256 x 256 bed. (Hinge-sleeves plate: 6 sleeves, 3 one-wood objects.)
4  Per cover / tray, in the part's own frame (spine at -x):
   - R4.5 rounded long edges (first-layer inset) and every inlay / mark within the first 5 layers;
   - WALLS (v10.1, after the 24 Nov test print): layer by layer, no inside opening comes closer than 1.1 mm to the outside
     (hinge knuckle zone excepted), and the tray's cavity stays fully enclosed from the floor to the rim (no breach anywhere);
   - two Ø5.35 magnet pockets per half, open from the floor to the closing face (glue-in).
5  A1-emulated PrusaSlicer slice of the file itself, exactly as laid out (--dont-arrange; sequential, A1 clearance 73 mm):
   time, grams, swaps, layers, no pauses.
6  The A·B as SLICED (v10.5, owner: "make sure the B is printed properly, not missing bits"): every first-layer line of each
   tray at its true width (from E). Inlaid: A, dot, B >= 98 % covered, no bare spot >= 0.3 mm, counters open and filled by the
   body wood. Engraved (KUMIKO): letters open, islands printed. No-initials files: no A·B anywhere. Writes ab_toolpaths.png.
   Dev only: REUSE_GCODE=1 re-checks the last slice in <work_dir> without slicing again."""
import sys, os, re, json, zipfile, subprocess, numpy as np, manifold3d as m3
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from shapely.geometry import Polygon, MultiPoint, Point, box
from shapely.ops import unary_union, nearest_points
from shapely import affinity
import a1_safe as S
F, WD = os.path.abspath(sys.argv[1]), os.path.abspath(sys.argv[2]); os.makedirs(WD, exist_ok=True)
INITIALS = os.path.basename(F).startswith('AB_')          # the exporter names A·B projects AB_..., the others ..._no_initials
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
ok = True
def chk(name, cond, info=''):
    global ok
    ok &= bool(cond); print(('PASS ' if cond else 'FAIL ') + name + (f'  [{info}]' if info else ''))

# ---- 1 loader
res = subprocess.run([sys.executable, f'{HERE}/bbsvalidate.py', F, 'v02.03.01.51', 'v02.08.04.61', 'v02.09.01.70'], capture_output=True, text=True, cwd=HERE)
base = open(f'{ROOT}/test-slice/bambu_loader_check_baseline.txt').read().splitlines()[:39]
chk('1 Bambu loader: identical to the 26-flag baseline at all 3 releases', res.stdout.splitlines() == base, ' '.join(re.findall(r'\d+ problem\(s\)', res.stdout)))

# ---- 2 settings
z = zipfile.ZipFile(F)
chk('2 zip CRC', z.testzip() is None)
cfg = json.loads(z.read('Metadata/project_settings.config'))
ref = json.loads(zipfile.ZipFile(f'{ROOT}/superseded/v7.0-first-print/AB_Rollie_Book_v7_A1_by_object.3mf').read('Metadata/project_settings.config'))
chk('2 settings: same 366 keys, same order as the v7.0 file that opened in Bambu', list(cfg) == list(ref), f'{len(cfg)} keys')
chk('2 settings: all values strings / string lists', all(isinstance(v, str) or (isinstance(v, list) and all(isinstance(x, str) for x in v)) for v in cfg.values()))
chk('2 settings: 4 x Bambu PLA Wood @BBL A1 (GFA16), A1 0.4, by object, no prime tower, textured PEI',
    len(cfg['filament_colour']) == 4 and cfg['filament_settings_id'] == ['Bambu PLA Wood @BBL A1'] * 4 and cfg['filament_ids'] == ['GFA16'] * 4
    and cfg['printer_settings_id'] == 'Bambu Lab A1 0.4 nozzle' and cfg['print_sequence'] == 'by object' and cfg['enable_prime_tower'] == '0'
    and cfg['curr_bed_type'] == 'Textured PEI Plate', f'colours {cfg["filament_colour"]}, nozzle {cfg["nozzle_temperature"][0]} C, bed {cfg["textured_plate_temp"][0]} C')
chk('2 settings: flush matrix 4 x 4, vector 8, different_settings_to_system 6', len(cfg['flush_volumes_matrix']) == 16 and len(cfg['flush_volumes_vector']) == 8 and len(cfg['different_settings_to_system']) == 6)
lg = cfg['layer_change_gcode']
chk('2 no pause anywhere (magnets are glued after printing)', 'M400 U1' not in lg and 'PAUSE' not in lg and 'M601' not in lg and lg.startswith('; layer num/total_layer_count'))
chk(f'2 print profile: {cfg["print_settings_id"]}, {cfg["layer_height"]} mm layers, scarf seams {cfg["filament_scarf_seam_type"][0]}, seam {cfg["seam_position"]}',
    cfg['print_settings_id'] in ('0.12mm High Quality @BBL A1', '0.16mm High Quality @BBL A1') and cfg['layer_height'] in ('0.12', '0.16'))
print(f'     print: infill {cfg["sparse_infill_density"]} {cfg["sparse_infill_pattern"]}, walls {cfg["wall_loops"]}, top/bottom {cfg["top_shell_layers"]}/{cfg["bottom_shell_layers"]} '
      f'(top min {cfg["top_shell_thickness"]} mm), brim {cfg["brim_type"]} {cfg["brim_width"]} mm, outer wall {cfg["outer_wall_speed"]} mm/s, first layer {cfg["initial_layer_speed"]} mm/s @ {cfg["initial_layer_line_width"]} mm')

# ---- 3 plate
top = z.read('3D/3dmodel.model').decode(); ms = z.read('Metadata/model_settings.config').decode()
def mesh(p):
    x = z.read(p.lstrip('/')).decode()
    V = np.array(re.findall(r'<vertex x="([^"]+)" y="([^"]+)" z="([^"]+)"', x), dtype=np.float32)
    T = np.array(re.findall(r'<triangle v1="(\d+)" v2="(\d+)" v3="(\d+)"', x), dtype=np.uint32)
    return m3.Manifold(m3.Mesh(vert_properties=V, tri_verts=T))
items = {o: [float(v) for v in t.split()] for o, t in re.findall(r'<item objectid="(\d+)"[^>]*transform="([^"]+)"', top)}
objs = []
for oid, comp in re.findall(r'<object id="(\d+)" p:UUID="[^"]+" type="model">\s*<components>(.*?)</components>', top, flags=re.S):
    oset = re.search(rf'<object id="{oid}">(.*?)</object>', ms, flags=re.S).group(1)
    name = re.search(r'<metadata key="name" value="([^"]+)"', oset).group(1)
    parts = []
    for path, pid in re.findall(r'p:path="([^"]+)" objectid="(\d+)"', comp):
        pdef = re.search(rf'<part id="{pid}" subtype="normal_part">(.*?)</part>', oset, flags=re.S).group(1)
        parts.append((mesh(path), re.search(r'key="name" value="([^"]+)"', pdef).group(1), int(re.search(r'key="extruder" value="(\d)"', pdef).group(1))))
    t = items[oid]; ang = np.degrees(np.arctan2(t[1], t[0]))
    assert abs(t[2]) < 1e-9 and abs(t[5]) < 1e-9 and abs(t[8] - 1) < 1e-9 and abs(t[11]) < 1e-9, 'only z rotations + xy shifts expected'
    objs.append(dict(name=name, parts=parts, ang=ang, tx=t[9], ty=t[10]))
SLEEVES = all('sleeve' in o['name'].lower() for o in objs)     # the morning plate: hinge sleeves only
if SLEEVES:
    nsl = sum(1 for o in objs for q, n_, e in o['parts'] if 'sleeve' in n_)
    chk('3 hinge-sleeves plate: six sleeves in three one-wood objects (2 colour changes)', nsl == 6 and len(objs) == 3 and
        all(len({e for q, n_, e in o['parts']}) == 1 for o in objs), ' / '.join(o['name'] for o in objs))
else:
    chk('3 four objects: cover, tray, cover, tray (= by-object print order)', [('cover' in o['name']) for o in objs] == [True, False, True, False] and len(objs) == 4,
        ' / '.join(o['name'] for o in objs))
world, used = {}, set()
for o in objs:
    pts = np.vstack([np.asarray(q.to_mesh().vert_properties)[:, :2] for q, n_, e in o['parts']])
    hl = affinity.translate(affinity.rotate(MultiPoint(pts).convex_hull, o['ang'], origin=(0, 0)), o['tx'], o['ty'])
    bb = m3.Manifold.batch_boolean([q for q, n_, e in o['parts']], m3.OpType.Add).bounding_box()
    world[o['name']] = (hl, bb[5]); used |= {e for q, n_, e in o['parts']}
    ovl = sum((o['parts'][i][0] ^ o['parts'][j][0]).volume() for i in range(len(o['parts'])) for j in range(i + 1, len(o['parts'])))
    chk(f'3 {o["name"]}: {len(o["parts"])} meshes valid, on the bed, parts do not overlap', all(q.status() == m3.Error.NoError for q, n_, e in o['parts'])
        and abs(bb[2]) < 1e-3 and ovl < 1e-3, f'filaments {sorted({e for q, n_, e in o["parts"]})}, h {bb[5]:.2f}, turned {o["ang"]:.0f} deg')
ks = list(world); gaps = {f'{a} | {b}': world[a][0].distance(world[b][0]) for i, a in enumerate(ks) for b in ks[i + 1:]}
brim = float(cfg['brim_width']) if cfg['brim_type'] != 'no_brim' else 0.0
ext = [min(world[k][0].bounds[0] for k in ks), min(world[k][0].bounds[1] for k in ks), max(world[k][0].bounds[2] for k in ks), max(world[k][0].bounds[3] for k in ks)]
chk('3 A1 by-object clearance: every pair of objects >= 73 mm apart (Bambu needs > 72.8), all < 25 mm tall', min(gaps.values()) >= 73.0 and max(h for _, h in world.values()) < 25,
    f'min gap {min(gaps.values()):.1f} mm, tallest {max(h for _, h in world.values()):.1f} mm')
chk('3 everything + brim inside the 256 x 256 bed', ext[0] - brim >= 0.5 and ext[1] - brim >= 0.5 and ext[2] + brim <= 255.5 and ext[3] + brim <= 255.5,
    'extent ' + ', '.join(f'{v:.1f}' for v in ext))
if not SLEEVES:
    chk('3 no hinge sleeves on this plate (they print on their own plate)', sum(1 for o in objs for q, n_, e in o['parts'] if 'sleeve' in n_) == 0)

# ---- 4 per half: edges, inlays, walls, pockets
def section(man, zz):
    g = None
    for q in man.slice(zz).to_polygons():
        p = Polygon(q).buffer(0); g = p if g is None else g.symmetric_difference(p)
    return g
def pockets(man, zz):
    g = section(man, zz); out = []
    if g is None: return out
    for q in getattr(g, 'geoms', [g]):
        for h in q.interiors:
            P = Polygon(h); x0, y0, x1, y1 = P.bounds; d = 2 * np.sqrt(P.area / np.pi)
            if 5.1 < d < 5.8 and abs((x1 - x0) - d) < 0.25 and abs((y1 - y0) - d) < 0.25: out.append((round(d, 2), P.centroid))
    return out
HINGE_W = 7.5                    # spine side (first 7.5 mm from the spine face): hinge knuckles interleave there by design
LH = float(cfg['layer_height'])
mids = [0.1] + [0.2 + LH / 2 + LH * k for k in range(int(14 / LH))]
floors = {}
for o in ([] if SLEEVES else objs):
    kind = 'cover' if 'cover' in o['name'] else 'tray'
    body_parts = [q for q, n_, e in o['parts'] if 'sleeve' not in n_]
    body = m3.Manifold.batch_boolean(body_parts, m3.OpType.Add) if len(body_parts) > 1 else body_parts[0]
    bb = body.bounding_box(); H = bb[5]
    zmax_inl = max([q.bounding_box()[5] for q, n_, e in o['parts'][1:] if 'sleeve' not in n_] or [0])
    chk(f'4 {o["name"]}: every inlay / mark sits in the first 5 layers (z <= 0.84)', zmax_inl <= 0.84 + 1e-3, f'top z {zmax_inl:.2f}')
    xs = lambda zz: [x for q in o['parts'][0][0].slice(zz).to_polygons() for x, y in q]
    inset = (65.0 - (max(xs(0.1)) - min(xs(0.1)))) / 2
    chk(f'4 {o["name"]}: R4.5 rounded long edges (first-layer inset 2.2-3.0 mm a side)', 2.2 < inset < 3.0, f'inset {inset:.2f} mm')
    # walls: openings vs the outside, layer by layer (hinge zone plugged); tray cavity must stay enclosed floor -> rim
    X_HINGE = bb[0] + HINGE_W
    plug = box(bb[0] - 5, bb[1] - 5, X_HINGE, bb[4] + 5)
    rows = []
    for zz in [m for m in mids if 0.9 < m < H]:
        g = section(body, zz)
        if g is None or g.is_empty: continue
        gp = g.union(plug.intersection(box(bb[0] - 5, bb[1] - 5, X_HINGE, bb[4] + 5)))
        main = max(getattr(gp, 'geoms', [gp]), key=lambda q: q.area)
        a_out = Polygon(main.exterior).area
        wall, at = 99.0, None
        for h in main.interiors:
            hp = Polygon(h)
            if hp.area < 0.05: continue
            a, b = nearest_points(h, main.exterior)
            if b.x < X_HINGE + 0.5: continue
            d = h.distance(main.exterior)
            if d < wall: wall, at = d, (round(a.x, 1), round(a.y, 1))
        cav = max([Polygon(h).area for h in main.interiors] or [0])
        rows.append((zz, a_out, wall, at, cav))
    amax = max(r[1] for r in rows)
    full = [r for r in rows if r[1] >= 0.9 * amax]
    if kind == 'tray':
        walled = [r for r in full if r[0] > 2.6]                    # above the 2 mm floor + its fillet
        breach = [r[0] for r in walled if r[4] < 0.5 * r[1]]
        chk(f'4 {o["name"]}: cavity fully enclosed on every layer from the floor to the rim (no breach)', not breach and walled,
            f'{len(walled)} layers z {walled[0][0]:.2f}-{walled[-1][0]:.2f}' + (f'; OPEN at z {breach[:6]}' if breach else ''))
        check = walled
    else:
        check = [r for r in full if r[0] < 2.0]                     # the 2 mm lid plate
    wmin = min(check, key=lambda r: r[2])
    chk(f'4 {o["name"]}: walls >= 1.1 mm between every inside opening and the outside', wmin[2] >= 1.1,
        f'thinnest {wmin[2]:.2f} mm at z {wmin[0]:.2f}, xy {wmin[3]}')
    # magnet pockets (glue): two Ø5.35 holes open from the floor to the closing face
    cnt = [(zz, pockets(body, zz)) for zz in mids if zz < H]
    open_layers = [zz for zz, p in cnt if len(p) == 2]
    if not open_layers: chk(f'4 {o["name"]}: two magnet pockets', False); continue
    z0, z1 = open_layers[0], open_layers[-1]
    contiguous = all(len(p) == 2 for zz, p in cnt if z0 <= zz <= z1)
    cen = [c for d, c in cnt[[zz for zz, p in cnt].index(z1)][1]]
    solid_above = any(section(body, zz) is not None and section(body, zz).contains(c) for c in cen for zz in np.arange(z1 + 0.04, H, 0.08))
    dia = min(d for zz, p in cnt if len(p) == 2 for d, c in p)
    floor_z, top_z = z0 - LH / 2, z1 + LH / 2
    recess = top_z - (floor_z + 2.0)                                  # Ø5 x 2 magnet glued on the floor: its face this far below the closing face
    floors[(o['name'].split()[0], kind)] = floor_z
    chk(f'4 {o["name"]}: two Ø5.35 pockets open from the floor (z {floor_z:.2f}) to the closing face; a glued Ø5x2 magnet sits {recess:.2f} mm below the face',
        contiguous and not solid_above and dia > 5.15 and 0.0 <= recess <= 0.15, f'Ø{dia:.2f}, {top_z - floor_z:.2f} mm deep (flush, never proud)')

D_CASE = 13.5   # case thickness: cover prints face-down (print z = y + D/2), tray back-down (print z = D/2 - y)
for dsg in sorted({k[0] for k in floors}):
    if (dsg, 'cover') in floors and (dsg, 'tray') in floors:
        gap = D_CASE - (floors[(dsg, 'cover')] + floors[(dsg, 'tray')] + 4.0)
        chk(f'4 {dsg}: closed case, magnet face to magnet face {gap:.2f} mm (was 2.4 in the test print)', 0.2 <= gap <= 0.5)

# ---- 5 slice
sys.argv = [sys.argv[0], WD]
import slicetest as ST
mach = S.TP.resolve(S.TAG_VALUES, 'machine', 'Bambu Lab A1 0.4 nozzle'); pr = S.TP.resolve(S.TAG_VALUES, 'process', '0.16mm High Quality @BBL A1')
s = lambda v: str(v[0] if isinstance(v, list) else v)
L = lambda key: ','.join(cfg[key])
def acc(k):
    v = str(cfg.get(k, '0')); d = float(cfg['default_acceleration'])
    if v.endswith('%'): return f'{d * float(v[:-1]) / 100:g}'
    return f'{d:g}' if float(v) == 0 else v
prusa = []
for o in objs:   # bake the plate transform into the meshes (PrusaSlicer project gets plain positions)
    prusa.append((o['name'], [(q.rotate((0, 0, o['ang'])), 'part', e, {}) for q, n_, e in o['parts']], (o['tx'], o['ty'])))
ST.prusa_3mf(f'{WD}/wood.3mf', prusa, [])
ini = f'{WD}/a1_wood_{LH}.ini'; ST.config(LH, ini); txt = open(ini).read()
rep = {'nozzle_diameter': '0.4,0.4,0.4,0.4', 'retract_length': '0.8,0.8,0.8,0.8', 'retract_speed': '30,30,30,30', 'retract_length_toolchange': '2,2,2,2',
       'filament_toolchange_delay': '0,0,0,0', 'filament_cooling_moves': '0,0,0,0', 'filament_diameter': '1.75,1.75,1.75,1.75',
       'wiping_volumes_matrix': ','.join(cfg['flush_volumes_matrix']), 'wiping_volumes_extruders': ','.join(['70'] * 8),
       'filament_type': 'PLA;PLA;PLA;PLA', 'filament_density': L('filament_density'), 'filament_colour': ';'.join(cfg['filament_colour']),
       'temperature': L('nozzle_temperature'), 'first_layer_temperature': L('nozzle_temperature_initial_layer'),
       'bed_temperature': L('textured_plate_temp'), 'first_layer_bed_temperature': L('textured_plate_temp_initial_layer'),
       'filament_max_volumetric_speed': L('filament_max_volumetric_speed'), 'fan_always_on': '1,1,1,1', 'min_fan_speed': L('fan_min_speed'), 'max_fan_speed': L('fan_max_speed'),
       'slowdown_below_layer_time': L('slow_down_layer_time'), 'min_print_speed': L('slow_down_min_speed'),
       'wipe_tower': '0', 'complete_objects': '1', 'extruder_clearance_radius': s(mach.get('extruder_clearance_max_radius', 73)),
       'extruder_clearance_height': s(mach.get('extruder_clearance_height_to_rod', 25)),
       'machine_max_acceleration_extruding': f"{s(mach['machine_max_acceleration_extruding'])},{s(mach['machine_max_acceleration_extruding'])}",
       'machine_max_acceleration_x': f"{s(mach['machine_max_acceleration_x'])},{s(mach['machine_max_acceleration_x'])}",
       'machine_max_acceleration_y': f"{s(mach['machine_max_acceleration_y'])},{s(mach['machine_max_acceleration_y'])}",
       'external_perimeter_speed': cfg['outer_wall_speed'], 'perimeter_speed': cfg['inner_wall_speed'], 'infill_speed': cfg['sparse_infill_speed'],
       'solid_infill_speed': cfg['internal_solid_infill_speed'], 'top_solid_infill_speed': cfg['top_surface_speed'], 'external_perimeter_acceleration': cfg['outer_wall_acceleration'],
       'default_acceleration': cfg['default_acceleration'], 'first_layer_speed': cfg['initial_layer_speed'], 'first_layer_extrusion_width': cfg['initial_layer_line_width'],
       'filament_load_time': ','.join([s(mach['machine_load_filament_time'])] * 4), 'filament_unload_time': ','.join([s(mach['machine_unload_filament_time'])] * 4),
       'perimeters': cfg['wall_loops'], 'top_solid_layers': cfg['top_shell_layers'], 'bottom_solid_layers': cfg['bottom_shell_layers'],
       'top_solid_min_thickness': cfg['top_shell_thickness'], 'bottom_solid_min_thickness': cfg['bottom_shell_thickness'],
       'fill_density': cfg['sparse_infill_density'], 'fill_pattern': 'gyroid', 'top_fill_pattern': 'concentric',
       'brim_width': cfg['brim_width'] if cfg['brim_type'] != 'no_brim' else '0', 'brim_type': 'outer_only' if cfg['brim_type'] != 'no_brim' else 'no_brim',
       'layer_gcode': 'G92 E0',
       # Bambu's own per-feature motion values from the file (0 / % = relative to the default), so the time is a fair stand-in for Bambu's estimate
       'perimeter_acceleration': acc('inner_wall_acceleration'), 'infill_acceleration': acc('sparse_infill_acceleration'),
       'solid_infill_acceleration': acc('sparse_infill_acceleration'), 'top_solid_infill_acceleration': acc('top_surface_acceleration'),
       'first_layer_acceleration': acc('initial_layer_acceleration'), 'travel_acceleration': s(cfg['machine_max_acceleration_travel']),
       'travel_speed': cfg['travel_speed'], 'gap_fill_speed': cfg['gap_infill_speed'], 'bridge_speed': cfg['bridge_speed'],
       'small_perimeter_speed': cfg['small_perimeter_speed'], 'first_layer_infill_speed': cfg['initial_layer_infill_speed']}
for k, v in rep.items():
    if re.search(rf'^{k} = ', txt, flags=re.M): txt = re.sub(rf'^{k} = .*$', lambda _m, k=k, v=v: f'{k} = {v}', txt, flags=re.M)
    else: txt += f'{k} = {v}\n'
open(ini, 'w').write(txt)
gc = f'{WD}/wood_{LH}.gcode'
if os.environ.get('REUSE_GCODE') and os.path.exists(gc):            # dev only: re-run the checks on the last slice
    import types; res = types.SimpleNamespace(returncode=0, stdout='', stderr='')
else: res = ST.slice_one(f'{WD}/wood.3mf', ini, gc, dont_arrange=True)   # slice the layout exactly as in the file
if res.returncode != 0:
    chk('5 slice (A1 emulation, sequential with 73 mm clearance)', False, (res.stdout + res.stderr)[-800:]); print('SOMETHING FAILED'); sys.exit(1)
r5 = ST.report(gc); r5.pop('zs')
msgs = [l.strip() for l in (res.stdout + res.stderr).splitlines() if l.strip() and not l.startswith('Slicing') and not re.match(r'^\d+ =>', l.strip())]
# purge time on the A1 (not in the emulation, which already counts 54 s load + unload per swap): flush volume at ~12 mm3/s + ~10 s cut / wipe
seq = [int(t) for t in re.findall(r'^T(\d)', open(gc).read(), flags=re.M)]
FM = [float(v) for v in cfg['flush_volumes_matrix']]
purge_s = sum(FM[a * 4 + b] / 12.0 + 10.0 for a, b in zip(seq, seq[1:]))
hms = re.findall(r'(\d+)([dhms])', r5['time']); emu_s = sum(int(v) * {'d': 86400, 'h': 3600, 'm': 60, 's': 1}[u] for v, u in hms)
est = emu_s + purge_s
r5['estimate_with_purges'] = f'{int(est // 3600)}h {int(est % 3600 // 60):02d}m'
print('     slice:', json.dumps(dict(r5, filaments_used=sorted(used))))
for w in msgs[-8:]: print('     slicer says:', w[:200])
chk('5 slice: OK (sequential, A1 73 mm clearance accepted), no pauses', r5['pauses'] == 0)

# ---- 6 the A·B as SLICED (owner: "make sure the B is printed properly, not missing bits")
# The first layer is the visible face (the trays print face-down). Every first-layer extrusion of each tray is read from the
# G-code and drawn at the width it really lays down: width from the plastic it pushes (E, relative) over the segment length,
# PrusaSlicer's rounded-rectangle bead (w = area / h + h (1 - pi/4)), round ends.
#   inlaid mark: its wood must cover each of A, dot and B, with no bare spot a 0.3 mm dot fits in, and must keep out of the
#                counters (the holes in A and B), which the body wood must fill.
#   engraved mark: the letters must stay open (no body wood in them).
from shapely.geometry import LineString
FIL_AREA, H1 = np.pi * (1.75 / 2) ** 2, float(cfg['initial_layer_print_height'])
glines = open(gc).read().split('\n'); labels6 = dict(re.findall(r'M486 S(\d+)\nM486 A(.+)', '\n'.join(glines)))
segs = {}; tool = 0; obj6 = None; zc = 0.0; x = y = 0.0
for l in glines:
    if l.startswith('M486 S'): obj6 = None if l.startswith('M486 S-1') else labels6.get(l.split()[1][1:])
    elif l.startswith(';Z:'): zc = float(l[3:])
    elif re.match(r'^T\d', l): tool = int(l[1])
    elif l.startswith('G1 '):
        mx = re.search(r' X([-\d.]+)', l); my = re.search(r' Y([-\d.]+)', l); me = re.search(r' E([-\d.]+)', l)
        nx = float(mx.group(1)) if mx else x; ny = float(my.group(1)) if my else y; ln = float(np.hypot(nx - x, ny - y))
        if me and float(me.group(1)) > 0 and zc <= H1 + 1e-4 and ln > 1e-6:
            w = float(me.group(1)) * FIL_AREA / (ln * H1) + H1 * (1 - np.pi / 4)
            segs.setdefault((obj6, tool), []).append((LineString([(x, y), (nx, ny)]), w))
        x, y = nx, ny
def laid(key, near):                                   # the plastic one wood lays on the face layer of one object, near the mark
    return unary_union([ls.buffer(w / 2, quad_segs=8) for ls, w in segs.get(key, []) if ls.distance(near) < 1.0])
def world(o, g): return affinity.translate(affinity.rotate(g, o['ang'], origin=(0, 0)), o['tx'], o['ty'])
def first_layer(man):
    g = None
    for q in man.slice(0.1).to_polygons():
        p_ = Polygon(q).buffer(0); g = p_ if g is None else g.symmetric_difference(p_)
    return g
marks = []
for o in ([] if SLEEVES else objs):
    ab = [(q, e) for q, n_, e in o['parts'] if 'A·B' in n_]
    body_e = o['parts'][0][2] - 1
    if ab:                                           # inlaid mark: a part of its own
        letters = world(o, first_layer(ab[0][0])); mark_e = ab[0][1] - 1; mode = 'inlaid'
    elif 'KUMIKO tray' in o['name']:                 # engraved mark: the letter-shaped holes in the tray's first layer, in the mark corner
        fl = first_layer(o['parts'][0][0]); holes_ = [Polygon(h) for q in getattr(fl, 'geoms', [fl]) for h in q.interiors]
        bbx = fl.bounds; corner = box(bbx[0], bbx[1], bbx[0] + 24, bbx[1] + 14)   # mirrored back face: hinge side, bottom corner
        # a letter = its hole in the face MINUS the islands standing inside it (the counters of A and B, which print in the body wood)
        cand = [h for h in holes_ if corner.contains(h.centroid) and h.area > 0.5]
        if not INITIALS:
            chk(f'6 {o["name"]}: no-initials file: nothing engraved in the A·B corner', not cand, f'{len(cand)} letter-sized holes there'); continue
        letters = world(o, unary_union(cand).difference(fl)); mark_e = None; mode = 'engraved'
    else: continue
    comps = sorted(getattr(letters, 'geoms', [letters]), key=lambda q: q.centroid.x if abs(o['ang']) < 45 else q.centroid.y)
    counters6 = unary_union([Polygon(h) for q in comps for h in q.interiors]); ncount = len([1 for q in comps for h in q.interiors])
    body = laid((o['name'], body_e), letters)
    if mode == 'inlaid':
        mk = laid((o['name'], mark_e), letters)
        cov = [round(mk.intersection(q.buffer(-0.05)).area / q.buffer(-0.05).area, 3) for q in comps]   # up to 0.05 mm in from the outline
        cov_raw = [round(mk.intersection(q).area / q.area, 3) for q in comps]
        bare = unary_union([q.buffer(-0.05).difference(mk) for q in comps])          # inside a letter, not covered by its wood
        holes6 = [g for g in getattr(bare, 'geoms', [bare]) if not g.is_empty and not g.buffer(-0.15).is_empty]   # a 0.3 mm dot fits
        cin = counters6.buffer(-0.1)
        spill = mk.intersection(cin).area / max(cin.area, 1e-9); cfill = body.intersection(cin).area / max(cin.area, 1e-9)
        chk(f'6 {o["name"]}: sliced A·B complete: A, dot and B each >= 98 % covered by their wood (from 0.05 mm inside the outline), no bare spot >= 0.3 mm; '
            f'the {ncount} counters stay open (<= 3 % letter wood) and are filled by the body wood (>= 95 %)',
            len(comps) == 3 and ncount == 3 and min(cov) >= 0.98 and not holes6 and spill <= 0.03 and cfill >= 0.95,
            f'coverage A/dot/B {cov} (to the very edge {cov_raw}), bare spots >= 0.3 mm: {len(holes6)}, letter wood in counters {100*spill:.1f} %, body wood in counters {100*cfill:.1f} %')
    else:
        core = unary_union([q.buffer(-0.05) for q in comps]); inside = body.intersection(core).area / core.area
        isl = counters6.buffer(-0.05); ifill = body.intersection(isl).area / max(isl.area, 1e-9)
        chk(f'6 {o["name"]}: engraved A·B: letters stay open (>= 98 % free of plastic from 0.05 mm inside the outline) and the {ncount} islands '
            f'inside A and B print in the body wood (>= 95 %)', len(comps) == 3 and ncount == 3 and inside <= 0.02 and ifill >= 0.95,
            f'letters {100 * (1 - inside):.1f} % open, islands {100 * ifill:.1f} % printed')
    marks.append((o['name'], mode, letters, mk if mode == 'inlaid' else body))
if not SLEEVES:
    trays6 = [o['name'] for o in objs if 'tray' in o['name']]; marked = [m[0] for m in marks]
    if INITIALS: chk('6 A·B file: both trays carry the A·B', sorted(marked) == sorted(trays6), f'{marked}')
    else: chk('6 no-initials file: no A·B part anywhere', not marked and not any('A·B' in n_ for o in objs for _, n_, _ in o['parts']))
if marks:
    import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
    from matplotlib.path import Path as MPath; from matplotlib.patches import PathPatch
    def patch(ax, g, **kw):                          # draws polygons WITH their holes
        for q in getattr(g, 'geoms', [g]):
            if q.geom_type != 'Polygon' or q.is_empty: continue
            vs, cs = [], []
            for ring in [q.exterior] + list(q.interiors):
                xy = np.asarray(ring.coords); vs += xy.tolist(); cs += [MPath.MOVETO] + [MPath.LINETO] * (len(xy) - 2) + [MPath.CLOSEPOLY]
            ax.add_patch(PathPatch(MPath(vs, cs), **kw))
    fig, axs = plt.subplots(1, len(marks), figsize=(6 * len(marks), 4.6)); axs = np.atleast_1d(axs)
    for ax, (nm, mode, letters, paths) in zip(axs, marks):
        bx = letters.bounds; win = box(bx[0] - 1, bx[1] - 1, bx[2] + 1, bx[3] + 1)
        patch(ax, paths.intersection(win), color='#c08a64' if mode == 'inlaid' else '#5e3b31', lw=0)
        bad = letters.buffer(-0.05).difference(paths) if mode == 'inlaid' else paths.intersection(letters.buffer(-0.05))
        patch(ax, bad, color='red', lw=0)
        for q in getattr(letters, 'geoms', [letters]):
            xx, yy = q.exterior.xy; ax.plot(xx, yy, 'k-', lw=0.8)
            for h in q.interiors: xx, yy = h.xy; ax.plot(xx, yy, 'b-', lw=0.8)
        ax.set_xlim(win.bounds[0], win.bounds[2]); ax.set_ylim(win.bounds[1], win.bounds[3])
        ax.set_aspect('equal'); ax.set_title(f'{nm}: {mode} A·B, first-layer toolpaths as laid\n'
            f'({"letter wood" if mode == "inlaid" else "body wood"} filled; black = letter outline, blue = counters; '
            f'red = {"letter not covered" if mode == "inlaid" else "plastic inside a letter"})', fontsize=8.5)
    plt.tight_layout(); plt.savefig(f'{WD}/ab_toolpaths.png', dpi=110)
    print(f'     A·B toolpath picture: {WD}/ab_toolpaths.png')
print('ALL PASS' if ok else 'SOMETHING FAILED')
