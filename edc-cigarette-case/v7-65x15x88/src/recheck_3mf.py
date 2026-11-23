"""Independent re-check of a SHIPPED v7.1 Bambu 3MF (reads only the file, not the CAD).
Usage: python3 src/recheck_3mf.py <file.3mf> [<roundtrip.gcode>]
Checks: zip/XML/JSON integrity, settings key set vs the proven template, object order cover -> tray -> sleeve,
by-object + plate + heights + spacing, pause block present with the right z per object, magnet pockets open right up
to each pause and sealed from the pause layer (meshes sliced layer by layer), pocket size vs magnet, and (optional)
exactly 2 pauses in a G-code made from this file, each on the right object."""
import sys, re, json, zipfile, numpy as np, manifold3d as m3
import xml.dom.minidom as X
from shapely.geometry import Polygon
f = sys.argv[1]; ok = True
def chk(name, cond, info=''):
    global ok
    ok &= bool(cond); print(('PASS ' if cond else 'FAIL ') + name + (f'  [{info}]' if info else ''))
z = zipfile.ZipFile(f)
chk('zip CRC', z.testzip() is None)
for n in z.namelist():
    if n.endswith(('.model', '.config', '.rels', '.xml')) and n != 'Metadata/project_settings.config':
        X.parseString(z.read(n))
chk('all XML parts parse', True, f'{len(z.namelist())} entries')
cfg = json.loads(z.read('Metadata/project_settings.config'))
chk('settings: all values strings / string lists', all(isinstance(v, str) or (isinstance(v, list) and all(isinstance(x, str) for x in v)) for v in cfg.values()))
ref = json.loads(zipfile.ZipFile(sys.argv[0].replace('src/recheck_3mf.py', '') + 'superseded/v7.0-first-print/AB_Rollie_Book_v7_A1_by_object.3mf').read('Metadata/project_settings.config'))
chk('settings: same 366 keys in the same order as v7.0 (the file that opened in Bambu)', list(cfg) == list(ref), f'{len(cfg)} keys, filament_colour index {list(cfg).index("filament_colour")}')
chk('settings: 3 filaments, by object, no prime tower, A1 0.4',
    len(cfg['filament_colour']) == 3 and cfg['print_sequence'] == 'by object' and cfg['enable_prime_tower'] == '0' and cfg['printer_settings_id'] == 'Bambu Lab A1 0.4 nozzle')
chk('settings: 100% infill, concentric top, brim 4, black capped 15',
    cfg['sparse_infill_density'] == '100%' and cfg['top_surface_pattern'] == 'concentric' and cfg['brim_type'] == 'outer_only' and cfg['filament_max_volumetric_speed'] == ['18', '15', '18'])
lg = cfg['layer_change_gcode']
m = re.search(r'current_object_idx == 0 and layer_z > ([\d.]+) and layer_z < ([\d.]+)\) or \(current_object_idx == 1 and layer_z > ([\d.]+) and layer_z < ([\d.]+)', lg)
chk('pause block present once, ends with M400 U1', m is not None and lg.count('M400 U1') == 1 and lg.count('{if') == lg.count('{endif}') == 1 and lg.startswith('; layer num/total_layer_count'))
zc = (float(m.group(1)) + float(m.group(2))) / 2; zt = (float(m.group(3)) + float(m.group(4))) / 2
top = z.read('3D/3dmodel.model').decode(); ms = z.read('Metadata/model_settings.config').decode()
names = re.findall(r'<object id="\d+">\s*<metadata key="name" value="([^"]+)"', ms)
chk('object order cover -> tray -> sleeve (= by-object print order)', names == ['Cover (grey)', 'Tray (black)', 'Spine sleeve (yellow)'], ' / '.join(names))
chk('plate is by object, no modifiers', 'value="by object"' in ms and 'modifier_part' not in ms)
def mesh(p):
    x = z.read(p.lstrip('/')).decode()
    V = np.array(re.findall(r'<vertex x="([^"]+)" y="([^"]+)" z="([^"]+)"', x), dtype=np.float32)
    T = np.array(re.findall(r'<triangle v1="(\d+)" v2="(\d+)" v3="(\d+)"', x), dtype=np.uint32)
    return m3.Manifold(m3.Mesh(vert_properties=V, tri_verts=T))
place = re.findall(r'<item objectid="(\d+)"[^>]*transform="1 0 0 0 1 0 0 0 1 ([-\d.]+) ([-\d.]+) 0"', top)
objs = re.findall(r'<object id="(\d+)" p:UUID="[^"]+" type="model">\s*<components>(.*?)</components>', top, flags=re.S)
hull = {}; body = {}
for (oid, comp), (_o, px, py) in zip(objs, place):
    parts = [mesh(p) for p in re.findall(r'p:path="([^"]+)"', comp)]
    bb = m3.Manifold.batch_boolean(parts, m3.OpType.Add).bounding_box()
    hull[oid] = (float(px) + bb[0], float(py) + bb[1], float(px) + bb[3], float(py) + bb[4], bb[5]); body[oid] = parts[0]
    chk(f'object {oid}: meshes valid, sits on bed', all(q.status() == m3.Error.NoError for q in parts) and abs(bb[2]) < 1e-3)
ids = [o for o, _ in objs]
def gap(a, b):
    ax0, ay0, ax1, ay1, _ = hull[a]; bx0, by0, bx1, by1, _ = hull[b]
    return float(np.hypot(max(bx0 - ax1, ax0 - bx1, 0), max(by0 - ay1, ay0 - by1, 0)))
gaps = [gap(a, b) for i, a in enumerate(ids) for b in ids[i + 1:]]
chk('A1 by-object clearance: hull gaps >= 73, heights < 25, inside bed with brim', min(gaps) >= 73 and max(h[4] for h in hull.values()) < 25 and
    all(4 <= h[0] and 4 <= h[1] and h[2] <= 252 and h[3] <= 252 for h in hull.values()), f'min gap {min(gaps):.1f}, max h {max(h[4] for h in hull.values()):.1f}')
def pockets(man, zz):
    g = None
    for q in man.slice(zz).to_polygons():
        p = Polygon(q).buffer(0); g = p if g is None else g.symmetric_difference(p)
    out = []
    for q in getattr(g, 'geoms', [g]):
        for h in q.interiors:                           # a round magnet-sized hole: width ~ height ~ Ø, area matches the circle
            P = Polygon(h); x0, y0, x1, y1 = P.bounds; d = 2 * np.sqrt(P.area / np.pi)
            if 9.3 < d < 10.5 and abs((x1 - x0) - d) < 0.3 and abs((y1 - y0) - d) < 0.3: out.append(d)
    return out
for nm, oid, zp in (('cover', ids[0], zc), ('tray', ids[1], zt)):
    man = body[oid]
    below = [pockets(man, zp - 0.16 - 0.08 - k * 0.16) for k in range(15)]   # mid-layers of the 15 layers before the pause layer
    open_ = all(len(b) == 1 for b in below); dia = below[0][0] if below[0] else 0
    first_open = None
    for k in range(40):
        if pockets(man, zp - 0.24 - k * 0.16): first_open = zp - 0.24 - k * 0.16
        else: break
    depth = (zp - 0.16) - (first_open - 0.08) if first_open else 0
    sealed = not pockets(man, zp - 0.08) and not pockets(man, zp + 0.08)
    chk(f'{nm}: pocket open on every layer up to the pause (z {zp:.2f}), sealed from the pause layer on', open_ and sealed)
    chk(f'{nm}: pocket fits a 9.53 x 2.53 magnet (Ø > 9.6, depth > 2.6)', dia > 9.6 and depth > 2.6, f'Ø{dia:.2f} x {depth:.2f} mm')
if len(sys.argv) > 2:
    g = open(sys.argv[2]).read().split('\n'); obj, zs, hits = None, None, []
    for l in g:
        mm = re.match(r'M486 A(.+)', l) or re.match(r'; printing object (.+)', l)
        if l.startswith('M486 S') and not l.startswith('M486 S-1'): obj = l
        if l.startswith(';Z:'): zs = float(l[3:])
        if l.startswith('M400 U1'): hits.append((obj, zs))
    labels = dict(re.findall(r'M486 S(\d+)\nM486 A(.+)', '\n'.join(g)))
    hits = [(labels.get(o.split()[1][1:], o), zz) for o, zz in hits]
    chk('G-code: exactly 2 pauses, cover then tray, at the pause layers', len(hits) == 2 and hits[0][0].startswith('Cover') and hits[1][0].startswith('Tray')
        and abs(hits[0][1] - zc) < 0.02 and abs(hits[1][1] - zt) < 0.02, str(hits))
print('ALL PASS' if ok else 'SOMETHING FAILED')
