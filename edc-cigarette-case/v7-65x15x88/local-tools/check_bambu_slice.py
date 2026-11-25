#!/usr/bin/env python3
"""Check a file that the REAL Bambu Studio sliced (a ".gcode.3mf" from "Export plate sliced file" or from the command line).

Usage:  python check_bambu_slice.py <sliced.gcode.3mf>

Prints Bambu's own time estimate, filament per slot, colour changes and, per object, what the first layer (the plate-side
face) is made of: outer wall / inner wall / bottom surface lengths and the direction of the straight lines.
Written against the G-code comments Bambu Studio 1.9 - 2.x writes ("; FEATURE: ...", "; CHANGE_LAYER", "; Z_HEIGHT: ...",
"; start printing object, unique label id: N"). It was NOT run against real Bambu output when written: if a marker is missing
it says so instead of guessing. Read-only: it never talks to a printer.
"""
import sys, re, zipfile, math, json

def main(path):
    z = zipfile.ZipFile(path)
    names = z.namelist()
    gcodes = [n for n in names if n.lower().endswith('.gcode')]
    if not gcodes:
        print('NOT SLICED: no *.gcode inside', path); print('entries:', names[:30]); return 2
    for n in names:
        if n.endswith('slice_info.config'):
            info = z.read(n).decode('utf-8', 'replace')
            for key in ('prediction', 'weight', 'outside', 'support_used', 'label_object_enabled'):
                m = re.search(rf'<metadata key="{key}" value="([^"]*)"', info)
                if m: print(f'slice_info {key} = {m.group(1)}' + (f'  (= {int(m.group(1)) // 3600} h {int(m.group(1)) % 3600 // 60:02d} m)' if key == 'prediction' and m.group(1).isdigit() else ''))
            for w in re.findall(r'<warning msg="([^"]*)"[^>]*>', info): print('slice_info WARNING:', w)
            for fid, typ, col, used_m, used_g in re.findall(r'<filament id="(\d+)"[^>]*type="([^"]*)"[^>]*color="([^"]*)"[^>]*used_m="([^"]*)"[^>]*used_g="([^"]*)"', info):
                print(f'slice_info filament slot {fid}: {typ} {col} {used_g} g ({used_m} m)')
            names_by_id = dict(re.findall(r'<object identify_id="(\d+)" name="([^"]*)"', info))
            break
    else:
        names_by_id = {}
    g = z.read(gcodes[0]).decode('utf-8', 'replace').split('\n')
    print(f'{gcodes[0]}: {len(g)} lines')
    for l in g[:400]:
        if re.match(r'; (model printing time|total estimated time|total layer number|total filament (length|weight|volume)|max_z_height|BambuStudio)', l): print(' ', l.strip())
    changes = [l for l in g if re.match(r'^M620 S\d+', l) and not l.startswith('M620 S255')]
    print('filament load commands (M620 S<n>, = colour changes + the first load):', len(changes))
    pauses = [l for l in g if re.match(r'^(M400 U1|M601|M25)\b', l)]
    print('pause commands in the G-code:', len(pauses), '(must be 0)')
    # ---- first layer, per object
    obj = None; layer_z = None; feat = None; x = y = None; stats = {}; nlayer = 0
    for l in g:
        if l.startswith('; CHANGE_LAYER'): nlayer += 1
        m = re.match(r'; Z_HEIGHT: ([\d.]+)', l)
        if m: layer_z = float(m.group(1)); continue
        m = re.match(r'; start printing object, unique label id: (\d+)', l)
        if m: obj = m.group(1); continue
        if l.startswith('; stop printing object'): obj = None; continue
        m = re.match(r'; FEATURE: (.+)', l)
        if m: feat = m.group(1).strip(); continue
        if l.startswith('G1 ') or l.startswith('G0 '):
            mx = re.search(r' X([-\d.]+)', l); my = re.search(r' Y([-\d.]+)', l); me = re.search(r' E([-\d.]+)', l)
            nx = float(mx.group(1)) if mx else x; ny = float(my.group(1)) if my else y
            if me and float(me.group(1)) > 0 and x is not None and nx is not None and layer_z is not None and layer_z <= 0.21 and obj and feat:
                d = math.hypot(nx - x, ny - y)
                if d > 0:
                    s = stats.setdefault(obj, {}).setdefault(feat, [0.0, {}])
                    s[0] += d
                    if d >= 1.0:
                        a = round(math.degrees(math.atan2(ny - y, nx - x)) % 180 / 5) * 5 % 180
                        s[1][a] = s[1].get(a, 0.0) + d
            x, y = nx, ny
    if not nlayer: print('NOTE: no "; CHANGE_LAYER" markers found: this Bambu version writes other markers; read the G-code by hand.')
    if not stats: print('NOTE: no per-object first-layer data found (object labels or FEATURE comments missing). Check "Label objects" / read the G-code by hand.')
    for o, fs in stats.items():
        nm = names_by_id.get(o, f'object {o}')
        print(f'first layer of {nm}:')
        for f_, (ln, ang) in sorted(fs.items(), key=lambda kv: -kv[1][0]):
            top = sorted(ang.items(), key=lambda kv: -kv[1])[:2]
            print(f'    {f_:22s} {ln:8.0f} mm' + (f'   main line direction(s): ' + ', '.join(f'{a} deg ({100 * v / max(sum(ang.values()), 1e-9):.0f} %)' for a, v in top) if top else ''))
    print('\nWHAT TO EXPECT (ENDGRAIN + CUBES, no initials, v10.6):')
    print('  - every lid and tray: "Inner wall" on the first layer is 0 or close to 0 (one outline per cell, no rings);')
    print('  - "Bottom surface" lines run along each part: 90 deg for the two parts that sit upright on the plate, 0 deg for the two turned 90;')
    print('  - total time about 5 h 20 m (+/- 20 m), 19 colour changes, no pause commands, filament about 11 g oak, 12 g teak, 0 g slot 3, 48 g walnut.')
    return 0

if __name__ == '__main__':
    sys.exit(main(sys.argv[1]) if len(sys.argv) == 2 else print(__doc__) or 1)
