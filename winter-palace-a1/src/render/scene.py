"""Write three.js scene files (binary meshes + json) for render/view.html."""
import json, os
import numpy as np


def put(outdir, name, V, F):
    """Write one mesh as <name>.bin (float32 positions then uint32 indices). Returns the manifest stub."""
    V = np.asarray(V, dtype=np.float32)
    F = np.asarray(F, dtype=np.uint32)
    with open(os.path.join(outdir, name + '.bin'), 'wb') as fh:
        fh.write(V.tobytes())
        fh.write(F.tobytes())
    return {'bin': name + '.bin', 'nv': int(len(V)), 'nt': int(len(F))}


def scene(outdir, name, meshes, cam, lights, **kw):
    d = {'meshes': meshes, 'cam': cam, 'lights': lights}
    d.update(kw)
    json.dump(d, open(os.path.join(outdir, name + '.json'), 'w'))


DAY = [{'t': 'hemi', 'c': '#ffffff', 'g': '#8a8f99', 'i': 1.9},
       {'t': 'dir', 'i': 2.6, 'p': [180, -330, 420], 'shadow': True, 'sd': 260},
       {'t': 'dir', 'i': 0.9, 'c': '#fff2dd', 'p': [-300, -120, 160]},
       {'t': 'dir', 'i': 0.6, 'p': [120, 300, 200]}]
