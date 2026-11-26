"""Shared paths + loaders for the Winter Palace A1 rework.

The designer's original 3MF is NOT kept in this repo (it is not ours to redistribute).
Pass its path in the WP_SRC environment variable, or to load_original().
"""
import os, re, zipfile
import numpy as np

WORK = os.environ.get('WP_WORK', '/tmp/wp_work')
SRC3MF = os.environ.get('WP_SRC', '')
NAMES = {'1': 'palace', '3': 'rosette', '5': 'base'}


def load_original(path=None):
    """Return {'palace': (V, F), 'rosette': (V, F), 'base': (V, F)} from the designer's Bambu 3MF.

    Vertices are in the file's own object coordinates (each part centred on its bounding box).
    The parsed meshes are cached as an npz in WORK.
    """
    path = path or SRC3MF
    os.makedirs(WORK, exist_ok=True)
    cache = os.path.join(WORK, 'orig_meshes.npz')
    if os.path.exists(cache):
        d = np.load(cache)
        return {n: (d['v_' + n], d['f_' + n]) for n in NAMES.values()}
    s = zipfile.ZipFile(path).read('3D/3dmodel.model').decode('utf-8')
    out = {}
    for m in re.finditer(r'<object id="(\d+)" type="model">\s*<mesh>(.*?)</mesh>', s, re.S):
        v = np.array(re.findall(r'<vertex x="([^"]+)" y="([^"]+)" z="([^"]+)"', m.group(2)), dtype=np.float64)
        f = np.array(re.findall(r'<triangle v1="(\d+)" v2="(\d+)" v3="(\d+)"', m.group(2)), dtype=np.int64)
        out[NAMES[m.group(1)]] = (v, f)
    np.savez_compressed(cache, **{'v_' + k: v for k, (v, f) in out.items()},
                        **{'f_' + k: f for k, (v, f) in out.items()})
    return out
