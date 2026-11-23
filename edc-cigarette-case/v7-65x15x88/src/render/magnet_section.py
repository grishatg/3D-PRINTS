"""Cut-through of the CLOSED v7.1 case at the magnets (mid-height): shows both sealed pockets, skins and the boss socket.
Usage (from v7-65x15x88/):  RIPPLE=rings python3 src/render/magnet_section.py <out.png>"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
import v7, numpy as np, matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
from matplotlib.patches import Polygon as MP, Rectangle
from shapely.geometry import Polygon
r = v7.build()
def sec(man):
    g = None
    for q in man.slice(v7.MZ).to_polygons():
        p = Polygon(q).buffer(0); g = p if g is None else g.symmetric_difference(p)
    return g
fig, ax = plt.subplots(figsize=(11, 6.4), dpi=160)
parts = [(r['cover'], '#9DA1A3')] + [(y, '#FFD00B') for y in r['yel_cover']] + [(r['tray'], '#2a2a2c')] + [(y, '#FFD00B') for y in r['yel_tray']]
for man, col in parts:
    g = sec(man)
    if g is None or g.is_empty: continue
    for q in getattr(g, 'geoms', [g]):
        ax.add_patch(MP(np.array(q.exterior.coords), closed=True, fc=col, ec='k', lw=0.5))
        for h in q.interiors: ax.add_patch(MP(np.array(h.coords), closed=True, fc='white', ec='k', lw=0.5))
MX, D, PH, MT = v7.MX, v7.D, v7.POCKET_H, v7.MAG_T
c0 = r['c_top_z'] - PH - D / 2; t1 = D / 2 - (r['t_top_z'] - PH)
for y0, lab in ((c0, 'grey-cover magnet'), (t1 - MT, 'black-tray magnet')):
    ax.add_patch(Rectangle((MX - v7.MAG_D / 2, y0), v7.MAG_D, MT, fc='#c0392b', ec='k', lw=0.8, zorder=5))
    ax.text(MX, y0 + MT / 2, lab, ha='center', va='center', color='white', fontsize=8.5, zorder=6, weight='bold')
nl = int(round(v7.SKIN / v7.LAYER))
def note(xy, txt, xt, yt):
    ax.annotate(txt, xy=xy, xytext=(xt, yt), fontsize=8.5, va='center', arrowprops=dict(arrowstyle='-', color='#555', lw=0.7))
note((MX + 3, c0 + MT + 0.4), f'{nl} layers (≈{v7.SKIN:.2f} mm) seal the cover magnet in\n(printed right after pause 1, z {r["pause_cover_z"]:.2f})', 35, -4.9)
note((MX + 3, t1 - MT - 0.45), f'{nl} layers (≈{v7.SKIN:.2f} mm) seal the tray magnet in\n(printed right after pause 2, z {r["pause_tray_z"]:.2f})', 35, -1.0)
note((MX + 4.6, -2.25 + (v7.SKIN - 0.48)), 'Ø11.85 socket in the round tray column\n(the grey boss sits in it: NOT the magnet hole)', 35, 2.6)
note((MX - 3, -6.2), f'{v7.SKIN_OUT:.2f} mm grey between magnet and outside', 35, -7.3)
ax.annotate('', xy=(MX - 6.4, c0 + MT), xytext=(MX - 6.4, t1 - MT), arrowprops=dict(arrowstyle='<->', color='#c0392b', lw=1.2))
ax.text(MX - 6.9, (c0 + MT + t1 - MT) / 2, f'{(t1 - MT) - (c0 + MT):.2f} mm\nmagnet to magnet', ha='right', va='center', color='#c0392b', fontsize=9, weight='bold')
ax.set_xlim(5, 58); ax.set_ylim(-D / 2 - 1.4, D / 2 + 1.2); ax.set_aspect('equal'); ax.invert_yaxis()
ax.set_title('Cut through the CLOSED case at the magnets (mid-height). Both magnets are sealed inside the plastic.', fontsize=10.5)
ax.text(5.3, -D / 2 - 0.6, 'outside: grey cover face', fontsize=8); ax.text(5.3, D / 2 + 0.9, 'outside: black tray back', fontsize=8)
ax.text(32.9, 4.9, 'opening\nedge', fontsize=8, ha='left')
ax.set_xlabel('mm'); ax.set_yticks([]); plt.tight_layout(); plt.savefig(sys.argv[1])
print('wrote', sys.argv[1], '| gap', round((t1 - MT) - (c0 + MT), 2))
